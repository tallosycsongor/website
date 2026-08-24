# Projektgyűjtemény

Ez a repository több, egymástól független webalkalmazást és két Windowsos segédszkriptet tartalmaz. A gyökérmappában nincs közös `package.json`, ezért minden alkalmazást a saját könyvtárából kell telepíteni, indítani és ellenőrizni.

## Mi micsoda?

| Mappa / fájl | Port | Feladat |
| --- | ---: | --- |
| `nexorawebsite/` | 3000 | Az OPSENTRA bemutatkozó és szolgáltatói weboldala. Next.js alkalmazás kapcsolatfelvételi űrlappal, SEO-metaadatokkal, sitemap- és robots-fájllal. |
| `neon-pulse/` | 3001 | Rövid, 30 másodperces ügyességi játék. A játékosnak a forgó jelzőt a céltartományban kell megállítania; a rekordot a böngésző helyben tárolja. |
| `csiperkegomba/` | 3002 | Üres, továbbfejlesztésre előkészített Next.js kezdőprojekt. Jelenleg csak egy státuszoldalt jelenít meg. Ez a mappa szándékosan nincs Gitben követve. |
| `csaladiindulo/` | 3003 | Családi indulási, csomagolási és ismétlődő listákhoz készült PWA. Helyi demómódban is működik, a felhős családi megosztáshoz Supabase-séma áll rendelkezésre. |
| `gyogyszervan/` | 3004 | Gyógyszerhiányok keresését és gyógyszertári közösségi jelzéseket bemutató PWA-MVP. Jelenleg kizárólag demóadatokat használ, egészségügyi döntésre nem alkalmas. |
| `helyifigyelo/` | 3005 | Helyi közérdekű eseményeket listán és térképen megjelenítő PWA. A beépített események demóadatok; az éles adatkezeléshez Supabase-migráció tartozik. |
| `kosaror/` | 3006 | Egységár-összehasonlító, bevásárlólista- és költségkeret-követő PWA. Vendég módban helyi tárolást, opcionálisan Supabase-fiókot használ. |
| `mikorjarle/` | 3007 | Lejáratok, garanciák, okmányok, gyógyszerek és előfizetések nyilvántartására szolgáló PWA naptárral, emlékeztetőkkel és CSV-exporttal. |
| `oddsagent/` | 3010 | OddsPilot napi sportodds-elemző; API-kulcs nélkül demómódban, Odds API-kulccsal élő piaci árakkal működik. |
| `homersekletfigyelo/temperature-logger.ps1` | – | A LibreHardwareMonitor szenzoraiból rendszeres időközönként kiolvassa a CPU, GPU, alaplap, memória és háttértár elérhető hőmérsékleteit, majd CSV-be írja őket. |
| `homersekletfigyelo/start-temperature-logging.ps1` | – | Rendszergazdai PowerShell-ablakban elindítja a hőmérséklet-naplózót 5 másodperces mintavétellel, 60 perces időtartamra. |

## Webalkalmazás indítása

Node.js és npm szükséges. A Vite-alapú alkalmazásokhoz Node.js 22 vagy újabb verzió ajánlott. Lépj be a választott projekt mappájába, majd futtasd:

```powershell
cd .\mikorjarle
npm.cmd install
Copy-Item .env.example .env.local
npm.cmd run dev
```

A példában a `mikorjarle` tetszőlegesen lecserélhető a fenti táblázat bármelyik projektmappájára. A Next.js projektekben (`nexorawebsite`, `neon-pulse`, `csiperkegomba`) nincs `.env.example`, ezért ott a másolási lépést ki kell hagyni.

Az alkalmazást ezután a táblázatban jelzett porton lehet megnyitni, például: `http://localhost:3007`.

> A `--strictPort` beállítást használó Vite-projektek nem választanak automatikusan másik portot. Ha a megadott port foglalt, előbb állítsd le az azt használó folyamatot.

## Gyakori npm-parancsok

A parancsokat mindig az adott projekt saját mappájában futtasd.

| Parancs | Mit csinál? |
| --- | --- |
| `npm.cmd install` | Telepíti a projekt `package.json` fájljában felsorolt függőségeket. |
| `npm.cmd run dev` | Elindítja a fejlesztői szervert automatikus újratöltéssel. |
| `npm.cmd run build` | Elkészíti és közben típusellenőrzi a production buildet. |
| `npm.cmd test` | Lefuttatja a Vitest teszteket, ha az adott projekt tartalmaz ilyen scriptet. |
| `npm.cmd run lint` | Lefuttatja a statikus kódelemzést, ha az adott projekt tartalmaz ilyen scriptet. |
| `npm.cmd run preview` | Helyben megnyitja az elkészült Vite production buildet, ahol ez a script elérhető. |
| `npm.cmd start` | Elindítja a korábban elkészített Next.js production buildet. |

## Supabase és helyi demómód

A `csaladiindulo`, `gyogyszervan`, `helyifigyelo`, `kosaror` és `mikorjarle` alkalmazás Supabase nélkül is elindítható helyi vagy demómódban. A böngészőben rögzített helyi adatok törlődhetnek a webhelyadatok vagy a `localStorage` ürítésekor.

Felhős működéshez:

1. másold az adott projekt `.env.example` fájlját `.env.local` néven;
2. add meg benne a Supabase projekt URL-jét és publikus anon kulcsát;
3. alkalmazd az adott projekt `supabase/migrations/` mappájában található SQL-migrációkat;
4. szükség esetén töltsd be a `seed.sql` vagy `demo.sql` mintaadatokat.

Részletes beállításokért és az egyes alkalmazások korlátaiért olvasd el az adott almappa saját `README.md` fájlját. Supabase `service_role` kulcsot soha ne tegyél kliensoldali környezeti fájlba.

## Hőmérséklet-naplózás Windows alatt

A naplózóhoz telepített LibreHardwareMonitor szükséges. Az alapértelmezett, egyórás mérés indítása:

```powershell
.\homersekletfigyelo\start-temperature-logging.ps1
```

A rendszer jogosultságkérést jelenít meg. A mérés eredménye alapértelmezés szerint a `homersekletfigyelo/temperature-history.csv` fájlba kerül. A futás `Ctrl+C` billentyűkombinációval leállítható.

Egyedi mintavétel és időtartam közvetlenül is megadható:

```powershell
.\homersekletfigyelo\temperature-logger.ps1 -IntervalSeconds 10 -DurationMinutes 30 -OutputPath .\meres.csv
```

## Fontosabb fájlok az alkalmazásokban

| Útvonal | Szerepe |
| --- | --- |
| `package.json` | Függőségek, indítási, build-, lint- és tesztparancsok. |
| `src/App.tsx` | A Vite/React alkalmazások fő felülete és vezérlési logikája. |
| `src/main.tsx` | A Vite/React alkalmazás böngészőoldali belépési pontja. |
| `app/page.tsx` | A Next.js alkalmazás kezdőoldala. |
| `app/layout.tsx` | A Next.js oldal közös kerete és metaadatai. |
| `src/lib/` | Újrafelhasználható üzleti logika, adattárolás, validáció és Supabase-kliens. |
| `src/components/` vagy `components/` | Újrafelhasználható felületi komponensek. |
| `supabase/migrations/` | Verziózott adatbázisséma, jogosultságok és Row Level Security szabályok. |
| `public/` | Statikus fájlok, például ikonok és PWA-erőforrások. |
| `vite.config.ts` | A Vite fejlesztői szerver, PWA és build beállításai. |
| `tsconfig*.json` | TypeScript fordítási és típusellenőrzési beállítások. |

## Repository-szintű segédfájlok

- `AGENTS.md`: a kódon dolgozó automatizált ügynökök projektutasításai.
- `CLAUDE.md`: további fejlesztői/ügynök-kontextus.
- `.gitignore`: meghatározza a Git által figyelmen kívül hagyott fájlokat és mappákat, köztük a helyi `csiperkegomba/` projektet és a generált állományokat.
