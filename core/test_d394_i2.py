# -*- coding: utf-8 -*-
"""GARD — D394 Î2: încasările din activitățile exceptate de la AMEF (deciziile Costin 03.10.2026).

Deciziile: bifa „activitate exceptată de la AMEF” pe profil, cu activitatea (OUG 28/1999 art.2); „cotă pe chitanță” —
încasările Î2 sunt chitanțele FĂRĂ factură, neanulate, cu cotă; firmă exceptată cu încasări neclasificate (chitanță fără
cotă) -> D394 refuză NUMIT, nu emite zero; o încasare din registrul de casă fără chitanță și fără caracter cunoscut de
non-vânzare -> semnal numit, fără blocaj.

Temei: OPANAF 2194/2025 anexa 2 lit.G — „Î2 - încasări lunare efectuate din activităţi exceptate de la obligaţia
utilizării aparatelor de marcat electronice fiscale”; pct.15 „Total încasări” lunar, pct.16–17 bază și TVA „defalcată pe
cote de TVA (21%, 19%, 11%, 9%, 5%)”; anexa 1 lit.G: „***) Se va completa numai pentru Î1” (nr. AMEF, nr. bonuri).
OUG 28/1999 art.1 alin.(1) (vânzarea cu amănuntul încasată în numerar -> AMEF) și art.2 (activitățile exceptate).
Structura: D394Validator v5, `Op2` („daca tip_op2 = 'I2' atunci nrAMEF / nrBF nu trebuie sa fie completat”).
"""
import contextlib
import datetime as _dt
import xml.etree.ElementTree as ET
from decimal import Decimal as D

import pytest

from core import activitati_amef as _amef
from core import d394 as _d394
from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

NS = "{%s}" % _d394.NS
PROF = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "cui": "26766053", "caen": "4322", "nume": "INSTAL SRL",
        "adresa": "Str. 1", "telefon": "0722000000", "judet": "B", "declarant_functie": "ADMIN", "tip_decont": "L"}


def _ch(i, data, suma, cota):
    return {"id": i, "serie": "CH", "numar": i, "data": data, "suma": D(str(suma)),
            "cota_tva": None if cota is None else D(str(cota))}


SEPT = [_ch(1, "2026-09-02", "1210.00", 21), _ch(2, "2026-09-15", "121.50", 21), _ch(3, "2026-09-20", "333.00", 11)]


def _calc(chitante, prof=PROF, luna=9, casa=()):
    return _d394.calcul_d394(prof, Perioada(2026, luna=luna), {"facturi": [], "rapoarte_z": [],
                                                               "chitante_i2": chitante, "casa_nelegate": list(casa)})


def _op2(xml):
    return [dict(e.attrib) for e in ET.fromstring(xml.split("?>", 1)[1]).iter(NS + "op2")]


# ── defalcarea (o singură funcție pentru notă, D300, D394) ─────────────────────────────────────────────────────
@pytest.mark.parametrize("suma,cota,baza,tva", [
    ("121", 21, "100.00", "21.00"),
    ("333", 11, "300.00", "33.00"),
    ("121", 11, "109.01", "11.99"),
    ("100", 0, "100.00", "0.00"),
    ("0.05", 21, "0.04", "0.01"),     # 0,05 x 21/121 = 0,00868 -> 0,01 (ROUND_HALF_UP, CLAUDE.md „Rotunjire fiscală”)
])
def test_defalcare_suta_marita(suma, cota, baza, tva):
    # CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă”; procedeul
    # sutei mărite (HG 1/2016): TVA = suma x cota / (100 + cota). MUTAȚIE: suma x cota/100 -> 121 la 21% dă 25,41 -> pică
    assert _amef.defalcare(suma, cota) == (D(baza), D(tva))


def test_cotele_permise_urmeaza_registrul_la_data_chitantei():
    # 2026: {21, 11} + 0; 2024 (era 19%): {19, 9, 5} + 0 — din registrul de cote, nu scrise în cod
    assert _amef.cote_permise(_dt.date(2026, 9, 1)) == [21, 11, 0]
    assert _amef.cote_permise(_dt.date(2024, 5, 1)) == [19, 9, 5, 0]


# ── calculul (pur) ────────────────────────────────────────────────────────────────────────────────────────
def test_o_sectiune_i2_pe_luna_fara_amef_si_bonuri():
    r = _calc(SEPT)
    (o,) = r.op2
    # pct.15–17: 21%: (1000 + 100,41) bază / (210 + 21,09) TVA; 11%: 300/33 — fiecare rubrică rotunjită o dată pe lună;
    # total = Σ rubrici rotunjite (1664), nu 1664,50 rotunjit separat (1665) — DUK R246, vezi testul următor
    assert o == dict({"tip_op2": "I2", "luna": 9, "total": 1664, "baza21": 1100, "TVA21": 231, "baza11": 300,
                      "TVA11": 33}, **{p + c: 0 for c in ("20", "19", "9", "5") for p in ("baza", "TVA")})
    assert "nrAMEF" not in o and "nrBF" not in o
    assert (r.informatii["incasari_i2"], r.informatii["incasari_i1"], r.informatii["nr_BF_i1"]) == (1664, 0, 0)
    assert r.op_efectuate == 1


@pytest.mark.parametrize("tip", ["I1", "I2"])
def test_totalul_lunii_e_suma_rubricilor_rotunjite(tip):
    # DUK R246 (atenționare): „total <> baza21 + … + TVA5”. Un total rotunjit separat (1664,50 -> 1665) diferă de
    # rubricile rotunjite (1664) și atenționa fals. CLASA: Î1 și Î2 calculau totalul la fel. MUTAȚIE: `_int(m["total"])`
    # în loc de `_total_op2(m)` -> 1665 -> pică
    if tip == "I2":
        (o,) = _calc(SEPT + [_ch(4, "2026-09-21", "40.40", 0)]).op2
    else:
        z = [{"id": 1, "numar": "Z-1", "data": "2026-09-02", "nui": "A1", "nr_bonuri": 3,
              "cote": [(D(21), D("1100.41"), D("231.09")), (D(11), D("300"), D("33")), (D(0), D("40.40"), D(0))]}]
        (o,) = _d394.calcul_d394(PROF, Perioada(2026, luna=9), {"facturi": [], "rapoarte_z": z}).op2
    rub = sum(o["baza" + c] + o["TVA" + c] for c in _d394.OP2_RUBRICI_NOMENCL.values())
    assert (rub, o["total"]) == (1664, 1664 + 40)       # + încasările la 0% (40,40 -> 40), fără rubrică


def test_rezumat2_agrega_i2_separat_de_i1():
    # DUK R246–R255: rubricile op2 se agregă în rezumat2-ul cotei; Î2 în *_incasari_i2, nu în *_incasari_i1
    # MUTAȚIE: sufixul fix „i1” -> baza_incasari_i1[21] = 1100 -> pică
    r = _calc(SEPT)
    assert {c: (v["baza_incasari_i2"], v["tva_incasari_i2"], v["baza_incasari_i1"]) for c, v in r.rezumat2.items()} == \
        {21: (1100, 231, 0), 20: (0, 0, 0), 19: (0, 0, 0), 11: (300, 33, 0), 9: (0, 0, 0), 5: (0, 0, 0)}


def test_cota_zero_intra_doar_in_total():
    # pct.15 „Total încasări” = toate încasările lunii; rubricile de cotă sunt doar 21/19/11/9/5 (pct.16–17)
    (o,) = _calc([_ch(1, "2026-09-02", "121", 21), _ch(2, "2026-09-03", "50", 0)]).op2
    assert (o["total"], o["baza21"], o["TVA21"]) == (171, 100, 21)


def test_chitanta_fara_cota_e_numita_si_nu_intra():
    r = _calc(SEPT + [_ch(9, "2026-09-25", "50", None)])
    assert r.i2_neclasificate == [{"numar": "CH-9", "data": "2026-09-25"}]
    assert r.op2[0]["total"] == 1664


def test_trimestrial_o_sectiune_pe_fiecare_luna():
    r = _calc([_ch(1, "2026-07-02", "121", 21), _ch(2, "2026-08-03", "111", 11)], prof=dict(PROF, tip_decont="T"))
    assert [(o["tip_op2"], o["luna"], o["total"]) for o in r.op2] == [("I2", 7, 121), ("I2", 8, 111)]


def test_incasarea_din_casa_fara_chitanta_e_avertisment_numit():
    casa = [{"id": 5, "data": "2026-09-22", "document": "DI-7", "partener": "Client", "suma": D("400.00"),
             "categorie": "incasare_client"}]
    r = _calc(SEPT, casa=casa)
    # MUTAȚIE: lista nu ajunge în rezultat -> [] -> pică
    assert r.casa_nelegate == [{"id": 5, "data": "2026-09-22", "document": "DI-7", "suma": D("400.00"),
                                "categorie": "incasare_client"}]
    assert len(r.avertismente) == len(_calc(SEPT).avertismente) + 1   # și contabilul îl vede, ca avertisment
    assert r.op2 and r.i2_neclasificate == []     # semnal, nu blocaj


def test_xml_i2_fara_nramef_nrbf():
    (o,) = _op2(_d394.build_xml(_calc(SEPT)))
    # anexa 1 lit.G „***) Se va completa numai pentru Î1”; validatorul v5 respinge nrAMEF/nrBF pe Î2
    assert set(o) == {"tip_op2", "luna", "total"} | {p + c for c in _d394.OP2_RUBRICI_NOMENCL.values()
                                                     for p in ("baza", "TVA")}
    assert (o["tip_op2"], o["total"]) == ("I2", "1664")


def _duk():
    try:
        from core import duk
        return duk if duk.poate_valida("d394") else None
    except Exception:
        return None


def test_DUK_valid_cu_op2_i2():
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    v = duk.valideaza(_d394.build_xml(_calc(SEPT)), "d394", an=2026, luna=9, timeout=180)
    assert v.get("stare") == "valid", v.get("erori")


def test_DUK_respinge_nramef_pe_i2():
    # MUTAȚIA structurii: nrAMEF/nrBF scrise și pe Î2 -> DUK: „daca tip_op2 = 'I2' atunci nrAMEF nu trebuie sa fie
    # completat” — dovada că omiterea nu e cosmetică
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    x = _d394.build_xml(_calc(SEPT)).replace('tip_op2="I2" luna="9"', 'tip_op2="I2" luna="9" nrAMEF="1" nrBF="3"')
    v = duk.valideaza(x, "d394", an=2026, luna=9, timeout=180)
    assert v.get("severitate") == "eroare" and "I2" in (v.get("erori") or ""), v


# ── emiterea, clasificarea, generarea — pe schemă efemeră (ROLLBACK) ─────────────────────────────────────────
_SCHEMA = "tenant_test_i2394"


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
def conn_i2(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare,declarant_nume,declarant_prenume,declarant_functie,"
                    "cont_venit_implicit,activitate_exceptata_amef,serie_chitanta) VALUES (1,'INSTAL SRL','14399840','Str Test 1','Bucuresti','B','4322','0722000000',"
                    "'BCR','RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR','704',false,'ZC')")   # „Nu”, declarat; seria aleasă (decizii 07.10 pct.5)
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_schema_sau_404", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_cere_luna_deschisa", lambda *a, **k: None)
            yield conn
        finally:
            conn.rollback()


def _exceptata(conn, da=True):
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET activitate_exceptata_amef = %s, activitate_amef = %s",
                    (da, "i" if da else None))


def _emite(**k):
    from core import uc_tenants
    from main import ChitantaEmite
    return uc_tenants.chitanta_emite(1, ChitantaEmite(**k), {"uid": 1})


def _nota(conn, cid):
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari_linii l JOIN chitante c "
                    "ON c.inregistrare_id = l.inregistrare_id WHERE c.id = %s ORDER BY l.id", (cid,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


def _cod(e):
    return e.value.detaliu.get("cod")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_firma_neexceptata_chitanta_de_creanta_ramane_dar_vanzarea_e_refuzata(conn_i2):
    from core import erori
    r = _emite(data="2026-09-05", suma=242)
    assert _nota(conn_i2, r["chitanta_id"]) == [("5311", "4111", "242.00")]     # fluxul de dinainte, neatins
    # OUG 28/1999 art.1 alin.(1): vânzarea cu amănuntul încasată în numerar -> AMEF. MUTAȚIE: scoasă poarta -> se emite
    with pytest.raises(erori.CerereGresita) as e:
        _emite(data="2026-09-05", suma=121, cota_tva=21)
    assert _cod(e) == _amef.COD_VANZARE_NEEXCEPTATA and e.value.detaliu["temei"] == "OUG 28/1999 art.1 alin.(1)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_firma_exceptata_vanzarea_merge_pe_venit_si_4427(conn_i2):
    from core import erori
    _exceptata(conn_i2)
    r = _emite(data="2026-09-12", suma=1210, cota_tva=21, client_nume="Ion Popescu", reprezentand="reparatie")
    # nota: 5311 = contul de venit din profil (704) pentru bază, 5311 = 4427 pentru TVA — nu 5311 = 4111
    assert _nota(conn_i2, r["chitanta_id"]) == [("5311", "704", "1000.00"), ("5311", "4427", "210.00")]
    for k, cod in (({}, _amef.COD_COTA_LIPSA), ({"cota_tva": 19}, _amef.COD_COTA_NEPERMISA)):
        with pytest.raises(erori.CerereGresita) as e:
            _emite(data="2026-09-12", suma=50, **k)
        assert _cod(e) == cod


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_dispozitia_generica_nu_poate_naste_o_vanzare_fara_cota(conn_i2):
    from core import uc_tenants, erori
    _exceptata(conn_i2)
    with pytest.raises(erori.CerereGresita):
        uc_tenants.casa_adauga(1, {"data": "2026-09-12", "categorie": "vanzare_fara_factura", "suma": 10}, {"uid": 1})


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_chitanta_fara_cota_blocheaza_d394_numit_pana_la_clasificare(conn_i2):
    from core import uc_tenants, erori
    from main import ChitantaCota
    vechi = _emite(data="2026-09-05", suma=242)          # emisă înainte de marcare: 5311=4111
    _exceptata(conn_i2)
    _emite(data="2026-09-12", suma=121, cota_tva=21)
    # decizia Costin: încasări neclasificate -> refuz NUMIT, nu Î2 pe zero. MUTAȚIE: scos refuzul -> D394 se generează
    with pytest.raises(ValueError) as e:
        _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert (e.value.cod, e.value.chitante) == ("D394_I2_NECLASIFICAT", ["ZC-%s" % vechi["numar"]])
    r = uc_tenants.chitanta_cota(1, vechi["chitanta_id"], ChitantaCota(cota_tva=21), {"uid": 1})
    assert r["cota_tva"] == 21 and _nota(conn_i2, vechi["chitanta_id"]) == [("5311", "704", "200.00"),
                                                                            ("5311", "4427", "42.00")]
    with pytest.raises(erori.CerereGresita) as e2:       # a doua oară: are deja cota
        uc_tenants.chitanta_cota(1, vechi["chitanta_id"], ChitantaCota(cota_tva=11), {"uid": 1})
    assert _cod(e2) == _amef.COD_CLASIFICARE
    xml, res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    (o,) = _op2(xml)
    assert (o["tip_op2"], o["total"], o["baza21"], o["TVA21"]) == ("I2", "363", "300", "63")
    duk = _duk()
    if duk is not None:
        v = duk.valideaza(xml, "d394", an=2026, luna=9, timeout=180)
        assert v.get("stare") == "valid", v.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_clasificarea_refuza_nota_validata(conn_i2):
    from core import uc_tenants, erori
    from main import ChitantaCota
    vechi = _emite(data="2026-09-05", suma=242)
    _exceptata(conn_i2)
    with conn_i2.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = (SELECT inregistrare_id FROM chitante "
                    "WHERE id = %s)", (vechi["chitanta_id"],))
    # o notă validată nu se rescrie (se stornează) — MUTAȚIE: scoasă condiția -> nota validată și-ar schimba rândurile
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.chitanta_cota(1, vechi["chitanta_id"], ChitantaCota(cota_tva=21), {"uid": 1})
    assert _cod(e) == _amef.COD_CLASIFICARE and _nota(conn_i2, vechi["chitanta_id"]) == [("5311", "4111", "242.00")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_incasarea_din_casa_fara_chitanta_e_semnalata_ridicarea_nu(conn_i2):
    from core import uc_tenants
    _exceptata(conn_i2)
    _emite(data="2026-09-12", suma=121, cota_tva=21)
    uc_tenants.casa_adauga(1, {"data": "2026-09-22", "categorie": "incasare_client", "suma": 400, "document": "DI-7"},
                           {"uid": 1})
    uc_tenants.casa_adauga(1, {"data": "2026-09-23", "categorie": "ridicare_banca", "suma": 1000}, {"uid": 1})
    xml, res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    # decizia Costin: ridicarea de numerar din bancă e cunoscută fără caracter de vânzare; încasarea fără chitanță nu
    assert [(x["data"], x["document"], x["suma"], x["categorie"]) for x in res.casa_nelegate] == \
        [("2026-09-22", "DI-7", D("400.00"), "incasare_client")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_exceptarea_neleasa_se_cere_la_prima_chitanta_fara_factura(conn_i2):
    """[lotul 07.10 B, comanda Costin A.3] fără implicit în schemă: neleasă, prima chitanță fără factură o cere, numit, cu ecranul
    Date firmă (OUG 28/1999 art.2). MUTAȚIE: scoasă ramura `exceptata is None` -> chitanța se emite ca încasare de creanță."""
    from core import erori
    _exceptata(conn_i2, None)
    with pytest.raises(erori.CerereGresita) as e:
        _emite(data="2026-09-05", suma=242)
    assert (_cod(e), e.value.detaliu["ecran"]) == (_amef.COD_NEDECLARATA, "date_firma")


def test_exceptarea_neleasa_opreste_d394_numai_cand_schimba_declaratia(conn_i2):
    """D394 se oprește pe exceptarea neleasă NUMAI dacă în perioadă sunt chitanțe fără factură și fără cotă (creanță la firma
    neexceptată, vânzare neclasificată la cea exceptată); fără ele, răspunsul n-ar schimba nimic și D394 se generează."""
    _emite(data="2026-09-05", suma=242)                  # emisă cu „Nu” declarat
    _exceptata(conn_i2, None)
    xml, _res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=8))       # luna fără chitanțe: trece
    with pytest.raises(ValueError) as e:
        _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert (e.value.cod, e.value.ecran) == (_amef.COD_NEDECLARATA, "date_firma")


def test_firma_neexceptata_nu_semnaleaza_si_nu_refuza(conn_i2):
    from core import uc_tenants
    _emite(data="2026-09-05", suma=242)                 # încasare de creanță, firmă neexceptată
    uc_tenants.casa_adauga(1, {"data": "2026-09-22", "categorie": "incasare_client", "suma": 400}, {"uid": 1})
    xml, res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert _op2(xml) == [] and res.casa_nelegate == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_include_vanzarile_pe_chitanta(conn_i2):
    from core import d300
    _exceptata(conn_i2)
    _emite(data="2026-09-12", suma=1210, cota_tva=21)
    _emite(data="2026-09-13", suma=333, cota_tva=11)
    # CF art.282 alin.(1): exigibilitatea la faptul generator; TVA-ul creditat în 4427 intră în decont, rd.9/10
    # MUTAȚIE: scos `_pull_chitante_i2` din `pull` -> R9_1 = 0 -> pică
    xml, res = d300.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert (res.R.get("R9_1"), res.R.get("R9_2"), res.R.get("R10_1"), res.R.get("R10_2")) == (1000, 210, 300, 33)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_doua_cale_recalculeaza_i2_din_chitante(conn_i2):
    from core.d394_reconciliere import reconciliaza
    _exceptata(conn_i2)
    _emite(data="2026-09-12", suma=1210, cota_tva=21)
    _emite(data="2026-09-13", suma=333, cota_tva=11)
    xml, res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert reconciliaza(conn_i2, Perioada(2026, luna=9), res)["divergente"] == []
    # MUTAȚIE (pe rezultat): o rubrică Î2 agregată greșit -> calea a doua o numește
    res.informatii["incasari_i2"] += 1
    res.rezumat2[11]["baza_incasari_i2"] += 1
    div = reconciliaza(conn_i2, Perioada(2026, luna=9), res)["divergente"]
    assert [(d["cota"], d["camp"], d["diferenta"]) for d in div] == [(0, "incasari_i2", 1), (11, "baza_incasari_i2", 1)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_doua_cale_aplica_aceeasi_definitie_a_totalului(conn_i2):
    # DUK R246: total = Σ rubrici rotunjite (+ cota 0). Calea a doua își calculează singură totalul; cu sume fracționare
    # (1100,41 + 231,09 + 300 + 33 = 1664,50) o definiție diferită ar da 1665 vs 1664 și ar bloca generarea.
    # MUTAȚIE: `_q(m["total"])` în loc de `_total_luna(m)` pe Î1 sau pe Î2 -> divergență numită -> pică
    from core.d394_reconciliere import reconciliaza
    _exceptata(conn_i2)
    for zi, suma, cota in (("02", "1210.00", 21), ("15", "121.50", 21), ("20", "333.00", 11)):
        _emite(data="2026-09-%s" % zi, suma=float(suma), cota_tva=cota)
    with conn_i2.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) "
                    "VALUES ('2026-09-10','Z-8000000009-0001','z','horeca_z','validata') RETURNING id")
        iid = cur.fetchone()[0]
        for c, b, t in ((21, "1100.41", "231.09"), (11, "300", "33")):
            cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s,%s,%s,%s)", (iid, c, b, t))
        cur.execute("INSERT INTO rapoarte_z_amef (inregistrare_id, nui, nr_bonuri) VALUES (%s,'8000000009',3)", (iid,))
    xml, res = _d394.genereaza(conn_i2, _SCHEMA, Perioada(2026, luna=9))
    assert (res.informatii["incasari_i1"], res.informatii["incasari_i2"]) == (1664, 1664)
    assert reconciliaza(conn_i2, Perioada(2026, luna=9), res)["divergente"] == []
