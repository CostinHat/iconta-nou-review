# -*- coding: utf-8 -*-
"""C5 + 277 — importul de extras bancar nu dublează mișcările și nu respinge mișcări noi.

C5 (audit 2026-09-17, decizia Costin 20.09 varianta A): reimportul aceluiași extras dubla `extras_linii`; reparat atunci cu idempotența pe
FIȘIER (hash de conținut, `extras_import`).
277 (comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.1a, verbatim în DECIZII — PIVOT peste varianta A): „o linie e duplicat numai dacă
aceeași mișcare (dată, sumă, sens, referință/descriere, cont) există deja.” Hash-ul fișierului respingea tot fișierul („Extras deja
importat: 2 linii”, F1, 16.10 13:18) și nu vedea un extras care se suprapune cu unul vechi. Acum cheia e mișcarea
(`reconciliere_api.cheie_miscare`), socotită cu multiplicitatea ei; răspunsul spune ce s-a găsit deja și ce e nou (pct.1c).

Temei: N/A — integritate tehnică (nu regulă fiscală). Principiu conex CLAUDE.md §8 (date nealterate).
Probe pe schema efemeră din template (gated DB), ROLLBACK la ieșire.
"""
import io
import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import reconciliere_api as _rec

_SCH = "efemer_c5_idem"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,
                           declarant_nume,declarant_prenume,declarant_functie,platitor_tva)
                           VALUES (1,'C5 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


_TZ = [{"data": "2026-03-10", "detalii": "PLATA FURNIZOR X", "suma": -119.00},
       {"data": "2026-03-11", "detalii": "INCASARE CLIENT Y", "suma": 238.00}]
_CONTINUT = b"data;detalii;suma\n2026-03-10;PLATA FURNIZOR X;-119.00\n2026-03-11;INCASARE CLIENT Y;238.00\n"


def _nr_linii(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_linii")
        return cur.fetchone()[0]


_TZ = [{"data": "2026-03-10", "detalii": "PLATA FURNIZOR X", "suma": -119.00},
       {"data": "2026-03-11", "detalii": "INCASARE CLIENT Y", "suma": 238.00}]
_CONTINUT = b"data;detalii;suma\n2026-03-10;PLATA FURNIZOR X;-119.00\n2026-03-11;INCASARE CLIENT Y;238.00\n"

#: fișierul din comanda Costin, 277 (F1, 16.10.2026)
MT940_277 = b""":20:EXTRAS20261016
:25:RO49AAAA1B31007593840000
:28C:00010/001
:60F:C261015RON10000,00
:61:2610161016C242,00NTRFNONREF
:86:Incasare FISCALOS ICONTA SRL CUI 55229657 contravaloare factura F1A4 din 16.10.2026
:61:2610161016D12,50NCHGNONREF
:86:Comision administrare cont octombrie
:62F:C261016RON10229,50
"""


def _nr_linii(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_linii")
        return cur.fetchone()[0]


def _importa_mt940(conn, continut, nume="extras.sta"):
    from core import banca_parser
    e = banca_parser.citeste_extras(continut, nume)
    r = _rec.importa_extras(conn, _SCH, e["tranzactii"], nume, continut, cont=e["cont"])
    conn.commit()
    return r


# ── 277: fișierul lui Costin se importă, apoi reimportul lui găsește ambele linii (nu „deja importat” pe fișier) ──
def test_277_extrasul_mt940_nou_se_importa_iar_reimportul_gaseste_liniile(conn):
    _rec.importa_extras(conn, _SCH, _TZ, "extras_martie.csv", _CONTINUT)   # un import vechi, pe altă lună
    conn.commit()
    r = _importa_mt940(conn, MT940_277)
    assert (r["rezumat"]["noi"], r["rezumat"]["deja"], len(r["linii"])) == (2, 0, 2), r["rezumat"]
    assert [x["suma"] for x in r["linii"]] == ["242.00", "12.50"]
    with conn.cursor() as cur:
        cur.execute("SELECT suma, tip, cont_extras, referinta FROM extras_linii WHERE data = '2026-10-16' ORDER BY id")
        assert [(str(a), b, c, d) for a, b, c, d in cur.fetchall()] == [
            ("242.00", "incasare", "RO49AAAA1B31007593840000", None), ("12.50", "plata", "RO49AAAA1B31007593840000", None)]
    r2 = _importa_mt940(conn, MT940_277)                                      # același fișier, a doua oară
    assert (r2["rezumat"]["noi"], r2["rezumat"]["deja"], r2["linii"]) == (0, 2, []), r2["rezumat"]
    assert [d["descriere"][:20] for d in r2["deja"]] == ["Incasare FISCALOS IC", "Comision administrar"]
    assert _nr_linii(conn) == 4


def test_277_extrasul_care_se_suprapune_adauga_numai_miscarea_noua(conn):
    """Același cont, a doua zi: extrasul repetă cele două linii din 16.10 și aduce una nouă. Cu hash-ul pe fișier (conținut diferit)
    cele două vechi se dublau; acum: 1 nouă, 2 găsite."""
    _importa_mt940(conn, MT940_277)
    al_doilea = MT940_277.replace(b":62F:", b":61:2610171017D50,00NTRFREF77\n:86:Plata furnizor Z\n:62F:")
    r = _importa_mt940(conn, al_doilea, "extras_2.sta")
    assert (r["rezumat"]["noi"], r["rezumat"]["deja"]) == (1, 2), r["rezumat"]
    assert [(x["data"], x["suma"]) for x in r["linii"]] == [("2026-10-17", "50.00")]
    with conn.cursor() as cur:
        cur.execute("SELECT referinta FROM extras_linii WHERE data = '2026-10-17'")
        assert cur.fetchone()[0] == "REF77"


def test_277_alt_cont_alta_referinta_alt_sens_nu_sunt_aceeasi_miscare(conn):
    """Fiecare element al cheii, schimbat singur, face mișcarea nouă (nu „găsită deja”): contul, referința, sensul, suma, data,
    descrierea. MUTAȚIE: un element scos din `cheie_miscare` -> rândul lui pică."""
    _importa_mt940(conn, MT940_277)
    variante = {
        "cont": MT940_277.replace(b"RO49AAAA1B31007593840000", b"RO66BACX0000001234567890"),
        "referinta": MT940_277.replace(b"C242,00NTRFNONREF", b"C242,00NTRFOP555"),
        "sens": MT940_277.replace(b"C242,00NTRF", b"D242,00NTRF"),
        "suma": MT940_277.replace(b"C242,00NTRF", b"C242,01NTRF"),
        "data": MT940_277.replace(b":61:2610161016C242", b":61:2610171017C242"),
        "descriere": MT940_277.replace(b"factura F1A4", b"factura F1A5"),
    }
    noi = {}
    for k, v in variante.items():
        r = _importa_mt940(conn, v, "v_%s.sta" % k)
        noi[k] = r["rezumat"]["noi"]
    # la „cont”, ambele linii sunt pe alt cont; la celelalte, numai încasarea s-a schimbat
    assert noi == {"cont": 2, "referinta": 1, "sens": 1, "suma": 1, "data": 1, "descriere": 1}, noi


# ── CALIBRARE (fără over-dedup): două tranzacții REALE identice în ACELAȘI fișier -> AMBELE păstrate; reimportul le găsește pe amândouă ──
def test_C5_doua_tranzactii_identice_in_acelasi_fisier_ambele_pastrate(conn):
    tz = [{"data": "2026-05-02", "detalii": "COMISION CARD", "suma": -5.00},
          {"data": "2026-05-02", "detalii": "COMISION CARD", "suma": -5.00}]
    cont = b"data;detalii;suma\n2026-05-02;COMISION CARD;-5.00\n2026-05-02;COMISION CARD;-5.00\n"
    r = _rec.importa_extras(conn, _SCH, tz, "mai.csv", cont)
    conn.commit()
    assert r["rezumat"]["noi"] == 2 and _nr_linii(conn) == 2
    tz3 = tz + [{"data": "2026-05-02", "detalii": "COMISION CARD", "suma": -5.00}]   # al treilea comision, în extrasul următor
    r = _rec.importa_extras(conn, _SCH, tz3, "mai_2.csv")
    conn.commit()
    assert (r["rezumat"]["noi"], r["rezumat"]["deja"]) == (1, 2), "multiplicitatea: 3 în fișier, 2 existente -> 1 nouă"
    assert _nr_linii(conn) == 3


# ── C5 păstrat: reimportul aceluiași fișier NU dublează (acum: toate liniile găsite deja) ──
def test_C5_reimport_acelasi_fisier_nu_dubleaza(conn):
    r1 = _rec.importa_extras(conn, _SCH, _TZ, "extras_martie.csv", _CONTINUT)
    conn.commit()
    assert r1["rezumat"]["noi"] == 2 and _nr_linii(conn) == 2
    r2 = _rec.importa_extras(conn, _SCH, _TZ, "extras_martie.csv", _CONTINUT)
    conn.commit()
    assert (r2["rezumat"]["noi"], r2["rezumat"]["deja"], r2["linii"]) == (0, 2, [])
    assert _nr_linii(conn) == 2
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_import")
        assert cur.fetchone()[0] == 1, "registrul fișierelor: același conținut, un singur rând"


def test_C5_fara_continut_tot_pe_miscare(conn):
    """Fără `continut` (apel programatic) cheia e tot mișcarea — înainte, fără hash, nu se verifica nimic și se dubla."""
    _rec.importa_extras(conn, _SCH, _TZ, "x.csv")
    _rec.importa_extras(conn, _SCH, _TZ, "x.csv")
    conn.commit()
    assert _nr_linii(conn) == 2


# ── 276b: soldurile extrasului față de 5121 ──
def test_276_soldurile_extrasului_fata_de_5121(conn):
    import datetime
    with conn.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES ('5121', 9000, 0, '2026-09-30')")
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-10-10', 'incasare', 'manual', 'validata') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 1000)", (iid,))
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-10-16', 'ciorna', 'manual', 'ciorna') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 77)", (iid,))
    conn.commit()
    from core import banca_parser
    e = banca_parser.citeste_extras(MT940_277, "x.sta")
    s = _rec.compara_solduri(conn, _SCH, e["sold_initial"], e["sold_final"])
    assert s == {"cont": "5121", "valuta": "RON",
                 "initial": {"data": "2026-10-15", "extras": "10000.00", "contabil": "10000.00", "diferenta": "0.00"},
                 "final": {"data": "2026-10-16", "extras": "10229.50", "contabil": "10000.00", "diferenta": "229.50"}}, s
    assert _rec.compara_solduri(conn, _SCH, None, None) is None, "extrasul în tabel n-are solduri"
    inainte = dict(e["sold_initial"], data="2026-09-01")
    assert _rec.compara_solduri(conn, _SCH, inainte, None)["initial"]["contabil"] is None, "înainte de preluare: necunoscut"
    assert datetime.date(2026, 10, 15)  # data soldului = sfârșitul zilei din `:60F:`
