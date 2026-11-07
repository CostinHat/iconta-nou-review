import csv, re, sys
D = sys.argv[1]
rows = list(csv.DictReader(open(D + "/baza_text_taiat.csv", encoding="utf-8")))
rez = open(D + "/rezumat.txt", encoding="utf-8").read().splitlines()
ok = len(rows) == 315
print("rânduri CSV: %d (așteptat 315): %s" % (len(rows), "ok" if ok else "ABATERE"))
gol = [r for r in rows if r["stare"] != "ok" and not r["motiv"]]
print("nedeschis/timeout cu motiv gol: %d: %s" % (len(gol), "ok" if not gol else "ABATERE"))
ok = ok and not gol
for z in ("603x590", "1366x768", "2133x1111"):
    pe = [r for r in rows if r["rezoluție"] == z]
    s = lambda c: sum(int(r[c] or 0) for r in pe)
    asteptat = "%s: deschideri=%d ok=%d nedeschis=%d timeout=%d | tăieturi=%d (lat=%d inalt=%d iesit=%d) | ecrane cu cel puțin o tăietură=%d" % (
        z, len(pe), sum(r["stare"] == "ok" for r in pe), sum(r["stare"] == "nedeschis" for r in pe), sum(r["stare"] == "timeout" for r in pe),
        s("număr"), s("lat"), s("inalt"), s("iesit"), sum(int(r["număr"] or 0) > 0 for r in pe))
    g = asteptat in rez
    print("%s: totalul din rezumat = suma din CSV: %s" % (z, "ok" if g else "ABATERE (%s)" % asteptat))
    ok = ok and g
print("VERIFICARE:", "ok" if ok else "ABATERE")
sys.exit(0 if ok else 1)
