# -*- coding: utf-8 -*-
"""Comparația 5(c) și 5(d) (17.5-A): cifrele arhitectului față de cele ale raportului de timp (docs/dovezi/17_5_A/timp/) și de controlul independent (control_independent.sh)."""
import os, re, subprocess, sys
AICI = os.path.dirname(os.path.abspath(__file__))
J = sys.argv[1]
ARH = {"17.1": {"timp_total": 602, "pytest": (154, 41), "poarta_plasa": (34, 2), "poarta_pytest": (19, 2), "hook": (12, 8)},
       "17.2": {"timp_total": 303, "pytest": (87, 40), "poarta_plasa": (38, 2)}}
def raport(lot):
    t = open(os.path.join(AICI, "timp", "lot_%s_timp.md" % lot.replace(".", "_").replace("-", "_")), encoding="utf-8").read()
    r = {"timp_total": float(re.search(r"timp total .*?: ([\d.]+) min", t).group(1))}
    m = re.search(r"pytest, toate sesiunile: (\d+) sesiuni, ([\d.]+) min", t)
    r["pytest"] = (float(m.group(2)), int(m.group(1)))
    for f in ("hook", "poarta_pytest", "poarta_plasa"):
        m = re.search(r"^\| %s \| (\d+) \| (\d+) \| (\d+) \| ([\d.]+) \|" % f, t, re.M)
        r[f] = (float(m.group(4)), int(m.group(1)), int(m.group(2))) if m else None
    return r
def control(lot):
    o = subprocess.run(["sh", os.path.join(AICI, "control_independent.sh"), J, "timp", lot], capture_output=True, text=True).stdout
    r = {"timp_total": float(re.search(r"timp_total_min=([\d.]+)", o).group(1))}
    m = re.search(r"pytest_toate=(\d+) min=([\d.]+)", o)
    r["pytest"] = (float(m.group(2)), int(m.group(1)))
    for f in ("hook", "poarta_pytest", "poarta_plasa"):
        m = re.search(r"^%s complete=(\d+) min=([\d.]+) intrerupte=(\d+)" % f, o, re.M)
        r[f] = (float(m.group(2)), int(m.group(1)), int(m.group(3)))
    return r
linii = ["%-8s %-22s %-14s %-14s %-14s %-9s %s" % ("lot", "măsură", "arhitect", "script", "control", "dif.min", "verdict")]
abateri = 0
for lot in ("17.1", "17.2", "17.2-A", "17.2-B", "17.3"):
    r, c = raport(lot), control(lot)
    arh = ARH.get(lot, {})
    for m in ("timp_total", "pytest", "hook", "poarta_pytest", "poarta_plasa"):
        if m == "timp_total":
            a_, s_, c_ = arh.get(m), r[m], c[m]
            dif = None if a_ is None else s_ - a_
            fmt = lambda v: "—" if v is None else "%.1f min" % v
            ok = (dif is None or abs(dif) <= 1) and abs(s_ - c_) < 0.05
            linii.append("%-8s %-22s %-14s %-14s %-14s %-9s %s" % (lot, m, fmt(a_), fmt(s_), fmt(c_), "—" if dif is None else "%+.1f" % dif, "ok" if ok else "ABATERE"))
        else:
            a_ = arh.get(m)
            s_, c_ = r[m], c[m]
            n_s, n_c = s_[1], c_[1] if m != "pytest" else c_[1]
            fm = lambda v: "—" if v is None else "%d min × %d" % (v[0], v[1])
            fs = lambda v: "%.1f min × %d" % (v[0], v[1])
            dif = None if a_ is None else s_[0] - a_[0]
            ok = (a_ is None or (abs(dif) <= 1 and a_[1] == s_[1])) and abs(s_[0] - c_[0]) < 0.05 and s_[1] == c_[1]
            linii.append("%-8s %-22s %-14s %-14s %-14s %-9s %s" % (lot, m, fm(a_), fs(s_), fs(c_), "—" if dif is None else "%+.1f" % dif, "ok" if ok else "ABATERE"))
    abateri += sum(1 for l in linii[-5:] if l.endswith("ABATERE"))
print("\n".join(linii))
print("\nabateri peste toleranță: %d" % abateri)
