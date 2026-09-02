# -*- coding: utf-8 -*-
"""GARD [02.09.2026, PRAG 1]: cheltuiala cu impozitul pe profit ramasa NEDEDUSA se SEMNALEAZA.

**DEFECTUL, masurat pe portofoliu** (`tenant_005`, anul 2025, in tura in care s-a scris regula 3
din `PLAN_LUCRU.md`). Contul 691 e un cont 6xx: intra in P2 si scade rezultatul. CF art.25
alin.(4) lit.a) il declara NEDEDUCTIBIL, iar formularul are randul lui — rd.23, verificat verbatim
in `anaf_surse/opanaf_206_2025_d101.txt`. Generatorul nu-l adauga inapoi (ajustarile fiscale sunt
ale contabilului) si **nu spunea nimic**: cu nota de impozit de 15.200 lei validata in evidenta,
acelasi D101 a coborat de la 15.200 la 12.768 lei. **2.432 lei sub impozitul datorat, in tacere.**

**DE CE SEMNAL, nu completare automata:** cat din soldul lui 691 merge la rd.23 e o decizie fiscala
(grup fiscal -> 694; regularizari de alt an). Rezerva legala (P13) se deriva automat fiindca
omisiunea ei SUPRA-declara; aici omisiunea SUB-declara, deci implicitul ar fi in defavoarea
corectitudinii. *Un implicit minte in amandoua directiile; diferenta e cine plateste minciuna.*

**CALIBRARE IN AMANDOUA DIRECTIILE** (METODA §22): fara nota pe 691 nu se semnaleaza nimic (altfel
avertismentul ar fi zgomot pe orice declaratie), iar cu rd.23 completat semnalul TACE (altfel
contabilul care a facut ajustarea ar fi certat pentru ea).
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import d101 as _d101          # noqa: E402
from core import db as _db              # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402
from core.common import Perioada        # noqa: E402

_SCHEMA = "ztest_d101_nededus"
#: Cheltuiala cu impozitul, inregistrata in evidenta. Nu e o valoare fiscala — e suma fixturii.
_IMPOZIT_691 = 5000


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _schema(cur, cu_691):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(
        open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute(
        "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, regim_fiscal, "
        "platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
        "VALUES (1,'PROBA NEDEDUS','14399840','Str. Test 1','Bucuresti','B','6202','real',"
        "true,'L','Pop','Ion','administrator')")
    # fixtura-sintetica-ok: schema EFEMERA, aruncata la rollback; anul e al fixturii, nu al bazei.
    cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere) "
                "VALUES ('2026-06-15','validata','test','Vanzare') RETURNING id")
    iid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                "VALUES (%s,'4111','707',100000)", (iid,))
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                "VALUES (%s,'607','401',60000)", (iid,))
    if cu_691:
        cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere) "
                    "VALUES ('2026-12-31','validata','test','Impozit pe profit') RETURNING id")
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                    "VALUES (%s,'691','4411',%s)", (nid, _IMPOZIT_691))


def _genereaza(cu_691, manual=None):
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                _schema(cur, cu_691)
            return _d101.genereaza(conn, _SCHEMA, Perioada(2026), manual)[1]
        finally:
            conn.rollback()


def _semnale(res):
    """Semnalul se recunoaste dupa PREFIXUL pe care modulul il DECLARA (`d101.PREFIX_AVERT_691`),
    nu dupa o bucata de proza copiata in gard. Asa, o reformulare a mesajului nu strica gardul si
    nici nu-l face sa treaca degeaba — METODA §23, structura in loc de text."""
    return [a for a in (res.avertismente or []) if a.startswith(_d101.PREFIX_AVERT_691)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cheltuiala_cu_impozitul_ramasa_nededusa_SE_SEMNALEAZA():
    """Directia care doare: 691 in evidenta, rd.23 gol -> impozit declarat mai mic decat cel datorat."""
    res = _genereaza(cu_691=True)
    semnale = _semnale(res)
    assert semnale, (
        "[anti-vacuu] 691 are rulaj debitor %d si rd.23 e %s, iar declaratia NU spune nimic — "
        "impozitul iese mai mic decat cel datorat, in tacere. Avertismente: %s"
        % (_IMPOZIT_691, res.P.get("P23"), res.avertismente))
    # Suma se cere ca NUMAR, parsat inapoi din mesaj — nu ca sub-sir (`"5000" in text` ar trece si
    # pe "15000"). Tiparul cerut e cel CANONIC (`pdf_util.bani`: 5.000,00), deci aserttiunea
    # verifica doua lucruri deodata: ca suma e acolo, si ca e scrisa in formatul romanesc.
    import re as _re
    from decimal import Decimal as _D
    numere = {_D(x.replace(".", "").replace(",", "."))
              for x in _re.findall(r"\d[\d.]*,\d\d", semnale[0])}
    assert _D(_IMPOZIT_691) in numere, (
        "semnalul nu poarta SUMA in format canonic, deci contabilul nu stie cat are de adaugat: "
        "%r (numere gasite: %s)" % (semnale[0], sorted(numere)))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_efectul_omisiunii_e_SUB_declarare_si_se_masoara():
    """Nu e o proprietate a mesajului, e una a CIFREI: fara nota pe 691, impozitul e mai mare.
    Fara aserttiunea asta, gardul ar pazi o fraza si nu efectul care costa la un control."""
    fara = _genereaza(cu_691=False)
    cu = _genereaza(cu_691=True)
    assert cu.P["P48"] < fara.P["P48"], (
        "cheltuiala cu impozitul nu mai scade impozitul declarat (%s vs %s) — daca s-a reparat "
        "prin adaugare automata la rd.23, semnalul asta nu-si mai are rostul si se scoate"
        % (cu.P["P48"], fara.P["P48"]))
    assert not _semnale(fara), (
        "se semnaleaza si cand nu exista nicio cheltuiala cu impozitul — atunci avertismentul e "
        "zgomot pe orice D101, iar contabilul se obisnuieste sa-l sara")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cand_contabilul_a_completat_rd23_semnalul_TACE():
    """A doua directie: ajustarea facuta nu se mai cere o data. Un semnal care nu se poate stinge
    prin actiunea ceruta e un semnal pe care omul invata sa-l ignore."""
    res = _genereaza(cu_691=True, manual={"P23": _IMPOZIT_691})
    assert res.P["P23"] == _IMPOZIT_691
    assert not _semnale(res), (
        "rd.23 e completat cu exact suma ceruta si semnalul persista: %s" % res.avertismente)
