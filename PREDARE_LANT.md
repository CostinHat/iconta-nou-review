Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968)

## REPORNIRE (comanda exacta, gata de dat)
Audit tenant_005 terminat pe: straturi migrare (toate 9), FRONT D (declaratii), FRONT E (editare salariat),
BACKLOG DIACRITICE generatoare declaratii (INCHIS). Continua cu CLUSTERELE RAMASE (metoda Regula 13+14:
captura PRIVITA + axe/mobil pe fiecare ecran atins, REPARAND, gard RED-probat; DS inainte de cod UI;
versioneaza_assets --scrie dupa editare static/js; commit pe iconta_nou = poarta ~9min + post-commit publica+restart).
Probe Playwright: helper frontend_test/w_auth (tenant_005 id=4840); scripturi in ~/probe_t005 (server).

## CLUSTERE RAMASE (in ordine sugerata)
- **CLUSTER A11Y (pe toate ecranele)** — axe da 14-15 noduri color-contrast (serious), ~11-17 tinte <44px, 2 info
  livrata EXCLUSIV prin `title` (pierduta pe touch, Pixel 5). Pre-existent APP-WIDE (CSS + componenta comuna
  .vf-opt/.mig-*). Cluster CSS dedicat.
- **Field-level error marking** — erorile de formular (ex. Vector) NU marcheaza campul vinovat cu contur (mesajul il
  numeste). Pattern app-wide (Regula 14 pct.4).

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = 09010f7. Comituri ultima tura: e651da0 (Front D+E),
b048943 (registre D+E), 09010f7 (campanie diacritice generatoare declaratii). Poarta verde pe fiecare (suita 1965
passed, verificator 0). RUNNING confirmat BEHAVIORAL: mesajul de blocaj D205 randeaza cu diacritice ("D205 fara ->
fără niciun beneficiar... nu se generează declarație fără conținut") - captura privita.

## LIVRAT (campanie diacritice, 09010f7)
Backlog-ul sistemic INCHIS: mesajele de blocaj/avertisment ale TUTUROR generatoarelor de declaratii (d100..d710 +
d101g/d212_engine/d406_active/d406_stocuri/bilant_api/declaratii_api, 58 fisiere) diacriticizate integral (~840
literale). Unealta gard-driven (dictionar high-precision aplicat DOAR pe literalii-mesaj: spatiu + cuvant mapat;
exclus XML-tag, SQL prin span execute() AST, alias.coloana, chei de dict). Cazuri-limita rezolvate: byte-string,
coloane SQL multi-fragment (f.directie), sageata "->" (nu tag XML), chei in backtick (`manual.obligatii` = cheie).
Gard test_generatoare_declaratii_cu_diacritice extins la toate 58 fisierele. ~18 fisiere de test aliniate.
Unealta reutilizabila: ~/probe_t005/diacriticize.py + diac_map.py (pe server).
