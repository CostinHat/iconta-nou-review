# -*- coding: utf-8 -*-
"""[lotul 12, C19 — comanda Costin 12.3 pct.6, verbatim în DECIZII] „rectificativa D394 pentru o perioadă deja depusă se generează doar
la cererea contabilului, cu diferențele față de cea depusă arătate înainte; niciodată automat.”

CE ERA: peste o D394 depusă, orice generare (pasul 2 al Declarațiilor, „Trimite în coadă”, „Generează din nou” din coadă și reluarea
AUTOMATĂ a declarației care aștepta validarea notelor — `uc_coada.reia_declaratiile_in_asteptare`) producea direct declarația care
înlocuiește depunerea, cu o singură mențiune pe ecran; diferențele față de cea depusă nu se vedeau nicăieri, iar reluarea automată o
punea în coadă fără niciun clic.

ACUM: `rectificativa.poarta_d394` (chemată de `uc_declaratii.poarta_cererii` pe fiecare drum al cererilor) refuză generarea peste o
depunere până când contabilul confirmă EXACT conținutul văzut ca diferențe (amprenta XML-ului), iar fără diferențe nu generează nimic;
la depunere, `rectificativa.refuz_la_depunere` oprește D394 din coadă fără confirmare (cele intrate înainte de reparație).

TEMEI (citat pe liniile aserțiunilor): OPANAF 2194/2025 anexa nr.2 pct.3 — „declaraţie care înlocuieşte declaraţia informativă depusă
iniţial”; D394 n-are bifă de rectificativă în XML (D394Validator v5: rădăcina fără `d_rec`), deci rectificativa = declarația completă.

Datele: firmă SINTETICĂ (schema `ztest_lot12_decl3` din `tenant_template.sql` + un rând nou în `public.tenants`, tenant_id sintetic), totul
într-o tranzacție ANULATĂ — depunerile din tabela partajată `public.declaratii_depuse` nu pot ciocni o depunere reală. CUI-urile
partenerilor (2864518, 1590082) și al firmei (14399840): cifra de control verificată cu `cui_valid` din CLAUDE.md."""
import ast
import contextlib
import glob
import inspect
import os
import textwrap
import types

import pytest

from core import d394, db as _db, duk, rectificativa as R, tenant_provisioning as _tp
from core import coada_api, uc_declaratii
from core.common import Perioada
from core import erori as _erori

_SCHEMA = "ztest_lot12_decl3"
_CUI = "14399840"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


nevoie_db = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def firma():
    """Firmă sintetică plătitoare de TVA lunar, profil complet pentru D394; ROLLBACK la final."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,regim_fiscal,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA C19 SRL',%s,'Str. Probei 9','Cluj-Napoca','CJ',"
                            "'4690','BT','RO59BTRLRONCRT0C69TEST01','0264111222','profit',true,'L','POPESCU','ION','ADMINISTRATOR')", (_CUI,))
                cur.execute("INSERT INTO public.tenants (schema_name, nume, cui) VALUES (%s, 'PROBA C19 SRL', %s) RETURNING id", (_SCHEMA, _CUI))
                tid = cur.fetchone()[0]
            yield {"conn": conn, "schema": _SCHEMA, "tid": tid}
        finally:
            conn.rollback()


def _factura(f, numar, cui, nume, baza, cota=21, data="2026-06-10"):
    with f["conn"].cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_oras, status, "
                    "taxare_inversa) VALUES ('E19', %s, %s, 'emisa', %s, %s, %s, %s, 'Cluj-Napoca', 'emisa', false) RETURNING id",
                    (numar, data, baza * (100 + cota) / 100, baza * cota / 100, cui, nume))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) VALUES (%s,'Marfa','buc',1,%s,%s)",
                    (fid, baza, cota))


# fixtura-sintetica-ok: tenant_id sintetic (rândul nou din public.tenants al fixturii `firma`), totul în ROLLBACK
def _depune(f, xml, sursa="iconta", luna=6):
    with f["conn"].cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, sursa, data_depunere, nr_depunere) "
                    "SELECT %s, 2026, %s, 'd394', %s, %s, '2026-07-20 10:00+03', COALESCE(MAX(nr_depunere), 0) + 1 "
                    "FROM public.declaratii_depuse WHERE tenant_id = %s AND an = 2026 AND luna = %s AND tip = 'd394'",
                    (f["tid"], luna, xml, sursa, f["tid"], luna))


def _gen(f, date_extra=None):
    body = {"an": 2026, "luna": 6}
    if date_extra:
        body["date_extra"] = date_extra
    xml, res = d394.genereaza(f["conn"], f["schema"], Perioada(2026, luna=6))
    return body, xml, res


def _poarta(f, body, xml, res):
    uc_declaratii.poarta_cererii(f["conn"], f["schema"], "d394", body, xml, res)


# ============================================================
#  1. Poarta cererii
# ============================================================
@nevoie_db
def test_fara_depunere_initiala_trece(firma):
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    body, xml, res = _gen(firma)
    _poarta(firma, body, xml, res)   # nicio depunere pe 06/2026: declarația inițială nu cere nicio confirmare


@nevoie_db
def test_peste_depunere_fara_cerere_nu_se_genereaza_si_arata_diferentele(firma):
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _b, xml_depus, _r = _gen(firma)
    _depune(firma, xml_depus)
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    body, xml, res = _gen(firma)
    with pytest.raises(R.RefuzRectificativa) as e:
        _poarta(firma, body, xml, res)
    d = e.value.detaliu()
    # OPANAF 2194/2025 anexa nr.2 pct.3: declarația nouă „înlocuieşte declaraţia informativă depusă iniţial” — deci se cere, nu se face
    assert d["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and d["xml_depus_pastrat"] is True and d["schimbata"] is False, d
    assert d["amprenta"] == coada_api.amprenta_xml(xml)
    assert d["mesaj"].startswith("D394 pe 06/2026 e deja depusă (declarația depusă prin iConta.eu pe 20.07.2026). O rectificativă o "
                                 "înlocuiește integral (OPANAF 2194/2025 anexa nr.2 pct.3)"), d["mesaj"]
    lista = "Secțiunea a 2-a, lista C — partener înregistrat în scopuri de TVA în România"
    rand = "L · CLIENT DOI SRL (1590082) · cota 21%"
    dif = {(x["sectiune"], x["rand"], x["camp"]): (x["depus"], x["nou"]) for x in d["diferente"]}
    # rândul nou din lista C (secțiunea a 2-a): partenerul care nu era în declarația depusă
    assert dif[(lista, rand, "nr. facturi (nrFact)")] == ("—", "1"), d["diferente"]
    assert dif[(lista, rand, "baza impozabilă (baza)")] == ("—", "500")
    assert dif[(lista, rand, "TVA (tva)")] == ("—", "105")
    # rezumatul C pe cota 21%: 1 -> 2 facturi, baza 1000 -> 1500
    rez = ("C. Rezumat — partener înregistrat în scopuri de TVA în România", "cota 21%")
    assert dif[rez + ("nr. facturi — livrări (facturiL)",)] == ("1", "2"), d["diferente"]
    assert dif[rez + ("baza impozabilă — livrări (bazaL)",)] == ("1000", "1500"), d["diferente"]
    # partenerul care nu s-a schimbat nu apare
    assert all(x["rand"] != "L · ALTEX ROMANIA SRL (2864518) · cota 21%" for x in d["diferente"]), d["diferente"]


@nevoie_db
def test_cererea_contabilului_genereaza_numai_continutul_vazut(firma):
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, _gen(firma)[1])
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    body, xml, res = _gen(firma)
    amprenta = coada_api.amprenta_xml(xml)
    body_c, xml_c, res_c = _gen(firma, {"rectificativa_confirmata": amprenta})
    _poarta(firma, body_c, xml_c, res_c)   # cererea contabilului pentru exact ce a văzut: se generează
    # datele s-au schimbat după ce a văzut diferențele: confirmarea veche nu mai ține
    _factura(firma, "3", "RO1590082", "CLIENT DOI SRL", 200)
    body_v, xml_v, res_v = _gen(firma, {"rectificativa_confirmata": amprenta})
    with pytest.raises(R.RefuzRectificativa) as e:
        _poarta(firma, body_v, xml_v, res_v)
    d = e.value.detaliu()
    assert d["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and d["schimbata"] is True and d["amprenta"] != amprenta, d
    assert d["mesaj"] == ("D394 pe 06/2026 e deja depusă (declarația depusă prin iConta.eu pe 20.07.2026). Datele perioadei s-au schimbat după "
                          "ce ai văzut diferențele; uită-te din nou la ele. O rectificativă o înlocuiește integral (OPANAF 2194/2025 anexa nr.2 "
                          "pct.3) și se generează numai la cererea ta, din Declarații, după ce vezi diferențele față de cea depusă."), d["mesaj"]


@nevoie_db
def test_fara_diferente_nu_genereaza_nimic_nici_cerut(firma):
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _b, xml, _r = _gen(firma)
    _depune(firma, xml)
    for extra in (None, {"rectificativa_confirmata": coada_api.amprenta_xml(xml)}):
        body, xml2, res2 = _gen(firma, extra)
        with pytest.raises(R.RefuzRectificativa) as e:
            _poarta(firma, body, xml2, res2)
        d = e.value.detaliu()
        assert d["cod"] == "RECTIFICATIVA_FARA_DIFERENTE" and d["diferente"] == [] and d["amprenta"] is None, d
        assert d["mesaj"] == ("D394 pe 06/2026: declarația generată acum din datele firmei e identică cu declarația depusă prin iConta.eu "
                              "pe 20.07.2026. Nu e nimic de rectificat, deci nu se generează nicio declarație.")


@nevoie_db
def test_depunerea_fara_xml_pastrat_arata_tot_continutul(firma):
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, None, sursa="extern")
    body, xml, res = _gen(firma)
    with pytest.raises(R.RefuzRectificativa) as e:
        _poarta(firma, body, xml, res)
    d = e.value.detaliu()
    assert d["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and d["xml_depus_pastrat"] is False, d
    assert d["diferente"] and {x["depus"] for x in d["diferente"]} == {d394.NECUNOSCUT}, d["diferente"][:3]
    assert ("Secțiunea a 2-a, lista C — partener înregistrat în scopuri de TVA în România", "L · ALTEX ROMANIA SRL (2864518) · cota 21%",
            "baza impozabilă (baza)", "1000") in {(x["sectiune"], x["rand"], x["camp"], x["nou"]) for x in d["diferente"]}


@nevoie_db
def test_rectificativa_ceruta_trece_validatorul_anaf(firma):
    """DUK D394 e judecătorul: rectificativa e declarația completă, fără marcaj (D394Validator v5 n-are `d_rec` pe rădăcină)."""
    if not duk.poate_valida("d394"):
        pytest.skip("DUK d394 indisponibil")
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, _gen(firma)[1])
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    _b, xml, _r = _gen(firma)
    body, xml_c, res_c = _gen(firma, {"rectificativa_confirmata": coada_api.amprenta_xml(xml)})
    _poarta(firma, body, xml_c, res_c)
    assert res_c.rectificativa and res_c.rectificativa.startswith("Rectificativă: înlocuiește declarația depusă prin iConta.eu")
    v = duk.valideaza(xml_c, "d394", an=2026, luna=6, timeout=180)
    if v.get("stare") == "gri":
        pytest.skip("validator D394 indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", (v.get("erori") or "")[:600]


# ============================================================
#  2. Drumurile cererilor: use-case-ul ecranului, coada (și reluarea automată), depunerea
# ============================================================
@nevoie_db
def test_pasul_2_al_declaratiilor_primeste_diferentele(firma, monkeypatch):
    """`POST /declaratii/d394/valideaza` (pasul 2): refuzul ajunge la ecran ca obiect (cod + diferențe), nu ca text."""
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, _gen(firma)[1])
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    monkeypatch.setattr(uc_declaratii.auth_api, "schema_tenant", lambda conn, uid, tid: firma["schema"])
    monkeypatch.setattr(uc_declaratii.db, "get_conn", lambda schema=None: contextlib.nullcontext(firma["conn"]))
    monkeypatch.setattr(uc_declaratii, "aduce_localitati_parteneri", lambda schema, tip: None)
    date = types.SimpleNamespace(model_dump=lambda **k: {"tenant_id": firma["tid"], "an": 2026, "luna": 6})
    with pytest.raises(_erori.DateInvalide) as e:
        uc_declaratii.declaratie_valideaza("d394", date, {"uid": 1})
    assert e.value.detaliu["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and e.value.detaliu["diferente"], e.value.detaliu


@nevoie_db
def test_coada_nu_primeste_rectificativa_neceruta(firma, monkeypatch):
    """„Trimite în coadă”, „Generează din nou” și reluarea automată după validarea notelor trec prin `coada_adauga`: fără cererea
    contabilului, D394 peste o depunere nu intră în coadă (refuzul e înaintea oricărei scrieri)."""
    from core import uc_coada as uq, uc_comun
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, _gen(firma)[1])
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, p: True)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: firma["schema"])
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: contextlib.nullcontext(firma["conn"]))
    monkeypatch.setattr(uc_declaratii, "aduce_localitati_parteneri", lambda schema, tip: None)
    scrieri = []
    monkeypatch.setattr(coada_api, "adauga_in_coada", lambda *a, **k: scrieri.append(a) or {"ok": True})
    d = types.SimpleNamespace(tip="d394", tenant_id=firma["tid"], an=2026, luna=6, trim=None, motiv_trecere=None, inceput_la=None,
                              inlocuieste=None, model_dump=lambda **k: {"tip": "d394", "tenant_id": firma["tid"], "an": 2026, "luna": 6})
    with pytest.raises(_erori.DateInvalide) as e:
        uq.coada_adauga(d, {"uid": 1, "firm": 1})
    assert e.value.detaliu["cod"] == "RECTIFICATIVA_DE_CONFIRMAT" and scrieri == [], e.value.detaliu


@nevoie_db
def test_depunerea_opreste_d394_din_coada_fara_cerere(firma):
    """Declarațiile intrate în coadă înainte de reparație (generate fără diferențe arătate) nu pleacă: „Confirmă depunerea” le refuză."""
    _factura(firma, "1", "RO2864518", "ALTEX ROMANIA SRL", 1000)
    _depune(firma, _gen(firma)[1])
    _factura(firma, "2", "RO1590082", "CLIENT DOI SRL", 500)
    body, xml, res = _gen(firma)
    rand = {"depunere_anterioara_nr": res.depunere_anterioara_nr}
    with firma["conn"].cursor() as cur:
        r = R.refuz_la_depunere(cur, firma["tid"], "d394", 2026, 6, {"xml": xml, "randuri": rand, "_cerere": body})
        assert r and r["cod"] == "RECTIFICATIVA_NECONFIRMATA", r
        assert r["mesaj"].startswith("D394 pe 06/2026 e deja depusă (declarația depusă prin iConta.eu pe 20.07.2026), iar declarația aceasta "
                                     "o înlocuiește fără ca diferențele față de ea să-ți fi fost arătate."), r["mesaj"]
        # coada de dinainte de C77 (fără `depunere_anterioara_nr`): la fel
        assert R.refuz_la_depunere(cur, firma["tid"], "d394", 2026, 6, {"xml": xml})["cod"] == "RECTIFICATIVA_NECONFIRMATA"
        cerere = dict(body, date_extra={"rectificativa_confirmata": coada_api.amprenta_xml(xml)})
        assert R.refuz_la_depunere(cur, firma["tid"], "d394", 2026, 6, {"xml": xml, "randuri": rand, "_cerere": cerere}) is None


# ============================================================
#  3. Gărzi structurale
# ============================================================
def _apeluri(nod):
    out = set()
    for n in ast.walk(nod):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                out.add(n.func.id)
            elif isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name):
                out.add("%s.%s" % (n.func.value.id, n.func.attr))
    return out


def test_orice_drum_al_cererilor_cheama_poarta():
    """Orice funcție a use-case-urilor (`core/uc_*.py`) care cheamă dispecerul (`declaratii_api.genereaza`) cheamă și `poarta_cererii` —
    un drum nou al cererilor fără poartă (ar genera rectificativa D394 neceruta) -> ROȘU. Anti-vacuu: drumurile de azi sunt găsite."""
    gasite, fara = set(), []
    for cale in sorted(glob.glob(os.path.join(_RAD, "core", "uc_*.py"))):
        arbore = ast.parse(open(cale, encoding="utf-8").read())
        for f in ast.walk(arbore):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and {"declaratii_api.genereaza"} <= _apeluri(f):
                gasite.add("%s.%s" % (os.path.basename(cale)[:-3], f.name))
                if not {"poarta_cererii"} <= _apeluri(f):
                    fara.append("%s.%s" % (os.path.basename(cale)[:-3], f.name))
    assert {"uc_declaratii.declaratie_valideaza", "uc_declaratii.declaratie_genereaza", "uc_coada.coada_adauga"} <= gasite, gasite
    assert fara == [], "drumuri ale cererilor fără poarta cererii (C19): %s" % fara


def test_poarta_cererii_cheama_poarta_rectificativei():
    corp = ast.parse(textwrap.dedent(inspect.getsource(uc_declaratii.poarta_cererii)))
    assert {"_rect.poarta_d394"} <= _apeluri(corp)


def test_diferentele_citesc_toate_sectiunile_d394():
    """Fiecare secțiune scrisă de `build_xml` are rândul ei în diferențe (nu cade pe „poziția N”): o rubrică schimbată se numește."""
    dep = ('<declaratie394 xmlns="%s" luna="6" an="2026" cui="14399840" totalPlata_A="10"><informatii nrCui1="1"/>'
           '<rezumat1 tip_partener="1" cota="21" facturiL="1"><detaliu bun="25" nrLivV="1"/></rezumat1><rezumat2 cota="21" bazaL="1"/>'
           '<serieFacturi tip="2" serieI="E19" nrI="1" nrF="1"/><op1 tip="V" tip_partener="1" cota="21" cuiP="2864518" denP="A" nrFact="1" '
           'baza="1"><op11 codPR="25" nrFactPR="1" bazaPR="1"/></op1><op2 tip_op2="I1" luna="6" nrAMEF="1" total="1"/></declaratie394>'
           % d394.NS)
    nou = dep
    for rubrica in ("nrCui1", "facturiL", "nrLivV", "bazaL", "nrF", "nrFact", "bazaPR", "total"):   # câte o rubrică în fiecare secțiune
        nou = nou.replace(' %s="1"' % rubrica, ' %s="2"' % rubrica)
    sect = {x["sectiune"] for x in d394.diferente(dep, nou)}
    assert sect == {"I. Alte informații", "C. Rezumat — partener înregistrat în scopuri de TVA în România", "H. Rezumatul declarației",
                    "Seriile facturilor", "Secțiunea a 2-a, lista C — partener înregistrat în scopuri de TVA în România",
                    "G. Încasări prin casa de marcat și din activități exceptate"}, sect
    assert d394.diferente(dep, dep) == [] and d394.diferente(None, dep) is None and d394.diferente("<nu-e-xml", dep) is None
    assert d394.diferente(dep.replace('luna="6"', 'luna="06"', 1), dep) == []   # aceeași valoare scrisă altfel nu e o diferență
