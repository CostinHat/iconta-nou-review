# -*- coding: utf-8 -*-
"""PROBA în browser — C1/C2/C7 + deciziile C3/C4/C11 (comanda Costin 07.10.2026), pe baza de TEST (8011). Reface drumurile
din parcurgerea din 06.10 (rolurile: asistentul = Ana — pregătește, nu validează, nu depune; patronul = cabinetul):

  C1   Distributie Profit IC 08/2026: Declarații → D390 → Continuă → „Trimite în coadă”.
  C2   Firma Grea Audit 08/2026: Declarații → D307 → o operațiune (A, CUI 14399840, TVA 5.000) → Regenerează → „Trimite în coadă”.
  C3   Panificatie 09/2026: D112 cu atenționarea DUK SP1B4_1 (numai când serverul de probă rulează validatorul VECHI —
       `--atentionare`): „Trimite în coadă” → confirmarea scrisă → coadă; apoi cabinetul aprobă și depune fără altă confirmare.
  C11  Constructii Profit Trim: Bilanț S1003 2025 → „Trimite în coadă” (Ana) → Ana nu aprobă (403) → cabinetul aprobă și depune.
  C4   Constructii Profit Trim: Operațiuni speciale → Reevaluare imobilizări → câmpul mijlocului fix (listă / număr).
  C7   Distributie Profit IC: Operațiuni speciale → „Achiziție de la agricultor (compensare 8%)” → titlul formularului deschis.

Aceeași probă pe codul VECHI (înainte) și NOU (după). SCRIE în baza de test (coadă, depuneri cu index de probă, notificări,
Date firmă pe Constructii, accesul și bifele asistentului); `curata()` le pune la loc după reperele de la pornire.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_c1_c2_c7.py --iesire /tmp/…/c127_dupa.json [--atentionare]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import auth_api, db  # noqa: E402
from proba_asistent_drepturi import _sesiune  # noqa: E402

ASIST, CAB = "asistent@prisma-cont.test", "patron@prisma-cont.test"
F = {"F1": (14769, "tenant_017", "Firma Grea Audit SRL"), "F1s": (4784, "tenant_001", "Panificatie Salarii Speciale SRL"),
     "F2": (4840, "tenant_005", "Constructii Profit Trim SRL"), "F3": (4839, "tenant_004", "Distributie Profit IC SRL")}
BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011")


def _cnp(baza12):
    """CNP cu cifra de control calculată (algoritmul oficial, CLAUDE.md) — nu un CNP inventat."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


def tok(email):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("select id from public.users where email=%s", (email,))
        s = auth_api.sesiune_pentru_user(c, cur.fetchone()[0])
        c.rollback()
    return s["token"]


def api(t, m, p, b=None):
    rq = urllib.request.Request(BAZA + p, method=m, data=json.dumps(b).encode() if b is not None else None,
                                headers={"Content-Type": "application/json", "Authorization": "Bearer " + t})
    try:
        with urllib.request.urlopen(rq, timeout=300) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw[:200].decode("utf-8", "replace")


def repere():
    rp = {"utn": []}
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("select coalesce(max(id),0) from public.declaratii_coada"); rp["coada"] = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.notificari"); rp["notif"] = cur.fetchone()[0]
        cur.execute("select tenant_id, an, luna, tip, nr_depunere from public.declaratii_depuse where tenant_id = any(%s)",
                    ([v[0] for v in F.values()],))
        rp["depuse"] = [list(x) for x in cur.fetchall()]
        cur.execute('select * from "%s".firma_profil limit 1' % F["F2"][1])
        rp["profil_col"] = [d[0] for d in cur.description]; rp["profil"] = list(cur.fetchone())
        cur.execute('select coalesce(max(id),0) from "%s".firma_profil_jurnal' % F["F2"][1]); rp["fpj"] = cur.fetchone()[0]
        cur.execute("select id, poate_pregati, poate_valida, poate_depune from public.users where email=%s", (ASIST,))
        uid, *rp["bife"] = cur.fetchone(); rp["uid"] = uid
        cur.execute("update public.users set poate_pregati=true, poate_valida=false, poate_depune=false where id=%s", (uid,))
        for tid, _s, _n in F.values():
            cur.execute("select 1 from public.user_tenants where user_id=%s and tenant_id=%s", (uid, tid))
            if not cur.fetchone():
                cur.execute("insert into public.user_tenants (user_id, tenant_id) values (%s,%s)", (uid, tid)); rp["utn"].append(tid)
        # bilanțul cere nr. de registrul comerțului (lipsă pe firma de test): pus temporar, ca la orice probă de bilanț
        cur.execute('update "%s".firma_profil set reg_com=coalesce(nullif(reg_com,\'\'),\'J40/123/2020\')' % F["F2"][1])
        c.commit()
    return rp


def curata(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("select tenant_id, an, luna, tip, nr_depunere from public.declaratii_depuse where tenant_id = any(%s)",
                    ([v[0] for v in F.values()],))
        exist = {tuple(x) for x in rp["depuse"]}
        for x in [x for x in cur.fetchall() if tuple(x) not in exist]:
            cur.execute("delete from public.declaratii_depuse where tenant_id=%s and an=%s and luna is not distinct from %s and tip=%s "
                        "and nr_depunere is not distinct from %s", x)
        cur.execute("delete from public.declaratii_coada where id > %s", (rp["coada"],))
        cur.execute("delete from public.notificari where id > %s", (rp["notif"],))
        cur.execute('delete from "%s".firma_profil_jurnal where id > %%s' % F["F2"][1], (rp["fpj"],))
        cols = [x for x in rp["profil_col"] if x != "id"]
        vals = [v for x, v in zip(rp["profil_col"], rp["profil"]) if x != "id"]
        cur.execute('update "%s".firma_profil set %s' % (F["F2"][1], ", ".join('"%s"=%%s' % x for x in cols)), vals)
        cur.execute("update public.users set poate_pregati=%s, poate_valida=%s, poate_depune=%s where id=%s", tuple(rp["bife"]) + (rp["uid"],))
        for tid in rp["utn"]:
            cur.execute("delete from public.user_tenants where user_id=%s and tenant_id=%s", (rp["uid"], tid))
        c.commit()
    return "curatat"


def pagina(pw, email):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1366, "height": 900})
    ctx.add_init_script(_sesiune(email))
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    return b, pg, erori


def firma(pg, nume):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=25000); pg.wait_for_timeout(500)
    if pg.query_selector(".asi-nod[data-nod='firme']"):
        pg.click(".asi-nod[data-nod='firme']")
    else:
        pg.click("button.cab-card:has([data-cheie='firme'])"); pg.wait_for_selector("#opt-existente"); pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
    pg.locator("#firme-lista button.firme-rand", has_text=re.compile(re.escape(nume))).first.click()
    pg.wait_for_selector("#fa-declaratii", timeout=15000); pg.wait_for_timeout(400)


def text(pg, n=1500):
    return pg.evaluate("(n) => { const c = document.querySelector('.fereastra-corp'); return c ? c.innerText.slice(0, n) : ''; }", n)


def declaratie(pg, nume_firma, tip, an, luna=None):
    firma(pg, nume_firma)
    pg.click("#fa-declaratii"); pg.wait_for_selector("#dec-tip", timeout=20000); pg.wait_for_timeout(500)
    pg.select_option("#dec-tip", tip); pg.wait_for_timeout(300)
    pg.fill("#dec-an", str(an))
    if luna:
        pg.select_option("#dec-luna", str(luna))
    pg.click("#dec-continua")
    pg.wait_for_function("() => /Pasul 2/.test(document.querySelector('.fereastra-corp').innerText)", timeout=90000)
    pg.wait_for_timeout(2500)


def trimite(pg, cap, nume):
    pg.screenshot(path=os.path.join(cap, nume + "_inainte_de_trimitere.png"), full_page=True)
    pg.click("#dec-trimite"); pg.wait_for_timeout(5000)
    pg.screenshot(path=os.path.join(cap, nume + "_dupa_trimitere.png"), full_page=True)
    return {"trimisa": bool(pg.query_selector(".dec-gata-titlu")),
            "mesaj": [e.inner_text().strip() for e in pg.query_selector_all(".fereastra-corp .msg-eroare, .fereastra-corp .caseta-atentie")][:3],
            "confirmare_ceruta": bool(pg.query_selector("#coada-confirmare"))}


def coada_noua(rp, tid, tip):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("select id, stare, payload->'confirmare_atentionari' is not null, length(payload->>'xml') from public.declaratii_coada "
                    "where id > %s and tenant_id=%s and tip=%s order by id desc limit 1", (rp["coada"], tid, tip))
        r = cur.fetchone(); c.rollback()
    return r


def flux_cabinet(rp, tid, tip, ana, cab):
    r = coada_noua(rp, tid, tip)
    if not r:
        return {"in_coada": False}
    cid = r[0]
    out = {"in_coada": True, "coada_id": cid, "confirmare_pastrata": r[2], "xml_octeti": r[3]}
    out["ana_aproba"] = api(ana, "POST", "/coada/%s/aproba" % cid, {})[0]
    out["cab_aproba"] = api(cab, "POST", "/coada/%s/aproba" % cid, {})
    out["cab_depune"] = api(cab, "POST", "/coada/%s/depune" % cid, {"spv_index": "PROBA-C127-%s" % cid})
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("select stare from public.declaratii_coada where id=%s", (cid,)); out["stare"] = cur.fetchone()[0]
        cur.execute("select tip, an, luna, length(xml), nr_depunere from public.declaratii_depuse where tenant_id=%s and upper(tip)=upper(%s) "
                    "order by data_depunere desc nulls last limit 1", (tid, tip))
        out["depusa"] = cur.fetchone(); c.rollback()
    return out


def proba(pw, cap, atentionare, rp, r):
    ana, cab = tok(ASIST), tok(CAB)
    b, pg, er = pagina(pw, ASIST)
    if atentionare:
        declaratie(pg, F["F1s"][2], "d112", 2026, 9)
        r["C3_pas2"] = text(pg, 600)
        r["C3_trimitere"] = trimite(pg, cap, "C3_D112")
        if r["C3_trimitere"]["confirmare_ceruta"]:
            pg.fill("#coada-confirmare", "B4_5P 4.125 = 4.325 − 200, OUG 89/2025 art.III alin.(5) lit.b; atenționarea vine din validatorul vechi")
            pg.click("#coada-confirma"); pg.wait_for_timeout(5000)
            pg.screenshot(path=os.path.join(cap, "C3_D112_dupa_confirmare.png"), full_page=True)
            r["C3_dupa_confirmare"] = {"trimisa": bool(pg.query_selector(".dec-gata-titlu"))}
        r["C3_cabinet"] = flux_cabinet(rp, F["F1s"][0], "d112", ana, cab)
        b.close()
        return
    # C1
    declaratie(pg, F["F3"][2], "d390", 2026, 8)
    r["C1_D390"] = trimite(pg, cap, "C1_D390")
    r["C1_cabinet"] = flux_cabinet(rp, F["F3"][0], "d390", ana, cab)
    # C2
    declaratie(pg, F["F1"][2], "d307", 2026, 8)
    pg.select_option("#d307-tip", "A"); pg.fill("#d307-cod", "14399840"); pg.fill("#d307-den", "Cedent SRL"); pg.fill("#d307-tva", "5000")
    pg.click("#d307-add"); pg.wait_for_timeout(500); pg.click("#d307-regen"); pg.wait_for_timeout(6000)
    r["C2_regenerat_valid"] = "fără erori" in text(pg, 3000)
    r["C2_D307"] = trimite(pg, cap, "C2_D307")
    r["C2_cabinet"] = flux_cabinet(rp, F["F1"][0], "d307", ana, cab)
    # C11 — bilanțul, pregătit de Ana
    firma(pg, F["F2"][2]); pg.click("#fa-bilant"); pg.wait_for_timeout(2500)
    r["C11_buton_coada"] = bool(pg.query_selector("#bl-coada"))
    if r["C11_buton_coada"]:
        pg.fill("#bl-an", "2025"); pg.select_option("#bl-tip", "s1003"); pg.click("#bl-coada"); pg.wait_for_timeout(6000)
        r["C11_mesaj"] = text(pg, 1500)[-400:]
    pg.screenshot(path=os.path.join(cap, "C11_bilant.png"), full_page=True)
    r["C11_cabinet"] = flux_cabinet(rp, F["F2"][0], "s1003", ana, cab)
    # C2/C11 — un tip ANUAL fără termen sursat (D230): intra în coadă cu 500 („scadenta: lipsește luna sau trim”)
    cnp = _cnp("196022915094")
    st, rr = api(ana, "POST", "/coada", {"tenant_id": F["F1"][0], "tip": "d230", "an": 2025,
                                          "manual": {"nume_c": "POPESCU", "initiala_c": "I", "prenume_c": "ANA MARIA", "cif_c": cnp,
                                                     "adresa_c": "Str Test 1 Bucuresti", "den_entitate": "Asociatia Binele",
                                                     "cif_entitate": "14399840", "cont_entitate": "RO49AAAA1B31007593840000",
                                                     "procent": 3.5, "valabilitate_distribuire": 2}})
    r["C2_D230_anual_in_coada"] = {"http": st, "raspuns": rr if isinstance(rr, dict) else str(rr)[:200]}
    r["erori_consola_ana"] = er
    b.close()
    # C4 și C7 — cabinetul, în Operațiuni speciale
    b, pg, er = pagina(pw, CAB)
    firma(pg, F["F2"][2]); pg.click("#fa-operatiuni"); pg.wait_for_selector("[data-op]", timeout=20000)
    pg.click("[data-op='reevaluare']"); pg.wait_for_selector("#op-trimite", timeout=15000)
    pg.select_option("#op-operatie", "reevaluare"); pg.wait_for_timeout(2500)
    el = pg.query_selector("#op-mijloc_fix_id")
    r["C4_camp"] = {"tag": el.evaluate("e => e.tagName"), "tip": el.get_attribute("type"),
                    "optiuni": el.evaluate("e => e.tagName === 'SELECT' ? [...e.options].map(o => o.textContent.trim()) : null"),
                    "eticheta": pg.eval_on_selector("label[for='op-mijloc_fix_id']", "e => e.innerText.trim()")}
    pg.screenshot(path=os.path.join(cap, "C4_reevaluare.png"), full_page=True)
    firma(pg, F["F3"][2]); pg.click("#fa-operatiuni"); pg.wait_for_selector("[data-op]", timeout=20000)
    pg.locator("button[data-op]", has_text="Achiziție de la agricultor").first.click()
    pg.wait_for_selector("#op-trimite", timeout=15000); pg.wait_for_timeout(500)
    r["C7_titlu_formular"] = pg.eval_on_selector(".fereastra-corp h2.pf-titlu", "e => e.innerText.trim()")
    r["C7_campuri"] = pg.eval_on_selector_all(".fereastra-corp label.camp-eticheta", "els => els.map(e => e.innerText.trim())")
    pg.screenshot(path=os.path.join(cap, "C7_agricultor.png"), full_page=True)
    r["erori_consola_cabinet"] = er
    b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iesire", required=True)
    ap.add_argument("--atentionare", action="store_true")
    a = ap.parse_args()
    cap = a.iesire.replace(".json", "_capturi"); os.makedirs(cap, exist_ok=True)
    db.init_pool()
    rp = repere(); r = {}
    t0 = time.time()
    try:
        with sync_playwright() as pw:
            proba(pw, cap, a.atentionare, rp, r)
    except Exception as e:  # noqa: BLE001
        r["EROARE_PROBA"] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:300])
    finally:
        r["curatenie"] = curata(rp); r["durata_s"] = round(time.time() - t0, 1)
        json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k, v in r.items():
        print(k, json.dumps(v, ensure_ascii=False, default=str)[:600])


if __name__ == "__main__":
    main()
