# -*- coding: utf-8 -*-
"""[257] CSP-ul paginii lasă widgetul Cloudflare Turnstile să se încarce — iar nginx-ul instalat e cel versionat.

CSP-ul nu stă în aplicație, ci în nginx (`/etc/nginx/sites-available/iconta`, root). Aplicația de probă a plasei (8019) n-are nginx în
față, deci plasa e2e n-ar vedea un CSP care blochează widgetul: pe producție formularul de înregistrare n-ar mai putea fi trimis. De aici
cele două gărzi: (1) configurația versionată (`config/nginx-iconta`) permite `challenges.cloudflare.com` exact în `script-src` și
`frame-src` (sursa: developers.cloudflare.com/turnstile/reference/content-security-policy) — originea e cea a scriptului pe care îl
încarcă aplicația (`inregistrare_libera.SCRIPT_WIDGET`); (2) fișierul instalat e IDENTIC cu cel versionat — o publicare cu Turnstile
peste un nginx vechi e roșie. Se instalează de Costin (sudo), ca `config/iconta-backup.sh`.
MUTAȚII: originea scoasă din `frame-src` -> (1) pică; un nginx instalat diferit de cel versionat -> (2) pică."""
import os
import urllib.parse

from core import inregistrare_libera as il

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSIONAT = os.path.join(RAD, "config", "nginx-iconta")
INSTALAT = "/etc/nginx/sites-available/iconta"


def _csp(text):
    """Directivele CSP-ului din `add_header Content-Security-Policy "…"`: {directivă: [surse]}."""
    (linie,) = [x for x in text.splitlines() if x.strip().startswith("add_header Content-Security-Policy")]
    valoare = linie.split('"')[1]
    return {p.split()[0]: p.split()[1:] for p in (x.strip() for x in valoare.split(";")) if p}


def test_csp_versionat_permite_turnstile():
    u = urllib.parse.urlsplit(il.SCRIPT_WIDGET)
    origine = "%s://%s" % (u.scheme, u.netloc)
    csp = _csp(open(VERSIONAT, encoding="utf-8").read())
    assert origine in csp["script-src"] and csp["frame-src"] == [origine], csp
    assert csp["default-src"] == ["'self'"] and csp["connect-src"] == ["'self'"], "CSP-ul s-a lărgit în afara widgetului: %s" % csp


def test_nginx_instalat_e_cel_versionat():
    assert open(INSTALAT, encoding="utf-8").read() == open(VERSIONAT, encoding="utf-8").read(), (
        "nginx-ul instalat diferă de config/nginx-iconta — instalează-l (Costin, sudo): sudo install -m 644 %s %s && "
        "sudo nginx -t && sudo systemctl reload nginx" % (VERSIONAT, INSTALAT))
