# -*- coding: utf-8 -*-
"""GARD — TVA-ul colectat din rapoartele Z intră în decontul D300 (lot 19 pct.4b, 02.10.2026).

Defectul: decontul se construia NUMAI din facturi. Rapoartele Z (import AMEF și ruta tastată) scriau doar nota
contabilă (5311/5125 = 707, 707 = 4427), fără defalcare pe cote — deci TVA-ul colectat pe bon fiscal ajungea în
4427, dar nu în rd.9/10. Reparația: ambele căi scriu și `rapoarte_z_cote` (baza + TVA pe cotă), `d300.pull` le
aduce ca livrări pe cotă, iar calea a doua (reconcilierea) le citește cu SQL propriu.

Temei: CF art.282 alin.(1) — „Exigibilitatea taxei intervine la data la care are loc faptul generator.”; instrucțiunile
D300 (OPANAF 174/2026) rd.9/10 — „se înscriu informațiile preluate din jurnalul de vânzări pentru operațiuni a căror
exigibilitate intervine în perioada de raportare, privind baza de impozitare și taxa pe valoarea adăugată colectată
pentru livrările de bunuri/prestările de servicii taxabile cu cota de 21%” (respectiv 11%).

Probele trec prin CODUL REAL al celor două rute (`uc_tenants.horeca_import_amef` / `horeca_raport_z`), pe o schemă
efemeră din tenant_template, în tranzacție anulată: conexiunea e învelită ca `commit()` să nu închidă tranzacția.
"""
import contextlib
from decimal import Decimal, ROUND_HALF_UP

import pytest

from core import d300 as _d300
from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "tenant_test_z300"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    """Conexiunea fixturii, cu `commit()` neutralizat: ruta comite, testul anulează."""

    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


# Raportul Z AMEF din specificație (OPANAF 146/2018 sect. II.7), același ca în amef_import._test: 2 cote.
_XML_AMEF = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<msj idM="8000000001202607041930120042">'
             '<rB idR="8000000001202607041930120042" nrAv="0" nrB="35" totB="2450.00"'
             ' nrBC="2" totBC="300.00" nrA="0" totA="0" nrR="0" totR="0" nrM="0" totM="0"'
             ' totTva="399.14" totTvaC="0" totTaxes="0" totTaxe="0" totNet="0"'
             ' sume_serv_in="0" sume_serv_out="0" monRef="RON">'
             '<pl tipP="1" valPl="1450.00" monPl="RON"/>'
             '<pl tipP="3" valPl="1000.00" monPl="RON"/>'
             '<coteZ cota="21" valOp="2100.00" tva="364.46"/>'
             '<coteZ cota="11" valOp="350.00" tva="34.68"/>'
             '</rB></msj>')


class _Z:
    data = "2026-07-10"
    nui = "8000000002"
    nr_raport = "0007"
    nr_bonuri = 42          # [D394 op2 Î1, decizia B] obligatoriu pe ruta tastată
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
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare,declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'HORECA Z SRL','14399840','Str Test 1','Bucuresti','B','5610','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR')")
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_cere_luna_deschisa", lambda *a, **k: None)
            yield conn
        finally:
            conn.rollback()


def _q(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _importa_ambele(conn):
    from core import uc_tenants
    r1 = uc_tenants.horeca_import_amef(1, _XML_AMEF.encode(), {"uid": 1})
    # ruta AMEF scrie CIORNĂ („de verificat cu Z tipărit"); contabilul o validează -> abia atunci intră în decont
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status='validata' WHERE id=%s", (r1["inregistrare_id"],))
    r2 = uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})
    return r1, r2


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tva_din_rapoartele_z_intra_in_rd9_rd10_si_reconcilierea_tine(conn_z):
    _importa_ambele(conn_z)
    xml, res = _d300.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=7))
    # AMEF: 21% valOp 2100 / tva 364,46 -> baza 1735,54; 11% valOp 350 / tva 34,68 -> baza 315,32 (bazele din Z)
    # tastat: 21% 1210 cu TVA -> TVA 1210*21/121 = 210,00, baza 1000,00; 11% 111 -> TVA 11,00, baza 100,00
    # CF art.282 alin.(1) + instrucțiuni D300 rd.9 (21%) / rd.10 (11%): livrările din jurnalul de vânzări, pe cotă
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (_q("2735.54"), _q("574.46")) == (2736, 574)
    assert (res.R.get("R10_1"), res.R.get("R10_2")) == (_q("415.32"), _q("45.68")) == (415, 46)
    assert res.tva_de_plata == 574 + 46
    # a doua cale (SQL propriu pe rapoarte_z_cote) confirmă aceleași totaluri — genereaza n-ar fi trecut altfel
    from core.d300_reconciliere import reconciliaza
    assert reconciliaza(conn_z, Perioada(2026, luna=7), res)["divergente"] == []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ambele_rute_scriu_defalcarea_pe_cote(conn_z):
    r1, r2 = _importa_ambele(conn_z)
    with conn_z.cursor() as cur:
        cur.execute("SELECT inregistrare_id, cota, baza, tva FROM rapoarte_z_cote ORDER BY inregistrare_id, cota")
        rows = [(i, Decimal(c), Decimal(b), Decimal(t)) for i, c, b, t in cur.fetchall()]
    a, z = r1["inregistrare_id"], r2["nota_id"]
    assert rows == [(a, Decimal(11), Decimal("315.32"), Decimal("34.68")), (a, Decimal(21), Decimal("1735.54"), Decimal("364.46")),
                    (z, Decimal(11), Decimal("100.00"), Decimal("11.00")), (z, Decimal(21), Decimal("1000.00"), Decimal("210.00"))]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_raport_z_ciorna_nu_intra_in_decont(conn_z):
    from core import uc_tenants
    uc_tenants.horeca_import_amef(1, _XML_AMEF.encode(), {"uid": 1})     # rămâne ciornă
    _xml, res = _d300.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=7))
    assert "R9_1" not in res.R and "R10_1" not in res.R, "o notă Z nevalidată nu e încă în evidență"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_raport_z_validat_fara_defalcare_e_REFUZAT_numit(conn_z):
    """O notă Z validată fără defalcare (ex. scrisă înainte de reparație) nu se sare tăcut: decontul se refuză și o numește."""
    with conn_z.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) "
                    "VALUES ('2026-07-15','Z-8000000003-0001','vechi','horeca_z','validata') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'707','4427',21)", (iid,))
    with pytest.raises(ValueError):
        _d300.genereaza(conn_z, _SCHEMA, Perioada(2026, luna=7))
    # motivul, ca dată: calculul numește nota fără defalcare (refuzul din genereaza e construit din lista asta)
    prof, facturi = _d300.pull(conn_z, _SCHEMA, Perioada(2026, luna=7))
    assert _d300.calcul_d300(prof, Perioada(2026, luna=7), facturi).z_fara_cote == ["Z-8000000003-0001"]


def test_calcul_pur_cota_z_fara_rand_e_semnalata_si_zero_nu_e_colectat():
    prof = {"cui": "14399840", "nume": "X", "banca": "BCR", "iban": "RO1", "caen": "5610", "tip_decont": "L", "pro_rata": 100}
    z = [{"raport_z": True, "id": 1, "numar": "Z-1", "cota": Decimal("5.00"), "baza": Decimal("100"), "tva": Decimal("5")},
         {"raport_z": True, "id": 1, "numar": "Z-1", "cota": Decimal("0.00"), "baza": Decimal("40"), "tva": Decimal("0")},
         {"raport_z": True, "id": 2, "numar": "Z-2", "cota": Decimal("21.00"), "baza": Decimal("1000"), "tva": Decimal("210")}]
    res = _d300.calcul_d300(prof, Perioada(2026, luna=7), z)
    fara_5 = _d300.calcul_d300(prof, Perioada(2026, luna=7), [x for x in z if x["cota"] != Decimal("5.00")])
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (1000, 210)          # instrucțiuni D300 rd.9: cota 21%
    assert res.R.get("R10_1") is None and res.R.get("R11_1") is None      # 5% nu are rând automat: nu se inventează unul
    # cota fără rând e SEMNALATĂ (un avertisment în plus față de același calcul fără ea), nu pierdută tăcut
    assert len(res.avertismente) == len(fara_5.avertismente) + 1


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_notele_raportului_z_poarta_raportul_ca_document(conn_z):
    """[05.10.2026, comanda Costin pct.6] „Notele automate poartă documentul sursă.” Raportul Z e documentul notei lui, pe
    ambele rute (Registrul-jurnal col.3: felul, numărul și data). MUTAȚIE: `document_ref` netransmis din `horeca_raport_z`
    -> None -> pică."""
    r1, r2 = _importa_ambele(conn_z)
    with conn_z.cursor() as cur:
        cur.execute("SELECT sursa, document_ref FROM inregistrari WHERE id IN (%s, %s) ORDER BY id", (r1["inregistrare_id"], r2["nota_id"]))
        rez = cur.fetchall()
    assert rez[1] == ("horeca_z", "Raport Z nr 0007 din 10.07.2026 (casa 8000000002)")
    import re
    assert rez[0][0] == "amef" and re.fullmatch(r"Raport Z nr \S+ din \d\d\.\d\d\.\d{4} \(AMEF \d+\)", rez[0][1]), rez[0]
