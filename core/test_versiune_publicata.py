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


def test_anuntul_NU_reincarca_singur():
    """Decizia lui Costin, verbatim: *„nu forta reincarcarea — un formular pe jumatate completat
    pierdut e mai rau decat defectul."*

    Ancorat pe TEXT, si spun de ce: nu exista parser de JS in repo. Proprietatea pazita e o
    NUMARATOARE — cate reincarcari exista in modul —, iar o a doua, oriunde, o face rosie. Un `in`
    n-ar fi facut asta."""
    sursa = io.open(_MODUL, encoding="utf-8").read()
    n = sursa.count("location.reload()")
    assert n == 1, (
        "`versiune.js` are %d reincarcari; trebuie sa ramana UNA, si aia legata de apasarea "
        "omului. Aplicatia nu reincarca singura." % n)
    # NUMARATOARE, nu cautare — de-aia `count`, nu `in`: o a doua reincarcare oriunde face gardul
    # rosu, iar o cautare cu `in` ar fi trecut la fel de bine pe zece.
    linii = [x for x in sursa.splitlines() if x.count("location.reload()")]
    assert len(linii) == 1 and linii[0].count('addEventListener("click"') == 1, (
        "singura reincarcare NU e in ascultatorul de apasare, deci se poate declansa singura: %r"
        % [x.strip() for x in linii])


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
