# -*- coding: utf-8 -*-
"""GARD — textele cozii de validare urmează dreptul real (deficiența 266, comanda Costin 15.10.2026, și 265 pentru poarta vie).

266: „coada de validare îi spune asistentului fără «Poate depune» că «Declarațiile le pregătești și le depui tu»; cardul promite
«Declarații și note de validat», iar ecranul vorbește doar de declarații.” Textul de sub titlu se compune acum într-un singur loc,
`introCoada` din static/js/ecrane/validat.js, din `poate_valida` / `poate_depune` (`/eu/permisiuni`). Gardul îl rulează (node) pe TOATE
combinațiile — drept de validare, drept de depunere, administrator, validarea în doi activă / suspendată / oprită, cu sau fără note — și
cere: (1) nicio frază nu-i spune „tu” validezi celui fără „Poate valida”, nici „tu” depui celui fără „Poate depune”; (2) textul vorbește
de declarații, iar de note NUMAI când sunt note de validat (PIVOT 19.10.2026, deficiența 323); (3) celui fără un drept îi spune cine face
pasul (dreptul, pe nume) — validatorul, când e ceva de validat.

CE NU VEDE (declarat): celelalte texte ale ecranului (cardurile, titlul) — pe ele le probează testul din browser
`frontend_test/e2e/e2e_lot5_roluri.py::test_def_266_coada_spune_dreptul_real_si_vorbeste_de_note`.
"""
import itertools
import json
import os
import re
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDAT = os.path.join(RAD, "static", "js", "ecrane", "validat.js")


def _functia(src, nume):
    m = re.search(r"^export function %s\(" % nume, src, re.M)
    assert m, "%s lipsește din validat.js" % nume
    i = src.index("{", src.index(")", m.end()))
    n = 0
    for j in range(i, len(src)):
        n += {"{": 1, "}": -1}.get(src[j], 0)
        if n == 0:
            return src[m.start() + len("export "):j + 1]
    raise AssertionError("corpul lui %s nu se închide" % nume)


def _texte(src=None):
    src = src if src is not None else open(VALIDAT, encoding="utf-8").read()
    consts = "\n".join(re.findall(r"^const CINE_\w+ = .*;$", src, re.M))
    combinatii = [dict(zip(("poateValida", "poateDepune", "admin", "patruOchi", "politica", "note"), c))
                  for c in itertools.product((False, True), (False, True), (False, True), (False, True), (False, True), (0, 2))]
    js = consts + "\n" + _functia(src, "introCoada") + "\nconsole.log(JSON.stringify(%s.map((c) => [c, introCoada(c)])));" % json.dumps(
        combinatii)
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


_TU_VALIDEZI = re.compile(r"\ble validezi\b|validarea ta|ești singurul validator")
_TU_DEPUI = re.compile(r"\bdepui\b|\ble depui\b|depui singur|pregătești și depui")


def test_textul_cozii_urmeaza_dreptul_real():
    rezultate = _texte()
    assert len(rezultate) == 64, len(rezultate)   # anti-vacuu: toate combinațiile au produs un text
    rele = []
    for c, t in rezultate:
        if not c["poateValida"] and _TU_VALIDEZI.search(t):
            rele.append(("îi spune că validează el, fără «Poate valida»", c, t))
        if not c["poateDepune"] and _TU_DEPUI.search(t):
            rele.append(("îi spune că depune el, fără «Poate depune»", c, t))
        if not c["poateDepune"] and "«Poate depune»" not in t:
            rele.append(("nu spune cine depune", c, t))
        # [323, retestul 19.10.2026 — PIVOT al condiției (2), DECIZII „Comanda 9.1”] „În De depus, textul de sus vorbește tot de «notele
        # pe care asistenții le trimit la validare»”: notele se pomenesc NUMAI când sunt note de validat; validatorul se numește când e
        # ceva de validat (note, sau declarațiile cu validarea în doi activă)
        if not c["poateValida"] and (c["note"] or c["patruOchi"]) and "«Poate valida»" not in t:
            rele.append(("nu spune cine validează", c, t))
        if c["note"] and not re.search(r"\b[Nn]otele\b", t):
            rele.append(("are note de validat și nu vorbește de ele", c, t))
        if not c["note"] and re.search(r"\b[Nn]ot(a|e|ele)\b", t):
            rele.append(("nu are note de validat și vorbește de note", c, t))
        if "eclarațiile" not in t:
            rele.append(("nu vorbește de declarații", c, t))
    assert not rele, "\n".join("%s: %s -> %s" % r for r in rele[:6])


def test_textul_de_la_217_ramane():
    """[217] Cu note de validat și validarea în doi oprită, administratorul (cu ambele drepturi) citește că notele le validează el, iar
    validarea în doi privește declarațiile — fără „validarea în doi nu e pornită” fără ce anume."""
    t = dict((json.dumps(c, sort_keys=True), t) for c, t in _texte())
    k = json.dumps({"poateValida": True, "poateDepune": True, "admin": True, "patruOchi": False, "politica": False, "note": 2}, sort_keys=True)
    assert t[k].startswith("Notele de mai sus le-au pregătit asistenții: le validezi sau le respingi."), t[k]
    assert (t[k].count("validarea în doi nu e pornită"), t[k].count("validarea în doi a declarațiilor nu e pornită")) == (0, 1), t[k]


def test_CALIBRARE_textul_vechi_era_prins():
    """Textul de dinainte (deficiența 266) pus înapoi într-o ramură: gardul îl vede."""
    src = open(VALIDAT, encoding="utf-8").read()
    rau = src.replace('`Declarațiile le depune ${CINE_DEPUNE} — validarea în doi a declarațiilor nu e pornită.`',
                      '"Declarațiile le pregătești și le depui tu (validarea în doi a declarațiilor nu e pornită)."', 1)
    assert rau != src, "ancora calibrării lipsește"
    rele = [c for c, t in _texte(rau) if not c["poateDepune"] and _TU_DEPUI.search(t)]
    assert rele, "gardul nu vede textul vechi"


# ── 265: poarta drepturilor e vie ─────────────────────────────────────────────────────────────────────────────────────────────
def _js(*p):
    return open(os.path.join(RAD, "static", "js", *p), encoding="utf-8").read()


def test_poarta_drepturilor_se_reaplica_pe_ceasul_aplicatiei():
    """265: „Ecranul urmează drepturile fără re-autentificare.” Lanțul, verigă cu verigă: ceasul (versiune.js: intervalul, revenirea în
    filă, întoarcerea acasă) bate și verificările înregistrate; navigatorul înregistrează recitirea drepturilor; drepturi.js o face,
    și dacă lista s-a schimbat reaplică poarta pe toată pagina — eliberând întâi ce ascunsese, nu doar ascunzând."""
    v = _js("versiune.js")
    assert re.search(r"setInterval\(\(\) => \{ verifica\(\); bataie\(\); \}, INTERVAL_MS\)", v), "intervalul nu mai bate verificările"
    assert re.search(r'visibilityState === "visible"\) \{ verifica\(\); bataie\(\); \}', v), "revenirea în filă nu mai bate verificările"
    assert re.search(r"export function laAcasa\(\) \{\s*bataie\(\);", v), "întoarcerea acasă nu mai bate verificările"
    n = _js("navigator.js")
    assert re.search(r'_versiune\.peAcelasiCeas\("drepturi", async \(\) => \{\s*const nou = await reimprospateazaDrepturi\(\);', n)
    assert n.count("sesiune.actualizeazaInLoc(nou.bife)") == 1 and n.count("data-functie-asistent") >= 1, \
        "sesiunea / eticheta nu urmează drepturile"
    assert n.count("desktopRandator(continut, nav)") >= 1 and n.count("!window._navAreModificari()") >= 1, \
        "cardurile nu se redesenează (sau peste un formular)"
    d = _js("drepturi.js")
    corp = re.search(r"export function reaplicaDrepturi\(radacina\) \{(.*?)\n\}", d, re.S)
    assert corp and corp.group(1).count('classList.remove("drept-refuzat")') == 1 and corp.group(1).count("aplicaDrepturi(radacina)") == 1, \
        "reaplicarea nu mai eliberează ce ascunsese poarta"
    assert re.search(r"if \(_amprenta\(\) === inainte\) return null;\s*reaplicaDrepturi\(document\.body\);", d)
    s = _js("sesiune.js")
    m = re.search(r"actualizeazaInLoc\(partial\) \{(.*?)\n  \},", s, re.S)
    assert m and "_anunta" not in m.group(1), "actualizarea în loc a sesiunii redesenează aplicația (ar pierde ecranul deschis)"


def test_ecranele_care_isi_calculeaza_textele_la_desenare_se_redeseneaza_la_drepturi():
    """[265] Pe lângă poarta `data-actiune` (reaplicată pe loc), jurnalul și coada își aleg textele și butoanele LA DESENARE („de
    validat”, „Trimite la validare”, butoanele cozii): `drepturi.js` emite `iconta:drepturi` când lista s-a schimbat, iar amândouă îl
    ascultă și se redesenează. MUTAȚIE: semnalul scos din `reimprospateazaDrepturi` -> pică; ascultătorul scos din jurnal -> pică."""
    def src(c):
        return open(os.path.join(RAD, c), encoding="utf-8").read()
    dr = src("static/js/drepturi.js")
    corp = dr[dr.index("export async function reimprospateazaDrepturi"):dr.index("export function reaplicaDrepturi")]
    assert corp.count('window.dispatchEvent(new CustomEvent("iconta:drepturi"))') == 1
    fi = src("static/js/ecrane/firme.js")
    jurnal = fi[fi.index("export async function ecranJurnal("):]
    jurnal = jurnal[:jurnal.index("\n}\n")]
    assert jurnal.count('window.addEventListener("iconta:drepturi", laDrepturi)') == 1
    assert src("static/js/ecrane/validat.js").count('window.addEventListener("iconta:drepturi", corp.__laDrepturi)') == 1
