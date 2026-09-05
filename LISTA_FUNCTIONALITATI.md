# LISTA FUNCȚIONALITĂȚILOR

**Derivată din cod cu `scripts/scan_functionalitati.py`** (03.09.2026), la comanda lui Costin: *„lista tuturor funcționalităților aplicației, derivată din cod, nu scrisă din memorie … nu lăsa nimic afară, fără excepții și fără filtrări de niciun fel.”*

**Fișierul se EDITEAZĂ de aici încolo, nu se regenerează.** Regenerarea (`--scrie`) rescrie tabelele și **pierde stările de probare**. Numerotarea e stabilă cât timp nu se regenerează: un rând se citează ca `#nr`.

**Ce e o unitate:** un **punct de intrare** — locul prin care ceva poate fi cerut, apăsat sau declanșat. Patru feluri, toate patru în listă: **A** rutele HTTP · **B** ecranele · **C** joburile de fundal · **D** instrumentele din `scripts/`.

**Ce NU e unitate, declarat:** modulele din `core/` (nu sunt puncte de intrare — se ajunge la ele prin A sau C, și apar ca *atribut*: coloana de declarație se calculează din ce scriu ele) · `frontend_test/` (probe) · `core/test_*.py` (gărzi).

**Coloana „declarație” se derivă**, nu se judecă: modulele `core/d<cifre>*` + `declaratii_api` + `declaratii_componente` + `bilant*` citesc un set de tabele; o unitate primește **da** dacă scrie într-unul dintre ele sau dacă cheamă ea însăși un modul de declarație. **`?`** înseamnă *nu se poate decide mecanic* — nu se rotunjește la „nu”.

**Stare probare:** `neprobat` peste tot la scriere. Se schimbă pe măsură ce se probează.

## A. Rute HTTP — 427

*Grupate pe traseul din `TRASEE.md` (derivat de `scan_trasee.acoperire`). Rolul cerut, unde există, e scris lângă rută — de el atârnă proba.*

### T-SPV — Conectorul SPV/ANAF (rute montate din core/spv_rute.py) (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 1 | Callback OAuth (URL inregistrat la ANAF, exact) | `GET /anaf/oauth/callback` · fără gardă | citire / afisare — `anaf_oauth_callback()` | ? | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 2 | URL-ul de autorizare ANAF pentru principalul apelantului | `GET /spv/autorizare` · fără gardă | citire / afisare — `spv_autorizare()` | ? | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 3 | Starea conexiunii SPV pentru ecran (fara secrete, fara apel ANAF). | `GET /spv/stare` · fără gardă | citire / afisare — `spv_stare()` | ? | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T01 — Declarația — generare, validare, coadă, aprobare, depunere (16)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 4 | coada lista | `GET /coada` · `cere_cabinet` | citire / afisare — `coada_lista()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 5 | coada adauga | `POST /coada` · rol `admin_firma/angajat` | creare sau executie — `coada_adauga()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 6 | coada aproba | `POST /coada/{coada_id}/aproba` · rol `admin_firma/angajat` | creare sau executie — `coada_aproba()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 7 | [patru-ochi] Continutul unui element din coada pentru VIZUALIZARE inainte de aprobare: declaratia (avertismente/note), … | `GET /coada/{coada_id}/continut` · `cere_cabinet` | citire / afisare — `coada_continut()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 8 | coada depune | `POST /coada/{coada_id}/depune` · rol `admin_firma` | creare sau executie — `coada_depune()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 9 | coada respinge | `POST /coada/{coada_id}/respinge` · rol `admin_firma/angajat` | creare sau executie — `coada_respinge()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 10 | Semafor pentru toate firmele cabinetului + sumar (verde/galben/rosu). | `GET /control-fiscal` · `cere_cabinet` | citire / afisare — `control_fiscal_portofoliu()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 11 | Detaliu conformare pentru o firma: lista lipsa + de urmarit + constatari contabile. | `GET /control-fiscal/{tenant_id}` · `cere_cabinet` | citire / afisare — `control_fiscal_detaliu()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 12 | declaratii tipuri | `GET /declaratii/tipuri` · `cere_cabinet` | citire / afisare — `declaratii_tipuri()` | da | probat invalid 03.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 13 | declaratie genereaza | `POST /declaratii/{tip}` · rol `admin_firma/angajat` | creare sau executie — `declaratie_genereaza()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 14 | Genereaza declaratia si o trece prin validatorul OFICIAL ANAF (DUKIntegrator) | `POST /declaratii/{tip}/valideaza` · rol `admin_firma/angajat` | creare sau executie — `declaratie_valideaza()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 15 | firma verificari | `GET /firme/{tenant_id}/verificari` · `cere_cabinet` | citire / afisare — `firma_verificari()` | nu | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 16 | SUPERVIZORUL, rulat LA CERERE pe firmele utilizatorului curent | `GET /supervizor` · `cere_cabinet` | citire / afisare — `supervizor_la_cerere()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 17 | istoric import salveaza | `POST /tenants/{tenant_id}/istoric-declaratii-import` · rol `admin_firma` | creare sau executie — `istoric_import_salveaza()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 18 | istoric import incarca | `POST /tenants/{tenant_id}/istoric-declaratii-import/incarca` · `cere_cabinet` | creare sau executie — `istoric_import_incarca()` | da | probat invalid 03.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1 |
| 19 | Scadente viitoare grupate pe data + tip, cu numarul de firme. | `GET /termene` · `cere_cabinet` | citire / afisare — `termene_portofoliu()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T02 — Factura emisă — creare, contabilizare, ieșiri (20)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 20 | apiv1 facturi | `GET /api/v1/firme/{tenant_id}/facturi` · `cere_api_key` | citire / afisare — `apiv1_facturi()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 21 | apiv1 factura emite | `POST /api/v1/firme/{tenant_id}/facturi` · `cere_api_key` | creare sau executie — `apiv1_factura_emite()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 22 | facturi lista | `GET /tenants/{tenant_id}/facturi` · `cere_context` | citire / afisare — `facturi_lista()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 23 | factura creeaza | `POST /tenants/{tenant_id}/facturi` · rol `admin_firma` | creare sau executie — `factura_creeaza()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 24 | fr lista | `GET /tenants/{tenant_id}/facturi-recurente` · `cere_context` | citire / afisare — `fr_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 25 | fr adauga | `POST /tenants/{tenant_id}/facturi-recurente` · `cere_context` | creare sau executie — `fr_adauga()` | nu | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 26 | fr sterge | `DELETE /tenants/{tenant_id}/facturi-recurente/{sid}` · `cere_context` | stergere — `fr_sterge()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 27 | fr comuta | `PUT /tenants/{tenant_id}/facturi-recurente/{sid}` · `cere_context` | modificare — `fr_comuta()` | nu | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 28 | facturi emite | `POST /tenants/{tenant_id}/facturi/emite` · rol `admin_firma` | creare sau executie — `facturi_emite()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 29 | facturi numerotare get | `GET /tenants/{tenant_id}/facturi/numerotare` · `cere_context` | citire / afisare — `facturi_numerotare_get()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 30 | facturi numerotare set | `PUT /tenants/{tenant_id}/facturi/numerotare` · rol `admin_firma` | modificare — `facturi_numerotare_set()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 31 | factura detalii | `GET /tenants/{tenant_id}/facturi/{factura_id:int}` · `cere_context` | citire / afisare — `factura_detalii()` | da | probat invalid 03.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 32 | [EEE2] Refuzul e EXPLICAT, nu o eroare de bază: `409`, cu numărul notei și cu ieșirea numită (storno) | `DELETE /tenants/{tenant_id}/facturi/{factura_id}` · rol `admin_firma` | stergere — `factura_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 33 | RUTA MANUALĂ de contare — **a doua cale, declarată** (R87, decizia lui Costin 29.08.2026, varianta (ii)+(iii) din AAA4) | `POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza` · `cere_cabinet` | creare sau executie — `factura_contabilizeaza()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 34 | factura email | `POST /tenants/{tenant_id}/facturi/{factura_id}/email` · rol `admin_firma` | creare sau executie — `factura_email()` | da | probat invalid 03.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 35 | F131: supapa per factura | `PUT /tenants/{tenant_id}/facturi/{factura_id}/notificare` · rol `admin_firma` | modificare — `scadentar_supapa()` | da | probat invalid 03.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 2 |
| 36 | factura pdf ruta | `GET /tenants/{tenant_id}/facturi/{factura_id}/pdf` · `cere_context` | citire / afisare — `factura_pdf_ruta()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 37 | RECUNOAȘTEREA unei facturi EMISE venite prin import — actul care îi scrie nota | `POST /tenants/{tenant_id}/facturi/{factura_id}/recunoaste` · rol `admin_firma` | creare sau executie — `factura_recunoaste()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 38 | facturi storno | `POST /tenants/{tenant_id}/facturi/{factura_id}/storno` · rol `admin_firma` | creare sau executie — `facturi_storno()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 39 | Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal). | `POST /tenants/{tenant_id}/facturi/{factura_id}/transforma` · rol `admin_firma` | creare sau executie — `proforma_transforma()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T03 — Statul de plată și fluturașul (8)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 40 | tenant fluturas | `GET /tenants/{tenant_id}/fluturas/{salariat_id}` · rol `admin_firma` | citire / afisare — `tenant_fluturas()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 41 | Scrie nota ciorna a statului de plata | `POST /tenants/{tenant_id}/salarii-contare` · `cere_cabinet` | creare sau executie — `salarii_contare_scrie()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 42 | Nota pe care ar scrie-o statul de plata + divergentele fata de D112, cu ambele cifre. | `POST /tenants/{tenant_id}/salarii-contare/propunere` · `cere_cabinet` | creare sau executie — `salarii_contare_propunere()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 43 | tenant stat plata | `GET /tenants/{tenant_id}/stat-plata` · `cere_cabinet` | citire / afisare — `tenant_stat_plata()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 44 | corp: {salariat_id, an, luna} | `POST /tenants/{tenant_id}/stat-plata/corectie` · `cere_cabinet` | creare sau executie — `tenant_stat_corectie()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 45 | Exemplarele emise + contradictiile DERIVATE (emis vs recalcul de acum) | `GET /tenants/{tenant_id}/stat-plata/emis` · `cere_cabinet` | citire / afisare — `tenant_stat_emis()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 46 | corp: {an, luna} | `POST /tenants/{tenant_id}/stat-plata/emite` · rol `admin_firma` | creare sau executie — `tenant_stat_emite()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 47 | corp: {exemplar_id, motiv} | `POST /tenants/{tenant_id}/stat-plata/motiv` · `cere_cabinet` | creare sau executie — `tenant_stat_motiv()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |

### T04 — Concediul medical (5)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 48 | corp: {salariat_id, an, luna (luna certificatului), zile_lucratoare_cm, cod?, zile_episod?, prima_zi_din_episod?, spita… | `POST /tenants/{tenant_id}/calcul-cm` · `cere_cabinet` | creare sau executie — `calcul_cm_endpoint()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 49 | Codurile de indemnizatie pentru ecran, cu procentul VALABIL LA DATA certificatului | `GET /tenants/{tenant_id}/concedii/coduri` · `cere_cabinet` | citire / afisare — `concedii_coduri()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 50 | cm lista | `GET /tenants/{tenant_id}/salariati/{salariat_id}/concedii` · `cere_cabinet` | citire / afisare — `cm_lista()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 51 | cm salveaza | `POST /tenants/{tenant_id}/salariati/{salariat_id}/concedii` · rol `admin_firma/angajat` | creare sau executie — `cm_salveaza()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 4 |
| 52 | cm sterge | `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}` · rol `admin_firma/angajat` | stergere — `cm_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T05 — Nota contabilă — de la document la registrul-jurnal (34)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 53 | apiv1 balanta | `GET /api/v1/firme/{tenant_id}/balanta` · `cere_api_key` | citire / afisare — `apiv1_balanta()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 54 | [lista 5, 30.08.2026] Balanta ca DATE, nu ca PDF | `GET /tenants/{tenant_id}/balanta` · `cere_cabinet` | citire / afisare — `cabinet_balanta_date()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 55 | cabinet documente balanta | `GET /tenants/{tenant_id}/documente/balanta` · `cere_cabinet` | citire / afisare — `cabinet_documente_balanta()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 56 | [lista 3, 30.08.2026] CARTEA MARE (14-1-3), prin inlocuitorul ei legal | `GET /tenants/{tenant_id}/fisa-cont` · `cere_cabinet` | citire / afisare — `cabinet_fisa_cont()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 57 | Registrul-jurnal (OMFP 2634/2015, cod 14-1-1), pe luna ceruta | `GET /tenants/{tenant_id}/jurnal` · `cere_cabinet` | citire / afisare — `tenant_jurnal()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 58 | jurnal creeaza | `POST /tenants/{tenant_id}/jurnal` · `cere_cabinet` | creare sau executie — `jurnal_creeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 59 | jurnal sterge | `DELETE /tenants/{tenant_id}/jurnal/{nota_id}` · `cere_cabinet` | stergere — `jurnal_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 60 | jurnal editeaza | `PUT /tenants/{tenant_id}/jurnal/{nota_id}` · `cere_cabinet` | modificare — `jurnal_editeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 61 | RUPE legătura notă↔factură, cu URMĂ | `POST /tenants/{tenant_id}/jurnal/{nota_id}/dezleaga` · rol `admin_firma` | creare sau executie — `jurnal_dezleaga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 62 | jurnal valideaza | `POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza` · rol `admin_firma` | creare sau executie — `jurnal_valideaza()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 63 | corp: {data, operatie dividend/regularizare/imprumut, descriere?, + dividend{brut, interimar?, cu_plata?}; regularizare… | `POST /tenants/{tenant_id}/nota-asociati` · `cere_cabinet` | creare sau executie — `nota_asociati()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 64 | corp: {data, operatie avans_platit/regularizare_platit/avans_incasat/ regularizare_incasat, suma (fara TVA), cota?, des… | `POST /tenants/{tenant_id}/nota-avans` · `cere_cabinet` | creare sau executie — `nota_avans()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 65 | corp: {data, fel incasare/distribuire, suma, sursa card/numerar (incasare) / banca/casa (distribuire), descriere?} | `POST /tenants/{tenant_id}/nota-bacsis` · `cere_cabinet` | creare sau executie — `nota_bacsis()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 66 | corp: {data, fel comodat/chirie_platita/chirie_incasata/refacturare, descriere?, cota?, + comodat{valoare, moment primi… | `POST /tenants/{tenant_id}/nota-chirie` · `cere_cabinet` | creare sau executie — `nota_chirie()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 67 | corp: {data, fel zilier/cenzor/mandat, brut, sursa casa/banca, descriere?} | `POST /tenants/{tenant_id}/nota-contract-special` · `cere_cabinet` | creare sau executie — `nota_contract_special()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 68 | corp: {data, operatie primire/dobanda/plata/restanta/garantie, tip lung/scurt, descriere?, + pe operatie: primire{suma}… | `POST /tenants/{tenant_id}/nota-credit` · `cere_cabinet` | creare sau executie — `nota_credit()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 69 | corp: {data, fel avans/decont/plafon, descriere?, sursa casa/banca, + avans{suma}; decont{avans, diurna?, transport?, c… | `POST /tenants/{tenant_id}/nota-decont-deplasare` · `cere_cabinet` | creare sau executie — `nota_decont_deplasare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 70 | corp: {data, operatie plus/plus_mf/minus/casare, descriere?, + plus{valoare, cont_stoc?}; plus_mf{valoare, cont_imobili… | `POST /tenants/{tenant_id}/nota-inventariere` · `cere_cabinet` | creare sau executie — `nota_inventariere()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 71 | corp: {data, tip primire/rata/reziduala/operational, descriere?, cota?, + campuri pe tip: primire{valoare_capital, doba… | `POST /tenants/{tenant_id}/nota-leasing` · `cere_cabinet` | creare sau executie — `nota_leasing()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 72 | corp: {data, operatie vanzare_activ/partaj, descriere?, + vanzare_activ{pret, valoare_bruta, amortizare_cumulata, contu… | `POST /tenants/{tenant_id}/nota-lichidare` · `cere_cabinet` | creare sau executie — `nota_lichidare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 73 | corp: {data, operatie achizitie/dare_folosinta/scoatere, valoare, cota?, descriere?} | `POST /tenants/{tenant_id}/nota-obiect-inventar` · `cere_cabinet` | creare sau executie — `nota_obiect_inventar()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 74 | corp: {data, operatie venit/scutire, descriere?, + venit{suma, fel cotizatie/contributie/donatie/sponsorizare/financiar… | `POST /tenants/{tenant_id}/nota-ong` · `cere_cabinet` | creare sau executie — `nota_ong()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 75 | corp: {data, valoare_intrari, procent_limita (coef | `POST /tenants/{tenant_id}/nota-perisabilitati` · `cere_cabinet` | creare sau executie — `nota_perisabilitati()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 76 | corp: {data, operatie obtinere/pic/vanzare, descriere?, + obtinere{cost_standard, cost_efectiv?}; pic{suma, moment cons… | `POST /tenants/{tenant_id}/nota-productie` · `cere_cabinet` | creare sau executie — `nota_productie()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 77 | corp: {data, fel creanta/provizion/stoc, actiune constituire/reluare, suma, descriere?, + creanta{zile_depasire?, garan… | `POST /tenants/{tenant_id}/nota-provizion` · `cere_cabinet` | creare sau executie — `nota_provizion_ep()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 78 | corp: {data, operatie achizitie/vanzare/restituire/autofactura/virare, descriere?, + nr_ambalaje/suma, sursa casa/banca… | `POST /tenants/{tenant_id}/nota-sgr` · `cere_cabinet` | creare sau executie — `nota_sgr()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 79 | corp: {data, suma, mod contract/plata, descriere?, + optional pentru calcul credit: cifra_afaceri, impozit_profit, tip_… | `POST /tenants/{tenant_id}/nota-sponsorizare` · `cere_cabinet` | creare sau executie — `nota_sponsorizare_ep()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 80 | corp: {data, fel exploatare/investitii/reluare, descriere?, + exploatare/investitii{suma, moment drept/incasare}; relua… | `POST /tenants/{tenant_id}/nota-subventie` · `cere_cabinet` | creare sau executie — `nota_subventie()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 81 | corp: {data, sens incasare/plata, suma_incasata, cota?, descriere?} | `POST /tenants/{tenant_id}/nota-tva-incasare` · `cere_cabinet` | creare sau executie — `nota_tva_incasare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 82 | tenant plan conturi lista | `GET /tenants/{tenant_id}/plan-conturi` · `cere_context` | citire / afisare — `tenant_plan_conturi_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 83 | tenant plan conturi adauga | `POST /tenants/{tenant_id}/plan-conturi` · rol `admin_firma` | creare sau executie — `tenant_plan_conturi_adauga()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 84 | [lista 3, 30.08.2026] Registrul-inventar (cod 14-1-2), al doilea registru obligatoriu | `GET /tenants/{tenant_id}/registru-inventar` · `cere_cabinet` | citire / afisare — `registru_inventar_citeste()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 85 | Inscrie un rand | `POST /tenants/{tenant_id}/registru-inventar` · `cere_cabinet` | creare sau executie — `registru_inventar_adauga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |
| 86 | Coloana 3 PROPUSA din balanta — soldurile pe cont, ca sa nu fie retastate | `GET /tenants/{tenant_id}/registru-inventar/propunere` · `cere_cabinet` | citire / afisare — `registru_inventar_propunere()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 3 |

### T06 — Importul de e-Factura și transmiterea prin SPV (7)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 87 | Facturi primite din SPV de VALIDAT (four-eyes): ciorne parsate + cont sugerat | `GET /tenants/{tenant_id}/facturi-primite` · `cere_context` | citire / afisare — `facturi_primite_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 88 | Respinge o factura primita: status=respinsa + motiv | `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/respinge` · `cere_context` | creare sau executie — `factura_primita_respinge()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 89 | FOUR-EYES: omul valideaza ciorna importata de cron -> creeaza cheltuiala (factura primita) + leaga factura_id + status=… | `POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza` · rol `admin_firma` | creare sau executie — `factura_primita_valideaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 90 | XML-ul brut arhivat (la click, nu in fata). | `GET /tenants/{tenant_id}/facturi-primite/{primita_id}/xml` · `cere_context` | citire / afisare — `factura_primita_xml()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 91 | Trimite o factura emisa in SPV (F126/F160) | `POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv` · rol `admin_firma` | creare sau executie — `factura_trimite_spv()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 92 | Upload XML/ZIP e-Factura | `POST /tenants/{tenant_id}/import-efactura` · `cere_cabinet` | creare sau executie — `import_efactura()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 93 | Starea SPV cea mai recenta per factura (pentru semaforul butonului) | `GET /tenants/{tenant_id}/trimiteri-spv` · `cere_context` | citire / afisare — `facturi_trimiteri_spv()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T07 — Extrasul bancar și potrivirea (7)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 94 | banca parse extras | `POST /tenants/{tenant_id}/banca/parse-extras` · `cere_cabinet` | creare sau executie — `banca_parse_extras()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 95 | banca rec lista | `GET /tenants/{tenant_id}/banca/reconciliere` · `cere_cabinet` | citire / afisare — `banca_rec_lista()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 96 | banca rec facturi | `GET /tenants/{tenant_id}/banca/reconciliere/facturi-deschise` · `cere_cabinet` | citire / afisare — `banca_rec_facturi()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 97 | banca rec import | `POST /tenants/{tenant_id}/banca/reconciliere/import` · `cere_cabinet` | creare sau executie — `banca_rec_import()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 98 | banca rec conteaza | `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza` · `cere_cabinet` | creare sau executie — `banca_rec_conteaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 99 | banca rec ignora | `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora` · `cere_cabinet` | creare sau executie — `banca_rec_ignora()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 100 | banca rec reactiveaza | `POST /tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza` · `cere_cabinet` | creare sau executie — `banca_rec_reactiveaza()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T08 — NIR și recepția (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 101 | stocuri lista | `GET /tenants/{tenant_id}/stocuri/nir` · `cere_cabinet` | citire / afisare — `stocuri_lista()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 102 | stocuri adauga | `POST /tenants/{tenant_id}/stocuri/nir` · `cere_cabinet` | creare sau executie — `stocuri_adauga()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |

### T09 — Casa și registrul de casă (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 103 | casa adauga | `POST /tenants/{tenant_id}/casa/operatiuni` · `cere_cabinet` | creare sau executie — `casa_adauga()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 104 | casa sterge | `DELETE /tenants/{tenant_id}/casa/operatiuni/{op_id}` · `cere_cabinet` | stergere — `casa_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 105 | casa registru | `GET /tenants/{tenant_id}/casa/registru` · `cere_cabinet` | citire / afisare — `casa_registru()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T10 — Inventarierea (5)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 106 | Sectiunea Assets SAF-T pentru anul dat (D406 anual | `GET /tenants/{tenant_id}/d406-active` · `cere_cabinet` | citire / afisare — `d406_active_xml()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 107 | Sectiunea PhysicalStock SAF-T pe perioada (D406 la cerere ANAF) | `GET /tenants/{tenant_id}/d406-stocuri` · `cere_cabinet` | citire / afisare — `d406_stocuri_xml()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 108 | rip inventar | `GET /tenants/{tenant_id}/rip/inventar/{an}` · `cere_cabinet` | citire / afisare — `rip_inventar()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 109 | cv inventar | `POST /tenants/{tenant_id}/stocuri/inventar` · `cere_cabinet` | creare sau executie — `cv_inventar()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 110 | Compara soldul contabil (solduri_initiale + note validate) pe fiecare cont de stoc folosit in articole cu valoarea insu… | `GET /tenants/{tenant_id}/verificare-stocuri` · `cere_cabinet` | citire / afisare — `verificare_stocuri()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T11 — Închiderea lunii (7)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 111 | [cap.23, 21.08.2026] Starea INCHIDERII lunii pe domeniul `facturi`: confirmat / cine / cand, daca se poate confirma acu… | `GET /tenants/{tenant_id}/facturi/perioada` · `cere_context` | citire / afisare — `tenant_facturi_perioada()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 112 | [cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate sprijini pe ea cand s… | `POST /tenants/{tenant_id}/facturi/perioada/confirma` · rol `admin_firma` | creare sau executie — `tenant_facturi_perioada_confirma()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 113 | [cap.23] Redeschide luna (o corectie de facturi cere redeschiderea) | `POST /tenants/{tenant_id}/facturi/perioada/redeschide` · rol `admin_firma` | creare sau executie — `tenant_facturi_perioada_redeschide()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 114 | perioada deblocheaza | `DELETE /tenants/{tenant_id}/perioade-blocate` · rol `admin_firma` | stergere — `perioada_deblocheaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 115 | perioade blocate lista | `GET /tenants/{tenant_id}/perioade-blocate` · `cere_cabinet` | citire / afisare — `perioade_blocate_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 116 | perioada blocheaza | `POST /tenants/{tenant_id}/perioade-blocate` · rol `admin_firma` | creare sau executie — `perioada_blocheaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 117 | perioade istoric | `GET /tenants/{tenant_id}/perioade-blocate/istoric` · `cere_cabinet` | citire / afisare — `perioade_istoric()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T12 — Închiderea anului și situațiile financiare (5)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 118 | [R3, lista 3, 30.08.2026] CATEGORIA DE MARIME — precondiția situațiilor financiare | `GET /tenants/{tenant_id}/categorie-marime` · `cere_cabinet` | citire / afisare — `cabinet_categorie_marime()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 119 | s1003 valideaza | `POST /tenants/{tenant_id}/s1003-valideaza` · `cere_cabinet` | creare sau executie — `s1003_valideaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 120 | s1003 xml | `GET /tenants/{tenant_id}/s1003-xml` · `cere_cabinet` | citire / afisare — `s1003_xml()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 121 | s1005 valideaza | `POST /tenants/{tenant_id}/s1005-valideaza` · `cere_cabinet` | creare sau executie — `s1005_valideaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 122 | s1005 xml | `GET /tenants/{tenant_id}/s1005-xml` · `cere_cabinet` | citire / afisare — `s1005_xml()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T13 — Trecerea de regim fiscal (8)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 123 | Lista firmelor cabinetului cu status vector (completat sau nu). | `GET /migrare/vector` · `cere_cabinet` | citire / afisare — `migrare_vector_status()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 124 | firma profil get | `GET /tenants/{tenant_id}/firma-profil` · `cere_context` | citire / afisare — `firma_profil_get()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 125 | firma profil date | `GET /tenants/{tenant_id}/firma-profil/date` · `cere_context` | citire / afisare — `firma_profil_date()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 126 | firma profil date salveaza | `POST /tenants/{tenant_id}/firma-profil/date` · `cere_cabinet` | creare sau executie — `firma_profil_date_salveaza()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 127 | firma profil model | `POST /tenants/{tenant_id}/firma-profil/model` · `cere_context` | creare sau executie — `firma_profil_model()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 128 | firma profil regim tva | `POST /tenants/{tenant_id}/firma-profil/regim-tva` · rol `admin_firma` | creare sau executie — `firma_profil_regim_tva()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 129 | vector citeste | `GET /tenants/{tenant_id}/vector` · `cere_cabinet` | citire / afisare — `vector_citeste()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 130 | vector salveaza | `POST /tenants/{tenant_id}/vector` · rol `admin_firma` | creare sau executie — `vector_salveaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T14 — Preluarea unei firme (32)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 131 | F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior (balanta echilibrata, d… | `POST /control-fiscal/{tenant_id}/audit-preluare` · rol `admin_firma` | creare sau executie — `control_fiscal_audit_preluare()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 132 | migrare asociati status | `GET /migrare/asociati` · `cere_cabinet` | citire / afisare — `migrare_asociati_status()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 133 | Primește un CSV/XLSX, extrage CUI-urile și le validează la ANAF. | `POST /migrare/fisier` · `cere_cabinet` | creare sau executie — `migrare_fisier()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 134 | Creează câte un tenant pentru fiecare firmă selectată | `POST /migrare/importa` · rol `admin_firma` | creare sau executie — `migrare_importa()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 135 | Primește un fișier (.csv/.xlsx), extrage CUI-urile și le validează la ANAF. | `POST /migrare/incarca` · `cere_cabinet` | creare sau executie — `migrare_incarca()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 136 | migrare istoric status | `GET /migrare/istoric-declaratii` · `cere_cabinet` | citire / afisare — `migrare_istoric_status()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 137 | migrare mijloace status | `GET /migrare/mijloace-fixe` · `cere_cabinet` | citire / afisare — `migrare_mijloace_status()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 138 | Lista firmelor cabinetului cu status parteneri (are/n-are, cati parteneri). | `GET /migrare/parteneri` · `cere_cabinet` | citire / afisare — `migrare_parteneri_status()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 139 | migrare plan conturi status | `GET /migrare/plan-conturi` · `cere_cabinet` | citire / afisare — `migrare_plan_conturi_status()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 140 | Lista firmelor cabinetului cu status salariati (are/n-are, cati). | `GET /migrare/salariati` · `cere_cabinet` | citire / afisare — `migrare_salariati_status()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 141 | Lista firmelor cabinetului cu status solduri (are/n-are, câte conturi). | `GET /migrare/solduri` · `cere_cabinet` | citire / afisare — `migrare_solduri_status()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 142 | Starea fiecărui strat de migrare + reminderul (straturi în lucru). | `GET /migrare/status` · `cere_cabinet` | citire / afisare — `migrare_status_citeste()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 143 | Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru). | `POST /migrare/status` · rol `admin_firma` | creare sau executie — `migrare_status_seteaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 144 | [p_pfa_rip 20.07] Straturile de migrare aplicabile unui regim (srl/pfa) | `GET /migrare/straturi` · `cere_cabinet` | citire / afisare — `migrare_straturi_aplicabile()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 145 | Verifică o listă de CUI-uri la ANAF; întoarce denumirea + status. | `POST /migrare/valideaza` · `cere_cabinet` | creare sau executie — `migrare_valideaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 146 | articole import salveaza | `POST /tenants/{tenant_id}/articole-import` · rol `admin_firma` | creare sau executie — `articole_import_salveaza()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 147 | articole import incarca | `POST /tenants/{tenant_id}/articole-import/incarca` · `cere_cabinet` | creare sau executie — `articole_import_incarca()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 148 | asociati import salveaza | `POST /tenants/{tenant_id}/asociati-import` · rol `admin_firma` | creare sau executie — `asociati_import_salveaza()` | da | probat invalid 03.09.2026 — **golea la intrare vidă, reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1b |
| 149 | asociati import incarca | `POST /tenants/{tenant_id}/asociati-import/incarca` · `cere_cabinet` | creare sau executie — `asociati_import_incarca()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 150 | mijloace import salveaza | `POST /tenants/{tenant_id}/mijloace-fixe-import` · rol `admin_firma` | creare sau executie — `mijloace_import_salveaza()` | nu | probat invalid 03.09.2026 — **golea la intrare vidă, reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1b |
| 151 | mijloace import incarca | `POST /tenants/{tenant_id}/mijloace-fixe-import/incarca` · `cere_cabinet` | creare sau executie — `mijloace_import_incarca()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 152 | Rezumatul partenerilor salvati pentru o firma. | `GET /tenants/{tenant_id}/parteneri` · `cere_cabinet` | citire / afisare — `parteneri_rezumat()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 153 | Salveaza soldurile partenerilor unei firme (inlocuieste ce era). | `POST /tenants/{tenant_id}/parteneri` · rol `admin_firma` | creare sau executie — `parteneri_salveaza()` | nu | probat invalid 03.09.2026 — **golea la intrare vidă, reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 1b |
| 154 | Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta. | `POST /tenants/{tenant_id}/parteneri/incarca` · `cere_cabinet` | creare sau executie — `parteneri_incarca()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 155 | retete import salveaza | `POST /tenants/{tenant_id}/retete-import` · rol `admin_firma` | creare sau executie — `retete_import_salveaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 156 | retete import incarca | `POST /tenants/{tenant_id}/retete-import/incarca` · `cere_cabinet` | creare sau executie — `retete_import_incarca()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 157 | Import registru incasari-plati la preluarea unui PFA | `POST /tenants/{tenant_id}/rip-import/incarca` · rol `admin_firma` | creare sau executie — `rip_import_incarca()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 158 | Importa salariatii cu CNP valid (upsert pe CNP) | `POST /tenants/{tenant_id}/salariati-import` · rol `admin_firma` | creare sau executie — `salariati_import_salveaza()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 159 | Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza). | `POST /tenants/{tenant_id}/salariati-import/incarca` · `cere_cabinet` | creare sau executie — `salariati_import_incarca()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 160 | Rezumatul soldurilor salvate pentru o firmă. | `GET /tenants/{tenant_id}/solduri` · `cere_cabinet` | citire / afisare — `solduri_rezumat()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 161 | Salvează soldurile inițiale ale unei firme (înlocuiește ce era). | `POST /tenants/{tenant_id}/solduri` · rol `admin_firma` | creare sau executie — `solduri_salveaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |
| 162 | Parsează o balanță și întoarce preview (nu salvează). | `POST /tenants/{tenant_id}/solduri/incarca` · `cere_cabinet` | creare sau executie — `solduri_incarca()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 6 |

### T15 — Salariatul — angajare, contract, adeverință, REGES (17)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 163 | contracte marcaje | `GET /contracte/marcaje` · `cere_cabinet` | citire / afisare — `contracte_marcaje()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 164 | [F137] Cauta in nomenclatorul COR national dupa cod (prefix) sau denumire (substring, diacritic-insensitiv) | `GET /cor` · `cere_context` | citire / afisare — `cor_cauta()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 165 | contracte genereaza | `POST /tenants/{tenant_id}/contracte/genereaza` · rol `admin_firma` | creare sau executie — `contracte_genereaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 166 | contracte sabloane lista | `GET /tenants/{tenant_id}/contracte/sabloane` · `cere_cabinet` | citire / afisare — `contracte_sabloane_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 167 | contracte sabloane salveaza | `POST /tenants/{tenant_id}/contracte/sabloane` · `cere_cabinet` | creare sau executie — `contracte_sabloane_salveaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 168 | contracte sabloane sterge | `DELETE /tenants/{tenant_id}/contracte/sabloane/{sid}` · `cere_cabinet` | stergere — `contracte_sabloane_sterge()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 169 | tenant prapastie salariu | `POST /tenants/{tenant_id}/prapastie-salariu` · `cere_cabinet` | creare sau executie — `tenant_prapastie_salariu()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 170 | corp: {username, parola, mediu test/prod} | `POST /tenants/{tenant_id}/reges-config` · rol `admin_firma` | creare sau executie — `reges_config()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 171 | Citeste+consuma un mesaj din coada REGES; salveaza referintele in reges_mesaje. | `POST /tenants/{tenant_id}/reges-poll` · rol `admin_firma` | creare sau executie — `reges_poll()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 172 | corp: {salariat_id, adresa, contract {numar, data_contract, data_inceput, salariu, cor, ...}?} | `POST /tenants/{tenant_id}/reges-trimite-salariat` · rol `admin_firma` | creare sau executie — `reges_trimite_salariat()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 173 | salariati lista | `GET /tenants/{tenant_id}/salariati` · `cere_cabinet` | citire / afisare — `salariati_lista()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 174 | salariat creeaza | `POST /tenants/{tenant_id}/salariati` · rol `admin_firma/angajat` | creare sau executie — `salariat_creeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 175 | salariat sterge | `DELETE /tenants/{tenant_id}/salariati/{salariat_id}` · rol `admin_firma/angajat` | stergere — `salariat_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 176 | salariat detalii | `GET /tenants/{tenant_id}/salariati/{salariat_id}` · `cere_cabinet` | citire / afisare — `salariat_detalii()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 177 | salariat actualizeaza | `PUT /tenants/{tenant_id}/salariati/{salariat_id}` · rol `admin_firma/angajat` | modificare — `salariat_actualizeaza()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 178 | F136: adeverinta de salariat (art | `POST /tenants/{tenant_id}/salariati/{salariat_id}/adeverinta` · rol `admin_firma` | creare sau executie — `tenant_adeverinta()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 179 | [F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) | `PUT /tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar` · rol `admin_firma/angajat` | modificare — `salariat_beneficiu_lunar()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T16 — Pontajul (4)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 180 | [cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv lucrate) | `POST /tenants/{tenant_id}/pontaj/confirma` · rol `admin_firma` | creare sau executie — `tenant_pontaj_confirma()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 181 | F135: grila lunara de pontaj (informativ) | `GET /tenants/{tenant_id}/salariati/{salariat_id}/pontaj` · `cere_context` | citire / afisare — `tenant_pontaj_get()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 182 | F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia). | `PUT /tenants/{tenant_id}/salariati/{salariat_id}/pontaj` · `cere_context` | modificare — `tenant_pontaj_set()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 183 | Zile lucratoare (L-V, fara sarbatori legale) intre doua date - auto-calcul CM (OUG 158/2005 art.10) | `GET /util/zile-lucratoare` · `cere_context` | citire / afisare — `util_zile_lucratoare()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T17 — Plata salariilor — fișierul către bancă (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 184 | [F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download) | `POST /tenants/{tenant_id}/plata-salarii-fisier` · rol `admin_firma` | creare sau executie — `tenant_plata_salarii_fisier()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 185 | [F134] Sumar inainte de generarea fisierului SEPA: cate plati, total, cine e exclus (fara IBAN). | `GET /tenants/{tenant_id}/plata-salarii-preview` · `cere_cabinet` | citire / afisare — `tenant_plata_salarii_preview()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T18 — Chitanța și încasarea (6)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 186 | Pagina mock: confirma plata (pana la integrarea provider real). | `GET /public/plata/{ref}` · fără gardă | citire / afisare — `plata_pagina()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 187 | plata confirma | `POST /public/plata/{ref}/confirma` · fără gardă | creare sau executie — `plata_confirma()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 188 | chitante lista | `GET /tenants/{tenant_id}/chitante` · `cere_context` | citire / afisare — `chitante_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 189 | Emite chitanta (cod 14-4-1, Ordin 2634/2015) pentru incasare in numerar: numerotare pe serie per firma + operatiune in … | `POST /tenants/{tenant_id}/chitante` · rol `admin_firma` | creare sau executie — `chitanta_emite()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 190 | chitanta pdf | `GET /tenants/{tenant_id}/chitante/{chitanta_id}/pdf` · rol `admin_firma` | citire / afisare — `chitanta_pdf()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 191 | factura link plata | `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata` · rol `admin_firma` | creare sau executie — `factura_link_plata()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T19 — Scadențarul și notificările de scadență (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 192 | F131: scadentarul facturilor emise neincasate (restante/scade curand/in termen) + fisa client agregata | `GET /tenants/{tenant_id}/scadentar` · `cere_context` | citire / afisare — `scadentar_get()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 193 | F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF). | `PUT /tenants/{tenant_id}/scadentar/opt-in` · rol `admin_firma` | modificare — `scadentar_optin()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T20 — Mișcarea de stoc — intrare, ieșire, transfer, reclasificare (12)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 194 | cv analitica | `GET /tenants/{tenant_id}/stocuri/analitica` · `cere_cabinet` | citire / afisare — `cv_analitica()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 195 | cv articole | `GET /tenants/{tenant_id}/stocuri/articole` · `cere_cabinet` | citire / afisare — `cv_articole()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 196 | cv barcode set | `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode` · `cere_cabinet` | creare sau executie — `cv_barcode_set()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 197 | cv fisa | `GET /tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa` · `cere_cabinet` | citire / afisare — `cv_fisa()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 198 | cv nivel minim | `POST /tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim` · `cere_cabinet` | creare sau executie — `cv_nivel_minim()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 199 | cv barcode gaseste | `GET /tenants/{tenant_id}/stocuri/barcode/{cod}` · `cere_cabinet` | citire / afisare — `cv_barcode_gaseste()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 200 | stocuri descarcare | `POST /tenants/{tenant_id}/stocuri/descarcare` · `cere_cabinet` | creare sau executie — `stocuri_descarcare()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 201 | cv iesire | `POST /tenants/{tenant_id}/stocuri/iesire` · `cere_cabinet` | creare sau executie — `cv_iesire()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 202 | cv intrare | `POST /tenants/{tenant_id}/stocuri/intrare` · `cere_cabinet` | creare sau executie — `cv_intrare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 203 | cv locatii | `GET /tenants/{tenant_id}/stocuri/locatii` · `cere_cabinet` | citire / afisare — `cv_locatii()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 204 | cv reclasificare | `POST /tenants/{tenant_id}/stocuri/reclasificare` · `cere_cabinet` | creare sau executie — `cv_reclasificare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 205 | cv transfer | `POST /tenants/{tenant_id}/stocuri/transfer` · `cere_cabinet` | creare sau executie — `cv_transfer()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T21 — Rețeta și producția (9)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 206 | produse lista | `GET /tenants/{tenant_id}/produse` · `cere_context` | citire / afisare — `produse_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 207 | produse creeaza | `POST /tenants/{tenant_id}/produse` · `cere_cabinet` | creare sau executie — `produse_creeaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 208 | produse potriveste | `POST /tenants/{tenant_id}/produse/potriveste` · `cere_context` | creare sau executie — `produse_potriveste()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 209 | produse sterge | `DELETE /tenants/{tenant_id}/produse/{produs_id}` · `cere_cabinet` | stergere — `produse_sterge()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 210 | produse actualizeaza | `PUT /tenants/{tenant_id}/produse/{produs_id}` · `cere_cabinet` | modificare — `produse_actualizeaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 211 | retete lista | `GET /tenants/{tenant_id}/retete` · `cere_cabinet` | citire / afisare — `retete_lista()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 212 | retete salveaza | `POST /tenants/{tenant_id}/retete` · `cere_cabinet` | creare sau executie — `retete_salveaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 213 | retete descarca | `POST /tenants/{tenant_id}/retete/descarca` · `cere_cabinet` | creare sau executie — `retete_descarca()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 214 | retete sterge | `DELETE /tenants/{tenant_id}/retete/{reteta_id}` · `cere_cabinet` | stergere — `retete_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T22 — Mijlocul fix și amortizarea (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 215 | Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ. | `POST /tenants/{tenant_id}/amortizare` · rol `admin_firma` | creare sau executie — `tenant_amortizare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 216 | [ecran_mf_v1 14.08.2026; amortizare pe metoda 16.08.2026] Registrul mijloacelor fixe ale firmei: valoare, amortizat la … | `GET /tenants/{tenant_id}/mijloace-fixe` · `cere_cabinet` | citire / afisare — `tenant_mijloace_fixe()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 217 | corp: {data, operatie reevaluare/surplus, + reevaluare{mijloc_fix_id, valoare_justa, sold_105_activ?, pierdere_655_ante… | `POST /tenants/{tenant_id}/reevaluare-imobilizare` · `cere_cabinet` | creare sau executie — `reevaluare_imobilizare()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T23 — Bonul de la client — portalul și decontul (9)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 218 | Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc | `POST /portal/bon` · `cere_context` | creare sau executie — `portal_bon()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 219 | Clientul reface poza -> draftul (status='extras') si pozele lui se sterg. | `DELETE /portal/bon/{bon_id}` · `cere_context` | stergere — `portal_bon_sterge()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 220 | Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil. | `POST /portal/bon/{bon_id}/confirma` · `cere_context` | creare sau executie — `portal_bon_confirma()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 221 | portal bon imagine | `GET /portal/bon/{bon_id}/imagine/{n}` · `cere_context` | citire / afisare — `portal_bon_imagine()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 222 | bonuri de verificat | `GET /tenants/{tenant_id}/bonuri/de-verificat` · `cere_cabinet` | citire / afisare — `bonuri_de_verificat()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 223 | bon aproba | `POST /tenants/{tenant_id}/bonuri/{bon_id}/aproba` · rol `admin_firma` | creare sau executie — `bon_aproba()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 224 | Pentru o chitanta: facturile PRIMITE, neplatite, care ar putea fi stinse de ea | `GET /tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate` · `cere_cabinet` | citire / afisare — `bon_facturi_candidate()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 225 | cabinet bon imagine | `GET /tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}` · rol `admin_firma` | citire / afisare — `cabinet_bon_imagine()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 226 | Chitanta certificata de contabil: plata furnizor prin Registrul de casa (casa_api.adauga -> 401=5311 ciorna + operatiun… | `POST /tenants/{tenant_id}/bonuri/{bon_id}/stinge` · rol `admin_firma` | creare sau executie — `chitanta_stinge()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T24 — Bonul fiscal și raportul Z (AMEF, horeca) (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 227 | Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA | `POST /tenants/{tenant_id}/horeca/import-amef` · `cere_cabinet` | creare sau executie — `horeca_import_amef()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 228 | horeca raport z | `POST /tenants/{tenant_id}/horeca/raport-z` · rol `admin_firma` | creare sau executie — `horeca_raport_z()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T25 — Comanda din magazinul online (WooCommerce) (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 229 | wc config get | `GET /tenants/{tenant_id}/woocommerce/config` · `cere_context` | citire / afisare — `wc_config_get()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 230 | wc config | `PUT /tenants/{tenant_id}/woocommerce/config` · rol `admin_firma` | modificare — `wc_config()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 231 | wc sinc | `POST /tenants/{tenant_id}/woocommerce/sincronizeaza` · rol `admin_firma` | creare sau executie — `wc_sinc()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T26 — Registratura (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 232 | registratura lista | `GET /tenants/{tenant_id}/registratura` · `cere_cabinet` | citire / afisare — `registratura_lista()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 233 | registratura creeaza | `POST /tenants/{tenant_id}/registratura` · `cere_cabinet` | creare sau executie — `registratura_creeaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |

### T27 — e-Transport (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 234 | etransport xml | `POST /tenants/{tenant_id}/etransport-xml` · `cere_cabinet` | creare sau executie — `etransport_xml()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 235 | Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp -> idempotency -> va… | `POST /tenants/{tenant_id}/etransport/trimite` · rol `admin_firma` | creare sau executie — `etransport_trimite()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 7 |
| 236 | UIT-uri trimise + semafor de TIMP (valabilitate UIT) SEPARAT de semaforul de trimitere | `GET /tenants/{tenant_id}/etransport/trimiteri` · `cere_context` | citire / afisare — `etransport_trimiteri_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T28 — Operațiunile intracomunitare, VIES și Intrastat (12)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 237 | public verifica cui | `GET /public/verifica-cui/{cui}` · fără gardă | citire / afisare — `public_verifica_cui()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 238 | AIC bunuri/servicii primite (art | `POST /tenants/{tenant_id}/achizitie-ic` · rol `admin_firma` | creare sau executie — `achizitie_ic()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 239 | Operatiunile auto-derivate (cu tipul curent) + liniile manuale, pt ecranul de clasificare. | `GET /tenants/{tenant_id}/d390-clasificare` · `cere_cabinet` | citire / afisare — `d390_clasificare_stare()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 240 | Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}. | `POST /tenants/{tenant_id}/d390-clasificare/manual` · `cere_cabinet` | creare sau executie — `d390_manual_adauga()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 241 | d390 manual sterge | `DELETE /tenants/{tenant_id}/d390-clasificare/manual/{mid}` · `cere_cabinet` | stergere — `d390_manual_sterge()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 242 | Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}. | `PUT /tenants/{tenant_id}/d390-clasificare/reclasificare` · `cere_cabinet` | modificare — `d390_reclasificare()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 243 | Monitor praguri Intrastat (Ordin INS 1604/2025, 1.000.000 lei/flux): introduceri = facturi primite de la parteneri UE; … | `GET /tenants/{tenant_id}/intrastat-praguri` · `cere_cabinet` | citire / afisare — `intrastat_praguri()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 244 | [lista 3, 30.08.2026] Cele doua registre cerute de art | `GET /tenants/{tenant_id}/registre-art321/{fel}` · `cere_cabinet` | citire / afisare — `registre_art321_citeste()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 245 | Inscrie un rand | `POST /tenants/{tenant_id}/registre-art321/{fel}` · `cere_cabinet` | creare sau executie — `registre_art321_adauga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 246 | LIC bunuri (art | `POST /tenants/{tenant_id}/vanzare-ic` · `cere_cabinet` | creare sau executie — `vanzare_ic()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 247 | verifica cui | `GET /tenants/{tenant_id}/verifica-cui/{cui}` · `cere_context` | citire / afisare — `verifica_cui()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 248 | Verifica un cod TVA UE in VIES (API oficial CE). | `GET /tenants/{tenant_id}/verifica-vies` · `cere_context` | citire / afisare — `verifica_vies_ep()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |

### T29 — Regimurile speciale de TVA — marjă, aur, agricultori, taxare inversă (11)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 249 | corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru, agricultor?, descriere?} | `POST /tenants/{tenant_id}/achizitie-agricultor` · `cere_cabinet` | creare sau executie — `achizitie_agricultor()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 250 | corp: {data, denumire, valoare (fara TVA), tip software/licenta/brevet/ dezvoltare/constituire, dnf_luni?, cota?, cod?} | `POST /tenants/{tenant_id}/achizitie-necorporala` · rol `admin_firma` | creare sau executie — `achizitie_necorporala()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 251 | Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2) | `POST /tenants/{tenant_id}/achizitie-neinregistrat` · rol `admin_firma` | creare sau executie — `achizitie_neinregistrat()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 252 | corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?, furnizor_platitor_tva, descriere?} | `POST /tenants/{tenant_id}/achizitie-taxare-inversa` · rol `admin_firma` | creare sau executie — `achizitie_taxare_inversa()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 253 | corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?} | `POST /tenants/{tenant_id}/export-extracomunitar` · `cere_cabinet` | creare sau executie — `export_extracomunitar()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 254 | corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?, cota?, certificat_amanare?, cont_destinat… | `POST /tenants/{tenant_id}/import-extracomunitar` · `cere_cabinet` | creare sau executie — `import_extracomunitar()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 5 |
| 255 | tip: secondhand/turism; luna: YYYY-MM | `GET /tenants/{tenant_id}/jurnal-marja` · `cere_cabinet` | citire / afisare — `jurnal_marja()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 256 | corp: {data, pret (fara taxa), descriere?} | `POST /tenants/{tenant_id}/vanzare-agricultor` · `cere_cabinet` | creare sau executie — `vanzare_agricultor()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 257 | corp: {data, tip lingou/plancheta/moneda, puritate, an_emisie?, pret_unitar?, valoare_aur?, suma, optiune_taxare?, cali… | `POST /tenants/{tenant_id}/vanzare-aur-investitii` · `cere_cabinet` | creare sau executie — `vanzare_aur_investitii()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 258 | corp: {data, pret_vanzare, pret_cumparare, cota?, descriere?} | `POST /tenants/{tenant_id}/vanzare-marja` · `cere_cabinet` | creare sau executie — `vanzare_marja()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 259 | corp: {data, calitate_client PF/PJ, locuri [RO/UE/NONUE], optiune_normal?, intermediar?, cota?, descriere?} + per regim… | `POST /tenants/{tenant_id}/vanzare-marja-turism` · `cere_cabinet` | creare sau executie — `vanzare_marja_turism()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |

### T30 — Operațiunile în valută (2)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 260 | Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765 | `POST /tenants/{tenant_id}/decontare-valuta` · `cere_cabinet` | creare sau executie — `decontare_valuta()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 261 | Reevaluare lunara solduri valuta (OMFP 1802 pct | `POST /tenants/{tenant_id}/reevaluare-valuta` · `cere_cabinet` | creare sau executie — `reevaluare_valuta()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |

### T31 — Completările manuale la o declarație (D300, D301) (8)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 262 | Randurile manuale ale perioadei + randurile inca disponibile de adaugat (allow-list minus auto-derivate minus deja intr… | `GET /tenants/{tenant_id}/d300-manual` · `cere_cabinet` | citire / afisare — `d300_manual_lista()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 263 | Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}. | `POST /tenants/{tenant_id}/d300-manual` · `cere_cabinet` | creare sau executie — `d300_manual_adauga()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 264 | d300 manual sterge | `DELETE /tenants/{tenant_id}/d300-manual/{rid}` · `cere_cabinet` | stergere — `d300_manual_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 265 | Operatiunile lunii + nomenclatoare (tipuri, valute, cote period-aware) pt ecranul D301. | `GET /tenants/{tenant_id}/d301-operatiuni` · `cere_cabinet` | citire / afisare — `d301_operatiuni_lista()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 266 | Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}. | `POST /tenants/{tenant_id}/d301-operatiuni` · `cere_cabinet` | creare sau executie — `d301_operatiuni_adauga()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 267 | d301 operatiuni sterge | `DELETE /tenants/{tenant_id}/d301-operatiuni/{op_id}` · `cere_cabinet` | stergere — `d301_operatiuni_sterge()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 268 | [lista 3, 30.08.2026] Registrul de evidență fiscală | `GET /tenants/{tenant_id}/registru-evidenta-fiscala` · `cere_cabinet` | citire / afisare — `registru_fiscal_citeste()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 269 | Înscrie un rând în varianta PERSOANE FIZICE — singura care se completează | `POST /tenants/{tenant_id}/registru-evidenta-fiscala` · `cere_cabinet` | creare sau executie — `registru_fiscal_adauga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |

### T32 — Registrul de încasări și plăți (partida simplă) (7)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 270 | rip d212 | `GET /tenants/{tenant_id}/rip/d212/{an}` · `cere_cabinet` | citire / afisare — `rip_d212()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 271 | rip import banca | `POST /tenants/{tenant_id}/rip/import-banca` · `cere_cabinet` | creare sau executie — `rip_import_banca()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 272 | rip import casa | `POST /tenants/{tenant_id}/rip/import-casa` · `cere_cabinet` | creare sau executie — `rip_import_casa()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 273 | rip adauga | `POST /tenants/{tenant_id}/rip/operatiuni` · `cere_cabinet` | creare sau executie — `rip_adauga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 274 | rip sterge | `DELETE /tenants/{tenant_id}/rip/operatiuni/{op_id}` · `cere_cabinet` | stergere — `rip_sterge()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 275 | rip valideaza | `PUT /tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza` · `cere_cabinet` | modificare — `rip_valideaza()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 276 | rip lista | `GET /tenants/{tenant_id}/rip/registru` · `cere_cabinet` | citire / afisare — `rip_lista()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |

### T33 — Exportul contabil (SAGA, WinMentor) (3)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 277 | export saga luna | `POST /tenants/{tenant_id}/facturi/export-saga` · rol `admin_firma` | creare sau executie — `export_saga_luna()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 278 | Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip | `POST /tenants/{tenant_id}/facturi/export-winmentor` · rol `admin_firma` | creare sau executie — `export_winmentor_luna()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 279 | export saga factura | `GET /tenants/{tenant_id}/facturi/{factura_id}/export-saga` · `cere_context` | citire / afisare — `export_saga_factura()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T34 — Rapoartele comerciale, centrele de cost și rapoartele salvate (14)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 280 | Prezentarea de ansamblu a aplicatiei (semnul "?" GENERAL din bara de stare + pagina de bun-venit) | `GET /ansamblu` · `cere_context` | citire / afisare — `ansamblu_aplicatie()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 281 | apiv1 kpi | `GET /api/v1/firme/{tenant_id}/kpi` · `cere_api_key` | citire / afisare — `apiv1_kpi()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 282 | cabinet consolidare | `GET /cabinet/consolidare` · `cere_cabinet` | citire / afisare — `cabinet_consolidare()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 283 | centre cost lista | `GET /tenants/{tenant_id}/centre-cost` · `cere_cabinet` | citire / afisare — `centre_cost_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 284 | centre cost adauga | `POST /tenants/{tenant_id}/centre-cost` · `cere_cabinet` | creare sau executie — `centre_cost_adauga()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 285 | Realizat pe centru de cost, perioada [de, pana] (note validate, clasele 6/7). | `GET /tenants/{tenant_id}/centre-cost/raport` · `cere_cabinet` | citire / afisare — `centre_cost_raport()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 286 | Buget vs realizat pe an, per centru (note validate, clasele 6/7). | `GET /tenants/{tenant_id}/centre-cost/varianta` · `cere_cabinet` | citire / afisare — `centre_cost_varianta()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 287 | centre cost activ | `PUT /tenants/{tenant_id}/centre-cost/{centru_id}` · `cere_cabinet` | modificare — `centre_cost_activ()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 288 | Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an. | `PUT /tenants/{tenant_id}/centre-cost/{centru_id}/buget` · `cere_cabinet` | modificare — `centre_cost_buget()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 289 | rapoarte comerciale | `GET /tenants/{tenant_id}/rapoarte-comerciale` · `cere_cabinet` | citire / afisare — `rapoarte_comerciale()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 290 | rapoarte comerciale fisa | `GET /tenants/{tenant_id}/rapoarte-comerciale/fisa` · `cere_cabinet` | citire / afisare — `rapoarte_comerciale_fisa()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 291 | rapoarte salvate lista | `GET /tenants/{tenant_id}/rapoarte-salvate` · `cere_cabinet` | citire / afisare — `rapoarte_salvate_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 292 | rapoarte salvate creeaza | `POST /tenants/{tenant_id}/rapoarte-salvate` · `cere_cabinet` | creare sau executie — `rapoarte_salvate_creeaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 8 |
| 293 | rapoarte salvate sterge | `DELETE /tenants/{tenant_id}/rapoarte-salvate/{vid}` · `cere_cabinet` | stergere — `rapoarte_salvate_sterge()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T35 — Pachetul lunar către client și solicitările lui (38)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 294 | pachet genereaza | `POST /pachete/{tenant_id}/genereaza` · `cere_cabinet` | creare sau executie — `pachet_genereaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 295 | pachet poveste get | `GET /pachete/{tenant_id}/poveste` · `cere_cabinet` | citire / afisare — `pachet_poveste_get()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 296 | pachet poveste set | `POST /pachete/{tenant_id}/poveste` · rol `admin_firma` | creare sau executie — `pachet_poveste_set()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 297 | pachet preview | `GET /pachete/{tenant_id}/preview` · `cere_cabinet` | citire / afisare — `pachet_preview()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 298 | pachet rezumat | `GET /pachete/{tenant_id}/rezumat` · `cere_cabinet` | citire / afisare — `pachet_rezumat()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 299 | pachet trimite | `POST /pachete/{tenant_id}/trimite` · rol `admin_firma` | creare sau executie — `pachet_trimite()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 300 | portal acasa | `GET /portal/acasa` · `cere_client` | citire / afisare — `portal_acasa()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 301 | portal acces cont | `GET /portal/acces-cont` · `cere_client` | citire / afisare — `portal_acces_cont()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 302 | portal adauga acces | `POST /portal/acces-cont/acces` · rol `verificat-în-corp` | creare sau executie — `portal_adauga_acces()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 303 | portal revoca acces | `DELETE /portal/acces-cont/acces/{user_id}` · `cere_client` | stergere — `portal_revoca_acces()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 304 | portal schimba email | `PUT /portal/acces-cont/email` · `cere_client` | modificare — `portal_schimba_email()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 305 | portal cashflow | `GET /portal/cashflow` · `cere_client` | citire / afisare — `portal_cashflow()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 306 | portal declaratii | `GET /portal/declaratii` · `cere_client` | citire / afisare — `portal_declaratii()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 307 | portal documente balanta | `GET /portal/documente/balanta` · `cere_client` | citire / afisare — `portal_documente_balanta()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 308 | portal documente luni | `GET /portal/documente/luni` · `cere_client` | citire / afisare — `portal_documente_luni()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 309 | portal facturi | `GET /portal/facturi` · `cere_client` | citire / afisare — `portal_facturi()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 310 | portal firma | `GET /portal/firma` · `cere_client` | citire / afisare — `portal_firma()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 311 | portal firme | `GET /portal/firme` · `cere_client` | citire / afisare — `portal_firme()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 312 | portal kpi | `GET /portal/kpi` · `cere_client` | citire / afisare — `portal_kpi()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 313 | portal povesti | `GET /portal/povesti` · `cere_client` | citire / afisare — `portal_povesti()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 314 | portal recomanda | `POST /portal/recomanda` · `cere_client` | creare sau executie — `portal_recomanda()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 315 | portal recomanda preview | `GET /portal/recomanda/preview` · `cere_client` | citire / afisare — `portal_recomanda_preview()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 316 | portal solicitari lista | `GET /portal/solicitari` · `cere_client` | citire / afisare — `portal_solicitari_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 317 | portal solicitari trimite | `POST /portal/solicitari` · `cere_client` | creare sau executie — `portal_solicitari_trimite()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 318 | portal solicitari contor | `GET /portal/solicitari/contor` · `cere_client` | citire / afisare — `portal_solicitari_contor()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 319 | [R62 (1)] Confirmarea schimbarii de adresa | `POST /public/confirma-email` · fără gardă | creare sau executie — `portal_confirma_email()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 320 | Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei | `POST /tenants/{tenant_id}/acces-portal` · rol `admin_firma/angajat/verificat-în-corp` | creare sau executie — `acces_portal_preview()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 321 | client acces lista | `GET /tenants/{tenant_id}/client-acces` · rol `admin_firma/angajat` | citire / afisare — `client_acces_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 322 | client acces creeaza | `POST /tenants/{tenant_id}/client-acces` · rol `admin_firma/verificat-în-corp` | creare sau executie — `client_acces_creeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 323 | client acces revoca | `DELETE /tenants/{tenant_id}/client-acces/{user_id}` · rol `admin_firma` | stergere — `client_acces_revoca()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 324 | clienti lista | `GET /tenants/{tenant_id}/clienti` · `cere_cabinet` | citire / afisare — `clienti_lista()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 325 | client creeaza | `POST /tenants/{tenant_id}/clienti` · rol `admin_firma/angajat` | creare sau executie — `client_creeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 326 | client sterge | `DELETE /tenants/{tenant_id}/clienti/{client_id}` · rol `admin_firma/angajat` | stergere — `client_sterge()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 327 | client detalii | `GET /tenants/{tenant_id}/clienti/{client_id}` · `cere_cabinet` | citire / afisare — `client_detalii()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 328 | client actualizeaza | `PUT /tenants/{tenant_id}/clienti/{client_id}` · rol `admin_firma/angajat` | modificare — `client_actualizeaza()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 329 | cabinet solicitari lista | `GET /tenants/{tenant_id}/solicitari` · `cere_context` | citire / afisare — `cabinet_solicitari_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 330 | cabinet solicitari raspunde | `POST /tenants/{tenant_id}/solicitari` · rol `admin_firma` | creare sau executie — `cabinet_solicitari_raspunde()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 331 | [R62 (3)] Urma se poate CITI | `GET /tenants/{tenant_id}/urme-portal` · `cere_cabinet` | citire / afisare — `cabinet_urme_portal()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### T36 — Ciclul de viață al firmei — creare, identitate, dezactivare, scoatere (9)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 332 | [R72] Urma firmelor scoase din portofoliu — CITITĂ, nu doar scrisă | `GET /firme-scoase` · `cere_cabinet` | citire / afisare — `firme_scoase()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 333 | `inactive=true` cuprinde ȘI firmele dezactivate — altfel o firmă dezactivată ar ieși din listă fără nicio cale de întoa… | `GET /tenants` · `cere_cabinet` | citire / afisare — `tenants()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 334 | tenant creeaza | `POST /tenants` · rol `admin_firma` | creare sau executie — `tenant_creeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 335 | [R72] Scoate din portofoliu o firmă FĂRĂ evidență | `DELETE /tenants/{tenant_id}` · rol `admin_firma` | stergere — `tenant_scoate()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 336 | tenant detalii | `GET /tenants/{tenant_id}` · `cere_cabinet` | citire / afisare — `tenant_detalii()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 337 | tenant actualizeaza | `PUT /tenants/{tenant_id}` · rol `admin_firma` | modificare — `tenant_actualizeaza()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 338 | [R72] Dezactivează / reactivează firma | `POST /tenants/{tenant_id}/activare` · rol `admin_firma` | creare sau executie — `tenant_activare()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 339 | [R77] Alegerea între denumirea din aplicație și cea de la ANAF | `POST /tenants/{tenant_id}/nume-ales` · rol `admin_firma` | creare sau executie — `tenant_nume_ales()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 340 | [R72] Ce se întâmplă dacă firma se scoate: are evidență sau nu, și ce anume s-a găsit | `GET /tenants/{tenant_id}/scoatere` · `cere_cabinet` | citire / afisare — `tenant_scoatere_previzualizare()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-ADM — suprafata ne-documentara: administrarea furnizorului (12)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 341 | admin activitate cabinet | `GET /admin/activitate/cabinet/{firm_id}` · rol `verificat-în-corp` | citire / afisare — `admin_activitate_cabinet()` | nu |probat invalid 05.09.2026 (lot 14) — reprobat cu token de **superadmin**, deci cererea a ajuns la verificările proprii: **defect găsit și reparat (R150)** — un cabinet INEXISTENT răspundea `200 {"activitate": []}`, adică „cabinetul ăsta n-a făcut nimic” la o întrebare despre un cabinet care nu există. Acum `404`, cu deosebirea scrisă în mesaj, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 342 | admin activitate cabinete | `GET /admin/activitate/cabinete` · rol `verificat-în-corp` | citire / afisare — `admin_activitate_cabinete()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 343 | admin alerte fiscale | `GET /admin/alerte-fiscale` · rol `superadmin` | citire / afisare — `admin_alerte_fiscale()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 344 | admin alerta tratata | `POST /admin/alerte-fiscale/{aid}/tratat` · rol `superadmin` | creare sau executie — `admin_alerta_tratata()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 345 | Cifre agregate din public.eveniment_public: pe eveniment, pe zi, pe pagina de provenienta | `GET /admin/analytics` · rol `superadmin` | citire / afisare — `admin_analytics()` | nu |probat invalid 05.09.2026 (lot 14) — **defect găsit și reparat (R150)**: `zile=-5` devenea tăcut `1`, iar `zile=99999` devenea `365`. Acum se refuză, cu intervalul numit, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 346 | admin anunt creeaza | `POST /admin/anunturi` · rol `superadmin` | creare sau executie — `admin_anunt_creeaza()` | nu |probat invalid 05.09.2026 (lot 14) — corp gol → `422` care numește câmpul lipsă (`mesaj`), cu erori per câmp. Fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 347 | admin cabinet reactiveaza | `POST /admin/cabinete/{firm_id}/reactiveaza` · rol `verificat-în-corp` | creare sau executie — `admin_cabinet_reactiveaza()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 348 | admin cabinet suspenda | `POST /admin/cabinete/{firm_id}/suspenda` · rol `verificat-în-corp` | creare sau executie — `admin_cabinet_suspenda()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 349 | admin sanatate | `GET /admin/sanatate` · rol `verificat-în-corp` | citire / afisare — `admin_sanatate()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 350 | admin sanatate istoric | `GET /admin/sanatate/istoric` · rol `verificat-în-corp` | citire / afisare — `admin_sanatate_istoric()` | nu |probat invalid 05.09.2026 (lot 14) — **defect găsit și reparat (R150)**: `ore=-5` și `ore=99999` erau strânse tăcut la 1 și 168, fără ca valoarea folosită să apară în răspuns. Acum se refuză, cu intervalul numit, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 351 | admin sanatate test alerta | `POST /admin/sanatate/test-alerta` · rol `verificat-în-corp` | creare sau executie — `admin_sanatate_test_alerta()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 352 | Detector "running == HEAD" (superadmin): commitul cu care a pornit procesul viu (stampilat in memorie la startup) vs HE… | `GET /admin/versiune` · rol `superadmin` | citire / afisare — `admin_versiune()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-CAB — suprafata ne-documentara: cabinetul și echipa (21)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 353 | asistenti lista | `GET /asistenti` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_lista()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 354 | asistent creeaza | `POST /asistenti` · rol `admin_firma` | creare sau executie — `asistent_creeaza()` | nu |probat invalid 04.09.2026 — **defect găsit și reparat (R138)**: `«»@#$%` conține un `@`, deci trecea singura verificare a rutei și ar fi inserat un `angajat` în `public.users` plus emailul de activare. Lotul 9 probase aceeași rută cu **corp gol** și primise un refuz corect — defectul n-a scăpat printr-o poartă de rol, ci fiindcă valoarea trimisă nu era greșită în felul care conta. v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
| 355 | asistenti centralizator | `GET /asistenti/echipa/centralizator` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_centralizator()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 356 | asistenti erori | `GET /asistenti/echipa/erori` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_erori()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 357 | asistenti jurnal | `GET /asistenti/echipa/jurnal` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_jurnal()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 358 | asistenti semafor | `GET /asistenti/echipa/semafor` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_semafor()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 359 | asistenti detalii | `GET /asistenti/{uid}` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_detalii()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 360 | asistenti activitate | `GET /asistenti/{uid}/activitate` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_activitate()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 361 | asistenti calitate | `GET /asistenti/{uid}/calitate` · rol `admin_firma(ajutor)` | citire / afisare — `asistenti_calitate()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 362 | asistenti dezactiveaza | `POST /asistenti/{uid}/dezactiveaza` · rol `admin_firma(ajutor)` | creare sau executie — `asistenti_dezactiveaza()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 363 | asistenti finalizeaza firme | `POST /asistenti/{uid}/finalizeaza-firme` · rol `admin_firma(ajutor)` | creare sau executie — `asistenti_finalizeaza_firme()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 364 | asistenti elimina | `DELETE /asistenti/{uid}/firme/{tid}` · rol `admin_firma(ajutor)` | stergere — `asistenti_elimina()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 365 | asistenti atribuie | `POST /asistenti/{uid}/firme/{tid}` · rol `admin_firma(ajutor)` | creare sau executie — `asistenti_atribuie()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 366 | asistenti permisiuni | `POST /asistenti/{uid}/permisiuni` · rol `admin_firma(ajutor)` | creare sau executie — `asistenti_permisiuni()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 367 | asistenti reactiveaza | `POST /asistenti/{uid}/reactiveaza` · rol `admin_firma(ajutor)` | creare sau executie — `asistenti_reactiveaza()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 368 | api chei lista | `GET /cabinet/api-chei` · rol `admin_firma` | citire / afisare — `api_chei_lista()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 369 | api cheie creeaza | `POST /cabinet/api-chei` · rol `admin_firma` | creare sau executie — `api_cheie_creeaza()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 370 | api cheie revoca | `DELETE /cabinet/api-chei/{kid}` · rol `admin_firma` | stergere — `api_cheie_revoca()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 371 | capacitate panou | `GET /capacitate` · rol `admin_firma` | citire / afisare — `capacitate_panou()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 372 | tipare panou | `GET /tipare` · rol `admin_firma` | citire / afisare — `tipare_panou()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 373 | tipare ai panou | `GET /tipare/ai` · rol `admin_firma` | citire / afisare — `tipare_ai_panou()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-CHE — suprafata ne-documentara: cheia de integrare (1)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 374 | apiv1 firme | `GET /api/v1/firme` · `cere_api_key` | citire / afisare — `apiv1_firme()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-CON — suprafata ne-documentara: contul actorului (15)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 375 | Marcheaza prezentarea de bun-venit ca vazuta (o data, la prima logare). | `POST /cont/bun-venit-vazut` · `cere_context` | creare sau executie — `cont_bun_venit_vazut()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 376 | eu anunturi | `GET /eu/anunturi` · `cere_cabinet` | citire / afisare — `eu_anunturi()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 377 | eu anunt confirma | `POST /eu/anunturi/{aid}/confirma` · `cere_cabinet` | creare sau executie — `eu_anunt_confirma()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 378 | eu cabinet get | `GET /eu/cabinet` · `cere_cabinet` | citire / afisare — `eu_cabinet_get()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 379 | eu cabinet set | `POST /eu/cabinet` · rol `verificat-în-corp` | creare sau executie — `eu_cabinet_set()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 380 | Self-view: propria calitate (nivel, semafor, rata, tipare) | `GET /eu/calitate` · `cere_cabinet` | citire / afisare — `eu_calitate()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 381 | eu competente get | `GET /eu/competente` · `cere_cabinet` | citire / afisare — `eu_competente_get()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 382 | eu competente set | `POST /eu/competente` · `cere_cabinet` | creare sau executie — `eu_competente_set()` | da | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 383 | eu educatie | `GET /eu/educatie` · rol `verificat-în-corp` | citire / afisare — `eu_educatie()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 384 | eu educatie vazut | `POST /eu/educatie/patru-ochi/vazut` · rol `verificat-în-corp` | creare sau executie — `eu_educatie_vazut()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 385 | [po_efectiv_v1] {activ, posibil, efectiv} din SURSA UNICA folosita si de enforcement (core.coada_api.patru_ochi_stare) | `GET /eu/patru-ochi` · `cere_cabinet` | citire / afisare — `eu_patru_ochi_stare()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 386 | eu patru ochi | `POST /eu/patru-ochi` · rol `verificat-în-corp` | creare sau executie — `eu_patru_ochi()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 387 | Permisiunile actorului curent | `GET /eu/permisiuni` · rol `verificat-în-corp` | citire / afisare — `eu_permisiuni()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 388 | eu profil | `POST /eu/profil` · `cere_cabinet` | creare sau executie — `eu_profil()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 389 | eu schimba parola | `POST /eu/schimba-parola` · `cere_cabinet` | creare sau executie — `eu_schimba_parola()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |

### S-CON — suprafata ne-documentara: cont și acces (9)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 390 | login | `POST /auth/login` · fără gardă | creare sau executie — `login()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 391 | register | `POST /auth/register` · fără gardă | creare sau executie — `register()` | da | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 392 | activare cont | `POST /public/activare` · fără gardă | creare sau executie — `activare_cont()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 393 | public config | `GET /public/config` · fără gardă | citire / afisare — `public_config()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 394 | Trimite link de logare fara parola | `POST /public/magic-link` · fără gardă | creare sau executie — `magic_link_cere()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 395 | magic login | `POST /public/magic-login` · fără gardă | creare sau executie — `magic_login()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 396 | reset parola cere | `POST /public/reset-parola/cere` · fără gardă | creare sau executie — `reset_parola_cere()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 397 | reset parola seteaza | `POST /public/reset-parola/seteaza` · fără gardă | creare sau executie — `reset_parola_seteaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 398 | public termeni | `GET /public/termeni` · fără gardă | citire / afisare — `public_termeni()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-GDP — suprafata ne-documentara: GDPR (4)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 399 | gdpr cerere stergere | `POST /gdpr/cerere-stergere` · rol `admin_firma` | creare sau executie — `gdpr_cerere_stergere()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 400 | gdpr export cabinet | `GET /gdpr/export-cabinet` · rol `admin_firma/verificat-în-corp` | citire / afisare — `gdpr_export_cabinet()` | nu | probat invalid 04.09.2026 — **defect găsit și reparat**, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 401 | gdpr sterge executa | `POST /gdpr/sterge-cabinet/{cabinet_id}/executa` · rol `superadmin` | creare sau executie — `gdpr_sterge_executa()` | da |probat invalid 05.09.2026 (lot 14) — `422` care numește câmpul lipsă (`confirmare`), înaintea oricărei ștergeri. Probat pe un cabinet inexistent. Fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 402 | gdpr sterge previzualizare | `POST /gdpr/sterge-cabinet/{cabinet_id}/previzualizare` · rol `superadmin` | creare sau executie — `gdpr_sterge_previzualizare()` | da | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-NOT — suprafata ne-documentara: notificări (5)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 403 | notificari lista | `GET /notificari` · `cere_cabinet` | citire / afisare — `notificari_lista()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 404 | notificari citit toate | `POST /notificari/citit` · `cere_cabinet` | creare sau executie — `notificari_citit_toate()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 405 | notificari contor | `GET /notificari/contor` · `cere_cabinet` | citire / afisare — `notificari_contor()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 406 | notificari sumar | `GET /notificari/sumar` · `cere_cabinet` | citire / afisare — `notificari_sumar()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 407 | notificari citit una | `POST /notificari/{nid}/citit` · `cere_cabinet` | creare sau executie — `notificari_citit_una()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-PAG — suprafata ne-documentara: pagini publice (6)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 408 | index | `GET /` · fără gardă | citire / afisare — `index()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 409 | favicon | `GET /favicon.ico` · fără gardă | citire / afisare — `favicon()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 410 | Index-ul ghidurilor: legat din subsol, ca paginile sa nu existe doar in sitemap | `GET /ghid` · fără gardă | citire / afisare — `public_ghid_index()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 411 | Pagina publica de ghid (DS cap.22) | `GET /ghid/{slug}` · fără gardă | citire / afisare — `public_ghid()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 412 | public robots | `GET /robots.txt` · fără gardă | citire / afisare — `public_robots()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 413 | Sitemap generat din aceleasi surse ca index-ul (CSV + fisiere) | `GET /sitemap.xml` · fără gardă | citire / afisare — `public_sitemap()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

### S-SUP — suprafata ne-documentara: suport și telemetrie (14)

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 414 | Ajutor contextual pentru contabil (semnul "?" din UI) | `GET /ajutor/{fid}` · fără gardă | citire / afisare — `ajutor_contextual()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 415 | Inregistrare eveniment public de interes (deschidere modal, click Intra in cont, vizita ghid) | `POST /api/eveniment-public` · fără gardă | creare sau executie — `eveniment_public()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 416 | raportari creeaza | `POST /raportari` · `cere_cabinet` | creare sau executie — `raportari_creeaza()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 417 | raportari admin | `GET /raportari/admin` · rol `verificat-în-corp` | citire / afisare — `raportari_admin()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 418 | raportari contor | `GET /raportari/contor` · `cere_cabinet` | citire / afisare — `raportari_contor()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 419 | raportari mele | `GET /raportari/eu` · `cere_cabinet` | citire / afisare — `raportari_mele()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 420 | raportari imagine | `POST /raportari/mesaj/{mid}/imagine` · rol `verificat-în-corp` | creare sau executie — `raportari_imagine()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 421 | raportari fir | `GET /raportari/{rid}` · rol `verificat-în-corp` | citire / afisare — `raportari_fir()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 422 | raportari citit | `POST /raportari/{rid}/citit` · rol `verificat-în-corp` | creare sau executie — `raportari_citit()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |
| 423 | raportari mesaj | `POST /raportari/{rid}/mesaj` · rol `verificat-în-corp` | creare sau executie — `raportari_mesaj()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 424 | raportari pentru admin | `POST /raportari/{rid}/pentru-admin` · rol `verificat-în-corp` | creare sau executie — `raportari_pentru_admin()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 425 | raportari stare | `POST /raportari/{rid}/stare` · rol `superadmin` | creare sau executie — `raportari_stare()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 426 | trimite recomandari | `POST /recomanda` · `cere_cabinet` | creare sau executie — `trimite_recomandari()` | nu | probat invalid 04.09.2026 — fără defect, v. `VERIFICARE_FUNCTIONALITATI.md` lot 9 |
| 427 | recomanda preview | `GET /recomanda/preview` · `cere_cabinet` | citire / afisare — `recomanda_preview()` | nu | în afara perimetrului etapei 1 — rută fără câmpuri de completat: nimeni nu poate tasta nimic greșit în ea |

## B. Ecrane — 75

*Un `fa-*` = un ecran de firmă; rutele lui se iau din **corpul funcției** care îl randează (`#fa-facturi` → `randeazaFacturi` → `facturi_ecran.js`). Un fișier de ecran fără niciun `fa-*` (cabinet, administrare, autentificare) e și el un ecran, sub numele fișierului.*

*Un fișier care e implementarea unui `fa-*` apare **și** ca unitate proprie, deliberat: cardul e intrarea, fișierul e suprafața cu dialogurile lui. Nu e o dublură — sunt două lucruri de probat. Unde handlerul nu s-a găsit, se scrie `handler negăsit` și rutele rămân neatribuite: `firme.js` are 94 de rute, iar atribuirea lor toate unui singur buton ar fi arătat la fel de plină ca una adevărată.*

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 428 | Ecranul `fa-acces` — 3 rute chemate: `/tenants/{}/acces-portal`, `/tenants/{}/client-acces`, `/tenants/{}/client-acces/{}` | `static/js/ecrane/firme.js::ecranAccesClient()` | interacțiune de ecran (atribuire pe funcție) | da |neprobat — parcurs 04.09.2026 (lot 11), fereastră deschisă cu «Invită client nou» (2 câmpuri), dar niciun buton de salvare vizibil pe ea|
|429|Ecranul `fa-balanta` — 2 rute chemate: `/tenants/{}/balanta`, `/tenants/{}/documente/balanta`|`static/js/ecrane/firme.js::ecranBalanta()`|interacțiune de ecran (atribuire pe funcție)|da|probat invalid 04.09.2026 — descarcarea balantei arunca motivul serverului; **reparat** (R131)|
|430|Ecranul `fa-banca` — 6 rute chemate: `/tenants/{}/banca/reconciliere`, `/tenants/{}/banca/reconciliere/facturi-deschise`, `/tenants/{}/banca/reconciliere/import`, `/tenants/{}/banca/reconciliere/{}/conteaza`, `/tenants/{}/banca/reconciliere/{}/ignora`, `/tenants/{}/banca/reconciliere/{}/reactiveaza`|`static/js/ecrane/firme.js::ecranBanca()`|interacțiune de ecran (atribuire pe funcție)|da|probat invalid 04.09.2026 — importul de extras arata „Nu am putut citi extrasul” peste motivul real; **reparat** (R131)|
| 431 | Ecranul `fa-bilant` — 1 rute chemate: `/tenants/{}/categorie-marime` | `static/js/ecrane/firme.js::ecranBilant()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 05.09.2026 (lot 14): două câmpuri de filtru (`bl-an`, `bl-tip`) și două acțiuni pe REZULTAT («Validează (ANAF)» — validatorul DUK local —, «Descarcă XML»). Niciun buton care ia conținutul unui formular, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
|432|Ecranul `fa-bonuri` — 7 rute chemate: `/portal/bon`, `/portal/bon/{}/confirma`, `/tenants/{}/bonuri/de-verificat`, `/tenants/{}/bonuri/{}/aproba`, `/tenants/{}/bonuri/{}/facturi-candidate`, `/tenants/{}/bonuri/{}/imagine/{}`, `/tenants/{}/bonuri/{}/stinge`|`static/js/ecrane/firme.js::ecranBonuri()`|interacțiune de ecran (atribuire pe funcție)|da|neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`; singurul buton deschide **selectorul de fișiere** (măsurat prin evenimentul `filechooser` — ecranul RĂSPUNDE, nu tace). Se probează cu un fișier invalid, nu cu un formular: lotul 12|
| 433 | Ecranul `fa-casa` — 4 rute chemate: `/tenants/{}/casa/operatiuni`, `/tenants/{}/casa/operatiuni/{}`, `/tenants/{}/casa/registru`, `/tenants/{}/verifica-cui/{}` | `static/js/ecrane/firme.js::ecranCasa()` | interacțiune de ecran (atribuire pe funcție) | da | neprobat |
|434|Ecranul `fa-centrecost` — 5 rute chemate: `/tenants/{}/centre-cost`, `/tenants/{}/centre-cost/raport`, `/tenants/{}/centre-cost/varianta`, `/tenants/{}/centre-cost/{}`, `/tenants/{}/centre-cost/{}/buget`|`static/js/ecrane/firme.js::ecranCentreCost()`|interacțiune de ecran (atribuire pe funcție)|nu|probat invalid 04.09.2026 — buton „Adauga” apasat pe formular invalid: **vorbeste** (a si acceptat numele liber, corect)|
|435|Ecranul `fa-contracte` — 5 rute chemate: `/contracte/marcaje`, `/tenants/{}/clienti`, `/tenants/{}/contracte/genereaza`, `/tenants/{}/contracte/sabloane`, `/tenants/{}/contracte/sabloane/{}`|`static/js/ecrane/firme.js::ecranContracte()`|interacțiune de ecran (atribuire pe funcție)|da|probat invalid 04.09.2026 (lot 11) — «+ Șablon nou» → «Salvează» pe formular invalid: **vorbește** (și acceptă numele liber de șablon, corect — nu pleacă în nicio declarație)|
| 436 | Ecranul `fa-control` — 1 rute chemate: `/control-fiscal/{}` | `static/js/ecrane/firme.js::ecranControlFirma()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: formularul cere un pas înainte (alegerea unui control)|
| 437 | Ecranul `fa-datefirma` — 3 rute chemate: `/tenants/{}`, `/tenants/{}/firma-profil/date`, `/tenants/{}/vector` | `static/js/ecrane/date_firma.js::randeazaDateFirma()` | interacțiune de ecran (atribuire pe funcție) | da |probat invalid 04.09.2026 (lot 11) — **trei defecte, toate reparate și reprobate**: ruta răspundea `500` la orice refuz (**R134**), accepta o denumire fără nicio literă (**R135**), iar ecranul trimitea redenumirea ÎNAINTEA a ce putea fi refuzat, deci firma rămânea redenumită sub un mesaj de eșec (**R136**)|
| 438 | Ecranul `fa-declaratii` — 0 rute chemate | `static/js/ecrane/firme.js` | interacțiune de ecran (atribuire pe handler negăsit) | ? |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: lista de declarații se deschide pe alegerea unei perioade|
| 439 | Ecranul `fa-etransport` — 3 rute chemate: `/tenants/{}/etransport-xml`, `/tenants/{}/etransport/trimite`, `/tenants/{}/etransport/trimiteri` | `static/js/ecrane/etransport_ecran.js::ecranEtransport()` | interacțiune de ecran (atribuire pe funcție) | nu | neprobat |
| 440 | Ecranul `fa-facturi` — 0 rute chemate | `static/js/ecrane/facturi_ecran.js::randeazaFacturi()` | interacțiune de ecran (atribuire pe funcție) | ? |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: emiterea trăiește într-un ecran propriu (#478), deschis din meniu|
| 441 | Ecranul `fa-fisacont` — 1 rute chemate: `/tenants/{}/fisa-cont` | `static/js/ecrane/firme.js::ecranFisaCont()` | interacțiune de ecran (atribuire pe funcție) | nu |verificat 05.09.2026 (lot 13) — **numai câmpuri de FILTRU** (`fc-an`, `fc-luna`, `fc-cont`): aleg ce se afișează, nu se înregistrează nicăieri. Criteriul din `DECIZII.md` 33|
| 442 | Ecranul `fa-import` — 0 rute chemate | `static/js/ecrane/firme.js::ecranSolicitariCabinet()` | interacțiune de ecran (atribuire pe funcție) | ? | neprobat |
| 443 | Ecranul `fa-jurnal` — 6 rute chemate: `/tenants/{}/amortizare`, `/tenants/{}/centre-cost`, `/tenants/{}/jurnal`, `/tenants/{}/jurnal/{}`, `/tenants/{}/jurnal/{}/valideaza`, `/tenants/{}/perioade-blocate` | `static/js/ecrane/firme.js::ecranJurnal()` | interacțiune de ecran (atribuire pe funcție) | da |probat invalid 04.09.2026 (lot 11) — «+ Notă nouă»: «Generează amortizarea» și «Salvează» pe formular invalid: **amândouă vorbesc**|
| 444 | Ecranul `fa-magazin` — 2 rute chemate: `/tenants/{}/woocommerce/config`, `/tenants/{}/woocommerce/sincronizeaza` | `static/js/ecrane/woo_ecran.js::ecranMagazin()` | interacțiune de ecran (atribuire pe funcție) | da |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: configurarea WooCommerce cere întâi o conexiune|
| 445 | Ecranul `fa-marja` — 1 rute chemate: `/tenants/{}/jurnal-marja` | `static/js/ecrane/firme.js::ecranJurnalMarja()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 05.09.2026 (lot 14): două câmpuri de filtru (`jm-tip`, `jm-luna`) și **niciun buton**. Ecran de raport, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 446 | Ecranul `fa-mijloace` — 3 rute chemate: `/tenants/{}/mijloace-fixe`, `/tenants/{}/nota-inventariere`, `/tenants/{}/reevaluare-imobilizare` | `static/js/ecrane/mijloace_ecran.js::ecranMijloace()` | interacțiune de ecran (atribuire pe funcție) | da |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: fereastra de mijloc fix cere doi pași|
| 447 | Ecranul `fa-operatiuni` — 0 rute chemate | `static/js/ecrane/operatiuni_ecran.js::ecranOperatiuni()` | interacțiune de ecran (atribuire pe funcție) | ? |probat invalid 04.09.2026 (lot 13) — ecranul e un MENIU cu **32 de feluri de operațiune**, fiecare cu formularul lui și cu «Generează nota (ciornă)». Toate 32 probate cu date imposibile: **32 au vorbit, 0 au scris, 0 au tăcut**. Două defecte, amândouă reparate și reprobate: «Aur de investiții» cădea cu **`500`** pe o puritate care nu e număr (**R144**), iar «Chirii / comodat / refacturări» **nu putea reuși niciodată din ecran** — formularul trimitea `suma`, ruta cere `valoare`/`chirie`/`total_factura` (**R145**). v. `VERIFICARE_FUNCTIONALITATI.md` lot 13|
| 448 | Ecranul `fa-produse` — 1 rute chemate: `/tenants/{}/produse` | `static/js/ecrane/produse_ecran.js::randeazaProduse()` | interacțiune de ecran (atribuire pe funcție) | nu |probat invalid 04.09.2026 (lot 11) — «+ Adaugă produs» pe formular invalid: **vorbește**|
|449|Ecranul `fa-rapoarte` — 4 rute chemate: `/tenants/{}/rapoarte-comerciale`, `/tenants/{}/rapoarte-comerciale/fisa`, `/tenants/{}/rapoarte-salvate`, `/tenants/{}/rapoarte-salvate/{}`|`static/js/ecrane/firme.js::ecranRapoarte()`|interacțiune de ecran (atribuire pe funcție)|nu|probat invalid 04.09.2026 — buton „Salveaza varianta” pe formular invalid: **vorbeste**|
| 450 | Ecranul `fa-raportz` — 3 rute chemate: `/tenants/{}/horeca/import-amef`, `/tenants/{}/horeca/raport-z`, `/tenants/{}/stocuri/descarcare` | `static/js/ecrane/firme.js::ecranRaportZ()` | interacțiune de ecran (atribuire pe funcție) | da |probat invalid 04.09.2026 (lot 11) — «Generează notă» pe formular invalid: **vorbește**|
| 451 | Ecranul `fa-regfiscal` — 1 rute chemate: `/tenants/{}/registru-evidenta-fiscala` | `static/js/ecrane/firme.js::ecranRegistruFiscal()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 05.09.2026 (lot 14): în DOM apar doar `rf-var` și `rf-an`; câmpurile de sume (`rf-venit_brut`, `rf-cheltuieli_deductibile`) se randează pe altă variantă decât cea implicită, iar sonda alege doar selecturile GOALE. Limită a sondei, scrisă, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 452 | Ecranul `fa-reginventar` — 2 rute chemate: `/tenants/{}/registru-inventar`, `/tenants/{}/registru-inventar/propunere` | `static/js/ecrane/firme.js::ecranRegistruInventar()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 05.09.2026 (lot 14): formularul de 10 câmpuri apare abia după «Adu soldurile din balanță», adică al doilea pas pe care sonda nu-l face. NU e „fără defect”, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 453 | Ecranul `fa-registratura` — 1 rute chemate: `/tenants/{}/registratura` | `static/js/ecrane/firme.js::ecranRegistratura()` | interacțiune de ecran (atribuire pe funcție) | nu | neprobat |
| 454 | Ecranul `fa-registre321` — 1 rute chemate: `/tenants/{}/registre-art321/{}` | `static/js/ecrane/firme.js::ecranRegistre321()` | interacțiune de ecran (atribuire pe funcție) | nu |probat invalid 05.09.2026 (lot 14) — 13 câmpuri umplute, «Înscrie în registru»: **vorbește**, numind câmpul și norma («Cantitatea — cerut de normă, nu poate lipsi»). Butonul n-a fost apăsat până azi fiindcă verbul lui nu era în lista sondei, v. `VERIFICARE_FUNCTIONALITATI.md` lot 14|
| 455 | Ecranul `fa-rip` — 8 rute chemate: `/tenants/{}/rip/d212/{}`, `/tenants/{}/rip/import-banca`, `/tenants/{}/rip/import-casa`, `/tenants/{}/rip/inventar/{}`, `/tenants/{}/rip/operatiuni`, `/tenants/{}/rip/operatiuni/{}`, `/tenants/{}/rip/operatiuni/{}/valideaza`, `/tenants/{}/rip/registru` | `static/js/ecrane/rip_ecran.js::ecranRip()` | interacțiune de ecran (atribuire pe funcție) | nu |probat invalid 04.09.2026 (lot 12) — cardul se randează acum: firma de **partidă simplă** a fost creată prin lanțul aplicației (`POST /tenants`, `tip_firma: "pfa"`, CUI cu cifră de control validă). «Adaugă (ciornă)» pe formular invalid → **R140**, reparat și reprobat. Măsurat: `#fa-rip` e **singurul** card exclusiv partidei simple (31 carduri pe dublă, 22 pe simplă, 21 comune), v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
|456|Ecranul `fa-salariati` — 11 rute chemate: `/tenants/{}/fluturas/{}`, `/tenants/{}/plata-salarii-fisier`, `/tenants/{}/plata-salarii-preview`, `/tenants/{}/reges-config`, `/tenants/{}/reges-poll`, `/tenants/{}/reges-trimite-salariat`, `/tenants/{}/salariati/{}`, `/tenants/{}/salariati/{}/beneficiu-lunar`, `/tenants/{}/salarii-contare`, `/te…|`static/js/ecrane/firme.js::ecranSalariati()`|interacțiune de ecran (atribuire pe funcție)|da|probat invalid 04.09.2026 — adeverinta, fluturasul si fisierul de plata aruncau motivul; **reparate** (R131). Pe server: adeverinta cerea numele administratorului INAINTE sa vada ca salariatul nu exista, iar fisierul de plata raspundea „month must be in 1..12”; **amandoua reparate**. · Lot 11: «+ Salariat nou» a deschis fereastra (14 câmpuri, `campuri=0` în lotul 10) → «Salvează» pe formular invalid: **vorbește**|
| 457 | Ecranul `fa-solicitari` — 0 rute chemate | `static/js/ecrane/firme.js::ecranSolicitariCabinet()` | interacțiune de ecran (atribuire pe funcție) | ? |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
|458|Ecranul `fa-stocuri` — 2 rute chemate: `/tenants/{}/stocuri/descarcare`, `/tenants/{}/stocuri/nir`|`static/js/ecrane/firme.js::ecranStocuri()`|interacțiune de ecran (atribuire pe funcție)|da|probat invalid 04.09.2026 — trei butoane de salvare (NIR, nivel minim, reteta) pe formular invalid: **toate vorbesc**|
| 459 | Ecranul `fa-verificari` — 3 rute chemate: `/firme/{}/verificari`, `/tenants/{}/intrastat-praguri`, `/tenants/{}/verificare-stocuri` | `static/js/ecrane/firme.js::ecranVerificari()` | interacțiune de ecran (atribuire pe funcție) | nu |neprobat — parcurs 04.09.2026 (lot 11), `campuri=0`: verificările se randează pe alegerea unei luni|
|460|Ecranul `static/js/api.js` — 1 rute chemate: `/ajutor/{}`|`static/js/api.js`|interacțiune de ecran (atribuire pe fișier)|nu|probat invalid 04.09.2026 — stratul de cereri: **13 descarcari** ocoleau `_refuzNevazut` si aruncau motivul serverului. Reparatie UNA: `cereBlob`/`descarca`/`deschide`; probat pe viu in browser (`proba_r131_descarcare_muta.py`)|
|461|Ecranul `static/js/app.js` — 5 rute chemate: `/cont/bun-venit-vazut`, `/public/activare`, `/public/confirma-email`, `/public/magic-login`, `/public/reset-parola/seteaza`|`static/js/app.js`|interacțiune de ecran (atribuire pe fișier)|nu|verificat 04.09.2026 — trateaza refuzul in lant (`.then(r => ({ok: r.ok, d}))`) si arata `detail`; fara defect|
| 462 | Ecranul `static/js/coaja.js` — 0 rute chemate | `static/js/coaja.js` | interacțiune de ecran (atribuire pe fișier) | ? |verificat 04.09.2026 (lot 12) — contractul proprietar↔chiriaș (DS cap.25): funcții pure de așezare a unui nod în bara de stare. Nicio cerere, niciun câmp; nu poate primi date greșite|
| 463 | Ecranul `static/js/ecrane/activitate_cabinet.js` — 2 rute chemate: `/asistenti/echipa/centralizator`, `/asistenti/echipa/jurnal` | `static/js/ecrane/activitate_cabinet.js` | interacțiune de ecran (atribuire pe fișier) | da |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 464 | Ecranul `static/js/ecrane/admin.js` — 5 rute chemate: `/admin/activitate/cabinete`, `/admin/alerte-fiscale`, `/admin/alerte-fiscale/{}/tratat`, `/admin/anunturi`, `/admin/versiune` | `static/js/ecrane/admin.js` | interacțiune de ecran (atribuire pe fișier) | nu |probat invalid 04.09.2026 (lot 12) — ecranul de admin: «Anunțuri» → «Mesaj» → «Trimite» pe formular invalid: **vorbește** («Alege întâi destinatarii (Cabinete).»). Butonul e pe lista OPRITE după nume, dar ruta lui doar inserează în `public.anunturi_cabinet` — excepție declarată la sursă, v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
| 465 | Ecranul `static/js/ecrane/admin_activitate.js` — 2 rute chemate: `/admin/activitate/cabinet/{}`, `/admin/activitate/cabinete` | `static/js/ecrane/admin_activitate.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **numai câmpuri de FILTRU** (`ac-cauta`): aleg ce se afișează, nu se înregistrează nicăieri. Criteriul din `DECIZII.md` 33|
| 466 | Ecranul `static/js/ecrane/admin_analytics.js` — 1 rute chemate: `/admin/analytics` | `static/js/ecrane/admin_analytics.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 467 | Ecranul `static/js/ecrane/admin_raportari.js` — 7 rute chemate: `/raportari/admin`, `/raportari/mesaj/{}/imagine`, `/raportari/{}`, `/raportari/{}/citit`, `/raportari/{}/mesaj`, `/raportari/{}/pentru-admin`, `/raportari/{}/stare` | `static/js/ecrane/admin_raportari.js` | interacțiune de ecran (atribuire pe fișier) | nu |neprobat — parcurs 04.09.2026 (lot 12), `campuri=0` pe starea goală: formularul de răspuns se randează pe o sesizare existentă, iar lista era goală. NU e „fără defect” — e un ecran neatins|
| 468 | Ecranul `static/js/ecrane/admin_sanatate.js` — 3 rute chemate: `/admin/sanatate`, `/admin/sanatate/istoric`, `/admin/sanatate/test-alerta` | `static/js/ecrane/admin_sanatate.js` | interacțiune de ecran (atribuire pe fișier) | nu | neprobat |
| 469 | Ecranul `static/js/ecrane/ansamblu.js` — 1 rute chemate: `/ansamblu` | `static/js/ecrane/ansamblu.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 470 | Ecranul `static/js/ecrane/asistent.js` — 2 rute chemate: `/control-fiscal`, `/raportari/contor` | `static/js/ecrane/asistent.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 471 | Ecranul `static/js/ecrane/asistenti.js` — 11 rute chemate: `/asistenti`, `/asistenti/echipa/erori`, `/asistenti/echipa/semafor`, `/asistenti/{}`, `/asistenti/{}/activitate`, `/asistenti/{}/calitate`, `/asistenti/{}/dezactiveaza`, `/asistenti/{}/finalizeaza-firme`, `/asistenti/{}/firme/{}`, `/asistenti/{}/permisiuni`, `/asistenti/{}/reactiveaza` | `static/js/ecrane/asistenti.js` | interacțiune de ecran (atribuire pe fișier) | da |probat invalid 04.09.2026 (lot 12) — «Trimite invitația» pe formular umplut cu `«»@#$%`: **defect găsit și reparat** — `«»@#$%` conține un `@`, deci trecea singura verificare a rutei și ar fi creat un cont de `angajat` plus un email real (**R138**). Reparat în `core/common.email_valid`, un singur loc pentru toate cele cinci rute; reprobat: «Adresă de email invalidă…», v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
| 472 | Ecranul `static/js/ecrane/cabinet.js` — 14 rute chemate: `/asistenti`, `/asistenti/echipa/centralizator`, `/asistenti/echipa/jurnal`, `/asistenti/echipa/semafor`, `/cabinet/consolidare`, `/coada`, `/control-fiscal`, `/eu/educatie`, `/eu/educatie/patru-ochi/vazut`, `/eu/patru-ochi`, `/migrare/status`, `/raportari/contor`, `/tenants`, `/termene` | `static/js/ecrane/cabinet.js` | interacțiune de ecran (atribuire pe fișier) | da |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 473 | Ecranul `static/js/ecrane/capacitate.js` — 1 rute chemate: `/capacitate` | `static/js/ecrane/capacitate.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 474 | Ecranul `static/js/ecrane/control.js` — 2 rute chemate: `/control-fiscal`, `/control-fiscal/{}` | `static/js/ecrane/control.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 475 | Ecranul `static/js/ecrane/control_verdict.js` — 2 rute chemate: `/control-fiscal/{}/audit-preluare`, `/tenants/{}/facturi/{}/contabilizeaza` | `static/js/ecrane/control_verdict.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 476 | Ecranul `static/js/ecrane/date_firma.js` — 3 rute chemate: `/tenants/{}`, `/tenants/{}/firma-profil/date`, `/tenants/{}/vector` | `static/js/ecrane/date_firma.js` | interacțiune de ecran (atribuire pe fișier) | da |probat invalid 04.09.2026 (lot 11) — fișierul ecranului «Date firmă»: v. #437 (R134, R135, R136)|
| 477 | Ecranul `static/js/ecrane/declaratii.js` — 12 rute chemate: `/coada`, `/declaratii/tipuri`, `/declaratii/{}/valideaza`, `/tenants`, `/tenants/{}/d300-manual`, `/tenants/{}/d300-manual/{}`, `/tenants/{}/d301-operatiuni`, `/tenants/{}/d301-operatiuni/{}`, `/tenants/{}/d390-clasificare`, `/tenants/{}/d390-clasificare/manual`, `/tenants/{}/d390-clasificare/manu… | `static/js/ecrane/declaratii.js` | interacțiune de ecran (atribuire pe fișier) | da |neprobat — parcurs 04.09.2026 (lot 12), fișierul ecranului «Declarații»; geamănul lui `#fa-declaratii` (#438) a dat `campuri=0` — lista se deschide pe alegerea unei perioade|
| 478 | Ecranul `static/js/ecrane/emitere_ecran.js` — 8 rute chemate: `/tenants/{}/facturi/emite`, `/tenants/{}/facturi/numerotare`, `/tenants/{}/firma-profil/regim-tva`, `/tenants/{}/produse/potriveste`, `/tenants/{}/stocuri/articole`, `/tenants/{}/vector`, `/tenants/{}/verifica-cui/{}`, `/tenants/{}/verifica-vies` | `static/js/ecrane/emitere_ecran.js` | interacțiune de ecran (atribuire pe fișier) | da |probat invalid 04.09.2026 (lot 12) — «Emite factură» pe formular invalid: **defect găsit și reparat** — mesajul de lângă câmp era chiar ETICHETA câmpului («Linia 1: cantitate»), iar rezumatul spunea «Completează» despre un câmp completat (**R139**). Reparat în `linii_campuri_lipsa`, sursa unică a emiterii și a facturilor recurente; reprobat, v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
|479|Ecranul `static/js/ecrane/etransport_ecran.js` — 3 rute chemate: `/tenants/{}/etransport-xml`, `/tenants/{}/etransport/trimite`, `/tenants/{}/etransport/trimiteri`|`static/js/ecrane/etransport_ecran.js`|interacțiune de ecran (atribuire pe fișier)|nu|probat invalid 04.09.2026 — buton „Doar genereaza XML” pe formular invalid: **vorbeste**|
|480|Ecranul `static/js/ecrane/facturi_ecran.js` — 30 rute chemate: `/tenants/{}/chitante`, `/tenants/{}/chitante/{}/pdf`, `/tenants/{}/facturi`, `/tenants/{}/facturi-primite`, `/tenants/{}/facturi-primite/{}/respinge`, `/tenants/{}/facturi-primite/{}/valideaza`, `/tenants/{}/facturi-primite/{}/xml`, `/tenants/{}/facturi-recurente`, `/tenants/{}/facturi-recurente/{…|`static/js/ecrane/facturi_ecran.js`|interacțiune de ecran (atribuire pe fișier)|da|probat invalid 04.09.2026 — cinci descarcari (SAGA luna/factura, WinMentor, PDF factura, PDF chitanta); doua spuneau „Eroare — reincearca” peste un refuz care nu se schimba la reincercare; **reparate** (R131)|
| 481 | Ecranul `static/js/ecrane/flux_concediu.js` — 3 rute chemate: `/tenants/{}/salariati/{}/concedii`, `/tenants/{}/salariati/{}/concedii/{}`, `/util/zile-lucratoare` | `static/js/ecrane/flux_concediu.js` | interacțiune de ecran (atribuire pe fișier) | da |probat invalid 04.09.2026 (lot 12) — «+ Certificat nou» → «Calculează și salvează» pe 9 câmpuri invalide: **vorbește**, câmp cu câmp («Completează data de început a concediului», «Zilele lucrătoare CM trebuie să fie cel puțin 1»), v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
|482|Ecranul `static/js/ecrane/login.js` — 9 rute chemate: `/api/eveniment-public`, `/auth/login`, `/auth/register`, `/ghid`, `/public/config`, `/public/magic-link`, `/public/reset-parola/cere`, `/public/termeni`, `/public/verifica-cui/{}`|`static/js/ecrane/login.js`|interacțiune de ecran (atribuire pe fișier)|da|verificat 04.09.2026 — singurul `fetch` care ignora deliberat raspunsul: telemetrie `keepalive` catre `/api/eveniment-public`. Declarat ca exceptie in `scan_descarcare_muta`|
|483|Ecranul `static/js/ecrane/migrare.js` — 33 rute chemate: `/migrare/asociati`, `/migrare/importa`, `/migrare/incarca`, `/migrare/istoric-declaratii`, `/migrare/mijloace-fixe`, `/migrare/parteneri`, `/migrare/plan-conturi`, `/migrare/salariati`, `/migrare/solduri`, `/migrare/status`, `/migrare/straturi`, `/migrare/valideaza`, `/migrare/vector`, `/tenants`,…|`static/js/ecrane/migrare.js`|interacțiune de ecran (atribuire pe fișier)|da|probat invalid 04.09.2026 — „Salveaza vectorul” si „Adauga cont” pe formular invalid: **amandoua vorbesc** (eroarea traieste in `.mig-eroare`, o clasa proprie, nu in conventia `.msg-eroare`)|
| 484 | Ecranul `static/js/ecrane/mijloace_ecran.js` — 3 rute chemate: `/tenants/{}/mijloace-fixe`, `/tenants/{}/nota-inventariere`, `/tenants/{}/reevaluare-imobilizare` | `static/js/ecrane/mijloace_ecran.js` | interacțiune de ecran (atribuire pe fișier) | da |neprobat — parcurs 04.09.2026 (lot 12), fișierul ecranului «Mijloace fixe»; geamănul lui `#fa-mijloace` (#446) a dat `campuri=0` — fereastra cere doi pași|
| 485 | Ecranul `static/js/ecrane/operatiuni_ecran.js` — 0 rute chemate | `static/js/ecrane/operatiuni_ecran.js` | interacțiune de ecran (atribuire pe fișier) | ? |probat invalid 04.09.2026 (lot 13) — fișierul ecranului «Operațiuni speciale»: v. #447, cele 32 de formulare, cu R144 și R145|
| 486 | Ecranul `static/js/ecrane/pachete.js` — 6 rute chemate: `/pachete/{}/genereaza`, `/pachete/{}/poveste`, `/pachete/{}/preview`, `/pachete/{}/rezumat`, `/pachete/{}/trimite`, `/tenants` | `static/js/ecrane/pachete.js` | interacțiune de ecran (atribuire pe fișier) | da |neprobat — parcurs 04.09.2026 (lot 12), 2 câmpuri și un selector de firmă completate, dar niciun buton probabil: singurul care ia formularul e «✨ Generează cu AI», iar `/pachete/{}/genereaza` iese la un furnizor din afară. «Salvează ciornă» apare abia după generare|
|487|Ecranul `static/js/ecrane/portal.js` — 15 rute chemate: `/portal/acasa`, `/portal/acces-cont`, `/portal/acces-cont/acces`, `/portal/acces-cont/email`, `/portal/bon`, `/portal/cashflow`, `/portal/declaratii`, `/portal/documente/balanta`, `/portal/documente/luni`, `/portal/firma`, `/portal/kpi`, `/portal/povesti`, `/portal/recomanda`, `/portal/recomanda/p…|`static/js/ecrane/portal.js`|interacțiune de ecran (atribuire pe fișier)|nu|probat invalid 04.09.2026 — balanta clientului arunca motivul; **reparata** (R131). Pe server: `luna=13` TIPAREA PDF-ul, desi calea de cabinet o refuza din lotul 3; **reparat**|
| 488 | Ecranul `static/js/ecrane/preturi.js` — 0 rute chemate | `static/js/ecrane/preturi.js` | interacțiune de ecran (atribuire pe fișier) | ? |verificat 04.09.2026 (lot 12) — SURSA UNICĂ a textului de prețuri, refolosită de `login.js`. Numai `preturiHTML()`: niciun câmp, nicio cerere|
| 489 | Ecranul `static/js/ecrane/produse_ecran.js` — 3 rute chemate: `/tenants/{}/produse`, `/tenants/{}/produse/potriveste`, `/tenants/{}/produse/{}` | `static/js/ecrane/produse_ecran.js` | interacțiune de ecran (atribuire pe fișier) | nu |probat invalid 04.09.2026 — fișierul ecranului «Produse»: v. #448, «+ Adaugă produs» pe formular invalid, **vorbește**|
| 490 | Ecranul `static/js/ecrane/raporteaza.js` — 4 rute chemate: `/raportari`, `/raportari/eu`, `/raportari/mesaj/{}/imagine`, `/raportari/{}/mesaj` | `static/js/ecrane/raporteaza.js` | interacțiune de ecran (atribuire pe fișier) | nu |probat invalid 04.09.2026 (lot 12) — «Adaugă captură»: **cere un fișier** (nici tăcere, nici refuz). «Trimite sesizarea» NU s-a apăsat: iese din aplicație prin email, v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
| 491 | Ecranul `static/js/ecrane/recomanda.js` — 2 rute chemate: `/recomanda`, `/recomanda/preview` | `static/js/ecrane/recomanda.js` | interacțiune de ecran (atribuire pe fișier) | nu |neprobat — parcurs 04.09.2026 (lot 12), 1 câmp completat, niciun buton probabil: «Trimite invitația» trimite un email REAL către adresele scrise. Refuzul lui rămâne neprobat de campanie, declarat|
| 492 | Ecranul `static/js/ecrane/rip_ecran.js` — 8 rute chemate: `/tenants/{}/rip/d212/{}`, `/tenants/{}/rip/import-banca`, `/tenants/{}/rip/import-casa`, `/tenants/{}/rip/inventar/{}`, `/tenants/{}/rip/operatiuni`, `/tenants/{}/rip/operatiuni/{}`, `/tenants/{}/rip/operatiuni/{}/valideaza`, `/tenants/{}/rip/registru` | `static/js/ecrane/rip_ecran.js` | interacțiune de ecran (atribuire pe fișier) | nu |probat invalid 04.09.2026 (lot 12) — **primul ecran de partidă simplă deschis vreodată** — pe firma creată azi prin `POST /tenants` cu `tip_firma: "pfa"`. «Adaugă (ciornă)» pe formular invalid: **defect găsit și reparat** — cele opt refuzuri ale registrului vorbeau limba programatorului (`suma trebuie să fie > 0`, `valuta != RON: suma_valuta si curs_valutar`), șapte din opt fără diacritice (**R140**). Rescrise și reprobate, v. `VERIFICARE_FUNCTIONALITATI.md` lot 12|
| 493 | Ecranul `static/js/ecrane/semafor.js` — 0 rute chemate | `static/js/ecrane/semafor.js` | interacțiune de ecran (atribuire pe fișier) | ? |verificat 04.09.2026 (lot 12) — helper care construiește HTML-ul semaforului de pe carduri. Nicio cerere, niciun câmp|
|494|Ecranul `static/js/ecrane/setari.js` — 10 rute chemate: `/cabinet/api-chei`, `/cabinet/api-chei/{}`, `/eu/cabinet`, `/eu/competente`, `/eu/profil`, `/eu/schimba-parola`, `/gdpr/cerere-stergere`, `/gdpr/export-cabinet`, `/spv/autorizare`, `/spv/stare`|`static/js/ecrane/setari.js`|interacțiune de ecran (atribuire pe fișier)|da|probat invalid 04.09.2026 — arhiva GDPR spunea „Incearca din nou” peste motivul real; **reparata** (R131)|
| 495 | Ecranul `static/js/ecrane/supervizor.js` — 1 rute chemate: `/supervizor` | `static/js/ecrane/supervizor.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 496 | Ecranul `static/js/ecrane/termene.js` — 1 rute chemate: `/termene` | `static/js/ecrane/termene.js` | interacțiune de ecran (atribuire pe fișier) | da |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 497 | Ecranul `static/js/ecrane/tipare.js` — 2 rute chemate: `/tipare`, `/tipare/ai` | `static/js/ecrane/tipare.js` | interacțiune de ecran (atribuire pe fișier) | nu |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 498 | Ecranul `static/js/ecrane/validat.js` — 8 rute chemate: `/coada`, `/coada/{}/aproba`, `/coada/{}/continut`, `/coada/{}/depune`, `/coada/{}/respinge`, `/eu/patru-ochi`, `/eu/permisiuni`, `/tenants` | `static/js/ecrane/validat.js` | interacțiune de ecran (atribuire pe fișier) | da |neprobat — parcurs 04.09.2026 (lot 12), 0 câmpuri: coada nu are formular. Butoanele («Confirmă depunerea», «Renunță») acționează pe un element ales — iar depunerea iese la SPV, deci nu se apasă|
| 499 | Ecranul `static/js/ecrane/woo_ecran.js` — 2 rute chemate: `/tenants/{}/woocommerce/config`, `/tenants/{}/woocommerce/sincronizeaza` | `static/js/ecrane/woo_ecran.js` | interacțiune de ecran (atribuire pe fișier) | da |neprobat — parcurs 04.09.2026 (lot 12), fișierul ecranului «Magazin online»; geamănul lui `#fa-magazin` (#444) a dat `campuri=0` — configurarea cere întâi o conexiune|
| 500 | Ecranul `static/js/navigator.js` — 8 rute chemate: `/admin/activitate/cabinete`, `/eu/anunturi`, `/eu/anunturi/{}/confirma`, `/eu/calitate`, `/notificari`, `/notificari/citit`, `/notificari/contor`, `/notificari/sumar` | `static/js/navigator.js` | interacțiune de ecran (atribuire pe fișier) | da |verificat 05.09.2026 (lot 13) — **fără suprafață de intrare**: șablonul care randează ecranul nu conține niciun `<input>`, `<textarea>` sau `<select>`. Nu e „fără defect” pe o probă — e verdict pe criteriul din `DECIZII.md` 33: un ecran fără câmp editabil nu poate primi date greșite de la un om|
| 501 | Ecranul `static/js/sesiune.js` — 0 rute chemate | `static/js/sesiune.js` | interacțiune de ecran (atribuire pe fișier) | ? |verificat 04.09.2026 (lot 12) — modulul de sesiune: citește/scrie `sessionStorage` și anunță schimbarea. Niciun câmp, nicio cerere pornită de om|
|502|Ecranul `static/js/versiune.js` — 0 rute chemate|`static/js/versiune.js`|interacțiune de ecran (atribuire pe fișier)|?|verificat 04.09.2026 — singura cerere catre un FISIER STATIC (`/static/versiune.json`), fara `detail` si necerută de om. Declarata ca exceptie in `scan_descarcare_muta`|

## C. Joburi de fundal — 14

*Din `core/cron.RITMURI` (supravegheate) și `core/cron.NESUPRAVEGHEATE`. Cele două nesupravegheate intră în listă tocmai fiindcă sunt declarate ca atare.*

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 503 | Jobul `alerta_acces` — supravegheat, prag 2 h | `core/alerta_acces.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 504 | Jobul `audit_retentie` — supravegheat, prag 50 h | `core/audit_retentie.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 505 | Jobul `expirare_cote` — supravegheat, prag 800 h | `core/expirare_cote.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 506 | Jobul `facturi_recurente` — supravegheat, prag 50 h | `core/facturi_recurente.py` (fundal) | rulare periodică | da | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 507 | Jobul `monitor_fiscal` — supravegheat, prag 50 h | `core/monitor_fiscal.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 508 | Jobul `notificari_scadenta` — supravegheat, prag 50 h | `core/notificari_scadenta.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 509 | Jobul `sinteza_zilnica` — supravegheat, prag 96 h | `core/sinteza_zilnica.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 510 | Jobul `sonda_web` — supravegheat, prag 2 h | `core/sonda_web.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 511 | Jobul `spv_poll` — supravegheat, prag 2 h | `core/spv_poll.py` (fundal) | rulare periodică | da | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 512 | Jobul `spv_receive` — supravegheat, prag 2 h | `core/spv_receive.py` (fundal) | rulare periodică | da | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 513 | Jobul `spv_refresh` — supravegheat, prag 50 h | `core/spv_refresh.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 514 | Jobul `woocommerce` — supravegheat, prag 50 h | `core/woocommerce.py` (fundal) | rulare periodică | da | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 515 | Jobul `cron` — NESUPRAVEGHEAT — heartbeat-ul insusi - cere deadman EXTERN | `core/cron.py` (fundal) | rulare periodică | nu | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |
| 516 | Jobul `iconta-backup` — NESUPRAVEGHEAT — shell, nu modul; alerteaza singur (iconta-backup.sh) | `core/iconta-backup.py` (fundal) | rulare periodică | ? | în afara perimetrului etapei 1 — job de fundal: nu primește nimic de la un om |

## D. Instrumente din `scripts/` — 37

*Nu le atinge un contabil, dar există și se execută. Intră în listă fiindcă comanda spune „fără filtrări de niciun fel”; se probează altfel decât o rută — prin rulare directă —, iar unele n-au sens de probat invalid/valid. Motivul se scrie la probare.*

| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |
|---|---|---|---|---|---|
| 517 | CONTAREA ISTORICULUI — R89, blocul JJJ (29.08.2026) | `scripts/contare_istorica.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 518 | scripts/curatenie.py — CE E UN COMMIT DE CURATENIE, derivat din INDEX, nu declarat | `scripts/curatenie.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 519 | FUZIUNEA ADRESELOR unei persoane — R63, blocul QQQ (29.08.2026) | `scripts/fuziune_adrese.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 520 | Inlocuire de text intr-un document, care AFIRMA ca a gasit potrivirea | `scripts/inlocuieste.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 521 | MĂSURĂTOARE (01.09.2026): cât se suprapun listele pe care le urmez | `scripts/masoara_suprapunerea.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 522 | scripts/perimetru.py — PERIMETRUL PORTII SCURTE, derivat din cod | `scripts/perimetru.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 523 | Unealta de aducere din legislatie.just.ro (Portalul Legislativ) | `scripts/portal_legislativ.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 524 | PROBA PE DATE REALE a lanțului facturii — DDD, EEE, FFF, GGG | `scripts/proba_contare_reala.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 525 | PROBA că un eșec de trimitere a emailului LASĂ URMĂ — R73, blocul TTT3 (29.08.2026) | `scripts/proba_esec_email.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 526 | EXECUȚIA celor 18 rânduri de verificare din `TRASEE_VERIFICARI.md` — dezlegarea și recunoașterea | `scripts/proba_verificari_trasee.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 527 | scripts/publica_static.py — CE SE SERVESTE nu mai e CE E IN LUCRU | `scripts/publica_static.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 528 | SECȚIUNEA B a raportului („UNDE SUNTEM"), DERIVATĂ din `CONFORMITATE.md` | `scripts/raport_b.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 529 | CE PRODUCE APLICAȚIA PE FIECARE REGIM REAL — pasul 1b, 29.08.2026 | `scripts/scan_1b_regimuri.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 530 | SE POATE VERIFICA CE IESE? — pasul 1c, 29.08.2026 | `scripts/scan_1c_verificabil.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 531 | Pentru cate rute e ORB PRIN CONSTRUCTIE detectorul de apelanti din R70 | `scripts/scan_ancore_rute.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 532 | FAZA 4, axa D despicata: „odata cu fixul" ascunde DOUA lucruri, iar „singura" ascunde alte doua | `scripts/scan_axa_garzi.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 533 | scripts/scan_contract_ecran.py — contractul ECRAN ↔ RUTĂ, măsurat | `scripts/scan_contract_ecran.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 534 | RAZA VERIFICATORULUI: fiecare regulă din DESIGN_SYSTEM.md, față în față cu ce verifică el — 30.08.2026 | `scripts/scan_ds_verificator.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 535 | scripts/scan_functionalitati.py — LISTA FUNCTIONALITATILOR, derivata din cod | `scripts/scan_functionalitati.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 536 | Inventarul gărzilor, DERIVAT din cod — blocul generat din `GARZI.md` | `scripts/scan_garzi_inventar.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 537 | scripts/scan_instrumente.py - FAZA 4: pe ce instrument sta fiecare garda, si a fost calibrat | `scripts/scan_instrumente.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 538 | scripts/scan_lista3.py — lista 3, DERIVATA din registru, nu numarata cu mana | `scripts/scan_lista3.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 539 | FAZA 4, pasul 5: mutatia care probeaza garda e REPRODUCTIBILA azi? O garda se dovedeste printr-un RED-proof: strici cod… | `scripts/scan_mutatie_garzi.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 540 | Cifrele despre DATE din `PREDARE_LANT.md`, interogate din bază — blocul generat | `scripts/scan_predare_cifre.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 541 | CÂT DE MARE E CLASA „RUTA LIVREAZĂ, ECRANUL TACE" — măsurarea lui R97, 29.08.2026 | `scripts/scan_r97_livrat_tacut.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 542 | scripts/scan_ramas.py — CE A RAMAS DE FACUT, derivat din fisiere, cu sursa pe fiecare rand | `scripts/scan_ramas.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 543 | scripts/scan_refuzuri.py — CE POARTA un refuz al aplicatiei, si ce nu poarta | `scripts/scan_refuzuri.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 544 | CÂTE REGIMURI FISCALE EXERCITĂ PORTOFOLIUL — prima operațiune din E1 (1a), 29.08.2026 | `scripts/scan_regimuri.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 545 | CLASIFICAREA rutelor fără apelant — R70, blocul SSS (29.08.2026) | `scripts/scan_rute_clasificate.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 546 | scripts/scan_trasee.py — INVENTARUL TRASEELOR, calculat, nu ținut minte | `scripts/scan_trasee.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 547 | Seed D406 pentru tenant_013 (ALFA) — date de TEST cu structura si validitate REALE, apte de proba DUK | `scripts/seed_alfa_d406.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 548 | SONDA CCC — cate facturi DECLARABILE nu au nicio nota contabila, cu TVA-ul lor, pe firme si luni | `scripts/sonda_facturi_necontate.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 549 | SONDA BBB — gaura mecanismului de idempotenta: note care ating conturi de factura, FARA sa poarte `factura_id` | `scripts/sonda_note_fara_factura_id.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 550 | SONDA R34 — nota de salarii vs D112 declarat, pe cele 40 de perechi (firma x luna) | `scripts/sonda_r34.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 551 | SONDA R35 — verdicte TVA care ies VERZI peste un necunoscut pe care il au in mana | `scripts/sonda_r35.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 552 | VERIFICAREA VIGORII PE ARTICOL (Partea 0, pasul 2) — la sursa externa sau din corpus | `scripts/vigoare_articol.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |
| 553 | scripts/vigoare_punct.py — vigoarea PE PUNCT, pentru actele structurate pe puncte (R2) | `scripts/vigoare_punct.py` | rulare din linia de comandă | nu | în afara perimetrului etapei 1 — instrument din `scripts/`: nu-l atinge un contabil |

---

## Ce a ieșit din derivare, ca cifre

- **rute**: 427 (din care 3 montate din `core/spv_rute.py`)
- **ecrane**: 75 · **joburi**: 14 · **instrumente**: 37
- **TOTAL unități: 553**
- **rute orfane** (în niciun traseu și în nicio suprafață declarată): 0
- **module de declarație** din care s-a derivat coloana: 70 · **tabele citite de ele**: 23
- **rute** cu declarație = **da**: 197 · **nu**: 227 · **?**: 3 *(numai secțiunea A; ecranele și joburile își poartă coloana în tabelele lor)*

