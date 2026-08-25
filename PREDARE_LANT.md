Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — inventarul traseelor și triajul celor 76 de interdicții (25.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-25** *(a doua oară în aceeași zi — s-au închis două restanțe și
  s-au luat patru decizii, deci tot ce scria la „fronturi deschise" se schimbase)*
- **pe commit**: `5ee504c`
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire, nu la câteva zile.** Regula e
  scrisă aici fiindcă a fost încălcată de două ori. Prima dată (22.08) versiunea veche conținea **trei
  afirmații false**. A doua oară (24→25.08) n-a fost rescrisă deloc: a rămas **38 de commituri în
  urmă**, la un prag care sună la 10, iar tot ce scria la „fronturi deschise" se rezolvase între timp.
  *Un PREDARE_LANȚ care instruiește sesiunea nouă să-l citească primul și e vechi de 38 de commituri
  e mai rău decât unul absent: cine îl citește n-are cum să știe care rând mai e adevărat.*
- **gardat**: `scripts/githooks/pre-commit` **avertizează** când `HEAD` e cu mai mult de **10**
  commituri mai nou decât ultimul care a atins fișierul ăsta, iar `core/test_predare_proaspata.py` nu
  lasă avertismentul să dispară tăcut. **Avertizează, nu blochează** — un blocaj pe fiecare commit ar
  face din predare un impozit pe reparațiile mici. *Avertismentul a sunat corect timp de două zile și
  n-a fost ascultat; asta e o limită a avertismentului, nu a hook-ului.*

## STAREA LA PREDARE

Poartă verde: pytest (suita întreagă, prin hook) · ruff OK · verificator **TOTAL 0** · site 200 ·
four-way HEAD = `origin/main` = ramura de backup = procesul viu. *(Cifra de teste se reverifică
rulând poarta, nu se crede pe cuvânt — de-aia nu e scrisă aici.)* Rămân artefacte **neurmărite** în
`frontend_test/` din rulările vizuale; nu sunt modificări.

**Unde suntem**: **E1, faza 1**. Se lucrează **triajul pe cele 76 de interdicții** din
`CONFORMITATE.md`. **Cifrele nu se scriu aici** — se derivă cu `scripts/raport_b.py`, care e sursa
pentru secțiunea B a fiecărui raport. La 25.08: MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 ·
NEÎNCEPUTE 38; restanțe deschise **35** (E1: **12**), ultima **R48**.

## CE S-A CONSTRUIT ÎN ULTIMELE DOUĂ TURE

- **`TRASEE.md`, al patrulea document** — ce parcurge un document de la intrare la ieșire. Părțile
  IX–X l-au completat din cod; **Partea XI** îi dă un **inventar calculat**.
- **`scripts/scan_trasee.py` + `core/test_trasee.py`** — inventarul celor **35 de trasee**, acoperirea
  celor **400 de rute** (orfane: **0**), clasificarea mecanică (**MECANIC 27 · PARȚIAL 3 · MANUAL 5**,
  clichet), și **care firmă poate exercita care traseu**. **Partea XII din `TRASEE.md` le SCRIE pe
  toate 35 — generat cu `--md`, nu de mână**, iar garda compară blocul din document cu ce produce
  instrumentul: doc și cod nu pot diverge tăcut. **Blocul nu se editează cu mâna** — se corectează
  inventarul și se regenerează.
- **R41 — ÎNCHISĂ, amândouă părțile.** Partea I: verdictul oficial se **păstrează** (rezultat ·
  moment · versiunea validatorului · amprenta XML-ului), iar aprobarea și depunerea se refuză fără
  verdict proaspăt. **Partea a II-a (25.08): ecranul.** „De depus" conține doar ce e gata; restul stă
  în „Generate, nevalidate", care spune ce lipsește și pe unde se iese; eticheta e derivată, cu patru
  stări; trecerea peste refuz cere motiv scris. **Și cardul** de pe tabloul cabinetului, care spunea
  *„3 declarații de depus"* despre trei pe care serverul le refuză.
- **Cele patru decizii ale lui Costin (25.08)** — R30 (MĂSURATĂ ȘI ACCEPTATĂ, reluare la grupul 4) ·
  R42 (criteriul: ce iese către o autoritate sau către un om, plus perioada — **14 rute** trecute pe
  `admin_firma`) · R45 (ce se păstrează: artefactul · momentul · autorul · amprenta · numărul
  exemplarului, plus verdictul la declarații) · și **`TRASEE_VERIFICARI.md`**, al cincilea document.
- **`TRASEE_VERIFICARI.md`** — **singurul document care NU se generează.** Scheletul o dată
  (`scripts/scan_trasee.py --verificari`); conținutul îl scrie Costin. **187 de locuri**, câte unul
  per pas care schimbă ceva. **Nu se regenerează peste el** — ar șterge tot ce s-a scris.
- **Cele trei decizii din Partea VII, luate** — roluri, margini netestabile, precondiții. Sunt în
  `DECIZII.md` 25.08, iar consecințele lor sunt R42, R43, R48.
- **Cele două mixturi, desfăcute** — factura n-are 4 ieșiri, are **20 de consumatori**; nota n-are 4
  registre, are **21**. Corectate în locul lor, în Părțile II și V.

## CIFRE INVALIDATE — nu se corectează, se RE-MĂSOARĂ

*Regula: o cifră ai cărei termeni nu se mai pot reconstitui se **invalidează**, nu se corectează.*

| cifra | unde apărea | de ce e invalidată |
|---|---|---|
| **131** (interdicția 1, valori fiscale în afara registrului) | predarea din 22.08 | termenii ei au fost recalculați pe un domeniu lărgit de trei ori. **INVALIDATĂ 23.08.2026.** Clichetul viu, care se poate crede, e cel din `core/test_constante_nesursate.py` |
| **„25 de trasee"** | comanda din 24 și 25.08 | nu exista instrument care să le numere. Cifra care se poate reface e **35**, din `scripts/scan_trasee.py`. Nici „9" nu era greșit — era numărul din Partea VI, alt lucru |
| `STALE_BAZA_BASELINE = 14` | `core/test_agenda.py` | măsurată pe graful conflat |

**Restul cifrelor confruntării se citesc din `CONFORMITATE.md`**, secțiune cu secțiune — fiecare
poartă `măsurat la` și `pe commit`, iar o gardă cade dacă îmbătrânesc tăcut.

## FRONTURI DESCHISE, în ordine

1. **`TRASEE_VERIFICARI.md` — îl completează Costin.** 187 de locuri goale. Până se scriu, inventarul
   de trasee e o **hartă a codului**, nu o listă de verificare. E cel mai mare lucru rămas, și nu e
   muncă de-a mea.
2. **R49 — DECIZIE, îl așteaptă pe Costin.** Avertismentul de prăpastie al salariului minim,
   desprins din R30 fiindcă R30 avea două condiții de închidere. (a) nu se întoarce · (b) se întoarce
   fără cifre · (c) cu cifre, calculate cu toate elementele. **Nu se începe fără decizie.**
3. **R42 — cele 134 rămase.** Criteriul e luat și aplicat pe clasa numită (14 rute). Restul de **134**
   de rute care schimbă date și nu verifică niciun rol se triază pe același criteriu, iar cifra devine
   clichet în `core/test_trasee.py`.
4. **R45 — de construit.** Decizia e scrisă (cele cinci câmpuri). Patru artefacte o așteaptă:
   situațiile financiare · fișierul de plată a salariilor · exportul contabil · auditul de preluare.
5. **R44 — un cuvânt, apoi se închide.** Refuzul e construit; rămâne ce se face cu rândul orfan care
   există (id 2020, `tenant_id` 13245): se șterge, sau se releagă de `tenant_017`, firma din payload.
6. **Pragul 3 din triaj** — amânat de nouă ture, cea mai mare datorie rămasă: îngustarea
   Registrului-inventar la partidă dublă, registrul de evidență fiscală pe partidă simplă (calculul
   există în `rip_api` + `d212_engine`), apoi deductibilitatea per operațiune.
7. **R43, R46, R47, R48** — deschise pe 25.08 din inventarul traseelor. Vezi `CONFORMITATE.md`.
8. **R8** (cele trei egalități stricte) și **R9** (ecranul statului de plată, STOP nemișcat) —
   deschise de peste 80 de commituri fiecare.
9. **Tensiunea P8 ↔ interdicția 16, NEREZOLVATĂ.** P8: *„arbitrul decide"*. Interdicția 16: *„nu
   deriva nomenclatorul dintr-o sursă secundară"*. `d390.TIPURI/TARI_UE`, `d301.VALUTE`,
   `d394.TIPURI` au ales **conștient** validatorul, cu probă scrisă. Planul nu spune care câștigă.
   **Decizie cerută lui Costin** — nu e aceeași cu R49.

## CE TREBUIE ȘTIUT DESPRE DATE, ÎNAINTE DE ORICE MĂSURĂTOARE

Măsurat 25.08, pe toate cele 17 firme:

- **evidența e concentrată în două firme** — `tenant_013` are rânduri în 26 de tabele, `tenant_003` în
  14; patru firme au **exact două** (planul de conturi și profilul);
- **41 de facturi · 34 de note · 24 de salariați · 2 state de plată · 55 de declarații depuse ·
  3 elemente în coadă · 0 pontaje · 0 operațiuni de partidă simplă · 0 NIR-uri**;
- **12 conturi în 7 cabinete**, din care **un singur `angajat`** — fără nicio firmă atribuită și fără
  niciun drept fin. **Patru-ochi nu se poate exercita azi pe nicio firmă**, și de-aia nu se inventează
  scenarii de test pe cabinete care nu există;
- **`public.spv_token` = 0** și **`reges_chei` = 0** — deci e-Factura, e-Transport și REGES se opresc
  la pasul „token", nu la marginea ANAF.

## CE SĂ NU FACI

- **Nu porni de la un nume primit în comandă fără să-l cauți la sursă.** Instanțele se adună: în
  ultimele ture, comenzi succesive au numit `estimare_impozit`, `_recalc()`, „ecranul POS", „cele 12
  constante", „3750 în JS", „25 de trasee", „jurnalul de vânzări" — **majoritatea nu existau**. De
  fiecare dată căutarea a scos altceva, real. Caută **eticheta pe care o vede omul**, nu doar
  identificatorul.
- **Nu ghici numele unei tabele.** Pe 25.08 o măsurătoare a raportat zece tabele ca „absente pe toate
  cele 17 firme"; **nouă existau** — trei partajate în `public` cu `tenant_id`, șase sub alt nume
  (`factura_linii`, `state_plata`, `perioada_confirmata`, `clienti`+`furnizori`,
  `notificari_scadenta`, `contracte_sabloane`). Lista reală se regenerează din bază:
  `scripts/scan_trasee.py --tabele`.
- **Nu lega o rută de un modul după aliasul de la nivel de fișier.** Multe rute își importă modulul
  **în corp** (`from core import stocuri_api as _s`), iar `_s` e refolosit în zeci de locuri. Prima
  formă a scanului de trasee atribuia ruta de NIR modulului `salarizare`. **O atribuire falsă e mai
  rea decât o absență** — trece verde.
- **Nu declara o clasă golită pe un singur limbaj.** `METODA` §17. R26 a fost măsurat corect prin AST
  pe Python și a fost **fals despre aplicație**.
- **Nu recicla un nume într-un fișier de gărzi.** Un `_JS` definit peste altul a mutat tăcut domeniul
  a două gărzi vechi.
- **Nu construi o gardă care verifică faptul că un temei DETERMINĂ o comparație.** Nu se poate.
- **Nu cere o cifră pentru interdicția 22.** N-are numitor.
- **Nu lărgi un scan ca să scadă un număr.** S-a încercat de două ori.
- **Nu edita scripturi de conversie din shell.** Escapările se rup pe ghilimelele românești și pe
  `\u`. Se scrie **fișierul** și se trimite octet cu octet (`METODA` §10.3).
- **Nu rula un RED-proof cu `git checkout`** când arborele are muncă necomisă.
- **Un RED-proof pe un REFUZ scrie.** Instanța: mutația care a ținut garda lui R44 pe `if False` a
  făcut ca un test care pe cod sănătos **nu scrie nimic** să insereze două rânduri orfane într-o
  tabelă partajată. Prinse de clichet și șterse — dar verificarea nu e „testul a picat", ci **„testul
  a picat ȘI n-a rămas nimic în urmă"**.
- **Nu regenera `TRASEE_VERIFICARI.md`.** E singurul document scris de om. `--verificari` produce
  scheletul; rulat peste fișierul completat, îl golește.
- **Nu curăța `__pycache__` doar la sfârșit.** Două mutații de aceeași dimensiune în aceeași secundă
  reciclează bytecode-ul și proba devine falsă.
