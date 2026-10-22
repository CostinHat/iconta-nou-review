# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 443 — datele existente, subagentul N] Regula Costin 11.2 pct.3a, verbatim: „Orice reparație acoperă și datele
existente.” 443 (comanda 11.1 pct.19, verbatim): „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”.

Reparația lotului 11 (`pdf_util.serie_nr`) scrie forma nouă numai pe ce se scrie de acum. Notele și mișcările scrise înainte păstrau forma
lipită (copia firmelor de test, 22.10.2026: F1 „Contare factura F1A3”…„F1A12”, „Factură F1A3 din 06.10.2026”; F6 „Contare factura F61”):
  · ciornele le rescrie `core/migrare_serie_nr_descrieri.py`, cu numărul din aceeași funcție ca la scriere;
  · notele validate nu se modifică (OMFP 1802/2014 pct.69 — „corectura se face prin stornare”, triggerul `regula_nota`); Registrul jurnal
    le arată cu seria separat, derivat din factura lor (`jurnal_api.note_fara_serie_lipita`, chemată din `uc_tenants.tenant_jurnal`).

DATE DE PORNIRE: forma veche se scrie pe DRUMUL aplicației (`facturi_api.emite_factura`, `stocuri_cv_api.intrare` / `iesire`) cu regula de
dinainte de 443 pusă la loc prin monkeypatch pe funcția regulii (`pdf_util.serie_nr` -> `pdf_util.numar_cu_serie`, exact ce chemau
`contare_facturi._descriere` și `jurnal_api.eticheta_factura` înainte) — nu prin INSERT-uri care ar ocoli drumul. Schemă efemeră din
`tenant_template.sql`, tranzacție anulată, date în 2099. CUI-uri: 14399840 (DANTE INTERNATIONAL SA) și 18547290 (clientul din
`test_lot11_t_proba_428`), cifra de control verificată cu algoritmul din CLAUDE.md."""
import ast
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_n_443"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZI = "2099-10-10"


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
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, platitor_tva_anaf_inceput, declarant_nume, declarant_prenume, declarant_functie, forma_juridica, "
                    "capital_subscris, telefon, metoda_stoc) VALUES (1,'N443 SRL','14399840','Str Test 1','Bucuresti','B','4719','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,"
                    "'0712345678','cantitativ_valoric')")
            yield _FaraCommit(c)
        finally:
            c.rollback()


def _emite(conn, serie="F6"):
    """Factura emisă pe ruta formularului (`emite_factura`; numerotarea din „Configurare emitere”, `seteaza_numerotare`)."""
    from core import facturi_api
    facturi_api.seteaza_numerotare(conn, serie=serie, numar_start=1)
    r = facturi_api.emite_factura(conn, [{"descriere": "Servicii de consultanță", "cantitate": 1, "um": "ora", "pret_unitar": 100,
                                          "cota_tva": 21, "cota_propusa": 21}],
                                  tert_nume="Client N SRL", tert_cui="18547290", tert_adresa="Str. Probei 1", tert_oras="Sector 1",
                                  tert_judet="B", data_emitere=ZI, data_scadenta=ZI, tert_platitor_tva=True)
    assert r.get("ok"), r
    return r["factura_id"]


def _regula_veche(monkeypatch):
    """Regula de dinainte de 443: `serie_nr` lipea seria de număr, ca `numar_cu_serie` („F6” + „1” = „F61”)."""
    from core import pdf_util
    monkeypatch.setattr(pdf_util, "serie_nr", pdf_util.numar_cu_serie)


def _iesire_din_factura(conn, fid):
    """Descărcarea stocului facturii, cum o face emiterea cu „pleacă marfa” (`stocuri_cv_api.descarca_factura` -> `iesire` cu documentul
    `jurnal_api.eticheta_factura`). Întoarce (id-ul notei de stoc, id-ul mișcării)."""
    from core import jurnal_api as _j, stocuri_cv_api as cva
    r = cva.intrare(conn, SCH, {"denumire": "Marfa N", "um": "buc", "cont_stoc": "371", "cont_cheltuiala": "607", "data": ZI,
                                "cantitate": 10, "pret_unitar": "10", "document": "NIR 1"})
    assert "eroare" not in r, r
    with conn.cursor() as cur:
        cur.execute("SELECT serie, numar, data_emitere, tip FROM facturi WHERE id = %s", (fid,))
        serie, numar, data, tip = cur.fetchone()
    r = cva.iesire(conn, SCH, {"articol_id": r["articol_id"], "data": ZI, "cantitate": 1,
                               "document": _j.eticheta_factura(tip, serie, numar, data)}, factura_id=fid)
    assert "eroare" not in r, r
    with conn.cursor() as cur:
        cur.execute("SELECT inregistrare_id, id FROM miscari_stoc WHERE factura_id = %s AND tip = 'iesire'", (fid,))
        return cur.fetchone()


def _nota_contare(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT id, descriere, status FROM inregistrari WHERE factura_id = %s AND sursa = 'facturi'", (fid,))
        return cur.fetchone()


def _text(conn, tabela, camp, rid):
    with conn.cursor() as cur:
        cur.execute("SELECT %s FROM %s WHERE id = %%s" % (camp, tabela), (rid,))
        return cur.fetchone()[0]


def test_443_nota_noua_din_emitere_scrie_seria_separat(conn):
    """Reparația pe notele NOI (W1/U0), pe drumul emiterii: „Contare factura F6 nr. 1”, documentul stocului „Factură F6 nr. 1 din …”."""
    fid = _emite(conn)
    assert _text(conn, "facturi", "numar", fid) == "F61"                               # numărul emis poartă seria în față
    assert _nota_contare(conn, fid)[1] == "Contare factura F6 nr. 1"                   # 443: „F6 nr. 1, nu F61”
    nid, mid = _iesire_din_factura(conn, fid)
    assert _text(conn, "inregistrari", "document_ref", nid) == "Factură F6 nr. 1 din 10.10.2099"
    assert _text(conn, "miscari_stoc", "document", mid) == "Factură F6 nr. 1 din 10.10.2099"


def test_443_ciorna_veche_rescrisa_de_migrare(conn, monkeypatch):
    """Ciornele scrise cu regula veche („Contare factura F61”, documentul „Factură F61 din 10.10.2099” pe notă și pe mișcare) ies cu seria
    separat după migrare; raportul firmei le numără. MUTAȚIE: UPDATE-ul ciornelor scos din `aplica` -> pică."""
    from core import migrare_serie_nr_descrieri as m
    with monkeypatch.context() as mp:
        _regula_veche(mp)
        fid = _emite(conn)
        nid_s, mid = _iesire_din_factura(conn, fid)
    nid_c, desc, st = _nota_contare(conn, fid)
    assert (desc, st) == ("Contare factura F61", "ciorna")                           # data de pornire: forma de dinainte de 443
    assert _text(conn, "inregistrari", "document_ref", nid_s) == "Factură F61 din 10.10.2099"
    r = m.aplica(conn, SCH)
    assert _text(conn, "inregistrari", "descriere", nid_c) == "Contare factura F6 nr. 1"                 # 443: „F6 nr. 1, nu F61”
    assert _text(conn, "inregistrari", "document_ref", nid_s) == "Factură F6 nr. 1 din 10.10.2099"
    assert _text(conn, "miscari_stoc", "document", mid) == "Factură F6 nr. 1 din 10.10.2099"
    assert sorted((n, c) for n, c, _v, _x in r["ciorne"]) == sorted([(nid_c, "descriere"), (nid_s, "document_ref")]), r
    assert [x[0] for x in r["miscari"]] == [mid] and not r["validate"] and not r["ciorne_lasate"], r
    assert m.verifica(conn, SCH)
    linie = m.text_raport(SCH, r).splitlines()[0]
    assert linie == "%s: 2 ciorne rescrise, 1 mișcare de stoc rescrisă, 0 note validate arătate derivat, 0 texte lăsate" % SCH, linie


def test_443_nota_validata_neatinsa_in_baza_dar_aratata_f6_nr_1(conn, monkeypatch):
    """Nota validată cu forma veche nu se rescrie (nici măcar când triggerul ar lăsa — nota e validată în aceeași tranzacție a testului,
    deci aici refuzul e al MIGRĂRII, nu al bazei); Registrul jurnal o arată „Contare factura F6 nr. 1” / „Factură F6 nr. 1 din …”.
    MUTAȚIE: `note_fara_serie_lipita` întoarce {} (afișarea derivată scoasă) -> pică; `status == "validata"` scos din `plan` -> pică."""
    from core import jurnal_api as _j, migrare_serie_nr_descrieri as m
    with monkeypatch.context() as mp:   # scrise ȘI validate înainte de 443 (ca notele 108 / 109 ale lui F1): azi, ciorna de stoc cu
        _regula_veche(mp)               # documentul vechi e „depășită” la validare (451), deci nu se mai poate valida așa
        fid = _emite(conn)
        nid_s, mid = _iesire_din_factura(conn, fid)
        nid_c = _nota_contare(conn, fid)[0]
        for nid in (nid_c, nid_s):
            r = _j.valideaza(conn, SCH, nid)
            assert not (isinstance(r, dict) and r.get("eroare")), r
            assert _text(conn, "inregistrari", "status", nid) == "validata"
    r = m.aplica(conn, SCH)
    # OMFP 1802/2014 pct.69 (triggerul `regula_nota`): nota validată nu se modifică — în bază rămâne cum a fost scrisă
    assert _text(conn, "inregistrari", "descriere", nid_c) == "Contare factura F61"
    assert _text(conn, "inregistrari", "document_ref", nid_s) == "Factură F61 din 10.10.2099"
    assert _text(conn, "miscari_stoc", "document", mid) == "Factură F61 din 10.10.2099"             # mișcarea în evidență
    assert not r["ciorne"] and not r["miscari"] and len(r["validate"]) == 2 and len(r["miscari_lasate"]) == 1, r
    with conn.cursor() as cur:
        afisat = _j.note_fara_serie_lipita(cur, SCH, [nid_c, nid_s])
    assert afisat == {nid_c: {"descriere": "Contare factura F6 nr. 1"}, nid_s: {"document": "Factură F6 nr. 1 din 10.10.2099"}}, afisat


def test_443_migrarea_e_idempotenta(conn, monkeypatch):
    """A doua rulare nu mai găsește nimic: forma nouă nu conține numărul lipit."""
    from core import migrare_serie_nr_descrieri as m
    with monkeypatch.context() as mp:
        _regula_veche(mp)
        _iesire_din_factura(conn, _emite(conn))
    assert m.aplica(conn, SCH)["ciorne"]
    r2 = m.aplica(conn, SCH)
    assert not any(r2.values()), r2


def test_443_textul_omului_si_al_bancii_nu_se_atinge(conn, monkeypatch):
    """Documentul tastat de om la casă („Încasare factura F61”) și descrierea venită din extras („… contravaloare factura F61 din …”) nu
    sunt scrise de aplicație: nici migrarea, nici Registrul jurnal nu le schimbă (CLAUDE.md §8 — datele omului, NEALTERATE)."""
    from core import jurnal_api as _j, migrare_serie_nr_descrieri as m, repo_contabilitate as rc
    with monkeypatch.context() as mp:
        _regula_veche(mp)
        fid = _emite(conn)
    with conn.cursor() as cur:
        banca = rc.nota_cu_sursa_si_status(cur, ZI, None, "Incasare CLIENT N SRL contravaloare factura F61 din 10.10.2099", "banca",
                                           "ciorna", document_ref="Încasare factura F61")
        banca = banca["id"] if isinstance(banca, dict) else banca[0]
        cur.execute("UPDATE inregistrari SET factura_id = %s WHERE id = %s", (fid, banca))
    r = m.aplica(conn, SCH)
    assert [n for n, _c, _v, _x in r["ciorne"] if n == banca] == []
    assert _text(conn, "inregistrari", "descriere", banca) == "Incasare CLIENT N SRL contravaloare factura F61 din 10.10.2099"
    assert _text(conn, "inregistrari", "document_ref", banca) == "Încasare factura F61"
    with conn.cursor() as cur:
        assert banca not in _j.note_fara_serie_lipita(cur, SCH, [banca])


def test_443_numarul_intreg_nu_o_parte_din_el():
    """Numai numărul întreg al facturii: „F1A1” nu atinge „F1A11”; seria cu separator („KAI-12”) și forma deja nouă rămân corecte."""
    from core import jurnal_api as _j
    assert _j.fara_serie_lipita("Retur la Factură F1A11 din 20.10.2026", "F1A", "F1A1") == "Retur la Factură F1A11 din 20.10.2026"
    assert _j.fara_serie_lipita("Retur la Factură F1A11 din 20.10.2026", "F1A", "F1A11") == "Retur la Factură F1A nr. 11 din 20.10.2026"
    assert _j.fara_serie_lipita("Contare factura F1A nr. 3", "F1A", "F1A3") == "Contare factura F1A nr. 3"     # idempotentă
    assert _j.fara_serie_lipita("Contare factura F6F61", "F6", "F61") == "Contare factura F6 nr. 1"   # seria lipită de mână peste număr
    assert _j.fara_serie_lipita("Contare factura 12", None, "12") == "Contare factura 12"              # fără serie: nimic de separat
    assert _j.scris_de_aplicatie_fara_serie_lipita("Diferență de preț NIR 4 / factura AB7", [("AB", "7")]) == \
        "Diferență de preț NIR 4 / factura AB nr. 7"
    assert _j.scris_de_aplicatie_fara_serie_lipita("Încasare factura F61", [("F6", "F61")]) == "Încasare factura F61"   # al omului


def _siruri_executate(src):
    """Șirurile executate (fără docstringuri), cu f-stringurile REFĂCUTE („UPDATE {}.inregistrari …”) — un f-string are bucăți separate."""
    arb = ast.parse(src)
    doc = {id(n.body[0].value) for n in ast.walk(arb)
           if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr)
           and isinstance(n.body[0].value, ast.Constant)}
    out = [n.value for n in ast.walk(arb) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc]
    out += ["".join(v.value if isinstance(v, ast.Constant) else "{}" for v in n.values) for n in ast.walk(arb) if isinstance(n, ast.JoinedStr)]
    return out


def test_443_migrarea_scrie_in_note_numai_pe_ciorne():
    """GARDĂ: singura scriere a migrării în note e un UPDATE condiționat de `status = 'ciorna'` (nota validată nu se modifică — OMFP
    1802/2014 pct.69); nicio ștergere, nicio inserare, nicio scriere în rândurile notei. MUTAȚIE: `AND status = 'ciorna'` scos din UPDATE
    -> pică."""
    import re
    src = io.open(os.path.join(RAD, "core", "migrare_serie_nr_descrieri.py"), encoding="utf-8").read()
    scrie = re.compile(r"(UPDATE|DELETE\s+FROM|INSERT\s+INTO)\s+[\"'{}A-Za-z_.@]*\binregistrari(_linii)?\b", re.I)
    gasite = [s for s in _siruri_executate(src) if scrie.search(s)]
    assert gasite, "anti-vacuu: scrierea ciornelor nu mai e găsită"
    # pe CLAUZE: verbul e UPDATE, tabelul e `inregistrari` (nu `inregistrari_linii`), iar WHERE-ul condiționează pe `status = 'ciorna'`
    ciorna = re.compile(r"\bWHERE\b.*\bstatus\s*=\s*'ciorna'", re.I | re.S)
    rele = [s for s in gasite
            if scrie.search(s).group(1).upper() != "UPDATE" or scrie.search(s).group(2) is not None or not ciorna.search(s)]
    assert rele == [], rele


def test_443_registrul_jurnal_cheama_afisarea_derivata():
    """GARDĂ de cablare: `uc_tenants.tenant_jurnal` (ruta Registrului jurnal) aplică `note_fara_serie_lipita` peste rândurile notelor.
    MUTAȚIE: apelul scos -> pică (și e2e-ul `test_def_443_nota_veche_din_registru_jurnal_arata_seria_separat`)."""
    import inspect
    import textwrap
    from core import uc_tenants
    # pe AST (un APEL `_j.note_fara_serie_lipita(...)` în corpul rutei), nu pe sub-șir: un comentariu / docstring care îl numește nu trece
    arb = ast.parse(textwrap.dedent(inspect.getsource(uc_tenants.tenant_jurnal)))
    apeluri = [ast.unparse(n) for n in ast.walk(arb) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "note_fara_serie_lipita" and isinstance(n.func.value, ast.Name) and n.func.value.id == "_j"]
    assert apeluri == ["_j.note_fara_serie_lipita(cur, schema, list(note))"], apeluri


def test_443_fisa_de_magazie_arata_miscarea_veche_cu_seria_separat(conn, monkeypatch):
    """Mișcarea de stoc a unei facturi, scrisă și validată înainte de 443, e în evidență (`regula_stoc`: nu se modifică), deci migrarea o
    lasă; fișa de magazie o arată „Factură F6 nr. 1 din …”, din aceeași regulă ca Registrul jurnal (patch-ul N-P3 în
    `stocuri_cv_api.documente_fisa`). MUTAȚIE: ramura „scris de aplicație” scoasă din `documente_fisa` -> pică."""
    from core import jurnal_api as _j, stocuri_cv_api as cva
    with monkeypatch.context() as mp:
        _regula_veche(mp)
        fid = _emite(conn)
        nid_s, mid = _iesire_din_factura(conn, fid)
        assert not (lambda r: isinstance(r, dict) and r.get("eroare"))(_j.valideaza(conn, SCH, nid_s))
    with conn.cursor() as cur:
        cur.execute("SELECT articol_id FROM miscari_stoc WHERE id = %s", (mid,))
        aid = cur.fetchone()[0]
    docs = [l["document"] for l in cva.fisa(conn, SCH, aid)["linii"]]
    assert _text(conn, "miscari_stoc", "document", mid) == "Factură F61 din 10.10.2099"     # în bază: cum a fost scrisă
    # lista EXACTĂ a documentelor fișei (fără ordine): 443 „F6 nr. 1, nu F61”, iar documentul omului („NIR 1”) neatins
    assert sorted(docs) == sorted(["Factură F6 nr. 1 din 10.10.2099", "NIR 1"]), docs


def test_443_refuzul_stergerii_facturii_emise_numeste_seria_separat(conn):
    """Același tipar, în SQL: refuzul ștergerii unei facturi emise lipea seria peste numărul care o poartă deja (`COALESCE(serie, '') ||
    numar` -> „Factura F1AF1A3 e emisă”). Acum „Factura F1A nr. 3 e emisă” (patch-ul N-P6 în `facturi_api.sterge_factura`).
    MUTAȚIE: `COALESCE(serie, '') || numar` pus la loc -> pică."""
    from core import contare_facturi as cf, facturi_api
    fid = _emite(conn, serie="F1A")
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET numar = 'F1A3' WHERE id = %s", (fid,))   # al treilea număr al seriei F1A (ca F1, nota 108)
        cur.execute("DELETE FROM inregistrari WHERE factura_id = %s", (fid,))   # ciorna emiterii scoasă: rămâne refuzul facturii emise
    with pytest.raises(cf.RefuzContare) as e:
        facturi_api.sterge_factura(conn, fid)
    # mesajul EXACT (443: „F1A nr. 3”, nu „F1AF1A3”); CF art.330 alin.(1): corecția prin factură de stornare
    assert (e.value.cod, e.value.mesaj) == ("FACTURA_EMISA", "Factura F1A nr. 3 e emisă, deci nu se șterge: se corectează prin factură de "
                                                            "stornare (CF art.330 alin.(1))."), e.value.mesaj


def test_443_sql_nu_lipeste_seria_de_numar():
    """GARDĂ de clasă pentru SQL (garda U0 vede numai Python: `serie + numar`, f"{serie}{numar}"): niciun șir executat din `core/` (fără
    teste și fără migrările deja rulate, a căror amprentă nu se mai schimbă) nu compune `serie || numar`. Limita declarată: mesajul
    triggerului `regula_factura_emisa` din `tenant_template.sql` (sursa lui, `migrare_reguli_fond_2`, e rulată) — raportat ca decizie.
    MUTAȚIE: `COALESCE(serie, '') || numar` pus la loc în `facturi_api.sterge_factura` -> pică."""
    import glob
    import re
    rx = re.compile(r"\bserie\b[^|;]{0,12}\|\|\s*[\w.]*\bnumar\b", re.I)
    fisiere = [p for p in sorted(glob.glob(os.path.join(RAD, "core", "*.py")))
               if not os.path.basename(p).startswith(("test_", "migrare_"))]
    assert len(fisiere) > 100, "anti-vacuu: %d module" % len(fisiere)
    rele = ["%s: %s" % (os.path.basename(p), s.strip()[:90]) for p in fisiere
            for s in _siruri_executate(io.open(p, encoding="utf-8").read()) if rx.search(s)]
    assert rx.search("SELECT COALESCE(serie, '') || numar FROM facturi") and not rx.search("SELECT serie, numar FROM facturi")
    assert not rele, rele


def test_443_fisa_contului_arata_nota_veche_cu_seria_separat(conn, monkeypatch):
    """Fișa contului 4111 (explicația rândului) pentru nota de contare VALIDATĂ înainte de 443: „Contare factura F6 nr. 1”, din aceeași
    regulă ca Registrul jurnal (patch-ul N-P7 în `fisa_cont.fisa_cont`); în bază nota rămâne cum a fost scrisă. MUTAȚIE: explicația din
    `descriere` salvată, fără `note_fara_serie_lipita` -> pică."""
    from core import fisa_cont as fc, jurnal_api as _j
    with monkeypatch.context() as mp:
        _regula_veche(mp)
        fid = _emite(conn)
        nid = _nota_contare(conn, fid)[0]
        assert not (lambda r: isinstance(r, dict) and r.get("eroare"))(_j.valideaza(conn, SCH, nid))
    f = fc.fisa_cont(conn, SCH, "4111", 2099, 10)
    rand = f["randuri"] if isinstance(f, dict) else getattr(f, "randuri", None)
    expl = [(x["explicatie"] if isinstance(x, dict) else x.explicatie) for x in rand]
    # mulțimea EXACTĂ a explicațiilor (rândurile notei pe 4111 — client / TVA — poartă aceeași explicație); 443: „F6 nr. 1, nu F61”
    assert set(expl) == {"Contare factura F6 nr. 1"}, expl
    assert _text(conn, "inregistrari", "descriere", nid) == "Contare factura F61"             # OMFP 1802/2014 pct.69: neatinsă
