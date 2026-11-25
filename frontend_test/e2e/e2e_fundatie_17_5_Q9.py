"""REAL în staging. Interacțiuni de citire și selecție, fără confirmarea vreunui document."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

IDS = ("e.1", "e.2", "e.3", "e.4")
DIM = ((1366, 768), (603, 590))
TOP = ".fereastra-overlay:not(.fundal)"
CARD = "button.cab-card:has([data-cheie='validat'])"

def luna(text, format_ui=False):
    model = r"(\d{2})/(\d{4})" if format_ui else r"(\d{4})-(\d{1,2})"
    m = re.fullmatch(model, text)
    if not m:
        raise ValueError(f"Lună invalidă {text!r}")
    a, b = map(int, m.groups())
    an, nr = (b, a) if format_ui else (a, b)
    if not 1 <= nr <= 12:
        raise ValueError(f"Lună invalidă {text!r}")
    return an, nr

def pe_rezolutii(i, observatii):
    if set(observatii) != {f"{w}x{h}" for w,h in DIM} or i not in IDS:
        raise ValueError("ID sau rezoluții incomplete")
    rezultate = []
    for w, h in DIM:
        r = observatii[f"{w}x{h}"]
        rezultate.append(pe_latime(i, r, w, h))
    return rezultate

def numara_coada(elemente):
    if not isinstance(elemente, list):
        raise ValueError("Răspunsul GET /coada nu conține lista coada")
    total = 0
    for element in elemente:
        if element["fel"] == "nota" and element["stare"] == "la_senior":
            membri = element.get("membri_ids", [])
            if membri is None:
                membri = []
            if not isinstance(membri, list):
                raise ValueError("Lista membrilor notei este invalidă")
            total += max(1, len(membri))
    return total

def pe_latime(i, r, w, h):
    note = numara_coada(r["elemente_coada"])
    titlu = "De validat" if note else "De depus"
    if r["dim"] != [w,h] or r["titlu_card"] != titlu or r["randuri"] < 1:
        raise ValueError("Ecran, dimensiune sau fixtură incorectă")
    if i in ("e.1", "e.2"):
        titluri = r["titluri_sectiuni"]
        sectiuni = ("Note de validat", "Declarații", "Notele tale în ciornă")
        if len(titluri) != 3:
            raise ValueError("Secțiuni F019 incomplete")
        numere = []
        for titlu, sectiune in zip(titluri, sectiuni):
            potrivire = re.fullmatch(re.escape(sectiune) + r"\s*\((\d+)\)", titlu.strip(), re.I)
            if not potrivire:
                raise ValueError("Titlu de secțiune F019 neidentificat")
            numere.append(int(potrivire.group(1)))
        if numere[0] != note:
            raise ValueError("Numărul notelor din secțiune diferă de GET /coada")
        if numere[2] != r["randuri"]:
            raise ValueError("Ciornele proprii nu corespund secțiunii măsurate")
    if i == "e.1":
        actiuni = r["principale_observate"]
        if not isinstance(actiuni, list) or len(actiuni) != r["primare_fereastra"]:
            raise ValueError("Inventarul principalelor este incomplet")
        if any(not isinstance(x["in_viewport"], bool) or not isinstance(x["pe_rand"], bool)
               or not isinstance(x["text"], str) for x in actiuni):
            raise ValueError("Măsurare incompletă a principalelor")
        if sum(x["pe_rand"] for x in actiuni) != r["primare_rand"]:
            raise ValueError("Număr de principale inconsistent")
        v = (len(actiuni) == 1 and not actiuni[0]["pe_rand"]
             and actiuni[0]["in_viewport"] and bool(actiuni[0]["text"].strip()))
    elif i == "e.2":
        v = (r["valideaza"] > 0 and r["validare_actionabila"] is True and len(r["iduri"]) == r["randuri"] == len(set(r["iduri"]))
             and all(isinstance(k,str) and k.strip() for k in r["iduri"]))
    elif i == "e.3":
        v = (r["tip_dupa"] == "plata_furnizor" and r["suma_input"] == "" and
             "tipul" in r["motiv_inainte"].lower() and "suma" in r["motiv_dupa"].lower()
             and "partenerul" in r["motiv_dupa"].lower() and "tipul" not in r["motiv_dupa"].lower() and r["motiv_vizibil"] == r["motiv_dupa"])
    else:
        if (r["eticheta_luni"] != "Luna comparată" or r["control_luni_in_viewport"] is not True
                or set(r["pixeli_text"]) != {"eticheta", "valoare"}
                or not all(type(n) is int and n >= 8 for n in r["pixeli_text"].values())
                or luna(r["valoare_afisata"], True) != luna(r["valoare_selectata"])
                or r["valoare_selectata"] not in r["luni_ui"]):
            raise ValueError("Captura e.4 nu poate proba controlul de lună")
        start = luna(r["preluare"], True)
        luni = [luna(x) for x in r["luni_ui"]]
        sursa = [luna(x) for x in r["luni_sursa"]]
        eligibile = {x for x in sursa if x >= start}
        if not eligibile:
            raise ValueError("F2 fără lună eligibilă pentru comparație")
        v = bool(luni) and len(luni)==len(set(luni)) and set(luni)==eligibile
    return v

def verdict(i, observatii):
    return all(pe_rezolutii(i, observatii))

MASOARA = """e => {
 const viz=n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);
   return r.width>1 && r.height>1 && s.visibility==='visible' && s.opacity!=='0'};
 const randuri=[...e.querySelectorAll('#val-ciorne tbody.tn-nota[data-tn]')].filter(viz);
 const butoane=[...e.querySelectorAll('button')].filter(viz);
 const titluri = ['#val-note-titlu','#val-decl-titlu','#val-ciorne-titlu'].map(k=>{
   const el=e.querySelector(k); return el && viz(el) ? el.textContent.trim() : '';
 });
 const primare=butoane.filter(n=>n.matches('.buton-primar'));
 const inFereastra=n=>{const r=n.getBoundingClientRect();
   return r.top>=0 && r.bottom<=innerHeight+1 && r.left>=0 && r.right<=innerWidth+1 &&
     n.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2));};
 return {dim:[innerWidth,innerHeight],titluri_sectiuni:titluri,randuri:randuri.length,iduri:randuri.map(n=>n.dataset.tn),
  valideaza:butoane.filter(n=>n.closest('#val-ciorne tbody.tn-nota') && n.textContent.trim()==='Validează' &&
   !n.disabled && n.getAttribute('aria-disabled')!=='true').length,
  primare_rand:primare.filter(n=>n.closest('tbody.tn-nota')).length,primare_fereastra:primare.length,
  principale_observate:primare.map(n=>({text:n.innerText.trim(),pe_rand:!!n.closest('tbody.tn-nota'),
    in_viewport:inFereastra(n)}))};
}"""

def pixeli_png(cale):
    """Decodează PNG-urile RGB/RGBA de opt biți ale Chromium, fără dependențe externe."""
    import struct
    import zlib
    with open(cale, "rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Semnătură PNG invalidă")
        comprimat = bytearray()
        antet = None
        while True:
            marime, bloc = struct.unpack(">I4s", f.read(8))
            corp = f.read(marime)
            if len(corp) != marime or f.read(4) != struct.pack(">I", zlib.crc32(bloc + corp)):
                raise ValueError("PNG trunchiat sau CRC invalid")
            if bloc == b"IHDR":
                antet = struct.unpack(">IIBBBBB", corp)
            elif bloc == b"IDAT":
                comprimat.extend(corp)
            elif bloc == b"IEND":
                break
    if not antet or antet[2:] not in ((8, 2, 0, 0, 0), (8, 6, 0, 0, 0)):
        raise ValueError("Format de captură Chromium nesuportat")
    w, h, _, culoare, *_ = antet
    if (w, h) not in DIM:
        raise ValueError("Dimensiuni martor incorecte")
    canale = 3 if culoare == 2 else 4
    n = w * canale
    raw = zlib.decompress(comprimat)
    if len(raw) != h * (1 + n):
        raise ValueError("Lungime raster invalidă")
    sus = bytearray(n)
    rezultat = []
    for y in range(h):
        pos = y * (1 + n)
        filtru = raw[pos]
        linie = bytearray(raw[pos+1:pos+1+n])
        if filtru == 1:
            for x in range(canale, n):
                linie[x] = (linie[x] + linie[x-canale]) & 255
        elif filtru == 2:
            linie = bytearray((a+b) & 255 for a, b in zip(linie, sus))
        elif filtru in (3, 4):
            for x in range(n):
                a = linie[x-canale] if x >= canale else 0
                b = sus[x]
                c = sus[x-canale] if x >= canale else 0
                if filtru == 3:
                    pred = (a+b)//2
                else:
                    p = a+b-c
                    pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                    pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                linie[x] = (linie[x] + pred) & 255
        elif filtru != 0:
            raise ValueError("Filtru PNG invalid")
        rezultat.append(linie)
        sus = linie
    return w, h, canale, rezultat


def martor_luna(dosar, dim, zone):
    """Numără pixeli ai textului care dispar și reapar exact în cele două zone."""
    size = "%dx%d" % tuple(dim)
    cadre = [pixeli_png(dosar / (n + size + ".png")) for n in ("e.4_", "e.4_text_ascuns_", "e.4_text_restabilit_")]
    if any(c[:2] != tuple(dim) or c[2] != cadre[0][2] for c in cadre):
        raise ValueError("Cadre incompatibile")
    if set(zone) != {"eticheta", "valoare"}:
        raise ValueError("Zonele pentru e.4 sunt incomplete")
    w, h, nc, _ = cadre[0]
    def dreptunghi(z):
        rect = zone[z]
        if len(rect) != 4 or any(type(n) is not int for n in rect):
            raise ValueError("Dreptunghi invalid")
        x, y, dx, dy = rect
        if dx < 2 or dy < 2 or not (0 <= x <= w-dx and 0 <= y <= h-dy):
            raise ValueError("Textul iese din captură")
        return x, y, dx, dy
    recturi = [dreptunghi(z) for z in ("eticheta","valoare")]
    a,b = recturi
    if min(a[0]+a[2],b[0]+b[2])>max(a[0],b[0]) and min(a[1]+a[3],b[1]+b[3])>max(a[1],b[1]):
        raise ValueError("Cele două zone se suprapun")
    rezultat = {}
    for nume, (x,y,dx,dy) in zip(("eticheta","valoare"),recturi):
        nr = 0
        for sy in range(y,y+dy):
            normal, ascuns, restabilit = [c[3][sy] for c in cadre]
            for i in range(x*nc,(x+dx)*nc,nc):
                if normal[i:i+3] == restabilit[i:i+3] and any(abs(normal[i+k]-ascuns[i+k]) >= 24 for k in range(3)):
                    nr += 1
        rezultat[nume] = nr
    return rezultat


def fotografiaza_luna(pg, dosar, size, dim, eticheta, valoare):
    """Păstrează imaginea originală. Numai culoarea celor două texte se schimbă în martor."""
    rect = """el => {
      const r=document.createRange(); r.selectNodeContents(el);
      const b=el.tagName==='SELECT' ? el.getBoundingClientRect() : r.getBoundingClientRect();
      return [Math.floor(b.left),Math.floor(b.top),Math.ceil(b.right)-Math.floor(b.left),Math.ceil(b.bottom)-Math.floor(b.top)];
    }"""
    zone = {k: el.evaluate(rect) for k, el in (("eticheta",eticheta),("valoare",valoare))}
    def cadru(prefix):
        return pg.screenshot(path=str(dosar/(prefix+size+".png")), animations="disabled", caret="hide", scale="css")
    original = cadru("e.4_")
    if dim[0] == 1366:
        (dosar/"e.4.png").write_bytes(original)
    selector = '[data-q7-text-martor]'
    try:
        for el in (eticheta, valoare):
            el.evaluate("el=>el.setAttribute('data-q7-text-martor','')")
        stil = pg.add_style_tag(content=f"{selector}, {selector} *, {selector}::after {{color:transparent!important; -webkit-text-fill-color:transparent!important; text-shadow:none!important;}}")
        try:
            cadru("e.4_text_ascuns_")
        finally:
            stil.evaluate("el=>el.remove()")
    finally:
        for el in (eticheta, valoare):
            el.evaluate("el=>el.removeAttribute('data-q7-text-martor')")
    cadru("e.4_text_restabilit_")
    return zone, martor_luna(dosar, dim, zone)


def card_cabinet(pg, selector):
    card = pg.locator(selector)
    card.wait_for(state="attached")
    if not card.is_visible():
        grup = card.locator("xpath=ancestor::*[@id][@hidden]").last
        if grup.count():
            pg.locator('button[aria-controls="' + grup.get_attribute("id") + '"]').click()
    card.wait_for(state="visible")
    return card

def test_fundatie_17_5_Q9(browser, capsys):
    from conftest import BAZA, CAPTURI, Ecran, sesiune
    from core.ceas_proba import MOMENT_REF
    u = urlsplit(BAZA)
    assert (u.scheme,u.hostname,u.port) in (("http","localhost",8019),("http","127.0.0.1",8019))
    out = Path(CAPTURI)/"17_5_Q9"
    out.mkdir(parents=True,exist_ok=True)
    data, erori, masuri = {}, {}, {}
    try:
        for w,h in DIM:
            size = f"{w}x{h}"
            ctx = browser.new_context(viewport={"width":w,"height":h})
            try:
                ctx.clock.set_fixed_time(MOMENT_REF)
                ctx.add_init_script(sesiune("dovada.71507@sesiuneab.test"))
                pg = ctx.new_page()
                ecran = Ecran(pg,"q7")
                ecran.acasa()
                card = card_cabinet(pg, CARD)
                titlu = card.locator(".cab-card-titlu").inner_text().strip()
                with pg.expect_response(lambda r: urlsplit(r.url).path == "/coada" and r.request.method == "GET") as apel:
                    card.click()
                raspuns = apel.value
                if not raspuns.ok:
                    raise ValueError("GET /coada a eșuat")
                elemente = raspuns.json()["coada"]
                numara_coada(elemente)
                top = pg.locator(TOP)
                top.locator("#val-ciorne tbody.tn-nota[data-tn]").first.wait_for(state="visible")
                obs = top.evaluate(MASOARA)
                obs["titlu_card"] = titlu
                obs["elemente_coada"] = [{k: el[k] for k in ("fel", "stare", "membri_ids") if k in el} for el in elemente]
                data[size] = obs
                def captura(*ids):
                    for ident in ids:
                        pg.screenshot(path=str(out/f"{ident}_{size}.png"))
                        if w==1366:
                            (out/f"{ident}.png").write_bytes((out/f"{ident}_{size}.png").read_bytes())
                captura("e.1")
                obs["validare_actionabila"] = False
                if obs["valideaza"]:
                    from playwright.sync_api import TimeoutError as TimeoutPlaywright
                    activ = top.locator("#val-ciorne tbody.tn-nota button:not(:disabled):not([aria-disabled='true'])").filter(
                        has_text=re.compile(r"^\s*Validează\s*$")).first
                    try:
                        activ.click(trial=True, timeout=3000)
                        obs["validare_actionabila"] = True
                    except TimeoutPlaywright:
                        pass
                captura("e.2")
                ecran.firma("F1 Comert Stoc")
                pg.locator("#fa-casa").click()
                top.locator("#c-toggle").click()
                btn = top.locator("#c-adauga")
                obs["motiv_inainte"] = btn.get_attribute("data-motiv-inactiv") or ""
                tip = top.locator("#c-cat")
                buton_tip = top.locator('#c-l-cat button[data-valoare="plata_furnizor"]')
                if buton_tip.is_visible():
                    buton_tip.click()
                else:
                    tip.select_option("plata_furnizor")
                # Permite redesenarea barei după evenimentul change, fără a aștepta verdictul dorit.
                pg.evaluate("() => new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok)))")
                motiv = top.locator(".fj-motiv:visible")
                obs["motiv_vizibil"] = " ".join(motiv.all_inner_texts()).strip()
                obs.update(tip_dupa=tip.input_value(),suma_input=top.locator("#c-suma").input_value(),
                           motiv_dupa=btn.get_attribute("data-motiv-inactiv") or "")
                captura("e.3")
                ecran.acasa()
                card_cabinet(pg, "button.cab-card:has([data-cheie='control'])").click()
                rand = top.locator("#cf-lista tbody tr").filter(has_text="F2 Profit Amortizare")
                rand.first.wait_for(state="visible")
                if rand.count()!=1:
                    raise ValueError("Identitatea firmei din Control fiscal este ambiguă")
                with pg.expect_response(lambda r: re.fullmatch(r"/control-fiscal/\d+",urlsplit(r.url).path) and r.request.method=="GET") as rr:
                    rand.click()
                if not rr.value.ok:
                    raise ValueError("Control fiscal fără răspuns valid")
                sursa = rr.value.json()
                sel = top.locator("#cf-luna-comparata")
                sel.wait_for(state="attached")
                obs.update(preluare=sursa["luna_preluare"],luni_sursa=[f'{m["an"]}-{m["luna"]}' for m in sursa["luni_comparabile"]],
                           luni_ui=sel.locator("option").evaluate_all("opts=>opts.map(x=>x.value).filter(Boolean)"))
                cutie = sel.locator("xpath=parent::*")
                eticheta = cutie.locator('label[for="cf-luna-comparata"]')
                inchise = cutie.locator("xpath=ancestor::details[not(@open)]")
                for grup in inchise.all():
                    grup.locator(":scope > summary").click()
                # Controlul public înlocuiește select-ul sursă când lista e lungă.
                buton_lista = cutie.locator(".ds-lista-titlu:visible")
                grup_butoane = cutie.locator(".alegere-butoane:visible")
                n_lista, n_grup = buton_lista.count(), grup_butoane.count()
                if n_lista + n_grup > 1:
                    raise ValueError("Mai multe reprezentări publice ale aceluiași selector")
                if n_lista:
                    control = buton_lista
                    valoare = control.locator(".ds-lista-ales")
                elif n_grup:
                    control = grup_butoane.locator('button[role="radio"][aria-checked="true"]')
                    valoare = control
                else:
                    if sel.get_attribute("aria-hidden") == "true" or not sel.is_enabled():
                        raise ValueError("Select sursă ascuns sau inactiv, fără control public")
                    control = sel
                    valoare = sel
                if control.count() != 1 or valoare.count() != 1:
                    raise ValueError("Controlul public de lună nu este unic")
                control.wait_for(state="visible")
                control.evaluate("el=>el.scrollIntoView({block:'center', inline:'nearest', behavior:'instant'})")
                buton_lista = cutie.locator(".ds-lista-titlu:visible")
                if buton_lista.count():
                    if buton_lista.get_attribute("aria-expanded") == "false":
                        buton_lista.click()
                    nume_ui = cutie.locator('[role="option"]:not(.ds-lista-inactiv) .ds-lista-nume').all_inner_texts()
                    optiuni = sel.locator("option").evaluate_all(
                        "opts=>opts.filter(x=>x.value).map(x=>[(x.dataset.nume || x.textContent).trim(),x.value])")
                    if not nume_ui or buton_lista.get_attribute("aria-expanded") != "true":
                        raise ValueError("Lista de luni nu s-a deschis")
                    dupa_nume = dict(optiuni)
                    if len(dupa_nume) != len(optiuni) or any(n.strip() not in dupa_nume for n in nume_ui):
                        raise ValueError("Lunile din control nu se identifică univoc")
                    obs["luni_ui"] = [dupa_nume[n.strip()] for n in nume_ui]
                    control.evaluate("el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
                obs["eticheta_luni"] = eticheta.inner_text().strip().rstrip(" *")
                if not buton_lista.count() and grup_butoane.count():
                    obs["luni_ui"] = grup_butoane.locator('button[role="radio"]:not(:disabled)').evaluate_all(
                        "els=>els.map(el=>el.dataset.valoare)")
                if not buton_lista.count() and not grup_butoane.count():
                    obs["luni_ui"] = sel.locator("option:not(:disabled)").evaluate_all(
                        "opts=>opts.map(x=>x.value).filter(Boolean)")
                obs["valoare_selectata"] = sel.input_value()
                if buton_lista.count() or grup_butoane.count():
                    obs["valoare_afisata"] = valoare.inner_text().strip()
                else:
                    obs["valoare_afisata"] = sel.locator("option:checked").inner_text().strip()
                obs["zone_text"], obs["pixeli_text"] = fotografiaza_luna(pg, out, size, [w,h], eticheta, valoare)
                obs["control_luni_in_viewport"] = all(n >= 8 for n in obs["pixeli_text"].values())
            except Exception as exc:
                erori[size] = repr(exc)
            finally:
                ctx.close()
        campuri = {
            "e.1": ("titluri_sectiuni", "primare_rand", "primare_fereastra", "principale_observate"),
            "e.2": ("titluri_sectiuni", "valideaza", "iduri", "validare_actionabila"),
            "e.3": ("tip_dupa", "suma_input", "motiv_inainte", "motiv_dupa", "motiv_vizibil"),
            "e.4": ("preluare", "luni_ui", "luni_sursa", "eticheta_luni", "valoare_afisata", "valoare_selectata", "zone_text", "pixeli_text", "control_luni_in_viewport"),
        }
        diagnostic = {}
        for i in IDS:
            masuri[i] = {}
            diagnostic[i] = {}
            for w,h in DIM:
                z = f"{w}x{h}"
                try:
                    bloc = {k: data[z][k] for k in ("dim","titlu_card","elemente_coada","randuri",*campuri[i])}
                    masuri[i][z] = bloc
                    # Valoarea locală este informativă atunci când alt martor nu se poate judeca.
                    diagnostic[i][z] = pe_latime(i, bloc, w, h)
                except (KeyError, ValueError, TypeError) as exc:
                    diagnostic[i][z] = {"neexecutat": str(exc)}
                    erori[i+" "+z] = repr(exc)
        (out/"diagnostic.json").write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2))
        if not erori:
            rezultate = {i:verdict(i, masuri[i]) for i in IDS}
    except Exception as exc:
        erori["parcurs"] = repr(exc)
    finally:
        for n,obj in (("masuri",masuri),("erori",erori),("partiale",data if erori else {})):
            (out/f"{n}.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2))
    assert not erori, f"Q7_NEEXECUTAT {erori}"
    with capsys.disabled():
        for i,v in rezultate.items():
            print(f"VERDICT {i} {'trece' if v else 'pica'}",flush=True)
    assert all(rezultate.values()), f"Q7_FUNDATIE {rezultate}"
