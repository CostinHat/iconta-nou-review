# -*- coding: utf-8 -*-
"""GARD [R118 + R129, 03.09.2026]: poarta de sintaxa a publicarii, si anuntul care NU intrerupe.

**CE PAZESTE, in ordinea in care s-ar putea strica:**

  1. **poarta de sintaxa a publicarii** (R118) — `verifica_js` prinde un modul care nu se parseaza,
     si TACE pe unul curat. Amandoua directiile: un instrument care ar refuza mereu ar opri
     publicarea cu totul, iar unul care ar accepta mereu n-ar apara nimic.
  2. **amprenta poarta cheile pe care le citeste ecranul** (R129) — `versiune.js` compara
     `commit` (publicare din HEAD) sau `la` (publicare din arbore). Daca amprenta si-ar pierde
     cheile, anuntul n-ar mai aparea NICIODATA, si nimic nu s-ar aprinde: un gard tacut peste un
     mecanism tacut.
  3. **anuntul nu reincarca singur** — chiar decizia lui Costin: *„nu forta reincarcarea, un
     formular pe jumatate completat pierdut e mai rau decat defectul."* O singura reincarcare in
     tot modulul, si aia legata de o apasare.

**CE NU PAZESTE, declarat:** ca anuntul APARE pe ecran — aia e proba de ecran
(`frontend_test/proba_r129_versiune.py`), care masoara si ca formularul supravietuieste.
"""
import io
import os
import sys
import tempfile

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from scripts import publica_static as _ps  # noqa: E402

_MODUL = os.path.join(_RAD, "static", "js", "versiune.js")
#: Aceeasi clasa de greseala ca instanta din 01.09: sir deschis cu ghilimea romaneasca `„`.
_STRICAT = 'const x = „text gresit";\n'
_CURAT = 'export const x = 1;\nexport function f() { return x + 1; }\n'


def _dir_cu(continut):
    d = tempfile.mkdtemp(prefix="ztest_publica_")
    io.open(os.path.join(d, "m.js"), "w", encoding="utf-8").write(continut)
    return d


def test_poarta_de_sintaxa_PRINDE_un_modul_care_nu_se_parseaza():
    rele = _ps.verifica_js(_dir_cu(_STRICAT))
    assert len(rele) == 1, "modulul stricat n-a fost prins: %r" % rele
    cale, mesaj = rele[0]
    assert cale == "m.js", "raportul nu numeste fisierul: %r" % (rele,)
    assert mesaj.strip(), "refuzul n-are motiv scris — nu se poate repara din el"


def test_poarta_de_sintaxa_TACE_pe_un_modul_curat():
    """Directia opusa. Un instrument care refuza mereu ar opri publicarea cu totul, iar gardul de
    sus ar trece verde din motivul gresit."""
    assert _ps.verifica_js(_dir_cu(_CURAT)) == []


def test_amprenta_poarta_CHEILE_pe_care_le_citeste_ecranul():
    """`versiune.js` citeste `commit` (publicare din HEAD) sau `la` (publicare din arbore). Fara
    ele, anuntul n-ar aparea niciodata — si nimic nu s-ar aprinde."""
    s = _ps.stare()
    if s is None:
        pytest.skip("nu s-a publicat inca pe masina asta (`scripts/publica_static.py`)")
    assert set(s) >= {"sursa", "la"}, "amprenta n-are cheile de baza: %r" % sorted(s)
    assert s.get("commit") or s.get("la"), (
        "amprenta n-are nici `commit`, nici `la` — ecranul n-are ce compara: %r" % s)
    assert s["sursa"] in ("commit", "arbore de lucru"), (
        "sursa publicarii nu e una dintre cele doua declarate: %r" % s.get("sursa"))


def test_reincarcarea_e_doar_la_clic_si_la_autentificare_fara_formular():
    """[PIVOT față de R129, decizia Costin 07.10.2026] Varianta (a) din 03.09.2026 — *„nu forta reincarcarea — un formular pe
    jumatate completat pierdut e mai rau decat defectul”* — ramane INTREAGA pentru formularul inceput. Nou: la autentificare,
    fara formular inceput, aplicatia se reincarca singura (nu exista ce pierde; codul vechi din fila, da).

    NUMARATOARE: exact DOUA reincarcari in modul. Una in ascultatorul de apasare (omul alege), una in ramura de autentificare —
    si AMANDOUA pazite de `formularInceput()`. O a treia, oriunde, face gardul rosu.
    MUTATIE: `!formularInceput()` scos din ramura de autentificare -> pica."""
    import re
    sursa = io.open(_MODUL, encoding="utf-8").read()
    linii = [x.strip() for x in sursa.splitlines() if re.search(r"location\.reload\(\)", x)]
    assert len(linii) == 2, "versiune.js are %d reincarcari, nu 2: %r" % (len(linii), linii)
    clic = [x for x in linii if re.search(r'addEventListener\("click", \(\) => \(formularInceput\(\) \? spuneDeCe\(\) : window\.location\.reload\(\)\)\)', x)]
    autent = [x for x in linii if re.match(r"if \(laAutentificare && !formularInceput\(\)\) \{ window\.location\.reload\(\); return; \}$", x)]
    assert (len(clic), len(autent)) == (1, 1), linii
    assert re.search(r"export function porneste\(\) \{[^}]*?verifica\(true\);", sursa)


def test_anuntul_nu_re_randeaza_coaja():
    """O re-randare a cojii ar demonta ferestrele deschise — adica ar pierde exact formularul pe
    care decizia il apara. Modulul aseaza un nod intr-un loc declarat; nu cheama nimic care
    reconstruieste ecranul."""
    sursa = io.open(_MODUL, encoding="utf-8").read()
    # `innerHTML` pe nodul PROPRIU e legitim — chiriasul isi construieste nodul lui. Ce nu e
    # legitim: sa cheme re-randarea cojii, sau sa-si caute singur un nod in DOM (`querySelector`),
    # fiindca de acolo incolo poate scrie in spatiul altcuiva. Contractul DS cap.25: chiriasul CERE
    # un loc prin `coaja.pune`, nu si-l ia. *Prima forma a gardului interzicea `innerHTML =` peste
    # tot si cadea pe nodul propriu — regula era prea larga, nu modulul gresit.*
    for interzis in ("randeazaDesktop", "randeazaFerestre", "document.querySelector"):
        assert sursa.count(interzis) == 0, (
            "`versiune.js` foloseste %r — de acolo poate demonta sau rescrie ce e pe ecran"
            % interzis)
    assert sursa.count("coaja.pune") >= 1, (
        "[anti-vacuu] modulul nu mai trece prin contractul cojii — atunci interdictiile de mai sus "
        "nu mai inseamna nimic")
