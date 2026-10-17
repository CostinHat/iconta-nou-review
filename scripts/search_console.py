# -*- coding: utf-8 -*-
"""scripts/search_console.py — exporturile Search Console, clasificate (lotul 7 pct.2.7, comanda Costin 17.10.2026, verbatim în DECIZII
„Lotul 6 închis”): „cele 17 pagini 404 [...] — redirecționare spre pagina corectă sau 410; verifică și cele 98 de pagini accesate, dar
neindexate, legat de măsurarea ghidurilor suprapuse.”

De ce o unealtă: lista din Search Console nu se vede de pe server (jurnalele nginx țin 14 zile; pe 03.10–17.10, Googlebot-ul real —
66.249.* — a cerut 2.662 de adrese distincte, iar azi toate răspund 200 sau 301; niciun 404 pe iconta.eu). Exportul (CSV, cu coloana
URL) îl descarcă Costin; unealta spune, pentru fiecare adresă, ce răspunde ACUM și ce propune.

  python scripts/search_console.py 404 <export.csv>          -> starea de acum + propunerea: 301 spre ghidul cel mai apropiat / 410
  python scripts/search_console.py neindexate <export.csv>   -> pentru fiecare ghid: publicat? în ce grup de suprapunere? cât text?

Cererile merg la aplicația locală (`http://127.0.0.1:8010`, antetul `Host: iconta.eu`), numai GET, fără redirecționări urmate.
"""
import csv
import difflib
import io
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
APLICATIA = os.environ.get("ICONTA_LOCAL", "http://127.0.0.1:8010")
PRAG_ASEMANARE = 0.6


class _FaraRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def stare(cale):
    """(cod HTTP, Location) pentru `cale`, fără a urma redirecționarea."""
    op = urllib.request.build_opener(_FaraRedirect)
    try:
        r = op.open(urllib.request.Request(APLICATIA + cale, headers={"Host": "iconta.eu"}), timeout=30)
        return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


def adrese(csv_cale):
    """Căile din export (prima coloană care arată ca un URL)."""
    out = []
    with io.open(csv_cale, encoding="utf-8-sig") as f:
        for rand in csv.reader(f):
            for celula in rand:
                if celula.startswith("http"):
                    u = urllib.parse.urlsplit(celula.strip())
                    out.append(u.path + (("?" + u.query) if u.query else ""))
                    break
    return out


def publicate():
    return {s.strip() for s in io.open(os.path.join(RAD, "ghid_publicate.txt"), encoding="utf-8") if s.strip()}


def propune(cale, cod, publ):
    """PURĂ. Ce se face cu o adresă raportată 404: nimic (răspunde altfel acum) / 301 spre ghidul cel mai apropiat / 410."""
    if cod != 404:
        return "nimic: răspunde %d acum" % cod
    m = re.fullmatch(r"/ghid/([\w-]+)", cale.split("?")[0])
    if m:
        cand = difflib.get_close_matches(m.group(1), sorted(publ), n=1, cutoff=PRAG_ASEMANARE)
        if cand:
            return "301 -> /ghid/%s (asemănare %.2f)" % (cand[0], difflib.SequenceMatcher(None, m.group(1), cand[0]).ratio())
    return "410: n-a existat ca pagină sau n-are succesor"


def raport_404(csv_cale):
    publ = publicate()
    for cale in adrese(csv_cale):
        cod, loc = stare(cale)
        print("%-70s %d%s  %s" % (cale[:70], cod, (" -> " + loc) if loc else "", propune(cale, cod, publ)))


def raport_neindexate(csv_cale):
    import scan_ghid_suprapuneri as sg
    publ = publicate()
    lista = sg.ghiduri()
    grup_al = {}
    for i, g in enumerate(sg.grupuri(lista), 1):
        for slug, _titlu in g:
            grup_al[slug] = i
    cuvinte = {}
    for slug in publ:
        try:
            cuvinte[slug] = len(io.open(os.path.join(RAD, "ghid", slug + ".md"), encoding="utf-8").read().split())
        except OSError:
            pass
    n = in_grup = scurte = 0
    for cale in adrese(csv_cale):
        m = re.fullmatch(r"/ghid/([\w-]+)", cale)
        if not m:
            print("%-70s (nu e un ghid)" % cale[:70])
            continue
        slug = m.group(1)
        n += 1
        g = grup_al.get(slug)
        in_grup += bool(g)
        scurte += cuvinte.get(slug, 0) < 400
        print("%-70s publicat=%s grup=%s cuvinte=%s" % (cale[:70], slug in publ, g or "-", cuvinte.get(slug, "?")))
    print("\n%d ghiduri; în grupuri de suprapunere: %d; sub 400 de cuvinte: %d" % (n, in_grup, scurte))


def main(argv):
    if len(argv) != 2 or argv[0] not in ("404", "neindexate"):
        print(__doc__)
        return 2
    (raport_404 if argv[0] == "404" else raport_neindexate)(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
