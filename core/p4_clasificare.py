# -*- coding: utf-8 -*-
"""core/p4_clasificare.py — CLASIFICAREA operațiilor compuse, scrisă o dată și păzită.

**DE CE EXISTĂ CA FIȘIER.** `scripts/scan_tranzactii.py` produce inventarul brut: ce cale are mai
multe frontiere de tranzacție, scrie în mai multe locuri, sau amestecă o scriere cu un efect pe care
`rollback` nu-l desface. Inventarul **nu judecă** — nu poate. Judecata e aici, iar regula lui P4 e
că **orice excludere din `CRITICAL_COMPOSITE` cere justificare explicită scrisă**.

Fișierul ăsta e chiar acea justificare, într-o formă care nu poate îmbătrâni tăcut:
`core/test_tranzactii_clasificate.py` recalculează inventarul la fiecare rulare și cere ca

  * **fiecare** cale peste prag să fie clasificată aici — una nouă, neclasificată, **cade poarta**;
  * **fiecare** clasificare să poarte un motiv scris (nu o etichetă);
  * **fiecare** `CRITICAL_COMPOSITE` să numească o probă de injecție de defect care **există**.

Fără gardul ăsta, clasificarea ar fi o listă din raportul unei zile — adevărată atunci, mută după.

---

## CRITERIUL, scris înainte de a fi aplicat

O cale e **CRITICAL_COMPOSITE** dacă un defect **între** două dintre efectele ei poate lăsa stare
persistentă care e:

  **(a) evidență greșită sau lipsă** — ceva ce se citește ca fapt și nu e (o confirmare peste o
      depunere care nu s-a făcut, un cont fără dovada acordului);
  **(b) o fundătură pentru om** — o stare din care actul nu se mai poate duce la capăt și nici
      relua (un utilizator fără nicio cale de intrare);
  **(c) un efect ireversibil rămas fără perechea lui din bază** — un e-mail plecat, un token rotit
      la ANAF, un fișier șters, în timp ce rândul care le consemna s-a întors;

**și** eșecul **nu e anunțat** — nu iese la iveală printr-o alertă, printr-un refuz care-l numește,
sau printr-o stare vizibilă pe ecran.

Ultima condiție face diferența dintre o gaură și o **degradare declarată**. Un act care își
înghite eșecul într-un `print` e altceva decât unul care alertează și lasă starea numită.

## Ce înseamnă celelalte două clase

**NON_CRITICAL_COMPOSITE** — calea CHIAR e compusă (inventarul are dreptate), dar defectul dintre
efecte nu produce niciunul din cele trei rezultate de mai sus: fie partea a doua e o urmă
best-effort care se anunță când cade, fie e un marcaj de progres pe care următoarea rulare îl
reface, fie despărțirea e **deliberată** și scrisă lângă cod.

**FALSE_POSITIVE** — inventarul s-a înșelat, și se spune **prin ce**: omonimie, ramuri exclusive
aplatizate, o interogare luată drept efect. Fiecare fals pozitiv numește oarbirea din antetul
instrumentului care l-a produs — altfel „fals pozitiv" ar fi doar un mod politicos de a spune
„n-am verificat".

---

## O deosebire care taie jumătate din listă: INTEROGARE ≠ EFECT

`requests.post` către validatorul de CUI al ANAF și `requests.post` care încarcă o factură în SPV
arată identic pentru un scaner. Nu sunt același lucru:

  * o **interogare** (validare CUI, XML-ul BNR, pagina de noutăți ANAF, comenzile WooCommerce) nu
    lasă nimic în urmă la celălalt capăt. Un `rollback` la noi n-are ce desface acolo. Ce rămâne e
    **durata** tranzacției, care e o întrebare de concurență (P3/R178), nu de proprietate;
  * un **efect** (e-mail trimis, factură încărcată la ANAF, token rotit, fișier șters) schimbă o
    stare care nu e a noastră.

Instrumentul nu poate face deosebirea; ea se scrie aici, per loc, și e chiar motivul pentru care
clasificarea nu se poate genera.

**NOTĂ DE FORMĂ:** citatele din interiorul șirurilor folosesc «...», nu ghilimele românești.
Un `„...”` scris cu ghilimea de închidere ASCII termină șirul Python — capcană cunoscută a casei,
și a picat chiar la prima scriere a fișierului ăstuia.
"""

import io
import os

#: Rădăcina repo-ului, ca `acoperire_injectie()` să poată citi fișierul de probe cu `ast`.
_RAD_MODUL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CRITIC = "CRITICAL_COMPOSITE"
NECRITIC = "NON_CRITICAL_COMPOSITE"
FALS = "FALSE_POSITIVE"

#: Tiparul de casă pentru un efect ireversibil, numit o dată și citat de mai multe ori.
TIPARUL_PREGATIT = (
    # [P7 · D2, 13.09.2026] `trimite` s-a mutat din `core/efactura_send.py` in
    # `core/efactura_trimitere.py` — acelasi cod, acelasi sir de trei tranzactii, alt strat.
    # Clasificarea P4 e neschimbata: s-a mutat fisierul, nu proprietatea.
    "tiparul din `efactura_trimitere.trimite` si `etransport_send.trimite`: randul care consemneaza "
    "actul se scrie si SE COMITE cu starea «pregatit» INAINTE de efectul ireversibil, iar "
    "rezultatul se scrie dupa, in tranzactia lui. Asa, un esec lasa un rand vizibil («pregatit» "
    "care n-a mai avansat), nu o tacere"
)

CLASIFICARE = {

    # ======================================================================
    #  CRITICAL_COMPOSITE — fiecare cu proba lui de injecție de defect
    # ======================================================================

    "POST /coada/{coada_id}/depune": {
        "clasa": CRITIC,
        "reparat": True,
        "efecte": "confirmarea supervizorului (public.supervizor_confirmari) <-> aprobarea si "
                  "marcarea depunerii (public.declaratii_coada, public.declaratii_depuse)",
        "de_ce":
            "(a) evidenta gresita. Confirmarea se scria in tranzactia ei, iar depunerea in alta; "
            "intre ele stateau trei refuzuri posibile — dreptul `poate_depune` (403), starea "
            "elementului (409/404) si orice eroare de baza. Rezultatul: o confirmare scrisa, cu "
            "numele omului si motivul lui, peste o depunere care nu s-a facut niciodata. Nimic "
            "n-o anunta. Iar `PREDARE_LANT.md` afirma, despre proba din 03.09, ca «confirmarea si "
            "depunerea sunt un singur act, nu doua care se pot desparti» — erau doua.",
        "reparatie":
            "o singura tranzactie tine confirmarea, aprobarea si marcarea; dreptul se cere inaintea "
            "oricarei scrieri; poarta supervizorului sta sub `SAVEPOINT`, ca sa nu blocheze "
            "niciodata fara sa otraveasca tranzactia depunerii",
        "proba": "test_depunere_confirmarea_nu_ramane_fara_depunere",
    },

    "POST /auth/login": {
        "clasa": NECRITIC,
        "efecte": "contorul de esecuri (public.login_esecuri) <-> verdictul de autentificare "
                  "<-> randul de audit (public.audit_log)",
        "de_ce":
            "[P6 val 1, 12.09.2026] ruta a intrat in inventar fiindca esecurile de autentificare "
            "nu mai stau in memoria procesului, ci in baza — deci ce era o scriere invizibila a "
            "devenit una numarata. Sunt patru tranzactii scurte, si sunt scurte DELIBERAT: "
            "(1) intrebarea «e blocat?», o citire; (2) autentificarea propriu-zisa; (3) "
            "consemnarea esecului SAU stergerea contorului la reusita; (4) auditul. "
            "NU se pot comasa intr-una singura, si nu dintr-un motiv de stil: blocarea trebuie sa "
            "fie COMISA si vizibila celorlalte procese in clipa in care s-a produs esecul, nu la "
            "sfarsitul cererii; iar o conexiune tinuta peste toti pasii ar fi exact clasa C5 pe "
            "care P5 a inchis-o. "
            "NIMIC PARTIAL NU POATE MINTI: contorul inregistreaza numai ESECURI, iar un esec se "
            "termina cu 401 — deci nu exista stare in care cineva e autentificat si contorul spune "
            "altceva. La reusita, stergerea contorului e ultima scriere inaintea tokenului; daca "
            "ea cade, cererea cade cu ea, iar contorul ramane pe o valoare mai MARE, adica in "
            "partea sigura. Auditul e a patra tranzactie, deliberat, cu `esec_secundar` la cadere "
            "— anuntat, nu tacut, aceeasi decizie ca la `/public/reset-parola/*` din 27.07.2026. "
            "Niciun efect ireversibil in afara aplicatiei pe calea asta.",
    },
    "POST /auth/register": {
        "clasa": CRITIC,
        "reparat": True,
        "efecte": "cabinetul + userul admin (public.accounting_firms, public.users) <-> dovada "
                  "acordului (public.acord_termeni) <-> provizionarea primei firme",
        "de_ce":
            "(a) evidenta lipsa, tacuta. Ruta refuza din prima linie o inregistrare fara bifa "
            "termenilor; dovada bifei se scria insa intr-o a doua tranzactie, ambalata intr-un "
            "`try` care doar TIPAREA la esec. Contul ramanea, dovada consimtamantului putea lipsi, "
            "si nimeni nu afla. Fara bifa contul nu se creeaza — deci nici fara dovada ei.",
        "reparatie":
            "versiunea termenilor se citeste inaintea tranzactiei (un fisier lipsa opreste "
            "inregistrarea, cu 503, inainte de orice scriere), iar `acord_termeni` intra in ACEEASI "
            "tranzactie cu contul. [lotul 12, deficienta 642, PIVOT fata de 27.07.2026] Al treilea "
            "domeniu — firma proprie din CUI — intra si el in tranzactia contului "
            "(`uc_auth._firma_proprie`): comanda Costin 12.2 pct.19, „contul si firma lui se creeaza "
            "impreuna sau deloc”; despartirea de pana atunci lasase un cont fara firma, cu bun venitul "
            "spunand ca firma exista. Bun venitul pleaca dupa commit si spune ce s-a creat.",
        "proba": "test_register_contul_nu_ramane_fara_dovada_acordului",
    },

    "POST /public/confirma-inregistrare": {
        "clasa": CRITIC,
        "reparat": False,
        "efecte": "cererea in asteptare folosita (public.inregistrari_in_asteptare) <-> cabinetul + userul admin "
                  "(public.accounting_firms, public.users) <-> dovada acordului (public.acord_termeni) <-> bun venit, anuntul "
                  "catre superadmin (dupa commit); firma din CUI IN tranzactie (lotul 12, 642)",
        "de_ce":
            "[15.10.2026, lotul 4] Construita direct in forma corecta: un cont fara cererea lui folosita ar putea fi creat de doua "
            "ori de acelasi link; o cerere folosita fara cont ar lasa omul fara cont si fara link. Cererea se blocheaza (`FOR "
            "UPDATE`) si se marcheaza IN ACEEASI tranzactie cu contul si cu dovada acordului (versiunea termenilor de la formular). "
            "Emailurile vin DUPA commit; firma din CUI intra in aceeasi tranzactie (lotul 12, 642: „contul si firma lui se creeaza "
            "impreuna sau deloc”) — un CUI refuzat la confirmare refuza contul, iar linkul ramane nefolosit.",
        "reparatie":
            "nimic de reparat: ruta s-a nascut in forma de mai sus (o tranzactie: cererea blocata + contul + acordul + folosirea "
            "cererii + firma din CUI, de la lotul 12; efectele externe dupa commit). Probele: injectia de mai jos si "
            "core/test_lot12_form2_register.py.",
        "proba": "test_confirmarea_inregistrarii_nu_lasa_cont_fara_cererea_folosita",
    },

    "POST /tenants/{tenant_id}/client-acces": {
        "clasa": CRITIC,
        "reparat": True,
        "efecte": "contul de client + legatura la firma + urma din portal (public.users, "
                  "public.user_tenants, public.urme_portal) <-> tokenul de activare "
                  "(public.tokene_activare) <-> e-mailul cu linkul",
        "de_ce":
            "(b) fundatura. Contul de client se crea cu o parola temporara pe care n-o stie nimeni, "
            "iar tokenul de activare — singura lui cale de intrare — se scria in a doua tranzactie. "
            "O eroare intre ele lasa un utilizator care nu poate intra NICIODATA, in timp ce urma "
            "din portal spunea «cabinetul a dat acces».",
        "reparatie":
            "tokenul se pregateste inaintea tranzactiei si intra in ea, langa cont. E-mailul — "
            "singurul efect ireversibil — ramane unde era: ultimul, dupa ce tranzactia s-a inchis.",
        "proba": "test_client_acces_contul_nu_ramane_fara_token",
    },

    "core/spv_conector.reimprospateaza_token": {
        "clasa": CRITIC,
        "reparat": True,
        "cale_interna": True,
        "efecte": "rotatia perechii de tokene la ANAF (efect ireversibil, in afara noastra) <-> "
                  "scrierea perechii noi in public.spv_token",
        "de_ce":
            "(c) efect ireversibil ramas fara perechea din baza, si cel mai grav din lista. ANAF "
            "ROTESTE la refresh: in secunda raspunsului, vechiul `refresh_token` e mort acolo. "
            "Perechea noua se scria pe conexiunea APELANTULUI — adica pe tranzactia deschisa de "
            "`apel_anaf`, care traieste pana la capatul apelului real catre ANAF. Orice eroare de "
            "dupa (403 fara drept, cadere de retea, backoff epuizat) intorcea tranzactia si stergea "
            "exact perechea pe care ANAF o considera singura valida. Principalul ramanea deconectat "
            "de la SPV, si nimic nu pica: apelul esua din alt motiv, iar tokenul disparea tacut. "
            "Aceeasi forma avea si `dezactiveaza_token` pe esecul de refresh — se intorcea, deci "
            "tokenul mort ramanea `activ = true`.",
        "reparatie":
            "`_roteste_si_comite()` — perechea rotita si, pe calea de esec, dezactivarea "
            "tokenului mort se COMIT imediat, pe conexiunea pe care o detine `apel_anaf`. E "
            "cealalta fata a regulii «efectul ireversibil vine ultimul»: cand efectul ireversibil e "
            "chiar SURSA valorii de scris, scrierea lui se comite PRIMA. "
            "PRIMA FORMA A REPARATIEI A FOST GRESITA si merita scris: deschidea o a doua conexiune "
            "si scria pe acelasi rand, ceea ce se BLOCHEAZA — tranzactia apelantului poate tine "
            "randul, iar a doua asteapta la infinit. Suita a atarnat la 80%, iar regula era deja "
            "scrisa in casa: o proba care tine o tranzactie deschisa nu poate deschide o a doua "
            "conexiune pe acelasi rand. Limita apartine USE-CASE-ului, nu unei conexiuni noi.",
        "proba": "test_token_rotit_supravietuieste_esecului_de_dupa",
    },

    "core/notificari_scadenta.py::__main__ -> _main()": {
        "clasa": CRITIC,
        "reparat": True,
        "efecte": "e-mailul de scadenta catre CLIENTUL firmei <-> randul care impiedica "
                  "retrimiterea (notificari_scadenta, in schema firmei)",
        "de_ce":
            "(c). E-mailul pleca la clientul firmei, iar randul care opreste a doua trimitere se "
            "scria dupa el — amandoua in tranzactia deschisa pentru TOATA firma, pentru toate "
            "facturile ei. O eroare la orice factura de dupa, sau la commit, intorcea tranzactia: "
            "e-mailurile plecate ramaneau plecate, randurile care le consemnau nu. A doua zi, "
            "cronul le trimitea din nou, aceluiasi client.",
        "reparatie":
            "modulul nu mai scrie NIMIC pe conexiunea apelantului. Pragul se rezerva cu `in_curs` "
            "in tranzactia lui, comisa, apoi pleaca e-mailul, apoi se scrie rezultatul. Alegerea e "
            "deliberata: CEL MULT O DATA, nu cel putin o data — o notificare pierduta ramane "
            "vizibila ca prag `in_curs`; una trimisa de doua ori ajunge la clientul firmei si nu se "
            "mai ia inapoi. " + TIPARUL_PREGATIT,
        "proba": "test_notificare_scadenta_nu_pleaca_de_doua_ori",
    },

    "core/alerta_acces.py::__main__ -> ruleaza()": {
        "clasa": CRITIC,
        "reparat": True,
        "efecte": "alerta de acces anormal (Brevo, art.33 GDPR) <-> randul de dedup "
                  "(public.alerte_acces_dedup)",
        "de_ce":
            "(c), aceeasi clasa ca notificarea de scadenta. Rezervarea ferestrei de dedup se scria "
            "pe conexiunea apelantului, iar `ruleaza` comitea abia la capatul buclei — dupa ce "
            "alertele plecasera. O eroare de dupa intorcea randurile, nu si alertele; la urmatoarea "
            "rulare (cron la 15 minute) plecau din nou, identice. "
            "Nota despre inventar: din cele 16 domenii care scriu pe calea asta, 15 sunt omonimie "
            "(parametrul `trimite` se ciocneste cu `efactura_trimitere.trimite` si surorile lui); real e "
            "unul singur, chiar rezervarea de dedup.",
        "reparatie":
            "`_poate_trimite` isi deschide propria tranzactie si o comite inainte ca alerta sa "
            "plece; conexiunea lui `ruleaza` a ramas o citire.",
        "proba": "test_alerta_acces_dedup_se_comite_inainte_de_alerta",
    },

    "POST /tenants/{tenant_id}/facturi/emite": {
        "clasa": CRITIC,
        "reparat": False,
        "efecte": "factura + liniile ei + numarul din serie + descarcarea de gestiune, toate in "
                  "tranzactia rutei; separat, cache-ul de curs BNR",
        "de_ce":
            "(a) daca ar fi despartita. E actul contabil central: o factura numerotata fara linii, "
            "sau numerotata fara descarcarea de gestiune pe care poarta a promis-o, e evidenta "
            "gresita. Instanta din 04.09 arata ca nu e o grija teoretica: `_salveaza_cache` comitea "
            "pe conexiunea facturii, iar un refuz de curs lasa in baza o factura numerotata si "
            "contata, fara curs.",
        "reparatie":
            "NIMIC DE REPARAT — si tocmai de-asta are proba. Emiterea e deja un singur domeniu "
            "tranzactional; ce se cerea era DOVADA, nu o schimbare. Al doilea domeniu e cache-ul de "
            "curs, mutat pe conexiunea lui prin decizia din 04.09, cu motivul scris langa cod: "
            "cache-ul e o preocupare a aplicatiei, nu a facturii, si trebuie sa supravietuiasca "
            "esecului actului care l-a declansat.",
        "proba": "test_emiterea_facturii_nu_lasa_numar_fara_factura",
    },

    # ======================================================================
    #  NON_CRITICAL_COMPOSITE — compuse, dar defectul dintre efecte nu produce
    #  niciunul din cele trei rezultate; motivul, per cale
    # ======================================================================

    "POST /tenants/{tenant_id}/vanzare-ic": {
        "clasa": NECRITIC,
        "efecte": "factura intracomunitară (un singur domeniu care scrie, prin `emite_factura`) și nota ei, în același domeniu; "
                  "verificarea VIES înainte, în afara oricărei conexiuni",
        "de_ce":
            "un singur domeniu scrie; externele din el sunt o INTEROGARE (modelul AI nu păstrează nimic, `EFECTE_EXTERNE`) și, numai "
            "pe plasă, jurnalul AI-ului simulat. Un eșec al întrebării întoarce „cota nedeterminată” (`cote_tva.potriveste_cota`), "
            "care se cere apoi explicit pe linie — nimic nu rămâne scris pe jumătate. Calea a devenit candidat pe 09.10.2026, când scanerele au învățat clientul SDK-ului Anthropic — nu "
            "fiindcă s-ar fi schimbat ceva în ea. [R193, 10.10.2026] Modelul nu mai e întrebat deloc pe calea asta: linia facturii poartă "
            "contul de venit ales de contabil (același ca pe notă), deci n-are ce cere; rămâne candidat prin scrierile ei compuse.",
    },
    "POST /eu/telefon/cod": {
        "clasa": NECRITIC,
        "efecte": "acordul pentru WhatsApp (public.users.acord_whatsapp_la) <-> codul de confirmare (public.telefon_coduri) <-> mesajul "
                  "cu codul, pe WhatsApp (după commit)",
        "de_ce":
            "[17.10.2026, lotul 7 pct.2.2] Două tranzacții DELIBERAT: (1) acordul se scrie și rămâne chiar dacă WhatsApp nu e activ pe "
            "platformă — omul a bifat, iar refuzul îi spune că acordul s-a salvat; (2) codul se scrie ÎNAINTEA trimiterii, fiindcă un cod "
            "trimis și nescris n-ar mai putea fi confirmat. Nicio combinație nu lasă o stare falsă: acordul fără cod e starea de dinainte "
            "de cerere (numărul rămâne neconfirmat, canalul pe email); un cod scris și netrimis expiră singur și se poate cere altul "
            "(`PAUZA_COD_SEC`). Canalul WhatsApp cere în plus numărul confirmat — CHECK-ul `users_canal_notificari_check` din bază.",
    },
    "POST /tenants/{tenant_id}/reevaluare-valuta/nota": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al lunii în cache (public.curs_bnr_zilnic, înaintea tranzacției) <-> nota de reevaluare (ciornă) cu rândurile "
                  "ei din reevaluari_valuta și înlocuirea ciornei vechi a lunii",
        "de_ce":
            "[lotul 10, deficiența 429, 20.10.2026] Două tranzacții DELIBERAT, ca la emiterea în valută: (1) cursul BNR al ultimei zile "
            "bancare se aduce și se scrie în cache ÎNAINTEA tranzacției notei (`uc_curs_bnr.asigura_cursul`, decizia din 04.09.2026: "
            "cache-ul supraviețuiește eșecului actului, iar descărcarea nu ține o conexiune); (2) actul — ștergerea ciornei vechi a lunii, "
            "nota nouă, liniile și rândurile `reevaluari_valuta` — e într-o singură tranzacție, tot-sau-nimic. Un curs scris și o notă "
            "neînregistrată lasă numai cache-ul mai bogat, care nu e stare a firmei.",
    },
    "POST /tenants/{tenant_id}/facturi-primite/manual": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al facturii în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> validarea: "
                  "factura (facturi + factura_tva_cote + cursul ei), clasificarea, nota contării, recepția în stoc",
        "de_ce":
            "[lotul 12, 477] `uc_factura_primita.factura_primita_manuala`: aceeași formă ca validarea facturii din XML (intrarea de mai "
            "jos) — pre-încălzirea cursului și statutul ANAF ÎNAINTEA tranzacției (cache public, eșecul înghițit deliberat), apoi ACTUL "
            "într-o singură tranzacție, pe drumul comun `uc_factura_primita.valideaza` (factura, clasificarea, `contabilizeaza`, "
            "`intrare_din_factura`); orice refuz (lună închisă, dublură, cotă) anulează tot actul.",
    },
    "POST /tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al facturii în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> validarea: "
                  "factura (facturi + factura_tva_cote + cursul ei), marcarea primitei, clasificarea, nota contării, recepția în stoc",
        "de_ce":
            "[lotul 11, C83, 22.10.2026] `uc_tenants.factura_primita_valideaza` (core/uc_tenants.py:7473): o citire scurtă a XML-ului "
            "(conn0, fără scrieri), apoi `_uc_comun._preincalzeste_cursul` (:7491) — `uc_curs_bnr.asigura_cursul` / `completeaza`, care "
            "scriu NUMAI în cache-ul public, fiecare pe conexiunea lui (decizia din 04.09.2026, `curs_bnr:_descarca`), iar orice eșec e "
            "înghițit DELIBERAT («pre-încălzirea nu poate strica o cerere»); apoi interogarea ANAF a statutului (fără conexiune); apoi "
            "ACTUL, într-o singură tranzacție (:7496 -> commit :7610): `_factura_importata` (factura, cotele, cursul — "
            "`contare_facturi.curs_factura_importate` decide pe cache), marcarea, clasificarea, `contabilizeaza`, `intrare_din_factura`. "
            "Refuzul NIR-ului face `rollback` pe tot actul (:7590). Un cache scris și un act căzut lasă numai cache-ul mai bogat, care nu "
            "e stare a firmei; un cache necompletat (BNR jos) lasă factura FĂRĂ curs, iar contarea o refuză cu ieșirea numită "
            "(`LIPSA_CURS_LEI`, «apasă din nou Contabilizează când BNR răspunde»), pe ecran — nu o tăcere. Același tipar ca "
            "`POST /tenants/{tenant_id}/reevaluare-valuta/nota`.",
    },
    "POST /tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al facturii în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> contarea: "
                  "cursul pus pe factura din XML, nota, refacerea stocului, notificarea «respinsă» marcată înlocuită",
        "de_ce":
            "[lotul 11, C83, 22.10.2026] `uc_tenants.factura_contabilizeaza` (core/uc_tenants.py:3890): citirea scurtă a monedei și "
            "datei (`repo_efactura.moneda_si_data`, fără scrieri), apoi `_preincalzeste_cursul` (:3901), care scrie NUMAI cache-ul public, "
            "pe conexiunile lui, cu eșecul înghițit deliberat; apoi ACTUL într-o singură tranzacție (:3902 -> commit :3942): "
            "`contabilizeaza` (care pune cursul pe factura din XML rămasă fără el — `curs_factura_importate` — și scrie nota, cu "
            "`rezolva_nota_inlocuita` pe ACEEAȘI conexiune), `stocuri_anulare.reface_factura`. Orice `RefuzContare` și avertismentul "
            "notei neschimbate fac `rollback` pe tot (:3925, :3928). Cache scris + act refuzat = numai cache mai bogat; cache "
            "necompletat = refuzul numit `LIPSA_CURS_LEI`, reîncercabil din același buton. Niciun efect al firmei în afara tranzacției.",
    },
    "GET /tenants/{tenant_id}/reevaluare-valuta": {
        "clasa": NECRITIC,
        "efecte": "cursurile BNR de sfârșit de lună în cache (public.alerte_cooldown + public.curs_bnr_zilnic) <-> propunerea "
                  "reevaluării (numai citire)",
        "de_ce":
            "[lotul 11, 22.10.2026] `uc_reevaluare.reevaluare_valuta_propunere` (core/uc_reevaluare.py:85): `_aduce_cursurile` (:92 -> "
            "`asigura_cursul` pe fiecare monedă, :51, regula sfârșitului de lună) scrie NUMAI cache-ul public, pe conexiunile lui, cu "
            "eșecul înghițit deliberat; propunerea (`reevaluare_valuta.propunere`) doar CITEȘTE — nicio scriere în schema firmei. Singurele "
            "scrieri ale căii sunt cache-ul de curs (idempotent, ON CONFLICT DO NOTHING) și rezervarea descărcării (`rezerva_alerta`, un "
            "cooldown), care sunt stare a aplicației, nu a firmei. Un curs lipsă din cache apare pe elementul propunerii ca refuz numit, "
            "pe ecran.",
    },
    "POST /tenants/{tenant_id}/decontare-valuta": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al decontării în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> nota de "
                  "decontare (ciornă) cu liniile ei",
        "de_ce":
            "[lotul 11, 22.10.2026] `uc_tenants.decontare_valuta` (core/uc_tenants.py:7615): `_preincalzeste_cursul` (:7617) scrie NUMAI "
            "cache-ul public, pe conexiunile lui, cu eșecul înghițit deliberat; apoi ACTUL într-o singură tranzacție (:7621 -> commit "
            ":7648): `curs_bnr.curs_pentru` decide pe cache (`CursIndisponibil` -> 409, `MonedaNecotata` -> refuz numit, înaintea "
            "oricărei scrieri), apoi nota și liniile ei. Un cache scris și un act refuzat lasă numai cache-ul mai bogat, care nu e stare a "
            "firmei. (Scanerul nu vede scrierile notei în domeniul actului — `nota_operatiune_ciorna` / `adauga_linie`; sunt în aceeași "
            "tranzacție, citite în cod.)",
    },
    "POST /tenants/{tenant_id}/facturi/previzualizare-lei": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al facturii în cache (public.alerte_cooldown + public.curs_bnr_zilnic) <-> previzualizarea cursului și a "
                  "sumelor în lei (numai citire)",
        "de_ce":
            "[lotul 10 pct.7g / lotul 11, 22.10.2026] `uc_tenants.facturi_previzualizare_lei` (core/uc_tenants.py:6477): "
            "`_preincalzeste_cursul` (:6501) scrie NUMAI cache-ul public, pe conexiunile lui, cu eșecul înghițit deliberat; apoi "
            "`facturi_api.previzualizare_lei` (:6504) doar CITEȘTE («nimic scris»), iar cursul zilei lipsă e întors numit "
            "(`curs_bnr.cursul_zilei_lipsa`) și arătat pe ecranul de emitere. Nicio scriere în schema firmei; cache-ul (idempotent) și "
            "rezervarea descărcării sunt stare a aplicației.",
    },
    "POST /tenants/{tenant_id}/jurnal/{nota_id}/reface": {
        "clasa": NECRITIC,
        "efecte": "verificarea ciornei depășite (regenerare pe uscat, sub SAVEPOINT anulat) <-> refacerea din sursă pe UNUL din drumuri: "
                  "mișcarea de stoc / contarea facturii emise (în tranzacția verificării) SAU statul de plată / amortizarea (tranzacția "
                  "rutei lor) <-> eticheta notei noi (citire)",
        "de_ce":
            "[lotul 11, deficiența 451, 22.10.2026] `uc_tenants.jurnal_reface` (core/uc_tenants.py:7319). Cele trei domenii care scriu din "
            "inventar sunt RAMURI EXCLUSIVE pe `fel`, aplatizate de scaner (ca și «commit parțial» :7347 -> repo_efactura.py:215: commitul "
            "e al ramurii stoc, scrierea al ramurii `factura_emisa`). Pe orice rulare scrie O SINGURĂ tranzacție: stoc -> "
            "`reface_nota_miscare` + commit (:7347); factura emisă -> `ciorne_depasite.reface_factura_emisa` (ștergerea ciornei vechi + "
            "`contabilizeaza` + descrierea, aceeași conexiune) + commit (:7354), iar un refuz face `rollback` pe tot (:7352); salarii / "
            "amortizare -> tranzacția verificării se anulează (:7356, n-a scris nimic: `verifica` rulează sub SAVEPOINT anulat), apoi "
            "`salarii_contare_scrie` / `tenant_amortizare` (:7360, :7362) — exact actul butoanelor «Contabilizează statul» / «Generează "
            "amortizarea», cu tranzacția lor. Citirea etichetei de la capăt nu scrie. O cădere după actul comis lasă ciorna nouă (corectă, "
            "de validat) și o eroare vizibilă; reluarea spune «Nota e la zi» — nicio stare falsă, niciun efect extern.",
    },
    "POST /coada": {
        "clasa": NECRITIC,
        "efecte": "elementul intra in coada <-> verdictul validatorului <-> notificarea validatorilor",
        "de_ce":
            "degradare DECLARATA, nu tacere. Verdictul si notificarea stau fiecare in tranzactia lui, "
            "prinse de `try/except` care LOGHEAZA. Un element fara verdict nu e o stare ascunsa: "
            "`coada_api.aproba` are cod propriu pentru ea (`FARA_VERDICT`) si refuza aprobarea, cu "
            "mesaj. Deci esecul e anuntat exact acolo unde conteaza — la actul urmator.",
    },
    "POST /coada/{coada_id}/regenereaza": {
        "clasa": NECRITIC,
        "efecte": "elementul nou + ieșirea celui vechi din coadă <-> verdictul validatorului <-> notificarea validatorilor",
        "de_ce":
            "[deficiența 297, 17.10.2026] același corp ca `POST /coada` (cererea păstrată în element trece din nou prin `coada_adauga`, "
            "cu aceleași porți), deci aceeași degradare DECLARATĂ. Actul — înlocuirea — e într-o singură tranzacție: UPDATE-ul care scoate "
            "elementul vechi și INSERT-ul celui nou stau în același domeniu (`coada_api.inlocuieste` + `adauga_in_coada`, rollback la "
            "eroare), deci coada nu rămâne nici cu două declarații active, nici cu niciuna. Verdictul și notificarea vin după, logate.",
    },
    "POST /coada/{coada_id}/aproba": {
        "clasa": NECRITIC,
        "efecte": "aprobarea elementului <-> notificarea pregatitorului",
        "de_ce":
            "a doua tranzactie e o notificare, prinsa de `try/except` cu `logging.warning` care "
            "numeste elementul. Actul — aprobarea — e intreg si corect; ce poate lipsi e un anunt, "
            "iar lipsa lui se vede in log. Nici evidenta gresita, nici fundatura.",
    },
    "POST /coada/{coada_id}/respinge": {
        "clasa": NECRITIC,
        "efecte": "respingerea cu motiv <-> notificarea pregatitorului",
        "de_ce":
            "identic cu `/aproba`: a doua tranzactie e anuntul, best-effort si logat, iar actul "
            "respingerii — cu motivul lui — e intreg intr-o singura tranzactie.",
    },
    "POST /tenants/{tenant_id}/jurnal/{nota_id}/retrimite": {
        "clasa": NECRITIC,
        "efecte": "elementul nou din coada (public.declaratii_coada) <-> notificarea validatorilor",
        "de_ce":
            "[validare_note 06.10.2026] ca `/respinge`: actul — nota respinsa pusa din nou la "
            "validare — e intreg intr-o singura tranzactie (verificarea notei si a lunii deschise, "
            "apoi INSERT-ul elementului). A doua tranzactie e anuntul catre validatori, scris DUPA "
            "commit; daca pica, elementul e totusi in coada si se vede in „De validat”. Nici "
            "evidenta gresita, nici fundatura.",
    },
    "POST /public/magic-link": {
        "clasa": NECRITIC,
        "efecte": "numararea ritmului (`cereri_ritm`) <-> tokenul de logare <-> e-mailul cu linkul",
        "de_ce":
            "[E1, 14.09.2026] Calea a devenit compusa fiindca numararea ritmului si-a luat propria "
            "tranzactie, inaintea muncii rutei. DESPARTIREA E SCOPUL, nu un efect secundar: "
            "incercarea se consemneaza INDEPENDENT de ce se intampla dupa. Daca numararea ar sta in "
            "aceeasi tranzactie cu trimiterea, o trimitere cazuta ar sterge si incercarea — iar "
            "cine poate forta esecul ar putea cere la nesfarsit. Ordinea efectelor e cea corecta: "
            "se numara, apoi se lucreaza, apoi pleaca e-mailul (ireversibilul, ultimul). Refuzul "
            "de ritm cade INAINTE de orice atingere a contului, deci nu exista stare partiala.",
    },
    "POST /public/reset-parola/cere": {
        "clasa": NECRITIC,
        "efecte": "tokenul de resetare <-> e-mailul cu linkul <-> randul de audit",
        "de_ce":
            "ordinea e deja cea corecta: tokenul se comite, apoi pleaca e-mailul (efectul "
            "ireversibil, ultimul), apoi se scrie auditul. Auditul e despartit deliberat din "
            "27.07.2026 si, la esec, cheama `observare.esec_secundar` — deci se ANUNTA. Un e-mail "
            "care nu pleaca alerteaza la randul lui (`alerta=True`), fiindca e cale de acces.",
    },
    "POST /public/reset-parola/seteaza": {
        "clasa": NECRITIC,
        "efecte": "parola noua + tokenul consumat <-> randul de audit",
        "de_ce":
            "actul (parola schimbata, token marcat folosit) e o singura tranzactie. Auditul e a "
            "doua, deliberat, cu `esec_secundar` la cadere — anuntat, nu tacut. Aceeasi "
            "justificare ca la `/cere`, si aceeasi decizie scrisa din 27.07.2026.",
    },
    "POST /tenants/{tenant_id}/vector": {
        "clasa": NECRITIC,
        "efecte": "vectorul fiscal + instantaneul TVA (schema firmei) <-> marcajul de progres al "
                  "migrarii (public.migrare_status)",
        "de_ce":
            "a doua tranzactie e un MARCAJ DE PROGRES pentru cardul de migrare, nu evidenta. Daca "
            "nu se scrie, stratul ramane «nefacut» si urmatoarea salvare il reface — starea se "
            "autocorecteaza. Apelul ANAF de dinainte e o INTEROGARE de CUI, nu un efect.",
    },
    "POST /tenants/{tenant_id}/rip-import": {
        "clasa": NECRITIC,
        "efecte": "importul registrului de incasari-plati (o tranzactie, in `rip_migrare_api.importa`) "
                  "<-> marcajul de progres al migrarii",
        "de_ce":
            "[372, comanda Costin 8.2] previzualizarea (`/rip-import/incarca`) nu mai scrie nimic; salvarea reverifica "
            "randurile si scrie numai pe cele bune, intr-o singura tranzactie, iar pe cele respinse le intoarce numite "
            "(niciun rand bun -> refuz, nimic scris). A doua tranzactie e marcajul de progres, aceeasi clasa ca la "
            "`/vector`: nescris, stratul ramane «in lucru» si urmatoarea salvare il reface. Reimportul e aparat de "
            "numaratoarea `sarite_duplicat`. Commitul partial semnalat de instrument e cele DOUA apeluri ale lui "
            "`seteaza_status` din ramurile exclusive ale unui `if`, aplatizate de scaner: nu se executa niciodata amandoua.",
    },
    "POST /tenants/{tenant_id}/etransport/trimite": {
        "clasa": NECRITIC,
        "efecte": "incarcarea notificarii UIT la ANAF (ireversibila) <-> randul din "
                  "etransport_trimiteri <-> rotatia tokenului SPV",
        "de_ce":
            "ordinea e deja corecta si e chiar modelul casei: " + TIPARUL_PREGATIT + ". Randul "
            "`pregatit` se comite inaintea incarcarii, iar rezultatul se scrie dupa, separat. "
            "Rotatia tokenului, cand se intampla pe calea asta, se COMITE imediat pe aceeasi "
            "conexiune (v. `core/spv_conector.reimprospateaza_token`) — deci nici ea nu asteapta "
            "sfarsitul apelului.",
    },
    "POST /tenants/{tenant_id}/facturi/{factura_id}/trimite-spv": {
        "clasa": NECRITIC,
        "efecte": "incarcarea facturii in SPV (ireversibila) <-> randul din efactura_trimiteri "
                  "<-> rotatia tokenului SPV",
        "de_ce":
            "aceeasi justificare ca e-Transport: `efactura_trimitere.trimite` scrie si comite randul "
            "`pregatit`, cu poarta de idempotenta inaintea lui, si abia apoi incarca. Upload-ul "
            "ANAF nu e idempotent, iar codul o spune explicit — de-aia poarta 3 exista.",
    },
    "POST /tenants/{tenant_id}/facturi/{factura_id}/transforma": {
        "clasa": NECRITIC,
        "efecte": "emiterea facturii din proforma + marcarea proformei <-> cache-ul de curs BNR",
        "de_ce":
            "aceeasi tranzactie ca `facturi/emite`, cu un `UPDATE` in plus pe proforma, IN "
            "INTERIORUL ei. Al doilea domeniu e cache-ul de curs, despartit prin decizia din "
            "04.09. Atomicitatea actului e probata de "
            "`test_emiterea_facturii_nu_lasa_numar_fara_factura`, care exercita chiar "
            "`facturi_api.emite_factura`.",
    },
    "POST /api/v1/firme/{tenant_id}/facturi": {
        "clasa": NECRITIC,
        "efecte": "emiterea facturii prin API-ul public <-> cache-ul de curs BNR",
        "de_ce":
            "aceeasi functie de emitere (`facturi_api.emite_factura`), aceeasi tranzactie, alta "
            "poarta de acces (cheie de API). Cache-ul de curs isi are tranzactia lui prin decizia "
            "din 04.09, iar apelul BNR e o INTEROGARE.",
    },
    "POST /tenants/{tenant_id}/woocommerce/sincronizeaza": {
        "clasa": NECRITIC,
        "efecte": "citirea comenzilor din WooCommerce (interogare) <-> emiterea facturilor <-> "
                  "cache-ul de curs",
        "de_ce":
            "`woocommerce.comenzi` e o INTEROGARE HTTP: nu lasa nimic la celalalt capat. Emiterea "
            "fiecarei facturi e atomica (aceeasi functie probata). Ce ramane e durata tranzactiei "
            "peste un apel de retea — intrebare de concurenta, nu de proprietate; e numita in "
            "raport, la restante.",
    },
    "POST /coada/aproba-mai-multe": {
        "clasa": NECRITIC,
        "efecte": "aprobarea fiecarei note selectate <-> notificarea pregatitorului ei",
        "de_ce":
            "fiecare nota trece prin `coada_aproba` — aceeasi functie, aceeasi tranzactie si aceeasi notificare best-effort ca "
            "aprobarea uneia singure (v. `POST /coada/{coada_id}/aproba`). O nota refuzata (alt cabinet, deja aprobata, poarta) "
            "se intoarce numita in `refuzate`, cu mesajul ei, iar celelalte raman aprobate: nu exista stare comuna intre ele, "
            "deci nicio aprobare pe jumatate (retest 08.10 pct.3).",
    },
    "core/migrare_nota_corectie.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "ștergerea stornărilor greșite (schema cu schema) <-> rescrierea descrierii notelor de refacere NIR <-> retrimiterea lor "
                  "la validare <-> notificarea validatorilor",
        "de_ce":
            "fiecare schemă e comisă SEPARAT, iar fiecare pas e idempotent: o a doua rulare nu mai găsește stornări peste o mișcare în "
            "evidență (aceeași definiție, `stocuri_anulare.IN_EVIDENTA`) și nici note respinse pentru descriere. O cădere între pași "
            "lasă o stare din care rularea următoare continuă; notificarea e best-effort, după commit. Niciun efect extern "
            "(comanda Costin 09.10.2026, pct.1).",
    },
    "core/migrari_registru.py::__main__ -> main()": {
        "clasa": NECRITIC,
        "efecte": "migrarea rulată (tranzacțiile ei) <-> rândul ei în `public.migrari_rulate` <-> repornirea aplicației",
        "de_ce":
            "rândul se scrie numai DUPĂ ce migrarea a trecut (o excepție oprește înainte); o cădere între migrare și rând lasă migrarea "
            "rulată dar neînregistrată — gardul rămâne fail-closed (restartul nu se face), iar rularea din nou e sigură fiindcă migrările "
            "sunt idempotente. Repornirea vine ultima, numai dacă `verifica` spune că HEAD nu mai are nimic de rulat (comanda Costin "
            "09.10.2026, pct.2).",
    },
    "core/migrare_retest2.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "coloana `casa_operatiuni.storno_de` (+ cheia străină și unicitatea), schema cu schema <-> rescrierea descrierii "
                  "notelor de refacere NIR <-> retrimiterea lor la validare <-> notificarea validatorilor",
        "de_ce":
            "fiecare schemă e comisă SEPARAT; coloana se adaugă numai dacă lipsește (idempotent); o notă se rescrie numai cât timp "
            "descrierea ei mai poartă „decizia Costin” (a doua rulare n-o mai găsește) și se retrimite numai dacă ultimul ei element "
            "din coadă e respins (`coada_api.retrimite_nota`, același drum ca butonul). Notificarea e best-effort, după commit. Niciun "
            "efect extern (Retest 2, pct.2 și pct.4).",
    },
    "core/migrare_retest_0810.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "analiticul 4428.02 + liniile/soldurile TVA-ului stocului, schema cu schema <-> scoaterea 731–738 nefolosite <-> "
                  "notele de refacere a NIR-urilor vechi <-> intrarea lor in coada",
        "de_ce":
            "fiecare pas, pe fiecare schema, e comis SEPARAT si e idempotent: contul se insereaza cu ON CONFLICT DO NOTHING, liniile "
            "se muta numai cat mai sunt pe 4428 cu contrapartida 371, un cont 73x se scoate numai daca nu e folosit si nu e in planul "
            "legal, iar un NIR refacut e marcat in `inregistrari_ids` (a doua rulare il sare). Coada primeste notele prin "
            "`uc_coada.note_in_coada`, idempotenta pe nota. Niciun efect extern.",
    },
    "core/migrare_decizii_0810.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "DDL-ul public (valoarea `inexistent`, gardul `notificari_element_ck`, triggerul extins) <-> marcarea "
                  "notificarilor de actiune fara element <-> documentul (`doc`) in payload-ul elementelor vechi din coada",
        "de_ce":
            "doua tranzactii, fiecare comisa la capat; DDL idempotent (DROP/ADD CONSTRAINT, CREATE OR REPLACE FUNCTION, DROP/CREATE "
            "TRIGGER), marcarea atinge numai randurile nerezolvate, completarea `doc` numai elementele fara el — rularea a doua nu "
            "schimba nimic; niciun efect extern.",
    },
    "core/migrare_fisiere_private.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "DDL-ul public (`fisiere_private`, `raportari.tip` / `aplicatie`) + copierea capturilor vechi în depozitul privat, cu "
                  "rândurile lor, și scoaterea tabelei `raportari_atasamente` <-> ștergerea fișierelor vechi din directorul publicat <-> "
                  "verificarea structurii",
        "de_ce":
            "o singură tranzacție, comisă la capăt; capturile se COPIAZĂ (sursa rămâne) înainte de INSERT, iar o eroare scoate copiile "
            "făcute. Fișierele vechi se șterg numai DUPĂ commit (cădere între commit și ștergere = copii rămase în directorul vechi, "
            "rularea a doua nu le mai atinge fiindcă tabela veche nu mai există — se văd în ieșirea migrării). Un fișier negăsit "
            "oprește tot ÎNAINTE de orice scriere (C36, comanda Costin 15.10.2026).",
    },
    "core/migrare_decizii_0710.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "DDL-ul public (notificari.rezolvata + triggerul) <-> DDL-ul fiecarei scheme <-> stornarea documentelor deja "
                  "respinse, schema cu schema <-> partenerul in payload-ul elementelor din coada",
        "de_ce":
            "fiecare pas e comis SEPARAT si e idempotent (ADD COLUMN IF NOT EXISTS, CREATE INDEX IF NOT EXISTS, stornarea numai a "
            "miscarilor VII — `anuleaza_id` unic —, partenerul numai unde lipseste). O cadere intre pasi lasa o stare din care "
            "rularea a doua continua fara efect dublu; niciun efect extern (e-mail, ANAF, disc).",
    },
    "core/migrare_curs_precizie.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "descărcarea arhivelor anuale BNR (interogare, fără conexiune) <-> lărgirea coloanei `public.curs_bnr_zilnic.curs` și "
                  "refacerea valorilor rotunjite ale cache-ului (o tranzacție) <-> lărgirea coloanelor de curs ale fiecărei firme (câte o "
                  "tranzacție pe schemă)",
        "de_ce":
            "[lotul 11, C88, 22.10.2026] `_main` (core/migrare_curs_precizie.py:128): (1) citește anii din cache, (2) `arhive` descarcă "
            "arhivele BNR FĂRĂ conexiune (o eroare de rețea ridică înaintea oricărei scrieri), (3) o tranzacție ține ALTER-ul pe cache și "
            "`refa_cache`, comisă la capăt (:136) — `refa_cache` ridică `ValueError` înaintea oricărui UPDATE dacă o valoare nu e nici a "
            "arhivei, nici rotunjirea ei, deci tranzacția se anulează întreagă; (4) fiecare schemă de firmă e lărgită și comisă SEPARAT "
            "(:149). Nicio stare intermediară nu e evidență greșită: datele firmelor NU se rescriu (HG 1/2016 pct.35 alin.(2)), numai "
            "tipul coloanei; o cădere între (3) și (4) sau pe o firmă e ANUNȚATĂ (`ESEC <schema>` + `SystemExit(1)`), deci "
            "`migrari_registru` nu-i scrie rândul și restartul rămâne oprit (fail-closed), iar rularea a doua e idempotentă (o coloană "
            "deja fără scală și o valoare deja exactă nu se ating). Cele patru domenii pe `public.spv_token` din inventar sunt OMONIMIE: "
            "parametrul local `descarca` al lui `arhive` (= `curs_bnr._descarca`) e rezolvat de scaner pe `spv_conector.descarca`; "
            "migrarea nu atinge SPV. Singurul efect extern real e citirea arhivelor BNR — interogare.",
    },
    "core/facturi_recurente.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "emiterea facturilor scadente, firma cu firma <-> cache-ul de curs",
        "de_ce":
            "lucratorul deschide o tranzactie PER FIRMA si cheama aceeasi `emite_factura` atomica; "
            "o firma care esueaza nu atinge firmele de dinainte. Al doilea domeniu e cache-ul de "
            "curs. Nicio scriere nu depinde de alta peste granita de tranzactie.",
    },
    "POST /tenants/{tenant_id}/facturi-recurente/{sid}/emite": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR în cache (înaintea emiterii) <-> emiterea facturii lunii din ciorna șablonului, cu marcarea șablonului și "
                  "anunțul avertismentelor <-> refuzul consemnat pe șablon <-> trimiterea în SPV (după emitere) <-> validarea notelor interne",
        "de_ce":
            "[lotul 13, 680, 26.10.2026] „Emite factura lunii” (`facturi_recurente.emite_unul_uc` -> `emite_unul` -> `emite_scadente(doar=)`) "
            "e EXACT calea cronului (`core/facturi_recurente.py::__main__`, rândul de mai sus), pe un singur șablon: o citire scurtă "
            "(:472, fără scrieri), cursul BNR și întrebarea către model FĂRĂ conexiune (:484, cache-ul public, eșecul înghițit deliberat), "
            "apoi emiterea pe o conexiune nouă (:496) care recitește șablonul — factura, ultima emitere și anunțul avertismentelor se comit "
            "împreună (:530) sau deloc (rollback pe orice refuz); un refuz se consemnează pe șablon și se anunță (`_consemneaza_refuzul`, "
            "commit :447 — marcaj de stare refăcut la încercarea următoare, nu evidență contabilă). Trimiterea în SPV (alegerea șablonului) "
            "se face DUPĂ ce conexiunea emiterii s-a închis (:542, `_trimite_spv`): principalul pe o conexiune scurtă, apoi "
            "`efactura_trimitere.trimite` — " + TIPARUL_PREGATIT + "; orice nereușită se anunță în clopoțel, iar factura rămâne emisă "
            "(trimiterea se reia din Istoric facturi). Validarea notelor interne vine după commit (`_note_interne`), cu refuzul în răspuns.",
    },
    "POST /tenants/{tenant_id}/achizitie-ic": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al zilei exigibilității în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> "
                  "achiziția intracomunitară: factura primită, nota de taxare inversă, operațiunea D301",
        "de_ce":
            "[lotul 13, 537, 26.10.2026] `uc_tenants.achizitie_ic` (core/uc_tenants.py:4697): pe factura în valută, "
            "`_preincalzeste_cursul` (:4710) scrie NUMAI cache-ul public, pe conexiunile lui, cu eșecul înghițit deliberat; apoi ACTUL "
            "într-o singură tranzacție (:4711 -> commit :4812): `curs_bnr.curs_pentru` decide pe cache (`MonedaNecotata` -> refuz lângă "
            "câmp, `CursIndisponibil` -> 409, înaintea oricărei scrieri), apoi factura primită, nota 4426 = 4427 și operațiunea D301, "
            "legate. Orice refuz (lună închisă, câmpuri, cod de TVA, factura refuzată) anulează tot actul. Cache scris + act refuzat = "
            "numai cache mai bogat, care nu e stare a firmei. Același tipar ca `POST /tenants/{tenant_id}/decontare-valuta`.",
    },
    "POST /tenants/{tenant_id}/nota-decont-deplasare": {
        "clasa": NECRITIC,
        "efecte": "cursul BNR al decontului în valută în cache (public.alerte_cooldown + public.curs_bnr_zilnic, înaintea tranzacției) <-> "
                  "nota decontului (ciornă) cu rândurile 542 pe salariat <-> excedentul diurnei spre statul de plată",
        "de_ce":
            "[lotul 13, 670, 26.10.2026] `uc_tenants.nota_decont_deplasare` (core/uc_tenants.py:6747): la decontul deplasării externe în "
            "valută, `_preincalzeste_cursul` (:6761) scrie NUMAI cache-ul public, pe conexiunile lui, cu eșecul înghițit deliberat; apoi "
            "ACTUL într-o singură tranzacție (:6762 -> commit :6821): verificările (salariatul, cotele, soldul 542, plafonul diurnei), nota "
            "și rândurile ei, iar excedentul diurnei peste plafon (`diurna_salariat.adauga_excedent`, :6816) legat de notă (cheia străină, "
            "ON DELETE CASCADE). Un refuz anulează tot; cache scris + act refuzat = numai cache mai bogat, care nu e stare a firmei.",
    },
    "POST /tenants/{tenant_id}/nota-productie": {
        "clasa": FALS,
        "efecte": "-",
        "de_ce":
            "OARBIREA «ramuri exclusive aplatizate», declarata in antetul instrumentului. `uc_tenants.nota_productie` "
            "(core/uc_tenants.py:5962, lotul 13, 510) are trei ramuri pe `operatie`, fiecare cu commitul ei urmat de `return`: productia "
            "in curs (commit :6001), obtinerea (commit :6030) si vanzarea (commit :6061). Scanerul le pune in ordinea sursei si vede "
            "«commit, apoi scriere» (articolul creat de emiterea vanzarii dupa commitul obtinerii); cele trei nu se executa niciodata "
            "impreuna. Pe fiecare ramura toate scrierile — nota, intrarea in fisa de magazie legata de nota; factura, descarcarea "
            "gestiunii si nota diferentelor de pret — sunt intr-o singura tranzactie, a rutei (:5976); `rollback`-ul din emitere "
            "(`facturi_api`, cursul refuzat) anuleaza tot actul, iar un refuz al descarcarii il opreste inaintea commitului.",
    },
    "POST /admin/cabinete/{firm_id}/suspenda": {
        "clasa": NECRITIC,
        "efecte": "suspendarea cabinetului și rândul jurnalului (o tranzacție) <-> emailurile către administratorii cabinetului (după "
                  "commit) <-> câte emailuri au plecat, pe rândul jurnalului",
        "de_ce":
            "[lotul 13, 645, 26.10.2026] `uc_admin.admin_cabinet_suspenda` (core/uc_admin.py:166): flagul cabinetului și rândul "
            "jurnalului suspendărilor se scriu în ACEEAȘI tranzacție (:182), cu refuzul suspendării duble înaintea scrierii; emailurile "
            "pleacă DUPĂ commit (:197 — o suspendare anulată nu anunță nimic), fiecare prin `trimite_email_html_sau_semnaleaza` (eșecul "
            "se semnalează operatorului, nu tace); a treia tranzacție (:198) scrie numai numărul celor plecate pe rândul jurnalului. Un "
            "defect între ele lasă suspendarea scrisă și numărul gol — un contor informativ, nu evidență: suspendarea însăși e completă și "
            "vizibilă în fișa cabinetului, iar răspunsul spune câte emailuri au plecat din câți destinatari.",
    },
    "core/woocommerce.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "sincronizarea WooCommerce ca lucrator de fundal",
        "de_ce":
            "aceeasi cale ca ruta `/woocommerce/sincronizeaza`, pornita din cron: interogare la "
            "WooCommerce, apoi emiteri atomice, apoi cache-ul de curs in tranzactia lui.",
    },
    "core/spv_poll.py::__main__ -> ruleaza()": {
        "clasa": NECRITIC,
        "efecte": "interogarea starii mesajelor la ANAF <-> descarcarea recipiselor pe disc <-> "
                  "randurile de stare <-> rotatia tokenului",
        "de_ce":
            "`stareMesaj` si `descarcare` sunt INTEROGARI: nu schimba nimic la ANAF. Recipisa "
            "scrisa pe disc e o copie a unui raspuns pe care il putem cere din nou — o tranzactie "
            "intoarsa lasa cel mult un fisier orfan, nu evidenta gresita. Rotatia tokenului se "
            "comite imediat, prin reparatia de azi.",
    },
    "core/spv_receive.py::__main__ -> ruleaza()": {
        "clasa": NECRITIC,
        "efecte": "lista de mesaje + descarcarea ZIP-urilor <-> importul facturilor primite <-> "
                  "rotatia tokenului",
        "de_ce":
            "aceeasi justificare ca `spv_poll`: apelurile sunt interogari, fisierele sunt copii "
            "reproductibile, iar importul fiecarui mesaj e o tranzactie proprie cu poarta lui de "
            "idempotenta pe id-ul mesajului descarcat.",
    },
    "POST /tenants/{tenant_id}/spv/verifica-acum": {
        "clasa": NECRITIC,
        "efecte": "lista de mesaje + descarcarea ZIP-urilor <-> importul facturilor primite <-> randul citirii "
                  "(public.spv_cui_acoperit) <-> rotatia tokenului",
        "de_ce":
            "[lotul 6, 273, 16.10.2026] butonul „Verifică acum în SPV” cheama EXACT `spv_receive.citeste_firma`, calea "
            "lucratorului de fundal (`core/spv_receive.py::__main__`): aceeasi justificare — apelurile la ANAF sunt "
            "interogari, fisierele sunt copii reproductibile, importul fiecarui mesaj e tranzactia lui cu poarta de "
            "idempotenta pe id-ul mesajului, iar randul citirii (drept / eroare / ultima reusita) se scrie DUPA "
            "raspuns, intr-o tranzactie scurta separata, fara conexiune tinuta peste apelul de retea.",
    },
    "core/spv_refresh.py::__main__ -> ruleaza()": {
        "clasa": NECRITIC,
        "efecte": "reimprospatarea preventiva a tokenelor SPV",
        "de_ce":
            "lucratorul deschide o tranzactie PER TOKEN si cheama rotatia in ea; un esec pe un "
            "token nu atinge tokenele deja reinnoite. V. `core/spv_conector.reimprospateaza_token`, "
            "clasificata critica si probata separat.",
    },
    "core/monitor_fiscal.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "citirea paginilor ANAF (interogare) <-> alertele fiscale salvate <-> anunturile "
                  "programate catre cabinete",
        "de_ce":
            "cele doua commituri sunt DOUA ACTE INDEPENDENTE, nu unul rupt in doua: «salveaza "
            "alertele gasite» si «emite anunturile programate». Fiecare e atomic si idempotent — "
            "alertele pe `ON CONFLICT (sursa, titlu) DO NOTHING`, anunturile pe jurnalul "
            "`public.alerte_emise (alerta_id, prag)`. Al doilea nu depinde de primul; o rulare "
            "urmatoare il reia. Apelurile de retea sunt citiri de pagini publice.",
    },
    "core/monitor_fiscal.py::__main__ -> ruleaza()": {
        "clasa": NECRITIC,
        "efecte": "aceeasi cale, intrata direct in `ruleaza`",
        "de_ce":
            "aceeasi justificare ca `_main`: e a doua intrare a aceluiasi lucrator, iar salvarea "
            "alertelor e idempotenta pe `(sursa, titlu)`, deci o rulare intrerupta se reia fara "
            "sa dubleze nimic.",
    },
    "core/proba_restaurare_noapte.py::__main__ -> proba()": {
        "clasa": NECRITIC,
        "efecte": "baza de proba (CREATE / restaurare / DROP, alta baza decat productia) <-> amprenta productiei (citire "
                  "REPEATABLE READ, read-only) <-> bataia de heartbeat sau alerta de esec",
        "de_ce":
            "[15.10.2026, decizia Costin pct.4: proba de restaurare in fiecare noapte] Nicio scriere in baza productiei in afara "
            "bataii de heartbeat (`cron.bate`, tranzactia ei, dupa reusita). Tot restul se scrie in `iconta_proba_restaurare`, o "
            "baza SEPARATA, stearsa in `finally` si verificata absenta — inclusiv la esec; o rulare intrerupta lasa cel mult baza "
            "de proba, pe care rularea urmatoare o refuza vizibil (nu o suprascrie). Alerta pleaca numai la esec si NU are "
            "pereche in baza: o alerta trimisa fara bataie e exact semnalul cerut. Semnele C1–C6 vin din apelurile psql / "
            "pg_restore si din cele doua conexiuni (productie read-only, baza de proba).",
    },
    "core/firma_rezumat.py::__main__ -> main()": {
        "clasa": NECRITIC,
        "efecte": "recalcularea modelului de citire, lot cu lot <-> bataia de heartbeat",
        "de_ce":
            "modelul de citire e derivat prin constructie: o firma recalculata partial ramane "
            "`invalidat` si se reia. Comanda P4 spune explicit «nu atinge read-modelul»; nu s-a "
            "atins. Bataia de heartbeat e a treia tranzactie, si TREBUIE sa fie separata — altfel "
            "un lot picat ar sterge dovada ca lucratorul a rulat.",
    },
    "core/audit_schema.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "auditul de structura al schemelor, pe scheme",
        "de_ce":
            "instrument de audit: citeste structura si scrie un raport despre ea. Nu produce "
            "evidenta contabila, nu atinge date de firma, iar o rulare intrerupta se reia integral "
            "fara sa lase nimic pe jumatate.",
    },
    "POST /tenants": {
        "clasa": NECRITIC,
        "efecte": "crearea firmei <-> interogarea ANAF pentru precompletare",
        "de_ce":
            "`anaf_api.valideaza_cui` e o INTEROGARE: nu lasa nimic la ANAF, deci nu poate ramane "
            "fara perechea din baza. Scrierile — firma, legatura, profilul — sunt intr-o singura "
            "tranzactie. Ce ramane e durata ei peste un apel de retea.",
    },
    "POST /migrare/importa": {
        "clasa": NECRITIC,
        "efecte": "importul firmelor migrate <-> interogarea ANAF",
        "de_ce":
            "identic cu `POST /tenants`: apelul extern e o interogare de CUI, iar scrierile stau "
            "intr-o singura tranzactie. Nici efect ireversibil, nici evidenta despartita.",
    },
    "POST /gdpr/cerere-stergere": {
        "clasa": NECRITIC,
        "efecte": "cererea de stergere depusa <-> alerta interna",
        "de_ce":
            "efectul extern e o ALERTA catre noi, prin `observare`, nu un act asupra datelor "
            "cuiva. Cererea in sine e o singura scriere; stergerea propriu-zisa e alt act, al "
            "superadminului, si are ordinea ei corecta (commit inainte de `rmtree`).",
    },
    "POST /pachete/{tenant_id}/poveste": {
        "clasa": NECRITIC,
        "efecte": "generarea povestii pachetului <-> e-mailul care o duce",
        "de_ce":
            "e-mailul duce un artefact care se poate regenera oricand din aceleasi date — nu e un "
            "act asupra evidentei. O tranzactie intoarsa nu lasa evidenta gresita; cel mult un "
            "mesaj despre o poveste care se produce din nou identic.",
    },
    "POST /tenants/{tenant_id}/firma-profil/date": {
        "clasa": FALS,
        "efecte": "-",
        "de_ce":
            "OARBIREA «ramuri exclusive aplatizate», declarata in antetul instrumentului. "
            "`salveaza_date` comite si se intoarce pe o ramura, iar pe cealalta actualizeaza "
            "profilul firmei si abia apoi comite. Scanerul le pune in ordinea sursei si vede "
            "«commit, apoi scriere». Cele doua nu se executa niciodata impreuna. Toate scrierile "
            "reale — CUI, denumire, profil — sunt intr-o singura tranzactie, a rutei. "
            "(Nota de forma: textul asta NU numeste tabelul urmat de cuvinte, fiindca prima lui "
            "forma a aprins `test_schema_coloane` — scanerul de coloane a citit proza mea ca pe "
            "referinte SQL, si avea dreptate ca tipar.)",
    },
    # [lotul 10, deficiența 431] asociații și cotele în Date firmă (corectura și cesiunea) — aceeași formă, același verdict
    "POST /tenants/{tenant_id}/asociati": {
        "clasa": FALS,
        "efecte": "-",
        "de_ce":
            "OMONIMIE in domeniul #0 (in afara oricarei conexiuni): verificarea comuna a randurilor "
            "(`asociati_import_api.verifica_randuri`) cheama `respinge`, iar scanerul il reuneste cu "
            "omonimul din coada declaratiilor; verificarea doar construieste refuzuri, nu scrie. Apelul "
            "ANAF de acolo e o INTEROGARE de CUI, facuta inaintea conexiunii pe schema firmei. Toate "
            "scrierile reale — structura asociatilor si randul din jurnalul Date firma — sunt intr-o "
            "singura tranzactie, a use-case-ului (`uc_asociati._scrie`); un refuz o anuleaza intreaga.",
    },
    "POST /tenants/{tenant_id}/asociati/cesiune": {
        "clasa": FALS,
        "efecte": "-",
        "de_ce":
            "aceeasi forma ca POST /tenants/{tenant_id}/asociati: OMONIMIE in domeniul #0 (`respinge` "
            "din verificarea comuna reunit cu omonimul din coada declaratiilor), interogarea ANAF "
            "inaintea conexiunii; arhivarea structurii de dinainte, structura noua si jurnalul sunt "
            "intr-o singura tranzactie (`uc_asociati._scrie`), intreaga sau deloc.",
    },
    "POST /tenants/{tenant_id}/solduri": {
        "clasa": NECRITIC,
        "efecte": "crearea tabelului de solduri (DDL, `asigura_tabel` comite) <-> conturile lipsa "
                  "din planul de conturi <-> DELETE+INSERT-ul soldurilor",
        "de_ce":
            "commitul lui `asigura_tabel` e un `CREATE TABLE IF NOT EXISTS` — idempotent, fara "
            "continut, imposibil de citit gresit. Ce conteaza — conturile adaugate si inlocuirea "
            "soldurilor — ramane intr-o singura tranzactie, deschisa dupa el, iar refuzul balantei "
            "neechilibrate e INAINTEA oricarei scrieri (regula probata pe 15.07.2026).",
    },
    "POST /tenants/{tenant_id}/parteneri": {
        "clasa": NECRITIC,
        "efecte": "crearea tabelului de solduri pe parteneri (DDL) <-> DELETE+INSERT-ul soldurilor",
        "de_ce":
            "identic cu `/solduri`: commitul despartit e DDL idempotent, iar inlocuirea soldurilor "
            "e o singura tranzactie. Validarea randurilor — CUI valid, cont care tine parteneri — "
            "precede orice scriere, deci un refuz nu lasa nimic in urma.",
    },
}


# ============================================================================
#  COMPLETITUDINEA — FIECARE candidat brut primeste un verdict, nu doar cei
#  de peste un prag. (Cerut de Costin, runda de acceptare din 10.09.2026.)
#
#  Regula lui P4 e limpede: orice cale care aprinde CEL PUTIN UNUL din C1..C6 e
#  candidat. Nu exista prag suplimentar inaintea clasificarii, si nu se filtreaza
#  C1 fiindca produce multe rezultate. Prima forma a livrarii mele clasifica 32 de
#  cai dintr-un inventar de 332, cu un prag pe care il alesesem eu — adica exact
#  „am declarat un candidat neimportant INAINTE de clasificare".
#
#  CE SE SCHIMBA: verdictul se da pe DOUA cai, si amandoua sunt trasabile.
#    * INDIVIDUAL — calea are un rand scris in `CLASIFICARE`, cu motivul ei;
#    * PE CLASA STRUCTURALA — o regula din `REGULI`, care se aplica pe FAPTELE
#      derivate ale caii (cate domenii, cate scriu, cate scrieri, ce efecte), nu
#      pe numele ei. Fiecare regula spune ce clasa da si DE CE tine argumentul.
#
#  Ce NU face niciun mecanism de aici: nu absoarbe tacut o cale care cere judecata.
#  Caile cu scrieri in mai multe tranzactii, cu commit partial sau cu efect
#  ireversibil inauntrul unei tranzactii care scrie **nu au regula de clasa** —
#  ele cad la „neclasificat" pana cand primesc un rand individual. Asta e chiar
#  refuzul pe care `core/test_tranzactii_clasificate.py` il transforma in poarta.
# ============================================================================

INDIVIDUAL = "INDIVIDUAL"

#: NUMELE CHEII e `de_ce`, nu `motiv`, si nu din stil: `motiv` e in
#: `core/scan_afirmatii.REVENDICARE` — vocabularul sub care casa tine AFIRMATII DESPRE DATELE UNEI
#: FIRME, care trebuie sa fie obiecte cu `fel` (decizia din 21.08). Regulile de aici justifica o
#: clasificare de COD, nu afirma nimic despre o firma; dar un scaner nu poate face deosebirea, si pe
#: drept — daca ar putea, ar face-o pe text. `CLASIFICARE` folosea deja `de_ce`, deci motorul se
#: aliniaza la fisierul in care traieste in loc sa ceara o exceptie. *Cinci garzi au picat pe aceeasi
#: cauza; toate se sting prin aceeasi potrivire de nume.*


def _f(x):
    """Faptele derivate ale unui candidat (v. `scan_tranzactii.inventar`)."""
    return x.get("fapte", {}), x.get("analiza", {})


def _cere_individual(x):
    """True daca semnele caii cer o judecata scrisa, nu o regula de clasa."""
    _fa, an = _f(x)
    return bool(an.get("domenii_care_scriu", 0) > 1
                or an.get("partial_commit")
                or an.get("extern_in_tranzactie"))


#: ORDINEA CONTEAZA: prima regula care se potriveste da verdictul.
#:
#: Regulile STRUCTURALE stau inaintea celei de omonimie, si nu din intamplare. Rezolvarea pe
#: omonimie (treapta a treia: toate definitiile cu acelasi nume, reunite) **adauga** evenimente,
#: niciodata nu scoate. Deci o concluzie de forma «nicio scriere» sau «cel mult un domeniu scrie»,
#: trasa pe faptele supra-aproximate, ramane adevarata **a fortiori** despre calea reala: daca nici
#: cu evenimente in plus nu apare un al doilea scriitor, cu atat mai putin fara ele. Un verdict
#: structural e mai tare decat unul de provenienta — asa ca `OMONIM` ramane ultima plasa, pentru
#: caile despre care nu se poate spune nimic altfel.
REGULI = [
    {
        "cod": "FARA-SCRIERI",
        "titlu": "calea nu scrie nimic în bază",
        "clasa": NECRITIC,
        "cand": lambda x: _f(x)[0].get("scrieri_total", 0) == 0,
        "de_ce": lambda x: (
            "%d domenii tranzactionale, ZERO scrieri. C1 aprinde pe numarul de FRONTIERE, nu pe "
            "scrieri — de-aia calea e candidat, si pe drept. Dar o operatie care nu scrie nimic "
            "nu poate lasa stare partiala: nu exista jumatate de nimic. Ce ramane e durata "
            "tranzactiilor de citire, care e o intrebare de concurenta (R178/R183), nu de "
            "proprietate." % _f(x)[0].get("domenii_total", 0)),
    },
    {
        "cod": "UN-SINGUR-SCRIITOR",
        "titlu": "mai multe tranzacții, dar una singură scrie",
        "clasa": NECRITIC,
        "cand": lambda x: (_f(x)[0].get("domenii_care_scriu", 0) == 1
                           and _f(x)[0].get("domenii_total", 0) > 1),
        "de_ce": lambda x: (
            "%d domenii tranzactionale, dintre care UNUL SINGUR scrie (%d scrieri, %d tabele). "
            "Celelalte sunt citiri — tipic poarta de acces (`_schema_sau_404` isi deschide propria "
            "conexiune) si contextul cererii. **O tranzactie care nu scrie nu poate lasa stare "
            "partiala**, deci toate scrierile caii sunt atomice impreuna, in singura tranzactie "
            "care le tine. C2 si C6, cand se aprind aici, privesc ordinea din INTERIORUL ei — iar "
            "interiorul unei tranzactii e tot-sau-nimic prin constructie."
            % (_f(x)[0].get("domenii_total", 0), _f(x)[0].get("scrieri_total", 0),
               len(_f(x)[0].get("tabele", [])))),
    },
    {
        "cod": "O-SINGURA-TRANZACTIE",
        "titlu": "tot actul într-o singură tranzacție",
        "clasa": NECRITIC,
        "cand": lambda x: (_f(x)[0].get("domenii_total", 0) <= 1
                           and _f(x)[0].get("domenii_care_scriu", 0) <= 1),
        "de_ce": lambda x: (
            "un singur domeniu tranzactional, %d scrieri in %d tabele. Calea e candidat fiindca "
            "aprinde C2 (mai multe tabele) sau C6 (ordinea scrierilor), dar amandoua descriu ce se "
            "intampla INAUNTRUL unei singure tranzactii — care se comite intreaga sau deloc. "
            "Nu exista frontiera intre efecte, deci nu exista loc unde un defect sa lase jumatate."
            % (_f(x)[0].get("scrieri_total", 0), len(_f(x)[0].get("tabele", [])))),
    },
    {
        "cod": "OMONIM",
        "titlu": "ULTIMA PLASĂ: toate evenimentele vin din nume cu mai multe definiții",
        "clasa": FALS,
        "cand": lambda x: bool(x.get("numai_omonim")),
        "de_ce": lambda x: (
            "FALS POZITIV prin OMONIMIE, oarbirea declarata in antetul instrumentului: toate "
            "evenimentele caii vin din nume rezolvate pe treapta a treia (toate definitiile cu "
            "acel nume, reunite), deci faptele pe care s-ar sprijini orice alta regula nu sunt "
            "ale caii asteia. Instanta din casa: parametrul `trimite` al lui `alerta_acces.ruleaza` "
            "se ciocneste cu `efactura_trimitere.trimite` si surorile lui"),
    },
]


def verdict(x, clasificare=None, reguli=None):
    """`{clasa, regula, motiv}` pentru un candidat, sau `None` daca nu-l acopera nimic.

    Ordinea: intai randul INDIVIDUAL (daca exista), apoi regulile pe clasa structurala, in
    ordinea din `REGULI`. Caile care cer judecata scrisa — scrieri in mai multe tranzactii,
    commit partial, efect ireversibil in tranzactie — **nu au regula de clasa**: pentru ele
    `None` e raspunsul corect, iar gardul il transforma in refuz.
    """
    clasificare = CLASIFICARE if clasificare is None else clasificare
    reguli = REGULI if reguli is None else reguli
    rand = clasificare.get(x.get("intrare"))
    if rand:
        return {"clasa": rand["clasa"], "regula": INDIVIDUAL, "de_ce": rand["de_ce"]}
    if _cere_individual(x):
        return None          # cere un rand scris; nicio regula de clasa nu-l acopera
    for r in reguli:
        try:
            if r["cand"](x):
                return {"clasa": r["clasa"], "regula": r["cod"], "de_ce": r["de_ce"](x)}
        except Exception:
            continue
    return None


def clasifica(inv, clasificare=None, reguli=None):
    """`(verdicte, neclasificate)` peste TOT inventarul brut.

    `verdicte` e `[(intrare, verdict)]`, unde verdictul poarta `clasa`, `regula` si `de_ce`, in ordinea inventarului; `neclasificate` e lista
    intrarilor pentru care nimic n-a dat un verdict. **A doua lista trebuie sa fie goala** —
    asta e `UNCLASSIFIED_RAW_CANDIDATES = 0`.
    """
    verdicte, neclasificate = [], []
    for x in inv:
        v = verdict(x, clasificare, reguli)
        if v is None:
            neclasificate.append(x.get("intrare"))
        else:
            verdicte.append((x.get("intrare"), v))
    return verdicte, neclasificate


def cai_interne():
    """Caile critice care NU sunt puncte de intrare — deci nu apar in inventarul brut."""
    return [k for k, v in CLASIFICARE.items()
            if v["clasa"] == CRITIC and v.get("cale_interna")]


def excluderi_toate(inv, clasificare=None, reguli=None):
    """`{intrare: de_ce}` pentru FIECARE candidat exclus din critic — nu doar cele individuale.

    Prima forma a lui `UNEXPLAINED_EXCLUSIONS` masura numai randurile scrise de mana, adica **35**
    din **331** de excluderi. Un zero pe o populatie mai mica decat cea despre care pare ca
    vorbeste e chiar clasa de cifra pe care casa o urmareste: adevarata, si inselatoare.
    Acum se deriva peste toti candidatii clasificati NON_CRITICAL sau FALSE_POSITIVE, oricum ar fi
    primit verdictul — individual sau prin regula."""
    out = {}
    for x in inv:
        v = verdict(x, clasificare, reguli)
        if v is not None and v["clasa"] != CRITIC:
            out[x.get("intrare")] = v.get("de_ce")
    return out


def acoperire_injectie():
    """`(cerute, acoperite, netestate)` pe universul CORECT: TOATE operatiile critice.

    Include calea interna. *Nu se pierde din acoperire ca sa iasa contabilitatea inventarului.*"""
    import ast as _ast
    fis = os.path.join(_RAD_MODUL, "core", "test_p4_fault_injection.py")
    functii = set()
    if os.path.exists(fis):
        functii = {n.name for n in _ast.walk(_ast.parse(io.open(fis, encoding="utf-8").read()))
                   if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))}
    cerute = probe_cerute()
    netestate = sorted(c for c, proba in cerute.items() if proba not in functii)
    return len(cerute), len(cerute) - len(netestate), netestate


def numaratori(inv, clasificare=None, reguli=None):
    """Blocul de cifre al acceptarii, derivat — pe DOUA universuri, numite separat.

    * `RAW_*` — peste inventarul brut. `RAW_CRITICAL + RAW_NON_CRITICAL + RAW_FALSE_POSITIVES`
      **trebuie** sa dea `CLASSIFIED_CANDIDATES`, care trebuie sa dea `RAW_CANDIDATES`;
    * `INTERNAL_CRITICAL_COMPOSITES` / `TOTAL_CRITICAL_OPERATIONS` — peste operatiile critice,
      unde intra si caile interne, care nu sunt puncte de intrare.

    Cele doua nu se aduna intre ele, si de-aia nu mai poarta acelasi nume.
    """
    verdicte, neclasificate = clasifica(inv, clasificare, reguli)
    pe_clasa, pe_regula = {}, {}
    for _intrare, v in verdicte:
        pe_clasa[v["clasa"]] = pe_clasa.get(v["clasa"], 0) + 1
        pe_regula[v["regula"]] = pe_regula.get(v["regula"], 0) + 1

    raw_critic = pe_clasa.get(CRITIC, 0)
    raw_necritic = pe_clasa.get(NECRITIC, 0)
    raw_fals = pe_clasa.get(FALS, 0)
    suma = raw_critic + raw_necritic + raw_fals
    interne = len(cai_interne())
    cerute, acoperite, netestate = acoperire_injectie()
    excl = excluderi_toate(inv, clasificare, reguli)
    nemotivate = sorted(k for k, m in excl.items()
                        if not isinstance(m, str) or len(m.strip()) < 80)

    return {
        # ── universul 1: INVENTARUL BRUT ──────────────────────────────────────
        "RAW_CANDIDATES": len(inv),
        "CLASSIFIED_CANDIDATES": len(verdicte),
        "UNCLASSIFIED_RAW_CANDIDATES": len(neclasificate),
        "neclasificate": neclasificate,
        "RAW_CRITICAL_COMPOSITES": raw_critic,
        "RAW_NON_CRITICAL_COMPOSITES": raw_necritic,
        "RAW_FALSE_POSITIVES": raw_fals,
        "RAW_CLASS_SUM": suma,
        "RAW_CLASS_ACCOUNTING": ("PASS" if (suma == len(verdicte) == len(inv)
                                            and not neclasificate) else "FAIL"),
        # ── universul 2: OPERATIILE CRITICE ───────────────────────────────────
        "INTERNAL_CRITICAL_COMPOSITES": interne,
        "TOTAL_CRITICAL_OPERATIONS": raw_critic + interne,
        "CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS": cerute,
        "CRITICAL_OPERATIONS_WITH_FAULT_TESTS": acoperite,
        "UNTESTED_CRITICAL_OPERATIONS": len(netestate),
        "netestate": netestate,
        # ── excluderile, peste TOTI candidatii exclusi ────────────────────────
        "EXCLUSIONS_TOTAL": len(excl),
        "UNEXPLAINED_EXCLUSIONS": len(nemotivate),
        "nemotivate": nemotivate,
        "pe_regula": pe_regula,
    }

def cai_critice():
    """Căile clasificate `CRITICAL_COMPOSITE`, în ordinea din fișier."""
    return [k for k, v in CLASIFICARE.items() if v["clasa"] == CRITIC]


def probe_cerute():
    """`{cale: nume_probă}` — ce probă de injecție trebuie să existe pentru fiecare cale critică."""
    return {k: v["proba"] for k, v in CLASIFICARE.items() if v["clasa"] == CRITIC}


def excluderi():
    """Căile EXCLUSE din critic, cu motivul. Comanda P4: nicio excludere fără justificare scrisă."""
    return {k: v["de_ce"] for k, v in CLASIFICARE.items() if v["clasa"] != CRITIC}


# ============================================================================
#  EFECTELE PE CARE `ROLLBACK` NU LE DESFACE — analiza separata ceruta de P4
#
#  Un `ROLLBACK` PostgreSQL desface scrieri in baza. Nu desface un e-mail plecat,
#  un fisier sters, un document incarcat la ANAF, un token rotit. Tabelul de mai
#  jos judeca FIECARE loc din productie in care un asemenea apel se face cat timp
#  exista scrieri necomise in aceeasi tranzactie — lista lui e derivata mecanic de
#  `scripts/scan_tranzactii.analiza()["extern_in_tranzactie"]`, nu scrisa din
#  memorie, iar `core/test_tranzactii_clasificate.py` cere ca fiecare loc gasit sa
#  aiba un rand aici. CHEIA e `fisier:functie`, nu `fisier:linie`: prima forma s-a
#  invalidat singura la prima editare a lui `spv_conector.py`, si un registru care se
#  invalideaza la orice linie adaugata invata pe cineva sa nu-l mai citeasca.
#
#  Doua feluri, si deosebirea e chiar miezul:
#    INTEROGARE — apelul nu lasa nimic la celalalt capat (validare CUI, XML-ul BNR,
#                 o pagina publica, o lista de mesaje). Un rollback la noi n-are ce
#                 desface acolo. Ce ramane e DURATA tranzactiei, care e o intrebare
#                 de concurenta (P3 / R178), nu de proprietate.
#    EFECT      — apelul schimba o stare care nu e a noastra. Pentru fiecare,
#                 ordinea corecta e ca efectul sa vina ULTIMUL, dupa ce tranzactia
#                 a reusit sigur; iar cand efectul e chiar SURSA valorii de scris
#                 (rotatia unui token), scrierea lui se comite PRIMA, separat.
# ============================================================================

INTEROGARE = "INTEROGARE"
EFECT = "EFECT"

EFECTE_EXTERNE = {
    "core/ai_client.py:genereaza_text": {
        "fel": INTEROGARE,
        "ce_e": "cererea către modelul AI (Anthropic): text propus (cota TVA a unui produs, povestea lunii, tiparele)",
        "verdict": "nu lasă nimic la celălalt capăt: e o întrebare, nu un act; un rollback la noi n-are ce desface acolo. Ce rămâne e "
                   "DURATA — conexiunea ținută peste apelul de rețea pe zece căi (clasa C5 din registrul P5, văzută abia după ce "
                   "scanerele au învățat clientul SDK-ului, 09.10.2026); e datorie scrisă în GARZI, nu proprietate a tranzacției.",
        "reparat": "[R193, comanda Costin 10.10.2026 pct.2: „cele 10 căi care cer un răspuns AI ținând o conexiune la bază se mută înaintea conexiunii”] Întrebarea nu se mai pune cu scrieri necomise: emiterea (ecran, API, proforma, vânzarea IC, magazinul, "
                   "facturile recurente) primește răspunsurile cerute după o citire scurtă și înaintea tranzacției "
                   "(`uc_comun._intreaba_modelul`, `cote_tva.intreaba`); vânzarea IC nu mai întreabă deloc — contul de venit al liniei e cel "
                   "ales de contabil.",
    },
    "core/ai_client.py:_raspuns_simulat": {
        "fel": EFECT,
        "ce_e": "AI-ul simulat al plasei: jurnalul prompturilor și coada răspunsurilor pregătite (comanda Costin 09.10.2026, pct.7)",
        "verdict": "scrie numai în directorul plasei (`ICONTA_AI_SIMULAT`), pe care `_director_simulat` îl refuză pe orice mediu care nu e "
                   "de test (`mediu_test.motive`); pe producție ramura nu există. Un rollback nu desface rândul de jurnal, dar jurnalul "
                   "e proba plasei (ce prompt a plecat), nu un fapt al firmei — iar un prompt scris pentru o cerere anulată e exact ce "
                   "trebuie văzut.",
        "reparat": "[R193, comanda Costin 10.10.2026 pct.2: „cele 10 căi care cer un răspuns AI ținând o conexiune la bază se mută înaintea conexiunii”] AI-ul simulat scrie acolo unde e chemat modelul, iar modelul nu mai e chemat din nicio tranzacție cu "
                   "scrieri (vezi `genereaza_text`): jurnalul plasei se scrie acum cu pool-ul liber, în afara oricărui domeniu.",
    },
    "core/migrari_registru.py:_git": {
        "fel": INTEROGARE,
        "ce_e": "citirea arborelui git (migrările și șablonul din commit)",
        "verdict": "interogare locală, fără efect: citește arborele unui commit (`git ls-tree`, `git show`) ca să afle ce migrări și "
                   "ce șablon poartă HEAD; un rollback n-are ce desface, iar baza nu e atinsă.",
    },
    "core/migrare_fisiere_private.py:muta_atasamentele": {
        "fel": EFECT,
        "ce_e": "copierea capturilor vechi (`<static>/raportari`) în depozitul privat (`core/fisiere_private.py`), la migrarea C36",
        "verdict":
            "copia se face înaintea rândului ei din `fisiere_private`, în tranzacția migrării; dacă INSERT-ul sau scoaterea tabelei "
            "vechi cad, copiile făcute se șterg în `except` înainte de a ridica, deci un rollback nu lasă fișiere fără rând. Sursa nu "
            "se atinge în tranzacție — se șterge din directorul publicat numai după commit, în `_main`.",
    },
    "core/migrari_registru.py:_reporneste_daca_e_cazul": {
        "fel": EFECT,
        "ce_e": "repornirea serviciului `iconta-nou` după ultima migrare lipsă (gardul „migrarea înainte de restart”)",
        "verdict":
            "se face DUPĂ commitul rândului din registru și numai dacă `verifica` întoarce 0 pe HEAD; o repornire eșuată lasă "
            "sentinela și tipărește comanda — starea bazei e deja completă, deci nu e nimic de desfăcut. Nu e un efect înăuntrul "
            "tranzacției care scrie registrul (`_cu_registrul` a comis înainte).",
    },
    "core/anaf_api.py:valideaza_cui": {
        "fel": INTEROGARE,
        "ce_e": "validarea unui CUI la serviciul public al ANAF",
        "verdict":
            "nu lasa nimic la ANAF: e o intrebare, nu un act. Un rollback la noi nu are ce "
            "desface acolo. Ce ramane e ca tranzactia sta deschisa peste un apel de retea — "
            "durata, nu proprietate; e numita la restante, ca intrebare de concurenta.",
        "reparat":
            "[P5 val 3, 11.09.2026] Chiar lucrul pe care verdictul il numea ca ramas — «tranzactia "
            "sta deschisa peste un apel de retea» — s-a inchis. Cele cinci cai care ajungeau aici "
            "au fost despartite: `precompleteaza_din_anaf` se imparte in `date_din_anaf` (apelul, "
            "fara conexiune) si scrierea, iar `platitor_tva_freeze` se cheama inaintea blocului, pe "
            "CUI-ul din payload. Caracterul de INTEROGARE ramane neschimbat, deci restul "
            "verdictului sta in picioare; ce s-a mutat e durata, nu proprietatea.",
    },
    "core/curs_bnr.py:_descarca": {
        "fel": INTEROGARE,
        "ce_e": "descarcarea XML-ului de cursuri de la BNR",
        "verdict":
            "interogare. Efectul persistent care decurge din ea — cache-ul de cursuri — nu mai "
            "traieste in tranzactia apelantului din 04.09.2026: `_salveaza_cache` isi deschide "
            "conexiunea lui, cu motivul scris langa cod. Cache-ul TREBUIE sa supravietuiasca "
            "esecului actului care l-a declansat, altfel fiecare incercare re-descarca de la BNR.",
        "reparat": "[R193, comanda Costin 10.10.2026 pct.2: „cele 10 căi care cer un răspuns AI ținând o conexiune la bază se mută înaintea conexiunii”] Locul ramas era cronul facturilor recurente: `emite_scadente` primea conexiunea apelantului si aducea cursul "
                   "cu ea in mana, dupa scrierile abonamentului anterior. Acum isi ia singur conexiunile, pe faze (citire scurta -> curs si "
                   "model fara conexiune -> emitere care reciteste abonamentele).",
    },
    "core/monitor_fiscal.py:ruleaza": {
        "fel": INTEROGARE,
        "ce_e": "citirea paginii de noutati legislative a ANAF",
        "verdict":
            "interogare pe o pagina publica. Alertele derivate din ea se scriu idempotent, pe "
            "`ON CONFLICT (sursa, titlu) DO NOTHING`, deci o rulare intrerupta se reia fara sa "
            "dubleze nimic.",
        "reparat":
            "[P5 val 3, 11.09.2026] Jobul nu mai tine o conexiune peste cele doua descarcari de "
            "cate 30 s: lista si PDF-ul se aduc fara nicio conexiune, iar `_procesat` si `salveaza` "
            "isi iau fiecare tranzactia lor scurta. Idempotenta descrisa mai sus e NEATINSA — "
            "`_procesat` a ramas verificarea de dinainte, iar buletinul se marcheaza chiar si fara "
            "alerte, ca pana acum.",
    },
    "core/woocommerce.py:comenzi": {
        "fel": INTEROGARE,
        "ce_e": "citirea comenzilor din magazinul WooCommerce al firmei",
        "verdict":
            "interogare. Facturile emise din comenzi sunt fiecare o tranzactie atomica, iar "
            "duplicarea e aparata de cheia comenzii, nu de soarta tranzactiei.",
        "reparat":
            "[P5 val 3, 11.09.2026] Citirea magazinului (termen 30 s) nu mai sta sub conexiunea "
            "firmei: `sincronizeaza` face config (faza 1) -> HTTP fara conexiune -> tranzactie "
            "scurta cu revalidarea configului (faza 2). Apararea impotriva duplicarii pe care o "
            "numeste verdictul — `deja_importata`, cheia comenzii — a ramas EXACT unde era, in "
            "bucla de emitere, si e chiar revalidarea per comanda ceruta de regula valului 3.",
    },
    "core/observare.py:_trimite_brevo": {
        "fel": EFECT,
        "ce_e": "alerta interna prin Brevo (`_trimite_brevo`)",
        "verdict":
            "e un efect, dar unul care VORBESTE DESPRE un esec, nu unul care consemneaza un act. "
            "Daca tranzactia se intoarce dupa alerta, ce ramane e o alerta despre ceva ce nu s-a "
            "scris — adica exact ce trebuie sa afle cineva. Ordinea inversa ar fi gresita: o "
            "alerta amanata pana dupa commit s-ar pierde chiar cand actul cade.",
        "reparat":
            "[P5 val 3, 10.09.2026] LOCUL A DISPARUT din inventarul derivat, iar verdictul de mai "
            "sus ramane scris — inclusiv partea care spune ca ordinea inversa ar fi GRESITA. Nu s-a "
            "amanat nimic dupa commit: alerta pleaca pe un FIR PROPRIU, prin "
            "`observare.alerteaza_in_fundal`, chemata din `esec_secundar`. Deci se trimite la fel "
            "de devreme ca inainte — chiar si cand tranzactia se intoarce dupa —, dar nu mai tine o "
            "conexiune din pool cele pana la 10 secunde ale apelului la Brevo. Firul NU e daemon: "
            "interpretorul il asteapta la oprire, ca o alerta ridicata inainte de restart sa nu se "
            "piarda. A doua cale, e-mailul cererii GDPR, s-a mutat DUPA commit si dupa iesirea din "
            "bloc — acolo ordinea P4 se aplica, fiindca ala consemneaza un act, nu vorbeste despre "
            "un esec. *Aceeasi familie, doua reparatii diferite, fiindcă verdictul de mai sus "
            "deosebeste corect cele doua feluri de e-mail.*",
    },
    "core/observare.py:trimite_email_html": {
        "fel": EFECT,
        "ce_e": "e-mail catre un om (`trimite_email_html`)",
        "verdict":
            "efect ireversibil, si a fost sursa a doua reparatii de azi (notificarea de scadenta "
            "si alerta de acces). Locurile ramase — povestea unui pachet, invitatia in portal, "
            "linkul de resetare — trimit fie un artefact REGENERABIL, fie un link a carui cheie e "
            "deja comisa inaintea plecarii mesajului. Regula scrisa pentru orice apelant nou: "
            "randul care face mesajul inutil de retrimis se comite INAINTEA lui.",
        "reparat":
            "[P5 val 3, 11.09.2026] LOCUL A DISPARUT din inventarul derivat: niciunul dintre cele "
            "17 locuri de apel nu se mai executa sub o conexiune din pool (masurat cu "
            "`scripts/inventar_email_html.py`, 3 -> 0). Verdictul de mai sus ramane scris integral, "
            "inclusiv regula pe care o enunta — iar una dintre cele trei cai o INCALCA, si asta a "
            "iesit la iveala abia acum: la `pachet_poveste_set`, `return r` statea IN blocul de "
            "conexiune, deci `db.get_conn` comitea abia la iesire, iar e-mailul despre raportul "
            "lunar pleca INAINTE. Un commit cazut lasa clientul cu un anunt despre un raport care "
            "nu exista. Contract aprobat de arhitect pe 11.09: commit reusit -> se trimite; commit "
            "cazut -> NU se trimite nimic. Celelalte doua cai (`magic_link_cere`, "
            "`cabinet_solicitari_raspunde`) aveau deja `commit()` inainte, deci acolo mutarea in "
            "afara blocului e strict eliberarea conexiunii, fara nicio schimbare de semantica. "
            "Pazit de `core/test_email_html_dupa_commit.py`, clichet 0 pe AST plus probe "
            "functionale pe fiecare cale de esec.",
    },
    "core/spv_conector.py:_post_token": {
        "fel": EFECT,
        "ce_e": "POST /token la ANAF — ROTATIA perechii de tokene",
        "verdict":
            "cel mai ireversibil efect din casa: in secunda raspunsului, vechiul `refresh_token` "
            "e mort la ANAF. REPARAT azi — `_roteste_si_comite()` COMITE perechea noua imediat, pe "
            "conexiunea pe care use-case-ul (`apel_anaf`) o detine, inainte ca apelul care a "
            "cerut-o sa poata esua. Prima forma a reparatiei deschidea o A DOUA conexiune si se "
            "BLOCA pe randul tinut de tranzactia apelantului; poarta a prins-o. V. randul critic "
            "`core/spv_conector.reimprospateaza_token`.",
        "reparat":
            "[P5 val 3, 11.09.2026] PROPRIETATEA TRANZACTIEI S-A MUTAT, prin decizia arhitectului. "
            "REGULA VECHE: commitul apartinea USE-CASE-ULUI — `apel_anaf` deschidea conexiunea, "
            "deci el hotara cand se comite. Consecinta nevazuta pana acum: apelul `/token`, cu "
            "termen de 30 s (cel mai lung din val), se executa cu o conexiune din pool in mana, pe "
            "toate cele sapte cai masurate. REGULA NOUA: rotatia detine tranzactia SCURTA de "
            "persist+commit, de dupa HTTP. Vechea regula e SUPERSEDED DOAR pentru rotatia de token; "
            "niciun alt contract P4 nu se redeschide. GARANTIA DE ATOMICITATE SE PASTREAZA: "
            "perechea noua e comisa inainte ca apelantul sa poata continua sau sa poata esua — "
            "probat pe calea reala in `test_C_tokenul_rotit_ramane_comis_cand_apelantul_cade_dupa`. "
            "REGRESIA CELOR DOUA CONEXIUNI e imposibila prin constructie, fiindca fiecare bloc se "
            "inchide inainte ca urmatorul sa se deschida — probat structural in "
            "`test_F_rotatia_nu_deschide_o_conexiune_peste_alta`. `_roteste_si_comite` a disparut: "
            "nu mai avea ce face, iar un invelis care nu mai inveleste nimic e cod mort.",
    },
    "core/spv_conector.py:apel_anaf": {
        "fel": EFECT,
        "ce_e": "apelul autentificat catre ANAF din `apel_anaf` — acelasi loc, doua feluri",
        "verdict":
            "AMESTECAT, si se spune: `stareMesaj`, `descarcare` si `listaMesaje` sunt INTEROGARI; "
            "`upload` (e-Factura, e-Transport) e un EFECT — documentul pleaca la autoritate si nu "
            "se mai poate lua inapoi. Pentru upload, ordinea e deja corecta si e modelul casei: "
            "`efactura_trimitere.trimite` si `etransport_send.trimite` scriu si COMIT randul `pregatit` "
            "inaintea incarcarii, cu poarta de idempotenta inaintea lui, si abia apoi incarca. "
            "Ce ramane deschis: tranzactia lui `apel_anaf` sta deschisa peste apel si peste "
            "backoff-ul de 429 — durata, nu proprietate; numita la restante.",
        "reparat":
            "[P5 val 3, 10.09.2026] INCHIS — chiar randul de mai sus, «ce ramane deschis», adica "
            "restanta R183. `apel_anaf` nu mai tine conexiunea peste apel: tokenul se citeste si se "
            "roteste intr-un bloc care SE INCHIDE, iar apelul HTTP, retry-ul de 401 si backoff-ul "
            "de la 429 se petrec fara nicio conexiune in mana. Deci nu mai exista scrieri necomise "
            "in timpul efectului extern, si locul a iesit din inventarul derivat. Verdictul de mai "
            "sus RAMANE scris: judecata despre ce e interogare si ce e efect nu s-a schimbat, si "
            "ordinea corecta a incarcarilor (randul `pregatit` comis inainte) e in continuare "
            "modelul casei. *Un verdict sters ar arata identic cu un defect care n-a existat "
            "niciodata.* Reparatia P4 (`_roteste_si_comite`) ramane si ramane necesara — rotatia "
            "tot se comite imediat, acum intr-o conexiune scurta luata anume pentru ea.",
    },
}


def efecte_ireversibile():
    """Locurile judecate ca EFECT — cele pe care un `rollback` nu le desface."""
    return {k: v for k, v in EFECTE_EXTERNE.items() if v["fel"] == EFECT}

