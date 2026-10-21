# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 428, comanda Costin 10.1] Regimul TVA la încasare pe firmă: perioadele, data de la care se aplică, ieșirea,
verificarea în registrul ANAF (RTVAI), jurnalul și indicatorul „se aplică azi”. Verbatim: „Firma nu poate fi declarată ca aplicând
sistemul: vectorul fiscal are doar «Înregistrată în scopuri de TVA: Da/Nu» […]. Construiește regimul pe firmă, cu data de la care se
aplică și verificarea în registrul ANAF”.

Temeiul fiecărei reguli e citat pe linie, din anaf_surse/cod_fiscal_227_2015_consolidat.txt (CF art.282, forma de la 01.03.2026).
Pe bază: schemă efemeră din tenant_template.sql, în ROLLBACK.
"""
import datetime as dt
import io
import os
import re

import pytest

from core import regim_tva_incasare as R

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = dt.date


# ── reguli pure ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _er(de_la, pana_la=None, platitor=True, tva_in=None, decont="lunar", altele=()):
    return R.valideaza(de_la, pana_la, platitor, tva_in, decont, altele)


def _forma(mesaj):
    """Structura unui refuz / avertisment, fără formularea lui: (articolele Codului fiscal citate, datele numite, în ordine). Regulile
    din `valideaza` care au același câmp se deosebesc prin ea (temeiul citat și datele pe care le numesc)."""
    return (re.findall(r"art\. (\d+ alin\. \([^)]+\))", mesaj), re.findall(r"\d{2}\.\d{2}\.\d{4}", mesaj))


def test_numai_la_firma_inregistrata_in_scopuri_de_tva():
    er, _ = _er(D(2026, 3, 1), platitor=False)
    # CF art.282 alin.(3^1) lit.a): eligibile sunt „persoanele impozabile înregistrate în scopuri de TVA conform art. 316”
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare", (["282 alin. (3^1)"], []))], er


def test_de_la_prima_zi_a_perioadei_fiscale_sau_data_inregistrarii():
    # CF art.282 alin.(3^1) lit.a): „aplică sistemul TVA la încasare începând cu prima zi a perioadei fiscale următoare celei în care […]
    # și-a exercitat opțiunea”
    assert _er(D(2026, 3, 1)) == ([], [])
    er, _ = _er(D(2026, 3, 15))
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare_de_la", (["282 alin. (3^1)"], ["15.03.2026"]))], er
    # CF art.282 alin.(3^1) lit.b): „Persoana impozabilă care optează pentru aplicarea sistemului TVA la încasare începând cu data
    # înregistrării în scopuri de TVA aplică sistemul TVA la încasare începând cu această dată.”
    assert _er(D(2026, 3, 15), tva_in=D(2026, 3, 15)) == ([], [])


def test_nu_inainte_de_inregistrarea_in_scopuri_de_tva():
    # CF art.282 alin.(3^1): numai persoanele „înregistrate în scopuri de TVA conform art. 316” — înainte de înregistrare nu se aplică
    er, _ = _er(D(2026, 2, 1), tva_in=D(2026, 3, 15))
    # (data înregistrării, apoi data „de la”), fără temei citat — altă regulă decât „prima zi a perioadei” (care îl citează)
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare_de_la", ([], ["15.03.2026", "01.02.2026"]))], er


def test_decont_trimestrial_inceput_in_mijlocul_trimestrului_e_avertisment():
    er, av = _er(D(2026, 2, 1), decont="trimestrial")
    # CF art.282 alin.(3^1): „prima zi a perioadei fiscale” — la decont trimestrial perioada e trimestrul; periodicitatea de atunci
    # poate fi alta decât cea de azi, deci avertisment, nu refuz
    assert er == [] and [_forma(m) for m in av] == [(["282 alin. (3^1)"], ["01.02.2026"])], (er, av)


def test_iesirea_la_sfarsitul_unei_perioade_fiscale():
    # CF art.282 alin.(5): „Radierea […] se realizează […] începând cu prima zi a perioadei fiscale următoare celei în care a fost depusă
    # notificarea” — ultima zi aplicată e sfârșitul unei perioade fiscale
    er, _ = _er(D(2026, 3, 1), D(2027, 6, 15))
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare_pana_la", (["282 alin. (5)"], ["15.06.2027"]))], er
    assert _er(D(2026, 3, 1), D(2027, 6, 30)) == ([], [])
    er, _ = _er(D(2026, 3, 1), D(2026, 2, 28))
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare_pana_la", ([], ["28.02.2026", "01.03.2026"]))], er   # „până la”, „de la”


def test_iesirea_inainte_de_sfarsitul_anului_optiunii_e_avertisment_nu_refuz():
    er, av = _er(D(2026, 3, 1), D(2026, 6, 30))
    # CF art.282 alin.(5): „obligată să aplice sistemul respectiv cel puțin până la sfârșitul anului calendaristic în care a optat […],
    # cu excepția situației în care în cursul aceluiași an cifra de afaceri depășește plafonul” — legea admite excepția: avertisment
    assert er == [] and [_forma(m) for m in av] == [(["282 alin. (5)"], ["31.12.2026", "30.06.2026"])], (er, av)


def test_perioadele_nu_se_suprapun():
    alta = {"id": 1, "de_la": D(2025, 1, 1), "pana_la": D(2025, 12, 31)}
    er, _ = _er(D(2025, 6, 1), altele=[alta])
    # o zi e sau nu e în sistem (CF art.282 alin.(3)): refuzul numește perioada existentă (`text_perioade`)
    assert [(c, _forma(m)) for c, m in er] == [("tva_incasare_de_la", ([], ["01.01.2025", "31.12.2025"]))], er
    assert _er(D(2026, 1, 1), altele=[alta]) == ([], [])


# ── ANAF: câmpurile RTVAI ───────────────────────────────────────────────────────────────────────────────────────────
def test_anaf_parseaza_toate_campurile_rtvai():
    from core import anaf_api
    # anaf_surse/doc_WS_V9.txt, inregistrare_RTVAI: „dataInceputTvaInc -- Data de la care aplica sistemul TVA la incasare”,
    # „dataSfarsitTvaInc -- Data pana la care aplica sistemul TVA la încasare”, „statusTvaIncasare”
    r = anaf_api._rtvai({"dataInceputTvaInc": "2026-03-01", "dataSfarsitTvaInc": "", "dataActualizareTvaInc": "2026-02-20",
                         "dataPublicareTvaInc": "2026-02-21", "tipActTvaInc": "Inregistrare", "statusTvaIncasare": True})
    assert (r["status"], r["data_inceput"], r["data_sfarsit"], r["data_actualizare"], r["data_publicare"], r["tip_act"]) == (
        True, "2026-03-01", None, "2026-02-20", "2026-02-21", "Inregistrare")
    # răspunsul real fără înregistrare (văzut 20.10.2026, CUI 14399840): toate șirurile goale, statusul false
    r0 = anaf_api._rtvai({"dataActualizareTvaInc": "", "dataPublicareTvaInc": "", "dataInceputTvaInc": "", "dataSfarsitTvaInc": "",
                          "tipActTvaInc": "", "statusTvaIncasare": False})
    assert (r0["status"], r0["data_inceput"], r0["data_sfarsit"]) == (False, None, None)
    assert anaf_api._rtvai({"dataInceputTvaInc": "01.03.2026"})["data_inceput"] is None   # altă formă: nu se ghicește


def test_compara_anaf_propune_si_spune_diferenta():
    rt = {"status": True, "data_inceput": "2026-03-01", "data_sfarsit": None, "brut": {}}
    v = R.compara_anaf(rt, None)
    # afirmație tipată (decizia 21.08): iConta și registrul ANAF diferă -> `contradictie`, cu amândouă sursele numite
    assert v["propunere"] == {"de_la": "2026-03-01", "pana_la": None} and v["fel"] == "contradictie" and len(v["sursele"]) == 2, v
    assert v["diferente"] == ["în iConta nu e înregistrată nicio perioadă"], v
    v = R.compara_anaf(rt, {"de_la": D(2026, 4, 1), "pana_la": None})
    assert v["diferente"] == ["„de la”: în iConta 01.04.2026, la ANAF 01.03.2026"], v
    v = R.compara_anaf(rt, {"de_la": D(2026, 3, 1), "pana_la": None})
    assert v["diferente"] == [] and v["fel"] == "fapt" and v["mesaj"].split(". ")[-1] == "coincide cu ce e scris în iConta.", v
    v = R.compara_anaf({"status": False, "data_inceput": None, "data_sfarsit": None,
                        "brut": {"dataInceputTvaInc": "01.03.2026"}}, None)
    # data din registru în altă formă se arată (citată), nu se propune
    assert re.findall(r"„([^”]+)”", v["mesaj"]) == ["01.03.2026"] and v["propunere"] is None and v["diferente"] == [], v


# ── pe bază ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_lot10_tvai"


@pytest.fixture
def cur():
    from core import db, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                c.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"),
                                                              encoding="utf-8").read(), SCH))
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                c.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_decont, platitor_tva_anaf_inceput) "
                          "VALUES (1, 'ZT', '14399840', true, 'lunar', '2025-01-01')")
                yield c
        finally:
            conn.rollback()


def _jurnal(c):
    c.execute("SELECT camp, valoare_veche, valoare_noua, user_id FROM firma_profil_jurnal ORDER BY id")
    return c.fetchall()


AZI = D(2026, 10, 20)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_intrarea_in_sistem_se_scrie_se_jurnalizeaza_si_aplica_de_la_data(cur):
    r = R.salveaza(cur, True, "2026-03-01", None, user_id=7, azi=AZI)
    assert r["ok"], r
    assert [(p["de_la"], p["pana_la"], p["sursa"]) for p in R.perioade(cur)] == [(D(2026, 3, 1), None, "manual")]
    # CF art.282 alin.(3): exigibilitatea la încasare pentru „persoane care aplică sistemul TVA la încasare” — de la data intrării
    assert R.aplica_la(cur, "2026-02-28") is False and R.aplica_la(cur, D(2026, 3, 1)) is True and R.aplica_la(cur, AZI) is True
    cur.execute("SELECT tva_la_incasare FROM firma_profil")
    assert cur.fetchone()[0] is True                       # indicatorul „azi”, sincronizat
    # PIVOT DECIZII 04.10.2026: „jurnalizarea fiecărei schimbări (utilizator, dată, vechi → nou)”
    assert _jurnal(cur) == [("tva_incasare_perioade", None, "de la 01.03.2026", 7), ("tva_la_incasare", "false", "true", 7)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_iesirea_inchide_perioada_si_o_noua_intrare_e_alta_perioada(cur):
    assert R.salveaza(cur, True, "2025-01-01", None, user_id=7, azi=AZI)["ok"]
    r = R.salveaza(cur, True, "2025-01-01", "2026-06-30", user_id=8, azi=AZI)        # ieșirea, la sfârșitul unei perioade
    assert r["ok"] and r["avertismente"] == [], r
    assert R.aplica_la(cur, "2026-06-30") is True and R.aplica_la(cur, "2026-07-01") is False
    cur.execute("SELECT tva_la_incasare FROM firma_profil")
    assert cur.fetchone()[0] is False
    r = R.salveaza(cur, True, "2027-01-01", None, user_id=8, azi=AZI)                 # după ieșire: perioadă nouă
    assert r["ok"], r
    assert [(p["de_la"], p["pana_la"]) for p in R.perioade(cur)] == [(D(2025, 1, 1), D(2026, 6, 30)), (D(2027, 1, 1), None)]
    assert R.aplica_la(cur, "2026-12-31") is False and R.aplica_la(cur, "2027-01-01") is True


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_refuzurile_nu_scriu_nimic(cur):
    r = R.salveaza(cur, True, "2026-03-15", None, user_id=7, azi=AZI)
    assert r["ok"] is False and r["camp"] == "tva_incasare_de_la", r      # CF art.282 alin.(3^1): prima zi a perioadei fiscale
    r = R.salveaza(cur, True, "2024-12-01", None, user_id=7, azi=AZI)
    assert (r["ok"], r["camp"], _forma(r["mesaj"])) == (False, "tva_incasare_de_la", ([], ["01.01.2025", "01.12.2024"])), r
    cur.execute("UPDATE firma_profil SET platitor_tva = false")
    r = R.salveaza(cur, True, "2026-03-01", None, user_id=7, azi=AZI)
    assert r["ok"] is False and r["camp"] == "tva_incasare", r             # CF art.282 alin.(3^1): numai înregistrate în scopuri de TVA
    assert R.perioade(cur) == [] and _jurnal(cur) == []
    assert R.salveaza(cur, True, "2026-03-01", None, user_id=None)["ok"] is False   # fără autor: nimic


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nu_cu_perioada_inregistrata_e_refuz_numit_iar_stergerea_e_jurnalizata(cur):
    assert R.salveaza(cur, True, "2026-03-01", None, user_id=7, azi=AZI)["ok"]
    r = R.salveaza(cur, False, user_id=7, azi=AZI)
    # CF art.282 alin.(5): ieșirea are o dată — refuzul numește perioada înregistrată
    assert (r["ok"], r["camp"], _forma(r["mesaj"])) == (False, "tva_incasare", ([], ["01.03.2026"])), r
    pid = R.perioade(cur)[0]["id"]
    assert R.sterge(cur, pid, 9, azi=AZI)["ok"]
    assert R.perioade(cur) == [] and R.aplica_la(cur, AZI) is False
    assert _jurnal(cur)[-2:] == [("tva_incasare_perioade", "de la 01.03.2026", None, 9), ("tva_la_incasare", "true", "false", 9)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_schimbarea_peste_o_luna_inchisa_e_refuzata_numai_daca_o_atinge(cur):
    cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 4)")
    r = R.salveaza(cur, True, "2026-03-01", None, user_id=7, azi=AZI)
    # [R46] perioadele decid exigibilitatea (CF art.282 alin.(3)) pe luni deja declarate: o schimbare peste aprilie 2026 rescrie trecutul
    from core.mesaje import MESAJ_PESTE_PERIOADA_INCHISA
    assert r == {"ok": False, "camp": "tva_incasare_de_la",
                 "mesaj": MESAJ_PESTE_PERIOADA_INCHISA % {"ce": "Regimul TVA la încasare", "an": 2026, "luna": 4}}, r
    assert R.salveaza(cur, True, "2026-05-01", None, user_id=7, azi=AZI)["ok"]   # de la o lună de după: nu atinge aprilie


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_perioade_raspunde_indicatorul_vechi_si_nu_il_stinge(cur):
    cur.execute("UPDATE firma_profil SET tva_la_incasare = true")
    # INTERPRETARE CU TEMEI (antetul `aplica_la`): firma marcată din ANAF la adăugare, fără dată, rămâne în sistem până i se scrie data
    assert R.aplica_la(cur, "2020-01-01") is True
    st = R.stare(cur, AZI)
    assert st["fara_data"] is True and st["aplica_azi"] is True and st["curenta"] is None, st
    assert R.salveaza(cur, False, user_id=7, azi=AZI)["ok"]                    # „Nu”: indicatorul se stinge, jurnalizat
    assert R.aplica_la(cur, AZI) is False and _jurnal(cur) == [("tva_la_incasare", "true", "false", 7)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_verificarea_anaf_se_consemneaza_pe_perioada(cur):
    assert R.salveaza(cur, True, "2026-03-01", None, user_id=7, azi=AZI)["ok"]
    v = R.compara_anaf({"status": True, "data_inceput": "2026-03-01", "data_sfarsit": None, "brut": {}}, R.perioade(cur)[-1])
    st = R.inregistreaza_anaf(cur, v)
    # pe perioadă se consemnează exact afirmația verificării (un „fapt”: registrul și iConta coincid)
    assert v["fel"] == "fapt" and st["curenta"]["verificat_anaf_la"] and st["curenta"]["stare_anaf"] == v["mesaj"], st


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_provizionarea_scrie_perioada_in_curs_din_anaf_si_nu_alta(cur):
    from core import tenant_provisioning as tp
    d = {"platitor_tva": True, "tva_la_incasare": True, "tva_data_inceput": "2025-01-01",
         "tva_incasare_rtvai": {"status": True, "data_inceput": "2026-03-01", "data_sfarsit": None}}
    assert tp.precompleteaza_din_anaf(cur.connection, SCH, d)
    assert [(p["de_la"], p["pana_la"], p["sursa"]) for p in R.perioade(cur)] == [(D(2026, 3, 1), None, "anaf")]
    cur.execute("DELETE FROM tva_incasare_perioade")
    d["tva_incasare_rtvai"] = {"status": False, "data_inceput": "2025-01-01", "data_sfarsit": "2025-12-31"}   # trecută: nu se scrie
    tp.precompleteaza_din_anaf(cur.connection, SCH, d)
    assert R.perioade(cur) == []
