# BRIEF_CODE_SEMAFOR — control_fiscal_api.py v2

## De ce v2 si nu patch

_arhiva_patchuri/ contine 5 patch-uri istorice de semafor (patch9_semafor_backend.py,
patch10_card_semafor.py, patch11_semafor_explicit.py, patch13_semafor_unitar.py,
patch14_semafor_ordine.py). Zona a fost carpita de cinci ori. Nu al saselea patch.

Defectele de mai jos au o cauza comuna: semaforul prefera un raspuns plauzibil in
locul lui "nu stiu".

F022 e marcat LIVE, "testat vizual + testat KAI". Testarea a confirmat ca ecranul
se afiseaza, nu ca verdictul e adevarat.

## FAZA 1 — cinci defecte mecanice. Fara schema. Reparabile acum.

### D1. Termenul ignora sarbatorile legale

`_zi_lucratoare` muta doar peste weekend (`while d.weekday() >= 5`).

Temei: Cod procedura fiscala (L.207/2015) art. 75 -> Cod procedura civila art. 181
alin. (2): termenul care cade in zi NELUCRATOARE se prelungeste pana in prima zi
lucratoare urmatoare. "Zi nelucratoare" include sarbatorile legale, nu doar weekendul.

Efect: daca 25 e sarbatoare, termenul calculat e mai DEVREME decat cel real ->
`term < azi` devine adevarat prematur -> firma apare ROSU desi e in termen.
FALS ROSU. Incalca principiul din control_incrucisat.py.

Reparatie: delegare la core/scadente.py::e_zi_lucratoare — sursa unica pentru zile
lucratoare (F081, stie L-V + sarbatori legale, inclusiv Pastele mobil).
Verifica intai ca nu se creeaza import circular.

### D2. Decembrie invizibil permanent

`declaratii_datorate` itereaza `for luna in range(1, 13)` doar peste anul curent
(`an = azi.year`). Perioada decembrie an-1 (termen 25 ian an) nu intra NICIODATA
in lista: in anul an-1 nu se ajunge la ea (termen viitor), iar in anul an bucla
n-o acopera.

Efect: D112/D300 nedepuse pe decembrie nu apar niciodata ca lipsa. Gaura permanenta,
in fiecare an. Mai grav decat D1.

Reparatie: perioadele candidate pornesc de la (an-1, 12), nu de la (an, 1). Acopera
si T4 an-1 pentru D300/D100 trimestrial (luna_fin 12, termen 25 ian an). Filtrul
`term <= limita` ramane si exclude singur ce e in viitor.

### D3. Fabrica obligatii din valori NULL

    decont = (vector.get("tip_decont") or "lunar").lower()
    regim  = (vector.get("regim_fiscal") or "micro").lower()

Vector completat PARTIAL -> codul ghiceste tacut. Platitor TVA cu tip_decont NULL
primeste 12 x D300 cerute in loc de 4. Firma cu regim_fiscal NULL primeste D100
trimestrial cerut, fie ca datoreaza sau nu.

Gri exista in cod, dar doar cand vectorul e complet gol (`if not vector`). Vector
pe jumatate -> nu gri, ci INVENTIE.

Reparatie: atribut lipsa -> GRI pe declaratiile care depind de el, cu cauza
declarata (ex: "tip_decont necompletat - nu pot sti periodicitatea D300"), NU
default tacut. Se supune regulii stare goala v2.13: gol + cauza + iesire (buton
catre Vector fiscal).

### D4. `_termen` presupune ziua 25 pentru orice declaratie

Functie unica cu 25 hardcodat. D101 e deja tratat ca exceptie separata (25 martie)
— semn ca abstractia e gresita. Scadentarul trebuie sa fie PER DECLARATIE, nu o
functie cu exceptii lipite pe langa.

Reparatie: tabel de scadente per tip, cu temeiul (OPANAF) langa fiecare.
VERIFICA FIECARE TERMEN LA SURSA OFICIALA ANAF. Nu din memorie, nu din codul
existent. Arata comanda/sursa de verificare pentru fiecare termen.

### D5. `_trimestre_pana_la` e cod mort

Construieste o lista si nimeni n-o cheama. Sterge (DS regula 0a: fara cod mort
lasat in urma).

## Teste obligatorii (functionale reale, nu py_compile)

1. `_termen(2026, 11)` -> 2026-12-28
   (25.12.2026 = vineri SI Craciun; 26.12 = sambata SI a doua zi de Craciun ->
   prima zi lucratoare = luni 28)
2. `declaratii_datorate` cu azi=2026-02-01, are_salariati=True -> contine
   ("D112", 2025, 12)
3. Vector cu tip_decont=None, platitor_tva=True -> D300 iese GRI cu cauza,
   NU 12 pozitii lunare
4. Regresie: firma cu toate depuse ramane verde

## FAZA 2 — STOP. Raporteaza, nu construi.

`declaratii_datorate` adauga doar D300, D112, D100, D101, D390 = 5 declaratii.
FUNCTIONALITATI.csv are 9 declaratii LIVE.
Absente din semafor: D205, D301, D394, D406.
F034 semnaleaza doar D394. D205, D301, D406 lipsesc NEDOCUMENTAT.

"Control fiscal automat" = promisiunea centrala a produsului. Verde azi inseamna
"ai depus 5 din 9". Verde castigat prin omisiune, nu prin adevar.

Pentru fiecare din cele 4, VERIFICA LA SURSA OFICIALA ANAF si raporteaza in tabel:
- conditia de datorare (ce atribut din vector o decide)
- periodicitatea
- termenul + temeiul (OPANAF)
- daca atributele necesare EXISTA in vectorul actual (F100: platitor_tva +
  periodicitate, regim micro/profit, operatiuni_ic, salariati) sau lipsesc

Ipoteza mea, DE VERIFICAT, nu de crezut:
- D301, D394 -> probabil derivabile din vectorul existent
- D205 -> depinde de dividende distribuite (fapt, nu atribut de vector) — poate
  cere citire pe cont 457
- D406 -> probabil cere ATRIBUT NOU in vector (categoria contribuabilului),
  fiindca obligatia porneste la date diferite pe categorii

Atribut nou in vector = schema = STOP, cere DA de la Costin.
NU construi Faza 2 fara decizia lui.

## Poarta

Faza 1: doar core/, fara schema, fara main.py. Buildabil direct.
Faza 2: raport + propunere. Zero cod.
