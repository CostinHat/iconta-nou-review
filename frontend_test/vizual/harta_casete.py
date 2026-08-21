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

STARE: DRAFT. `STRUCTURA` e citită din cod și o susțin. `TEMEI` e despărțit în temei_legal/regula_produs
(R5 20.08.2026) și are gardă: core/test_harta_temei.py. `CONSTRANGERI` rămân PROPUNERI —
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
        "campuri_ceruti": ["fel", "tip", "motiv", "temei_completitudine"],
        "domeniu_alternativ": ["an+luna", "unde"],
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
        "nota": "[22.08.2026] DOMENIU ALTERNATIV: `an`+`luna` SAU `unde` (o referință structurată din "
                "core/unde.py), unul din două OBLIGATORIU. Lipsa era a DOMENIULUI, nu a felului: un "
                "fapt despre pachetul de preluare și unul despre o lună sunt același fel de afirmație. "
                "Nomenclatorul fusese enumerat pe rânduri de DECLARAȚIE, unde domeniul e mereu o "
                "perioadă. Un fapt FĂRĂ NICIUN domeniu rămâne INTERZIS. || "
                "Un fapt constatat pe o perioadă anume (d390 «nicio operațiune IC în lună», d100 «fără "
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
    "contradictie": {
        "domeniu": ["doua_afirmatii"],
        "campuri_ceruti": ["fel", "tip", "motiv", "sursele"],
        "nota": "[21.08.2026] Doua afirmatii care nu pot fi amandoua adevarate: profilul zice ca "
                "firma nu are operatiuni IC, dar exista facturi IC reale; sau o depunere pe o "
                "perioada declarata neaplicabila. NU e necunoastere - acolo nu stim, aici stim doua "
                "lucruri incompatibile. `sursele` le numeste pe amandoua, altfel nu se poate arbitra.",
    },
    "verificare_rupta": {
        "domeniu": ["fara_domeniu"],
        "campuri_ceruti": ["fel", "tip", "motiv", "eroare"],
        "nota": "[21.08.2026] Verificarea INSASI s-a oprit - bug, deriva de semnatura. NU e "
                "necunoastere: aia ar ascunde-o ca verdict permanent gri, si asa a stat D300 mort "
                "(vezi `_c_rupt` in control_incrucisat). O verificare rupta arata pe ecran la fel cu "
                "una care „nu poate spune\", si de-aia trebuie sa poarte alt nume. Fara domeniu: nu "
                "afirma nimic despre vreo perioada, fiindca n-a apucat sa se uite. `eroare` e "
                "obligatorie - fara ea nimeni nu poate incepe s-o repare.",
    },
    "neconformitate": {
        "domeniu": ["locul_din_date"],
        "campuri_ceruti": ["fel", "tip", "motiv", "unde", "regula"],
        "nota": "[21.08.2026] O VALOARE nu satisface o REGULA: „randul 7: CNP invalid\", „durata "
                "lipseste\". Nu incape in celelalte - nu e necunoastere (stim foarte bine), nu e "
                "absenta (valoarea E acolo, dar nu tine), nu e statut. Domeniul nu e o PERIOADA, ci "
                "LOCUL: care rand, care inregistrare. `regula` numeste de ce nu tine - fara ea, "
                "respingerea e un repros fara adresa, si contabilul nu stie ce sa corecteze.",
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
             "apare_cand": "len(d.neclar) > 0 sau len(opinii) > 0", "rand": "motiv", "numarata": True,
             "rand_secundar": "semnal",
             "nota": "[R6 21.08.2026] Grupul apare si cand `neclar` e gol dar exista OPINII "
                     "(depuneri pe un tip neclar). Contorul din titlu numara doar `neclar` - "
                     "opinia NU e o obligatie, deci n-are ce numara acolo."},
            {"id": "nu_se_datoreaza", "cheie": 'neaplicabile', "conditie": 'lista_nevida', "titlu": "Nu se datorează", "sursa": "d.neaplicabile",
             "apare_cand": "len(d.neaplicabile) > 0 sau len(contraziceri) > 0", "rand": "motiv", "numarata": True,
             "rand_secundar": "semnal",
             "nota": "[R6 21.08.2026] Un motiv poate purta un SEMNAL: o depunere care il contrazice. "
                     "Rosu SOBRU (--rosu pe --rosu-fundal), NU rosu-semafor - nu e o restanta a firmei, "
                     "e o incoerenta a NOASTRA; din acelasi motiv NU urca pastila. Grupul apare si "
                     "cand `neaplicabile` e gol dar exista contraziceri; contorul din titlu numara "
                     "doar obligatiile, fiindca un semnal nu e o obligatie."},
            {"id": "ce_nu_poate_spune", "cheie": 'limite', "conditie": 'lista_nevida',
             "titlu": "Ce nu poate spune verificarea asta", "sursa": "d.limite",
             "apare_cand": "intotdeauna (lista e compusa, nu conditionata de date)", "rand": "limita",
             "numarata": False,
             "nota": "[P4 21.08.2026, DS cap.25.4] Despre CAPACITATE, nu despre date: ce nu poate "
                     "afirma instrumentul, indiferent ce contine firma. PERMANENTA - daca ar aparea "
                     "doar cateodata, prezenta ei ar deveni semnal si absenta ar minti. Necolorata "
                     "(nu e problema de rezolvat), jos (nu e alarma), compacta cu detaliul la "
                     "extindere (nu intr-un ?, care dispare exact pentru cine are nevoie). Se COMPUNE "
                     "din limite declarate ca DATE: acoperirea, perimetrul calculat din fereastra "
                     "reala, si limita fiecarui verificator prezent. NU intra necunoasterea legata de "
                     "un obiect (ramane langa obiect) si nici datoriile de dezvoltare (sunt ale "
                     "noastre, nu ale contabilului).",
             },
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
#
# DOUĂ CÂMPURI, fiindcă unul singur amestecă două lucruri care SE REVIZUIESC DIFERIT (R5, 20.08.2026):
#   temei_legal   — se schimbă când se schimbă legea; nu decizi nimic.
#   regula_produs — se schimbă când decizi tu, iar „mai e bună?" e o întrebare legitimă oricând.
# Amestecate, o regulă de produs devine imposibil de repus în discuție (nimeni nu contestă un articol de
# lege), iar o prevedere legală devine negociabilă — ceea ce e mai rău. Exemplul care a produs regula:
# indicatorul de patru ochi. Dacă ar fi fost etichetat temei legal în loc de control intern, nimeni n-ar
# fi discutat dacă „posibil" înseamnă >=2 validatori, și fundătura rămânea.
#
# AL TREILEA FEL nu cere un al treilea câmp: e cazul în care AMÂNDOUĂ sunt pline. Termenul care se mută
# în ziua lucrătoare următoare e lege; alegerea de a afișa firma ca restanțieră de a doua zi e produs.
# Intrarea e unitatea: `regula_produs` spune CE ADAUGă peste actul citat, nu reformulează actul.
#
# `decizie` + `data` pe fiecare regulă de produs: funcția spune ce face, decizia spune de ce și când.
# Fără dată, peste șase luni nu se știe dacă regula a fost gândită sau a apărut din inerție. Când decizia
# nu e consemnată, se scrie NEDOCUMENTATA — tăcerea s-ar citi ca „gandită".
# ───────────────────────────────────────────────────────────────────────────────

NEDOCUMENTATA = "NEDOCUMENTATA"   # decizia care a fixat regula nu e consemnată nicăieri


def DATORIE(unde):
    """Temei legal ABSENT și declarat ca atare. NU e același lucru cu tăcerea: tăcerea se citește ca
    „n-are nevoie de temei", datoria spune „are, și încă nu l-am scris — se urmărește aici"."""
    return {"stare": "datorie", "unde": unde}


def PRODUS(regula, decizie, data):
    return {"regula": regula, "decizie": decizie, "data": data}


_DATORIE_TERMENE = "R4 20.08.2026 — temeiul se atașează PER TIP; legat în core/test_temei_termene.py (xfail strict)"

TEMEI = {
    "restante.termen": {
        "temei_legal": DATORIE(_DATORIE_TERMENE),
        "regula_produs": PRODUS(
            "O obligație intră în «Restanțe» din ziua URMĂTOARE termenului: control_fiscal_api "
            "clasifică `term < azi` ca restanță (l.503), deci în chiar ziua termenului e încă «de urmărit». "
            "Ce adaugă peste lege: legea fixează termenul, nu ziua din care ești numit restanțier.",
            decizie=NEDOCUMENTATA, data=None)},

    "de_urmarit.termen": {
        "temei_legal": DATORIE(_DATORIE_TERMENE),
        "regula_produs": PRODUS(
            "Fereastra galbenă e de 7 zile: control_fiscal_api.PRAG_URMARIT_ZILE = 7. Integral produs — "
            "nicio lege nu cere un avertisment anticipat. Valoarea e și în clasa C a scanului de constante "
            "nesursate (core/scan_constante.py), deci apare în două inventare independente.",
            decizie=NEDOCUMENTATA, data=None)},

    "depuse_cu_intarziere.termen": {
        "temei_legal": DATORIE(_DATORIE_TERMENE),
        "regula_produs": PRODUS(
            "O depunere târzie rămâne marcată târzie — nu se «vindecă». Două depuneri pe aceeași perioadă "
            "produc două RÂNDURI, nu un rând care își schimbă starea: un rând care și-ar schimba starea ar "
            "șterge faptul că prima a fost la timp. Motivul e fiscal, nu de UI.",
            decizie="R1", data="2026-08-20")},

    "la_zi.termen": {
        "temei_legal": DATORIE(_DATORIE_TERMENE),
        "regula_produs": PRODUS(
            "«La zi» = depusă la sau înaintea termenului. Simetric cu restanța, deci aceeași graniță în "
            "control_fiscal_api trebuie să le separe pe amândouă.",
            decizie=NEDOCUMENTATA, data=None)},

    "coerenta_tva.detaliu": {
        # singurul temei legal REZOLVABIL azi: planul de conturi e în corpus (anaf_surse/omfp_1802_2014).
        "temei_legal": "OMFP 1802/2014",
        "regula_produs": PRODUS(
            "Coerența se verifică pe soldurile 4426 (TVA deductibilă) / 4427 (TVA colectată) din balanță. "
            "Ce adaugă peste ordin: ordinul fixează conturile și conținutul lor, nu obligația de a le "
            "reconcilia cu D300 și nici pragul de la care diferența se raportează.",
            decizie=NEDOCUMENTATA, data=None)},

    "totul_la_zi": {
        # nu are temei legal, și asta e o AFIRMAȚIE, nu o omisiune — de-aia e scris explicit, nu lăsat gol.
        "temei_legal": None,
        "regula_produs": PRODUS(
            "d.stare = control_fiscal_api._stare(lipsa, urmarit, neclar), cu prioritatea "
            "roșu > galben > gri > verde. Griul NU poate fi ascuns ca verde: verdele e o afirmație "
            "(«am verificat și e în regulă»), griul spune că afirmația nu se poate face, iar o afirmație "
            "parțial imposibilă nu devine adevărată prin partea care s-a putut face. "
            "Gardat: core/test_pastila_gri.py.",
            decizie="gri_nu_devine_verde", data="2026-08-20")},
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
