Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968)

## REPORNIRE (comanda exacta, gata de dat)
Audit tenant_005 terminat pe: straturi migrare (9), FRONT D (declaratii), FRONT E (editare salariat), BACKLOG
DIACRITICE generatoare declaratii, CLUSTER A11Y (contrast/title-only/tinta). Continua cu clusterul RAMAS (metoda
Regula 13+14: captura PRIVITA + axe/mobil pe fiecare ecran atins, REPARAND, gard RED-probat; DS inainte de cod UI;
versioneaza_assets --scrie dupa editare static/js; commit pe iconta_nou = poarta ~9min + post-commit publica+restart).
Probe Playwright: helper frontend_test/w_auth (tenant_005 id=4840); scripturi in ~/probe_t005 (server).

## CLUSTER RAMAS
- **Field-level error marking** — erorile de formular (ex. Vector fiscal, la salvare fara camp obligatoriu) NU
  marcheaza campul vinovat cu contur/mesaj langa el; apare o cutie generica jos, iar mesajul NUMESTE campul dar nu-l
  evidentiaza vizual. Pattern app-wide (Regula 14 pct.4 "eroarea care nu marcheaza campul vinovat"). Componenta comuna:
  formularele cu .vf-eroare/.mig-eroare/#*-eroare. De reparat la nivel de tipar (marcaj rosu pe campul cu eroare +
  ancorare mesaj). axe/mobil pe fiecare ecran atins.

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = 09bb2cd. Comituri ultima tura: 09010f7 (diacritice generatoare),
ad1f6a8 (registre), 09bb2cd (a11y contrast/title-only/tinta). Poarta verde pe fiecare (suita 2292 passed, verificator
0). RUNNING confirmat: axe contrast=0 pe dashboard/vector/salariati (captura privita, identitate vizuala pastrata).

## LIVRAT (cluster a11y, 09bb2cd)
axe-core (audit) a gasit 5 perechi text/fundal sub 4.5:1 - reparate la SURSA (token/paleta, nu instanta): --albastru
#3d8fd6->#347ab8; .camp-ajutor ->#2f6fa6; CULORI_CARD (api.js) verde #16a34a->#117f39 + teal #0a807b->#097a76;
po-indicator var(--verde)->var(--verde-inchis #1b7349). title-only pierdut pe touch (po-indicator + nav-ghid) ->
aria-label. tinta .subbara-edu 18px->24px (AA). Gard browser-free core/test_a11y_contrast_tokens.py (recalcul contrast
din sursa, RED-probat). DS v2.42. RAMAS notat: butoanele nav (30-36px) trec AA(24) dar nu AAA(44); .btn-link are inca
#3d8fd6 literal (de verificat pe fundal alb intr-un audit viitor).
