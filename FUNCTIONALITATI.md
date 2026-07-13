# iConta — Functionalitati (inventar complet)
*Document de referinta · 13 iulie 2026 · construit din auditul vizual complet al aplicatiei*

## 1. NIVEL CABINET (desktopul contabilului-sef)

- **Firme** — portofoliul cabinetului: lista firmelor-client cu cautare nume/CUI, adaugare firma cu validare CUI la ANAF (completare automata denumire/date), fisa individuala per firma (vezi cap. 2).
- **Migrare cabinet** — aducerea datelor din vechiul program, in 9 straturi ghidate cu stare per firma (gata/de incarcat) si decizie explicita de finalizare per strat: 1. Firme (CUI-uri in masa, lipite sau Excel/CSV, validate la ANAF), 2. Vector fiscal (TVA/regim/intracomunitar — fara el firma nu e procesabila), 3. Solduri initiale (balanta de deschidere, conturile analitice intra automat in plan), 4. Solduri parteneri (4111/401 defalcat pe partener, verificat automat cu balanta), 5. Salariati (nume/CNP/salariu/contract, CNP-uri verificate), 6. Asociati (nume/cota %, pentru D205), 7. Mijloace fixe (registru amortizare in curs), 8. Istoric declaratii (ce s-a depus deja — iConta nu le mai cere ca restanta), 9. Plan de conturi (OMFP standard automat + analitice/nestandard manual).
- **Termene** — scadentele urmatoarelor 60 de zile grupate pe data, cu drill-down pe declaratie -> firmele vizate.
- **Pachete lunare (Povestea lunii)** — rezumatul lunii pentru antreprenor, scris de AI, aprobat de contabil, trimis pe email (Brevo); selectie firma cu cautare, an/luna.
- **De validat** — coada de validare patru-ochi: declaratiile pregatite de asistenti asteapta aprobarea; cine a pregatit nu poate aproba; afiseaza pregatitorul pe nume; actiuni Aproba/Respinge (cu motiv)/Confirma depunerea (cu index SPV optional). Nimic nu se depune nevalidat.
- **Control fiscal (tot cabinetul)** — semafor de conformare pe fiecare firma (verde la zi / galben de urmarit / rosu restanta), cu drill-down: declaratii lipsa cu termene + verificari de coerenta contabila (echilibru, TVA, stocuri, documente pozate).
- **Asistenti (management echipa)** — roluri si permisiuni (poate pregati/valida/depune), firmele alocate, calitatea echipei pe 30 zile cu semafor si drill-down pe erori, fereastra per asistent (nivel, perioada, calitate, tipare sistematic/accident, drift, activitate), editare competente cu regula patru-ochi si avertisment soft; adaugare asistent.
- **Capacitate** — incarcarea echipei: in lucru / de validat / depuse luna asta / ritm pe zi lucratoare; tabel per asistent (in lucru, pregatite, depuse, % acceptate); timp mediu pe tip de declaratie (masurat real, de la deschiderea ecranului la generare).
- **Consolidare portofoliu** — cifrele tuturor firmelor cumulat de la inceputul anului: venituri/cheltuieli/profit/cash per firma + TOTAL.
- **Sinteza zilei** — brief la cerere (click pe card): astazi in cabinet (pregatite/validate/respinse/depuse/de validat/sesizari noi), productia echipei, ultimele evenimente.
- **Activitate** — doua zone: Activitatea echipei (centralizator + jurnal cronologic: cine ce a pregatit/validat/depus) si Tipare de erori (unde se greseste des si de ce — educatie AI din respingerile reale).
- **Setari cont** — date cabinet, competente proprii (ce pot face), chei API, date profil, schimbare parola.
- **Raporteaza (Suport)** — sesizari catre iConta cu capturi de ecran (buton sau Ctrl+V), istoric sesizari, raspunsuri in fir.
- **Recomanda** — invitatie de cabinete noi in iConta (emailuri multiple).
- **Notificari** — clopotel cu sumar la login + email zilnic (mesaje de la clienti, evenimente echipa).

## 2. FISA FIRMEI (21 de carduri per firma-client)

- **Facturi** — emitere factura (beneficiar cu verificare CUI la ANAF, linii cu potrivire automata a cotei TVA din nomenclator, numerotare automata), istoric cu navigare pe luni, detaliu factura (contare/stornare — doar cabinet), model factura (logo, font, culoare accent — identitatea vizuala a FIRMEI-CLIENT pe documente, preview live), facturi recurente (sabloane emise automat lunar, verificare zilnica 07:00), transformare proforma -> factura.
- **Declaratii** — generare per firma prin fluxul in 3 pasi (tip + perioada dupa periodicitate -> generare cu avertismente + XML -> trimitere in coada de validare); 9 tipuri: D100, D101 (cu IMCA), D112, D205 (cu impartire automata pe asociati), D300, D301, D390, D394, D406 SAF-T (cu mapare manuala de conturi).
- **Control fiscal** — semafor per firma: declaratii de depus cu termene + verificari de coerenta (echilibru balanta, TVA vs contabilitate, documente pozate).
- **Salariati** — stat de plata lunar (brut->net cu toate regulile 2026: facilitati, part-time cu supliment angajator, deduceri), fluturasi PDF per salariat, trimitere REGES (chei + raspunsuri), concedii medicale (certificat cu cod indemnizatie, calcul OUG 34/2024: CASS doar codurile 01/07/10, zile platite dupa diminuare, angajator zile 2-6 / FNUASS din ziua 7, auto-calcul zile lucratoare), salariat nou.
- **Bonuri si chitante** — documente pozate de client sau incarcate de contabil: clasificare AI (bon/chitanta), extragere comerciant/data/total/TVA/articole cu conturi propuse, poza cu zoom/rotire fina, verificare suma articole vs total, certificare si contare (bon -> nota; chitanta -> potrivire cu facturi 401=5311).
- **Registru jurnal** — notele contabile ale lunii cu stare (ciorna/validata), Valideaza/Editeaza/Sterge per nota, nota manuala noua, generare amortizare, blocare/deblocare luna, navigare pe luni.
- **Raport Z** — import AMEF (.p7b/XML) sau introducere manuala (total 11% mancare / 21% alcool-sucuri, numerar+card=total) -> nota ciorna pe zi, idempotent; descarcarea gestiunii dupa nota.
- **Stocuri** — NIR (numar/data/furnizor/CUI + articole cu cantitate/pret achizitie/pret raft/cota TVA) -> note ciorne; fise de magazie cantitativ-valoric CMP; descarcarea gestiunii lunii.
- **Balanta de verificare** — PDF lunar cu solduri si rulaje, navigare pe luni.
- **Bilant anual** — S1005 micro / S1003 mici: generare + validare ANAF pe server + descarcare XML.
- **Casa** — registru de casa pe luna cu sold curent per operatiune, dispozitie noua (incasare/plata pe tipuri cu conturi), avertismente plafoane numerar.
- **e-Transport** — notificare UIT: XML v2 pentru incarcare manuala in SPV; tip operatiune (AIC etc.), bunuri (cod tarifar NC, greutati, valoare), partener comercial, punct incarcare/descarcare cu judet, vehicul.
- **Operatiuni speciale** — note contabile pentru operatiuni punctuale, toate ca ciorna: Finantare (leasing, credite bancare, decontari asociati 455/457, avansuri 409/419), Imobilizari si capital (reevaluare 105, obiecte de inventar 303, provizioane si ajustari, productie 711/345, inventariere anuala), TVA regimuri speciale (TVA la incasare art.282, marja second-hand, marja agentii turism, taxare inversa art.331, achizitie de la agricultor 8%), Extern (achizitie/livrare intracomunitara), SGR garantii, ONG venituri, lichidare (vanzare activ, partaj).
- **Incasari/plati (RIP)** — partida simpla PFA/II/IF: registru pe luna cu totaluri, operatiune noua (tip/categorie/deductibilitate/metoda), import ciorne din banca si din casa, Fisa D212 (venit net, CAS/CASS datorate, cheltuieli limitate de analizat), registru-inventar.
- **Banca** — import extras (.xls/.xlsx/.csv, ING/Jasper, format detectat dupa continut), citire + potrivire automata a platilor cu facturile (pe CUI si sume, alocare partiala pe mai multe facturi), propuneri de contare per linie, ignorare/reactivare linii.
- **Magazin online** — WooCommerce: comenzile devin facturi emise automat (zilnic 07:30), sincronizare manuala la cerere, configurare conexiune.
- **Verificari** — coerenta lunara: echilibru balanta, trezorerie (fara solduri creditoare pe conturi de datorii salariale/fiscale), documente pozate, TVA vs contabilitate (cu drill-down pe facturile necontabilizate), D205 vs cont 457 (dividende).
- **Solicitari client** — mesajele firmei-client in fir de conversatie, cu raspuns din cabinet; notificari doar catre rolurile de cabinet.
- **Acces client** — conturile de portal ale firmei (email + nume), invitare client nou (magic-link, fara parola), revocare.
- **Import date** — cele 9 straturi de migrare direct pentru firma curenta (fara reselectarea firmei).
- **Produse** — nomenclatorul firmei: denumire -> AI potriveste cota TVA din legislatie (21/11/0%) cu justificare afisata, corectabila manual; cautare; folosit automat la emiterea facturilor.

## 3. PORTAL CLIENT (firma-client, read-only + actiuni proprii)

- **Acasa** — cardurile firmei cu cifrele lunii (formulare prietenoase, rotunjite la leu).
- **Facturile mele** — istoric pe luni (fara actiuni de contabil).
- **Cifrele firmei** — venituri/cheltuieli/profit/cash.
- **Declaratii depuse** — ce s-a depus, cu termene prietenoase.
- **Documente** — arhiva documentelor firmei.
- **Pozeaza bon** — fotografiere document -> clasificare AI -> confirmare client -> ajunge la contabil pentru certificare; emitere chitanta cu PDF.
- **Solicitari** — mesaje catre cabinet in fir.
- **Povestea lunii** — pachetul lunar primit.
- **Recomanda** — invita alta firma.
- **Acces cont** — schimbare email propriu, acces suplimentar pentru colegi (magic-link), revocare.

## 4. ROL ASISTENT (angajat de cabinet)

- **Desktop propriu** — 7 carduri limitate la firmele alocate; bara de calitate personala (pregatite luna aceasta, % acceptate din prima); antet cu nume + nivel (junior/senior).
- **Firme** — doar firmele alocate lui.
- **Declaratii** — fluxul 3 pasi cu selectie de firma; totul intra in coada de validare (nu poate depune direct fara permisiune).
- **De validat** — declaratiile colegilor; patru-ochi pe ID: la propriile declaratii vede "ai pregatit-o tu — o valideaza altcineva".
- **Control fiscal / Termene / Pachete lunare / Recomanda / Raporteaza** — aceleasi ecrane, restranse la firmele lui.
- **Permisiuni granulare** — poate_pregati / poate_valida / poate_depune, acordate de admin; zero firme -> cont dezactivat automat.

## 5. ROL ADMIN iCONTA (superadmin platforma)

- **Cabinete** — toate cabinetele din platforma cu categorii si cifre (firme, angajati, facturi, declaratii, recomandari, ultima activitate).
- **Activitate** — centralizator cross-platforma.
- **Sanatate server** — grafice load/memorie/disc pe istoric.
- **Gratuite / Anunturi** — gestiune conturi gratuite si anunturi in aplicatie.
- **Sesizari** — sesizarile din Raporteaza, cu raspuns.

## 6. TRANSVERSALE & INFRASTRUCTURA

- **Autentificare** — parola clasica + magic-link fara parola (clienti); landing public cu inregistrare cabinet self-service (CUI verificat la ANAF, avertisment CAEN non-6920).
- **Navigator** — ferestre modale cu traseu real: fir de parinti in antet, titlul pasului in corp, sageata = pop pe traseu, entitatea (cabinet/firma + CUI) doar in antet; sesiune per-tab (doua cabinete in taburi diferite nu se amesteca).
- **Design System** — DESIGN_SYSTEM.md v2.11 (16 capitole normative) + verificator_conformitate.py (gardian mecanic, TOTAL 0 pe toate ecranele): set inchis de butoane, tokeni de culoare/tipografie/spatiere, formatori canonici (bani/baniRotund/dataRo/pct/esc), dictionar unic de iconite si culori-card, diacritice obligatorii pe text afisat.
- **Fiscal la sursa** — toate valorile fiscale verificate la ANAF/lege inainte de cod (TVA 21/11%, salariu minim, CAS/CASS/CAM, IMCA, OUG 34/2024 etc.); generatoarele validate cu DUKIntegrator.
- **Securitate** — nginx cu SSL + rate limiting + headere (HSTS etc.), fail2ban 3 jails, XSS escapat centralizat (esc canonic), patru-ochi pe ID, roluri stricte (superadmin/admin_firma/angajat/client), actiuni de contabil ascunse pe portal.
- **Infrastructura** — FastAPI + PostgreSQL schema-per-tenant (iconta_v2), uvicorn prin systemd (iconta-nou.service, reporneste la boot), git pe ~/iconta_nou, fisiere normative canonice editate prin SSH.
