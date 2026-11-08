# -*- coding: utf-8 -*-
"""scripts/praguri_automate.py — pragurile unui lot, calculate din .lot_jurnal.log (lotul 17.5-A, cerința A). Citește jurnalul fără să scrie în el (nu cheamă `marcheaza_intrerupte`).

  ./venv/bin/python scripts/praguri_automate.py <lot> <produs|unelte> [--inainte-de <lot>] [--loturi <lot>...] [--faze <fază>...] [--jurnal <cale>]
                                                [--iesire <cale>] [--adauga <fișier>] [--suprascrie]

Pragul unei faze = maximul duratelor rulărilor complete (pereche început/sfârșit fără «intrerupt») din ultimele N_LOTURI loturi publicate × 1,2, rotunjit în sus la secundă
întreagă, în aritmetică întreagă. Fișierul: ~/ghid_incoming/praguri_<lot_fisier(lot)>.txt (`--iesire`: alt fișier sau un director); dacă există, refuz cu 1 (fără `--suprascrie`)."""
import datetime
import os
import sys

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import jurnal_lot as JL  # noqa: E402
import poarta_lib as L  # noqa: E402

N_LOTURI = 3
#: factorul 1,2 ca raport întreg 12/10 (rotunjirea în sus fără virgulă mobilă)
FACTOR_NUM, FACTOR_DEN = 12, 10
FAZE_IMPLICITE = ("hook", "poarta_verificator", "poarta_pytest", "poarta_plasa")
FRAZA_UNELTE = ("fara praguri numerice pe durate in aceasta schema (lot de unelte; niciun rand `max <faza> <secunde>`: scripts/publica_lot.py compara numai randurile `max`); "
                "referintele de mai jos sunt cerinte de raport, cu cifra si cu sursa ei")
LIMITE = "limite aplicate de scripts/poarta_rulare.py (:116, :146): cel mult 2 rulari complete si 2 reluari; nu se scriu aici."


def prag(maxim):
    """Maximul × 1,2 rotunjit în sus: 92 -> 111, 84 -> 101, 602 -> 723, 100 -> 120."""
    return -((-maxim * FACTOR_NUM) // FACTOR_DEN)


def loturi_publicate(rows):
    """-> [(lot, momentul publicării)] în ordinea momentului: «publicare», «sfarsit», «publicat»; momentul = ora ultimului astfel de rând."""
    momente = {}
    for r in rows:
        if len(r) > 5 and r[1] == "publicare" and r[2] == "sfarsit" and r[5] == "publicat":
            if r[0] not in momente or JL._t(r[3]) >= JL._t(momente[r[0]]):
                momente[r[0]] = r[3]
    return sorted(momente.items(), key=lambda x: JL._t(x[1]))


def selecteaza(rows, inainte_de=None, loturi=None):
    """Loturile din care se calculează pragurile: lista dată, sau ultimele N_LOTURI publicate (cu `inainte_de`: numai cele publicate înaintea primului rând al lotului dat)."""
    if loturi:
        return list(loturi)
    pub = loturi_publicate(rows)
    if inainte_de:
        prim = next((r[3] for r in rows if len(r) > 5 and r[0] == inainte_de), None)
        if prim:
            pub = [(l, m) for l, m in pub if l != inainte_de and JL._t(m) < JL._t(prim)]
    return [l for l, _ in pub[-N_LOTURI:]]


def calculeaza(rows, loturi, faze):
    """-> {faza: {maxim, lot, id, complete, intrerupte}}; `maxim` e None când faza nu are nicio rulare completă; la egalitate de maxim între loturi rămâne cel mai recent din selecție."""
    iesire = {}
    for faza in faze:
        info = {"maxim": None, "lot": None, "id": None, "complete": 0, "intrerupte": 0}
        for lot in loturi:
            for x in JL.rulari(rows, lot):
                if x["faza"] != faza:
                    continue
                if x["intrerupt"]:
                    info["intrerupte"] += 1
                elif x["complet"]:
                    info["complete"] += 1
                    if info["maxim"] is None or x["secunde"] >= info["maxim"]:
                        info["maxim"], info["lot"], info["id"] = x["secunde"], lot, x["id"]
        iesire[faza] = info
    return iesire


def tabel(calc):
    linii = ["%-20s %7s %-10s %9s %12s %7s" % ("faza", "maxim", "lot", "complete", "intrerupte", "prag")]
    for faza, i in calc.items():
        linii.append("%-20s %7s %-10s %9d %12d %7s" % (faza, i["maxim"] if i["maxim"] is not None else "-", i.get("lot") or "-", i["complete"], i["intrerupte"],
                                                       prag(i["maxim"]) if i["maxim"] is not None else "-"))
    return "\n".join(linii)


def text_fisier(lot, tip, calc, loturi, adauga, acum):
    """Conținutul fișierului de praguri, în schema pragurilor de azi (prima linie «produs»/«unelte»)."""
    sursa = ["sursa pragurilor %s: generate de scripts/praguri_automate.py la %s din .lot_jurnal.log; loturi folosite: %s (%d)" % (lot, acum, ", ".join(loturi) or "-", len(loturi))]
    for faza, i in calc.items():
        sursa.append("  %s: maxim %d s (lotul %s, rularea %s) din %d rulari complete, %d rulari «intrerupt» ignorate, prag %d s" %
                     (faza, i["maxim"], i["lot"], i["id"], i["complete"], i["intrerupte"], prag(i["maxim"])))
    linii = [tip, "lot: %s" % lot]
    if tip == "produs":
        linii += ["max %s %d" % (faza, prag(i["maxim"])) for faza, i in calc.items()]
    else:
        linii.append(FRAZA_UNELTE)
        linii += ["  %s ≤ %d s (= %d × 1,2; sursa: lotul %s, rularea %s, %d rulari complete)" % (faza, prag(i["maxim"]), i["maxim"], i["lot"], i["id"], i["complete"])
                  for faza, i in calc.items()]
    linii.append("runde_verificator_max: %d" % (2 if tip == "produs" else 0))
    linii += ["\n".join(sursa), LIMITE]
    text = "\n".join(linii) + "\n"
    if adauga:
        text += open(adauga, encoding="utf-8").read()
        if not text.endswith("\n"):
            text += "\n"
    return text


def _optiuni(a):
    """-> (pozitionale, {optiune: valori}); valorile unei opțiuni merg până la următoarea opțiune."""
    poz, opt, cur = [], {}, None
    for x in a:
        if x.startswith("--"):
            cur = x
            opt[cur] = []
        elif cur:
            opt[cur].append(x)
        else:
            poz.append(x)
    return poz, opt


def main(a):
    poz, opt = _optiuni(a)
    if len(poz) != 2 or poz[1] not in ("produs", "unelte"):
        print(__doc__)
        return 2
    lot, tip = poz
    rows = JL.citeste_jurnal(opt["--jurnal"][0] if opt.get("--jurnal") else None)
    loturi = selecteaza(rows, opt["--inainte-de"][0] if opt.get("--inainte-de") else None, opt.get("--loturi"))
    faze = tuple(opt["--faze"]) if opt.get("--faze") else FAZE_IMPLICITE
    calc = calculeaza(rows, loturi, faze)
    print("loturi folosite: %s (%d)" % (", ".join(loturi) or "-", len(loturi)))
    print(tabel(calc))
    lipsa = [f for f, i in calc.items() if i["maxim"] is None]
    for f in lipsa:
        print("lipsesc date pentru %s" % f)
    if lipsa:
        return 1
    nume = "praguri_%s.txt" % L.lot_fisier(lot)
    iesire = opt["--iesire"][0] if opt.get("--iesire") else os.path.expanduser("~/ghid_incoming")
    fisier = iesire if iesire.endswith(".txt") and not os.path.isdir(iesire) else os.path.join(iesire, nume)
    if os.path.exists(fisier) and "--suprascrie" not in opt:
        print("REFUZ: %s există deja (--suprascrie îl rescrie)" % fisier)
        return 1
    adauga = opt["--adauga"][0] if opt.get("--adauga") else None
    acum = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(fisier) or ".", exist_ok=True)
    open(fisier, "w", encoding="utf-8").write(text_fisier(lot, tip, calc, loturi, adauga, acum))
    print("scris %s" % fisier)
    if tip == "produs" and not adauga:
        print("AVERTISMENT: lipsește fisiere_permise (scripts/publica_lot.py o cere la un lot «produs»; --adauga <fișier>)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
