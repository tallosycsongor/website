from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".rtf", ".csv", ".odt", ".xlsx"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".heic"}
MONTHS = {"január": "01", "február": "02", "március": "03", "április": "04", "május": "05", "június": "06", "július": "07", "augusztus": "08", "szeptember": "09", "október": "10", "november": "11", "december": "12"}


def safe_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("A megadott mappa nem létezik.")
    return root


def within(root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("A fájl kívül esik az engedélyezett mappán.")
    return candidate


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_name(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:180] or "nevtelen"


def classify(name: str) -> str:
    lowered = name.lower()
    rules = {
        "Számlák": ("számla", "invoice", "nyugta"),
        "Szerződések": ("szerződés", "contract", "megállapodás"),
        "Biztosítás": ("biztosítás", "kötvény"),
        "Garancia": ("garancia", "jótállás"),
        "Egészségügy": ("lelet", "recept", "ambuláns", "zárójelentés"),
        "Hivatalos": ("határozat", "igazolás", "kérelem", "adó"),
    }
    return next((category for category, words in rules.items() if any(word in lowered for word in words)), "Egyéb")


def date_from_name(name: str) -> str | None:
    match = re.search(r"(?<!\d)(20\d{2})[-_. ](0?[1-9]|1[0-2])[-_. ]([0-2]?\d|3[01])(?!\d)", name)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    lowered = name.lower()
    for month, number in MONTHS.items():
        match = re.search(rf"(20\d{{2}}).*?{month}", lowered)
        if match:
            return f"{match.group(1)}-{number}"
    return None


def unique_target(target: Path, source: Path | None = None) -> Path:
    if target == source or not target.exists():
        return target
    for index in range(2, 10_000):
        candidate = target.with_name(f"{target.stem}_{index:02d}{target.suffix}")
        if not candidate.exists():
            return candidate
    raise ValueError("Nem található szabad fájlnév.")


def inspect_file(root: Path, path: Path, hashes: dict[str, str]) -> dict:
    stat = path.stat()
    extension = path.suffix.lower()
    kind = "image" if extension in IMAGE_EXTENSIONS else "document"
    digest = file_hash(path)
    duplicate_of = hashes.get(digest)
    hashes.setdefault(digest, str(path.relative_to(root)))
    created = datetime.fromtimestamp(stat.st_ctime)
    modified = datetime.fromtimestamp(stat.st_mtime)
    found_date = date_from_name(path.stem) or modified.strftime("%Y-%m-%d")
    if kind == "image":
        destination = Path("Képek") / found_date[:4] / found_date[:7]
        suggested_name = clean_name(f"{found_date}_{path.stem}{extension}")
        category = "Kép"
    else:
        category = classify(path.stem)
        destination = Path("Dokumentumok") / category / found_date[:4]
        prefix = "" if date_from_name(path.stem) else f"{found_date}_"
        suggested_name = clean_name(f"{prefix}{path.stem}{extension}")
    target = unique_target(root / destination / suggested_name, path)
    return {
        "path": str(path.relative_to(root)), "name": path.name, "kind": kind,
        "category": category, "size": stat.st_size, "modified": modified.isoformat(timespec="seconds"),
        "hash": digest, "duplicateOf": duplicate_of,
        "suggestedPath": str(target.relative_to(root)),
        "needsChange": path != target,
    }


def scan(root: Path) -> list[dict]:
    hashes: dict[str, str] = {}
    results = []
    supported = DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in supported and ".dokumentum-asszisztens" not in path.parts:
            try:
                results.append(inspect_file(root, path, hashes))
            except (OSError, PermissionError):
                continue
    return results


class Journal:
    def __init__(self, database: Path):
        database.parent.mkdir(parents=True, exist_ok=True)
        self.database = database
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, original_path TEXT NOT NULL,
                current_path TEXT NOT NULL, content_hash TEXT NOT NULL, status TEXT NOT NULL
            )""")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.database)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def list(self, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM operations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def move(self, root: Path, source_value: str, target_value: str) -> dict:
        source = within(root, source_value)
        target = within(root, target_value)
        if not source.is_file():
            raise ValueError("A forrásfájl nem található.")
        target = unique_target(target, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = file_hash(source)
        source.rename(target)
        with self.connect() as db:
            cursor = db.execute(
                "INSERT INTO operations(created_at, original_path, current_path, content_hash, status) VALUES(?,?,?,?,?)",
                (datetime.now().isoformat(timespec="seconds"), str(source.relative_to(root)), str(target.relative_to(root)), digest, "applied"),
            )
            operation_id = cursor.lastrowid
        return {"id": operation_id, "originalPath": str(source.relative_to(root)), "currentPath": str(target.relative_to(root))}

    def undo(self, root: Path, operation_id: int) -> dict:
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM operations WHERE id = ?", (operation_id,)).fetchone()
            if not row or row["status"] != "applied":
                raise ValueError("A művelet nem vonható vissza.")
            current = within(root, row["current_path"])
            original = within(root, row["original_path"])
            if not current.is_file():
                raise ValueError("Az áthelyezett fájl már nem található.")
            if file_hash(current) != row["content_hash"]:
                raise ValueError("A fájl tartalma megváltozott; a visszavonás leállt.")
            if original.exists():
                raise ValueError("Az eredeti helyen már létezik azonos nevű fájl.")
            original.parent.mkdir(parents=True, exist_ok=True)
            current.rename(original)
            db.execute("UPDATE operations SET status = 'undone' WHERE id = ?", (operation_id,))
        return {"id": operation_id, "restoredPath": str(original.relative_to(root))}
