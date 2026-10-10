# -*- coding: utf-8 -*-
"""GARDA deciziilor Costin 08.10.2026 §6 pct.6 + pct.7 (verbatim în DECIZII):

  pct.6 „Amortizarea și descărcarea GV: aceeași regulă ca T1 — înlocuire automată a ciornei nevalidate; ce e validat nu se atinge.”
  pct.7 „R36: evidența = ce a validat un om. Balanța arată implicit doar validatul, iar ciornele apar separat, cu indicator. Porțile
         D300/D394/D390/D406 compară validat cu validat; dacă există ciorne în lună, dau doar avertisment, nu blocaj. Gardă pe această
         regulă.”

CE FACE IMPOSIBIL:
  * o notă de amortizare scrisă direct `validata` (fără om) — și, cu `core/test_rol_pe_efect.py`, orice rută care produce evidență
    fără validare;
  * a doua notă de amortizare / al doilea set de descărcare peste o ciornă nevalidată (se înlocuiește), sau atingerea celei validate;
  * o ciornă numărată în balanță; ciornele lunii nevăzute (indicatorul);
  * o poartă de declarație care blochează când perioada are ciorne (avertisment) — sau care lasă să treacă o diferență fără ciorne.
Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; date în 2099. Nimic în tabele partajate.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_r36"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def lume():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, metoda_stoc, tip_decont) "
                        "VALUES (1, 'R36 SRL', 'RO14399840', true, 'global_valoric', 'L')" % SCH)
        c.commit()
    yield
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nota(conn, data, sursa, linii, status="validata"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'n', %s, %s, 'NC n') RETURNING id",
                    (data, sursa, status))   # [09.10.2026, regulile de fond R3] nota validată are documentul justificativ
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                        (nid, d, c, Decimal(str(s))))
    return nid


def _note(conn, numar):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, document_ref FROM inregistrari WHERE numar = %s ORDER BY id", (numar,))
        return cur.fetchall()


# ── pct.6: amortizarea ──────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def amortizare(lume, monkeypatch):
    from core import auth_api, uc_tenants, common
    import datetime as _d
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    monkeypatch.setattr(common, "azi_ro", lambda: _d.date(2100, 1, 10))   # [deficiența 216] 10/2099 = lună încheiată
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO %s.mijloace_fixe (denumire, cont_imobilizare, cont_amortizare, valoare, dnf_luni, data_pif, metoda, "
                        "activ) VALUES ('Laptop', '2141', '2814', 3600, 36, '2099-01-15', 'liniara', true) RETURNING id" % SCH)
            mid = cur.fetchone()[0]
        c.commit()

    def gen():
        return uc_tenants.tenant_amortizare(1, 2099, 10, {"uid": 1})

    def valoare(v):
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("UPDATE %s.mijloace_fixe SET valoare = %%s WHERE id = %%s" % SCH, (v, mid))
            c.commit()
    return gen, valoare


def test_amortizarea_intra_ciorna_si_se_inlocuieste_cat_e_nevalidata(amortizare):
    """pct.7 + pct.6: nota de amortizare e CIORNĂ; registrul schimbat -> ciorna se înlocuiește (aceeași lună, același tablou, fără
    număr nou); registrul neschimbat -> rămâne ea. MUTAȚIE: ramura `ciorna_nevalidata` scoasă din tenant_amortizare -> „deja
    generată” -> pică."""
    gen, valoare = amortizare
    r1 = gen()
    with _db.get_conn(SCH) as c:
        ((id1, st1, doc1),) = _note(c, "AMORT-2099-10")
    assert (r1["nota_id"], st1) == (id1, "ciorna") and r1["total"] == 100.0
    r2 = gen()
    assert (r2["nota_id"], r2.get("deja_generata")) == (id1, True)                     # aceleași sume: ciorna rămâne
    valoare(7200)
    r3 = gen()
    with _db.get_conn(SCH) as c:
        ((id3, st3, doc3),) = _note(c, "AMORT-2099-10")
    assert (r3["inlocuita"], id3 != id1, st3, doc3, r3["total"]) == (id1, True, "ciorna", doc1, 200.0)


def test_amortizarea_validata_nu_se_atinge(amortizare):
    """„ce e validat nu se atinge.” MUTAȚIE: refuzul pe validată scos -> a doua notă -> pică."""
    from core import erori
    gen, valoare = amortizare
    r1 = gen()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (r1["nota_id"],))
        c.commit()
    valoare(7200)
    with pytest.raises(erori.CerereGresita):
        gen()
    with _db.get_conn(SCH) as c:
        assert [x[0] for x in _note(c, "AMORT-2099-10")] == [r1["nota_id"]]


# ── pct.6: descărcarea global-valorică ──────────────────────────────────────────────────────────────────────────────────────
def test_descarcarea_gv_inlocuieste_ciornele_si_nu_atinge_validatul(lume):
    """Ciornele descărcării se înlocuiesc când rulajele s-au schimbat; aceleași sume -> rămân; validate -> refuz. MUTAȚIE: ramura
    de înlocuire scoasă (orice notă existentă refuză) -> a doua descărcare refuzată -> pică."""
    from core import stocuri_api as sa
    with _db.get_conn(SCH) as conn:
        _nota(conn, "2099-10-01", "stocuri", [("371", "401", 1000), ("371", "378", 200), ("371", "4428.02", 252)])
        _nota(conn, "2099-10-10", "facturi", [("4111", "707", 500), ("4111", "4427", 105)])
        r1 = sa.descarca_luna(conn, SCH, 2099, 10)
        assert sa.descarca_luna(conn, SCH, 2099, 10)["aceleasi_sume"] is True
        _nota(conn, "2099-10-20", "facturi", [("4111", "707", 100), ("4111", "4427", 21)])
        r3 = sa.descarca_luna(conn, SCH, 2099, 10)
        assert r3["inlocuite"] == r1["inregistrari"] and set(r3["inregistrari"]).isdisjoint(r1["inregistrari"])
        refs = {x[2] for x in _note(conn, "DESC-GV-2099-10")}
        assert len(refs) == 1 and len(_note(conn, "DESC-GV-2099-10")) == len(r3["inregistrari"])   # același document, fără dubluri
        with conn.cursor() as cur:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE numar = 'DESC-GV-2099-10'")
        _nota(conn, "2099-10-25", "facturi", [("4111", "707", 100), ("4111", "4427", 21)])
        r4 = sa.descarca_luna(conn, SCH, 2099, 10)
        validate = [x[0] for x in _note(conn, "DESC-GV-2099-10")]
        assert (r4["cod"], r4["inregistrari_existente"], r4.get("aceleasi_sume")) == ("DEJA_DESCARCATA", validate, None)
        conn.rollback()


# ── pct.7: balanța și porțile ───────────────────────────────────────────────────────────────────────────────────────────────
def test_balanta_arata_numai_validatul_iar_ciornele_separat(lume):
    """„Balanța arată implicit doar validatul, iar ciornele apar separat, cu indicator.” MUTAȚIE: filtrul `status = 'validata'` scos
    din `balanta` -> 5311 D 150 -> pică."""
    from core import documente_api as da
    with _db.get_conn(SCH) as conn:
        _nota(conn, "2099-09-05", "banca", [("5311", "5121", 7)], status="ciorna")
        _nota(conn, "2099-10-05", "banca", [("5311", "5121", 100)])
        _nota(conn, "2099-10-06", "banca", [("5311", "5121", 50)], status="ciorna")
        r = {x["cont"]: x for x in da.balanta(conn, SCH, 2099, 10)}
        assert (r["5311"]["rul_d"], r["5311"]["prec_d"]) == (100.0, 0)
        c = da.ciorne_balanta(conn, SCH, 2099, 10)
        assert (c["luna"], c["inainte"], len(c["note"])) == (1, 1, 2)
        assert da.note_lunii(conn, SCH, 2099, 10) == 1
        conn.rollback()


def test_d406_si_tva_blocheaza_diferenta_si_cu_ciorne_ciornele_singure_avertizeaza():
    """[PIVOT 09.10.2026, deficiențele 120 + 210] la TVA; [PIVOT 10.10.2026, comanda Costin pct.3, verbatim în DECIZII: „D406: blocajul
    la o diferență față de balanță se extinde și la D406, inclusiv când luna are ciorne, ca la D300/D394/D390.”] La toate patru porțile:
    o diferență blochează — și cu ciorne în perioadă, iar mesajul le numește —; ciornele fără diferență dau numai avertisment.
    MUTAȚIE: refuzul cu ciorne transformat iar în avertisment (R36 vechi) -> pică, la D406 și la TVA."""
    from core import uc_coada as uq
    for refuz in ({"cod": uq.COD_D406_BALANTA, "mesaj": "D406 nu intră în coadă: diferență 7,00 lei."},
                  {"cod": uq.COD_TVA_BALANTA, "mesaj": "Declarația nu intră în coadă: contul 4426 are 241.50."}):
        assert uq.decizie_poarta(refuz, 0) == (refuz, None)
        blocaj, avert = uq.decizie_poarta(refuz, 2)
        assert avert is None and (blocaj["cod"], blocaj["ciorne"]) == (refuz["cod"], 2), blocaj
        assert blocaj["mesaj"] == refuz["mesaj"] + uq.MESAJ_CIORNE_BLOCAJ % 2
    assert uq.decizie_poarta(None, 0) == (None, None)
    assert uq.decizie_poarta(None, 2) == (None, uq.MESAJ_CIORNE_POARTA % 2)

def test_ciornele_perioadei_se_numara_pe_fereastra_declaratiei(lume):
    """Ciornele se numără pe perioada fiscală a declarației (lunar aici). MUTAȚIE: `note_nevalidate_in_interval` pe status
    'validata' -> 0 -> pică."""
    from core import uc_coada as uq
    with _db.get_conn(SCH) as conn:
        _nota(conn, "2099-10-06", "banca", [("5311", "5121", 50)], status="ciorna")
        _nota(conn, "2099-11-06", "banca", [("5311", "5121", 50)], status="ciorna")
        conn.commit()
    assert uq.ciorne_in_perioada(SCH, 2099, 10) == 1
    assert uq.ciorne_in_perioada(SCH, 2099, None) == 0
