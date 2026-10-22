# -*- coding: utf-8 -*-
"""[lotul 11, subagentul P2] Două surse unice aplicate peste drumurile care le ocoleau:
(1) „partida simplă” (PFA / II / IF) a capitalului social vine din `migrare_api.regim_contabil` (ca `control_fiscal_api.neaplicabile_forma`),
    nu dintr-o comparație `tip_firma == "pfa"` care pierdea forma nenormalizată („PFA ”) și cerea capital unui PFA;
(2) CUI-ul se compară și se scrie în forma păstrată (`cui_forma.stocare`: fără „RO”, fără spații — decizia Costin 10.3 pct.4) și la
    crearea firmei / corectura CUI-ului / Date cabinet: „RO123” și „123” sunt același cod fiscal pentru verificarea unicității.
Temei (1): Legea 31/1990 art.74 alin.(3) — capitalul se menționează de societăți, nu de PFA / II / IF (core/capital_social.TEMEI).
Temei (2): N/A — forma de stocare e decizia lui Costin, nu o normă (CF art.318 alin.(1) privește afișarea, `cui_forma`).
Schemă efemeră / tranzacție anulată."""
import io

import pytest

from core import capital_social as cs
from core import db as _db


@pytest.mark.parametrize("tip", ["pfa", "PFA", " pfa "])
def test_capitalul_nu_se_cere_partidei_simple_oricum_e_scris_tipul(tip):
    # Legea 31/1990 art.74 alin.(3): numai „o societate cu răspundere limitată / pe acțiuni / în comandită pe acțiuni” menționează capitalul
    assert cs.lipsa({"tip_firma": tip}) == []
    assert cs.text_factura({"tip_firma": tip, "forma_juridica": "SRL", "capital_subscris": "200"}) is None


def test_societatea_cere_forma_si_capitalul():
    assert cs.lipsa({"tip_firma": "srl"}) == ["forma juridică a firmei (SRL, SA etc.)"]
    assert cs.lipsa({}) == ["forma juridică a firmei (SRL, SA etc.)"]   # fără coloană: societate (implicitul `tip_firma_nrm`)
    assert cs.text_factura({"tip_firma": "srl", "forma_juridica": "SRL", "capital_subscris": "200"}) == "Capital social: 200,00 lei"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_unicitatea_cui_la_creare_si_la_corectura_compara_forma_pastrata(contor_schema_pastrat):
    from core import tenant_provisioning as tp
    from core import auth_api
    _db.init_pool()
    c = _db.pool().getconn()
    try:
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF P2 CUI') RETURNING id"); fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_p2_cui@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,)); uid = cur.fetchone()[0]
        sql_t = io.open("tenant_template.sql", encoding="utf-8").read()
        # CUI 14399840: cifra de control verificată (algoritmul din CLAUDE.md)
        r = tp.provision_tenant(c, "EF P2 CUI UNU SRL", " ro 14399840 ", fid, uid, sql_t)
        with c.cursor() as cur:
            cur.execute("SELECT cui FROM public.tenants WHERE id = %s", (r["tenant_id"],))
            assert cur.fetchone()[0] == "14399840"
            cur.execute('SELECT cui FROM "%s".firma_profil WHERE id = 1' % r["schema_name"])
            assert cur.fetchone()[0] == "14399840"
        with pytest.raises(ValueError, match="Ai deja în portofoliu o firmă cu codul fiscal 14399840"):
            tp.provision_tenant(c, "EF P2 CUI DOI SRL", "RO14399840", fid, uid, sql_t)   # același cod, scris cu „RO”
        r2 = tp.provision_tenant(c, "EF P2 CUI TREI SRL", "2864518", fid, uid, sql_t)   # 2864518: cifra de control verificată
        with pytest.raises(ValueError, match="Ai deja în portofoliu"):
            tp.cere_cui_unic(c, r2["tenant_id"], "RO 14399840")
        tp.alege_cui(c, r2["tenant_id"], "RO2864518")
        with c.cursor() as cur:
            cur.execute("SELECT cui FROM public.tenants WHERE id = %s", (r2["tenant_id"],))
            assert cur.fetchone()[0] == "2864518"
        cab = auth_api.actualizeaza_cabinet(c, fid, cui=" RO 2864518")
        assert cab["ok"] and cab["cabinet"]["cui"] == "2864518", cab
        for sch in (r["schema_name"], r2["schema_name"]):
            with c.cursor() as cur:
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % sch)
    finally:
        c.rollback()
        _db.pool().putconn(c)
