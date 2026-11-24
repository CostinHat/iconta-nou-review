"""17.5-R2 pct.3 — semnalarea posibilelor erori din cele 210 texte (numai citire; Code nu corectează textele, decizia R2).
Semnale mecanice: cuvinte uzuale fără diacritice (fără formele corecte «lunii», «factura», «intre», care dau numai alarme false), spațiu înaintea punctuației, spații duble, mențiuni ale funcțiilor arhivate
(cont gratuit, link de plată), ID-uri F### din registrul arhivat. Fiecare semnal se judecă apoi de mână."""
import csv, re, sys
from pathlib import Path
D = Path(__file__).resolve().parents[1]
RAD = D.parents[2]
arh = {r[2] for r in csv.reader(open(RAD / "FUNCTIONALITATI_ARHIVA.csv", encoding="utf-8", newline=""))}
txt = (D / "texte_ajutor_revizuite_final_17_5_R2.txt").read_text(encoding="utf-8")
FARA = re.compile(r"\b(si|sa|fara|daca|in|inainte|dupa|catre|aplicatia|declaratie|contabila|cand|tara)\b")
for bloc in txt.split("=== ")[1:]:
    fid, _, corp = bloc.partition("\n")
    for n, rand in enumerate(corp.splitlines(), 1):
        semne = []
        if FARA.search(rand): semne.append("posibil fără diacritice: " + ", ".join(sorted(set(FARA.findall(rand)))))
        if re.search(r"\s[,.;:!?](\s|$)", rand): semne.append("spațiu înainte de punctuație")
        if "  " in rand: semne.append("spații duble")
        if re.search(r"(?i)gratuit|link de plat|link plat", rand): semne.append("menționează o funcție mutată în arhivă (cont gratuit / link de plată)")
        for f in sorted(set(re.findall(r"\bF\d{3}\b", rand)) & arh): semne.append("ID arhivat " + f)
        for s in semne: print(f"{fid.strip()} | rândul {n} | {s} | {rand[:160]}")
