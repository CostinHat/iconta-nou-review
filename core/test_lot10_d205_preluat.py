# -*- coding: utf-8 -*-
"""Lotul 10, decizia Costin B (verbatim în DECIZII, „Lotul 10: deciziile lui Costin la întrebările din lot”): la firma preluată,
dividendele plătite înainte de preluare există numai ca debit 457 în balanța importată — „Da, cu completare manuală”: controlul fiscal
arată D205 datorat; beneficiarii se completează manual (calea manuală existentă a D205).

Datele: `solduri_initiale.rulaj_an_debit` = rulajul 01.01 .. data preluării, fără soldul inițial (`core/rulaje_preluate.py`); debitul
457 = dividende plătite (structura ANAF D205 rd.39.b, divid_P „8.V. Dividende platite”). Temeiul obligației: OPANAF 179/2022 anexa 1,
instrucțiunile D205, cap.I pct.1 lit.a) — „Declaraţia se completează şi se depune de către plătitorii de venituri [...] pentru
următoarele tipuri de venituri: a) venituri din dividende”; cap.II pct.9 col.4 — „totalul venitului plătit acţionarilor sau
asociaţilor din dividendele distribuite, într-un an fiscal”. CNP 1800101400016 și CUI 14399840 cu cifra de control verificată."""
import datetime
import io
import os

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core.common import Perioada
from core.erori import RefuzGenerare

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot10_d205_preluat"
MOTIV = ("dividende plătite înainte de preluare (5.000,00 lei), din balanța de deschidere — beneficiarii se completează manual "
         "în D205")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def firma():
    """Firmă preluată la 30.06.2026: balanța de deschidere are pe 457 soldul inițial 5.000 (dividend distribuit în 2025) și rulajul
    debitor 5.000 (plătit în 2026, înainte de preluare); sold final 0. Niciun dividend în note."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1, 'PRELUATA TEST SRL', '14399840', 'Str. Test 1, Bucuresti', 'POPESCU', 'ION', 'ADMINISTRATOR')")
        cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 100)")
        cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta, si_an_debit, si_an_credit, "
                    "rulaj_an_debit, rulaj_an_credit) VALUES ('457', 0, 0, '2026-06-30', 0, 5000, 5000, 0)")
        c.commit()
    yield SCH
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _sql(q, a=()):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, a)
        c.commit()


def _nota(data, linii):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'dividende', 'operatiuni', "
                    "'ciorna', 'Hotărârea AGA nr 5') RETURNING id", (data,))
        nid = cur.fetchone()[0]
        for d, cc, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                        (nid, d, cc, s))
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
        c.commit()


def _genereaza(an, manual=None):
    from core import d205
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        return d205.genereaza(c, SCH, Perioada(an), manual)


def test_d205_fara_note_cu_457_preluat_cere_beneficiarii_manual(firma):
    with pytest.raises(RefuzGenerare) as e:
        _genereaza(2026)
    m = str(e.value)
    # decizia B: „beneficiarii se completează manual (calea manuală existentă a D205)” — refuzul spune ce și de unde
    assert m.startswith("D205 pe 2026: dividende plătite înainte de preluare (5.000,00 lei), din balanța de deschidere la 30.06.2026. "
                        "iConta.eu nu are notele acestor dividende, deci nici împărțirea lor pe asociați. Completează beneficiarii "
                        "manual în D205"), m


def test_d205_cu_note_dupa_preluare_si_457_preluat_tot_manual(firma):
    """Notele de după preluare nu fac declarația completă: plățile dinainte de preluare (balanța) n-au beneficiari în iConta.eu."""
    _nota("2026-09-01", [("117", "457", 3000), ("457", "5121", 3000)])
    with pytest.raises(RefuzGenerare) as e:
        _genereaza(2026)
    # același refuz ca fără note (balanța are plățile dinainte de preluare), care cere și dividendele din notele de după preluare
    assert str(e.value).startswith("D205 pe 2026: dividende plătite înainte de preluare (5.000,00 lei), din balanța de deschidere la "
                                   "30.06.2026. iConta.eu nu are notele acestor dividende"), str(e.value)
    assert str(e.value).endswith("în 2026, baza și impozitul — inclusiv dividendele din notele de după preluare."), str(e.value)


def test_d205_cu_beneficiarii_completati_manual_valid_la_duk(firma):
    from core import duk
    manual = {"beneficiari": [{"categ": "1.a", "nume": "POPESCU ION", "cif": "1800101400016", "divid_d": 0, "divid_p": 5000,
                               "baza": 0, "imp": 0}]}
    xml, res = _genereaza(2026, manual)
    # col.4 (divid_P) „totalul venitului plătit [...] într-un an fiscal” = 5.000; baza și impozitul în D205/2025 (anul distribuirii)
    assert [(b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res.beneficiari] == [(0, 5000, 0, 0)]
    if not duk.poate_valida("d205"):
        pytest.skip("validatorul DUK D205 nu e instalat")
    v = duk.valideaza(xml, "d205", an=2026)
    assert v["stare"] == "valid", v


def test_anul_de_dupa_preluare_se_genereaza_din_note(firma):
    _nota("2027-05-10", [("117", "457", 2000)])
    _xml, res = _genereaza(2027)
    assert [(b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res.beneficiari] == [(2000, 0, 2000, 320)]


def test_control_fiscal_d205_datorat_din_balanta_de_deschidere(firma):
    from core import control_fiscal_api, control_incrucisat
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        fapt, are_note = control_incrucisat.dividende_distribuite(c, SCH, 2026)
        # afirmația tipată (`core/afirmatii.py`, fel „fapt” pe an), cu motivul din comanda Costin
        assert (fapt["fel"], fapt["tip"], fapt["an"], fapt["motiv"], are_note) == ("fapt", "d205", 2026, MOTIV, False), fapt
        rez = control_fiscal_api.declaratii_fapt(c, SCH, {"platitor_tva": True}, datetime.date(2027, 2, 1))
    d205 = [d for d in rez["datorate"] if d["tip"] == "d205"]
    # înainte: niciun debit 457 în note -> „nu se poate verifica”, nu datorată
    assert [(d["an"], d["fapt"]) for d in d205] == [(2026, MOTIV)], rez
    assert not [n for n in rez["neclar"] if n.get("tip") == "d205"], rez["neclar"]


def test_ruta_declaratiilor_transmite_beneficiarii_manuali(firma, monkeypatch):
    """[lotul 10, decizia Costin B, sesiunea principală] Calea manuală nu era legată: `declaratii_api._d205` nu transmitea `manual`, deci
    refuzul trimitea la un formular care nu exista. Acum ecranul (formularul „Beneficiari completați manual”, `declaratii.js`) trimite
    `manual.beneficiari` (valorile din câmpuri, ca text), iar ruta le dă generatorului. MUTAȚIE: `b.get("manual")` scos din
    `declaratii_api._d205` -> refuzul revine -> pică."""
    # [lotul 10, 383] generarea cere perioada încheiată (`coada_api.perioada_neincheiata`); testul nu e despre poarta ei: generează ca
    # după încheierea perioadei (ceasul porții mutat peste perioadă), restul ceasului aplicației rămâne cel real
    import datetime as _dt383, functools as _ft383
    from core import coada_api as _coada383
    monkeypatch.setattr(_coada383, "perioada_neincheiata", _ft383.partial(_coada383.perioada_neincheiata,
                                                                          azi=_dt383.date(_dt383.date.today().year + 2, 1, 1)))
    from core import declaratii_api
    corp = {"an": 2026, "manual": {"beneficiari": [{"categ": "1.a", "nume": "POPESCU ION", "cif": "1800101400016", "divid_d": 0,
                                                    "divid_p": 5000, "baza": 0, "imp": 0}]}}
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        xml, res = declaratii_api.genereaza(c, SCH, "d205", corp)
    # OPANAF 179/2022 cap.II pct.9, col.4: „totalul venitului plătit [...] într-un an fiscal” — scris de contabil
    assert [(b.nume1, b.divid_p) for b in res.beneficiari] == [("POPESCU ION", 5000)]
