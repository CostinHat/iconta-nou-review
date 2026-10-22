# -*- coding: utf-8 -*-
"""429 + decizia 10.3 (lotul 11, comanda Costin 11.1 pct.1 și pct.11, verbatim în DECIZII „Comanda 10.3” și „Comanda 11.1”):
„Reevaluarea valutei se face pe soldul în valută al partenerului, inclusiv plățile nelegate; avansurile intră doar dacă OMFP 1802 pct.
325 le cuprinde, verificat verbatim.” și „429: reevaluarea în valută e neschimbată pe producție (formular manual, fără propunere, fără
curs BNR, nimic la închiderea lunii)”.

Temei, verbatim (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
  OMFP 1802/2014 pct.325 alin.(1): „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței
  valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză.”
  OMFP 1802/2014 pct.316 alin.(2): „[...] cele reflectate în conturile 409 "Furnizori - debitori" și 419 "Clienți - creditori", nu mai
  fac obiectul evaluării în funcție de cursul valutar, la finele lunii, respectiv la finele exercițiului financiar.”
  OMFP 1802/2014 pct.322 alin.(1) (plata stinge creanța la valoarea din evidență): „Diferențele de curs valutar care apar cu ocazia
  decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate [...]”.

Datele (schemă efemeră din șablon, perioade SINTETICE 2099, cursurile 2099 scrise și șterse de test). Codurile fiscale de test sunt
verificate cu algoritmul cifrei de control (CLAUDE.md): 14399840 (DANTE INTERNATIONAL SA), 55229657 (FISCALOS ICONTA S.R.L.).
"""
import datetime
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

SCH = "efemer_429p"
CTX = {"uid": 1, "firm": 1}
A, B = "14399840", "55229657"


def _cui_valid(cui):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _factura(cur, numar, data, total, curs, cui, nume, moneda="EUR", status_nota="validata", cont="4111"):
    cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, tert_cui, curs_bnr, "
                "total_lei, tva_lei, data_curs) VALUES (%s, 'EX', %s, %s, 0, %s, 'emisa', 'emisa', %s, %s, %s, %s, 0, %s) RETURNING id",
                (numar, data, total, moneda, nume, cui, curs, Decimal(str(total)) * Decimal(str(curs)), data))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status, document_ref) VALUES (%s, %s, 't', 'facturi', "
                "'ciorna', %s) RETURNING id", (data, fid, "Factura EX %s" % numar))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, '707', %s)",
                (nid, cont, Decimal(str(total)) * Decimal(str(curs))))
    if status_nota == "validata":
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
    return fid


def _incasare(cur, data, suma, cui, cont_credit="4111", doc="Extras 1", valideaza=True):
    """O încasare NELEGATĂ de factură (banca nealocată): 5124.EUR = <cont> cu partenerul pe linie."""
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 't', 'banca', 'ciorna', %s) "
                "RETURNING id", (data, doc))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui) VALUES "
                "(%s, '5124.EUR', %s, %s, %s)", (nid, cont_credit, suma, "RO" + cui))
    if valideaza:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
    return nid


def _valideaza_plata_b():
    """Încasarea nelegată a lui B, ciornă în fixtură, se validează (de acum intră în evidență)."""
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE document_ref = 'Extras B'" % SCH)
        c.commit()


@pytest.fixture()
def firma(monkeypatch):
    """Partenerul A (14399840): F1 1.000 EUR la 4,97 (10.09.2099) și F2 500 EUR la 4,98 (15.09.2099), contate și validate; o încasare
    NELEGATĂ de 2.000,00 lei pe 4111 (20.09.2099) și un AVANS de 1.000,00 lei pe 419 (21.09.2099). Partenerul B (55229657): F3 100 EUR
    la 5,00 și F4 300 RON, plus o încasare nelegată de 200,00 lei pe 4111, în ciornă (`_valideaza_plata_b`) — B are facturi în două
    monede. Partenerul C (fără cod): F5
    200 EUR cu nota de contare în CIORNĂ (cazul F1 de pe producție). Cursul BNR la 30.09.2099: EUR 5,0000."""
    from core import auth_api, common, uc_curs_bnr
    assert _cui_valid(A) and _cui_valid(B)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")
            cur.execute("INSERT INTO plan_conturi (simbol, denumire) VALUES ('5124.EUR', 'Cont BT EUR')")
            ids = {"F1": _factura(cur, "1", "2099-09-10", 1000, "4.97", A, "DANTE INTERNATIONAL SA"),
                   "F2": _factura(cur, "2", "2099-09-15", 500, "4.98", A, "DANTE INTERNATIONAL SA"),
                   "F3": _factura(cur, "3", "2099-09-11", 100, "5.00", B, "FISCALOS ICONTA S.R.L."),
                   "F4": _factura(cur, "4", "2099-09-12", 300, "1", B, "FISCALOS ICONTA S.R.L.", moneda="RON"),
                   "F5": _factura(cur, "5", "2099-09-13", 200, "4.99", None, "Kunde GmbH", status_nota="ciorna")}
            _incasare(cur, "2099-09-20", 2000, A)
            _incasare(cur, "2099-09-21", 1000, A, cont_credit="419", doc="Extras avans")
            _incasare(cur, "2099-09-22", 200, B, doc="Extras B", valideaza=False)
            cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES ('2099-09-30', 'EUR', 5.0000) "
                        "ON CONFLICT (data, moneda) DO UPDATE SET curs = EXCLUDED.curs")
        c.commit()
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2099, 12, 15))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)
    yield ids
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE data = '2099-09-30' AND moneda = 'EUR'")
        c.commit()


def _el(p, cheie):
    return next(e for e in p["elemente"] if e["cheie"] == cheie)


def test_def_429_soldul_partenerului_scade_plata_nelegata_si_nu_atinge_avansul(firma):
    """MUTAȚIE: în `_elemente_parteneri`, `gs[0]["ev"].append((p["data"], 1, "plata", stinge))` scos -> soldul rămâne 1.500 EUR -> pică."""
    from core import uc_reevaluare
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    a = _el(p, "p:4111:%s:EUR" % A)
    # decizia 10.3: soldul partenerului = F1 + F2 (1.500 EUR, 7.460,00 lei) − încasarea nelegată de 2.000,00 lei, stinsă la cursul din
    # evidență al partenerului (OMFP 1802/2014 pct.322 alin.(1)): 2.000 / (7.460 / 1.500) = 402,14 EUR -> 1.097,86 EUR, 5.460,00 lei;
    # avansul de pe 419 NU scade nimic (OMFP 1802/2014 pct.316 alin.(2): 419 „nu mai face obiectul evaluării”)
    assert (a["facturi"], a["sold_valuta"], a["lei_evidenta"], a["estimat"]) == (sorted([firma["F1"], firma["F2"]]), "1097.86", "5460.00",
                                                                                 True), a
    assert [x["lei"] for x in a["plati_nelegate"]] == ["2000.00"], a
    # OMFP 1802/2014 pct.325 alin.(1): 1.097,86 x 5,0000 = 5.489,30 -> +29,30 pe 765 (creanța crește)
    assert (a["curs_bnr"], a["lei_bnr"], a["diferenta"], a["cont_diferenta"]) == ("5.0000", "5489.30", "29.30", "765"), a
    assert not [e for e in p["elemente"] if e["cont"].startswith("419")], p["elemente"]


def test_def_429_plata_nelegata_a_partenerului_cu_doua_monede_se_cere_legata(firma):
    """Partenerul B are facturi în EUR și în RON: plata lui nelegată nu se atribuie unei monede — se arată și oprește generarea, lângă
    rândul lui. MUTAȚIE: condiția `len(monede...) > 1` scoasă -> plata intră în soldul EUR -> pică."""
    from core import erori, uc_reevaluare
    _valideaza_plata_b()
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    b = _el(p, "p:4111:%s:EUR" % B)
    assert (b["sold_valuta"], [x["lei"] for x in b["plati_de_legat"]], b["plati_nelegate"]) == ("100.00", ["200.00"], []), b
    with pytest.raises(erori.DateInvalide) as e:
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "640"}}}, CTX)
    assert [x["camp"] for x in e.value.detaliu["erori_campuri"]] == ["rv-sold_valuta-p:4111:%s:EUR" % B], e.value.detaliu
    # motivul, ca a doua parte a frazei câmpului (după „ are facturi ”), întreagă — nu „fragmentul apare” (core/test_garzi_pe_text.py)
    assert e.value.detaliu["erori_campuri"][0]["mesaj"].partition(" are facturi ")[2] == \
        "în mai multe monede, deci nu se poate afla în ce monedă e plata", e.value.detaliu


def test_def_429_factura_cu_contarea_in_ciorna_se_spune_nu_se_sare(firma):
    """Cazul de pe producție (F1, 19–20.10.2026): facturile EUR aveau nota de contare în ciornă, iar propunerea le sărea tăcut. MUTAȚIE:
    `neincluse.append(...)` scos din ramura contării -> pică."""
    from core import uc_reevaluare
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    n = [x for x in p["neincluse"] if x["factura_id"] == firma["F5"]]
    assert [x["motiv"] for x in n] == ["nota ei de contare e ciornă — valideaz-o în Registrul jurnal, apoi reevaluarea o cuprinde"], \
        p["neincluse"]
    assert not [e for e in p["elemente"] if firma["F5"] in (e.get("facturi") or [])]


def test_def_429_nota_pe_partener_poarta_partenerul_si_luna_urmatoare_porneste_de_la_ea(firma):
    """Nota scrie rândul de terți cu partenerul (381: nota pe 4111 / 401 îl cere), iar reevaluarea consemnată pe partener devine cursul din
    evidență al lunii următoare. MUTAȚIE: în `consemneaza`, `e.get("partener_cheie")` -> `None` -> luna următoare reia de la facturi
    (diferența s-ar înregistra a doua oară) -> pică."""
    from core import uc_reevaluare
    r = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "600"}}}, CTX)
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma, partener_cui, partener_nume FROM %s.inregistrari_linii WHERE inregistrare_id = "
                    "%%s AND cont_debit = '4111' ORDER BY suma" % SCH, (r["inregistrare_id"],))
        linii = [tuple(str(x) if isinstance(x, Decimal) else x for x in row) for row in cur.fetchall()]
        cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (r["inregistrare_id"],))
        cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES ('2099-10-30', 'EUR', 5.1000) "
                    "ON CONFLICT (data, moneda) DO UPDATE SET curs = EXCLUDED.curs")
        c.commit()
    try:
        # B (plata lui încă ciornă): 100 EUR la 5,00 = 500 lei -> la 5,00 nicio diferență; A: +29,30 (testul de mai sus)
        assert ("4111", "765", "29.30", A, "DANTE INTERNATIONAL SA") in linii, linii
        p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 10, CTX)
        a = _el(p, "p:4111:%s:EUR" % A)
        # OMFP 1802/2014 pct.325 alin.(1), luna a doua: pornește de la 1.097,86 EUR x 5,00 = 5.489,30 lei, nu de la facturi
        assert (a["sold_valuta"], a["lei_evidenta"], a["curs_evidenta_din"], a["diferenta"]) == ("1097.86", "5489.30", "2099-09-30",
                                                                                                 "109.79"), a
    finally:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE data = '2099-10-30' AND moneda = 'EUR'")
            c.commit()


def test_def_429_blocajul_numara_partenerii_si_conturile(firma):
    from core import reevaluare_valuta as rv
    _valideaza_plata_b()
    with _db.get_conn() as c, c.cursor() as cur:
        mesaj, n = rv.blocaj_inchidere(cur, SCH, 2099, 9)
    # A, B (de legat) și contul 5124.EUR (soldul în valută cerut) — OMFP 1802/2014 pct.325 alin.(1), lunar
    assert mesaj.partition("(%s: " % rv.TEMEI)[2].partition(");")[0] == "2 parteneri, 1 cont în valută" and n == 3, mesaj
