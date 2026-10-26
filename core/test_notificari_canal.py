# -*- coding: utf-8 -*-
"""Lotul 7 (comanda Costin 17.10.2026, verbatim în DECIZII „Lotul 6 închis”) — notificările pe canalul ales (2.1–2.3), WhatsApp (2.4),
Postmark (2.5), Search Console (2.7).

Ce se păzește:
  1. livrarea clopoțelului: după commit, o singură dată, pe canalul omului; WhatsApp numai cu numărul confirmat și acordul (și în bază);
     WhatsApp refuzat / nelivrat -> email (o singură dată); afară pleacă eticheta tipului, nu textul notificării;
  2. orice tip scris în clopoțel are etichetă de livrare (scanare AST a apelurilor) — un tip nou nu pleacă necunoscut;
  3. Setări cont -> Notificări: numărul, acordul, codul (hash, expirare, încercări), canalul — în ordinea cerută;
  4. superadminul primește notificare la fiecare cerere de import și sesizare;
  5. webhook-ul: verificarea, semnătura (fail-closed), stările;
  6. emailurile tranzacționale pe Postmark când există tokenul; adresele retrase -> 410; linkul `/deschide/<cheie>`.
Pe baza de TEST, într-o singură tranzacție anulată la final (`commit` = no-op)."""
import ast
import contextlib
import hashlib
import hmac
import io
import json
import os

import pytest

from core import db as _db
from core import notificari as N
from core import whatsapp as W

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def baza(monkeypatch):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.notificari SET de_livrat = false WHERE de_livrat")   # numai rândurile probei, în tranzacție
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST NOTIF') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) VALUES "
                        "('ztest_notif_a@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (firm,))
            uid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            yield _ConnProxy(conn)
        monkeypatch.setattr(_db, "get_conn", _fake)
        trimise = {"email": [], "wa": []}
        monkeypatch.setattr(N._obs, "trimite_email_html_sau_semnaleaza",
                            lambda et, catre, subiect, html, **k: trimise["email"].append((catre, subiect, html)) or True)
        yield {"conn": conn, "uid": uid, "firm": firm, "trimise": trimise}
    finally:
        conn.rollback()
        p.putconn(conn)


def _sql(b, q, *a):
    with b["conn"].cursor() as cur:
        cur.execute(q, a)
        return cur.fetchall() if cur.description else None


def _notifica(b, tip="de_validat", text="Declarația D300 (09/2026) a firmei X: 1.234 lei de plată, de validat."):
    from core import notificari_api
    return notificari_api.adauga(b["conn"], b["uid"], tip, text, "validat:999999901")["id"]   # forma cerută de `notificari_element_ck`; elementul e sintetic


# ── 1. livrarea ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_notificarea_pleaca_o_data_pe_email_cu_eticheta_nu_cu_textul(baza):
    """MUTAȚIE: revendicarea (`SET de_livrat = false`) scoasă din `_revendica` -> a doua trecere trimite iar -> pică."""
    _notifica(baza)
    assert N.livreaza_in_asteptare() == {"email": 1}
    assert N.livreaza_in_asteptare() == {}, "a doua trecere nu mai trimite nimic"
    (catre, subiect, html), = baza["trimise"]["email"]
    assert (catre, subiect) == ("ztest_notif_a@invalid", "iConta.eu — un element nou de validat")
    # [lotul 13, 567: „emailul nu spune ce element și la ce firmă”] emailul poartă eticheta ca propoziție + elementul și firma (prima
    # propoziție a textului din clopoțel, `N.rezumat`; formele reale: core/test_lot13_portal_p2_notificari.py)
    assert html == N.html_email("de_validat", "Declarația D300 (09/2026) a firmei X: 1.234 lei de plată, de validat."), html
    assert "Un element nou de validat." in html and "Ai un element" not in html, html
    assert _sql(baza, "SELECT canal, stare, rezerva_email FROM public.notificari_jurnal WHERE user_id = %s", baza["uid"]) == [
        ("email", "trimis", False)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_notificarea_veche_nu_pleaca_retroactiv(baza):
    """Rândurile de dinainte (fără `de_livrat`) nu pleacă. MUTAȚIE: `de_livrat` scos din INSERT-ul lui `notificari_api.adauga` (rândul nou
    n-ar mai pleca) -> pică testul de mai sus; aici: valoarea implicită a coloanei."""
    _sql(baza, "INSERT INTO public.notificari (user_id, tip, text, link) VALUES (%s, 'de_validat', 'veche', 'validat:999999903')", baza["uid"])
    assert N.livreaza_in_asteptare() == {}


def _whatsapp_deschis(b):
    _sql(b, "UPDATE public.users SET telefon = '+40759638499', telefon_confirmat_la = now(), acord_whatsapp_la = now(), "
            "canal_notificari = 'whatsapp' WHERE id = %s", b["uid"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pe_whatsapp_iar_nelivrat_cade_o_data_pe_email(baza, monkeypatch):
    """MUTAȚIE: `if r and stare == "esuat" and not r[3]` -> fără `not r[3]` -> al doilea „eșuat” trimite iar emailul -> pică."""
    _whatsapp_deschis(baza)
    monkeypatch.setattr(W, "trimite_notificare", lambda tel, et, cale: baza["trimise"]["wa"].append((tel, et, cale)) or "wamid.Z1")
    _notifica(baza)
    assert N.livreaza_in_asteptare() == {"whatsapp": 1}
    assert baza["trimise"]["wa"] == [("+40759638499", "un element nou de validat", "notificari")] and baza["trimise"]["email"] == []
    assert N.stare_livrare("wamid.Z1", "livrat") is True and baza["trimise"]["email"] == []
    N.stare_livrare("wamid.Z1", "esuat", "131026 Message undeliverable")
    N.stare_livrare("wamid.Z1", "esuat", "131026 Message undeliverable")
    assert len(baza["trimise"]["email"]) == 1, "rezerva pe email pleacă o singură dată"
    assert _sql(baza, "SELECT canal, stare, rezerva_email FROM public.notificari_jurnal WHERE user_id = %s ORDER BY id", baza["uid"]) == [
        ("whatsapp", "esuat", True), ("email", "trimis", True)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_whatsapp_neconfigurat_sau_refuzat_trimite_pe_email(baza, monkeypatch):
    """MUTAȚIE: `except (_wa.Neconfigurat, ...)` scos din `livreaza` -> notificarea se pierde -> pică."""
    _whatsapp_deschis(baza)
    monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
    _notifica(baza)
    assert N.livreaza_in_asteptare() == {"email": 1}
    assert _sql(baza, "SELECT canal, rezerva_email FROM public.notificari_jurnal WHERE user_id = %s", baza["uid"]) == [("email", True)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_baza_refuza_canalul_whatsapp_fara_confirmare_si_acord(baza):
    """CHECK-ul `users_canal_notificari_check`: nicio cale (nici una viitoare) nu pune WhatsApp fără număr confirmat și acord."""
    import psycopg2
    with baza["conn"].cursor() as cur:
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.errors.CheckViolation):
            cur.execute("UPDATE public.users SET telefon = '+40759638499', canal_notificari = 'whatsapp' WHERE id = %s", (baza["uid"],))
        cur.execute("ROLLBACK TO SAVEPOINT s")


# ── 2. orice tip din clopoțel are etichetă ──────────────────────────────────────────────────────────────────────────────────────────
def _tipuri_scrise():
    """Tipurile date lui `adauga` / `adauga_multi` (al treilea argument) și lui `pentru_superadmini` (al doilea), în tot `core/`; un tip
    variabil se rezolvă din apelurile funcției care îl primește (`_notif_pregatitor(…, "respinsa")`)."""
    const, variabile, apeluri = set(), set(), {}
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        for n in ast.walk(arb):
            if not isinstance(n, ast.Call):
                continue
            nume = getattr(n.func, "attr", getattr(n.func, "id", ""))
            poz = {"adauga": 2, "adauga_multi": 2, "pentru_superadmini": 1}.get(nume)
            apeluri.setdefault(nume, []).append(n)
            if poz is None or len(n.args) <= poz:
                continue
            if nume == "adauga" and not ast.unparse(n.func).startswith(("_notif", "notificari_api", "_n.")):
                continue
            a = n.args[poz]
            if isinstance(a, ast.Constant):
                const.add(a.value)
            elif isinstance(a, ast.Name):
                variabile.add(a.id)
    assert variabile <= {"tip_eveniment", "tip"}, variabile
    for c in apeluri.get("_notif_pregatitor", []):
        const.add(c.args[2].value)
    return const


def test_fiecare_tip_din_clopotel_are_eticheta_de_livrare():
    """MUTAȚIE: `"control_fiscal"` scos din `TIPURI` -> pică (alerta de control fiscal n-ar mai pleca pe canal)."""
    tipuri = _tipuri_scrise()
    assert {"de_validat", "aprobata", "respinsa", "solicitare_client", "control_fiscal", "declaratie_reluata"} <= tipuri, tipuri
    assert tipuri - set(N.TIPURI) == set(), sorted(tipuri - set(N.TIPURI))


def test_eticheta_e_scurta_fara_cifre_si_linkul_e_o_cale_cunoscuta():
    """„mesaj scurt, fără conținut fiscal, cu link în aplicație”."""
    for tip, t in N.TIPURI.items():
        assert len(t["eticheta"]) <= 60 and not any(ch.isdigit() for ch in t["eticheta"]), tip
        assert t["deschide"] in N.DESCHIDERI, tip


# ── 3. Setări cont -> Notificări ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_numarul_se_normalizeaza_sau_se_refuza():
    assert [W.normalizeaza(x) for x in ("0759 638 499", "+40 759-638-499", "0040759638499", "+44 20 7946 0958", "12345", "07591",
                                        "")] == ["+40759638499", "+40759638499", "+40759638499", "+442079460958", None, None, None]


class _D:
    def __init__(self, **k):
        self.__dict__.update(k)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ordinea_numar_acord_cod_canal(baza, monkeypatch):
    """MUTAȚIE: `hmac.compare_digest` -> `True` în `confirma_cod` -> un cod greșit confirmă numărul -> pică."""
    from core import erori, uc_cont_notificari as U
    ctx = {"uid": baza["uid"]}
    coduri = []
    monkeypatch.setenv("WHATSAPP_TOKEN", "t")
    monkeypatch.setattr(W, "trimite_cod", lambda tel, cod: coduri.append((tel, cod)) or "wamid.C")
    with pytest.raises(erori.CerereGresita) as e:
        U.telefon_seteaza(_D(telefon="07591"), ctx)
    assert e.value.detaliu["cod"] == U.COD_TELEFON_INVALID and e.value.detaliu["erori_campuri"][0]["camp"] == "not-telefon"
    assert U.telefon_seteaza(_D(telefon="0759 638 499"), ctx)["telefon"] == "+40759638499"
    with pytest.raises(erori.CerereGresita) as e:
        U.cere_cod(_D(acord=False), ctx)
    assert e.value.detaliu["cod"] == U.COD_ACORD_LIPSA and coduri == [], "fără acord nu pleacă nimic, nici codul"
    with pytest.raises(erori.Conflict) as e:
        U.canal_seteaza(_D(canal="whatsapp", acord=True), ctx)
    assert e.value.detaliu["cod"] == U.COD_NECONFIRMAT
    assert U.cere_cod(_D(acord=True), ctx) == {"ok": True, "minute": W.COD_MINUTE}
    (tel, cod), = coduri
    assert tel == "+40759638499" and len(cod) == 6 and cod.isdigit()
    assert _sql(baza, "SELECT cod_hash FROM public.telefon_coduri WHERE user_id = %s", baza["uid"])[0][0] != cod, "numai hash-ul"
    with pytest.raises(erori.CerereGresita) as e:
        U.confirma_cod(_D(cod="%06d" % ((int(cod) + 1) % 10 ** 6)), ctx)
    assert e.value.detaliu["cod"] == U.COD_COD_GRESIT
    assert U.confirma_cod(_D(cod=cod), ctx)["confirmat"] is True
    st = U.canal_seteaza(_D(canal="whatsapp", acord=None), ctx)
    assert (st["canal"], st["acord"], st["confirmat"]) == ("whatsapp", True, True)
    st = U.telefon_seteaza(_D(telefon="+40 722 000 111"), ctx)
    assert (st["canal"], st["confirmat"]) == ("email", False), "un număr nou se confirmă din nou; canalul revine pe email"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_codul_expira_dupa_incercari(baza, monkeypatch):
    from core import erori, uc_cont_notificari as U
    ctx = {"uid": baza["uid"]}
    coduri = []
    monkeypatch.setenv("WHATSAPP_TOKEN", "t")
    monkeypatch.setattr(W, "trimite_cod", lambda tel, cod: coduri.append(cod) or "wamid.C")
    U.telefon_seteaza(_D(telefon="0759638499"), ctx)
    U.cere_cod(_D(acord=True), ctx)
    for _ in range(U.INCERCARI):
        with pytest.raises(erori.CerereGresita):
            U.confirma_cod(_D(cod="xxxxxx"), ctx)
    with pytest.raises(erori.CerereGresita) as e:
        U.confirma_cod(_D(cod=coduri[0]), ctx)
    assert e.value.detaliu["cod"] == U.COD_COD_EXPIRAT, "după încercările permise nici codul corect nu mai trece"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_whatsapp_configurat_acordul_ramane_si_spune_de_ce(baza, monkeypatch):
    from core import erori, uc_cont_notificari as U
    ctx = {"uid": baza["uid"]}
    monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
    U.telefon_seteaza(_D(telefon="0759638499"), ctx)
    with pytest.raises(erori.Conflict) as e:
        U.cere_cod(_D(acord=True), ctx)
    assert e.value.detaliu["cod"] == U.COD_WA_INDISPONIBIL and U.stare(ctx)["acord"] is True


# ── 4. superadminul ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_sesizarea_si_cererea_de_import_ajung_la_superadmin(baza, monkeypatch):
    """MUTAȚIE: apelul `pentru_superadmini` scos din `uc_raportari.raportari_creeaza` -> pică."""
    from core import uc_raportari
    monkeypatch.setattr("threading.Thread.start", lambda self: None)   # triajul AI al sesizării nu pornește în probă
    sup = [r[0] for r in _sql(baza, "INSERT INTO public.users (email,password_hash,nume,rol,activ) VALUES "
                                    "('ztest_notif_super@invalid','x','S','superadmin',true) RETURNING id")]
    toti = {r[0] for r in _sql(baza, "SELECT id FROM public.users WHERE rol = 'superadmin' AND activ")}
    ctx = {"uid": baza["uid"], "firm": baza["firm"]}
    uc_raportari.raportari_creeaza(_D(tip="sesizare", text="nu merge X", subiect="X", aplicatie=None), ctx)
    uc_raportari.raportari_creeaza(_D(tip="cerere_import", text="", subiect=None, aplicatie="SAGA"), ctx)
    rand = _sql(baza, "SELECT user_id, tip, text, link, de_livrat FROM public.notificari WHERE user_id = ANY(%s) ORDER BY id", list(toti))
    assert {(r[1], r[3], r[4]) for r in rand if r[0] == sup[0]} == {("sesizare", "deschide:raportari", True),
                                                                      ("cerere_import", "deschide:raportari", True)}, rand
    assert {r[0] for r in rand} == toti, "fiecare superadmin activ"
    assert any(r[2] == "Cerere de import din «SAGA» de la ZTEST NOTIF." for r in rand), rand


# ── 5. webhook-ul ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_semnatura_webhookului_e_fail_closed(monkeypatch):
    corp = b'{"entry":[]}'
    monkeypatch.delenv("WHATSAPP_APP_SECRET", raising=False)
    assert W.semnatura_valida(corp, "sha256=00") is False
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "s3cr3t")
    bun = "sha256=" + hmac.new(b"s3cr3t", corp, hashlib.sha256).hexdigest()
    assert W.semnatura_valida(corp, bun) is True and W.semnatura_valida(corp + b" ", bun) is False and W.semnatura_valida(corp, None) is False


def test_starile_din_webhook():
    p = {"entry": [{"changes": [{"value": {"statuses": [
        {"id": "wamid.A", "status": "delivered"}, {"id": "wamid.B", "status": "failed", "errors": [{"code": 131026, "title": "Undeliverable"}]},
        {"id": "wamid.C", "status": "necunoscut"}]}}]}]}
    assert W.stari_din_webhook(p) == [("wamid.A", "livrat", None), ("wamid.B", "esuat", "131026 Undeliverable")]


def test_verificarea_webhookului(monkeypatch):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "tok")
    assert W.verificare_webhook("subscribe", "tok", "123") == "123"
    assert W.verificare_webhook("subscribe", "altul", "123") is None
    monkeypatch.delenv("WHATSAPP_VERIFY_TOKEN")
    assert W.verificare_webhook("subscribe", "", "123") is None, "fără token configurat: refuz"


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def test_rutele_publice_ale_lotului(monkeypatch):
    """`/deschide/<cheie>` -> aplicația cu locul de deschis (cheie necunoscută -> pagina principală); webhook-ul fără semnătură -> 403; adresele
    retrase -> 410. MUTAȚIE: `status_code=410` -> 404 în `_adresa_retrasa` -> pică."""
    c = _client()
    r = c.get("/deschide/raportari", follow_redirects=False)
    assert (r.status_code, r.headers["location"]) == (302, "/#deschide=raportari")
    assert c.get("/deschide/oriunde", follow_redirects=False).headers["location"] == "/"
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "s")
    assert c.post("/whatsapp/webhook", content=b"{}", headers={"x-hub-signature-256": "sha256=00"}).status_code == 403
    import main
    assert [c.get(x).status_code for x in main.ADRESE_RETRASE] == [410] * len(main.ADRESE_RETRASE)


# ── 6. Postmark ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tranzactionalele_pe_postmark_cand_exista_tokenul(monkeypatch):
    """MUTAȚIE: `postmark=True` scos din resetarea parolei -> pleacă pe Brevo -> pică (al doilea assert)."""
    from core import observare as O
    cereri = []

    class _R:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"ErrorCode": 0, "MessageID": "x"}).encode()

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=0: cereri.append(req) or _R())
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE", raising=False)
    monkeypatch.setenv("POSTMARK_SERVER_TOKEN", "pm")
    monkeypatch.setenv("BREVO_API_KEY", "bv")
    assert O.trimite_email_html("a@b.ro", "Resetare", "<p>x</p>", postmark=True) is True
    assert O.trimite_email_html("a@b.ro", "Sinteza", "<p>x</p>") is True
    assert [r.full_url for r in cereri] == ["https://api.postmarkapp.com/email", "https://api.brevo.com/v3/smtp/email"]
    assert cereri[0].headers["X-postmark-server-token"] == "pm"
    assert json.loads(cereri[0].data)["MessageStream"] == "outbound"
    src = io.open(os.path.join(RAD, "core", "uc_public.py"), encoding="utf-8").read() + io.open(
        os.path.join(RAD, "core", "uc_auth.py"), encoding="utf-8").read()
    for eticheta in ("email resetare parola", "email link de logare", "email confirmare inregistrare"):
        apel = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant)
                and n.args[0].value == eticheta]
        assert apel and all(any(k.arg == "postmark" and getattr(k.value, "value", None) is True for k in a.keywords) for a in apel), eticheta


# ── 2.6 a doua sursă ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lista_actelor_din_portal():
    from core import monitor_fiscal as m
    html = ('<a href="/Public/DetaliiDocument/314897" class="x">8. ORDIN               1123 21/09/2026</a>'
            '<a href="/Public/DetaliiDocument/314897">Vizualizează</a><a href="/Public/DetaliiDocument/315227">12. PROCEDURA  29/09/2026</a>')
    assert m.acte_din_pagina(html) == [("314897", "ORDIN 1123 21/09/2026"), ("315227", "PROCEDURA 29/09/2026")]


def test_alertele_importante_devin_notificarea_superadminilor(monkeypatch):
    """MUTAȚIE: `notifica_importante(noi)` scos din `monitor_fiscal._main` -> al doilea assert pică; aici: numai cele `mare`."""
    from core import monitor_fiscal as m
    scrise = []

    @contextlib.contextmanager
    def _fake(schema=None):
        yield None
    monkeypatch.setattr(_db, "get_conn", _fake)
    monkeypatch.setattr(N, "pentru_superadmini", lambda conn, tip, text, leg: scrise.append((tip, text, leg)) or {"trimise": 1})
    assert m.notifica_importante([{"titlu": "OPANAF 602/2026", "_relevanta": "mare"}, {"titlu": "altceva", "_relevanta": "medie"}]) == 1
    assert scrise == [("alerta_legislativa", "Alertă legislativă importantă: OPANAF 602/2026", "deschide:anunturi")]
    assert m.notifica_importante([{"titlu": "x", "_relevanta": "zero"}]) == 0
    corp = [f for f in ast.parse(io.open(os.path.join(RAD, "core", "monitor_fiscal.py"), encoding="utf-8").read()).body
            if isinstance(f, ast.FunctionDef) and f.name == "_main"][0]
    chemate = {ast.unparse(n.func) for n in ast.walk(corp) if isinstance(n, ast.Call)}
    assert {"ruleaza_portal", "notifica_importante"} <= chemate and "observare._trimite_brevo" not in chemate, chemate


def test_refuzul_meta_spune_cauza_pentru_utilizator(monkeypatch):
    """Lotul 9 D1 (19.10.2026): `POST /<PHONE_NUMBER_ID>/register` a întors `message: "Invalid parameter"`, iar cauza era numai în
    `error_user_title` / `error_user_msg` (subcodul 2388001, politica WhatsApp). Refuzul o poartă, ca să nu se ghicească."""
    import urllib.error
    corp = json.dumps({"error": {"message": "Invalid parameter", "code": 100, "error_subcode": 2388001,
                                 "error_user_title": "Nu pot crea certificatul",
                                 "error_user_msg": "your business doesn't meet WhatsApp's policy requirements"}}).encode()

    def _refuz(req, timeout=0):
        raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, io.BytesIO(corp))
    monkeypatch.setenv("WHATSAPP_TOKEN", "t")
    monkeypatch.setattr("urllib.request.urlopen", _refuz)
    with pytest.raises(W.Refuzat) as e:
        W.inregistreaza_numarul("123456")
    m = str(e.value)
    assert m == ("Meta a refuzat cererea (HTTP 400, cod 100/2388001): Invalid parameter | Nu pot crea certificatul — your business doesn't "
                 "meet WhatsApp's policy requirements"), m
