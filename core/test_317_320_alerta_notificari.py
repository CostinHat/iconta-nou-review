# -*- coding: utf-8 -*-
"""317 + 320 (comanda Costin 17.10.2026 7.2, verbatim în DECIZII „Comanda 7.2”).

317: „eroare 500 reală pe 17.10, ~11:05–11:15 (alerta de la 11:15) [...] Emailul de alertă e fără diacritice”. Cauza găsită în
`public.audit_log`: la 11:13:11, `GET /tenants/…/verifica-cui/…` a răspuns 502 — ANAF nu răspundea la verificarea CUI, iar ruta transforma
orice excepție a lui în `HTTPException(502, "ANAF indisponibil: <textul bibliotecii>")`; alerta de sănătate număra orice status ≥ 500 ca
„eroare server”. Iar o cădere reală a aplicației (excepție neprinsă) ieșea din `call_next` înaintea jurnalului, deci nu se număra deloc.
320: bifele din Notificări decid ce pleacă pe WhatsApp / email; clopoțelul arată tot. Temei: N/A — reguli de proces.
"""
import requests

from core import anaf_api, notificari


def test_317_anaf_care_nu_raspunde_e_spus_pe_intelesul_omului():
    """MUTAȚIE: `mesaj_indisponibil` întoarce `str(e)` (textul bibliotecii, ca înainte) -> pică."""
    m = anaf_api.mesaj_indisponibil(requests.exceptions.ReadTimeout("HTTPSConnectionPool(host='webservicesp.anaf.ro'): Read timed out."))
    assert m == anaf_api.MESAJ_ANAF_NU_RASPUNDE and "HTTPSConnectionPool" not in m
    assert anaf_api.mesaj_indisponibil(requests.exceptions.ConnectionError("x")) == anaf_api.MESAJ_ANAF_NU_RASPUNDE
    r = requests.models.Response()
    r.status_code = 503
    m503 = anaf_api.mesaj_indisponibil(requests.exceptions.HTTPError("503 Server Error", response=r))
    assert m503 == "ANAF a refuzat verificarea CUI (răspunsul serviciului: 503). Încearcă din nou peste un minut.", m503


def test_317_alerta_numara_numai_erorile_aplicatiei():
    """MUTAȚIE: `= 500` -> `>= 500` în `repo_main.select_public` -> un refuz scris de noi pentru ANAF căzut (502) devine iar „eroare
    server” -> pică."""
    from core import db, repo_main
    db.init_pool()
    with db.get_conn() as conn:          # rândurile sintetice se anulează la final (tabel partajat)
        with conn.cursor() as cur:
            inainte = repo_main.select_public(cur)[0]
            for st in (500, 502, 503, 200):
                cur.execute("INSERT INTO public.audit_log (actiune, detalii) VALUES ('zt_317', %s::jsonb)", ('{"status": %d}' % st,))
            dupa = repo_main.select_public(cur)[0]
        conn.rollback()
    assert dupa - inainte == 1, (inainte, dupa)


def test_317_caderea_aplicatiei_se_scrie_in_jurnal_cu_500(monkeypatch):
    """O excepție neprinsă trece prin `_audit_middleware` cu statusul 500 scris (înainte nu se scria nimic). Proba: o rută care cade,
    chemată prin aplicație; jurnalul primește (metoda, calea, 500). MUTAȚIE: ramura `except` scoasă din middleware -> pică."""
    import main
    from fastapi.testclient import TestClient
    scrise = []
    monkeypatch.setattr(main, "_inregistreaza_activitate", lambda metoda, cale, status, auth: scrise.append((metoda, cale, status)))

    def _cade():
        raise RuntimeError("cădere sintetică 317")

    main.app.add_api_route("/zt-cadere-317", _cade, methods=["GET"])
    try:
        r = TestClient(main.app, raise_server_exceptions=False).get("/zt-cadere-317")
    finally:
        main.app.router.routes[:] = [x for x in main.app.router.routes if getattr(x, "path", None) != "/zt-cadere-317"]
    assert r.status_code == 500 and scrise == [("GET", "/zt-cadere-317", 500)], (r.status_code, scrise)


def test_317_emailul_de_alerta_are_diacritice(monkeypatch):
    """317: alerta „erori 500” se scrie cu diacritice — subiectul și rândul, citite din emailul care pleacă (nu din sursă). MUTAȚIE:
    subiectul fără diacritice („Alerta iConta.eu — sanatate server”) -> pică."""
    import main
    randuri, plecate = [], []
    monkeypatch.setattr(main, "_citeste_metrici_pentru_alerte", lambda: {"disc_procent": None, "erori_noi": 2})
    monkeypatch.setattr(main, "_verifica_drift_p2", lambda: None)
    monkeypatch.setattr(main, "_poate_alerta", lambda cod: True)
    monkeypatch.setattr(main, "_email_superadmin", lambda: "alerta@exemplu.test")
    monkeypatch.setattr(main.db, "get_conn", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fără bază în test")))
    monkeypatch.setattr(main._obs, "esec_secundar", lambda *a, **k: None)
    monkeypatch.setattr(main._alerta_load, "rand", lambda cod, text: randuri.append((cod, text)) or text)
    # [lotul 12, 12.2] alerta pleacă pe Postmark (`postmark=True`, canalul tranzacțional al lui `observare`), nu pe Brevo
    monkeypatch.setattr(main._obs, "trimite_email_html_sau_semnaleaza",
                        lambda ce, email, subiect, html, **k: plecate.append((email, subiect, k)))
    main._verifica_si_alerta()
    assert randuri == [("erori", "2 erori ale aplicației (500) în ultimele 10 minute")], randuri
    assert plecate == [("alerta@exemplu.test", "Alertă iConta.eu — sănătate server", {"postmark": True})], plecate


def test_320_bifele_decid_canalul_clopotelul_ramane(monkeypatch):
    """Tipul nebifat nu pleacă pe email / WhatsApp (rămâne în clopoțel, cu jurnalul „nebifat”); implicitul: termenele și validările.
    MUTAȚIE: ramura `elif not dorit(...)` scoasă din `livreaza_in_asteptare` -> pleacă -> pică."""
    plecate, jurnal = [], []
    d = {"uid": 5, "email": "x@exemplu.test", "canal": "email", "telefon": None, "confirmat": False, "acord": False, "activ": True}
    monkeypatch.setattr(notificari, "_revendica", lambda limita: [(1, "solicitare_client", dict(d, preferinte=None)),
                                                                 (2, "de_validat", dict(d, preferinte=None)),
                                                                 (3, "de_validat", dict(d, preferinte={"de_validat": False}))])
    monkeypatch.setattr(notificari, "livreaza", lambda nid, dd, tip: plecate.append((nid, tip)) or "email")
    monkeypatch.setattr(notificari, "_jurnal", lambda *a, **k: jurnal.append((a, k)))
    rez = notificari.livreaza_in_asteptare()
    assert plecate == [(2, "de_validat")], plecate
    assert rez == {"nedorit": 2, "email": 1}, rez
    assert [k.get("detaliu") for _a, k in jurnal] == [notificari.DETALIU_NEBIFAT] * 2, jurnal


def test_320_fiecare_tip_are_grupa_randul_si_cine_il_vede():
    """Mulțimea închisă: fiecare tip din clopoțel are grupa dintre cele cinci, rândul pentru Notificări și cine îl vede."""
    for k, v in notificari.TIPURI.items():
        assert v["grup"] in notificari.GRUPURI and v["rand"].endswith(".") and v["cine"] in notificari.CINE, k
    admin = [t["cheie"] for g in notificari.lista_pentru({"rol": "admin_firma"}, None) for t in g["tipuri"]]
    assert {"asistent_activat"} <= set(admin) and not {"sesizare", "pachet_lunar"} & set(admin), admin


def test_320_termenele_de_notificat_sunt_cele_de_peste_trei_zile():
    import datetime
    from core import notificari_termene as nt
    azi = datetime.date(2026, 10, 22)
    termene = [{"tip": "d300", "termen": "2026-10-25", "perioada": "09/2026"}, {"tip": "d390", "termen": "2026-11-25", "perioada": "10/2026"}]
    assert nt.de_notificat(termene, azi) == [termene[0]]
    assert nt.text("Firma X SRL", termene[0]) == "Firma X SRL: D300 · 09/2026 are termenul pe 25.10.2026 (peste 3 zile) și nu e încă depusă."


def test_397_tipurile_platformei_au_grupa_lor_vazuta_numai_de_superadmin():
    """[397, retestul 19.10.2026] „O alertă legislativă importantă” stătea sub „Termene și declarații”. Tipurile superadminului (`cine:
    superadmin`) stau în grupa „Platformă”, iar grupa nu apare la nimeni altcineva.
    MUTAȚIA: alerta legislativă înapoi la „Termene și declarații” -> ROȘU."""
    super_ = [k for k, v in notificari.TIPURI.items() if v["cine"] == "superadmin"]
    assert sorted(super_) == ["alerta_legislativa", "cerere_import", "sesizare"], super_
    assert all(notificari.TIPURI[k]["grup"] == "Platformă" for k in super_)
    assert [g["grup"] for g in notificari.lista_pentru({"rol": "superadmin"}, None)] == ["Platformă"]
    for actor in ({"rol": "admin_firma"}, {"rol": "angajat", "poate_pregati": True, "poate_valida": True}, {"rol": "client"}):
        assert "Platformă" not in [g["grup"] for g in notificari.lista_pentru(actor, None)], actor
