# -*- coding: utf-8 -*-
"""GARD (D7/D8/D9, 20.08.2026): mesajele `ValueError` PUBLICATE contabilului sunt în limba lui.

DE CE UN GARD NOU și nu o extindere a celor două existente. Ambele gărzi F5 cheie pe ROL SINTACTIC:
`test_diacritice_afisate.py` cere `HTTPException(detail=)` / cheie de afișare în dict / corp de
subclasă de excepție de business; `test_mesaje_generare_fara_camp_intern.py` se uită doar la funcții
numite `valideaza`/`erori*`. Un `ValueError` gol ridicat într-un helper din `core/` nu e în niciunul
dintre roluri — deci amândouă raportau VERDE pe mesaje pe care nu le vedeau. Auditul t001 (20.08) a
scos trei aşa: `tip_decont` pe ecranul Control fiscal, `D_9`/`Str_codBoalaSType` la D112,
`numitor <= 0` la Stocuri. Nu erau înghețate — erau în afara razei.

CANALUL, definit mecanic (nu prin listă scrisă de mână): `main.py` are **71 de rute** care fac
`except ValueError -> HTTPException(...)`, adică PUBLICĂ deliberat orice `ValueError` primesc.
Mesajele care ajung la contabil sunt cele ridicate de funcțiile din `core/` chemate în interiorul
acelor `try`. Sunt 116 funcții, cu 148 de mesaje în proză.

DOUĂ DIMENSIUNI, tratate diferit:
  • NUME INTERN (token snake_case în mesaj) — **ZERO admis, fără baseline**. Cele 4 existente
    (`tip_operatiune`, `furnizor_tva_incasare`, `firma_profil` ×2) au fost rescrise pe 20.08, deci
    dimensiunea pornește curată și trebuie să rămână.
  • DIACRITICE — **clichet per fișier** (`_BASELINE_DIACRITICE`, 84 la 20.08). Niciun fișier nu
    poate CREȘTE; un fișier nou = 0 admis. Burn-down: rescrii, scazi numărul, conștient. Țintă: gol.

Mutație probată: reintroducerea unui nume intern într-un mesaj publicat -> roșu, cu fișier și linie.
"""
import ast
import collections
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_DIAC = set("ăâîșțĂÂÎȘȚşţŞŢ")

# Datoria de diacritice a canalului la 20.08.2026 (burn-down). Scade pe măsură ce rescrii.
_BASELINE_DIACRITICE = {
    # [R147, 05.09.2026] `core/bacsis.py` A IESIT din baseline: 2 -> 0. Cele doua mesaje erau
    # `"bacsis invalid"`, acelasi text in doua locuri cu intelesuri diferite (bacsis incasat vs
    # bacsis BRUT de distribuit). Rescrise deosebit, cu diacritice. La fel `core/tva_incasare.py`:
    # 1 -> 0. Amandoua au iesit la iveala proband cele 32 de operatiuni speciale.
    "core/bilant_api.py": 2, "core/clienti_api.py": 1,
    "core/comodat_chirii.py": 3, "core/d406_active.py": 2, "core/facturi_api.py": 2,
    "core/gdpr_cerere.py": 2, "core/gdpr_sterge.py": 3, "core/import_export.py": 3,
    "core/intracomunitar.py": 5, "core/inventariere.py": 5, "core/migrare_api.py": 1,
    "core/plata_salarii.py": 2, "core/productie.py": 1, "core/provizioane.py": 1,
    "core/reset_parola.py": 1, "core/retete_api.py": 3, "core/salariati_api.py": 10,
    "core/subventii.py": 1, "core/taxare_inversa.py": 4,
    # [LOTUL 11, 04.09.2026] `core/tenant_provisioning.py` A IESIT din baseline: 2 -> 0.
    # Reparatia lui R134 (refuzurile rutei nu mai ies `500`) a PUBLICAT patru mesaje care
    # pana atunci nu ajungeau la nimeni, iar doua erau scrise fara diacritice. Rescrise in
    # AMANDOUA locurile in care traiau — creare si actualizare —, nu doar pe calea noua.
    "core/tva_agricultori.py": 1, "core/tva_aur.py": 2, "core/tva_marja_turism.py": 3,
}


def _publica_valueerror(fn):
    """`ast.Try` din rută care prind ValueError și ridică HTTPException = publică mesajul."""
    out = []
    for t in ast.walk(fn):
        if not isinstance(t, ast.Try):
            continue
        for h in t.handlers:
            ty = h.type
            tipuri = ty.elts if isinstance(ty, ast.Tuple) else ([ty] if ty else [])
            if not any(isinstance(x, ast.Name) and x.id == "ValueError" for x in tipuri):
                continue
            if "HTTPException" in ast.dump(ast.Module(body=h.body, type_ignores=[])):
                out.append(t)
    return out


def _tinte():
    """{(modul_core, functie)} chemate direct în interiorul unui try care publică."""
    arb = ast.parse(open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    glob = {}
    for n in arb.body:
        if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            for a in n.names:
                glob[a.asname or a.name] = a.name
    out, rute = set(), 0
    for fn in ast.walk(arb):
        # RUTELE `async def` INTRĂ ȘI ELE. Prima formă cerea `ast.FunctionDef`, deci cele 20
        # de rute asincrone erau în afara razei de la scrierea gardului (20.08.2026) — un
        # fals-negativ tăcut, descoperit abia când valul 1 al lui P5 le-a făcut sincrone și
        # una din ele a adus un mesaj fără diacritice. *Un gard care nu vede jumătate din
        # canal raportează verde despre o lume pe care n-o vede.*
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        ali = dict(glob)
        for n in ast.walk(fn):
            if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
                for a in n.names:
                    ali[a.asname or a.name] = a.name
        tries = _publica_valueerror(fn)
        if tries:
            rute += 1
        for t in tries:
            for b in t.body:
                for c in ast.walk(b):
                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) \
                            and isinstance(c.func.value, ast.Name):
                        m = ali.get(c.func.value.id)
                        if m:
                            out.add((m, c.func.attr))
    return out, rute


def _sir(r):
    e = r.exc
    if not (isinstance(e, ast.Call) and isinstance(e.func, ast.Name)
            and e.func.id == "ValueError" and e.args):
        return None
    a0 = e.args[0]
    if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
        return a0.value
    if isinstance(a0, ast.BinOp) and isinstance(a0.left, ast.Constant) \
            and isinstance(a0.left.value, str):
        return a0.left.value
    if isinstance(a0, ast.JoinedStr):
        return "".join(v.value for v in a0.values
                       if isinstance(v, ast.Constant) and isinstance(v.value, str))
    return None


def _scan():
    """(mesaje_totale, [nume_intern], Counter(diacritice_per_fisier))."""
    total, interne, diac = 0, [], collections.Counter()
    tinte, _ = _tinte()
    for modul, functie in sorted(tinte):
        cale = os.path.join(_RAD, "core", modul + ".py")
        if not os.path.exists(cale):
            continue
        try:
            arb = ast.parse(open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        for f in ast.walk(arb):
            if not (isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and f.name == functie):
                continue
            for r in ast.walk(f):
                if not (isinstance(r, ast.Raise) and r.exc is not None):
                    continue
                s = _sir(r)
                if not s or " " not in s:
                    continue
                total += 1
                rel = "core/%s.py" % modul
                m = _SNAKE.search(s)
                if m:
                    interne.append("%s:%d  token %r in: %s" % (rel, r.lineno, m.group(0), s[:80]))
                if not (set(s) & _DIAC) and any(c.islower() for c in s):
                    diac[rel] += 1
    return total, interne, diac


def test_niciun_nume_intern_in_mesaj_publicat():
    """ZERO, fara baseline: contabilul nu vede niciodata numele unei coloane sau al unui camp."""
    _, interne, _ = _scan()
    assert not interne, (
        "Mesaje publicate contabilului care contin un nume intern de camp/coloana:\n  - "
        + "\n  - ".join(interne))


def test_diacritice_clichet_per_fisier():
    """Clichet: niciun fisier nu poate creste; un fisier nou in canal porneste de la 0."""
    _, _, diac = _scan()
    crescute = []
    for rel, n in sorted(diac.items()):
        plafon = _BASELINE_DIACRITICE.get(rel, 0)
        if n > plafon:
            crescute.append("%s: %d mesaje fara diacritice (baseline %d)" % (rel, n, plafon))
    assert not crescute, (
        "Mesaje publicate FARA diacritice, peste clichet (rescrie-le, nu ridica baseline-ul):\n  - "
        + "\n  - ".join(crescute))


def test_baseline_nu_ramane_umflat():
    """Anti-baseline-stătut: daca un fisier a fost curatat, baseline-ul TREBUIE scazut in aceeasi
    tura - altfel clichetul lasa loc sa reintre exact atatea mesaje cate s-au reparat."""
    _, _, diac = _scan()
    umflate = ["%s: baseline %d, real %d" % (rel, plafon, diac.get(rel, 0))
               for rel, plafon in sorted(_BASELINE_DIACRITICE.items()) if diac.get(rel, 0) < plafon]
    assert not umflate, (
        "Baseline mai mare decat realitatea - scade-l la valoarea reala:\n  - " + "\n  - ".join(umflate))


def test_gardul_chiar_vede_canalul():
    """Anti-gard-mort: daca un refactor rupe euristica, testele de mai sus ar trece pe GOL.
    Cere ca respectiv canalul sa fie in continuare gasit, cu ordin de marime plauzibil."""
    tinte, rute = _tinte()
    total, _, _ = _scan()
    assert rute >= 40, "doar %d rute publica ValueError - euristica s-a rupt sau rutele au disparut" % rute
    assert len(tinte) >= 60, "doar %d functii core in canal - euristica s-a rupt" % len(tinte)
    assert total >= 100, "doar %d mesaje in canal - euristica s-a rupt" % total
