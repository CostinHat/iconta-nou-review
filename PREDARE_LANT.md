Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — P8: afirmatiile sunt obiecte, in TOATA aplicatia (tura 21–22.08)

## STAREA LA PREDARE

`HEAD = origin/main = backup/lant-2026-08-22 = RUNNING`. Poarta verde, verificator TOTAL 0.

**Cifra campaniei: 120 afirmatii netipate -> 24, din care 7 declarate ca exceptii -> DATORIE REALA 17.**
`control_incrucisat` a ajuns la ZERO si a iesit din tabel.

Cifra care conteaza e `registru_exceptii.datorie_reala()`, nu numarul brut: **aia poate ajunge la zero**.

## CE E CONSTRUIT SI PAZIT

- `core/afirmatii.py` — SAPTE feluri (cele cinci + `verificare_rupta` + `neconformitate`).
  `fapt` are DOMENIU ALTERNATIV: `an`+`luna` SAU `unde`, unul din doua obligatoriu; **fara niciunul e
  interzis**, cu test propriu.
- `core/unde.py` — referinta STRUCTURATA (subclasa de `str`, ca `common.Temei`), nomenclator INCHIS de
  14 feluri de referent. Se randeaza ca text, deci niciun randor nu s-a atins.
- `core/migrare_api.REGULI` + `respinge()` — nomenclator INCHIS de 24 de coduri de respingere la
  import, cu forma (lipsa / invalid / duplicat / incoerent / esec). Constructor unic.
- `core/registru_exceptii.py` — 7 exceptii declarate, cu trei zavoare (nu creste · fiecare intrare e
  VIE · motiv din set INCHIS de patru ratiuni).
- Sase garzi noi (vezi TESTE.md), fiecare RED-probata.

## FRONTURI DESCHISE — de unde se reia

### 1. Cele 17 afirmatii netipate reale
`./venv/bin/python -c "from core import scan_afirmatii as s, registru_exceptii as r; inv={(x[0],x[2]) for x in s.netipate_in_scop()}; print(r.datorie_reala(inv))"`
Sunt in 13 fisiere, majoritatea cate una. Nu mai exista familii — de-acum e munca de unul-cate-unul,
si fiecare cere o judecata: e o afirmatie despre datele firmei, sau e altceva?
**Regula, invatata scump:** daca raspunsul e „altceva", NU se largeste scanul si NU se adauga in
registru fara sa incapa intr-una din cele patru ratiuni. Se REPARA.

### 2. Ecranul statului de plata — STOP DECLARAT, nemiscat
Statul de plata se emite si se ingheata cu amprenta; corectia e al doilea exemplar si se ANUNTA pe
hartie. Dar semnalul de contradictie si butoanele emite/corecteaza **NU sunt in interfata**.
Capabilitatea e ajunsa prin API: `POST /stat-plata/emite` · `GET /stat-plata/emis` ·
`POST /stat-plata/corectie` · `POST /stat-plata/motiv`.
Propunerea vizuala (cinci puncte, nemodificata) a fost data lui Costin in tura asta si asteapta.

### 3. Baza CM se calculeaza din RECALCUL, nu din statele EMISE
OUG 158/2005 art.10 al.4. Cat timp lunile nu se emit, e acelasi lucru; dupa ce se emit, sunt doua
raspunsuri la aceeasi intrebare — iar cel din recalcul poate contrazice fluturasii deja dati.
**DECIZIE CERUTA, nedata:** care e baza legala — ce s-a platit efectiv (emis), sau ce rezulta azi?

### 4. Sonda de default-uri: 25 de parametri, clichet nepus
`/tmp/sonda_default.py` (NECOMISA — traieste in /tmp, se pierde la repornire; de comis daca se
pastreaza). Masoara parametrii cu default `None` din modulele fiscale care n-au fost NICIODATA `None`
la niciun apel din suita: **25 din 78**. Clasa a produs trei defecte reale in doua zile.
E grea (~10 min, inveleste la import) — locul ei e langa scanul de constante, nu in pre-commit.
**Atentie:** prima ei forma a STRICAT un test (functia invelita returna sursa spionului la
`inspect.getsource`); reparat cu `functools.wraps`, dar o sonda care strica lumea pe care o masoara
nu masoara acea lume.

### 5. Garzi „dupa fix", neinchise (din tura precedenta, nemiscat)
P2 · P5 · #13 · octeti · P4 · P7 au garda scrisa DUPA reparatie, RED-probata cu mutatii alese de
mine. Nu sunt inchise. Ce le-ar inchide: falsificare INDEPENDENTA (mutatii generate sistematic) =
#2 din roadmap. Vezi tabelul din GARZI.md, 21.08.

## CE SA NU FACI

- **Nu largi scanul ca sa scada numarul.** S-a incercat o data in tura asta: a scos 16 din 32,
  jumatate din datorie, printre care o constatare adevarata. Exista acum
  `test_excluderea_nomenclatoarelor_ramane_tintita` care pica la urmatoarea largire.
- **Nu pune default `None` la un parametru pe care tipul il cere.** De trei ori in doua zile a produs
  o ramura care cade si pe care niciun test n-o atinge.
- **Nu scrie scripturi de conversie in heredoc.** De trei ori in tura asta ghilimelele s-au evaporat
  (`manual['operatiuni']` rupe parsarea). Se scrie FISIERUL (METODA §10.3).
