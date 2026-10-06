# -*- coding: utf-8 -*-
"""GARDA pasului C din comanda Costin 05.10.2026 („fluxul de factură pe F1”, pct.6–9), pe schemă efemeră din `tenant_template.sql`.

Costin, verbatim (DECIZII 05.10.2026):
  6. „Notele automate (607=371 la emitere, 627=5121 din extras) poartă documentul sursă. Validarea unei note fără document
     justificativ trece fără niciun avertisment — validatorul trebuie să vadă lipsa înainte să apese.”
  7. „Detaliul facturii afișează «contabilizată» cât timp nota e ciornă. Starea spune adevărul …, iar din factură se ajunge la
     nota ei.”
  8. „Mesaje false la bancă … Mesajul spune exact ce s-a întâmplat. Liniile noi ale extrasului apar primele.”
  9. „cantități și prețuri cu zecimale în exces și fără unitate; prețul din nomenclator nu se precompletează …”

Temeiul pentru coloana „document justificativ”: OMFP 2634/2015 (Registrul-jurnal, cod 14-1-1, col.3 — „felul, numărul și data
documentului justificativ”). Restul pașilor nu invocă o regulă fiscală — sunt adevărul afișat al unor stări pe care aplicația
le știe.
"""
import datetime
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_flux_f1_c"
ZI = datetime.date(2026, 10, 5)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'ZT Flux SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")   # [06.10.2026 §6.3]
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _factura_cu_articol(conn, numar="FCT12", serie="FCT"):
    from core import stocuri_cv_api as cv
    art = cv.intrare(conn, SCH, {"denumire": "Pâine", "um": "buc", "data": "2026-10-01", "cantitate": 10, "pret_unitar": 2})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva) VALUES (%s, %s, %s, 'emisa', 10, 0) RETURNING id",
                    (numar, serie, ZI))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, articol_id) "
                    "VALUES (%s, 'Pâine', 2, 5, 11, %s)", (fid, art["articol_id"]))
    return fid


# ── C1: notele automate poartă documentul ───────────────────────────────────────────────────────────────────────────────
def test_descarcarea_din_factura_poarta_factura_ca_document_justificativ(conn):
    """MUTAȚIE: `document_ref` scos din INSERT-ul notei în `stocuri_cv_api.iesire` -> None -> pică."""
    from core import stocuri_cv_api as cv
    fid = _factura_cu_articol(conn)
    r = cv.descarca_factura(conn, SCH, fid, ZI)
    assert r["erori"] == [] and len(r["descarcate"]) == 1
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref, factura_id FROM inregistrari WHERE sursa = 'stocuri'")
        rows = cur.fetchall()
    # factura_id rămâne NULL: nota 607=371 nu e nici contare, nici plată — legată, ar bloca ștergerea facturii (ARE_NOTA_LEGATA)
    assert rows == [("Factură FCT12 din 05.10.2026", None)]


def test_iesirea_manuala_poarta_documentul_scris(conn):
    from core import stocuri_cv_api as cv
    art = cv.intrare(conn, SCH, {"denumire": "Făină", "data": "2026-10-01", "cantitate": 5, "pret_unitar": 3})
    cv.iesire(conn, SCH, {"articol_id": art["articol_id"], "data": ZI, "cantitate": 1, "document": "Bon de consum 7"})
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE sursa = 'stocuri'")
        assert cur.fetchone()[0] == "Bon de consum 7"


def test_documentul_justificativ_nu_dubleaza_seria_si_scrie_data_romaneste():
    """Numărul facturii emise conține deja seria (`facturi_api`: numar = serie + număr). MUTAȚIE: compunerea veche
    (serie + număr, data ISO) -> „FCTFCT12 din 2026-10-05” -> pică."""
    from core import jurnal_api as j
    assert j.document_justificativ(None, "factura", "FCT", "FCT12", ZI) == "Factură FCT12 din 05.10.2026"
    assert j.document_justificativ(None, "factura", "FCT", "12", ZI) == "Factură FCT12 din 05.10.2026"   # număr fără serie
    assert j.document_justificativ(None, "factura", None, "A-77", ZI) == "Factură A-77 din 05.10.2026"   # primită
    assert j.document_justificativ("Extras bancar x.csv din 05.10.2026", "factura", "FCT", "FCT12", ZI) == "Extras bancar x.csv din 05.10.2026"
    assert j.document_justificativ(None, None, None, None, ZI) is None


# ── C4: banca ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _importa(conn, linii, fisier="extras_oct.csv"):
    from core import banca, reconciliere_api as rec
    tr = []
    for suma, detalii in linii:
        r = banca.regula_cont({"sens": "debit" if suma < 0 else "credit", "suma": abs(suma), "descriere": detalii})
        tr.append({"suma": suma, "detalii": detalii, "data": "2026-10-05", "cui": r.get("cui"), "tip": r.get("tip"), "nota": r.get("nota")})
    return rec.importa_extras(conn, SCH, tr, fisier, "continut-" + fisier + str(linii))


def test_contarea_pe_nota_propusa_se_opreste_si_spune_nota_creata(conn):
    """Constatarea lui Costin: după contare, „Nota 401=5121 — 0 înregistrări create” deși s-a creat 627=5121. Cauza:
    ramura notei propuse nu se oprea — cădea în ramura alocărilor (fără alocări: 0 note, nota 401=5121 din tipul liniei) și
    rescria `inregistrari_ids` cu []. MUTAȚIE: `return`-ul scos din ramura notei propuse -> pică."""
    from core import reconciliere_api as rec
    r = _importa(conn, [(-12.5, "Comision administrare cont")])
    lid = r["linii"][0]["id"]
    rez = rec.conteaza(conn, SCH, lid)
    assert rez["nota"] == "627=5121" and len(rez["inregistrari"]) == 1
    with conn.cursor() as cur:
        cur.execute("SELECT alocari->'inregistrari_ids', status FROM extras_linii WHERE id = %s", (lid,))
        ids, st = cur.fetchone()
        assert ids == rez["inregistrari"] and st == "contat"
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (rez["inregistrari"][0],))
        assert cur.fetchone()[0] == "Extras bancar extras_oct.csv din 05.10.2026"


def test_contarea_pe_factura_poarta_extrasul(conn):
    from core import reconciliere_api as rec, facturi_api as fa
    f = fa.creeaza_factura(conn, "FCT20", "2026-10-01", "emisa", [{"descriere": "x", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}],
                           tert_nume="Client SRL", tert_cui="14399840")
    r = _importa(conn, [(121.0, "Incasare factura FCT20 CUI 14399840")])
    lid = r["linii"][0]["id"]
    rez = rec.conteaza(conn, SCH, lid, [{"factura_id": f["factura_id"], "suma": "121.00"}])
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref, factura_id FROM inregistrari WHERE id = ANY(%s)", (rez["inregistrari"],))
        assert cur.fetchall() == [("Extras bancar extras_oct.csv din 05.10.2026", f["factura_id"])]


def test_importul_numara_ce_s_a_potrivit_si_ce_nu(conn):
    """„2 linii importate și potrivite” când una era fără potrivire. MUTAȚIE: `rezumat` scos -> pică."""
    r = _importa(conn, [(-12.5, "Comision administrare cont"), (500.0, "Incasare necunoscuta")])
    assert r["rezumat"] == {"total": 2, "potrivite": 0, "fara_potrivire": 2}


def test_filtrul_pe_stare_si_ordinea_liniilor(conn):
    """Filtrul primea stările „noua/potrivita/…”, baza scrie „nou/potrivit/…” -> lista era mereu goală. Liniile noi apar
    primele. MUTAȚIE: ordinea veche `ORDER BY data, id` -> pică."""
    from core import reconciliere_api as rec, uc_tenants
    _importa(conn, [(-1.0, "Comision vechi")], "a.csv")
    _importa(conn, [(-2.0, "Comision nou")], "b.csv")
    toate = rec.lista(conn, SCH)
    assert [x["descriere"] for x in toate] == ["Comision nou", "Comision vechi"]
    assert [x["descriere"] for x in rec.lista(conn, SCH, "nou")] == ["Comision nou", "Comision vechi"]
    assert set(uc_tenants.STARI_EXTRAS) == {"nou", "potrivit", "contat", "ignorat"}


def test_sugestia_invatata_ruleaza_pe_linia_de_tip_necunoscut(conn):
    """Ramura `ai_sugestie_v1` din `importa_extras` era cod mort: `regula_cont` pune mereu o notă implicită (client/furnizor),
    iar ramura cerea „fără notă”. Pe o linie al cărei tip nu se recunoaște din descriere, istoricul validat (`ai_corectii`)
    propune contul. MUTAȚIE: condiția veche (`not t.get("nota")`) -> nota rămâne 401=5121 -> pică."""
    with conn.cursor() as cur:
        for _ in range(3):
            cur.execute("INSERT INTO ai_corectii (context, cont_propus, cont_final, corectat) VALUES (%s, '628', '628', false)",
                        (__import__("core.ai_incredere", fromlist=["x"]).normalizeaza("Plata abonament internet"),))
    r = _importa(conn, [(-50.0, "Plata abonament internet")])
    assert r["linii"][0]["incredere"] == "sigur"
    with conn.cursor() as cur:
        cur.execute("SELECT nota_propusa->>'debit', nota_propusa->>'credit' FROM extras_linii")
        assert cur.fetchone() == ("628", "5121")


# ── clasa „seria dublată” (generalizare C1) ─────────────────────────────────────────────────────────────────────────────────
def test_e_factura_poarta_numarul_facturii_fara_seria_dublata():
    """Numărul unei facturi emise conține deja seria (măsurat 05.10.2026 în baza de test: 19 din 19 facturi emise cu serie).
    `efactura_send` compunea serie + număr -> ID-ul către ANAF ar fi fost „COERCOER-T3”, altul decât cel de pe PDF.
    MUTAȚIE: compunerea veche în `genereaza_xml` -> pică."""
    import xml.etree.ElementTree as ET
    from core import efactura_send as ef
    from core.test_efactura_send import _factura_minima, _linii, _furnizor, _client
    root = ET.fromstring(ef.genereaza_xml(_factura_minima(serie="FCT", numar="FCT0007"), _linii(), _furnizor(), _client()))
    assert root.find("cbc:ID", {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}).text == "FCT0007"


def test_nicio_compunere_serie_plus_numar_in_afara_helperului():
    """GARD DE CLASĂ: numărul cu serie se compune numai prin `pdf_util.numar_cu_serie` (Python) și `numarCuSerie` (api.js).
    MUTAȚIE: `"%s%s" % (factura.get("serie") or "", factura.get("numar") or "")` repus în efactura_send -> pică."""
    import glob
    import re
    rele = []
    for p in glob.glob(os.path.join(RAD, "core", "*.py")):
        if os.path.basename(p).startswith("test_") or p.endswith("pdf_util.py"):
            continue
        for i, ln in enumerate(io.open(p, encoding="utf-8"), 1):
            if re.search(r"""%s%s["']\s*%\s*\(.*serie.*numar(?!_int)""", ln) or re.search(r"""\(\s*serie\s+or\s+["']{2}\s*\)\s*\+""", ln):
                rele.append("%s:%d" % (os.path.basename(p), i))
    for p in glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True):
        if p.endswith(os.sep + "api.js"):
            continue
        for i, ln in enumerate(io.open(p, encoding="utf-8"), 1):
            if re.search(r"""serie\s*\|\|\s*["']{2}\s*\)?\s*\}\s*\$\{\s*(?:esc\()?\s*[\w.]*numar""", ln):
                rele.append("%s:%d" % (os.path.basename(p), i))
    assert not rele, "serie + număr compus în afara helperului (dublează seria când numărul o conține): %s" % rele


# ── C2: nota fără document justificativ ───────────────────────────────────────────────────────────────────────────────────
def test_documentul_justificativ_se_poate_scrie_pe_nota(conn):
    """Avertismentul de la validare spune „scrie referința în notă” — mesajul nu promite ce aplicația nu face (Costin 05.10):
    creează și editează primesc `document_ref`. MUTAȚIE: `document_ref` scos din UPDATE-ul lui `editeaza` -> pică."""
    from core import jurnal_api as j
    r = j.creeaza(conn, SCH, "Chirie octombrie", "2026-10-05", [{"debit": "612", "credit": "401", "suma": 100}],
                  document_ref="Factură CH-9 din 01.10.2026")
    assert r["ok"]
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (r["id"],))
        assert cur.fetchone()[0] == "Factură CH-9 din 01.10.2026"
    j.editeaza(conn, SCH, r["id"], document_ref="Contract 4/2026")
    j.editeaza(conn, SCH, r["id"], descriere="Chirie oct.")          # fără document_ref: neschimbat
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref, descriere FROM inregistrari WHERE id = %s", (r["id"],))
        assert cur.fetchone() == ("Contract 4/2026", "Chirie oct.")



# ── C3: starea facturii spune adevărul ────────────────────────────────────────────────────────────────────────────────────
def _nota(conn, data, linii, factura_id, status, sursa="facturi"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status) VALUES (%s,%s,'n',%s,%s) RETURNING id",
                    (data, factura_id, sursa, status))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                        (nid, d, c, Decimal(str(s))))
    return nid


def test_contabilizata_numai_cu_nota_de_contare_validata(conn):
    """„Detaliul facturii afișează «contabilizată» cât timp nota e ciornă.” Înainte: `EXISTS(orice notă cu factura_id)` — și
    ciorna, și încasarea din bancă făceau factura „contabilizată”. Acum: nota de CONTARE (predicatul canonic
    `contare_facturi.e_nota_de_contare`) și VALIDATĂ; `nota_contare` spune care și în ce stare.
    MUTAȚIE: predicatul vechi (orice notă) -> factura cu doar încasare iese contabilizată -> pică."""
    from core import facturi_api as fa
    with conn.cursor() as cur:
        ids = []
        for nr in ("Z1", "Z2", "Z3"):
            cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva) VALUES (%s, %s, 'emisa', 121, 21) RETURNING id",
                        (nr, ZI))
            ids.append(cur.fetchone()[0])
    ciorna = _nota(conn, ZI, [("4111", "707", 100), ("4111", "4427", 21)], ids[0], "ciorna")
    _nota(conn, ZI, [("5121", "4111", 121)], ids[1], "validata", sursa="banca")                 # doar încasarea
    valid = _nota(conn, ZI, [("4111", "707", 100), ("4111", "4427", 21)], ids[2], "validata")
    pe = {f["id"]: f for f in fa.lista_facturi(conn)}
    assert (pe[ids[0]]["contabilizata"], pe[ids[0]]["nota_contare"]["id"], pe[ids[0]]["nota_contare"]["status"]) == (False, ciorna, "ciorna")
    assert (pe[ids[1]]["contabilizata"], pe[ids[1]]["nota_contare"]) == (False, None)
    assert (pe[ids[2]]["contabilizata"], pe[ids[2]]["nota_contare"]["id"]) == (True, valid)
    d = fa.detalii_factura(conn, ids[0])
    assert d["contabilizata"] is False and d["nota_contare"] == {"id": ciorna, "status": "ciorna", "data": "2026-10-05"}


# ── C5: linia de factură ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_propunerea_pentru_linie_ia_pretul_si_um_din_nomenclator(conn, monkeypatch):
    """„prețul din nomenclator nu se precompletează”: potrivirea pe linie întreba doar cota (AI), fără să caute produsul în
    nomenclator. Acum nomenclatorul e întâi (cota, UM, preț); AI-ul numai pentru o denumire necunoscută.
    MUTAȚIE: căutarea în nomenclator scoasă -> pică pe preț/UM."""
    from core import produse_api as pa, cote_tva
    monkeypatch.setattr(cote_tva, "potriveste_cota", lambda d, platitor_tva=True: {"ok": True, "cota": 21, "sursa": "ai"})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO produse (denumire, um, pret_unitar, cota_tva, sursa, confirmat) VALUES ('Pâine albă', 'kg', 4.5, 11, 'manual', true)")
    r = pa.propunere_pentru_linie(conn, "pâine ALBĂ ", True)
    assert (r["ok"], r["cota"], r["um"], r["pret_unitar"], r["sursa"]) == (True, 11, "kg", 4.5, "nomenclator")
    r = pa.propunere_pentru_linie(conn, "Consultanță fiscală", True)
    assert (r["cota"], r.get("um"), r.get("pret_unitar"), r["sursa"]) == (21, None, None, "ai")
    r = pa.propunere_pentru_linie(conn, "Pâine albă", False)            # neplătitor: cota 0 prin lege, prețul tot din nomenclator
    assert (r["cota"], r["pret_unitar"]) == (0, 4.5)


def test_descrierea_notei_de_iesire_are_cantitatea_cu_um(conn):
    """„x2.000”: descrierea notei 607=371 purta cantitatea brută a coloanei NUMERIC(12,3)."""
    from core import stocuri_cv_api as cv
    fid = _factura_cu_articol(conn)
    cv.descarca_factura(conn, SCH, fid, ZI)
    with conn.cursor() as cur:
        cur.execute("SELECT descriere FROM inregistrari WHERE sursa = 'stocuri'")
        assert cur.fetchone()[0] == "Ieșire stoc Pâine × 2 buc"


# ── C6: generalizarea pct.6 — notele automate care au documentul în mână îl poartă ─────────────────────────────────────────
def test_eticheta_documentului_e_derivata_nu_fabricata():
    from core import jurnal_api as j
    assert j.eticheta_document("NIR", "12", ZI) == "NIR nr 12 din 05.10.2026"
    assert j.eticheta_document("Bon fiscal", None, ZI, "Mega Image") == "Bon fiscal din 05.10.2026 (Mega Image)"   # fără număr: se omite
    assert j.eticheta_document("Raport Z", "0007", "2026-07-10", "casa 8000000002") == "Raport Z nr 0007 din 10.07.2026 (casa 8000000002)"


def test_nota_de_casa_poarta_documentul_operatiunii(conn):
    """MUTAȚIE: `document_ref` scos din INSERT-ul notei în `casa_api.adauga` -> None -> pică."""
    from core import casa_api
    r = casa_api.adauga(conn, SCH, {"data": "2026-10-05", "categorie": "depunere_banca", "suma": 100, "document": "DP 7"})
    assert not r.get("eroare"), r
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE sursa = 'casa'")
        assert [x[0] for x in cur.fetchall()] == ["DP 7"]


def test_notele_nir_poarta_nir_ul(conn):
    """MUTAȚIE: documentul netransmis la `_noteaza` -> None -> pică."""
    from core import stocuri_api
    r = stocuri_api.adauga_nir(conn, SCH, {"numar": "12", "data": "2026-10-05", "furnizor": "Furnizor SRL",
                                    "linii": [{"denumire": "Făină", "cantitate": 10, "pret_achizitie": 3, "pret_vanzare": 4.5, "cota_tva": 11}]})
    assert not r.get("eroare"), r
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT document_ref FROM inregistrari WHERE sursa = 'stocuri'")
        assert [x[0] for x in cur.fetchall()] == ["NIR nr 12 din 05.10.2026"]


class _FaraCommit:
    """Conexiunea fixturii cu `commit()` neutralizat: ruta comite, fixtura aruncă schema."""

    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture()
def uc(conn, monkeypatch):
    import contextlib
    from core import uc_tenants, auth_api, uc_comun
    proxy = _FaraCommit(conn)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
    monkeypatch.setattr(uc_comun, "_schema_cabinet_sau_404", lambda *a, **k: SCH)
    monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
    return uc_tenants


def test_nota_bonului_si_a_statului_de_plata_poarta_documentul(conn, uc, monkeypatch):
    """Bonul aprobat și statul de plată contat: documentul lor e al notei. MUTAȚIE: documentul netransmis din
    `bon_aproba` / `salarii_contare_scrie` -> None -> pică."""
    import types
    from core import salarii_contare
    with conn.cursor() as cur:
        cur.execute("INSERT INTO bonuri (comerciant, data, total, tip) VALUES ('Mega Image', '2026-10-05', 12.1, 'bon') RETURNING id")
        bid = cur.fetchone()[0]
    b = types.SimpleNamespace(data="2026-10-05", comerciant="Mega Image", total=12.1, tva=0,
                              linii=[types.SimpleNamespace(cont="604", valoare=12.1)])
    uc.bon_aproba(1, bid, b, {"uid": 1})
    monkeypatch.setattr(salarii_contare, "propunere", lambda *a: {"document_ref": "SAL-2026-09", "note": [{"debit": "641", "credit": "421", "suma": 100}]})
    uc.salarii_contare_scrie(1, 2026, 9, {"uid": 1})
    with conn.cursor() as cur:
        cur.execute("SELECT sursa, document_ref FROM inregistrari WHERE sursa IN ('bon', 'salarii') ORDER BY sursa")
        # [lotul 07.10 pct.13] documentul statului din sursa unică `jurnal_api.eticheta_document` (fel, număr, data = ultima zi)
        assert cur.fetchall() == [("bon", "Bon fiscal din 05.10.2026 (Mega Image)"), ("salarii", "Stat de plată nr SAL-2026-09 din 30.09.2026")]
