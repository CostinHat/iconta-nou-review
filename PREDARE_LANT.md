Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANȚ — triajul celor 76 de interdicții (turele 23–24.08.2026)

## ANTET — cât de veche e predarea asta

- **ultima rescriere**: **2026-08-24**
- **pe commit**: `afb709e`
- **cine o rescrie și când**: **se rescrie ÎNAINTE de fiecare oprire, nu la câteva zile.** Regula e
  scrisă aici fiindcă a fost încălcată: versiunea dinainte era din **22.08** și conținea **trei
  afirmații false** — starea pe `backup/lant-2026-08-22`, cifra `131` (invalidată între timp) și un
  front deja rezolvat. *Un PREDARE_LANȚ care instruiește sesiunea nouă să-l citească primul și
  conține afirmații false e mai rău decât unul absent: cine îl citește n-are cum să știe care rând mai
  e adevărat.* (Costin, 24.08.2026.)
- **gardat**: `scripts/githooks/pre-commit` **avertizează** când `HEAD` e cu mai mult de **10**
  commituri mai nou decât ultimul care a atins fișierul ăsta, iar `core/test_predare_proaspata.py` nu
  lasă avertismentul să dispară tăcut. **Avertizează, nu blochează** — un blocaj pe fiecare commit ar
  face din predare un impozit pe reparațiile mici. Pragul de 10 e ales ca să sune ~o dată pe zi de
  lucru, nu la fiecare tură.

## STAREA LA PREDARE

`HEAD = origin/main = backup/lant-2026-08-24 = RUNNING = afb709e`. Poartă verde: **3008 passed**,
8 skipped, 14 xfailed · ruff OK · verificator **TOTAL 0** · site 200 · arbore curat (rămân artefacte
**neurmărite** în `frontend_test/`, din rulările vizuale — nu sunt modificări).

**Unde suntem**: E1, faza 1 **completă**; se lucrează **triajul pe cele 76 de interdicții** din
`CONFORMITATE.md`. Cifrele nu se scriu aici — se derivă cu `scripts/raport_b.py`, care e sursa pentru
secțiunea B a fiecărui raport. La 24.08: MĂSURATE 21 · PARȚIAL 16 · NEMĂSURABILE 1 · NEÎNCEPUTE 38;
restanțe deschise **21**, ultima **R32**.

## CE S-A CONSTRUIT ÎN CELE DOUĂ TURE

- **`core/test_valori_fiscale_js.py`** (9 teste) — fiecare cotă scrisă literal într-un **ecran** se
  confruntă cu `COTE` la data de azi. Când o cotă se schimbă în registru, testul devine roșu **și
  numește fișierul de ecran** rămas în urmă. RED-proof prin mutație. Vezi `METODA` §18.
- **`core/test_an_hardcodat.py`** (6 teste) — un **an scris într-o cerere** îngheață ecranul în trecut.
  Clichet **1**, ancorat pe fișier (`rip_ecran.js`), cu anti-stale.
- **`core/test_aritmetica_in_prezentare.py`, +4 teste** — calibrarea pe **nume neutre** ca **clichet**
  (2, ambele calendaristice, zero fiscale), plus o calibrare pe **propriul mod de eșec**: curățarea
  comentariilor trebuie să păstreze numerotarea liniilor.
- **`core/scan_valori_afisate.py`** — instrumentul care alimentează tabelul gardului de mai sus.
- **`METODA_VERIFICARE.md` §17 și §18** — o clasă golită se golește pe **toate limbajele** în care
  poate exista · la o schimbare de valoare fiscală, **JS-ul se caută explicit**.
- **Reparat**: R28 (ecranul de angajare nu mai estimează un net — vezi `ISTORIC.md` 24.08), plus cele
  șase din 23.08, toate în `ISTORIC.md`.

## CIFRE INVALIDATE — nu se corectează, se RE-MĂSOARĂ

*Regula: o cifră ai cărei termeni nu se mai pot reconstitui se **invalidează**, nu se corectează.
Tabelul complet e în `CONFORMITATE.md`; aici sunt cele care ar induce în eroare o sesiune nouă.*

| cifra | unde apărea | de ce e invalidată |
|---|---|---|
| **131** (interdicția 1, valori fiscale în afara registrului; „~100 reale") | **chiar în versiunea de 22.08 a acestui fișier** | termenii ei (`A+C+E−43`) au fost recalculați pe un domeniu **lărgit** de trei ori (`scan_constante`), deci descompunerea nu se mai poate reface. **INVALIDATĂ 23.08.2026.** Clichetul viu, care se poate crede, e cel din `core/test_constante_nesursate.py` |
| `STALE_BAZA_BASELINE = 14` | `core/test_agenda.py` | măsurată pe graful **conflat** (cheie pe nume simplu) |
| „2 reale" la interdicția 21 | vechea predare | **plafon inferior**, declarat ca atare |

**Restul tabelului din vechea predare nu se mai folosește.** Cifrele confruntării se citesc din
`CONFORMITATE.md`, secțiune cu secțiune — fiecare poartă `măsurat la` și `pe commit`, iar o gardă cade
dacă îmbătrânesc tăcut.

## FRONTURI DESCHISE, în ordine

1. **R29 — PRAG 1, singurul deschis. Se face primul.** Cota de TVA scrisă ca valoare implicită în
   **ecranul de NIR**, de trei ori (`firme.js:1649/1660/1738`); `:1738` o trimite **în corpul cererii**.
   R26 scosese aceleași valori implicite din **Python** și declarase clasa golită — ea trăia în
   JavaScript, și aceea rulează: refuzul pe care serverul îl învățase (`main.py:798`, *„fără valoare
   implicită"*) **nu se poate declanșa din ecranul acela**.
2. **R30 — DECIZIE, îl așteaptă pe Costin.** Avertismentul despre prăpastia salariului minim a plecat
   odată cu estimarea scoasă prin R28. Se întoarce fără cifre, se mută la salvare, sau nu se întoarce?
   **Nu se începe fără decizie.**
3. **Pragul 3 din triaj** — amânat șapte ture, și e cea mai mare datorie rămasă: îngustarea
   Registrului-inventar la partidă dublă, livrarea registrului de evidență fiscală pe partidă simplă
   (calculul există deja în `rip_api` + `d212_engine`), iar la sfârșit, deliberat, deductibilitatea
   per operațiune pentru impozitul pe profit.
4. **R31** — anul scris în cerere (`rip_ecran.js:142` cere `/rip/d212/2025`). Reparația URL-ului e
   mecanică (ecranul are deja `an` în stare); eticheta cere ca **serverul** să întoarcă anul și
   salariul minim al lui.
5. **R32** — trei facturi de test al căror antet își contrazice liniile (seria `COER`, din seeder).
   Contează fiindcă orice gard viitor care confruntă antetul cu liniile ar fi calibrat pe date false.
6. **Interdicția 2 — încă deschisă, și e cea mai ieftină.** `core/common.py:658`: `cota(nume,
   la_data=None, ...)` face `la_data = la_data or date.today()`. **Defaultul tăcut e tot acolo.** Scos,
   interdicția 2 devine imposibilă prin construcție. *Verificat 24.08 la sursă — nu preluat din vechea
   predare.*
7. **Codurile de boală, contradicție reală între straturi.** `core/d112.py:373` cade pe un interval
   **GHICIT** (`1..15`) când XSD-ul nu se poate citi, iar interfața oferă coduri în afara lui.
8. **R8** (cele trei egalități stricte, redeschise) și **R9** (ecranul statului de plată, STOP
   nemișcat) — deschise de peste 50 de commituri fiecare.
9. **Tensiunea P8 ↔ interdicția 16, NEREZOLVATĂ.** P8: *„arbitrul decide"*. Interdicția 16: *„nu
   deriva nomenclatorul dintr-o sursă secundară"*. `d390.TIPURI/TARI_UE`, `d301.VALUTE`, `d394.TIPURI`
   au ales **conștient** validatorul, cu probă scrisă. Planul nu spune care câștigă. **Decizie cerută
   lui Costin** — nu e aceeași cu R30.

## CE SĂ NU FACI

- **Nu porni de la un nume primit în comandă fără să-l cauți la sursă.** În ultimele cinci ture, comenzi
  succesive au numit `estimare_impozit`, `_recalc()`, `R28`–`R33`, „ecranul POS", „cele 12 constante",
  „5 formule", „3750 în JS" — **majoritatea nu existau**. De fiecare dată căutarea a scos altceva, real.
  Caută **eticheta pe care o vede omul**, nu doar identificatorul: „Impozit estimat" n-a apărut la
  `grep estimare_impozit`, dar clasa a apărut căutând textul.
- **Nu declara o clasă golită pe un singur limbaj.** `METODA` §17. R26 a fost măsurat corect prin AST
  pe Python și a fost **fals despre aplicație**.
- **Nu recicla un nume într-un fișier de gărzi.** Am definit `_JS` peste un `_JS` care exista deja în
  `test_aritmetica_in_prezentare.py` și arăta spre alt director — două gărzi vechi au început tăcut să
  măsoare altceva și au picat cu „fișier inexistent".
- **Nu construi o gardă care verifică faptul că un temei DETERMINĂ o comparație.** Nu se poate; o gardă
  care pretinde că o face transformă o citire umană într-un verde automat.
- **Nu cere o cifră pentru interdicția 22.** N-are numitor.
- **Nu lărgi un scan ca să scadă un număr.** S-a încercat de două ori: o dată a scos 16 din 32, o dată
  a dat 1167 din care 90% zgomot.
- **Nu edita scripturi de conversie din shell.** Escapările se rup pe ghilimelele românești și pe
  `\u`. Se scrie **fișierul** și se trimite octet cu octet (`METODA` §10.3).
- **Nu rula un RED-proof cu `git checkout`** când arborele are muncă necomisă — se scrie mutația, se
  rulează, se restaurează din conținutul citit înainte, și se **verifică** că restaurarea e identică.
- **Nu curăța `__pycache__` doar la sfârșit.** Două mutații de aceeași dimensiune în aceeași secundă
  reciclează bytecode-ul și proba devine falsă.
