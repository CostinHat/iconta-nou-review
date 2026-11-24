"""Proba de produs R. Se copiază integral în frontend_test/e2e."""
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

IDS = tuple(f"e.{i}" for i in range(1, 6))
TITLURI = ("Ce face", "Când se folosește", "Ce trebuie pregătit înainte", "Pas cu pas",
           "Ce iese la capăt", "Greșeli frecvente", "Reguli fiscale")
FER = {"asistenti": ("F006",), "termene": ("F081", "F093"), "capacitate": ("F014",),
       "pachete": ("F065",), "tipare": ("F094", "F120")}
MARCAJ = {"asistenti": "#asi-lista", "termene": ".mig-intro", "capacitate": ".cap-ecran, .cap-cifre",
          "pachete": "#pac-firma", "tipare": "#tip-ai"}
REZ = ((1366, 768), (603, 590))
TOP = ".fereastra-overlay:not(.fundal)"
NORME = ("texte_ajutor_revizuite_final_17_5_R2.txt", "harta_plasare_semne.tsv", "curatenie_registru_lista.tsv",
         "fara_loc.txt", "referinta_randuri_17_5_R2.json")


def unice(perechi):
    rezultat = {}
    for k, v in perechi:
        if k in rezultat:
            raise ValueError(f"cheie dublă: {k}")
        rezultat[k] = v
    return rezultat


def director_date(repo):
    # Un singur set de intrări, fără amestec între pachet și arborele testat.
    for d in (repo / "docs/dovezi/17_5_R2", Path.home() / "ghid_incoming"):
        if any((d / n).is_file() for n in NORME):
            if not all((d / n).is_file() for n in NORME):
                raise ValueError(f"intrări incomplete în {d}")
            return d
    raise FileNotFoundError("lipsesc intrările normative R")


def tabel(p, sep=","):
    with p.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter=sep)
        cap = r.fieldnames
        if not cap or "ID" not in cap or len(set(cap)) != len(cap):
            raise ValueError(f"antet invalid în {p.name}")
        randuri = {}
        for row in r:
            ident = row["ID"]
            if not re.fullmatch(r"F\d{3}", ident or "") or ident in randuri or None in row or None in row.values():
                raise ValueError(f"rând invalid în {p.name}: {ident}")
            randuri[ident] = row
    return cap, randuri


def suma_rand(row):
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def citeste_texte(p):
    s = p.read_text(encoding="utf-8")
    blocuri = re.split(r"^=== (F\d{3})[ \t]*$", s, flags=re.M)
    texte = unice((blocuri[i], blocuri[i+1].strip("\n")) for i in range(1, len(blocuri), 2))
    for ident, txt in texte.items():
        if re.findall(r"^## (.+)$", txt, re.M) != list(TITLURI) or "**" in txt:
            raise ValueError(f"secțiuni invalide: {ident}")
    if len(texte) != 210 or "F067" in texte:
        raise ValueError("setul celor 210 texte diferă")
    return texte


def id_semne(repo):
    gasite = {}
    for p in sorted((repo / "static/js").rglob("*.js")):
        cod = re.sub(r"/\*.*?\*/", "", p.read_text(encoding="utf-8"), flags=re.S)
        cod = "\n".join(l.split("//", 1)[0] if "//" in l and "://" not in l else l for l in cod.splitlines())
        ids = set(re.findall(r"""\bsemnAjutor\(\s*["'`](F\d{3})["'`]\s*\)""", cod))
        for d in re.findall(r"\b(?:_DECL_AJUTOR|_OP_AJUTOR)\s*=\s*\{([^{}]*)\}", cod, re.S):
            ids.update(re.findall(r"""["'`](F\d{3})["'`]""", d))
        for ident in ids:
            gasite.setdefault(ident, set()).add(p.relative_to(repo / "static/js").as_posix())
    return gasite


def observa_static(repo, date):
    cap, activ = tabel(repo / "FUNCTIONALITATI.csv")
    arc = repo / "FUNCTIONALITATI_ARHIVA.csv"
    cap_arc, arhiva = tabel(arc) if arc.exists() else ([], {})
    texte = citeste_texte(date / NORME[0])
    _, harta = tabel(date / NORME[1], "\t")
    _, lista = tabel(date / NORME[2], "\t")
    ref = json.loads((date / NORME[4]).read_text(), object_pairs_hook=unice)
    mut = {i for i, r in lista.items() if r["actiune"] == "MUTA IN ARHIVA"}
    exceptii = unice((l.split("|", 1)[0].strip(), l.split("|", 1)[1].strip())
                     for l in (date/NORME[3]).read_text().splitlines() if l.strip())
    locuri = {i:r["fisier:linie"].rsplit(":",1)[0] for i,r in harta.items()
              if not r["fisier:linie"].startswith("FĂRĂ LOC")}
    if not (len(mut)==21 and mut==set(ref["randuri"]) and len(harta)==146 and len(locuri)==124
            and len(exceptii)==26 and set(exceptii)==(set(harta)-set(locuri))|{"F001","F105","F106","F116"}
            and len(set(texte)-set(exceptii))==185 and set(locuri)<=set(texte) and all(exceptii.values())):
        raise ValueError("intrările R1–R3 nu sunt concordante")
    if not (repo / "static/js/api.js").is_file():
        raise FileNotFoundError("static/js/api.js")
    gasite = id_semne(repo)
    retinut = "F160" in activ
    trebuie = mut
    rele = []
    unificate = {**arhiva, **activ}
    initial = ref["conservate"]
    arhiva_initiala = ref["arhiva_initiala"]
    if set(unificate) != set(initial) | set(arhiva_initiala): rele.append("inventarul ID-urilor")
    for i, amprenta in initial.items():
        if i not in unificate: continue
        omit = {"ajutor", "Stare"} if i == "F067" else ({"ajutor"} if i in texte else set())
        if suma_rand({k:v for k,v in unificate[i].items() if k not in omit}) != amprenta:
            rele.append(f"{i}: câmpuri protejate")
        if i not in mut and i not in activ: rele.append(f"{i}: lipsește din activ")
    for i, amprenta in arhiva_initiala.items():
        if i not in arhiva or suma_rand(arhiva[i]) != amprenta: rele.append(f"{i}: istoric arhivă")
    if cap != ref["coloane"] or cap_arc != cap: rele.append("coloane arhivă/registru")
    if set(activ)&set(arhiva): rele.append("ID comun")
    for i in sorted(trebuie):
        if i in activ or i not in arhiva or suma_rand(arhiva[i]) != ref["randuri"][i]:
            rele.append(i)
    if not activ.get("F067",{}).get("Stare","").startswith("INTERN") or activ.get("F067",{}).get("ajutor"):
        rele.append("F067")
    if any(not r["Stare"].startswith(("ELIMINAT","RESPINS")) for r in arhiva.values()):
        rele.append("stare în arhivă")
    asteptate=set(texte)-set(exceptii)
    return {
      "e.1":{"verificate":sorted(mut),"abateri":rele,"activ":len(activ),"arhiva":len(arhiva),"f160_retinut":retinut},
      "e.2":{"verificate":len(texte),"abateri":sorted(i for i,t in texte.items() if activ.get(i,{}).get("ajutor") != t)},
      "e.3":{"cu_loc":len(asteptate),"mapate":len(locuri),"fara_semn":sorted(asteptate-set(gasite)),
             "loc_gresit":sorted(i for i,cale in locuri.items() if cale not in gasite.get(i,set())),
             "excluse_cu_semn":sorted(set(exceptii)&set(gasite))},
      "e.4":{"semne":len(gasite),"fara_text":sorted(i for i in gasite if not activ.get(i,{}).get("ajutor","").strip())},
    }


def schema(i, m):
    def cere(ok):
        if not ok: raise ValueError(f"măsurare incompletă sau invalidă: {i}")
    def intreg(x): return type(x) is int and x >= 0
    def texte(x): return isinstance(x,list) and all(isinstance(v,str) for v in x)
    def campuri(o, n): cere(isinstance(o,dict) and set(o)==set(n))
    if i != "e.5":
        categorii = {
            "e.1": (("activ","arhiva"),("verificate","abateri"),("f160_retinut",)),
            "e.2": (("verificate",),("abateri",),()),
            "e.3": (("cu_loc","mapate"),("fara_semn","loc_gresit","excluse_cu_semn"),()),
            "e.4": (("semne",),("fara_text",),())}
        n,l,b = categorii[i]
        campuri(m,n+l+b)
        cere(all(intreg(m[k]) for k in n) and all(texte(m[k]) for k in l) and all(type(m[k]) is bool for k in b))
        return
    campuri(m,(f"{w}x{h}" for w,h in REZ))
    for w,h in REZ:
        scene=m[f"{w}x{h}"]
        campuri(scene,FER)
        for card, ids in FER.items():
            x=scene[card]
            campuri(x,("viewport","ordine","suprapuneri","butoane")+(("ajutor",) if card=="asistenti" else ()))
            cere(x["viewport"]==[w,h] and texte(x["ordine"]) and all(k in ids for k in x["ordine"]) and intreg(x["suprapuneri"]))
            campuri(x["butoane"],ids)
            for b in x["butoane"].values():
                campuri(b,("numar","vizibil","incadrat","loc"))
                cere(intreg(b["numar"]) and all(type(b[k]) is bool for k in ("vizibil","incadrat","loc")))
            if card=="asistenti":
                a=x["ajutor"]
                campuri(a,("titlu","text_corect"))
                cere(isinstance(a["titlu"],str) and type(a["text_corect"]) is bool)


def rezultat(i, m):
    schema(i,m)
    if i == "e.1":
        return len(set(m["verificate"])) == 21 and m["activ"] > 0 and m["arhiva"] >= 21 and not m["f160_retinut"] and m["abateri"] == []
    if i == "e.2":
        return m["verificate"] == 210 and m["abateri"] == []
    if i == "e.3":
        return (m["cu_loc"],m["mapate"]) == (185,124) and all(m[k] == [] for k in ("fara_semn","loc_gresit","excluse_cu_semn"))
    if i == "e.4":
        return m["semne"] > 0 and m["fara_text"] == []
    if i != "e.5":
        raise ValueError(i)
    for w,h in REZ:
        scene=m[f"{w}x{h}"]
        if set(scene) != set(FER): raise ValueError("parcurs incomplet")
        for card, ids in FER.items():
            x = scene[card]
            if x["viewport"] != [w,h] or x["ordine"] != list(ids) or x["suprapuneri"] != 0:
                return False
            if any(x["butoane"][k] != {"numar":1,"vizibil":True,"incadrat":True,"loc":True} for k in ids): return False
            if card=="asistenti" and not (x["ajutor"]["titlu"]=="Ce face" and x["ajutor"]["text_corect"] is True):
                return False
    return True


def deschide(pg, baza, card):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.reload(wait_until="domcontentloaded")
    cheie = "activitate" if card == "tipare" else card
    buton = pg.locator(f"button.cab-card:has([data-cheie='{cheie}'])")
    buton.wait_for(state="attached")
    if buton.locator("xpath=ancestor::*[@id='fgc-sef']").count() and not buton.is_visible():
        pg.locator("button[aria-controls='fgc-sef'][aria-expanded='false']").click()
    buton.click()
    if card == "tipare":
        pg.locator(TOP + " #opt-tipare").click()
    fer = pg.locator(TOP).locator(".fereastra").first
    fer.locator(MARCAJ[card]).first.wait_for(state="attached")
    fer.locator(".fereastra-corp h2").first.wait_for(state="attached")
    return fer


MASOARA = """(fer, ids) => {
 const toate = Array.from(fer.querySelectorAll('button.ajutor-btn[data-ajutor]'));
 const alese = toate.filter(b=>ids.includes(b.dataset.ajutor));
 const drept = b=>b.getBoundingClientRect(), f=drept(fer);
 const titlu=fer.querySelector('.fereastra-corp h2');
 const zonaTitlu=b=>titlu && (titlu.contains(b) || (titlu.nextElementSibling===b.parentElement));
 const intersect=(a,b)=>a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom;
 const viz=b=>{const r=drept(b),s=getComputedStyle(b);return r.width>1&&r.height>1&&s.visibility==='visible'&&s.display!=='none';};
 const butoane={}; for(const id of ids){
   const a=alese.filter(b=>b.dataset.ajutor===id), b=a[0], r=b&&drept(b);
   const randAI=b?.closest('p, .cap-nota, .tip-ai-intro');
   const eticheta=randAI && Array.from(randAI.querySelectorAll('b,strong')).find(e=>/^analiz[ăa] AI$/i.test(e.textContent.trim()));
   const loc=b && (id==='F120' ? !!eticheta && !!(eticheta.compareDocumentPosition(b)&4) : zonaTitlu(b));
   butoane[id]={numar:a.length,vizibil:!!b&&viz(b),incadrat:!!r && r.left>=Math.max(0,f.left)-1 && r.right<=Math.min(innerWidth,f.right)+1 && r.top>=Math.max(0,f.top)-1 && r.bottom<=Math.min(innerHeight,f.bottom)+1,loc:!!loc};
 }
 let suprapuneri=0; for(const a of alese) for(const b of toate) if(a!==b&&viz(a)&&viz(b)&&intersect(drept(a),drept(b))) suprapuneri++;
 return {viewport:[innerWidth,innerHeight],ordine:alese.map(b=>b.dataset.ajutor),suprapuneri,butoane};
}"""


def test_ajutor_17_5_R2(browser, capsys):
    from conftest import BAZA, CAPTURI, sesiune
    from core.ceas_proba import MOMENT_REF
    repo = Path(__file__).resolve().parents[2]
    dest = Path(CAPTURI) / "17_5_R2"
    dest.mkdir(parents=True, exist_ok=True)
    masuri, partiale, erori = {}, {}, {}
    pas = "inițializarea"
    try:
        url = urlsplit(BAZA)
        if (url.scheme, url.hostname, url.port) not in (("http","localhost",8019),("http","127.0.0.1",8019)):
            raise ValueError("testul cere instanța locală de test pe 8019")
        date = director_date(repo)
        prima = citeste_texte(date / NORME[0])["F006"].splitlines()[1].strip()
        init = sesiune("dovada.71507@sesiuneab.test")
        statice = observa_static(repo,date)
        scene = {}
        for w,h in REZ:
            ctx = browser.new_context(viewport={"width":w,"height":h})
            try:
                ctx.clock.set_fixed_time(MOMENT_REF)
                ctx.add_init_script(init)
                pg = ctx.new_page()
                dim = f"{w}x{h}"
                scene[dim]={}
                for card,ids in FER.items():
                    pas = f"{dim} / {card} / deschidere"
                    fer = deschide(pg,BAZA,card)
                    if card == "asistenti" and w == 1366:
                        for i,m in statice.items():
                            pg.screenshot(path=str(dest / f"{i}.png"))
                            masuri[i]=m
                    pas = f"{dim} / {card} / poziție și captură"
                    # Semnele pot fi pe rândul de sub titlu. Adu zona funcției în fereastra vizibilă.
                    grupa=fer.locator("h2").first
                    grupa.scroll_into_view_if_needed()
                    x=fer.evaluate(MASOARA,list(ids))
                    if card=="tipare":
                        tinta=fer.locator("button.ajutor-btn[data-ajutor='F120']")
                        if tinta.count()==1:
                            tinta.scroll_into_view_if_needed()
                            x["butoane"]["F120"]=fer.evaluate(MASOARA,list(ids))["butoane"]["F120"]
                    scene[dim][card]=x
                    pg.screenshot(path=str(dest/f"{dim}_{card}.png"))
                    if card=="tipare" and w==603: pg.screenshot(path=str(dest/"e.5.png"))
                    if card=="asistenti":
                        pas=f"{dim} / ajutor F006"
                        x["ajutor"]={"titlu":"","text_corect":False}
                        b=fer.locator("button.ajutor-btn[data-ajutor='F006']")
                        if b.count()==1 and b.is_visible():
                            b.click()
                            continut=pg.locator(TOP+" .aj-continut")
                            continut.wait_for(state="visible")
                            if continut.locator("h4").count() and continut.locator("p").count():
                                x["ajutor"]={"titlu":continut.locator("h4").first.inner_text().strip(),
                                    "text_corect":continut.locator("p").first.inner_text().strip()==prima}
                            pg.screenshot(path=str(dest/f"{dim}_ajutor_F006.png"))
            finally:
                ctx.close()
        masuri["e.5"]=scene
    except Exception as exc:
        erori[pas] = f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}"
        partiale["e.5"]=locals().get("scene",{})
    for nume,ob in (("masuri",masuri),("erori",erori),("partiale",partiale)):
        (dest/f"{nume}.json").write_text(json.dumps(ob,ensure_ascii=False,indent=2),encoding="utf-8")
    verdict = {i:rezultat(i,m) for i,m in masuri.items()}
    with capsys.disabled():
        for i,v in verdict.items(): print(f"VERDICT {i} {'trece' if v else 'pica'}",flush=True)
    if erori: raise RuntimeError(f"NEEXECUTAT: {erori}")
    assert set(verdict)==set(IDS) and all(verdict.values()), f"R_PRODUS {verdict}"
