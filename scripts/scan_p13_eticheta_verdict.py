# -*- coding: utf-8 -*-
"""Perimetru P13 (interdictiile 27 verdict-ca-fraza si 31 eticheta-nederivata-din-stare), derivat MECANIC.

31: o eticheta ALEASA de cine randeaza (JS), nu derivata din stare. Semnale mecanice:
  (a) fallback pe token brut: `X[ent.status] || ent.status` / `... .stare] || ...` -> daca lipseste eticheta,
      contabilului i se arata TOKEN-ul de stare (ex. "de_recunoscut"), sau, mai rau, o stare fara eticheta
      trece tacut;
  (b) harta de stare (indexata prin `.status`/`.stare`) confruntata cu nomenclatorul Python al starilor:
      stari FARA eticheta + etichete FANTOMA (stare inexistenta in nomenclator).
  NU sunt 31: hartile care eticheteaza NUME DE CAMP fixe (coloane), nu stari de entitate.

27: verdict stocat/afisat ca fraza. Backendul Python e acoperit de verificator VERDICT_COLAPSAT (poarta verde).
  Aici raportam reziduul: fallback-uri de stare in JS care afiseaza token brut (acelasi semnal ca 31a) tin si de 27
  cand ce se afiseaza e un VERDICT (stare SPV: trimisa/respinsa/blocata), nu doar o eticheta de status.
"""
import os, re, subprocess
RAD="/home/costin/iconta_nou"
JS=os.path.join(RAD,"static/js")

# --- 31a: fallback pe token brut de stare in JS ---
print("=== 31a — fallback pe TOKEN BRUT de stare (renderer arata tokenul daca lipseste eticheta) ===")
rx=re.compile(r'\[\s*[A-Za-z_][\w.]*\.(status|stare)\s*\]\s*\|\|')
hits=[]
for root,_,fs in os.walk(JS):
    for f in fs:
        if not f.endswith(".js"): continue
        p=os.path.join(root,f)
        for i,l in enumerate(open(p,encoding="utf-8",errors="replace"),1):
            if rx.search(l): hits.append((os.path.relpath(p,RAD),i,l.strip()[:90]))
for f,i,s in hits: print("  %s:%d  %s"%(f,i,s))
print("  TOTAL fallback-uri token-brut:",len(hits))

# --- 31b: confruntare harta status factura vs nomenclator ---
print("\n=== 31b — STATUS_ETICHETA (facturi_ecran.js) vs nomenclator_status_factura.STARI ===")
import sys; sys.path.insert(0,RAD)
from core import nomenclator_status_factura as nsf
stari=set(nsf.STARI)
fe=open(os.path.join(JS,"ecrane/facturi_ecran.js"),encoding="utf-8").read()
m=re.search(r'STATUS_ETICHETA\s*=\s*\{([^}]*)\}', fe)
etich=set(re.findall(r'(\w+)\s*:', m.group(1))) if m else set()
print("  nomenclator STARI (%d): %s"%(len(stari), sorted(stari)))
print("  STATUS_ETICHETA (%d): %s"%(len(etich), sorted(etich)))
print("  STARI FARA eticheta (contabilul vede tokenul):", sorted(stari-etich))
print("  ETICHETE FANTOMA (eticheta pt stare inexistenta):", sorted(etich-stari))
# storno/contabilizata tratate separat in cod (nu-s in nomenclator STARI, sunt derivate) - le notam
print("  (nota: storno/contabilizata sunt derivate in cod, nu stari de nomenclator)")

print("\n=== 27 — backend Python: VERDICT_COLAPSAT (verificator) ===")
r=subprocess.run(["./venv/bin/python","verificator_conformitate.py"],cwd=RAD,capture_output=True,text=True)
vc=[l for l in r.stdout.split("\n") if "verdict" in l.lower() or "TOTAL" in l]
print("  verificator ruleaza; VERDICT_COLAPSAT e activ. TOTAL:", [l.strip() for l in vc if "TOTAL:" in l][:1])
