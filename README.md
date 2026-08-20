# Projekt

Két egymástól független Next.js weboldal található ebben a repositoryban.

- `website/` – NEXORA IT weboldal
- `csiperkegomba/` – az új csiperkegomba weboldal kiinduló projektje

Mindkét oldal külön telepíthető és indítható a saját mappájából:

```powershell
npm.cmd install
npm.cmd run dev
```

Ha egyszerre futnak, a második projektet eltérő porton indítsd: `npm.cmd run dev -- -p 3001`.
