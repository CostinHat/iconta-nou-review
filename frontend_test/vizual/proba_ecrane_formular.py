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
  1. **incearca cel mult trei deschizatoare**, in ordinea din DOM. Daca formularul cere doi pasi
     (alege luna, apoi apasa), nu ajunge la el.
  2. **nu stie daca un deschizator a si SCRIS.** De-aia se masoara starea schemei si inainte de
     deschidere, nu doar in jurul apasarii probate.
  3. **vede ce s-a schimbat, nu CE anume s-a schimbat.** Amprenta spune ca tabelul difera;
     care rand si care coloana se afla citind, nu din artefact.

──────────────────────────────────────────────────────────────────────────────
CE A ADAUGAT LOTUL 12 (04.09.2026) — trei schimbari, fiecare ceruta de o masuratoare.

**(1) UN CONTEXT PER ROL.** Cele 33 de unitati ramase (`#462`–`#501`) sunt ecrane de cabinet,
admin si portal. `app.js` alege desktopul din `sesiune.rol()` **la pornire**, deci rolul nu se
poate schimba in aceeasi fila: un ecran de admin cerut intr-un context de cabinet ar randa
desktopul cabinetului, iar sonda ar raporta „navigare esuata" despre un ecran sanatos. Lista
`nav_ecrane.ECRANE_CABINET` poarta contul langa fiecare ecran, iar hamul deschide cate un
context per cont — grupat, nu unul per ecran.

**(2) CAMPURILE NU MAI SUNT CAUTATE DOAR IN `.fereastra`.** Limitarea era declarata de lotul 11
si a devenit falsificatoare la lotul 12: desktopul unui rol (`cabinet.js`, `admin.js`,
`navigator.js`) **nu e o fereastra**, deci pe el `campuri=0` n-ar fi insemnat „n-are formular",
ci „n-am stiut unde sa ma uit". Acum domeniul e `.fereastra` **daca exista**, altfel `body` —
si domeniul ales se SCRIE in artefact (`domeniu`), ca sa nu se confunde niciodata cele doua.

**(3) SELECTURILE SE ALEG, si sunt declarate ca VALIDE.** Din cele 15 ecrane ale lotului 10,
noua raportau `campuri=0` pentru ca formularul lor cere intai o alegere — o luna, un partener, o
firma. Un `<select>` nu poate primi `«»@#$%`: nu se tasteaza in el. Deci alegerea e **pasul care
deschide formularul**, nu obiectul probei — se ia prima optiune cu valoare nevida, iar cate s-au
ales se scrie in artefact (`selectii`). *Ce se probeaza ramane ce se poate TASTA gresit.*

CUM SE RULEAZA:
    PROBA_ECRANE=poarta      — numai ecranele din `nav_ecrane.ECRANE` (inventarul portii vizuale)
    PROBA_ECRANE=campanie    — numai ecranele din `nav_ecrane.ECRANE_CAMPANIE`
    PROBA_ECRANE=cabinet     — numai ecranele din `nav_ecrane.ECRANE_CABINET` (cabinet/admin)
    PROBA_ECRANE=tot         — toate trei (implicit)
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
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402

# [LOTUL 12] „emite" adaugat dupa CITIREA rutei, nu dupa nume. Diagnosticul a aratat ca pe ecranul
# de emitere (#478) — cel mai mare formular al lotului, 6 campuri si 5 selecturi — singurul buton
# apasat era «+ Adauga linie»: butonul de fond, «Emite factura», nu contine niciun cuvant din lista,
# deci ecranul ar fi fost raportat „fara defect" fara sa fi fost apasat. `POST /tenants/{}/facturi/emite`
# (main.py:3224) creeaza factura in baza si NU trimite nimic la SPV — deci nu intra sub regula
# `depun`/`trimit`. Consuma insa un numar din serie: daca e acceptata, verdictul e «a scris», si
# curatenia de dupa proba are ce sa numeasca.
PROBATE = ("salveaz", "salvez", "salvare", "adaug", "genereaz", "emite")
# [LOTUL 12] „cu ai" / „analiza ai" s-au adaugat pe ACELASI temei ca `depun`/`trimit`, nu pe altul:
# ies din aplicatie. Verificat la sursa, nu dedus din nume — `/tipare/ai` cheama `tipare_api.analiza_ai`,
# care cheama `core.ai_client` (main.py:901), iar `/pachete/{}/genereaza` trece prin `genereaza_poveste`.
# Un refuz care nu cade ar fi facut un apel real, contra cost, la un furnizor din afara.
OPRITE = ("sterg", "șterg", "import", "depun", "trimit", "cu ai", "analiza ai", "analiză ai")

# Butoane pe care NUMELE le opreste, dar ruta lor nu iese nicaieri — deblocate una cate una, fiecare
# cu ruta citita si numita. Potrivirea e pe textul INTREG, nu pe bucata: „trimite" deblocat ca
# substring ar fi deblocat si «Trimite invitația», care chiar pleaca prin email.
#
# DE CE EXISTA. Lista `OPRITE` decide dupa NUME, iar numele nu spune unde ajunge actiunea. «Trimite»
# de pe ecranul de anunturi al adminului face un `INSERT` in `public.anunturi_cabinet` (main.py:676)
# si atat — nicio iesire. Fara exceptie, singurul formular din `admin.js` ar fi ramas neprobat, iar
# raportul ar fi spus „fara defect" despre un ecran pe care nu l-am apasat. *Un instrument care
# refuza mereu invata pe cineva sa-l ocoleasca* — se repara instrumentul, nu se ia excepția pe furis.
EXCEPTII_OPRITE = {
    "trimite": "POST /admin/anunturi — INSERT in public.anunturi_cabinet (main.py:676), fara iesire",
}
# Deschizatoarele NU sunt aceleasi cu cele probate: „Adauga" e in amandoua liste, fiindca pe un
# ecran deschide fereastra, iar in fereastra e chiar butonul de salvare. Se decide dupa EFECT
# (a aparut un camp de completat?), nu dupa nume.
DESCHIZATOARE = ("adaug", "nou", "noua", "nouă", "emite", "creeaz", "inregistr", "înregistr",
                 "editeaz", "deschide", "completeaz")

INVALID_TEXT = "«»@#$%"
INVALID_NUMAR = "-99999999"
INVALID_DATA = "1899-02-30"

# [LOTUL 12] STAREA SE MASOARA PE TOATE SCHEMELE ATINSE, nu pe una.
# Pana azi era o singura schema, si asta a fost adevarat cat timp toate ecranele erau ale aceleiasi
# firme. Lotul 12 probeaza si ecranul RIP, care traieste pe firma de PARTIDA SIMPLA — alta schema.
# O sonda care numara `tenant_003` in timp ce apasa butoane pe alta schema ar fi raportat „n-a scris
# nimic" despre scrieri pe care nu le poate vedea. *A treia instanta a clasei „sonda era oarba" —
# si singura pe care am prins-o INAINTE de a raporta, nu dupa.*
# Schema firmei de partida simpla se CITESTE din baza dupa numele ei, nu se scrie aici: numele de
# schema se aloca dintr-o secventa la creare, deci scris in cod ar fi o cifra care imbatraneste tacut.
SCHEME = [x.strip() for x in os.environ.get("PROBA_SCHEMA", "tenant_003").split(",") if x.strip()]
SET = os.environ.get("PROBA_ECRANE", "tot")

JS_TEXT = "() => (document.body.innerText || '').replace(/\\s+/g, ' ').trim()"

# [LOTUL 12] Domeniul, intr-un singur loc. O fereastra modala e frontiera fireasca a unui ecran;
# cand nu exista — desktopurile de rol —, ecranul E pagina. Amandoua se declara in artefact.
JS_DOMENIU = """
() => (document.querySelector(".fereastra") ? "fereastra" : "pagina")
"""

_JS_RAD = 'const R = document.querySelector(".fereastra") || document.body;'

JS_NR_CAMPURI = """
() => {
  %s
  let n = 0;
  for (const e of R.querySelectorAll("input, textarea")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || e.readOnly || e.disabled) continue;
    const t = (e.getAttribute("type") || "text").toLowerCase();
    if (t === "checkbox" || t === "radio" || t === "file" || t === "hidden") continue;
    n++;
  }
  return n;
}
""" % _JS_RAD

JS_UMPLE = """
(v) => {
  %s
  let n = 0;
  for (const e of R.querySelectorAll("input, textarea")) {
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
""" % _JS_RAD

# [LOTUL 12] Alegerea dintr-un `<select>` e PASUL care deschide formularul, nu obiectul probei:
# intr-un select nu se poate tasta o valoare imposibila. Se ia prima optiune cu valoare nevida
# si numai daca selectul e inca pe una goala — altfel s-ar strica alegerea facuta de ecran.
JS_SELECTURI = """
() => {
  %s
  let n = 0;
  for (const s of R.querySelectorAll("select")) {
    const r = s.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || s.disabled) continue;
    if (s.value) continue;
    const o = Array.from(s.options).find((x) => x.value && !x.disabled);
    if (!o) continue;
    s.value = o.value;
    s.dispatchEvent(new Event("input", { bubbles: true }));
    s.dispatchEvent(new Event("change", { bubbles: true }));
    n++;
  }
  return n;
}
""" % _JS_RAD

# [LOTUL 12] SANTINELA — cate campuri mai poarta chiar valoarea pe care am scris-o eu.
#
# DE CE. „A vorbit" se masoara pe text nou vizibil (lotul 10), si asta a reparat sub-numararea:
# un ecran cu clasa proprie de eroare nu mai e acuzat de tacere. Dar masura are si celalalt sens
# de eroare, si el s-a vazut la prima rulare a lotului 12: din sase „a vorbit", TREI erau text nou
# care nu raspundea la nimic — o fereastra care s-a inchis (`asistenti`), o navigare catre alt
# ecran (`capacitate`), un buton care a mai adaugat o linie de formular (`emitere`). *Acelasi
# instrument gresea in AMANDOUA directiile — deci n-avea niciun plafon (METODA §22).*
#
# Deosebirea nu se poate face pe text, si nu se face: **daca formularul pe care l-am umplut nu mai
# e acolo, butonul nu mi-a raspuns — m-a dus in alta parte.** Se numara campurile care mai poarta
# santinela, INAINTE si DUPA apasare; asta e o proprietate a DOM-ului, nu o fraza.
JS_SANTINELA = """
(v) => {
  %s
  let n = 0;
  for (const e of R.querySelectorAll("input, textarea")) {
    const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) continue;
    if (e.value === v.text || e.value === v.numar || e.value === v.data) n++;
  }
  return n;
}
""" % _JS_RAD

JS_BUTOANE = """
(g) => {
  %s
  const out = [];
  R.querySelectorAll("button, .buton-primar").forEach((b, i) => {
    const r = b.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0) || b.disabled) return;
    const t = (b.textContent || "").toLowerCase();
    // exceptia se cere pe textul INTREG si trece INAINTEA opririi — v. EXCEPTII_OPRITE
    const exceptat = g.exceptii.includes(t.trim());
    if (!exceptat) {
      if (g.oprite.some((x) => t.includes(x))) return;
      if (!g.probate.some((x) => t.includes(x))) return;
    }
    b.setAttribute("data-proba-formular", String(i));
    out.push({ i, text: (b.textContent || "").trim().slice(0, 40), exceptat: exceptat || undefined });
  });
  return out;
}
""" % _JS_RAD

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


def _schema_firmei(conn, nume):
    """Schema unei firme, dupa numele ei. Derivata din baza, nu scrisa in cod."""
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE nume=%s", (nume,))
        r = cur.fetchone()
    conn.rollback()
    return r[0] if r else None


def _tabele(conn, scheme):
    """[(schema, tabel), ...] pentru toate schemele urmarite."""
    out = []
    with conn.cursor() as cur:
        for sch in scheme:
            cur.execute("SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY 1", (sch,))
            out += [(sch, r[0]) for r in cur.fetchall()]
    return out


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


def alege_ecrane():
    """Ecranele cerute, normalizate la (nume, cont, functie).

    `ECRANE` si `ECRANE_CAMPANIE` sunt perechi si raman asa: ele au un singur cont, cel implicit.
    `ECRANE_CABINET` poarta contul explicit — v. schimbarea (1) din antet."""
    din_perechi = []
    if SET in ("poarta", "tot"):
        din_perechi += list(nav_ecrane.ECRANE)
    if SET in ("campanie", "tot"):
        din_perechi += list(nav_ecrane.ECRANE_CAMPANIE)
    out = [(n, w_auth.EMAIL_IMPLICIT, f) for n, f in din_perechi]
    if SET in ("cabinet", "tot"):
        out += list(nav_ecrane.ECRANE_CABINET)
    return out


from core import db  # noqa: E402

db.init_pool()
conn = db.get_conn().__enter__()
if SET in ("cabinet", "tot"):
    _s_pfa = _schema_firmei(conn, nav_ecrane.FIRMA_PFA)
    if _s_pfa and _s_pfa not in SCHEME:
        SCHEME.append(_s_pfa)
    elif not _s_pfa:
        # Nu se trece tacit peste: fara firma de partida simpla, ecranul RIP nu se poate deschide,
        # iar „fara defect" despre el ar fi o afirmatie despre un ecran neatins.
        print("ATENTIE: firma «%s» nu exista in baza — ecranul RIP nu poate fi probat."
              % nav_ecrane.FIRMA_PFA)
TABELE = _tabele(conn, SCHEME)
print("set: %s · scheme urmarite: %s · tabele: %d" % (SET, ", ".join(SCHEME), len(TABELE)))
stare0 = stare(conn, TABELE)

ECRANELE = alege_ecrane()
print("ecrane de parcurs: %d" % len(ECRANELE))

rez = {}
scrieri = []
erori = []
# Ecranele se grupeaza pe CONT, pastrand ordinea din liste: un context de browser per rol, nu unul
# per ecran (rolul se alege la pornirea filei — v. schimbarea (1) din antet).
CONTURI = []
for _n, _c, _f in ECRANELE:
    if _c not in CONTURI:
        CONTURI.append(_c)
print("conturi: %s" % ", ".join(CONTURI))

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)

    # Un buton care deschide selectorul de fisiere A RASPUNS. Fara ascultatorul asta, el arata
    # identic cu unul care nu face nimic — v. „al patrulea raspuns" din antet.
    fisiere_cerute = []

    def _fisier_cerut(fc):
        fisiere_cerute.append(1)
        try:
            fc.set_files([])
        except Exception:  # noqa: BLE001
            pass

    def pregateste(pg, deschide):
        """Ecran -> alege selecturile -> (daca trebuie) deschide fereastra -> umple.

        Intoarce (campuri, deschis_cu, selectii, domeniu)."""
        def _umple():
            sel = pg.evaluate(JS_SELECTURI)
            if sel:
                pg.wait_for_timeout(900)   # alegerea poate cere date de la server
            n = pg.evaluate(JS_NR_CAMPURI)
            if n == 0:
                return None, sel
            return pg.evaluate(JS_UMPLE, {"text": INVALID_TEXT, "numar": INVALID_NUMAR,
                                          "data": INVALID_DATA}), sel

        deschide(pg)
        pg.wait_for_timeout(500)
        n, sel = _umple()
        if n:
            return n, None, sel, pg.evaluate(JS_DOMENIU)
        candidati = pg.evaluate(JS_DESCHIZATOARE, {"deschizatoare": list(DESCHIZATOARE),
                                                   "oprite": list(OPRITE)})
        for cand in candidati[:3]:
            try:
                pg.click('[data-proba-deschide="%d"]' % cand["i"], timeout=4000)
            except Exception:  # noqa: BLE001
                continue
            pg.wait_for_timeout(1200)
            n2, sel2 = _umple()
            if n2:
                return n2, cand["text"], sel + sel2, pg.evaluate(JS_DOMENIU)
            sel += sel2
            # n-a deschis nimic: se revine pe ecran curat si se incearca urmatorul
            deschide(pg)
            pg.wait_for_timeout(400)
            pg.evaluate(JS_DESCHIZATOARE, {"deschizatoare": list(DESCHIZATOARE),
                                           "oprite": list(OPRITE)})
        return 0, None, sel, pg.evaluate(JS_DOMENIU)

    for cont in CONTURI:
        try:
            init = w_auth.init_pentru(cont)
        except Exception as ex:  # noqa: BLE001  (w_auth.ContInactiv si orice altceva)
            for nume, c, _f in ECRANELE:
                if c == cont:
                    rez[nume] = {"eroare_cont": str(ex)[:160]}
            print("CONT INDISPONIBIL %s: %s" % (cont, str(ex)[:90]))
            continue
        ctx = b.new_context(viewport={"width": 1250, "height": 1100})
        ctx.add_init_script(init)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: erori.append(str(e)))
        pg.on("filechooser", _fisier_cerut)
        print("\n── cont %s ──" % cont)

        for nume, _c, deschide in [x for x in ECRANELE if x[1] == cont]:
            s_inainte_nav = stare(conn, TABELE)
            try:
                umplute, deschis_cu, selectii, domeniu = pregateste(pg, deschide)
            except Exception as ex:  # noqa: BLE001
                rez[nume] = {"eroare_navigare": str(ex)[:120]}
                print("%-24s NAVIGARE ESUATA: %s" % (nume, str(ex)[:70]))
                continue
            s_dupa_nav = stare(conn, TABELE)
            sch_nav = {k: (s_inainte_nav.get(k), s_dupa_nav.get(k))
                       for k in s_dupa_nav if s_inainte_nav.get(k) != s_dupa_nav.get(k)}
            if sch_nav:
                scrieri.append((nume, "DESCHIDERE: %s" % deschis_cu, sch_nav))
            butoane = pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE),
                                       "exceptii": list(EXCEPTII_OPRITE)})
            ecran = {"cont": cont, "domeniu": domeniu, "campuri_umplute": umplute,
                     "deschis_cu": deschis_cu, "selectii": selectii,
                     "scris_la_deschidere": sch_nav or None, "butoane": []}
            _SANT = {"text": INVALID_TEXT, "numar": INVALID_NUMAR, "data": INVALID_DATA}
            for bt in butoane:
                # Butonul care a DESCHIS formularul nu se apasa a doua oara: el nu trimite nimic,
                # doar re-randeaza — si asta se citea ca „a vorbit". (`asistenti`, prima rulare.)
                if deschis_cu and bt["text"].strip().lower() == deschis_cu.strip().lower():
                    ecran["butoane"].append({"buton": bt["text"], "verdict": "sarit: e deschizatorul"})
                    continue
                t0 = pg.evaluate(JS_TEXT)
                sant0 = pg.evaluate(JS_SANTINELA, _SANT)
                camp0 = pg.evaluate(JS_NR_CAMPURI)
                s0 = stare(conn, TABELE)
                f0 = len(fisiere_cerute)
                try:
                    pg.click('[data-proba-formular="%d"]' % bt["i"], timeout=4000)
                except Exception as ex:  # noqa: BLE001
                    ecran["butoane"].append({"buton": bt["text"],
                                             "click": "esuat: %s" % str(ex)[:60]})
                    continue
                pg.wait_for_timeout(1800)
                t1 = pg.evaluate(JS_TEXT)
                sant1 = pg.evaluate(JS_SANTINELA, _SANT)
                camp1 = pg.evaluate(JS_NR_CAMPURI)
                s1 = stare(conn, TABELE)
                schimbat = {k: (s0.get(k), s1.get(k)) for k in s1 if s0.get(k) != s1.get(k)}
                if schimbat:
                    scrieri.append((nume, bt["text"], schimbat))
                a_cerut_fisier = len(fisiere_cerute) > f0
                # Ordinea conteaza si e argumentata:
                #  · „a scris" primul — un buton care a schimbat baza a raspuns, orice ar scrie pe ecran;
                #  · „a plecat de pe formular" INAINTEA lui „a vorbit" — daca santinelele au disparut
                #    si nimic nu s-a scris, textul nou e al ALTUI ecran, nu un raspuns la datele mele;
                #  · „a crescut formularul" la fel — butonul a construit, n-a trimis;
                #  · „a vorbit" ramane pentru cazul in care formularul e inca acolo, cu ce am scris in el.
                if schimbat:
                    verdict = "a scris"
                elif sant0 > 0 and sant1 == 0:
                    verdict = "a plecat de pe formular"
                elif camp1 > camp0:
                    verdict = "a crescut formularul"
                elif t1 != t0:
                    verdict = "a vorbit"
                elif a_cerut_fisier:
                    verdict = "a cerut un fisier"
                else:
                    verdict = "TACE"
                ecran["butoane"].append({
                    "buton": bt["text"],
                    "text_nou": (t1 != t0),
                    "delta_text": (t1[len(t0):] if t1.startswith(t0) else "")[:200] or _dif(t0, t1),
                    "a_scris": schimbat or None,
                    "a_cerut_fisier": a_cerut_fisier or None,
                    "santinele": "%d->%d" % (sant0, sant1),
                    "campuri": "%d->%d" % (camp0, camp1),
                    # un buton apasat pe un ecran fara niciun camp completat NU probeaza date gresite
                    "fara_date": (umplute == 0) or None,
                    "verdict": verdict,
                })
                try:
                    pregateste(pg, deschide)
                    pg.evaluate(JS_BUTOANE, {"probate": list(PROBATE), "oprite": list(OPRITE),
                                       "exceptii": list(EXCEPTII_OPRITE)})
                except Exception:  # noqa: BLE001
                    break
            rez[nume] = ecran
            print("%-24s [%-9s] campuri=%-3s sel=%-3s %-22s %s" % (
                nume, domeniu, ecran["campuri_umplute"], selectii,
                ("(deschis cu «%s»)" % deschis_cu[:16]) if deschis_cu else "",
                "  ".join("[%s → %s]" % (x.get("buton", "?")[:22],
                                         x.get("verdict", x.get("click", "?")))
                          for x in ecran["butoane"])))
        ctx.close()

stare1 = stare(conn, TABELE)
sch = {k: (stare0.get(k), stare1.get(k)) for k in stare1 if stare0.get(k) != stare1.get(k)}
print()
print("SCHIMBARI DE STARE, cap la cap:", sch or "niciuna")
for s in scrieri:
    print("   a scris:", s)
print("erori JS:", erori[:3] or "niciuna")

with open(os.path.join(_HERE, "proba_ecrane_%s.json" % SET), "w", encoding="utf-8") as f:
    json.dump({"set": SET, "scheme": SCHEME, "schimbari": sch, "scrieri": scrieri, "ecrane": rez,
               "erori_js": erori[:10]}, f, ensure_ascii=False, indent=1)

tot = [x for e in rez.values() for x in e.get("butoane", []) if "verdict" in x]
fara_campuri = [n for n, e in rez.items() if e.get("campuri_umplute") == 0]
# [LOTUL 12] Cele trei feluri de NEATINS se numara SEPARAT, si nu se rotunjesc la „fara defect":
# un cont care nu exista, o navigare care a cazut si un ecran fara camp sunt trei cauze diferite,
# cu trei reparatii diferite. Un singur numar peste ele ar ascunde care.
fara_cont = [n for n, e in rez.items() if e.get("eroare_cont")]
nenavigat = [n for n, e in rez.items() if e.get("eroare_navigare")]
print()
import collections as _col  # noqa: E402
_v = _col.Counter(x["verdict"] for x in tot)
# Se numara SEPARAT butoanele apasate pe un formular UMPLUT: doar acelea probeaza date gresite.
_cu_date = [x for x in tot if not x.get("fara_date")]
print("TOTAL butoane apasate: %d (din care pe formular umplut: %d)" % (len(tot), len(_cu_date)))
for _k, _n in _v.most_common():
    print("   %-26s %d" % (_k, _n))
print("TAC (singurul defect): %d" % _v["TACE"])
print("ecrane FARA niciun camp de completat (deci NEPROBATE, nu «fara defect»): %d — %s"
      % (len(fara_campuri), ", ".join(sorted(fara_campuri)) or "niciunul"))
print("ecrane fara CONT viu: %d — %s" % (len(fara_cont), ", ".join(sorted(fara_cont)) or "niciunul"))
print("ecrane la care NAVIGAREA a cazut: %d — %s"
      % (len(nenavigat), ", ".join(sorted(nenavigat)) or "niciunul"))
