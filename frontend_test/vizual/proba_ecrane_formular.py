# -*- coding: utf-8 -*-
"""PROBA PE ECRAN: cand formularul primeste date gresite, VORBESTE ecranul?

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

AL PATRULEA RASPUNS, adaugat in lotul 11: **a cerut un fisier**. Butonul «Adauga document
(pozeaza / incarca)» de pe ecranul bonurilor a fost raportat **TACE** — si nu tacea: cheama
`input[type=file].click()`, adica deschide selectorul de fisiere al sistemului, pe care
sonda nu-l vede. *Un instrument care nu poate vedea un raspuns nu are voie sa-l numeasca
tacere.* Playwright ridica evenimentul `filechooser`; el se asculta, si verdictul devine
«a cerut un fisier» — nici defect, nici trecut cu vederea.

──────────────────────────────────────────────────────────────────────────────
CE A ADAUGAT LOTUL 11 (04.09.2026), si de ce era nevoie. Din cele 15 ecrane parcurse in lotul 10,
**noua** au raportat `campuri=0`: sonda ajungea pe ecran si nu gasea nimic de completat, fiindca
formularul lor traieste intr-o FEREASTRA care se deschide abia dupa o apasare — «Adauga», «Nou»,
«Emite». Un `campuri=0` se citea ca „ecran parcurs", si nu era: era **un ecran neprobat cu numele
unuia probat**. Acum, daca nu se gaseste niciun camp, sonda cauta un DESCHIZATOR si il apasa, apoi
recontroleaza. Ce s-a deschis se scrie in artefact (`deschis_cu`), ca sa nu se confunde niciodata
un ecran care n-are formular cu unul al carui formular n-a fost gasit.

CE NU FACE, declarat:
  1. **umple numai ce e in `.fereastra`.** Un formular randat inline, in corpul ecranului, nu e
     completat — si atunci `campuri=0` ramane onest: „n-am avut ce completa", nu „nu refuza".
  2. **incearca cel mult trei deschizatoare**, in ordinea din DOM. Daca formularul cere doi pasi
     (alege luna, apoi apasa), nu ajunge la el.
  3. **nu stie daca un deschizator a si SCRIS.** De-aia se masoara starea schemei si inainte de
     deschidere, nu doar in jurul apasarii probate.
  4. **vede ce s-a schimbat, nu CE anume s-a schimbat.** Amprenta spune ca tabelul difera;
     care rand si care coloana se afla citind, nu din artefact.

CUM SE RULEAZA:
    PROBA_ECRANE=poarta      — numai ecranele din `nav_ecrane.ECRANE` (inventarul portii vizuale)
    PROBA_ECRANE=campanie    — numai ecranele din `nav_ecrane.ECRANE_CAMPANIE`
    PROBA_ECRANE=tot         — amandoua (implicit)
Artefactul se scrie ca `proba_ecrane_<set>.json`, langa fisierul asta.
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
import nav_ecrane  # noqa: E402

PROBATE = ("salveaz", "salvez", "salvare", "adaug", "genereaz")
OPRITE = ("sterg", "șterg", "import", "depun", "trimit")
# Deschizatoarele NU sunt aceleasi cu cele probate: „Adauga" e in amandoua liste, fiindca pe un
# ecran deschide fereastra, iar in fereastra e chiar butonul de salvare. Se decide dupa EFECT
# (a aparut un camp de completat?), nu dupa nume.
DESCHIZATOARE = ("adaug", "nou", "noua", "nouă", "emite", "creeaz", "inregistr", "înregistr",
                 "editeaz", "deschide", "completeaz")

INVALID_TEXT = "«»@#$%"
INVALID_NUMAR = "-99999999"
INVALID_DATA = "1899-02-30"

SCHEMA = os.environ.get("PROBA_SCHEMA", "tenant_003")
SET = os.environ.get("PROBA_ECRANE", "tot")

JS_TEXT = "() => (document.body.innerText || '').replace(/\\s+/g, ' ').trim()"

JS_NR_CAMPURI = """
() => {
  let n = 0;
  for (const e of document.querySelectorAll(".fereastra input, .fereastra textarea")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.readOnly || e.disabled) continue;
    const t = (e.getAttribute("type") || "text").toLowerCase();
    if (t === "checkbox" || t === "radio" || t === "file" || t === "hidden") continue;
    n++;
  }
  return n;
}
"""

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
    b.setAttribute("data-proba-formular", String(i));
    out.push({ i, text: (b.textContent || "").trim().slice(0, 40) });
  });
  return out;
}
"""

# Deschizatoarele se cauta in TOT ecranul, nu in `.fereastra` — tocmai fiindca fereastra inca
# nu exista. Se sar cele oprite, ca sa nu se apese „Sterge" ca sa se deschida ceva.
JS_DESCHIZATOARE = """
(g) => {
  const out = [];
  document.querySelectorAll("button, .buton-primar, a.btn-link").forEach((b, i) => {
    const r = b.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || b.disabled) return;
    const t = (b.textContent || "").toLowerCase().trim();
    if (!t || t.length > 40) return;
    if (g.oprite.some((x) => t.includes(x))) return;
    if (!g.deschizatoare.some((x) => t.includes(x))) return;
    b.setAttribute("data-proba-deschide", String(i));
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
    """CONTINUTUL fiecarui tabel al schemei — numarul de randuri SI o amprenta a lor.

    [LOTUL 11, 04.09.2026] Pana azi asta numara `count(*)`, si atat. Consecinta n-a fost teoretica:
    la prima rulare pe ecranele de firma, sonda a apasat «Salveaza» pe ecranul «Date firma» cu
    formularul umplut cu `«»@#$%`, iar serverul A REDENUMIT FIRMA — in `public.tenants` si in
    `firma_profil`, amandoua UPDATE-uri. Numarul de randuri n-a miscat, deci sonda a raportat
    „SCHIMBARI DE STARE: niciuna" despre o firma careia tocmai ii schimbase denumirea de pe
    declaratii. Numele vechi s-a refacut citindu-l din D394-urile DEPUSE (`denP` pe CUI 95141537),
    nu din memorie.

    *O sonda care numara randuri masoara INSERT-urile si stergerile, si e oarba la exact felul de
    scriere pe care il face un ecran de «date»: modificarea.* Amprenta o vede.

    Nu o lista de tabele aleasa de mine: TOATE tabelele schemei — o sonda care se uita doar la
    tabelele la care s-a gandit e oarba exact acolo unde nu s-a gandit.
    """
    out = {}
    with conn.cursor() as cur:
        for t in tabele:
            try:
                cur.execute('SELECT count(*), coalesce(md5(string_agg(md5(x::text), \'\' '
                            'ORDER BY md5(x::text))), \'-\') FROM "%s"."%s" x' % (SCHEMA, t))
                n, amp = cur.fetchone()
                out[t] = "%d/%s" % (n, amp[:8])
            except Exception:  # noqa: BLE001
                conn.rollback()
    conn.rollback()
    return out


def alege_ecrane():
    if SET == "poarta":
        return list(nav_ecrane.ECRANE)
    if SET == "campanie":
        return list(nav_ecrane.ECRANE_CAMPANIE)
    return list(nav_ecrane.ECRANE) + list(nav_ecrane.ECRANE_CAMPANIE)


from core import db  # noqa: E402

db.init_pool()
conn = db.get_conn().__enter__()
TABELE = _tabele(conn)
print("set: %s · tabele in %s: %d" % (SET, SCHEMA, len(TABELE)))
stare0 = stare(conn, TABELE)

ECRANELE = alege_ecrane()
print("ecrane de parcurs: %d" % len(ECRANELE))

rez = {}
scrieri = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1250, "height": 1100})
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))

    # Un buton care deschide selectorul de fisiere A RASPUNS. Fara ascultatorul asta, el arata
    # identic cu unul care nu face nimic — v. „al patrulea raspuns" din antet.
    fisiere_cerute = []

    def _fisier_cerut(fc):
        fisiere_cerute.append(1)
        try:
            fc.set_files([])
        except Exception:  # noqa: BLE001
            pass

    pg.on("filechooser", _fisier_cerut)

    def pregateste(deschide):
        """Ecran -> (daca trebuie) deschide fereastra -> umple. Intoarce (campuri, deschis_cu)."""
        deschide(pg)
        pg.wait_for_timeout(500)
        if pg.evaluate(JS_NR_CAMPURI) > 0:
            return pg.evaluate(JS_UMPLE, {"text": INVALID_TEXT, "numar": INVALID_NUMAR,
                                          "data": INVALID_DATA}), None
        candidati = pg.evaluate(JS_DESCHIZATOARE, {"deschizatoare": list(DESCHIZATOARE),
                                                   "oprite": list(OPRITE)})
        for cand in candidati[:3]:
            try:
                pg.click('[data-proba-deschide="%d"]' % cand["i"], timeout=4000)
            except Exception:  # noqa: BLE001
                continue
            pg.wait_for_timeout(1200)
            if pg.evaluate(JS_NR_CAMPURI) > 0:
                return pg.evaluate(JS_UMPLE, {"text": INVALID_TEXT, "numar": INVALID_NUMAR,
                                              "data": INVALID_DATA}), cand["text"]
            # n-a deschis nimic: se revine pe ecran curat si se incearca urmatorul
            deschide(pg)
            pg.wait_for_timeout(400)
            pg.evaluate(JS_DESCHIZATOARE, {"deschizatoare": list(DESCHIZATOARE),
                                           "oprite": list(OPRITE)})
        return 0, None

    for nume, deschide in ECRANELE:
        s_inainte_nav = stare(conn, TABELE)
        try:
            umplute, deschis_cu = pregateste(deschide)
        except Exception as ex:  # noqa: BLE001
            rez[nume] = {"eroare_navigare": str(ex)[:120]}
            print("%-24s NAVIGARE ESUATA: %s" % (nume, str(ex)[:70]))
            continue
        s_dupa_nav = stare(conn, TABELE)
        sch_nav = {k: (s_inainte_nav.get(k), s_dupa_nav.get(k))
                   for k in s_dupa_nav if s_inainte_nav.get(k) != s_dupa_nav.get(k)}
        if sch_nav:
            scrieri.append((nume, "DESCHIDERE: %s" % deschis_cu, sch_nav))
        butoane = pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE)})
        ecran = {"campuri_umplute": umplute, "deschis_cu": deschis_cu,
                 "scris_la_deschidere": sch_nav or None, "butoane": []}
        for bt in butoane:
            t0 = pg.evaluate(JS_TEXT)
            s0 = stare(conn, TABELE)
            f0 = len(fisiere_cerute)
            try:
                pg.click('[data-proba-formular="%d"]' % bt["i"], timeout=4000)
            except Exception as ex:  # noqa: BLE001
                ecran["butoane"].append({"buton": bt["text"], "click": "esuat: %s" % str(ex)[:60]})
                continue
            pg.wait_for_timeout(1800)
            t1 = pg.evaluate(JS_TEXT)
            s1 = stare(conn, TABELE)
            schimbat = {k: (s0.get(k), s1.get(k)) for k in s1 if s0.get(k) != s1.get(k)}
            if schimbat:
                scrieri.append((nume, bt["text"], schimbat))
            a_cerut_fisier = len(fisiere_cerute) > f0
            ecran["butoane"].append({
                "buton": bt["text"],
                "text_nou": (t1 != t0),
                "delta_text": (t1[len(t0):] if t1.startswith(t0) else "")[:200] or _dif(t0, t1),
                "a_scris": schimbat or None,
                "a_cerut_fisier": a_cerut_fisier or None,
                "verdict": ("a vorbit" if t1 != t0 else
                            ("a scris" if schimbat else
                             ("a cerut un fisier" if a_cerut_fisier else "TACE"))),
            })
            try:
                pregateste(deschide)
                pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE)})
            except Exception:  # noqa: BLE001
                break
        rez[nume] = ecran
        print("%-24s campuri=%-3s %-22s %s" % (
            nume, ecran["campuri_umplute"],
            ("(deschis cu «%s»)" % deschis_cu[:16]) if deschis_cu else "",
            "  ".join("[%s → %s]" % (x.get("buton", "?")[:22], x.get("verdict", x.get("click", "?")))
                      for x in ecran["butoane"])))

stare1 = stare(conn, TABELE)
sch = {k: (stare0.get(k), stare1.get(k)) for k in stare1 if stare0.get(k) != stare1.get(k)}
print()
print("SCHIMBARI DE STARE, cap la cap:", sch or "niciuna")
for s in scrieri:
    print("   a scris:", s)
print("erori JS:", erori[:3] or "niciuna")

with open(os.path.join(_HERE, "proba_ecrane_%s.json" % SET), "w", encoding="utf-8") as f:
    json.dump({"set": SET, "schema": SCHEMA, "schimbari": sch, "scrieri": scrieri, "ecrane": rez,
               "erori_js": erori[:10]}, f, ensure_ascii=False, indent=1)

tot = [x for e in rez.values() for x in e.get("butoane", []) if "verdict" in x]
fara_campuri = [n for n, e in rez.items() if e.get("campuri_umplute") == 0]
print()
print("TOTAL butoane probate: %d · au vorbit: %d · au scris: %d · au cerut un fisier: %d · TAC: %d"
      % (len(tot), sum(1 for x in tot if x["verdict"] == "a vorbit"),
         sum(1 for x in tot if x["verdict"] == "a scris"),
         sum(1 for x in tot if x["verdict"] == "a cerut un fisier"),
         sum(1 for x in tot if x["verdict"] == "TACE")))
print("ecrane FARA niciun camp de completat (deci NEPROBATE, nu «fara defect»): %d — %s"
      % (len(fara_campuri), ", ".join(sorted(fara_campuri)) or "niciunul"))
