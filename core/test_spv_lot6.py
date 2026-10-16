# -*- coding: utf-8 -*-
"""Lotul 6 (comanda Costin 16.10.2026, verbatim în DECIZII „Lotul 6, comanda 1” și „a treia completare”): SPV — 273 (facturile primite:
starea, „Verifică acum”, importul XML UBL, câmpurile de completat), 275b (starea în SPV a facturii emise, cu termenul), 289a (emitentul
certificatului), pct.2b (prima citire a unei firme cuprinde 60 de zile).

Temei: OUG 120/2021 art.10 alin.(7) (anaf_surse/oug_120_2021.txt): „Termenul-limită pentru transmiterea facturilor [...] este de 5 zile
lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la
art. 319 alin. (16) [...]. Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71”. Ghidul MF al
codurilor e-Factura v2.9, cap.3 (anaf_surse/mf_ghid_coduri_facturi_efactura_v2_9.txt): categoria „AE” = taxare inversă (art.331).
ARHITECTURA_SPV.md (18.07.2026, pe token real): refuzul de drept pe CIF vine ca HTTP 200 + „Nu aveti drept in SPV pentru CIF=…”; JWT-ul
are `issuer` (emitentul certificatului), nu titularul.
"""
import base64
import datetime
import io
import json

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_spv_lot6"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


# ── 275b: termenul de transmitere ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_275_termenul_spv_5_zile_lucratoare_fara_sarbatori():
    from core.facturi_api import termen_spv
    d = datetime.date
    assert termen_spv(d(2026, 10, 16)) == d(2026, 10, 23)                    # vineri -> vinerea următoare
    assert termen_spv(d(2026, 11, 27)) == d(2026, 12, 8)                     # 30.11 și 01.12 sunt sărbători legale (Codul muncii art.139)
    assert termen_spv(d(2026, 10, 16), d(2026, 8, 1)) == d(2026, 9, 22)      # emisă târziu: 15.09 (art.319 alin.(16)) + 5 zile lucrătoare


# ── 273c: categoria TVA din XML ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_273_parserul_citeste_categoria_si_taxarea_inversa():
    from core import efactura_import as efi
    from core.test_a12b_destinatie_linie import _UBL
    f = efi.parseaza_xml(_UBL.replace("<cbc:Percent>21</cbc:Percent>", "<cbc:ID>AE</cbc:ID><cbc:Percent>0</cbc:Percent>", 1), "RO14399840")
    assert [l["categorie_tva"] for l in f["linii"]] == ["AE", None] and f["taxare_inversa"] is True
    assert efi.parseaza_xml(_UBL, "RO14399840")["taxare_inversa"] is False


# ── 289a: emitentul certificatului, din tokenul stocat ─────────────────────────────────────────────────────────────────────────────
def test_289_emitentul_vine_din_claim_ul_issuer():
    from core import spv_conector as sc
    corp = base64.urlsafe_b64encode(json.dumps({"issuer": "DigiSign", "serial": "20:05"}).encode()).decode().rstrip("=")
    assert sc.emitent_certificat(sc.cripteaza("x.%s.y" % corp)) == "DigiSign"
    assert sc.emitent_certificat(sc.cripteaza("neinteligibil")) is None


# ── pct.2b + 273a: citirea unei firme ─────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def schema_firma():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui) VALUES (1, 'FISCALOS TEST', 'RO55229657')" % _SCH)
        c.commit()
    yield _SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def test_prima_citire_cuprinde_60_de_zile_iar_refuzul_de_drept_se_tine_minte(schema_firma, monkeypatch):
    """MUTAȚIE: `ZILE if _citire_anterioara(...) else ZILE_PRIMA_CITIRE` -> `ZILE` -> prima citire cere 3 zile -> pică."""
    from core import spv_receive as sr
    citiri, inreg = [], []
    monkeypatch.setattr(sr.spv_conector, "principal_pentru_schema", lambda c, s: "P")
    monkeypatch.setattr(sr.spv_conector, "ia_token_activ", lambda c, p: {"id": 7})
    stare = {"ultima_reusita": None}
    monkeypatch.setattr(sr, "_citire_anterioara", lambda c, t, cif: stare["ultima_reusita"])
    monkeypatch.setattr(sr, "_inregistreaza_citire", lambda c, t, cif, err, n: inreg.append((t, cif, err, n)))

    def lista(principal, cif, mediu, zile=3, filtru="P"):
        citiri.append((cif, zile, filtru))
        return [], "Nu aveti drept in SPV pentru CIF=%s" % cif
    monkeypatch.setattr(sr.efs, "lista_mesaje", lista)
    r = sr.citeste_firma(schema_firma)
    assert citiri == [("55229657", 60, "P")] and "Nu aveti drept in SPV" in r["eroare"], (citiri, r)   # textul ANAF, trecut neschimbat
    assert inreg == [(7, "55229657", "Nu aveti drept in SPV pentru CIF=55229657", 0)]
    stare["ultima_reusita"] = datetime.datetime.now()
    monkeypatch.setattr(sr.efs, "lista_mesaje", lambda *a, **k: (citiri.append(k["zile"]), ([], "Nu exista mesaje in ultimele 3 zile"))[1])
    r = sr.citeste_firma(schema_firma)
    assert citiri[-1] == sr.ZILE and r["eroare"] is None and inreg[-1][2] is None, "„Nu exista mesaje” = citire reușită, zero facturi"


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_citirea_se_scrie_pe_cui_in_spv_cui_acoperit():
    """Tabela exista (ARHITECTURA_SPV.md: se populează empiric, per CIF) și n-o scria nimeni; acum o scrie fiecare citire."""
    from core import spv_conector as sc
    from core import spv_receive as sr
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("SELECT id FROM public.accounting_firms ORDER BY id LIMIT 1")
                af = cur.fetchone()[0]
                cur.execute("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, "
                            "refresh_expira, activ) VALUES (%s, 'TEST-LOT6', %s, %s, now() + interval '1 day', now() + interval '2 days', false) "
                            "RETURNING id", (af, sc.cripteaza("a"), sc.cripteaza("r")))
                tok = cur.fetchone()[0]
            sr._inregistreaza_citire(c, tok, "55229657", "Nu aveti drept in SPV pentru CIF=55229657", 0)
            with c.cursor() as cur:
                cur.execute("SELECT are_drept, eroare, ultima_reusita FROM public.spv_cui_acoperit WHERE token_id = %s", (tok,))
                assert cur.fetchone() == (False, "Nu aveti drept in SPV pentru CIF=55229657", None)
            sr._inregistreaza_citire(c, tok, "55229657", None, 2)
            with c.cursor() as cur:
                cur.execute("SELECT are_drept, eroare, mesaje, ultima_reusita IS NOT NULL FROM public.spv_cui_acoperit WHERE token_id = %s", (tok,))
                assert cur.fetchone() == (True, None, 2, True)
        finally:
            c.rollback()


# ── 275b: starea în SPV a facturii emise ──────────────────────────────────────────────────────────────────────────────────────────
def test_275_starea_spv_netrimisa_acceptata_respinsa(schema_firma):
    """MUTAȚIE: `_cu_stare_spv(cur, out)` scos din `lista_facturi` -> `stare_spv` lipsește -> pică."""
    from core import facturi_api as fa
    with _db.get_conn(schema_firma) as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, status, tip) "
                        "VALUES ('F1A9', '2026-10-16', 'emisa', 242, 42, 'emisa', 'factura') RETURNING id")
            fid = cur.fetchone()[0]
        c.commit()
        stare = lambda: [f["stare_spv"] for f in fa.lista_facturi(c) if f["id"] == fid][0]   # noqa: E731
        s = stare()
        assert (s["stare"], s["termen"]) == ("netrimisa", "2026-10-23"), s
        with c.cursor() as cur:
            cur.execute("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256, error_message) VALUES (%s, 'prod', 'nok', 'x', 'eroare ANAF')",
                        (fid,))
        assert (stare()["stare"], stare()["eroare"]) == ("respinsa", "eroare ANAF")
        with c.cursor() as cur:
            cur.execute("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, xml_sha256) VALUES (%s, 'prod', 'ok', 'y')", (fid,))
        assert stare()["stare"] == "acceptata"
        c.rollback()


# ── 287: pasul următor după „Trimite în coadă” ───────────────────────────────────────────────────────────────────────────────────
def test_287_pasul_urmator_dupa_starea_reala(monkeypatch):
    """MUTAȚIE: `if coada_api.patru_ochi_stare(...)["efectiv"]` -> `if True` -> fără validare în doi tot „la validare” -> pică."""
    from core import uc_coada as uc
    stare = {"efectiv": False}
    monkeypatch.setattr(uc.coada_api, "patru_ochi_stare", lambda c, f: dict(stare))
    perm = {"poate_depune": True}
    monkeypatch.setattr(uc._uc_comun, "_are_permisiune", lambda ctx, flag: perm.get(flag, False))
    ctx = {"firm": 1, "uid": 1}
    assert uc.pas_urmator(None, ctx)["cod"] == "depunere"
    perm["poate_depune"] = False
    assert uc.pas_urmator(None, ctx)["cod"] == "depunere_altcineva"
    stare["efectiv"] = True
    p = uc.pas_urmator(None, ctx)
    assert (p["fel"], p["statut"], p["cod"], p["mesaj"]) == ("statut", "validare", "validare", uc.PAS_VALIDARE), p
