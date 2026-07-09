# verificator_sageti.py — unealta de audit: cine e deschis in fereastra si nu gestioneaza sageata
# Ruleaza pe server: /opt/iconta/venv/bin/python3 verificator_sageti.py
# Verifica TOATE ecranele din static/js/ecrane. Face parte din trusa de audit
# (alaturi de grep alert/confirm). Zero modificari — doar raport.
import re, os

BAZA = os.path.expanduser("~/iconta_nou/static/js/ecrane")
fisiere = {}
for f in sorted(os.listdir(BAZA)):
    if f.endswith(".js") and ".bak" not in f:
        with open(os.path.join(BAZA, f), encoding="utf-8") as h:
            fisiere[f] = h.read()

tot = "\n".join(fisiere.values())
# ecranele deschise in fereastra (nav.deschide) — ele au sageata de gestionat
deschise = set(re.findall(r'nav\.deschide\([^,]+,\s*\(?(?:corp|c2|c)\)?\s*=>\s*(\w+)\(', tot))
deschise |= set(re.findall(r'nav\.deschide\([^,]+,\s*(\w+)\s*\)', tot))

rezultat = []
for fn in sorted(deschise):
    loc = None
    for nume, t in fisiere.items():
        m = re.search(r'(?:export )?(?:async )?function ' + re.escape(fn) + r'\s*\([^)]*\)\s*\{', t)
        if not m:
            continue
        loc = nume
        start = m.end()
        urm = re.search(r'\n(?:export )?(?:async )?function \w+\s*\(', t[start:])
        corp = t[start:start + urm.start()] if urm else t[start:]
        in_corp = "setInapoi" in corp
        in_fisier = "setInapoi" in t
        rezultat.append((fn, nume, in_corp, in_fisier))
        break
    if loc is None:
        rezultat.append((fn, "NEGASIT", None, None))

neconforme = 0
print("%-28s %-24s %s" % ("ECRAN (in fereastra)", "FISIER", "verdict sageata"))
print("-" * 90)
for fn, f, in_corp, in_fis in rezultat:
    if in_corp is None:
        v = "functia negasita — verifica manual"
    elif in_corp:
        v = "OK — seteaza inapoiul"
    elif in_fis:
        v = "probabil OK — inapoiul e in acelasi fisier (copii); confirmare vizuala"
    else:
        v = "*** NECONFORM — nimeni nu seteaza inapoiul (sageata inchide fereastra) ***"
        neconforme += 1
    print("%-28s %-24s %s" % (fn, f, v))
print("-" * 90)
print("NECONFORME certe:", neconforme)
