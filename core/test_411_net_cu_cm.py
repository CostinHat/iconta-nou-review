# -*- coding: utf-8 -*-
"""[deficiența 411, retestul Costin 19.10.2026, PRIORITAR] „Stat de plată cu CM (F5 Ionescu Vasile 10/2026, CM cod 01 13–15.10): net în
stat/compoziție/fluturaș 2.612,18 (fără CM) — corect 2.765,18; cost total angajator fără indemnizația brută 262; pe fluturaș «Deducere
personală 865,00» printre rețineri ca sumă pozitivă.”

Temei:
- OUG 158/2005 art.36 alin.(3) lit.a): „Plata indemnizațiilor se face lunar de către: a) angajator, cel mai târziu odată cu lichidarea
  drepturilor salariale pe luna respectivă” — netul de plată al lunii = salariul net + indemnizația netă (aceeași sumă ca fișierul de
  plată, `plata_salarii`);
- OUG 158/2005 art.12 alin.(1): primele zile de incapacitate se suportă de angajator — partea lui din indemnizație e cost al lui;
- CF art.78 alin.(2) lit.a): impozitul se calculează pe venitul net minus deducerea personală — deducerea scade baza, nu se reține.
Schemă efemeră din template, în tranzacție anulată."""
import pytest

from core import db as _db, perioada as _per, stat_plata_api as sp, tenant_provisioning as _tp

SCHEMA = "ztest_411_net_cm"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def stat():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,email,telefon,"
                            "regim_fiscal,platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                            "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','BCR','RO49RNCB0000000000000001',"
                            "'a@b.ro','0700000000','profit',true,'L','Pop','Ion','administrator')")
                # CNP 1900101410011 — cifra de control verificată (algoritmul din CLAUDE.md), ca în test_exces_vacanta_d112
                cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,judet_casa) VALUES "
                            "('1900101410011','IONESCU','VASILE','2024-01-01',8,'B') RETURNING id, data_angajare), "
                            "i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, 4050 FROM s) "
                            "SELECT id FROM s")
                sid = cur.fetchone()[0]
                # CM cod 01, 13–15.10.2026: 3 zile, toate suportate de angajator (primele 5 zile)
                cur.execute("INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, baza, media_zilnica, procent, "
                            "diminuare, zile_platite, zile_ang, zile_fnuass, brut_ang, brut_fnuass, cass, impozit, cas, net, serie, numar, "
                            "loc_prescriere, data_acordare, data_inceput, data_sfarsit) VALUES (%s,2026,10,'01',3,262,24300,116.45,75,false,"
                            "3,3,0,262,0,26,17,66,153,'AB','1234567',1,'2026-10-13','2026-10-13','2026-10-15')", (sid,))
            _per.confirma(c, SCHEMA, 2026, 10, "pontaj", user_id=1)
            yield [r for r in sp.stat_final(c, SCHEMA, 2026, 10) if r["id"] == sid][0]
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_netul_de_plata_cuprinde_indemnizatia_si_costul_partea_angajatorului(stat):
    r = stat
    assert r["cm_zile"] == 3 and r["cm_net"] > 0, r
    assert r["net_de_plata"] == pytest.approx(r["net"] + r["cm_net"], abs=0.001) and r["net_de_plata"] > r["net"], r
    assert float(sp.de_plata(r)) == pytest.approx(r["net_de_plata"], abs=0.001)          # fișierul de plată = fluturașul
    assert (r["cm_brut_ang"], r["cost_total"]) == (262.0, pytest.approx(r["cost"] + 262, abs=0.001)), r
    comp = sp.compozitie_fluturas(r)
    totaluri = [(c["eticheta"], c["valoare"]) for c in comp if c["fel"] == sp.FEL_TOTAL]
    assert totaluri == [("Net de plată (salariu + indemnizație CM)", r["net_de_plata"])], totaluri
    linii = [(c["eticheta"], c["valoare"]) for c in comp if c["fel"] == sp.FEL_LINIE]
    assert linii[-2:] == [("Salariu net", r["net"]), ("Indemnizație CM (netă)", r["cm_net"])], linii
    note = {c["eticheta"]: c["valoare"] for c in comp if c["fel"] == sp.FEL_NOTA}
    assert note["Cost total angajator (cu indemnizația CM suportată de angajator)"] == r["cost_total"], note


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_deducerea_nu_sta_printre_retineri(stat):
    """Deducerea personală: rând de defalcare a impozitului (FEL_DETALIU), sub el, nu o linie a compoziției netului."""
    comp = sp.compozitie_fluturas(stat)
    et = [c["eticheta"] for c in comp]
    i_imp = et.index("Impozit pe venit")
    assert (comp[i_imp + 1]["eticheta"], comp[i_imp + 1]["fel"], comp[i_imp + 1]["valoare"]) == (
        "  în calculul impozitului, scade baza (nu se reține): deducere personală", sp.FEL_DETALIU, stat["deducere_baza"]), comp
    assert [c for c in comp if c["fel"] == sp.FEL_LINIE and c["eticheta"].startswith("Deducere")] == []


def test_fara_cm_netul_ramane_salariul_net():
    r = {"brut": 4050, "cas": 1012.5, "cass": 405, "impozit_salariu": 197, "net": 2435.5, "deducere": 0, "deducere_baza": 0,
         "cost": 4141.13, "cam": 91.13}
    sp._cu_de_plata(r)
    comp = sp.compozitie_fluturas(r)
    assert [(c["eticheta"], c["valoare"]) for c in comp if c["fel"] == sp.FEL_TOTAL] == [("Salariu net", 2435.5)]
    assert {c["eticheta"]: c["valoare"] for c in comp if c["fel"] == sp.FEL_NOTA}["Cost total angajator"] == 4141.13


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_413_tariful_orar_al_salariului_de_baza(stat):
    """[deficiența 413] „Ore suplimentare: aplicația propune suma (tarif orar × ore × (1+spor)), avertizează la spor < 75% (Codul muncii
    art.123 alin.2).” Tariful = salariul de bază / orele normei lunii (zile lucrătoare ale lunii × ore pe zi): 4.050 / (22 × 8) în 10/2026
    (zilele lucrătoare din `scadente.zile_lucratoare_luna`, fără sărbători)."""
    from core import scadente
    zile = scadente.zile_lucratoare_luna(2026, 10)
    assert stat["tarif_orar"] == round(4050 / (zile * 8), 4), (stat["tarif_orar"], zile)   # round-ok: aceeași rotunjire ca a rândului


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_412_functia_din_cor_pe_adeverinta(monkeypatch):
    """[deficiența 412] „Adeverință: Funcția [...] se precompletează din fișă.” Funcția necompletată = ocupația COR a salariatului
    (nomenclatorul COR, public.cor_ocupatii), nu „___”."""
    import io as _io
    from pypdf import PdfReader
    from core import adeverinta as ad
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,declarant_nume,declarant_prenume,declarant_functie,patron_nume) "
                            "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Pop','Ion','administrator','Pop Ion')")
                cur.execute("WITH s AS (INSERT INTO salariati (cnp,nume,prenume,data_angajare,ore_zi,cor) VALUES "
                            "('1900101410011','IONESCU','VASILE','2024-01-01',8,'241107') RETURNING id, data_angajare), "
                            "i AS (INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, 4050 FROM s) "
                            "SELECT id FROM s")
                sid = cur.fetchone()[0]
            pdf = ad.pdf(c, SCHEMA, sid, {"scop": "grădiniță", "tip_contract": "nedeterminata", "an": 2026, "luna": 10})
            text = " ".join(" ".join(p.extract_text().split()) for p in PdfReader(_io.BytesIO(pdf)).pages)
            assert text.count("în funcția de auditor financiar (cod COR 241107)") == 1, text
        finally:
            c.rollback()
