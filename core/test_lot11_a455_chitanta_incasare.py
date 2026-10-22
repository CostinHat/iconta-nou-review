# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 456] „încasarea în numerar de la o firmă se salvează fără chitanță. Emite automat chitanța, cu seria firmei și
PDF.”

Drumul: Casă -> „+ Dispoziție nouă” -> Încasare client (5311=4111) -> factura bifată -> „Adaugă” (`POST /casa/operatiuni`,
`uc_tenants.casa_adauga`). Până azi scria operațiunea și nota, fără chitanță; chitanța se emitea numai din detaliul facturii („Emite
chitanță”, `uc_tenants.chitanta_emite`). Acum încasarea facturii emite chitanța pe același drum (`chitanta_serie_sau_refuz`,
`chitanta_scrie`): seria firmei din Date firmă, numărul următor, legată de operațiune, de notă și de factură; fără serie, refuz numit cu
„Deschide Date firmă”.

Temei: OMFP 2634/2015 anexa 2, Chitanța (cod 14-4-1), anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt: „Chitanța și chitanța pentru
operațiuni în valută sunt documente justificative de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a
încasărilor și plăților efectuate în numerar (lei/valută) [...] Se întocmește pentru fiecare sumă încasată, de către casierul entității și
se semnează de acesta pentru primirea sumei.”

Schemă efemeră din template, în tranzacție anulată. Factura de PORNIRE scrisă direct (declarat): emiterea facturii nu e obiectul probei.
"""
import contextlib
import io
import pathlib
from decimal import Decimal

import pytest

from core import casa_api as _ca, db as _db, erori as _erori, tenant_provisioning as _tp

_SCH = "efemer_lot11_a455_ch"
_RAD = pathlib.Path(__file__).resolve().parent.parent
CUI_CLIENT = "55229657"   # FISCALOS ICONTA S.R.L. (din comanda lui Costin) — cifra de control verificată (algoritmul CUI din CLAUDE.md)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def conn(monkeypatch):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(_RAD / "tenant_template.sql", encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
                cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                               declarant_functie,platitor_tva,activitate_exceptata_amef,serie_chitanta)
                               VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true,false,'CHF1')""")
            proxy = _FaraCommit(c)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCH)
            monkeypatch.setattr(_uc, "_schema_sau_404", lambda *a, **k: _SCH)
            yield c
        finally:
            c.rollback()


def _factura(conn, numar="12", total="64.46"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip_operatiune) "
                    "VALUES ('F1A', %s, '2026-10-20', 'emisa', %s, 0, 'FISCALOS ICONTA S.R.L.', %s, 'emisa', 'normal') RETURNING id",
                    ("F1A" + numar, Decimal(total), CUI_CLIENT))
        return cur.fetchone()[0]


def _incaseaza(fid, suma="64.46", **k):
    from core import uc_tenants
    corp = {"data": "2026-10-22", "categorie": "incasare_client", "suma": suma, "partener": "FISCALOS ICONTA S.R.L.",
            "cui": CUI_CLIENT, "facturi": [{"factura_id": fid, "suma": suma}] if fid else []}
    corp.update(k)
    return uc_tenants.casa_adauga(1, corp, {"uid": 1})


def _chitante(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT serie, numar, data::text, factura_id, client_nume, client_cui, suma, reprezentand, casa_operatiune_id, "
                    "inregistrare_id, anulata FROM chitante ORDER BY id")
        return cur.fetchall()


def test_incasarea_facturii_din_casa_emite_chitanta_cu_seria_firmei(conn):
    """Cazul F1 (încasarea de 64,46 lei a facturii F1A12 din 22.10, salvată fără chitanță): acum chitanța CHF1 nr. 1, cu data
    operațiunii, clientul și „contravaloare factura” de pe factură, legată de operațiune și de notă; documentul operațiunii și al notei e
    numărul ei; factura încasată integral devine încasată; PDF-ul se generează."""
    from core import uc_tenants
    fid = _factura(conn)
    r = _incaseaza(fid)
    (op,) = r["operatiuni"]
    # OMFP 2634/2015 14-4-1: „Se întocmește pentru fiecare sumă încasată” — o chitanță pe încasare, seria firmei (anexa 1 pct.24)
    assert [(c["serie"], c["numar"], c["factura_id"], c["operatiune_id"]) for c in r["chitante"]] == [("CHF1", 1, fid, op["id"])]
    assert _chitante(conn) == [("CHF1", 1, "2026-10-22", fid, "FISCALOS ICONTA S.R.L.", CUI_CLIENT, Decimal("64.46"),
                                "contravaloare factura F1A nr. 12 din 20.10.2026", op["id"], op["inregistrare_id"], False)]
    with conn.cursor() as cur:
        cur.execute("SELECT o.document, i.document_ref, f.platita_la IS NOT NULL FROM casa_operatiuni o JOIN inregistrari i "
                    "ON i.id = o.inregistrare_id JOIN facturi f ON f.id = %s WHERE o.id = %s", (fid, op["id"]))
        assert cur.fetchone() == ("CHF1-1", "CHF1-1", True)
    reg = _ca.registru(conn, _SCH, 2026, 10)
    (rand,) = reg["operatiuni"]
    assert (rand["chitanta_id"], rand["fara_chitanta"], rand["document"]) == (r["chitante"][0]["chitanta_id"], False, "CHF1-1")
    pdf, _r = uc_tenants.chitanta_pdf(1, r["chitante"][0]["chitanta_id"], {"uid": 1})
    assert pdf[:5] == b"%PDF-" and len(pdf) > 1000
    # a doua încasare continuă numerotarea seriei
    fid2 = _factura(conn, numar="13", total="10.00")
    assert [(c["serie"], c["numar"]) for c in _incaseaza(fid2, suma="10.00")["chitante"]] == [("CHF1", 2)]


def test_documentul_scris_de_contabil_ramane(conn):
    """Documentul scris de contabil pe dispoziție nu se schimbă (datele lui, nealterate — CLAUDE.md §8); chitanța se emite oricum."""
    fid = _factura(conn)
    r = _incaseaza(fid, document="Încasare factura F1A12")
    assert [(c["serie"], c["numar"]) for c in r["chitante"]] == [("CHF1", 1)]
    with conn.cursor() as cur:
        cur.execute("SELECT document FROM casa_operatiuni WHERE id = %s", (r["id"],))
        assert cur.fetchone() == ("Încasare factura F1A12",)


def test_fara_serie_refuz_numit_spre_date_firma_si_nimic_scris(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_chitanta = NULL")
    fid = _factura(conn)
    with pytest.raises(_erori.CerereGresita) as e:
        _incaseaza(fid)
    d = e.value.detaliu
    assert (d["cod"], d["ecran"]) == ("SERIE_CHITANTA_LIPSA", "date_firma"), d
    assert d["mesaj"].startswith("Încasarea nu s-a salvat: încasarea în numerar a facturii se face cu chitanță (OMFP 2634/2015, "
                                 "cod 14-4-1)"), d["mesaj"]
    with conn.cursor() as cur:
        cur.execute("SELECT (SELECT count(*) FROM casa_operatiuni), (SELECT count(*) FROM chitante)")
        assert cur.fetchone() == (0, 0)


def test_stergerea_operatiunii_anuleaza_chitanta(conn):
    """Chitanța emisă nu se șterge (OMFP 2634/2015 anexa 1 pct.15, `trg_regula_chitanta`): ștergerea dispoziției (nota încă ciornă) o
    anulează, iar factura redevine neîncasată."""
    from core import uc_tenants
    fid = _factura(conn)
    r = _incaseaza(fid)
    assert uc_tenants.casa_sterge(1, r["id"], {"uid": 1}) == {"ok": True}
    assert [x[-1] for x in _chitante(conn)] == [True]
    with conn.cursor() as cur:
        cur.execute("SELECT platita_la FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone() == (None,)


def test_incasarea_veche_fara_chitanta_se_vede_pe_rand(conn):
    """Datele de dinainte (3a): încasarea de la client salvată fără chitanță (drumul vechi, `casa_api.adauga` direct) e numită pe rândul
    registrului — „fără chitanță”; încasarea fără factură (avans) nu primește chitanță automată (decizie cerută)."""
    fid = _factura(conn)
    vechi = _ca.adauga(conn, _SCH, {"data": "2026-10-22", "categorie": "incasare_client", "suma": "64.46", "cui": CUI_CLIENT,
                                    "facturi": [{"factura_id": fid, "suma": "64.46"}]})
    avans = _incaseaza(None, suma="100", avans=True)
    assert avans.get("chitante") is None
    reg = {o["id"]: o for o in _ca.registru(conn, _SCH, 2026, 10)["operatiuni"]}
    assert (reg[vechi["id"]]["fara_chitanta"], reg[vechi["id"]]["chitanta_id"]) == (True, None)


def test_stergerea_notei_din_jurnal_anuleaza_chitanta(conn):
    """Același drum din Registrul jurnal: nota ciornă a încasării (documentul ei e operațiunea de casă) se șterge, iar chitanța emisă pe
    operațiune se anulează și se păstrează (OMFP 2634/2015 anexa 1 pct.15), nu rămâne vie fără operațiune. MUTAȚIE: apelul
    `anuleaza_chitantele_operatiunii` scos din `jurnal_api.sterge` -> chitanța rămâne neanulată -> pică."""
    from core import uc_tenants
    fid = _factura(conn)
    r = _incaseaza(fid)
    assert uc_tenants.jurnal_sterge(1, r["inregistrare_id"], {"uid": 1}) == {"ok": True}
    assert [x[-1] for x in _chitante(conn)] == [True]
    with conn.cursor() as cur:
        cur.execute("SELECT platita_la FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone() == (None,)
