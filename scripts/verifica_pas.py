# -*- coding: utf-8 -*-
"""scripts/verifica_pas.py — verificatorul pe pas al jurnalului de verificare (comanda 16.1, pct.3). Face un pas pe serverul de lucru (8019), ia JSON-ul ecranului
(cererea GET a ecranului) și captura paginii, compară JSON-ul cu așteptarea pasului și scrie rândul în docs/dovezi/<lot>/jurnal_verificare.csv. VERDICTUL îl scrie această
comparație (trece / pică), nu executorul; `neexecutat` = pasul n-a putut rula (server căzut, captură imposibilă). Un rând fără captură existentă, cu mtime în intervalul
declarat (inceput–sfarsit), se refuză (control încrucișat în scripts/jurnal_verificator.sh).
  verifica_pas.py --lot 16.1-C3 --pas P1 --actiune "<text>" --json-url /public/config --pasi docs/dovezi/16_1_C3/pasi.json --asertiune P1 [--pagina /] [--baza http://127.0.0.1:8019] [--csv cale]
Oracolul (16.1-C3, pct.1): așteptarea vine din pasi.json, nu din linia de comandă. Fiecare asertiune are „operator” și „valoare” (copiate literal din pasi_<lot>.txt al arhitectului: acolo sunt
singurele coloane comparate, „descriere” nu) și „cheie” (a lui Code): cheia JSON a ecranului (cu puncte pentru cuib) sau o sursă `text:<url>` (corpul răspunsului) / `dom:<selector css>`
(elementele paginii: nr_randuri = câte sunt, activ = primul e activ, interval_px = înălțimile lor, text = textul lor). Compararea e `compara_asertiune(operator, valoare, observat)`, fără altă interpretare.
„valoare” (16.5) = valoarea curentă brută (`.value`, fără trim) a câmpurilor de formular (input în afara checkbox/radio/button/submit/reset/image/file, textarea, select); un câmp se judecă prin valoare, nu prin text
(„text” citește `textContent`, gol la <input>); un element fără valoare sau niciun element = „pică” cu motiv, pentru orice operator. Operatori: egal / contine / nr_randuri / lipseste / interval_px / activ / text_contine (definiți în antetul pasi_<lot>.txt).
Parcursul (16.3, pct.1): `verifica_pagina(pagina, lot, pas, parcurgere, verificator, pasi_json, csv)` citește starea paginii VII (sesiune autentificată, după acțiunile parcursului lui Code) prin
cheia fiecărei aserțiuni a pasului și o compară cu `compara_asertiune`; scrie câte un rând pe aserțiune (coloana „pas” = id-ul aserțiunii) și captura, ambele cu marcaj HMAC. Chei: `dom:<selector>|<masura>`
(text, numar, activ, inaltime_px, distanta_px, diferenta_latime_px, depasire, valoare), `json:<url>|<cale.in.json>` (cerut din contextul paginii, cu sesiunea ei), `pdf:<url>` sau `pdf:fisier:<cale relativă la directorul
parcurgerii>`. Marcajul: HMAC-SHA256 pe rând cu ~/.iconta/cheie_oracol (600, în afara depozitului) — urmă, nu barieră: cheia e citibilă de Code."""
import argparse
import csv
import datetime
import decimal
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPURI_VECHI = ["lot", "commit", "verificator", "inceput", "sfarsit", "pas", "actiune", "verdict", "captura", "motiv"]
#: coloanele noi (16.3) stau la sfârșitul antetului; rândurile vechi (docs/dovezi/16_1_C3/) se citesc cu r.get
CAMPURI = CAMPURI_VECHI + ["parcurgere", "marcaj", "verificator_independent", "verificator_independent_2", "mediu"]
CHEIE_ORACOL = os.environ.get("CHEIE_ORACOL_FISIER") or os.path.expanduser("~/.iconta/cheie_oracol")
SETTLE_MS = 1200
MASURI = ("text", "numar", "activ", "inaltime_px", "distanta_px", "diferenta_latime_px", "depasire", "valoare")
#: cheia obiectului întors de măsura „valoare” când elementul n-are valoare sau selectorul n-are niciun element
CHEIE_FARA_VALOARE = "__fara_valoare__"


OPERATORI = ("egal", "contine", "nr_randuri", "lipseste", "interval_px", "activ", "text_contine")


def _text(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, (list, tuple)):
        return ",".join(_text(i) for i in x)
    return "" if x is None else str(x)


def compara_asertiune(operator, valoare, observat):
    """Singura comparație a oracolului: operator + valoare (literale din fișierul arhitectului) față de ce s-a citit prin cheie. -> (verdict, motiv)."""
    val = str(valoare)
    if isinstance(observat, dict) and CHEIE_FARA_VALOARE in observat:   # măsura „valoare” pe un element fără valoare: pică pentru orice operator
        return "pica", str(observat[CHEIE_FARA_VALOARE])
    if operator == "egal":
        o = _text(observat)
        try:   # numere: cu punct și 2 zecimale, comparate ca valori exacte (1210.00 = 1210.0), nu ca text
            if re.fullmatch(r"-?\d+\.\d{2}", val) and re.fullmatch(r"-?\d+(\.\d+)?", o):
                return ("trece", "") if decimal.Decimal(o) == decimal.Decimal(val) else ("pica", "găsit %s, așteptat %s" % (o, val))
        except decimal.InvalidOperation:
            pass
        return ("trece", "") if o == val else ("pica", "găsit %r, așteptat %r" % (o, val))
    if operator == "contine" or operator == "text_contine":
        return ("trece", "") if val in _text(observat) else ("pica", "%r nu apare în %r" % (val, _text(observat)[:200]))
    if operator == "lipseste":
        return ("trece", "") if val not in _text(observat) else ("pica", "%r apare în %r" % (val, _text(observat)[:200]))
    if operator == "nr_randuri":
        n = len(observat) if isinstance(observat, (list, tuple, dict)) else (0 if observat in (None, "") else None)
        if n is None:
            return "pica", "nu e o listă: %r" % (observat,)
        return ("trece", "") if n == int(val) else ("pica", "găsit %d, așteptat %s" % (n, val))
    if operator == "interval_px":
        lo, hi = [float(x) for x in val.split("-")]
        valori = observat if isinstance(observat, (list, tuple)) else [observat]
        try:
            rele = [v for v in valori if not lo <= float(v) <= hi]
        except (TypeError, ValueError):
            return "pica", "nu e număr: %r" % (observat,)
        return ("trece", "") if valori and not rele else ("pica", "în afara %s: %r" % (val, rele or "nicio valoare"))
    if operator == "activ":
        if not isinstance(observat, bool):
            return "pica", "nu e true/false: %r" % (observat,)
        return ("trece", "") if _text(observat) == val else ("pica", "găsit %s, așteptat %s" % (_text(observat), val))
    return "pica", "operator necunoscut: %r" % operator


def citeste_cheia(raspuns, cheie):
    """Valoarea de la cheia JSON (cu puncte pentru cuib; un segment numeric indexează o listă); -> (găsit, valoare)."""
    cur = raspuns
    for p in cheie.split("."):
        if isinstance(cur, list) and p.isdigit() and int(p) < len(cur):
            cur = cur[int(p)]
        elif isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return False, None
    return True, cur


def observa(cheie, raspuns, baza, pagina):
    """Calea veche (16.1-C3, linia de comandă): cheia JSON a ecranului, `text:<url>` (corpul răspunsului) sau `dom:<selector>` (elementele paginii, în pagina deschisă aici). -> (găsit, observat)."""
    if cheie.startswith("text:"):
        return True, urllib.request.urlopen(baza + cheie[5:], timeout=20).read().decode("utf-8", "replace")
    if cheie.startswith("dom:"):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pag = b.new_page(viewport={"width": 1366, "height": 768})
            pag.goto(baza + pagina, wait_until="load", timeout=30000)
            el = pag.query_selector_all(cheie[4:])
            rez = {"n": len(el), "activ": el[0].is_enabled() if el else None, "px": [e.bounding_box()["height"] for e in el if e.bounding_box()],
                   "text": " ".join(e.inner_text() for e in el)}
            b.close()
        return True, rez
    return citeste_cheia(raspuns, cheie)


def compara(asertiune, observat):
    """Aserțiunea din pasi.json ({operator, valoare, cheie}) față de ce s-a citit. -> (verdict, motiv)."""
    if isinstance(observat, dict) and set(observat) == {"n", "activ", "px", "text"}:   # sursa dom: operatorul alege ce se compară
        op = asertiune["operator"]
        observat = {"nr_randuri": [None] * observat["n"], "activ": observat["activ"], "interval_px": observat["px"]}.get(op, observat["text"])
    return compara_asertiune(asertiune["operator"], asertiune["valoare"], observat)


def incarca_asertiune(cale, id_):
    for a in json.load(open(cale, encoding="utf-8"))["asertiuni"]:
        if a["id"] == id_:
            return a
    raise SystemExit("asertiunea %s nu e în %s" % (id_, cale))


# ---------------------------------------------------------------------------------------------------------------------------------------------
# 16.3, pct.1 — parcursul: starea paginii vii, citită prin cheie; marcajul rândului
# ---------------------------------------------------------------------------------------------------------------------------------------------
def cheie_secreta(creeaza=True):
    """Cheia HMAC a oracolului (~/.iconta/cheie_oracol, 600); creată la prima folosire (`creeaza`)."""
    if not os.path.exists(CHEIE_ORACOL):
        if not creeaza:
            return None
        os.makedirs(os.path.dirname(CHEIE_ORACOL), exist_ok=True)
        fd = os.open(CHEIE_ORACOL, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(secrets.token_hex(32) + "\n")
    return open(CHEIE_ORACOL, "rb").read().strip()


def marcaj_rand(rand):
    """HMAC-SHA256 pe toate coloanele rândului, în ordinea antetului, în afară de „marcaj”."""
    mesaj = "\x1f".join(str(rand.get(c) or "") for c in CAMPURI if c != "marcaj").encode("utf-8")
    return hmac.new(cheie_secreta(), mesaj, hashlib.sha256).hexdigest()


def marcaj_valid(rand):
    """Marcajul rândului e cel calculat de oracol; fără cheie pe disc sau fără marcaj = nevalid."""
    m = (rand.get("marcaj") or "").strip()
    if not m or cheie_secreta(creeaza=False) is None:
        return False
    return hmac.compare_digest(m, marcaj_rand(rand))


def marcaj_faza(rand):
    """HMAC-SHA256 (aceeași cheie) pe un rând al jurnalului de faze (lot, faza, eveniment, ora, sha, rezultat, id, pid, detalii fără „marca=”). 16.3-A pct.1."""
    camp = list(rand) + [""] * (9 - len(rand))
    detalii = re.sub(r"\s?marca=[0-9a-f]{64}$", "", camp[8])
    return hmac.new(cheie_secreta(), "\x1f".join(map(str, camp[:8] + [detalii])).encode("utf-8"), hashlib.sha256).hexdigest()


def scrie_faza(lot, faza, eveniment, rezultat="-", id_=None, detalii="", sha=None, pid=None):
    """Scrie în jurnalul de faze (cale_jurnal(): LOT_JURNAL sau jurnalul comun) un rând cu marcaj de oracol — numai lansatorul scrie așa faza „verificator” (16.3-A pct.1). -> id-ul rulării."""
    id_ = id_ or "%d-%d" % (os.getpid(), time.time() * 1000)
    rand = [lot, faza, eveniment, JL._acum(), (sha or JL._sha())[:12], rezultat, id_, str(pid or os.getpid()), detalii]
    rand[8] = (detalii + " marca=" + marcaj_faza(rand)).strip()
    JL._scrie(JL.cale_jurnal(), rand)
    return id_


def faza_marcata_valida(rand):
    """Rândul de jurnal are marcajul scris de `scrie_faza` (scris de mână sau copiat de la alt rând = nevalid)."""
    m = re.search(r"marca=([0-9a-f]{64})$", rand[8] if len(rand) > 8 else "")
    if not m or cheie_secreta(creeaza=False) is None:
        return False
    return hmac.compare_digest(m.group(1), marcaj_faza(rand))


def cheia_unica(rand):
    """(lot, parcurgere, pas, sha, verificator) — rândul care o repetă e refuzat (C213)."""
    return (rand.get("lot"), rand.get("parcurgere") or "", rand.get("pas"), rand.get("commit"), rand.get("verificator"))


def director_parcurgere(csv_, parcurgere, verificator):
    """docs/dovezi/<lot>/<parcurgere>/<verificator>/ — unde parcursul salvează fișierele descărcate și unde stau capturile (în `capturi/`)."""
    return os.path.join(os.path.dirname(os.path.abspath(csv_)), parcurgere, verificator)


def cale_captura(csv_, lot, parcurgere, verificator, pas, sha):
    return os.path.join(director_parcurgere(csv_, parcurgere, verificator), "capturi", "%s_%s_%s_%s.png" % (JL.L.lot_fisier(lot), parcurgere, pas, sha[:8]))


def randuri_csv(csv_):
    if not os.path.exists(csv_):
        return []
    return list(csv.DictReader(open(csv_, encoding="utf-8")))


def _scrie_randuri(csv_, randuri):
    """Rescrie fișierul întreg (antet nou) — numai pentru completarea coloanelor verificatorului independent, de către oracol."""
    with open(csv_, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPURI, lineterminator="\n", extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(randuri)


def adauga_rand(csv_, rand):
    """Adaugă un rând cu marcaj. Cheia (lot, parcurgere, pas, sha, verificator) deja în fișier = refuz (ValueError cu numele capturii existente); nimic nu se suprascrie."""
    rand = dict(rand)
    for r in randuri_csv(csv_):
        if cheia_unica(r) == cheia_unica(rand):
            raise ValueError("cheia %s există deja în %s (captura %s); un rând și o captură nu se suprascriu" % (cheia_unica(rand), os.path.basename(csv_), r.get("captura")))
    if os.path.exists(csv_) and open(csv_, encoding="utf-8").readline().strip().split(",") != CAMPURI:
        raise ValueError("antetul lui %s nu e cel al oracolului (16.3)" % csv_)
    rand["marcaj"] = marcaj_rand(rand)
    nou = not os.path.exists(csv_)
    os.makedirs(os.path.dirname(os.path.abspath(csv_)), exist_ok=True)
    with open(csv_, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPURI, lineterminator="\n", restval="")
        if nou:
            w.writeheader()
        w.writerow(rand)


def completeaza_independent(csv_, lot, parcurgere, sha, verificator, pas, r1, r2=None):
    """Singura cale prin care coloanele verificatorului independent intră într-un rând: oracolul rescrie rândul și îl re-marchează."""
    randuri = randuri_csv(csv_)
    gasit = False
    for r in randuri:
        if cheia_unica(r) == (lot, parcurgere, pas, sha, verificator):
            r["verificator_independent"] = r1
            r["verificator_independent_2"] = r2 or ""   # o reluare a verificatorului nu păstrează a doua instanță a răspunsului dinainte
            r["marcaj"] = marcaj_rand(r)
            gasit = True
    if not gasit:
        raise ValueError("rândul %s nu există în %s" % ((lot, parcurgere, pas, sha, verificator), csv_))
    _scrie_randuri(csv_, randuri)


def refuzuri_rand(r, rad=None, exceptat=False):
    """Controlul unui rând din CSV: captura există și (în afara loturilor exceptate din publica_lot.py) marcajul e valid. -> motivele de refuz."""
    ref = []
    cap = r.get("captura") or ""
    if r.get("verdict") != "neexecutat" and not os.path.exists(cap if os.path.isabs(cap) else os.path.join(rad or RAD, cap)):
        ref.append("rândul %s: captura %s lipsește" % (r.get("pas"), cap))
    if not exceptat and not marcaj_valid(r):
        ref.append("rândul %s (%s, parcurgerea %s): verdict în afara oracolului (marcaj lipsă sau nevalid)" % (r.get("pas"), (r.get("commit") or "")[:8], r.get("parcurgere") or "-"))
    return ref


def refuzuri_csv(csv_, rad=None, exceptat=False):
    """Toate rândurile unui CSV: captura, marcajul, cheia unică. -> motivele de refuz (listă goală = curat)."""
    ref, vazute = [], {}
    for r in randuri_csv(csv_):
        ref += refuzuri_rand(r, rad, exceptat)
        k = cheia_unica(r)
        if r.get("parcurgere") and k in vazute:
            ref.append("cheia %s repetată (captura %s)" % (k, r.get("captura")))
        vazute[k] = 1
    return ref


_JS_MASURA = """([sel, masura]) => {
  const el = Array.from(document.querySelectorAll(sel));
  const cut = e => e.getBoundingClientRect();
  const rand = (a, b) => Math.abs(a.top - b.top) <= 1;
  const grupe = () => { const g = []; el.forEach(e => { const r = cut(e); const x = g.find(h => rand(h[0], r)); if (x) x.push(r); else g.push([r]); }); return g; };
  if (masura === 'text') return el.map(e => (e.textContent || '').trim().replace(/\\s+/g, ' ')).join(',');
  if (masura === 'numar') return el.map(e => (e.textContent || '').trim().replace(/\\s+/g, ' '));
  if (masura === 'activ') return el.length > 0 && el.every(e => !(e.hasAttribute('disabled') || e.getAttribute('aria-disabled') === 'true'));
  if (masura === 'inaltime_px') return el.map(e => cut(e).height);
  if (masura === 'distanta_px') { const d = []; for (let i = 1; i < el.length; i++) { const a = cut(el[i - 1]), b = cut(el[i]); if (rand(a, b)) d.push(b.left - a.right); } return d; }
  if (masura === 'diferenta_latime_px') return grupe().map(g => Math.max(...g.map(r => r.width)) - Math.min(...g.map(r => r.width)));
  if (masura === 'depasire') return el.filter(e => e.scrollWidth > e.clientWidth).length;
  if (masura === 'valoare') {
    if (!el.length) return {__fara_valoare__: 'niciun element pentru selector'};
    const fara = ['checkbox', 'radio', 'button', 'submit', 'reset', 'image', 'file'];
    const areValoare = e => e.tagName === 'TEXTAREA' || e.tagName === 'SELECT' || (e.tagName === 'INPUT' && !fara.includes((e.type || '').toLowerCase()));
    if (!el.every(areValoare)) return {__fara_valoare__: 'elementul nu are valoare'};
    return el.map(e => e.value).join(',');
  }
  throw new Error('măsură necunoscută: ' + masura);
}"""

_JS_JSON = """async (url) => {
  const t = sessionStorage.getItem('iconta_token');
  const r = await fetch(url, {credentials: 'same-origin', headers: t ? {Authorization: 'Bearer ' + t} : {}});
  if (!r.ok) throw new Error('HTTP ' + r.status + ' pe ' + url);
  return await r.json();
}"""

_JS_BYTES = """async (url) => {
  const t = sessionStorage.getItem('iconta_token');
  const r = await fetch(url, {credentials: 'same-origin', headers: t ? {Authorization: 'Bearer ' + t} : {}});
  if (!r.ok) throw new Error('HTTP ' + r.status + ' pe ' + url);
  return Array.from(new Uint8Array(await r.arrayBuffer()));
}"""


def text_pdf(octeti):
    """Textul extras dintr-un PDF — aceeași funcție pentru `pdf:<url>` și `pdf:fisier:<cale>`."""
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(octeti)).pages)


def observa_pagina(pagina, cheie, director):
    """Ce citește oracolul din pagina vie prin cheia aserțiunii (formatele din antet). -> (găsit, observat)."""
    if cheie.startswith("dom:"):
        sel, _, masura = cheie[4:].rpartition("|")
        if not sel or masura not in MASURI:
            raise ValueError("cheie dom: fără măsură cunoscută (%s): %r" % (", ".join(MASURI), cheie))
        return True, pagina.evaluate(_JS_MASURA, [sel, masura])
    if cheie.startswith("json:"):
        url, _, cale = cheie[5:].rpartition("|")
        if not url or not cale:
            raise ValueError("cheie json: cere <url>|<cale.in.json>: %r" % cheie)
        return citeste_cheia(pagina.evaluate(_JS_JSON, url), cale)
    if cheie.startswith("pdf:fisier:"):
        rel = cheie[len("pdf:fisier:"):]
        cale = os.path.normpath(os.path.join(director, rel))
        if not cale.startswith(os.path.normpath(director) + os.sep):
            raise ValueError("pdf:fisier: în afara directorului parcurgerii: %r" % rel)
        return True, text_pdf(open(cale, "rb").read())
    if cheie.startswith("pdf:"):
        return True, text_pdf(bytes(pagina.evaluate(_JS_BYTES, cheie[4:])))
    raise ValueError("cheie necunoscută (dom:/json:/pdf:): %r" % cheie)


def sha_curent():
    """Sha-ul parcurgerii: PARCURS_SHA (dat de lanseaza_verificator.py din HEAD al worktree-ului); nimeni altcineva nu-l dă."""
    return os.environ.get("PARCURS_SHA") or subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()


def verifica_pagina(pagina, lot, pas, parcurgere, verificator, pasi_json, csv):
    """Predă pagina vie oracolului: aserțiunile pasului `pas` din pasi_json, citite prin cheie și comparate cu operator + valoare. Scrie câte un rând pe aserțiune (coloana „pas” = id-ul ei) și captura, cu marcaj;
    NU aruncă excepții pe „pica” (parcursul „înainte” continuă). -> (lista [(id, verdict, motiv)], verdictul pasului: trece / pica / neexecutat)."""
    csv_ = csv
    sha = sha_curent()
    directorul = director_parcurgere(csv_, parcurgere, verificator)
    try:
        ast = [a for a in json.load(open(pasi_json, encoding="utf-8"))["asertiuni"] if (a.get("pas") or a["id"].split(".")[0]) == pas]
    except (OSError, ValueError, KeyError) as e:
        return [(pas, "neexecutat", "%s: %s" % (type(e).__name__, e))], "neexecutat"
    if not ast:
        return [(pas, "neexecutat", "pasul %r nu are aserțiuni în %s" % (pas, os.path.basename(pasi_json)))], "neexecutat"
    mediu = ";".join("%s=%s" % (k, os.environ[k]) for k in sorted(os.environ) if k.startswith(("ICONTA_", "CEAS_")) and "PAROLA" not in k and "TOKEN" not in k)
    rez = []
    for a in ast:
        t0 = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        cap = cale_captura(csv_, lot, parcurgere, verificator, a["id"], sha)
        verdict, motiv = "neexecutat", ""
        try:
            if os.path.exists(cap):
                raise ValueError("captura %s există deja pentru cheia (%s, %s, %s, %s, %s); nu se suprascrie" % (cap, lot, parcurgere, a["id"], sha[:8], verificator))
            pagina.wait_for_timeout(SETTLE_MS)   # ecranul se așază (tranzițiile aplicației) înainte de citire și de captură: prima rulare Haiku a primit o captură la jumătatea unei tranziții (cabinetul peste fereastră)
            gasit, obs = observa_pagina(pagina, a["cheie"], directorul)
            verdict, motiv = compara(a, obs) if gasit else ("pica", "cheia %s lipsește din pagină" % a["cheie"])
            os.makedirs(os.path.dirname(cap), exist_ok=True)
            pagina.screenshot(path=cap)
            adauga_rand(csv_, {"lot": lot, "commit": sha, "verificator": verificator, "inceput": t0, "sfarsit": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                               "pas": a["id"], "actiune": a.get("actiune") or "pasul %s" % pas, "verdict": verdict, "captura": os.path.relpath(cap, RAD) if cap.startswith(RAD) else cap,
                               "motiv": motiv, "parcurgere": parcurgere, "mediu": mediu})
        except Exception as e:   # noqa: BLE001 — pasul nu s-a putut executa (pagină închisă, cheie greșită, cheie repetată): „neexecutat”, nu „a trecut”; parcursul continuă  # invariant-intern-ok: oracol
            verdict, motiv = "neexecutat", "%s: %s" % (type(e).__name__, e)
        rez.append((a["id"], verdict, motiv))
    v = "neexecutat" if any(r[1] == "neexecutat" for r in rez) else ("pica" if any(r[1] == "pica" for r in rez) else "trece")
    return rez, v


# ---------------------------------------------------------------------------------------------------------------------------------------------
# calea veche, din linia de comandă (16.1-C3): o pagină nouă, fără sesiune; rămâne pentru aserțiunile pe ecrane publice
# ---------------------------------------------------------------------------------------------------------------------------------------------
def captura(url, cale):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pag = b.new_page(viewport={"width": 1366, "height": 768})
        pag.goto(url, wait_until="load", timeout=30000)
        pag.screenshot(path=cale)
        b.close()


def main(a):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lot", required=True)
    ap.add_argument("--pas", required=True)
    ap.add_argument("--actiune", required=True)
    ap.add_argument("--json-url", required=True)
    ap.add_argument("--pasi", required=True, help="docs/dovezi/<lot>/pasi.json")
    ap.add_argument("--asertiune", required=True, help="id-ul asertiunii din pasi.json")
    ap.add_argument("--pagina", default="/")
    ap.add_argument("--baza", default="http://127.0.0.1:8019")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--parcurgere", default="cli")
    ap.add_argument("--verificator", default="code")
    o = ap.parse_args(a)
    lotf = JL.L.lot_fisier(o.lot)
    csv_ = o.csv or os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    sha = sha_curent()
    cap = cale_captura(csv_, o.lot, o.parcurgere, o.verificator, o.pas, sha)
    t0 = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    verdict, motiv = "neexecutat", ""
    try:
        if os.path.exists(cap):
            raise ValueError("captura %s există deja; nu se suprascrie" % cap)
        asr = incarca_asertiune(o.pasi, o.asertiune)
        raspuns = json.load(urllib.request.urlopen(o.baza + o.json_url, timeout=20))
        gasit, obs = observa(asr["cheie"], raspuns, o.baza, o.pagina)
        verdict, motiv = compara(asr, obs) if gasit else ("pica", "cheia %s lipsește din ecran" % asr["cheie"])
        os.makedirs(os.path.dirname(cap), exist_ok=True)
        captura(o.baza + o.pagina, cap)
        adauga_rand(csv_, {"lot": o.lot, "commit": sha, "verificator": o.verificator, "inceput": t0, "sfarsit": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                           "pas": o.pas, "actiune": o.actiune, "verdict": verdict, "captura": os.path.relpath(cap, RAD) if cap.startswith(RAD) else cap, "motiv": motiv, "parcurgere": o.parcurgere})
    except Exception as e:   # noqa: BLE001 — serverul căzut, captura imposibilă sau cheie repetată: pasul nu s-a executat  # invariant-intern-ok: verificator pe pas
        verdict, motiv = "neexecutat", "%s: %s" % (type(e).__name__, e)
    print("[verifica_pas] %s %s: %s %s" % (o.lot, o.pas, verdict, motiv))
    return 0 if verdict == "trece" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
