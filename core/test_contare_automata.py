# -*- coding: utf-8 -*-
"""GARDA contării automate a facturii — blocurile DDD (cheia), EEE (emisă), FFF (primită).

CE FACE IMPOSIBIL:
  * ca o notă de PLATĂ a unei firme cu **TVA la încasare** să treacă drept contare — `reconciliere_api`
    îi adaugă linia de exigibilitate (`4428 = 4427`), iar nota devine terț + TVA. *Clasă LATENTĂ:
    nicio firmă din portofoliu nu e în regimul ăla azi, deci se apără pe clasă, nu pe instanță;*
  * ca o notă de CONTARE să se poată **dezlega** de factura ei, sau ca dezlegarea să se facă fără
    motiv, pe o lună închisă, sau fără urmă;
  * ca o notă de **PLATĂ** să treacă drept contare și să blocheze contabilizarea (fals-pozitivul
    măsurat pe 3 facturi la BLOC BBB) — și, în direcția cealaltă, ca o notă de contare **să nu**
    blocheze;
  * ca emiterea unei facturi să nu producă nota, sau s-o producă VALIDATĂ;
  * ca o proformă sau o factură primită să primească notă la creare;
  * ca ștergerea unei facturi contabilizate să pice cu o eroare brută de bază în loc de un refuz;
  * ca a doua chemare a rutei manuale să scrie a doua notă, sau să răspundă cu eroare;
  * ca automatul să scrie peste o notă din jurnalul liber care contează deja factura (plasa DDD2);
  * ca o notă din jurnalul liber care contează evident o factură să rămână fără cheie (DDD3);
  * ca factura de la furnizor cu TVA la încasare să fie contată automat pe 4426.

CE NU FACE, DECLARAT: nu verifică dacă factura **trebuia** contabilizată în luna aia, și nu judecă
dacă contul de cheltuială ales de om e cel potrivit — verifică doar că actul se produce, cu forma
cerută, și că refuzurile refuză exact clasele numite.

CALIBRAREA E ÎN AMBELE DIRECȚII (METODA §22). Fiecare interdicție are perechea ei: nota de plată NU
blochează / nota de contare BLOCHEAZĂ · plasa se aprinde pe sumă+lună / NU se aprinde pe altă sumă
sau altă lună · jurnalul leagă când e o singură potrivire / NU leagă când sunt două.

RED-PROOF pe funcția REALĂ, nu pe un șablon: `test_red_proof_*` mută
`contare_facturi.e_nota_de_contare` în cele două forme greșite — „totul e contare" (comportamentul
`COUNT(*)` de dinainte) și „nimic nu e contare" — și arată că garda se aprinde pe amândouă.
"""
import ast
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import contare_facturi as _cf
from core import facturi_api as _fa
from core import jurnal_api as _ja

_SCH = "efemer_contare_automata"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")

_LINII = [{"descriere": "marfa", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21,
           "cont_venit": "707"}]


@pytest.fixture()
def conn():
    """Schemă efemeră din `tenant_template.sql`, curățată la ieșire. Nicio scriere pe date reale."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(io.open("tenant_template.sql", encoding="utf-8").read()
                        .replace("TENANT_PLACEHOLDER", _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email,
                           telefon, caen, declarant_nume, declarant_prenume, declarant_functie,
                           platitor_tva)
                           VALUES (1,'GARDA SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722',
                                   '4690','P','I','ADMIN', true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _factura(conn, numar, data, directie="emisa", **kw):
    return _fa.creeaza_factura(conn, numar, data, directie, _LINII, tert_nume="Partener SRL",
                               tert_cui="RO14399840", **kw)


def _nota_bruta(conn, data, linii, factura_id=None, sursa="banca", status="validata"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status) "
                    "VALUES (%s,%s,'proba',%s,%s) RETURNING id", (data, factura_id, sursa, status))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, "
                        "suma) VALUES (%s,%s,%s,%s)", (nid, d, c, Decimal(str(s))))
    return nid


def _note_ale(conn, factura_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, sursa FROM inregistrari WHERE factura_id=%s ORDER BY id",
                    (factura_id,))
        return cur.fetchall()


# ═══════════════════════════════════════════════ EEE1 — nota se scrie la emitere
def test_emiterea_produce_nota_in_acelasi_act(conn):
    r = _factura(conn, "G-1", "2026-08-10")
    assert r["contare"]["stare"] == "contata", r["contare"]
    note = _note_ale(conn, r["factura_id"])
    assert len(note) == 1, note
    _id, status, sursa = note[0]
    assert status == "ciorna", "automat NU înseamnă validat — patru-ochi rămâne (R47)"
    assert sursa == "facturi", "`sursa` numește ACTUL, nu omul"
    linii = {(l["debit"], l["credit"], l["suma"]) for l in r["contare"]["linii"]}
    assert linii == {("4111", "707", "1000.00"), ("4111", "4427", "210.00")}, linii


def test_proforma_nu_primeste_nota(conn):
    """Calibrare negativă: fără ea, o gardă care cere „nota există" ar trece și dacă s-ar scrie
    pentru orice document."""
    r = _factura(conn, "PF-1", "2026-08-10", tip="proforma")
    assert r["contare"]["stare"] == "neaplicabil"
    assert not _note_ale(conn, r["factura_id"])


def test_primita_nu_se_conteaza_la_creare(conn):
    """A doua calibrare negativă: la primită faptul e RECUNOAȘTEREA cheltuielii (`/valideaza`), nu
    sosirea documentului."""
    r = _factura(conn, "G-P1", "2026-08-10", directie="primita")
    assert r["contare"]["stare"] == "neaplicabil"
    assert not _note_ale(conn, r["factura_id"])


def test_rollback_complet_nu_lasa_nici_factura_nici_nota(conn, monkeypatch):
    """Tiparul NIR, proprietatea 2: dacă nota cade cu o eroare NEDECLARATĂ, cade și factura.
    *Nu există factură fără notă, și nici notă fără factură.*"""
    def explodeaza(*a, **k):
        raise RuntimeError("eroare nedeclarată în generarea notei")
    monkeypatch.setattr(_cf, "contabilizeaza", explodeaza)
    with pytest.raises(RuntimeError):
        _factura(conn, "G-BOOM", "2026-08-10")
    conn.rollback()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM facturi WHERE numar='G-BOOM'")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT COUNT(*) FROM inregistrari")
        assert cur.fetchone()[0] == 0


def test_un_refuz_declarat_nu_anuleaza_factura(conn):
    """Direcția inversă: un refuz DECLARAT oprește nota, nu emiterea. Altfel o factură validă n-ar
    mai putea fi emisă dintr-un motiv de contabilitate."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, status, total, tva) "
                    "VALUES ('G-FC','2026-08-10','emisa','emisa',1210,210) RETURNING id")
        fid = cur.fetchone()[0]           # factură FĂRĂ linii -> fără cotă de unde s-o citească
    with _cf.cursor_dict(conn) as cur:
        with pytest.raises(_cf.RefuzContare) as e:
            _cf.contabilizeaza(cur, "", fid, automat=True)
    assert e.value.cod == "FARA_COTA"
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM facturi WHERE id=%s", (fid,))
        assert cur.fetchone()[0] == 1, "factura rămâne; doar nota lipsește"


# ═══════════════════════════════════════════════ DDD1 — cheia distinge contarea de plată
def test_nota_de_plata_nu_blocheaza_contarea(conn):
    """Fals-pozitivul măsurat: 3 facturi reale au cheia ocupată de o notă de plată sau de încasare.
    `COUNT(*)` le refuza cu «factura are deja înregistrare» — un mesaj fals."""
    r = _factura(conn, "G-2", "2026-08-10", directie="primita")
    fid = r["factura_id"]
    _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=fid)
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contare_existenta(cur, "", fid) is None
        rez = _cf.contabilizeaza(cur, "", fid, automat=False, cont_cheltuiala="371")
    assert rez["stare"] == "contata"


def test_nota_de_incasare_nu_blocheaza_contarea(conn):
    """A doua formă a aceleiași clase, cealaltă direcție de flux: `5311 = 4111` (instanța
    `tenant_013` #14)."""
    r = _factura(conn, "G-3", "2026-08-10")
    fid = r["factura_id"]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM inregistrari WHERE factura_id=%s", (fid,))
    _nota_bruta(conn, "2026-08-21", [("5311", "4111", "1210.00")], factura_id=fid, sursa="casa")
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contare_existenta(cur, "", fid) is None


def test_nota_de_contare_BLOCHEAZA(conn):
    """Calibrarea pozitivă a aceleiași funcții. Fără ea, un `e_nota_de_contare` care ar întoarce
    mereu False ar face toate testele de mai sus verzi și ar deschide dubla contare."""
    r = _factura(conn, "G-4", "2026-08-10")
    with _cf.cursor_dict(conn) as cur:
        n = _cf.contare_existenta(cur, "", r["factura_id"])
    assert n is not None and n["e_contare"]


def test_a_doua_contare_e_no_op_nu_a_doua_nota(conn):
    """[EEE3/FFF3] Idempotență ca RĂSPUNS, nu ca eroare."""
    r = _factura(conn, "G-5", "2026-08-10")
    with _cf.cursor_dict(conn) as cur:
        rez = _cf.contabilizeaza(cur, "", r["factura_id"], automat=False)
    assert rez["stare"] == "deja_contata"
    assert len(_note_ale(conn, r["factura_id"])) == 1


# ═══════════════════════════════════════════════ EEE2 — ștergerea
def test_stergerea_refuza_motivat_cand_exista_nota_de_contare(conn):
    r = _factura(conn, "G-6", "2026-08-10")
    with pytest.raises(_cf.RefuzContare) as e:
        _fa.sterge_factura(conn, r["factura_id"])
    assert e.value.cod == "ARE_NOTA_DE_CONTARE"
    assert e.value.detalii["iesire"] == "storno", (
        "refuzul trebuie să NUMEASCĂ ieșirea, ca dată — nu doar să refuze")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM facturi WHERE id=%s", (r["factura_id"],))
        assert cur.fetchone()[0] == 1


def test_stergerea_refuza_ALTFEL_cand_nota_legata_nu_e_contare(conn):
    """Găsit de garda asta la prima rulare, nu presupus: cheia străină `inregistrari_factura_id_fkey`
    n-are `ON DELETE`, deci blochează ștergerea și pentru o notă de **plată** — cu o eroare brută de
    bază. EEE2 cere să nu mai pice așa. Refuzul acoperă și clasa asta, dar cu **alt cod și alt
    motiv**, fiindcă ieșirea e alta: aici dezlegi nota, nu stornezi factura."""
    r = _factura(conn, "G-7", "2026-08-10", directie="primita")
    _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=r["factura_id"])
    with pytest.raises(_cf.RefuzContare) as e:
        _fa.sterge_factura(conn, r["factura_id"])
    assert e.value.cod == "ARE_NOTA_LEGATA"
    # [R90, aceeași zi] IEȘIREA EXISTĂ ACUM. Când testul s-a scris, nu exista: nota de plată e
    # validată, `jurnal_api.sterge` refuză orice notă care nu e ciornă, iar dezlegare nu era — deci
    # refuzul numea un zid, iar aserțiunea de atunci era `iesire == "fara_iesire"`. Se schimbă
    # fiindcă s-a schimbat APLICAȚIA, nu ca să treacă testul.
    assert e.value.detalii["status_nota"] == "validata"
    assert e.value.detalii["iesire"] == "dezleaga_nota"


def test_stergerea_TRECE_cand_factura_n_are_nicio_nota(conn):
    """Calibrarea pozitivă a ștergerii. Fără ea, un refuz care ar refuza *întotdeauna* ar face
    testele de mai sus verzi și ar bloca orice ștergere legitimă."""
    r = _factura(conn, "G-8", "2026-08-10", directie="primita")
    assert not _note_ale(conn, r["factura_id"])
    assert _fa.sterge_factura(conn, r["factura_id"])["ok"] is True


# ═══════════════════════════════════════════════ DDD2 — plasa
def _plasa(conn, luna_nota, suma_tert):
    r = _factura(conn, "G-PL%s" % luna_nota, "2026-1%s-10" % luna_nota, directie="primita")
    _nota_bruta(conn, "2026-1%s-15" % luna_nota,
                [("371", "401", suma_tert), ("4426", "401", "0.01")],
                factura_id=None, sursa="manual")
    return r["factura_id"]


def test_plasa_opreste_automatul_pe_suma_si_luna(conn):
    fid = _plasa(conn, "0", "1209.99")     # 1209.99 + 0.01 = 1210.00 = totalul facturii
    with _cf.cursor_dict(conn) as cur:
        with pytest.raises(_cf.RefuzContare) as e:
            _cf.contabilizeaza(cur, "", fid, automat=True, cont_cheltuiala="371")
    assert e.value.cod == "POSIBILA_DUBLARE"
    assert e.value.detalii.get("note"), "refuzul trebuie să NUMEASCĂ nota găsită"


def test_plasa_nu_se_aprinde_pe_alta_suma(conn):
    """Calibrare negativă. Criteriul e STRICT tocmai fiindcă cel larg a produs 3 fals-pozitive pe
    date reale — note de încasare care se potrivesc cu factura pe care chiar o încasează."""
    fid = _plasa(conn, "1", "999.99")
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contabilizeaza(cur, "", fid, automat=True,
                                  cont_cheltuiala="371")["stare"] == "contata"


def test_plasa_nu_se_aprinde_pe_alta_luna(conn):
    r = _factura(conn, "G-PL2", "2026-12-10", directie="primita")
    _nota_bruta(conn, "2026-11-15", [("371", "401", "1209.99"), ("4426", "401", "0.01")],
                factura_id=None, sursa="manual")
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contabilizeaza(cur, "", r["factura_id"], automat=True,
                                  cont_cheltuiala="371")["stare"] == "contata"


def test_plasa_avertizeaza_omul_in_loc_sa_l_opreasca(conn):
    fid = _plasa(conn, "0", "1209.99")
    with _cf.cursor_dict(conn) as cur:
        rez = _cf.contabilizeaza(cur, "", fid, automat=False, cont_cheltuiala="371")
    assert rez["stare"] == "contata"
    assert rez["avertisment"]["cod"] == "POSIBILA_DUBLARE", rez
    assert rez["avertisment"]["note"], "avertismentul trebuie să NUMEASCĂ notele găsite"


# ═══════════════════════════════════════════════ DDD3 — legarea la sursă
def test_jurnalul_leaga_factura_cand_potrivirea_e_UNICA(conn):
    r = _factura(conn, "G-J1", "2026-09-05", directie="primita")
    rez = _ja.creeaza(conn, _SCH, "contare manuală", "2026-09-20",
                      [{"debit": "371", "credit": "401", "suma": 1000},
                       {"debit": "4426", "credit": "401", "suma": 210}])
    assert rez.get("factura_id") == r["factura_id"], rez


def test_jurnalul_NU_leaga_cand_doua_facturi_se_potrivesc(conn):
    """*O legătură greșită e mai rea decât lipsa ei*: ar face o factură să pară contată de altcineva.
    Calibrarea asta e cea care ține definiția lui «evident» îngustă."""
    _factura(conn, "G-J2", "2026-09-05", directie="primita")
    _factura(conn, "G-J3", "2026-09-06", directie="primita")
    rez = _ja.creeaza(conn, _SCH, "contare manuală", "2026-09-20",
                      [{"debit": "371", "credit": "401", "suma": 1000},
                       {"debit": "4426", "credit": "401", "suma": 210}])
    assert rez.get("factura_id") is None, rez


def test_jurnalul_NU_leaga_o_nota_care_nu_e_contare(conn):
    _factura(conn, "G-J4", "2026-09-05", directie="primita")
    rez = _ja.creeaza(conn, _SCH, "plată furnizor", "2026-09-20",
                      [{"debit": "401", "credit": "5121", "suma": 1210}])
    assert rez.get("factura_id") is None, rez


# ═══════════════════════════════════════════════ FFF2 — clasa ambiguă de TVA la încasare
def test_clasa_ambigua_e_refuzata_de_automat(conn):
    r = _factura(conn, "G-TI", "2026-11-10", directie="primita", furnizor_tva_incasare=True)
    with _cf.cursor_dict(conn) as cur:
        with pytest.raises(_cf.RefuzContare) as e:
            _cf.contabilizeaza(cur, "", r["factura_id"], automat=True, cont_cheltuiala="371")
    assert e.value.cod == "TVA_LA_INCASARE_MANUAL"
    assert e.value.detalii["cont_tva"] == "4428"
    assert e.value.detalii["temei"] == _cf.TEMEI_TVA_INCASARE
    assert e.value.detalii["iesire"] == "contabilizare_manuala"


def test_clasa_ambigua_trece_pe_ruta_manuala_cu_TVA_pe_4428(conn):
    """Varianta (ii): automatul refuză, omul contează. Iar când o face, TVA-ul intră pe **4428**
    (neexigibil), nu pe 4426 — exact ce rutează D300 pe același câmp. Divergența măsurată pe 2
    facturi reale înainte de reparație era că ruta citea regimul PROPRIU al firmei și îl aplica pe
    amândouă direcțiile."""
    r = _factura(conn, "G-TI2", "2026-11-10", directie="primita", furnizor_tva_incasare=True)
    with _cf.cursor_dict(conn) as cur:
        rez = _cf.contabilizeaza(cur, "", r["factura_id"], automat=False, cont_cheltuiala="371")
    conturi = {l["debit"] for l in rez["linii"]}
    # Forma de mulțime, nu `in`: `>=` crapă pe un șir, `in` ar trece ca sub-șir (scan_garzi_pe_text).
    assert conturi >= {"4428"}, rez["linii"]
    assert not conturi >= {"4426"}, rez["linii"]


def test_primita_normala_ramane_pe_4426(conn):
    """Calibrare negativă: fără ea, un `e_clasa_ambigua_tva` care ar întoarce mereu True ar trece
    tot pe 4428 și ar produce o evidență greșită în cealaltă direcție."""
    r = _factura(conn, "G-TI3", "2026-11-10", directie="primita")
    with _cf.cursor_dict(conn) as cur:
        rez = _cf.contabilizeaza(cur, "", r["factura_id"], automat=True, cont_cheltuiala="371")
    assert {l["debit"] for l in rez["linii"]} >= {"4426"}, rez["linii"]


# ═══════════════════════════════════════════════ FFF1 — contul obligatoriu la validare
_MESAJ = [0]


def _primita_de_validat(conn, status="descarcata"):
    _MESAJ[0] += 1
    with conn.cursor() as cur:
        cur.execute("INSERT INTO efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, "
                    "xml_brut, xml_sha256, status) "
                    "VALUES (%s,'RO14399840','RO14399840','NU E XML','sha',%s) RETURNING id",
                    ("MSG-%d" % _MESAJ[0], status))
        return cur.fetchone()[0]


def test_validarea_fara_cont_refuza(conn, monkeypatch):
    import main
    from fastapi import HTTPException
    pid = _primita_de_validat(conn)
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    with pytest.raises(HTTPException) as e:
        main.factura_primita_valideaza(1, pid, {}, {"uid": 1})
    assert e.value.status_code == 422
    assert e.value.detail["cod"] == "CONT_CHELTUIALA_OBLIGATORIU", e.value.detail


def test_validarea_CU_cont_trece_de_verificarea_de_cont(conn, monkeypatch):
    """Cealaltă direcție: cu cont, refuzul de cont nu se mai aprinde — se ajunge la parsarea XML-ului.
    Fără testul ăsta, o verificare care ar refuza *întotdeauna* ar arăta la fel de verde."""
    import main
    from fastapi import HTTPException
    pid = _primita_de_validat(conn)
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    with pytest.raises(HTTPException) as e:
        main.factura_primita_valideaza(1, pid, {"cont": "628"}, {"uid": 1})
    assert e.value.status_code == 422
    cod = e.value.detail.get("cod") if isinstance(e.value.detail, dict) else None
    assert cod != "CONT_CHELTUIALA_OBLIGATORIU", (
        "cu cont ales, refuzul de cont nu mai are voie să se aprindă — s-a ajuns mai departe")


# ═══════════════════════════════════════════════ CABLAJUL, citit ca AST (METODA §23)
def _apeluri(cale, nume_functie):
    """Numele apelate în corpul unei funcții — noduri de AST, nu șiruri căutate în text.

    Ia amândouă formele de apel: `modul.functie(...)` (Attribute) și `functie(...)` (Name). Prima
    formă a testului lua doar Attribute, și a raportat lipsă pe un apel care exista — o gardă care
    se uită în jumătate de loc raportează despre o lume pe care n-o vede."""
    arbore = ast.parse(io.open(cale, encoding="utf-8").read())
    for n in ast.walk(arbore):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume_functie:
            out = set()
            for c in ast.walk(n):
                if not isinstance(c, ast.Call):
                    continue
                if isinstance(c.func, ast.Attribute):
                    out.add(c.func.attr)
                elif isinstance(c.func, ast.Name):
                    out.add(c.func.id)
            return out
    raise AssertionError("funcția %s nu există în %s" % (nume_functie, cale))


def test_cititorul_de_apeluri_chiar_vede_amandoua_formele():
    """ANTI-VACUU pe cititor: fără el, cele trei gărzi de cablaj de mai jos ar putea trece pe o
    mulțime goală și n-ar spune nimic."""
    assert _apeluri("core/contare_facturi.py", "e_nota_de_contare") >= {"e_cont_tert"}
    assert _apeluri("core/contare_facturi.py", "luna_blocata") >= {"execute"}


def test_creeaza_factura_chiar_cheama_contarea():
    assert _apeluri("core/facturi_api.py", "creeaza_factura") >= {"_conteaza_la_creare"}


def test_valideaza_chiar_cheama_contarea():
    assert _apeluri("main.py", "factura_primita_valideaza") >= {"contabilizeaza"}


def test_jurnalul_chiar_cheama_legarea():
    assert _apeluri("core/jurnal_api.py", "creeaza") >= {"leaga_nota_de_factura"}


def test_ruta_manuala_nu_mai_scrie_SQL_propriu():
    """ANTI-VACUU pe reparația însăși, pe STRUCTURĂ nu pe text: ruta nu mai are voie să execute SQL
    în corpul ei. Prima formă căuta șirul `COUNT(*)` — dar un `SELECT count(*)` scris altfel ar fi
    trecut, iar mutarea interogării în altă parte a rutei la fel. Zero apeluri `execute` e o
    proprietate care nu se poate ocoli prin rescriere: **toată** vorbirea cu baza s-a mutat în
    `core/contare_facturi.py`."""
    assert "execute" not in _apeluri("main.py", "factura_contabilizeaza"), (
        "ruta și-a recăpătat SQL propriu — contarea are un singur loc (P1)")
    assert _apeluri("main.py", "factura_contabilizeaza") >= {"contabilizeaza"}


# ═══════════════════════════════════════════════ RED-PROOF pe funcția REALĂ
def test_red_proof_totul_e_contare_reproduce_defectul_vechi(conn, monkeypatch):
    """Mutația 1 — `e_nota_de_contare` întoarce mereu True: exact ce făcea `COUNT(*)`. Nota de plată
    redevine blocantă, deci garda TREBUIE să se aprindă."""
    r = _factura(conn, "G-RP1", "2026-08-10", directie="primita")
    fid = r["factura_id"]
    _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=fid)
    monkeypatch.setattr(_cf, "e_nota_de_contare", lambda linii: True)
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contare_existenta(cur, "", fid) is not None, (
            "mutația n-a produs efectul — garda de mai sus nu dovedește nimic")
        assert _cf.contabilizeaza(cur, "", fid, automat=False)["stare"] == "deja_contata"


def test_red_proof_nimic_nu_e_contare_deschide_dubla_contare(conn, monkeypatch):
    """Mutația 2, direcția opusă — `e_nota_de_contare` întoarce mereu False: contarea existentă nu
    mai blochează, deci a doua chemare ar scrie a doua notă."""
    r = _factura(conn, "G-RP2", "2026-08-10")
    fid = r["factura_id"]
    monkeypatch.setattr(_cf, "e_nota_de_contare", lambda linii: False)
    with _cf.cursor_dict(conn) as cur:
        assert _cf.contare_existenta(cur, "", fid) is None
        assert _cf.contabilizeaza(cur, "", fid, automat=False)["stare"] == "contata"
    assert len(_note_ale(conn, fid)) == 2, "mutația trebuie să producă DOUĂ note"


# ═══════════════════════════════════════════════ GGG — trezoreria taie contarea
def test_nota_de_plata_cu_TVA_la_incasare_NU_e_contare():
    """Clasa LATENTĂ, găsită prin citirea codului înainte de a construi: la o firmă cu TVA la
    încasare, `reconciliere_api` adaugă pe nota de plată linia de exigibilitate — `4428 = 4427` pe
    emisă, `4426 = 4428` pe primită (art. 282 alin. 3 și 8). Nota devine **terț + TVA**, adică exact
    semnătura de contare. Fără regula «fără trezorerie», fals-pozitivul închis la DDD1 s-ar fi întors
    pe altă ușă: o factură plătită ar fi părut deja contată.

    **Nicio instanță vie azi** — nicio firmă din portofoliu nu e în regimul ăla. Se apără pe CLASĂ."""
    incasare = [("5121", "4111", 1210), ("4428", "4427", 210)]
    plata = [("401", "5121", 1210), ("4426", "4428", 210)]
    assert not _cf.e_nota_de_contare(incasare)
    assert not _cf.e_nota_de_contare(plata)


def test_o_linie_de_trezorerie_scoate_nota_din_clasa_de_contare():
    """Direcția inversă a aceleiași reguli, ca mutație: aceeași contare, plus o linie de trezorerie,
    **nu mai e** contare. Fără testul ăsta, `e_cont_trezorerie` ar putea întoarce mereu False și
    testul de mai sus ar trece la fel."""
    contare = [("4111", "707", 1000), ("4111", "4427", 210)]
    assert _cf.e_nota_de_contare(contare)
    assert not _cf.e_nota_de_contare(contare + [("5121", "4111", 1210)])


def test_red_proof_fara_regula_trezoreriei_plata_redevine_contare(monkeypatch):
    """RED-PROOF pe funcția reală: cu `e_cont_trezorerie` întors mereu la False — adică regula
    scoasă — nota de plată cu TVA la încasare **redevine** contare. Mutația trebuie să producă
    efectul, altfel testele de mai sus nu dovedesc nimic."""
    monkeypatch.setattr(_cf, "e_cont_trezorerie", lambda c: False)
    assert _cf.e_nota_de_contare([("5121", "4111", 1210), ("4428", "4427", 210)])


# ═══════════════════════════════════════════════ GGG — actul de dezlegare
def test_dezlegarea_rupe_legatura_unei_note_de_plata(conn):
    r = _factura(conn, "G-DZ1", "2026-08-10", directie="primita")
    fid = r["factura_id"]
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=fid)
    with _cf.cursor_dict(conn) as cur:
        assert _cf.dezleaga_nota(cur, "", nid) == fid
    with conn.cursor() as cur:
        cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (nid,))
        assert cur.fetchone()[0] is None


def test_dezlegarea_REFUZA_o_nota_de_contare(conn):
    """*O cifră fără documentul care o justifică nu se mai poate desface* (P14). Nota de contare
    **este** evidența facturii — ruptă, factura ar redeveni «necontată» fără să se fi întâmplat
    nimic în realitate."""
    r = _factura(conn, "G-DZ2", "2026-08-10")
    with _cf.cursor_dict(conn) as cur:
        nota = _cf.contare_existenta(cur, "", r["factura_id"])
        with pytest.raises(_cf.RefuzContare) as e:
            _cf.dezleaga_nota(cur, "", nota["id"])
    assert e.value.cod == "E_NOTA_DE_CONTARE"
    assert e.value.detalii["iesire"] == "storno"


def test_dezlegarea_refuza_o_nota_care_nu_e_legata(conn):
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=None)
    with _cf.cursor_dict(conn) as cur:
        with pytest.raises(_cf.RefuzContare) as e:
            _cf.dezleaga_nota(cur, "", nid)
    assert e.value.cod == "NOTA_NELEGATA"


def test_dezlegarea_refuza_pe_luna_inchisa(conn, monkeypatch):
    """Dezlegarea schimbă soldul unei facturi, deci e o modificare a evidenței lunii (P15).

    Se probează pe RUTĂ, nu pe modul, fiindcă acolo stă poarta — la `_cere_perioada_deschisa`,
    același helper pe care îl cheamă editarea, ștergerea și validarea unei note. *Prima formă a
    testului chema modulul; acolo nu mai e nicio poartă, iar `UPDATE`-ul ajungea la declanșatorul din
    bază, care ridică o eroare BRUTĂ. Un `423` cu mesaj și o excepție de PL/pgSQL nu sunt același
    lucru pentru omul din fața ecranului.*"""
    import main
    from fastapi import HTTPException
    r = _factura(conn, "G-DZ3", "2026-08-10", directie="primita")
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")],
                      factura_id=r["factura_id"])
    with conn.cursor() as cur:
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 8)")
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    with pytest.raises(HTTPException) as e:
        main.jurnal_dezleaga(1, nid, {"motiv": "probă"}, {"uid": 1})
    assert e.value.status_code == 423


def test_dupa_dezlegare_stergerea_facturii_TRECE(conn):
    """Drumul întreg al lui R90: refuz → dezlegare → ștergere. Înainte de azi, pasul 3 era
    imposibil pentru o notă validată."""
    r = _factura(conn, "G-DZ4", "2026-08-10", directie="primita")
    fid = r["factura_id"]
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=fid)
    with pytest.raises(_cf.RefuzContare) as e:
        _fa.sterge_factura(conn, fid)
    assert e.value.detalii["iesire"] == "dezleaga_nota"
    with _cf.cursor_dict(conn) as cur:
        _cf.dezleaga_nota(cur, "", nid)
    assert _fa.sterge_factura(conn, fid)["ok"] is True


# ═══════════════════════════════════════════════ GGG — ruta: motiv, urmă, cablaj
def test_ruta_de_dezlegare_cere_MOTIV(conn, monkeypatch):
    import main
    from fastapi import HTTPException
    r = _factura(conn, "G-RT1", "2026-08-10", directie="primita")
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")],
                      factura_id=r["factura_id"])
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    with pytest.raises(HTTPException) as e:
        main.jurnal_dezleaga(1, nid, {}, {"uid": 1})
    assert e.value.status_code == 422
    assert e.value.detail["cod"] == "MOTIV_OBLIGATORIU"


def test_ruta_de_dezlegare_scrie_URMA_cu_ce_s_a_dezlegat(conn, monkeypatch):
    """Middleware-ul de audit scrie `POST <cale>` și statusul — adică *că* s-a cerut ceva. Urma
    cerută de R90 e alta: **ce** s-a dezlegat, de pe ce factură, cu ce motiv."""
    import main
    import json as _json
    r = _factura(conn, "G-RT2", "2026-08-10", directie="primita")
    fid = r["factura_id"]
    nid = _nota_bruta(conn, "2026-08-20", [("401", "5121", "1210.00")], factura_id=fid)
    conn.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    rez = main.jurnal_dezleaga(1, nid, {"motiv": "potrivire greșită la reconciliere"}, {"uid": 1})
    assert rez["factura_id_dezlegata"] == fid
    with _db.get_conn() as c2:
        with c2.cursor() as cur:
            cur.execute("SELECT id, detalii FROM public.audit_log "
                        "WHERE actiune = 'DEZLEGARE nota-factura' ORDER BY id DESC LIMIT 1")
            rand = cur.fetchone()
            assert rand, "actul n-a lăsat nicio urmă proprie"
            d = rand[1] if isinstance(rand[1], dict) else _json.loads(rand[1])
            assert d["nota_id"] == nid
            assert d["factura_id"] == fid
            assert d["motiv"], "urma fără motiv nu spune peste șase luni dacă a fost eroare"
            # curățenie: proba nu lasă rânduri în registrul de audit al instalării
            cur.execute("DELETE FROM public.audit_log WHERE id=%s", (rand[0],))
        c2.commit()


def test_ruta_de_dezlegare_chiar_cheama_actul_si_urma():
    assert _apeluri("main.py", "jurnal_dezleaga") >= {"dezleaga_nota", "_urma_dezlegare"}


# ═══════════════════════════════════════════════ ANTI-VACUU pe clasificator
def test_clasificatorul_nu_spune_da_la_tot():
    assert _cf.e_nota_de_contare([("4111", "707", 1), ("4111", "4427", 1)])
    assert _cf.e_nota_de_contare([("2131", "404", 1), ("4426", "404", 1)])
    assert not _cf.e_nota_de_contare([("401", "5121", 1)])
    assert not _cf.e_nota_de_contare([("5311", "4111", 1)])
    assert not _cf.e_nota_de_contare([("5311", "707", 1), ("5311", "4427", 1)])
    assert not _cf.e_nota_de_contare([("6811", "2813", 1)])
    assert not _cf.e_nota_de_contare([("5121", "4111", 1), ("4428", "4427", 1)])
    assert _cf.valoare_pe_tert([("4111", "707", 1000), ("4111", "4427", 210)]) == Decimal(1210)
    assert _cf.valoare_pe_tert([("371", "401", 1000), ("4426", "401", 210)]) == Decimal(1210)
