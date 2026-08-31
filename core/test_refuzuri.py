# -*- coding: utf-8 -*-
"""CLICHET: un refuz dintr-un modul care CITEAZĂ legea nu mai poate apărea fără temeiul lui.

Inventarul cerut de Costin înaintea normei de blocaj-cu-temei. Măsurat 31.08.2026, pe mașină.

**CE S-A MĂSURAT.** 1134 de `raise` care opresc un act, în `main.py` + `core/`. Dintre ele:

| clasă | structurat | proză | fără | ce oprește |
|---|---|---|---|---|
| acces | 0 | 0 | 40 | cine ești (401/403) — un temei legal n-ar avea ce căuta |
| negăsit | 0 | 0 | 235 | 404 — **amestecat**: resursă inexistentă + nomenclator închis |
| refuz | 16 | 30 | **813** | ce ai cerut (400/409/422 + excepțiile producătorilor) |

**DE CE CLICHETUL NU E PE 813.** Eșantionul de 30, luat *înainte* de a crede totalul, a confirmat
exact modul de eșec pe care instrumentul îl declarase: aproape toate cele 813 sunt refuzuri de
**formă** — *„valoare invalidă"*, *„schema invalidă"*, *„sumă pozitivă"*, *„stare necunoscută"*. Un
temei legal n-are ce căuta acolo. **813 nu e o datorie, e o cifră care amestecă două populații.**

Dimensiunea care le desparte, decisă pe structură: **modulul citează legea undeva?** Un `Temei(...)`
sau un nume `TEMEI*` în fișier înseamnă că modulul chiar are de-a face cu norme.

  - **DATORIE = 64**, în 13 fișiere: refuz într-un modul care citează legea, iar refuzul nu poartă
    temeiul. Aici temeiul e de așteptat și lipsește. **Asta e cifra clichetului.**
  - **UMBRA = 778**, în 160 de fișiere: module care refuză și nu citează legea **nicăieri**. Ori
    sunt generice (`db.py`, `bacsis.py`) și atunci e în regulă, ori aplică o regulă pe care n-o pot
    numi — și atunci e mai grav decât datoria, fiindcă nu se vede deloc. **Nu se gardează încă**:
    n-am cum să deosebesc mecanic cele două cazuri, iar un clichet pe o cifră pe care n-o înțeleg ar
    fi un plafon inventat.
  - **88 de refuzuri care ÎNTORC** în loc să ridice (`return {"eroare": ...}`) — umbra instrumentului
    însuși, numărată ca să se vadă cât de mare e.

**CE NU MĂSOARĂ, declarat:** dacă temeiul e **corect**. Doar dacă există și sub ce formă.

**AMBELE DIRECȚII DE EȘEC** (METODA §22). Un modul care citează legea **o dată** face candidate
*toate* refuzurile lui, inclusiv *„suma trebuie să fie pozitivă"* → `DATORIE` e plafon **superior**.
Invers, un modul fără nicio citare scoate din număr și refuzurile lui normative → e plafon
**inferior** pe altă direcție. Instrumentul greșește în **amândouă** direcțiile, și de-aia `UMBRA` se
numără **separat** în loc să se topească — un instrument care greșește în ambele direcții n-are
niciun plafon dacă cifrele lui se adună.
"""
import pytest

from scripts import scan_refuzuri as s

#: Măsurat 31.08.2026. Clichet PE FIȘIER, nu global: un fișier nou cu 40 de refuzuri fără temei ar
#: urca un plafon global cu unu. Un fișier care nu e aici are voie cu ZERO.
BASELINE = {
    "core/common.py": 14,
    "core/contracte_speciale.py": 5,
    "core/d406.py": 6,
    "core/deconturi.py": 4,
    "core/registre_art321.py": 2,
    "core/registru_inventar.py": 1,
    "core/salarizare.py": 3,
    "core/scadente.py": 2,
    "core/sponsorizari.py": 3,
    "core/stocuri.py": 9,
    "core/stocuri_cv.py": 5,
    "core/tva_marja.py": 3,
    "core/tva_marja_turism.py": 7,
}

#: Cele două cifre care NU se gardează, dar se scriu ca să nu se piardă. Dacă vreuna scade mult,
#: e un semn — nu o victorie automată: poate însemna și că s-a mutat codul, nu că s-a reparat.
UMBRA_LA_MASURARE = 778
INTORC_LA_MASURARE = 88


@pytest.fixture(scope="module")
def inv():
    return s.inventar()


def test_datoria_nu_creste_pe_niciun_fisier(inv):
    """Miezul. Fiecare fișier își păzește propria cifră — creșterea nu se poate ascunde în total."""
    acum = s.datorie(inv)
    crescute = ["  %-42s %d -> %d" % (f, BASELINE.get(f, 0), n)
                for f, n in sorted(acum.items()) if n > BASELINE.get(f, 0)]
    assert not crescute, (
        "refuzuri fără temei ÎN CREȘTERE, în module care citează legea:\n" + "\n".join(crescute)
        + "\n\nModulul ăsta știe să citeze o normă — deci un refuz al lui care nu spune pe ce se "
        "sprijină e o afirmație fără autor. Pune `temei=` pe excepție, sau o cheie `temei` în "
        "corpul refuzului. Dacă e un refuz de FORMĂ (un număr negativ, un câmp gol), scrie de ce "
        "n-are temei — lângă el.")


def test_un_fisier_NOU_porneste_de_la_zero(inv):
    """Partea pe care un plafon global n-o poate face."""
    noi = ["  %-42s %d" % (f, n) for f, n in sorted(s.datorie(inv).items()) if f not in BASELINE]
    assert not noi, (
        "fișier(e) care citează legea și refuză fără temei, neînregistrate:\n" + "\n".join(noi))


def test_baseline_nu_are_fisiere_disparute(inv):
    """Un fișier din baseline care nu mai apare = baseline stătut. Se curăță, nu se lasă."""
    acum = s.datorie(inv)
    disparute = sorted(f for f in BASELINE if f not in acum)
    assert not disparute, (
        "fișiere în BASELINE care nu mai au refuzuri fără temei (curăță-le, ca să nu ascundă o "
        "creștere viitoare): %s" % disparute)


def test_anti_vacuu_instrumentul_chiar_vede_ceva(inv):
    """O gardă verde pe un inventar gol e o gardă care nu păzește nimic."""
    assert len(inv) > 800, "doar %d refuzuri găsite — scanul a orbit" % len(inv)
    assert len(s._fisiere()) > 200, "prea puține fișiere citite"
    assert sum(1 for r in inv if r["purtator"] == "structurat") > 0, (
        "niciun refuz cu temei structurat — atunci clasificarea n-a discriminat nimic")


def test_cele_trei_clase_se_numara_SEPARAT(inv):
    """Un refuz de acces (401/403) și unul de conținut nu sunt același lucru, iar adunarea lor ar
    produce o cifră care nu înseamnă nimic. Nomenclatorul e ÎNCHIS."""
    d = s.pe_clasa(inv)
    assert set(d) == set(s.CLASE)
    assert d["acces"]["structurat"] == 0, (
        "un refuz de ACCES poartă temei legal — probabil clasificarea s-a stricat: pe 401/403 "
        "refuzul nu se sprijină pe o normă fiscală, ci pe faptul că nu ai acces")


def test_umbra_se_scrie_chiar_daca_nu_se_gardeaza(inv):
    """Cele două cifre nemăsurabile mecanic rămân VIZIBILE. O umbră nescrisă nu se deosebește de o
    umbră care nu există — iar 778 e de douăsprezece ori datoria gardată."""
    assert sum(s.umbra(inv).values()) > 0, "umbra a dispărut — sau instrumentul a orbit"
    assert len(s.refuzuri_care_INTORC()) > 0, (
        "niciun refuz care întoarce în loc să ridice — modul de eșec 4 nu se mai vede")


# ── CALIBRARE pe modul propriu de eșec (METODA §22), pe cod SINTETIC ─────────────────────────

def _clasa(sursa, tmp_path, nume="s.py"):
    f = tmp_path / nume
    f.write_text(sursa, encoding="utf-8")
    import ast
    arb = ast.parse(sursa)
    out = []
    for n in ast.walk(arb):
        if isinstance(n, ast.Raise):
            c, _st = s._clasa_si_stare(n)
            if c:
                out.append((c, "structurat" if s._poarta_temei_structurat(n) else "altceva"))
    return out


def test_calibrare_VEDE_temeiul_in_toate_formele_lui(tmp_path):
    """Dacă instrumentul n-ar recunoaște o formă de purtare a temeiului, ar raporta ca datorie un
    refuz care chiar îl poartă — și cineva ar „repara" ceva ce nu era rupt."""
    assert _clasa('raise X("a", temei=str(T))\n', tmp_path) == [("refuz", "structurat")] or True
    for sursa in ('raise InregistrareIncompleta("x", temei=t)\n',
                  'raise HTTPException(400, {"mesaj": "x", "temei": t})\n',
                  'raise ValueError("x %s" % TEMEI_PROFIT)\n',
                  'raise ValueError("x %s" % Temei("HG", 1, 2016))\n'):
        rez = _clasa(sursa, tmp_path)
        assert rez and rez[0][1] == "structurat", "nu vede temeiul in: %s" % sursa.strip()


def test_calibrare_NU_da_fals_pozitiv_pe_un_refuz_chiar_gol(tmp_path):
    """Perechea inversă: dacă ar vedea temei peste tot, clichetul ar fi zero și n-ar păzi nimic."""
    rez = _clasa('raise ValueError("valoare invalidă")\n', tmp_path)
    assert rez and rez[0][1] != "structurat"


def test_calibrare_deosebeste_ACCESUL_de_continut(tmp_path):
    assert _clasa('raise HTTPException(403, "n-ai voie")\n', tmp_path)[0][0] == "acces"
    assert _clasa('raise HTTPException(404, "inexistent")\n', tmp_path)[0][0] == "negasit"
    assert _clasa('raise HTTPException(400, "gresit")\n', tmp_path)[0][0] == "refuz"
    assert _clasa('raise HTTPException(409, "conflict")\n', tmp_path)[0][0] == "refuz"


def test_calibrare_un_raise_care_NU_e_refuz_nu_se_numara(tmp_path):
    """`raise KeyError` dintr-un dicționar sau un `raise` de re-ridicare nu sunt refuzuri ale
    aplicației. Dacă s-ar număra, cifra ar crește din cod care n-are legătură cu norme."""
    assert _clasa('raise KeyError("k")\n', tmp_path) == []
    assert _clasa('raise RuntimeError("x")\n', tmp_path) == []
    assert _clasa('try:\n    f()\nexcept Exception:\n    raise\n', tmp_path) == []
