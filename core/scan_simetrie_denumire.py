# -*- coding: utf-8 -*-
"""Instrumentul simetriei de scriere a denumirii unei firme (R81, decis 28.08.2026).

REGULA PĂZITĂ, în cuvintele lui Costin: *„orice act care redenumește o firmă scrie denumirea în
AMBELE locuri (`public.tenants.nume` și `{schema}.firma_profil.nume`), în aceeași tranzacție, cu
aceeași valoare. Nu se construiește alias."*

DE CE UN SCAN, și nu doar o probă funcțională. O probă spune că **cele trei căi de azi** scriu
simetric. Nu spune nimic despre a patra, scrisă peste două săptămâni de cineva care n-a citit R81 —
iar exact așa s-au născut cele trei asimetrii de la început: fiecare cale a fost scrisă separat,
fiecare atingea ce avea la îndemână. Scanul mută întrebarea de la *„sunt cele de azi corecte"* la
*„poate exista una incorectă"*.

CE CITEȘTE, și de ce **nu** e o căutare de text. Fiecare `…execute(<sql>, …)` se ia din **AST** —
argumentul apelului, nu un șir găsit în fișier. Pe un SQL compus prin concatenare se coboară pe
stânga, unde stă litera; pe un f-string se păstrează bucățile literale. Deci un `UPDATE` scris
într-un comentariu sau într-un text de ajutor **nu** ajunge aici, iar unul asamblat la rulare nu
dispare din raport: intră în clasa **COMPUS**, care se numără separat și nu are voie să crească.

CELE TREI CLASE ale unei instrucțiuni `UPDATE` pe una din cele două tabele:

  1. **scrie nume** — `SET` literal care conține `nume =`. `nume_ales` și `nume_anaf` **nu** intră:
     potrivirea e pe cuvântul întreg, iar asta e chiar prima formă de eșec a instrumentului.
  2. **COMPUS** — `SET`-ul se asamblează la rulare (`", ".join(seturi)`), deci coloanele nu se pot
     citi din instrucțiune. Se rezolvă privind **fragmentele** literale din aceeași funcție: dacă
     vreunul e `nume = …`, funcția poate scrie denumirea. Instanța din care s-a învățat că merită:
     `actualizeaza_tenant` compunea `SET`-ul, deci niciun literal dat lui `execute` nu conținea
     cuvântul `nume` — un detector care s-ar uita doar la argument ar fi raportat **zero** și ar
     fi părut complet (a opta instanță, R77).
  3. **nu scrie nume** — restul.

VERDICTUL: o funcție care scrie denumirea într-**una** din cele două tabele și nu în cealaltă e o
încălcare. Simetria e o proprietate a **funcției**, fiindcă tranzacția e a apelantului: două
`UPDATE`-uri în aceeași funcție sunt în aceeași tranzacție prin construcție, iar unul singur nu
poate fi „compensat" altundeva fără ca legătura să devină invizibilă.

CE NU FACE, declarat:
  - **nu urmărește tranzacția.** Nu poate spune că nu există un `commit()` între cele două scrieri.
    Aia o spune `core/test_simetrie_denumire.py`, care citește nodurile funcției.
  - **nu verifică valoarea.** Că amândouă primesc **aceeași** valoare se probează pe date (O5), nu
    se citește din AST.
  - **nu acoperă crearea.** `provision_tenant` scrie prin `INSERT`, nu prin `UPDATE`; e verificată
    separat, cu propriul test.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TABELE = ("tenants", "firma_profil")

# `\bnume\s*=` și nimic altceva: `nume_ales=`, `nume_anaf=` sau `prenume=` n-au voie să treacă
# drept denumirea firmei. E prima formă de eșec a instrumentului, și e calibrată în ambele direcții.
RE_SET_NUME = re.compile(r"\bnume\s*=", re.I)
RE_UPDATE = re.compile(r'^UPDATE\s+(?:[\w"%{}.\']+\.)?"?(tenants|firma_profil)"?\b(.*)$', re.I | re.S)
RE_FRAGMENT_NUME = re.compile(r"^\s*nume\s*=", re.I)


def fisiere_productie():
    out = ["main.py"]
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_") and not f.startswith("scan_"):
            out.append("core/" + f)
    return out


def _literal_sql(nod):
    """Litera SQL a argumentului, sau None. Coboară pe stânga pe concatenări (`"…" % x`, `"…" + x`)
    și păstrează bucățile constante ale unui f-string, cu interpolările marcate."""
    a = nod
    while isinstance(a, ast.BinOp):
        a = a.left
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return a.value
    if isinstance(a, ast.JoinedStr):
        bucati = []
        for v in a.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                bucati.append(v.value)
            else:
                bucati.append("\x01")
        return "".join(bucati)
    return None


def _executari(fn):
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            sql = _literal_sql(n.args[0])
            if sql is not None:
                yield n, " ".join(sql.split())


def _fragmente_nume(fn):
    """Fragmentele literale de forma `nume = …` din corpul funcției — bucățile din care se poate
    asambla un `SET` la rulare."""
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and RE_FRAGMENT_NUME.match(n.value):
            out.append(n.value.strip())
    return out


def analizeaza_sursa(rel, sursa):
    """Aceeasi analiza, pe o sursa data. Exista ca sa poata fi CALIBRATA: un instrument care se
    poate rula numai pe arborele real nu se poate proba pe cazul pe care ar trebui sa-l prinda."""
    out = []
    try:
        arb = ast.parse(sursa)
    except SyntaxError:      # pragma: no cover
        return out
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        fragmente = _fragmente_nume(fn)
        for nod, sql in _executari(fn):
            m = RE_UPDATE.match(sql)
            if not m:
                continue
            tabela, restul = m.group(1).lower(), m.group(2)
            if RE_SET_NUME.search(restul):
                fel = "nume"
            elif re.search(r"\bSET\s*$", restul, re.I) or "\x01" in restul:
                fel = "compus" if fragmente else "alt"
            else:
                fel = "alt"
            out.append((rel, fn.name, tabela, fel, nod.lineno))
    return out


def analizeaza():
    """[(fisier, functie, tabela, fel, linia)] — `fel` in {'nume', 'compus', 'alt'}."""
    out = []
    for rel in fisiere_productie():
        sursa = io.open(os.path.join(RAD, rel), encoding="utf-8").read()
        out += analizeaza_sursa(rel, sursa)
    return out


def asimetrii():
    """Funcțiile care scriu denumirea într-una din tabele și nu în cealaltă."""
    scrie = {}
    for rel, fnume, tabela, fel, ln in analizeaza():
        if fel in ("nume", "compus"):
            scrie.setdefault((rel, fnume), {})[tabela] = ln
    rele = []
    for (rel, fnume), tab in sorted(scrie.items()):
        lipsa = [t for t in TABELE if t not in tab]
        if lipsa:
            rele.append((rel, fnume, sorted(tab), lipsa[0], min(tab.values())))
    return rele


def simetrice():
    """Funcțiile care scriu denumirea în AMÂNDOUĂ tabelele — anti-vacuul verdictului."""
    scrie = {}
    for rel, fnume, tabela, fel, _ln in analizeaza():
        if fel in ("nume", "compus"):
            scrie.setdefault((rel, fnume), set()).add(tabela)
    return sorted(k for k, v in scrie.items() if set(TABELE) <= v)


def compuse():
    """`UPDATE`-urile cu `SET` asamblat la rulare pe una din cele două tabele — clasa despre care
    instrumentul nu poate afirma singur nimic. Se numără, ca să nu crească tăcut."""
    return sorted({(rel, fnume, tabela) for rel, fnume, tabela, fel, _l in analizeaza()
                   if fel == "compus"})


if __name__ == "__main__":
    for r in analizeaza():
        print("  %-34s %-28s %-13s %-7s l.%d" % r)
    print("\nsimetrice: %s" % (simetrice(),))
    print("asimetrii: %s" % (asimetrii(),))
    print("compuse  : %s" % (compuse(),))
