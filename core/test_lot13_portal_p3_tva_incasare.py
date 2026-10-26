# -*- coding: utf-8 -*-
"""[lotul 13, comanda 13.1] Deficiența 541 — Date firmă → TVA la încasare.

Comanda 13.1, verbatim: „Pe 22.10.2026 s-a salvat «Aplică de la 01.10.2026» fără avertisment: opțiunea nu se aplică retroactiv în perioada
în curs, ci din prima zi a perioadei fiscale următoare (art. 282; F2 trimestrială → 01.01.2027). Aplicația refuză sau propune data corectă.
Jurnalul perioadelor există (de la / până la / sursă / verificat ANAF), dar nu arată cine și când a schimbat, iar «Sșterge» scoate perioada
fără urmă.”

TEMEI (citat verbatim din anaf_surse/cod_fiscal_227_2015_consolidat.txt, forma în vigoare de la 01.03.2026):
  CF art.282 alin.(3^1) lit.a): „Persoana impozabilă care în anul precedent nu a aplicat sistemul TVA la încasare, dar a cărei cifră de
  afaceri este inferioară plafonului […] și care optează pentru aplicarea sistemului TVA la încasare, aplică sistemul TVA la încasare
  începând cu prima zi a perioadei fiscale următoare celei în care persoana impozabilă și-a exercitat opțiunea”;
  lit.b): „Persoana impozabilă care optează pentru aplicarea sistemului TVA la încasare începând cu data înregistrării în scopuri de TVA
  aplică sistemul TVA la încasare începând cu această dată. Persoana impozabilă care optează […] ulterior, în cursul anului înregistrării în
  scopuri de TVA, aplică sistemul TVA la încasare începând cu prima zi a perioadei fiscale următoare celei în care și-a exercitat opțiunea”.

Pe bază: schemă efemeră din tenant_template.sql + migrarea lotului (`core/migrare_tva_incasare_perioade_optiune.py`, coloana nouă — până la
aplicarea peticului pe șablon), în ROLLBACK. MUTAȚII: `erori_optiune` întoarce [] -> testele refuzului ROȘII; `istoric_perioade` fără
perioadele scoase -> `test_541_stergerea_lasa_urma_cu_cine_si_cand` ROȘU.
"""
import datetime as _dt
import io
import os

import pytest

from core import regim_tva_incasare as R

D = _dt.date
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZI = D(2026, 10, 22)          # ziua din comandă: „Pe 22.10.2026 s-a salvat «Aplică de la 01.10.2026»”


# ── regula pură ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_541_perioada_urmatoare_luna_si_trimestrul():
    assert R.perioada_urmatoare(D(2026, 10, 22), "trimestrial") == D(2027, 1, 1)     # comanda: „F2 trimestrială → 01.01.2027”
    assert R.perioada_urmatoare(D(2026, 9, 20), "trimestrial") == D(2026, 10, 1)
    assert R.perioada_urmatoare(D(2026, 10, 22), "lunar") == D(2026, 11, 1)
    assert R.perioada_urmatoare(D(2026, 12, 5), "lunar") == D(2027, 1, 1)
    assert R.inceput_perioada(D(2026, 11, 30), "trimestrial") == D(2026, 10, 1)


def test_541_f2_trimestriala_de_la_01_10_scrisa_pe_22_10_se_refuza_cu_01_01_2027():
    """Cazul din comandă. ROȘU înainte: salvat fără niciun cuvânt."""
    er = R.erori_optiune(D(2026, 10, 1), None, "trimestrial", "2026-03-15", AZI)
    assert [c for c, _m in er] == ["tva_incasare_de_la"], er
    m = er[0][1]
    assert "trimestrul IV 2026" in m and "01.01.2027" in m and "art. 282 alin. (3^1) lit. a)" in m and "Data notificării" in m, m


def test_541_cu_notificarea_din_perioada_anterioara_01_10_e_corect():
    """Notificarea depusă pe 20.09.2026 (trimestrul III) -> sistemul de la 01.10.2026: corect, fără refuz."""
    assert R.erori_optiune(D(2026, 10, 1), D(2026, 9, 20), "trimestrial", "2026-03-15", AZI) == []


def test_541_cu_notificarea_din_perioada_in_curs_propune_data_corecta():
    er = R.erori_optiune(D(2026, 10, 1), D(2026, 10, 22), "trimestrial", "2026-03-15", AZI)
    assert len(er) == 1 and er[0][0] == "tva_incasare_de_la" and "se aplică de la 01.01.2027" in er[0][1], er
    assert R.erori_optiune(D(2027, 1, 1), D(2026, 10, 22), "trimestrial", "2026-03-15", AZI) == []
    er = R.erori_optiune(D(2026, 11, 1), D(2026, 10, 22), "trimestrial", "2026-03-15", AZI)   # lună din mijlocul trimestrului
    assert len(er) == 1 and "01.01.2027" in er[0][1], er


def test_541_lunar_propune_luna_urmatoare():
    er = R.erori_optiune(D(2026, 10, 1), None, "lunar", "2020-01-01", AZI)
    assert len(er) == 1 and "octombrie 2026" in er[0][1] and "01.11.2026" in er[0][1], er


def test_541_notificarea_in_viitor_se_refuza():
    er = R.erori_optiune(D(2027, 1, 1), D(2026, 12, 1), "trimestrial", None, AZI)
    assert [c for c, _m in er] == ["tva_incasare_data_optiune"], er


def test_541_trecutul_dinaintea_perioadei_in_curs_si_viitorul_trec():
    """Firmă preluată, cu opțiunea veche (01.07.2026, înainte de trimestrul în curs) și o intrare viitoare (01.01.2027): fără refuz."""
    assert R.erori_optiune(D(2026, 7, 1), None, "trimestrial", "2020-01-01", AZI) == []
    assert R.erori_optiune(D(2027, 1, 1), None, "trimestrial", "2020-01-01", AZI) == []


def test_541_de_la_inregistrarea_in_scopuri_de_tva_lit_b():
    """lit.b) teza a 2-a: opțiunea de la înregistrarea în scopuri de TVA (15.10.2026) se aplică de la acea dată, chiar în perioada în curs."""
    assert R.erori_optiune(D(2026, 10, 15), None, "lunar", "2026-10-15", AZI) == []
    assert R.erori_optiune(D(2026, 10, 15), D(2026, 10, 15), "lunar", "2026-10-15", AZI) == []
    er = R.erori_optiune(D(2026, 11, 1), D(2026, 10, 10), "lunar", "2026-10-15", AZI)
    assert len(er) == 1 and "15.10.2026" in er[0][1] and "lit. b)" in er[0][1], er


def test_541_avertismentul_pe_perioada_scrisa_retroactiv_date_existente():
    """Datele existente (perioada F2 scrisă pe 22.10.2026, de la 01.10.2026, fără data notificării): avertismentul derivat din `creat_la`."""
    p = {"sursa": "manual", "data_optiune": None, "de_la": D(2026, 10, 1), "creat_la": _dt.datetime(2026, 10, 22, 19, 12)}
    a = R.avertisment_optiune(p, "trimestrial")
    assert a and "01.01.2027" in a and "22.10.2026" in a, a
    assert R.avertisment_optiune(dict(p, data_optiune=D(2026, 9, 20)), "trimestrial") is None
    assert R.avertisment_optiune(dict(p, sursa="anaf"), "trimestrial") is None
    assert R.avertisment_optiune(dict(p, de_la=D(2027, 1, 1)), "trimestrial") is None


# ── pe bază ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
SCH = "ztest_lot13_tvai"
AUTOR = {}   # utilizatorul care „scrie” perioadele (pus de fixture)


@pytest.fixture
def cur():
    from core import db, migrare_tva_incasare_perioade_optiune as _mig, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                c.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                _mig.aplica(conn, SCH)
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                c.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_decont, platitor_tva_anaf_inceput) "
                          "VALUES (1, 'ZT', '14399840', true, 'trimestrial', '2026-03-15')")
                # autorul: un utilizator al bazei de test (patronul cabinetului de test al plasei), numele lui cum îl arată jurnalul
                c.execute("SELECT id, COALESCE(NULLIF(TRIM(CONCAT_WS(' ', prenume, nume)), ''), email) FROM public.users "
                          "WHERE email = 'patron@prisma-cont.test'")
                AUTOR["uid"], AUTOR["nume"] = c.fetchone()
                yield c
        finally:
            conn.rollback()


def test_541_salvarea_refuza_si_cu_notificarea_scrie_si_jurnalizeaza(cur):
    r = R.salveaza(cur, True, "2026-10-01", None, user_id=AUTOR["uid"], azi=AZI)
    assert r["ok"] is False and r["camp"] == "tva_incasare_de_la" and "01.01.2027" in r["mesaj"], r
    assert R.perioade(cur) == []                                               # refuzul nu scrie nimic
    r = R.salveaza(cur, True, "2026-10-01", None, user_id=AUTOR["uid"], azi=AZI, data_optiune="2026-09-20")
    assert r["ok"], r
    (p,) = R.perioade(cur)
    assert (p["de_la"], p["data_optiune"]) == (D(2026, 10, 1), D(2026, 9, 20)), p
    cur.execute("SELECT camp, valoare_veche, valoare_noua FROM firma_profil_jurnal WHERE camp LIKE 'tva_incasare%%' ORDER BY id")
    assert cur.fetchall() == [("tva_incasare_perioade", None, "de la 01.10.2026"), ("tva_incasare_data_optiune", None, "20.09.2026")]
    st = r["stare"]
    assert st["perioade"][0]["scrisa"]["cine"] == AUTOR["nume"] and st["perioade"][0]["scrisa"]["la"], st["perioade"]
    assert st["avertismente"] == [], st["avertismente"]


def test_541_data_din_registrul_anaf_nu_se_mai_judeca(cur):
    """„de la” egal cu data din Registrul ANAF (citit de `uc_regim_tva_incasare` chiar înainte): faptul ANAF, fără refuz."""
    r = R.salveaza(cur, True, "2026-10-01", None, user_id=AUTOR["uid"], azi=AZI, de_la_anaf="2026-10-01")
    assert r["ok"], r


def test_541_stergerea_lasa_urma_cu_cine_si_cand(cur):
    """ROȘU înainte: după „Șterge”, perioada dispărea din tabel fără urmă."""
    assert R.salveaza(cur, True, "2027-01-01", None, user_id=AUTOR["uid"], azi=AZI)["ok"]
    pid = R.perioade(cur)[0]["id"]
    assert R.sterge(cur, pid, AUTOR["uid"], azi=AZI)["ok"]
    st = R.stare(cur, AZI)
    assert st["perioade"] == []
    assert [(x["text"], x["cine"], x["inlocuita_cu"]) for x in st["scoase"]] == [("de la 01.01.2027", AUTOR["nume"], None)], st["scoase"]
    assert st["scoase"][0]["la"]


def test_541_corectura_arata_perioada_inlocuita(cur):
    assert R.salveaza(cur, True, "2027-01-01", None, user_id=AUTOR["uid"], azi=AZI)["ok"]
    assert R.salveaza(cur, True, "2027-04-01", None, user_id=AUTOR["uid"], azi=AZI)["ok"]      # corectura „de la”
    st = R.stare(cur, AZI)
    assert [p["de_la"] for p in st["perioade"]] == ["2027-04-01"]
    assert [(x["text"], x["inlocuita_cu"]) for x in st["scoase"]] == [("de la 01.01.2027", "de la 01.04.2027")], st["scoase"]
