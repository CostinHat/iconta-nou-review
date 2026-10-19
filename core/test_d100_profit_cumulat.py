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
