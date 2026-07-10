
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
