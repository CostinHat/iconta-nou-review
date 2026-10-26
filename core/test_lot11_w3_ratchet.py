# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 440 — clasa, gardă ratchet (W3a, coborâtă și de W3b). Comanda Costin 11.1 pct.16, verbatim în DECIZII
„Comanda 11.1”: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp; pe toată aplicația”.]

CLASA: o funcție a serverului care refuză datele omului de DOUĂ sau mai multe ori în șir, fiecare refuz oprind tot, fără colectorul
`core.erori.ErorileFormularului` și fără `erori_campuri` — omul repară o greșeală, apasă, află de a doua.

METODA (a lui U0, inventarul lotului 11, aceeași aici, mecanic): fiecare `def` din `core/*.py` (fără `test_*`) și din `main.py` e
corpul de la linia lui până la următorul `def` (orice indentare); se numără refuzurile de date —
`raise _erori.DateInvalide(` / `raise _erori.CerereGresita(`, `raise ValueError(`, `raise HTTPException(400|422`, `return {"eroare"`,
`return {"ok": False`. O funcție cu ≥ 2 astfel de refuzuri, în care nu apar nici `ErorileFormularului`, nici `erori_campuri` (nici
ajutorul care le adună: `_campuri_lipsa(`, `_refuz_adunat(`, `_refuz_formular(` — completarea W3a a metodei U0), intră în cifră. LIMITA, declarată: numărătoarea e textuală — nu deosebește un refuz de STARE (lună închisă, document validat — refuz unic, corect)
de unul de date, nici două refuzuri ale aceluiași câmp care se exclud (ex. „lipsește” / „nu e valid”); de aceea e RATCHET (nu poate
crește), nu cerință de zero. Un refuz de stare corect păstrat unic nu trebuie „reparat” ca să coboare cifra.

CIFRA: la HEAD-ul de intrare al lotului 11 (381c82df) = 285 (U0 numărase 287, cu awk, fără ajutoarele colectorului); după reparațiile W3a + W3b (22.10.2026) =
`PRAG`. Crește -> pică (o funcție nouă refuză iar la prima eroare). Coboară -> trece și spune cifra nouă, ca pragul să fie coborât.
"""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: 22.10.2026, după W3a (B1–B20, B25–B26, A1–A4) și W3b (B21–B23, B27–B31, B35–B37, B39), măsurat cu `_functii_clasei(RAD)`
PRAG = 242
# [26.10.2026, loturile 12 + 13, reparațiile finale înaintea porții] 238 -> 242, măsurat pe ramura integrată cu peticele: 5 au ieșit
# (`common.cota`, `comodat_chirii.nota_chirie_incasata` — 531, `intracomunitar.valideaza_lic` — C84, `productie.nota_vanzare` — 510,
# `uc_tenants.factura_primita_valideaza` — C120), 2 noi au trecut pe colector chiar acum (`uc_admin.admin_anunt_creeaza` 646 și
# `admin_cabinet_suspenda` 645: câmpuri independente, refuzul adunat — `core/test_lot13_admin_suspendare.py::test_440_…`), iar 9 noi
# rămân, NUMITE: niciuna nu validează câmpuri independente ale unui formular — refuzurile lor sunt în ȘIR (al doilea nu se poate
# judeca înaintea primului) sau de STARE:
#   - `ciorne_formular.ciorna_scrie` (lotul 12): forma ciornei, apoi mărimea ei (aceeași valoare, citită întâi);
#   - `clienti_api._sterge_fisa` (lotul 12): fișa inexistentă / fișa cu facturi — stări, nu câmpuri;
#   - `diurna_salariat._suma` (lotul 13, 670): suma nu e număr / suma nu e pozitivă — aceeași valoare;
#   - `diurna_salariat.adauga_excedent` (lotul 13, 670): API intern chemat de decont (referința, luna, salariatul, nota) — nu e un formular;
#   - `facturi_recurente.emite_unul` (lotul 13, 680): șablonul inexistent / nescadent azi — stări;
#   - `numere.numar_ro` (lotul 13, 655): o singură valoare scrisă de om, refuzată cu același mesaj pe două forme;
#   - `uc_tenants._emite_catre` (lotul 13, 530 / 531): emiterea refuzată / nota facturii nescrisă — în șir;
#   - `uc_tenants._partaj_lichidare` (lotul 13, 533): data înaintea soldurilor / nimic de împărțit / fără asociați — stări ale firmei;
#   - `uc_tenants.operatiuni_date` (lotul 13): parametrii unei LISTE (data, tipul, ce) — o citire, nu un formular.

_REFUZ = re.compile(r'raise\s+_erori\.(?:DateInvalide|CerereGresita)\(|raise\s+ValueError\(|'
                    r'raise\s+HTTPException\(\s*(?:status_code\s*=\s*)?(?:400|422)\b|'
                    r'return\s+\{\s*"eroare"|return\s+\{\s*"ok"\s*:\s*False')
_DEF = re.compile(r'^\s*(?:async\s+)?def\s+(\w+)')
#: semnul colectorului în corpul funcției: el însuși, lista trimisă, sau ajutorul care le adună (`uc_comun._campuri_lipsa`, refuzul
#: adunat al modulului — `_refuz_adunat` / `_refuz_formular` construiesc `erori_campuri` din `ErorileFormularului`)
_COLECTOR = ("ErorileFormularului", "erori_campuri", "_campuri_lipsa(", "_refuz_adunat(", "_refuz_formular(")


def _functii(cale):
    """(nume, linie, corp) pentru fiecare `def` din fișier — corpul ține până la următorul `def`, de orice indentare."""
    linii = open(cale, encoding="utf-8").read().split("\n")
    nume, start, corp = None, 0, []
    for i, l in enumerate(linii):
        m = _DEF.match(l)
        if m:
            if nume:
                yield nume, start, "\n".join(corp)
            nume, start, corp = m.group(1), i + 1, []
        corp.append(l)
    if nume:
        yield nume, start, "\n".join(corp)


def _functii_clasei(rad):
    fisiere = [p for p in sorted(glob.glob(os.path.join(rad, "core", "*.py"))) if not os.path.basename(p).startswith("test_")]
    if os.path.exists(os.path.join(rad, "main.py")):
        fisiere.append(os.path.join(rad, "main.py"))
    out = []
    for p in fisiere:
        for nume, linie, corp in _functii(p):
            if len(_REFUZ.findall(corp)) >= 2 and not any(m in corp for m in _COLECTOR):
                out.append("%s:%d:%s" % (os.path.relpath(p, rad), linie, nume))
    return out


def test_cifra_clasei_nu_creste():
    """MUTAȚIE: o funcție nouă cu două `raise ValueError(...)` în `core/` -> cifra PRAG+1 -> pică (proba de mai jos, pe un arbore mic)."""
    acum = _functii_clasei(RAD)
    assert len(acum) <= PRAG, ("440: %d funcții refuză iar la prima eroare (pragul e %d). Adună refuzurile cu "
                               "`core.erori.ErorileFormularului` și trimite-le pe toate (`erori_campuri`). Funcțiile clasei:\n%s"
                               % (len(acum), PRAG, "\n".join(acum)))
    if len(acum) < PRAG:
        print("440: cifra a coborât la %d — coboară PRAG din %s" % (len(acum), os.path.basename(__file__)))


def test_numaratoarea_prinde_clasa_si_iarta_colectorul(tmp_path):
    """Anti-vacuu: pe un arbore mic, funcția cu două refuzuri în șir e numărată; cea cu colectorul nu; una cu un singur refuz nu."""
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "x.py").write_text(
        "def rea(c):\n    if not c.get('a'):\n        raise ValueError('a')\n    if not c.get('b'):\n        return {\"eroare\": 'b'}\n\n"
        "def buna(c):\n    er = ErorileFormularului()\n    if not c.get('a'):\n        raise ValueError('a')\n    raise ValueError('b')\n\n"
        "def unica(c):\n    raise ValueError('a')\n", encoding="utf-8")
    assert _functii_clasei(str(tmp_path)) == ["core/x.py:1:rea"]
