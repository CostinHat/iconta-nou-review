Marca de referință: infra vizuală 17.08.2026 (intrare 66f50cd). Citește CLAUDE.md §2.2 (structura raportului) și §2.3 (lanț, siguranță, limbă — ACUM cu pct.11 „poarta verde vizuală") și ARHITECT.md „FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, înainte de a începe. Stare: infrastructură de testare vizuală (axe/mobil/baseline) LIVRATĂ ca infra permanentă; NU s-a reparat niciun ecran (comanda a cerut măsurare, nu reparație). Front deschis rămas: C3 (schema-migration plan_conturi.sursa).

# PREDARE LANT — infrastructură de testare vizuală LIVRATĂ (axe / mobil / baseline)

## FOUR-WAY (ultima execuție, 17.08.2026)
HEAD = origin/main = backup/lant-2026-08-17 = RUNNING = commitul de infră vizuală al acestei ture
(`git log -1 --oneline` pe server; SHA exact confirmat FOUR-WAY în raportul turei §11).

## LIVRAT ACEASTĂ TURĂ — infra vizuală permanentă în frontend_test/vizual/ (NU s-a reparat niciun ecran; doar măsurat)
Trei unelte pe pagina randată (Playwright autentificat via w_auth), probate pe 5 ecrane
(nav_ecrane.ECRANE: import_mijloace_fixe, vector_fiscal, plan_conturi, stat_plata, declaratii):
- **axe_scan.py** (axe-core 4.10.2 vandorizat offline) — pe ecran: 1 regulă = `color-contrast`
  (12–15 noduri, `serious`); 0 fără-etichetă; 0 title-only strict; **1–3 title-extra** (motivul
  blocării livrat DOAR prin `title`: REGES/IBAN pe stat_plata). Contrastul e concentrat în chrome-ul
  comun (bara sus alb-pe-albastru 3.44, sub-bara edu 4.16) + grila de cabinet din fundal.
- **mobil_scan.py** (Pixel 5, touch, fără hover) — overflow-x **0** pe toate; CSS `:hover` doar
  decorativ (0 conținut ascuns); `title` pierdut pe touch 2–5/ecran (info unică = motive blocare);
  ținte de atingere <44px **11–40** (icoanele barei 26–36px înălțime; 40 pe stat_plata, tabel dens).
- **baseline_scan.py** — 5 baseline STABILE (self-diff 0%), `--compare` identic 0% (determinist și
  între rulări), detecție probată = 25,28% pe cross-screen. baseline/*.png versionate.

Guvernanță înscrisă (cele trei locuri care supraviețuiesc /clear):
- CLAUDE.md §2.3 **pct.11** — poarta verde vizuală (cele trei rulate pe ecranele atinse înainte de poartă).
- TESTE.md — secțiunea „Infrastructură de testare vizuală" (inventar: unealtă/fișier/acoperire/ieșire).
- MEMORY.md **Regula 14** — la orice ecran atins: axe-core + o deschidere pe profil telefon, rezultatul în raport §3.
- Gardă `core/test_infra_vizuala.py` (4 passed): infra nu poate dispărea tăcut (Regula 6).

**Verdict zgomot:** niciuna nu dă „sute pe ecran" → toate pot fi obligatorii. Singurul volum notabil =
ținte <44px pe tabele dense (40 pe stat_plata) → raportate ca CIFRĂ + top-N, nu enumerate integral.

**DECIZIE DE PRODUS DESCHISĂ (conform comenzii — nu s-a reparat):** ce se repară întâi din constatări.
Costin dă ordinea (a cerut cifrele înainte de a decide).

## FRONT DESCHIS — C3 (rămas din tura dd25c3e, NEATINS acum)
Badge stare per strat în `meniuMigrarePerFirma` (migrare.js:1435) + flag `plan_conturi.sursa`
('standard'/'balanta'/'manual'). Decizia lui Costin DATĂ: adaugi flagul. Schimbare de schemă pe 28
tenanturi — `test_audit_schema` PICĂ dacă template diverge → template + migrare + rulare pe 28 scheme
ÎNTR-UN SINGUR cluster. Scop complet (6 puncte: schema/migrare/import/UI/gărzi/probă) în versiunea
acestui fișier la commit dd25c3e (`git show dd25c3e:PREDARE_LANT.md`).

## BACKLOG (din PREDARE dd25c3e, tot deschis)
Q9 coerență blocantă parteneri · Q18 XSD auto-select · Q7 mesaj confirmare · Q8 badge per-strat
(blocat: semnal prezență plan_conturi = flagul C3) · Q12 avertisment pe rând accesibil · Q14 CSV model x5.

## CE URMEAZĂ (decizie de produs — Costin dă ordinea)
1. Ordinea reparațiilor din constatările vizuale (recomandare: contrast chrome comun întâi — cleară
   majoritatea nodurilor pe toate ecranele dintr-o dată; apoi title-extra „motiv blocare"; apoi ținte <44px).
2. C3 schema-migration (cluster focalizat, decizia dată).
