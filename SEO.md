# SEO.md — campania SEO

## Faza 0: vizibilitate (nicio pagină nouă până nu confirmăm indexarea celor existente)

**POARTA FAZEI 0:** nu se scrie nicio pagină nouă de ghid până când TOATE cele publicate au
`Indexat Google = da`. „Servit 200" (corect tehnic) NU e același lucru cu „indexat de Google" —
o pagină poate fi impecabilă tehnic și încă absentă din indexul Google.

**Ce înseamnă coloanele:**
- **Publicat** — data `published` din front matter; pagina există în `ghid/` (sursa UNICĂ; `FUNCTIONALITATI.csv` nu mai decide ce pagini există).
- **Servit 200** — producția o servește la `/ghid/{slug}` cu 200, `noindex` absent, canonical propriu, în `sitemap.xml`. Auditat 12.08.2026 (vezi mai jos).
- **Indexat Google** — CONFIRMAT prezent în indexul Google (`site:iconta.eu/ghid/{slug}` întoarce pagina, sau Search Console → Pages = Indexed). Trece la `da` DOAR pe confirmare reală, niciodată dedus din faptul că e servit sau din vechime.

**Baseline 12.08.2026: `Indexat Google = nu` pe TOATE paginile din ghid/ — fără excepție, inclusiv cele trei din iulie.**
Vechimea (3 săptămâni) NU e dovadă de indexare; până nu confirm în `site:` / Search Console, statusul e „nu".

| # | Ghid | Publicat | Servit 200 | Indexat Google |
|---|------|----------|:----------:|:--------------:|
| 1 | ce-verifici-cand-preiei-o-firma-de-la-alt-contabil | 2026-07-26 (iul) | da | **nu** |
| 2 | concediu-medical-cine-suporta | 2026-08-12 | da | **nu** |
| 3 | control-incrucisat-d112 | 2026-08-12 | da | **nu** |
| 4 | control-incrucisat-d390 | 2026-07-26 (iul) | da | **nu** |
| 5 | cota-tva-avans-inainte-livrare-dupa | 2026-07-26 (iul) | da | **nu** |
| 6 | cote-tva-2025 | 2026-08-12 | da | **nu** |
| 7 | d311-tva-cod-anulat | 2026-08-13 | da | **nu** |
| 8 | d394-ce-declari-reconciliere | 2026-08-12 | da | **nu** |
| 9 | decont-tva-d300-rezultat | 2026-08-12 | da | **nu** |
| 10 | diurna-externa-neimpozabila | 2026-08-12 | da | **nu** |
| 11 | diurna-interna-neimpozabila | 2026-08-12 | da | **nu** |
| 12 | formular-230-redirectionare | 2026-08-13 | da | **nu** |
| 13 | impozit-dividende-2026 | 2026-08-12 | da | **nu** |
| 14 | impozit-micro-2026 | 2026-08-12 | da | **nu** |
| 15 | plafon-plati-numerar | 2026-08-13 | da | **nu** |
| 16 | regim-marja-second-hand | 2026-08-12 | da | **nu** |
| 17 | regim-special-agentii-turism | 2026-08-12 | da | **nu** |
| 18 | saf-t-ce-contine-fisierul | 2026-08-13 | da | **nu** |
| 19 | saf-t-d406-cine-depune | 2026-08-13 | da | **nu** |
| 20 | salariu-minim-2026 | 2026-08-12 | da | **nu** |
| 21 | sponsorizare-credit-fiscal | 2026-08-12 | da | **nu** |
| 22 | taxare-inversa-interna | 2026-08-12 | da | **nu** |
| 23 | termen-depunere-d101 | 2026-08-12 | da | **nu** |
| 24 | tva-la-incasare-exigibilitate | 2026-08-12 | da | **nu** |

**Total: toate paginile din ghid/ publicate · toate servite 200 · 0 confirmate indexate în Google.** Poarta faza 0 = ÎNCHISĂ (toate × „nu").

## Constatări audit tehnic 12.08.2026 (partea „Servit 200")

Cele existente sunt corecte tehnic — nimic nu blochează crawl/index:
- `sitemap.xml`: URL-uri = landing `/` + `/ghid` + toate paginile din ghid/ + `/public/termeni`.
- `robots.txt`: `User-agent: *` / `Allow: /` / `Sitemap: https://iconta.eu/sitemap.xml` — indexare permisă, fără `Disallow`.
- Per ghid: 200, un singur `<title>` / meta description / canonical (auto-referit) / og:* / JSON-LD `Article` propriu, exact un `<h1>`, `noindex` absent (0 pagini cu noindex din ghid/).
- 404 corect (cu `noindex`) pe slug inexistent — nu 200 cu conținut gol.

## Slăbiciuni de calitate (deschise — nu blochează indexarea, de decis în faza următoare)

1. `og:image` e placeholder global (`static/logo_login.png`) pe toate paginile și în JSON-LD `image`; codul are `DE_FACUT: imagine dedicata per ghid`. Inconsecvent cu `publisher.logo` = `icon-512.png`.
2. Landing `<title>` = „iConta.eu" sec — fără titlu descriptiv/cu cuvinte-cheie pe cea mai importantă pagină.
3. Meta description landing fără diacritice („Contabilitate in cloud… inainte… Declaratii… si"), inconsecvent cu ghidurile.

## Ce urmează (faza 0, înainte de orice pagină nouă)

- Trimite `sitemap.xml` în Google Search Console; cere indexare pentru toate paginile din ghid/.
- Verifică `site:iconta.eu/ghid/{slug}` per pagină; pe confirmare, treci rândul la `Indexat Google = da`.
- Când toate paginile din ghid/ = `da`, poarta faza 0 se deschide → se pot scrie pagini noi.

## 19.10.2026 — Search Console (comanda 9.1 D2): ce spun exporturile și ce s-a reparat

- **404 (17 adrese, ultima accesare 12.06–30.07):** niciuna nu are rută; 7 răspundeau deja 410 (lotul 7), 10 încă 404 -> retrase (410 +
  `X-Robots-Tag: noindex`, `main.ADRESE_RETRASE`). `robots.txt` (`Disallow: /`) le închidea, deci Google nu vedea niciodată 410-ul: acum
  permite numai calea exactă a fiecărei adrese retrase (`Allow: <cale>$` și `<cale>?`, RFC 9309 §2.2.2), restul aplicației rămâne închis
  (C54, `core/test_search_console_404.py`). După publicare: „Validare remediere” în Search Console.
- **Accesată, neindexată (98) / descoperită, neindexată (4.185; exportul are primele 1.000):** ghiduri, tehnic curate (200, canonical
  propriu, fără noindex, `lastmod` din front-matter, la 3 clicuri de `/ghid`). Cauzele verificabile: pagina principală goală pentru crawler
  (`index.html` are numai `<div id="app">`, JS-ul e în `Disallow`), volumul (6.513 ghiduri deodată pe un domeniu nou: „descoperită” 0 ->
  3.652 pe 05.10), legăturile interne subțiri (830 de ghiduri fără niciun link de la alt ghid). Googlebot (nginx, 05–19.10): 2.711 cereri pe
  `/ghid/`, 2.404 ghiduri distincte, niciun 5xx.
- **Decizii cerute (raportul 9.1):** blocul static pe pagina principală; suprafața indexată (toate / fără cele sub 400 de cuvinte),
  paginarea temelor mari, legăturile între ghiduri. Analiza: `~/ghid_incoming/lot9_search_console/`.
