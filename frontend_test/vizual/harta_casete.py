# -*- coding: utf-8 -*-
"""HARTA CASETELOR — așteptarea scrisă a unui ecran, ÎNAINTE de a-l privi.

DE CE EXISTĂ. Verificarea vizuală de până acum era observație fără așteptare: mă uitam și căutam ce
arată ciudat. Asta găsește anomalii de aspect, dar nu poate găsi nici absența, nici incoerența, nici
o cifră greșită bine formatată. Harta e cealaltă jumătate: ce ar trebui să fie în fiecare casetă,
scris separat de observație, ca să existe cu ce compara.

DE UNDE VINE CONȚINUTUL. Nu din privit, și nu din domeniu — din **codul de randare**. Cine a scris
ecranul a decis deja ce casete există și ce se leagă în fiecare; harta e o consultare, nu o
interpretare. Excepția e `TEMEI` și `CONSTRANGERI` de mai jos, care NU se pot citi din cod.

DE CE AICI ȘI NU LÂNGĂ RENDERER. `VC_RANDATE` din `control_verdict.js` stă în JS tocmai ca să fie sub
ochii cui schimbă ecranul, și e pățit — s-a născut din incidentul de pe 24.07 (trei renderere
divergente ascundeau constatări blocante). Am ținut harta asta separat, în Python, din trei motive:
comparatorul e în Python și citește nativ; conține temeiuri, care trăiesc în registrul de cote, nu în
JS; și proprietatea anti-derivă nu vine din vecinătate, ci din gardă. `VC_RANDATE` rămâne neatins —
păzește altceva, mai îngust, și funcționează.

STARE: DRAFT. `STRUCTURA` e citită din cod și o susțin. `TEMEI` și `CONSTRANGERI` sunt PROPUNERI —
nu le pot închide singur fără să fiu și observator, și comparator (vezi DECIZII 20.08, calea a doua).
"""

# ─────────────────────────────────────────────────────────────────────────────
# ANATOMII DE RÂND — ce câmpuri poartă un rând, per fel de rând.
# Sursa: funcțiile randDecl / randMotiv / randA / randConst / randVerif din control_verdict.js.
# Câmpul marcat cu "?" e opțional (randat doar dacă e prezent).
# ─────────────────────────────────────────────────────────────────────────────
# [R1'+R2, 20.08.2026] Un rând poartă CHEIA DE IDENTIFICARE a entității pe care o randează.
# Identitatea nu e o alegere de design: `public.declaratii_depuse` o definește deja prin cheia primară
# (tenant_id, an, luna, tip, nr_depunere). `campuri_ceruti` = ce TREBUIE să poarte; `campuri` = ce
# poartă AZI. Diferența dintre ele e datoria, vizibilă, nu ascunsă.
ANATOMII = {
    "decl":   {"randeaza": "randDecl",  "campuri": ["tip", "perioada", "termen", "motiv?"],
               "campuri_ceruti": ["tip", "perioada", "termen", "nr_depunere?"],
               "nota": "nr_depunere e OBLIGATORIU pe obiectele care sunt depuneri (La zi, Depuse cu "
                       "intarziere) si absent pe obligatii nedepuse (Restante, De urmarit). O "
                       "rectificativa = AL DOILEA obiect, nu o schimbare de stare a primului."},
    "motiv":  {"randeaza": "randMotiv", "campuri": ["tip", "motiv"],
               "campuri_ceruti": ["tip", "domeniu_de", "domeniu_pana", "motiv"],
               "nota": "domeniul e INTERVAL marginit la ambele capete. Capat de jos nedeterminabil "
                       "= a DOUA necunoscuta, declarata separat. Exceptia pe STATUT: R2' deschisa."},
    "a":      {"randeaza": "randA",     "campuri": ["stare", "mesaj", "temei", "remediu?"]},
    "const":  {"randeaza": "randConst", "campuri": ["stare", "mesaj", "temei", "remediu?"]},
    "verif":  {"randeaza": "randVerif", "campuri": ["eticheta", "ok", "detaliu?"]},
}

# ─────────────────────────────────────────────────────────────────────────────
# FELURI — nomenclatorul afirmațiilor din „Nu pot verifica" / „Nu se datorează".
# [R2′, 20.08.2026] Payload-ul DECLARĂ felul; garda nu-l deduce din prezența câmpurilor. O deducție
# din câmpuri e o afirmație implicită — clasa închisă de două ori azi. Un rând pe statut care are din
# întâmplare și o perioadă ar fi clasificat greșit, în tăcere.
# NOMENCLATOR ÎNCHIS: un `fel` nou fără intrare aici = ROȘU (tiparul VC_RANDATE).
# Enumerat pe 13 firme, 8 formulări distincte — nu propus din exemple.
# ─────────────────────────────────────────────────────────────────────────────
FELURI = {
    "necunoastere": {
        "domeniu": ["interval", "perioada"],
        "campuri_ceruti": ["fel", "tip", "motiv", "domeniu_de", "domeniu_pana"],
        "nota": "Forma domeniului urmează forma constatării: necunoscuta e un PUNCT pe axă (d300 — "
                "data înregistrării în scopuri de TVA) -> interval; e PE AN (d100, d205) -> perioadă. "
                "Capătul de jos nedeterminabil = A DOUA necunoaștere, declarată separat, nu ascunsă "
                "într-un «toate perioadele anterioare».",
    },
    "fapt": {
        "domeniu": ["perioada", "interval"],
        "campuri_ceruti": ["fel", "tip", "motiv", "an", "luna", "temei_completitudine"],
        "grade_de_temei": {
            "confirmat": "contabilul a afirmat completitudinea (perioada_confirmata pe domeniul "
                         "relevant). AZI EXISTĂ DOAR pentru `pontaj`, cu un singur consumator în tot "
                         "codul (stat_plata_api:50, tichete/HG 1045/2018). Deci gradul ăsta e "
                         "INACCESIBIL pentru orice ține de TVA — lacună de implementare, nu alegere.",
            "dedus": "sistemul deduce din perioadă ÎNCHISĂ + nimic în așteptare. Îl au `d100_fapt` și "
                     "`d390_fapt`, cu contract pe TREI valori (are / nu are / nu se poate ști). "
                     "Mai slab decât confirmarea, dar real.",
            "niciunul": "tabel gol -> verdict. NU e `fapt`, e `absenta_observatie`.",
        },
        "nota": "Un fapt constatat pe o perioadă anume (d390 «nicio operațiune IC în lună», d100 «fără "
                "venituri în trimestru»). SINGURELE rânduri corecte azi — poartă deja an+luna. "
                "ÎNCADRARE INCERTĂ: d301 «nicio operațiune IC înregistrată» (3 apariții) — reținut aici "
                "ca fapt pe interval, nu ca statut; de reconfirmat.",
    },
    "absenta_observatie": {
        "domeniu": ["sursa_numita"],
        "campuri_ceruti": ["fel", "tip", "motiv", "surse_consultate"],
        "nota": "NU am înregistrări într-o sursă numită. NU e fapt: absența unei înregistrări nu e "
                "absența unui fapt. Se distinge de `necunoastere` prin REMEDIU, nu prin taxonomie — "
                "necunoașterea trimite la «completează atributul X», asta trimite la «verifică dacă "
                "faptul a existat». Criteriul de separare (Costin, 20.08): felurile se disting prin "
                "ce are omul de făcut, nu prin eleganță. APARȚINE lui «Nu pot verifica», NICIODATĂ "
                "lui «Nu se datorează». PRECEDENT: tenant_006 — «nu se datorează» din vector, în timp "
                "ce firma avea achiziții IC reale.",
    },
    "statut": {
        "domeniu": ["relatie_deschisa"],
        "campuri_ceruti": ["fel", "tip", "motiv", "statut", "statut_din"],
        "nota": "Relație, nu interval: cât timp ține statutul, obligația nu există. Capătul de sus e "
                "DESCHIS prin natura afirmației — a-l închide artificial pe perioada evaluată ar afirma "
                "o graniță pe care realitatea n-o are, iar peste șase luni s-ar citi ca fapt. "
                "Capătul de jos e determinabil: firma_profil.platitor_tva_anaf_inceput (sursa ANAF).",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURA — casetele ecranului, în ordinea de randare.
#   sursa      : de unde vine conținutul, în payload-ul /control-fiscal/{id}
#   apare_cand : condiția din cod care decide dacă secțiunea se randează deloc
#   rand       : anatomia rândurilor (None = secțiune fără rânduri repetate)
#   numarata   : titlul poartă un contor "(n)" — deci n TREBUIE să fie len(sursa)
#   cheie      : cheia din payload (sau chei separate prin "|"); None = nu depinde de o listă
#   conditie   : forma CITIBILĂ DE MAȘINĂ a lui `apare_cand`. Proza rămâne ca documentație, dar
#                garda rulează pe câmpul ăsta. Valorile "special" sunt NUMITE, nu ascunse:
#                lista_nevida · lista_nevida_dupa_filtrare · vc_prezent · vc_cu_constatari ·
#                vc_oricare_cu_constatari · stare_verde · intotdeauna
# ─────────────────────────────────────────────────────────────────────────────
STRUCTURA = {
    "control_fiscal": {
        "renderer": "static/js/ecrane/control_verdict.js::randeazaCorpVerdict",
        "payload": "/control-fiscal/{tenant_id}",
        "casete": [
            {"id": "restante", "cheie": 'lipsa', "conditie": 'lista_nevida', "titlu": "Restanțe", "sursa": "d.lipsa",
             "apare_cand": "len(d.lipsa) > 0", "rand": "decl", "numarata": True},
            {"id": "de_urmarit", "cheie": 'urmarit', "conditie": 'lista_nevida', "titlu": "De urmărit", "sursa": "d.urmarit",
             "apare_cand": "len(d.urmarit) > 0", "rand": "decl", "numarata": True},
            {"id": "nu_pot_verifica", "cheie": 'neclar', "conditie": 'lista_nevida', "titlu": "Nu pot verifica", "sursa": "d.neclar",
             "apare_cand": "len(d.neclar) > 0", "rand": "motiv", "numarata": True},
            {"id": "nu_se_datoreaza", "cheie": 'neaplicabile', "conditie": 'lista_nevida', "titlu": "Nu se datorează", "sursa": "d.neaplicabile",
             "apare_cand": "len(d.neaplicabile) > 0", "rand": "motiv", "numarata": True},
            {"id": "depuse_cu_intarziere", "cheie": 'cu_intarziere', "conditie": 'lista_nevida', "titlu": "Depuse cu întârziere", "sursa": "d.cu_intarziere",
             "apare_cand": "len(d.cu_intarziere) > 0", "rand": "decl", "numarata": True},
            {"id": "la_zi", "cheie": 'confirmate', "conditie": 'lista_nevida', "titlu": "La zi", "sursa": "d.confirmate",
             "apare_cand": "len(d.confirmate) > 0", "rand": "decl", "numarata": True},
            {"id": "declaratie_vs_contabilitate", "cheie": 'tva_incrucisat|d112_incrucisat|d390_incrucisat', "conditie": 'vc_oricare_cu_constatari', "titlu": "Declarație vs contabilitate",
             "sursa": "vc.tva_incrucisat + vc.d112_incrucisat + vc.d390_incrucisat",
             "apare_cand": "cel putin un verificator are constatari", "rand": "const", "numarata": False},
            {"id": "conformitate_facturi", "cheie": 'cota_tva_conformitate', "conditie": 'vc_cu_constatari', "titlu": "Conformitate facturi emise",
             "sursa": "vc.cota_tva_conformitate",
             "apare_cand": "are constatari", "rand": "const", "numarata": False},
            {"id": "coerenta_tva", "cheie": 'tva', "conditie": 'vc_prezent', "titlu": "Coerență TVA (balanță)", "sursa": "vc.tva",
             "apare_cand": "vc.tva prezent", "rand": "verif", "numarata": False},
            {"id": "documente_pozate", "cheie": 'documente_pozate', "conditie": 'vc_prezent', "titlu": "Documente pozate", "sursa": "vc.documente_pozate",
             "apare_cand": "vc.documente_pozate prezent", "rand": "verif", "numarata": False},
            {"id": "verificari_contabile", "cheie": 'contabil', "conditie": 'lista_nevida_dupa_filtrare', "titlu": "Verificări contabile",
             "sursa": "d.contabil, fara etichetele din DEJA_IN_INCRUCISAT",
             "apare_cand": "raman elemente dupa filtrare", "rand": "a", "numarata": True},
            {"id": "totul_la_zi", "cheie": None, "conditie": 'stare_verde', "titlu": "Totul depus la zi", "sursa": "d.stare",
             "apare_cand": "d.stare == 'verde'", "rand": None, "numarata": False},
            {"id": "audit_preluare", "cheie": None, "conditie": 'intotdeauna', "titlu": "Audit de preluare",
             "sursa": "/control-fiscal/{tenant_id}/audit-preluare (la cerere)",
             "apare_cand": "intotdeauna", "rand": "a", "numarata": False},
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# TEMEI — pentru casetele care poartă o valoare GUVERNATĂ DE O REGULĂ.
# PROPUNERE. Nu se citește din cod: aici e granița dintre ce pot consulta și ce ceri tu.
# ─────────────────────────────────────────────────────────────────────────────
TEMEI = {
    "restante.termen":            "scadența legală per declarație — core/scadente.py; de legat la actul care o fixează",
    "de_urmarit.termen":          "idem",
    "depuse_cu_intarziere.termen": "idem",
    "la_zi.termen":               "idem",
    "coerenta_tva.detaliu":       "soldurile 4426/4427 din balanță; regula de coerență TVA",
    "totul_la_zi":                "d.stare, calculată de control_fiscal_api._stare(lipsa, urmarit, neclar)",
}

# ─────────────────────────────────────────────────────────────────────────────
# CONSTRÂNGERI ÎNTRE CASETE — relații, nu proprietăți. Nu există nicăieri în cod.
# DOUĂ câmpuri, fiindcă unul singur minte:
#   marcaj : CINE decide — [COD] derivabilă din cod / [TU] judecată de domeniu, la Costin
#   stare  : CE se întâmplă azi —
#            'verifica'        = implementată și trece pe datele curente
#            'datorie'         = implementată și PICĂ deliberat (xfail), defectul e cunoscut
#            'neexercitat'     = decisă și implementabilă, dar datele nu o pun la încercare
#                                (a NU se confunda cu 'verifica' — verde fiindcă n-are ce contrazice)
#            'asteapta_decizie'= nimic nu o verifică; e la Costin
# ─────────────────────────────────────────────────────────────────────────────
CONSTRANGERI = [
    {"id": "contor_egal_lungime", "stare": 'verifica', "marcaj": "[COD]",
     "regula": "Pentru fiecare casetă cu numarata=True, n din titlu == len(sursa)."},

    {"id": "identitate_completa", "stare": 'datorie', "marcaj": "[COD]",
     "regula": "Un rând poartă cheia de identificare a entității randate. Pentru declarații, cheia e "
               "cea din public.declaratii_depuse: (tip, perioada, nr_depunere). AZI PICĂ: nr_depunere "
               "lipsește din toate rândurile, perioada lipsește din anatomia `motiv`. "
               "Decis 20.08.2026 (R1'), vezi DECIZII."},

    {"id": "obiecte_distincte_nu_suprapunere", "stare": 'neexercitat', "marcaj": "[COD]",
     "regula": "Două rânduri cu aceeași (tip, perioada) dar nr_depunere diferit NU sunt o suprapunere — "
               "sunt obiecte declarative distincte (inițială + rectificativă), fiecare cu starea lui. "
               "Constrângerea de unicitate se aplică pe cheia ÎNTREAGĂ, nu pe (tip, perioada)."},

    {"id": "motiv_poarta_domeniul", "stare": 'datorie', "marcaj": "[COD]",
     "regula": "Fiecare rând de anatomie `motiv` (Nu pot verifica / Nu se datorează) poartă perioada "
               "sau intervalul la care se referă. AZI PICĂ: intrările din d.neclar au doar {tip, motiv}, "
               "iar textul lor afirmă 'pentru restanțele trecute' — un domeniu pe care datele nu-l poartă. "
               "Lăsată deliberat neredusă: vreau ca garda s-o prindă, nu eu. "
               "DECIS 20.08.2026 (R2): interval mărginit la ambele capete; forma domeniului urmează "
               "forma constatării. Excepția pe STATUT (12 rânduri D301) = R2', încă deschisă."},

    {"id": "payload_declara_felul", "stare": "datorie", "marcaj": "[COD]",
     "regula": "Fiecare rând din `neclar`/`neaplicabile` poartă un `fel` din nomenclatorul FELURI, "
               "DECLARAT de payload. Garda nu deduce felul din prezența câmpurilor — o deducție e o "
               "afirmație implicită. AZI PICĂ: niciun rând nu poartă `fel`. Decis 20.08 (R2')."},

    {"id": "campurile_urmeaza_felul", "stare": "datorie", "marcaj": "[COD]",
     "regula": "Câmpurile cerute ale unui rând depind de `fel` (vezi FELURI.campuri_ceruti): "
               "necunoastere -> domeniu_de+domeniu_pana; fapt -> an+luna; statut -> statut+statut_din. "
               "AZI PICĂ pentru necunoastere și statut; `fapt` cu perioadă e deja corect."},

    {"id": "nomenclator_feluri_inchis", "stare": "verifica", "marcaj": "[COD]",
     "regula": "Un `fel` produs de backend fără intrare în FELURI = ROȘU, nu omisiune tăcută. "
               "Tiparul VC_RANDATE. Verificabil azi chiar dacă payload-ul încă nu poartă `fel`."},

    {"id": "stare_coerenta_cu_continut", "stare": 'verifica', "marcaj": "[COD]",
     "regula": "Pastila d.stare e coerentă cu grupurile randate: rosu <-> lipsa nevidă; "
               "verde <-> lipsa și urmarit vide. Regula există în _stare(); constrângerea cere ca "
               "ce se AFIȘEAZĂ să corespundă."},

    {"id": "verde_exclude_restante", "stare": 'neexercitat', "marcaj": "[COD]",
     "regula": "Dacă apare 'Totul depus la zi', nu apare nici 'Restanțe', nici 'De urmărit'."},

    {"id": "fara_dublare_incrucisat", "stare": 'neexercitat', "marcaj": "[COD]",
     "regula": "O etichetă din DEJA_IN_INCRUCISAT nu apare simultan în 'Verificări contabile' "
               "și în 'Declarație vs contabilitate'."},

    {"id": "datorate_egal_suma_categoriilor", "stare": "verifica", "marcaj": "[COD]",
     "regula": "«n datorate» din pastilă == lipsa + urmarit + confirmate + cu_intarziere. Adevărat PRIN "
               "CONSTRUCȚIE: _clasifica() sparge aceeași listă în cele patru. Decis 20.08 (R3): "
               "«datorate» = toate obligațiile perioadei, nu cele neonorate — un numitor care se "
               "micșorează pe măsură ce depui nu e numitor."},

    {"id": "depuse_din_aceeasi_multime", "stare": "datorie", "marcaj": "[COD]",
     "regula": "«n depuse» == |{(tip, perioadă) din confirmate ∪ cu_intarziere}| — numărul de OBLIGAȚII "
               "stinse, nu de depuneri. Ambele numere ale pastilei trebuie să numere același fel de "
               "lucru, altfel «8 datorate · 9 depuse» e o propoziție care nu se poate citi. "
               "R1' atinge LISTA (două rânduri pentru iunie), nu PASTILA (o obligație în contor), deci "
               "`DISTINCT ON` din vedere e CORECT aici. "
               "AZI PICĂ din DOUĂ cauze distincte, ambele verificate: (1) `depuse` numără toată "
               "istoria firmei (declaratii_depuse_curente, fără WHERE), iar `datorate` e pe fereastra "
               "[≈ termenul lui dec. anul trecut … azi+7]; (2) mai grav — o depunere a cărei obligație "
               "e clasificată `neclar` nu are ce stinge, fiindcă obligația nu intră în `datorate`. "
               "Constructii Profit Trim: D300/06-2026 DEPUS, dar d300 e în `neclar` -> «0 datorate · 1 "
               "depuse». Derivat din cod+git 20.08 (R3): eticheta a apărut la 12 zile după câmp, pe un "
               "backend «deja existent». Vezi R6 (deschisă): depunerea e dovadă care rezolvă neclar-ul?"},

]

# ─────────────────────────────────────────────────────────────────────────────
# LIMITE DECLARATE ale hărții — ce NU poate acoperi, ca să nu pară acoperire.
# ─────────────────────────────────────────────────────────────────────────────
LIMITE = [
    "GARDUL CITEȘTE O SINGURĂ FIRMĂ. Artefactul e produs pe un tenant; o constrângere poate TRECE "
    "fiindcă starea acelei firme n-o pune la încercare, deși pică pe alta. Descoperit la prima folosire "
    "reală: `depuse_din_aceeasi_multime` trece pe t001 (0=0) și pică pe Constructii Profit Trim "
    "(0 datorate · 1 depuse). Instrumentul construit ca să repare punctul orb «o firmă» îl reproduce. "
    "Fix: scanerul să acopere mai multe firme, artefactul să le poarte pe toate.",

    "Cifrele din confruntarea declarație↔contabilitate (ex. «D112 declară X, contul Y are Z») sunt "
    "ÎNCORPORATE ÎN PROZA din `mesaj`, nu câmpuri separate în payload. Nicio intrare de hartă nu poate "
    "arăta spre ele și niciun comparator nu le poate verifica. Ca să devină verificabile, backendul ar "
    "trebui să le dea ca valori, iar mesajul să se compună din ele.",

    "Harta descrie CORPUL verdictului. Antetul (pastila, «n datorate · n depuse») e pus de apelant "
    "(control.js / firme.js), nu de renderer — deci o parte din ce se vede pe ecran nu e în harta asta.",

    "«În ce stări apare o casetă» e exprimat ca `apare_cand`, adică o condiție pe payload, nu o listă "
    "de stări de firmă. E suficient pentru gardă, dar NU răspunde la «pe ce firmă se vede starea asta» "
    "— aia rămâne la registrul de stări, neconstruit.",
]
