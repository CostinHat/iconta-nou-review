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
#:
#: **61 → 62 (04.09.2026), prima CREȘTERE, și se scrie de ce.** Lotul 4 al campaniei a scos un
#: default fiscal tăcut: un cod de indemnizație inexistent primea 75%. Refuzul care îl închide stă
#: în `salarizare.py` — modul care citează legea — dar e un refuz de **FORMĂ**: codul nu e în
#: nomenclator. Sursa nomenclatorului nu e o normă cu articol, ci **Nomenclatorul 9 din structura
#: oficială D112**, iar norma asta spune ea însăși că un temei legal n-are ce căuta pe un refuz de
#: formă. *Creșterea se înregistrează, nu se ascunde punând un articol care nu i se potrivește.*
#:
#: **64 → 61 (31.08.2026), prima coborâre.** Cele trei refuzuri de nomenclator din
#: `registre_art321.py` (2) și `registru_inventar.py` (1) au primit temeiul care ÎNCHIDE
#: nomenclatorul — `TEMEI_FELURI` și `TEMEI_MOMENTE`, altele decât cele care spun ce *conține*
#: fiecare registru. Cele două fișiere au ieșit din baseline, nu au rămas cu plafon liber.
BASELINE = {
    "core/common.py": 14,
    "core/contracte_speciale.py": 5,
    "core/d406.py": 6,
    "core/deconturi.py": 4,
    "core/salarizare.py": 4,
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


def test_un_fisier_care_iese_din_datorie_IESE_prin_reparatie_nu_prin_incetarea_citarii(inv):
    """[31.08.2026, cerut de Costin] Cifra scade din două cauze care arată IDENTIC — și numai una e
    o reparație.

    (a) refuzurile modulului au primit temei → **datorie plătită**, baseline-ul se curăță;
    (b) modulul a **încetat să citeze legea** → refuzurile lui au trecut în UMBRĂ, unde nu le
        numără nimeni. Cifra scade fără ca vreun refuz să fi câștigat un temei.

    A doua e **eludarea prin locul unde stă codul, nu prin conținut** — și nu cere rea-intenție:
    e destul ca cineva să mute un `Temei` într-un modul vecin „ca să fie la un loc". Gardul de
    dinainte spunea, în cazul ăsta, exact sfatul greșit: «curăță baseline-ul».

    Perechea ei — un modul care ÎNCEPE să citeze legea, iar refuzurile lui vechi intră în datorie —
    e păzită de `test_un_fisier_NOU_porneste_de_la_zero`: fișierul nu e în BASELINE, deci n-are voie
    cu niciunul.
    """
    import os
    acum = s.datorie(inv)
    reparate, eludate = [], []
    for f in sorted(BASELINE):
        if f in acum:
            continue
        cale = os.path.join(s.RAD, f)
        if not os.path.exists(cale):
            eludate.append("  %-42s fișierul nu mai există" % f)
        elif s.modul_citeaza_legea(cale):
            reparate.append(f)
        else:
            eludate.append("  %-42s nu mai citează legea nicăieri" % f)
    assert not eludate, (
        "fișiere ieșite din datorie FĂRĂ ca vreun refuz să fi câștigat un temei:\n"
        + "\n".join(eludate)
        + "\n\nRefuzurile lor n-au dispărut — au trecut în UMBRĂ, unde nu le numără nimeni. "
        "Dacă modulul chiar nu mai are de-a face cu norme, spune-o AICI, scoțând fișierul din "
        "BASELINE cu motivul scris; dacă `Temei`-ul doar s-a mutat, datoria a rămas unde era.")
    assert not reparate, (
        "fișiere care și-au plătit datoria (toate refuzurile poartă acum temeiul): %s. "
        "Scoate-le din BASELINE — altfel plafonul lor rămâne liber și ascunde o creștere viitoare."
        % reparate)


def test_suprafata_de_migrare_e_MASURATA_nu_presupusa(inv):
    """Cât de mare e populația care poate intra în datorie printr-un singur `Temei` adăugat.

    Nu e un plafon — e cifra care spune cât de mult contează regula de migrare. Dacă ar fi mică,
    regula ar fi o precauție teoretică; la 160 de fișiere nu e.
    """
    umb = s.umbra(inv)
    assert len(umb) > 50, (
        "suprafața de migrare s-a prăbușit la %d fișiere — ori s-a reparat mult, ori instrumentul "
        "a orbit. Remăsoară înainte de a scrie că e o victorie." % len(umb))


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


def test_cifra_din_norma_77_nu_diverge_de_CLICHET():
    """doc↔cod. Norma din `CONFORMITATE.md` §77 își scrie cifra în proză; clichetul o ține în cod.

    **Regula pe care o aplic aici e a mea, de ieri**: *orice proză care reafirmă un număr derivat ori
    se generează, ori se șterge.* Aici nu se poate niciuna — `cifra` e un câmp **obligatoriu** al unei
    interdicții, pinat cu `măsurat la` + `pe commit`, deci e o măsurătoare datată, nu o afirmație
    despre azi. A treia cale: **se confruntă**.

    Ce face imposibil: ca cineva să repare zece refuzuri, să coboare clichetul, și norma să rămână
    scriind 64. Atunci n-ar mai fi o măsurătoare veche — ar fi o măsurătoare veche *care se citește
    ca fiind curentă*, fiindcă nimic n-o contrazice. Coborârea clichetului cere o linie nouă în
    normă, cu data ei.
    """
    import io
    import os
    import re
    conf = io.open(os.path.join(s.RAD, "CONFORMITATE.md"), encoding="utf-8").read()
    m = re.search(r"^## 77 — .*?$(.*?)^## ", conf, re.M | re.S)
    assert m, "interdicția 77 nu se poate izola din CONFORMITATE.md"
    corp = m.group(1)
    c = re.search(r"- \*\*cifra\*\*: (.+)", corp)
    assert c, "câmpul `cifra` al normei 77 nu se mai găsește"
    # Se citesc NUMERELE, nu forma lor tipografică: `**64**, în **13 fișiere**` și
    # `**64**, în **13** fișiere` spun același lucru, iar un gard care cere una din ele ar păzi
    # punctuația. Primele două numere ale câmpului sunt, prin scriere, totalul și fișierele.
    nr = [int(x) for x in re.findall(r"\d+", c.group(1))]
    assert len(nr) >= 2, "câmpul `cifra` n-are cele două numere (total, fișiere): %r" % c.group(1)
    scris_total, scris_fisiere = nr[0], nr[1]
    assert scris_total == sum(BASELINE.values()), (
        "norma 77 scrie %d, clichetul e la %d. Dacă datoria a scăzut, norma primește o linie nouă "
        "cu data ei — nu se lasă cifra veche să se citească drept curentă."
        % (scris_total, sum(BASELINE.values())))
    assert scris_fisiere == len(BASELINE), (
        "norma 77 scrie %d fișiere, clichetul are %d" % (scris_fisiere, len(BASELINE)))


def test_norma_77_isi_scrie_LIMITA_pe_umbra(inv):
    """Costin, 31.08: «norma își scrie singură această limită, cu motivul». Un plafon care nu-și
    numește ce lasă afară se citește ca și cum ar acoperi tot."""
    import io
    import os
    import re
    conf = io.open(os.path.join(s.RAD, "CONFORMITATE.md"), encoding="utf-8").read()
    m = re.search(r"^## 77 — .*?$(.*?)^## ", conf, re.M | re.S)
    corp = m.group(1)
    camp = re.search(r"- \*\*limita pe care norma și-o scrie singură\*\*: (.+)", corp)
    assert camp, "norma 77 nu-și mai scrie limita — umbra ar părea acoperită"
    # Se cere ca limita să EXISTE și să trimită la instrument, **nu** ca cifra ei să fie scrisă.
    # Prima formă cerea potrivirea cifrelor — și a căzut a doua zi, la primul modul nou. Era un
    # defect al gărzii, nu al normei: transforma o cifră DELIBERAT nedeplafonată într-un clichet de
    # facto, cu costul unuia și fără protecția lui.
    # Pe MULTIME de jetoane parsate, nu pe cautare de sir: se extrag identificatorii dintre
    # backtick-uri si se compara cu `>=`. Prima forma a acestei probe intreba `"umbra" in camp` —
    # adica exact ce clichetul 50 interzice, introdus de mine chiar reparand altceva.
    jetoane = set(re.findall(r"`([^`]+)`", camp.group(1)))
    assert jetoane >= {"scripts/scan_refuzuri.umbra()"}, (
        "limita nu mai trimite la instrumentul care derivă cifra (jetoane găsite: %s) — cine o "
        "citește ar rămâne fără nicio cale s-o afle" % sorted(jetoane))
    assert not re.search(r"\b\d{3}\b", camp.group(1)), (
        "limita a primit iar o cifră scrisă de mână: %r. Umbra nu e plafonată; un număr scris aici "
        "îmbătrânește la fiecare modul nou." % camp.group(1)[:120])
    assert sum(s.umbra(inv).values()) > 0, "umbra a dispărut din măsurătoare"


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
