"""
core/retete_import_api.py - import retete HoReCa (F150) per firma.
Format: un rand per ingredient - Reteta; Pret vanzare (fara TVA); Ingredient; Cantitate/portie.
Gruparea pe reteta o face importul. Ingredientele se potrivesc pe articolele existente
dupa denumire (exact, apoi continere); nepotrivirile se raporteaza si reteta se sare.
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
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def extrage(continut, nume_fisier=""):
    """Intoarce [{denumire, pret, linii:[{ingredient, cantitate}]}] grupat pe reteta."""
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
    grup = {}
    ordine = []
    for r in randuri[1:]:
        ret = _it.celula(r, i_ret)
        ing = _it.celula(r, i_ing)
        if not ret or not ing:
            continue
        cant = _numar(_it.valoare(r, i_cant)) if i_cant >= 0 else 0.0
        pret = _numar(_it.valoare(r, i_pret)) if i_pret >= 0 else 0.0
        if ret not in grup:
            grup[ret] = {"denumire": ret[:255], "pret": pret, "linii": []}
            ordine.append(ret)
        if pret > 0:
            grup[ret]["pret"] = pret
        grup[ret]["linii"].append({"ingredient": ing[:255], "cantitate": cant})
    return [grup[k] for k in ordine]


def potriveste(conn, schema, retete):
    """Potriveste ingredientele pe articole. Adauga articol_id sau motiv per linie
    + valid/motiv per reteta (toate liniile potrivite si cantitati > 0)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, denumire FROM {schema}.articole")
        arts = cur.fetchall()
    exact = {d.strip().lower(): i for i, d in arts}
    for ret in retete:
        motive = []
        for l in ret["linii"]:
            cheie = l["ingredient"].strip().lower()
            aid = exact.get(cheie)
            if aid is None:
                cand = [i for i, d in arts if cheie in d.strip().lower() or d.strip().lower() in cheie]
                aid = cand[0] if len(cand) == 1 else None
            l["articol_id"] = aid
            if aid is None:
                motive.append(f"ingredient negăsit: {l['ingredient']}")
            elif l["cantitate"] <= 0:
                motive.append(f"cantitate invalidă la {l['ingredient']}")
        ret["valid"] = not motive
        ret["motiv"] = "; ".join(motive) if motive else "ok"
    return retete


def rezumat(retete):
    ok = [r for r in retete if r.get("valid")]
    return {"total": len(retete), "valide": len(ok), "invalide": len(retete) - len(ok),
            "ingrediente": sum(len(r["linii"]) for r in retete)}


def importa(conn, schema, retete):
    """Creeaza retetele valide prin retete_api.salveaza. Existentele/invalidele se sar."""
    from core import retete_api
    create, sarite = 0, []
    with conn.cursor() as cur:
        for ret in retete:
            if not ret.get("valid"):
                if ret.get("fel"):
                    sarite.append(dict(ret))          # afirmatia vine gata de la potrivire
                elif not ret.get("denumire"):
                    sarite.append(respinge("rețetă", "o rețetă din fișier", "denumire_lipsa",
                                           ret.get("motiv", "denumire lipsă")))
                else:
                    sarite.append(respinge("rețetă", "rețeta „%s”" % ret["denumire"],
                                           "cantitate_pret_negativ",
                                           ret.get("motiv", "invalid"), denumire=ret["denumire"]))
                continue
            cur.execute(f"SELECT id FROM {schema}.retete WHERE lower(denumire)=lower(%s)", (ret["denumire"],))
            if cur.fetchone():
                sarite.append(respinge("rețetă", "rețeta „%s”" % ret["denumire"], "deja_exista",
                                       "există deja - nu s-a dublat", denumire=ret["denumire"]))
                continue
            retete_api.salveaza(conn, schema, {"denumire": ret["denumire"], "pret_fara_tva": ret.get("pret") or 0,
                "linii": [{"articol_id": l["articol_id"], "cantitate": l["cantitate"]} for l in ret["linii"]]})
            create += 1
    return {"create": create, "sarite": sarite}
