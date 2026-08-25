Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — inventarul traseelor și triajul celor 76 de interdicții (25.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-25**
- **pe commit**: `3cb6c44` — starea de **intrare** a turei care a scris fișierul ăsta. Commitul care
  îl aduce e cel imediat următor, iar de la el se numără vechimea.
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
  clichet), și, cu `--db`, **care firmă poate exercita care traseu**.
- **R41 partea I** — verdictul oficial de validare se **păstrează** (rezultat · moment · versiunea
  validatorului · amprenta XML-ului), iar aprobarea și depunerea se refuză fără verdict proaspăt.
  **Partea II — ecranul — NU e făcută.** E a treia tură în care se amână.
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

1. **R41 partea a II-a — ECRANUL. Se face prima.** Serverul refuză deja depunerea fără verdict
   proaspăt, dar ecranul **încă numește „De depus"** o listă în care intră și ce nu e gata. Decizia e
   luată și scrisă (`DECIZII.md` 24.08): verdict afișat · blocare pe respins **sau lipsă** · trecere
   explicită și consemnată · două liste separate, iar cea de nevalidate spune **ce lipsește**.
2. **R30 — DECIZIE, îl așteaptă pe Costin. Cea mai veche.** Avertismentul despre prăpastia salariului
   minim a plecat odată cu estimarea scoasă prin R28. Se întoarce fără cifre, se mută la salvare, sau
   nu se întoarce? **Nu se începe fără decizie.**
3. **R42 — DECIZIE.** Care operațiuni cer `admin_firma`. **144** de rute care schimbă date nu verifică
   niciun rol; pe traseul notei contabile, **24 din 24**. A pune `admin_firma` peste tot ar bloca
   asistenții pe munca lor zilnică — de-aia e decizie, nu reparație.
4. **R45 — DECIZIE.** Se păstrează un artefact produs, și cu ce câmpuri? Patru instanțe ale aceleiași
   clase (situații financiare · fișierul de salarii · exportul contabil · auditul de preluare), plus
   R41 ca a cincea. O decizie, nu patru.
5. **Pragul 3 din triaj** — amânat de opt ture, și e cea mai mare datorie rămasă: îngustarea
   Registrului-inventar la partidă dublă, livrarea registrului de evidență fiscală pe partidă simplă
   (calculul există în `rip_api` + `d212_engine`), iar la sfârșit deductibilitatea per operațiune.
6. **R43, R44, R46, R47, R48** — deschise azi, din inventarul traseelor. Vezi `CONFORMITATE.md`.
7. **R8** (cele trei egalități stricte) și **R9** (ecranul statului de plată, STOP nemișcat) —
   deschise de peste 80 de commituri fiecare.
8. **Tensiunea P8 ↔ interdicția 16, NEREZOLVATĂ.** P8: *„arbitrul decide"*. Interdicția 16: *„nu
   deriva nomenclatorul dintr-o sursă secundară"*. `d390.TIPURI/TARI_UE`, `d301.VALUTE`,
   `d394.TIPURI` au ales **conștient** validatorul, cu probă scrisă. Planul nu spune care câștigă.
   **Decizie cerută lui Costin** — nu e aceeași cu R30.

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
- **Nu curăța `__pycache__` doar la sfârșit.** Două mutații de aceeași dimensiune în aceeași secundă
  reciclează bytecode-ul și proba devine falsă.
