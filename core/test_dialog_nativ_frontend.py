# -*- coding: utf-8 -*-
"""GARD (09.08.2026): dialoguri native alert()/prompt()/confirm() INTERZISE in TOT frontendul (DS cap.5:
"confirm(), alert() si prompt() native de browser sunt INTERZISE"). Verificatorul (regula DIALOG_BROWSER)
scaneaza DOAR static/js/ecrane/*.js -> static/js/*.js (app.js / navigator.js / sesiune.js / api.js) scapau
controlului; app.js avea alert() pe caile de eroare magic-login (o oprire adusa userului ca dialog nativ
generic/blocant, in loc de mesaj canonic in-ecran). Acest gard acopera AMBELE zone.
Confirmari = confirmaCaseta; input = formular in-ecran. Mutatie: un alert(/prompt(/confirm( nativ nou -> rosu."""
import re, glob, os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# alert(/prompt( = apel; confirm( doar cel NATIV (lookbehind pe "confirma" -> ignora confirmaCaseta)
_DLG = re.compile(r"\balert\s*\(|\bprompt\s*\(|(?<!confirma)\bconfirm\s*\(")


def _fisiere_js():
    return (sorted(glob.glob(os.path.join(_RAD, "static/js/ecrane/*.js"))) +
            sorted(glob.glob(os.path.join(_RAD, "static/js/*.js"))))


def _in_comentariu(src, pos):
    # comentariu de linie: // inaintea pozitiei pe aceeasi linie (dar nu ://)
    ls = src.rfind("\n", 0, pos) + 1
    pre = src[ls:pos]
    i = pre.find("//")
    while i != -1:
        if i == 0 or pre[i - 1] != ":":
            return True
        i = pre.find("//", i + 2)
    # comentariu bloc: ultimul /* inainte de pos nu are un */ intre el si pos
    ob = src.rfind("/*", 0, pos)
    cb = src.rfind("*/", 0, pos)
    return ob != -1 and ob > cb


def test_niciun_dialog_nativ_in_frontend():
    hits = []
    for f in _fisiere_js():
        src = open(f, encoding="utf-8").read()
        for m in _DLG.finditer(src):
            if _in_comentariu(src, m.start()):
                continue
            ln = src[:m.start()].count("\n") + 1
            hits.append("%s:%d  %s" % (os.path.basename(f), ln, " ".join(src[m.start():m.start() + 45].split())))
    assert not hits, ("dialog nativ (alert/prompt/confirm) in frontend - DS cap.5 INTERZIS. Confirmari via "
                      "confirmaCaseta; input via formular in-ecran; erori via arataMesaj/caseta canonica:\n"
                      + "\n".join(hits))


def test_ratchet_mig_gol_nu_creste():
    """RATCHET: `.mig-gol` (clasa ad-hoc deprecata pt mesaje de stare, DS cap.6: "mig-gol NU se mai foloseste
    pentru stari goale... datorie de migrat la arataMesaj") NU trebuie sa creasca. Load-error-urile au fost
    migrate la ecran-nota (asistenti Calitate / firme Verificari / admin_activitate istoric). Cele 3 ramase
    (firme.js: r.mesaj rezultat descarcare, lista alerte, nota-avertisment factura) = CONTINUT, nu opriri;
    se migreaza separat. La reparare, coboara BASELINE. Mutatie: un mig-gol NOU -> rosu."""
    BASELINE = 3   # 09.08.2026, dupa migrarea celor 3 load-error la ecran-nota
    n = sum(open(f, encoding="utf-8").read().count("mig-gol") for f in _fisiere_js())
    assert n <= BASELINE, ("mig-gol NOU (%d > %d): mesaj de stare prin clasa ad-hoc (DS cap.6). "
                           "Foloseste arataMesaj (stare tranzitorie) sau ecran-nota (eroare de load)." % (n, BASELINE))
