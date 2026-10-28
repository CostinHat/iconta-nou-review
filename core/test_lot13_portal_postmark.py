# -*- coding: utf-8 -*-
"""[lotul 13, comanda 13.1 pct.1 — Postmark] Emailurile tranzacționale (confirmare cont, resetare parolă, link de logare, invitații, alerte)
pleacă pe Postmark, expeditor contact@iconta.eu; „Domeniul iconta.eu e încă neverificat [...]; până la verificare și aprobarea contului,
Postmark e în mod de test, deci Brevo rămâne rezervă și nu se scoate.” (comanda 13.1 pct.1, verbatim).

Ce apără fișierul:
  1. Postmark REFUZĂ (HTTP 4xx cu `{"ErrorCode": N, "Message": ...}` — contul în mod de test refuză destinatarii din afara domeniului) ->
     emailul pleacă pe Brevo; refuzul (codul și mesajul Postmark) e în jurnal, tokenul NU.
  2. Postmark NU RĂSPUNDE (rețea / timp de așteptare) -> Brevo.
  3. Postmark răspunde 200 cu `ErrorCode` != 0 -> Brevo.
  4. Postmark PRIMEȘTE (`ErrorCode` 0) -> Brevo nu e chemat (un singur email).
  5. Alerta internă (`_trimite_brevo`) are aceeași rezervă.
  6. Clasa „emailuri tranzacționale” [14.2, 268.2]: tot ce nu e `informativ` pleacă pe Postmark când există tokenul, fără steag pe apel (nu
     există parametrul `postmark`); numai cu atașamente sau informativ rămâne pe Brevo. Un email de acces nou nu poate uita Postmark.
Nicio cerere nu pleacă: `urllib.request.urlopen` e înlocuit în fiecare test.
"""
import ast
import io
import json
import os
import urllib.error

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "pm-token-de-proba-0123456789"
POSTMARK = "https://api.postmarkapp.com/email"
BREVO = "https://api.brevo.com/v3/smtp/email"


class _Raspuns:
    def __init__(self, corp, status=200):
        self.status, self._corp = status, corp

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps(self._corp).encode()


def _post(monkeypatch, postmark):
    """`postmark(req)` decide ce face Postmark (întoarce un răspuns sau ridică); Brevo primește mereu (201)."""
    cereri = []

    def urlopen(req, timeout=0):
        cereri.append(req)
        if req.full_url == POSTMARK:
            return postmark(req)
        return _Raspuns({"messageId": "b"}, status=201)

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE", raising=False)
    monkeypatch.delenv("ICONTA_SENDER_EMAIL", raising=False)
    monkeypatch.setenv("POSTMARK_SERVER_TOKEN", TOKEN)
    monkeypatch.setenv("BREVO_API_KEY", "bv")
    monkeypatch.setenv("ICONTA_ALERTA_EMAIL", "alerta@exemplu.test")
    return cereri


def _refuz(cod_http, corp):
    def f(req):
        raise urllib.error.HTTPError(req.full_url, cod_http, "refuz", {}, io.BytesIO(json.dumps(corp).encode()))
    return f


# Răspunsul Postmark la un destinatar din afara domeniului cât contul așteaptă aprobarea (documentația Postmark „API error codes”: 412 —
# „Account is pending approval”: „While your account is pending approval, all recipient addresses must share the same domain as the
# 'From' address.”) — forma corpului e cea din documentație: ErrorCode + Message.
REFUZ_412 = {"ErrorCode": 412, "Message": "Account is pending approval. All recipient addresses must share the same domain as the 'From' address."}


def test_postmark_refuza_emailul_pleaca_pe_brevo_iar_refuzul_e_in_jurnal_fara_token(monkeypatch, capsys):
    """MUTAȚIE: rezerva scoasă din `trimite_email_html` (`if _trimite_postmark(...): return True` -> `return _trimite_postmark(...)`)
    -> False, o singură cerere -> ROȘU."""
    from core import observare as O
    cereri = _post(monkeypatch, _refuz(422, REFUZ_412))
    assert O.trimite_email_html("client@gmail.com", "Link de logare iConta.eu", "<p>x</p>") is True
    assert [r.full_url for r in cereri] == [POSTMARK, BREVO]
    pm, bv = (json.loads(r.data) for r in cereri)
    assert pm["From"] == "iConta.eu <contact@iconta.eu>" and pm["MessageStream"] == "outbound", pm   # expeditorul cerut de comandă
    assert bv["sender"]["email"] == "contact@iconta.eu" and bv["to"] == [{"email": "client@gmail.com"}], bv
    jurnal = capsys.readouterr().out
    assert "[email esuat Postmark, trece pe Brevo] Link de logare iConta.eu -> client@gmail.com: HTTP 422 — ErrorCode 412" in jurnal, jurnal
    assert TOKEN not in jurnal, jurnal


def test_postmark_nu_raspunde_emailul_pleaca_pe_brevo(monkeypatch, capsys):
    from core import observare as O

    def cade(req):
        raise urllib.error.URLError("timed out")
    cereri = _post(monkeypatch, cade)
    assert O.trimite_email_html("a@b.ro", "Resetare parola iConta.eu", "<p>x</p>") is True
    assert [r.full_url for r in cereri] == [POSTMARK, BREVO]
    jurnal = capsys.readouterr().out
    assert "URLError" in jurnal and TOKEN not in jurnal, jurnal


def test_postmark_200_cu_eroare_emailul_pleaca_pe_brevo(monkeypatch, capsys):
    from core import observare as O
    cereri = _post(monkeypatch, lambda req: _Raspuns({"ErrorCode": 406, "Message": "Inactive recipient"}))
    assert O.trimite_email_html("a@b.ro", "Confirmă contul iConta.eu", "<p>x</p>") is True
    assert [r.full_url for r in cereri] == [POSTMARK, BREVO]
    assert "ErrorCode 406 — Inactive recipient" in capsys.readouterr().out


def test_postmark_primeste_brevo_nu_e_chemat(monkeypatch):
    """MUTAȚIE: `return True` după reușita Postmark scos -> pleacă și pe Brevo (două emailuri) -> ROȘU."""
    from core import observare as O
    cereri = _post(monkeypatch, lambda req: _Raspuns({"ErrorCode": 0, "MessageID": "x"}))
    assert O.trimite_email_html("a@iconta.eu", "Confirmă contul iConta.eu", "<p>x</p>") is True
    assert [r.full_url for r in cereri] == [POSTMARK]
    assert cereri[0].headers["X-postmark-server-token"] == TOKEN


def test_tranzactionalul_oarecare_pleaca_pe_postmark_iar_informativul_si_atasamentul_pe_brevo(monkeypatch):
    """[14.2, 268.2] Facturile, amintirile, notificările (tot ce nu e informativ) trec pe Postmark fără steag; informativul (cu „Dezabonează-te”,
    pe care Postmark îl are doar pe fluxul Broadcast) și emailul cu atașament rămân pe Brevo.
    MUTAȚIE: `not informativ and` scos din condiția Postmark -> informativul pleacă pe Postmark -> ROȘU."""
    from core import observare as O
    monkeypatch.setattr(O, "refuz_dezabonare", lambda catre: None)
    cereri = _post(monkeypatch, lambda req: _Raspuns({"ErrorCode": 0}))
    assert O.trimite_email_html("a@b.ro", "Factura F1", "<p>x</p>") is True
    assert O.trimite_email_html("a@b.ro", "Sinteza", "<p>x</p>", informativ=True) is True
    assert O.trimite_email_html("a@b.ro", "Raport", "<p>x</p>", attachments=[{"content": "QQ==", "name": "r.pdf"}]) is True
    assert [r.full_url for r in cereri] == [POSTMARK, BREVO, BREVO]


def test_alerta_interna_postmark_refuza_pleaca_pe_brevo(monkeypatch, capsys):
    """MUTAȚIE: rezerva scoasă din `_trimite_brevo` (`return _trimite_postmark(...)`) -> False, o singură cerere -> ROȘU."""
    from core import observare as O
    cereri = _post(monkeypatch, _refuz(422, REFUZ_412))
    assert O._trimite_brevo("Disc plin", "Discul are 95%") is True
    assert [r.full_url for r in cereri] == [POSTMARK, BREVO]
    assert json.loads(cereri[1].data)["subject"] == "[iConta.eu] Disc plin"
    assert TOKEN not in capsys.readouterr().out


# ── 6. Clasa: nicio cale de trimitere nu mai alege furnizorul pe apel ────────────────────────────────────────────────────────────────
def _apeluri():
    out = []
    surse = [os.path.join(RAD, "main.py")] + [os.path.join(RAD, "core", f) for f in sorted(os.listdir(os.path.join(RAD, "core")))
                                              if f.endswith(".py") and not f.startswith("test_")]
    for cale in surse:
        arb = ast.parse(io.open(cale, encoding="utf-8").read())
        for n in ast.walk(arb):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", "")) in (
                    "trimite_email_html", "trimite_email_html_sau_semnaleaza"):
                out.append((os.path.relpath(cale, RAD), n.lineno, sorted(k.arg for k in n.keywords if k.arg)))
    return out


def test_niciun_apel_nu_alege_furnizorul_si_emailurile_contului_exista():
    """Furnizorul nu mai e un steag pe apel (`postmark=`): îl decide `trimite_email_html` după `informativ` și atașamente, deci un email nou
    de acces nu poate uita Postmark. Anti-vacuu: cel puțin 20 de apeluri, iar cele ale contului există.
    MUTAȚIE: `postmark=True` pus înapoi pe un apel -> ROȘU."""
    apeluri = _apeluri()
    assert len(apeluri) >= 20, len(apeluri)
    assert [a for a in apeluri if "postmark" in a[2]] == []
    import inspect
    from core import observare as O
    assert "postmark" not in inspect.signature(O.trimite_email_html).parameters
