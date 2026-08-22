Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — confruntarea cu planul normativ, partea de registru (tura 22.08)

## STAREA LA PREDARE

`HEAD = origin/main = backup/lant-2026-08-22 = RUNNING`. Poarta verde, verificator TOTAL 0.

Doua fire in aceeasi tura:
1. **P8 (afirmatiile sunt obiecte)** - INCHEIAT ca faza: 120 netipate -> 6 datorie reala.
2. **P11 (interpretarea declarata)** - INCEPUT: obiectul si garzile exista, registrul are DOUA intrari.

## CE E CONSTRUIT SI PAZIT (P11)

- `core/interpretare.py` - obiectul. Variantele OBLIGATORII (minim doua). Dezacordul cu arbitrul se
  DERIVA, nu se tine intr-un camp. Nomenclator INCHIS de cinci forme de incertitudine.
- `core/registru_interpretari.py` - DOUA intrari, gasite prin masuratoare: `incadrat_la_minim` si
  `podea_part_time_minus_facilitate`.
- `core/test_comparatii_clasificate.py` - clichet 13 pe comparatii NECLASIFICATE.
- `ARHITECTURA_NORMATIV.md` - COMIS (era necomis) + categoria „Conventii de calcul" + sectiunea despre
  ce se poate masura.

## CIFRELE CONFRUNTARII (fara reparatii, cum s-a cerut)

| # | brut | real |
|---|---|---|
| 1 valoare fiscala in afara registrului | 131 | ~100 |
| 2 interogare fara data | 3 | 3 |
| 16 nomenclator din sursa secundara | 39 din 93 | 39 |
| 17a valoare re-declarata | 42 | ~34 |
| 17b formula in >= 2 module | 1 | 1 |
| 21 interpretare care apare ca lege | 15 | 2 (plafon inferior) |
| 22 | - | NEMASURABILA, declarat |
| 23 | 0 | 0, deja gardat |

## FRONTURI DESCHISE

### 1. Reparatiile de la registru (ordinea 1 din Partea VII)
Cea mai ieftina si cu cel mai mare efect: **#2, trei instante, o singura cauza** - defaultul
`la_data=None` din `common.cota`. Scos, interdictia 2 devine imposibila prin constructie.

Apoi **17b** - o singura formula (`sm - facilitate`) in trei module; urca in registru, categoria
„Formule".

Apoi **#1**, ~100 - munca mare, se face pe module.

### 2. Tensiunea P8 vs interdictia 16, NEREZOLVATA
P8: „arbitrul decide". Interdictia 16: „nu deriva nomenclatorul dintr-o sursa secundara".
`d390.TIPURI/TARI_UE`, `d301.VALUTE`, `d394.TIPURI` au ales CONSTIENT validatorul, cu proba scrisa.
Planul nu spune care castiga. **Decizie ceruta lui Costin.**

### 3. Codurile de boala - patru straturi, cu o contradictie REALA
Interfata (`flux_concediu.js`) ofera 16/17/51; validarea din `d112` cade pe `1..15` cand XSD-ul nu se
poate citi. Nu e doar re-declarare: straturile nu spun acelasi lucru.

### 4. Cele trei egalitati stricte re-deschise
`d223:159` („100% doar cu un singur asociat"), `d406:1338` si `:1367` (codul fiscal pentru cota zero).
Le-am numit zgomot la prima citire, pe linie. Pe context, merita a doua privire. Pana atunci, „2 reale"
la interdictia 21 e un PLAFON INFERIOR.

### 5. Restul de la P8: 6 afirmatii netipate reale
`control_fiscal_api` x3 (containere), `articole_import`, `rip_migrare`, `istoric` (container cu lista).

### 6. Ecranul statului de plata - STOP nemiscat
Semnalul de contradictie si butoanele emite/corecteaza nu sunt in interfata. Capabilitatea e ajunsa
prin API. Propunerea vizuala in cinci puncte asteapta.

### 7. Garzi „dupa fix", neinchise
Noua: P2 · P5 · #13 · octeti · P4 · P7 + `test_chei_duplicate` · `test_flag_constatare` +
re-ancorarile. Ce le-ar inchide: falsificare INDEPENDENTA (#2 din roadmap).

## CE SA NU FACI

- **Nu construi o garda care verifica ca un temei DETERMINA o comparatie.** Nu se poate; o garda care
  pretinde ca o face transforma o citire umana intr-un verde automat. Vezi capul lui
  `test_comparatii_clasificate.py`.
- **Nu cere o cifra pentru interdictia 22.** N-are numitor. Scrie in plan de ce.
- **Nu largi un scan ca sa scada un numar.** S-a incercat de doua ori in doua ture: o data a scos 16
  din 32 (jumatate din datorie), o data a dat 1167 din care 90% zgomot.
- **Nu edita scripturi de conversie din shell.** A patra oara azi cand escaparile s-au rupt. Se scrie
  FISIERUL (METODA §10.3).
- **Nu rula un RED-proof fara curatare de `__pycache__`.** Doua mutatii de aceeasi dimensiune in
  aceeasi secunda recicleaza bytecode-ul si proba devine falsa.
