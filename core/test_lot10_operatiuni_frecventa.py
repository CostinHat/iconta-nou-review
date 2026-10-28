# -*- coding: utf-8 -*-
"""Pct.9 al comenzii Costin 20.10.2026 (verbatim): „Direcție (din 428 și 429): treci prin toate Operațiunile speciale și separă-le pe
cele lunare sau recurente (TVA la încasare, valută, avansuri și altele) de cele rare (lichidare, reevaluare imobilizări etc.). Pentru
cele lunare, aplicația propune nota din datele firmei; formularul manual rămâne pentru cele rare. Raportează lista, cu ce ai făcut pentru
fiecare.”

CE FACE IMPOSIBIL: o operațiune din `REGISTRU` fără frecvență; o lunară care nu spune nici unde o propune aplicația, nici de ce n-o poate
propune încă (fără date în aplicație, nu se inventează); ecranul care nu mai separă lunarele de cele rare. N/A temei fiscal — tooling UI."""
# ecranul se citește din ARBORELE SINTACTIC (acorn): obiectele din `REGISTRU` cu proprietățile lor, apelurile cu argumentele lor — nu
# „șirul apare în fișier” (core/test_garzi_pe_text.py). Uneltele sunt cele din test_lot10b_facturi.py (refolosite, nu dublate).
from core.arbore_js import arbore_js, elemente_html, functia, noduri

ARB, COD = arbore_js("operatiuni_ecran.js")


def _declarat(nume):
    d = [x for x in noduri(ARB, "VariableDeclarator") if x["id"].get("name") == nume]
    assert len(d) == 1 and d[0]["init"]["type"] == "ArrayExpression", (nume, len(d))
    return d[0]["init"]["elements"]


def _intrari():
    """{cheie: {frecventa, propune, faraPropunere}} — din obiectul fiecărei intrări din `REGISTRU` (proprietățile lui, cu valoarea șir)."""
    out = {}
    for o in _declarat("REGISTRU"):
        p = {COD(x["key"]): x["value"] for x in o["properties"]}
        sir = {k: v["value"] for k, v in p.items() if v["type"] == "Literal" and isinstance(v["value"], str) and v["value"].strip()}
        out[sir["cheie"]] = {"frecventa": sir.get("frecventa"), "propune": sir.get("propune") is not None,
                                 "faraPropunere": sir.get("faraPropunere") is not None}
    return out


def test_toate_cele_32_au_frecventa():
    i = _intrari()
    # [lotul 11, 429] 34 -> 33: „Reevaluare lunară solduri valută” a ieșit — reevaluarea are un singur formular, în Închidere lună
    # [lotul 11, 450 / pct.23] 33 -> 32: „Achiziție de la neînregistrat” a ieșit — borderoul are ecranul lui, în Stocuri (borderou_ecran.js)
    assert len(i) == 32, sorted(i)
    assert {k for k, v in i.items() if v["frecventa"] not in ("lunar", "rar")} == set()


def test_exemplele_comenzii_sunt_unde_le_pune_comanda():
    i = _intrari()
    assert all(i[k]["frecventa"] == "lunar" for k in ("tva_incasare", "decont_valuta", "avans"))       # „TVA la încasare, valută, avansuri”
    assert all(i[k]["frecventa"] == "rar" for k in ("lichidare", "reevaluare"))                         # „lichidare, reevaluare imobilizări”


def test_fiecare_lunara_spune_unde_o_propune_aplicatia_sau_de_ce_nu_poate():
    i = _intrari()
    rele = {k for k, v in i.items() if v["frecventa"] == "lunar" and v["propune"] == v["faraPropunere"]}
    assert rele == set(), rele
    assert {k for k, v in i.items() if v["frecventa"] == "rar" and (v["propune"] or v["faraPropunere"])} == set()
    # cele propuse din alt ecran (verificate la sursă: T — bancă / casă / compensare; V — reevaluarea la închiderea lunii; facturile de
    # avans și casa; contarea facturii cu taxare inversă; asociații din Date firmă)
    # [lotul 11, 429] reevaluarea în valută nu mai are formular aici: se propune și se generează numai din Închidere lună
    # [lotul 13, 528] subvenția pentru investiții: reluarea lunară 4751 = 7584 o generează amortizarea lunii (`uc_tenants._reluare_subventii`,
    # chemată din generarea amortizării)
    assert {k for k, v in i.items() if v["propune"]} == {"tva_incasare", "avans", "taxare_inversa", "asociati", "subventie"}


def test_ecranul_separa_lunarele_de_cele_rare():
    # grupurile ecranului, în ordine: [frecvența, titlul]
    assert [[e["value"] for e in g["elements"][:2]] for g in _declarat("GRUPURI")] == [["lunar", "Lunare și recurente"], ["rar", "Rare"]]
    fn = functia(ARB, "ecranOperatiuni")
    # fiecare grup (`<section data-frecventa>`) arată numai operațiunile frecvenței lui: condițiile filtrelor pe `REGISTRU`, exact
    filtre = [COD(c["arguments"][0]["body"]) for c in noduri(fn, "CallExpression") if COD(c["callee"]) in ("REGISTRU.filter", "REGISTRU.some")]
    # [lotul 14, 687] notele „se propune automat” stau în cardul ferestrei (`CU_PROPUNERE`, filtrul `o.propune`, la nivel de modul)
    assert filtre == ["o.cat === cat && o.frecventa === frecventa"] * 2 + ["permis(actiuneOp(o))"], filtre   # ultimul: lista goală explicată
    # [lotul 14, 687] grupul are și rolul de panou de filă și atributul `hidden` condiționat: se compară numai ce definește grupul
    assert [{k: v for k, v in a.items() if k in ("class", "data-frecventa", "data-propune")} for _t, a in elemente_html(fn)
            if a.get("class") in ("op-grup", "ecran-nota op-propune")] == [
        {"class": "op-grup", "data-frecventa": "\x00"}, {"class": "ecran-nota op-propune", "data-propune": "\x00"}]
    # nota lunarei: unde o propune aplicația (`o.propune`), după titlu
    nota = [([q["value"]["cooked"] for q in t["quasis"]], [COD(e) for e in t["expressions"]]) for t in noduri(fn, "TemplateLiteral")
            if [COD(e) for e in t["expressions"]][-1:] == ["esc(o.propune)"]]
    assert nota == [(['<p class="ecran-nota op-propune" data-propune="', '"><b>', "</b> — se propune automat: ", "</p>"],
                     ["o.cheie", "esc(o.titlu)", "esc(o.propune)"])], nota
