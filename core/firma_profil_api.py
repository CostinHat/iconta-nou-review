"""
core/firma_profil_api.py — profilul firmei din schema unui tenant.
Ruleaza pe conexiunea deja pozitionata pe schema tenantului (get_conn(schema)).
Folosit de ecranul "Model factura": datele firmei (pt preview) + personalizare
(font, culoare, logo). Logo = string base64 (data URI), stocat in coloana logo (text).
"""
from __future__ import annotations

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
CAMPURI_FISCALE = ("nume", "cui", "reg_com", "caen", "adresa", "oras", "judet",
                   "cod_postal", "banca", "iban", "telefon", "email",
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
}


def lipsuri(profil):
    """PURA: campurile obligatorii necompletate + ce declaratii blocheaza fiecare.
    Intoarce [{camp, declaratii}] - gol daca profilul e complet."""
    out = []
    for camp, decl in OBLIGATORII.items():
        if not str((profil or {}).get(camp) or "").strip():
            out.append({"camp": camp, "declaratii": list(decl)})
    return out


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
    return {"profil": prof, "lipsuri": lipsuri(prof), "conturi_venit": CONTURI_VENIT}


def salveaza_date(conn, date):
    """Salveaza datele fiscale. Refuza daca un camp obligatoriu ramane gol:
    fara ele declaratiile nu se pot depune, iar utilizatorul ar afla abia cand
    ANAF le respinge, cu mesaj criptic (DS cap.6: validari preventive cu mesaj
    explicativ, nu doar refuz)."""
    curat = {k: (str(date.get(k)).strip() if date.get(k) is not None else None)
             for k in CAMPURI_FISCALE if k in (date or {})}
    for camp, decl in OBLIGATORII.items():
        if camp in curat and not curat[camp]:
            return {"ok": False, "camp": camp,
                    "mesaj": "%s e obligatoriu — fara el nu se pot depune: %s."
                             % (ETICHETE.get(camp, camp), ", ".join(decl))}
    # [F182] cont venit implicit: optional, dar daca vine trebuie sa fie cont de venit (clasa 70) valid.
    # Refuz un cont invalid la sursa — altfel emiterea ar scrie o nota contabila pe un cont gresit.
    if "cont_venit_implicit" in (date or {}):
        cv = str(date.get("cont_venit_implicit") or "").strip()
        if not cont_venit_valid(cv):
            return {"ok": False, "camp": "cont_venit_implicit",
                    "mesaj": "Contul de venit implicit trebuie sa fie un cont din clasa 70 (cifra de afaceri)."}
        curat["cont_venit_implicit"] = cv
    if not curat:
        return {"ok": True, "profil": citeste_date(conn)["profil"]}
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
