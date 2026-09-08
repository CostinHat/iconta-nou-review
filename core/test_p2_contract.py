# -*- coding: utf-8 -*-
"""GARD P2 — CONTRACTUL ARHITECTURAL, în șapte propoziții și sub zece secunde.

**DE CE EXISTĂ, deși fiecare propoziție are deja o gardă amănunțită.** Suita P2 completă
(`test_firma_rezumat`, `test_p2_infrastructura`, `test_dependente_ramuri`, `test_paritate_p2`,
`test_dependente_masurate`) e temeinică, dar se citește greu și rulează în minute. Fișierul ăsta e
**lista scurtă**: dacă peste șase luni cineva atinge autentificarea, lucrătorul sau pornirea, o
regresie P2 trebuie să iasă la iveală **repede**, fără să fie nevoie să rulezi tot.

*Nu înlocuiește nimic.* E o plasă de siguranță cu ochiuri mari, pusă peste una cu ochiuri mici.

**CELE ȘAPTE CONTRACTE:**

  1. infrastructură incompletă  → aplicația NU pornește;
  2. scriere într-o sursă        → aspectele care o citesc devin `invalidat`;
  3. trecerea zilei              → verdictele de zi devin `invalidat`, fără nicio scriere;
  4. lucrătorul                  → aduce înapoi la `curent`;
  5. doi lucrători pe o firmă    → cel mult unul calculează;
  6. 5 firme vs 50               → același număr de interogări pe cele cinci rute;
  7. `tip_firma`                 → nicio buclă per firmă pe calea de cerere.

Se rulează cu `pytest core/test_p2_contract.py`. E un GRUP prin fișier, nu prin marcaj: suita n-are
registru de marcaje, iar un marcaj neînregistrat ar produce avertismente la fiecare rulare —
adică zgomot permanent pentru o comoditate de selecție.
"""
import datetime
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import masoara_interogari as MI  # noqa: E402
from core import auth_api  # noqa: E402
from core import db as _db  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402

SCHEMA = "proba_p2_contract"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def firma():
    """O firmă efemeră cu schemă reală și triggere legate. Ștearsă la final."""
    if not _db_ok():
        pytest.skip("fara baza de date")

    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (SCHEMA,))
                r = cur.fetchone()
                if r:
                    for t in ("firma_rezumat", "firma_sursa_versiune", "supervizor_sursa",
                              "firma_tip"):
                        cur.execute("DELETE FROM public.%s WHERE tenant_id = %%s" % t, (r[0],))
                    cur.execute("DELETE FROM public.tenants WHERE id = %s", (r[0],))
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA)
            c.commit()

    # SCHEMĂ REALĂ, din chiar template-ul de provisionare — nu tabele-jucărie. Contractul 4 spune
    # „lucrătorul aduce înapoi la CURENT"; pe tabele inventate, aspectele ușoare cad în `eroare`
    # (corect!) și proba ar fi verificat altceva decât contractul.
    tpl_cale = os.path.join(_RAD, "tenant_template.sql")
    if not os.path.exists(tpl_cale):
        pytest.skip("tenant_template.sql lipsește")
    with open(tpl_cale, encoding="utf-8") as f:
        tpl = f.read()
    from core import tenant_provisioning as TP

    sterge()
    with _db.get_conn() as c:
        TP.creeaza_schema(c, SCHEMA, tpl)
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.tenants (schema_name, nume, activ) "
                        "VALUES (%s, 'PROBA P2 CONTRACT', true) RETURNING id", (SCHEMA,))
            tid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, serie_factura, '
                        '  urmator_numar_factura, tip_firma, regim_fiscal, platitor_tva, '
                        "  tip_decont, operatiuni_ic) "
                        "VALUES (1,'PROBA P2 CONTRACT','12345678','PC',1,'srl','micro',true,'L',"
                        "        false) ON CONFLICT (id) DO NOTHING" % SCHEMA)
        FR.leaga_triggerele_firma(c, SCHEMA, tid)
        c.commit()
    yield tid, SCHEMA
    sterge()


def _curente(tid, azi=None):
    azi = azi or datetime.date.today()
    with _db.get_conn() as c:
        v = FR.versiuni_aspecte(c, tid, list(FR.TOATE))
        for a in FR.TOATE:
            FR.scrie(c, tid, a, {"contract": True}, v[a], epoca=FR.epoca_pentru(a, azi))
        c.commit()


def _stari(tid, azi=None):
    with _db.get_conn() as c:
        d = FR.citeste(c, [tid], list(FR.TOATE), azi=azi)
    return {a: d[tid][a]["stare"] for a in FR.TOATE}


# ============================================================================
def test_contract_1_infrastructura_incompleta_opreste_pornirea(monkeypatch):
    """Fără infrastructură, aplicația n-are voie să pretindă că garantează prospețimea."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    from fastapi.testclient import TestClient
    import main as _main

    def _explodeaza(conn):
        raise RuntimeError("contract: infrastructura P2 lipsește")

    monkeypatch.setattr(FR, "aplica_ddl", _explodeaza)
    with pytest.raises(RuntimeError, match="contract: infrastructura P2 lipsește"):
        with TestClient(_main.app):
            pass
    try:
        _db.init_pool()
    except Exception:
        pass


def test_contract_2_scrierea_intr_o_sursa_invalideaza_ce_o_citeste(firma):
    """Și NUMAI ce o citește: o factură nu atinge soldurile."""
    tid, schema = firma
    _curente(tid)
    assert all(s == FR.CURENT for s in _stari(tid).values())
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".facturi (numar, data_emitere, directie, total, tva) '
                        "VALUES ('PC-1', CURRENT_DATE, 'emisa', 1190, 190)" % schema)
        c.commit()
    st = _stari(tid)
    assert st["control_fiscal"] == FR.INVALIDAT and st["termene"] == FR.INVALIDAT
    assert st["solduri"] == FR.CURENT and st["plan_conturi"] == FR.CURENT


def test_contract_3_trecerea_zilei_invalideaza_verdictele_de_zi(firma):
    """Fără nicio scriere în bază: doar s-a schimbat ziua."""
    tid, _schema = firma
    ieri = datetime.date.today() - datetime.timedelta(days=1)
    _curente(tid, azi=ieri)
    assert _stari(tid, azi=ieri)["control_fiscal"] == FR.CURENT
    azi = _stari(tid, azi=datetime.date.today())
    assert azi["termene"] == FR.INVALIDAT and azi["control_fiscal"] == FR.INVALIDAT
    assert azi["plan_conturi"] == FR.CURENT, "ce nu depinde de ceas nu se invalidează cu ziua"


def test_contract_4_lucratorul_aduce_inapoi_la_curent(firma):
    """Aspectele UȘOARE, pe o schemă de probă: din `lipseste` în `curent`, printr-o tură."""
    tid, schema = firma
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    assert all(_stari(tid)[a] == FR.LIPSESTE for a in FR.ASPECTE_USOARE)
    FR.recalculeaza_firma(tid, schema, aspecte=list(FR.ASPECTE_USOARE))
    st = _stari(tid)
    ramase = [a for a in FR.ASPECTE_USOARE if st[a] != FR.CURENT]
    assert not ramase, "aspecte rămase necurente după recalculare: %s (%s)" % (
        ramase, {a: st[a] for a in ramase})


def test_contract_5_doi_lucratori_pe_o_firma_doar_unul_calculeaza(firma):
    """Blocaj de sesiune, neblocant: al doilea SARE firma, nu o așteaptă."""
    tid, _schema = firma
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    p = _db.pool()
    alta = p.getconn()
    try:
        luat, _pid = FR.ia_blocajul(alta, tid)
        assert luat, "n-am putut lua blocajul; proba n-ar avea obiect"
        r = FR.recalculeaza_lot(limita=5000)
        assert r["sarite_blocate"] >= 1
    finally:
        FR.lasa_blocajul(alta, tid)
        p.putconn(alta)


def test_contract_6_acelasi_numar_de_interogari_la_5_si_la_50_de_firme():
    """CERINȚA P2, pe cererea HTTP întreagă. Curba pe șase puncte stă în artefacte."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import masoara_rute_portofoliu as MR
    ok, _ = MR.calibreaza(verbose=False)
    assert ok, "hamul HTTP nu e calibrat — nicio cifră n-ar valora nimic"
    masurat = {}
    try:
        for n in (5, 50):
            with _db.get_conn() as conn:
                MR.curata(conn)
                conn.commit()
            with _db.get_conn() as conn:
                uid, _ids = MR.construieste(conn, n, procent_invalidat=10, rece=False)
                tok = MR._token(conn, uid)
            with MR.client_test() as cl:
                cl.get(MR.RUTE[0], headers={"Authorization": "Bearer " + tok})
                masurat[n] = {r: MR.masoara_ruta(cl, tok, r) for r in MR.RUTE}
    finally:
        with _db.get_conn() as conn:
            MR.curata(conn)
            conn.commit()
    crescute = [r for r in MR.RUTE
                if masurat[5][r]["interogari"] != masurat[50][r]["interogari"]
                or masurat[5][r]["conexiuni"] != masurat[50][r]["conexiuni"]]
    assert all(masurat[n][r]["status"] == 200 for n in masurat for r in MR.RUTE)
    assert not crescute, "interogările cresc cu numărul de firme pe: %s" % crescute


def test_contract_7_tip_firma_fara_bucla_per_firma():
    """`tip_firma` vine din proiecția sincronă. Nicio interogare per firmă pe calea de cerere."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT u.id, count(t.id) FROM public.users u "
                        "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                        " WHERE u.rol = 'admin_firma' AND u.activ AND t.activ "
                        " GROUP BY u.id ORDER BY 2 DESC LIMIT 1")
            r = cur.fetchone()
    if not r or r[1] < 2:
        pytest.skip("niciun cabinet cu cel puțin două firme")
    uid, cate = r
    with MI.numara() as n:
        with _db.get_conn() as c:
            lista = auth_api.tenantii_userului(c, uid)
    assert len(lista) == cate
    assert n.interogari <= 3, (
        "%d interogări pentru %d firme — a reapărut bucla per firmă" % (n.interogari, cate))
    assert all(t.get("tip_firma") for t in lista), "proiecția `tip_firma` nu acoperă tot portofoliul"
