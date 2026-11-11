# -*- coding: utf-8 -*-
"""[lotul 17.5-W, AC184 + AC185] Decontul care spune ce îi lipsește și Control fiscal care explică diferența (comanda 17.5-W, textele impuse de arhitect).

AC184: rapoartele Z (surse horeca_z / amef) cu nota în ciornă NU intră în decont (regula de calcul rămâne: numai Z validat); D300 și D394 le numesc ca
PRIM avertisment (`coada_api.avertisment_rapoarte_z`) și refuză depunerea cu RAPOARTE_Z_NEVALIDATE (`coada_api.blocaj_rapoarte_z`) pe cele patru
drumuri: pasul 2 (`uc_declaratii.blocaj_depunere`), intrarea în coadă (`uc_coada.coada_adauga`, ÎNAINTEA porții de balanță), rândul din «De depus»
(`lista_coada`) și marcarea ca depusă (`marcheaza_depusa`). Fereastra e fereastra decontului, nu a D406.
AC185: `control_incrucisat` pune pe constatările roșii 4427 / 4426 / 4423 / 4424 cheia `explicatie_ciorne` (număr și sumă de note în ciornă pe cont).
Schemă efemeră din tenant_template, perioade sintetice 2099, ROLLBACK la final."""
import contextlib
import json
import os
import types
from decimal import Decimal

import pytest

from core import coada_api, erori as _erori, uc_coada
from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_ciorne_decont_17_5_w"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _fixtura(tip_decont):
    c = _db.pool().getconn()
    with c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
        cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
        cur.execute("SET search_path TO %s, public" % _SCHEMA)
        cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                    "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA Z SRL','14399840','Str 1','Buc','B','5610',"
                    "'BCR','RO49RNCB0000000000000001','real',true,%s,'Pop','Ion','administrator')", (tip_decont,))
    return c


@contextlib.contextmanager
def _firma(tip_decont="L"):
    c = _fixtura(tip_decont)
    try:
        yield c
    finally:
        c.rollback()
        with c.cursor() as cur:
            cur.execute("RESET search_path")
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
        c.commit()
        _db.pool().putconn(c)


def _z(cur, data, numar, cote, status="ciorna", sursa="horeca_z"):
    """Raport Z: nota (`inregistrari`) cu defalcarea pe cote [(cota, baza, tva)] — gol = fără defalcare."""
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status, document_ref) VALUES (%s,%s,'Raport Z',%s,%s,%s) RETURNING id",
                (data, numar, sursa, status, numar))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'5311','707',100)", (nid,))
    for cota, baza, tva in cote:
        cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s,%s,%s,%s)", (nid, cota, baza, tva))
    return nid


def _nota_cont(cur, data, status, debit, credit, suma):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES (%s,'N','t',%s) RETURNING id", (data, status))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, debit, credit, suma))
    return nid


def _rapoarte(c, de_la, pana_la):
    with c.cursor() as cur:
        return coada_api.rapoarte_z_in_ciorna(cur, None, de_la, pana_la)


def _doua_rapoarte(cur):
    _z(cur, "2099-10-21", "Z-8000000001-0043", [(21, 100, "21.00")])
    _z(cur, "2099-10-20", "Z-8000000001-0042", [(21, 100, "21.00"), (11, 100, "10.90")])   # defalcarea, în ordinea inversă a cotei


# ── (i) textele pentru 2 rapoarte și pentru 1 raport ─────────────────────────────────────────────────────────────────────────────────────────
def test_avertismentul_cu_doua_rapoarte_e_textul_impus_si_rapoartele_stau_in_ordinea_datei():
    with _firma() as c:
        with c.cursor() as cur:
            _doua_rapoarte(cur)
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    assert coada_api.avertisment_rapoarte_z(z) == (
        "Din decont lipsește TVA din rapoarte Z în ciornă: 2 rapoarte Z nevalidate nu intră în calcul până la validare — "
        "Z-8000000001-0042 din 20.10.2099 (TVA 11%: 10,90 lei; TVA 21%: 21,00 lei); Z-8000000001-0043 din 21.10.2099 (TVA 21%: 21,00 lei). "
        "TVA colectată lipsă din decont: 52,90 lei (11%: 10,90 lei; 21%: 42,00 lei). Validează-le în Registrul jurnal, apoi generează din nou.")


def test_refuzul_cu_doua_rapoarte_are_textul_cu_lista_si_textul_de_langa_butoane():
    with _firma() as c:
        with c.cursor() as cur:
            _doua_rapoarte(cur)
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    r = coada_api.blocaj_rapoarte_z_din(z)
    assert (r["ok"], r["cod"]) == (False, "RAPOARTE_Z_NEVALIDATE")
    assert r["mesaj"] == ("Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z în ciornă "
                          "(Z-8000000001-0042 din 20.10.2099; Z-8000000001-0043 din 21.10.2099), în total 52,90 lei. "
                          "Validează-le în Registrul jurnal, apoi generează din nou.")
    assert r["mesaj_langa_note"] == ("Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z în ciornă, "
                                     "în total 52,90 lei. Validează-le în Registrul jurnal, apoi generează din nou.")
    assert [(n["data"], n["eticheta"].startswith("nota "), n["eticheta"].split(" — ")[1]) for n in r["note"]] == [
        ("2099-10-20", True, "Z-8000000001-0042, TVA 31,90 lei"), ("2099-10-21", True, "Z-8000000001-0043, TVA 21,00 lei")]


def test_cu_un_singur_raport_textele_sunt_la_singular():
    with _firma() as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-21", "Z-8000000001-0043", [(21, 100, "21.00")])
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    assert coada_api.avertisment_rapoarte_z(z) == (
        "Din decont lipsește TVA din rapoarte Z în ciornă: 1 raport Z nevalidat nu intră în calcul până la validare — "
        "Z-8000000001-0043 din 21.10.2099 (TVA 21%: 21,00 lei). TVA colectată lipsă din decont: 21,00 lei (21%: 21,00 lei). "
        "Validează-l în Registrul jurnal, apoi generează din nou.")
    assert coada_api.blocaj_rapoarte_z_din(z)["mesaj"] == (
        "Declarația nu se depune până la validarea raportului Z: din decont lipsește TVA din 1 raport Z în ciornă "
        "(Z-8000000001-0043 din 21.10.2099), în total 21,00 lei. Validează-l în Registrul jurnal, apoi generează din nou.")


# ── (ii) raport fără defalcare; (vi) total 0,00 lei ──────────────────────────────────────────────────────────────────────────────────────────
def test_raport_fara_defalcare_se_numeste_intra_in_numar_dar_nu_in_total():
    with _firma() as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-20", "Z-8000000001-0042", [])
            _z(cur, "2099-10-21", "Z-8000000001-0043", [(21, 100, "21.00")])
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    a = coada_api.avertisment_rapoarte_z(z)
    assert ("2 rapoarte Z nevalidate nu intră în calcul până la validare — Z-8000000001-0042 din 20.10.2099 "
            "(fără defalcare pe cote: TVA-ul lui nu se cunoaște); Z-8000000001-0043 din 21.10.2099 (TVA 21%: 21,00 lei). "
            "TVA colectată lipsă din decont: 21,00 lei (21%: 21,00 lei).") in a
    r = coada_api.blocaj_rapoarte_z_din(z)
    assert "din 2 rapoarte Z în ciornă (Z-8000000001-0042 din 20.10.2099; Z-8000000001-0043 din 21.10.2099), în total 21,00 lei." in r["mesaj"]
    assert r["note"][0]["eticheta"].endswith("— Z-8000000001-0042") and "TVA" not in r["note"][0]["eticheta"]   # eticheta fără TVA: fără defalcare


def test_cand_niciun_raport_nu_are_defalcare_totalul_lipsa_se_omite():
    with _firma() as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-20", "Z-8000000001-0042", [])
            _z(cur, "2099-10-21", "Z-8000000001-0043", [])
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    assert "TVA colectată lipsă" not in coada_api.avertisment_rapoarte_z(z)
    assert coada_api.avertisment_rapoarte_z(z).endswith("Validează-le în Registrul jurnal, apoi generează din nou.")
    assert coada_api.blocaj_rapoarte_z_din(z)["mesaj"] == (
        "Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z în ciornă "
        "(Z-8000000001-0042 din 20.10.2099; Z-8000000001-0043 din 21.10.2099). Validează-le în Registrul jurnal, apoi generează din nou.")
    assert coada_api.blocaj_rapoarte_z_din(z)["mesaj_langa_note"] == (
        "Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z în ciornă. "
        "Validează-le în Registrul jurnal, apoi generează din nou.")


# ── (iii) niciun raport în ciornă = nici avertisment, nici refuz ──────────────────────────────────────────────────────────────────────────────
def test_fara_rapoarte_in_ciorna_nu_e_nici_avertisment_nici_refuz_iar_raportul_validat_nu_conteaza():
    with _firma() as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-20", "Z-8000000001-0042", [(21, 100, "21.00")], status="validata")
            _z(cur, "2099-11-02", "Z-8000000001-0050", [(21, 100, "21.00")])   # în ciornă, dar în luna următoare
            _nota_cont(cur, "2099-10-22", "ciorna", "5311", "707", 50)         # ciornă care nu e raport Z
        assert _rapoarte(c, "2099-10-01", "2099-11-01") == []
        with c.cursor() as cur:
            assert coada_api.avertisment_rapoarte_z([]) is None and coada_api.blocaj_rapoarte_z_din([]) is None
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, 10, None) is None
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d394", 2099, 10, None) is None


# ── (iv) sumele pe cote, în ordinea crescătoare ──────────────────────────────────────────────────────────────────────────────────────────────
def test_sumele_pe_cote_sunt_in_ordinea_crescatoare_a_cotei_inclusiv_0_la_suta():
    with _firma() as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-20", "Z-8000000001-0042", [(21, 100, "21.00"), (0, 50, "0.00"), (11, 100, "10.90")])
            _z(cur, "2099-10-21", "Z-8000000001-0043", [(11, 100, "11.10"), (21, 100, "1.00")])
        z = _rapoarte(c, "2099-10-01", "2099-11-01")
    a = coada_api.avertisment_rapoarte_z(z)
    assert "(TVA 0%: 0,00 lei; TVA 11%: 10,90 lei; TVA 21%: 21,00 lei)" in a
    assert "TVA colectată lipsă din decont: 44,00 lei (0%: 0,00 lei; 11%: 22,00 lei; 21%: 22,00 lei)." in a


# ── (v) AC185: numărul și suma pe cont, forma «niciuna» ──────────────────────────────────────────────────────────────────────────────────────
def test_explicatia_ciornelor_numara_notele_o_singura_data_in_sensul_comparat_si_spune_niciuna():
    from core import control_incrucisat as ci
    with _firma() as c:
        with c.cursor() as cur:
            _nota_cont(cur, "2099-10-05", "ciorna", "4111", "4427", 100)
            n2 = _nota_cont(cur, "2099-10-06", "ciorna", "4111", "4427", 40)
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'4111','4427',2.50)", (n2,))   # a doua linie, aceeași notă
            _nota_cont(cur, "2099-10-07", "validata", "4111", "4427", 999)     # validată: nu se numără
            _nota_cont(cur, "2099-11-01", "ciorna", "4111", "4427", 999)       # în afara ferestrei
            _nota_cont(cur, "2099-10-08", "ciorna", "4426", "401", 70)         # 4426 pe debit
            _nota_cont(cur, "2099-10-09", "ciorna", "4427", "4111", 5)         # 4427 pe DEBIT: nu e sensul comparat al lui 4427
        cs = [{"stare": "rosu", "cont": k, "diferenta": Decimal("1")} for k in ("4427", "4426", "4423", "4424")] + [{"stare": "verde", "cont": "4427"}]
        out = ci.ciorne_care_explica(c, _SCHEMA, "2099-10-01", "2099-11-01", cs)
    ex = {x["cont"]: x.get("explicatie_ciorne") for x in out[:4]}
    assert ex["4427"] == ("Note în ciornă pe contul 4427 în perioadă: 2, cu suma de 142,50 lei. Balanța cuprinde numai note validate, deci diferența "
                          "poate veni din ele; validează-le și reia verificarea.")
    assert ex["4426"].startswith("Note în ciornă pe contul 4426 în perioadă: 1, cu suma de 70,00 lei. ") and "validează-o" in ex["4426"]
    assert ex["4423"] == "Note în ciornă pe contul 4423 în perioadă: niciuna. Diferența nu vine din note nevalidate."
    assert ex["4424"] == "Note în ciornă pe contul 4424 în perioadă: niciuna. Diferența nu vine din note nevalidate."
    assert "explicatie_ciorne" not in out[4]   # constatarea verde nu primește explicație
    assert "ciorne" in out[0] and "ciorne" not in out[2]   # cheia veche rămâne numai la 4427 / 4426


def test_constatarile_rezultatului_decontului_poarta_contul():
    from core import control_incrucisat as ci
    rez = ci.compara_tva({"R17_2": 0, "R27_2": 0, "R41_2": 100, "R42_2": 50}, {"4423": {"credit": 0}, "4424": {"debit": 0}}, 2099, 10)
    assert {c["cont"] for c in rez if c["eticheta"].startswith("TVA de ")} >= {"4423", "4424"}


# ── (vii) fereastra decontului, nu a D406 ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_decont_semestrial_numeste_raportul_din_alt_trimestru_al_semestrului():
    with _firma("S") as c:
        with c.cursor() as cur:
            _z(cur, "2099-02-10", "Z-8000000001-0007", [(21, 100, "21.00")])   # T1, iar ancora 6 are fereastra D406 = T2
            r = coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, 6, None)
            assert r and [n["data"] for n in r["note"]] == ["2099-02-10"]
            assert "Z-8000000001-0007 din 10.02.2099" in r["mesaj"]
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d394", 2099, 6, None)["cod"] == "RAPOARTE_Z_NEVALIDATE"
    with _firma("L") as c:
        with c.cursor() as cur:
            _z(cur, "2099-02-10", "Z-8000000001-0007", [(21, 100, "21.00")])
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, 6, None) is None   # lunar: iunie nu cuprinde februarie
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, 2, None)["cod"] == "RAPOARTE_Z_NEVALIDATE"


def test_decont_trimestral_ia_trimestrul_declaratiei_si_alt_tip_de_declaratie_nu_e_refuzat():
    with _firma("T") as c:
        with c.cursor() as cur:
            _z(cur, "2099-04-10", "Z-8000000001-0007", [(21, 100, "21.00")])
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, None, 2)["cod"] == "RAPOARTE_Z_NEVALIDATE"   # trimestrul 2 = ancora 6
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, None, 3) is None
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d390", 2099, 4, None) is None   # numai D300 și D394
            assert coada_api.blocaj_declaratie(cur, _SCHEMA, "d300", 2099, 4, None)["cod"] == "RAPOARTE_Z_NEVALIDATE"   # pasul 2 și «De depus»
            assert coada_api.blocaj_declaratie(cur, _SCHEMA, "d301", 2099, 4, None) is None


def test_firma_fara_tip_decont_nu_primeste_refuz_si_nici_exceptie():
    with _firma(None) as c:
        with c.cursor() as cur:
            _z(cur, "2099-10-10", "Z-8000000001-0007", [(21, 100, "21.00")])
            assert coada_api.blocaj_rapoarte_z(cur, _SCHEMA, "d300", 2099, 10, None) is None
            assert coada_api.blocaj_declaratie(cur, _SCHEMA, "d394", 2099, 10, None) is None
            assert coada_api.avertisment_rapoarte_z_decont(c, _SCHEMA, types.SimpleNamespace(an=2099, luna=10)) is None


# ── generatoarele: avertismentul e PRIMUL; regula de calcul rămâne ──────────────────────────────────────────────────────────────────────────
def test_avertismentul_din_generator_e_primul_si_calculul_nu_se_schimba():
    from core import d300 as _d300
    from core.common import Perioada
    with _firma() as c:
        with c.cursor() as cur:
            _doua_rapoarte(cur)
        az = coada_api.avertisment_rapoarte_z_decont(c, _SCHEMA, Perioada(2099, luna=10))
        assert az and az.startswith("Din decont lipsește TVA din rapoarte Z în ciornă: 2 rapoarte Z nevalidate")
        prof, facturi = _d300.pull(c, _SCHEMA, Perioada(2099, luna=10))
        assert not [f for f in facturi if f.get("raport_z")], "un raport Z în ciornă nu intră în decont"
    import inspect
    for modul in ("d300", "d394"):
        src = inspect.getsource(__import__("core." + modul, fromlist=["genereaza"]).genereaza)
        assert "avertisment_rapoarte_z_decont" in src and "avertismente.insert(0," in src, modul


# ── cele patru drumuri ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def rollback(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


class _Cerere:
    def __init__(self, **k):
        self.__dict__.update(k)

    def model_dump(self, exclude_none=True):
        return {k: v for k, v in self.__dict__.items() if v is not None}


class _Balanta(Exception):
    pass


def _pregateste_coada(monkeypatch, c):
    from core import declaratii_api, uc_comun, uc_declaratii
    proxy = _FaraCommit(c)
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda *a, **k: True)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCHEMA)
    monkeypatch.setattr(uc_declaratii, "aduce_localitati_parteneri", lambda *a, **k: None)
    monkeypatch.setattr(uc_declaratii, "poarta_cererii", lambda *a, **k: None)
    monkeypatch.setattr(uc_coada.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(declaratii_api, "genereaza", lambda *a, **k: ("<x/>", types.SimpleNamespace(avertismente=[], note_rezultat=[])))
    monkeypatch.setattr(coada_api, "randuri_din_res", lambda res: None)

    def _balanta(*a, **k):
        raise _Balanta()
    monkeypatch.setattr(uc_coada, "poarta_tva_balanta", _balanta)


@pytest.mark.parametrize("tip", ["d300", "d394"])
def test_intrarea_in_coada_refuza_rapoartele_z_inaintea_portii_de_balanta(monkeypatch, tip):
    with _firma() as c:
        _pregateste_coada(monkeypatch, c)
        date = _Cerere(tenant_id=-1, tip=tip, an=2099, luna=10, trim=None)
        with c.cursor() as cur:
            _doua_rapoarte(cur)
        with pytest.raises(_erori.DateInvalide) as e:
            uc_coada.coada_adauga(date, {})
        refuz = e.value.args[0]
        assert refuz["cod"] == "RAPOARTE_Z_NEVALIDATE" and "mesaj_langa_note" in refuz and len(refuz["note"]) == 2
        # contraproba: după validare refuzul dispare și se ajunge la poarta de balanță (ordinea: Z înainte, balanța după)
        with c.cursor() as cur:
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE sursa = 'horeca_z'")
        with pytest.raises(_Balanta):
            uc_coada.coada_adauga(date, {})


def test_rand_din_de_depus_are_refuzul_numai_cand_e_activ_iar_depunerea_il_refuza(monkeypatch):
    import functools
    import datetime as _dt
    with _firma() as c:
        with c.cursor() as cur:
            _doua_rapoarte(cur)
            cur.execute("INSERT INTO public.accounting_firms (nume, patru_ochi_activ) VALUES ('ZTEST 17.5-W', false) RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ, poate_valida, poate_depune) "
                        "VALUES ('ztest_175w@invalid','x','ZTest','angajat',%s,true,true,true) RETURNING id", (fid,))
            uid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s,'ZT 17.5-W',%s) RETURNING id", (_SCHEMA, fid))
            tid = cur.fetchone()[0]
            surse = {"de_la": "2099-10-01", "pana_la": "2099-11-01"}
            surse["amprenta"] = coada_api.amprenta_surse(cur, _SCHEMA, surse["de_la"], surse["pana_la"])   # nedepășită: aceleași documente
            ids = {}
            for stare in ("la_senior", "depusa"):
                # fixtura-sintetica-ok: cabinet și tenant create în tranzacție + rollback; perioada sintetică 2099
                cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload, creat_de, creat_de_id) "
                            "VALUES (%s,%s,'d300','2099-10-25',%s,%s,%s,%s) RETURNING id",
                            (fid, tid, stare, json.dumps({"xml": "<x/>", "_an": 2099, "_luna": 10, "_surse": surse}), str(uid), uid))
                ids[stare] = cur.fetchone()[0]
        monkeypatch.setattr(coada_api, "perioada_neincheiata", functools.partial(coada_api.perioada_neincheiata, azi=_dt.date(2100, 1, 1)))
        rand = {x["id"]: x for x in coada_api.lista_coada(c, fid)}
        assert rand[ids["la_senior"]]["blocaj_depunere"].startswith("Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z")
        assert "Z-8000000001-0042 din 20.10.2099; Z-8000000001-0043 din 21.10.2099" in rand[ids["la_senior"]]["blocaj_depunere"]   # textul cu listă
        assert rand[ids["la_senior"]]["gata_de_depus"] is False
        assert not rand[ids["depusa"]]["blocaj_depunere"]   # rând inactiv: fără refuz Z
        coada_api.scrie_verdict(c, ids["la_senior"], {"stare": "valid", "erori": ""}, "test-validator", "<x/>")
        ap = coada_api.aproba(c, ids["la_senior"], "ztest", aprobat_de_id=uid)
        assert ap.get("ok", True) is not False, ap
        r = coada_api.marcheaza_depusa(c, ids["la_senior"], depus_de="ztest", depus_de_id=uid)
        assert r["ok"] is False and r["cod"] == "RAPOARTE_Z_NEVALIDATE" and len(r["note"]) == 2, r
        with c.cursor() as cur:
            cur.execute("SELECT stare FROM public.declaratii_coada WHERE id=%s", (ids["la_senior"],))
            assert cur.fetchone()[0] == "aprobata"   # nimic marcat


def test_pasul_2_da_refuzul_prin_blocaj_depunere_si_celelalte_tipuri_raman_ca_inainte():
    from core import uc_declaratii
    with _firma() as c:
        with c.cursor() as cur:
            _doua_rapoarte(cur)
        r = uc_declaratii.blocaj_depunere(c, _SCHEMA, "d300", {"an": 2099, "luna": 10})
        assert r["cod"] == "RAPOARTE_Z_NEVALIDATE" and r["mesaj_langa_note"] and len(r["note"]) == 2
        assert uc_declaratii.blocaj_depunere(c, _SCHEMA, "d394", {"an": 2099, "luna": 10})["cod"] == "RAPOARTE_Z_NEVALIDATE"
        assert uc_declaratii.blocaj_depunere(c, _SCHEMA, "d112", {"an": 2099, "luna": 10}) is None
    assert "d300" not in coada_api.DECLARATII_DIN_EVIDENTA and "d394" not in coada_api.DECLARATII_DIN_EVIDENTA   # poarta lor rămâne balanța (R36)
