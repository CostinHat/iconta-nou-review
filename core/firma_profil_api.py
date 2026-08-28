"""
core/firma_profil_api.py — profilul firmei din schema unui tenant.
Ruleaza pe conexiunea deja pozitionata pe schema tenantului (get_conn(schema)).
Folosit de ecranul "Model factura": datele firmei (pt preview) + personalizare
(font, culoare, logo). Logo = string base64 (data URI), stocat in coloana logo (text).
"""
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
import re as _re
from core import plan_omfp as _plan

CONTURI_VENIT = {c: _plan.PLAN_OMFP[c] for c in sorted(_plan.PLAN_OMFP)
                 if _re.fullmatch(r"70[0-9]", c)}
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
            "font_factura, culoare_factura, serie_factura, urmator_numar_factura "
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
        conn.commit()

    return {"ok": True, "profil": citeste_profil(conn)}

# ============================================================
#  DATE FIRMA — campurile cerute de ANAF in declaratii
# ============================================================
# Sursa: validatoarele din core/dXXX.py (functiile valideaza()), care ridica
# "LIPSA <camp>" cand declaratia nu se poate genera. Dovedit 15.07.2026 pe
# validatorul oficial ANAF. Fiecare camp obligatoriu are asterisc in interfata
# (DS cap.6) si blocheaza salvarea daca lipseste.
# [R66, 26.08.2026] `patron_nume` a intrat aici fiindca avea drum de CITIRE si niciun drum de
# SCRIERE: il citesc `adeverinta`, `contracte_api` si `pachete_api` — deci se TIPARESTE pe
# documente care ajung la oameni — iar nimic din aplicatie nu-l scria. A treia coloana din clasa
# asta gasita in aceeasi zi, si singura care nu se putea scoate: primele doua aveau inlocuitor,
# asta lasa un gol pe hartie. Decizia lui Costin: *„numele administratorului e un fapt al firmei,
# ca denumirea si CUI-ul. Nu se derivă din nimic — cine tine evidenta nu e neaparat cine semneaza."*
CAMPURI_FISCALE = ("nume", "cui", "reg_com", "caen", "adresa", "oras", "judet",
                   "cod_postal", "banca", "iban", "telefon", "email", "patron_nume",
                   "declarant_nume", "declarant_prenume", "declarant_functie")

# camp -> declaratiile care il cer OBLIGATORIU (pentru mesajul din interfata)
OBLIGATORII = {
    "nume": ("D100", "D101", "D205", "D301", "D390", "D394", "D406"),
    "cui": ("D100", "D101", "D205", "D300", "D301", "D390", "D394", "D406"),
    "caen": ("D101", "D300", "D394"),
    "adresa": ("D100", "D205", "D394"),
    "banca": ("D300", "D301"),
    "iban": ("D300", "D301"),
    "telefon": ("D394",),
    "reg_com": ("Bilant S1005",),
    # [declarant_oblig 17.08.2026] nume+functia declarantului: DUK respinge campul gol al declarantului
    # (nume_declar/functie_declar) -> se cer EXPLICIT (ca regim_fiscal), nu se fabrica "ADMINISTRATOR" tacit.
    "declarant_nume": ("D100", "D101", "D112", "D205", "D300", "D301", "D390", "D394", "Bilant"),
    "declarant_functie": ("D100", "D101", "D112", "D205", "D300", "D301", "D390", "D394", "Bilant"),
}


def lipsuri(profil):
    """PURA: campurile obligatorii necompletate + ce declaratii blocheaza fiecare.
    Intoarce [{camp, declaratii}] - gol daca profilul e complet."""
    out = []
    for camp, decl in OBLIGATORII.items():
        if not str((profil or {}).get(camp) or "").strip():
            out.append({"camp": camp, "declaratii": list(decl)})
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


def citeste_date(conn):
    """Profilul complet + lipsurile + optiunile de cont venit, pentru ecranul Date firma."""
    import psycopg2.extras as _E
    coloane = list(CAMPURI_FISCALE) + ["cont_venit_implicit"]  # [F182] preferinta contabila, nu camp fiscal obligatoriu
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT %s FROM firma_profil LIMIT 1" % ", ".join(coloane))
        r = cur.fetchone()
    prof = dict(r) if r else {}
    if not str(prof.get("cont_venit_implicit") or "").strip():
        prof["cont_venit_implicit"] = CONT_VENIT_IMPLICIT_DEFAULT  # coerent cu COALESCE-ul de la emitere
    return {"profil": prof, "lipsuri": lipsuri(prof), "conturi_venit": CONTURI_VENIT,
            "blocaje": blocaje(conn, prof)}


def salveaza_date(conn, date, tenant_id=None):
    """Salveaza datele fiscale. Refuza daca un camp obligatoriu ramane gol:
    fara ele declaratiile nu se pot depune, iar utilizatorul ar afla abia cand
    ANAF le respinge, cu mesaj criptic (DS cap.6: validari preventive cu mesaj
    explicativ, nu doar refuz)."""
    curat = {k: (str(date.get(k)).strip() if date.get(k) is not None else None)
             for k in CAMPURI_FISCALE if k in (date or {})}
    # [R46] Doar câmpurile care DECID. Un telefon corectat pe o firmă cu ianuarie închis trebuie
    # să treacă mai departe — altfel poarta ar bloca munca de zi cu zi ca să apere trecutul.
    decid = sorted(set(curat) & set(CAMPURI_CARE_DECID))
    if decid:
        cere_perioade_deschise(conn, "CUI-ul firmei" if decid == ["cui"] else ", ".join(decid))
    for camp, decl in OBLIGATORII.items():
        if camp in curat and not curat[camp]:
            return {"ok": False, "camp": camp,
                    "mesaj": "%s e obligatoriu — fără el nu se pot depune: %s."
                             % (ETICHETE.get(camp, camp), ", ".join(decl))}
    # [F182] cont venit implicit: optional, dar daca vine trebuie sa fie cont de venit (clasa 70) valid.
    # Refuz un cont invalid la sursa — altfel emiterea ar scrie o nota contabila pe un cont gresit.
    if "cont_venit_implicit" in (date or {}):
        cv = str(date.get("cont_venit_implicit") or "").strip()
        if not cont_venit_valid(cv):
            return {"ok": False, "camp": "cont_venit_implicit",
                    "mesaj": "Contul de venit implicit trebuie să fie un cont din clasa 70 (cifra de afaceri)."}
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
    if nume_nou is not None:
        if not tenant_id:
            return {"ok": False, "camp": "nume",
                    "mesaj": "Denumirea firmei nu se poate salva fără identificatorul firmei."}
        from core import tenant_provisioning as _tp
        try:
            _tp.scrie_denumirea(conn, tenant_id, nume_nou)
        except ValueError as e:
            conn.rollback()
            return {"ok": False, "camp": "nume", "mesaj": str(e)}
    if not curat:
        conn.commit()
        return dict({"ok": True}, **citeste_date(conn))
    seturi = ", ".join("%s = %%s" % k for k in curat)
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET " + seturi + " WHERE id = 1",
                    tuple(curat.values()))
    conn.commit()
    return dict({"ok": True}, **citeste_date(conn))


ETICHETE = {
    "nume": "Denumirea firmei", "cui": "CUI", "reg_com": "Nr. registrul comertului",
    "caen": "Cod CAEN", "adresa": "Adresa", "oras": "Localitatea", "judet": "Judetul",
    "cod_postal": "Cod postal", "banca": "Banca", "iban": "IBAN",
    "telefon": "Telefon", "email": "E-mail",
    "declarant_nume": "Nume declarant", "declarant_prenume": "Prenume declarant",
    "declarant_functie": "Functia declarantului",
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
