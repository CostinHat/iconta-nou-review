# -*- coding: utf-8 -*-
"""LOTUL 13 — «Operațiuni speciale»: 32 de formulare de notă contabilă, sub UN SINGUR rând de listă.

DE CE E UN LOT ÎNTREG SUB O SINGURĂ UNITATE. `#447 fa-operatiuni` e o linie în
`LISTA_FUNCTIONALITATI.md`, dar ecranul e un MENIU cu 32 de feluri de operațiune, fiecare cu
formularul lui și cu propriul buton «Generează nota (ciornă)». Un „probat" pe rândul acela ar fi
spus, până azi, ceva despre **unul** din 32.

CUM SE NAVIGHEAZĂ, și de ce nu pe index: prima formă a enumerării apăsa pe poziția din DOM
(`data-op="i"`), după o re-navigare — iar pozițiile se re-atribuie, deci clicurile cădeau alături.
Rezultatul arăta ca o descoperire („niciun formular nu se deschide, 0 din 32") și era o **ratare a
instrumentului**: probat cu grijă pe un singur caz, «Leasing» deschide un formular întreg. *A treia
oară în aceeași tură când o măsurătoare proprie s-a dovedit falsă înainte de a fi raportată.* Se
navighează pe NUME (`get_by_role("button", name=..., exact=True)`).

CE APASĂ: numai butonul de generare al formularului deschis. Toate operațiunile intră ca **ciornă**
— ecranul o spune el însuși, iar `INSERT`-ul e desfăcut de `curata_proba_ecrane.py`.

CE MĂSOARĂ: mesajul verbatim, plus starea celor două scheme (număr + amprentă) înainte și după
fiecare apăsare — deci se vede și dacă o operațiune a fost ACCEPTATĂ pe date imposibile.
"""
import json
import os
import sys

_H = os.path.dirname(os.path.abspath(__file__))
_R = os.path.abspath(os.path.join(_H, "..", ".."))
sys.path.insert(0, os.path.join(_R, "frontend_test"))
sys.path.insert(0, _H)
sys.path.insert(0, _R)

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402
from core import db  # noqa: E402

# `1899-02-30` NU aterizeaza intr-un `input[type=date]`: 30 februarie nu exista, deci browserul
# refuza valoarea si campul ramane gol. Masurat: toate cele 32 de operatiuni au raspuns „Camp
# obligatoriu: Data" — proba masura un camp LIPSA, nu o data imposibila. `1899-01-01` exista
# (deci aterizeaza) si e la fel de imposibila ca data contabila a firmei.
INVALID = {"text": "«»@#$%", "numar": "-99999999", "data": "1899-01-01"}

# [R170, 06.09.2026] Enumerarea se face pe STRUCTURA, nu pe euristici de text.
#
# Prima forma culegea toate butoanele vizibile si arunca ce nu parea o operatiune: fara sageti, si
# `t.length > 46 -> sari`. Efectul, masurat azi: registrul are **34** de intrari, proba a raportat
# **32**, iar cele doua aruncate erau chiar cele cu titlul lung —
#   47  «Achizitie necorporala (software/licenta/brevet)»
#   60  «Achizitie de la neinregistrat (persoana fizica) - D394 op. N»
# Nu erau „fara defect": erau NEDESCHISE, purtand numele unora probate. *Un plafon tacut intr-un
# instrument de masura se citeste ca acoperire.*
#
# Butoanele de operatiune poarta `data-op` — asta le deosebeste de orice alt buton al ecranului,
# fara sa ghiceasca din text. Filtrul de sageti si de lungime dispare cu totul.
JS_OPERATIUNI = """
() => {
  const R = document.querySelector(".fereastra-corp") || document.body;
  const out = [];
  R.querySelectorAll("button[data-op]").forEach((e) => {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.disabled) return;
    const t = (e.textContent || "").trim().replace(/\\s+/g, " ");
    if (!t) return;
    out.push(t);
  });
  return out;
}
"""
JS_UMPLE = """
(v) => {
  const R = document.querySelector(".fereastra-corp") || document.body;
  let n = 0, s = 0;
  for (const e of R.querySelectorAll("select")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.disabled || e.value) continue;
    const o = Array.from(e.options).find((x) => x.value && !x.disabled);
    if (!o) continue;
    e.value = o.value;
    e.dispatchEvent(new Event("input", { bubbles: true }));
    e.dispatchEvent(new Event("change", { bubbles: true }));
    s++;
  }
  for (const e of R.querySelectorAll("input, textarea")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.readOnly || e.disabled) continue;
    const t = (e.getAttribute("type") || "text").toLowerCase();
    if (["checkbox", "radio", "file", "hidden"].includes(t)) continue;
    e.value = t === "number" ? v.numar : (t === "date" ? v.data : v.text);
    e.dispatchEvent(new Event("input", { bubbles: true }));
    e.dispatchEvent(new Event("change", { bubbles: true }));
    n++;
  }
  return { camp: n, sel: s };
}
"""
JS_GENEREAZA = """
() => {
  const R = document.querySelector(".fereastra-corp") || document.body;
  const b = Array.from(R.querySelectorAll("button, .buton-primar")).find((e) => {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.disabled) return false;
    const t = (e.textContent || "").toLowerCase();
    return t.includes("generează") || t.includes("genereaza") || t.includes("salveaz");
  });
  if (!b) return null;
  b.setAttribute("data-gen", "1");
  return (b.textContent || "").trim().slice(0, 34);
}
"""
JS_TEXT = "() => (document.body.innerText || '').replace(/\\s+/g, ' ').trim()"


def _dif(a, b):
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return b[max(0, i - 20):i + 260]


def _tabele(conn, scheme):
    out = []
    with conn.cursor() as cur:
        for sch in scheme:
            cur.execute("SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY 1", (sch,))
            out += [(sch, r[0]) for r in cur.fetchall()]
    return out


def stare(conn, tabele):
    out = {}
    with conn.cursor() as cur:
        for sch, t in tabele:
            try:
                cur.execute('SELECT count(*), coalesce(md5(string_agg(md5(x::text), \'\' '
                            'ORDER BY md5(x::text))), \'-\') FROM "%s"."%s" x' % (sch, t))
                n, amp = cur.fetchone()
                out["%s.%s" % (sch, t)] = "%d/%s" % (n, amp[:8])
            except Exception:  # noqa: BLE001
                conn.rollback()
    conn.rollback()
    return out


db.init_pool()
conn = db.get_conn().__enter__()
TABELE = _tabele(conn, ["tenant_003"])
print("tabele urmarite: %d" % len(TABELE))

rez = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1200})
    ctx.add_init_script(w_auth.init_pentru(w_auth.EMAIL_IMPLICIT))
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    # Ecranul poate sta in oricare din liste — s-a mutat in `ECRANE` cand lotul i-a atins JS-ul
    # (R143). Unealta nu trebuie sa stie in care: cauta in toate, ca sa nu cada la urmatoarea mutare.
    _toate = dict(list(nav_ecrane.ECRANE) + list(nav_ecrane.ECRANE_CAMPANIE))
    deschide = _toate["operatiuni"]

    deschide(pg)
    pg.wait_for_timeout(1400)
    operatiuni = pg.evaluate(JS_OPERATIUNI)
    print("operatiuni gasite: %d\n" % len(operatiuni))

    for nume in operatiuni:
        try:
            deschide(pg)
            pg.wait_for_timeout(800)
            pg.get_by_role("button", name=nume, exact=True).first.click(timeout=6000)
            pg.wait_for_timeout(1500)
        except Exception as ex:  # noqa: BLE001
            rez.append({"op": nume, "verdict": "navigare esuata", "detaliu": str(ex)[:80]})
            print("%-44s NAVIGARE ESUATA" % nume[:44])
            continue
        u = pg.evaluate(JS_UMPLE, INVALID)
        pg.wait_for_timeout(400)
        buton = pg.evaluate(JS_GENEREAZA)
        if not buton:
            rez.append({"op": nume, "camp": u["camp"], "sel": u["sel"], "verdict": "fara buton de generare"})
            print("%-44s camp=%-3d sel=%-3d FARA BUTON" % (nume[:44], u["camp"], u["sel"]))
            continue
        t0 = pg.evaluate(JS_TEXT)
        s0 = stare(conn, TABELE)
        try:
            pg.click('[data-gen="1"]', timeout=5000)
        except Exception as ex:  # noqa: BLE001
            rez.append({"op": nume, "verdict": "click esuat", "detaliu": str(ex)[:70]})
            print("%-44s CLICK ESUAT" % nume[:44])
            continue
        pg.wait_for_timeout(2000)
        t1 = pg.evaluate(JS_TEXT)
        s1 = stare(conn, TABELE)
        schimbat = {k: (s0.get(k), s1.get(k)) for k in s1 if s0.get(k) != s1.get(k)}
        verdict = ("a scris" if schimbat else ("a vorbit" if t1 != t0 else "TACE"))
        mesaj = ((t1[len(t0):] if t1.startswith(t0) else "") or _dif(t0, t1)).strip()[:240]
        rez.append({"op": nume, "camp": u["camp"], "sel": u["sel"], "buton": buton,
                    "verdict": verdict, "mesaj": mesaj, "a_scris": schimbat or None})
        print("%-44s camp=%-3d sel=%-3d [%s] %s" % (nume[:44], u["camp"], u["sel"], verdict, mesaj[:70]))
    ctx.close()

with open(os.path.join(_H, "proba_operatiuni.json"), "w", encoding="utf-8") as fh:
    json.dump({"erori_js": erori[:10], "operatiuni": rez}, fh, ensure_ascii=False, indent=1)

import collections  # noqa: E402
c = collections.Counter(r.get("verdict") for r in rez)
print("\nTOTAL %d operatiuni:" % len(rez))
for k, v in c.most_common():
    print("   %-24s %d" % (k, v))
print("erori JS:", erori[:3] or "niciuna")
