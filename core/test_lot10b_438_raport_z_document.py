# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 pct.8 — raportul Z (F1, Z-8000000001-0042 din 20.10, retestul Costin 20.10.2026).

  8a / 438  „descărcarea mărfii vândute pe Z are ca document justificativ «Bon de consum nr 1 din 20.10.2026». Bonul de consum e
            pentru consum intern; la vânzarea pe Z documentul e raportul Z (nr. 0042, casa 8000000001).” Clasa: orice descărcare de
            stoc pe vânzarea de pe Z — ieșirea pe articol (`stocuri_cv_api.iesire`) și consumul pe rețetă (`retete_api.descarca`).
  8b        „La refuzul «numerar + card ≠ total» mesajul nu dă cifrele (total 231,00, încasat 200,00, diferență 31,00).”
  8c        „După generare […] conturile notei nu se văd” — răspunsul generării poartă rândurile notei (ecranul le arată).
  8e        „După descărcare nu se vede valoarea descărcată” — lista rapoartelor Z poartă valoarea ieșirilor vii legate de Z.

Schemă efemeră din `tenant_template.sql`, într-o tranzacție anulată la final (rândul din `public.tenants` e sintetic, în ROLLBACK);
datele sunt în 2099 (perioadă evident sintetică). CUI-ul firmei efemere: 14399840 (DANTE INTERNATIONAL SA, firmă reală — cifra de
control verificată cu algoritmul din CLAUDE.md).
"""
import io
from decimal import Decimal

import psycopg2.extras as _E
import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot10b_z"
DATA = "2099-10-20"
#: documentul Z-ului tastat, cum îl scrie `uc_tenants.horeca_raport_z` (`jurnal_api.eticheta_document`)
DOC_Z = "Raport Z nr 0042 din 20.10.2099 (casa 8000000001)"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='patron@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    uid, cab = r
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'Z LOT10 SRL', '14399840', 'cantitativ_valoric')"
                % SCH)
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT Lot 10.2 Z',%s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
    try:
        yield conn, cur, tid, uid
    finally:
        conn.rollback()  # SET LOCAL de mai sus moare odată cu tranzacția: conexiunea se întoarce în pool fără search_path
        p.putconn(conn)


def _articol(conn, den="Marfa A", cant=139, pret="2"):
    from core import stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": den, "um": "buc", "data": "2099-10-01", "cantitate": cant, "pret_unitar": pret,
                                "document": "Inventar inițial probă"})
    assert "eroare" not in r, r
    return r["articol_id"]


def _z(cur, nr="0042", doc=DOC_Z):
    """Un raport Z ciornă cum îl scrie ruta tastată (nota + casa și bonurile)."""
    from core import repo_contabilitate as rc
    iid = rc.nota_horeca_z_ciorna(cur, SCH, DATA, "Z-8000000001-%s" % nr, "Raport Z %s casa 8000000001 nr %s" % (DATA, nr), doc)[0]
    rc.adauga_linie_3(cur, SCH, iid, "5311", "707", 200)
    rc.adauga_linie_3(cur, SCH, iid, "5125", "707", 31)
    rc.adauga_linie_3(cur, SCH, iid, "707", "4427", 40.09)
    rc.adauga_z_amef(cur, SCH, iid, "8000000001", 12)
    return iid


def _doc(cur, iid):
    cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (iid,))
    return cur.fetchone()[0]


# ── 8a / 438 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_438_iesirea_pe_z_are_ca_document_raportul_z_nu_bon_de_consum(tx):
    """MUTAȚIE: în `stocuri_cv_api.iesire` documentul Z-ului scos (`_zd.document_z(...)` -> None) -> nota primește «Bon de consum nr 1»
    -> pică."""
    from core import stocuri_cv_api as cva
    conn, cur, *_ = tx
    aid = _articol(conn)
    z = _z(cur)
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 2, "z_id": z})
    assert "eroare" not in r, r
    # Legea 82/1991 art.6 alin.(1): „Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un
    # document care stă la baza înregistrărilor în contabilitate” — vânzarea de pe Z se consemnează în raportul Z, nu în bonul de consum
    assert _doc(cur, r["inregistrare_id"]) == DOC_Z
    cur.execute("SELECT document FROM miscari_stoc WHERE id = %s", (r["id"],))
    assert cur.fetchone()[0] == DOC_Z                                  # și fișa de magazie numește raportul Z
    cur.execute("SELECT count(*) FROM documente_interne_contor WHERE tip = 'bon_consum'")
    assert cur.fetchone()[0] == 0                                      # niciun bon de consum numerotat pentru vânzare


def test_def_438_iesirea_fara_z_si_fara_document_ramane_pe_bon_de_consum(tx):
    """Consumul intern (ieșire fără Z, fără document scris de om) își păstrează bonul de consum (comanda Costin 06.10.2026 §6.2)."""
    from core import stocuri_cv_api as cva
    conn, cur, *_ = tx
    aid = _articol(conn)
    r = cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 1})
    assert _doc(cur, r["inregistrare_id"]) == "Bon de consum nr 1 din 20.10.2099"


def test_def_438_consumul_pe_reteta_pe_z_are_ca_document_raportul_z(tx):
    """Clasa: consumul pe rețetă legat de un Z. MUTAȚIE: `doc_z = None` în `retete_api.descarca` -> «Bon de consum» -> pică."""
    from core import retete_api as ra
    conn, cur, *_ = tx
    aid = _articol(conn, "Faina", 50, "3")
    cur.execute("INSERT INTO retete (denumire) VALUES ('Clatite') RETURNING id")
    rid = cur.fetchone()[0]
    cur.execute("INSERT INTO retete_linii (reteta_id, articol_id, cantitate) VALUES (%s, %s, 0.2)", (rid, aid))
    z = _z(cur)
    r = ra.descarca(conn, SCH, {"reteta_id": rid, "portii": 5, "data": DATA, "z_id": z})
    assert _doc(cur, r["inregistrare_id"]) == DOC_Z                   # Legea 82/1991 art.6 alin.(1) — documentul vânzării: raportul Z
    cur.execute("SELECT document FROM miscari_stoc WHERE inregistrare_id = %s", (r["inregistrare_id"],))
    assert [x[0] for x in cur.fetchall()] == [DOC_Z]
    r2 = ra.descarca(conn, SCH, {"reteta_id": rid, "portii": 1, "data": DATA})   # fără Z: consum intern, bonul de consum rămâne
    assert _doc(cur, r2["inregistrare_id"]).startswith("Bon de consum nr ")


def test_def_438_z_fara_text_de_document_se_numeste_din_cheie(tx):
    """Un Z scris înainte de 05.10.2026 (fără `document_ref`) se numește din casa și numărul din cheia lui — numai din ce există."""
    from core import z_descarcare as zd
    conn, cur, *_ = tx
    z = _z(cur, "0007", doc=None)
    assert zd.document_z(cur, SCH, z) == "Raport Z nr 0007 din 20.10.2099 (casa 8000000001)"


# ── 8b ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_zrefuz_mesajul_numerar_plus_card_da_cifrele():
    """MUTAȚIE: diferența scoasă din mesaj -> pică."""
    from core import raport_z
    m = raport_z.mesaj_plata_diferita(Decimal("231.00"), 200, 0)
    # cifrele cerute de comandă: „total 231,00, încasat 200,00, diferență 31,00” (format românesc, DS cap.7)
    assert m == ("Numerarul și cardul trebuie să dea totalul pe cote: total 231,00 lei, încasat 200,00 lei "
                 "(numerar 200,00 + card 0,00), diferență 31,00 lei."), m


def _ctx(uid):
    return {"uid": uid}


def _pe_conexiune(monkeypatch, conn):
    """Use-case-ul își deschide conexiunea (`db.get_conn()`): aici primește tranzacția anulată a testului (nu comite nimic)."""
    import contextlib

    @contextlib.contextmanager
    def _gc(*a, **k):
        yield conn
    monkeypatch.setattr(_db, "get_conn", _gc)


def test_def_zrefuz_ruta_refuza_cu_cifrele(tx, monkeypatch):
    """Ruta (use-case-ul `horeca_raport_z`) refuză Z-ul cu numerar + card ≠ total, cu cifrele. MUTAȚIE: refuzul vechi
    („numerar + card trebuie să fie egal cu totalul pe cote”) pus înapoi -> pică."""
    from types import SimpleNamespace as NS
    from core import erori, raport_z, uc_tenants
    conn, cur, tid, uid = tx
    _pe_conexiune(monkeypatch, conn)
    rz = NS(data=DATA, nui="8000000001", nr_raport="0042", nr_bonuri=12, total_11=0, total_21=231, numerar=200, card=0)
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.horeca_raport_z(tid, rz, _ctx(uid))
    # refuzul rutei e mesajul cu cifrele (total, încasat, diferența), pe sumele raportului — testul de mai sus îi probează cifrele
    assert e.value.detaliu == raport_z.mesaj_plata_diferita(Decimal("231"), 200, 0), e.value.detaliu


# ── 8c ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_zgenerat_raspunsul_poarta_conturile_notei(tx, monkeypatch):
    """„După generare […] conturile notei nu se văd” -> răspunsul generării poartă rândurile notei (debit, credit, sumă). MUTAȚIE:
    cheia `linii` scoasă din răspuns -> pică."""
    from types import SimpleNamespace as NS
    from core import uc_tenants
    conn, cur, tid, uid = tx
    _pe_conexiune(monkeypatch, conn)
    rz = NS(data=DATA, nui="8000000001", nr_raport="0042", nr_bonuri=12, total_11=0, total_21=231, numerar=200, card=31)
    r = uc_tenants.horeca_raport_z(tid, rz, _ctx(uid))
    # TVA = 231 × 21 / 121 = 40,09 (CF art.291 alin.(1) lit.a — cota standard; rotunjire aritmetică)
    assert r["linii"] == [{"debit": "5311", "credit": "707", "suma": "200.00"}, {"debit": "5125", "credit": "707", "suma": "31.00"},
                          {"debit": "707", "credit": "4427", "suma": "40.09"}], r
    cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (r["nota_id"],))
    assert [{"debit": a, "credit": b, "suma": c} for a, b, c in cur.fetchall()] == r["linii"]   # exact rândurile scrise


# ── 8e ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_zdescarcare_lista_arata_valoarea_descarcata(tx):
    """MUTAȚIE: `valoare_descarcata` întoarce 0 -> pică."""
    from core import stocuri_cv_api as cva, z_descarcare as zd
    conn, cur, *_ = tx
    aid = _articol(conn, cant=139, pret="2.5")
    z = _z(cur)
    cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 4, "z_id": z})
    cva.iesire(conn, SCH, {"articol_id": aid, "data": DATA, "cantitate": 6, "z_id": z})
    (rand,) = zd.lista_luna(conn, SCH, 2099, 10)
    # OMFP 1802/2014 pct.96 — ieșirea la CMP: 10 buc × 2,50 = 25,00 lei
    assert (rand["iesiri"], rand["valoare_descarcata"]) == (2, "25.00"), rand
    with conn.cursor(cursor_factory=_E.RealDictCursor) as c2:
        assert zd.valoare_descarcata(c2, SCH, z) == Decimal("25.00")
