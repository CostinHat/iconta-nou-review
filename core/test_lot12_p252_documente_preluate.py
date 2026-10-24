# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 252 — grupa 2, poziția pilot F085 „Import solduri parteneri”] „Import parteneri: facturi deschise neimportate;
scadențarul nealimentat.” Importul soldurilor pe parteneri (forma SAGA a situației clienților / furnizorilor: Nr. factură, Data, Scadență,
Sumă neachitată) nu crea documentele deschise: scadențarul nu le vedea, iar o încasare din bancă după preluare n-avea ce stinge.

REPARAȚIA (cap-coadă, pe mecanismele existente): facturile deschise intră în `facturi` cu `tip = 'preluata'`
(`nomenclator_status_factura.TIP_SOLD_PRELUAT`) — din forma pe facturi câte una pe rând, din forma pe solduri soldul partenerului întreg
(„Sold la <data preluării>”, fără scadență). Scadențarul le arată cu restul (`repo_facturi.de_incasat`), banca / casa / compensările le
sting prin aceeași legătură notă–factură (`reconciliere_api.facturi_deschise`), iar declarațiile, notele și balanța nu le citesc (tipul nu
e în `TIPURI_FISCALE`; soldul lor e deja în soldurile inițiale). Auditul de preluare confruntă suma lor cu soldul partenerului; al doilea
import cere confirmarea înlocuirii (426) și refuză înlocuirea facturilor pe care le stinge deja o încasare.

CIFRELE (sintetice, CUI-uri cu cifra de control verificată — CLAUDE.md §10): balanța la 31.08.2026: 4111 D 5.000 (ALFA 1.000 + 2.000,
BETA 2.000), 401 C 1.500 (GAMMA), 5121 D 10.000, 1012 C 13.500. Extrasul: +1.000 de la ALFA (16.09), −1.500 către GAMMA (17.09).

TEMEI: N/A — regulă de produs (comanda lotului 12, deficiența 252). Soldul preluat nu se mai înregistrează: OMFP 1802/2014 pct.130 (soldurile
de deschidere sunt cele ale exercițiului precedent) — de aceea facturile preluate n-au notă. Schemă efemeră din template, tranzacție anulată.
"""
import datetime as _dt
import os
from decimal import Decimal

import pytest

from core import db as _db, solduri_parteneri_api as sp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot12_p252"
ALFA, BETA, GAMMA = ("25200012", "ALFA DISTRIBUTIE SRL"), ("25200020", "BETA CONSTRUCT SRL"), ("25200039", "GAMMA LOGISTIC SRL")
DATA = "2026-08-31"

FISIER_FACTURI = ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată\n"
                  "4111;RO%s;%s;FA-101;10.08.2026;09.09.2026;1000,00\n"
                  "4111;RO%s;%s;FA-102;20.08.2026;19.09.2026;2000,00\n"
                  "4111;%s;%s;FB-7;25.08.2026;;2000,00\n"
                  "401;%s;%s;G-55;15.08.2026;14.09.2026;1500,00\n"
                  % (ALFA + ALFA + BETA + GAMMA)).encode("utf-8")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA 252 SRL','14399840','Str 1','Buc','B',"
                            "'4690','BCR','RO49RNCB0000000000000001','0700000000',true,'L','Popescu','Ion','ADMINISTRATOR')")
                for cont, d, cr in (("4111", 5000, 0), ("401", 0, 1500), ("5121", 10000, 0), ("1012", 0, 13500)):
                    cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (%s,%s,%s,%s)",
                                (cont, d, cr, DATA))
            yield c
        finally:
            c.rollback()


def _importa(c, continut=FISIER_FACTURI, nume="situatie_clienti_furnizori.csv", inlocuieste=False):
    randuri = sp.extrage(continut, nume)
    return sp.importa(c, randuri, DATA, schema=SCHEMA, inlocuieste=inlocuieste)


def _preluate(c):
    with c.cursor() as cur:
        cur.execute("SELECT numar, directie, tert_cui, data_emitere::text, data_scadenta::text, total, tva FROM facturi "
                    "WHERE tip = 'preluata' ORDER BY numar")
        return cur.fetchall()


# ── citirea fișierului ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_252_forma_pe_facturi_se_citeste_pe_parteneri_cu_facturile_lor():
    """Forma SAGA pe facturi: un rând = o factură deschisă; ALFA (două facturi) devine UN partener de 3.000,00 cu cele două facturi.
    ROȘU înainte: „Același partener apare de două ori pe același cont” (rândurile ALFA, refuzul C73). MUTAȚIA: `grupeaza_pe_parteneri`
    scos din `extrage` -> același refuz."""
    r = sp.extrage(FISIER_FACTURI, "situatie.csv")
    assert [(x["cont"], x["cui"], x["debit"], x["credit"], x["rand_fisier"]) for x in r] == [
        ("4111", ALFA[0], 3000.0, 0.0, 2), ("4111", BETA[0], 2000.0, 0.0, 4), ("401", GAMMA[0], 0.0, 1500.0, 5)]
    assert r[0]["documente"] == [{"numar": "FA-101", "data": "2026-08-10", "scadenta": "2026-09-09", "suma": 1000.0, "rand_fisier": 2},
                                 {"numar": "FA-102", "data": "2026-08-20", "scadenta": "2026-09-19", "suma": 2000.0, "rand_fisier": 3}]
    assert r[1]["documente"] == [{"numar": "FB-7", "data": "2026-08-25", "scadenta": None, "suma": 2000.0, "rand_fisier": 4}]
    assert r[2]["documente"] == [{"numar": "G-55", "data": "2026-08-15", "scadenta": "2026-09-14", "suma": 1500.0, "rand_fisier": 5}]


def test_252_factura_fara_data_e_refuzata_numit():
    f = "Cont;Cod fiscal;Denumire;Nr. factură;Data;Sumă neachitată\n4111;%s;%s;FA-1;;100\n" % ALFA
    with pytest.raises(ValueError) as e:
        sp.extrage(f.encode(), "x.csv")
    assert str(e.value) == "Rândul 2 (%s, factura FA-1): data facturii lipsește. Corectează celula și încarcă fișierul din nou." % ALFA[1]


def test_252_randul_fara_numar_de_factura_e_spus_nu_adunat():
    """Un subtotal al partenerului (fără nr. factură) nu se adună a doua oară: e ignorat, cu motivul."""
    f = ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Sumă neachitată\n4111;%s;%s;FA-1;01.08.2026;100\n4111;%s;%s;;;100\n"
         % (ALFA + ALFA)).encode()
    ign = []
    r = sp.extrage(f, "x.csv", ignorate=ign)
    assert [(x["debit"], len(x["documente"])) for x in r] == [(100.0, 1)]
    assert [x["motiv"] for x in ign] == ["%s: rând fără numărul facturii — nu e o factură (subtotal?), nu intră" % ALFA[1]]


def test_252_documentele_din_randuri_pe_cele_doua_forme():
    """Forma pe solduri: soldul partenerului de pe 4111 / 401 = un document „Sold la 31.08.2026”, fără scadență; pe 409 nu."""
    docs, nec = sp.documente_din_randuri([
        {"cont": "401", "cui": GAMMA[0], "denumire": GAMMA[1], "debit": 0, "credit": 1000},
        {"cont": "4111", "cui": ALFA[0], "denumire": ALFA[1], "debit": 0, "credit": 50},
        {"cont": "409", "cui": BETA[0], "denumire": BETA[1], "debit": 300, "credit": 0}], DATA)
    assert [(d["directie"], d["numar"], d["data"], d["scadenta"], d["suma"]) for d in docs] == [
        ("primita", "Sold la 31.08.2026", DATA, None, Decimal("1000.00"))]
    assert nec == ["%s, contul 4111: sold creditor — nu e de încasat, nu devine document deschis" % ALFA[1],
                   "%s, contul 409: soldul rămâne pe partener — pe 409 nu se țin facturi de încasat / de plătit" % BETA[1]]


def test_252_facturile_trimise_pe_ruta_trebuie_sa_dea_soldul_partenerului():
    """Rândurile trimise direct pe rută (nu din `extrage`): facturile care nu dau soldul partenerului, sau fără dată, sunt refuzate
    înainte de orice scriere (conexiunea nu e atinsă)."""
    r = {"cont": "4111", "cui": ALFA[0], "denumire": ALFA[1], "debit": 3000, "credit": 0,
         "documente": [{"numar": "FA-1", "data": "2026-08-01", "suma": 1000}]}
    assert sp.documente_nepotrivite([r]) == ["%s: facturile dau 1.000,00 lei, soldul e 3.000,00 lei" % ALFA[1]]
    r2 = dict(r, documente=[{"numar": "FA-1", "data": "01/13/2026", "suma": 3000}])
    assert sp.documente_nepotrivite([r2]) == ["%s: factura FA-1 n-are număr sau dată din calendar" % ALFA[1]]
    assert sp.documente_nepotrivite([dict(r, documente=[{"numar": "FA-1", "data": "2026-08-01", "suma": 3000}])]) == []
    with pytest.raises(ValueError) as e:
        sp.importa(None, [r], DATA)
    assert str(e.value).startswith("Facturile deschise nu dau soldul partenerului: %s: facturile dau 1.000,00 lei" % ALFA[1])


# ── cap-coadă: import -> scadențar -> bancă -> stinsă ──────────────────────────────────────────────────────────────────────────
def test_def_252_import_scadentar_incasare_din_banca_stinge(conn):
    """Import (forma pe facturi) -> 4 facturi deschise preluate -> scadențarul (la 15.09.2026): FA-101 restantă 1.000,00 (6 zile),
    FA-102 scade în 4 zile 2.000,00, FB-7 fără scadență 2.000,00 -> extrasul cu +1.000 de la ALFA: „potrivire exactă” pe FA-101 -> notă
    5121 = 4111 1.000,00 legată de FA-101 -> scadențarul n-o mai are; plata −1.500 către GAMMA stinge G-55 (401 = 5121).
    ROȘU înainte: nicio factură preluată, scadențar gol, linia băncii „niciun document deschis pentru CUI 25200012”.
    MUTAȚIE: `_inlocuieste_documentele(cur, docs)` scos din `importa` -> 0 documente."""
    from core import reconciliere_api as rec, scadentar
    rez = _importa(conn)
    assert rez["randuri"] == 3 and not rez["respinse"], rez
    assert rez["documente"] == {"n": 4, "emise": 3, "total_emise": 5000.0, "primite": 1, "total_primite": 1500.0, "neconvertite": []}
    assert _preluate(conn) == [("FA-101", "emisa", ALFA[0], "2026-08-10", "2026-09-09", Decimal("1000.00"), Decimal("0.00")),
                               ("FA-102", "emisa", ALFA[0], "2026-08-20", "2026-09-19", Decimal("2000.00"), Decimal("0.00")),
                               ("FB-7", "emisa", BETA[0], "2026-08-25", None, Decimal("2000.00"), Decimal("0.00")),
                               ("G-55", "primita", GAMMA[0], "2026-08-15", "2026-09-14", Decimal("1500.00"), Decimal("0.00"))]
    sc = scadentar.pull(conn, SCHEMA, azi=_dt.date(2026, 9, 15))
    assert [(x["numar"], x["stare"], x["zile"], x["suma"]) for x in sc["linii"]] == [
        ("FA-101", "restanta", -6, Decimal("1000.00")), ("FA-102", "scade_curand", 4, Decimal("2000.00")),
        ("FB-7", "fara_scadenta", None, Decimal("2000.00"))]
    r = rec.importa_extras(conn, SCHEMA, [{"data": "16.09.2026", "suma": 1000, "detalii": "Incasare FA-101 CUI RO%s" % ALFA[0],
                                            "cui": ALFA[0]},
                                           {"data": "17.09.2026", "suma": -1500, "detalii": "Plata G-55 CUI RO%s" % GAMMA[0],
                                            "cui": GAMMA[0]}], fisier="extras_092026.csv")
    assert [(x["status"], x["motiv"]) for x in r["linii"]] == [("potrivit", "potrivire exactă pe o factură")] * 2, r
    for x in r["linii"]:
        assert rec.conteaza(conn, SCHEMA, x["id"])["nota"] in ("5121=4111", "401=5121")
    with conn.cursor() as cur:
        cur.execute("SELECT f.numar, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "JOIN facturi f ON f.id = i.factura_id WHERE i.sursa = 'banca' ORDER BY f.numar")
        assert cur.fetchall() == [("FA-101", "5121", "4111", Decimal("1000.00")), ("G-55", "401", "5121", Decimal("1500.00"))]
    sc = scadentar.pull(conn, SCHEMA, azi=_dt.date(2026, 9, 18))
    assert [(x["numar"], x["suma"]) for x in sc["linii"]] == [("FA-102", Decimal("2000.00")), ("FB-7", Decimal("2000.00"))]
    deschise = sorted((x["numar"], x["sold"]) for x in rec.facturi_deschise_detalii(conn, SCHEMA))
    assert deschise == [("FA-102", "2000.00"), ("FB-7", "2000.00")]


def test_def_252_forma_pe_solduri_da_un_document_pe_partener_pe_care_plata_il_stinge(conn):
    """Cazul pilotului (F085): fișierul fără facturi (401, furnizorul, creditor 1.500) -> documentul „Sold la 31.08.2026”, 1.500,00,
    fără scadență -> în potrivirea băncii -> plata −1.500: potrivire exactă, stins. ROȘU înainte: lista documentelor deschise goală."""
    from core import reconciliere_api as rec
    with conn.cursor() as cur:
        cur.execute("UPDATE solduri_initiale SET sold_debitor = 0 WHERE cont = '4111'")
        cur.execute("UPDATE solduri_initiale SET sold_debitor = 8500 WHERE cont = '5121'")
    f = ("cont;cui;denumire;sold debitor;sold creditor\n401;RO%s;%s;0;1500\n" % GAMMA).encode()
    rez = _importa(conn, f, "parteneri.csv")
    assert rez["documente"]["n"] == 1 and rez["randuri"] == 1
    d = rec.facturi_deschise_detalii(conn, SCHEMA)
    assert [(x["numar"], x["directie"], x["tert_cui"], x["data_emitere"], x["sold"]) for x in d] == [
        ("Sold la 31.08.2026", "primita", GAMMA[0], DATA, "1500.00")]
    r = rec.importa_extras(conn, SCHEMA, [{"data": "05.09.2026", "suma": -1500, "detalii": "Plata CUI %s" % GAMMA[0], "cui": GAMMA[0]}])
    assert r["linii"][0]["motiv"] == "potrivire exactă pe o factură"
    rec.conteaza(conn, SCHEMA, r["linii"][0]["id"])
    assert rec.facturi_deschise_detalii(conn, SCHEMA) == []


# ── nicio cifră a declarațiilor / balanței nu se schimbă ───────────────────────────────────────────────────────────────────────────
def _cititori(c):
    """Ce citesc declarațiile (pe luna facturilor preluate, 08/2026, și pe trimestrul ei), balanța și controlul încrucișat."""
    from core.common import Perioada
    from core import d300, d394, d390, d406, documente_api, repo_control_incrucisat as rci
    import psycopg2.extras as _E
    out = {}
    for nume, fn in (("d300", lambda: d300.pull(c, SCHEMA, Perioada(2026, luna=8))),
                     ("d394", lambda: d394.pull(c, SCHEMA, Perioada(2026, luna=8))),
                     ("d390", lambda: d390.pull(c, SCHEMA, 2026, 8)),
                     ("d406", lambda: d406.pull(c, SCHEMA, 2026, 8)),
                     ("balanta", lambda: documente_api.balanta(c, SCHEMA, 2026, 8))):
        try:
            out[nume] = repr(fn())
        except Exception as e:  # noqa: BLE001 — aceeași excepție înainte și după e tot „neschimbat”; o comparăm
            out[nume] = "EXC " + repr(e)
    with c.cursor(cursor_factory=_E.RealDictCursor) as cur:
        out["control_fara_nota"] = repr(rci.select_inregistrari_3(cur, SCHEMA, "2026-08-01", "2026-09-01"))
        out["control_facturi"] = repr(rci.select_inregistrari_6(cur, SCHEMA, "2026-08-01", "2026-09-01"))
    return out


def test_def_252_declaratiile_balanta_si_controlul_nu_se_schimba(conn):
    """D300, D394, D390, D406 (08/2026), balanța și controlul „facturi fără notă” (08/2026): aceleași
    înainte și după import — soldul facturilor preluate e deja în soldurile inițiale (OMFP 1802/2014 pct.130). MUTAȚIE: tipul
    `preluata` adăugat în `TIPURI_FISCALE` -> D300 / D394 / D406 citesc facturile -> pică."""
    inainte = _cititori(conn)
    _importa(conn)
    dupa = _cititori(conn)
    assert {k: v for k, v in dupa.items() if v != inainte[k]} == {}
    assert not any(v.startswith("EXC") for k, v in dupa.items() if k in ("d300", "d394", "d406")), dupa


def test_252_numaratoarea_facturilor_emise_din_d100_si_control_fiscal_le_ocoleste(conn):
    """Textul refuzului D100 („Există N facturi emise necontabilizate”) și semaforul D100 din Control fiscal numără facturile emise din
    trimestru: facturile preluate (nu se contează niciodată) n-au ce căuta acolo."""
    import psycopg2.extras as _E
    from core import repo_control_fiscal_api as rcf, repo_d100
    _importa(conn)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        assert repo_d100.select_facturi(cur, _dt.date(2026, 7, 1), _dt.date(2026, 10, 1))["count"] == 0
        assert rcf.select_facturi(cur, _dt.date(2026, 7, 1), _dt.date(2026, 10, 1))["count"] == 0


def test_252_lista_facturilor_si_actiunile_de_document_fiscal_le_ocolesc(conn):
    """Istoric facturi n-are facturile preluate; stornarea, ștergerea, contarea, PDF-ul și SPV-ul le refuză cu același text."""
    from core import contare_facturi as cf, efactura_trimitere as eft, facturi_api as fa, factura_pdf as fp, nomenclator_status_factura as nsf
    _importa(conn)
    assert [f["numar"] for f in fa.lista_facturi(conn)] == []
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM facturi WHERE numar = 'FA-101'")
        fid = cur.fetchone()[0]
    with pytest.raises(ValueError) as e:
        fa.storneaza(conn, fid)
    assert str(e.value) == nsf.MESAJ_SOLD_PRELUAT
    with pytest.raises(cf.RefuzContare) as e2:
        fa.sterge_factura(conn, fid)
    assert e2.value.mesaj == nsf.MESAJ_SOLD_PRELUAT
    with pytest.raises(ValueError) as e3:
        fp.genereaza_pdf({}, fa.detalii_factura(conn, fid))
    assert str(e3.value) == nsf.MESAJ_SOLD_PRELUAT
    assert eft.refuz_din_efactura(conn, SCHEMA, fid)["cod"] == "SOLD_PRELUAT"
    with cf.cursor_dict(conn) as cur:
        with pytest.raises(cf.RefuzContare) as e4:
            cf.contabilizeaza(cur, "", fid, automat=False)
    assert e4.value.cod == "SOLD_PRELUAT"
    d = fa.detalii_factura(conn, fid)
    assert d["tip"] == "preluata" and d["stare_incasare"]["stare"] == "neincasata"


# ── al doilea import (426) și legăturile ─────────────────────────────────────────────────────────────────────────────────────────
def test_def_252_al_doilea_import_cere_confirmare_si_nu_sterge_facturi_stinse(conn):
    """Al doilea import: confirmarea înlocuirii numește și facturile deschise vechi; după o încasare legată de FA-101, înlocuirea e
    refuzată numit (nimic scris). MUTAȚIE: verificarea `vechi["legate"]` scoasă din `importa` -> nota băncii cade pe cheia străină."""
    from core import migrare_api as mig, reconciliere_api as rec
    _importa(conn)
    with pytest.raises(mig.InlocuireNeconfirmata) as e:
        _importa(conn)
    assert str(e.value).startswith("Firma are deja solduri pe parteneri la 31.08.2026: 3 parteneri, debit 5.000,00 lei, credit 1.500,00 "
                                   "lei, cu 4 facturi deschise preluate. Fișierul nou: 3 parteneri, debit 5.000,00 lei, credit 1.500,00 lei. "
                                   "Salvarea le înlocuiește pe cele vechi."), str(e.value)
    assert _importa(conn, inlocuieste=True)["documente"]["n"] == 4      # fără legături: înlocuite
    r = rec.importa_extras(conn, SCHEMA, [{"data": "16.09.2026", "suma": 1000, "detalii": "Incasare", "cui": ALFA[0]}])
    rec.conteaza(conn, SCHEMA, r["linii"][0]["id"])
    with pytest.raises(ValueError) as e:
        _importa(conn, inlocuieste=True)
    assert str(e.value) == sp.MESAJ_DOCUMENTE_LEGATE % "FA-101 (%s, 1.000,00 lei)" % ALFA[1]
    assert len(_preluate(conn)) == 4


# ── auditul de preluare ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_252_auditul_confrunta_facturile_preluate_cu_soldul_partenerului(conn):
    """Verde după import; după ce o factură preluată lipsește, diferența se spune pe partener."""
    from core import audit_preluare as ap
    _importa(conn)
    r = ap.verifica_documente_preluate(conn, SCHEMA)
    assert [(c["stare"], c["mesaj"]) for c in r] == [
        ("verde", "Facturile deschise preluate dau soldul fiecărui partener (3 parteneri pe 4111 / 401).")]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM facturi WHERE numar = 'FA-102'")
    r = ap.verifica_documente_preluate(conn, SCHEMA)
    assert [(c["stare"], c["mesaj"]) for c in r] == [
        ("rosu", "Contul 4111, %s: facturile deschise preluate dau 1.000,00 lei, iar soldul preluat al partenerului e 3.000,00 lei "
                 "(diferență 2.000,00 lei)." % ALFA[1])]


# ── datele existente (migrarea) ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_252_migrarea_scrie_documentele_soldurilor_vechi_si_sare_contul_cu_plati_nelegate(conn):
    """Soldurile pe parteneri salvate înainte de reparație (fără documente): migrarea scrie „Sold la 31.08.2026” pe fiecare partener —
    numai pe contul fără încasări / plăți nelegate de facturi după preluare (aici 401 are o plată de mână de 500: sărit, numit)."""
    from core import migrare_documente_preluate as m
    with conn.cursor() as cur:
        sp.asigura_tabel(conn)
        for cont, cui, den, d, c in (("4111", ALFA[0], ALFA[1], 3000, 0), ("4111", BETA[0], BETA[1], 2000, 0), ("401", GAMMA[0], GAMMA[1], 0, 1500)):
            cur.execute("INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) VALUES (%s,%s,%s,%s,%s,%s)",
                        (cont, cui, den, d, c, DATA))
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-09-05', 'plata', 'banca', 'validata') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '401', '5121', 500)", (iid,))
    r = m.aplica(conn, SCHEMA)
    assert r["documente"] == 2 and r["sarite"] == [
        "contul 401: după 2026-08-31 are încasări / plăți nelegate de facturi (net 500.00 lei) — soldurile partenerilor lui nu devin "
        "documente; se reîncarcă din ecran după legarea lor"], r
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
    assert [(x[0], x[2], x[5]) for x in _preluate(conn)] == [("Sold la 31.08.2026", ALFA[0], Decimal("3000.00")),
                                                            ("Sold la 31.08.2026", BETA[0], Decimal("2000.00"))]
    assert m.verifica(conn, SCHEMA) is True
    assert m.aplica(conn, SCHEMA) == {"index": False, "documente": 0, "sarite": []}      # idempotentă


def test_252_template_are_indexul_numerotarii_fara_facturile_preluate():
    from core import migrare_unic_numar_factura as mu
    t = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    assert ("CREATE UNIQUE INDEX IF NOT EXISTS facturi_numar_emisa_uniq ON TENANT_PLACEHOLDER.facturi (COALESCE(serie, ''), numar) WHERE "
            + mu.CONDITIE + ";") in t

