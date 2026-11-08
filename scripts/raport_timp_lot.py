# -*- coding: utf-8 -*-
"""scripts/raport_timp_lot.py — raportul de timp al unui lot, calculat mecanic din .lot_jurnal.log (lotul 17.5-A, cerința C). Citește jurnalul fără să scrie în el.

  ./venv/bin/python scripts/raport_timp_lot.py <lot> [--jurnal <cale>] [--arhitect <fișier>] [--iesire <cale>]

Scrie ~/lot_<lot_fisier(lot)>_timp.md (`--iesire`: alt fișier sau director) și tipărește același text. Secțiuni: (a) tabelul fazelor, (b) totaluri, (c) timpul de lucru al lui Code, (d) timpul arhitectului."""
import datetime
import os
import sys

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import jurnal_lot as JL  # noqa: E402
import poarta_lib as L  # noqa: E402

_ARHITECT = os.path.expanduser("~/ghid_incoming/jurnal_arhitect.tsv")


def _min(sec):
    return "%.1f" % (sec / 60.0)


def uniune(intervale):
    """Lungimea (secunde) reuniunii unor intervale (datetime, datetime)."""
    total, cur_a, cur_b = 0.0, None, None
    for a, b in sorted(intervale):
        if cur_b is None or a > cur_b:
            if cur_b is not None:
                total += (cur_b - cur_a).total_seconds()
            cur_a, cur_b = a, b
        elif b > cur_b:
            cur_b = b
    if cur_b is not None:
        total += (cur_b - cur_a).total_seconds()
    return total


def _rulari_cu_derivate(rows, lot):
    """Rulările lotului; dacă jurnalul nu are rândurile fazelor de lucru, le derivă (funcția pură, fără scrieri) -> (rulări, derivat_acum)."""
    rl = JL.rulari(rows, lot)
    if any(x["faza"] in JL.FAZE_LUCRU for x in rl):
        return rl, False
    for k, x in enumerate(JL.deriva_lucru(rows, lot)):
        rl.append({"faza": x["faza"], "id": "calculat-%d" % k, "inceput": x["inceput"], "sfarsit": x["sfarsit"], "rezultat": x["rezultat"], "secunde": JL._sec(x["inceput"], x["sfarsit"]),
                   "complet": True, "intrerupt": False, "pid": "", "detalii": x["detalii"]})
    return rl, True


def tabel_faze(rl):
    ordine = []
    for x in rl:
        if x["faza"] not in ordine:
            ordine.append(x["faza"])
    linii = ["| fază | rulări complete | rulări «intrerupt» | rulări roșii | minute | maxim (s) |", "|---|---|---|---|---|---|"]
    for f in ordine:
        r = [x for x in rl if x["faza"] == f]
        c = [x for x in r if x["complet"]]
        linii.append("| %s | %d | %d | %d | %s | %s |" % (f, len(c), sum(1 for x in r if x["intrerupt"]), sum(1 for x in c if x["rezultat"].startswith("rosu")),
                                                        _min(sum(x["secunde"] for x in c)), max((x["secunde"] for x in c), default="-")))
    return linii


def totaluri(rows, lot, rl):
    rand = [r for r in rows if len(r) > 6 and r[0] == lot]
    ore = [JL._t(r[3]) for r in rand]
    linii = []
    total = (max(ore) - min(ore)).total_seconds()
    linii.append("- timp total (primul → ultimul rând al lotului): %s min" % _min(total))
    runde = JL.runde_poarta(rows, lot)
    pornire = next((r for r in rand if r[1] == "pornire" and r[2] == "inceput"), None)
    ultim = runde[-1]["sfarsit"] if runde else None
    if pornire and ultim:
        pub, n = JL._publicare_dupa(rows, lot, ultim)
        if pub:
            linii.append("- pornire → publicare: %s min%s" % (_min(JL._sec(pornire[3], pub[3])), " (%d rânduri «inceput» ale fazei «publicare»)" % n if n > 1 else ""))
        else:
            linii.append("- pornire → publicare: lipsă (nu există rând «inceput» al fazei «publicare» după ultimul verdict)")
    else:
        linii.append("- pornire → publicare: lipsă (%s)" % ("fără rând «pornire»" if not pornire else "fără rulare de poartă"))
    ses = JL.sesiuni_pytest(rows, lot)
    # sesiunile fără sfârșit (proces mort) nu intră în minute și se numără separat
    cu_durata = [s for s in ses if s["secunde"] is not None]
    fara = [s for s in ses if s["secunde"] is None]
    intr = [s for s in cu_durata if s["intrerupt"]]
    linii.append("- pytest, toate sesiunile: %d sesiuni, %s min (include sesiunile «intrerupt»; numără de două ori sesiunile din poartă)" % (len(cu_durata), _min(sum(s["secunde"] for s in cu_durata))))
    linii.append("  - din care întrerupte: %d, %s min" % (len(intr), _min(sum(s["secunde"] for s in intr))))
    linii.append("  - început fără sfârșit (ignorate în minute): %d" % len(fara))
    interv = lambda l: [(JL._t(s["inceput"]), JL._t(s["sfarsit"])) for s in l if s["sfarsit"]]  # noqa: E731
    poarta = [(JL._t(x["inceput"]), JL._t(x["sfarsit"])) for x in rl if x["faza"] in JL._FAZE_POARTA and x["sfarsit"]]
    code = [s for s in cu_durata if not s["colectare"] and not s["in_faza"]]
    u_poarta = uniune(poarta)
    u_code = uniune(interv(code))
    u_ambele = uniune(poarta + interv(code))
    linii.append("- fără dublă numărătoare (reuniune de intervale): poartă %s min; pytest Code %s min; restul %s min (= timp total − reuniunea poartă ∪ pytest Code)" %
                 (_min(u_poarta), _min(u_code), _min(total - u_ambele)))
    in_hook = [s for s in ses if any(JL._t(a) <= JL._t(s["inceput"]) <= JL._t(b) for a, b in
                                                                     [(x["inceput"], x["sfarsit"] or x["inceput"]) for x in rl if x["faza"] == "hook"])]
    in_poarta = [s for s in ses if any(JL._t(a) <= JL._t(s["inceput"]) <= JL._t(b) for a, b in
                                        [(x["inceput"], x["sfarsit"] or x["inceput"]) for x in rl if x["faza"] in JL._FAZE_POARTA])]
    linii.append("- sesiuni pytest: colectări %d; pornite în hook %d; pornite în poartă %d; ale lui Code %d" %
                 (sum(1 for s in ses if s["colectare"]), len(in_hook), len(in_poarta), len([s for s in ses if not s["colectare"] and not s["in_faza"]])))
    return linii


def lucru_code(rl, derivat_acum):
    linii = []
    if derivat_acum:
        linii.append("Lotul nu are în jurnal rândurile fazelor de lucru: derivate acum cu funcția pură (nimic scris în jurnal).")
    linii += ["| fază | număr | minute |", "|---|---|---|"]
    for f in JL.FAZE_LUCRU:
        if f == "pytest_intre_commituri":
            continue
        r = [x for x in rl if x["faza"] == f and x["complet"]]
        linii.append("| %s | %d | %s |" % (f, len(r), _min(sum(x["secunde"] for x in r))))
    d = [x for x in rl if x["faza"] == "pytest_intre_commituri" and x["complet"]]
    linii += ["", "descriptiv, nu se adună (se suprapune cu celelalte faze):", "", "| fază | număr | minute |", "|---|---|---|",
              "| pytest_intre_commituri | %d | %s |" % (len(d), _min(sum(x["secunde"] for x in d)))]
    return linii


def citeste_arhitect(cale):
    """-> [(lot, eveniment, moment, nota)] sau None dacă fișierul lipsește sau are un rând nepărsabil."""
    try:
        linii = [ln.rstrip("\n") for ln in open(cale, encoding="utf-8")]
    except OSError:
        return None
    iesire = []
    for ln in linii:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        c = ln.split("\t")
        try:
            if len(c) < 3:
                raise ValueError
            JL._t(c[2])
        except ValueError:
            return None
        iesire.append((c[0], c[1], c[2], c[3] if len(c) > 3 else ""))
    return iesire


def timp_arhitect(rows, lot, arhitect):
    ev = citeste_arhitect(arhitect)
    if ev is None:
        return ["fără jurnal arhitect"]
    ale = sorted((e for e in ev if e[0] == lot), key=lambda e: JL._t(e[2]))
    linii = []
    if not ale:
        linii.append("fără evenimente ale lotului în jurnalul arhitectului")
    prec = None
    for e in ale:
        linii.append("- %s %s%s%s" % (e[2], e[1], (" — " + e[3]) if e[3] else "", (" (pauză de la precedentul: %s min)" % _min(JL._sec(prec, e[2]))) if prec else ""))
        prec = e[2]
    rand = [r for r in rows if len(r) > 6 and r[0] == lot]
    pregatire = "lipsă"
    if rand:
        prim = JL._t(min(rand, key=lambda r: JL._t(r[3]))[3])
        # lotul publicat imediat înaintea primului rând al lotului
        import praguri_automate as PA
        ant = [l for l, m in PA.loturi_publicate(rows) if l != lot and JL._t(m) < prim]
        coada = next((e for e in ale if e[1] == "coada_scrisa"), None)
        raport = next((e for e in ev if ant and e[0] == ant[-1] and e[1] == "raport_code"), None)
        if coada and raport:
            pregatire = "%s min (coada_scrisa %s − raport_code %s al lotului %s)" % (_min(JL._sec(raport[2], coada[2])), lot, ant[-1], ant[-1])
    linii.append("- pregătire: %s" % pregatire)
    linii.append("- runde externe: %d" % sum(1 for e in ale if e[1] == "verdict_extern"))
    return linii


def raport(lot, jurnal=None, arhitect=None):
    rows = JL.citeste_jurnal(jurnal)
    rl, derivat_acum = _rulari_cu_derivate(rows, lot)
    if not any(r[0] == lot for r in rows if len(r) > 6):
        return None
    text = ["# Raport de timp — lotul %s" % lot, "", "## (a) Fazele lotului", ""] + tabel_faze(rl)
    text += ["", "## (b) Totaluri", ""] + totaluri(rows, lot, rl)
    text += ["", "## (c) Timpul de lucru al lui Code", ""] + lucru_code(rl, derivat_acum)
    text += ["", "## (d) Timpul arhitectului", ""] + timp_arhitect(rows, lot, arhitect or _ARHITECT)
    return "\n".join(text) + "\n"


def cale_implicita(lot):
    return os.path.expanduser("~/lot_%s_timp.md" % L.lot_fisier(lot))


def scrie(lot, jurnal=None, arhitect=None, iesire=None):
    """-> (text, fișier) sau (None, None) dacă lotul nu are rânduri în jurnal."""
    text = raport(lot, jurnal, arhitect)
    if text is None:
        return None, None
    fisier = iesire or cale_implicita(lot)
    if os.path.isdir(fisier):
        fisier = os.path.join(fisier, os.path.basename(cale_implicita(lot)))
    os.makedirs(os.path.dirname(fisier) or ".", exist_ok=True)
    open(fisier, "w", encoding="utf-8").write(text)
    return text, fisier


def main(a):
    poz = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    if len(poz) != 1:
        print(__doc__)
        return 2

    def opt(nume):
        return a[a.index(nume) + 1] if nume in a and a.index(nume) + 1 < len(a) else None
    text, fisier = scrie(poz[0], opt("--jurnal"), opt("--arhitect"), opt("--iesire"))
    if text is None:
        print("REFUZ: lotul %s nu are rânduri în jurnal" % poz[0])
        return 1
    print(text)
    print("scris %s" % fisier)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
