# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 457 (comanda Costin 11.3 pct.4, verbatim în DECIZII „Comanda 11.3”): „ciornele făcute de contabil nu ajung în
nicio coadă (182 nerezolvată); după contarea din bancă, rândul spune «la validare» deși nota e ciornă.”

Două gărzi pe server (ecranul îl apără e2e-ul `frontend_test/e2e/e2e_lot11_a457.py`):
  1. Banca: starea notelor unei linii contate se citește din coada de validare (`reconciliere_api.stare_note_linie`), nu se presupune din
     „nevalidată”: ciorna netrimisă (a celui care validează) e „ciornă”, nu „la validare”; „la validare” numai când nota e în coadă.
  2. Ciornele contabilului (`coada_api.ciorne_proprii`, sursa listei „Notele tale în ciornă” din „De validat”): ciorna validatorului e
     acolo, netrimisă; a asistentului, trimisă, e „la_senior”; starea vine din aceeași citire a cozii (`stari_note`).

Schemă efemeră din `tenant_template.sql`, într-o tranzacție anulată (forma din `core/test_lot0710_p2.py`), an sintetic 2099.
Temei: N/A — starea notei pe ecran (ciornă / la validare / validată) nu e o regulă fiscală; ecranul spune ce e în bază.
"""
import io
import json

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot11_a457"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='asistent@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    asist, cab = r
    cur.execute("SELECT id FROM public.users WHERE email='patron@prisma-cont.test'")
    patron = cur.fetchone()[0]
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 11 A457 SRL',%s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, cab, asist, patron
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        conn.commit()
        p.putconn(conn)


def _ca(cur, uid):
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))


def _nota(conn, desc, debit="627", credit="5121", suma=12.5):
    """O notă manuală pe drumul aplicației (`jurnal_api.creeaza`), autorul = utilizatorul pus pe conexiune (`iconta.utilizator`)."""
    from core import jurnal_api
    linie = {"debit": debit, "credit": credit, "suma": suma}
    if {debit, credit} & {"401", "4111"}:      # [381] nota pe un cont de terți cere partenerul
        linie["partener_nume"] = "PARTENER PROBA SRL"
    r = jurnal_api.creeaza(conn, SCH, desc, "2099-10-16", [linie], document_ref="Extras 1 din 16.10.2099")
    assert r.get("id"), r
    return r["id"]


def _linie_contata(cur, nid):
    cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip, status, alocari) VALUES ('2099-10-16', 'Comision administrare cont', "
                "12.5, 'plata', 'contat', %s) RETURNING id", (json.dumps({"alocari": [], "inregistrari_ids": [nid]}),))
    return cur.fetchone()[0]


# ── 1. Banca: starea notei pe rândul liniei contate ───────────────────────────────────────────────────────────────────────────

def test_stare_note_linie_spune_coada_numai_cum_e():
    """PURĂ. MUTAȚIE: `"la_senior" if all(...)` -> `"la_senior"` (orice nevalidată = „la validare”, ca înainte) -> pică pe ciorna netrimisă."""
    from core.reconciliere_api import stare_note_linie as s
    assert s([], {}, {}) is None                                                   # linie fără note: nimic de spus
    assert s([1], {1: "validata"}, {})["nota_status"] == "validata"                  # contată și în evidență: „Contat ✓”
    c = s([1], {1: "ciorna"}, {})                                                   # 457: ciorna netrimisă -> ciornă, nu „la validare”
    assert (c["nota_status"], c["stare_coada"], c["nevalidate"]) == ("ciorna", None, 1), c
    c = s([1], {1: "ciorna"}, {1: {"stare_coada": "la_senior"}})                    # trimisă: la validare în cabinet
    assert c["stare_coada"] == "la_senior", c
    c = s([1, 2], {1: "ciorna", 2: "ciorna"}, {1: {"stare_coada": "la_senior"}})    # una trimisă, una nu: NU „la validare”
    assert c["stare_coada"] is None and c["nevalidate"] == 2, c
    c = s([1, 2], {1: "ciorna", 2: "validata"}, {1: {"stare_coada": "respinsa", "motiv_respingere": "lipsește extrasul"}})
    assert (c["stare_coada"], c["motiv_respingere"], c["nevalidate"]) == ("respinsa", "lipsește extrasul", 1), c


def test_banca_ciorna_validatorului_e_ciorna_iar_nota_trimisa_e_la_validare(tx):
    """457, al doilea defect: contarea din bancă a celui care validează lasă nota ciornă, netrimisă — rândul nu spune „la validare”.
    MUTAȚIE: în `reconciliere_api.lista`, `coada = {}` (starea cozii necitită) -> nota asistentului, trimisă, iese „ciornă” -> pică."""
    from core import coada_api, reconciliere_api as ra
    conn, cur, tid, cab, asist, patron = tx
    _ca(cur, patron)
    n_patron = _nota(conn, "Comision administrare cont — contabil")
    l_patron = _linie_contata(cur, n_patron)
    _ca(cur, asist)
    n_asist = _nota(conn, "Comision administrare cont — asistent")
    l_asist = _linie_contata(cur, n_asist)
    coada_api.pune_notele_in_coada(conn, cab, tid, asist)                            # drumul asistentului: nota pleacă la validare
    linii = {l["id"]: l for l in ra.lista(conn, '"%s"' % SCH)}
    p, a = linii[l_patron]["nota_stare"], linii[l_asist]["nota_stare"]
    assert (p["nota_status"], p["stare_coada"]) == ("ciorna", None), p             # ciornă netrimisă -> „Contată · notă ciornă”
    assert (a["nota_status"], a["stare_coada"]) == ("ciorna", "la_senior"), a      # în coadă -> „Contată · notă la validare în cabinet”
    assert linii[l_patron]["note_de_validat"] == 1 and linii[l_asist]["note_de_validat"] == 1   # numărul nevalidatelor (309) rămâne
    _ca(cur, patron)
    cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n_patron,))
    assert ra.lista(conn, '"%s"' % SCH) and [l for l in ra.lista(conn, '"%s"' % SCH) if l["id"] == l_patron][0]["nota_stare"]["nota_status"] \
        == "validata"


# ── 2. Ciornele contabilului: sursa listei „Notele tale în ciornă” ────────────────────────────────────────────────────────────

def test_ciorna_contabilului_e_in_lista_lui_netrimisa_iar_a_asistentului_trimisa(tx):
    """457, primul defect: ciorna scrisă de cel care validează nu intră în coada patru-ochi (o validează el) — lista lui o are, cu starea
    „netrimisă” (None); ciorna asistentului, trimisă de drumul lui, e „la_senior”; nota altuia nu e în lista ta.
    MUTAȚIE: în `ciorne_proprii`, `stari_note(...)` -> `{}` -> nota asistentului iese netrimisă -> pică."""
    from core import coada_api
    conn, cur, tid, cab, asist, patron = tx
    _ca(cur, patron)
    n_patron = _nota(conn, "Încasare de la client — contabil", debit="5311", credit="4111")
    _ca(cur, asist)
    n_asist = _nota(conn, "Plată furnizor — asistent", debit="401", credit="5311")
    coada_api.pune_notele_in_coada(conn, cab, tid, asist)
    ale_patron = coada_api.ciorne_proprii(conn, tid, patron)
    ale_asist = coada_api.ciorne_proprii(conn, tid, asist)
    assert [(n["id"], n["in_coada"]) for n in ale_patron] == [(n_patron, None)], ale_patron
    assert [(n["id"], n["in_coada"]) for n in ale_asist] == [(n_asist, "la_senior")], ale_asist
    assert ale_patron[0]["data"] == "2099-10-16" and ale_patron[0]["rulaj"] == 12.5


# ── 3. Garda clasei: „la validare” spus fără starea din coadă ───────────────────────────────────────────────────────────────

#: [457, clasa] afirmații de stare scrise de mână, care spun „la validare” despre ORICE notă nevalidată (deci și despre ciorna netrimisă):
#: rândul Băncii („Contată, nota e la validare”, 309) și mesajul NIR-ului salvat („notele merg la validare”). Starea pe rând vine din coadă
#: (`stareNotaCasa` pe câmpurile `stare_coada` / `nota_status`), iar după o salvare din antetul răspunsului (`api.stareNota` / `pasNota`).
_AFIRMATII_FARA_COADA = ("nota e la validare", "merg la validare", "notele sunt la validare", "nota este la validare")


def test_niciun_ecran_nu_spune_la_validare_fara_starea_din_coada():
    """MUTAȚIE: în `firme.js`, eticheta rândului Băncii -> „Contată, nota e la validare” (forma de dinainte) -> pică."""
    import glob
    import os
    import re
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gasite = []
    for p in sorted(glob.glob(os.path.join(rad, "static", "js", "**", "*.js"), recursive=True)):
        for i, linie in enumerate(io.open(p, encoding="utf-8"), 1):
            fara_comentariu = re.sub(r"^\s*//.*$", "", linie)
            for a in _AFIRMATII_FARA_COADA:
                if a in fara_comentariu.lower():
                    gasite.append("%s:%d %s" % (os.path.relpath(p, rad), i, a))
    assert not gasite, ("„la validare” scris de mână, fără starea din coadă (o ciornă netrimisă nu e la validare): %s" % gasite)
