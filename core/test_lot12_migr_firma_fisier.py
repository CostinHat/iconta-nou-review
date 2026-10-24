# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 599, comanda Costin 12.1, verbatim în DECIZII „Comanda 12.1”] „Importul de migrare primește fără întrebare balanța
altei firme (antet «SC Firmă Probă Rulaje SRL» încărcat pe DANTE INTERNATIONAL SA); compară firma din fișier cu firma aleasă și cere
confirmare când diferă, la toate importurile.”

Clasa (toate drumurile): cele nouă importuri de migrare ale unei firme — balanța (`/solduri/incarca`), soldurile pe parteneri, salariații,
asociații, mijloacele fixe, istoricul declarațiilor, articolele, rețetele, registrul de încasări și plăți. Un singur mecanism:
`import_tabel.firma_din_antet` + `import_tabel.confrunta_firma` (sursa unică), adus în previzualizare de `uc_migrare.firma_fisier`, iar
pe ecran avertismentul și confirmarea vin din `_casetaInlocuire` / `_cuFirmaConfirmata` (static/js/ecrane/migrare.js). Gărzile de mai jos
pică dacă apare un import nou (o rută `/tenants/{tenant_id}/…/incarca` sau o previzualizare) care nu trece pe aici.

TEMEI: N/A — regulă de produs (comanda 12.1). Fișierul lui Costin: `date_test/import_saga/balanta_saga_completa.xlsx` (antetul
„SC Firmă Probă Rulaje SRL”). Schemă efemeră din template, tranzacție anulată."""
import ast
import contextlib
import json
import os
import re

import pytest

from core import db as _db, import_tabel as it

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FISIER_COSTIN = os.path.join(RAD, "date_test", "import_saga", "balanta_saga_completa.xlsx")
SCHEMA = "ztest_lot12_migr_firma"
DANTE = ("DANTE INTERNATIONAL SA", "14399840")      # CUI cu cifra de control verificată (modelul de parteneri, găsit la ANAF 19.10.2026)
TITLU = [["Balanță de verificare analitică"], ["SC Firmă Probă Rulaje SRL"], ["Perioada: 01.09.2026 - 30.09.2026"]]


def _csv(randuri):
    return "\n".join(";".join(str(c) for c in r) for r in randuri).encode("utf-8")


# ── detecția și comparația (pur) ────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_599_balanta_altei_firme_e_semnalata_cu_ambele_denumiri():
    """Cazul lui Costin, pe fișierul lui: antetul „SC Firmă Probă Rulaje SRL”, firma aleasă DANTE INTERNATIONAL SA. ROȘU înainte: nicio
    comparație (previzualizarea n-avea `firma_fisier`). MUTAȚIA: `difera = False` în `confrunta_firma` -> pică."""
    rr = it.citeste(open(FISIER_COSTIN, "rb").read(), "balanta_saga_completa.xlsx")
    din = it.firma_din_antet(rr)
    assert din == {"denumire": "SC Firmă Probă Rulaje SRL", "cui": None}
    c = it.confrunta_firma(din, *DANTE)
    assert c["difera"] is True
    assert c["mesaj"] == ("Fișierul pare al altei firme: în antetul lui scrie „SC Firmă Probă Rulaje SRL”, iar firma aleasă e DANTE "
                          "INTERNATIONAL SA. Verifică dacă ai încărcat fișierul firmei potrivite; datele intră numai după ce confirmi.")
    assert c["intrebare"] == ("Datele din fișierul cu „SC Firmă Probă Rulaje SRL” intră la DANTE INTERNATIONAL SA. Confirmi că sunt ale "
                              "acestei firme?")


@pytest.mark.parametrize("din_fisier, firma", [
    ("SC Firmă Probă Rulaje SRL", "FIRMA PROBA RULAJE S.R.L."),      # forma juridică scrisă altfel, fără diacritice, majuscule
    ("S.C. DANTE INTERNATIONAL S.A.", "Dante International SA"),
    ("DANTE INTERNATIONAL", "DANTE INTERNATIONAL SA"),               # fără formă în fișier
    ("Alfa  Construct SRL-D", "ALFA CONSTRUCT SRL"),
    ("Popescu Ion PFA", "POPESCU ION PERSOANA FIZICA AUTORIZATA"),
    ("Ţesătoria Şerban SRL", "Țesătoria Șerban SRL"),               # sedilă / virgulă
])
def test_599_aceeasi_firma_scrisa_altfel_nu_e_semnalata(din_fisier, firma):
    c = it.confrunta_firma({"denumire": din_fisier, "cui": None}, firma, None)
    assert c["difera"] is False and c["mesaj"] is None, (din_fisier, firma)


def test_599_cui_ul_decide_cand_il_au_amandoua():
    """Același CUI, denumire schimbată între timp -> aceeași firmă; alt CUI, aceeași denumire -> altă firmă (CUI-ul o identifică)."""
    assert it.confrunta_firma({"denumire": "DANTE SRL", "cui": "RO 14399840"}, *DANTE)["difera"] is False
    c = it.confrunta_firma({"denumire": "DANTE INTERNATIONAL SA", "cui": "4221306"}, *DANTE)
    assert c["difera"] is True
    assert c["mesaj"].startswith("Fișierul pare al altei firme: în antetul lui scrie CUI 4221306 („DANTE INTERNATIONAL SA”), iar firma "
                                 "aleasă, DANTE INTERNATIONAL SA, are CUI 14399840.")


@pytest.mark.parametrize("randuri, asteptat", [
    ([["Firma:", "SC ALFA SRL", "CUI:", "RO14399840"], ["Cont", "Debit", "Credit"]], {"denumire": "SC ALFA SRL", "cui": "14399840"}),
    ([["Societatea: ALFA SRL, CUI RO 14399840"], ["Cont", "Debit", "Credit"]], {"denumire": "ALFA SRL", "cui": "14399840"}),
    ([["Firma", "SC GAMA SRL"], ["CUI", "RO14399840"], ["Nume", "CNP", "Cota"]], {"denumire": "SC GAMA SRL", "cui": "14399840"}),
    ([["Situație clienți"], ["SC BETA SRL"], ["Cont", "CUI", "Denumire", "Sold"], ["4111", "RO14399840", "DANTE SA", "5"]],
     {"denumire": "SC BETA SRL", "cui": None}),
    ([["Cod fiscal", "4221306"], ["Cont", "Debit", "Credit"]], {"denumire": None, "cui": "4221306"}),
])
def test_599_firma_se_citeste_din_titlu_in_formele_exporturilor(randuri, asteptat):
    assert it.firma_din_antet(randuri) == asteptat


@pytest.mark.parametrize("randuri", [
    [["cont", "cui", "denumire", "sold debitor", "sold creditor"], ["4111", "RO14399840", "DANTE INTERNATIONAL SA", "5000", "0"]],
    [["Balanță trimestrul II"], ["Cont", "Debit", "Credit"]],          # „II” dintr-un titlu nu e o întreprindere individuală
    [["Denumire", "CUI"], ["SC X SRL", "RO14399840"]],                 # niciun antet de tabel recunoscut: nu ghicesc printre date
])
def test_599_fara_firma_deasupra_tabelului_nu_se_compara_nimic(randuri):
    """Datele tabelului (un rând de parteneri are și el denumire și CUI) nu sunt antetul fișierului."""
    assert it.firma_din_antet(randuri) is None
    assert it.confrunta_firma(None, *DANTE) is None


# ── previzualizarea fiecărui import (funcțional, schemă efemeră) ────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def uc(monkeypatch):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp, uc_tenants, uc_comun, uc_migrare
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)

            @contextlib.contextmanager
            def _gc(schema=None):
                yield c
            monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
            monkeypatch.setattr(uc_migrare.db, "get_conn", _gc)
            monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCHEMA)
            monkeypatch.setattr(uc_migrare.repo_tenants, "nume_si_cui_spatiat", lambda cur, tid: DANTE)
            yield uc_tenants
        finally:
            c.rollback()


#: importul -> (funcția use-case, antetul + un rând valid, ca în modelele descărcabile din migrare.js)
IMPORTURI = {
    "balanta": ("solduri_incarca", [["Cont", "Denumire", "Sold debitor", "Sold creditor"], ["5121", "Bancă", "100", "0"],
                                    ["1012", "Capital", "0", "100"]]),
    "parteneri": ("parteneri_incarca", [["cont", "cui", "denumire", "sold debitor", "sold creditor"],
                                        ["4111", "RO4221306", "CLIENT SA", "50", "0"]]),
    "salariati": ("salariati_import_incarca", [["nume", "prenume", "cnp", "data angajare", "norma", "ore", "brut"],
                                               ["Popescu", "Ana", "2900215410011", "2020-01-15", "intreaga", "8", "5000"]]),
    "asociati": ("asociati_import_incarca", [["nume", "cnp/cui", "cota %"], ["Popescu Ana", "2900215410011", "100"]]),
    "mijloace": ("mijloace_import_incarca", [["cod", "denumire", "valoare intrare", "data PIF", "durata luni", "metoda",
                                              "cont imobilizare", "cont amortizare"],
                                             ["MF001", "Laptop", "6000", "2024-03-15", "36", "liniara", "2131", "2813"]]),
    "articole": ("articole_import_incarca", [["denumire", "um", "cantitate", "pret", "cont stoc"], ["Apă", "buc", "10", "2", "371"]]),
    "retete": ("retete_import_incarca", [["reteta", "pret vanzare", "ingredient", "cantitate"], ["Clătite", "18", "Făină", "0,08"]]),
    "rip": ("rip_import_incarca", [["data", "tip", "explicatie", "suma", "categorie", "metoda"],
                                   ["2026-01-10", "incasare", "Factura 1", "1500", "venituri", "banca"]]),
}


@pytest.mark.parametrize("imp", sorted(IMPORTURI))
def test_def_599_fiecare_previzualizare_spune_firma_din_fisier(uc, imp):
    """Același fișier, cu titlul balanței lui Costin deasupra tabelului, încărcat pe DANTE INTERNATIONAL SA, la fiecare import: previzu-
    alizarea poartă `firma_fisier.difera` și textul. MUTAȚIA: `**_firma_fisier(...)` scos din previzualizarea unui import -> pică."""
    fn, tabel = IMPORTURI[imp]
    r = getattr(uc, fn)(9990599, _csv(TITLU + tabel), "%s.csv" % imp, {"uid": 1})
    d = json.loads(r.body) if hasattr(r, "body") else r
    ff = d.get("firma_fisier")
    assert ff and ff["difera"] is True and ff["denumire"] == "SC Firmă Probă Rulaje SRL", (imp, ff)
    # fără titlu: nimic de comparat, previzualizarea rămâne cea de până azi
    r = getattr(uc, fn)(9990599, _csv(tabel), "%s.csv" % imp, {"uid": 1})
    d = json.loads(r.body) if hasattr(r, "body") else r
    assert d.get("firma_fisier", "lipsa") is None, imp


# ── gărzile de clasă (structurale) ──────────────────────────────────────────────────────────────────────────────────────────────
# pe NOD (apelul, cu cine e chemat), nu „șirul apare în sursă” — care trece și dintr-un comentariu (`core/test_garzi_pe_text.py`)
def _functii(cale):
    src = open(os.path.join(RAD, cale), encoding="utf-8").read()
    return src, {n.name: n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}


def _chemate(fn):
    """Numele funcțiilor chemate în `fn` (`f(…)` și `x.f(…)`)."""
    return {getattr(n.func, "attr", None) or getattr(n.func, "id", None) for n in ast.walk(fn) if isinstance(n, ast.Call)}


def test_599_garda_fiecare_ruta_de_incarcare_a_unui_import_de_firma_aduce_firma_din_fisier():
    """Fiecare `POST /tenants/{tenant_id}/…/incarca` din main.py (importurile de migrare ale firmei) duce la `firma_fisier`: în corpul
    rutei sau în use-case-ul `_uc_tenants.<f>` pe care îl cheamă. O rută nouă de încărcare fără comparație pică aici."""
    src_main, rute = _functii("main.py")
    _src_uc, uc = _functii("core/uc_tenants.py")
    cai = re.findall(r'@app\.post\("(/tenants/\{tenant_id\}/[^"]+/incarca)"\)\s*\ndef (\w+)', src_main)
    assert len(cai) >= 9, cai
    lipsa = []
    for cale, nume in cai:
        corp = rute[nume]
        chemate = [n.func.attr for n in ast.walk(corp) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and isinstance(n.func.value, ast.Name) and n.func.value.id == "_uc_tenants"]
        if _chemate(corp) & {"firma_fisier", "_firma_fisier"} or [f for f in chemate if f in uc and {"_firma_fisier"} <= _chemate(uc[f])]:
            continue
        lipsa.append(cale)
    assert lipsa == [], "importuri care nu compară firma din fișier cu firma aleasă: %s" % lipsa


def test_599_garda_fiecare_previzualizare_de_import_arata_firma_si_cere_confirmarea():
    """Fiecare `previzualizeaza*` din migrare.js (una pe import) desenează zona avertismentului (`_casetaFirma(date)`), o umple
    (`_arataFirma`) și salvează numai prin `_cuFirmaConfirmata`; confirmarea înlocuirii (426) se cere numai după a firmei."""
    js = open(os.path.join(RAD, "static", "js", "ecrane", "migrare.js"), encoding="utf-8").read()
    corpuri = dict(re.findall(r"\nfunction (previzualizeaza\w+)\(([\s\S]*?)(?=\n(?:async )?function |\nexport |\Z)", js))
    incarcari = re.findall(r"fetch\(`/tenants/\$\{firma\.tenant_id\}/([\w-]+(?:/[\w-]+)?)/incarca`", js)
    assert len(corpuri) == len(incarcari) == 9, (sorted(corpuri), incarcari)
    rele = [n for n, c in corpuri.items()
            if "_casetaFirma(date)" not in c or "_arataFirma(" not in c or "_cuFirmaConfirmata(" not in c]
    assert rele == [], "previzualizări care nu arată firma din fișier sau salvează fără confirmarea ei: %s" % rele
    # fiecare cerere a confirmării înlocuirii stă în continuarea confirmării firmei (un singur drum: firma întâi, apoi înlocuirea)
    from core import arbore_js as _aj
    arb, cod = _aj.arbore_js("migrare.js")
    cereri = [c["start"] for c in _aj.noduri(arb, "CallExpression") if cod(c["callee"]) == "_confirmaInlocuirea"]
    assert len(cereri) == 6, cereri
    # fiecare e corpul funcției-continuare (al treilea argument) al unui `_cuFirmaConfirmata(eroare, date, () => …)`
    in_continuare = [c["arguments"][2]["body"]["start"] for c in _aj.noduri(arb, "CallExpression")
                     if cod(c["callee"]) == "_cuFirmaConfirmata" and [cod(a) for a in c["arguments"][:2]] == ["eroare", "date"]
                     and c["arguments"][2]["type"] == "ArrowFunctionExpression" and c["arguments"][2]["body"]["type"] == "CallExpression"
                     and cod(c["arguments"][2]["body"]["callee"]) == "_confirmaInlocuirea"]
    assert sorted(in_continuare) == cereri, (in_continuare, cereri)
