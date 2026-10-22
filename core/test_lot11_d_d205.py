# -*- coding: utf-8 -*-
"""[lotul 11] D205 — două decizii ale lui Costin (10.3, verbatim în DECIZII „Comanda 10.3” pct.4):

  B. „D205 pe anii depuși după regula veche: fără rectificative.” Regula nouă (lotul 10, decizia A: dividendele distribuite neplătite
     la 31.12 intră pe anul distribuirii) e în aplicație de la publicarea lotului 10 (restartul din 21.10.2026 16:24:12, DECIZII
     „Comanda 10.3” pct.1). Ce făcea aplicația: pe un an cu D205 depusă după regula veche, generarea producea o D205 nouă după regula
     nouă, care intra în coadă și la depunere devenea a doua depunere pe an (`coada_api.marcheaza_depusa`: nr_depunere = MAX + 1) —
     o rectificativă. Acum: refuzul cu motivul numit, pe ambele drumuri (automat și beneficiari manuali).
  C. „Semaforul D205 numără 457 preluat ca incomplet până la completarea manuală.” Ce făcea: la firma preluată cu 457 în balanța de
     deschidere, D205 intra în `datorate` (de urmărit / restanță), deși generarea automată e refuzată (`d205.refuz_preluate`). Acum:
     stă la „nu se poate verifica” (necunoaștere, cu motivul „incompletă până la completarea manuală”) până e depusă sau în coadă cu
     beneficiarii scriși manual.

Fixturile scriu în `public.tenants` / `public.declaratii_depuse` / `public.declaratii_coada` numai în ROLLBACK, pe anul SINTETIC 2099
(CLAUDE.md „Testele nu presupun gol un interval unde pot ajunge date reale”), cu o schemă efemeră din tenant_template.
CNP-uri sintetice cu cifra de control verificată (algoritmul din CLAUDE.md): 1800101400016; CUI 14399840 (verificat)."""
import datetime
import io
import os

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core.common import Perioada
from core.erori import RefuzGenerare

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot11_d_d205"
AN = 2099   # fixtura-sintetica-ok: an sintetic, evident nereal, în ROLLBACK
# semaforul se uită la D205 pe anul trecut față de „azi”; tabelul sărbătorilor (`scadente.sarbatori_legale`) acoperă până la 2099,
# deci „azi” = 20.02.2099 și anul D205 = 2098 — tot sintetic
AN_S = 2098  # fixtura-sintetica-ok
BENEF = [{"categ": "1.a", "nume": "POPESCU ION", "cif": "1800101400016", "divid_d": 1000, "divid_p": 1000, "baza": 1000, "imp": 160}]


@pytest.fixture()
def firma():
    """(conn, tenant_id): schemă efemeră + rândul ei în public.tenants, totul în tranzacția testului, anulată la final."""
    try:
        _db.init_pool()
        conn = _db.pool().getconn()
    except Exception:
        pytest.skip("DB indisponibil")
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, declarant_nume, declarant_prenume, declarant_functie) "
                        "VALUES (1, 'DIVIDENDE L11 SRL', '14399840', 'Str. Test 1, Bucuresti', 'POPESCU', 'ION', 'ADMINISTRATOR')")
            cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU ION', '1800101400016', 100)")
            cur.execute("INSERT INTO public.tenants (schema_name, nume) VALUES (%s, 'DIVIDENDE L11 SRL') RETURNING id", (SCH,))
            tid = cur.fetchone()[0]
        yield conn, tid
    finally:
        conn.rollback()
        _db.pool().putconn(conn)


def _depusa(conn, tid, data, sursa="iconta", an=AN):
    # fixtura-sintetica-ok: anul vine ca PARAMETRU (2099 / 2098), tenant_id sintetic (rând nou în public.tenants), totul în ROLLBACK
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, data_depunere, sursa) "
                    "VALUES (%s, %s, 12, 'd205', '<x/>', %s, %s)", (tid, an, data, sursa))


def _preluat_457(conn, platit=5000):
    """Balanța de deschidere cu rulajul anului pe 457 (firma preluată în 2098): dividende plătite înainte de preluare."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta, si_an_debit, si_an_credit, "
                    "rulaj_an_debit, rulaj_an_credit) VALUES ('457', 'Dividende de plata', 0, 0, %s, 0, 0, %s, %s)",
                    (datetime.date(AN_S, 6, 30), platit, platit))


def _genereaza(conn, manual=None):
    from core import d205
    return d205.genereaza(conn, SCH, Perioada(AN), manual)


# ---------------------------------------------------------------- B: fără rectificative pe anii regulii vechi
@pytest.mark.parametrize("manual", [None, {"beneficiari": BENEF}], ids=["automat", "manual"])
def test_an_depus_dupa_regula_veche_nu_mai_genereaza(firma, manual):
    conn, tid = firma
    _depusa(conn, tid, "2026-09-01 10:00:00+03")          # înainte de publicarea regulii noi (21.10.2026 16:24:12)
    with pytest.raises(RefuzGenerare) as ei:
        _genereaza(conn, manual)
    m = ei.value.args[0]   # mesajul refuzului (câmpul lui), nu reprezentarea excepției
    # decizia Costin 10.3: „D205 pe anii depuși după regula veche: fără rectificative.” — motivul numit, cu data depunerii
    assert m == ("D205 pe 2099 e depusă prin iConta.eu la 01.09.2026, după regula de atunci: baza și impozitul pe dividendele plătite în "
                 "an. Regula de acum (dividendele distribuite în an, plătite sau nu la 31.12, cu impozitul lor) se aplică numai anilor "
                 "nedepuși: pentru anii depuși după regula veche nu se face rectificativă (decizia din 21.10.2026), deci iConta.eu nu mai "
                 "generează D205 pe 2099."), m   # mesajul întreg (core/test_garzi_pe_text.py)


def test_an_depus_dupa_regula_noua_nu_e_refuzat_pe_motivul_regulii(firma):
    conn, tid = firma
    _depusa(conn, tid, "2026-10-21 16:30:00+03")          # după publicare: depunerea e deja după regula nouă
    xml, res = _genereaza(conn, {"beneficiari": BENEF})
    assert [b.baza1 for b in res.beneficiari] == [1000]


def test_depunerea_marcata_extern_nu_e_regula_aplicatiei(firma):
    conn, tid = firma
    _depusa(conn, tid, "2026-09-01 10:00:00+03", sursa="extern")   # conținut făcut în afara aplicației: regula veche nu e a lui
    xml, res = _genereaza(conn, {"beneficiari": BENEF})
    assert [b.imp1 for b in res.beneficiari] == [160]


# ---------------------------------------------------------------- C: semaforul, 457 preluat = incomplet
def _fapt(conn):
    from core import control_fiscal_api as cf
    return cf.declaratii_fapt(conn, SCH, {"platitor_tva": True}, datetime.date(AN_S + 1, 2, 20))


def test_semafor_457_preluat_necompletat_e_incomplet(firma):
    conn, _tid = firma
    _preluat_457(conn)
    r = _fapt(conn)
    assert not [d for d in r["datorate"] if d["tip"] == "d205"], r["datorate"]
    n = [x for x in r["neclar"] if x["tip"] == "d205"]
    # decizia Costin 10.3: „Semaforul D205 numără 457 preluat ca incomplet până la completarea manuală.”
    assert len(n) == 1 and n[0]["fel"] == "necunoastere", n
    assert n[0]["motiv"].startswith("D205 pe 2098 — incompletă până la completarea manuală: dividende plătite înainte de preluare "
                                    "(5.000,00 lei)"), n[0]["motiv"]


def test_semafor_457_preluat_depus_redevine_obligatie(firma):
    conn, tid = firma
    _preluat_457(conn)
    _depusa(conn, tid, "2099-02-10 10:00:00+02", sursa="extern", an=AN_S)
    r = _fapt(conn)
    assert [d["an"] for d in r["datorate"] if d["tip"] == "d205"] == [AN_S]
    assert not [x for x in r["neclar"] if x["tip"] == "d205"]


def test_semafor_457_preluat_in_coada_cu_beneficiari_manuali_e_completat(firma):
    conn, tid = firma
    _preluat_457(conn)
    import json
    # fixtura-sintetica-ok: anul 2098 sintetic, tenant_id sintetic, în ROLLBACK
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload) "
                    "VALUES (0, %s, 'd205', '2098', 'la_senior', %s::jsonb)",
                    (tid, json.dumps({"_an": AN_S, "_cerere": {"manual": {"beneficiari": BENEF}}})))
    r = _fapt(conn)
    assert [d["an"] for d in r["datorate"] if d["tip"] == "d205"] == [AN_S]


def test_semafor_fara_preluat_neschimbat(firma):
    conn, _tid = firma
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'dividende', 'operatiuni', "
                    "'validata', 'Hotărârea AGA nr 3') RETURNING id", (datetime.date(AN_S, 5, 20),))
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '117', '457', 1000)", (nid,))
    r = _fapt(conn)
    assert [d["an"] for d in r["datorate"] if d["tip"] == "d205"] == [AN_S]
    assert not [x for x in r["neclar"] if x["tip"] == "d205"]
