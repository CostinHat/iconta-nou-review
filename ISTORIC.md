


## 13.09.2026, partea a patra — **P7 · valul D4: 215 instrucțiuni mutate, și faza tot nu se închide**

Pentru un contabil, a patra oară azi: nu s-a schimbat nimic. Aceleași ecrane, aceleași declarații,
aceleași cifre. Ce s-a schimbat e unde stă SQL-ul — și ce știm despre cât mai avem de făcut.

### Ce s-a schimbat, sub capotă

Cele **37 de module mixte** — cele care făceau două straturi deodată, de la `core/d223.py` cu o
instrucțiune la `core/control_incrucisat.py` cu 45 și `main.py` cu 38 în helperii de modul — și-au
dat cele **215 instrucțiuni SQL** la **37 de `core/repo_*.py`**. `D4` **37 → 0**.

Mutarea a fost făcută de un instrument, `scripts/p7_d4_separa.py`, nu cu mâna. Motivul e o
măsurătoare, nu o preferință: 215 poziții în 13 forme diferite de loc, iar modul de eșec al unei
mutări manuale — parametri schimbați de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
**nu se vede la citire**. Instrumentul mută expresii, nu text; ce nu poate rezolva mecanic
raportează și lasă neatins. **Rest: 0 din 215.**

**Dovada că s-a mutat, nu s-a rescris:** amprenta SQL a întregului cod de producție — **1050
instrucțiuni distincte, 1307 în total** — e identică înainte și după.

### Partea care merită citită: cifra care arăta bine

După val: `D1`=0, `D2`=0, `D4`=0, **`P7_ACTION_REQUIRED`=0**. Citită singură, cifra spune că faza s-a
terminat. **Nu s-a.** Textul canonic cere patru straturi, iar despre use-case spune că *deține
tranzacția (P4) și orchestrează*. Măsurat: **385 din 421 de rute își deschid singure tranzacția**,
doar **7** deleagă către un modul `USE_CASE`, iar use-case-uri declarate sunt **4**.

*Un `ACTION_REQUIRED=0` care nu acoperă un criteriu canonic nu e o stare, e o lipsă de detector.* Am
închis golul cu un instrument și o gardă, nu cu o propoziție în predare: `scripts/p7_criterii.py`
măsoară toate patru criteriile, iar `core/test_p7_criterii.py` ține clichetul celor 385 **și
interzice planului să declare P7 închisă peste el**.

### Ce a mai scos valul, și toate trei sunt aceeași clasă

1. **O justificare ancorată prin vecinătate nu se mută cu codul.** Trei `ON CONFLICT DO UPDATE` au
   trecut în depozit, iar `# upsert-ok:` a rămas în modulul vechi. Prins de `test_upsert_motivat` la
   prima rulare — de instrument, nu de mine.
2. **Instrumentul traseelor a tăcut din nou**, a doua oară în două valuri: 12 adnotări deodată.
   Reparat cu **perechea nominală** modul ↔ `repo_<același nume>`.
3. **Citările în plan s-au mutat iar** — 8 ancore. De data asta reparate cu un instrument,
   `scripts/reancoreaza_plan.py`, care a greșit el însuși de două ori înainte să meargă: cerea
   unicitatea fragmentului pe tot planul, și lua reperul din fișierul deja editat.

### Cifre

`D4` **37 → 0** · `P7_RAW_ITEMS` **38 → 1** · `P7_ACTION_REQUIRED` **37 → 0** · straturi declarate
**167** (96 `FISCAL_ENGINE` · 65 `REPOSITORY` · 4 `USE_CASE` · 2 `HTTP`). Criteriul rămas:
**385/421**. Poarta: **5795 verzi / 0 roșii** · 12 sărite · 14 xfail ·
verificator **TOTAL 0**.

**P7 RĂMÂNE DESCHISĂ.** *Zero pe toate detectoarele nu e zero pe fază.*
