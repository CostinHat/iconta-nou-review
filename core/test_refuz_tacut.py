# -*- coding: utf-8 -*-
"""GARD [27.08.2026]: un refuz al serverului la o SCRIERE nu poate rămâne nevăzut.

DE UNDE VINE. Costin: *„am pierdut o jumătate de oră pe «butonul nu face nimic» […] cauza e
aceeași cu observația 2 din R71 și cu `except Exception: pass` de la R73: eroarea e prinsă și nu
ajunge la om. Iar consecința nu e neplăcerea. E că nu se poate diagnostica nimic din afară."*

MĂSURAT ÎNTÂI, cum a cerut — `core/scan_refuz_tacut.py`, 27.08.2026: din **243** de `catch`-uri
peste un apel `api.*`, **227 arată ceva** și **16 sunt SCRIERI care pot refuza fără să spună
motivul**. *(Cifrele astea sunt de la măsurătoarea din 27.08 și au fost făcute cu un cititor
orb; cele vii sunt clichetele de mai jos, remăsurate pe 04.09 — 18 și 74.)* Prima măsurătoare dăduse 25; citite una câte una, nouă foloseau `insertAdjacentHTML`,
pe care detectorul nu-l știa. **Calibrat pe instanțe reale înainte de a scrie cifra** — o cifră
umflată e la fel de rea ca una mică.

REPARAȚIA E UNA, nu șaisprezece: în `static/js/api.js`, după un refuz la o scriere, dacă mesajul
**nu apare nicăieri în pagină**, îl arată stratul de prezentare. Verificarea e pe DOM-ul randat,
nu pe cooperarea apelantului — un ecran care afișează prin `arataMesaj`, prin `insertAdjacentHTML`
sau altfel e recunoscut la fel, fără să fie modificat.

CE FACE IMPOSIBIL:
  1. creșterea clasei: o scriere nouă care înghite refuzul fără să-l arate;
  2. dispariția plasei din `api.js` — fără ea, cele 18 redevin mute;
  3. întinderea plasei peste citiri: cele **74** de citiri tăcute (badge-uri, contoare) rămân
     tăcute **deliberat** — un badge care eșuează n-are voie să întrerupă omul.

CE NU FACE, declarat: **nu spune că mesajul e bun**, doar că ajunge. Și **nu scade clasa** — cele
18 rămân mute la locul lor; plasa le prinde, dar un mesaj lângă buton e mai bun decât un banner.
Clichetul e ca să nu crească, nu ca să fie declarată rezolvată.
"""
import io
import os

from core import scan_refuz_tacut as scan

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Măsurat 27.08.2026, după calibrarea pe instanțe reale. **REMĂSURAT 04.09.2026**, după ce
# cititorul comun a fost reparat (`core/cititor_js.py`): 16 → **18** și 70 → **74**.
# Urcarea NU e o regresie — e orbirea corectată. Măsurat în amândouă felurile pe ACELAȘI
# commit `277e4300`: cu cititorul vechi 16, cu cel reparat 18. Cele două care lipseau
# stăteau în `ecrane/facturi_ecran.js`, într-o parte a fișierului pe care cititorul o
# albea din randul 530 încolo. Amândouă sunt instanțe ale modurilor de eșec DECLARATE ale
# instrumentului, nu refuzuri înghițite: una cheamă o funcție proprie care afișează
# (`plaseazaErori`, modul 1), cealaltă e o căutare de fundal la tastare (`produse/
# potriveste`, modul 3 — `POST` folosit ca citire).
_SCRIERI_MUTE = 18
_CITIRI_MUTE = 74


def test_ANTI_VACUU_instrumentul_chiar_vede_ecranele():
    r = scan.masoara()
    assert r["cu_mesaj"] >= 150, (
        "doar %d `catch`-uri care arată ceva — scanul s-a rupt, iar clichetele de mai jos ar "
        "trece în gol" % r["cu_mesaj"])


def test_scrierile_mute_nu_cresc():
    r = scan.masoara()
    n = len(r["scrieri_mute"])
    assert n <= _SCRIERI_MUTE, (
        "scrieri NOI care pot refuza fără să spună motivul: %d > %d\n  %s\n"
        "Arată mesajul lângă butonul apăsat — plasa din `api.js` e ultima linie, nu prima."
        % (n, _SCRIERI_MUTE, "\n  ".join("%s:%d" % x for x in r["scrieri_mute"])))


def test_clichetul_de_scrieri_mute_nu_ramane_peste_realitate():
    n = len(scan.masoara()["scrieri_mute"])
    assert n == _SCRIERI_MUTE, (
        "sunt doar %d — coboară `_SCRIERI_MUTE` la %d" % (n, n))


def test_citirile_mute_raman_declarate_nu_uitate():
    """Cele 70 nu sunt un defect, sunt o alegere. Dar dacă se dublează, alegerea nu mai e alegere."""
    n = len(scan.masoara()["citiri_mute"])
    assert n <= _CITIRI_MUTE + 5, (
        "citirile tăcute au crescut de la %d la %d — dacă e deliberat, urcă pragul cu motivul"
        % (_CITIRI_MUTE, n))


def test_plasa_din_api_js_exista():
    """Fără ea, cele 18 redevin mute. Se caută marcajul funcției, nu un comentariu."""
    src = io.open(os.path.join(_RAD, "static", "js", "api.js"), encoding="utf-8").read()
    assert src.count("function _refuzNevazut(") == 1, (
        "`_refuzNevazut` a dispărut din `api.js` — refuzurile înghițite nu mai ajung la om")
    assert src.count("_refuzNevazut(") >= 3, (
        "plasa nu mai e chemată din amândouă căile (`_cere` și `_cereForm`)")
    assert src.count('if (metoda === "GET") return;') == 1, (
        "cuțitul dintre scriere și citire a dispărut — ori se pierd refuzurile, ori badge-urile "
        "încep să întrerupă omul")


# ── CALIBRARE: instrumentul, pe cazuri scrise ──────────────────────────────
def test_CALIBRARE_un_catch_gol_peste_o_scriere_E_prins(tmp_path):
    f = tmp_path / "x.js"
    f.write_text("async function a(){ try { await api.post('/x', {}); } catch {} }\n",
                 encoding="utf-8")
    curat = scan.fara_siruri(f.read_text(encoding="utf-8"))
    p = scan.perechi(curat)
    assert len(p) == 1
    assert not scan._ARATA.search(p[0][2]), "un `catch {}` gol e socotit ca arătând ceva"
    assert scan._SCRIERE.search(p[0][1]), "apelul de scriere nu e recunoscut"


def test_CALIBRARE_insertAdjacentHTML_CHIAR_arata(tmp_path):
    """Direcția «acuză pe nedrept» — chiar cazul care a umflat prima măsurătoare cu nouă."""
    corp = "{ b.insertAdjacentHTML('afterend', `<span>${e.mesaj}</span>`); }"
    assert scan._ARATA.search(corp), (
        "`insertAdjacentHTML` nu e recunoscut ca afișare — detectorul ar supra-raporta din nou")


def test_CALIBRARE_try_finally_NU_e_socotit_catch(tmp_path):
    f = tmp_path / "y.js"
    f.write_text("async function a(){ try { await api.post('/x', {}); } finally { g(); } }\n",
                 encoding="utf-8")
    assert scan.perechi(scan.fara_siruri(f.read_text(encoding="utf-8"))) == [], (
        "un `try/finally` nu înghite nimic; n-are ce căuta în clasă")


def test_CALIBRARE_o_acolada_dintr_un_sir_nu_muta_blocul(tmp_path):
    """Potrivirea e pe acolade — deci șirurile trebuie albite ÎNTÂI, altfel blocul alunecă."""
    f = tmp_path / "z.js"
    f.write_text("async function a(){ try { await api.post('/x', {m:'}'}); } catch { } }\n",
                 encoding="utf-8")
    p = scan.perechi(scan.fara_siruri(f.read_text(encoding="utf-8")))
    assert len(p) == 1 and scan._SCRIERE.search(p[0][1]), (
        "o acoladă dintr-un șir a mutat capătul blocului: %s" % p)
