import tempfile
import unittest
from pathlib import Path

from core import Journal, clean_name, scan, within


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def test_rejects_path_outside_root(self):
        with self.assertRaises(ValueError):
            within(self.root, "../titok.txt")

    def test_move_and_undo_preserves_content(self):
        source = self.root / "scan001_számla.txt"
        source.write_text("próba", encoding="utf-8")
        journal = Journal(self.root / ".state" / "journal.sqlite3")
        operation = journal.move(self.root, source.name, "Dokumentumok/Számlák/2026/szamla.txt")
        moved = self.root / operation["currentPath"]
        self.assertTrue(moved.exists())
        journal.undo(self.root, operation["id"])
        self.assertEqual(source.read_text(encoding="utf-8"), "próba")

    def test_scan_marks_duplicate(self):
        (self.root / "a.jpg").write_bytes(b"same")
        (self.root / "b.jpg").write_bytes(b"same")
        results = scan(self.root)
        self.assertEqual(sum(bool(item["duplicateOf"]) for item in results), 1)

    def test_clean_name_removes_windows_reserved_characters(self):
        self.assertEqual(clean_name('rossz:<név>?.pdf'), "rossz--név--.pdf")


if __name__ == "__main__":
    unittest.main()
