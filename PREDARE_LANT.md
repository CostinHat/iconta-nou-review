Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII" (7 puncte), apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_002 (Coafor Micro Neplatitor SRL, cabinet 1968); 2 defecte de cod reparate

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_002 cap-coada cu Playwright (captura PRIVITA, nu selectoare - Regula 14),
REPARAND ce gasesti; ce gasesti pe o firma cauta pe toate (Regula 13). Punctul la care am ramas: parcurse
VIZUAL ecranele de sus (meniu firma, Import=10 straturi listate, Date firma, Facturi, Banca, Casa, Salariati
gol canonic, Declaratii wizard pas 1, Control fiscal semafor). RAMASE, NEATINSE:
- **Cele 9-10 straturi de migrare INDIVIDUAL**: import->previzualizare->salvare->confirmare->ecranul unde apar
  datele. Doar meniul Import a fost privit (straturile listate); niciun strat parcurs cap-coada. tenant_002 are
  DOAR plan_conturi populat (185 randuri) + 1 factura; restul straturi goale.
- **Provocarea deliberata a blocajelor**: fisiere stricate la PREVIZUALIZARE (nu salvare) pe straturile de
  import; campuri obligatorii goale la fiecare formular. NEFACUTA sistematic (doar reg_com->Bilant, reparat).
- **Fiecare declaratie datorata pana la XML + DUK din UI**: D100 (micro) REFUZA corect pe zero (venituri 70x=0;
  hint "1 factura necontabilizata" pe T1) - de confirmat din ECRAN, nu doar din modul. D406 (SAF-T) datorat pe
  semafor T1/T2 - NEPARCURS deloc (generare+DUK). Bilant S1005 acum REFUZA fara reg_com (reparat) - de confirmat
  refuzul pe ECRAN. D205/D301 neaplicabile/fara subiect.

## FOUR-WAY (ultima executie, 17.08.2026)
HEAD = origin/main = backup/lant-2026-08-17 = RUNNING = 86b776a. Sentinele push absente; tree tracked-clean;
divergent=False; service ActiveEnter 04:56 > commit 04:48 (post-commit a restartat: "procesul viu preia 86b776a").
pytest 2258 passed / 0 failed / 4 skipped / 16 xfailed (COLLECTED 2278); verificator TOTAL: 0.

## LIVRAT ACEASTA TURA (2 clustere, fiecare cu gard RED-probat)
1. **Reconciliere D100 pe semafor** (control_incrucisat._thunk_d100): despacheta 2 valori de la d100.pull care
   intoarce 3 (prof, venituri, cheltuieli, de la profit-base-fix 16.08) -> ValueError "too many values to
   unpack" pe ORICE firma, clasificat GRI de _ruleaza_una PASUL 1 (opusul intentiei "deriva de semnatura =
   rosu rupt"), cu textul Python scurs in motiv; a-doua-cale D100 MOARTA universal (micro t002 + profit t004).
   Latent: ramura profit calcula cota pe VENITURI, nu pe profit. Fix structural (Regula 13): extras
   d100.deriva_obligatii (sursa unica) chemata de genereaza SI de thunk. Gard test_reconciliere_d100_wiring
   (RED micro+profit gri-crash -> GREEN). test_d100_cota + test_base_nula_generatoare reancorate la refactor.
2. **Bilant S1005/S1003 refuza fara reg_com** (bilant_api.erori_generare): poarta verifica doar cui+nume, deci
   genereaza emitea bilant FARA regCom - respins de DUKIntegrator ("regCom: atributul trebuie sa existe", reguli
   2026.1) desi UI promitea "blocheaza Bilant S1005". Fix: reg_com in poarta partajata -> refuz cu mesaj clar.
   Gard test_bilant_regcom_poarta (RED S1005+S1003 nu ridicau -> GREEN).

## FRONTURI DESCHISE / OBSERVATII (neatinse, pentru decizie sau tura viitoare)
- **Tensiune de semafor D100 (tenant_002)**: semaforul arata D100 T1/T2 2026 ca RESTANTE ROSII, dar generarea
  REFUZA "nu se depune pe zero" (venituri 70x=0). Verdictele despre aceeasi declaratie NU coincid (Regula 14
  pct.2). Sectiunea "NU POT VERIFICA" spune simultan "nu pot demonstra ca firma exista in 2025". Necesita
  DECIZIE DE POLITICA: o factura emisa necontabilizata declanseaza restanta D100 dura? Nereparata (decizie).
- **D406 (SAF-T) datorat de micro neplatitor TVA**: semaforul il pune restanta T1/T2 pentru un coafor micro
  neplatitor. De VERIFICAT LA SURSA daca periodicitatea/obligativitatea SAF-T pentru micro neplatitor e corecta
  (Regula 5). Neverificat din cod.
- **Clasa "erori generare dXXX fara diacritice"** (deja DECLARATA in GARZI 17.08): mesajul de refuz D100 "nu se
  depune pe zero: nicio obligatie..." e fara diacritice (user-facing). Parte din clasa deschisa, neatinsa.
- **Prefix "Bilant nu se poate genera" fara diacritice** (bilant_api) - preexistent, neatins.
- **Badge stare per strat de migrare** (C3, din predarea tenant_004): meniul Import nu arata explicit ce strat
  are deja date (plan_conturi populat apare doar subtil umbrit). Front deschis mai vechi.

## BACKLOG (mostenit din predarea tenant_004, tot deschis)
d406 divergenta factura COER-T5 pe tenant_004 (antet net, alt modul, neatins). Q9/Q18/Q7/Q8/Q12/Q14 din predarea
anterioara. Constatari infra vizuala (contrast, title-extra, tinte <44px) - Costin da ordinea.
