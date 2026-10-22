# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 442, comanda Costin 11.1 pct.18, verbatim] „capitalul social lipsă apare în «Profil incomplet», cu «blochează emiterea
facturilor».”

Temei: Legea 31/1990 art.74 alin.(1) — „În orice factură, ofertă, comandă, tarif, prospect și alte documente întrebuințate în comerț,
emanând de la o societate, trebuie să se menționeze denumirea, forma juridică, sediul social, numărul din registrul comerțului și codul unic
de înregistrare.”; alin.(3) — „În documentele prevăzute la alin. (1) , dacă acestea provin de la o societate cu răspundere limitată, se va
menționa și capitalul social, iar dacă ele provin de la o societate pe acțiuni sau în comandită pe acțiuni, se vor menționa atât capitalul
social subscris, cât și cel vărsat.” (anaf_surse/legea_31_1990_societatile.txt). CF art.319 alin.(20) (mențiunile obligatorii ale
facturii, din punctul de vedere al TVA) NU cere capitalul — obligația e a Legii societăților, iar refuzul emiterii fără el e decizia lui
Costin din 03.10.2026 (`core/capital_social.py`), deja în vigoare (`facturi_api`). Ce lipsea: „Profil incomplet” nu o spunea.
MUTAȚIE: blocul capitalului scos din `firma_profil_api.lipsuri` -> `test_profil_incomplet_spune_ce_blocheaza_emiterea` pică.
"""
import io

import pytest

from core import capital_social as cs, firma_profil_api as fp


def _emitere(lips):
    return {x["camp"] for x in lips if x["declaratii"] == [fp.BLOCHEAZA_EMITEREA]}


def test_profil_incomplet_spune_ce_blocheaza_emiterea():
    assert _emitere(fp.lipsuri({"tip_firma": "srl"})) == {"forma_juridica"}                       # fără formă: nu se știe ce capital
    assert _emitere(fp.lipsuri({"tip_firma": "srl", "forma_juridica": "SRL"})) == {"capital_subscris"}   # art.74 alin.(3): SRL -> capitalul
    assert _emitere(fp.lipsuri({"tip_firma": "srl", "forma_juridica": "SA"})) == {"capital_subscris", "capital_varsat"}   # SA: ambele
    assert _emitere(fp.lipsuri({"tip_firma": "srl", "forma_juridica": "SRL", "capital_subscris": "200"})) == set()


@pytest.mark.parametrize("profil", [{"tip_firma": "pfa"}, {"tip_firma": "pfa", "forma_juridica": "SRL"},
                                    {"tip_firma": "srl", "forma_juridica": "SNC"}, {"tip_firma": "srl", "forma_juridica": "SCS"},
                                    {"tip_firma": "srl", "forma_juridica": "ALTA"}])
def test_formele_fara_capital_nu_primesc_lipsa(profil):
    # art.74 alin.(3) numește numai SRL, SA, SCA; PFA / II / IF (partidă simplă) nu sunt societăți (aceeași formă ca `neaplicabile_forma`)
    assert _emitere(fp.lipsuri(profil)) == set()


def test_aceeasi_regula_ca_refuzul_de_la_emitere():
    """Profil incomplet == refuzul de la emitere, pe fiecare ramură (o singură regulă: `capital_social.lipsa`)."""
    from core.control_fiscal_api import neaplicabile_forma
    for tip in ("srl", "pfa"):
        for forma in [None] + list(cs.FORME):
            for cap in (None, "200"):
                p = {"tip_firma": tip, "forma_juridica": forma, "capital_subscris": cap, "capital_varsat": cap}
                assert bool(_emitere(fp.lipsuri(p))) == bool(cs.lipsa(p)), p
                if set(neaplicabile_forma(tip)) >= {"bilant"}:   # partida simplă (sursa unică a formei) -> nimic despre capital
                    assert not _emitere(fp.lipsuri(p)), p


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_citirea_ecranului_si_salvarea_spun_lipsa_capitalului():
    from core import db, tenant_provisioning as tp
    s = "ztest_l11p_capital"
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % s)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), s))
                cur.execute("SET LOCAL search_path TO %s, public" % s)
                cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'FIRMA L11 SRL', '14399840')")
            assert _emitere(fp.citeste_date(c)["lipsuri"]) == {"forma_juridica"}
            r = fp.salveaza_date(c, {"forma_juridica": "SRL"}, user_id=1)
            assert r["ok"] is True and _emitere(r["lipsuri"]) == {"capital_subscris"}, r   # „Salvat. Lipsește Capital social subscris …”
            r = fp.salveaza_date(c, {"forma_juridica": "SRL", "capital_subscris": "200"}, user_id=1)
            assert r["ok"] is True and _emitere(r["lipsuri"]) == set(), r
        finally:
            c.rollback()
