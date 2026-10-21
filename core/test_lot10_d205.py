# -*- coding: utf-8 -*-
"""431 — D205 (lotul 10, comanda Costin 20.10.2026, verbatim): „D205 pe 2026 la F6 se oprește cu «D205 fără niciun beneficiar de
venit», deși există nota de dividende de 10.000 (ciornă). Mesajul nu spune unde se adaugă asociații, nici că nota nu e validată. Fluxul
e unul singur: asociații și cotele (cu istoricul cesiunilor) în datele firmei; nota de dividende împarte automat pe asociați; D205 preia
din notele validate; mesajul de refuz trimite la ce lipsește.”

Găsit pe drum (aceeași clasă, același flux): nota de dividende cu „Dividendul se plătește acum: Nu” înregistrează impozitul la
distribuire (457 = 446), iar D205 îl citea ca PLATĂ — un dividend neplătit ieșea cu baza = impozitul (1.600) și impozit pe impozit
(256). Și dividendele interimare (463 = 456, 456 = 446, 456 = 5121) nu se citeau deloc.

Temei: CF art.97 alin.(7) — „Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor
juridice, odată cu plata dividendelor”; CF art.7 pct.11 (dividendul = „o distribuire în bani sau în natură, efectuată de o persoană
juridică unui participant”); Legea 141/2025 art.VII alin.(2) (interimarele nu se recalculează la regularizare); D205: structura ANAF
(`anaf_surse/d205_struct_anaf.txt`, rd.39.a/39.b divid_D / divid_P) + validatorul DUK. CNP-uri sintetice cu cifra de control verificată."""
import datetime
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import dividende_curs as dc
from core import tenant_provisioning as _tprov
from core.common import Perioada

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot10_d205"
R16 = lambda d: Decimal("0.16")   # noqa: E731 — cota de la data distribuirii (2026+)


def _m(data, **k):
    return dict({"data": datetime.date(*data)}, **k)


# ── atribuirea plată -> distribuire (pur) ─────────────────────────────────────────────────────────────────────────────────────
def test_431_impozitul_inregistrat_la_distribuire_nu_e_plata():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600)]
    # CF art.97 alin.(7): impozitul se reține „odată cu plata dividendelor” — fără plată, nimic plătit în an (divid_P 0). [lotul 10,
    # decizia Costin A] impozitul distribuirii neplătite la 31.12 intră totuși în anul distribuirii (OPANAF 179/2022 cap.II pct.9:
    # „se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea dividendelor”) -> 1.600 pe 10.000
    assert dc.impozit_ponderat(m, 2026, R16) == (Decimal("1600.00"), 0, 10000)


def test_431_plata_netului_aduce_brutul_platit():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600), _m((2026, 6, 10), platit=8400)]
    imp, platit, dist = dc.impozit_ponderat(m, 2026, R16)
    assert (platit, dist) == (10000, 10000) and imp == Decimal("1600.00")


def test_431_plata_partiala_a_netului():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600), _m((2026, 6, 10), platit=4200)]
    _imp, platit, _d = dc.impozit_ponderat(m, 2026, R16)
    assert platit == 5000          # 4.200 net = jumătate din net -> jumătate din brut


def test_431_nota_cu_plata_in_aceeasi_nota_ramane_ca_inainte():
    m = [_m((2026, 5, 20), distribuit=10000, impozit=1600, platit=8400)]
    assert dc.impozit_ponderat(m, 2026, R16)[1] == 10000


def test_431_plata_fara_impozit_inregistrat_e_bruta_ca_inainte():
    """Regula de dinainte (test_d205_divid_platit): plată 6.000 pe o distribuire de 10.000 fără impozit înregistrat = 6.000 plătit."""
    m = [_m((2026, 3, 1), distribuit=10000), _m((2026, 4, 1), platit=6000)]
    assert dc.impozit_ponderat(m, 2026, R16)[1:] == (6000, 10000)


def test_431_dividendele_interimare_se_citesc():
    m = [_m((2026, 4, 30), distribuit_interimar=50000, impozit_interimar=8000), _m((2026, 5, 5), platit_interimar=42000)]
    # CF art.7 pct.11: interimarul e „o distribuire în bani [...] unui participant” — dividend, declarat la plată
    imp, platit, dist = dc.impozit_ponderat(m, 2026, R16)
    assert (platit, dist, imp) == (50000, 50000, Decimal("8000.00"))


def test_431_plata_pe_456_fara_interimar_nu_e_dividend():
    """Pe 456 se decontează și capitalul (aport, reducere): o plată 456 fără distribuire interimară deschisă nu se ia."""
    assert dc.impozit_ponderat([_m((2026, 5, 5), platit_interimar=7000)], 2026, R16) == (0, 0, 0)


def test_431_compensarea_cu_interimarele_nu_e_plata_noua():
    """Legea 141/2025 art.VII alin.(2): interimarele „fără recalcularea impozitului [...] după regularizarea acestora” — 457 = 463 nu e
    o plată nouă, iar dividendul anual compensat nu se mai socotește distribuit a doua oară."""
    m = [_m((2027, 4, 30), distribuit=30000, compensat=30000)]
    assert dc.impozit_ponderat(m, 2027, R16) == (0, 0, 0)


# ── refuzul fără beneficiari: cauza reală, cu trimiterea ─────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def firma():
    """Firmă în schemă EFEMERĂ (nicio tabelă `public.*` scrisă de D205), cu declarantul complet."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1, 'F6 TEST SRL', '14399840', 'Str. Test 1, Bucuresti', 'POPESCU', 'ION', 'ADMINISTRATOR')")
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
        return cur.fetchall() if cur.description else None


def _nota(data, linii, status="ciorna"):
    nid = _sql("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'dividende', 'operatiuni', "
               "'ciorna', 'Hotărârea AGA nr 3') RETURNING id", (data,))[0][0]
    for d, c, s in linii:
        _sql("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    if status == "validata":
        _sql("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
    return nid


def _genereaza():
    from core import d205
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        return d205.genereaza(c, SCH, Perioada(2026))


def _refuz(obiect=False):
    with pytest.raises(ValueError) as e:
        _genereaza()
    return e.value if obiect else str(e.value)


def test_431_fara_asociati_trimite_la_date_firma(firma):
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])
    r = _refuz(obiect=True)
    m = str(r)
    assert m.startswith("D205 pe 2026 fără niciun beneficiar de venit: firma nu are asociați înregistrați"), m
    # [431] „mesajul de refuz trimite la ce lipsește”: ecranul primește și unde se repară — Date firmă, cu „+ Asociat” adus în vedere
    # (MUTAȚIE: `ecran="date_firma"` scos -> pică)
    assert (r.ecran, r.camp_ecran, r.note) == ("date_firma", "as-adauga", []), r.detaliu()


def test_431_nota_ciorna_e_numita_si_trimisa_la_registrul_jurnal(firma):
    _sql("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 100)")
    nid = _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)])
    r = _refuz(obiect=True)
    m = str(r)
    # nota numită (data, suma, starea) și trimiterea la Registrul jurnal, de la începutul refuzului
    assert m.startswith("D205 pe 2026 fără niciun beneficiar de venit: nota de dividende din 20.05.2026 (10.000,00 lei) e ciornă. "
                        "D205 preia numai notele validate: valideaz-o în Registrul jurnal"), m
    # [431] nota de deschis, în forma pe care o citește `coada_trimite.legaturiNote` (MUTAȚIE: `note=[...]` scos -> pică)
    assert r.note == [{"nota_id": nid, "eticheta": "din 20.05.2026", "data": "2026-05-20"}], r.detaliu()


def test_431_distribuite_neplatite_nu_mai_sunt_motiv_de_refuz(firma):
    """[lotul 10, decizia Costin A, supersedează refuzul „D205 cuprinde dividendele plătite”] „D205 include și dividendele distribuite
    neplătite la 31.12, pe anul distribuirii, cu impozitul datorat” — cazurile complete în `test_lot10_d205_neplatite.py`."""
    _sql("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 100)")
    _nota("2026-05-20", [("117", "457", 10000), ("457", "446", 1600)], "validata")
    _xml, res = _genereaza()
    # OPANAF 179/2022 cap.II pct.9: impozitul distribuitelor neplătite „se cuprinde în declaraţia aferentă perioadei în care s-a
    # aprobat distribuirea dividendelor”
    assert [(b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res.beneficiari] == [(10000, 0, 10000, 1600)]


def test_431_doi_asociati_platiti_d205_valid_la_duk(firma):
    from core import duk
    _sql("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 60), ('IONESCU MARIA', '2850202400023', 40)")
    _nota("2026-05-20", [("117", "457", 6000), ("457", "446", 960), ("117", "457", 4000), ("457", "446", 640)], "validata")
    _nota("2026-06-10", [("457", "5121", 5040), ("457", "5121", 3360)], "validata")
    xml, res = _genereaza()
    # brutul plătit = netul (8.400) + impozitul reținut pe el (1.600); impozitul pe fiecare asociat
    assert [(b.nume1, b.divid_d, b.divid_p, b.baza1, b.imp1) for b in res.beneficiari] == [
        ("POPESCU ION", 6000, 6000, 6000, 960), ("IONESCU MARIA", 4000, 4000, 4000, 640)]
    if not duk.poate_valida("d205"):
        pytest.skip("validatorul DUK D205 nu e instalat")
    v = duk.valideaza(xml, "d205", an=2026)
    assert v["stare"] == "valid", v
