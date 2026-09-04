# -*- coding: utf-8 -*-
"""[R131, 04.09.2026] INSTRUMENT: un `fetch` direct care ARUNCA motivul serverului.

## Ce masoara

Raspunsurile binare (PDF, XML, ZIP, imagine) nu pot trece prin `api.get` — deci ecranele care
descarca un fisier cheama `fetch` direct, si ocolesc si `_refuzNevazut` din `api.js`. Intrebarea
e ce fac cand serverul refuza. Masurat la 04.09.2026, **toate 13** aveau aceeasi forma:

    if (!r.ok) throw new Error("eroare " + r.status);

adica *aruncau motivul serverului si puneau in locul lui propriul numar*. Serverul spunea
„chitanta inexistenta"; omul citea „eroare 404", iar la doua locuri „Eroare — reincearca" — un
sfat care nu poate reusi, fiindca factura tot nu exista la a doua apasare.

## Cum masoara — si de ce nu pe text

Nu exista AST de JavaScript in Python, deci analiza e pe linii. Ca sa nu fie „`sir` in text"
(clichetul 50, METODA §23), instrumentul lucreaza pe o STRUCTURA pe care si-o construieste
singur: pentru fiecare `fetch(` isi delimiteaza blocul (pana la urmatorul `fetch(` sau la
sfarsitul functiei), gaseste in el ramurile de esec (`if (!X.ok)`, `if (X.status`, `r.ok ?`),
si intreaba daca pe DRUMUL de la refuz la om se citeste corpul raspunsului (`.json()`/`.text()`
INAINTE de `throw`/de afisare).

## Ce NU vede, declarat

  * `fetch`-uri care nu se uita deloc la `.ok` — aceea e alta clasa (raspunsul ignorat), nu asta.
    Singurul din cod, `login.js` `/api/eveniment-public`, e telemetrie `keepalive` deliberat
    tacuta si nu intra in masuratoare.
  * ce se intampla cu eroarea DUPA ce e aruncata — daca apelantul o inghite in `catch {}`, asta
    e treaba lui `scan_refuz_tacut.py` (27.08.2026), care masoara exact acel drum.
  * `fetch` in fisiere care nu sunt sub `static/js/`.
"""
import io
import os
import re
import glob

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: `api.js` — el e stratul care DA motivul (`cereBlob` de acolo e chiar reparatia).
#: `versiune.js` — singura cerere din aplicatie care nu merge la o ruta, ci la un FISIER STATIC
#: (`/static/versiune.json`). N-are `detail` de citit, iar omul n-o cere: e sonda care afla daca
#: s-a publicat o versiune noua. *Ce nimeni n-a cerut n-are cui sa raporteze.*
_EXCEPTATE = {"api.js", "versiune.js"}

#: Cat de departe se uita dupa un `fetch(` ca sa-i gaseasca ramura de esec. Masurat pe cele 31
#: de apeluri din 04.09.2026: cea mai lunga distanta reala intre `fetch(` si `if (!x.ok)` e de
#: 5 linii (corpul cererii scris pe mai multe randuri). 30 lasa loc larg fara sa inghita
#: apelul urmator — iar daca il inghite, blocul se taie oricum la urmatorul `fetch(`.
FEREASTRA = 30

_FETCH = re.compile(r"\bfetch\s*\(")
#: Orice ATINGERE a raspunsului, nu doar `if (!x.ok)`. Calibrat pe `app.js`, unde refuzul se
#: trateaza in lant (`.then((r) => r.json().then((d) => ({ ok: r.ok, d }))))`): forma aceea era
#: clasata „fara ramura de esec", desi face exact ce trebuie. Un instrument care pune un caz bun
#: intr-o categorie gresita minte si cand nu acuza pe nedrept (METODA §22).
_ESEC = re.compile(r"\.ok\b|\.status\b")
_CITESTE_CORP = re.compile(r"\.(json|text)\s*\(\s*\)")


def blocuri(text):
    """Taie textul in blocuri, unul per `fetch(`. Blocul unui `fetch` tine pana la urmatorul
    `fetch(` sau pana la `FEREASTRA` linii — ce vine primul. *Un bloc care ar inghiti apelul
    urmator ar raporta despre doua cereri deodata, si n-ar mai fi o masuratoare.*"""
    linii = text.split("\n")
    porniri = [i for i, l in enumerate(linii) if _FETCH.search(l)]
    for k, i in enumerate(porniri):
        stop = min(i + FEREASTRA, len(linii))
        if k + 1 < len(porniri):
            stop = min(stop, porniri[k + 1])
        yield i + 1, linii[i:stop]


def analizeaza_text(text, nume="<text>"):
    """(mute, cu_motiv, fara_ramura) — trei liste de (nume, linie, prima_linie).

    * **mute**: au ramura de esec, dar nu citesc corpul inainte s-o trateze.
    * **cu_motiv**: citesc corpul pe drumul de esec.
    * **fara_ramura**: nu se uita deloc la raspuns (alta clasa, se raporteaza separat).
    """
    mute, cu_motiv, fara = [], [], []
    for nr, bloc in blocuri(text):
        corp = "\n".join(bloc)
        m = _ESEC.search(corp)
        intrare = (nume, nr, bloc[0].strip()[:80])
        if not m:
            fara.append(intrare)
            continue
        # de la linia refuzului incolo: se citeste corpul inainte de `throw`/afisare?
        dupa = corp[m.start():]
        pana_la_throw = dupa.split("throw")[0] if "throw" in dupa else dupa
        inainte = corp[:m.start()]
        if _CITESTE_CORP.search(pana_la_throw) or _CITESTE_CORP.search(inainte):
            cu_motiv.append(intrare)
        else:
            mute.append(intrare)
    return mute, cu_motiv, fara


def scaneaza(radacina=None):
    """La fel, peste tot `static/js/`. `api.js` e EXCLUS: el e stratul care da motivul, nu unul
    care il pierde — `cereBlob` de acolo e chiar reparatia."""
    rad = radacina or os.path.join(_RAD, "static", "js")
    mute, cu_motiv, fara = [], [], []
    for f in sorted(glob.glob(os.path.join(rad, "**", "*.js"), recursive=True)):
        if os.path.basename(f) in _EXCEPTATE:
            continue
        rel = os.path.relpath(f, _RAD).replace("\\", "/")
        a, b, c = analizeaza_text(io.open(f, encoding="utf-8").read(), rel)
        mute += a
        cu_motiv += b
        fara += c
    return mute, cu_motiv, fara


if __name__ == "__main__":
    m, c, f = scaneaza()
    print("MUTE (arunca motivul serverului): %d" % len(m))
    for x in m:
        print("   %s:%d  %s" % x)
    print("CU MOTIV: %d" % len(c))
    print("FARA RAMURA DE ESEC (alta clasa): %d" % len(f))
    for x in f:
        print("   %s:%d  %s" % x)
