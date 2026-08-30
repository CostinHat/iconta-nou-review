# -*- coding: utf-8 -*-
"""GARD [R84/PP3, 28.08.2026]: poarta de citire-istorica are EXACT 13 apelanti, si sunt GET-uri.

DE UNDE VINE. `auth_api.schema_tenant` cere `activ = true` pe toate trei ramurile de rol, deci
jurnalul, balanta, rapoartele si exporturile unei firme dezactivate raspundeau **404** — desi
confirmarea de pe ecran promite ca *„datele ei raman neatinse"*. Ramaneau, dar necitibile.

DECIZIA lui Costin, varianta **(b)**: o poarta DECLARATA de citire-istorica,
`schema_tenant_citire`, ceruta **explicit** doar de cele 13 rute. Restul aplicatiei ramane pe
`schema_tenant`, neschimbat.

CE FACE IMPOSIBIL:
  1. **raspandirea portii**: exact 13 apelanti, si exact cele 13 numite. Al 14-lea nu e o
     scapare, e varianta (c) pe furis — „firmele inactive accesibile tuturor rutelor";
  2. **strecurarea unei SCRIERI** pe poarta de citire: fiecare apelant trebuie sa fie decorat
     `@app.get`. `POST /jurnal` si `POST /rapoarte-salvate` stau pe aceleasi CAI ca doua dintre
     cele 13 — daca vreodata s-ar muta si ele, s-ar scrie in evidenta unei firme scoase din
     portofoliu;
  3. **pierderea izolarii intre cabinete**: poarta noua scoate `activ`, si NUMAI `activ`.
     Regula de rol se verifica pe date, nu prin citirea codului;
  4. **intoarcerea tacita**: daca vreuna din cele 13 revine la `schema_tenant`, R84 reapare
     fara ca nimic sa cada.

CE NU FACE, declarat: **nu trece prin HTTP.** Ca rutele raspund 200 pe o firma dezactivata s-a
masurat separat, prin apeluri reale pe toate 13 (PP4/PP5). Aici se pazeste FORMA.

CUM SE SCRIU ASERTIUNILE AICI: pe numaratori de noduri, nu pe `"nume" in lista` — un `in` trece
si pe iterabil gol (clichetul 50 / METODA §23).
"""
import ast
import io
import os

from core import auth_api, db, tenant_stergere as ts

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")

#: rutele de citire istorica, pe NUMELE functiei (ancora stabila: calea are parametri)
#:
#: 13 la deschidere (28.08.2026). A 14-a, `cabinet_balanta_date`, intrata pe 30.08.2026 la lista 5,
#: si motivul se scrie aici fiindca gardul avertizeaza — pe drept — ca al 14-lea apelant ar putea fi
#: „varianta (c) pe furis". NU E: `cabinet_documente_balanta` e deja printre cele 13, iar noua ruta
#: serveste ACELASI artefact, aceeasi luna, aceleasi cifre — doar ca DATE in loc de PDF. Daca ar sta
#: pe poarta comuna, balanta unei firme scoase din portofoliu s-ar putea DESCARCA dar nu s-ar putea
#: CITI, ceea ce ar rupe pe jumatate chiar promisiunea pentru care s-a facut poarta: „datele ei raman
#: neatinse". Nu se largeste clasa de acces; se adauga a doua iesire a unui membru existent.
RUTE_CITIRE = frozenset({
    "cabinet_urme_portal", "perioade_istoric", "tenant_jurnal", "cabinet_documente_balanta",
    "cabinet_balanta_date",
    "rapoarte_comerciale", "rapoarte_comerciale_fisa", "rapoarte_salvate_lista",
    "export_saga_factura", "centre_cost_raport", "casa_registru", "cv_fisa",
    "jurnal_marja", "factura_primita_xml"})

#: Perechile „acelasi artefact, doua iesiri". O intrare noua in RUTE_CITIRE care nu e nici in lista
#: de la deschidere, nici perechea uneia dintre ele, e o LARGIRE a deciziei (b) — si aia se cere, nu
#: se face. Gardul de mai jos o verifica.
PERECHI_ACELASI_ARTEFACT = {"cabinet_balanta_date": "cabinet_documente_balanta"}

#: acte de SCRIERE pe aceleasi cai — raman pe poarta comuna, si asta se pazeste
SCRIERI_PE_ACELEASI_CAI = frozenset({"jurnal_creeaza", "rapoarte_salvate_creeaza"})


def _arbore():
    return ast.parse(io.open(_MAIN, encoding="utf-8").read())


def _nume_apel(c):
    return c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)


def _apeluri(fn):
    return [n for n in (_nume_apel(c) for c in ast.walk(fn) if isinstance(c, ast.Call)) if n]


def _functii(arb):
    return [n for n in ast.walk(arb)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _metode(fn):
    """Metodele HTTP cu care e decorata functia: ['get'], ['post'], sau [] daca nu e ruta."""
    out = []
    for d in fn.decorator_list:
        if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"):
            out.append(d.func.attr)
    return out


def test_poarta_de_citire_are_exact_cei_13_apelanti_numiti():
    """[1] Decizia (b) e „ceruta EXPLICIT doar de cele 13". Al 14-lea apelant ar transforma-o
    in varianta (c) — firmele inactive accesibile tuturor rutelor — fara ca nimeni s-o fi cerut."""
    apelanti = {f.name for f in _functii(_arbore())
                if f.name != "schema_tenant_citire"
                and _apeluri(f).count("schema_tenant_citire") > 0}
    assert apelanti == RUTE_CITIRE, (
        "poarta de citire-istorica are alti apelanti decat cei 13 declarati.\n"
        "  in plus: %s\n  lipsa:   %s" % (sorted(apelanti - RUTE_CITIRE),
                                          sorted(RUTE_CITIRE - apelanti)))


def test_orice_intrare_noua_e_a_doua_iesire_a_uneia_vechi_nu_o_clasa_noua():
    """ZAVORUL care tine decizia (b) sa nu devina (c) prin acumulare.

    Gardul de mai sus cere ca multimea sa fie EXACT cea declarata — dar cine adauga un nume acolo
    a trecut deja de el. Ce nu poate trece: o intrare care nu e nici din cele 13 de la deschidere,
    nici declarata pereche a uneia dintre ele. Asa, largirea clasei de acces cere o propozitie
    scrisa, nu doar un nume adaugat intr-un `frozenset`.
    """
    la_deschidere = RUTE_CITIRE - set(PERECHI_ACELASI_ARTEFACT)
    assert len(la_deschidere) == 13, (
        "cele de la deschidere nu mai sunt 13, ci %d — o ruta noua a intrat fara sa se declare "
        "perechea artefactului pe care il serveste" % len(la_deschidere))
    for noua, veche in PERECHI_ACELASI_ARTEFACT.items():
        assert la_deschidere >= {veche}, (
            "%s e declarata a doua iesire a lui %s, dar %s nu e printre cele de la deschidere"
            % (noua, veche, veche))
        assert RUTE_CITIRE >= {noua}, "%s e declarata pereche, dar nu e in RUTE_CITIRE" % noua


def test_niciuna_din_cele_13_nu_mai_trece_prin_poarta_comuna():
    """[4] Intoarcerea tacita: daca una revine la `schema_tenant`, ea redevine 404 pe firma
    dezactivata, iar restul continua sa mearga — un gol care nu se vede din nicio parte."""
    ramase = {}
    for f in _functii(_arbore()):
        if f.name in RUTE_CITIRE:
            n = _apeluri(f).count("schema_tenant")
            if n:
                ramase[f.name] = n
    assert not ramase, (
        "rute de citire-istorica intoarse la poarta comuna (care cere `activ = true`): %s" % ramase)


def test_poarta_de_citire_e_ceruta_NUMAI_de_GET_uri():
    """[2] O poarta care nu cere `activ` pe un POST ar lasa sa se SCRIE in evidenta unei firme
    scoase din portofoliu. Doua dintre cele 13 au un POST pe aceeasi cale — se verifica anume."""
    arb = _arbore()
    nu_s_get = {}
    for f in _functii(arb):
        if _apeluri(f).count("schema_tenant_citire") > 0 and f.name != "schema_tenant_citire":
            met = _metode(f)
            if met != ["get"]:
                nu_s_get[f.name] = met or ["(nedecorata)"]
    assert not nu_s_get, (
        "poarta de CITIRE e ceruta de rute care nu sunt GET: %s" % nu_s_get)

    # si perechea inversa: actele de scriere de pe aceleasi cai n-au migrat
    for f in _functii(arb):
        if f.name in SCRIERI_PE_ACELEASI_CAI:
            assert _apeluri(f).count("schema_tenant") == 1, (
                "`%s` (act de SCRIERE) nu mai trece prin poarta comuna — o firma scoasa din "
                "portofoliu ar deveni scriibila" % f.name)
            assert _apeluri(f).count("schema_tenant_citire") == 0, (
                "`%s` a migrat pe poarta de citire" % f.name)


def test_poarta_de_citire_scoate_activ_SI_NUMAI_activ():
    """[3] Se citeste din SQL-ul dat lui `execute`, ca nod — nu ca text cautat in fisier.
    Cele trei ramuri trebuie sa pastreze exact predicatele de rol ale portii comune."""
    sursa = io.open(os.path.join(_RAD, "core", "auth_api.py"), encoding="utf-8").read()
    arb = ast.parse(sursa)

    def interogari(nume):
        fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == nume)
        out = []
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "execute" and n.args):
                a = n.args[0]
                while isinstance(a, ast.BinOp):
                    a = a.left
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    out.append(" ".join(a.value.split()))
        return out

    comuna, citire = interogari("schema_tenant"), interogari("schema_tenant_citire")
    assert len(comuna) == 3 and len(citire) == 3, (
        "porti cu %d / %d interogari, nu 3 — s-a schimbat forma, reciteste" % (len(comuna), len(citire)))
    for q in citire:
        assert "activ" not in q, "poarta de CITIRE cere tot `activ`: %s" % q[:80]
    # fiecare ramura a portii de citire e ramura corespondenta a celei comune, fara `activ`
    for i, (qc, qi) in enumerate(zip(comuna, citire)):
        redus = qc.replace(" AND activ = true", "").replace(" AND t.activ = true", "")
        assert redus == qi, (
            "ramura %d difera prin mai mult decat `activ`:\n  comuna: %s\n  citire: %s"
            % (i + 1, redus, qi))


def test_pe_date_izolarea_intre_cabinete_ramane_INTACTA():
    """[3] Proba care conteaza, pe date, in tranzactie intoarsa: firma dezactivata devine
    citibila pentru cine avea dreptul, si RAMANE invizibila pentru cine nu-l avea."""
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT t.id, t.accounting_firm_id, u.id FROM public.tenants t "
                        "JOIN public.users u ON u.accounting_firm_id = t.accounting_firm_id "
                        "WHERE t.activ AND u.rol = 'admin_firma' ORDER BY t.id LIMIT 1")
            tid, cab, uid = cur.fetchone()
            cur.execute("SELECT u.id FROM public.users u WHERE u.rol = 'admin_firma' "
                        "AND u.accounting_firm_id IS NOT NULL AND u.accounting_firm_id <> %s "
                        "ORDER BY u.id LIMIT 1", (cab,))
            strain = cur.fetchone()
            cur.execute("SELECT id FROM public.users WHERE rol = 'superadmin' ORDER BY id LIMIT 1")
            super_ = cur.fetchone()
            cur.execute("SAVEPOINT p_r84")
        assert auth_api.schema_tenant(conn, uid, tid), "[anti-vacuu] firma nu e accesibila nici activa"

        ts.comuta_activ(conn, tid, False, uid)
        assert auth_api.schema_tenant(conn, uid, tid) is None, (
            "poarta comuna vede o firma inactiva — atunci R84 n-ar fi existat, iar testul asta "
            "nu masoara ce crede")
        assert auth_api.schema_tenant_citire(conn, uid, tid), (
            "poarta de citire refuza o firma inactiva — trecutul ramane necitibil (R84)")
        if strain:
            assert auth_api.schema_tenant_citire(conn, strain[0], tid) is None, (
                "un admin din ALT cabinet citeste firma — izolarea s-a rupt")
        if super_:
            assert auth_api.schema_tenant_citire(conn, super_[0], tid) is None, (
                "superadmin ajunge la o firma CU cabinet — regula GDPR s-a pierdut")

        ts.comuta_activ(conn, tid, True, uid)
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT p_r84")
        conn.rollback()
