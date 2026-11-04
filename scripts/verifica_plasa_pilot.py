# -*- coding: utf-8 -*-
"""scripts/verifica_plasa_pilot.py — pasul din poartă care REFUZĂ (comanda 15.1-E7, pct.5): fiecare poziție pilot marcată „ok” în scenarii_pilot.txt are în plasa e2e a publicării
(harta porții + plasa fixă pilot) cel puțin un fișier de test care citează ID-ul poziției ȘI cifrele (sumele în format românesc, cu virgulă) din scenariul ei. Lipsa pică poarta.
Scris în lotul 15.1-E7; nu se modifică de comenzile de reparații. Ieșire 0 = toate pozițiile „ok” au test; 1 = cel puțin una nu are."""
import glob
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)
SCENARII = os.path.join(RAD, "docs", "scenarii_pilot.txt")   # copia din repo (16.0 pct.4), nu fișierul din afara git-ului
_SUMA = re.compile(r"(?<![\d.,])\d{1,3}(?:\.\d{3})*,\d{2}(?![\d,])")


def pozitii_ok(text):
    """ID-urile din fraza „Poziții „ok” la <data> (cu test obligatoriu în hartă): X02, F012, …” a antetului."""
    m = re.search(r"Poziții „ok” la [^:]*:\s*([^.]*)\.", text)
    return [x.strip() for x in m.group(1).split(",")] if m else []


def scenariu(text, id_):
    for ln in text.splitlines():
        if ln.startswith(id_ + " ·") or ln.startswith(id_ + " "):
            return ln
    return ""


def plasa_publicarii():
    from core.test_deficiente import plasa_publicarii as p
    return sorted(os.path.join(RAD, "frontend_test", "e2e", f) for f in p())


def restante():
    """{ID: motiv} din scripts/plasa_pilot_restante.txt — restanța vizibilă găsită la prima rulare (15.1-E7)."""
    out = {}
    for ln in io.open(os.path.join(RAD, "scripts", "plasa_pilot_restante.txt"), encoding="utf-8"):
        if ln.strip() and not ln.startswith("#") and " · " in ln:
            k, v = ln.split(" · ", 1)
            out[k.strip()] = v.strip()
    return out


def verifica(text, fisiere, restant=None):
    """[(id, motiv)] — pozițiile „ok” fără test care citează ID-ul și cifrele (în afara restanței vizibile); o poziție din restanță care are acum testul complet pică (se scoate din listă)."""
    restant = restante() if restant is None else restant
    continut = {f: io.open(f, encoding="utf-8").read() for f in fisiere if os.path.isfile(f)}
    rele = []
    ok = pozitii_ok(text)
    if not ok:
        return [("-", "antetul scenariilor nu numește pozițiile „ok” (frază „Poziții „ok” la …: …”)")]
    for id_ in ok:
        ln = scenariu(text, id_)
        cifre = sorted(set(_SUMA.findall(ln)))
        cu_id = [f for f, t in continut.items() if re.search(r"\b%s\b" % re.escape(id_), t)]
        motiv = None
        if not cu_id:
            motiv = "niciun test din plasa de publicare nu citează ID-ul"
        elif not any(all(c in continut[f] for c in cifre) for f in cu_id):
            lipsa = sorted({c for c in cifre if not any(c in continut[f] for f in cu_id)})
            motiv = "testele care citează ID-ul (%s) nu conțin cifrele din scenariu: %s" % (", ".join(os.path.basename(f) for f in cu_id), ", ".join(lipsa[:6]))
        if motiv and id_ not in restant:
            rele.append((id_, motiv))
        if not motiv and id_ in restant:
            rele.append((id_, "are acum testul complet: scoate-o din scripts/plasa_pilot_restante.txt"))
    for id_ in restant:
        if id_ not in ok:
            rele.append((id_, "e în scripts/plasa_pilot_restante.txt, dar nu mai e marcată „ok” în scenarii_pilot.txt: scoate-o din listă"))
    return rele


if __name__ == "__main__":
    if not os.path.isfile(SCENARII):
        print("[plasa pilot] REFUZ: lipsește %s" % SCENARII)
        sys.exit(1)
    text = io.open(SCENARII, encoding="utf-8").read()
    rele = verifica(text, plasa_publicarii())
    for id_, m in rele:
        print("[plasa pilot] ROSU %s: %s" % (id_, m))
    print("[plasa pilot] %s: %d poziții „ok”, %d fără test cu ID și cifre" % ("ROSU" if rele else "VERDE", len(pozitii_ok(text)), len(rele)))
    sys.exit(1 if rele else 0)
