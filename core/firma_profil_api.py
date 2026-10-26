"""
core/firma_profil_api.py — profilul firmei din schema unui tenant.
Ruleaza pe conexiunea deja pozitionata pe schema tenantului (get_conn(schema)).
Folosit de ecranul "Model factura": datele firmei (pt preview) + personalizare
(font, culoare, logo). Logo = string base64 (data URI), stocat in coloana logo (text).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations

from core.mesaje import MESAJ_FARA_ADMINISTRATOR, MESAJ_PESTE_PERIOADA_INCHISA

from core import afirmatii as _af  # [P8] blocajul numeste regula

MODUL = "firma_profil_api"

# fonturi web-safe permise (merg garantat la print/PDF)
FONTURI = ("sans", "serif", "mono")

# ============================================================
#  CONT VENIT IMPLICIT — [F182] contul de venit folosit implicit la emitere factura
# ============================================================
# Sursa unica: planul OMFP (core/plan_omfp.PLAN_OMFP). Se permit DOAR conturile din
# clasa 70 (cifra de afaceri) — NU clasa 7 intreaga: 74x (subventii), 76x (venituri
# financiare), 78x (provizioane) nu sunt venituri din vanzare care se factureaza.
# Fallback la 707 (marfuri), la fel ca COALESCE-ul de la emitere (main.py). Vezi DECIZII 21.07 F182.
# [387, 19.10.2026] Cu planul întreg (OMFP 1802/2014 pct.594) grupa 70 are și 709 „Reduceri comerciale acordate” — un cont care
# micșorează cifra de afaceri, nu unul pe care se facturează o vânzare: nu e cont de venit implicit.
import re as _re
from core import plan_omfp as _plan

CONTURI_VENIT = {c: _plan.PLAN_OMFP[c] for c in sorted(_plan.PLAN_OMFP)
                 if _re.fullmatch(r"70[0-8]", c)}
CONT_VENIT_IMPLICIT_DEFAULT = "707"


def cont_venit_valid(cont):
    """PURA: True daca `cont` e un cont de venit din exploatare (clasa 70) valid."""
    return str(cont or "").strip() in CONTURI_VENIT

# ============================================================
#  [F180] REGIM TVA vs ANAF — snapshot separat + comparatie
# ============================================================
# platitor_tva = valoare EDITABILA manual (Configurare emitere / Vector fiscal).
# platitor_tva_anaf = snapshot al scpTVA de la ANAF v9 (SEPARAT), + data interogarii.
# Comparatia e apples-to-apples: scpTVA = "platitor la data interogarii" (verificat la
# sursa 22.07). Vezi DECIZII.md 22.07 F180. Fara snapshot -> "gri" (nu rosu).
def stare_tva_anaf(local, anaf):
    """PURA. Stare F180 din platitor_tva(local) vs platitor_tva_anaf(snapshot).
    `anaf` None (fara snapshot / ANAF necunoscut) -> 'gri'; difera -> 'rosu';
    coincid -> 'verde'. `local` None (vector necompletat) -> 'gri' (nu comparam)."""
    if anaf is None or local is None:
        return "gri"
    return "verde" if bool(local) == bool(anaf) else "rosu"


def avertisment_tva_anaf(local, anaf_val):
    """PURA. Avertisment F180 (dict) daca valoarea manuala difera de scpTVA ANAF, altfel
    None. `anaf_val` None (ANAF necunoscut) -> None (nu avertizam pe necunoscut)."""
    if anaf_val is None or local is None or bool(local) == bool(anaf_val):
        return None
    _txt = lambda b: "platitoare TVA" if b else "neplatitoare TVA"
    return {"camp": "platitor_tva", "local": bool(local), "anaf": bool(anaf_val),
            "mesaj": ("Ai setat firma ca %s, dar ANAF o are ca %s. Verifică în SPV; poți salva oricum."
                      % (_txt(local), _txt(anaf_val)))}


def citeste_tva(conn):
    """(cui, platitor_tva, platitor_tva_anaf, platitor_tva_anaf_data) din firma_profil."""
    with conn.cursor() as cur:
        cur.execute("SELECT cui, platitor_tva, platitor_tva_anaf, platitor_tva_anaf_data "
                    "FROM firma_profil LIMIT 1")
        row = cur.fetchone()
    if not row:
        return {"cui": None, "platitor_tva": None, "platitor_tva_anaf": None, "data": None}
    return {"cui": row[0], "platitor_tva": row[1],
            "platitor_tva_anaf": row[2], "data": row[3]}


def seteaza_snapshot_tva(conn, scp_tva, data_inceput=None):
    """Scrie snapshot-ul ANAF (scpTVA + data inregistrarii in scopuri de TVA la data curenta). `scp_tva` = bool;
    `data_inceput` = 'YYYY-MM-DD'|None (fapt ANAF, doar la platitor). Idempotent pe firma_profil (singleton).
    [tva_inceput_protejat] ANAF e autoritar CAND are data: o suprascrie. Cand ANAF NU intoarce data
    (data_inceput=None), NU golim coloana - pastram valoarea introdusa manual de contabil (altfel apelul
    de dupa salveaza in vector_salveaza ar sterge exact ce a completat contabilul)."""
    with conn.cursor() as cur:
        if data_inceput:
            cur.execute("UPDATE firma_profil SET platitor_tva_anaf=%s, platitor_tva_anaf_data=CURRENT_DATE, "
                        "platitor_tva_anaf_inceput=%s", (bool(scp_tva), data_inceput))
        else:
            cur.execute("UPDATE firma_profil SET platitor_tva_anaf=%s, platitor_tva_anaf_data=CURRENT_DATE",
                        (bool(scp_tva),))

# ============================================================
#  CITIRE profil (pentru preview + model)
# ============================================================
def citeste_profil(conn):
    """Datele firmei relevante pentru factura + personalizare. Dict (mereu 1 rand)."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT nume, cui, reg_com, adresa, oras, judet, cod_postal, "
            "iban, banca, email, telefon, logo, "
            "font_factura, culoare_factura, serie_factura, urmator_numar_factura, "
            "platitor_tva, "   # [lot 19 pct.4d] factura unui neplatitor nu mentioneaza taxa (CF art.310 alin.(10) lit.b))
            "tip_firma, forma_juridica, capital_subscris, capital_varsat "   # [lot 19 d12] L31/1990 art.74 alin.(3)
            "FROM firma_profil LIMIT 1")
        r = cur.fetchone()
    return dict(r) if r else {}

# ============================================================
#  SALVARE model (font, culoare, logo)
# ============================================================
def salveaza_model(conn, font=None, culoare=None, logo=None):
    """
    Actualizeaza doar campurile de personalizare a facturii.
    - font: unul din FONTURI (altfel se ignora, ramane cel curent)
    - culoare: hex '#rrggbb' (validare simpla)
    - logo: data URI base64 sau None (None = nu schimba; '' = sterge)
    Intoarce {"ok": True, "profil": {...}} cu valorile noi.
    """
    seturi = []
    valori = []

    if font is not None:
        f = str(font).strip().lower()
        if f in FONTURI:
            seturi.append("font_factura = %s")
            valori.append(f)

    if culoare is not None:
        c = str(culoare).strip()
        if _culoare_valida(c):
            seturi.append("culoare_factura = %s")
            valori.append(c)

    if logo is not None:
        # '' sterge logo-ul; alt string il seteaza
        seturi.append("logo = %s")
        valori.append(logo if logo != "" else None)

    if seturi:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE firma_profil SET " + ", ".join(seturi) + " WHERE id = 1",
                tuple(valori))

    return {"ok": True, "profil": citeste_profil(conn)}

# ============================================================
#  DATE FIRMA — campurile cerute de ANAF in declaratii
# ============================================================
# Sursa: validatoarele din core/dXXX.py (functiile valideaza()), care ridica
# "LIPSA <camp>" cand declaratia nu se poate genera. Dovedit 15.07.2026 pe
# validatorul oficial ANAF. Fiecare camp obligatoriu are asterisc in interfata
# (DS cap.6); lipsa lui NU blocheaza salvarea, ci declaratiile din OBLIGATORII [lotul 10, deficienta 427].
# [R66, 26.08.2026] `patron_nume` a intrat aici fiindca avea drum de CITIRE si niciun drum de
# SCRIERE: il citesc `adeverinta`, `contracte_api` si `pachete_api` — deci se TIPARESTE pe
# documente care ajung la oameni — iar nimic din aplicatie nu-l scria. A treia coloana din clasa
# asta gasita in aceeasi zi, si singura care nu se putea scoate: primele doua aveau inlocuitor,
# asta lasa un gol pe hartie. Decizia lui Costin: *„numele administratorului e un fapt al firmei,
# ca denumirea si CUI-ul. Nu se derivă din nimic — cine tine evidenta nu e neaparat cine semneaza."*
# [lot 19 d12] Legea 31/1990 art.74 alin.(3): forma juridica + capitalul de pe factura (v. core/capital_social.py)
CAMPURI_CAPITAL = ("forma_juridica", "capital_subscris", "capital_varsat")
# [D394 Î2] activitatea exceptată de la AMEF (OUG 28/1999 art.2, v. core/activitati_amef.py)
CAMPURI_AMEF = ("activitate_exceptata_amef", "activitate_amef")

CAMPURI_FISCALE = ("nume", "cui", "reg_com", "caen", "adresa", "oras", "judet",
                   "cod_postal", "banca", "iban", "telefon", "email", "patron_nume",
                   "declarant_nume", "declarant_prenume", "declarant_functie")

#: [lotul 10, deficiența C69, deciziile Costin 20.10.2026, verbatim în DECIZII „Lotul 10, C69 … deciziile lui Costin”] „Câmpuri noi +
#: blocaj”: „mare contribuabil (Da/Nu)” și „forma de proprietate” (nomenclatorul ANAF, `bilant.FORME_PROPRIETATE`) — bilanțul le cere
#: (bifaMC / codJJ / codPP) și se oprește fără ele; „Varianta 1”: bifa „nu are cont bancar”, lângă IBAN — D406 scrie atunci „Fara cont
#: bancar” (S.BA.2), iar rulajul / soldul pe 512x în perioadă o contrazice și oprește D406. Coloanele: core/migrare_profil_c69.py.
CAMPURI_C69 = ("mare_contribuabil", "forma_proprietate", "fara_cont_bancar")

#: [lotul 11, decizia Costin 10.3 pct.4, verbatim în DECIZII „Comanda 10.3”: „Întocmitorul bilanțului: calitatea întocmitorului în profilul
#: cabinetului, interesul public în Date firmă; ambele blochează dacă lipsesc.”] Structura ANAF a bilanțului (anaf_surse/
#: structura_SC_1225_270126.txt, S1002 / S1003 / S1005): „15. interes_public Entitati de interes public N(1) DA interes_public=(0,1)”.
#: Generatorul scria 0 oricărei firme (`bilant.xml_s1005`); acum Da / Nu din Date firmă, NULL = nedeclarat -> bilanțul se oprește.
#: Coloana: core/migrare_intocmitor_bilant.py.
CAMPURI_BILANT = ("interes_public",)

#: [06.10.2026, comanda Costin §6.4] „Orice modificare [a Date firmă] se jurnalizează (cine, când, valoare veche → nouă),
#: inclusiv forma juridică și capitalul, iar jurnalul e vizibil cabinetului.” Toate câmpurile ecranului, din toate grupurile.
CAMPURI_JURNAL = CAMPURI_FISCALE + CAMPURI_CAPITAL + CAMPURI_AMEF + CAMPURI_C69 + CAMPURI_BILANT + ("cont_venit_implicit", "metoda_stoc", "serie_chitanta",
                                                                    "luna_preluare",   # [08.10 §6 pct.4] „Schimbarea se jurnalizează.”
                                                                    "data_infiintare")   # [deficiența 229, 12.10.2026]


def _instantaneu(conn):
    """Câmpurile Date firmă ca text (forma în care se compară și se jurnalizează)."""
    with conn.cursor() as cur:
        cur.execute("SELECT %s FROM firma_profil WHERE id = 1" % ", ".join(CAMPURI_JURNAL))
        r = cur.fetchone()
    if not r:
        return {}
    return {c: (None if v is None else (str(v).lower() if isinstance(v, bool) else str(v))) for c, v in zip(CAMPURI_JURNAL, r)}


# camp -> declaratiile care il cer OBLIGATORIU (pentru mesajul din interfata)
OBLIGATORII = {
    "nume": ("D100", "D101", "D205", "D301", "D390", "D394", "D406"),
    "cui": ("D100", "D101", "D205", "D300", "D301", "D390", "D394", "D406"),
    # [lotul 10, deficiența 427] + D112: structura ANAF D112 „6 caen Cod CAEN N(4) DA  Nomenclator 1 – coduri CAEN si tarife de
    # risc […] ERR caen ‘Cod caen inexistent in nomenclator’” (anaf_surse/d112_struct_anaf.txt) — generatorul punea „0000”.
    "caen": ("D101", "D112", "D300", "D394"),
    "adresa": ("D100", "D101", "D205", "D394"),   # D101: structura ANAF „28. adresa Adresa C(1000) DA" — citit 30.08.2026; codul o oprea deja, harta n-o spunea
    "banca": ("D300", "D301"),
    # [lotul 10, deficiența C69] + D406: antetul SAF-T cere localitatea (S.AD.5 City „Mandatory … 1”), telefonul (S.CTH.2
    # Telephone „Mandatory … 1”), contul bancar (S.CMH.6 BankAccount „Mandatory … 1..*”, S.BA.1 IBANNumber) și persoana de contact
    # (S.PN.2 FirstName / S.PN.5 LastName „Mandatory … 1”) — anaf_surse/d406_schema_anaf.xlsx, foaia „5. Structures”. Generatorul
    # le umplea cu „-” / „RO00BANK0000000000000000” / numele firmei; acum lipsa oprește D406 (`d406.erori_generare`).
    "oras": ("D406",),
    # [lotul 10, deficiența C69] bilanțul: „16. codTT Cod judet sediu (fara cod 41) N(2) DA Nomenclator Judete”
    # (anaf_surse/structura_SC_1225_270126.txt); lipsa devenea „bucuresti” (40) — acum oprește bilanțul (`bilant_api.erori_generare`).
    "judet": ("Bilanț",),
    "iban": ("D300", "D301", "D406"),   # [lotul 10, C69] D406 nu-l mai cere cu bifa „nu are cont bancar” (`lipsuri`, `d406.erori_generare`)
    "telefon": ("D394", "D406"),
    "reg_com": ("Bilanț S1005",),
    # [declarant_oblig 17.08.2026] nume+functia declarantului: DUK respinge campul gol al declarantului
    # (nume_declar/functie_declar) -> se cer EXPLICIT (ca regim_fiscal), nu se fabrica "ADMINISTRATOR" tacit.
    # [R101, 30.08.2026] `declarant_prenume` — structura ANAF a fiecareia din cele opt il cere
    # explicit, cu mesaj propriu de eroare: „prenume_declar Prenume declarant C(75) DA ...
    # ERR - prenume declarant necompletat". A stat AFARA pana azi printr-o decizie din
    # 17.08.2026 care spunea ca „nu orice declarant are prenume in forma ANAF"; decizia s-a
    # ANULAT pe 30.08.2026, cu motivul: daca exista un declarant fara prenume, intrebarea e ce
    # se completeaza acolo, nu un motiv sa lasi campul liber. SURSA BATE DECIZIA.
    # [lotul 10, C69] + D710: structura D100-D710 „nume_declar / prenume_declar / functie_declar … DA” (generatorul punea ADMINISTRATOR / „-”)
    # [lotul 10, C69] + Bilanț la prenume („19. nume_admin Nume si prenume Administrator C(75) DA”, structura SC 1225 — administratorul e
    # declarantul, decizia Costin); + D101G la toate trei: validatorul ANAF D101G v2 (~/duk/dist/lib/D101GValidator.jar, J2.0.0, același
    # sha256 cu cel publicat de ANAF) respinge lipsa: „eroare atribut: nume_declar: atributul trebuie sa existe” (la fel prenume / functie)
    "declarant_prenume": ("D100", "D101", "D101G", "D112", "D205", "D300", "D301", "D390", "D394", "D406", "D710", "Bilanț"),
    "declarant_nume": ("D100", "D101", "D101G", "D112", "D205", "D300", "D301", "D390", "D394", "D406", "D710", "Bilanț"),
    "declarant_functie": ("D100", "D101", "D101G", "D112", "D205", "D300", "D301", "D390", "D394", "D710", "Bilanț"),
    # [lotul 10, C69] bilanțul: „10. bifaMC … DA” / „17. codJJ … codJJ=41 daca bifa_MC=1” și „18. codPP Cod forma de proprietate N(2) DA
    # Nomenclator forme de proprietate” (anaf_surse/structura_SC_1225_270126.txt) — generatorul punea 1 / 10 / 35 oricărei firme
    "mare_contribuabil": ("Bilanț",),
    "forma_proprietate": ("Bilanț",),
    # [lotul 11, decizia 10.3] „15. interes_public Entitati de interes public N(1) DA interes_public=(0,1)” (structura SC 1225, S1002 /
    # S1003 / S1005); Nu (False) e o alegere, lipsă e numai nedeclarat (NULL) — ca `mare_contribuabil`
    "interes_public": ("Bilanț",),
}

#: [lotul 11, deficiența 442, comanda Costin 11.1 pct.18, verbatim: „capitalul social lipsă apare în «Profil incomplet», cu «blochează
#: emiterea facturilor».”] Ce blochează lipsa formei juridice / a capitalului: nu o declarație, emiterea facturilor (Legea 31/1990 art.74
#: alin.(3), refuzul de la emitere `facturi_api` -> `capital_social.refuz`).
BLOCHEAZA_EMITEREA = "emiterea facturilor"


def erori_declarant(prof):
    """Cele TREI campuri ale declarantului, cerute de structura ANAF a fiecareia din cele opt.

    [R101, 30.08.2026] DE CE E BLOCANT, si de ce s-a citit sursa inainte de a decide. La R93 harta
    avea dreptate si codul gresea; aici putea fi invers, deci nu s-a presupus. Citit verbatim din
    corpus (`anaf_surse/dXXX_struct_anaf.txt`), toate cu marcajul DA si cu mesaj propriu de eroare:

        D100  „3 nume_declar Nume declarant C(75) DA  ERR - Nume declarant"
        D101  „21. nume_declar Nume declarant C(75) DA  ERR - nume declarant necompletat"
        D112  „3b nume_declar Nume declarant C(75) DA  ERR nume_declar necompletat"
        D205  „5. nume_declar Nume declarant C(75) DA  ERR - nume declarant"
        D300  „6. nume_declar Nume declarant C(75) DA  ERR - nume declarant"
        D301  „29. nume_declarant Nume Declarant C(75) DA  ERR- camp necompletat"
        D390  „4 nume_declar Nume declarant C(75) DA  ERR - nume declarant"
        D394  „7. nume_declar Nume declarant C(75) DA  ERR - nume declarant necompletat"

    — si la fel `prenume_declar` si `functie_declar`. Deci harta avea dreptate pe toate opt, iar
    codul fabrica: „ADMINISTRATOR" pentru nume si functie, „-" pentru prenume.

    CE INLOCUIESTE: un avertisment. Declaratia pleca la ANAF in numele cuiva care n-a declarat, iar
    XML-ul arata identic cu unul corect. Decizia lui Costin, 30.08.2026: *„Fabricarea unei valori
    implicite pe un document care pleaca la ANAF e defectul pe care il vanam de la inceput. Ca cele
    7 firme nu mai pot depune e adevarul devenit vizibil, nu un cost."*
    """
    # Cele trei se scriu EXPLICIT, cu numele lor, nu printr-o buclă peste un tuplu: sonda care
    # confruntă harta cu ce oprește codul (`core/scan_camp_blocant.py`) citește `prof.get("X")` cu
    # X literal, iar o buclă i-ar ascunde exact câmpurile pe care garda trebuie să le vadă.
    # *Măsurat: prima formă, cu buclă, făcea sonda să raporteze „nu oprește" despre un cod care
    # oprea — adică fix clasa pe care garda o păzește, produsă de reparația ei.*
    _MESAJ = ("Lipsă %s (obligatoriu la ANAF: structura declarației îl cere, cu mesaj propriu de "
              "eroare). Completează declarantul în Date firmă.")
    prof = prof or {}
    erori = []
    if not str(prof.get("declarant_nume") or "").strip():
        erori.append(_MESAJ % "numele declarantului")
    if not str(prof.get("declarant_prenume") or "").strip():
        erori.append(_MESAJ % "prenumele declarantului")
    if not str(prof.get("declarant_functie") or "").strip():
        erori.append(_MESAJ % "funcția declarantului")
    return erori


#: [lotul 13, deficiența C71.1] câmpurile care există NUMAI pentru bilanț (structura ANAF SC 1225: „bifaMC”, „codPP”, „interes_public”):
#: la o firmă care nu întocmește situații financiare anuale (partidă simplă — Legea 82/1991 art.28 alin.(1), citat în
#: `control_fiscal_api._NEAP_FORMA_SIMPLA["bilant"]`) nu au niciun rost pe ecran. Nr. registrului comerțului și județul rămân (PFA are și
#: el număr de înregistrare și adresă), dar fără „*”.
NUMAI_BILANT = ("mare_contribuabil", "forma_proprietate", "interes_public")


def _decl_aplicabile(decl, neap):
    """Declarațiile din `decl` (OBLIGATORII) pe care forma firmei le poate datora (`neap` = `control_fiscal_api.neaplicabile_forma`)."""
    return [d for d in decl if ("bilant" if d.startswith("Bilanț") else d.lower()) not in neap]


def campuri_forma(tip_firma):
    """PURĂ. [lotul 13, deficiența C71.1, comanda 13.1: „La F4 PFA caseta «Profil incomplet» cere corect doar Banca și IBAN, dar formularul
    marchează cu * câmpuri de SRL «cerute la bilanț» (Nr. registrul comerțului, Mare contribuabil, Forma de proprietate, Entitate de
    interes public) și oferă Regim fiscal micro/profit (D100/D101), care nu privesc un PFA.”] Ce marchează ecranul Date firmă, din
    ACEEAȘI sursă cu „Profil incomplet” (`lipsuri`): {"obligatorii": câmpurile cerute de o declarație pe care forma o poate datora (cu „*”),
    "fara_rost": câmpurile numai-bilanț la o formă care nu întocmește bilanț (nu se arată)}."""
    from core.control_fiscal_api import neaplicabile_forma
    neap = neaplicabile_forma(tip_firma)
    return {"obligatorii": [c for c, decl in OBLIGATORII.items() if _decl_aplicabile(decl, neap)],
            "fara_rost": [c for c in NUMAI_BILANT if "bilant" in neap]}


def lipsuri(profil):
    """PURA: campurile obligatorii necompletate + ce declaratii blocheaza fiecare.
    Intoarce [{camp, declaratii}] - gol daca profilul e complet."""
    from core.control_fiscal_api import neaplicabile_forma
    out = []
    profil = profil or {}
    # [lotul 10, C71] numai declarațiile pe care forma firmei le poate datora: la PFA (partidă simplă) „Mare contribuabil” / „Forma de
    # proprietate” blocau „Bilanț”, iar CAEN / IBAN blocau D101 / D406 — declarații pe care nu le depune (sursa unică a excluderii
    # prin formă, `control_fiscal_api.neaplicabile_forma`)
    neap = neaplicabile_forma(profil.get("tip_firma"))
    for camp, decl in OBLIGATORII.items():
        decl = _decl_aplicabile(decl, neap)
        v = profil.get(camp)
        # [lotul 10, C69] `mare_contribuabil` = Nu (False) e o alegere făcută, nu o lipsă; lipsă e numai nedeclarat (NULL) sau gol
        if v is None or (not isinstance(v, bool) and not str(v).strip()):
            # [lotul 10, C69, decizia Costin „Varianta 1”] firma care a declarat că nu are cont bancar scrie în D406 „Fara cont bancar”
            # (S.BA.2), deci IBAN-ul gol nu mai blochează D406 (D300 / D301 rămân cum erau)
            decl = [d for d in decl if not (camp == "iban" and d == "D406" and profil.get("fara_cont_bancar") is True)]
            if decl:
                out.append({"camp": camp, "declaratii": list(decl)})
    # [lotul 11, deficiența 442] forma juridică și capitalul social: aceeași regulă care REFUZĂ emiterea (`capital_social.lipsa`, chemată
    # de `facturi_api` pe orice emitere), deci panoul spune exact ce oprește factura — nici mai mult (PFA / II / IF, SNC, SCS, ONG nu au
    # capital de menționat: Legea 31/1990 art.74 alin.(3) numește numai SRL, SA și SCA), nici mai puțin. Câmpul = id-ul din Date firmă.
    from core import capital_social as _cs
    for et in _cs.lipsa(profil):
        out.append({"camp": _cs.CAMP_LIPSA[et][len("df-"):], "declaratii": [BLOCHEAZA_EMITEREA]})
    return out


def blocaje(conn, profil):
    """Motive pentru care unele declaratii NU se pot genera desi campurile obligatorii sunt PREZENTE.
    Nu 'lipsa camp' (aia e lipsuri), ci 'prezent-dar-invalid' (CAEN in afara nomenclatorului inchis al
    D112 - Q1) sau 'vector necompletat la platitor' (periodicitate / data inregistrarii TVA - Q8).
    Ecranul foloseste asta ca sa NU pretinda 'toate declaratiile se pot genera' desi ceva le blocheaza.
    Textele 'motiv' sunt AFISATE -> diacritice (nu ASCII de log)."""
    out = []
    caen = str((profil or {}).get("caen") or "").strip()
    if caen:
        from core import d112
        if not d112.caen_in_nomenclator(caen):
            out.append(dict(_af.afirmatie(
                "neconformitate", "d112",
                "CAEN %s nu e în nomenclatorul acceptat de D112 — corectează "
                "CAEN-ul, altfel D112 (dacă ai salariați) e respins de ANAF." % caen,
                unde="codul CAEN al firmei (%s)" % caen, regula="caen_in_afara_nomenclatorului_d112"),
                declaratie="D112"))
    try:
        from core import vector_fiscal_api
        v = vector_fiscal_api.citeste(conn)
    except Exception:
        v = {}
    if v.get("platitor_tva") is True:
        if not str(v.get("tip_decont") or "").strip():
            out.append(dict(_af.afirmatie(
                "neconformitate", "d300",
                "periodicitatea TVA nu e aleasă (apare „—”) — alege lunar sau trimestrial.",
                unde="vectorul fiscal al firmei", regula="periodicitate_tva_nealeasa"),
                declaratie="D300/D394"))
        if not str(v.get("tva_data_inceput") or "").strip():
            out.append(dict(_af.afirmatie(
                "neconformitate", "d300",
                "data înregistrării în scopuri de TVA lipsește — fără "
                "ea, verdictele pe lunile trecute rămân „necunoscut”.",
                unde="vectorul fiscal al firmei", regula="data_inceput_tva_lipsa"),
                declaratie="D300/D394/D406"))
    return out


# [R46] Ce DECIDE ce se datorează, nu ce doar apare pe declarație. Măsurat 26.08.2026: din cele
# 16 câmpuri din `CAMPURI_FISCALE`, 14 sunt citite de generatoarele de declarații — dar aia e un
# PLAFON, nu răspunsul: `telefon`, `adresa`, `judet` ajung în antetul formularului, nu în ce se
# datorează. Costin a numit criteriul: *„vectorul, regimul, CUI-ul. Nu telefonul sau adresa de
# corespondență."* Vectorul și regimul nu sunt în `CAMPURI_FISCALE` — trăiesc pe rutele lor.
CAMPURI_CARE_DECID = ("cui",)

COD_CUI_NEMODIFICABIL = "CUI_NEMODIFICABIL"
MESAJ_CUI_NEMODIFICABIL = ("CUI-ul nu se modifică din Date firmă. Dacă CUI-ul înregistrat e greșit, îl corectează administratorul "
                           "cabinetului, din butonul „Corectează CUI-ul” — operațiune separată, cu avertisment.")
#: [deficiența 272] ce spune avertismentul corecturii, înainte de confirmare
AVERTISMENT_CORECTURA_CUI = ("Corectezi CUI-ul firmei din %s în %s. CUI-ul intră în fiecare declarație și factură de acum înainte; "
                             "declarațiile și facturile emise deja rămân cu CUI-ul vechi (o declarație depusă greșit se corectează "
                             "cu o declarație rectificativă). Folosește corectura numai dacă CUI-ul înregistrat e greșit — o firmă "
                             "nouă (alt CUI) se adaugă ca firmă nouă, nu se corectează.")


#: [459] fără datele ANAF ale CUI-ului nou, ce rămâne de verificat (spus în avertisment și după corectură, nu tăcut)
DE_VERIFICAT_FARA_ANAF = ("Denumirea, adresa, nr. registrului comerțului, codul CAEN, localitatea, județul, înregistrarea în scopuri de TVA, "
                          "TVA la încasare, data înființării și forma juridică rămân cele de acum, scrise pentru CUI-ul vechi — de verificat "
                          "în Date firmă după corectură. Denumirea de la ANAF, starea TVA citită la ANAF și perioadele TVA la încasare aduse "
                          "din ANAF pentru CUI-ul vechi se șterg.")


def _anaf_pentru_corectura(conn, cui_nou, anaf, anaf_eroare):
    """[459] Ce spune corectura despre datele ANAF ale CUI-ului nou: {gasit, schimbari: [{camp, eticheta, acum, anaf}], mesaj}.

    [lotul 11, AT] O AFIRMAȚIE TIPATĂ (`afirmatii.afirmatie`, decizia 21.08.2026), cu felul după ce s-a aflat: ANAF dă datele -> `fapt`
    (despre CUI-ul firmei, temeiul = răspunsul ANAF comparat câmp cu câmp); ANAF nu le are -> `absenta_observatie` (registrul
    contribuabililor); ANAF n-a răspuns (`anaf_eroare`) -> `verificare_rupta` — nu „nu există la ANAF” (ca `uc_regim_tva_incasare`).
    `motiv` = același text ca `mesaj`; `gasit`, `schimbari`, `mesaj` (pe care le citește `date_firma.js`) rămân."""
    from core import afirmatii as _af
    from core import tenant_provisioning as _tp
    from core.unde import Unde as _Unde
    with conn.cursor() as cur:
        cur.execute("SELECT %s FROM firma_profil WHERE id = 1" % ", ".join(c for c, _e, _k in _tp.CAMPURI_ANAF))
        r = cur.fetchone()
    acum = dict(zip([c for c, _e, _k in _tp.CAMPURI_ANAF], list(r.values()) if isinstance(r, dict) else (r or ())))
    if anaf:
        sch = _tp.propunere_anaf(acum, anaf)
        mesaj = ("La ANAF, CUI-ul %s e al firmei „%s”. " % (cui_nou, (anaf.get("denumire") or "").strip() or "—")) + (
            "La confirmare, datele de mai jos se înlocuiesc cu cele de la ANAF:" if sch
            else "Datele din Date firmă coincid cu cele de la ANAF: nu se schimbă nimic în afară de CUI.")
        return _af.afirmatie("fapt", "datele ANAF ale CUI-ului nou", mesaj, unde=_Unde("camp_profil", "CUI", cui_nou),
                             temei_completitudine="răspunsul ANAF pentru CUI-ul %s, comparat câmp cu câmp cu Date firmă" % cui_nou,
                             gasit=True, schimbari=sch, mesaj=mesaj)
    if anaf_eroare:
        mesaj = anaf_eroare + " " + DE_VERIFICAT_FARA_ANAF
        return _af.afirmatie("verificare_rupta", "datele ANAF ale CUI-ului nou", mesaj, eroare=anaf_eroare,
                             gasit=False, schimbari=[], mesaj=mesaj)
    mesaj = ("ANAF nu are date pentru CUI-ul %s (nu apare în registrul contribuabililor)." % cui_nou) + " " + DE_VERIFICAT_FARA_ANAF
    return _af.afirmatie("absenta_observatie", "datele ANAF ale CUI-ului nou", mesaj,
                         surse_consultate="registrul contribuabililor ANAF, pentru CUI-ul %s" % cui_nou,
                         gasit=False, schimbari=[], mesaj=mesaj)


def corecteaza_cui(conn, tenant_id, cui, user_id, confirmat=False, anaf=None, anaf_eroare=None):
    """[deficiența 272] Corectura CUI-ului — operațiunea separată a administratorului (ruta o păzește: `drepturi.ADMIN`). Fără
    `confirmat`, întoarce avertismentul (nimic scris). Cu el: cifra de control, perioadele deschise (CUI-ul decide declarațiile), scrierea
    în AMBELE locuri (`tenant_provisioning.alege_cui`) și jurnalul Date firmă, cu autorul. Nu comite (apelantul deține tranzacția).

    [459, comanda Costin 11.3 pct.5: „la schimbarea CUI-ului rămân datele celui vechi”] `anaf` = datele ANAF ale CUI-ului NOU
    (`tenant_provisioning.date_din_anaf`, cerute de apelant ÎNAINTE de conexiune; None = negăsit / necitit, `anaf_eroare` = de ce n-au
    venit). Avertismentul le arată ca propunere, câmp cu câmp (`anaf`: acum -> ANAF), ca la 444 („se spune și se propune actualizarea”);
    confirmarea le aplică: datele de la ANAF înlocuiesc ce era scris pentru CUI-ul vechi (`tenant_provisioning.inlocuieste_din_anaf`),
    denumirea trece prin `alege_denumirea` („anaf”, cu autorul), iar dacă firma e chiar firma proprie a cabinetului, CUI-ul cabinetului se
    corectează odată cu ea. Fără date ANAF, avertismentul și răspunsul spun ce rămâne de verificat (`DE_VERIFICAT_FARA_ANAF`).
    Verificarea CUI-ului e aceeași ca la crearea firmei (`tenant_provisioning.motiv_cui_firma_invalid`)."""
    from core import cui_forma as _cf   # [lotul 11, decizia 10.3] CUI-ul se păstrează fără „RO” și fără spații
    from core import tenant_provisioning as _tp, repo_firma_profil as _rfp
    _cui = _cf.stocare(cui) or ""
    inainte = _instantaneu(conn)
    _vechi = (inainte.get("cui") or "").strip()
    if not _cui:
        return {"ok": False, "camp": "cui", "mesaj": "Scrie CUI-ul corect."}
    if _cui == (_cf.stocare(_vechi) or ""):
        return {"ok": False, "camp": "cui", "cod": "CUI_NESCHIMBAT", "mesaj": "CUI-ul scris e cel înregistrat deja: nu e nimic de corectat."}
    _motiv = _tp.motiv_cui_firma_invalid(_cui)
    if _motiv:
        return {"ok": False, "camp": "cui", "mesaj": _motiv}
    _anaf = _anaf_pentru_corectura(conn, _cui, anaf, anaf_eroare)
    if not confirmat:
        return {"ok": False, "cod": "CONFIRMARE_CERUTA", "avertisment": AVERTISMENT_CORECTURA_CUI % (_vechi or "—", _cui), "anaf": _anaf}
    _den_anaf = ((anaf or {}).get("denumire") or "").strip()
    _cu_nume = any(s["camp"] == "nume" for s in _anaf["schimbari"]) and bool(_den_anaf)
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name, accounting_firm_id FROM public.tenants WHERE id = %s", (tenant_id,))
        _schema, _cabinet = cur.fetchone()
        # firma proprie a cabinetului: CUI-ul cabinetului e chiar al ei (`uc_auth._dupa_cont_nou` îl scrie din același CUI)
        cur.execute("SELECT id FROM public.accounting_firms WHERE id = %s AND " + _cf.SQL.format(c="cui") + " = %s",
                    (_cabinet, _cf.stocare(_vechi) or ""))
        _cab_propriu = cur.fetchone()
    try:
        _tp.cere_cui_unic(conn, tenant_id, _cui)
        cere_perioade_deschise(conn, "CUI-ul firmei")
        if _cu_nume:   # poarta denumirii ÎNAINTE de orice scriere (aceeași ca la redenumire)
            _tp.cere_nume_unic(conn, _tp.cere_denumire_scriibila(_den_anaf), _cabinet, exclude_id=tenant_id)
    except ValueError as e:
        return {"ok": False, "camp": "cui", "mesaj": str(e)}
    from core import regim_tva_incasare as _rti
    with conn.cursor() as cur:
        _regim_vechi = dict(_rfp.regim_tva_pentru_schimbare(cur) or {}, tva_incasare_perioade=_rti.text_perioade(_rti.perioade(cur)))
    if _cab_propriu:
        from core import auth_api as _aa, chei_unice as _chei
        try:
            _aa.actualizeaza_cabinet(conn, _cabinet, cui=_cui)
        except _chei.CheieDublata as e:
            return {"ok": False, "camp": "cui", "mesaj": str(e)}
    _tp.alege_cui(conn, tenant_id, _cui)
    _tp.inlocuieste_din_anaf(conn, _schema, anaf)
    if _cu_nume:
        _tp.alege_denumirea(conn, tenant_id, "anaf", user_id)
    with conn.cursor() as cur:
        # indicatorul „se aplică azi” urmează perioadele, când există (`regim_tva_incasare.aplica_la`); jurnalul regimului, o dată
        if _rti.perioade(cur):
            from core.common import azi_ro as _azi   # ziua decide verdictul „se aplică azi”: ziua din București
            cur.execute("UPDATE firma_profil SET tva_la_incasare = %s WHERE id = 1", (_rti.aplica_la(cur, _azi()),))
        _rn = _rfp.regim_tva_pentru_schimbare(cur) or {}
        _rfp.jurnalizeaza_regim_tva(cur, _regim_vechi, {"platitor_tva": _rn.get("platitor_tva"), "tva_la_incasare": _rn.get(
            "tva_la_incasare"), "tva_incasare_perioade": _rti.text_perioade(_rti.perioade(cur))}, user_id)
        _rfp.jurnalizeaza_campuri(cur, inainte, _instantaneu(conn), user_id)
    return {"ok": True, "cui": _cui, "anaf": _anaf}


def cere_perioade_deschise(conn, ce):
    """[R46, 26.08.2026] Un câmp care decide ce se datorează nu se schimbă peste o perioadă închisă.

    Decizia lui Costin, cu motivul: *„o schimbare de date fiscale ale firmei într-o perioadă închisă
    nu e o corecție, e o rescriere a trecutului. Iar datele acelea decid ce declarații s-au datorat
    pentru perioada aceea — declarații care s-au depus deja."*

    De ce REFUZ și nu trecere consemnată, deși R58 a ales invers pentru redeschidere: *„trecerea
    consemnată e potrivită acolo unde actul e legitim și rar — redeschiderea unei perioade. Acolo
    omul ia o decizie despre perioadă. Aici ar lua o decizie despre trecut fără să redeschidă nimic,
    iar urma ar rămâne singura care știe."* Calea corectă rămâne deschisă și e mai bună: redeschide,
    schimbă, închide — trei acte consemnate în loc de unul tăcut."""
    with conn.cursor() as cur:
        cur.execute("SELECT an, luna FROM perioade_blocate ORDER BY an, luna LIMIT 1")
        r = cur.fetchone()
    if r:
        raise ValueError(MESAJ_PESTE_PERIOADA_INCHISA
                         % {"ce": ce, "an": r[0], "luna": int(r[1])})


def cere_administrator(conn, document):
    """[R66 (c), 26.08.2026] Un document care TIPARESTE numele administratorului nu se produce fara el.

    Pana azi, `patron_nume` n-avea nicio cale de scriere, iar adeverinta si contractul ieseau cu un
    gol in locul lui — interdictia 20 in forma ei de zi cu zi: un artefact care se produce si nu
    spune nimic. Refuzul singur n-ar fi fost onest cat timp omul nu putea completa campul; de aceea
    intra IMPREUNA cu el, in aceeasi tura (*„coloana si calea ei intra impreuna"*).

    Refuzul NUMESTE documentul si spune UNDE se completeaza — altfel muta munca fara s-o indrume."""
    with conn.cursor() as cur:
        cur.execute("SELECT patron_nume FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not str((r[0] if r else None) or "").strip():
        raise ValueError(MESAJ_FARA_ADMINISTRATOR % document)


def _metode_stoc():
    """Metodele suportate + cele nesuportate încă (afișate, refuzate la salvare — decizia Costin 07.10, pct.1)."""
    from core.metoda_stoc import ETICHETE, NESUPORTATE
    return {**ETICHETE, **NESUPORTATE}


def _activitati_amef():
    from core.activitati_amef import ACTIVITATI
    return ACTIVITATI


def _forme_proprietate():
    from core.bilant import FORME_PROPRIETATE
    return FORME_PROPRIETATE


def citeste_date(conn):
    """Profilul complet + lipsurile + optiunile de cont venit, pentru ecranul Date firma."""
    import psycopg2.extras as _E
    coloane = (list(CAMPURI_FISCALE) + ["cont_venit_implicit"] + list(CAMPURI_CAPITAL) + ["tip_firma"]
               + list(CAMPURI_AMEF) + ["metoda_stoc", "serie_chitanta", "data_infiintare"] + list(CAMPURI_C69)  # [F182]; [lot 19 d12]; [D394 Î2]; [06.10.2026 §6.3]; [decizii 07.10 pct.5]
               + list(CAMPURI_BILANT))   # [lotul 11, decizia 10.3] interesul public (bilanțul)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT %s FROM firma_profil LIMIT 1" % ", ".join(coloane))
        r = cur.fetchone()
    prof = dict(r) if r else {}
    if not str(prof.get("cont_venit_implicit") or "").strip():
        prof["cont_venit_implicit"] = CONT_VENIT_IMPLICIT_DEFAULT  # coerent cu COALESCE-ul de la emitere
    for k in ("capital_subscris", "capital_varsat"):
        if prof.get(k) is not None:
            prof[k] = str(prof[k])
    if prof.get("data_infiintare") is not None:
        prof["data_infiintare"] = prof["data_infiintare"].isoformat()
    # [lotul 11, decizia Costin 10.3] „«RO» apare doar la afișare, după starea de plătitor de TVA” (CF art.318 alin.(1)): CUI-ul arătat
    from core import cui_forma as _cf
    with conn.cursor() as cur:
        cur.execute("SELECT platitor_tva FROM firma_profil LIMIT 1")
        _pt = cur.fetchone()
    prof["cui_afisat"] = _cf.afisare(prof.get("cui"), _pt[0] if _pt else None)
    from core import capital_social as _cs
    from core import luna_preluare as _lp, repo_firma_profil as _rfp
    with conn.cursor() as cur:   # [08.10 §6 pct.4] luna preluării: salvată / propusă (dedusă, plafonată la prima notă) / efectivă
        prof["luna_preluare"] = _lp.stare(_rfp.fapte_preluare(cur))
    return {"profil": prof, "lipsuri": lipsuri(prof), "conturi_venit": CONTURI_VENIT,
            **campuri_forma(prof.get("tip_firma")),   # [lotul 13, C71.1] „*” și câmpurile fără rost, după forma firmei
            "forme_juridice": [[k, v[0]] for k, v in _cs.FORME.items()],
            "activitati_amef": [[k, v] for k, v in _activitati_amef().items()],
            "forme_proprietate": [[k, v] for k, v in _forme_proprietate().items()],   # [lotul 10, C69] nomenclatorul ANAF (bilanț codPP)
            "metode_stoc": [[k, v] for k, v in _metode_stoc().items()],
            "blocaje": blocaje(conn, prof)}


def _refuz_formular(er, coduri):
    """[lotul 11, deficiența 440] Refuzul Date firmă cu TOATE erorile adunate (`core.erori.ErorileFormularului`): `camp` / `cod` = ale
    primei (apelanții care citeau un singur câmp), `mesaj` = toate, rând cu rând, `erori_campuri` = fiecare cu câmpul ei."""
    d = er.detaliu()
    prima = (d["erori_campuri"] or [{"camp": None}])[0]["camp"]
    r = {"ok": False, "camp": prima, "mesaj": d["mesaj"], "erori_campuri": d["erori_campuri"]}
    cod = next((coduri[c["camp"]] for c in d["erori_campuri"] if c["camp"] in coduri), None)
    if cod:
        r["cod"] = cod
    return r


def salveaza_date(conn, date, tenant_id=None, user_id=None):
    """Salveaza datele fiscale. [lotul 10, deficiența 427] Un câmp obligatoriu gol NU refuză salvarea: ce s-a completat se
    salvează, iar lipsa rămâne în `lipsuri` (răspunsul o întoarce — ecranul o spune după salvare) și blochează numai declarațiile
    care o cer (`OBLIGATORII` -> generatoarele). Se refuză numai o valoare INVALIDĂ (CUI, cont, serie, dată …).
    [06.10.2026 §6.4] Orice câmp schimbat se jurnalizează (`firma_profil_jurnal`: cine, când, vechi -> nou) — de aceea
    salvarea cere utilizatorul.
    [lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă
    câmp”] Refuzurile care țin de STAREA evidenței (autorul lipsă, CUI-ul înregistrat schimbat, perioada închisă) vin întâi, singure;
    apoi fiecare valoare invalidă se ADAUGĂ (`ErorileFormularului`) și se refuză o dată, cu toate (`erori_campuri`, `camp` = numele
    din cerere — ecranul pune prefixul „df-”). Nimic nu se scrie până nu trec toate."""
    from core.erori import ErorileFormularului as _Erori
    if date and user_id is None:
        return {"ok": False, "camp": None,
                "mesaj": "Date firmă se salvează cu utilizatorul care le schimbă — orice schimbare rămâne în jurnal; lipsește."}
    inainte = _instantaneu(conn)
    curat = {k: (str(date.get(k)).strip() if date.get(k) is not None else None)
             for k in CAMPURI_FISCALE if k in (date or {})}
    # ── STAREA evidenței (refuzuri unice, înaintea câmpurilor) ──────────────────────────────────────────────────────────────
    # [R46] Doar câmpurile care DECID. Un telefon corectat pe o firmă cu ianuarie închis trebuie
    # să treacă mai departe — altfel poarta ar bloca munca de zi cu zi ca să apere trecutul.
    # [05.10.2026, găsit la proba pct.2] poarta se aplică la SCHIMBAREA unui câmp care decide, nu la prezența lui: formularul
    # trimite mereu CUI-ul, deci pe o firmă cu o lună închisă Date firmă nu se mai putea salva deloc — iar refuzul ieșea 500.
    # [deficiența 272, comanda Costin 16.10.2026, verbatim în DECIZII] „CUI-ul nu se modifică din acest ecran, de niciun rol; o corectură
    # reală de CUI e o operațiune separată, a administratorului, cu avertisment.” Formularul trimite mereu CUI-ul: același trece (nu se
    # rescrie); altul se refuză (`corecteaza_cui` e operațiunea separată). Numai o firmă FĂRĂ CUI îl primește de aici (completare).
    # [lotul 11, decizia Costin 10.3] „CUI-ul se păstrează fără «RO» și fără spații”: forma păstrată (`cui_forma.stocare`) — „RO 123” și
    # „123” sunt același CUI (nu e o schimbare refuzată), iar cel scris se păstrează fără prefix
    from core import cui_forma as _cf
    if "cui" in curat:
        curat["cui"] = _cf.stocare(curat["cui"])
    _cui_vechi = (inainte.get("cui") or "").strip()
    if "cui" in curat and _cui_vechi:
        if (curat["cui"] or "") != (_cf.stocare(_cui_vechi) or ""):
            return {"ok": False, "camp": "cui", "cod": COD_CUI_NEMODIFICABIL, "mesaj": MESAJ_CUI_NEMODIFICABIL}
        curat.pop("cui")
    with conn.cursor() as _cur:
        _cur.execute("SELECT %s FROM firma_profil WHERE id = 1" % ", ".join(CAMPURI_CARE_DECID))
        _act = _cur.fetchone()
    _act = dict(zip(CAMPURI_CARE_DECID, _act)) if _act else {}
    decid = sorted(c for c in set(curat) & set(CAMPURI_CARE_DECID)
                   if str(curat[c] or "").strip().upper() != str(_act.get(c) or "").strip().upper())
    if decid:
        try:
            cere_perioade_deschise(conn, "CUI-ul firmei" if decid == ["cui"] else ", ".join(decid))
        except ValueError as e:
            return {"ok": False, "camp": decid[0], "mesaj": str(e)}
    # ── VALORILE scrise de om: toate se verifică, fiecare eroare se adaugă ───────────────────────────────────────────────────
    er = _Erori("Datele firmei nu s-au salvat")
    coduri = {}
    # [lot 19 d12] forma juridică + capitalul (L31/1990 art.74 alin.(3)): validate și scrise separat — numere, nu text
    cap = {k: date.get(k) for k in CAMPURI_CAPITAL if k in (date or {})}
    if cap:
        from core import capital_social as _cs
        for _c, _m in _cs.valideaza(cap):
            er.camp(_c, _m)
    _val = {k: (None if cap[k] in (None, "") else
                (str(cap[k]).strip().upper() if k == "forma_juridica" else _cs._suma(cap[k]))) for k in cap} if cap else {}
    # [06.10.2026 §6.3] metoda de stoc: explicită, fără implicit; odată declarată nu se șterge, se schimbă (și rămâne în jurnal)
    if "metoda_stoc" in (date or {}):
        from core import metoda_stoc as _ms
        _m = str(date.get("metoda_stoc") or "").strip() or None
        if _m is None:
            if inainte.get("metoda_stoc"):
                er.camp("metoda_stoc", "Metoda de stoc nu se șterge după ce a fost declarată — se schimbă cu cealaltă, iar "
                                       "schimbarea rămâne în jurnal.")
        elif _m in _ms.NESUPORTATE:   # [decizia Costin 07.10, pct.1] refuz clar, „nesuportat încă”
            er.camp("metoda_stoc", _ms.MESAJ_NESUPORTATA % _ms.NESUPORTATE[_m])
            coduri["metoda_stoc"] = _ms.COD_NESUPORTATA
        elif _m not in (_ms.GV, _ms.CV):
            er.camp("metoda_stoc", "Metoda de stoc e global-valorică sau cantitativ-valorică.")
        else:
            _val["metoda_stoc"] = _m
    # [decizia Costin 07.10, pct.5] seria chitanțelor: „cerută la prima folosire, ca seria facturii; fără «CH» din oficiu”.
    # OMFP 2634/2015 anexa 1 pct.24: seria e „stabilit(ă) de entitate”. Odată stabilită nu se șterge (numerotarea continuă pe ea).
    if "serie_chitanta" in (date or {}):
        _sc = str(date.get("serie_chitanta") or "").strip().upper() or None
        if _sc is None:
            if inainte.get("serie_chitanta"):
                er.camp("serie_chitanta", "Seria chitanțelor nu se șterge după ce a fost stabilită — se schimbă, iar schimbarea "
                                          "rămâne în jurnal.")
        elif not _re.fullmatch(r"[A-Z0-9]{1,10}", _sc):
            er.camp("serie_chitanta", "Seria chitanțelor: litere și cifre, cel mult 10 (ex. CH, CA).")
        else:
            _val["serie_chitanta"] = _sc
    # [08.10.2026, decizia Costin §6 pct.4] „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere, dar niciodată
    # după luna primei note.” Gol = propunerea (`luna_preluare.efectiva`).
    if "luna_preluare" in (date or {}):
        from core import luna_preluare as _lp, repo_firma_profil as _rfp
        try:
            _l = _lp.din_text(date.get("luna_preluare"))
        except ValueError as e:
            er.camp("luna_preluare", str(e))
        else:
            with conn.cursor() as _cur:
                _erl = _lp.eroare(_l, _rfp.fapte_preluare(_cur)["prima_nota"])
            if _erl:
                er.camp("luna_preluare", _erl)
            else:
                _val["luna_preluare"] = _l
    # [deficiența 229, comanda Costin 12.10.2026] data înființării: de la ea curge primul exercițiu financiar (Legea 82/1991 art.27
    # alin.(8)), în care coloana „An precedent” a bilanțului rămâne goală. Gol = necunoscută; o dată din viitor nu e o înființare.
    if "data_infiintare" in (date or {}):
        import datetime as _dt
        _di = str(date.get("data_infiintare") or "").strip() or None
        _di_ok = True
        if _di is not None:
            try:
                _di = _dt.date.fromisoformat(_di)
            except ValueError:
                er.camp("data_infiintare", "Data înființării: o dată (zi, lună, an).")
                _di_ok = False
            else:
                if _di > _dt.date.today():
                    er.camp("data_infiintare", "Data înființării nu poate fi în viitor.")
                    _di_ok = False
        if _di_ok:
            _val["data_infiintare"] = _di
    # [D394 Î2] bifa „activitate exceptată de la AMEF” + litera din OUG 28/1999 art.2 (cerută când bifa e da)
    if any(k in (date or {}) for k in CAMPURI_AMEF):
        from core.uc_comun import bifa as _bifa
        try:
            exc = _bifa(date, "activitate_exceptata_amef", None)   # [lotul 07.10 B] gol = neales (NULL), nu „Nu”
        except ValueError as e:
            er.camp("activitate_exceptata_amef", str(e))
        else:
            lit = str(date.get("activitate_amef") or "").strip().lower() or None
            if exc and lit not in _activitati_amef():
                er.camp("activitate_amef", "Alege activitatea exceptată de la casa de marcat (OUG 28/1999 art.2) — fără ea, "
                                           "încasările fără bon nu au temei.")
            _val["activitate_exceptata_amef"] = exc
            _val["activitate_amef"] = lit if exc else None
    # [lotul 10, C69] mare contribuabil (Da / Nu; gol = nedeclarat, NULL — bilanțul îl cere la generare, DS cap.17 „cerut la prima
    # folosire”), forma de proprietate (un cod din nomenclatorul ANAF, altfel refuz), „nu are cont bancar” (Da / Nu, coloana NOT NULL)
    if any(k in (date or {}) for k in CAMPURI_C69):
        from core.uc_comun import bifa as _bifa
        for k, implicit in (("mare_contribuabil", None), ("fara_cont_bancar", False)):
            if k in (date or {}):
                try:
                    _val[k] = _bifa(date, k, implicit)
                except ValueError as e:
                    er.camp(k, str(e))
        if "forma_proprietate" in (date or {}):
            _fp_cod = str(date.get("forma_proprietate") or "").strip() or None
            if _fp_cod is not None and _fp_cod not in _forme_proprietate():
                er.camp("forma_proprietate",
                        "Forma de proprietate: alege una din lista ANAF (codul din nomenclatorul formelor de proprietate).")
            else:
                _val["forma_proprietate"] = _fp_cod
    # [lotul 11, decizia Costin 10.3] entitate de interes public (Da / Nu; gol = nedeclarat, NULL — bilanțul o cere: „15. interes_public
    # … DA interes_public=(0,1)”, structura SC 1225)
    if "interes_public" in (date or {}):
        from core.uc_comun import bifa as _bifa
        try:
            _val["interes_public"] = _bifa(date, "interes_public", None)
        except ValueError as e:
            er.camp("interes_public", str(e))
    # [lotul 10, deficiența 427] „Ce s-a completat se salvează; lipsurile rămân în «Profil incomplet» și blochează doar declarațiile
    # afectate, cum spune deja ecranul.” Un câmp obligatoriu GOL nu mai refuză salvarea: rămâne în `lipsuri()` (panoul și mesajul de
    # după salvare), iar fiecare generator îl oprește pe declarația lui (`core/test_camp_blocant.py` păzește perechile OBLIGATORII).
    # Refuzul întreg (aici) era a doua poartă peste aceeași lipsă și oprea și restul formularului (vectorul fiscal, capitalul …).
    # [lotul 6, 04.09.2026] CUI-ul firmei: cifra de control, si SIMETRIA celor doua locuri.
    # Probat: `{"cui": "RO1234567890"}` intra fara nicio verificare, si numai in `firma_profil` —
    # `public.tenants.cui` ramanea cel vechi. Validatorul exista deja in aplicatie, pentru
    # PARTENERI (`solduri_parteneri_api.valideaza_cui`); firma proprie n-avea niciunul.
    _cui_nou = (curat.get("cui") or "").strip() if "cui" in curat else ""
    if _cui_nou:
        from core import tenant_provisioning as _tpc   # [459] aceeași verificare ca la crearea firmei
        _m_cui = _tpc.motiv_cui_firma_invalid(_cui_nou)
        if _m_cui:
            er.camp("cui", _m_cui)
        elif tenant_id is None:
            er.camp("cui", "CUI-ul se schimbă prin calea care atinge amândouă locurile în "
                           "care e scris; cererea asta n-a spus despre ce firmă e vorba.")
    # [F182] cont venit implicit: optional, dar daca vine trebuie sa fie cont de venit (clasa 70) valid.
    # Refuz un cont invalid la sursa — altfel emiterea ar scrie o nota contabila pe un cont gresit.
    if "cont_venit_implicit" in (date or {}):
        cv = str(date.get("cont_venit_implicit") or "").strip()
        if not cont_venit_valid(cv):
            er.camp("cont_venit_implicit", "Contul de venit implicit trebuie să fie un cont din clasa 70 (cifra de afaceri).")
        else:
            curat["cont_venit_implicit"] = cv
    # [R81/O3, 28.08.2026] DA, ecranul „Date firmă" are o cale de editare directă a denumirii
    # fiscale: `CAMPURI[0]` din `date_firma.js` e chiar `nume`, iar el ajungea aici. Sub simetrie,
    # denumirea nu se mai scrie de aici, ci prin scriitorul unic din `tenant_provisioning` — care
    # atinge amândouă locurile, în aceeași tranzacție, și trece prin poarta de unicitate.
    #
    # `tenant_id` e obligatoriu **numai** când se schimbă denumirea: restul câmpurilor fiscale n-au
    # nimic de-a face cu `public`, iar a cere identificatorul pentru un telefon corectat ar lega
    # inutil două straturi.
    nume_nou = curat.pop("nume", None)
    if nume_nou is not None and not tenant_id:
        er.camp("nume", "Denumirea firmei nu se poate salva fără identificatorul firmei.")
    if er:
        return _refuz_formular(er, coduri)
    # ── SCRIEREA: numai după ce au trecut toate valorile ─────────────────────────────────────────────────────────────────────
    if _cui_nou:
        from core import tenant_provisioning as _tp
        _tp.alege_cui(conn, tenant_id, _cui_nou)
        curat.pop("cui")     # scris deja, simetric — nu se mai scrie o data, doar aici
    if nume_nou is not None:
        from core import tenant_provisioning as _tp
        try:
            _tp.scrie_denumirea(conn, tenant_id, nume_nou)
        except ValueError as e:
            conn.rollback()
            return {"ok": False, "camp": "nume", "mesaj": str(e)}
    if _val:   # scris DUPĂ toate validările: un refuz mai jos/mai sus nu lasă capitalul scris pe jumătate
        with conn.cursor() as _cur:
            _cur.execute("UPDATE firma_profil SET %s WHERE id = 1" % ", ".join("%s = %%s" % k for k in _val),
                         list(_val.values()))
    if curat:
        seturi = ", ".join("%s = %%s" % k for k in curat)
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET " + seturi + " WHERE id = 1",
                        tuple(curat.values()))
    # [06.10.2026 §6.4] jurnalul: diferența dintre instantaneul de dinainte și cel de după, pe TOATE drumurile de scriere de mai
    # sus (fiscale, capital, AMEF, metoda de stoc, CUI-ul și denumirea prin provisioning) — niciunul nu poate scăpa
    from core import repo_firma_profil as _rfp
    with conn.cursor() as cur:
        _rfp.jurnalizeaza_campuri(cur, inainte, _instantaneu(conn), user_id)
    return dict({"ok": True}, **citeste_date(conn))


ETICHETE = {
    "nume": "Denumirea firmei", "cui": "CUI", "reg_com": "Nr. registrul comertului",
    "caen": "Cod CAEN", "adresa": "Adresa", "oras": "Localitatea", "judet": "Judetul",
    "cod_postal": "Cod postal", "banca": "Banca", "iban": "IBAN",
    "telefon": "Telefon", "email": "E-mail",
    "declarant_nume": "Nume declarant", "declarant_prenume": "Prenume declarant",
    "declarant_functie": "Functia declarantului",
    "mare_contribuabil": "Mare contribuabil", "forma_proprietate": "Forma de proprietate",   # [lotul 10, C69]
    "fara_cont_bancar": "Nu are cont bancar",
    "interes_public": "Entitate de interes public",   # [lotul 11, decizia 10.3]
    # [lotul 11, deficiența 442] capitalul social (Legea 31/1990 art.74 alin.(3)) — în „Profil incomplet” cu „blochează emiterea facturilor”
    "forma_juridica": "Forma juridica", "capital_subscris": "Capital social subscris", "capital_varsat": "Capital social varsat",
}


# ============================================================
#  helper PUR — validare culoare hex
# ============================================================
def _culoare_valida(c):
    """Accepta '#rgb' sau '#rrggbb' (hex)."""
    if not c or not c.startswith("#"):
        return False
    corp = c[1:]
    if len(corp) not in (3, 6):
        return False
    try:
        int(corp, 16)
        return True
    except ValueError:
        return False
