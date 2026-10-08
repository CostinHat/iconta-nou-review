# -*- coding: utf-8 -*-
"""GARD — încasările prin casa de marcat (rapoartele Z) intră în D394, secțiunea op2 Î1 (decizia Costin B, 02.10.2026).

Datoria închisă: `test_datorie_d394_op2_incasari_amef_din_rapoarte_z`. D394 ținea pe 0 `nr_BF_i1`/`incasari_i1` și
`rezumat2.baza/tva_incasari_i1` și nu emitea niciun `<op2>`, deși D300 citea deja rapoartele Z. Decizia: ruta tastată
cere numărul de bonuri (NUI-ul casei îl cerea deja), ambele rute scriu ACELAȘI rând `rapoarte_z_amef`, D394 citește o
singură sursă, iar un raport Z validat fără casă / bonuri / cote face D394 să refuze NUMIT, nu să emită zero.

Temei (OPANAF 2194/2025, anexa D394 lit.G + instrucțiuni): „Î1 - încasări lunare prin intermediul aparatelor de marcat
electronice fiscale”; „nr. de AMEF - se va completa numărul aparatelor de marcat electronice fiscale ce sunt utilizate în
fiecare lună din perioada de raportare”; pct.14 „Nr. bonuri fiscale - se înscrie numărul total al bonurilor fiscale emise
în fiecare lună”. Structura și regulile: D394Validator v5 (`Op2`; DUK regulile R246–R255 + regula op_efectuate/rezumat2).
"""
import contextlib
import xml.etree.ElementTree as ET
from decimal import Decimal as D

import pytest

from core import d394 as _d394
from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

NS = "{%s}" % _d394.NS
PROF = {"declarant_nume": "Popescu", "declarant_prenume": "Ion", "cui": "26766053", "caen": "5610", "nume": "HORECA SRL",
        "adresa": "Str. 1", "telefon": "0722000000", "judet": "B", "declarant_functie": "ADMIN", "tip_decont": "L"}


def _z(i, data, nui, bonuri, cote):
    return {"id": i, "numar": "Z-%s-%04d" % (nui or "X", i), "data": data, "nui": nui, "nr_bonuri": bonuri,
            "cote": [(D(str(c)), D(str(b)), D(str(t))) for c, b, t in cote]}


IUNIE = [_z(1, "2026-06-03", "A1", 120, [(21, "1000", "210"), (11, "100", "11")]),
         _z(2, "2026-06-20", "A1", 30, [(21, "200", "42")]),
         _z(3, "2026-06-04", "A2", 80, [(21, "500.40", "105.08"), (0, "40", "0")])]


IUNIE_TAXABIL = IUNIE[:2] + [_z(3, "2026-06-04", "A2", 80, [(21, "500.40", "105.08")])]


def _calc(z, prof=PROF, luna=6, facturi=()):
    return _d394.calcul_d394(prof, Perioada(2026, luna=luna), {"facturi": list(facturi), "rapoarte_z": z,
                                                               "serii": {"A": (1, 1)} if facturi else {}})


def _op2(xml):
    return [dict(e.attrib) for e in ET.fromstring(xml.split("?>", 1)[1]).iter(NS + "op2")]


# ── calculul (pur) ────────────────────────────────────────────────────────────────────────────────────────
def test_o_sectiune_pe_luna_case_distincte_bonuri_insumate():
    # instrucțiuni: nr. de AMEF = „numărul aparatelor … utilizate în fiecare lună” (A1 de două ori = o casă);
    # pct.14: nr. bonuri = totalul lunii. MUTAȚIE: nrAMEF = numărul de rapoarte -> 3 -> pică
    r = _calc(IUNIE)
    assert len(r.op2) == 1
    o = r.op2[0]
    assert (o["tip_op2"], o["luna"], o["nrAMEF"], o["nrBF"]) == ("I1", 6, 2, 230)
    # pct.15–17: total încasări (toate cotele, inclusiv 0%) 2208,48; bază/TVA 21% 1700,40/357,08; 11% 100/11 — lei întregi
    assert (o["total"], o["baza21"], o["TVA21"], o["baza11"], o["TVA11"], o["baza9"], o["TVA5"]) == \
        (2208, 1700, 357, 100, 11, 0, 0)
    assert (r.informatii["nr_BF_i1"], r.informatii["incasari_i1"]) == (230, 2208)


def test_rezumat2_agrega_op2_pe_fiecare_cota_rubricii():
    # DUK R246–R255: fiecare rubrică op2 (obligatorie, deci și la 0) se agregă în rezumat2-ul cotei ei
    r = _calc(IUNIE)
    assert {c: (v["baza_incasari_i1"], v["tva_incasari_i1"]) for c, v in r.rezumat2.items()} == \
        {21: (1700, 357), 20: (0, 0), 19: (0, 0), 11: (100, 11), 9: (0, 0), 5: (0, 0)}
    assert r.op_efectuate == 1     # validator v5: op_efectuate = 0 interzice rezumat2


def test_trimestrial_o_sectiune_pe_fiecare_luna():
    # anexa D394 lit.G: „încasări lunare” — pe un trimestru, câte o secțiune op2 pentru fiecare lună cu rapoarte
    z = [_z(1, "2026-04-10", "A1", 10, [(21, "121", "21")]), _z(2, "2026-05-11", "A1", 5, [(11, "111", "11")])]
    r = _calc(z, prof=dict(PROF, tip_decont="T"))
    assert [(o["luna"], o["nrBF"], o["total"]) for o in r.op2] == [(4, 10, 142), (5, 5, 122)]


def test_raportul_incomplet_e_numit_si_nu_intra():
    # decizia Costin 02.10: un raport fără casă/bonuri face D394 să refuze NUMIT (nu op2 pe zero)
    z = [_z(1, "2026-06-03", None, None, [(21, "100", "21")]),
         _z(2, "2026-06-04", "A1", 9, []),
         _z(3, "2026-06-05", "A1", 9, [(24, "100", "24")]),
         _z(4, "2026-06-06", "A2", 9, [(21, "100", "21")])]
    r = _calc(z)
    assert [(x["numar"], len(x["lipsa"])) for x in r.z_incomplete] == [("Z-X-0001", 1), ("Z-A1-0002", 1), ("Z-A1-0003", 1)]
    assert [(o["nrAMEF"], o["nrBF"]) for o in r.op2] == [(1, 9)]


def test_fara_rapoarte_z_nu_apare_op2():
    r = _calc([], facturi=[{"cui": "RO14399840", "nume": "P", "directie": "emisa", "cota": 21, "baza": D(1000),
                             "tva": D(210), "taxare_inversa": False, "categorie_331": None}])
    assert r.op2 == [] and _op2(_d394.build_xml(r)) == [] and r.informatii["nr_BF_i1"] == 0


def test_xml_op2_are_toate_rubricile_si_op_efectuate():
    x = _d394.build_xml(_calc(IUNIE))
    rad = ET.fromstring(x.split("?>", 1)[1])
    assert rad.get("op_efectuate") == "1"
    (o,) = _op2(x)
    # „atributul trebuie sa existe” — toate rubricile de cotă ale clasei Op2 (v5)
    assert set(o) == {"tip_op2", "luna", "nrAMEF", "nrBF", "total"} | {p + c for c in _d394.OP2_RUBRICI_NOMENCL.values()
                                                                         for p in ("baza", "TVA")}
    assert (o["nrAMEF"], o["nrBF"], o["total"]) == ("2", "230", "2208")


def _duk():
    try:
        from core import duk
        return duk if duk.poate_valida("d394") else None
    except Exception:
        return None


@pytest.mark.parametrize("caz", ["doar_z", "z_si_facturi", "trimestrial"])
def test_DUK_valid_cu_op2(caz):
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    if caz == "trimestrial":
        r = _calc([_z(1, "2026-04-10", "A1", 10, [(21, "121", "21")]), _z(2, "2026-05-11", "A2", 5, [(11, "111", "11")])],
                  prof=dict(PROF, tip_decont="T"))
    else:
        fact = [] if caz == "doar_z" else [{"cui": "RO14399840", "nume": "P", "directie": "emisa", "cota": 21,
                                            "baza": D(1000), "tva": D(210), "taxare_inversa": False, "categorie_331": None}]
        r = _calc(IUNIE_TAXABIL, facturi=fact)
    v = duk.valideaza(_d394.build_xml(r), "d394", an=2026, luna=6, timeout=180)
    assert v.get("stare") == "valid", v.get("erori")


def test_DUK_incasarile_la_cota_zero_dau_doar_atentionare():
    # pct.15: „Total încasări” = toate încasările lunii, deci și cele la 0%; validatorul admite (total ≥ Σbaze, eroare
    # doar sub) și doar ATENȚIONEAZĂ R246 când total ≠ Σ(baze+TVA) — semnul că o încasare n-are cotă. Neblocant.
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    v = duk.valideaza(_d394.build_xml(_calc(IUNIE)), "d394", an=2026, luna=6, timeout=180)
    assert v.get("severitate") == "atentionare", v.get("erori")


# ── rutele + generarea, pe schemă efemeră (ROLLBACK) ───────────────────────────────────────────────────────────
_SCHEMA = "tenant_test_z394"


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


_XML_AMEF = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<msj idM="8000000001202606041930120042">'
             '<rB idR="8000000001202606041930120042" nrAv="0" nrB="%s" totB="2450.00"'
             ' nrBC="2" totBC="300.00" nrA="0" totA="0" nrR="0" totR="0" nrM="0" totM="0"'
             ' totTva="399.14" totTvaC="0" totTaxes="0" totTaxe="0" totNet="0"'
             ' sume_serv_in="0" sume_serv_out="0" monRef="RON">'
             '<pl tipP="1" valPl="1450.00" monPl="RON"/>'
             '<pl tipP="3" valPl="1000.00" monPl="RON"/>'
             '<coteZ cota="21" valOp="2100.00" tva="364.46"/>'
             '<coteZ cota="11" valOp="350.00" tva="34.68"/>'
             '</rB></msj>')


class _Z:
    data = "2026-06-10"
    nui = "8000000002"
    nr_raport = "0007"
    nr_bonuri = 42
    total_11 = 111.0
    total_21 = 1210.0
    numerar = 1321.0
    card = 0.0


@pytest.fixture
def conn_z(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare,declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'HORECA Z SRL','14399840','Str Test 1','Bucuresti','B','5610','0722000000','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR')")
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_cere_luna_deschisa", lambda *a, **k: None)
            yield conn
        finally:
            conn.rollback()


def _amef_rows(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT nui, nr_bonuri FROM rapoarte_z_amef ORDER BY nui")
        return [tuple(r) for r in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ambele_rute_scriu_acelasi_rand_amef(conn_z):
    from core import uc_tenants
    uc_tenants.horeca_import_amef(1, (_XML_AMEF % 35).encode(), {"uid": 1})
    uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})
    # importul: NUI din idR + nrB din fișier; tastat: NUI + nr. bonuri cerute contabilului — același tabel
    assert _amef_rows(conn_z) == [("8000000001", 35), ("8000000002", 42)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ruta_tastata_refuza_raportul_fara_numar_de_bonuri(conn_z):
    from core import uc_tenants, erori
    from core.mesaje import MESAJ_Z_FARA_BONURI

    class _Fara(_Z):
        nr_bonuri = 0
    # MUTAȚIE: scoasă poarta din horeca_raport_z -> rândul ar pica pe CHECK în bază (500), nu un refuz de contabil
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.horeca_raport_z(1, _Fara(), {"uid": 1})
    assert e.value.args[0] == MESAJ_Z_FARA_BONURI and _amef_rows(conn_z) == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_importul_fara_nrB_e_refuzat(conn_z):
    from core import uc_tenants, erori
    with pytest.raises(erori.DateInvalide):
        uc_tenants.horeca_import_amef(1, (_XML_AMEF % 0).encode(), {"uid": 1})
    assert _amef_rows(conn_z) == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_generarea_d394_citeste_ambele_rute_si_e_valida(conn_z):
    from core import uc_tenants
    r1 = uc_tenants.horeca_import_amef(1, (_XML_AMEF % 35).encode(), {"uid": 1})
    with conn_z.cursor() as cur:   # importul scrie ciornă; contabilul o validează
        cur.execute("UPDATE inregistrari SET status='validata' WHERE id=%s", (r1["inregistrare_id"],))
    r2 = uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})
    with conn_z.cursor() as cur:   # [08.10.2026, R36] și Z-ul tastat intră ciornă; contabilul îl validează
        cur.execute("UPDATE inregistrari SET status='validata' WHERE id=%s", (r2["nota_id"],))
    xml, res = _d394.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=6))
    (o,) = _op2(xml)
    # 2 case (NUI distincte), 35 + 42 bonuri; total 2450 (AMEF) + 1321 (tastat) = 3771
    assert (o["nrAMEF"], o["nrBF"], o["total"]) == ("2", "77", "3771")
    duk = _duk()
    if duk is not None:
        v = duk.valideaza(xml, "d394", an=2026, luna=6, timeout=180)
        assert v.get("stare") == "valid", v.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_raport_z_validat_fara_rand_amef_face_d394_sa_refuze_numit(conn_z):
    # un raport scris înainte de decizie (sau pe altă cale) — fără casă și bonuri: refuz numit, nu op2 pe zero
    with conn_z.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) "
                    "VALUES ('2026-06-15','Z-8000000003-0001','vechi','horeca_z','validata') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s, 21, 100, 21)", (iid,))
    # MUTAȚIE: scos refuzul din genereaza -> D394 ar ieși cu op2 fără raportul ăsta
    with pytest.raises(ValueError) as e:
        _d394.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=6))
    assert (e.value.cod, e.value.rapoarte) == ("D394_Z_INCOMPLET", ["Z-8000000003-0001"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_a_doua_cale_recalculeaza_incasarile_din_tabelele_z(conn_z):
    from core import uc_tenants
    from core.d394_reconciliere import reconciliaza
    r2 = uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})
    with conn_z.cursor() as cur:   # [08.10.2026, R36] Z-ul tastat intră ciornă; validat
        cur.execute("UPDATE inregistrari SET status='validata' WHERE id=%s", (r2["nota_id"],))
    xml, res = _d394.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=6))
    assert reconciliaza(conn_z, Perioada(2026, luna=6), res)["divergente"] == []
    # MUTAȚIE (pe rezultat, nu pe cod): o rubrică op2 agregată greșit în generator -> calea a doua o numește
    res.informatii["nr_BF_i1"] += 1
    res.rezumat2[21]["tva_incasari_i1"] += 1
    div = reconciliaza(conn_z, Perioada(2026, luna=6), res)["divergente"]
    assert [(d["cota"], d["camp"], d["diferenta"]) for d in div] == [(0, "nr_BF_i1", 1), (21, "tva_incasari_i1", 1)]
