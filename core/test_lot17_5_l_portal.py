# -*- coding: utf-8 -*-
"""Lotul 17.5-L — portalul clientului, partea de server: AC146 (limita de 4 fotografii), AC148 (valori AI invalide), AC152 (TVA la data bonului),
AC169 (facturi deschise neînregistrate, disjuncte de cele validate), AC172 (mesajul clientului: tăiere, gol, limită), AC156/AC158 (refuzurile din
portal_bon / confirma / sterge, citite exact de client).

Temei AC152: cotele TVA valabile la data bonului vin din `common.cota` (Legea 141/2025: 21% / 11% de la 01.08.2025; înainte 19%, fără cotă redusă
unică — cele 9% / 5% istorice rămân numai în JSON-ul `tva`). Fără bază de date, în afară de testul AC169 (schemă efemeră, în tranzacție anulată).
"""
import contextlib
import datetime
import json
from decimal import Decimal as D

import pytest

from core import erori, repo_casa, repo_portal, repo_tenants, uc_portal
from core import ai_client
from core import uc_comun as _uc_comun
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura și ajutoarele ei
from core.test_lot13_portal_p1_cifre import _factura, _nota

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


class _Cursor:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn(_Cursor):
    def cursor(self, *a, **k):
        return _Cursor()


@pytest.fixture
def server(monkeypatch, tmp_path):
    """portal_bon și portal_solicitari_trimite fără bază: tenantul, AI-ul și scrierile sunt înlocuite; `scrise` păstrează ce s-ar fi scris."""
    scrise = {"bon": [], "mesaje": []}
    monkeypatch.setattr(_uc_comun, "_tenant_pentru_documente", lambda ctx, tid: {"id": 1, "schema_name": "ztest"})
    monkeypatch.setattr(_uc_comun, "_tenant_client", lambda ctx, tid: {"id": 1, "schema_name": "ztest"})
    monkeypatch.setattr(uc_portal.db, "get_conn", lambda *a, **k: _Conn())
    monkeypatch.setattr(repo_casa, "sterge_bonurile_extrase_vechi", lambda cur, schema: [])
    monkeypatch.setattr(repo_casa, "adauga_bon", lambda cur, schema, *a: scrise["bon"].append(a) or (7,))
    monkeypatch.setattr(repo_portal, "adauga_solicitare", lambda cur, tid, mesaj, uid: scrise["mesaje"].append(mesaj))
    monkeypatch.setattr(repo_tenants, "cabinetul_si_numele", lambda cur, tid: None)
    monkeypatch.setenv("ICONTA_BON_DIR", str(tmp_path))
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    return scrise


def _ai(monkeypatch, raspuns):
    monkeypatch.setattr(ai_client, "citeste_imagini", lambda imagini, prompt: raspuns if isinstance(raspuns, str) else json.dumps(raspuns))


def _bon(monkeypatch, n=1, **campuri):
    _ai(monkeypatch, {"tip": "bon", "comerciant": "X", "data": "2026-10-01", "total": 10.5, "tva": [], "orientare": 0, **campuri})
    return uc_portal.portal_bon([(PNG, "p%d.png" % i) for i in range(n)], None, {"uid": 1})


# ── AC146 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ac146_serverul_refuza_peste_patru_fotografii_fara_sa_taie_lista(server, monkeypatch):
    """Cinci imagini: refuz explicit, înaintea apelului AI (nu se citește nimic, nu se scrie nimic); patru trec. MUTAȚIE: `fisiere[:4]` readus
    -> a cincea ar fi tăiată în tăcere și nu mai apare refuzul."""
    apeluri = []
    monkeypatch.setattr(ai_client, "citeste_imagini", lambda imagini, prompt: apeluri.append(len(imagini)) or json.dumps({"tip": "bon", "total": 1}))
    with pytest.raises(erori.CerereGresita) as e:
        uc_portal.portal_bon([(PNG, "p%d.png" % i) for i in range(5)], None, {"uid": 1})
    assert e.value.detaliu == "Poți trimite cel mult 4 fotografii pentru același document."
    assert apeluri == [] and server["bon"] == []
    assert uc_portal.portal_bon([(PNG, "p%d.png" % i) for i in range(4)], None, {"uid": 1})["ok"] is True
    assert apeluri == [4]


# ── AC148 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("camp,valoare", [("total", "douăzeci"), ("total", [1]), ("total", {"a": 1}), ("total", "nan"), ("total", "inf"),
                                          ("orientare", "dreapta"), ("orientare", [90]), ("orientare", "9.5"),
                                          ("tva", "21"), ("tva", [{"cota": 21, "valoare": "mult"}]), ("tva", ["21"])])
def test_ac148_valorile_ai_invalide_sunt_refuz_controlat_fara_bon_partial(server, monkeypatch, camp, valoare):
    """Total, orientare sau TVA care nu sunt numere: DateInvalide cu mesajul clientului (nu 500) și niciun bon scris. MUTAȚIE: conversiile scoase
    din `try` -> ValueError / TypeError ies ca erori neprinse și pică."""
    with pytest.raises(erori.DateInvalide) as e:
        _bon(monkeypatch, **{camp: valoare})
    assert e.value.detaliu == "Nu s-a putut citi bonul. Încearcă o poză mai clară."
    assert server["bon"] == []


def test_ac148_un_raspuns_ai_care_nu_e_obiect_e_tot_refuz_controlat(server, monkeypatch):
    for text in ("[1, 2]", "42", "null", "nu e json"):
        _ai(monkeypatch, text)
        with pytest.raises(erori.DateInvalide) as e:
            uc_portal.portal_bon([(PNG, "p.png")], None, {"uid": 1})
        assert e.value.detaliu == "Nu s-a putut citi bonul. Încearcă o poză mai clară."
    assert server["bon"] == []


# ── AC152 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _tva(server):
    a = server["bon"][-1]   # (comerciant, cui, data, total, tva_11, tva_21, articole, tva, nr_imagini, complet, tip, numar, mentiuni, orientare)
    return a[4], a[5], json.loads(a[7])


def test_ac152_dupa_01_08_2025_cota_standard_e_21_si_cea_redusa_11(server, monkeypatch):
    r = _bon(monkeypatch, data="2025-08-01", tva=[{"cota": 21, "valoare": 1.82}, {"cota": 11, "valoare": 0.5}])
    assert _tva(server)[:2] == (0.5, 1.82) and r["avertismente"] == []


@pytest.mark.parametrize("data", ["2025-06-15", "2025-07-31"])
def test_ac152_inainte_de_01_08_2025_standardul_e_19_fara_cota_redusa_si_cu_avertisment(server, monkeypatch, data):
    """Bon din iunie / iulie 2025: «tva_21» = suma pe 19% (cota standard a datei), «tva_11» = 0 (cota redusă unică nu exista), cele 9% și 5% rămân
    în JSON-ul `tva`, nemutate în tva_11; cota redusă indisponibilă = avertismentul din comandă. MUTAȚIE: `cota` cerută fără `la_data` -> 21% azi -> pică."""
    tva = [{"cota": 19, "valoare": 3.0}, {"cota": 9, "valoare": 0.7}, {"cota": 5, "valoare": 0.1}]
    r = _bon(monkeypatch, data=data, tva=tva)
    t11, t21, in_json = _tva(server)
    assert (t11, t21) == (0.0, 3.0) and in_json == tva
    assert uc_portal.AVERT_COTE_TVA_INDISPONIBILE in r["avertismente"]
    assert r["avertismente"].count(uc_portal.AVERT_COTE_TVA_INDISPONIBILE) == 1


def test_ac152_data_lipsa_sau_invalida_pastreaza_ziua_de_azi(server, monkeypatch):
    for data in (None, "", "ieri", "2026-13-45"):
        r = _bon(monkeypatch, data=data, tva=[{"cota": 21, "valoare": 2.0}])
        assert _tva(server)[:2] == (0.0, 2.0)
        assert r["avertismente"] == []


def test_ac152_cota_nedefinita_la_data_bonului_se_spune_iar_cealalta_se_calculeaza_singura(server, monkeypatch):
    """Înainte de 2017 nici cota standard nu e cunoscută: tva_21 = 0, avertisment; cealaltă (redusă) nu inventează nimic."""
    r = _bon(monkeypatch, data="2010-05-05", tva=[{"cota": 19, "valoare": 3.0}])
    assert _tva(server)[:2] == (0.0, 0.0)
    assert uc_portal.AVERT_COTE_TVA_INDISPONIBILE in r["avertismente"]


def test_ac152_sumele_se_rotunjesc_in_decimal_half_up(server, monkeypatch):
    _bon(monkeypatch, data="2025-09-01", tva=[{"cota": 21, "valoare": 0.125}, {"cota": 21, "valoare": 0.125}, {"cota": 21, "valoare": "0.005"}])
    assert _tva(server)[1] == 0.26   # 0,255 -> 0,26 (ROUND_HALF_UP), nu 0,25 din round() în virgulă mobilă


# ── AC172 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class _Mesaj:
    def __init__(self, mesaj):
        self.mesaj = mesaj


@pytest.mark.parametrize("mesaj", ["", "   ", "\n\t  "])
def test_ac172_mesajul_gol_sau_numai_spatii_e_refuzat(server, mesaj):
    with pytest.raises(erori.CerereGresita) as e:
        uc_portal.portal_solicitari_trimite(_Mesaj(mesaj), None, {"uid": 1})
    assert e.value.detaliu == "Scrie solicitarea înainte de a o trimite."
    assert server["mesaje"] == []


def test_ac172_peste_4000_de_caractere_dupa_trim_e_refuzat_iar_4000_trece(server):
    with pytest.raises(erori.CerereGresita) as e:
        uc_portal.portal_solicitari_trimite(_Mesaj("a" * 4001), None, {"uid": 1})
    assert e.value.detaliu == "Mesajul are peste 4.000 de caractere. Scurtează-l."
    with pytest.raises(erori.CerereGresita):
        uc_portal.portal_solicitari_trimite(_Mesaj("  " + "a" * 4001 + "  "), None, {"uid": 1})
    uc_portal.portal_solicitari_trimite(_Mesaj("  " + "a" * 4000 + "  "), None, {"uid": 1})   # spațiile nu se numără
    assert server["mesaje"] == ["a" * 4000]


def test_ac172_mesajul_salvat_e_cel_normalizat(server):
    uc_portal.portal_solicitari_trimite(_Mesaj("  Salut \n"), None, {"uid": 1})
    assert server["mesaje"] == ["Salut"]


def test_ac172_modelul_comun_al_cabinetului_ramane_neatins():
    """SolicitareIn e comun cu răspunsul cabinetului: validarea clientului stă în use-case, nu în model (un mesaj gol al cabinetului NU se
    refuză aici). MUTAȚIE: un validator pe model ar refuza și mesajul de 4001 al cabinetului -> pică."""
    import main
    assert main.SolicitareIn(mesaj="").mesaj == "" and len(main.SolicitareIn(mesaj="a" * 5000).mesaj) == 5000


# ── AC156 / AC158 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ac156_refuzurile_portalului_sunt_scrise_pentru_client(server, monkeypatch):
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    with pytest.raises(erori.ServiciuIndisponibil) as e:
        uc_portal.portal_bon([(PNG, "p.png")], None, {"uid": 1})
    assert e.value.detaliu == "Serviciul AI nu e disponibil acum. Încearcă din nou peste puțin timp."
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    with pytest.raises(erori.CerereGresita) as e:
        uc_portal.portal_bon([(PNG + b"0" * 8_000_001, "mare.png")], None, {"uid": 1})
    assert e.value.detaliu == "Imaginea e prea mare. Dimensiunea maximă este 8 MB."
    _ai(monkeypatch, "nu e json")
    with pytest.raises(erori.DateInvalide) as e:
        uc_portal.portal_bon([(PNG, "p.png")], None, {"uid": 1})
    assert e.value.detaliu == "Nu s-a putut citi bonul. Încearcă o poză mai clară."
    with pytest.raises(erori.DateInvalide) as e:   # mesajul deja corect pentru fișier care nu e imagine rămâne cel citit de teste
        uc_portal.portal_bon([(b"text simplu", "nu_e.png")], None, {"uid": 1})
    assert "nu e o imagine" in e.value.detaliu


def test_ac156_bonul_inexistent_sau_deja_trimis_la_confirmare_si_la_stergere(server, monkeypatch):
    monkeypatch.setattr(repo_casa, "trece_bonul_la_de_verificat", lambda cur, schema, bon_id: False)
    monkeypatch.setattr(repo_casa, "sterge_bonul_extras", lambda cur, schema, bon_id: False)
    for functie in (uc_portal.portal_bon_confirma, uc_portal.portal_bon_sterge):
        with pytest.raises(erori.Inexistent) as e:
            functie(9, None, {"uid": 1})
        assert e.value.detaliu == "Bonul nu există sau a fost deja trimis."


def test_ac157_mesajul_modului_de_previzualizare_e_numai_in_romana():
    import re
    sursa = open("main.py", encoding="utf-8").read()
    assert "Previzualizare: doar vizualizare. Acțiunile sunt dezactivate în modul de previzualizare." in sursa
    assert not re.search(r"modul preview|Previzualizare — doar", sursa)


# ── AC169 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@DB
def test_ac169_neinregistratele_si_validatele_sunt_multimi_disjuncte_care_acopera_toate_deschise(conn):
    """F-A (nota validată), F-B (nota ciornă), F-C (fără notă), sold preluat (fără notă, intră la validate), F-E (EUR, validată): validate =
    {A, preluata, E}; neînregistrate = {B, C}; reuniunea = toate cele deschise, intersecția goală. MUTAȚIE: `CONDITIE_NOTA_NEVALIDATA` fără NOT ->
    intersecția nu mai e goală -> pică."""
    a = _factura(conn, "L169A", 1000, 1000)
    b = _factura(conn, "L169B", 500, 500)
    c = _factura(conn, "L169C", 250, 250)
    p = _factura(conn, "Sold L169", 2000, 2000, tip="preluata", scadenta=None)
    e = _factura(conn, "L169E", D("60.50"), D("323.64"), moneda="EUR")
    _nota(conn, a, "validata")
    _nota(conn, b, "ciorna")
    _nota(conn, e, "validata")
    with conn.cursor() as cur:
        validate = {f["id"] for f in repo_portal.facturi_deschise_validate(cur, "emisa")}
        neinreg = {f["id"] for f in repo_portal.facturi_deschise_nevalidate(cur, "emisa")}
        from core import repo_facturi as _rf
        toate = {f["id"] for f in _rf.de_incasat(cur, "emisa")}
    assert validate == {a, p, e} and neinreg == {b, c}, (validate, neinreg)
    assert not (validate & neinreg) and (validate | neinreg) == toate


def test_ac169_kpi_poarta_neinregistratele_separat_fara_sa_schimbe_totalul_validat(server, monkeypatch):
    """portal_kpi: «De plătit» rămâne cel din balanță (note validate); sub el, numărul și sumele pe monedă ale facturilor primite nevalidate."""
    from core import documente_api
    monkeypatch.setattr(documente_api, "balanta", lambda conn, schema, an, luna: [{"cont": "401", "denumire": "", "si_d": 0, "si_c": 0, "prec_d": 0, "prec_c": 0,
                                                                               "rul_d": 0, "rul_c": 3000, "tot_d": 0, "tot_c": 3000, "sf_d": 0, "sf_c": 3000}])
    monkeypatch.setattr(uc_portal, "_starea_lunilor", lambda conn, schema, luni: [{"luna": luni[0], "definitiva": False, "neverificate": 0}])
    validate = [{"moneda": "RON", "rest": D("3000"), "rest_lei": D("3000")}]
    nevalidate = [{"moneda": "RON", "rest": D("100"), "rest_lei": D("100")}, {"moneda": "EUR", "rest": D("20"), "rest_lei": D("100")}]
    monkeypatch.setattr(repo_portal, "facturi_deschise_validate", lambda cur, d: validate if d == "primita" else [])
    monkeypatch.setattr(repo_portal, "facturi_deschise_nevalidate", lambda cur, d: nevalidate if d == "primita" else [])
    k = uc_portal.portal_kpi(2099, 10, None, {"uid": 1})["kpi"]
    assert k["de_platit"] == 3000 and k["facturi_de_platit"]["nr"] == 1
    n = k["facturi_neinregistrate_de_platit"]
    assert n["nr"] == 2 and n["pe_moneda"] == [{"moneda": "RON", "suma": "100"}, {"moneda": "EUR", "suma": "20"}]
