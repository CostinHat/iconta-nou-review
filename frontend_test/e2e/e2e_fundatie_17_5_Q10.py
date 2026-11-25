"""F018. Probă de citire pe 8019, pe datele firmei din snapshot."""

import json
from pathlib import Path
import unicodedata

DIM = ((1366, 768), (603, 590))
IDS = ("e.1", "e.2", "e.3")


CAMPURI = {
    "e.1": ("latime", "registru", "initial"),
    "e.2": ("cautari", "ales", "vizibil", "operabil", "filtre", "restabilit"),
    "e.3": ("butoane", "adaugare", "activ"),
}


def impacheteaza(tot):
    return {i: {z: {k: m[k] for k in CAMPURI[i]} for z, m in tot.items()} for i in IDS}


def normal(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(c)
    )


def valideaza(m):
    registru = m["registru"]
    chei = [str(p["cheie"]) for p in registru]
    if len(chei) < 2 or len(set(chei)) != len(chei) or any(not k for k in chei):
        raise ValueError("Registrul independent nu identifică partenerii")
    if m["latime"] not in (1366, 603) or m["cautari"] != 1 or m["butoane"] != 1:
        raise ValueError("Fixtura Parteneri este incompletă")
    initial = sorted(chei) == sorted(m["initial"])
    filtrat = m["vizibil"] is True and m["operabil"] is True
    for termen, ids in m["filtre"].items():
        expected = sorted(
            str(p["cheie"])
            for p in registru
            if normal(termen) in normal(str(p["nume"]))
            or normal(termen) in normal(str(p["cui"] or ""))
        )
        filtrat = filtrat and 0 < len(expected) < len(chei) and sorted(ids) == expected
    ales = m["ales"]
    if not any(
        str(p["cheie"]) == ales["cheie"]
        and p["nume"] == ales["nume"]
        and p["cui"] == ales["cui"]
        for p in registru
    ):
        raise ValueError("Martorul filtrării lipsește din răspuns")
    termeni = {str(ales["nume"]), str(ales["cui"])}
    filtrat = (
        filtrat
        and len(termeni) == 2
        and set(m["filtre"]) == termeni
        and sorted(m["restabilit"]) == sorted(chei)
    )
    return dict(
        zip(
            IDS,
            (
                initial,
                filtrat,
                m["adaugare"] == "+ Fișă de partener" and m["activ"] is True,
            ),
        )
    )


def test_fundatie_17_5_Q10(browser, capsys):
    from conftest import BAZA, CAPTURI, Ecran, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import F1, TOP, firma, origine_proba, stabil
    from urllib.parse import urlsplit

    origine_proba(BAZA)
    director = Path(CAPTURI) / "17_5_Q10"
    director.mkdir(parents=True, exist_ok=True)
    tot = {}
    for w, h in DIM:
        z = f"{w}x{h}"
        ctx = browser.new_context(viewport={"width": w, "height": h})
        try:
            ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(sesiune("dovada.71507@sesiuneab.test"))
            pg = ctx.new_page()
            Ecran(pg, "q10").acasa()
            with pg.expect_response(
                lambda r: (
                    urlsplit(r.url).path == "/tenants/105779/parteneri-firma"
                    and r.request.method == "GET"
                )
            ) as rasp:
                firma(pg, F1, "#fa-parteneri")
            assert rasp.value.ok
            registru = [
                {k: p.get(k) for k in ("cheie", "nume", "cui")}
                for p in rasp.value.json()["parteneri"]
            ]
            tinta = next(
                p
                for p in registru
                if p["cui"]
                and p["nume"]
                and all(
                    any(
                        normal(str(p[k])) not in normal(str(q["nume"]))
                        and normal(str(p[k])) not in normal(str(q["cui"] or ""))
                        for q in registru
                    )
                    for k in ("nume", "cui")
                )
            )
            top = pg.locator(TOP.strip())
            randuri = top.locator("#pt-tabel tbody tr[data-cheie]")
            randuri.first.wait_for(state="attached")
            stabil(pg)

            def chei():
                return randuri.evaluate_all(
                    "rows => rows.filter(r=>!r.hidden && r.getClientRects().length).map(r=>r.dataset.cheie)"
                )

            def captura(nume):
                img = pg.screenshot(path=str(director / f"{nume}_{z}.png"))
                if w == 1366 and nume in IDS:
                    (director / f"{nume}.png").write_bytes(img)

            c = top.locator("#pt-cauta")
            ad = top.locator("#pt-nou")
            m = {
                "latime": w,
                "registru": registru,
                "initial": chei(),
                "cautari": c.count(),
                "butoane": ad.count(),
                "adaugare": ad.inner_text().strip(),
                "activ": ad.is_enabled(),
                "ales": tinta,
                "vizibil": c.is_visible(),
                "operabil": False,
                "filtre": {},
                "restabilit": [],
            }
            captura("e.1")
            if m["vizibil"]:
                c.scroll_into_view_if_needed()
                m["operabil"] = (
                    c.evaluate("""n=>{const r=n.getBoundingClientRect();return !n.disabled && !n.readOnly &&
                    n.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}""")
                )
            if m["operabil"]:
                c.click()
                for k in ("nume", "cui"):
                    termen = str(tinta[k])
                    c.fill(termen)
                    stabil(pg)
                    m["filtre"][termen] = chei()
                    captura("filtru_" + k)
                c.fill("")
                stabil(pg)
                m["restabilit"] = chei()
            captura("e.2")
            captura("e.3")
            tot[z] = m
        finally:
            ctx.close()
    (director / "masuri.json").write_text(
        json.dumps(impacheteaza(tot), ensure_ascii=False, indent=2)
    )
    (director / "erori.json").write_text("{}")
    (director / "partiale.json").write_text("{}")
    pe_rezolutie = [valideaza(m) for m in tot.values()]
    with capsys.disabled():
        for i in IDS:
            print(
                "VERDICT",
                i,
                "trece" if all(v[i] for v in pe_rezolutie) else "pica",
                flush=True,
            )
    assert all(all(v.values()) for v in pe_rezolutie), "Q10_F018"
