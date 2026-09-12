# -*- coding: utf-8 -*-
"""REGISTRUL STRATURILOR — singura sursă autoritativă pentru întrebarea „ce strat e modulul ăsta?".

DE CE EXISTĂ (P7 valul V3, 13.09.2026). Diagnosticul P7 a măsurat criteriul canonic *„un motor
fiscal nu importă `db`"* și a găsit **zero** încălcări — dar pe un univers derivat din DOUĂ
instrumente care nu cad de acord: generatoarele celor nouă declarații (25 de module) și modulele
care poartă valori fiscale (104). Șapte module cădeau între ele, iar pentru ele întrebarea nu se
putea decide. *Un criteriu al cărui univers nu e definit nu e o măsurătoare, e o aproximare.*

Registrul închide nedeterminarea: fiecare modul relevant are EXACT un strat, scris, cu motivul
mecanic lângă el și cu regula canonică pe care se sprijină.

CELE PATRU STRATURI sunt cele din `PLAN_HARDENING.md:742-746`, niciunul în plus:
  · **HTTP**          — validare de formă, autentificare, traducerea erorilor în coduri;
  · **USE_CASE**      — deține tranzacția (P4), orchestrează, fără reguli fiscale;
  · **FISCAL_ENGINE** — primește date, întoarce rezultat, nu deschide conexiuni;
  · **REPOSITORY**    — singurul care știe SQL și scheme.

## CE ÎNSEAMNĂ `mixt_cu`, și de ce nu e un al cincilea strat

Multe module fac azi două lucruri deodată — un motor fiscal care își citește singur datele, o rută
care scrie SQL. Comanda V3 e limpede: *„Dacă un modul combină efectiv două straturi și nu poate primi
onest un singur strat: NU inventa clasificarea."* Deci `strat` rămâne **responsabilitatea principală**
(una singură, niciodată două), iar `mixt_cu` numește al doilea strat pe care modulul îl atinge de
fapt. Un modul cu `mixt_cu` nu e o excepție tolerată: e o poziție de lucru pentru valul care separă.

**38 din 114** sunt mixte azi. Cifra nu se ascunde și nu se rotunjește.

## DE UNDE VINE FIECARE DECLARAȚIE

`motiv` e faptul mecanic măsurat la declarare (câte rute, câte instrucțiuni SQL, dacă importă `db`,
dacă e generator de declarație), iar `regula` e linia din textul canonic pe care se sprijină. Pentru
**29 de module** faptele mecanice nu ajungeau — acolo scrie *„citit la sursa"*, fiindcă le-am citit
și am decis, nu le-am derivat dintr-un nume de fișier.

## CE NU E REGISTRUL

Nu e generat la fiecare rulare: e **scris**. Un registru care s-ar regenera din euristici ar muta
autoritatea înapoi la euristică — exact ce V3 trebuia să elimine. Tabelul de mai jos a fost tastat o
dată cu ajutorul unui script, apoi verificat; de aici încolo, adevărul e ce scrie aici, iar
`scripts/scan_p7_straturi.py` îl **consumă**, nu îl recalculează.

UNIVERSUL (cine TREBUIE să fie în registru) se derivă însă mecanic, în afara fișierului ăstuia, și e
verificat de `core/test_p7_straturi.py`: reuniunea celor două definiții de „fiscal" plus modulele cu
rute, fără instrumentele de măsură și fără probe. Un modul nou care intră în univers fără declarație
**pică poarta** — registrul e exhaustiv față de UNIVERS, nu față de ziua în care a fost scris.
"""
import collections

HTTP = "HTTP"
USE_CASE = "USE_CASE"
FISCAL_ENGINE = "FISCAL_ENGINE"
REPOSITORY = "REPOSITORY"

#: Cele patru, în ordinea din textul canonic. Orice altă valoare e invalidă, iar o probă o cere.
STRATURI = (HTTP, USE_CASE, FISCAL_ENGINE, REPOSITORY)

D = collections.namedtuple("D", "cale strat mixt_cu motiv regula")

#: Felurile de declarație stricată — mulțime ÎNCHISĂ, ca o probă să întrebe codul, nu proza.
STRAT_NECUNOSCUT = "STRAT_NECUNOSCUT"
MIXT_NECUNOSCUT = "MIXT_NECUNOSCUT"
MIXT_CU_SINE = "MIXT_CU_SINE"
DUBLURA = "DUBLURA"
FARA_TEMEI = "FARA_TEMEI"

Invalid = collections.namedtuple("Invalid", "cale cod detaliu")

#: TUPLU, nu dicționar — deliberat, două motive: un tuplu e imutabil, deci nu intră în inventarul de
#: stare mutabilă al P6; și un dicționar ar ascunde o cale declarată de două ori, pe când aici
#: dublura rămâne vizibilă și o probă o caută.
REGISTRU = (
    D("core/amef_import.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/asistenti_api.py", REPOSITORY, None,
      "«managementul actorilor de cabinet» — operatii pe date, 25 de instructiuni SQL, nicio regula fiscala proprie",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/asociati_import_api.py", REPOSITORY, None,
      "import de asociati per firma; 4 SQL, zero calcul fiscal",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/audit_preluare.py", REPOSITORY, None,
      "«audit de PRELUARE firma» — citeste si scrie urme; 10 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/avansuri.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/bacsis.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/beneficii_api.py", FISCAL_ENGINE, REPOSITORY,
      "«beneficii extrasalariale ONE-OFF pe luna» — plafoane fiscale aplicate pe date, si 6 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/bilant_api.py", REPOSITORY, None,
      "isi spune singur stratul: «S1005 - strat DB: solduri finale + rulaje din note VALIDATE, apoi core.bilant» — calculul e in `core/bilant.py`, aici e accesul la date",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/casa.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/cashflow.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/categorie_marime.py", FISCAL_ENGINE, REPOSITORY,
      "«Categoria de marime a entitatii» — incadrare pe praguri legale; 1 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/common.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/comodat_chirii.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/contracte_speciale.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/control_fiscal_api.py", FISCAL_ENGINE, REPOSITORY,
      "«semafor de conformare fiscala per firma» — produce un verdict fiscal; 8 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/control_incrucisat.py", FISCAL_ENGINE, REPOSITORY,
      "«verificare INCRUCISATA declaratie vs contabilitate» — compara doua evidente dupa reguli fiscale; 45 SQL, cel mai amestecat modul din univers",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/cor_api.py", REPOSITORY, None,
      "nomenclatorul COR — depozit de nomenclator; 5 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/cote_tva.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/curs_bnr.py", REPOSITORY, None,
      "«curs valutar BNR pentru facturi in valuta» — aduce si pastreaza cursuri, nu aplica o regula fiscala; valorile fiscale numarate de scan_constante sunt praguri de cache",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/d100.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 3 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d100_pozitia_116.py", FISCAL_ENGINE, None,
      "generator al uneia dintre cele noua declaratii; zero SQL, zero db",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d100_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 2 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d101.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 5 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d101_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d101g.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d104.py", FISCAL_ENGINE, REPOSITORY,
      "poarta valori fiscale (scan_constante) si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d108.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d112.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 3 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d112_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 6 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d120.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d169.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d169n.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d200.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d201.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d204.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d205.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 3 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d205_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 2 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d207.py", FISCAL_ENGINE, REPOSITORY,
      "poarta valori fiscale (scan_constante) si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d212.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d212_engine.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d213.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d214.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d216.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d220.py", FISCAL_ENGINE, REPOSITORY,
      "poarta valori fiscale (scan_constante) si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d221.py", FISCAL_ENGINE, REPOSITORY,
      "poarta valori fiscale (scan_constante) si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d223.py", FISCAL_ENGINE, REPOSITORY,
      "poarta valori fiscale (scan_constante) si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d230.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d300.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 8 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d300_manual_api.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 5 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d300_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 2 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d301.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 2 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d301_operatiuni_api.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 4 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d301_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d318.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d390.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 12 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d390_clasificare_api.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 5 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d390_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 5 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d394.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 4 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d394_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 1 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d397.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d398.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d399.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d401.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d402.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d403.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d406.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 9 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d406_active.py", FISCAL_ENGINE, None,
      "generator al uneia dintre cele noua declaratii; zero SQL, zero db",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d406_reconciliere.py", FISCAL_ENGINE, REPOSITORY,
      "generator al uneia dintre cele noua declaratii si 2 instructiuni SQL",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d406_stocuri.py", FISCAL_ENGINE, None,
      "generator al uneia dintre cele noua declaratii; zero SQL, zero db",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d407.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d600.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/d603.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/decontari_asociati.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/deconturi.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/duk.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/efactura_send.py", FISCAL_ENGINE, REPOSITORY,
      "«generator XML UBL 2.1 / CIUS-RO» — produce un document normat din date; 8 SQL + import `db`",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/export_saga.py", REPOSITORY, None,
      "export de facturi catre alt program; 4 SQL, zero regula fiscala",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/factura_pdf.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/facturi_api.py", REPOSITORY, None,
      "«facturi in schema unui tenant: lista, creare, detalii, stergere» — CRUD; 19 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/firma_rezumat.py", REPOSITORY, None,
      "«MODELUL DE CITIRE al portofoliului» — P2; un read-model e prin definitie repository",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/import_export.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/intrastat.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/leasing.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/lichidare.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/monitor_fiscal.py", USE_CASE, REPOSITORY,
      "«cron saptamanal. Citeste noutatile ANAF/MF, AI filtreaza» — orchestreaza o munca de fundal si o persista; nu calculeaza nicio obligatie",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/motor.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/notificari_scadenta.py", USE_CASE, REPOSITORY,
      "«notificare email scadenta/restanta» — orchestreaza un efect extern peste date citite; pragul de zile e o regula de produs, nu o cota",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/obiecte_inventar.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/ong.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/perisabilitati.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/provizioane.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/registru_evidenta_fiscala.py", FISCAL_ENGINE, REPOSITORY,
      "registru fiscal: compune si persista randuri dupa norma; 3 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/registru_inventar.py", FISCAL_ENGINE, REPOSITORY,
      "«Registrul-inventar (cod 14-1-2)» — unul dintre cele trei registre obligatorii; 3 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/reverificare.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/salariati_api.py", REPOSITORY, None,
      "«salariati in schema unui tenant: lista, creare, detalii» — CRUD; 21 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/salariati_import_api.py", REPOSITORY, None,
      "import de salariati per firma; 4 SQL",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/salarii_contare.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/salarizare.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/scadentar.py", FISCAL_ENGINE, REPOSITORY,
      "«scadentar facturi emise neincasate» — clasificare pe praguri de zile. ATENTIE: docstringul spune «Calcul PUR, fara DB», dar modulul are `pull`/`seteaza_optin`/`seteaza_supapa` cu 5 SQL — proza descrie doar miezul pur (clasa R16). Consemnat, NEreparat aici",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/scadente.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/sponsorizari.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/spv_rute.py", HTTP, None,
      "3 rute montate in modul",
      "PLAN_HARDENING.md:743 — stratul HTTP e acolo unde sunt rutele"),
    D("core/stare_partajata.py", REPOSITORY, None,
      "«starea business care nu mai are voie sa traiasca in memoria unui proces» (P6 valul 1) — esecuri de autentificare si cooldown de alerte; nicio regula fiscala",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/stat_plata_api.py", REPOSITORY, None,
      "acces la statele de plata; 3 SQL, calculul e in `salarizare`",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/stat_plata_emis.py", REPOSITORY, None,
      "«statul de plata ca DOCUMENT EMIS, nu ca vedere recalculata» — pastreaza documentul emis",
      "citit la sursa (docstring + ce face modulul)"),
    D("core/stocuri.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/taxare_inversa.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/termene_api.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/tva_agricultori.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/tva_aur.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/tva_incasare.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/tva_marja.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/tva_marja_turism.py", FISCAL_ENGINE, None,
      "poarta valori fiscale (scan_constante); zero SQL, zero db — pur prin constructie",
      "PLAN_HARDENING.md:745 — motorul fiscal primeste date si intoarce rezultat"),
    D("core/repo_admin.py", REPOSITORY, None,
      "P7 · V1: panoul de administrare: sănătate, activitate, anunțuri, evenimente publice — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_casa.py", REPOSITORY, None,
      "P7 · V1: casa: bonuri și chitanțe — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_contabilitate.py", REPOSITORY, None,
      "P7 · V1: notele contabile, planul de conturi, perioadele blocate — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_declaratii.py", REPOSITORY, None,
      "P7 · V1: coada declarațiilor și artefactele lor — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_efactura.py", REPOSITORY, None,
      "P7 · V1: e-Factura primită și trimiterile către SPV — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_facturi.py", REPOSITORY, None,
      "P7 · V1: facturile din schema unui tenant — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_firma_profil.py", REPOSITORY, None,
      "P7 · V1: profilul firmei din schema ei — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_mijloace_fixe.py", REPOSITORY, None,
      "P7 · V1: mijloacele fixe din schema unui tenant — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_portal.py", REPOSITORY, None,
      "P7 · V1: portalul clientului: solicitări și clienți — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_salariati.py", REPOSITORY, None,
      "P7 · V1: salariații și cheile REGES — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_stocuri.py", REPOSITORY, None,
      "P7 · V1: articolele și mișcările de stoc — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_tenants.py", REPOSITORY, None,
      "P7 · V1: firmele din portofoliu și cabinetele lor — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("core/repo_utilizatori.py", REPOSITORY, None,
      "P7 · V1: conturile și accesul clienților — citiri mutate din rute, zero `get_conn`, zero commit",
      "PLAN_HARDENING.md:746 — repository-ul e singurul care stie SQL si scheme"),
    D("main.py", HTTP, REPOSITORY,
      "421 rute montate in modul si 295 instructiuni SQL",
      "PLAN_HARDENING.md:743 — stratul HTTP e acolo unde sunt rutele"),)


def pe_cale():
    """{cale: D} — construit la apel, nu ținut la nivel de modul (v. nota de la `REGISTRU`)."""
    return {d.cale: d for d in REGISTRU}


def strat(cale):
    """Stratul declarat, sau `None` dacă modulul nu e în registru. Fără implicit: absența se vede."""
    return pe_cale().get(cale, D(cale, None, None, "", "")).strat


def module_din_strat(s):
    """Căile declarate în stratul `s`. Asta consumă detectorul D2 — nicio altă definiție."""
    return {d.cale for d in REGISTRU if d.strat == s}


def mixte():
    """[D] — modulele care ating două straturi. Poziții de lucru pentru valul care separă."""
    return [d for d in REGISTRU if d.mixt_cu]


def declaratii_invalide(registru=None):
    """[(cale, motiv)] — tot ce ar face registrul de necrezut, într-un singur loc.

    Trei feluri, toate cerute de contractul V3: un strat care nu e dintre cele patru · aceeași cale
    declarată de două ori · o declarație fără motiv sau fără regulă (o clasificare fără temei e o
    părere, nu o declarație).
    """
    rele, vazute = [], set()
    for d in (REGISTRU if registru is None else registru):
        if d.strat not in STRATURI:
            rele.append(Invalid(d.cale, STRAT_NECUNOSCUT, repr(d.strat)))
        if d.mixt_cu is not None and d.mixt_cu not in STRATURI:
            rele.append(Invalid(d.cale, MIXT_NECUNOSCUT, repr(d.mixt_cu)))
        if d.mixt_cu == d.strat:
            rele.append(Invalid(d.cale, MIXT_CU_SINE, repr(d.strat)))
        if d.cale in vazute:
            rele.append(Invalid(d.cale, DUBLURA, "a doua declaratie pentru aceeasi cale"))
        vazute.add(d.cale)
        if not (d.motiv or "").strip() or not (d.regula or "").strip():
            rele.append(Invalid(d.cale, FARA_TEMEI, "motiv sau regula lipsa"))
    return rele


def numaratori():
    """Cifrele registrului, într-un singur loc, ca raportul să nu le recalculeze cu altă definiție."""
    pe_strat = collections.Counter(d.strat for d in REGISTRU)
    return {
        "MODULE_DECLARATE": len(REGISTRU),
        "MULTI_LAYER_MODULES": len([1 for x in declaratii_invalide() if x.cod == DUBLURA]),
        "UNKNOWN_LAYER_MODULES": len([1 for x in declaratii_invalide()
                                      if x.cod in (STRAT_NECUNOSCUT, MIXT_NECUNOSCUT)]),
        "MIXED_LAYER_MODULES": len(mixte()),
        "pe_strat": dict(pe_strat),
    }


def main():
    n = numaratori()
    print("REGISTRUL STRATURILOR")
    print("  module declarate     : %d" % n["MODULE_DECLARATE"])
    for s in STRATURI:
        print("    %-14s %d" % (s, n["pe_strat"].get(s, 0)))
    print("  mixte (doua straturi): %d" % n["MIXED_LAYER_MODULES"])
    for d in mixte()[:5]:
        print("    %s  %s + %s" % (d.cale, d.strat, d.mixt_cu))
    print("  declaratii invalide  : %d" % len(declaratii_invalide()))
    for x in declaratii_invalide():
        print("    %s: %s (%s)" % (x.cale, x.cod, x.detaliu))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
