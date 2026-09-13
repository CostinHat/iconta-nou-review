# -*- coding: utf-8 -*-
"""P7 — TOATE criteriile canonice, nu doar cele trei detectoare.

DE CE EXISTA (13.09.2026, la capatul valului D4). Dupa D4, contabilitatea P7 arata asa:
`D1`=0, `D2`=0, `D4`=0, `P7_ACTION_REQUIRED`=**0**. Citita singura, cifra spune „faza e gata".
Nu e: textul canonic (`PLAN_HARDENING.md:733-817`) cere **separarea HTTP -> use-case -> motor fiscal
-> repository**, iar despre use-case spune ca **detine tranzactia (P4) si orchestreaza**. Masurat
aici: **385 din 421 de rute isi deschid singure tranzactia**, deci stratul HTTP orchestreaza in
continuare si stratul use-case aproape ca nu exista.

*Un `ACTION_REQUIRED=0` care nu acopera un criteriu canonic nu e o stare, e o lipsa de detector.*
Instrumentul asta inchide golul: masoara criteriul si il da drept cifra, ca sa nu mai depinda de
proza cuiva ca faza ramane deschisa.

CE MASOARA, si de unde:
  · `D1/D2/D4` — din `scripts/scan_p7_straturi.py` (nu se recalculeaza aici, se citesc);
  · `RUTE_TOTAL` si `RUTE_CARE_DESCHID_SINGURE_TRANZACTIA` — pe AST, in `main.py`: o ruta care
    cheama `get_conn` in corpul ei detine tranzactia, deci face munca de use-case;
  · `RUTE_CARE_CHEAMA_UN_USE_CASE` — rutele care deleaga catre un modul declarat `USE_CASE`;
  · `MODULE_USE_CASE_DECLARATE` — din registrul de straturi.

CE NU MASOARA, declarat: daca separarea e *buna*, doar daca EXISTA. O ruta care cheama un use-case
poate face oricat de multa orchestrare pe langa; cifra de aici e un plafon superior al progresului,
nu o nota.
"""
import ast
import collections
import io
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RAD, os.path.join(RAD, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

METODE_HTTP = ("get", "post", "put", "patch", "delete", "head", "options")


def _arbore(cale):
    return ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())


def rute_din_main():
    """Functiile din `main.py` decorate cu o metoda HTTP — aceeasi populatie ca la D1."""
    out = []
    for n in ast.walk(_arbore("main.py")):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            f = d.func if isinstance(d, ast.Call) else d
            if isinstance(f, ast.Attribute) and f.attr in METODE_HTTP:
                out.append(n)
                break
    return out


def _cheama(fn, nume):
    for x in ast.walk(fn):
        if isinstance(x, ast.Call):
            f = x.func
            if isinstance(f, ast.Attribute) and f.attr == nume:
                return True
            if isinstance(f, ast.Name) and f.id == nume:
                return True
    return False


def _module_use_case():
    from core import straturi as R
    return {os.path.basename(d.cale)[:-3] for d in R.REGISTRU if d.strat == R.USE_CASE}


def _cheama_use_case(fn, module):
    """Delegare catre un modul declarat `USE_CASE`, citita pe AST (atribut sau nume importat)."""
    for x in ast.walk(fn):
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) and x.value.id in module:
            return True
        if isinstance(x, ast.ImportFrom) and (x.module or "") == "core":
            if any(a.name in module for a in x.names):
                return True
    return False


def detaliu():
    """(numaratori, {clasa: [nume de rute]}) — cifra si lista, ca la restul instrumentelor P7."""
    import scan_p7_straturi as S
    module = _module_use_case()
    rute = rute_din_main()
    detin, deleaga = [], []
    for fn in rute:
        if _cheama(fn, "get_conn"):
            detin.append(fn.name)
        if _cheama_use_case(fn, module):
            deleaga.append(fn.name)
    n = collections.OrderedDict()
    n["D1_SQL_IN_RUTA"] = len(S.d1_sql_in_ruta()[0])
    n["D2_MOTOR_FISCAL_CU_DB"] = len(S.d2_motor_fiscal_cu_db())
    n["D4_STRAT_MIXT"] = len(S.d4_strat_mixt())
    n["RUTE_TOTAL"] = len(rute)
    n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"] = len(detin)
    n["RUTE_CARE_CHEAMA_UN_USE_CASE"] = len(deleaga)
    n["MODULE_USE_CASE_DECLARATE"] = len(module)
    return n, {"detin_tranzactia": sorted(detin), "deleaga": sorted(deleaga),
               "use_case": sorted(module)}


def numaratori():
    return detaliu()[0]


def criterii():
    """[(nume, satisfacut, cifra, temei)] — verdictul pe fiecare criteriu canonic."""
    n = numaratori()
    return [
        ("ruta nu contine SQL", n["D1_SQL_IN_RUTA"] == 0, n["D1_SQL_IN_RUTA"],
         "PLAN_HARDENING.md:812"),
        ("un motor fiscal nu importa `db`", n["D2_MOTOR_FISCAL_CU_DB"] == 0,
         n["D2_MOTOR_FISCAL_CU_DB"], "PLAN_HARDENING.md:811"),
        ("niciun modul nu face doua straturi deodata", n["D4_STRAT_MIXT"] == 0,
         n["D4_STRAT_MIXT"], "PLAN_HARDENING.md:804-808"),
        ("use-case-ul detine tranzactia, nu ruta",
         n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"] == 0,
         n["RUTE_CARE_DESCHID_SINGURE_TRANZACTIA"], "PLAN_HARDENING.md:806"),
    ]


def se_poate_inchide():
    return all(ok for _nume, ok, _cifra, _temei in criterii())


def main():
    n, d = detaliu()
    print("P7 — CRITERIILE CANONICE, masurate")
    for k, v in n.items():
        print("  %-40s %5d" % (k, v))
    print()
    for nume, ok, cifra, temei in criterii():
        print("  [%s] %-46s cifra=%-5d %s" % ("DA " if ok else "NU ", nume, cifra, temei))
    print()
    print("SE POATE INCHIDE P7:", "DA" if se_poate_inchide() else "NU")
    if not se_poate_inchide():
        print("  rute care isi deschid singure tranzactia, primele 10: %s"
              % d["detin_tranzactia"][:10])
    print("  use-case-uri declarate: %s" % d["use_case"])


if __name__ == "__main__":
    main()
