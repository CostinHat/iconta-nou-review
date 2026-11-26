"""F018 — ierarhia vizibilă a adăugării în cele trei registre ale firmei F1."""

import json
import math
from pathlib import Path


DIM = ((1366, 768), (603, 590))
IDS = ("e.1", "e.2", "e.3")
ECRANE = (
    ("parteneri", "#fa-parteneri", "#pt-nou", "+ Fișă de partener"),
    ("clienti", "#fa-clienti", "#cl-nou", "+ Client nou"),
    ("furnizori", "#fa-furnizori", "#fz-nou", "+ Furnizor nou"),
)


def contract_fereastra(item, nume, baza):
    primare = item["principale"]
    pdf = item["pdf"]
    if not isinstance(primare, list) or not isinstance(pdf, list):
        raise ValueError("Inventar incomplet al acțiunilor")
    for actiune in primare:
        if not isinstance(actiune["text"], str) or not actiune["text"].strip():
            raise ValueError("Acțiune principală fără etichetă")
        for cheie in ("adaugare", "in_bara", "clasa_primara"):
            if type(actiune[cheie]) is not bool:
                raise ValueError("Starea acțiunii principale este incompletă")
    for buton in pdf:
        if any(type(buton[k]) is not bool for k in ("primar", "secundar", "activ")):
            raise ValueError("Starea acțiunii PDF este incompletă")
    pdf_principal = baza and nume == "parteneri"
    asteptat = {"text": "Descarcă PDF" if pdf_principal else item["text"],
                "adaugare": not pdf_principal, "in_bara": True, "clasa_primara": True}
    rol = "buton-secundar" if pdf_principal else "buton-primar"
    pdf_corect = nume != "parteneri" or pdf == [
        {"primar": pdf_principal, "secundar": not pdf_principal, "activ": True}
    ]
    return primare == [asteptat] and rol in item["clase"] and pdf_corect


def valideaza(date, dim):
    """Lipsa ecranului sau o citire parțială nu constituie roșul prezis."""
    if set(date) != {ecran[0] for ecran in ECRANE}:
        raise ValueError("Trei ecrane distincte obligatorii")
    controale = []
    for nume, _, selector, eticheta in ECRANE:
        item = date[nume]
        if item["viewport"] != list(dim) or item["selector"] != selector:
            raise ValueError("Rezoluție sau selector străin ecranului")
        if item["hover"] is not False:
            raise ValueError("Controlul trebuie măsurat în repaus")
        suprafata = (item["latime"], item["inaltime"])
        if item["text"] != eticheta or not all(
            type(x) in (int, float) and math.isfinite(x) and x > 0 for x in suprafata
        ):
            raise ValueError("Controlul de adăugare nu este identificat pe ecran")
        if type(item["activ"]) is not bool or type(item["clicabil"]) is not bool:
            raise ValueError("Starea controlului este incompletă")
        clase = set(item["clase"])
        if len(clase.intersection({"buton-primar", "buton-secundar"})) != 1:
            raise ValueError("Ierarhia declarată de design este ambiguă")
        if not item["fundal"] or not item["culoare"]:
            raise ValueError("Lipsesc stilurile calculate")
        controale.append(item)
    ierarhii = {
        ("buton-primar" in item["clase"], item["fundal"], item["culoare"])
        for item in controale
    }
    return {
        "e.1": all(item["activ"] for item in controale),
        "e.2": all(contract_fereastra(date[n], n, False) for n, *_ in ECRANE) and len(ierarhii) == 1,
        "e.3": all(item["clicabil"] for item in controale),
    }


def test_fundatie_17_5_Q12(browser, capsys):
    from conftest import BAZA, CAPTURI, Ecran, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import TOP, F1, firma, origine_proba

    origine_proba(BAZA)
    director = Path(CAPTURI) / "17_5_Q12"
    director.mkdir(parents=True, exist_ok=True)
    masuri = {i: {} for i in IDS}
    per_dim = []
    for dim in DIM:
        w, h = dim
        z = f"{w}x{h}"
        date = {}
        for indice, (nume, intrare, selector, _) in enumerate(ECRANE):
            ctx = browser.new_context(viewport={"width": w, "height": h})
            try:
                ctx.clock.set_fixed_time(MOMENT_REF)
                ctx.add_init_script(sesiune("dovada.71507@sesiuneab.test"))
                pg = ctx.new_page()
                Ecran(pg, "q12").acasa()
                firma(pg, F1, intrare)
                buton = pg.locator(TOP + selector)
                buton.wait_for(state="visible")
                buton.scroll_into_view_if_needed()
                neutru = buton.evaluate("""el => {
                    for (const y of [0, innerHeight-1]) for (const x of [0, innerWidth-1])
                        if (!el.contains(document.elementFromPoint(x,y))) return [x,y];
                    throw Error('Niciun punct neutru');
                }""")
                pg.mouse.move(*neutru)
                pg.evaluate("""() => new Promise((ok, rau) => {
                    const t = setTimeout(() => rau(Error('pagina nedesenata')), 1500);
                    requestAnimationFrame(() => requestAnimationFrame(() => {clearTimeout(t);ok()}));
                })""")
                date[nume] = buton.evaluate("""(el, selector) => {
                    const r = el.getBoundingClientRect(), css = getComputedStyle(el);
                    const punct = document.elementFromPoint(r.x+r.width/2, r.y+r.height/2);
                    const fereastra = el.closest(".fereastra-overlay:not(.fundal) .fereastra");
                    if (!fereastra) throw Error("Fereastra activă lipsește");
                    const vizibil = b => {
                        const s = getComputedStyle(b), r = b.getBoundingClientRect();
                        return s.visibility === "visible" && s.display !== "none" &&
                            r.width > 0 && r.height > 0 && !b.closest("[hidden], [inert]");
                    };
                    const butoane = [...fereastra.querySelectorAll("button")].filter(vizibil);
                    const principale = butoane.filter(b => b.matches(".buton-primar, .fj-principal"))
                        .map(b => ({text:b.innerText.trim(), adaugare:b === el,
                            in_bara:b.matches(".fj-butoane .fj-principal"),
                            clasa_primara:b.classList.contains("buton-primar")}));
                    const pdf = butoane.filter(b => b.innerText.trim() === "Descarcă PDF")
                        .map(b => ({primar:b.matches(".buton-primar, .fj-principal"),
                            secundar:b.classList.contains("buton-secundar"),
                            activ:!b.disabled && b.getAttribute("aria-disabled") !== "true"}));
                    return {principale, pdf, selector, viewport:[innerWidth,innerHeight], text:el.innerText.trim(),
                        clase:[...el.classList], hover:el.matches(':hover'), latime:r.width, inaltime:r.height,
                        activ:!el.disabled && el.getAttribute('aria-disabled') !== 'true',
                        clicabil:!!punct && el.contains(punct), fundal:css.backgroundColor,
                        culoare:css.color};
                }""", selector)
                img = pg.screenshot(path=str(director / f"{nume}_{z}.png"))
                aid = IDS[indice]
                (director / f"{aid}_{z}.png").write_bytes(img)
                if w == 1366:
                    (director / f"{aid}.png").write_bytes(img)
            finally:
                ctx.close()
        per_dim.append(valideaza(date, dim))
        for i in IDS:
            masuri[i][z] = date
    (director / "masuri.json").write_text(json.dumps(masuri, ensure_ascii=False))
    for nume in ("erori.json", "partiale.json"):
        (director / nume).write_text("{}")
    with capsys.disabled():
        for i in IDS:
            print("VERDICT", i, "trece" if all(x[i] for x in per_dim) else "pica", flush=True)
    assert all(all(x.values()) for x in per_dim), "Q12_F018_IERARHIE"
