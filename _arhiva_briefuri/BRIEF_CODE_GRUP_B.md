# BRIEF CLAUDE CODE — GRUP B (26 pozitii), stabilit 16.07.2026

## Ce este
Cele 26 de pozitii PLANIFICAT din FUNCTIONALITATI.csv fara risc fiscal/bancar/ANAF direct.
Grupul A (10 pozitii: F120, F121, F123, F125, F126, F127, F128, F129, F130, F160) NU se atinge.
F149 = RESPINS 16.07.2026, nu se reia.

## REGULA 0 — DESIGN SYSTEM INAINTE DE ORICE CONSTRUCTIE
Inainte de ORICE cod de interfata (ecran, card, buton, mesaj, culoare, iconita,
data, bani, semafor): se CITESTE DESIGN_SYSTEM.md si se CITEAZA in conversatie
capitolul + regula aplicata. Fara citare = nu se scrie cod.
    grep -n "<tema>" DESIGN_SYSTEM.md
Daca regula NU exista scrisa -> STOP, se stabileste cu Costin. NU se inventeaza
tipar generic, NU se copiaza de pe alt ecran "ca asa e acolo".
Aceeasi situatie = aceeasi solutie peste tot.
Regula noua intra in DESIGN_SYSTEM.md SI in verificator_conformitate.py simultan.

## Extragerea listei (la sursa, nu din memorie)
    grep -n "PLANIFICAT" FUNCTIONALITATI.csv
Din rezultat se exclud pozitiile grupului A si F149. Ce ramane = grupul B.
Daca numarul != 26, STOP si raporteaza diferenta. Nu ghici.

## Ordinea loturilor (nu se sare)
1. F124 (pilot, redefinit 16.07)
2. Notificari
3. Pontaj / adeverinte
4. Stoc
5. Rapoarte
6. Arhivare
7. Cont gratuit: F154-F159, F161 (ultimele — se leaga peste module deja stabilizate)
F131-F135 se incadreaza pe tema, nu pe numar.

## Ciclul per pozitie (obligatoriu)
0. CITESTE DESIGN_SYSTEM.md pe tema pozitiei si CITEAZA capitolul (vezi Regula 0)
1. CITESTE linia din FUNCTIONALITATI.csv (temei scris)
2. GREP pe TOT ~/iconta_nou/ + /opt/iconta (buildul vechi port 8000 contine
   implementari pierdute la refacere) inainte de a declara ceva absent
3. SCRIE specificatia (ce ecran, ce ruta, ce tabel, ce regula DS) — cere confirmare
4. IMPLEMENTEAZA
5. VERIFICA: test functional real (curl/script pe Postgres cu INSERT+ROLLBACK),
   NU py_compile / node --check — alea prind doar sintaxa
6. COMMIT + actualizeaza statusul in FUNCTIONALITATI.csv, apoi GREP ca dovada

## Garduri (STOP, intreaba)
- Orice valoare fiscala (cota, plafon, formula) -> STOP. Se verifica la ANAF, nu de Code.
- Orice apel catre ANAF/SPV/banca/plati -> STOP, e grup A.
- Regula UI care nu exista scrisa in DESIGN_SYSTEM.md -> STOP (vezi Regula 0).
- Schema noua de date -> STOP, e decizie de arhitectura.

## Reguli permanente
- (0a) Reparatie reala: fara cod mort, fara cai comentate ramase.
- (0b) Global-first: inainte de orice CSS, verifica daca elementul e prins de o regula globala.
- (0c) Verificare functionala reala dupa orice schimbare de backend.
- Nu umbla peste ce functioneaza.
- Oprirea se justifica tehnic, nu prin oboseala.
- Cautari ample, executii tintite, apoi verificare/salvare.
- Diacritice: text afisat CU, cod/markere FARA.
- Restart: sudo systemctl restart iconta-nou
- verificator_conformitate.py trebuie sa ramana TOTAL 0 dupa fiecare lot.

## Definitia de terminat (per lot)
verificator TOTAL 0 + test functional trecut + FUNCTIONALITATI.csv actualizat
si dovedit cu grep + commit.
