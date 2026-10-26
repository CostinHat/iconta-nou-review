# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 pct.6 (verbatim în DECIZII „Comanda 12.2”), pachetul `fact2` — C73.1 (grav).

„Aceeași factură de furnizor (CUI 14399840, nr. LIC-73, 1.000 + 210) introdusă de două ori la «Achiziție necorporală» pe F1 a generat două
note 205 = 404 / 4426 = 404, fără niciun avertisment: imobilizarea și TVA-ul deductibil se dublează. Dublura (același furnizor + același
număr de factură) se oprește pe toate căile prin care intră o factură de furnizor.”

Cheia și refuzul: `core/factura_primita_dublura.py`; citirea: `repo_facturi.primite_cu_aceeasi_cheie`; cele trei căi prin care se naște o
factură (`core/scan_cai_factura.py`): `facturi_api.creeaza_factura` (Operațiuni, `POST /facturi`), `uc_comun._factura_din_parsat` (XML / SPV,
factura de mână, importul de fișiere), `solduri_parteneri_api._scrie_documente` (preluarea soldurilor).

Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c — „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui
document”: un singur document justifică o singură înregistrare a cheltuielii / imobilizării și a TVA-ului de dedus.
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417); zilele sunt SINTETICE (2099). CUI-urile 14399840 și 18547290: cifra de
control verificată cu algoritmul oficial (`test_cuiurile_de_proba_au_cifra_de_control_buna`)."""
import ast
import io
import os
from decimal import Decimal as D

import pytest

from core import chei_unice, erori, facturi_api, factura_primita_dublura as fpd, repo_facturi, solduri_parteneri_api as spa
from core import uc_comun, uc_factura_primita as ufp
from core.test_417_storno_trimitere import _SCHEMA, _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cui_valid(cui):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    return (0 if r == 10 else r) == ctrl


def test_cuiurile_de_proba_au_cifra_de_control_buna():
    assert _cui_valid("14399840") and _cui_valid("18547290")


# ── pur: cheia ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c73_1_numarul_cheii_ignora_semnele_spatiile_si_zerourile():
    """„LIC-73” din XML (BT-1, fără serie separată), „LIC 73”, „lic/073” și seria „LIC” + numărul „73” (factura de mână) sunt aceeași
    factură; „0” singur rămâne; alt număr e altă factură. MUTAȚIE: fără `_ZEROURI` -> „LIC073” ≠ „LIC73” -> pică."""
    assert {fpd.numar(None, "LIC-73"), fpd.numar(None, "LIC 73"), fpd.numar("lic", "/073"), fpd.numar("LIC", "73"),
            fpd.numar("LIC-", "0073")} == {"LIC73"}
    assert fpd.numar(None, "A0") == "A0" and fpd.numar(None, "0") == "0" and fpd.numar(None, "") == "" and fpd.numar(None, None) == ""
    assert fpd.numar(None, "LIC-74") != fpd.numar(None, "LIC-73")


def test_def_c73_1_furnizorul_e_codul_fiscal_altfel_denumirea():
    """Codul fiscal în forma păstrată („RO14399840” și „14399840” sunt același furnizor); fără cod, denumirea normalizată."""
    assert fpd.furnizor("RO 14399840", "X") == fpd.furnizor("14399840", "Y") == (True, "14399840")
    assert fpd.furnizor("", "Ion Popescu P.F.") == fpd.furnizor(None, "ION POPESCU PF") == (False, "IONPOPESCUPF")


@DB
def test_def_c73_1_cheia_e_aceeasi_in_python_si_in_sql(conn):
    """Paritatea normalizării: aceeași cheie în Python (factura nouă) și în SQL (facturile din bază), inclusiv pe litere din afara ASCII
    (scoase în ambele) și pe zerourile din fața cifrelor."""
    probe = [("LIC", "73"), (None, "LIC-0073"), ("ș", "ă-07"), ("F1A", "014"), (None, "Sold la 01.01.2026"), ("", "0")]
    with conn.cursor() as cur:
        for serie, nr in probe:
            cur.execute("SELECT " + fpd.SQL_NUMAR.format(serie="%s::text", numar="%s::text"), (serie, nr))
            assert cur.fetchone()[0] == fpd.numar(serie, nr), (serie, nr)
        cur.execute("SELECT " + fpd.SQL_NUME.format(nume="%s::text"), ("Ion Popescu P.F. ș",))
        assert cur.fetchone()[0] == fpd.furnizor(None, "Ion Popescu P.F. ș")[1]


# ── pe bază ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _primita(conn, numar="LIC-73", cui="14399840", nume="DANTE INTERNATIONAL SA", data="2099-03-10", pret="1000", serie=None, tip="factura",
             cant=1):
    return facturi_api.creeaza_factura(conn, numar, data, "primita", [{"descriere": "Licență", "cantitate": cant, "pret_unitar": pret,
                                                                       "cota_tva": 21}],
                                       tert_nume=nume, tert_cui=cui, status="importata", tert_platitor_tva=True, serie=serie, tip=tip)


def _n(conn, numar_cheie="LIC73"):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE directie = 'primita' AND " + fpd.SQL_NUMAR.format(serie="serie", numar="numar")
                    + " = %s", (numar_cheie,))
        return cur.fetchone()[0]


@DB
def test_def_c73_1_a_doua_introducere_prin_operatiuni_se_refuza(conn):
    """C73.1, cazul lui Costin: LIC-73 de la 14399840 (1.000 + 210) a doua oară, pe drumul Operațiunilor (`creeaza_factura`, directie
    primită) — cu altă dată și scrisă altfel („lic 73”): refuz numit, cu factura existentă (număr, dată, total), nimic scris.
    MUTAȚIE: verificarea scoasă din `creeaza_factura` -> a doua factură intră -> pică."""
    _primita(conn)
    with pytest.raises(chei_unice.CheieDublata) as e:
        _primita(conn, numar="lic 73", data="2099-03-11", cui="RO14399840")
    assert str(e.value).startswith("Factura LIC-73 de la DANTE INTERNATIONAL SA e deja înregistrată: factura LIC-73 din 10.03.2099, "
                                   "1.210,00 lei. O factură de furnizor intră o singură dată în evidență"), str(e.value)
    assert _n(conn) == 1


@DB
def test_def_c73_1_cazurile_legitime_trec(conn):
    """Permis: alt furnizor cu același număr; stornarea furnizorului (cu minus) cu același număr; alt număr de la același furnizor; borderoul
    (cheia lui proprie). MUTAȚIE: semnul scos din comparație -> stornarea e refuzată -> pică."""
    _primita(conn)
    _primita(conn, cui="18547290", nume="ALT FURNIZOR SRL")
    _primita(conn, cant=-1)
    _primita(conn, numar="LIC-74")
    assert _n(conn) == 3 and _n(conn, "LIC74") == 1


def _xml_f(conn, numar, data, serie=None, xml="<Invoice>LIC-73</Invoice>"):
    f = ufp.factura_din_formular({"tert_tara": "RO", "tert_cui": "RO14399840", "tert_nume": "DANTE INTERNATIONAL SA", "serie": serie or "",
                                  "numar": numar, "data_emitere": data, "moneda": "RON", "cont": "205",
                                  "linii": [{"descriere": "Licență", "cantitate": "1", "um": "buc", "pret_unitar": "1000",
                                             "cota_tva": "21"}]})
    f.update(xml=xml, manuala=False)
    return f


@DB
def test_def_c73_1_xml_dupa_factura_existenta_se_refuza_acelasi_xml_se_leaga(conn):
    """Calea XML (`_factura_din_parsat`, folosită de SPV, de „Importă XML” și de factura de mână): LIC-73 deja intrată din Operațiuni ->
    XML-ul aceleiași facturi (altă dată) se refuză, cu sfatul de respingere; același document e-Factura importat de două ori se leagă de
    factura lui (nimic scris a doua oară). MUTAȚIE: refuzul scos din `_factura_din_parsat` -> a doua factură intră -> pică."""
    with conn.cursor() as cur:
        f1 = _xml_f(conn, "LIC-77", "2099-03-01", xml="<Invoice>LIC-77</Invoice>")
        fid, nou = uc_comun._factura_din_parsat(cur, _SCHEMA, f1)
        assert nou is True
        assert uc_comun._factura_din_parsat(cur, _SCHEMA, dict(f1)) == (fid, False)   # același XML: legat, nu scris
        with pytest.raises(chei_unice.CheieDublata) as e:   # alt XML (altă dată), aceeași factură
            uc_comun._factura_din_parsat(cur, _SCHEMA, _xml_f(conn, "LIC 77", "2099-03-02", xml="<Invoice>altul</Invoice>"))
        assert str(e.value).endswith("Dacă ai primit-o din SPV, respinge-o din lista facturilor de validat, cu motivul „dublură”."), e.value
    _primita(conn)
    with conn.cursor() as cur, pytest.raises(chei_unice.CheieDublata):
        uc_comun._factura_din_parsat(cur, _SCHEMA, _xml_f(conn, "LIC-73", "2099-04-01"))
    assert _n(conn) == 1 and _n(conn, "LIC77") == 1


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, k):
        return getattr(self._c, k)


@DB
def test_def_c73_1_factura_de_mana_cu_alta_data_se_refuza(conn):
    """Factura de mână (`uc_factura_primita.valideaza`): LIC-73 deja intrată din Operațiuni; seria „LIC” + numărul „73”, cu altă dată ->
    `Conflict`, refuzul lângă numărul facturii (`pm-numar`). Înainte cheia cerea și data, deci trecea."""
    _primita(conn)
    corp = {"tert_tara": "RO", "tert_cui": "14399840", "tert_nume": "DANTE INTERNATIONAL SA", "serie": "LIC", "numar": "73",
            "data_emitere": "2099-03-20", "moneda": "RON", "cont": "205",
            "linii": [{"descriere": "Licență", "cantitate": "1", "um": "buc", "pret_unitar": "1000", "cota_tva": "21"}],
            "destinatii": ["taxabil"], "conturi": [""],
            # [lotul 13, 601] linia pe un cont de imobilizare (205) cere fișa activului înaintea oricărei verificări: o dăm completă, ca să
            # rămână testat refuzul dublurii (nu cel al fișei)
            "imobilizari": [{"cod_catalog": "", "dnf_luni": "36", "data_pif": "2099-03-20", "metoda": "liniara"}]}
    with pytest.raises(erori.Conflict) as e:
        ufp.valideaza(_FaraCommit(conn), _SCHEMA, ufp.factura_din_formular(corp), dict(corp), {"platitor_tva": True, "tva_la_incasare": False})
    assert e.value.detaliu["erori_campuri"][0]["camp"] == "pm-numar" and e.value.detaliu["cod"] == "CHEIE_DUBLATA", e.value.detaliu
    assert _n(conn) == 1


@DB
def test_def_c73_1_preluarea_soldurilor_nu_dubleaza(conn):
    """Preluarea soldurilor (`_scrie_documente`): factura deschisă de furnizor deja în evidență -> refuz, nimic scris; aceeași factură de
    două ori în același fișier -> refuz. Factura de client (emisă) nu e atinsă. MUTAȚIE: verificarea scoasă -> intră -> pică."""
    _primita(conn)
    doc = {"directie": "primita", "tert_cui": "14399840", "tert_nume": "DANTE INTERNATIONAL SA", "numar": "LIC-73", "data": "2099-01-31",
           "scadenta": None, "suma": D("1210.00")}
    nou = dict(doc, numar="LIC-80")
    for docs in ([doc], [nou, dict(nou)]):
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT p")   # refuzul anulează salvarea întreagă (aici, ca la `get_conn`: înapoi la punctul de dinainte)
            with pytest.raises(chei_unice.CheieDublata):
                spa._scrie_documente(cur, docs)
            cur.execute("ROLLBACK TO SAVEPOINT p")
    with conn.cursor() as cur:
        spa._scrie_documente(cur, [nou, dict(doc, directie="emisa", numar="LIC-73")])
    assert _n(conn) == 1 and _n(conn, "LIC80") == 1
    # factura preluată intră în comparație: aceeași factură introdusă după preluare se refuză (soldul ei e deja în balanța de deschidere)
    with pytest.raises(chei_unice.CheieDublata):
        _primita(conn, numar="LIC-80")


@DB
def test_def_c73_1_lista_dublurilor_existente(conn):
    """Dublurile scrise înainte de reparație (cum sunt cele două LIC-73 de pe F1) se văd, grupate, fără a fi atinse."""
    _primita(conn)
    with conn.cursor() as cur:   # a doua, scrisă pe ocolite (cum intra înainte de C73.1)
        cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, moneda, directie, status, tert_nume, tert_cui) "
                    "VALUES ('LIC-73', '2099-03-10', 1210, 210, 'RON', 'primita', 'importata', 'DANTE INTERNATIONAL SA', '14399840')")
        g = repo_facturi.dubluri_primite(cur, _SCHEMA)
    assert [[(x["numar"], x["total"]) for x in gr] for gr in g] == [[("LIC-73", D("1210.00")), ("LIC-73", D("1210.00"))]], g


# ── garda: cele trei căi ───────────────────────────────────────────────────────────────────────────────────────────────────
CAI = {("core/facturi_api.py", "creeaza_factura"), ("core/uc_comun.py", "_factura_din_parsat"),
       ("core/solduri_parteneri_api.py", "_scrie_documente")}


def _apeleaza_verificarea(rel, functie):
    arb = ast.parse(io.open(os.path.join(RAD, rel), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == functie)
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "primite_cu_aceeasi_cheie"
               for c in ast.walk(fn))


def test_cele_trei_cai_cheama_verificarea():
    """GARDA: cele trei căi prin care se naște o factură (inventarul `scan_cai_factura`, pinat în `test_cai_creare_factura`) sunt exact
    cele de aici și fiecare cheamă verificarea dublurii. O cale nouă (sau una care pierde verificarea) pică aici.
    MUTAȚIE: apelul scos din `_scrie_documente` -> pică."""
    from core import scan_cai_factura as sc
    gasite = set(sc.cai(RAD, doar=lambda r: r == "main.py" or (r.startswith("core/") and not os.path.basename(r).startswith("test_"))))
    assert gasite == CAI, gasite
    assert {c for c in CAI if not _apeleaza_verificarea(*c)} == set()
