# -*- coding: utf-8 -*-
"""GARD [R83/JJ2, 28.08.2026]: reactivarea e posibilă, iar excepția rămâne LOCALĂ.

DE UNDE VINE. `POST /tenants/{id}/activare` se apăra cu `auth_api.schema_tenant`, care cere
`activ = true` pe **toate trei** ramurile de rol. Pentru o firmă dezactivată poarta întorcea `None`
→ **404**, inclusiv când actul cerut era chiar **reactivarea**. Deci o firmă dezactivată **nu se
putea reactiva niciodată prin ecran**, iar două confirmări îi spuneau omului exact să încerce.

DECIZIA lui Costin, varianta **(a)**: verificare proprie **pe rută**, restul rutelor neatinse, nicio
semnătură comună schimbată.

CE FACE IMPOSIBIL:
  1. întoarcerea la poarta comună pe ruta de activare — adică defectul, reintrodus tăcut;
  2. **răspândirea excepției**: `_acces_pentru_activare` are voie să fie chemată dintr-un
     **singur** loc. A doua chemare ar face-o o poartă paralelă, adică exact varianta (b) pe furiș;
  3. slăbirea porții COMUNE: `schema_tenant` trebuie să ceară în continuare `activ` pe toate trei
     ramurile — altfel toate celelalte 154 de rute ar căpăta acces la firme inactive **ca efect
     secundar**, ceea ce decizia (a) refuză explicit;
  4. pierderea regulii de rol în excepție: superadmin doar pe firme fără cabinet, restul doar pe
     cabinetul lor.

CUM SE SCRIU ASERȚIUNILE AICI: pe **numărători** de noduri, nu pe `"nume" in listă`. Un `in` pe
un iterabil trece și când iterabilul e **gol** — adică și când funcția căutată a dispărut cu totul,
nu doar apelul ei. `.count(...) == 1` spune ce trebuie spus: **o dată**, nici zero, nici de două ori.
(Clichetul 50 / METODA §23; prins de `core/scan_garzi_pe_text.py` la prima rulare a suitei.)

CE NU FACE, declarat: **nu trece prin HTTP.** Verifică poarta și efectul ei pe date, nu stiva
FastAPI. Că ruta chiar cheamă poarta se citește din AST; că un om poate apăsa butonul s-a probat pe
ecran (JJ3/KK1), nu aici.
"""
import ast
import io
import os

from core import db, tenant_stergere as ts

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")


def _arbore():
    return ast.parse(io.open(_MAIN, encoding="utf-8").read())


def _functia(arb, nume):
    fn = next((n for n in ast.walk(arb)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume), None)
    assert fn is not None, "`%s` nu mai există în main.py" % nume
    return fn


def _apeluri(fn):
    out = []
    for c in ast.walk(fn):
        if isinstance(c, ast.Call):
            n = c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)
            if n:
                out.append(n)
    return out


def test_ruta_de_activare_NU_mai_trece_prin_poarta_comuna():
    ap = _apeluri(_functia(_arbore(), "tenant_activare"))
    assert ap.count("_acces_pentru_activare") == 1, (
        "ruta de activare cheamă verificarea proprie de %d ori, nu exact o dată: %s"
        % (ap.count("_acces_pentru_activare"), sorted(set(ap))))
    assert ap.count("schema_tenant") == 0, (
        "ruta de activare a revenit la `schema_tenant` — aia cere `activ = true`, deci reactivarea "
        "redevine imposibilă (R83)")


def test_exceptia_ramane_LOCALA_un_singur_apelant():
    """[2] Decizia (a) e „local și reversibil". O a doua chemare ar transforma excepția într-o
    poartă paralelă — adică varianta (b), pe furiș și nemăsurată."""
    arb = _arbore()
    apelanti = []
    for n in ast.walk(arb):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if n.name == "_acces_pentru_activare":
            continue
        if _apeluri(n).count("_acces_pentru_activare"):
            apelanti.append(n.name)
    assert apelanti == ["tenant_activare"], (
        "verificarea proprie e chemată din %s — trebuie dintr-un singur loc" % apelanti)


def test_poarta_COMUNA_cere_in_continuare_activ_pe_toate_trei_ramurile():
    """[3] Efectul secundar pe care decizia (a) îl refuză: dacă `schema_tenant` ar pierde `activ`,
    toate celelalte rute ar căpăta acces la firme inactive fără ca cineva s-o fi cerut.

    Se citește din SQL-ul dat lui `execute`, ca nod — nu ca text căutat în fișier."""
    sursa = io.open(os.path.join(_RAD, "core", "auth_api.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "schema_tenant")
    interogari = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            a = n.args[0]
            while isinstance(a, ast.BinOp):
                a = a.left
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                interogari.append(" ".join(a.value.split()))
    assert len(interogari) == 3, (
        "`schema_tenant` are %d interogări, nu 3 — s-a schimbat forma, recitește" % len(interogari))
    fara = [q[:70] for q in interogari if "activ = true" not in q and "activ=true" not in q]
    assert not fara, (
        "ramuri ale porții COMUNE care nu mai cer `activ = true`: %s\n"
        "Decizia (a) spune explicit: restul rutelor rămân neatinse." % fara)


def test_regula_de_ROL_e_pastrata_in_exceptie():
    """[4] Excepția schimbă UN singur lucru — `activ`. Dacă ar pierde și regula de rol, ar deveni
    o gaură, nu o excepție."""
    import main
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants "
                    "WHERE accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
        tid, cab = cur.fetchone()
    with db.get_conn() as conn:
        assert main._acces_pentru_activare(conn, "admin_firma", cab, tid) is True
        assert main._acces_pentru_activare(conn, "admin_firma", cab + 1, tid) is False, (
            "un admin din ALT cabinet poate comuta firma — izolarea s-a rupt")
        assert main._acces_pentru_activare(conn, "superadmin", None, tid) is False, (
            "superadmin ajunge la o firmă CU cabinet — regula GDPR din poarta comună s-a pierdut")
        assert main._acces_pentru_activare(conn, "admin_firma", cab, 10 ** 9) is False, (
            "un tenant inexistent trece")


def test_pe_date_o_firma_INACTIVA_e_accesibila_activarii_si_NUMAI_ei():
    """[1] Proba care contează, pe date, în tranzacție întoarsă la savepoint: cu firma dezactivată,
    poarta **comună** o refuză (și e corect — restul rutelor nu trebuie s-o vadă), iar poarta
    **rutei de activare** o acceptă. Exact diferența cerută, măsurată, nu presupusă."""
    import main
    from core import auth_api
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT t.id, t.accounting_firm_id, u.id FROM public.tenants t "
                        "JOIN public.users u ON u.accounting_firm_id = t.accounting_firm_id "
                        "WHERE t.activ AND u.rol = 'admin_firma' ORDER BY t.id LIMIT 1")
            tid, cab, uid = cur.fetchone()
            cur.execute("SAVEPOINT p_r83")
        assert auth_api.schema_tenant(conn, uid, tid), "[anti-vacuu] firma nu e accesibilă nici activă"
        ts.comuta_activ(conn, tid, False, uid)
        assert auth_api.schema_tenant(conn, uid, tid) is None, (
            "poarta comună vede o firmă inactivă — atunci defectul R83 n-ar fi existat, iar testul "
            "ăsta nu măsoară ce crede")
        assert main._acces_pentru_activare(conn, "admin_firma", cab, tid) is True, (
            "poarta rutei de activare refuză o firmă inactivă — reactivarea rămâne imposibilă")
        r = ts.comuta_activ(conn, tid, True, uid)
        assert r["schimbat"] is True and r["activ"] is True
        # idempotent, decis explicit: a doua oară nu e eroare și nu scrie nimic
        r2 = ts.comuta_activ(conn, tid, True, uid)
        assert r2["schimbat"] is False, "activarea unei firme deja active nu mai e no-op"
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT p_r83")
        conn.rollback()
