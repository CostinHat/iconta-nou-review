# -*- coding: utf-8 -*-
"""SCANNER de CITĂRI VERIFICABILE: `text_citat` chiar există în documentul citat? (21.08.2026)

DE CE EXISTĂ. Gardul de temeiuri verifică azi doar că citarea ATERIZEAZĂ pe un document din
`anaf_surse/`. Limita e scrisă pe față: nu verifică dacă actul spune ce pretinzi. Iar datoria din
30.07 o numește exact: opt mențiuni canonizate la „DUK regula X" fără reverificare — *dacă una cita o
regulă greșită înainte, canonizarea a făcut-o să arate corect și să rămână greșită.*

CE A ARĂTAT CALIBRAREA (34 de citări din `common`, toate la nivel MO): 10 se găsesc verbatim în
document, 24 nu. **Cele 24 nu sunt greșite.** Sunt de altă formă: o parafrază cu localizator —
„art. II pct.42 modifică art.291 alin.(1) CF: cota standard TVA 21%" — care spune ce FACE actul.
Uneori mai utilă decât un citat brut. Deci `text_citat` poartă azi două lucruri, iar doar unul e
verificabil mecanic. A cere verbatim de la toate ar fi însemnat rescrierea a 24 de citări corecte.

DE-AIA CLICHETUL CREȘTE, nu scade. Numărul de citări verificabile mecanic e o proprietate care se
poate doar îmbunătăți: o citare nouă scrisă verbatim ridică pragul; una rescrisă din verbatim în
parafrază îl coboară și pică. Nu acuzăm parafrazele — dar nu mai putem pierde tăcut ce s-a câștigat.

CE NU POATE SPUNE. Când un citat NU se găsește, cauza poate fi oricare din trei, iar scanul nu le
deosebește: (1) e o parafrază; (2) documentul din corpus e altă consolidare a actului; (3) citatul e
GREȘIT. Fără fraza asta, gardul ar acuza corpusul. Cu ea, numărul e o măsură, nu un verdict.
"""
import os
import re
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _norm(s):
    """Normalizare pentru comparație: fără diacritice, fără marcaj HTML, fără punctuație."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _module():
    """Modulele în care se caută temeiuri: `core/common` (registrul de cote) **plus** orice modul
    `core/*.py` care declară obiecte `Temei` la nivel de modul.

    DE CE NU DOAR `common` (06.09.2026, R169). Prima formă citea numai `common`, iar asta a devenit
    fals pe măsură ce repo-ul a urmat propria politică: **decizia 73** cere ca temeiul să stea în
    modulul REGULII, nu în rută — `core/cota_tva_incasare.py` (art. 291 alin. 5),
    `core/perioada_fiscala_tva.py` (art. 322). Amândouă erau **invizibile** aici, deci citarea lor
    verbatim nu era verificată de nimeni, iar clichetul raporta despre o lume din ce în ce mai mică.
    *Un gard cu domeniul greșit dă verde despre ce nu vede.*

    Domeniul se ia din STRUCTURĂ, nu dintr-o listă scrisă de mână: se importă modulele `core/*.py`
    (fără `test_*`/`scan_*`) și se păstrează cele care chiar au un `Temei` la nivel de modul. O
    listă de nume ar fi îmbătrânit exact ca `common`-ul singur.
    """
    import glob
    import importlib
    from core import common as c

    mod, sarite = [c], []
    for cale in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        nume = os.path.basename(cale)[:-3]
        if nume.startswith(("test_", "scan_", "__")) or nume == "common":
            continue
        try:
            m = importlib.import_module("core." + nume)
        except Exception as e:  # noqa: BLE001
            # NU se sare in tacere. Un modul cu temeiuri care ar inceta sa se importe ar disparea
            # din inventar fara ca nimic sa spuna ceva — chiar forma de orbire pe care o repara
            # R169. Cine nu s-a importat se NUMESTE, iar `test_citate_verbatim` o cere goala.
            sarite.append("%s (%s)" % (nume, type(e).__name__))
            continue
        if any(isinstance(getattr(m, a, None), c.Temei) for a in dir(m) if not a.startswith("__")):
            mod.append(m)
    return mod, sarite


def module_sarite():
    """Modulele `core/*.py` care NU s-au putut importa la culegerea temeiurilor. Gol = domeniul
    scanului e intreg. Se raporteaza, nu se ascunde: *un plafon tacut se citeste ca acoperire.*"""
    return _module()[1]


def _temeiuri():
    """Toate obiectele `Temei` unice din modulele cu temeiuri, oricât de adânc în structuri."""
    from core import common as c
    gasite, vaz, unice = [], set(), []

    def culege(o, cale=""):
        if isinstance(o, c.Temei):
            gasite.append((cale, o))
        elif isinstance(o, dict):
            for k, v in o.items():
                culege(v, "%s.%s" % (cale, k))
        elif isinstance(o, (list, tuple)):
            for i, v in enumerate(o):
                culege(v, "%s[%d]" % (cale, i))

    for m in _module()[0]:
        prefix = "" if m.__name__ == "core.common" else m.__name__.split(".")[-1] + "."
        for nume in dir(m):
            if not nume.startswith("_"):
                culege(getattr(m, nume), prefix + nume)
    for cale, t in gasite:
        k = (str(t), t.text_citat)
        if k not in vaz:
            vaz.add(k)
            unice.append((cale, t))
    return unice


def _verbatim(t):
    """Citatul (sau o bucată semnificativă din el) apare în documentul citat?
    Se sparge pe `:` și `;` fiindcă forma uzuală e «localizator: citat» — verificăm citatul,
    nu localizatorul, care oricum e o construcție a noastră."""
    if not (t.text_citat and t.url):
        return None
    p = os.path.join(RAD, t.url)
    if not os.path.exists(p):
        return None
    doc = _norm(open(p, encoding="utf-8", errors="replace").read())
    intreg = _norm(t.text_citat)
    if intreg and intreg in doc:
        return True
    for b in re.split(r"[:;]", t.text_citat):
        nb = _norm(b)
        if len(nb) > 25 and nb in doc:
            return True
    return False


def inventar():
    """[(cale, temei, verbatim)] — verbatim: True / False / None (fără citat, url sau fișier)."""
    return [(cale, t, _verbatim(t)) for cale, t in _temeiuri()]


def cate_verbatim():
    return sum(1 for _c, _t, v in inventar() if v is True)


if __name__ == "__main__":
    inv = inventar()
    from collections import Counter
    c = Counter(v for _a, _b, v in inv)
    print("citări: %d | verbatim: %d | negăsite: %d | neverificabile: %d"
          % (len(inv), c[True], c[False], c[None]))
    print("")
    for cale, t, v in inv:
        if v is not True:
            print("  [%s] %-30s %s" % ("negăsit" if v is False else "n/a", cale[:30], str(t)[:44]))
