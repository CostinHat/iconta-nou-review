
## NC-22 (10.07.2026) — CAMP_DIALECT in rip_ecran.js
6 campuri construite ca <label>text<br>input (linii 61-70), in loc de structura
canonica .camp + .camp-eticheta (Design System v1.1, regula stabilita la #61).
Detectat mecanic de verificator (categorie noua CAMP_DIALECT). De migrat pe canonic.

## NC-23 (10.07.2026) — DIACRITICE in etichetele REGISTRU (operatiuni_ecran.js)
Etichetele afisate din configuratia REGISTRU (titluri operatiuni, etichete campuri,
optiuni select) sunt fara diacritice ("Suma incasata/platita", "Incasare de la client").
Incalca regula 6. Verificatorul nu le prinde: scaneaza doar linii cu </placeholder,
REGISTRU e configuratie pura. De reparat: diacritice in etichete + extindere detector.

## NC-24 (10.07.2026) — R4 nav.setInapoi: lista completa ecrane nemigrate
19 fisiere fara setInapoi (verificat grep -L): activitate_cabinet, admin_gratuite,
admin, admin_sanatate, asistenti, asistent, cabinet, capacitate, control,
etransport_ecran, login, produse_ecran, raporteaza, recomanda, rip_ecran, semafor,
termene, tipare, validat. operatiuni_ecran migrat acum (patch 61b), scos din lista.
De migrat R4 (Sonnet), conform planului Faza B.

## NC-25 (10.07.2026) — Operatiuni speciale: test functional "Genereaza nota" neexecutat
Patch-urile 61a-61d (aliniere campuri + nav.mergi cu scroll memorat + fix corp stale
+ fix .closest(".camp")) verificate sintactic si vizual (navigare stabila, scroll
memorat). Ramane de rulat: generare efectiva a unei note (ex. TVA la incasare) si
verificare ciorna in Registru jurnal — pt validarea end-to-end a fix-ului closest.

## Test #62 (10.07.2026) — Amortizare MF liniara: PASS
Verificat pe KAI PERFORMANCE (tenant_002), luna 07/2026: 3 linii generate
(Laptop Dell 166.67, Dacia Duster 1250.00, Laptop test 166.67), total 1583.34 lei.
Aritmetica validata manual (formula liniara, start luna urmatoare PIF, stop la DNF)
- coincide exact cu rezultatul din baza. ERP test corect exclus (PIF in luna curenta).
Cont 6811/2813 monografie corecta.
JURNAL_OKcat

## Test #64 (10.07.2026) — Stocuri: fise CV + CMP: PASS
11/11 teste unitare pytest (core/test_stocuri_cv.py). Verificare end-to-end pe
tenant_002 (KAI), 2 articole, 5 miscari: CMP recalculat corect la intrare (5.00,
7.00 lei), neschimbat la iesiri succesive, sold cantitate/valoare exact la fiecare
linie. Surse diverse (inventar, reteta) alimenteaza corect aceeasi fisa - integrare
reala confirmata, nu doar motor izolat.

## Test #65 (10.07.2026) — Operatiuni speciale (30, ecran generic): PASS
Testat end-to-end operatiunea "sponsorizare" (POST /tenants/2/nota-sponsorizare):
1000 lei mod contract -> nota 6582=401 corecta, status ciorna, descriere pastrata.
Numar gol la generare e comportament normal (populat abia la validare); Registru
jurnal are deja fallback descriere||numar||#id (firme.js:1172), afisare corecta.
Nota de test stearsa dupa verificare. Include si fix-urile de aliniere/navigare
din aceasta sesiune (patch 61a-61d): structura .camp, nav.mergi cu scroll memorat.

## Test #66 (10.07.2026) — Perioada blocata: FAIL initial -> PASS dupa reparatie
Bug real gasit: doar 3 din 39 puncte de inserare in {schema}.inregistrari verificau
perioada blocata (doar editare/stergere/validare nota manuala). Toate cele 30 module
+ crearea de nota noua + amortizarea ocoleau blocarea complet (testat empiric:
amortizare generata cu succes pe luna blocata, status validata direct).
REPARATIE: trigger SQL (verifica_perioada_blocata) pe INSERT/UPDATE/DELETE, aplicat
pe toate cele 6 scheme tenant existente + tenant_template.sql (tenanti noi). Exception
handler specific (nu Exception generic - doar traduce PERIOADA_BLOCATA) -> 423 curat.
Testat: amortizare pe luna blocata->423, luna libera->200 (flux normal nestricat),
creare nota manuala pe luna blocata->423 (cazul gaurii reale, acum acoperit).

## Test #67 (10.07.2026) — PFA partida simpla + RIP: PASS
Motor complet testat end-to-end pe AMZUICĂ (tenant_004, id=13): adaugare incasare
5000+plata deductibila 800 (sold 4200 exact), validare, fisa D212 pe 2025 cu date
reale (venit 80000, cheltuiala 15000): CAS 12150 (baza fixa 12x4050, 25%), CASS
6500 (baza=venit net, regula 2025), impozit 4635 (10%), total 23285 - aritmetica
verificata manual, exacta. Motorul refuza corect calculul pt alt an decat 2025
(plafoane neverificate) - comportament defensiv corect, nu bug.
Gaura similara cu #66 gasita si reparata: rip_operatiuni nu avea trigger perioada
blocata. Extins acelasi tipar (trigger pe data_operatiune) pe toate 6 scheme +
tenant_template.sql. Testat: 423 pe luna blocata, 200 pe luna libera.
