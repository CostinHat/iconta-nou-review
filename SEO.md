# SEO.md — campania SEO

## Faza 0: vizibilitate (nicio pagină nouă până nu confirmăm indexarea celor existente)

**POARTA FAZEI 0:** nu se scrie nicio pagină nouă de ghid până când TOATE cele publicate au
`Indexat Google = da`. „Servit 200" (corect tehnic) NU e același lucru cu „indexat de Google" —
o pagină poate fi impecabilă tehnic și încă absentă din indexul Google.

**Ce înseamnă coloanele:**
- **Publicat** — data `published` din front matter; pagina există în `ghid/` și în `FUNCTIONALITATI.csv` (`ghid_slug`).
- **Servit 200** — producția o servește la `/ghid/{slug}` cu 200, `noindex` absent, canonical propriu, în `sitemap.xml`. Auditat 12.08.2026 (vezi mai jos).
- **Indexat Google** — CONFIRMAT prezent în indexul Google (`site:iconta.eu/ghid/{slug}` întoarce pagina, sau Search Console → Pages = Indexed). Trece la `da` DOAR pe confirmare reală, niciodată dedus din faptul că e servit sau din vechime.

**Baseline 12.08.2026: `Indexat Google = nu` pe TOATE cele 19 — fără excepție, inclusiv cele trei din iulie.**
Vechimea (3 săptămâni) NU e dovadă de indexare; până nu confirm în `site:` / Search Console, statusul e „nu".

| # | Ghid | Publicat | Servit 200 | Indexat Google |
|---|------|----------|:----------:|:--------------:|
| 1 | ce-verifici-cand-preiei-o-firma-de-la-alt-contabil | 2026-07-26 (iul) | da | **nu** |
| 2 | control-incrucisat-d390 | 2026-07-26 (iul) | da | **nu** |
| 3 | cota-tva-avans-inainte-livrare-dupa | 2026-07-26 (iul) | da | **nu** |
| 4 | concediu-medical-cine-suporta | 2026-08-12 | da | **nu** |
| 5 | control-incrucisat-d112 | 2026-08-12 | da | **nu** |
| 6 | cote-tva-2025 | 2026-08-12 | da | **nu** |
| 7 | d394-ce-declari-reconciliere | 2026-08-12 | da | **nu** |
| 8 | decont-tva-d300-rezultat | 2026-08-12 | da | **nu** |
| 9 | diurna-externa-neimpozabila | 2026-08-12 | da | **nu** |
| 10 | diurna-interna-neimpozabila | 2026-08-12 | da | **nu** |
| 11 | impozit-dividende-2026 | 2026-08-12 | da | **nu** |
| 12 | impozit-micro-2026 | 2026-08-12 | da | **nu** |
| 13 | regim-marja-second-hand | 2026-08-12 | da | **nu** |
| 14 | regim-special-agentii-turism | 2026-08-12 | da | **nu** |
| 15 | salariu-minim-2026 | 2026-08-12 | da | **nu** |
| 16 | sponsorizare-credit-fiscal | 2026-08-12 | da | **nu** |
| 17 | taxare-inversa-interna | 2026-08-12 | da | **nu** |
| 18 | termen-depunere-d101 | 2026-08-12 | da | **nu** |
| 19 | tva-la-incasare-exigibilitate | 2026-08-12 | da | **nu** |

**Total: 19 publicate · 19 servite 200 · 0 confirmate indexate în Google.** Poarta faza 0 = ÎNCHISĂ (19 × „nu").

## Constatări audit tehnic 12.08.2026 (partea „Servit 200")

Cele existente sunt corecte tehnic — nimic nu blochează crawl/index:
- `sitemap.xml`: 22 URL = landing `/` + `/ghid` + 19 ghiduri + `/public/termeni`.
- `robots.txt`: `User-agent: *` / `Allow: /` / `Sitemap: https://iconta.eu/sitemap.xml` — indexare permisă, fără `Disallow`.
- Per ghid: 200, un singur `<title>` / meta description / canonical (auto-referit) / og:* / JSON-LD `Article` propriu, exact un `<h1>`, `noindex` absent (0/19).
- 404 corect (cu `noindex`) pe slug inexistent — nu 200 cu conținut gol.

## Slăbiciuni de calitate (deschise — nu blochează indexarea, de decis în faza următoare)

1. `og:image` e placeholder global (`static/logo_login.png`) pe toate paginile și în JSON-LD `image`; codul are `DE_FACUT: imagine dedicata per ghid`. Inconsecvent cu `publisher.logo` = `icon-512.png`.
2. Landing `<title>` = „iConta.eu" sec — fără titlu descriptiv/cu cuvinte-cheie pe cea mai importantă pagină.
3. Meta description landing fără diacritice („Contabilitate in cloud… inainte… Declaratii… si"), inconsecvent cu ghidurile.

## Ce urmează (faza 0, înainte de orice pagină nouă)

- Trimite `sitemap.xml` în Google Search Console; cere indexare pentru cele 19 URL.
- Verifică `site:iconta.eu/ghid/{slug}` per pagină; pe confirmare, treci rândul la `Indexat Google = da`.
- Când toate 19 = `da`, poarta faza 0 se deschide → se pot scrie pagini noi.
