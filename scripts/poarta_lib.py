# -*- coding: utf-8 -*-
"""scripts/poarta_lib.py — piesele comune ale bazei și ale clasificării porții (comanda 16.1, pct.1a).
  nume_stabil / citeste_junit   rezultatul pe test, din raportul junit al pytest (numele = cale::test, fără parametri de rulare)
  asertiuni                     numărul de aserțiuni statice dintr-un test (nodurile `assert` și apelurile assert*/expect*/raises)
  hash_fisier                   sha256 pe fișier (hash-urile scripturilor porții, ale manifestului)"""
import ast
import hashlib
import os
import re
import xml.etree.ElementTree as ET

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def hash_fisier(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest() if os.path.exists(cale) else "lipsa"


def nume_stabil(classname, name, rad):
    """`core.test_x.TestC` + `test_y[p]` -> `core/test_x.py::TestC::test_y[p]`; cu `classname` fără director (plasa e2e, rootdir = e2e) fișierul se caută în frontend_test/e2e."""
    parti = classname.split(".")
    for i in range(len(parti), 0, -1):
        for baza in ("", "frontend_test/e2e/"):
            cale = baza + "/".join(parti[:i]) + ".py"
            if os.path.isfile(os.path.join(rad, cale)):
                return "::".join([cale] + parti[i:] + [name])
    return "::".join([classname, name])


_INFRA = re.compile(r"(Connection refused|Connection reset|could not connect to server|server closed the connection|ECONNREFUSED|ERR_CONNECTION|"
                    r"Target page, context or browser has been closed|aplicația exportului n-a răspuns|OperationalError)", re.I)


def citeste_junit(cale, rad):
    """-> listă de {nume, rezultat: trece|pica|sarit, infra: bool, durata, mesaj}. Un fișier lipsă sau stricat = listă goală."""
    try:
        arbore = ET.parse(cale).getroot()
    except (OSError, ET.ParseError):
        return []
    rez = []
    for tc in arbore.iter("testcase"):
        r, mesaj = "trece", ""
        for fiu in tc:
            if fiu.tag in ("failure", "error"):
                r, mesaj = "pica", (fiu.get("message") or "") + " " + (fiu.text or "")[:2000]
            elif fiu.tag == "skipped" and r == "trece":
                r = "sarit"
        rez.append({"nume": nume_stabil(tc.get("classname", ""), tc.get("name", ""), rad), "rezultat": r,
                    "infra": r == "pica" and bool(_INFRA.search(mesaj)), "durata": round(float(tc.get("time") or 0), 3), "mesaj": mesaj[:300].strip()})
    return rez


def _numara(nod):
    n = 0
    for x in ast.walk(nod):
        if isinstance(x, ast.Assert):
            n += 1
        elif isinstance(x, ast.Call):
            f = x.func
            nume = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if nume.startswith(("assert", "expect")) or nume in ("raises", "fail"):
                n += 1
    return n


def asertiuni(rad, fisier):
    """-> {`Clasa::test` sau `test`: număr}, din AST; fișier lipsă sau care nu se parsează = {}."""
    try:
        arbore = ast.parse(open(os.path.join(rad, fisier), encoding="utf-8").read())
    except (OSError, SyntaxError):
        return {}
    rez = {}
    for nod in arbore.body:
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)) and nod.name.startswith("test"):
            rez[nod.name] = _numara(nod)
        elif isinstance(nod, ast.ClassDef):
            for f in nod.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"):
                    rez[nod.name + "::" + f.name] = _numara(f)
    return rez


def cheie_asertiuni(nume):
    """`cale::[Clasa::]test[param]` -> (cale, `[Clasa::]test`)."""
    p = nume.split("::")
    return p[0], "::".join(p[1:]).split("[")[0]
