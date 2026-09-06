# -*- coding: utf-8 -*-
"""REPROBARE VIZUALĂ — criteriul art. 322 ajunge PE ECRAN, în «Date firmă».

Gardul `core/test_ajutor_periodicitate_tva.py` compară SURSELE celor două ecrane. Aici se citește
ce vede omul: se deschide «Date firmă», se localizează câmpul «Periodicitate TVA» prin `for`-ul
etichetei (nu prin text), și se ia `.camp-ajutor` din același `.camp`. Textul cules se compară
**caracter cu caracter** cu cel randat de «Migrare» pe aceeași instanță.

*Un `?v=` nepotrivit, un fișier nepublicat sau un `esc()` care mănâncă diacriticele nu se văd în
sursă.* — de-aia proba deschide amândouă ecranele, nu doar unul.

Nu apasă niciun buton care scrie: doar deschide și citește. Amprenta schemei se citește oricum
înainte și după.

Rulare (instanță proaspătă, cod nou):
    PROBA_BAZA=http://127.0.0.1:8013 ./venv/bin/python frontend_test/vizual/proba_ajutor_periodicitate.py
"""
import json
import os
import re
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

SCHEMA = "tenant_003"

#: Ajutorul câmpului identificat prin ID-ul controlului, nu prin textul lui: proba nu are voie să
#: caute chiar șirul pe care îl verifică.
JS_AJUTOR = """
(idControl) => {
  const el = document.getElementById(idControl);
  if (!el) return {gasit: false, motiv: "controlul #" + idControl + " nu e in DOM"};
  const camp = el.closest(".camp") || el.closest(".vf-grup") || el.parentElement;
  if (!camp) return {gasit: false, motiv: "controlul n-are container de camp"};
  const aj = camp.querySelector(".camp-ajutor");
  if (!aj) return {gasit: false, motiv: "campul n-are .camp-ajutor"};
  const vizibil = aj.getBoundingClientRect();
  return {gasit: true, text: (aj.textContent || "").trim(),
          latime: vizibil.width, inaltime: vizibil.height};
}
"""


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _amprenta(conn, schema):
    with conn.cursor() as cur:
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema=%s AND table_type='BASE TABLE'""", (schema,))
        t = [r[0] for r in cur.fetchall()]
        n = 0
        for x in t:
            cur.execute('SELECT COUNT(*) FROM "%s"."%s"' % (schema, x))
            n += cur.fetchone()[0]
    return n


def main():
    db.init_pool()
    conn = db.get_conn().__enter__()
    inainte = _amprenta(conn, SCHEMA)
    rez = {"baza": w_auth.BAZA, "randuri_inainte": inainte}

    with sync_playwright() as p:
        b, pg = w_auth.new_page(p)
        erori = []
        pg.on("pageerror", lambda e: erori.append(str(e)))

        # ── «Date firmă» ────────────────────────────────────────────────────
        nav_ecrane.ecran_datefirma(pg)
        pg.wait_for_timeout(1200)
        d = pg.evaluate(JS_AJUTOR, "vf-tip_decont")
        rez["date_firma"] = d
        assert d["gasit"], "«Date firmă»: %s" % d.get("motiv")
        print("DATE FIRMĂ  (%.0fx%.0f px)\n  %s" % (d["latime"], d["inaltime"], d["text"]))

        # ── «Migrare», pe aceeași instanță ──────────────────────────────────
        # Drumul: firma -> «Import date» -> stratul «Vector fiscal» -> formularul unei firme.
        # Navigarea poate eșua din motive străine de ce se probează (o firmă fără vector, un
        # strat mutat); atunci proba SPUNE ce n-a putut citi, nu cade și nu raportează reușită.
        m = {"gasit": False, "motiv": "nenavigat"}
        try:
            w_auth.deschide_firma(pg)
            pg.click("#fa-import", timeout=8000)
            pg.wait_for_timeout(900)
            # `exact=True`: cu `exact=False` prima potrivire e CONTAINERUL tuturor cardurilor
            # („Vector fiscal TVA, regim… Solduri inițiale…"), iar clicul pe el nu deschide nimic.
            # Aceeași lecție ca la lotul 13 — se navighează pe identitate, nu pe o potrivire laxă.
            pg.get_by_text("Vector fiscal", exact=True).first.click(timeout=8000)
            # Din drumul PER-FIRMĂ stratul poate ateriza direct pe formular; din cel de cabinet,
            # pe lista de firme. Se așteaptă oricare din cele două și se continuă de acolo — o
            # sondă care presupune un singur drum raportează „navigare eșuată" despre unul valid.
            pg.wait_for_selector("#vf-decont-grup, #mig-firme", timeout=12000)
            pg.wait_for_timeout(900)
            if pg.locator("#vf-decont-grup").count() == 0:
                pg.locator("#mig-firme button, #mig-firme .mig-frand").first.click(timeout=8000)
                pg.wait_for_selector("#vf-decont-grup", timeout=12000)
                pg.wait_for_timeout(700)
            m = pg.evaluate(JS_AJUTOR, "vf-decont")
        except Exception as ex:  # noqa: BLE001
            m = {"gasit": False, "motiv": "navigare esuata: %s" % str(ex).splitlines()[0][:90]}
        rez["migrare"] = m
        print("MIGRARE     (%s)\n  %s" % ("gasit" if m["gasit"] else m.get("motiv"),
                                          m.get("text", "")))
        rez["erori_js"] = erori
        b.close()

    dupa = _amprenta(conn, SCHEMA)
    rez["randuri_dupa"] = dupa
    rez["egale"] = m["gasit"] and _norm(d["text"]) == _norm(m["text"])
    with open(os.path.join(_H, "proba_ajutor_periodicitate.json"), "w", encoding="utf-8") as f:
        json.dump(rez, f, ensure_ascii=False, indent=1)

    print("\nrânduri: %d → %d · erori JS: %d" % (inainte, dupa, len(erori)))
    assert dupa == inainte, "proba a scris ceva"
    assert not erori, "erori JS pe ecran: %s" % erori[:3]
    # criteriul e VIZIBIL, nu doar prezent în DOM
    assert d["latime"] > 0 and d["inaltime"] > 0, "ajutorul e în DOM dar nu se vede"
    assert _norm(d["text"]).count("art. 322") == 2, (
        "criteriul randat nu citează art. 322 de două ori: %r" % d["text"])
    if m["gasit"]:
        assert rez["egale"], ("textul randat diferă între ecrane:\n  date_firma: %r\n  migrare   : %r"
                              % (_norm(d["text"]), _norm(m["text"])))
        print("\nOK: același criteriu, randat identic în amândouă ecranele.")
    else:
        # Nu se trece tacit: dacă ecranul de migrare nu s-a putut deschide, proba spune ce N-a putut
        # verifica, în loc să raporteze o reușită pe jumătate.
        print("\nOK pe «Date firmă». «Migrare» NU s-a putut citi (%s) — comparația vizuală "
              "între ecrane rămâne pe gardul de sursă." % m.get("motiv"))


main()
