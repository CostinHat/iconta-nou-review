# -*- coding: utf-8 -*-
"""17.5-C9 pct.4 — probele regulilor C9 prin GARDA REALĂ (verificator_conformitate.py, intrarea normală, cea din
scripts/inainte_de_commit.sh și din treapta verificatorului a porții), pe o copie: un worktree git detașat al commitului dat.
Trei rulări ale verificatorului întreg, cu codul de retur și ieșirea păstrate:
  1. «inainte»: pe copia commitului de BAZĂ, cu verificatorul C9 adus peste ea (abaterile mecanice ale bazei);
  2. «negative»: pe copia candidatului, cu mutațiile minime locale de mai jos (fiecare trebuie să dea constatarea așteptată: ID, fișier, linie,
     motiv), un ecran NOU într-un subdirector în afara ecranelor martor (inventarul și garda trebuie să-l descopere), cazul exceptat (api.js) și
     cazul asemănător refuzat (aceeași linie în alt fișier);
  3. «revenire»: aceeași copie, exemplarul bun pus la loc -> constatările dispar, TOTAL: 0.
Judecata TOTAL urmează scripts/inainte_de_commit.sh («TOTAL: 0» = verde; altfel roșu, rc 1).
Uz: ./venv/bin/python docs/dovezi/17_5_C9/verificator/proba_verificator.py <commit_baza> <commit_candidat> <director_iesire>"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# (id, fișier relativ, text vechi, text nou, regula așteptată, fișierul așteptat în constatare)
MUTATII = [
    ("N-MINUS-1", "static/js/ecrane/pachete.js", 'function bani(x){ return baniSemn(x) + " lei"; }',
     'function bani(x){ try { return Number(x).toLocaleString("ro-RO",{minimumFractionDigits:2,maximumFractionDigits:2}) + " lei"; } catch { return x; } }',
     "C9-MINUS", "pachete.js"),
    ("N-MINUS-2", "static/js/ecrane/emitere_ecran.js", 'total ${baniSemn(r.total)} ${monedaSel}', 'total ${"-" + bani(-r.total)} ${monedaSel}', "C9-MINUS", "emitere_ecran.js"),
    ("N-REZUMAT", "static/js/ecrane/control_verdict.js", None, '\nexport const _probaC9Rezumat = (t) => String(t).split(". ")[0];\n', "C9-REZUMAT", "control_verdict.js"),
    ("N-F018-a", "static/js/ecrane/clienti_ecran.js", '<button type="button" class="buton-primar" id="pt-nou" data-actiune-principala',
     '<button type="button" class="buton-secundar" id="pt-nou" data-actiune-principala', "C9-F018", "clienti_ecran.js"),
    ("N-F018-b", "static/js/ecrane/clienti_ecran.js", '<button type="button" class="buton-secundar" id="pt-pdf"',
     '<button type="button" class="buton-primar" id="pt-pdf" data-actiune-principala', "C9-F018", "clienti_ecran.js"),
    ("N-F019", "static/js/ds_piese.js", "{ pre, pePagina = 8, stare,", "{ pre, pePagina = 10, stare,", "C9-F019", "ds_piese.js"),
    ("N-NOU", "static/js/ecrane/proba_c9/ecran_nou.js", None,
     '// ecran nou de probă (17.5-C9), în afara ecranelor martor\nexport function randeazaProba(corp, v) {\n'
     '  corp.innerHTML = `<p>Total ${Number(v).toLocaleString("ro-RO", {minimumFractionDigits: 2})} lei</p>`;\n}\n', "C9-MINUS", "proba_c9/ecran_nou.js"),
    ("N-SIMILAR", "static/js/ds_piese.js", None,
     '\nexport const _probaC9Similar = (n) => Number(n).toLocaleString("ro-RO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });\n', "C9-MINUS", "ds_piese.js"),
]


def sh(*a, cwd=None):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True)


def copie(commit):
    d = tempfile.mkdtemp(prefix="vc_c9_")
    os.rmdir(d)
    r = sh("git", "worktree", "add", "--detach", d, commit, cwd=RAD)
    if r.returncode:
        raise SystemExit("worktree: " + r.stderr)
    for n in ("venv", "import_fiscalos"):
        os.symlink(os.path.join(RAD, n), os.path.join(d, n))
    return d


def sterge(d):
    sh("git", "worktree", "remove", "--force", d, cwd=RAD)
    shutil.rmtree(d, ignore_errors=True)


def ruleaza(d, iesire, eticheta):
    r = sh(os.path.join(d, "venv", "bin", "python"), "verificator_conformitate.py", "--inventar", os.path.join(iesire, "inventar_%s.tsv" % eticheta), cwd=d)
    out = r.stdout + r.stderr
    open(os.path.join(iesire, "verificator_%s.txt" % eticheta), "w", encoding="utf-8").write(out + "\nrc=%d\n" % r.returncode)
    tot = re.search(r"TOTAL: (\d+)", out)
    rc_poarta = 0 if tot and tot.group(1) == "0" else 1       # aceeași judecată ca scripts/inainte_de_commit.sh
    c9 = re.findall(r"^\s+(\S+)\s+(\d+)\s+(C9-[A-Z0-9-]+)\s+(.*)$", out, re.M)
    return rc_poarta, int(tot.group(1)) if tot else None, c9, out


def main(baza, cand, iesire):
    iesire = os.path.abspath(iesire)
    os.makedirs(iesire, exist_ok=True)
    rap = []
    # 1. «inainte»: baza, cu verificatorul C9
    d = copie(baza)
    try:
        shutil.copy(os.path.join(RAD, "verificator_conformitate.py"), os.path.join(d, "verificator_conformitate.py"))
        rc, tot, c9, _ = ruleaza(d, iesire, "inainte_baza")
        rap.append("## 1. Înainte — baza %s cu verificatorul C9\nrc poartă %d, TOTAL %s\n%s\n" % (baza[:12], rc, tot, "\n".join("  %s:%s %s %s" % x for x in c9)))
    finally:
        sterge(d)
    # 2. negative + 3. revenire, pe candidat
    d = copie(cand)
    rele = 0
    try:
        bune = {}
        for id_, rel, vechi, nou, regula, fis in MUTATII:
            cale = os.path.join(d, rel)
            if vechi is None:
                os.makedirs(os.path.dirname(cale), exist_ok=True)
                bune.setdefault(rel, open(cale, encoding="utf-8").read() if os.path.exists(cale) else None)
                with open(cale, "a", encoding="utf-8") as f:
                    f.write(nou)
            else:
                t = open(cale, encoding="utf-8").read()
                assert t.count(vechi) == 1, (id_, vechi)
                bune.setdefault(rel, t)
                open(cale, "w", encoding="utf-8").write(t.replace(vechi, nou))
        rc, tot, c9, out = ruleaza(d, iesire, "negative")
        rap.append("## 2. Negative — candidat %s cu mutațiile minime\nrc poartă %d, TOTAL %s" % (cand[:12], rc, tot))
        for id_, rel, vechi, nou, regula, fis in MUTATII:
            gasite = [x for x in c9 if x[2] == regula and x[0] == fis]
            ok = bool(gasite)
            rele += not ok
            rap.append("  %s → %s în %s: %s%s" % (id_, regula, fis, "CONSTATAT" if ok else "NECONSTATAT", ("  [%s]" % "; ".join("%s:%s %s" % (g[0], g[1], g[3][:90]) for g in gasite)) if gasite else ""))
        exceptat = [x for x in c9 if x[0] == "api.js"]
        rap.append("  exceptat api.js (sursa canonică, EXCEPTII_C9): %s" % ("NICIO CONSTATARE (corect)" if not exceptat else "CONSTATAT (greșit)"))
        rele += bool(exceptat)
        inv = open(os.path.join(iesire, "inventar_negative.tsv"), encoding="utf-8").read()
        nou_inv = "proba_c9/ecran_nou.js" in inv
        rap.append("  ecranul nou în inventar: %s" % ("DA" if nou_inv else "NU"))
        rele += not nou_inv
        rele += rc != 1
        # 3. revenire
        for rel, t in bune.items():
            cale = os.path.join(d, rel)
            if t is None:
                os.remove(cale)
            else:
                open(cale, "w", encoding="utf-8").write(t)
        shutil.rmtree(os.path.join(d, "static/js/ecrane/proba_c9"), ignore_errors=True)
        rc2, tot2, c92, _ = ruleaza(d, iesire, "revenire")
        rap.append("## 3. Revenire — exemplarul bun la loc\nrc poartă %d, TOTAL %s, constatări C9: %d\n" % (rc2, tot2, len(c92)))
        rele += rc2 != 0 or bool(c92)
    finally:
        sterge(d)
    rap.append("NECONFORME: %d" % rele)
    open(os.path.join(iesire, "proba_verificator.txt"), "w", encoding="utf-8").write("\n".join(rap) + "\n")
    print("\n".join(rap))
    return 1 if rele else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
