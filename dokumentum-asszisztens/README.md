# Irattár – helyi dokumentum-asszisztens

Internet és külső API nélkül futó első verzió dokumentumok és képek átvizsgálására. A program javaslatot tesz a fájlok év és kategória szerinti elhelyezésére, felismeri a tartalmilag azonos fájlokat, és minden alkalmazott átnevezést vagy áthelyezést visszavonhatóan naplóz.

## Indítás

Python 3.11 vagy újabb szükséges, további csomagot nem kell telepíteni.

```powershell
cd G:\Projekt\dokumentum-asszisztens
npm.cmd run dev
```

Ezután nyisd meg a `http://localhost:3011` címet. Első alkalommal add meg a kezelendő mappa teljes útvonalát. Célszerű először egy másolatokat tartalmazó tesztmappával kipróbálni.

## Biztonsági modell

- A szerver kizárólag a `127.0.0.1` helyi címen figyel.
- A beállított gyökérmappán kívüli útvonalakat elutasítja.
- Átvizsgáláskor nem módosít fájlt.
- Névütközésnél sorszámozott új nevet választ, nem ír felül.
- Minden műveletet a `.local/operations.sqlite3` helyi adatbázis tárol.
- Visszavonás előtt ellenőrzi, hogy a fájl tartalma nem változott-e.
- Automatikus törlés nincs.

## Jelenlegi hatókör

Az MVP fájlnév, kiterjesztés, dátum, méret és SHA-256 tartalmi hash alapján dolgozik. A következő fejlesztési lépcső a helyi EXIF-kiolvasás, PDF/DOCX szövegkinyerés, OCR és az Ollamán futó helyi nyelvi modell bekötése.
