# -*- coding: utf-8 -*-
"""GARD [R123, 02.09.2026]: fiecare pereche orizontala citeste CHEIA PE CARE GENERATORUL O SCRIE.

**CLASA, si instanta care a produs-o.** Perechea D101 rd.50 ↔ Σ D100 era calibrata *in amandoua
directiile* si totusi oarba: testele isi fabricau `randuri` cu cheia `suma_plata`, iar generatorul
**nu o scria** — traia doar in formatarea XML-ului, nu ca **camp** al dataclass-ului, iar
`dataclasses.asdict` vede numai campuri. Pe orice depunere facuta prin aplicatie perechea aduna
**0**. **R125**, reparata; **R123** e clasa, si asta e gardul ei.

**CE FACE, si de-aia e altfel decat gardurile de langa el:** nu scrie el `randuri`. Le cere
GENERATORULUI REAL, prin exact functia care le persista la depunere (`coada_api.randuri_din_res`),
si le da cititorului perechii. Un camp scos din dataclass sau o cheie redenumita pe o latura il fac
rosu. *Un test care isi fabrica singur intrarea dovedeste ca functia e corecta pe intrarea pe care
i-o dai tu, nu ca intrarea aia e cea pe care o produce aplicatia.*

**MUTATIA, in fiecare test:** cheia se STERGE din dictionarul serializat, iar raspunsul cititorului
trebuie sa se schimbe. Fara ea, o aserttiune care trece n-ar dovedi ca poate si sa cada.

**CE NU ACOPERA, declarat:** perechea D101 rd.50 ↔ Σ D100 are gardul ei separat, in
`core/test_supervizor.py` (a fost prima, si a ramas langa instanta). Aici sunt celelalte patru.
Nu se verifica nici CORECTITUDINEA fiscala a cifrelor — doar ca aceeasi cifra trece intreaga de la
generator la cititor.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import coada_api as _ca            # noqa: E402
from core import control_incrucisat as _ci   # noqa: E402
from core import d101 as _d101               # noqa: E402
from core import d300 as _d300               # noqa: E402
from core import d390 as _d390               # noqa: E402
from core import d394 as _d394               # noqa: E402
from core import db as _db                   # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402
from core.common import Perioada             # noqa: E402

_SCHEMA = "ztest_perechi_gen"
_AN, _LUNA = 2026, 6

#: Sumele fixturii. NU sunt valori fiscale — sunt cifre alese ca sa fie distincte intre ele, ca o
#: cheie citita gresit sa nu poata nimeri accidental valoarea alteia.
_IC_LIVRARE = 7000
_IC_ACHIZITIE = 5000
_TAXARE_INVERSA = 3000
_EMISA_BAZA, _EMISA_TVA = 2000, 420


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_gen():
    """Schema EFEMERA, cu exact felurile de factura de care are nevoie fiecare pereche. Rollback
    garantat; nu se scrie nimic pe tabele partajate (deci nici an de fixtura sintetica)."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                    "telefon,platitor_tva,operatiuni_ic,tip_decont,regim_fiscal,declarant_nume,"
                    "declarant_prenume,declarant_functie) VALUES (1,'PROBA PERECHI','14399840',"
                    "'Str 1','Bucuresti','B','6202','BCR','RO49RNCB0000000000000001','0700000000',"
                    "true,true,'L','profit','Popescu','Ion','ADMINISTRATOR')")
                zi = "%d-%02d-10" % (_AN, _LUNA)
                # livrare intracomunitara (partener UE) -> D390 baza L, D300 rd.1.1
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "tert_tara,total,tva,taxare_inversa) VALUES ('IC-L',%s,'emisa',"
                            "'FR40303265045','PARTENER FR','FR',%s,0,false)", (zi, _IC_LIVRARE))
                # achizitie intracomunitara -> D390 baza A, D300 rd.5.1
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "tert_tara,total,tva,taxare_inversa) VALUES ('IC-A',%s,'primita',"
                            "'DE136695976','PARTENER DE','DE',%s,0,false)", (zi, _IC_ACHIZITIE))
                # achizitie cu TAXARE INVERSA (art.331) -> D300 rd.12, D394 operatiune de tip C
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "tert_tara,tert_platitor_tva,total,tva,taxare_inversa,categorie_331) "
                            "VALUES ('TI-1',%s,'primita','14399840','FURNIZOR RO','RO',true,%s,0,"
                            "true,'deseuri')", (zi, _TAXARE_INVERSA))
                # emisa obisnuita -> D394 o include intre `facturi_incluse`
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "tert_tara,tert_platitor_tva,total,tva,taxare_inversa) VALUES "
                            "('EM-1',%s,'emisa','14399840','CLIENT RO','RO',true,%s,%s,false)",
                            (zi, _EMISA_BAZA + _EMISA_TVA, _EMISA_TVA))
                # nota validata: baza contabila a lui D101 (rd.48 nu poate iesi din nimic)
                cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES "
                            "(%s,'validata','test','Vanzare') RETURNING id", ("%d-06-15" % _AN,))
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,"
                            "suma) VALUES (%s,'4111','707',100000)", (iid,))
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,"
                            "suma) VALUES (%s,'607','401',60000)", (iid,))
            yield conn
        finally:
            conn.rollback()


def _randuri_d300(conn):
    _xml, res = _d300.genereaza(conn, _SCHEMA, Perioada(_AN, luna=_LUNA))
    return _ca.randuri_din_res(res)


def _randuri_d394(conn):
    _xml, res = _d394.genereaza(conn, _SCHEMA, Perioada(_AN, luna=_LUNA))
    return _ca.randuri_din_res(res)


# ── 1. D390 ↔ D300 depus: rândurile intracomunitare ────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D390_vs_D300_citeste_randurile_IC_pe_care_le_SCRIE_d300(conn_gen):
    """Perechea citeste `randuri.R.R1_1` si `R5_1`. Daca d300 nu le-ar scrie sub numele astea,
    comparatia ar vedea 0 si ar numi ROSU orbirea ei — exact tiparul lui R125."""
    randuri = _randuri_d300(conn_gen)
    res390 = _d390.calculeaza(conn_gen, _SCHEMA, _AN, _LUNA)
    rez = res390["rezumat"] if isinstance(res390, dict) else getattr(res390, "rezumat", {})
    baze = {"L": int(rez.get("L", 0)), "A": int(rez.get("A", 0))}
    assert baze["L"] == _IC_LIVRARE and baze["A"] == _IC_ACHIZITIE, (
        "[anti-vacuu] D390 nu vede facturile intracomunitare ale fixturii: %r" % baze)

    cs = _ci.compara_d390_vs_d300(baze, True, randuri, perioada="%02d/%d" % (_LUNA, _AN))
    stari = {c["eticheta"].split(" —")[0]: c["stare"] for c in cs}
    assert len(cs) == 2, "asteptam o constatare pe fiecare rand IC, sunt %d: %r" % (len(cs), stari)
    assert set(stari.values()) == {"verde"}, (
        "cifra generatorului nu ajunge intreaga la pereche: %r · randuri.R=%r"
        % (stari, (randuri.get("R") or {})))

    # MUTATIA: fara cheia livrarilor, perechea vede 0 si acuza — deci verdele de sus nu e vacuu.
    ciuntit = {"R": {k: v for k, v in (randuri.get("R") or {}).items() if k != "R1_1"}}
    cs_m = _ci.compara_d390_vs_d300(baze, True, ciuntit, perioada="x")
    assert any(c["stare"] == "rosu" and c["declarat_d300"] == 0 for c in cs_m), (
        "stergerea cheii n-a schimbat nimic — atunci aserttiunea de sus nu dovedeste nimic")


# ── 2. D300 rd.12 ↔ D394 lit. C: baza taxarii inverse ──────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D300_vs_D394_citeste_baza_taxarii_inverse_pe_care_o_SCRIE_d394(conn_gen):
    """Perechea citeste `randuri.op1` din D394 (chei tuplu serializate ca JSON) si `R.R12_1` din
    D300. Amandoua trebuie sa poarte ACEEASI baza, pe date produse de generatoare."""
    r394 = _randuri_d394(conn_gen)
    r300 = _randuri_d300(conn_gen)

    baza394, n_op, necitibile = _ci._baza_taxare_inversa_d394(r394)
    assert necitibile == 0, (
        "chei din `op1` pe care perechea nu le poate citi: %d — cheile sunt tupluri serializate "
        "JSON (`coada_api._chei_serializabile`), iar daca forma se schimba perechea tace motivat"
        % necitibile)
    assert n_op >= 1, "[anti-vacuu] nicio operatiune de tip «C» in D394 generat: %r" % list(
        (r394.get("op1") or {}).keys())
    assert int(baza394) == _TAXARE_INVERSA, (
        "baza taxarii inverse din D394 generat e %s, nu %s" % (baza394, _TAXARE_INVERSA))

    r12 = int((r300.get("R") or {}).get("R12_1") or 0)
    assert r12 == _TAXARE_INVERSA, (
        "D300 generat nu scrie rd.12 sub cheia pe care o citeste perechea; R=%r"
        % sorted((r300.get("R") or {})))

    # MUTATIA: o cheie de `op1` care nu se mai poate citi -> perechea NU tace, o numara.
    op1 = dict(r394.get("op1") or {})
    cheie = next(iter(op1))
    op1["cheie-care-nu-e-JSON"] = op1.pop(cheie)
    _b, _n, necit_m = _ci._baza_taxare_inversa_d394({"op1": op1})
    assert necit_m == 1, "o cheie necitibila trece nenumarata — perechea ar afirma pe o parte din date"


# ── 3. e-Factura ↔ D394: facturile pe care generatorul declara ca le-a inclus ───────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_EFACTURA_vs_D394_citeste_facturile_pe_care_le_EXPUNE_d394(conn_gen):
    """Perechea citeste `randuri.facturi_incluse` si `randuri.manuale_fara_factura` (R119). Prima
    lipsa ar face-o sa creada ca D394 n-a inclus nicio factura — deci ar raporta ca «transmisa si
    nedeclarata» orice factura plecata la ANAF. A doua lipsa i-ar lua motivul de a tacea."""
    r394 = _randuri_d394(conn_gen)
    # Operatorul de MULTIME, nu `in`: `>=` CRAPA daca `r394` devine vreodata un sir, in loc sa
    # treaca ca sub-sir. Forma recomandata in antetul lui `core/scan_garzi_pe_text.py`.
    assert set(r394) >= {"facturi_incluse", "manuale_fara_factura"}, (
        "D394 generat nu-si expune facturile incluse; cheile de nivel inalt: %r" % sorted(r394))

    declarate = set()
    for ids in (r394.get("facturi_incluse") or {}).values():
        declarate.update(ids or [])
    assert declarate, "[anti-vacuu] `facturi_incluse` e gol pe o declaratie cu patru facturi"

    with conn_gen.cursor() as cur:
        cur.execute("SELECT id FROM %s.facturi WHERE numar = 'EM-1'" % _SCHEMA)
        id_emisa = cur.fetchone()[0]
    assert id_emisa in declarate, (
        "factura emisa nu se regaseste printre cele declarate: %r" % sorted(declarate))
    assert int(r394.get("manuale_fara_factura") or 0) == 0, (
        "fixtura n-are operatiuni manuale, dar generatorul raporteaza %r"
        % r394.get("manuale_fara_factura"))

    # MUTATIA: fara cheia expusa, multimea declarata se goleste — iar perechea ar acuza tot ce
    # a plecat la ANAF. Asta e chiar clasa lui R125, pe alta latura.
    fara = {k: v for k, v in r394.items() if k != "facturi_incluse"}
    goale = set()
    for ids in (fara.get("facturi_incluse") or {}).values():
        goale.update(ids or [])
    assert not goale, "stergerea cheii n-a schimbat nimic"


# ── 3b. CAMPURILE, la nivel de dataclass ───────────────────────────────────────────────────────
def test_campurile_citite_de_perechi_SUNT_CAMPURI_ale_rezultatelor():
    """Conditia de inchidere a lui **R123**, luata literal: *un camp scos deliberat din rezultat
    trebuie sa PICE.* Testele de mai sus sterg cheia din dictionarul SERIALIZAT — echivalent ca
    efect, dar nu ca instanta. Asta se uita direct la `dataclasses.fields`.

    **Se aplica doar acolo unde conceptul E un camp.** `R1_1`, `R5_1`, `R12_1` si `P48` sunt CHEI
    intr-un dictionar calculat (`d300.Rezultat.R`, `d101.RezultatD101.P`), nu campuri — pentru ele
    gardul e cel de sus, pe cheile produse. `facturi_incluse` si `manuale_fara_factura` sunt insa
    campuri adevarate (R119), si exact ele ar disparea tacut din `randuri` daca cineva le-ar scoate:
    `dataclasses.asdict` vede numai campuri. *Chiar mecanismul lui R125, pe alt generator.*

    Nu e o aserttiune pe TEXT: se citeste structura clasei, nu sursa ei (METODA §23)."""
    import dataclasses
    campuri_394 = {f.name for f in dataclasses.fields(_d394.Rezultat)}
    assert campuri_394 >= {"facturi_incluse", "manuale_fara_factura"}, (
        "perechea e-Factura ↔ D394 citeste chei care nu mai sunt CAMPURI ale rezultatului; "
        "campurile de acum: %s" % sorted(campuri_394))
    # containerele in care traiesc celelalte chei citite raman campuri, altfel `randuri` n-ar avea
    # nici macar unde sa le poarte
    assert {f.name for f in dataclasses.fields(_d300.Rezultat)} >= {"R"}
    assert {f.name for f in dataclasses.fields(_d101.RezultatD101)} >= {"P", "d_grup"}


# ── 4. D101 rd.48 ↔ cont 691 ───────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D101_vs_691_citeste_randul_48_pe_care_il_SCRIE_d101(conn_gen):
    """Perechea citeste `randuri.P.P48` si `randuri.d_grup`. Fara P48 ar compara zero cu
    contabilitatea; fara `d_grup` ar vorbi despre un rand care, la membrii unui grup fiscal, NU se
    completeaza — adica ar acuza o firma pentru ca a respectat ordinul."""
    _xml, res = _d101.genereaza(conn_gen, _SCHEMA, Perioada(_AN))
    randuri = _ca.randuri_din_res(res)
    P = randuri.get("P") or {}
    assert set(P) >= {"P48"} and set(randuri) >= {"d_grup"}, (
        "D101 generat nu scrie cheile citite de pereche; nivel inalt=%r, chei P=%r"
        % (sorted(randuri), sorted(P)[:12]))
    p48 = int(P["P48"])
    assert p48 > 0, "[anti-vacuu] impozitul iese 0 pe fixtura cu profit — nu se poate proba nimic"

    cs = _ci._pereche_691(conn_gen, _SCHEMA, _AN, p48, int(randuri.get("d_grup") or 0))
    assert len(cs) == 1 and cs[0]["declarat_d101"] == p48, (
        "cifra din declaratie nu ajunge intreaga la pereche: %r" % cs)

    # MUTATIA: cu P48 lipsa, cititorul primeste 0 si perechea tace (0 vs 0) — adica pierde exact
    # constatarea pe care ar fi trebuit s-o faca.
    p48_lipsa = int((randuri.get("P") or {}).get("P48_INEXISTENT") or 0)
    cs_m = _ci._pereche_691(conn_gen, _SCHEMA, _AN, p48_lipsa, 0)
    assert cs_m == [], "cheia lipsa ar fi trebuit sa duca la tacere, nu la o constatare: %r" % cs_m
