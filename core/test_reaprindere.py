# -*- coding: utf-8 -*-
"""GARD: o restanță al cărei DECLANȘATOR s-a produs nu poate rămâne nereluată.

CE FACE IMPOSIBIL. `PLAN_LUCRU.md` („Reaprinderea") cere ca la fiecare tură să se verifice ce
restanțe au blocajul dispărut. Măsurat pe 23.08.2026, la cererea lui Costin: **reaprinderea n-a
funcționat niciodată** — câmpul `reluări` era **0 pe toate cele 25 de restanțe**, de la prima până la
ultima. Iar condiția lui **R8** — *„la primul commit care atinge `d223.py` ori `d406.py`"* — se
declanșase de **două** ori chiar în ziua aceea, prin commituri proprii, fără ca nimeni s-o observe.

Regula era scrisă și nepăzită, deci se citea ca respectată. Gardul o face mecanică pentru clasa în
care declanșatorul E mecanic: o condiție care numește un FIȘIER și cuvântul „atinge".

CE NU FACE, declarat: nu verifică dacă restanța a fost și REZOLVATĂ — reaprinderea e reluare, nu
rezolvare. Și nu vede declanșatoarele care nu sunt fișiere („la punctul de decizie 2", „când există
iar clustere"): acelea rămân de citit de om. Gardul închide clasa mecanică, nu clasa întreagă.
"""
import io
import os
import re
import subprocess

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(_RAD, "CONFORMITATE.md")
_FIS = re.compile(r"`([A-Za-z0-9_/]+\.(?:py|js|sql|json))`")


def _git(*a):
    return subprocess.run(["git"] + list(a), cwd=_RAD, capture_output=True, text=True).stdout.strip()


def _restante():
    t = io.open(CONF, encoding="utf-8").read()
    m = re.search(r"^## RESTANȚE[ \t]*$(.*?)^## ", t, re.M | re.S)
    assert m, "CONFORMITATE.md n-are secțiunea RESTANȚE"
    out = {}
    for b in re.finditer(r"^### (R\d+) — (.*?)$(.*?)(?=^### R\d+|\Z)", m.group(1), re.M | re.S):
        corp = b.group(3)

        def g(nume):
            mm = re.search(r"^- \*\*%s\*\*: (.*)$" % nume, corp, re.M)
            return mm.group(1).strip() if mm else ""

        out[b.group(1)] = {"titlu": b.group(2).strip(), "stare": g("stare").strip("* "),
                           "reluari": g("reluări").strip("* "), "cond": g("condiția de deblocare"),
                           "commit": g("deschisă pe commit").strip("`")}
    return out


def _declansatoare():
    """[(cod, fișier, commit_deschidere, reluări)] pentru restanțele DESCHISE cu declanșator MECANIC:
    condiția numește un fișier ȘI cuvântul «atinge». Un fișier citat ca INSTRUMENT („garda
    `test_x.py` transformă tăcerea în poartă") nu e un declanșator — de-aia se cere verbul."""
    out = []
    for cod, r in sorted(_restante().items(), key=lambda x: int(x[0][1:])):
        if "DESCHISĂ" not in r["stare"] or not r["commit"] or "atinge" not in r["cond"]:
            continue
        for f in sorted(set(_FIS.findall(r["cond"]))):
            out.append((cod, f, r["commit"], r["reluari"]))
    return out


def _cale_reala(f):
    for c in (f, os.path.join("core", f), os.path.join("scripts", f)):
        if os.path.exists(os.path.join(_RAD, c)):
            return c
    return None


def test_ANTIVACUU_exista_macar_un_declansator_mecanic():
    """Fără nicio condiție de forma «la primul commit care atinge X», gardul de mai jos ar trece pe
    zero rânduri și ar raporta verde despre o regulă pe care n-o verifică."""
    d = _declansatoare()
    assert d, ("nicio restanță deschisă n-are declanșator mecanic — ori s-au închis toate, ori "
               "formularea condițiilor s-a schimbat și regexul nu le mai vede")


def test_o_restanta_cu_declansatorul_produs_a_fost_RELUATA():
    """Miezul. Dacă fișierul numit în condiție s-a schimbat de la deschiderea restanței, momentul a
    venit — iar `reluări` trebuie să fi crescut. Zero după declanșare = reaprinderea nu s-a făcut."""
    rele = []
    for cod, f, sha, reluari in _declansatoare():
        cale = _cale_reala(f)
        if not cale:
            continue
        log = _git("log", "--oneline", "%s..HEAD" % sha, "--", cale)
        if not log:
            continue
        n = len(log.splitlines())
        try:
            k = int(reluari)
        except ValueError:
            k = 0
        if k == 0:
            rele.append("  %s: condiția numește `%s`, atins de %d commituri de la `%s`, dar "
                        "`reluări` = %s" % (cod, f, n, sha, reluari or "(lipsă)"))
    assert not rele, (
        "restanțe al căror declanșator s-a produs și care n-au fost reluate:\n" + "\n".join(rele)
        + "\n\nReaprinderea nu e opțională (`PLAN_LUCRU.md`): se reia, se scrie rezultatul în raport, "
          "iar `reluări` crește. Dacă reluarea a avut loc și n-a mers, contorul crește oricum — "
          "de trei ori înseamnă că e greșită condiția, nu restanța.")


def test_contorul_de_reluari_e_un_numar():
    """Un contor scris ca text nu se poate compara cu pragul de trei din `PLAN_LUCRU.md`."""
    rele = [c for c, r in _restante().items() if not r["reluari"].isdigit()]
    assert not rele, "restanțe cu `reluări` necitibil ca număr: %s" % rele


def test_pragul_de_trei_reluari_e_respectat():
    """`PLAN_LUCRU.md`: «reluată de trei ori și tot nerezolvată → condiția de deblocare e scrisă
    greșit». Peste trei, fără rescrierea condiției, e a patra reluare pe aceeași condiție."""
    rele = ["  %s: reluări = %s" % (c, r["reluari"])
            for c, r in sorted(_restante().items())
            if "DESCHISĂ" in r["stare"] and r["reluari"].isdigit() and int(r["reluari"]) > 3]
    assert not rele, ("restanțe reluate de peste trei ori pe aceeași condiție — rescrie condiția, "
                      "prin decizie, cu motivul:\n" + "\n".join(rele))
