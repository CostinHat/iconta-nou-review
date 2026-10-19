# -*- coding: utf-8 -*-
"""GARDA DE CLASĂ — regula importurilor de migrare (comanda Costin 8.2 pct.4, 18.10.2026, verbatim în DECIZII „Comanda 8.2”):

    „orice rând citit e afișat sau semnalat cu motiv, nimic nu se înlocuiește pe tăcute, totul trece prin previzualizare înainte de
    salvare, erorile interne nu ajung la utilizator, modelele se deschid pe coloane în Excel.”

Clasa a ieșit în 341–381 pe fiecare import în parte: rândul fără nume dispărea (364), rândul fără denumire dispărea (373), rândul fără
rețetă dispărea (375), RIP-ul scria fără previzualizare și arăta eroarea Postgres-ului (372). Garda le ia pe TOATE, nu pe cele găsite:
  1. fiecare parser de import păstrează orice rând cu date (cel fără câmpul-cheie inclus) — sau îl spune, cu motiv, în lista ignoratelor;
  2. fiecare rută `/tenants/{tenant_id}/…/incarca` are previzualizarea ei pe tabelul comun (`tabelPrevizualizare` + `bandaStari`);
  3. niciun handler `except Exception` din importuri nu pune textul excepției într-un mesaj (ar ajunge la contabil).
(Modelele pe coloane: `core/test_c4_model_csv.py`.)
"""
import ast
import glob
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNP = "1800101221144"      # cifra de control verificată (algoritmul din CLAUDE.md)
CUI_A, CUI_B = "14399840", "12345674"   # cifra de control verificată

#: parser -> (fișierul minim: rândul 2 complet, rândul 3 cu date dar FĂRĂ câmpul-cheie, rândul 4 gol, rândul 5 complet)
MOSTRE = {
    "core.salariati_import_api:extrage": "Nume;CNP;Salariu brut\nPop Ion;%s;5000\n;;4000\n;;\nIon Pop;%s;4500\n" % (CNP, CNP),
    "core.asociati_import_api:extrage": "Nume;CNP;Cota\nPop Ion;%s;60\n;;40\n;;\nIon Pop;%s;0\n" % (CNP, CNP),
    "core.mijloace_fixe_import_api:extrage": "Cod;Denumire;Valoare\nMF1;Laptop;5000\nMF2;;3000\n;;\nMF3;Imprimanta;900\n",
    "core.istoric_declaratii_import_api:extrage": "Tip;Luna;An\nD300;09;2026\n;09;2026\n;;\nD112;09;2026\n",
    "core.articole_import_api:extrage": "Denumire;UM;Cantitate;Pret;Cont stoc\nA;buc;1;2;371\n;buc;1;2;371\n;;;;\nB;kg;2;3;371\n",
    "core.retete_import_api:extrage": "Reteta;Pret;Ingredient;Cantitate\nPizza;25;Faina;0.2\n;25;Sare;1\n;;;\nSupa;12;Apa;1\n",
    "core.rip_migrare_api:extrage": "Data;Tip;Explicatie;Suma\n15.01.2026;incasare;vanzare;10\n;incasare;fara data;5\n;;;\n16.01.2026;plata;chirie;3\n",
}


def _fn(cale):
    mod, nume = cale.split(":")
    return getattr(__import__(mod, fromlist=["x"]), nume)


@pytest.mark.parametrize("cale", sorted(MOSTRE))
def test_fiecare_rand_cu_date_se_citeste(cale):
    """Rândul cu date dar fără câmpul-cheie NU dispare: iese din parser cu numărul lui din fișier (verdictul îl dă `verifica_randuri`).
    MUTAȚIA: `if not den: continue` repus în `articole_import_api.extrage` -> ROȘU pe articole (rândul 3 lipsește)."""
    rez = _fn(cale)(MOSTRE[cale].encode("utf-8"), "m.csv")
    citite = sorted(int(r["rand_fisier"]) for r in rez)
    assert citite == [2, 3, 5], "%s: rândurile citite %s, așteptat [2, 3, 5] (3 = fără câmpul-cheie, 4 = gol)" % (cale, citite)


def test_partenerii_care_nu_intra_sunt_spusi():
    """Situația partenerilor: rândul de total și partenerul cu sold 0 nu intră, dar se SPUN (`ignorate`), nu se sar în tăcere.
    MUTAȚIA: `ignorate.append` scos din ramura soldului 0 -> ROȘU (rândul 4 nu e nici citit, nici spus)."""
    from core import solduri_parteneri_api as sp
    csv = "Cont;CUI;Denumire;Debit;Credit\n4111;%s;Alfa;10;0\n4111;;Total;10;0\n4111;%s;Beta;0;0\n" % (CUI_A, CUI_B)
    ignorate = []
    rez = sp.extrage(csv.encode("utf-8"), "p.csv", ignorate=ignorate)
    vazute = sorted([int(r["rand_fisier"]) for r in rez] + [int(x["rand"]) for x in ignorate])
    assert vazute == [2, 3, 4], "rânduri citite sau spuse: %s" % vazute
    assert all(x["motiv"] for x in ignorate)


def _functii_js(src):
    """{nume: corp} pentru funcțiile de nivel superior din modulul JS (corpul = până la următoarea funcție de nivel superior)."""
    poz = [(m.start(), m.group(1)) for m in re.finditer(r"^(?:async )?function (\w+)\(", src, re.M)]
    return {n: src[p:(poz[i + 1][0] if i + 1 < len(poz) else len(src))] for i, (p, n) in enumerate(poz)}


def test_fiecare_import_are_previzualizare_pe_tabelul_comun():
    """Fiecare rută `/tenants/{tenant_id}/…/incarca` are o previzualizare, iar fiecare previzualizare arată rândurile pe tabelul comun, cu
    starea fiecăruia. Un import nou fără previzualizare (cum era RIP-ul până la 372) schimbă numărătoarea -> ROȘU.
    MUTAȚIA: `tabelPrevizualizare(` scos din `previzualizeazaRip` -> ROȘU."""
    rute = re.findall(r'@app\.post\("/tenants/\{tenant_id\}/([\w-]+)/incarca"\)', open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    fn = _functii_js(open(os.path.join(RAD, "static", "js", "ecrane", "migrare.js"), encoding="utf-8").read())
    prev = {n: c for n, c in fn.items() if n.startswith("previzualizeaza")}
    assert len(rute) >= 9, "anti-vacuu: %d rute de încărcare citite" % len(rute)
    assert len(prev) == len(rute), "rute de încărcare %s, previzualizări %s" % (sorted(rute), sorted(prev))
    fara = [n for n, c in prev.items() if "tabelPrevizualizare(" not in c or "bandaStari(" not in c]
    assert not fara, "previzualizări fără tabelul comun / banda stărilor: %s" % fara


#: modulele importurilor de migrare (parsere + verificări) și use-case-urile lor
MODULE = sorted(set(glob.glob(os.path.join(RAD, "core", "*_import_api.py"))) |
                {os.path.join(RAD, "core", f) for f in ("rip_migrare_api.py", "solduri_api.py", "solduri_parteneri_api.py",
                                                         "uc_migrare.py", "audit_preluare.py")})


#: unde are voie să ajungă excepția: jurnalul aplicației (`_obs.esec_secundar`, `logging…exception/warning/error`) și mesajul ANAF care
#: citește numai codul răspunsului (`anaf_api.mesaj_indisponibil` — „niciodată textul excepției”)
_JURNAL = ("esec_secundar", "exception", "warning", "error", "mesaj_indisponibil")


def _jurnal(f):
    return isinstance(f, ast.Attribute) and f.attr in _JURNAL


def test_nicio_exceptie_interna_in_mesaj():
    """Un handler `except Exception` (sau fără tip) care pune textul excepției într-un mesaj îl duce la contabil — „date/time field value
    out of range… HINT: datestyle” (372). Excepțiile de domeniu (`ValueError` cu textul nostru) rămân permise.
    MUTAȚIA: `% e` repus în constatarea gri din `audit_preluare.audit` -> ROȘU."""
    rele = []
    for fn in MODULE:
        arb = ast.parse(open(fn, encoding="utf-8").read())
        for h in ast.walk(arb):
            if not isinstance(h, ast.ExceptHandler) or not h.name:
                continue
            tip = h.type
            generic = tip is None or (isinstance(tip, ast.Name) and tip.id in ("Exception", "BaseException"))
            if not generic:
                continue
            for n in ast.walk(ast.Module(body=h.body, type_ignores=[])):
                if not (isinstance(n, ast.Call) or isinstance(n, (ast.BinOp, ast.JoinedStr))):
                    continue
                if isinstance(n, ast.Call) and _jurnal(n.func):
                    continue                       # jurnalul aplicației și mesajul fără textul excepției: permise
                if isinstance(n, ast.Call):
                    args = list(n.args) + [k.value for k in n.keywords]
                    if any(isinstance(a, ast.Name) and a.id == h.name for a in args):
                        rele.append("%s:%d" % (os.path.basename(fn), n.lineno))
                elif any(isinstance(x, ast.Name) and x.id == h.name for x in ast.walk(n)):
                    rele.append("%s:%d" % (os.path.basename(fn), n.lineno))
    assert not rele, "textul unei excepții interne poate ajunge la utilizator: %s" % rele
