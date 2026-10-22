# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 451, S2] Ciorna de contare a facturii EMISE se validează numai cât e ce ar scrie factura ACUM (comanda Costin 11.1
pct.6, verbatim: „ciornele generate înainte de o reparație rămân validabile cu regula veche [...] Toate trebuie refăcute din sursă sau
marcate depășite și oprite de la validare, pe toate firmele.”).

Felul „factura_emisa” (`ciorne_depasite.SURSE`, REGENERAT): la validare, contarea se regenerează pe uscat cu `contare_facturi.note_propuse`
— aceeași funcție pe care o cheamă `contabilizeaza` — și se compară pe conturi și sume (data — contarea istorică — și documentul, derivat din
factură, rămân ale notei). Ciorna scrisă cu regula VECHE e reprodusă prin monkeypatch pe funcția regulii (`cont_venit_linie`), nu prin
INSERT-uri care ar ocoli drumul. Temei: OMFP 2634/2015 pct.58 lit.c — „fiecare dată înregistrată în contabilitate trebuie să se regăsească
în conținutul unui document”.

Schemă efemeră din `tenant_template.sql`, în tranzacție anulată; date în 2099 (sintetic). CUI-uri: 14399840 (DANTE INTERNATIONAL SA) și
18547290 (clientul din `test_lot11_b_449`), cifra de control verificată cu algoritmul din CLAUDE.md."""
import ast
import glob
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot11_s2_451"


def _azi():
    """Ziua în care testul a scris nota („generată pe …” din mesaj), în formatul românesc ZZ.LL.AAAA."""
    import datetime as _dt
    a = _dt.date.today()
    return "%02d.%02d.%d" % (a.day, a.month, a.year)
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                # profilul cerut de emitere (forma juridică și capitalul: Legea 31/1990 art.74 alin.(3); seria facturii)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura) VALUES (1,'S2 SRL',"
                            "'14399840','Str 1','Cluj-Napoca','CJ','4621','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu',"
                            "'Ion','ADMINISTRATOR','SRL',200,'SDA')")
            yield c
        finally:
            c.rollback()


def _emite(conn, numar="E1", data="2099-10-10"):
    """Factura emisă pe drumul aplicației (`creeaza_factura` scrie singură contarea ciornă, `_conteaza_la_creare`)."""
    from core import facturi_api as fa
    r = fa.creeaza_factura(conn, numar, data, "emisa",
                           [{"descriere": "Marfă", "um": "buc", "cantitate": 3, "pret_unitar": "33.33", "cota_tva": 21},
                            {"descriere": "Serviciu", "um": "buc", "cantitate": 1, "pret_unitar": "10.05", "cota_tva": 21}],
                           tert_nume="CLIENT SRL", tert_cui="18547290", status="emisa")
    assert r["contare"]["stare"] == "contata", r["contare"]
    return r["factura_id"], r["contare"]["inregistrare_id"]


def _linii(conn, nid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY cont_debit, cont_credit",
                    (nid,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


def test_451_contarea_facturii_emise_la_zi_trece(conn):
    """Fără fals pozitiv: contarea scrisă la emitere și contarea istorică (altă dată decât emiterea) sunt la zi."""
    from core import ciorne_depasite as cd, contare_facturi as cf, jurnal_api as _j
    _fid, nid = _emite(conn)
    fid2, nid2 = _emite(conn, "E2", "2099-10-11")
    with conn.cursor() as cur:   # contarea istorică: nota emiterii scoasă (ciornă), contată din nou la altă dată, cu motivul omului
        cur.execute("DELETE FROM inregistrari WHERE id = %s", (nid2,))
    with cf.cursor_dict(conn) as cur:
        nid2 = cf.contabilizeaza(cur, SCH, fid2, automat=False, data_nota="2099-10-25", motiv_data="descoperită la inventar")["inregistrare_id"]
    with conn.cursor() as cur:
        for x in (nid, nid2):
            assert cd.felul(cur, SCH, x) == "factura_emisa"
            assert cd.verifica(conn, cur, SCH, x) is None, cd.verifica(conn, cur, SCH, x)
    for x in (nid, nid2):
        assert _j.valideaza(conn, SCH, x) == {"ok": True}


def test_def_451_contarea_facturii_emise_cu_regula_veche_e_depasita_si_se_reface(conn, monkeypatch):
    """Roșu înainte (felul „factura” era NEREGENERABIL: validarea trecea); acum refuz numit, refacere din factură, validare."""
    from core import ciorne_depasite as cd, contare_facturi as cf, jurnal_api as _j
    monkeypatch.setattr(cf, "cont_venit_linie", lambda cont_venit, cont_venit_implicit=None, tip_operatiune=None: "704")   # regula veche
    fid, nid = _emite(conn)
    monkeypatch.undo()
    assert ("4111", "704", "110.04") in _linii(conn, nid)
    with conn.cursor() as cur:
        cur.execute("SELECT data, descriere FROM inregistrari WHERE id = %s", (nid,))
        data_veche, descr_veche = cur.fetchone()
    rez = _j.valideaza(conn, SCH, nid)
    # OMFP 2634/2015 pct.58 lit.c: nota trebuie să se regăsească în documentul ei — factura emisă are venitul pe 707 (contul liniei / firmei)
    assert rez.get("cod") == cd.COD, rez
    d = rez["depasita"]
    assert d["sursa_fel"] == "factura_emisa" and d["refacere"]["eticheta"] == "Refă nota din factură", d
    assert d["diferente"] == [{"ce": "rândurile", "acum": "4111 = 707 110,04", "pe_ciorna": "4111 = 704 110,04"}], d
    # mesajul întreg, pe câmpul `eroare` (core/test_garzi_pe_text.py)
    assert rez["eroare"] == (
        "Nota din 10.10.2099 a fost generată pe %s după o regulă care s-a schimbat de atunci: acum Factură E1 din 10.10.2099 ar scrie "
        "rândurile 4111 = 707 110,04 (pe ciornă: 4111 = 704 110,04). Nota e depășită și nu se validează — refă-o din Factură E1 din "
        "10.10.2099 („Refă nota din factură”), apoi valideaz-o." % _azi()), rez["eroare"]
    nou = cd.reface_factura_emisa(conn, SCH, nid)
    assert nou != nid
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari WHERE id = %s", (nid,))
        assert cur.fetchone()[0] == 0   # ciorna veche a fost înlocuită
        cur.execute("SELECT data, descriere, factura_id, status FROM inregistrari WHERE id = %s", (nou,))
        assert cur.fetchone() == (data_veche, descr_veche, fid, "ciorna")   # data și descrierea notei rămân; nota e tot ciornă
    assert ("4111", "707", "110.04") in _linii(conn, nou)
    assert _j.valideaza(conn, SCH, nou) == {"ok": True}


def test_451_refacerea_refuza_nota_care_nu_e_ciorna_de_contare(conn):
    from core import ciorne_depasite as cd, jurnal_api as _j
    _fid, nid = _emite(conn)
    assert _j.valideaza(conn, SCH, nid) == {"ok": True}
    with pytest.raises(ValueError, match="nu mai e o ciornă de contare"):
        cd.reface_factura_emisa(conn, SCH, nid)


def test_garda_contarea_facturii_are_o_singura_regula():
    """`genereaza_note` / `note_storno` (regula contării) se cheamă, în cod, NUMAI din `contare_facturi.note_propuse` — pe care le cheamă și
    `contabilizeaza`, și regenerarea pe uscat. Un al doilea apelant ar putea scrie altă contare decât cea comparată la validare.
    MUTAȚIE: corpul lui `note_propuse` copiat înapoi în `contabilizeaza` -> pică."""
    gasite = []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py")) + glob.glob(os.path.join(RAD, "*.py"))):
        if os.path.basename(f).startswith("test_"):
            continue
        arb = ast.parse(io.open(f, encoding="utf-8").read())
        for fn in ast.walk(arb):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for x in ast.walk(fn):
                if isinstance(x, ast.Call):
                    nume = x.func.attr if isinstance(x.func, ast.Attribute) else getattr(x.func, "id", None)
                    if nume in ("genereaza_note", "note_storno"):
                        gasite.append((os.path.relpath(f, RAD), fn.name, nume))
    assert sorted(set(gasite)) == [("core/contare_facturi.py", "note_propuse", "genereaza_note"),
                                   ("core/contare_facturi.py", "note_propuse", "note_storno")], gasite


class _FaraTranzactie:
    """Conexiunea fixturii cu `commit()` / `rollback()` neutralizate: use-case-ul își închide tranzacția, fixtura aruncă schema."""

    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def rollback(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def uc(conn, monkeypatch):
    import contextlib
    from core import auth_api, uc_tenants
    proxy = _FaraTranzactie(conn)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
    return uc_tenants


def test_451_ruta_refacerii_reface_contarea_depasita_si_refuza_ciorna_la_zi(conn, uc, monkeypatch):
    """Ruta `POST …/jurnal/{nota_id}/reface` (`uc_tenants.jurnal_reface`): ciorna la zi -> refuz numit, nimic scris; ciorna depășită a
    facturii emise -> nota nouă din factură, cea veche scoasă. MUTAȚIE: ramura „factura_emisa” scoasă din `jurnal_reface` -> refuzul
    „nu se poate reface din aplicație” -> pică."""
    from core import contare_facturi as cf, erori
    _fid, la_zi = _emite(conn, "E3")
    with pytest.raises(erori.CerereGresita, match="nu e nimic de refăcut"):
        uc.jurnal_reface(1, la_zi, {"uid": 1})
    assert _linii(conn, la_zi) != []   # ciorna la zi a rămas neatinsă
    regula_de_acum = cf.cont_venit_linie
    monkeypatch.setattr(cf, "cont_venit_linie", lambda cont_venit, cont_venit_implicit=None, tip_operatiune=None: "704")   # regula veche
    _fid, veche = _emite(conn, "E4")
    monkeypatch.setattr(cf, "cont_venit_linie", regula_de_acum)
    r = uc.jurnal_reface(1, veche, {"uid": 1})
    assert r["ok"] and r["nota_veche"] == veche and r["nota_id"] != veche, r
    assert ("4111", "707", "110.04") in _linii(conn, r["nota_id"]) and _linii(conn, veche) == []
    assert r["mesaj"].startswith("Nota a fost refăcută din Factură E4 din 10.10.2099"), r["mesaj"]
