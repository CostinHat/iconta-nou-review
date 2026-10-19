"""
core/retete_import_api.py - import retete HoReCa (F150) per firma.
Format: un rand per ingredient - Reteta; Pret vanzare (fara TVA); Ingredient; Cantitate/portie.
Gruparea pe reteta o face importul. Ingredientele se potrivesc pe articolele existente
dupa denumire (exact, apoi continere — semnalata pe rand); nepotrivirile se resping si reteta se sare intreaga.
Idempotenta: reteta existenta (aceeasi denumire) se sare cu motiv.
"""
from __future__ import annotations


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Citirea fișierului și potrivirea coloanelor trec prin
# `core.import_tabel` (sursa unică: format, codare Windows-1250 recunoscută sau refuzată, antet sub titluri, coloane pe cuvinte
# întregi, ambiguitate refuzată numit) — nu mai e o copie a lui `_gaseste_col` aici.
from core import import_tabel as _it

CAMPURI = {
    "reteta": ("denumire reteta", "reteta", "preparat", "produs finit"),
    "pret": ("pret vanzare", "pret*"),
    "ingredient": ("ingredient*", "articol*", "materie*"),
    "cantitate": ("cantitate*", "cant", "consum*"),
}


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def _numar_sau_none(v):
    """Numărul din celulă; None dacă celula NU e goală dar nu e un număr. Goală -> None la fel (spus separat, prin `*_brut` gol)."""
    if v is None or str(v).strip() == "":
        return None
    try:
        return _numar(v, strict=True)
    except ValueError:
        return None


def extrage(continut, nume_fisier=""):
    """Fiecare rând citit (un ingredient al unei rețete), cu valorile din fișier lângă cele interpretate:
    [{rand_fisier, reteta, pret, pret_brut, ingredient, cantitate, cantitate_brut}].

    [375, comanda Costin 8.2] Până azi rândul fără rețetă dispărea, aceeași rețetă cu două prețuri lua tacit ultimul, rețeta fără preț
    intra cu 0, iar gruparea pe rețetă se făcea înainte de orice verificare. Acum se citesc rândurile; verdictul e al lui
    `verifica_randuri`, iar gruparea (`grupeaza`) se face numai pe rândurile care intră."""
    randuri = _it.citeste(continut, nume_fisier)
    if not randuri or all(_it.rand_gol(r) for r in randuri):
        return []
    try:
        antet, start = _it.gaseste_antet(randuri, CAMPURI, obligatorii=("reteta", "ingredient", "cantitate"),
                                         nume_fisier=nume_fisier)
    except _it.FisierNecitit as e:
        if isinstance(e, _it.ColoaneAmbigue):
            raise
        raise ValueError("nu se găsesc coloanele Rețeta / Ingredient / Cantitate")
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=camp)
    i_ret = col("reteta")
    i_pret = col("pret")
    i_ing = col("ingredient", (i_ret,))
    i_cant = col("cantitate")
    randuri = randuri[start - 1:]
    out = []
    for nr, r in enumerate(randuri[1:], start=start + 1):
        if _it.rand_gol(r):
            continue
        out.append({"rand_fisier": nr, "reteta": _it.celula(r, i_ret)[:255],
                    "pret": _numar_sau_none(_it.valoare(r, i_pret)) if i_pret >= 0 else None, "pret_brut": _it.celula(r, i_pret),
                    "ingredient": _it.celula(r, i_ing)[:255],
                    "cantitate": _numar_sau_none(_it.valoare(r, i_cant)), "cantitate_brut": _it.celula(r, i_cant)})
    return out


def potriveste(conn, schema, randuri):
    """Potrivește ingredientul fiecărui rând pe articolele din stoc: întâi denumirea exactă, apoi o singură denumire care o conține
    (sau e conținută). Adaugă `articol_id`, `articol_denumire`, `articol_um` (UM-ul în care se citește cantitatea pe porție — 375) și
    `potrivire` ∈ exact / aproximativ / None. Potrivirea aproximativă se SPUNE pe rând (`semnale_randuri`)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, denumire, um FROM {schema}.articole")
        arts = cur.fetchall()
    exact = {d.strip().lower(): (i, d, um) for i, d, um in arts}
    for r in randuri:
        cheie = str(r.get("ingredient") or "").strip().lower()
        a, fel = exact.get(cheie), "exact"
        if a is None and cheie:
            cand = [(i, d, um) for i, d, um in arts if cheie in d.strip().lower() or d.strip().lower() in cheie]
            a, fel = (cand[0], "aproximativ") if len(cand) == 1 else (None, None)
        r["articol_id"], r["articol_denumire"], r["articol_um"] = (a[0], a[1], a[2] or "") if a else (None, "", "")
        r["potrivire"] = fel if a else None
    return randuri


def verifica_randuri(randuri):
    """PURĂ (după `potriveste`): respingerile [{rand, motiv, mesaj}]. O rețetă intră întreagă sau deloc: un rând respins scoate și celelalte
    rânduri ale rețetei lui (altfel s-ar salva o rețetă fără un ingredient)."""
    er = []
    preturi = {}
    for i, r in enumerate(randuri or [], start=2):
        ret = str(r.get("reteta") or "").strip()
        if ret and r.get("pret") is not None:
            preturi.setdefault(ret.lower(), {}).setdefault(float(r["pret"]), _it.nr_rand(r, i))
    rele = set()
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        ret = str(r.get("reteta") or "").strip()
        ing = str(r.get("ingredient") or "").strip()
        et = "rețeta „%s”" % ret if ret else "rândul fără rețetă"
        n0 = len(er)
        if not ret:
            er.append(respinge("rețetă", i, "denumire_lipsa", "rândul n-are numele rețetei (ingredientul «%s»)" % (ing or "—")))
        if not ing:
            er.append(respinge("rețetă", i, "ingredient_lipsa", "%s: rândul n-are ingredientul" % et))
        elif r.get("articol_id") is None:
            er.append(respinge("rețetă", i, "ingredient_negasit",
                               "%s: ingredientul «%s» nu e în articolele din stoc — importă întâi articolele (pasul „Articole și stoc "
                               "inițial”)" % (et, ing)))
        c = r.get("cantitate")
        if c is None:
            er.append(respinge("rețetă", i, "cantitate_invalida", "%s: cantitatea pe porție «%s» nu e un număr"
                               % (et, r.get("cantitate_brut") or "")) if str(r.get("cantitate_brut") or "").strip() else
                      respinge("rețetă", i, "cantitate_invalida", "%s: cantitatea pe porție lipsește (%s)" % (et, ing or "—")))
        elif c == 0:
            er.append(respinge("rețetă", i, "cantitate_invalida", "%s: cantitatea pe porție e 0 (%s)" % (et, ing or "—")))
        elif c < 0:
            er.append(respinge("rețetă", i, "cantitate_invalida", "%s: cantitatea pe porție e negativă (%s)" % (et, ing or "—")))
        if ret:
            p = preturi.get(ret.lower(), {})
            if not p:
                if str(r.get("pret_brut") or "").strip():
                    er.append(respinge("rețetă", i, "pret_invalid", "%s: prețul «%s» nu e un număr" % (et, r.get("pret_brut"))))
                else:
                    er.append(respinge("rețetă", i, "pret_lipsa", "%s: prețul de vânzare lipsește — nu intră cu 0 lei" % et))
            elif len(p) > 1:
                er.append(respinge("rețetă", i, "pret_contradictoriu", "%s are prețuri diferite în fișier: %s — lasă unul singur" % (
                    et, ", ".join("%s (rândul %s)" % (("%g" % k).replace(".", ","), v) for k, v in sorted(p.items())))))
            elif r.get("pret") is not None and float(r["pret"]) <= 0:
                er.append(respinge("rețetă", i, "pret_lipsa", "%s: prețul de vânzare e %s — trebuie să fie mai mare ca 0" % (et, r["pret"])))
        if len(er) > n0 and ret:
            rele.add(ret.lower())
    # o rețetă intră întreagă: celelalte rânduri ale unei rețete cu un rând respins se spun și ele
    deja = {e["rand"] for e in er}
    for i, r in enumerate(randuri or [], start=2):
        n = _it.nr_rand(r, i)
        ret = str(r.get("reteta") or "").strip()
        if ret.lower() in rele and n not in deja:
            er.append(respinge("rețetă", n, "reteta_incompleta",
                               "rețeta „%s” nu intră: alt rând al ei e respins (corectează-l și reîncarcă fișierul)" % ret))
    return er


def semnale_randuri(randuri):
    """PURĂ: [375] ingredientul potrivit APROXIMATIV pe un articol (denumirea nu e identică) se spune pe rând."""
    return [semnaleaza("rețetă", _it.nr_rand(r, i), "ingredient_aproximativ",
                       "ingredientul «%s» e potrivit pe articolul «%s» (denumirea nu e identică) — verifică" % (
                           r.get("ingredient"), r.get("articol_denumire")))
            for i, r in enumerate(randuri or [], start=2) if r.get("potrivire") == "aproximativ"]


def eticheteaza(randuri):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând (ok / semnalat / respins), cu motivele."""
    er, sem = verifica_randuri(randuri), semnale_randuri(randuri)
    for i, r in enumerate(randuri, start=2):
        n = _it.nr_rand(r, i)
        resp = [e["mesaj"] for e in er if e.get("rand") == n]
        obs = [e["mesaj"] for e in sem if e.get("rand") == n]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def grupeaza(randuri, respinse):
    """Rețetele formate din rândurile care intră: [{denumire, pret, linii:[{articol_id, ingredient, cantitate}]}], în ordinea din fișier."""
    afara = {e["rand"] for e in respinse}
    grup, ordine = {}, []
    for i, r in enumerate(randuri or [], start=2):
        if _it.nr_rand(r, i) in afara:
            continue
        k = str(r["reteta"]).strip()
        if k.lower() not in grup:
            grup[k.lower()] = {"denumire": k, "pret": r["pret"], "linii": []}
            ordine.append(k.lower())
        grup[k.lower()]["linii"].append({"articol_id": r["articol_id"], "ingredient": r["ingredient"], "cantitate": r["cantitate"]})
    return [grup[k] for k in ordine]


def rezumat(randuri):
    er = verifica_randuri(randuri)
    retete = grupeaza(randuri, er)
    toate = {str(r.get("reteta") or "").strip().lower() for r in randuri if str(r.get("reteta") or "").strip()}
    return {"total": len(toate), "valide": len(retete), "invalide": len(toate) - len(retete),
            "ingrediente": sum(len(x["linii"]) for x in retete)}


def importa(conn, schema, randuri):
    """Creează rețetele formate din rândurile bune (prin retete_api.salveaza). Potrivirea și verificarea se refac AICI (nu se crede
    `valid` / `articol_id` venit din cererea ecranului); existentele se sar cu motiv."""
    from core import retete_api
    if not randuri:
        raise ValueError("nu ai trimis niciun rând — un import fără rânduri n-are ce adăuga în rețetar.")
    potriveste(conn, schema, randuri)
    er = verifica_randuri(randuri)
    retete = grupeaza(randuri, er)
    if not retete:
        raise ValueError("nicio rețetă nu poate intra: %s" % "; ".join("rândul %s: %s" % (e["rand"], e["mesaj"]) for e in er[:6]))
    create, sarite = 0, list(er)
    with conn.cursor() as cur:
        for ret in retete:
            cur.execute(f"SELECT id FROM {schema}.retete WHERE lower(denumire)=lower(%s)", (ret["denumire"],))
            if cur.fetchone():
                sarite.append(respinge("rețetă", "rețeta „%s”" % ret["denumire"], "deja_exista",
                                       "există deja - nu s-a dublat", denumire=ret["denumire"]))
                continue
            retete_api.salveaza(conn, schema, {"denumire": ret["denumire"], "pret_fara_tva": ret["pret"],
                "linii": [{"articol_id": l["articol_id"], "cantitate": l["cantitate"]} for l in ret["linii"]]})
            create += 1
    return {"create": create, "sarite": sarite, "respinse": er}
