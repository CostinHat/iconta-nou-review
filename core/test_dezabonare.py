# -*- coding: utf-8 -*-
"""Dezabonarea numai pe emailurile INFORMATIVE (deficiența 268; comanda 4 a lotului 5, verbatim în DECIZII: „emailurile tranzacționale nu
au deloc «Dezabonează-te» și nici antet List-Unsubscribe … Dezabonarea rămâne numai pe emailurile informative/de promovare”).

Ce apără, pe baza de TEST, cu adrese sintetice (`@proba-dezabonare.test`, șterse la sfârșit) și Brevo ÎNLOCUIT (`urlopen` prins: nimic
nu pleacă în afară):
  1. GARDA DE STRUCTURĂ (AST): orice trimitere de email din codul de producție trece prin `observare`; `informativ=True` stă EXACT pe
     locurile din `dezabonare.INFORMATIVE` (fișier + funcția care trimite) — un email tranzacțional marcat informativ, sau un informativ
     nou nescris în listă, pică; vechea excepție `cerut_de_destinatar` nu mai există.
  2. Emailul tranzacțional (HTML) și alerta către admin (text): fără subsol, fără antete, și pleacă și la o adresă dezabonată.
  3. Emailul informativ: subsolul „Dezabonează-te” + antetele List-Unsubscribe / List-Unsubscribe-Post; la o adresă dezabonată nu pleacă
     (refuz în jurnal, `False`), nici când registrul nu se poate citi (fail-closed); recomandarea spune „dezabonat”, nu „eșuat”.
  4. Pagina: semnătura greșită e refuzată; GET nu dezabonează (un scanner de linkuri nu dezabonează pe nimeni); POST dezabonează; pagina
     spune ce vine în continuare.
MUTAȚII (raportul lotului): subsolul pus la toate emailurile -> pică 2; `informativ=True` pe invitație -> pică 1; refuzul scos -> pică 3;
GET care dezabonează -> pică 4."""
import ast
import glob
import json
import os
import re
import types
import urllib.request

from html.parser import HTMLParser

import pytest

from core import db, dezabonare as dez, observare, uc_public

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMENIU = "@proba-dezabonare.test"
A = "ana" + DOMENIU
B = "bogdan" + DOMENIU
FAMILIA = ("trimite_email_html", "trimite_email_html_sau_semnaleaza")


class _Elemente(HTMLParser):
    """Elementele unei pagini / unui email: [(tag, atribute, text)] — aserțiunile se fac pe ELEMENTE, nu pe sub-șiruri din HTML."""

    def __init__(self, html):
        super().__init__()
        self.toate, self._deschise = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        el = [tag, dict(attrs), ""]
        self.toate.append(el)
        if tag not in ("br", "hr", "meta", "link", "input", "img"):
            self._deschise.append(el)

    def handle_endtag(self, tag):
        for i in range(len(self._deschise) - 1, -1, -1):
            if self._deschise[i][0] == tag:
                del self._deschise[i:]
                break

    def handle_data(self, data):
        for el in self._deschise:
            el[2] += data

    def cu_id(self, id_):
        return [e for e in self.toate if e[1].get("id") == id_]

    def texte(self, tag):
        return [" ".join(e[2].split()) for e in self.toate if e[0] == tag]


def _linkul_de_dezabonare(html):
    """(href) al linkului „Dezabonează-te” din email, sau None."""
    a = [e[1].get("href") for e in _Elemente(html).toate if e[0] == "a" and e[2].strip() == "Dezabonează-te"]
    return a[0] if len(a) == 1 else None


def _sql(q, p=()):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, p)
            r = cur.fetchall() if cur.description else None
        conn.commit()
    return r


@pytest.fixture()
def mediu(monkeypatch):
    """Brevo înlocuit: `urlopen` reține corpul cererii și răspunde 201. Fără cutia de test (corpul real către Brevo)."""
    db.init_pool()
    trimise = []

    class _Raspuns:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _urlopen(req, timeout=None):
        trimise.append(json.loads(req.data.decode()))
        return _Raspuns()

    monkeypatch.setattr(urllib.request, "urlopen", _urlopen)
    monkeypatch.setenv("BREVO_API_KEY", "cheie-de-proba")
    monkeypatch.delenv("ICONTA_EMAIL_CUTIE", raising=False)
    monkeypatch.setenv("ICONTA_BAZA_URL", "https://iconta.eu")
    _sql("DELETE FROM public.emailuri_dezabonate WHERE email LIKE %s", ("%" + DOMENIU,))
    try:
        yield trimise
    finally:
        _sql("DELETE FROM public.emailuri_dezabonate WHERE email LIKE %s", ("%" + DOMENIU,))


# ── 1. structura: o singură cale de trimitere ─────────────────────────────────────────────────────────────────────────────────────
def _surse_productie():
    out = [os.path.join(RAD, "main.py")]
    out += [f for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) if not os.path.basename(f).startswith("test_")]
    return out


def _alias_observare(arbore):
    """Numele sub care fișierul vede modulul `core.observare`."""
    nume = set()
    for n in ast.walk(arbore):
        if isinstance(n, ast.ImportFrom) and n.module == "core":
            nume |= {a.asname or a.name for a in n.names if a.name == "observare"}
        elif isinstance(n, ast.Import):
            nume |= {a.asname or a.name for a in n.names if a.name == "core.observare"}
    return nume


def inventar():
    """[(fisier, linie, functia, pe_observare, functia_care_trimite, informativ)] pentru fiecare apel din familie + definițiile din afara
    observare + apelurile care încă poartă `cerut_de_destinatar`."""
    apeluri, definitii, vechi = [], [], []
    for cale in _surse_productie():
        rel = os.path.relpath(cale, RAD)
        arbore = ast.parse(open(cale, encoding="utf-8").read())
        alias = _alias_observare(arbore)
        gazda = {}       # nodul -> funcția care îl conține (ast.walk merge în lățime: funcția interioară suprascrie)
        for fn in [x for x in ast.walk(arbore) if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]:   # cea mai interioară
            for n in ast.walk(fn):
                if n is not fn:
                    gazda[id(n)] = fn.name
        for n in ast.walk(arbore):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in FAMILIA and rel != "core/observare.py":
                definitii.append((rel, n.lineno, n.name))
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            nume = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nume not in FAMILIA:
                continue
            pe_obs = (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in alias) or \
                     (isinstance(f, ast.Name) and rel == "core/observare.py")
            kw = {k.arg: k.value for k in n.keywords}
            if kw.get("cerut_de_destinatar") is not None:
                vechi.append((rel, n.lineno))
            inf = isinstance(kw.get("informativ"), ast.Constant) and kw["informativ"].value is True
            apeluri.append((rel, n.lineno, nume, pe_obs, gazda.get(id(n)), inf))
    return apeluri, definitii, vechi


def test_orice_email_pleaca_prin_observare():
    apeluri, definitii, _ = inventar()
    assert len(apeluri) >= 15, "anti-vacuu: doar %d apeluri `trimite_email_html*` găsite" % len(apeluri)
    assert definitii == [], "altă definiție a trimiterii de email, în afara observare.py: %s" % definitii
    ocolite = [a[:3] for a in apeluri if not a[3]]
    assert ocolite == [], "trimitere care nu trece prin modulul `observare`: %s" % ocolite
    brevo = sorted({os.path.relpath(c, RAD) for c in _surse_productie()            # adresa Brevo, ca CONSTANTĂ în arbore (nu în comentarii)
                    for n in ast.walk(ast.parse(open(c, encoding="utf-8").read()))
                    if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("https://api.brevo.com")})
    assert brevo == ["core/observare.py"], "Brevo chemat direct, pe lângă observare: %s" % brevo
    smtp = [os.path.relpath(c, RAD) for c in _surse_productie() if re.search(r"\bsmtplib\b", open(c, encoding="utf-8").read())]
    assert smtp == [], smtp


def test_informativ_sta_exact_pe_emailurile_informative():
    """Lista închisă `dezabonare.INFORMATIVE`: fiecare loc din ea trimite cu `informativ=True`, și niciun alt apel nu o face."""
    apeluri, _, vechi = inventar()
    informative = {(a[0], a[4]) for a in apeluri if a[5]}
    assert informative == set(dez.INFORMATIVE), ("emailurile cu dezabonare s-au schimbat: în plus %s (un email tranzacțional NU are "
                                                 "dezabonare — comanda 4 a lotului 5), lipsă %s"
                                                 % (sorted(informative - set(dez.INFORMATIVE)), sorted(set(dez.INFORMATIVE) - informative)))
    assert vechi == [], "excepția veche `cerut_de_destinatar` (tranzacționalele nu se mai opresc deloc): %s" % vechi


# ── 2. tranzacționalele: fără dezabonare, pleacă oricum ─────────────────────────────────────────────────────────────────────────────
def test_emailul_tranzactional_n_are_subsol_nici_antete_si_pleaca_la_adresa_dezabonata(mediu):
    assert uc_public.dezabonare_confirma(A, dez.semnatura(A))[0] == 200
    assert observare.trimite_email_html_sau_semnaleaza("email invitatie cabinet", A.upper(), "Invitație iConta.eu", "<p>Corp</p>") is True
    (corp,) = mediu
    assert corp["htmlContent"] == "<p>Corp</p>" and "headers" not in corp, corp
    assert _linkul_de_dezabonare(corp["htmlContent"]) is None


def test_alerta_catre_admin_n_are_dezabonare_si_pleaca(mediu, monkeypatch):
    monkeypatch.setenv("ICONTA_ALERTA_EMAIL", B)
    uc_public.dezabonare_confirma(B, dez.semnatura(B))
    assert observare._trimite_brevo("Proba 268", "Mesaj") is True
    (corp,) = mediu
    assert corp["to"] == [{"email": B}] and corp["textContent"] == "Mesaj" and "headers" not in corp, corp


def test_resetarea_parolei_e_tranzactionala(mediu, monkeypatch):
    """Drumul aplicației (`reset_parola_cere`), cu contul înlocuit (adresa sintetică n-are cont)."""
    from core import reset_parola, repo_admin
    monkeypatch.setattr(reset_parola, "cere_reset", lambda conn, email: ("tok-proba", {"user_id": 0, "nume": "Test 253", "prenume": None,
                                                                                       "email": A}))
    monkeypatch.setattr(repo_admin, "scrie_audit_reset_cerut", lambda cur, uid: None)
    uc_public.reset_parola_cere(types.SimpleNamespace(email=A))
    (corp,) = mediu
    assert corp["to"] == [{"email": A}] and corp["subject"] == "Resetare parola iConta.eu"
    assert corp["htmlContent"].startswith("<p>Bună Test 253,</p>")             # [269] numele întreg, nu „253”
    assert _linkul_de_dezabonare(corp["htmlContent"]) is None and "headers" not in corp


# ── 3. informativele: cu dezabonare ───────────────────────────────────────────────────────────────────────────────────────────────
def test_emailul_informativ_are_subsolul_si_antetele(mediu):
    assert observare.trimite_email_html(A, "Proba 268", "<p>Corp</p>", informativ=True) is True
    (corp,) = mediu
    link = dez.link(A)
    assert link.startswith("https://iconta.eu/public/dezabonare?e=ana%40proba-dezabonare.test&s=")
    assert corp["headers"] == {"List-Unsubscribe": "<%s>" % link, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    assert corp["htmlContent"].startswith("<p>Corp</p>")
    assert _linkul_de_dezabonare(corp["htmlContent"]) == link


def test_informativul_nu_pleaca_la_adresa_dezabonata(mediu, capsys):
    cod, _ = uc_public.dezabonare_confirma(A, dez.semnatura(A))
    assert cod == 200 and _sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (A,)) == [(1,)]
    assert observare.trimite_email_html(A.upper(), "Sinteza zilei", "<p>x</p>", informativ=True) is False   # adresa, oricum ar fi scrisă
    assert mediu == []
    assert "[email netrimis, adresa %s s-a dezabonat de la emailurile informative iConta.eu]" % A in capsys.readouterr().out
    from core import uc_comun
    assert uc_comun._trimite_recomandari([A, B], "<p>Recomandare</p>", "O recomandare") == [
        {"email": A, "stare": "dezabonat"}, {"email": B, "stare": "trimis"}]
    assert [c["to"] for c in mediu] == [[{"email": B}]]


def test_registrul_necitibil_opreste_informativul_nu_tranzactionalul(mediu, monkeypatch):
    def _cade(email):
        raise RuntimeError("baza nu răspunde")
    monkeypatch.setattr(observare, "adresa_dezabonata", _cade)
    assert observare.trimite_email_html(A, "Sinteza zilei", "<p>x</p>", informativ=True) is False
    assert mediu == []
    from core import uc_comun
    assert uc_comun._trimite_recomandari([A], "<p>x</p>", "O recomandare") == [{"email": A, "stare": "esuat"}]   # necunoscut ≠ dezabonat
    assert observare.trimite_email_html(A, "Resetare parola iConta.eu", "<p>x</p>") is True
    assert [c["to"] for c in mediu] == [[{"email": A}]]


# ── 4. pagina publică ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pagina_semnatura_get_post(mediu):
    for e, s in ((A, dez.semnatura(B)), (A, ""), ("", ""), (A, dez.semnatura(A)[:-1] + "x")):
        assert uc_public.dezabonare_pagina(e, s)[0] == 400 and uc_public.dezabonare_confirma(e, s)[0] == 400
    (mesaj,) = _Elemente(uc_public.dezabonare_pagina(A, dez.semnatura(B))[1]).cu_id("dz-mesaj")
    assert mesaj[2] == uc_public.MESAJ_DEZABONARE_LINK_INVALID
    cod, pagina = uc_public.dezabonare_pagina(A, dez.semnatura(A))
    el = _Elemente(pagina)
    (buton,) = el.cu_id("dz-confirma")
    (formular,) = [e for e in el.toate if e[0] == "form"]
    assert cod == 200 and buton[0] == "button" and formular[1]["method"] == "post"
    assert formular[1]["action"] == "/public/dezabonare?e=ana%40proba-dezabonare.test&s=" + dez.semnatura(A)
    assert dez.MESAJ_CE_RAMANE in el.texte("p")                               # pagina spune ce vine în continuare
    assert _sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (A,)) == [(0,)]   # GET nu dezabonează
    assert uc_public.dezabonare_confirma(A, dez.semnatura(A))[0] == 200
    assert uc_public.dezabonare_confirma(A, dez.semnatura(A))[0] == 200     # a doua oară: tot dezabonată, fără eroare
    assert _sql("SELECT count(*) FROM public.emailuri_dezabonate WHERE email = %s", (A,)) == [(1,)]
    cod, pagina = uc_public.dezabonare_pagina(A, dez.semnatura(A))
    el = _Elemente(pagina)
    assert cod == 200 and el.cu_id("dz-confirma") == []
    assert el.cu_id("dz-mesaj")[0][2] == "Adresa %s e deja dezabonată de la emailurile informative iConta.eu." % A


def test_semnatura_e_a_adresei_si_a_scopului(monkeypatch):
    assert dez.semnatura_valida(" Ana" + DOMENIU.upper(), dez.semnatura(A))     # aceeași adresă, normalizată
    assert not dez.semnatura_valida(B, dez.semnatura(A))
    import base64
    import hashlib
    import hmac
    direct = base64.urlsafe_b64encode(hmac.new(os.environ["JWT_SECRET"].encode(), A.encode(), hashlib.sha256).digest()).rstrip(b"=")
    assert dez.semnatura(A) != direct.decode()                                  # cheia e derivată pe scop, nu JWT_SECRET gol-goluț
    monkeypatch.setenv("JWT_SECRET", "")
    with pytest.raises(RuntimeError):
        dez.semnatura(A)                                                        # cheie goală = refuz, nu semnătură forjabilă
