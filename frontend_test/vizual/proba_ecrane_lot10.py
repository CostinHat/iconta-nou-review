# -*- coding: utf-8 -*-
"""PROBA LOT 10 — pe ECRAN: cand formularul primeste date gresite, VORBESTE ecranul?

`interactiune_scan.py` (19.08.2026) parcurge deja toate ecranele, umple casetele si apasa
butoanele — dar **sare deliberat butoanele destructive**, adica exact pe cele care declanseaza
refuzuri. Proba asta e complementara: umple formularul cu date IMPOSIBILE si apasa chiar butonul
sarit, apoi intreaba daca omul vede ceva.

CE APASA, si de ce nu tot:
  * **DA** — `salveaz`, `adaug`, `genereaz`: iau continutul formularului, deci un formular invalid
    e chiar intrebarea lor.
  * **NU** — `sterg`: nu depinde de formular (sterge ce e selectat); `import`: cere un fisier;
    `depun`/`trimit`: **ies din aplicatie** catre SPV/email — un refuz care nu cade ar trimite
    ceva real.

CUM SE MASOARA „a vorbit" — pe TEXT NOU VIZIBIL, nu pe o lista de clase. Prima varianta a probei
cauta `.msg-eroare`, `[role=alert]` si celelalte nume din conventie, si a raportat „TACE" despre
`plan_conturi`, care de fapt raspunde perfect — doar ca `migrare.js` isi scrie eroarea intr-un
`<div class="mig-eroare">`, o clasa proprie. *Un instrument care cauta conventia nu vede ecranele
care n-o urmeaza, si le acuza de tacere.* Acum se compara `innerText`-ul vizibil al paginii,
inainte si dupa apasare.

CELE TREI RASPUNSURI, nu doua. Prima varianta stia doar „a vorbit / tace", si a numit „TACE" doua
butoane care de fapt **au reusit**: au scris in baza un centru de cost si un raport salvat, amandoua
cu numele `«»@#$%`. *O sonda „de citire" scrie pana n-o dovedesti.* Acum starea schemei se numara
INAINTE si DUPA fiecare apasare, iar raspunsurile sunt trei: **a vorbit** · **a scris** (a fost
acceptat) · **TACE** (n-a scris si n-a spus nimic — singurul care e defect).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAD = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_RAD, "frontend_test"))
sys.path.insert(0, _HERE)
sys.path.insert(0, _RAD)

from playwright.sync_api import sync_playwright  # noqa: E402
from w_auth import INIT  # noqa: E402
from nav_ecrane import ECRANE  # noqa: E402

PROBATE = ("salveaz", "salvez", "salvare", "adaug", "genereaz")
OPRITE = ("sterg", "șterg", "import", "depun", "trimit")

INVALID_TEXT = "«»@#$%"
INVALID_NUMAR = "-99999999"
INVALID_DATA = "1899-02-30"

SCHEMA = os.environ.get("PROBA_SCHEMA", "tenant_003")

JS_TEXT = "() => (document.body.innerText || '').replace(/\\s+/g, ' ').trim()"

JS_UMPLE = """
(v) => {
  let n = 0;
  for (const e of document.querySelectorAll(".fereastra input, .fereastra textarea")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.readOnly || e.disabled) continue;
    const t = (e.getAttribute("type") || "text").toLowerCase();
    if (t === "checkbox" || t === "radio" || t === "file" || t === "hidden") continue;
    if (t === "number") e.value = v.numar;
    else if (t === "date") e.value = v.data;
    else e.value = v.text;
    e.dispatchEvent(new Event("input", { bubbles: true }));
    e.dispatchEvent(new Event("change", { bubbles: true }));
    n++;
  }
  return n;
}
"""

JS_BUTOANE = """
(g) => {
  const out = [];
  document.querySelectorAll(".fereastra button, .fereastra .buton-primar").forEach((b, i) => {
    const r = b.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || b.disabled) return;
    const t = (b.textContent || "").toLowerCase();
    if (g.oprite.some((x) => t.includes(x))) return;
    if (!g.probate.some((x) => t.includes(x))) return;
    b.setAttribute("data-proba-lot10", String(i));
    out.push({ i, text: (b.textContent || "").trim().slice(0, 40) });
  });
  return out;
}
"""


def _dif(a, b):
    """Prima bucata de text care difera — ca sa se vada CE a aparut, nu doar ca s-a schimbat."""
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return b[max(0, i - 20):i + 180]


def _tabele(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY 1", (SCHEMA,))
        return [r[0] for r in cur.fetchall()]


def stare(conn, tabele):
    """count(*) pe FIECARE tabel al schemei. Nu o lista aleasa de mine: o sonda care numara
    doar tabelele la care s-a gandit e oarba exact acolo unde nu s-a gandit."""
    out = {}
    with conn.cursor() as cur:
        for t in tabele:
            try:
                cur.execute('SELECT count(*) FROM "%s"."%s"' % (SCHEMA, t))
                out[t] = cur.fetchone()[0]
            except Exception:  # noqa: BLE001
                conn.rollback()
    conn.rollback()
    return out


from core import db  # noqa: E402

db.init_pool()
conn = db.get_conn().__enter__()
TABELE = _tabele(conn)
print("tabele in %s: %d" % (SCHEMA, len(TABELE)))
stare0 = stare(conn, TABELE)

rez = {}
scrieri = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1100})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    for nume, deschide in ECRANE:
        try:
            deschide(pg)
        except Exception as ex:  # noqa: BLE001
            rez[nume] = {"eroare_navigare": str(ex)[:120]}
            print("%-24s NAVIGARE ESUATA: %s" % (nume, str(ex)[:70]))
            continue
        pg.wait_for_timeout(500)
        umplute = pg.evaluate(JS_UMPLE, {"text": INVALID_TEXT, "numar": INVALID_NUMAR,
                                         "data": INVALID_DATA})
        butoane = pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE)})
        ecran = {"campuri_umplute": umplute, "butoane": []}
        for bt in butoane:
            t0 = pg.evaluate(JS_TEXT)
            s0 = stare(conn, TABELE)
            try:
                pg.click('[data-proba-lot10="%d"]' % bt["i"], timeout=4000)
            except Exception as ex:  # noqa: BLE001
                ecran["butoane"].append({"buton": bt["text"], "click": "esuat: %s" % str(ex)[:60]})
                continue
            pg.wait_for_timeout(1800)
            t1 = pg.evaluate(JS_TEXT)
            s1 = stare(conn, TABELE)
            schimbat = {k: (s0.get(k), s1.get(k)) for k in s1 if s0.get(k) != s1.get(k)}
            if schimbat:
                scrieri.append((nume, bt["text"], schimbat))
            ecran["butoane"].append({
                "buton": bt["text"],
                "text_nou": (t1 != t0),
                "delta_text": (t1[len(t0):] if t1.startswith(t0) else "")[:200] or _dif(t0, t1),
                "a_scris": schimbat or None,
                "verdict": ("a vorbit" if t1 != t0 else ("a scris" if schimbat else "TACE")),
            })
            try:
                deschide(pg)
                pg.wait_for_timeout(300)
                pg.evaluate(JS_UMPLE, {"text": INVALID_TEXT, "numar": INVALID_NUMAR,
                                       "data": INVALID_DATA})
                pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE)})
            except Exception:  # noqa: BLE001
                break
        rez[nume] = ecran
        print("%-24s campuri=%-3s  %s" % (
            nume, ecran["campuri_umplute"],
            "  ".join("[%s → %s]" % (x.get("buton", "?")[:22], x.get("verdict", x.get("click", "?")))
                      for x in ecran["butoane"])))

stare1 = stare(conn, TABELE)
sch = {k: (stare0.get(k), stare1.get(k)) for k in stare1 if stare0.get(k) != stare1.get(k)}
print()
print("SCHIMBARI DE STARE, cap la cap:", sch or "niciuna")
for s in scrieri:
    print("   a scris:", s)
print("erori JS:", erori[:3] or "niciuna")

with open(os.path.join(_HERE, "proba_ecrane_lot10.json"), "w", encoding="utf-8") as f:
    json.dump({"schema": SCHEMA, "schimbari": sch, "scrieri": scrieri, "ecrane": rez,
               "erori_js": erori[:10]}, f, ensure_ascii=False, indent=1)

tot = [x for e in rez.values() for x in e.get("butoane", []) if "verdict" in x]
print()
print("TOTAL butoane probate: %d · au vorbit: %d · au scris: %d · TAC: %d"
      % (len(tot), sum(1 for x in tot if x["verdict"] == "a vorbit"),
         sum(1 for x in tot if x["verdict"] == "a scris"),
         sum(1 for x in tot if x["verdict"] == "TACE")))
