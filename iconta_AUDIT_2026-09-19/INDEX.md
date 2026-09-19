# PACHET DE AUDIT INDEPENDENT — iConta

**Ce e pachetul ăsta.** Materialul pentru un audit independent asupra **întregii aplicații**, nu
asupra unei ture. E construit ca să poți **reproduce** cifrele, nu să le crezi: fiecare număr din el
are lângă el instrumentul care îl recalculează, iar instrumentele sunt în pachet și rulează pe
depozitul public.

**Regula care guvernează tot ce urmează, și pe care o poți verifica:** *o cifră pe care n-o poți
recalcula nu e o măsurătoare, e o amintire.* Dacă găsești una fără instrument, e un defect al
pachetului și merită raportat ca atare.

---

## 0. INDEXUL — ce răspuns dă fiecare piesă, și ce întrebare rămâne fără răspuns

| piesa | la ce întrebare răspunde | la ce NU răspunde |
|---|---|---|
| `01_COMMIT/` | **pe ce cod** se aplică tot restul; cum ajungi la el; cum rulezi poarta completă de la zero | nu spune dacă poarta e *suficientă* — v. `04_NEVERIFICAT` |
| `02_REGISTRE/` | **ce și-a propus** aplicația, **ce a decis** și **de ce**; cum se verifică; ce funcționalități există | registrele descriu intenția și istoria; **nu sunt probe**. Proba e suita |
| `03_PROBAT/` | **ce e verificat mecanic și cum** — clichetele cu cifra lor, gărzile, probele de lanț, instrumentele | nu spune că acoperirea e completă. Spune exact cât e |
| `04_NEVERIFICAT/` | **ce NU e verificat** — restanțe, interdicții nemăsurate, `xfail`, orbirea declarată a instrumentelor, rutele fără probă, acoperirea de browser | — *asta E răspunsul; secțiunea nu are „dar"* |
| `05_FISCAL/` | **valorile fiscale în vigoare**, cu temeiul legal și data verificării la sursă, plus corpusul de acte | nu garantează că legea nu s-a schimbat după data scrisă. Data e acolo tocmai ca s-o poți verifica |
| `06_ARTEFACTE/` | **măsurătorile brute** — ieșiri de instrument, loguri de poartă, rezultatele probelor de lanț | sunt brute dinadins: concluziile sunt în rapoarte, materia primă e aici |
| `07_RAPOARTE/` | ce s-a lucrat în ultima serie de loturi, cu ce s-a măsurat și ce a respins poarta | sunt despre **ture**, nu despre aplicație în ansamblu |

### Întrebările care rămân FĂRĂ RĂSPUNS în pachetul ăsta

Scrise aici, în față, nu îngropate:

1. **Nu există niciun audit extern anterior.** Tot ce e aici e auto-raportat. Instrumentele sunt ale
   noastre; calibrarea lor e făcută de noi. *Un instrument calibrat de cel care îl folosește poate
   greși în ambele direcții* — de-aia `03_PROBAT` dă comanda de recalculare, ca să nu depinzi de
   cuvântul nostru.
2. **Aplicația n-a fost folosită de un contabil real.** Toate cele ~20 de firme din bază sunt de
   test. Ce spune pachetul e *ce face aplicația când e apăsată*, nu *ce a făcut în producție*.
3. **Nicio declarație n-a fost depusă efectiv la ANAF prin aplicație** (restanța R40). Validatorul
   oficial DUK e rulat local și dă `valid`; depunerea propriu-zisă, cu recipisă, nu s-a exercitat.
4. **Acoperirea de browser e parțială și disjunctă de backlog** — măsurat: 90% din ce atinge
   checklistul de browser nu apare în backlog, 89% din backlog n-are nicio verificare de browser.
   Și, peste asta: **niciunul** dintre cele nouă fișiere de checklist nu e rulat de poartă — sunt
   liste scrise, nu probe. *E cea mai mare zonă neacoperită a aplicației; v.
   `04_NEVERIFICAT/CE_NU_SE_POATE_VERIFICA.md` §2.*
5. **Suita rulează pe o bază de test care e o copie a producției**, nu pe date sintetice construite
   de la zero. Un defect care depinde de date reale specifice poate să nu apară.
6. **Ce e în `frontend_test/` NU rulează la poartă.** Cele 35 de probe de lanț sunt rulate de mână,
   pe o instanță vie. La fiecare commit e păzit doar ce stă în `core/test_*.py`.

---

## 1. `01_COMMIT/` — pe ce cod, și cum verifici tu însuți

- `COMMIT.txt` — hash-ul exact, data, subiectul, `--stat`-ul.
- `OGLINDA_PUBLICA.md` — depozitul public și cum îl clonezi.
- `CUM_RULEZI_POARTA.md` — ce trebuie instalat, comenzile, **durata măsurată**, și ce NU acoperă.

## 2. `02_REGISTRE/` — starea lor curentă, întreagă

Cele nouă cerute, plus patru pe care le adaug fiindcă fără ele trei dintre celelalte nu se pot citi:
`CLAUDE.md` (procedura), `PLAN_LUCRU.md` (regulile în vigoare), `INVENTAR_A.md` (valorile fiscale —
e și în `05_FISCAL/`), `ISTORIC.md` (ce s-a făcut, când).

## 3. `03_PROBAT/` — inventarul, cu instrumentul lângă fiecare cifră

- `deriva_cifrele.py` — **rulează-l tu**: recalculează fiecare clichet și compară cu valoarea scrisă
  în cod. Dacă vreuna diverge, o spune.
- `INVENTAR.txt` — ieșirea lui, la data pachetului.

## 4. `04_NEVERIFICAT/` — lista declarată, fără atenuare

- `deriva_neverificatul.py` — **rulează-l tu**.
- `NEVERIFICAT.txt` — ieșirea lui.
- `CE_NU_SE_POATE_VERIFICA.md` — limitele poziției din care s-a scris pachetul, plus lipsa
  principală: acoperirea de browser, cu cifrele ei.
- `SCAN_SECRETE.txt` — ce s-a căutat în pachet înainte de publicare (chei, parole, șiruri de
  conexiune, conținut de bază) și ce s-a găsit. **Rulabil de tine**: `scan_secrete.py`.

## 5. `05_FISCAL/` — valorile, temeiul, data verificării

- `INVENTAR_A.md` — tabelul generat: cluster, valoare, temei structurat, intrare/ieșire în vigoare,
  risc, **data verificării la sursă**, notă.
- `CORPUS_ACTE.txt` — inventarul actelor din `anaf_surse/`, cu amprenta fiecăruia.

## 6. `06_ARTEFACTE/` — materia primă

Ieșiri de instrument, loguri de poartă (inclusiv **respinse**), rezultatele probelor de lanț.
*Respinsele sunt aici dinadins: o poartă care n-a picat niciodată nu dovedește nimic despre ea.*

## 7. `07_RAPOARTE/` — ultima serie de loturi

Rapoartele și măsurătorile celor patru lucrări din 16–17.09.2026.

---

## MANIFEST

`MANIFEST.sha256` — amprenta SHA-256 a **fiecărui fișier** din pachet. Verifică:

```
sha256sum -c MANIFEST.sha256
```
