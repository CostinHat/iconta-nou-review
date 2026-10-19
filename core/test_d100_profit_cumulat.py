# -*- coding: utf-8 -*-
"""D100 pe impozitul pe profit, pe rezultatul fiscal CUMULAT (deficiențele 377 și 378, comanda Costin 8.2, verbatim în DECIZII „Comanda 8.2”).

Temeiul (anaf_surse/cod_fiscal_227_2015_consolidat.html; anaf_surse/opanaf_587_2016_*):
- CF art.41 alin.(1): „Calculul, declararea și plata impozitului pe profit [...] se efectuează trimestrial, până la data de 25 inclusiv a
  primei luni următoare încheierii trimestrelor I-III.”
- CF art.19 alin.(1): rezultatul fiscal = venituri − cheltuieli − venituri neimpozabile − deduceri + cheltuieli nedeductibile.
- OPANAF 587/2016 anexa 4 pct.3.1.2: impozitul se calculează cumulat de la începutul anului și se declară diferența față de trimestrul
  anterior; trimestrul cu pierdere se declară cu 0.
Schema efemeră din tenant_template, ROLLBACK la final; trimestrele depuse (tabelul partajat `public.declaratii_depuse`) vin prin depozit,
înlocuit în test — interogarea lui reală e probată de e2e (`test_def_377_…`).
"""
import pytest

from core import d100
from core import db as _db, tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "test_d100_profit_cumulat"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _nota(cur, data, deb, cre, suma):
    cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere,document_ref) VALUES (%s,'validata','t','N','DOC') RETURNING id", (data,))
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,%s,%s,%s)",
                (cur.fetchone()[0], deb, cre, suma))


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET search_path TO %s, public" % _SCHEMA)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                        "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA PROFIT SRL','14399840','Str 1','Buc','B','6202',"
                        "'BCR','RO49RNCB0000000000000001','profit',true,'T','Pop','Ion','administrator')")
            _nota(cur, "2026-01-15", "5311", "704", 10000)      # T1: profit 10.000
            _nota(cur, "2026-08-14", "5311", "704", 5000)       # T3: profit 5.000
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _depuse(monkeypatch, randuri):
    monkeypatch.setattr(d100._repo, "d100_depuse_an", lambda cur, schema, an: randuri)


def _103(res):
    return [int(o.suma_dat) for o in res.obligatii if str(o.cod_oblig) == "103"]


def test_378_ajustarile_intra_in_rezultatul_fiscal_cumulat(conn, monkeypatch):
    """Venituri cumulate 15.000 + cheltuieli nedeductibile 1.000 (rd.33, T3) -> profit impozabil 16.000 -> impozit cumulat 2.560; T1 nedepus
    (stabilit 1.600, restanță pe T1), T2 stabilit 0 -> de plată pe T3/2026: 2.560 − 1.600 = 960.
    MUTAȚIA: `ajustari_fiscale.cumulat` întors gol în `_impozit_cumulat` -> 800 (fără rd.33) -> ROȘU."""
    from core import ajustari_fiscale as af
    with conn.cursor() as cur:
        af.adauga(cur, _SCHEMA, 2026, 3, "P33", 1000, "amendă")
    _depuse(monkeypatch, [])
    xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    # CF art.19 alin.(1): „[...] la care se adaugă cheltuielile nedeductibile” -> 15.000 + 1.000 = 16.000; cota 16% (CF art.17) -> 2.560
    assert res.profit["cumulat"] == 2560
    # OPANAF 587/2016 anexa 4 pct.3.1.2: se declară diferența față de cumulatul trimestrelor anterioare (T1 stabilit 1.600)
    assert _103(res) == [960], res.obligatii
    assert res.profit["avertismente"][0] == ("D100 pe T1/2026 nu e depus: impozitul stabilit pe T1/2026 (1.600,00 lei) se declară pe T1/2026, nu "
                                             "aici — e restanță pe T1/2026."), res.profit["avertismente"]


def test_377_trimestrul_declarat_inainte_de_preluare_se_scade(conn, monkeypatch):
    """D100 T1 depus în vechiul program, preluat din istoric cu suma 1.600 -> D100 T3 scade 1.600 și spune de unde vine cifra.
    MUTAȚIA: ramura „depus” din `profit_trimestru` care ignoră suma (0) -> 2.400 -> ROȘU."""
    import datetime as _dt
    _depuse(monkeypatch, [(3, {"obligatii": [{"cod_oblig": "103", "suma_plata": 1600}]}, "migrare", _dt.date(2026, 4, 25))])
    xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    # CF art.41 alin.(1) + OPANAF 587/2016 pct.3.1.2: impozitul cumulat 2.400 (16% din 15.000) − declarat pe T1 1.600 − T2 0 = 800
    assert _103(res) == [800], res.obligatii
    assert res.sinteza[4] == "deja declarat pe T1/2026: 1.600,00 lei (preluat din istoric la migrare (depus pe 25.04.2026))", res.sinteza


def test_377_trimestrul_depus_fara_suma_opreste_calculul(conn, monkeypatch):
    """Un trimestru consemnat ca depus, fără suma păstrată: impozitul lui s-ar cere încă o dată — refuz numit, nu 0 tacit.
    MUTAȚIA: `if suma is None: raise` înlocuit cu `suma = 0` -> ROȘU."""
    import datetime as _dt
    _depuse(monkeypatch, [(3, None, "migrare", _dt.date(2026, 4, 25))])
    with pytest.raises(ValueError, match="fără suma declarată"):
        d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))


def test_376_t4_se_definitiveaza_in_d101(conn):
    """CF art.41 alin.(1): trimestrial numai „pentru trimestrele I-III”; T4 -> D101."""
    with pytest.raises(ValueError, match="trimestrul IV se definitivează în D101"):
        d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=4))


def test_xml_e_valid_la_duk(conn, monkeypatch):
    """Judecătorul final: validatorul oficial DUK, pe XML-ul generat (cod 103, suma cumulată)."""
    from core import duk
    _depuse(monkeypatch, [])
    xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    v = duk.valideaza(xml, "d100", an=2026, luna=9)
    assert v["stare"] == "valid", "DUK a respins D100: %s" % v


def test_376_trimestrul_cu_pierdere_se_declara_cu_0_si_e_valid_la_duk(conn, monkeypatch):
    """Semaforul cere D100 pe fiecare trimestru I–III la impozitul pe profit, și pe cel cu pierdere (`cu_baza_venituri=False`):
    generatorul trebuie să-l poată produce, cu 0, iar validatorul să-l primească.
    OPANAF 587/2016 anexa 4 pct.3.1.2: „În situația în care, în perioada de raportare s-a înregistrat pierdere fiscală [...] la rândul 1
    din formular se va înscrie cifra 0”."""
    from core import duk
    with conn.cursor() as cur:
        _nota(cur, "2026-08-20", "628", "5311", 40000)      # T3: cheltuieli 40.000 > venituri cumulate 15.000 -> pierdere fiscală
    _depuse(monkeypatch, [])
    xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    assert _103(res) == [0], res.obligatii
    v = duk.valideaza(xml, "d100", an=2026, luna=9)
    assert v["stare"] == "valid", "DUK a respins D100 cu 0: %s" % v


# ── 378, lotul 9 (retestul 19.10.2026): rândul 25 se umple din contul 6581 ────────────────────────────────────────────────────────
@pytest.fixture
def conn_amenda(conn):
    """Cazul din retest, refăcut cu cifre minime: venituri cumulate 4.600, amenda 100 pe 6581 validată pe 30.09 (6581 = 5311),
    rezultatul contabil 4.500; T1 depus cu 600 lei."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM inregistrari_linii; DELETE FROM inregistrari")
        _nota(cur, "2026-01-15", "5311", "704", 3750)
        _nota(cur, "2026-08-14", "5311", "704", 850)
        _nota(cur, "2026-09-30", "6581", "5311", 100)
    return conn


def _linia(linii, inceput):
    """Singura linie care începe cu `inceput` (un mesaj al aplicației se compară întreg, nu prin sub-șir)."""
    gasite = [x for x in linii if x.startswith(inceput)]
    assert len(gasite) == 1, (inceput, linii)
    return gasite[0]


def _t1_depus_600(monkeypatch):
    import datetime as _dt
    _depuse(monkeypatch, [(3, {"obligatii": [{"cod_oblig": "103", "suma_plata": 600}]}, "iconta", _dt.date(2026, 4, 24))])


def test_378_amenda_pe_6581_intra_la_nedeductibile_din_cont(conn_amenda, monkeypatch):
    """Retestul 19.10: nedeductibile 0, profit 4.500, impozit 720, de plată 120. Corect: nedeductibile 100, profit 4.600, impozit 736,
    de plată 136.
    MUTAȚIA: `din_conturi` întors gol în `_impozit_cumulat` -> 120 -> ROȘU."""
    _t1_depus_600(monkeypatch)
    xml, res = d100.genereaza(conn_amenda, _SCHEMA, Perioada(2026, trim=3))
    P = res.profit["P"]
    # CF art.25 alin.(4) lit.b): „[...] amenzile, confiscările și penalitățile, datorate către autoritățile române/străine [...]” nu sunt
    # deductibile -> rd.25 = rulajul 6581 = 100; CF art.19 alin.(1): rezultatul fiscal = 4.500 + 100 = 4.600
    assert (P["P25"], P["P34"], P["P40"]) == (100, 100, 4600), P
    # CF art.17: 16% × 4.600 = 736; OPANAF 587/2016 pct.3.1.2: − 600 declarat pe T1 = 136
    assert res.profit["cumulat"] == 736 and _103(res) == [136], res.obligatii
    assert _linia(res.sinteza, "deduceri:") == (
        "deduceri: 0,00 lei; venituri neimpozabile: 0,00 lei; cheltuieli nedeductibile: 100,00 lei (din care rd.25 — amenzi, majorări și "
        "penalități (art.25 alin.(4) lit.b), din contul 6581 — despăgubiri, amenzi și penalități: 100,00 lei — scrie rândul în Registrul "
        "de evidență fiscală dacă o parte e deductibilă)")


def test_378_randul_scris_in_registru_inlocuieste_contul(conn_amenda, monkeypatch):
    """Partea deductibilă din 6581 (o despăgubire contractuală) se scoate scriind rândul 25: cifra omului înlocuiește contul, nu se adună.
    MUTAȚIA: în `calcul_cu_ajustari`, `din_conturi` aplicat peste registru (fără `if k not in I`) -> rd.25 = 100 -> ROȘU."""
    from core import ajustari_fiscale as af
    with conn_amenda.cursor() as cur:
        af.adauga(cur, _SCHEMA, 2026, 3, "P25", 40, "amenda ITM; restul e penalitate contractuală")
    _t1_depus_600(monkeypatch)
    xml, res = d100.genereaza(conn_amenda, _SCHEMA, Perioada(2026, trim=3))
    # CF art.19 alin.(1): 4.500 + 40 = 4.540; 16% = 726,4 -> 726 (rotunjit la leu); − 600 = 126
    assert res.profit["P"]["P25"] == 40 and _103(res) == [126], (res.profit["P"].get("P25"), res.obligatii)
    assert _linia(res.sinteza, "deduceri:") == ("deduceri: 0,00 lei; venituri neimpozabile: 0,00 lei; cheltuieli nedeductibile: 40,00 "
                                                "lei")   # fără „din care … din contul 6581”: cifra omului înlocuiește contul


def test_378_d101_ia_acelasi_rand_din_cont(conn_amenda):
    """Aceeași regulă în D101 (o singură sursă): rd.25 = 100 din 6581.
    MUTAȚIA: `din_conturi=` scos din `d101.genereaza` -> rd.25 = 0 -> ROȘU."""
    from core import d101
    xml, res = d101.genereaza(conn_amenda, _SCHEMA, Perioada(2026))
    # CF art.25 alin.(4) lit.b) -> rd.25 = 100; CF art.19 alin.(1) -> rd.40 = 4.600
    assert (res.P["P25"], res.P["P40"]) == (100, 4600), res.P


def test_378_d100_cu_amenda_e_valid_la_duk(conn_amenda, monkeypatch):
    """Judecătorul final pe XML-ul cu rd.25 derivat."""
    from core import duk
    _t1_depus_600(monkeypatch)
    xml, res = d100.genereaza(conn_amenda, _SCHEMA, Perioada(2026, trim=3))
    v = duk.valideaza(xml, "d100", an=2026, luna=9)
    assert v["stare"] == "valid", "DUK a respins D100: %s" % v


# ── 382, lotul 9: amortizarea în ciornă și notele nevalidate se spun la generare ──────────────────────────────────────────────────
def _amortizare_in_ciorna(cur):
    """Un mijloc fix de 12.000 lei, pus în funcțiune pe 15.12.2025, 60 de luni, liniar -> 200 lei/lună din 01/2026; amortizarea 01–07/2026
    generată și nevalidată (ciornă), 08–09/2026 validată."""
    cur.execute("INSERT INTO mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,valoare,dnf_luni,data_pif,metoda) "
                "VALUES ('MF1','Laptop','2131','2813',12000,60,'2025-12-15','liniara')")
    for luna in range(1, 10):
        cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere,document_ref) VALUES (%s,%s,'amortizare','Amortizare','AM') "
                    "RETURNING id", ("2026-%02d-28" % luna, "ciorna" if luna <= 7 else "validata"))
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'6811','2813',200)",
                    (cur.fetchone()[0],))


def test_382_d100_spune_amortizarea_nevalidata_din_fereastra_cumulata(conn_amenda, monkeypatch):
    """Retestul 19.10: „D100 T3/2026 calculează fără ea și nu avertizează nimic”. Acum avertismentul numește lunile, contul și suma, iar
    ciornele (din toată fereastra 01.01 – 30.09) sunt numite.
    MUTAȚIA: `avert.extend(_d101.avertismente_evidenta(...))` scos din `profit_trimestru` -> ROȘU."""
    with conn_amenda.cursor() as cur:
        _amortizare_in_ciorna(cur)
    _t1_depus_600(monkeypatch)
    xml, res = d100.genereaza(conn_amenda, _SCHEMA, Perioada(2026, trim=3))
    assert _linia(res.avertismente, "Amortizarea") == (
        "Amortizarea pe 01–07/2026 (contul 2813, 1.400,00 lei) e generată, dar nevalidată: D100 pe T3/2026 se calculează fără ea, deci "
        "profitul și impozitul ies mai mari. Validează notele de amortizare în Registrul jurnal, apoi generează din nou.")
    assert _linia(res.avertismente, "D100 pe T3/2026 nu cuprinde").startswith(
        "D100 pe T3/2026 nu cuprinde 7 note nevalidate din 01.01.2026 – 30.09.2026: nota din 28.01.2026 — AM, 200,00 lei;")


def test_382_d101_spune_amortizarea_neinregistrata(conn_amenda, monkeypatch):
    """Aceeași regulă la D101 (anul): fără nicio notă de amortizare, lunile încheiate apar „neînregistrate”.
    MUTAȚIA: `res.avertismente.extend(avertismente_evidenta(...))` scos din `d101.genereaza` -> ROȘU."""
    import datetime as _dt
    from core import common, d101
    monkeypatch.setattr(common, "azi_ro", lambda: _dt.date(2026, 10, 19))   # ultima lună încheiată: 09/2026
    with conn_amenda.cursor() as cur:
        cur.execute("INSERT INTO mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,valoare,dnf_luni,data_pif,metoda) "
                    "VALUES ('MF1','Laptop','2131','2813',12000,60,'2025-12-15','liniara')")
    xml, res = d101.genereaza(conn_amenda, _SCHEMA, Perioada(2026))
    assert _linia(res.avertismente, "Amortizarea") == (
        "Amortizarea pe 01–09/2026 (contul 2813, 1.800,00 lei) e neînregistrată: D101 pe 2026 se calculează fără ea, deci profitul și "
        "impozitul ies mai mari. Generează-o din Închidere lună („Generează amortizarea restantă”) și valideaz-o, apoi generează din nou.")


def test_382_d100_micro_numeste_nota_de_venit_nevalidata(conn):
    """Micro: o notă de venit nevalidată în trimestru se numește (impozitul pe venituri n-o cuprinde).
    MUTAȚIA: avertismentul scos din ramura micro a lui `d100.genereaza` -> ROȘU."""
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET regim_fiscal='micro'")
        cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere,document_ref) VALUES ('2026-08-20','ciorna','t','Vânzare','F9') "
                    "RETURNING id")
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'5311','704',300)",
                    (cur.fetchone()[0],))
    xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    assert _linia(res.avertismente, "D100 pe T3/2026 nu cuprinde") == (
        "D100 pe T3/2026 nu cuprinde 1 notă nevalidată din 01.07.2026 – 30.09.2026: nota din 20.08.2026 — F9, 300,00 lei. "
        "Validează în Registrul jurnal înainte de depunere și generează din nou.")


def test_382_fereastra_documentelor_d100_la_profit_e_cumulata(conn):
    """Documentele pe care se sprijină D100 T3 la profit sunt ale ferestrei 01.01 – 30.09 (calculul e cumulat): o notă din ianuarie
    validată după generare o face depășită. La micro fereastra rămâne trimestrul.
    MUTAȚIA: ramura „d100 la profit” scoasă din `coada_api.fereastra_perioadei` -> 2026-07-01 -> ROȘU."""
    from core import coada_api
    with conn.cursor() as cur:
        assert coada_api.fereastra_perioadei(cur, _SCHEMA, "d100", 2026, None, 3) == ("2026-01-01", "2026-10-01")
        cur.execute("UPDATE firma_profil SET regim_fiscal='micro'")
        assert coada_api.fereastra_perioadei(cur, _SCHEMA, "d100", 2026, None, 3) == ("2026-07-01", "2026-10-01")
