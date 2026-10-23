# -*- coding: utf-8 -*-
"""GARD — răspunsul unei cereri vechi nu se scrie peste cel nou (C103, găsită de Code la rularea țintită de după poarta 2 a lotului 11;
C102, zilele concediului medical, e prima ei instanță).

Clasa, din perspectiva contabilului: editează un câmp (sau dă un clic care schimbă luna, filtrul, pagina), ecranul cere din nou de la
server, iar dacă el mai editează o dată înainte de răspuns, răspunsul vechi, sosit ultimul, pune pe ecran altă cifră decât cea scrisă
(reevaluarea valutară fără soldul tocmai scris, 1010 zile de concediu, lista altei luni sub eticheta lunii alese). Mecanismul unic e
`ultimaCerere()` din `static/js/api.js`; detectorul (`scripts/scan_cerere_veche.js`, pe arborele sintactic, acorn) găsește fiecare
cerere atinsă dintr-un handler de editare și cere verificarea jetonului după ea și în fiecare `catch` din jurul ei.

Ce nu intră în clasă, cu motivul: cererile de SCRIERE pornite de un clic (butonul e blocat cât e cererea în zbor — `blocheazaButon`,
deci nu pot fi două); cererile de scriere pornite dintr-o editare se clasifică una câte una (`SCRIERI_DIN_EDITARE`), fiindcă refuzul
unei salvări nu are voie să fie ascuns ca „răspuns vechi”. Limita, declarată în detector: se urmăresc funcțiile chemate pe nume din
același fișier. Cursa propriu-zisă se probează în browser numai cu răspunsurile ținute pe loc (`page.route`): C102 în
`e2e_lot11_s9.py`, C103 în `e2e_lot11_v.py`.
"""
import json
import os
import subprocess
import tempfile

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_cerere_veche.js")

# Cererile ne-GET pornite din editarea unui câmp (`input` / `change` / ...), clasificate: o SALVARE rămâne cum e (refuzul ei se arată
# întotdeauna). Cheia: fișier::funcția care cere. O cerere nouă de felul ăsta, neclasificată, oprește poarta.
SCRIERI_DIN_EDITARE = {
    "static/js/ecrane/declaratii.js::randeazaClasificareD390›anonim›anonim": "PUT reclasificarea D390 — salvare",
    "static/js/ecrane/facturi_ecran.js::primiteSPV›anonim": "importul XML UBL al facturilor primite — salvare",
    "static/js/ecrane/facturi_ecran.js::deseneaza›anonim": "PUT opțiunea scadențarului — salvare",
    "static/js/ecrane/firme.js::deseneaza›anonim›anonim": "PUT starea zilei în pontaj — salvare",
    "static/js/ecrane/firme.js::ecranBanca›anonim": "importul extrasului bancar — salvare",
    "static/js/ecrane/firme.js::ecranRaportZ›anonim": "importul raportului Z (AMEF) și nota lui — salvare",
    "static/js/ecrane/firme.js::randeazaLista›anonim": "bonul încărcat intră ciornă și se confirmă — salvare",
    "static/js/ecrane/portal.js::laSelectie": "bonul clientului salvat ca ciornă — salvare",
}

# Cererile GET din editare lăsate fără jeton, cu motivul (gol = niciuna).
EXCEPTII = {
    "static/js/ecrane/emitere_ecran.js::trimiteEmitere": "citirea stării SPV după emitere: butonul „Emite” rămâne dezactivat după "
                                                        "succes, deci nu pot pleca două",
    "static/js/ecrane/portal.js::randeazaFormEmail›anonim": "citirea accesului după salvarea emailului, cu butonul dezactivat cât "
                                                           "durează; după succes ecranul se re-desenează",
    "static/js/ecrane/portal.js::randeazaFormAdauga›anonim": "citirea accesului după adăugarea persoanei, cu butonul dezactivat cât "
                                                            "durează; după succes ecranul se re-desenează",
    "static/js/ecrane/firme.js::legaBlocareLuna": "scrie numai în butonul și zona de mesaj ale desenului care a chemat-o; un desen nou "
                                                 "le înlocuiește (`corp.innerHTML`), deci un răspuns vechi cade pe elemente scoase din pagină",
}


def _scan(*fisiere):
    r = subprocess.run(["node", _SCAN, *fisiere], cwd=_RAD, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, "detectorul nu a putut citi sursele (fail-closed): %s" % r.stderr[-500:]
    return json.loads(r.stdout)


def _cheie(g):
    return "%s::%s" % (g["fisier"], g["functie"])


def test_nicio_cerere_din_editare_nu_scrie_un_raspuns_vechi():
    """Măsurat pe 23.10.2026: 39 de funcții cu cereri GET atinse din editare sau dintr-un clic care schimbă starea, pe 20 de fișiere —
    toate trecute pe `ultimaCerere()`. MUTAȚIE: verificarea scoasă din `deseneaza` (reevaluare) -> pică."""
    rele = [g for g in _scan() if g["metoda"] == "get" and not (g["aparat"] and g["catch_aparat"]) and _cheie(g) not in EXCEPTII]
    assert not rele, "Cereri din editare al căror răspuns vechi poate acoperi ecranul nou (mecanismul: `ultimaCerere()` din api.js):\n" + \
        "\n".join("  %(fisier)s:%(linie)s %(functie)s (din %(eveniment)s, linia %(handler)s) — după cerere: %(aparat)s, catch: %(catch_aparat)s"
                  % g for g in rele)


def test_campul_in_care_scrie_omul_nu_se_pierde_la_redesenare():
    """A doua fațetă: răspunsul unei editări re-desenează câmpurile formularului (`innerHTML` cu <input>/<select>/<textarea>) cât omul
    scrie deja în câmpul următor; fără `pastreazaCampulActiv`, ce a tastat și n-a confirmat dispare (testul ajustării manuale din
    reevaluare a picat așa). MUTAȚIE: `pastreazaCampulActiv` scos din `deseneaza` (reevaluare) -> pică."""
    rele = sorted({_cheie(g) for g in _scan() if g["metoda"] == "get" and g["eveniment"] != "click"
                   and g["redeseneaza_campuri"] and not g["pastreaza_campul"]} - set(EXCEPTII))
    assert not rele, "Răspunsuri de editare care re-desenează câmpurile fără `pastreazaCampulActiv` (api.js):\n  " + "\n  ".join(rele)


def test_scrierile_din_editare_sunt_clasificate():
    """O cerere ne-GET pornită din editarea unui câmp e ori o salvare (listată, cu motivul), ori un calcul — și atunci are jetonul."""
    noi = sorted({_cheie(g) for g in _scan() if g["metoda"] != "get" and g["eveniment"] != "click"
                  and not (g["aparat"] and g["catch_aparat"]) and _cheie(g) not in SCRIERI_DIN_EDITARE})
    assert not noi, "Cereri de scriere din editare neclasificate (salvare -> SCRIERI_DIN_EDITARE cu motivul; calcul -> jetonul):\n  " + \
        "\n  ".join(noi)


def test_clasificarile_nu_raman_in_urma():
    """O intrare din liste care nu mai corespunde niciunei cereri e o clasificare moartă — se scoate."""
    chei = {_cheie(g) for g in _scan()}
    moarte = sorted((set(SCRIERI_DIN_EDITARE) | set(EXCEPTII)) - chei)
    assert not moarte, "Clasificări fără cerere (codul s-a mutat): %s" % moarte


def test_detectorul_are_dinti(tmp_path):
    """Fiecare formă a clasei e prinsă; forma reparată trece."""
    f = tmp_path / "proba.js"
    f.write_text(
        'import { api, ultimaCerere, pastreazaCampulActiv } from "../api.js";\n'
        # rele
        'export function r1(c) { const d = async () => { const r = await api.get("/a"); c.innerHTML = r; };'
        ' c.querySelector("#x").addEventListener("change", d); }\n'
        'export function r2(c) { const cn = ultimaCerere(); const d = async () => { const a = cn(); try { const r = await api.get("/b");'
        ' if (!a()) return; c.innerHTML = r; } catch (e) { c.innerHTML = "eroare"; } };'
        ' c.querySelector("#x").addEventListener("input", d); }\n'
        'export function r3(c) { const d = async () => { const cn = ultimaCerere(); const a = cn(); const r = await api.get("/c");'
        ' if (!a()) return; c.innerHTML = r; }; c.querySelector("#x").addEventListener("change", d); }\n'
        'export function r4(c) { let luna = 1; const d = async () => { const r = await api.get("/d?l=" + luna); c.innerHTML = r; };'
        ' c.querySelector("#n").addEventListener("click", () => { luna += 1; d(); }); }\n'
        'export function r5(c) { let t = null; c.querySelector("#q").addEventListener("input", () => { clearTimeout(t);'
        ' t = setTimeout(async () => { const r = await api.get("/e"); c.innerHTML = r; }, 500); }); }\n'
        'export function r6(c) { c.querySelector("#q").oninput = () => api.get("/f").then((r) => { c.innerHTML = r; }); }\n'
        # bune
        'export function b1(c) { const cn = ultimaCerere(); const d = async () => { const a = cn(); try { const r = await api.get("/g");'
        ' if (!a()) return; c.innerHTML = r; } catch (e) { if (!a()) return; c.innerHTML = "eroare"; } };'
        ' c.querySelector("#x").addEventListener("change", d); }\n'
        'export function b2(c) { c.querySelector("#v").addEventListener("click", async () => { const r = await api.get("/h");'
        ' c.innerHTML = r; }); }\n'
        'export function b3(c) { const deseneaza = async () => { await api.get("/i"); }; c.innerHTML = ""; }\n'
        'export function r7(c) { const cn = ultimaCerere(); const d = async () => { const a = cn(); const r = await api.get("/j");'
        ' if (!a()) return; c.innerHTML = `<input id="v" value="${r}">`; }; c.querySelector("#x").addEventListener("change", d); }\n'
        'export function r8(c) { const cn = ultimaCerere(); const d = async () => { const a = cn(); try { const r = await api.get("/m");'
        ' c.innerHTML = r; } catch (e) { if (!a()) return; c.innerHTML = "eroare"; } };'
        ' c.querySelector("#x").addEventListener("change", d); }\n'
        'export function r9(c) { const cn = ultimaCerere(); const fa = (r) => { c.innerHTML = `<input id="v" value="${r}">`; };'
        ' const d = async () => { const a = cn(); try { const r = await api.get("/n"); if (!a()) return; fa(r); } catch (e) {'
        ' if (!a()) return; pastreazaCampulActiv(c, () => fa("")); } }; c.querySelector("#x").addEventListener("change", d); }\n'
        'export function b5(c) { const cn = ultimaCerere(); const d = async () => { const a = cn(); const r = await api.get("/k");'
        ' if (!a()) return; pastreazaCampulActiv(c, () => { c.innerHTML = `<input id="v" value="${r}">`; }); };'
        ' c.querySelector("#x").addEventListener("change", d); }\n'
        'export function b6(c) { const d = async () => { const a = ultimaCerere(c)(); const r = await api.get("/l");'
        ' if (!a()) return; c.innerHTML = r; }; c.querySelector("#x").addEventListener("change", d); }\n'
        'export function b4(c) { const deseneaza = () => { c.innerHTML = "nimic"; }; c.querySelector("#x").addEventListener("change", deseneaza); }\n',
        encoding="utf-8")
    gasite = _scan(str(f))
    pe_linie = {}
    for g in gasite:
        pe_linie.setdefault(g["handler"], []).append(g)
    linii = f.read_text(encoding="utf-8").splitlines()
    rau = lambda n: any(not (g["aparat"] and g["catch_aparat"]) or (g["redeseneaza_campuri"] and not g["pastreaza_campul"])   # noqa: E731
                        for g in pe_linie.get(n, []))
    for nr, txt in enumerate(linii, 1):
        if txt.startswith("export function r"):
            assert rau(nr), "forma %s nu e prinsă" % txt[16:18]
        if txt.startswith("export function b"):
            assert not rau(nr), "forma bună %s e prinsă greșit" % txt[16:18]
    b2 = [i for i, t in enumerate(linii, 1) if t.startswith("export function b2")][0]
    assert b2 not in pe_linie, "clicul care nu schimbă starea nu intră în clasă"


def test_formele_vechi_sunt_prinse():
    """Calibrare pe cazurile care au deschis clasa: reevaluarea și certificatul de concediu din versiunea publicată (22c71846)."""
    for cale, functie in (("static/js/ecrane/reevaluare_ecran.js", "deseneaza"), ("static/js/ecrane/flux_concediu.js", "recalcZile")):
        vechi = subprocess.run(["git", "show", "22c71846:" + cale], cwd=_RAD, capture_output=True, text=True)
        assert vechi.returncode == 0, vechi.stderr
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as t:
            t.write(vechi.stdout)
        try:
            g = [x for x in _scan(t.name) if x["functie"] == functie and x["metoda"] == "get"]
        finally:
            os.unlink(t.name)
        assert g and not all(x["aparat"] and x["catch_aparat"] for x in g), (cale, g)


def test_mecanismul_lasa_numai_ultima_cerere():
    """`ultimaCerere()`: jetonul luat mai devreme nu mai e „actual” după ce a pornit altă cerere; fabrici diferite nu se încurcă.
    (api.js atinge `document` la încărcare, deci în node rulează numai funcția, extrasă din sursă.)"""
    src = open(os.path.join(_RAD, "static", "js", "api.js"), encoding="utf-8").read()
    i = src.index("const _fabriciPeElement")
    functia = src[i:src.index("\n}\n", src.index("export function ultimaCerere(", i)) + 3].replace("export ", "", 1)
    cod = functia + ("const f = ultimaCerere(), g = ultimaCerere();\n"
                     "const a = f(); const b = f(); const c = g();\n"
                     "const e1 = {}, e2 = {}; const x = ultimaCerere(e1)(); const y = ultimaCerere(e2)(); const z = ultimaCerere(e1)();\n"
                     "console.log(JSON.stringify([a(), b(), c(), x(), y(), z(), ultimaCerere(e1) === ultimaCerere(e1)]));\n")
    r = subprocess.run(["node", "-e", cod], cwd=_RAD, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    # pe element: același element -> aceeași fabrică (x depășit de z); alt element -> neatins (y rămâne actual)
    assert json.loads(r.stdout.strip()) == [False, True, True, False, True, True, True]
