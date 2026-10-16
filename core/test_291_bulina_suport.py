# -*- coding: utf-8 -*-
"""291 — bulina de pe „Suport” (comanda Costin 16.10.2026, completarea 290–295 la lotul 6, verbatim în DECIZII): „Bulina roșie de pe
butonul Suport apare pentru cererea trimisă chiar de utilizator. Bulina anunță un răspuns sau o schimbare de stare venită de la iConta,
nu propria cerere.” Temei: N/A — produs. Totul într-o tranzacție anulată, pe un cont de test existent."""
import pytest

from core import db as _db


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_291_bulina_numara_vestile_de_la_iconta_nu_cererea_mea():
    """MUTAȚIE: `contor_necitite` înapoi pe `r.stare = 'noua'` -> cererea proprie aprinde bulina -> pică."""
    from core import raportari_api as rap
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", ("patron@prisma-cont.test",))
                uid, firm = cur.fetchone()
            n0 = rap.contor_necitite(c, uid)["necitite"]
            rid = rap.creeaza_raportare(c, uid, firm, None, "Nu merge importul.")["raportare_id"]
            assert rap.contor_necitite(c, uid)["necitite"] == n0, "cererea mea nu e o veste"
            fir = lambda: [f for f in rap.raportarile_mele(c, uid)["raportari"] if f["id"] == rid][0]   # noqa: E731
            assert fir()["necitite"] == 0
            rap.adauga_mesaj(c, rid, None, "admin", "Ne uităm.")
            assert rap.contor_necitite(c, uid)["necitite"] == n0 + 1 and fir()["necitite"] == 1, "răspunsul iConta e o veste"
            rap.marcheaza_citit(c, rid, "utilizator")
            assert rap.contor_necitite(c, uid)["necitite"] == n0
            rap.seteaza_stare(c, rid, "inchisa")
            assert rap.contor_necitite(c, uid)["necitite"] == n0 + 1, "starea schimbată de iConta e o veste"
            rap.marcheaza_citit(c, rid, "utilizator")
            rap.seteaza_stare(c, rid, "inchisa")
            assert rap.contor_necitite(c, uid)["necitite"] == n0, "aceeași stare din nou nu e o veste"
            rap.adauga_mesaj(c, rid, None, "ai", "Încearcă exportul CSV.")
            assert rap.contor_necitite(c, uid)["necitite"] == n0 + 1
            rap.marcheaza_citit(c, rid, "utilizator")
            assert rap.contor_necitite(c, uid)["necitite"] == n0, "și răspunsul asistentului AI se marchează citit"
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_291_confirmarea_automata_a_escaladarii_nu_e_o_veste(monkeypatch):
    """Cauza observată: la o sesizare escaladată, triajul AI scrie „Sesizarea ta a fost transmisă echipei iConta…” — ecoul cererii
    proprii, care aprindea bulina. MUTAȚIE: `veste=False` scos din `raportari_ai.proceseaza` -> bulina 1 după cererea proprie -> pică."""
    from core import raportari_api as rap, raportari_ai as rai
    monkeypatch.setattr(rai, "triaj", lambda subiect, text: {"decizie": "escaladez", "motiv": "proba"})
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", ("patron@prisma-cont.test",))
            uid, firm = cur.fetchone()
        rid = rap.creeaza_raportare(c, uid, firm, None, "Proba 291 escaladare.")["raportare_id"]
        c.commit()
    try:
        rai.proceseaza(rid, None, "Proba 291 escaladare.")
        with _db.get_conn() as c:
            fir = [f for f in rap.raportarile_mele(c, uid)["raportari"] if f["id"] == rid][0]
        assert [m["rol_autor"] for m in fir["mesaje"]] == ["utilizator", "ai"] and fir["necitite"] == 0, fir
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.raportari_mesaje WHERE raportare_id = %s", (rid,))
                cur.execute("DELETE FROM public.raportari WHERE id = %s", (rid,))
            c.commit()
