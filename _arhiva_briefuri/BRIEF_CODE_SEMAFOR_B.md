# BRIEF_CODE_SEMAFOR_B — D205/D301 fact-aware + motiv pe orice culoare

## Decizia (DECIZII.md commit 898482a — reciteste intai)
Varianta B: semaforul devine constient de fapte pentru D205 si D301, DAR motoarele
raman separate (o punte, nu fuziune). Plus: fiecare verdict poarta MOTIVUL, pe ORICE
culoare, inclusiv verde. C (fuziune) a fost RESPINS.

## Autonomie
Executie completa, fara opriri pe intrebari de implementare. Decizi singur si mergi
pana termini. Raspunzi si executi la tot.
POARTA (singura oprire): daca ai nevoie de SCHEMA NOUA sau sa MODIFICI cod LIVE care
schimba comportament existent (nu doar sa adaugi) -> STOP si intreaba. Nu ar trebui:
citesti rulaje din note validata (read), adaugi D205/D301 in semafor, adaugi motiv.

## FAZA 0 — verifica la sursa INAINTE de cod (regula de aur)
NU presupune ca functiile de citit faptul exista sau nu. Verifica:
1. control_incrucisat.py citeste deja rulaje pe conturi (4427/4426/4315/4316/444/436).
   grep cum citeste un rulaj pe cont dintr-o luna, din note status='validata'. Exista o
   functie refolosibila (rulaj pe cont X, luna Y)? Daca da, REFOLOSESTE-o - nu scrie
   una paralela (regula "nu construi paralel"). Daca nu, extrage una comuna pe care s-o
   foloseasca si D205 si D301.
2. Pentru D301: cum stie iConta ce luni au operatiuni IC? grep operatiuni intracomunitare
   / VIES / cont specific IC in cod (intracomunitar.py F050, d301.py, d390.py). Faptul
   pentru D301 poate fi deja calculat undeva.
3. Pentru D205: dividende distribuite = rulaj pe cont 457. Confirma contul exact la
   sursa (decontari_asociati.py F039, d205.py) - 457 sau 457 + alt analitic.
Raporteaza ce ai gasit inainte de a construi puntea. Daca faptul e deja citibil, puntea
e mica.

## FAZA 1 — puntea fact-aware (D205, D301)
Regula: semaforul cheama o functie care CITESTE faptul si decide. Motoarele raman
separate - functia de citit faptul traieste langa control_incrucisat (sursa faptelor),
semaforul o CHEAMA, nu o absoarbe.

D205 (anuala, termen ultima zi feb an+1 - deja verificat in brief-ul semafor faza 2):
- fapt: exista rulaj pe 457 (dividende distribuite) in anul evaluat?
- DA -> D205 datorata -> verde daca depusa / rosu daca nu.
- NU -> D205 NU se datoreaza -> NU apare ca lipsa (nu gri, nu rosu - pur si simplu nu e
  obligatie). Dar vezi FAZA 2: chiar si "nu se datoreaza" poarta un motiv.
- GRI daca nu poti citi faptul (lipsesc note validate pe anul ala): "nu pot verifica
  daca s-au distribuit dividende - lipsesc note validate".

D301 (lunar, doar lunile cu operatiuni IC, termen 25 luna urmatoare):
- fapt: luna are operatiuni IC (neplatitor TVA cu achizitii IC/servicii)?
- DA -> D301 datorata pe luna aia -> verde/rosu.
- NU -> nu se datoreaza pe luna aia.
- GRI daca nu poti sti.

VERIFICA LA SURSA termenele si conditiile exacte (OPANAF D205, D301) - nu din memorie.
Arata sursa pentru fiecare.

## FAZA 2 — motiv pe orice culoare (se aplica la TOATE cele 9, nu doar D205/D301)
Fiecare verdict din semafor poarta un MOTIV textual, pe orice culoare:
- verde: DE CE verde. Ex: "D300 depusa 24.04.2026, la termen (termen 25.04)".
- rosu: DE CE rosu. Ex: "D112 mai 2026 nedepusa, termen 25.06 depasit".
- gri: DE CE nu se poate verifica. Ex: "tip_decont necompletat - nu pot sti
  periodicitatea D300".
- "nu se datoreaza" (D205/D301 fara fapt): si asta poarta motiv. Ex: "D205 nu se
  datoreaza - niciun rulaj 457 in 2026 (fara dividende distribuite)".

Structura: fiecare intrare din rezultatul evalueaza_firma capata un camp `motiv` (text
scurt, cu temei). NU doar culoarea. Aliniat cu control_incrucisat (temei + limita pe
fiecare constatare). Diacritice in text afisat: CU. In cod/markeri: FARA.

UI: motivul se afiseaza langa fiecare linie de declaratie in ecranul Control fiscal
(cabinet + per firma). Citeste regula Design System pentru cum se afiseaza text
secundar/explicativ langa un rand inainte de a scrie UI. Daca nu exista regula pentru
asta, STOP si stabileste cu Costin (regula 0 DS).

## Reguli permanente (CLAUDE.md)
- Verificare functionala reala pe tenant_002, nu py_compile: evalueaza_firma pe o firma
  reala, verifica ca D205/D301 apar corect si ca fiecare linie are motiv.
- Termene/conditii fiscale: verificate la sursa oficiala ANAF, cu comanda aratata.
- verificator_conformitate.py TOTAL 0.
- FUNCTIONALITATI.csv: F022 actualizat (semafor 9/9 + motiv), ACELASI commit.
- Teste: test_control_fiscal.py extins pe D205 (cu/fara 457), D301 (cu/fara IC), si pe
  prezenta campului motiv pe fiecare stare.
- Restart: sudo systemctl restart iconta-nou.

## Legatura cu tema urmatoare (nu o construi, doar tine cont)
Dupa asta urmeaza #2 (punte factura->stoc). Aceeasi tensiune: surse de fapt contabil
deconectate. Functia de citit fapte pe care o faci/refolosesti aici trebuie sa fie
GENERALA (rulaj pe cont X, luna Y), nu specifica D205/D301 - ca #2 s-o poata refolosi.
O punte, nu doua.

## Ce raportezi la final
Commit-ul, ce ai gasit in Faza 0 (functie refolosita sau extrasa), un exemplu de
evalueaza_firma pe tenant_002 cu motivele vizibile pe fiecare linie, si limita declarata.
