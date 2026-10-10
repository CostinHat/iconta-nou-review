# -*- coding: utf-8 -*-
"""GARD — un clic al contabilului nu se pierde (comanda Costin 10.10.2026 pct.8, verbatim: „Clasa «butoane legate după o cerere
așteptată»: măsoar-o pe toate ecranele și repar-o unde apare, cu gard. Un clic al contabilului nu se pierde nicăieri.”)

Clasa: un buton ajunge în pagină, funcția așteaptă o cerere (`await`, `.then`), și abia apoi îi leagă clicul. Cât durează cererea,
butonul e pe ecran și nu face nimic. Detectorul (`scripts/scan_legari_await.js`) citește arborele sintactic al fiecărui fișier din
`static/js` (acorn), deci vede și șabloanele imbricate, legările prin `forEach` și pe cele dintr-o funcție interioară.

Limita, declarată: un element pus în pagină de o funcție ajutătoare care întoarce HTML se vede numai ca „randare necunoscută”;
legarea lui e judecată atunci față de ultima randare din funcție (al doilea test). Cursa propriu-zisă nu se probează stabil în
browser — iese la întâmplare —, deci gardul e pe forma codului (ca `test_retestul_plasei::test_jurnalul_si_inchiderea_...`).
"""
import json
import os
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_legari_await.js")


def _scan(*fisiere):
    r = subprocess.run(["node", _SCAN, *fisiere], cwd=_RAD, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, "detectorul nu a putut citi sursele (fail-closed): %s" % r.stderr[-500:]
    return json.loads(r.stdout)


def test_niciun_buton_nu_se_leaga_dupa_o_cerere_asteptata():
    """Măsurat pe 10.10.2026: 2 legări pe toate ecranele („Închide” / „Redeschide evidența facturilor” din „Închidere lună”, legate
    după cererile controalelor și ale blocării) — reparate. MUTAȚIE: legarea lor mutată înapoi după `await legaBlocareLuna` -> pică."""
    gasite = _scan()
    assert not gasite, "Butoane legate după o cerere așteptată (clicul dat între timp se pierde):\n" + "\n".join(
        "  %(fisier)s:%(legat)s %(selector)s — randat la %(randat)s, așteptat la %(asteptat)s" % g for g in gasite)


def test_detectorul_are_dinti(tmp_path):
    """Fiecare formă a clasei e prinsă; legarea făcută înaintea cererii și randarea de după cerere trec."""
    f = tmp_path / "proba.js"
    f.write_text(
        'export async function f1(c) { c.innerHTML = `<button id="b1">x</button>`; await api.get("/x");'
        ' c.querySelector("#b1").addEventListener("click", g); }\n'
        'export function f2(c) { c.innerHTML = `<button id="b2">x</button>`; const inc = async () => { await api.get("/y");'
        ' c.querySelector("#b2").onclick = g; }; inc(); }\n'
        'export function f3(c) { c.innerHTML = `<button data-sterge="1">x</button>`; api.get("/z").then((r) => {'
        ' c.querySelectorAll("[data-sterge]").forEach((b) => b.addEventListener("click", g)); }); }\n'
        'export async function f4(c) { c.innerHTML = `<p>${a ? `<button class="buton-x">x</button>` : ""}</p>`; await 1;'
        ' c.querySelector(".buton-x")?.addEventListener("click", g); }\n'
        'export async function ok1(c) { c.innerHTML = `<button id="b5">x</button>`; c.querySelector("#b5").addEventListener("click", g);'
        ' await api.get("/x"); }\n'
        'export async function ok2(c) { await api.get("/x"); c.innerHTML = `<button id="b6">x</button>`;'
        ' c.querySelector("#b6").addEventListener("click", g); }\n', encoding="utf-8")
    assert sorted(g["selector"] for g in _scan(str(f))) == ["#b1", "#b2", ".buton-x", "[data-sterge]"]


def test_forma_veche_a_jurnalului_e_prinsa():
    """Calibrare pe cazul care a deschis clasa (deficiențele 58 și 96): jurnalul de dinainte de dc5e44df își lega butoanele după
    `await legaBlocareLuna(...)`. Detectorul trebuie să vadă cele opt legări de atunci."""
    vechi = subprocess.run(["git", "show", "445f9932:static/js/ecrane/firme.js"], cwd=_RAD, capture_output=True, text=True)
    assert vechi.returncode == 0, vechi.stderr
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as t:
        t.write(vechi.stdout)
    try:
        sel = sorted(g["selector"] for g in _scan(t.name))
    finally:
        os.unlink(t.name)
    assert sel == sorted(["#il-fac-inchide", "#il-fac-redeschide", "#il-prev", "#il-next",
                          "#j-prev", "#j-next", "#j-nota-noua", "#j-amort"]), sel
