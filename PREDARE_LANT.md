Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — 193 din 193, și prima exercitare pe date (26.08.2026, seara)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-26** (seara), *rescriere COMPLETĂ, nu petic*
- **pe commit**: `ada9d23`
- **de ce completă**: regula stă din 26.08 dimineața și e respectată. Versiunea de dinainte era
  scrisă la `7e07265`, adică **cu 12 commituri în urmă**, și afirma lucruri care nu mai sunt
  adevărate: *„150 din 192 de locuri scrise, 42 goale"*, *„rămâne lotul 7"*, *„restanțe deschise
  36"*. Toate trei s-au schimbat. **Un document care se contrazice nu e „parțial vechi": cine îl
  citește nu poate ști care rând mai e adevărat.**
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire.** Azi avertismentul porții a
  sunat la `ada9d23` și **a fost executat în aceeași tură, la cererea lui Costin** — nu doar
  raportat. Diferența contează: în zilele dinainte a fost raportat corect de trei ori la rând și
  n-a fost executat niciodată. *Un avertisment care se raportează și nu se execută e o linie de
  raport, nu o gardă.*
- **gardat**: `scripts/githooks/pre-commit` **avertizează** peste 10 commituri de la ultima
  atingere; `core/test_predare_proaspata.py` nu lasă avertismentul să dispară tăcut. Avertizează,
  nu blochează.

---

## STAREA LA PREDARE

Poartă verde la `ada9d23`: **3293 teste** ✓ · 10 skip · 14 xfail · ruff OK · verificator
**TOTAL 0** · site 200 · four-way `HEAD = origin/main = backup/lant-2026-08-26 = ada9d23`, proces
viu pornit **după** commit. *(Cifra de teste se reverifică rulând poarta, nu se crede pe cuvânt.)*

Rămân **neurmărite**: cele șapte `LOT_*_VERIFICARI.md`, `corectii_lot_1.md`, și artefacte din
rulările vizuale în `frontend_test/`. Nu sunt modificări necomise.

**Cifrele nu se scriu aici** — se derivă cu `scripts/raport_b.py`. Fotografia de la `ada9d23`:
interdicții MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 · NEÎNCEPUTE 38; restanțe deschise **43**
(E1: **20**).

---

## PASUL CURENT ȘI-A ATINS CRITERIUL — și asta schimbă ce urmează

**`TRASEE_VERIFICARI.md`: 193 din 193 de locuri scrise, 0 goale.** Loturile 6 și 7 au fost scrise
de Costin și **mutate** în fișierul canonic; loturile rămân netracked ca istoric, nu se șterg.

Cifra e **193, nu 192**: o rută nouă (`POST /public/confirma-email`, R62) a adăugat un pas.

**Ce urmează NU mai e scriere.** E ce scrie chiar `TRASEE.md` la început: *un traseu se parcurge,
nu se citește.* Din cele 193 de verificări, **niciuna n-a fost rulată pe date** — cu o singură
excepție, care e cea mai importantă lecție a zilei (mai jos).

---

## TREI LUCRURI CARE SCHIMBĂ FELUL ÎN CARE LUCREZI MÂINE

### 1. Prima exercitare pe date a găsit un prag 1 pe cod gardat și verde

Costin a parcurs pe o firmă de test cei opt pași ai probei R62. A găsit un defect pe care
**nicio gardă nu-l vedea**: `POST /public/confirma-email` era scrisă, gardată, trecea toată suita
— și **nimic n-o chema**. Linkul din email ducea în SPA cu fragmentul `#email-nou=`, pe care
`app.js` nu-l cunoștea. Clientul credea că și-a schimbat adresa; nu se schimbase nimic.

Gărzile verificau ce face ruta **dacă** e chemată. Niciuna nu întreba **dacă** e chemată.

**Regula care iese, și e a treia formă a aceleiași reguli:** *ruta și calea ei de apelare intră
împreună* — ca *coloana și calea ei de scriere*. Consemnat în **R70**, cu măsurătoare: **5 din
193** de rute n-au apelant în `static/`, una declarată intenționat, patru nu.

### 2. Forma nouă a zilei: drum de citire fără drum de scriere

Găsită de **trei** ori, în aceeași zi, în trei locuri diferite:

| coloana | ce citea | ce s-a făcut |
|---|---|---|
| `tenants.principal_client_id` | patru SELECT-uri; citirea avea *fallback*, scrierile nu | **scoasă** (R62) — ecranul spunea unui om real „ești titularul", rutele răspundeau 403 |
| `firma_profil.patron_email` | avea **precedență** la trimiterea pachetului | **scoasă** (R65) — `coalesce` o ascundea azi și ar fi activat-o mâine |
| `firma_profil.patron_nume` | se **tipărește** pe adeverințe și contracte | **reparată** (R66) — a primit câmp în *Date firmă*, apoi documentele refuză fără el |

Prima e vizibilă (produce un refuz), a doua e tăcută (produce comportamentul corect), a treia lasă
un gol pe hârtie. **Aceeași formă, trei semne diferite.**

### 3. Calea de scriere nu e un fapt textual — de patru ori într-o zi

Fiecare instrument construit ca scan pe text a greșit, în ambele direcții:

- `_siruri` citea **docstringurile** ca SQL → tabela inventată `oarb`;
- instrumentul pentru „coloane citite și scrise de nimic" a dat **17**, iar calibrarea pe un caz
  cunoscut rezolvat (R51) l-a infirmat → cifra **nu s-a publicat**;
- „teste cuplate la firme reale": **18 → 6 → 4**, iar cifra reală, obținută **citind**, e **3** —
  și garda permanentă din 29.07 le ratează pe toate trei, raportând zero;
- „rute fără apelant": **5**, declarat ca **plafon superior**.

**Consecința practică:** în codul ăsta calea de scriere sau de apelare se asamblează la rulare
(`UPDATE … SET " + ", ".join(seturi)`, liste de coloane generate, căi compuse). *Cine scrie
coloana* și *cine cheamă ruta* nu se pot răspunde citind textul. **Un scan pe text pe clasele
astea se calibrează pe un caz cunoscut rezolvat înainte de a publica orice cifră.**

---

## CE S-A ÎNCHIS ȘI CE S-A DESCHIS AZI

**26 de commituri.** Detaliul e în `CONFORMITATE.md`, cu `măsurat la` și `pe commit`.

**Închise:** **R60** (instrumentul atribuia rutei modulul importat de altcineva — 14 rute cu
atribuire falsă) · **R61** (raportul Z tastat nu avea verificare de duplicat; cheia e
`Z-{NUI}-{nr}`, nu data) · **R62** (portalul muta identitatea fără confirmare — **prag 1**) ·
**R65** (`patron_email` cu precedență și fără scriitor) · **R46** (schimbarea de regim peste o
perioadă închisă — **prima reaprindere mecanică reală** de când există mecanismul: s-a aprins pe
un fișier atins pentru altceva, și s-a închis în aceeași tură).

**Deschise:** **R63** (două adrese pentru aceeași persoană — decis: rămân două, se numesc diferit)
· **R64** (contabilitatea și stocul, două evidențe disjuncte — decis: documentele operaționale
produc mișcarea; **nefăcut**, cere `articol_id` pe `nir_linii` întâi) · **R66** (aplicat, rămâne
deschis pe restul clasei) · **R67** (suita rulează pe baza de **producție**; decis: utilizator de
test restrâns — **nu se poate face de mine**, cere `postgres`) · **R68** (bază de test separată,
după ce cele 3 teste se decuplează) · **R69** (declarație depusă pe un regim schimbat între timp —
**6 firme, 55 de declarații**, mai mare decât poarta care o precede) · **R70**, **R71**.

---

## CE BLOCHEAZĂ, ÎN ORDINE

1. **R67 cere `postgres`.** `iconta_user` n-are CREATEROLE. Comanda e scrisă în raportul turei;
   fără ea, bariera dintre teste și firmele reale rămâne o convenție.
2. **R64 cere o decizie de construcție**: `nir_linii` are `denumire` ca text liber, fără
   `articol_id`. Coloana și calea ei intră împreună — de aceea nu s-a adăugat singură.
3. **Cele două firme `PROBA PORTAL SRL`** rămân în bază ca dovadă până se confirmă reparația
   defectului de prag 1. Se șterg amândouă după.
4. **Reparația de la R70 nu e confirmată.** Am reparat-o; **n-o pot proba** — cere apăsarea unui
   link dintr-un email la care n-am acces. Se probează de Costin, iar eu verific în bază
   (`schimbari_email.confirmat_la`, `users.email`, `urme_portal`).

---

## REGULI EXERCITATE AZI, CU INSTANȚA LOR

- **Consemnează întâi, decide după.** Toate cele nouă restanțe noi au fost scrise înainte de a fi
  decise; niciuna n-a așteptat o decizie ca să existe.
- **O măsurătoare se calibrează înainte de a fi publicată.** Cifra 17 a murit **înainte** de a
  intra în registru, nu după. E prima dată.
- **Clichetul 50 respinge și gărzile proprii.** Două fișiere de gardă scrise azi au fost rescrise
  pe structură după ce scanul le-a numărat aserțiuni pe text. Forma acceptată: operator de mulțime
  (`>= {…}`), nu `in`.
- **Un refuz numește lucrul și locul.** `UNDE_ADMINISTRATOR`, `UNDE_PERIOADE` — valori cu nume, ca
  gardul să asertea că mesajul e **compus** din ele, nu că fraza conține un șir.
- **Poarta a respins de trei ori azi** (a 23-a, 24-a, 25-a din jurnal), de fiecare dată pe ceva
  produs de propria reparație: import nefolosit, reaprindere neexecutată, blocul din `TRASEE.md`
  desincronizat, fixtură care numea o tabelă reală.
- **Mesajele de commit se trimit ca FIȘIER.** Un heredoc neghilimelat prin `ssh` a executat
  backtick-urile și a golit un cuvânt din `892b337`. Regula era notată; s-a sărit la un retuș, nu
  la actul principal.

---

## CIFRE INVALIDATE — se păstrează, nu se șterg

*O cifră ai cărei termeni nu se mai pot reconstitui se **INVALIDEAZĂ**, nu se corectează.*
Tabelul se moștenește din predările dinainte: o cifră ștearsă se poate reîntoarce.

| cifra | unde apărea | de ce e INVALIDATĂ |
|---|---|---|
| **131** (valori fiscale în afara registrului) | predarea din 22.08 | termenii recalculați pe domeniu lărgit de trei ori. Clichetul viu e în `core/test_constante_nesursate.py` |
| **„25 de trasee”** | comenzile din 24 si 25.08 | nu exista instrument care să le numere. Cifra care se poate reface e **35** |
| **„129 de rute schimbă date fără rol”** | predarea din 26.08 dimineață | raza nu se mai poate reconstitui; re-măsurat pe **metodă + cale** dă alt domeniu, nu alt progres |
| **„R55: șapte rute”** | comanda din 26.08 | proxy pe **numele grupului**. Real: **40** de rute în clasă, din care 36 scriu `ciorna` și **3** scriu `validata` direct |
| **17** (coloane citite și scrise de nimic) | instrumentul construit **26.08 seara** | **INVALIDATĂ înainte de a fi publicată** — calibrarea pe un caz cunoscut rezolvat (R51) a infirmat-o. Cifra reală, obținută citind, e **3** |
| **18** (teste cuplate la firme reale) | raportul din 26.08 | grep naiv; numărările succesive au dat 18, 6, 4, iar cifra reală, prin citire, e **3** |

## CE NU E ADEVĂRAT DESPRE STAREA ASTA, ȘI SE SPUNE

- **Verde nu înseamnă exercitat.** 3293 de teste trec, și tot un defect de prag 1 a stat ascuns o
  zi întreagă pe cod gardat. Ce prinde suita e ce știe să întrebe.
- **Cele 193 de verificări sunt scrise, nu rulate.** Una singură a fost exercitată pe date (proba
  R62), și a găsit un defect. Rata nu se extrapolează dintr-un caz — dar nici nu se ignoră.
- **Trei observații din R71 sunt de așezare** (refuz sub câmpul greșit, fereastră sub marginea
  ecranului, buton nereseta) — clasa e declarată **nemăsurabilă** în CLAUDE.md, iar verificatorul
  nu ajunge acolo. Se repară pe judecată, se confirmă pe ochi.
