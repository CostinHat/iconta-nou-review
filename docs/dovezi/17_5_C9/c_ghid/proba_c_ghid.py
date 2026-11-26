# -*- coding: utf-8 -*-
"""17.5-C9, C-ghid pct.4 — probele gărzii de publicare a ghidurilor pe copii (ghidul și registrul de pe disc nu se ating).
Fiecare caz: o copie a ghidului impozit-dividende-2026.md (mutația minimă), CLI-ul de publicare `python -m core.ghid_poarta <copie>`
cu rc real și mesajul; după fiecare mutație se revine la sursa bună (copia nouă pornește din fișierul neatins). Registrul mutat se
probează prin `verifica_valori_fiscale(corp, cote=<copie a registrului>)`, aceeași funcție pe care o folosește garda.
Uz: ./venv/bin/python docs/dovezi/17_5_C9/c_ghid/proba_c_ghid.py <director_iesire>"""
import copy
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from decimal import Decimal

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, RAD)
GHID = os.path.join(RAD, "ghid", "impozit-dividende-2026.md")

CAZURI = [  # (id, așteptat rc, descriere, înlocuiri [(vechi, nou)] sau adăugare)
    ("P1", 0, "ghidul publicat, neatins", []),
    ("P2", 0, "8% legitim pentru distribuirile din 2024 (frază adăugată)", [("## Ce se greșește în practică", "Un dividend distribuit în 2024 a avut cota de **8%**.\n\n## Ce se greșește în practică")]),
    ("P3", 0, "interimare 2025 regularizate în 2026 la 10% (frază adăugată)", [("## Ce se greșește în practică", "Dividendele distribuite în 2025 pe baza situațiilor interimare, regularizate în 2026, rămân la **10%**.\n\n## Ce se greșește în practică")]),
    ("P4", 0, "alt 10% în context nesupus regulii dividendelor (salarii, art. 78)", [("## Ce se greșește în practică", "Impozitul pe venitul din salarii are cota de **10%** în 2025 (art. 78).\n\n## Ce se greșește în practică")]),
    ("N1", 1, "2025 → 8%", [("- Dividend distribuit în 2025 → **10%**.", "- Dividend distribuit în 2025 → **8%**.")]),
    ("N2", 1, "2026 → 10% pentru o distribuire nouă", [("- Dividend distribuit de la 1 ianuarie 2026 → **16%**", "- Dividend distribuit de la 1 ianuarie 2026 → **10%**")]),
    ("N3", 1, "text corect, exemplu numeric greșit (net 92.000 în loc de 90.000)", [("dividend net **90.000 lei**", "dividend net **92.000 lei**")]),
    ("N4", 1, "afirmația că 10% nu a existat la dividende", [("## Ce face iConta.eu", "Pe dividende cotele au fost 5%, 8% și 16% — niciodată 10%.\n\n## Ce face iConta.eu")]),
    ("N6", 1, "valoare fiscală nouă fără corespondent în registru (2027 → 18%)", [("## Ce se greșește în practică", "Un dividend distribuit în 2027 are cota de **18%**.\n\n## Ce se greșește în practică")]),
]


def ruleaza_cli(cale):
    r = subprocess.run([os.path.join(RAD, "venv", "bin", "python"), "-m", "core.ghid_poarta", cale], cwd=RAD, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main(iesire):
    os.makedirs(iesire, exist_ok=True)
    bun = open(GHID, encoding="utf-8").read()
    rap, rele = [], 0
    tmp = tempfile.mkdtemp(prefix="c_ghid_")
    for id_, rc_ast, desc, inloc in CAZURI:
        txt = bun
        for v, n in inloc:
            assert txt.count(v) == 1, (id_, v)
            txt = txt.replace(v, n)
        cale = os.path.join(tmp, "impozit-dividende-2026.md")   # același slug, copie
        open(cale, "w", encoding="utf-8").write(txt)
        rc, out = ruleaza_cli(cale)
        ok = (rc == rc_ast)
        rele += not ok
        rap.append("## %s — %s\nrc așteptat %d, rc real %d → %s\n%s\n" % (id_, desc, rc_ast, rc, "CONFORM" if ok else "NECONFORM", out))
    # N5: schimbare numai în registru (2025 → 8%), ghidul rămas în urmă; P5: registrul neschimbat
    from core import common as c, ghid_poarta as gp
    _m, corp = gp._frontmatter(bun)
    reg = copy.deepcopy(c.COTE)
    reg["impozit_dividend"] = [(d, (Decimal("0.08") if d == date(2025, 1, 1) else v), t) for d, v, t in reg["impozit_dividend"]]
    ab_n5 = gp.verifica_valori_fiscale(corp, cote=reg)
    ab_p5 = gp.verifica_valori_fiscale(corp)
    rele += (not ab_n5) + bool(ab_p5)
    rap.append("## N5 — schimbare numai în registru (2025 → 8%%), ghid rămas în urmă\nabateri: %d → %s\n%s\n" % (
        len(ab_n5), "CONFORM" if ab_n5 else "NECONFORM", "\n".join(gp._mesaj_valoare("impozit-dividende-2026", a) for a in ab_n5)))
    rap.append("## P5 — registrul de pe disc, după revenire\nabateri: %d → %s\n" % (len(ab_p5), "CONFORM" if not ab_p5 else "NECONFORM"))
    rc, out = ruleaza_cli(GHID)
    rap.append("## Revenire — ghidul de pe disc prin CLI\nrc %d\n%s\n" % (rc, out))
    shutil.rmtree(tmp)
    open(os.path.join(iesire, "proba_c_ghid.txt"), "w", encoding="utf-8").write("\n".join(rap) + "\nNECONFORME: %d\n" % rele)
    print("\n".join(rap)); print("NECONFORME:", rele)
    return 1 if rele else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
