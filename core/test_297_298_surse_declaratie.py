# -*- coding: utf-8 -*-
"""297 + 298 — datele-sursă ale declarației din coadă (comanda Costin 17.10.2026 7.2 pct.3, verbatim în DECIZII):
„297 (D300 din «De depus» se regenerează sau se marchează depășită după validarea unei note din perioadă, conform deciziei 284;
«Confirmă depunerea» oprit pe o declarație depășită) și 298 (declarațiile se fac numai din notele validate sau numesc explicit notele
nevalidate pe care se bazează; garda nu se limitează la TVA).”

Pe o schemă efemeră din `tenant_template.sql` (anul 2099, sintetic), în tranzacție anulată. Temei: N/A — regula de proces e decizia lui
Costin; cifrele declarației nu se schimbă aici.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_297"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.fixture()
def lume():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    yield _SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(cur, data, linii, status="ciorna", factura_id=None, document=None):
    cur.execute("INSERT INTO inregistrari (data, descriere, status, factura_id, document_ref) VALUES (%s,'n',%s,%s,%s) RETURNING id",
                (data, status, factura_id, document))
    nid = cur.fetchone()[0]
    for deb, cre, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, deb, cre, s))
    return nid


def _factura(cur, numar, data, total, tva, tert="Client Irlanda Ltd"):
    cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, tert_nume, tert_tara) VALUES (%s,%s,%s,%s,'emisa',%s,'IE') "
                "RETURNING id", (numar, data, total, tva, tert))
    return cur.fetchone()[0]


def test_297_amprenta_se_schimba_la_validarea_unei_note_din_perioada_si_numai_atunci(lume):
    """MUTAȚIE: `i.status` scos din amprentă (`concat_ws(':', i.id, i.data, …)`) -> validarea notei nu mai schimbă amprenta -> pică."""
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            nid = _nota(cur, "2099-10-17", [("4111", "704", 1000)], document="F1A5")
            _nota(cur, "2099-11-03", [("5121", "4111", 10)], document="EXTRAS 3")   # în afara ferestrei: nu contează
            a0 = ca.amprenta_surse(cur, lume, "2099-10-01", "2099-11-01")
            assert ca.amprenta_surse(cur, lume, "2099-10-01", "2099-11-01") == a0, "aceleași documente -> aceeași amprentă"
            payload = {"_surse": {"de_la": "2099-10-01", "pana_la": "2099-11-01", "amprenta": a0,
                                  "note": [{"nota_id": nid, "eticheta": "nr. crt. 1 din 17.10.2099 (F1A5, 1.000,00 lei)"}]}}
            assert ca.depasire(cur, lume, payload, "d300") is None
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
            dep = ca.depasire(cur, lume, payload, "d300")
            assert dep and dep["mesaj"] == ("Declarația e depășită: după generare s-a validat nr. crt. 1 din 17.10.2099 (F1A5, 1.000,00 lei). "
                                            "Cifrele ei nu mai sunt cele din evidență; generează-o din nou."), dep
            assert [n["nota_id"] for n in dep["note_validate"]] == [nid]
            assert dep["fel"] == "contradictie" and len(dep["sursele"]) == 2, dep   # tipată: cele două afirmații care nu țin împreună
            # o notă din afara ferestrei nu face declarația depășită
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE data = '2099-11-03'")
            payload["_surse"]["amprenta"] = ca.amprenta_surse(cur, lume, "2099-10-01", "2099-11-01")
            assert ca.depasire(cur, lume, payload, "d300") is None
        c.rollback()


def test_297_declaratia_fara_amprenta_e_depasita_fail_closed(lume):
    """O declarație intrată în coadă înainte de 17.10.2026 n-are amprentă: nu se poate ști, deci e depășită (nu „proaspătă”).
    MUTAȚIE: `if not s: return None` -> pică."""
    from core import coada_api as ca
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            dep = ca.depasire(cur, lume, {"_an": 2099, "_luna": 10}, "d300")
        c.rollback()
    assert dep and dep["mesaj"] == ("Declarația a intrat în coadă înainte ca aplicația să-i păstreze datele-sursă, deci nu se poate ști dacă "
                                    "cifrele ei mai sunt cele din evidență. Generează-o din nou."), dep
    assert dep["fel"] == "verificare_rupta" and dep["eroare"], dep   # nu „necunoaștere”: confruntarea însăși n-are pe ce rula


def test_298_factura_cu_tva_0_fara_nota_validata_e_numita_la_orice_tva(lume, monkeypatch):
    """298: „o factură cu TVA 0 trece nesemnalată”. Acum D300 numește factura fără notă validată (și cu TVA 0), iar notele nevalidate
    ale perioadei se numesc la ORICE declarație (aici D100, care nu are poartă de TVA). MUTAȚIE: `if tip in DECLARATII_TVA else []`
    -> `[]` (facturile nu se mai numesc) -> pică."""
    from core import uc_coada as uq
    monkeypatch.setattr(uq, "fereastra_declaratie", lambda schema, tip, an, luna, trim: ("2099-10-01", "2099-11-01"))
    with _db.get_conn(lume) as c:
        with c.cursor() as cur:
            fid = _factura(cur, "F1A5", "2099-10-17", 1000, 0)
            _nota(cur, "2099-10-17", [("4111", "704", 1000)], factura_id=fid, document="F1A5")
        c.commit()
    s = uq.surse_declaratiei(lume, "d300", 2099, 10, None)   # schema efemeră: fixture-ul o șterge cu tot cu ce s-a scris
    assert [f["factura_id"] for f in s["facturi"]] == [fid], s
    a = s["documente_nevalidate"]                            # afirmația despre perioadă e tipată (`core/afirmatii.py`)
    assert a["fel"] == "fapt" and a["unde"] == "perioada declarației 2099-10-01 – 2099-11-01", a
    assert a["motiv"] == ("Declarația cuprinde 1 factură fără notă validată, deci încă în afara evidenței: factura F1A5 (emisă către Client "
                          "Irlanda Ltd, 1.000,00 lei, nota ei e ciornă, nevalidată). În perioadă este 1 notă nevalidată, pe care evidența nu o "
                          "cuprinde până nu o validează un om: nota din 17.10.2099 — F1A5, 1.000,00 lei. Validează-le înainte de depunere: "
                          "după validare declarația devine depășită și se generează din nou."), a["motiv"]
    s100 = uq.surse_declaratiei(lume, "d100", 2099, None, 4)
    assert s100["facturi"] == [] and "1 notă nevalidată" in s100["documente_nevalidate"]["motiv"], s100


def test_297_fereastra_declaratiei_pe_perioada_declarata():
    """Luna, trimestrul, anul (în afara TVA-ului, unde fereastra e a profilului de TVA)."""
    from core import uc_coada as uq
    assert uq.fereastra_declaratie("x", "d112", 2099, 12, None) == ("2099-12-01", "2100-01-01")
    assert uq.fereastra_declaratie("x", "d100", 2099, None, 4) == ("2099-10-01", "2100-01-01")
    assert uq.fereastra_declaratie("x", "d101", 2099, None, None) == ("2099-01-01", "2100-01-01")


def test_299_perioada_declarata_nu_termenul():
    from core import uc_coada as uq
    assert [uq.perioada_text(2026, 10, None), uq.perioada_text(2026, None, 3), uq.perioada_text(2026, None, None)] == [
        "10/2026", "T3/2026", "anul 2026"]


def test_297_elementul_fara_cerere_pastrata_e_refuzat_cu_drumul_spus(monkeypatch):
    """„Generează din nou” pe un element intrat în coadă înainte să i se păstreze cererea: refuz cu drumul (Declarații -> „Înlocuiește”),
    nu o regenerare din altceva. MUTAȚIE: `if not cerere: raise` scos -> `coada_adauga` e chemată cu o cerere goală -> pică."""
    import contextlib
    from core import erori, uc_coada as uq

    class _C:
        def cursor(self):
            return contextlib.nullcontext(None)

    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: contextlib.nullcontext(_C()))
    monkeypatch.setattr(uq.coada_api, "element_declaratie",
                        lambda cur, cid: (7, 1, "d300", "la_senior", {"_an": 2099, "_luna": 9}, "declaratie"))
    monkeypatch.setattr(uq, "coada_adauga", lambda date, ctx: pytest.fail("regenerată fără cererea păstrată"))
    with pytest.raises(erori.Conflict) as e:
        uq.coada_regenereaza(5, {"firm": 7})
    d = e.value.args[0]
    assert d == {"ok": False, "cod": "FARA_CERERE", "mesaj": (
        "Declarația a intrat în coadă înainte ca aplicația să-i păstreze cererea, deci nu se poate genera din nou de aici. Generează-o din "
        "Declarații (D300 09/2099) și alege „Înlocuiește”.")}, d
