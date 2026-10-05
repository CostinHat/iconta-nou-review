# -*- coding: utf-8 -*-
"""GARD — un contabil nu pierde ce a completat (comanda Costin 05.10.2026, pct.1).

Costin: *„un contabil nu pierde niciodată ce a completat — nici la expirarea sesiunii, nici la publicare, nici când e trimis să
completeze altceva. Se aplică tuturor formularelor; un mesaj nu promite ce aplicația nu face.”*

Cauzele, măsurate (DECIZII 05.10.2026):
- a) tokenul Anei a expirat la 24 h după logare, în mijlocul unei facturi; `api.js` făcea `sesiune.iesi()` la orice 401 cu sesiune
  -> aplicația se redesena de la zero;
- b) navigatorul redesena fereastra de la zero la „Înapoi” -> factura dispărea după Date firmă, deși refuzul promitea păstrarea.

Ce apără gardul:
- serverul reînnoiește o sesiune VIE (și numai pe ea): `POST /auth/reinnoieste`;
- interfața are UN drum pentru cererile cu sesiune (`_cuSesiune`): reînnoire, apoi reautentificare peste ecran și reluarea cererii;
  `sesiune.iesi()` rămâne doar pe ramura „omul a ales să iasă”;
- reînnoirea nu anunță schimbarea de sesiune (anunțul redesenează aplicația);
- navigatorul păstrează ecranul în care s-a tastat, la `deschide` și la `mergi`, și îl pune la loc la revenire;
- butonul „versiune nouă” nu reîncarcă peste un formular început.
Comportamentul complet îl probează `frontend_test/proba_fara_pierdere.py` (înainte/după, în browser). Aici se fixează STRUCTURA
care îl produce, ca să nu poată dispărea tăcut.
"""
import io
import os
import re
import time

import pytest

from core.test_drepturi_rol import _H, _cl, _db_ok, cabinet  # noqa: F401  (fixtura `cabinet` se folosește prin nume)

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")


def _js(nume):
    return io.open(os.path.join(JS, nume), encoding="utf-8").read()


# ── serverul ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def _token(cabinet, cheie="asist", **k):
    from core import auth_api
    ctx = auth_api.context_din_token(cabinet[cheie])
    return auth_api.emite_token({"id": ctx["uid"], "rol": ctx["rol"], "accounting_firm_id": ctx["firm"], **{x: v for x, v in k.items() if x == "preview"}},
                                durata=k.get("durata"), acum=k.get("acum"))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_sesiunea_vie_se_reinnoieste_cu_acelasi_utilizator(cabinet):
    from core import auth_api
    vechi = _token(cabinet, durata=24 * 3600, acum=int(time.time()) - 13 * 3600)
    r = _cl().post("/auth/reinnoieste", headers=_H(vechi))
    assert r.status_code == 200, r.text
    nou, v = auth_api.context_din_token(r.json()["token"]), auth_api.context_din_token(vechi)
    assert nou["ok"] and nou["uid"] == v["uid"] and nou["rol"] == v["rol"] and nou["iat"] > v["iat"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_sesiunea_expirata_invalidata_sau_de_previzualizare_nu_se_reinnoieste(cabinet):
    """MUTAȚIE: verificarea `sesiuni_valide_de` scoasă din `uc_auth.reinnoieste` -> sesiunea invalidată primește token nou -> pică."""
    from core import uc_auth
    cl = _cl()
    expirat = _token(cabinet, durata=60, acum=int(time.time()) - 3600)
    assert cl.post("/auth/reinnoieste", headers=_H(expirat)).status_code == 401
    pv = _token(cabinet, preview=True)
    r = cl.post("/auth/reinnoieste", headers=_H(pv))
    assert r.status_code == 403, r.text
    # parola schimbată după emiterea tokenului -> sesiunea e moartă și NU se reînnoiește
    vechi = _token(cabinet, durata=3600, acum=int(time.time()) - 600)
    with cabinet["conn"].cursor() as c:
        c.execute("SET search_path TO public")
        c.execute("UPDATE public.users SET sesiuni_valide_de = now() WHERE id = %s", (cabinet["uid_asist"],))
    r = cl.post("/auth/reinnoieste", headers=_H(vechi))
    assert r.status_code == 401 and r.json()["detail"] == uc_auth.MESAJ_REINNOIRE_INVALIDATA, r.text


# ── interfața: structura care produce comportamentul ─────────────────────────────────────────────────────────────────
def test_un_singur_drum_pentru_cererile_cu_sesiune():
    """Cele trei căi de cerere din `api.js` (JSON, blob, formular) trec prin `_cuSesiune`; `sesiune.iesi()` apare o singură dată,
    pe ramura în care omul n-a reautentificat. MUTAȚIE: o cale cu `if (r.status === 401 && token) { sesiune.iesi(); …` repusă -> pică."""
    t = _js("api.js")
    assert len(re.findall(r"await _cuSesiune\(", t)) == 3, "fiecare cale de cerere trece prin _cuSesiune"
    assert len(re.findall(r"(?m)^\s*sesiune\.iesi\(\);", t)) == 1, "sesiune.iesi() în afara drumului unic: ar pierde ecranul la 401"
    assert re.search(r"await ceraReautentificare\(\)\) return trimite\(sesiune\.token\(\)\)", t), "cererea nu se reia după reautentificare"
    assert re.search(r'fetch\("/auth/reinnoieste"', t) and re.search(r"p\.iat \+ \(p\.exp - p\.iat\) / 2", t), "reînnoirea la jumătatea duratei"


def test_reinnoirea_nu_redeseneaza_aplicatia():
    """`sesiune.reinnoieste` schimbă tokenul fără `_anunta()` — anunțul redesenează aplicația (`app.js`)."""
    t = _js("sesiune.js")
    corp = re.search(r"reinnoieste\(token, user\) \{(.*?)\n  \},", t, re.S)
    assert corp, "sesiune.reinnoieste lipsește"
    assert not re.search(r"_anunta\(", corp.group(1)), "reînnoirea anunță schimbarea -> aplicația s-ar redesena"
    assert len(re.findall(r"sesiune\.reinnoieste\(", _js("reautentificare.js") + _js("api.js"))) >= 2


def test_navigatorul_pastreaza_ecranul_in_care_s_a_tastat():
    """MUTAȚIE: păstrarea scoasă din `deschide` -> factura se pierde iar după Date firmă -> pică."""
    t = _js("navigator.js")
    assert len(re.findall(r"_dePastrat\(\)", t)) == 3, "păstrarea la deschide + mergi (+ definiția)"
    assert len(re.findall(r"sus\.pastrat = p\.pastrat \|\| null;", t)) == 3, "revenirea pe pas (buton, inapoiPas, fir)"
    assert re.search(r"replaceWith\(pastrat\.corp\)", t) and re.search(r'new CustomEvent\("nav:revenire"\)', t)
    assert re.search(r'addEventListener\("input", murdar, true\)', t)


def test_versiunea_noua_nu_reincarca_peste_un_formular_inceput():
    t = _js("versiune.js")
    assert re.search(r"window\._navAreModificari\(\)", t), "verificarea formularului început lipsește"
    assert re.search(r'addEventListener\("click", \(\) => \(formularInceput\(\) \? spuneDeCe\(\) : window\.location\.reload\(\)\)\)', t), \
        "reîncărcarea trebuie condiționată de formularul început, pe linia ascultătorului (vezi și test_versiune_publicata)"


def test_mesajul_care_promite_pastrarea_are_acoperire():
    """„Un mesaj nu promite ce aplicația nu face”: refuzul pentru capitalul social promite că factura rămâne — promisiune ținută
    de navigator (`deschide` păstrează pasul emiterii). Dacă păstrarea dispare, mesajul devine fals."""
    from core import capital_social
    assert re.search(r"factura rămâne așa cum ai scris-o", capital_social.mesaj_refuz(["forma juridică a firmei (SRL, SA etc.)"]))
    assert len(re.findall(r"_dePastrat\(\)", _js("navigator.js"))) == 3
