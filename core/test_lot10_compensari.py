# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 428, decizia Costin 20.10.2026 „Construiesc acum”] Compensarea creanțelor și datoriilor reciproce.

Decizia, verbatim (DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „tabelă de compensări (factura emisă ↔ factura primită,
suma, data) și ecran; fiecare compensare stinge cele două facturi și mută TVA-ul prin același punct ca banca și casa.” Comanda 10.1
(428): „fiecare încasare (bancă, casă, compensare) legată de factură mută automat partea încasată în 4427”.

Temeiul e citat verbatim pe linie, lângă fiecare assert (`anaf_surse/`). Profilul de probă, într-o schemă efemeră din `tenant_template.sql`
(ROLLBACK la final): firma în sistemul TVA la încasare din 01.10.2026 (CUI 14399840), partenerul X (18547290) — client și furnizor:
  E1  emisă 10.10 către X 1.000 + 210 = 1.210, contată (4111 = 4428)
  P1  primită 12.10 de la X 500 + 105 = 605, contată (4428 = 401: firma în sistem, CF art.297 alin.(3))
  E2  emisă 11.10 către X în EUR (nu se compensează: refuz numit)
  E3  emisă 13.10 către X, necontată (OMFP 1802/2014 pct.56 alin.(3): refuz numit)
  P2  primită 12.10 de la Y (1590082) — alt partener
  Ordinul de compensare nr 7 din 20.10.2026: E1 cu P1, 605 lei.
CUI-urile: cifra de control verificată cu algoritmul din CLAUDE.md.
"""
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import compensari_api as _cz
from core.common import Perioada

_SCHEMA = "test_lot10_compensari"
D = Decimal
_X, _Y = "18547290", "1590082"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _duk(tip):
    try:
        from core import duk
        return duk if duk.poate_valida(tip) else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════ PUR
def test_perechile_se_sting_pana_la_cea_mai_mica():
    # Codul civil art.1616: „Datoriile reciproce se sting prin compensaţie până la concurenţa celei mai mici dintre ele.”
    e = [{"id": 1, "rest": "1210.00"}, {"id": 2, "rest": "100.00"}]
    p = [{"id": 10, "rest": "605.00"}, {"id": 11, "rest": "800.00"}]
    assert _cz.perechi_propuse(e, p) == [
        {"factura_emisa_id": 1, "factura_primita_id": 10, "suma": "605.00"},
        {"factura_emisa_id": 1, "factura_primita_id": 11, "suma": "605.00"},
        {"factura_emisa_id": 2, "factura_primita_id": 11, "suma": "100.00"}]
    # totalul compensat = cel mai mic dintre totaluri (1.310 de încasat, 1.405 de plătit)
    assert sum(D(x["suma"]) for x in _cz.perechi_propuse(e, p)) == D("1310.00")
    assert _cz.perechi_propuse(e, []) == []


def test_partenerul_e_acelasi_cu_sau_fara_RO():
    assert _cz.cui_partener("RO 18547290") == _cz.cui_partener("18547290") == "18547290"
    assert _cz.cui_partener("DE123456789") == "DE123456789"


def test_documentul_e_ordinul_de_compensare():
    # HG 685/1999 anexa 2 art.11: „Ordinul de compensare [...] reprezinta document justificativ de inregistrare in contabilitate”
    import datetime as dt
    assert _cz.document("7", dt.date(2026, 10, 20)) == "Ordin de compensare nr 7 din 20.10.2026"


def test_ordinul_fara_numar_e_refuzat_pe_camp():
    # HG 685/1999 anexa 2 art.11: „Ordinele de compensare au regim special, sunt numerotate din tipografie” — numărul e al ordinului,
    # scris de contabil; aplicația nu-l inventează
    from core import erori as _erori, uc_compensari
    with pytest.raises(_erori.CerereGresita) as e:
        uc_compensari.compensari_genereaza(1, {"data": "2026-10-20", "numar": " ", "perechi": []}, {"uid": 0})
    assert e.value.detaliu["erori_campuri"] == [{"camp": "cz-numar", "mesaj": "Scrie numărul ordinului de compensare."}]


# ═══════════════════════════════════════════════════════════════════════ PROFILUL DE PROBĂ
def _factura(cur, numar, data, directie, baza, cui, moneda="RON", curs=1):
    tva = D(baza) * 21 / 100
    cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, total_lei, tva_lei, curs_bnr, moneda, tert_nume, "
                "tert_cui, tert_tara, tert_platitor_tva, tert_adresa, tert_oras, tert_judet, status) "
                "VALUES (%s,'CZ',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'RO',true,'Str. Probei 1','Sector 1','B','emisa') RETURNING id",
                (numar, data, directie, D(baza) + tva, tva, (D(baza) + tva) * curs, tva * curs, curs, moneda,
                 "PARTENER X SRL" if cui == _X else "PARTENER Y SRL", cui))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, cont_cheltuiala) "
                "VALUES (%s,'servicii',1,%s,21,%s)", (fid, baza, None if directie == "emisa" else "628"))
    return fid


def _conteaza(conn, fid):
    from core import contare_facturi as _cf
    with _cf.cursor_dict(conn) as cur:
        return _cf.contabilizeaza(cur, "", fid, automat=True, cont_cheltuiala=None)["inregistrare_id"]


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        return [(d, c, D(s)) for d, c, s in cur.fetchall()]


def _compenseaza(conn, data, perechi, numar="7"):
    import datetime as dt
    ver = _cz.verifica(conn, _SCHEMA, data, perechi)
    with conn.cursor() as cur:
        return [_cz.scrie(cur, _SCHEMA, dt.date.fromisoformat(data), _cz.document(numar, dt.date.fromisoformat(data)), p)[0]
                for p in ver]


def _stare(conn, fid):
    from core import facturi_api
    from psycopg2.extras import RealDictCursor
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM facturi WHERE id = %s", (fid,))
        f = [dict(cur.fetchone())]
        facturi_api._cu_stare_incasare(cur, f)
    return f[0]["stare_incasare"]


def _sold(conn, fid):
    from core import reconciliere_api
    return {f["id"]: f["sold"] for f in reconciliere_api.facturi_deschise(conn, _SCHEMA)}.get(fid)


@pytest.fixture(scope="module")
def prob():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, platitor_tva, "
                    "tip_decont, tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie, cont_venit_implicit) "
                    "VALUES (1,'COMPENSARE SRL','14399840','Str Test 1','Sector 1','B','6920','0722000000','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',true,'Popescu','Ion','ADMINISTRATOR','704')")
                cur.execute("INSERT INTO tva_incasare_perioade (de_la) VALUES ('2026-10-01')")
                ids = {"E1": _factura(cur, "1", "2026-10-10", "emisa", 1000, _X),
                       "P1": _factura(cur, "P1", "2026-10-12", "primita", 500, _X),
                       "E2": _factura(cur, "2", "2026-10-11", "emisa", 100, _X, moneda="EUR", curs=D("4.9700")),
                       "E3": _factura(cur, "3", "2026-10-13", "emisa", 100, _X),
                       "P2": _factura(cur, "P2", "2026-10-12", "primita", 100, _Y)}
            note = {k: _conteaza(conn, ids[k]) for k in ("E1", "P1", "E2", "P2")}
            yield conn, ids, note
        finally:
            conn.rollback()


pytestmark_db = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytestmark_db
def test_propunerea_aduce_perechea_partenerului(prob):
    conn, ids, note = prob
    p = {x["cui"]: x for x in _cz.propunere(conn, _SCHEMA)["parteneri"]}
    # numai partenerul cu AMBELE feluri de facturi deschise (Y are doar o primită)
    assert set(p) == {_X}, p
    x = p[_X]
    # Codul civil art.1616: „până la concurenţa celei mai mici dintre ele” — 605 (P1) din 1.210 (E1)
    assert x["perechi"] == [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "605.00"}], x
    # ce oprește o factură e o afirmație tipată (`neconformitate`, decizia 21.08): factura, regula și motivul
    assert {f["afirmatie"]["fel"] for f in x["emise"] if f["afirmatie"]} == {"neconformitate"}
    assert all(f["afirmatie"]["motiv"] for f in x["emise"] if f["afirmatie"]), x["emise"]     # refuz numit: motivul nu e gol
    # regula care oprește fiecare emisă, ca dată: E2 în valută (refuz numit, nu tratament ghicit); E3 necontată — OMFP 1802/2014
    # pct.56 alin.(3): „pot fi înregistrate numai după contabilizarea creanțelor și veniturilor”; E1 compensabilă
    assert {f["id"]: (f["afirmatie"] or {}).get("regula") for f in x["emise"]} == {
        ids["E1"]: None, ids["E2"]: _cz.REGULA_VALUTA, ids["E3"]: _cz.REGULA_CONTARE}, x["emise"]
    assert next(f for f in x["emise"] if f["id"] == ids["E2"])["moneda"] == "EUR"
    # E1 e în sistem la data ei: partea compensată mută TVA-ul (CF art.282 alin.(3))
    assert next(f for f in x["emise"] if f["id"] == ids["E1"])["tva_la_incasare"] is True


@pytestmark_db
def test_refuzurile_sunt_numite(prob):
    conn, ids, note = prob
    with pytest.raises(_cz.RefuzCompensare) as e:   # Codul civil art.1616: cel mult restul fiecărei facturi (P1: 605)
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "606"}])
    assert (e.value.cod, e.value.detalii) == (_cz.COD_DATE, {"factura": ids["P1"], "ramas": D("605.00"), "suma": D("606")}), e.value.mesaj
    with pytest.raises(_cz.RefuzCompensare) as e:   # art.1616: „datoriile reciproce” — același partener
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P2"], "suma": "10"}])
    assert (e.value.cod, e.value.detalii) == (_cz.COD_STARE, {"facturi": [ids["E1"], ids["P2"]], "parteneri": [_X, _Y]}), e.value.mesaj
    with pytest.raises(_cz.RefuzCompensare) as e:   # HG 685/1999 anexa 2 art.5: data stingerii = data ordinului; datoria trebuie să existe
        _cz.verifica(conn, _SCHEMA, "2026-10-11", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "10"}])
    assert (e.value.cod, e.value.detalii) == (_cz.COD_DATE, {"factura": ids["P1"], "data_factura": "2026-10-12"}), e.value.mesaj
    with pytest.raises(_cz.RefuzCompensare) as e:   # OMFP 1802/2014 pct.56 alin.(3): numai după contabilizare
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E3"], "factura_primita_id": ids["P1"], "suma": "10"}])
    assert (e.value.cod, e.value.detalii) == (_cz.COD_STARE, {"factura": ids["E3"], "regula": _cz.REGULA_CONTARE}), e.value.mesaj
    with pytest.raises(_cz.RefuzCompensare) as e:   # suma pe aceeași factură, cumulat pe perechi
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "600"},
                                                     {"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "10"}])
    # cumulat: P1 (605) a dat deja 600 primei perechi -> rămân 5,00 lei, a doua pereche cere 10
    assert (e.value.cod, e.value.detalii) == (_cz.COD_DATE, {"factura": ids["P1"], "ramas": D("5.00"), "suma": D("10")}), e.value.mesaj
    with pytest.raises(_cz.RefuzCompensare):
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "0"}])


@pytestmark_db
def test_compensarea_in_valuta_e_refuzata_cu_motiv_pe_cerere(prob):
    """[lotul 11, decizia Costin din 10.3: „Compensarea în valută rămâne refuzată, cu motiv.”] Drumul cererii (API-ul / butonul, `verifica`):
    factura în EUR se refuză numit, cu regula și temeiul, nu se compensează în lei. MUTAȚIE: `if d["moneda"] != "RON":` -> `if False:` în
    `facturi_deschise` -> perechea în valută trece -> pică."""
    conn, ids, note = prob
    with pytest.raises(_cz.RefuzCompensare) as e:
        _cz.verifica(conn, _SCHEMA, "2026-10-20", [{"factura_emisa_id": ids["E2"], "factura_primita_id": ids["P1"], "suma": "10"}])
    assert (e.value.cod, e.value.detalii) == (_cz.COD_STARE, {"factura": ids["E2"], "regula": _cz.REGULA_VALUTA}), e.value.mesaj
    # OMFP 1802/2014 pct.322 alin.(1): „Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută [...]
    # trebuie recunoscute în luna în care apar” — motivul refuzului îl numește
    assert e.value.mesaj == (
        "Factura CZ nr. 2 nu se poate compensa: în EUR: compensarea în valută nu se face în aplicație — stingerea cere și diferența de curs "
        "la data ordinului (%s), pe care aplicația n-o calculează; înregistreaz-o din Registrul jurnal, cu diferența pe 665 / 765."
        % _cz.TEMEI_VALUTA), e.value.mesaj   # mesajul întreg (core/test_garzi_pe_text.py)


@pytestmark_db
def test_compensarea_stinge_ambele_facturi_si_muta_tva(prob):
    conn, ids, note = prob
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT cz")
    try:
        [iid] = _compenseaza(conn, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "605"}])
        # OMFP 1802/2014 pct.56 alin.(3) — compensarea datoriei (401) cu creanța (4111); HG 1/2016 pct.26 alin.(7): încasarea înseamnă
        # și „compensarea”; CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă” —
        # 605 din 1.210 pe E1 -> 105 trece 4428 -> 4427; P1 (605, TVA 105) plătită integral -> 105 trece 4428 -> 4426 (CF art.297 alin.(3))
        assert _linii(conn, iid) == [("401", "4111", D("605.00")), ("4428", "4427", D("105.00")), ("4426", "4428", D("105.00"))]
        with conn.cursor() as cur:
            cur.execute("SELECT i.status, i.sursa, i.document_ref, i.factura_id, l.partener_cui FROM inregistrari i "
                        "JOIN inregistrari_linii l ON l.inregistrare_id = i.id AND l.cont_debit = '401' WHERE i.id = %s", (iid,))
            st, sursa, doc, fid, pcui = cur.fetchone()
            cur.execute("SELECT factura_emisa_id, factura_primita_id, suma, data::text FROM compensari WHERE inregistrare_id = %s", (iid,))
            cz = cur.fetchone()
        # R36: nota intră ciornă; HG 685/1999 anexa 2 art.11: „Ordinul de compensare se anexeaza la nota contabila”
        assert (st, sursa, doc, fid, pcui) == ("ciorna", "operatiuni", "Ordin de compensare nr 7 din 20.10.2026", None, _X)
        assert cz == (ids["E1"], ids["P1"], D("605.00"), "2026-10-20")
        # „fiecare compensare stinge cele două facturi”: E1 încasată parțial 605, P1 plătită integral
        assert _stare(conn, ids["E1"])["stare"] == "partial" and _stare(conn, ids["E1"])["incasat"] == "605.00"
        assert _stare(conn, ids["P1"])["stare"] == "incasata"
        # banca și casa nu mai încasează partea compensată (soldul reconcilierii)
        assert _sold(conn, ids["E1"]) == D("605.00") and _sold(conn, ids["P1"]) is None
        # fișa partenerului (rapoartele comerciale) vede aceeași decontare
        from core import rapoarte_comerciale_api as _rca
        fisa = {f["id"]: f for f in _rca.fisa_partener(conn, _SCHEMA, _X, "2026-10-01", "2026-10-31")["facturi"]}
        assert (fisa[ids["E1"]]["decontat"], fisa[ids["P1"]]["stare"]) == (605.0, "achitata"), fisa
        from core import tva_incasare as _tvi
        from core import repo_tva_incasare as _rti
        assert _tvi.rest_neexigibil(conn.cursor(), _SCHEMA, _rti.factura(conn.cursor(), _SCHEMA, ids["E1"])) == D("105.00")
        # o a doua încasare (casa) mută numai restul: 605 -> 105, nu mai mult (alin.(8), plafonul restului)
        assert _tvi.linii_la_incasare(conn.cursor(), _SCHEMA, ids["E1"], 605) == [("4428", "4427", D("105.00"))]
        assert _tvi.linii_la_incasare(conn.cursor(), _SCHEMA, ids["P1"], 1) == []
        # nota compensării nu e contare a facturii (stare „contabilizată” neschimbată) și nu se editează din jurnal
        from core import note_derivate as _nd
        assert _nd.documentul_sursa(conn.cursor(), _SCHEMA, iid)[0] == "compensare"
        # ștergerea facturii compensate: refuz numit (cheia `compensari` fără ON DELETE)
        from core import facturi_api, contare_facturi as _cf
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT st")
        with pytest.raises(_cf.RefuzContare) as e:
            facturi_api.sterge_factura(conn, ids["P1"])
        # refuzul numește ordinul care ține factura (documentul notei, ca în Registrul jurnal), ca dată
        assert (e.value.cod, e.value.detalii) == ("COMPENSATA", {"document": "Ordin de compensare nr 7 din 20.10.2026", "iesire": "storno"})
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT st")
        # ștergerea compensării = ștergerea notei ei ciornă din Registrul jurnal: rândul cade (ON DELETE CASCADE), facturile redevin deschise
        from core import jurnal_api
        assert jurnal_api.sterge(conn, _SCHEMA, iid) == {"ok": True}
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM compensari")
            assert cur.fetchone()[0] == 0
        assert _sold(conn, ids["E1"]) == D("1210.00") and _sold(conn, ids["P1"]) == D("605.00")
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT cz")


@pytestmark_db
def test_d300_si_d394_vad_compensarea(prob):
    conn, ids, note = prob
    from core import d300 as _d300, d394 as _d394
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT dz")
    try:
        _compenseaza(conn, "2026-10-20", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "605"}])
        with conn.cursor() as cur:
            cur.execute("UPDATE facturi SET status = 'anulata' WHERE id = %s", (ids["E2"],))   # factura în valută nu e în proba D300
            cur.execute("UPDATE inregistrari SET status = 'validata'")
        prof, fac = _d300.pull(conn, _SCHEMA, Perioada(2026, luna=10))
        res = _d300.calcul_d300(prof, Perioada(2026, luna=10), fac)
        # HG 1/2016 pct.26 alin.(9): „se consideră că furnizorul/prestatorul a încasat, respectiv beneficiarul a plătit contravaloarea
        # [...] la data la care se sting total sau parțial datoriile” — 605 compensat pe E1 -> rd.9 500 / 105 (CF art.282 alin.(3), (8))
        assert (res.R.get("R9_1"), res.R.get("R9_2")) == (500, 105), res.R
        # P1 plătită prin compensare -> deducerea amânată devine exercitabilă (CF art.297 alin.(3)): rd.24 500 / 105, plus P2 (Y, 100/21)
        assert (res.R.get("R22_1"), res.R.get("R22_2")) == (500, 105), res.R
        # OPANAF 174/2026 rd.A „taxa [...] a ramas neexigibila, existenta in sold la sfarsitul perioadei”: E1 rămâne cu 105 (baza 500) după
        # compensare, plus E3 neîncasată 21 (baza 100); rd.B: P2 (Y) 21 nededus — P1, plătită integral prin compensare, nu mai e acolo
        assert (res.neexigibil.get("tva_a"), res.neexigibil.get("valoare_a")) == (126, 600), res.neexigibil
        assert (res.neexigibil.get("tva_b"), res.neexigibil.get("valoare_b")) == (21, 100), res.neexigibil
        xml = _d300.build_xml(res)
        duk = _duk("d300")
        if duk is not None:
            v = duk.valideaza(xml, "d300", an=2026, luna=10, timeout=180)
            assert v.get("stare") == "valid", v
        xml394, r394 = _d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=10))
        # OPANAF 2194/2025 pct.5.1 „TVA colectată aferentă facturilor încasate în perioada de raportare” — încasată prin compensare: 105
        assert r394.informatii["tvaCol21"] == 105, r394.informatii
        # pct.5.2 TVA dedusă aferentă facturilor achitate (furnizor în sistemul normal): P1 prin compensare 105
        assert r394.informatii["tvaDed21"] == 105, r394.informatii
        duk = _duk("d394")
        if duk is not None:
            v = duk.valideaza(xml394, "d394", an=2026, luna=10, timeout=180)
            assert v.get("stare") == "valid", v
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT dz")


@pytestmark_db
def test_dupa_iesire_compensarea_continua_sistemul_si_reconcilierea_d300_o_vede(prob):
    conn, ids, note = prob
    from core import d300 as _d300, d300_reconciliere as _rec
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT ie")
        # ieșirea din sistem la 31.10 (CF art.282 alin.(5)); compensarea pe 05.11, după ieșire
        cur.execute("UPDATE tva_incasare_perioade SET pana_la = '2026-10-31'")
    try:
        [iid] = _compenseaza(conn, "2026-11-05", [{"factura_emisa_id": ids["E1"], "factura_primita_id": ids["P1"], "suma": "605"}])
        # CF art.282 alin.(7) lit.b): pentru facturile emise înainte de ieșire „se continuă aplicarea sistemului, respectiv exigibilitatea
        # taxei intervine conform alin. (3) și (5)” — E1 și P1 (emise în sistem) mută TVA-ul și după ieșire
        assert _linii(conn, iid) == [("401", "4111", D("605.00")), ("4428", "4427", D("105.00")), ("4426", "4428", D("105.00"))]
        with conn.cursor() as cur:
            cur.execute("UPDATE facturi SET status = 'anulata' WHERE id = %s", (ids["E2"],))
            cur.execute("UPDATE inregistrari SET status = 'validata'")
        prof, fac = _d300.pull(conn, _SCHEMA, Perioada(2026, luna=11))
        res = _d300.calcul_d300(prof, Perioada(2026, luna=11), fac)
        assert (res.R.get("R9_1"), res.R.get("R9_2")) == (500, 105), res.R
        # firma nu mai e în sistem în noiembrie -> reconcilierea pe emitere se aplică; nota compensării (fără `factura_id`) e o decontare
        # cu linia 4428 = 4427, deci rândurile colectate nu se confruntă pe emitere (calea 2 nu le poate recalcula) — fără divergență falsă
        rap = _rec.reconciliaza(conn, Perioada(2026, luna=11), res)
        assert rap["acoperit"] and not rap["divergente"], rap
        assert set(rap["sarite"]) >= {"R9_2"}, rap
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT ie")
