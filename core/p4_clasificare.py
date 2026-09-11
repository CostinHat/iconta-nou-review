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
    "tiparul din `efactura_send.trimite` si `etransport_send.trimite`: randul care consemneaza "
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
            "tranzactie cu contul. Al treilea domeniu — provizionarea firmei — ramane despartit "
            "DELIBERAT si declarat in cod din 27.07.2026: contul e valid si util fara firma, iar "
            "raspunsul poarta adevarul (`firma_ok`, `firma_motiv`), deci esecul e anuntat.",
        "proba": "test_register_contul_nu_ramane_fara_dovada_acordului",
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
            "(parametrul `trimite` se ciocneste cu `efactura_send.trimite` si surorile lui); real e "
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

    "POST /coada": {
        "clasa": NECRITIC,
        "efecte": "elementul intra in coada <-> verdictul validatorului <-> notificarea validatorilor",
        "de_ce":
            "degradare DECLARATA, nu tacere. Verdictul si notificarea stau fiecare in tranzactia lui, "
            "prinse de `try/except` care LOGHEAZA. Un element fara verdict nu e o stare ascunsa: "
            "`coada_api.aproba` are cod propriu pentru ea (`FARA_VERDICT`) si refuza aprobarea, cu "
            "mesaj. Deci esecul e anuntat exact acolo unde conteaza — la actul urmator.",
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
    "POST /tenants/{tenant_id}/rip-import/incarca": {
        "clasa": NECRITIC,
        "efecte": "importul registrului de incasari-plati (atomic, in `rip_migrare_api.importa`) "
                  "<-> marcajul de progres al migrarii",
        "de_ce":
            "faptul contabil — operatiunile importate — e atomic prin constructie si refuza la "
            "prima eroare. A doua tranzactie e marcajul de progres, aceeasi clasa ca la `/vector`. "
            "Reimportul e aparat de numaratoarea `sarite_duplicat`. Commitul partial semnalat de "
            "instrument e cele DOUA apeluri ale lui `seteaza_status` din ramurile exclusive ale "
            "unui `if`, aplatizate de scaner: nu se executa niciodata amandoua.",
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
            "aceeasi justificare ca e-Transport: `efactura_send.trimite` scrie si comite randul "
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
    "core/facturi_recurente.py::__main__ -> _main()": {
        "clasa": NECRITIC,
        "efecte": "emiterea facturilor scadente, firma cu firma <-> cache-ul de curs",
        "de_ce":
            "lucratorul deschide o tranzactie PER FIRMA si cheama aceeasi `emite_factura` atomica; "
            "o firma care esueaza nu atinge firmele de dinainte. Al doilea domeniu e cache-ul de "
            "curs. Nicio scriere nu depinde de alta peste granita de tranzactie.",
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
            "se ciocneste cu `efactura_send.trimite` si surorile lui"),
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
            "`efactura_send.trimite` si `etransport_send.trimite` scriu si COMIT randul `pregatit` "
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

