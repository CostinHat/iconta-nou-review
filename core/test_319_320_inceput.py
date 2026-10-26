# -*- coding: utf-8 -*-
"""319 + 320 — cardurile de început (comanda Costin 17.10.2026 7.2, verbatim în DECIZII „Comanda 7.2”). Temei: N/A — produs.

319: „textul aprobat de Costin, pus întocmai; numele ecranelor, butoanelor și verificările auditului de preluare le aliniezi cu cele
reale”. Garda: fiecare frază a cardurilor administratorului e, cuvânt cu cuvânt, în textul aprobat din DECIZII — în afara celor aliniate,
numite aici, fiecare cu motivul (`ALINIATE`).
"""
import io
import os

import pytest

from core import uc_inceput as ui

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: frazele aliniate la ecranele reale (319), cu motivul — nimic altceva nu se abate de la textul aprobat
ALINIATE = {
    ("preluare", 5): "auditul de preluare verifică pachetul ADUS, nu situația la ANAF; butonul „Rulează auditul de preluare”, în Control fiscal",
    ("anaf", 1): "butonul se numește „Conectează SPV”",
    ("echipa", 4): "butonul formularului se numește „Trimite invitația”",
}


def _aprobat():
    t = io.open(os.path.join(RAD, "DECIZII.md"), encoding="utf-8").read()
    i = t.index("## 17.10.2026 — Comanda 7.2 (lotul 7)")
    return t[i:t.index("**Decizia 320, verbatim:**", i)]


def test_319_textul_cardurilor_e_cel_aprobat_in_afara_alinierilor_numite():
    """MUTAȚIE: un cuvânt schimbat într-un pas al cardului („alege prima firmă” -> „alege firma”) -> pică."""
    aprobat = _aprobat()
    for c in ui.CARDURI_ADMIN:
        assert c["titlu"] in aprobat and c["ce_faci"] in aprobat and c["verde"] in aprobat, c["cheie"]
        if c["nota"]:
            assert c["nota"] in aprobat
        for i, p in enumerate(c["pasi"]):
            assert (c["cheie"], i) in ALINIATE or p in aprobat, (c["cheie"], i, p)
    for (k, i), motiv in ALINIATE.items():
        p = next(c for c in ui.CARDURI_ADMIN if c["cheie"] == k)["pasi"][i]
        assert p not in aprobat, ("alinierea declarată nu mai e o abatere — scoate-o din ALINIATE", k, i, motiv)


@pytest.fixture()
def lume(monkeypatch):
    """Semnalele din bază, simulate (repo), fără conexiune."""
    import contextlib

    class _C:
        def cursor(self):
            return contextlib.nullcontext(None)

        def rollback(self):
            pass

        def commit(self):
            pass

    st = {"omul": ("admin_firma", 7, "+40700000000", True, False, True, True, True), "firme": [(1, "tenant_1")], "preluare": (True, False),
          "spv": False, "echipa": (False, False), "asistent_firme": []}
    monkeypatch.setattr(ui.db, "get_conn", lambda schema=None: contextlib.nullcontext(_C()))
    monkeypatch.setattr(ui._repo, "omul", lambda cur, uid: st["omul"])
    monkeypatch.setattr(ui._repo, "firmele_cabinetului", lambda cur, cab: st["firme"])
    monkeypatch.setattr(ui._repo, "preluare_facuta", lambda cur, schema: st["preluare"])
    monkeypatch.setattr(ui._repo, "spv_conectat", lambda cur, cab: st["spv"])
    monkeypatch.setattr(ui._repo, "echipa", lambda cur, cab: st["echipa"])
    monkeypatch.setattr(ui._repo, "firmele_asistentului", lambda cur, uid: st["asistent_firme"])
    return st


def test_320_cardul_se_bifeaza_numai_din_semnalul_ecranului_real(lume):
    """Pasul 1: balanța FĂRĂ audit nu e făcut; cu audit, da. Pasul 2: SPV + notificările. Pasul 3: un asistent SAU „Lucrez singur”.
    MUTAȚIE: `if sold and audit` -> `if sold` -> pasul 1 verde fără audit -> pică."""
    r = ui.carduri({"uid": 1})
    assert [c["facut"] for c in r["carduri"]] == [False, False, False] and not r["toate_facute"]
    lume["preluare"], lume["spv"], lume["echipa"] = (True, True), True, (False, True)
    r = ui.carduri({"uid": 1})
    assert [c["facut"] for c in r["carduri"]] == [True, True, True] and r["toate_facute"]


def test_320_asistentul_si_clientul_au_cardurile_lor(lume):
    lume["omul"] = ("angajat", 7, None, False, False, True, False, False)
    lume["asistent_firme"] = [(4, "Comert Micro TVA SRL")]
    r = ui.carduri({"uid": 2})
    assert [c["cheie"] for c in r["carduri"]] == ["notificari", "firme"]
    pasi = r["carduri"][1]["pasi"]          # firmele alocate, apoi numai dreptul pe care îl are (fără „Poate valida”)
    assert pasi[:2] == ["Firmele tale: Comert Micro TVA SRL.", dict(ui.DREPTURI_NUME)["poate_pregati"]], pasi
    assert len(pasi) == 3, pasi
    lume["omul"] = ("client", None, "+40700000000", True, False, False, False, False)
    r = ui.carduri({"uid": 3})
    assert [c["cheie"] for c in r["carduri"]] == ["client"] and r["toate_facute"]


def test_320_numai_conturile_noi_trec_prin_prima_intrare(monkeypatch):
    """Decizia Costin 17.10.2026 („7.2 – continuare”, verbatim în DECIZII): „Numai conturile noi”. Contul existent la publicare
    (`prima_intrare_scutita_la`, pus o dată de `core/migrare_canal_notificari.py`) e complet fără telefon; contul nou, numai cu telefonul
    și bifele salvate. MUTAȚIE: `bool(p[5]) or` scos din `uc_cont_notificari._stare` -> contul existent e oprit la prima intrare -> pică."""
    from core import uc_cont_notificari as uc
    monkeypatch.setattr(uc._wa, "configurat", lambda: False)
    st = {"stare": (None, False, "email", False), "pref": (None, False, "admin_firma", True, True, True)}
    monkeypatch.setattr(uc._repo, "stare", lambda cur, uid: st["stare"])
    monkeypatch.setattr(uc._repo, "preferintele", lambda cur, uid: st["pref"])
    monkeypatch.setattr(uc._repo, "alte_conturi_cu_telefonul", lambda cur, uid, tel: 0)   # [338] fără bază: niciun alt cont
    monkeypatch.setattr(uc._repo, "emailul", lambda cur, uid: None)   # [lotul 13, 565] nota sintezei citește adresa: fără bază, niciuna
    assert uc._stare(None, 1)["complet"] is True                          # existent: fără telefon, fără bife — intră direct
    st["pref"] = (None, False, "admin_firma", True, True, False)
    assert uc._stare(None, 1)["complet"] is False                         # nou: oprit până la telefon + bife
    st["stare"], st["pref"] = ("+40700000001", False, "email", False), (None, True, "admin_firma", True, True, False)
    assert uc._stare(None, 1)["complet"] is True


def test_320_scutirea_se_da_o_singura_data_odata_cu_coloana():
    """Scutirea e în același bloc cu crearea coloanei: o rulare ulterioară a migrării nu scutește conturile create între timp.
    MUTAȚIE: UPDATE-ul mutat în afara blocului `IF NOT EXISTS` -> pică."""
    from core import db, migrare_canal_notificari as m
    # blocul migrării, rulat de DOUĂ ori pe un tabel temporar în locul lui `public.users` (tranzacție anulată): numai contul existent
    # la prima rulare e scutit
    bloc = m.DDL[m.DDL.index("DO $$"):m.DDL.index("END $$;") + len("END $$;")]
    bloc = bloc.replace("table_schema = 'public' AND table_name = 'users'", "table_name = 'zt_users_320'").replace(
        "public.users", "zt_users_320")
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TEMP TABLE zt_users_320 (id int)")
            cur.execute("INSERT INTO zt_users_320 VALUES (1)")
            cur.execute(bloc)                                   # publicarea: coloana apare, contul 1 e scutit
            cur.execute("INSERT INTO zt_users_320 VALUES (2)")
            cur.execute(bloc)                                   # o rulare ulterioară: contul 2 (nou) NU e scutit
            cur.execute("SELECT id, prima_intrare_scutita_la IS NOT NULL FROM zt_users_320 ORDER BY id")
            rez = cur.fetchall()
        conn.rollback()
    assert rez == [(1, True), (2, False)], rez


@pytest.mark.parametrize("firma_refuzata", [None, 2])
def test_319_invitatia_cu_drepturi_si_firme_e_o_singura_tranzactie(monkeypatch, firma_refuzata):
    """319: „Bifează ce poate face [...] Bifează firmele pe care le lucrează” — din aceeași invitație. Contul, drepturile, firmele și
    linkul de activare se scriu în ACEEAȘI tranzacție: o firmă refuzată (din alt cabinet) oprește invitația întreagă — niciun link,
    niciun email, deci niciun cont rămas fără firme pe care nu-l mai poți invita din nou. MUTAȚIE: drepturile / firmele scrise prin
    rutele lor (câte o tranzacție, după link) -> `get_conn` de trei ori și linkul pus înaintea refuzului -> pică."""
    import contextlib
    import types
    from core import erori, nucleu, uc_asistenti as ua
    jurnal = []

    class _C:
        def cursor(self, **_k):
            # [lotul 10, C73 / U3] contul se scrie sub savepoint (`chei_unice.refuza_dublura`): cursorul simulat primește SAVEPOINT-urile
            return contextlib.nullcontext(types.SimpleNamespace(execute=lambda *a, **k: None, fetchone=lambda: None))   # [560] `nume_cabinet`: niciun rând

    @contextlib.contextmanager
    def _conn(schema=None):
        jurnal.append("conn")
        yield _C()

    monkeypatch.setattr(ua.db, "get_conn", _conn)
    monkeypatch.setattr(nucleu, "hash_parola", lambda p: "x")
    monkeypatch.setattr(ua.repo_utilizatori, "contul_dupa_email", lambda cur, e: None)
    monkeypatch.setattr(ua.repo_utilizatori, "creeaza_cont_asistent", lambda *a: {"id": 99})
    monkeypatch.setattr(ua._asist, "set_permisiuni", lambda conn, cab, uid, p, v, d: jurnal.append(("drepturi", cab, d)) or {"ok": True})
    monkeypatch.setattr(ua._asist, "atribuie_firma", lambda conn, cab, uid, tid: jurnal.append(("firma", tid))
                        or ({"ok": False, "cod": "firma_alt_cabinet"} if tid == firma_refuzata else {"ok": True}))
    monkeypatch.setattr(ua._uc_comun, "_pune_token", lambda cur, tok, uid, ttl: jurnal.append("link"))
    from core import repo_cabinet
    monkeypatch.setattr(repo_cabinet, "nume_cabinet", lambda cur, firm_id: "Cabinet Probă")   # [lotul 13, 560] numele în email, fără bază
    monkeypatch.setattr(ua._obs, "trimite_email_html_sau_semnaleaza", lambda *a, **k: jurnal.append("email") or True)   # [598] a plecat
    date = types.SimpleNamespace(email="zt.319@exemplu.ro", nume="ZT", poate_pregati=True, poate_valida=False, poate_depune=True,
                                 firme=[1, 2])
    ctx = {"rol": "admin_firma", "firm": 7, "uid": 1}
    if firma_refuzata:
        with pytest.raises(erori.CerereGresita):
            ua.asistent_creeaza(date, ctx)
        assert jurnal == ["conn", ("drepturi", 7, True), ("firma", 1), ("firma", 2)]     # fără link, fără email
    else:
        assert ua.asistent_creeaza(date, ctx) == {"ok": True, "user_id": 99}
        assert jurnal == ["conn", ("drepturi", 7, True), ("firma", 1), ("firma", 2), "link", "email"]
