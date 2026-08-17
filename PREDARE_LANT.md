Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit tenant_005 (Constructii Profit Trim SRL / P2, cabinet 1968); straturi migrare + fronturi D/E TERMINATE

## REPORNIRE (comanda exacta, gata de dat)
Auditul tenant_005 e terminat pe: straturile de migrare (toate 9), FRONT D (declaratii D112/D101/D205/Bilant),
FRONT E (editare salariat). Continua cu CLUSTERELE RAMASE de mai jos (metoda Regula 13+14: captura PRIVITA +
axe/mobil pe fiecare ecran atins, REPARAND, gard RED-probat per defect; DS inainte de cod UI; versioneaza_assets
--scrie dupa editare static/js INAINTE de commit; commit pe iconta_nou = poarta ~9min + post-commit publica+restart).
Probe Playwright: helper frontend_test/w_auth (tenant_005 id=4840); scripturi+CSV in ~/probe_t005 (server).

## CLUSTERE RAMASE (in ordine sugerata)
- **BACKLOG DIACRITICE GENERATOARE DECLARATII (mare, ~330 mesaje, ~50 fisiere)** — mesajele de blocaj/avertisment
  ale generatoarelor (d100/d101/d112/d300/d301/d390/d394/d406/d107/d177/d207/bilant_api/declaratii_api + set extins
  d104-d710) sunt fara diacritice (raise/er.append/avertisment). d205 curatat integral (17 mesaje) ca exemplar +
  gard `test_generatoare_declaratii_cu_diacritice` cu lista `_GEN_DECLARATII` care CRESTE pe masura ce se curata
  cate un fisier. Metoda: adaugi fisierul in _GEN_DECLARATII, rulezi scan (~/probe_t005/scan_decl.py il enumera),
  diacriticizezi mesajele flagate (substring-uri unice per fisier), verifici green, RED-probat. Sweep exhaustiv in
  transcript. Atentie: unele mesaje scapa si nume de camp (ex. d112 data_angajare, cont_imobilizare) - Regula 14 pct.4.
- **CLUSTER A11Y (pe toate ecranele)** — axe da 14-15 noduri color-contrast (serious), ~11-17 tinte <44px, 2 info
  livrata EXCLUSIV prin `title` (pierduta pe touch). Pre-existent APP-WIDE (CSS + componenta comuna .vf-opt/.mig-*).
- **Field-level error marking** — erorile de formular (ex. Vector) NU marcheaza campul vinovat cu contur (mesajul il
  numeste). Pattern app-wide (Regula 14 pct.4).

## FOUR-WAY (de confirmat de urmatoarea tura)
HEAD = origin/main = backup/lant-2026-08-17 (remote) = e651da0. Comituri ultima tura: 58fd46e (diacritice import),
368325e (plan conturi 422), b5a066b (registre 6+7), e651da0 (Front D+E). Poarta verde pe fiecare. RUNNING confirmat
BEHAVIORAL: formularul "Corecteaza datele" pre-completeaza CNP/nume/data angajare/norma si valideaza CNP (captura).

## LIVRAT (fronturi D + E, e651da0)
FRONT D (declaratii): D112 scutire constructii VERIFICAT LA SURSA = NU e defect (art.60 pct.5 + art.60^1 ABROGATE
01-01-2025 OUG 156/2024 pct.7-8 art.LXIV, MO 1334/31.12.2024; temei adaugat salarizare.py nivel MO). D101 genereaza+
DUK ok. D205 blocheaza corect pe "fara beneficiar" - 17 mesaje diacriticizate + gard. Bilant S1005 formular corect.
d301/d390 dezactivate corect cu temei.
FRONT E (editare salariat): buton "Corecteaza datele" in ecranSalariati (firme.js) - editeaza nume/prenume/CNP/
data_angajare/norma (backendul le accepta deja via SalariatEdit+_CAMPURI_API; UI-ul nu le cabla - MEMORY §13). CNP
validat client-side. stat_plata expune cnp+tip_norma. Gard test_front_e_editare_identitate (contract+clamp UI).
