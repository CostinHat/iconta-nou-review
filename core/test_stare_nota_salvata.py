# -*- coding: utf-8 -*-
"""GARD — deficiența 279 (comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.4, verbatim în DECIZII): „după salvare mesajul spunea
«creată ca ciornă», dar nota a plecat singură la validare, fără să i se spună Anei [...] Starea reală a notei se spune la salvare și pe
rând; pentru o notă la validare nu se oferă ștergerea.”

CAUZA: notele scrise de cine n-are drept de validare intră în coadă în middleware (`main._autor_si_note_in_coada`), DUPĂ ce ruta a
răspuns; mesajul se compunea din răspuns, cu „ciornă” scris de mână. ACUM: middleware-ul trimite antetul `X-Iconta-La-Validare`, `api.js`
îl pune pe rezultat (`laValidare`), iar mesajele spun starea prin `stareNota` / `pasNota`.

CLASA (măsurată 16.10.2026): 22 de mesaje de după salvare în 6 fișiere de ecran (casă, chitanță, bancă, NIR, ieșire CMP, consum, inventar,
reclasificare, GV, raport Z, mijloace fixe, operațiuni speciale, factura contată, nota de închidere propusă — aceasta din textul serverului).
CE RĂMÂNE, cu motiv: etichetele butoanelor („Salvează NIR (note ciorne)”) — descriu starea la creare, care e adevărată; starea citită
din bază pe un rând (`stareNotaCasa`).
LIMITA: un mesaj care spune starea fără cuvântul „ciornă” („se validează din Registrul jurnal” singur) nu e prins de tipar.
"""
import glob
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TIPAR = re.compile(r"\(ciorn[aă]\)|\(ciorn\\u0103\)|\be ciornă\b|\bca ciornă\b|\"notă ciornă\"|\"note ciorne\"|\(ciornele \$\{|"
                   r"\(ciorna \$\{|<b>ciornă</b>|creat\w* ca ciorn")
#: eticheta unui buton descrie starea la creare („Salvează NIR (note ciorne)”), care e adevărată
_BUTON = re.compile(r"<button\b")
#: (fișier, fragmentul rândului) -> motivul pentru care rândul spune „ciornă” fără să mintă
EXCEPTII = {
    ("firme.js", 'return "notă ciornă";'): "stareNotaCasa: starea citită din bază (nota_status + coada), pe rând",
}


def _ecrane():
    for p in sorted(glob.glob(os.path.join(_RAD, "static", "js", "ecrane", "*.js"))):
        yield os.path.basename(p), io.open(p, encoding="utf-8").read().splitlines()


def test_niciun_mesaj_de_ecran_nu_afirma_ciorna_scris_de_mana():
    """MUTAȚIE: `Nota ${esc(r.nota)} a fost creată ca ciornă.` pus înapoi în ecranul Casă -> pică."""
    rele, ecrane = [], list(_ecrane())
    assert len(ecrane) > 30, "premisa: ecranele din static/js/ecrane sunt citite"
    for nume, linii in ecrane:
        for i, l in enumerate(linii, 1):
            s = l.strip()
            if s.startswith("//") or _BUTON.search(l) or not TIPAR.search(l):
                continue
            if any(n == nume and frag in l for (n, frag) in EXCEPTII):
                continue
            rele.append("%s:%d %s" % (nume, i, s[:120]))
    assert rele == [], rele


def test_exceptiile_inca_exista():
    """O excepție a cărei linie a dispărut se scoate din listă (altfel lista crește tăcut)."""
    toate = {n: "\n".join(l) for n, l in _ecrane()}
    assert [k for k in EXCEPTII if k[1] not in toate.get(k[0], "")] == []


def test_starea_vine_din_antetul_cozii():
    """Middleware-ul care pune notele în coadă o spune ecranului: o atribuire `response.headers["X-Iconta-La-Validare"] = …` în
    `_autor_si_note_in_coada` (nodul AST, nu textul). Că `api.js` o citește și mesajele spun starea (`stareNota` / `pasNota`) probează
    e2e-ul 279 (`frontend_test/e2e/e2e_lot6.py`), pe ecran: nota scrisă de asistent arată „trimisă la validare”."""
    import ast
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    fn = [n for n in ast.walk(arb) if isinstance(n, ast.AsyncFunctionDef) and n.name == "_autor_si_note_in_coada"]
    assert len(fn) == 1
    chei = [t.slice.value for n in ast.walk(fn[0]) if isinstance(n, ast.Assign) for t in n.targets
            if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute) and t.value.attr == "headers"
            and isinstance(t.slice, ast.Constant)]
    assert chei.count("X-Iconta-La-Validare") == 1, chei


def test_refuzul_de_pe_rand_nu_mai_se_lipeste_de_buton():
    """279, clasa 259: refuzul unei acțiuni de pe rând („e la validare în cabinet”) se punea ca `<span class="msg-eroare">` lângă buton și
    strângea textul rândului. Acum trece prin `api.refuzPeRand` (sub textul rândului). Măsurat 16.10.2026: 11 apariții în 6 fișiere.
    MUTAȚIE: `b.insertAdjacentHTML("afterend", '<span class="msg-eroare" style="margin-left:8px">' + …)` pus înapoi în casă -> pică."""
    rele = ["%s:%d" % (n, i) for n, linii in _ecrane() for i, l in enumerate(linii, 1)
            if re.search(r"""insertAdjacentHTML\(\s*["']afterend["'],\s*['"`]<span class="msg-eroare\"""", l)]
    assert rele == [], rele
