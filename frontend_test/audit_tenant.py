# -*- coding: utf-8 -*-
"""ORCHESTRATOR audit multifatetat per tenant (MODEL_AUDIT_TENANT.md, fatetele AUTOMATIZABILE).

  audit_tenant.py <tenant_id> [--fara-vizual]

Ruleaza si raporteaza, cu verdict verde/rosu per fateta:
  F2 (corectitudine calcul + DUK)  = pt fiecare declaratie DATORATA (semafor), genereaza + DUKIntegrator.
  F7 (coerenta semafor)            = starea semaforului + restante care NU se pot genera (posibil restanta falsa).
  F6 (a11y vizual + mobil)         = axe (region/contrast/eticheta) + Pixel5 (tinta <24px / revarsare) pe ecranele accesibile.

F3 (integritate seed<->consumator) si F5 (mesaje de blocaj provocate) RAMAN semi-manuale (cer date deliberat
gresite + citirea ecranului) - nu se automatizeaza; scriptul le listeaza ca "de facut manual".

Nu repara nimic. Iese 1 daca vreo fateta e ROSIE. Sursele: /control-fiscal, /declaratii/tipuri,
/declaratii/{tip}/valideaza (DUK), + uneltele vizuale din frontend_test/vizual/.
"""
import os
import sys
import json
import urllib.request
import urllib.error

BAZA = "http://127.0.0.1:8010"
HERE = os.path.dirname(os.path.abspath(__file__))
AXE = open(os.path.join(HERE, "vizual", "axe.min.js"), encoding="utf-8").read()

CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        CFG[k] = v


def call(path, payload=None, tok=None, method=None):
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BAZA + path, data, h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=90)), None
    except urllib.error.HTTPError as e:
        try:
            body = json.load(e)
        except Exception:
            body = {"detail": e.read().decode(errors="replace")[:300]}
        return None, {"cod": e.code, "detail": body.get("detail") if isinstance(body, dict) else body}


class Raport:
    def __init__(self):
        self.fatete = []  # (nume, verdict "VERDE"/"ROSU"/"MANUAL", linii[])

    def add(self, nume, verdict, linii):
        self.fatete.append((nume, verdict, linii))

    def tipar(self):
        print("\n" + "=" * 72)
        rosu = 0
        for nume, verdict, linii in self.fatete:
            mark = {"VERDE": "[VERDE]", "ROSU": "[ROSU ]", "MANUAL": "[MANUAL]"}.get(verdict, "[?]")
            print("%s %s" % (mark, nume))
            for l in linii:
                print("        " + l)
            if verdict == "ROSU":
                rosu += 1
        print("=" * 72)
        print("VERDICT: %s (%d fatete rosii)" % ("AUDIT ROSU" if rosu else "AUTOMAT VERDE", rosu))
        return rosu


def _perioada_body(tip, per, an, luna):
    b = {"an": an}
    if per == "lunar":
        b["luna"] = luna or 12
    elif per == "trimestrial":
        b["trim"] = ((int(luna or 12) - 1) // 3) + 1
    # anual: doar an
    return b


def faceta_f2_f7(rap, tok, tid):
    """F2 (DUK pe datorate) + F7 (coerenta semafor)."""
    sem, err = call("/control-fiscal/%d" % tid, tok=tok)
    if err:
        rap.add("F7 semafor + F2 DUK", "ROSU", ["nu pot citi /control-fiscal: %s" % err])
        return
    stare = sem.get("stare")
    lipsa = sem.get("lipsa") or []
    urmarit = sem.get("urmarit") or []
    neclar = sem.get("neclar") or []
    tipuri, e2 = call("/declaratii/tipuri?tenant_id=%d" % tid, tok=tok)
    per_map = (tipuri or {}).get("periodicitate", {}) if not e2 else {}

    f7 = ["semafor: stare=%s | datorate=%s depuse=%s | lipsa=%d urmarit=%d neclar=%d"
          % (stare, sem.get("datorate"), sem.get("depuse"), len(lipsa), len(urmarit), len(neclar))]
    for n in neclar:
        f7.append("  neclar: %s - %s" % (n.get("tip"), n.get("cauza") or n.get("motiv") or ""))
    _con = sem.get("contabil")
    _constat = _con if isinstance(_con, list) else (_con.get("constatari") if isinstance(_con, dict) else [])
    for c in (_constat or []):
        if isinstance(c, dict) and c.get("stare") == "rosu":
            f7.append("  constatare ROSIE: %s" % (c.get("eticheta") or str(c.get("mesaj",""))[:70]))

    # F2: genereaza+DUK fiecare declaratie DATORATA (lipsa)
    f2 = []
    rosu_f2 = False
    falsa_restanta = []
    de_verificat = [("restanta", x) for x in lipsa] + [("de urmarit", x) for x in urmarit]
    if not de_verificat:
        f2.append("nicio declaratie datorata/de urmarit de validat - firma la zi pe vector")
    for _cat, it in de_verificat:
        tip = it.get("tip")
        an = it.get("an")
        luna = it.get("luna")
        per = per_map.get(tip, "lunar")
        body = {"tenant_id": tid}
        body.update(_perioada_body(tip, per, an, luna))
        rez, e = call("/declaratii/%s/valideaza" % tip, body, tok=tok, method="POST")
        et = "%s %s (%s)" % (tip.upper(), it.get("perioada") or ("%s/%s" % (luna, an)), _cat)
        if e and e["cod"] == 422:
            # refuz PRE-XML: declaratia nu se poate genera (ex. pe zero) desi semaforul o cere -> semnal F7
            f2.append("%-16s REFUZ generare (422): %s" % (et, str(e["detail"])[:90]))
            falsa_restanta.append(et)
        elif e:
            f2.append("%-16s EROARE %s: %s" % (et, e["cod"], str(e["detail"])[:80]))
            rosu_f2 = True
        else:
            st = rez.get("stare")
            if st == "valid":
                f2.append("%-16s DUK valid" % et)
            elif st == "erori":
                f2.append("%-16s DUK ERORI: %s" % (et, (rez.get("erori") or "")[:100]))
                rosu_f2 = True
            else:
                f2.append("%-16s DUK gri (nevalidat): %s" % (et, rez.get("temei") or ""))
                rosu_f2 = True

    if falsa_restanta:
        f7.append("POSIBILA RESTANTA FALSA (semaforul o cere, generatorul o refuza pe zero): %s"
                  % ", ".join(falsa_restanta))
        f7.append("  -> verifica manual: e restanta reala (lipsesc date) sau falsa (nu se datoreaza)?")

    rap.add("F2 corectitudine calcul + DUK pe declaratiile datorate", "ROSU" if rosu_f2 else "VERDE", f2)
    # F7 rosu doar daca semaforul insusi e rosu; restanta-falsa e semnal de verificat, nu rosu automat
    rap.add("F7 coerenta semafor", "ROSU" if stare == "rosu" else "VERDE", f7)


# ---- F6: axe + mobil pe ecranele accesibile (Playwright) ----
AXE_RUN = """async () => {
  const r = await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
  const REGION = await axe.run(document, {runOnly:{type:'rule',values:['region','landmark-unique','landmark-one-main']}, resultTypes:['violations']});
  const C=new Set(['color-contrast','color-contrast-enhanced']);
  const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
  let contrast=0,label=0,alte=[];
  for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
  let region=0; for (const v of REGION.violations) region+=v.nodes.length;
  // tinte <24px (AA 2.5.8) + revarsare
  let sub24=0; for (const e of document.querySelectorAll('button,a[href],input,select,textarea,[role=button],.btn-link')){const b=e.getBoundingClientRect(); if(b.width&&b.height&&(b.width<24||b.height<24))sub24++;}
  const overflow = document.body.scrollWidth > window.innerWidth + 2;
  return {contrast,label,region,alte,sub24,overflow};
}"""


def faceta_f6(rap, tok, user, tid, firm_nume):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        rap.add("F6 a11y vizual + mobil", "MANUAL", ["Playwright indisponibil: %s" % e])
        return
    INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(tok) + ');'
            'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(user)) + ');')
    linii = []
    rosu = False
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        # profil desktop (axe) + mobil (Pixel5) pe aceleasi ecrane
        for prof, vp, extra in [("desktop", {"width": 1300, "height": 2000}, {}),
                                ("mobil", {"width": 393, "height": 851},
                                 {"device_scale_factor": 2.75, "is_mobile": True, "has_touch": True})]:
            ctx = b.new_context(viewport=vp, **extra)
            ctx.add_init_script(INIT)
            def _deschide(pg):
                pg.goto(BAZA + "/", wait_until="networkidle")
                pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(600)
                pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
                pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
                pg.wait_for_selector("button.firme-rand", timeout=10000)
                pg.get_by_text(firm_nume, exact=False).first.click(timeout=8000)
                pg.wait_for_selector("[id^='fa-']", timeout=10000); pg.wait_for_timeout(300)
            try:
                pg0 = ctx.new_page(); _deschide(pg0)
                ecrane = pg0.eval_on_selector_all("button.firme-optiune[id^='fa-']:not([disabled])",
                                                  "els => els.map(e => e.id)")
                pg0.close()
            except Exception as ex:
                linii.append("[%s] deschidere firma esuata: %s" % (prof, str(ex)[:80])); ctx.close(); continue
            for eid in ecrane:
                pg = ctx.new_page()
                try:
                    _deschide(pg)  # navigare PROASPATA per ecran -> stare curata
                    pg.click("#" + eid); pg.wait_for_timeout(1700)
                    pg.evaluate(AXE)
                    r = pg.evaluate(AXE_RUN)
                    probleme = []
                    if r["contrast"]: probleme.append("contrast=%d" % r["contrast"])
                    if r["label"]: probleme.append("fara-eticheta=%d" % r["label"])
                    if r["region"]: probleme.append("region=%d" % r["region"])
                    if prof == "mobil" and r["sub24"]: probleme.append("tinte<24px=%d" % r["sub24"])
                    if prof == "mobil" and r["overflow"]: probleme.append("REVARSARE-X")
                    if probleme:
                        rosu = True; linii.append("[%s] %-16s %s" % (prof, eid, ", ".join(probleme)))
                    else:
                        linii.append("[%s] %-16s curat" % (prof, eid))
                except Exception as ex:
                    linii.append("[%s] %-16s navigare esuata: %s" % (prof, eid, str(ex)[:60]))
                finally:
                    pg.close()
            ctx.close()
        b.close()
    rap.add("F6 a11y vizual (axe) + mobil (Pixel5) pe ecranele accesibile", "ROSU" if rosu else "VERDE", linii)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Utilizare: audit_tenant.py <tenant_id> [--fara-vizual]")
        sys.exit(2)
    tid = int(args[0])
    fara_vizual = "--fara-vizual" in sys.argv

    d, err = call("/auth/login", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
    if err:
        print("login esuat:", err)
        sys.exit(2)
    tok = d["token"]
    user = d["user"]
    tn, e = call("/tenants", tok=tok)
    firma = next((t for t in (tn or {}).get("tenants", []) if t.get("id") == tid), None)
    if not firma:
        print("tenant %d nu e in lista userului de test (acces?)" % tid)
        sys.exit(2)
    print("AUDIT tenant %d — %s (CUI %s, schema %s)" % (tid, firma.get("nume"), firma.get("cui"), firma.get("schema_name")))

    rap = Raport()
    faceta_f2_f7(rap, tok, tid)
    if not fara_vizual:
        faceta_f6(rap, tok, user, tid, firma.get("nume"))
    else:
        rap.add("F6 a11y vizual + mobil", "MANUAL", ["sarit (--fara-vizual)"])
    # fatetele semi-manuale, mereu listate ca reminder
    rap.add("F3 integritate date (seed<->consumator)", "MANUAL",
            ["de facut manual: urmareste fiecare camp de la producator la consumator pe date populate"])
    rap.add("F5 mesaje de blocaj (limba contabilului)", "MANUAL",
            ["de facut manual: provoaca fiecare refuz/camp obligatoriu si citeste ecranul (Regula 14.4)"])

    rosu = rap.tipar()
    sys.exit(1 if rosu else 0)


if __name__ == "__main__":
    main()
