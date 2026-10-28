# -*- coding: utf-8 -*-
"""[lotul 12, comanda 12.2 pct.20, deficiența 268.1] Emailul „TEST Alertă iConta.eu — sănătate server” are „Dezabonează-te”, care ar opri
alertele de server. Dezabonarea rămâne numai pe recomandări și pe sinteza zilnică (268, `core/dezabonare.py` `INFORMATIVE`).

CE E AL NOSTRU ȘI CE NU. Alerta pleacă din `main.admin_sanatate_test_alerta` / `main._verifica_si_alerta` prin
`observare.trimite_email_html(informativ=False)`: fără subsolul nostru și fără antetele noastre (probat mai jos și de
`core/test_dezabonare.py`). „Dezabonează-te” din Gmail vine din antetul List-Unsubscribe pe care Brevo îl pune singur pe orice email, inclusiv
tranzacțional (DEFICIENTE 268; LANSARE „Lotul 9, comanda 9.1 D3”, antetele brute ale emailului din 19.10.2026 07:07). Singurul drum din cod
fără antet e fluxul tranzacțional Postmark (decizia Costin 17.10.2026 7.2 pct.2.5, `observare._trimite_postmark`), activ numai cu
`POSTMARK_SERVER_TOKEN` (de la Costin, încă neconfigurat). Gardul de aici: alertele către administrator merg pe drumul acela.
"""
import ast
import io
import json
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _Raspuns:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps({"ErrorCode": 0, "MessageID": "x"}).encode()


def _cereri(monkeypatch, token):
    cereri = []
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=0: cereri.append(req) or _Raspuns())
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE", raising=False)
    monkeypatch.setenv("BREVO_API_KEY", "bv")
    monkeypatch.setenv("ICONTA_ALERTA_EMAIL", "alerta@exemplu.test")
    if token:
        monkeypatch.setenv("POSTMARK_SERVER_TOKEN", token)
    else:
        monkeypatch.delenv("POSTMARK_SERVER_TOKEN", raising=False)
    return cereri


def test_def_268_1_alerta_interna_pleaca_pe_postmark_cand_exista_tokenul(monkeypatch):
    """MUTAȚIE: ramura Postmark scoasă din `_trimite_brevo` -> cererea pleacă la Brevo -> pică."""
    from core import observare as O
    cereri = _cereri(monkeypatch, "pm")
    assert O._trimite_brevo("Disc plin", "Discul are 95% <ocupat>") is True
    (r,) = cereri
    corp = json.loads(r.data)
    assert (r.full_url, r.headers["X-postmark-server-token"], corp["To"], corp["Subject"], corp["MessageStream"]) == (
        "https://api.postmarkapp.com/email", "pm", "alerta@exemplu.test", "[iConta.eu] Disc plin", "outbound"), corp
    assert corp["HtmlBody"] == "<pre style='font-family:sans-serif;white-space:pre-wrap'>Discul are 95% &lt;ocupat&gt;</pre>", corp
    assert sorted(corp) == ["From", "HtmlBody", "MessageStream", "Subject", "To"], corp   # niciun antet de dezabonare


def test_def_268_1_fara_token_alerta_ramane_pe_brevo_fara_antetele_noastre(monkeypatch):
    from core import observare as O
    cereri = _cereri(monkeypatch, None)
    assert O._trimite_brevo("Disc plin", "Mesaj") is True
    (r,) = cereri
    corp = json.loads(r.data)
    assert r.full_url == "https://api.brevo.com/v3/smtp/email" and sorted(corp) == ["sender", "subject", "textContent", "to"], corp


def test_def_268_1_emailul_test_alerta_nu_are_dezabonarea_noastra(monkeypatch):
    """Drumul real al butonului „Trimite alertă de test” (`main.admin_sanatate_test_alerta`), fără token: pe Brevo, fără subsol și fără
    antete; cu token: pe Postmark (MUTAȚIE: `informativ=True` pus pe apel -> subsol și antete -> pică)."""
    import main
    monkeypatch.setattr(main, "_email_superadmin", lambda: "admin@exemplu.test")
    cereri = _cereri(monkeypatch, None)
    main.admin_sanatate_test_alerta(ctx={"rol": "superadmin"})
    (r,) = cereri
    corp = json.loads(r.data)
    assert corp["subject"] == "TEST Alertă iConta.eu — sănătate server" and "headers" not in corp, corp
    assert corp["htmlContent"].count("Dezabonează") == 0 and corp["htmlContent"].count("dezabonare") == 0, corp["htmlContent"]
    cereri = _cereri(monkeypatch, "pm")
    main.admin_sanatate_test_alerta(ctx={"rol": "superadmin"})
    assert [x.full_url for x in cereri] == ["https://api.postmarkapp.com/email"], [x.full_url for x in cereri]


def _apeluri_alerta_sanatate():
    """Apelurile `trimite_email_html*` din main.py al căror subiect (constantă) e alerta de sănătate server."""
    arb = ast.parse(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    out = []
    for n in ast.walk(arb):
        if not (isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", "")).startswith("trimite_email_html")):
            continue
        subiecte = [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.endswith("sănătate server")]
        if subiecte:
            out.append((n.lineno, subiecte[0], any(k.arg == "informativ" and getattr(k.value, "value", None) is True for k in n.keywords)))
    return out


def test_def_268_1_ambele_alerte_de_sanatate_cer_drumul_fara_dezabonare():
    """Alerta reală și alerta de test: amândouă tranzacționale (fără `informativ=True`), deci cu token pleacă pe Postmark, fără antetul Brevo
    [14.2: furnizorul nu mai e steag pe apel]. Anti-vacuu: exact două apeluri."""
    apeluri = _apeluri_alerta_sanatate()
    assert sorted(s for _l, s, _p in apeluri) == ["Alertă iConta.eu — sănătate server", "TEST Alertă iConta.eu — sănătate server"], apeluri
    assert [a for a in apeluri if a[2]] == [], apeluri
