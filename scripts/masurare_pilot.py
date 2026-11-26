# -*- coding: utf-8 -*-
"""scripts/masurare_pilot.py — unealta de măsurare Pilot (17.5-C9, pct.5, decizia D5). Intrarea UNICĂ pentru grila unei funcții:
cod × criteriu × rezoluție, pe o versiune măsurată. O folosesc F501 și F502 fără a schimba algoritmul: funcția se identifică prin cod și prin
contractul ei de probă (inventarul), iar codurile noi nu intră în numitorul istoric de 45 (`--numitor`).

Pornește de la mecanismele existente: comparația unei observații cu așteptarea e `scripts/verifica_pas.py::compara_asertiune` (aceiași
operatori ca oracolul pașilor: egal / contine / nr_randuri / lipseste / interval_px / activ / text_contine …); citirea paginii vii e
`verifica_pas.observa_pagina` (cheile `dom:<selector>|<măsură>`, `json:…`, `pdf:…`), apelată de `masoara_celula` din parcursul de probă
(Playwright, pe 8019, numai prin lansatorii oficiali: scripts/e2e_poarta.py / rulare_8019.sh); validarea martorilor urmează regulile
„Pilot 17.5-Q9” (martor legat de commit, SHA-256 al fiecărui fișier, captura verificabilă, aceeași cheie o singură dată).

CHEIA celulei: (cod, criteriu, rezoluție) pe versiunea măsurată. Criteriile: Funcțional, Aspect, Design, Simplitate, Conformitate,
Stabilitate. Rezoluțiile: 1366x768 și 603x590. Un cod are exact 12 celule.

SUBCOMENZI
  valideaza  <inventar.tsv>                                     -> inventarul de probă e valid? (rc 0 / 2)
  judeca     <inventar.tsv> <dir_martori> <commit> <iesire.tsv> [--faza baza|candidat|servita] [--rezumat <json>]
                                                                -> grila celulelor (schema COLOANE_CELULA), rezumatul pe cod
  bilant     <celule_baza.tsv> <celule_retest.tsv> --numitor <coduri.txt> [--iesire <json>]
                                                                -> I0, I1, închise acum, redeschise, NET, cu celula, motivul și martorul
  importa-q12 <rezultate_17_5_Q12.tsv> <celule_Q12.tsv> <coduri.txt> <commit> <iesire.tsv>
                                                                -> adaptorul măsurării Q12 publicate (55 de celule) la schema uneltei;
                                                                   celelalte chei ale celor 45 de coduri ies «-» cu motivul lor
CODURI DE IEȘIRE: 0 = complet verde (toate celulele 1); 1 = inventar valid, cu celule 0 sau «-» (numite în ieșire); 2 = refuz (inventar
invalid, martor alterat, apel greșit).

INVENTARUL (TSV, un rând pe celulă): COLOANE_INVENTAR. MARTORUL unei celule: `<dir>/<cod>__<criteriu>__<rezolutie>.json`, cu
{cod, criteriu, rezolutie, commit, firma, rol, ruta, stare, document_perioada, gest, dimensiune, ecran_desenat, selector_gasit,
lipsa_confirmata, observat, captura: {cale, sha256}, consola_erori, motiv_neexecutat}; manifestul `<dir>/martori.sha256` (scris de
`masoara_celula`) leagă fiecare martor de SHA-ul lui; un martor schimbat după măsurare = refuz (rc 2).
"""
import csv
import hashlib
import json
import os
import sys

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)

CRITERII = ("Funcțional", "Aspect", "Design", "Simplitate", "Conformitate", "Stabilitate")
CRITERII_ISTORICE = CRITERII[:5]          # scorul istoric pe ecran: primele cinci; închiderea cere toate șase
REZOLUTII = ("1366x768", "603x590")
COLOANE_INVENTAR = ("cod", "criteriu", "rezolutie", "firma", "rol", "ruta", "stare", "document_perioada", "gest", "dimensiune",
                    "cheie", "operator", "asteptat")
COLOANE_CELULA = ("cod", "criteriu", "rezolutie", "versiune", "faza", "firma", "rol", "ruta", "stare", "document_perioada", "gest",
                  "dimensiune", "asteptat", "observat", "rezultat", "motiv", "martor", "martor_sha256", "captura", "captura_sha256")


class Refuz(Exception):
    """Inventar invalid sau martor alterat: nu există grilă judecabilă (rc 2)."""


def sha_fisier(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest()


def citeste_tsv(cale):
    with open(cale, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def scrie_tsv(cale, coloane, randuri):
    with open(cale, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=coloane, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in randuri:
            w.writerow(r)


def nume_martor(cod, criteriu, rezolutie):
    return "%s__%s__%s.json" % (cod, criteriu, rezolutie)


def valideaza_inventar(randuri):
    """Refuzurile inventarului (listă de texte; goală = valid): coloane, criteriu / rezoluție / operator necunoscute, rând dublu,
    cod fără cele 12 celule (de exemplu o singură rezoluție)."""
    from verifica_pas import OPERATORI
    erori, vazute, pe_cod = [], set(), {}
    if not randuri:
        return ["inventar gol"]
    lipsa = [c for c in COLOANE_INVENTAR if c not in randuri[0]]
    if lipsa:
        return ["coloane lipsă: %s" % ", ".join(lipsa)]
    for i, r in enumerate(randuri, 2):
        cheie = (r["cod"], r["criteriu"], r["rezolutie"])
        if r["criteriu"] not in CRITERII:
            erori.append("rândul %d: criteriu necunoscut «%s»" % (i, r["criteriu"]))
        if r["rezolutie"] not in REZOLUTII:
            erori.append("rândul %d: rezoluție necunoscută «%s»" % (i, r["rezolutie"]))
        if r["operator"] not in OPERATORI:
            erori.append("rândul %d: operator necunoscut «%s»" % (i, r["operator"]))
        if not r["cod"].strip():
            erori.append("rândul %d: cod gol" % i)
        if cheie in vazute:
            erori.append("rândul %d: celulă dublă %s" % (i, "/".join(cheie)))
        vazute.add(cheie)
        pe_cod.setdefault(r["cod"], set()).add((r["criteriu"], r["rezolutie"]))
    for cod, celule in sorted(pe_cod.items()):
        lipsesc = sorted({(c, z) for c in CRITERII for z in REZOLUTII} - celule)
        if lipsesc:
            erori.append("codul %s nu are cele 12 celule: lipsesc %s" % (cod, ", ".join("%s/%s" % x for x in lipsesc)))
    return erori


def _manifest(director):
    cale = os.path.join(director, "martori.sha256")
    if not os.path.isfile(cale):
        return {}
    out = {}
    for linie in open(cale, encoding="utf-8"):
        p = linie.strip().split("  ", 1)
        if len(p) == 2:
            out[p[1]] = p[0]
    return out


def judeca_celula(rand, director, commit, faza, manifest):
    """Celula judecată (dict COLOANE_CELULA). «-» = neexecutat (cu motivul); 0 = încălcare observată pe ecranul corect; 1 = conform."""
    from verifica_pas import compara_asertiune
    c = {k: rand.get(k, "") for k in COLOANE_CELULA}
    c.update(versiune=commit, faza=faza, observat="", martor="", martor_sha256="", captura="", captura_sha256="")
    nume = nume_martor(rand["cod"], rand["criteriu"], rand["rezolutie"])
    cale = os.path.join(director, nume)
    neex = lambda motiv: dict(c, rezultat="-", motiv=motiv)
    if not os.path.isfile(cale):
        return neex("martor lipsă")
    sha = sha_fisier(cale)
    c.update(martor=nume, martor_sha256=sha)
    if manifest.get(nume) != sha:
        raise Refuz("martor alterat sau nemanifestat: %s (SHA %s, manifest %s)" % (nume, sha[:12], (manifest.get(nume) or "-")[:12]))
    m = json.load(open(cale, encoding="utf-8"))
    if (m.get("cod"), m.get("criteriu"), m.get("rezolutie")) != (rand["cod"], rand["criteriu"], rand["rezolutie"]):
        raise Refuz("martorul %s descrie altă celulă: %s" % (nume, (m.get("cod"), m.get("criteriu"), m.get("rezolutie"))))
    for k in ("firma", "rol", "stare", "document_perioada", "gest", "dimensiune"):
        c[k] = m.get(k, c[k]) or c[k]
    if m.get("commit") != commit:
        return neex("martor de pe alt commit (%s), nu de pe versiunea măsurată" % str(m.get("commit"))[:12])
    cap = m.get("captura") or {}
    cap_cale = os.path.join(director, cap.get("cale") or "")
    if not cap.get("cale") or not os.path.isfile(cap_cale):
        return neex("captura lipsește")
    c.update(captura=cap["cale"], captura_sha256=sha_fisier(cap_cale))
    if c["captura_sha256"] != cap.get("sha256"):
        return neex("captura nu are SHA-ul din martor (altă captură / alt commit)")
    if m.get("ruta") != rand["ruta"]:
        return neex("rută greșită: %s, cerută %s" % (m.get("ruta"), rand["ruta"]))
    if not m.get("ecran_desenat"):
        return neex("ecranul nu s-a desenat")
    if m.get("motiv_neexecutat"):
        return neex(m["motiv_neexecutat"])
    if not m.get("selector_gasit"):
        if m.get("lipsa_confirmata"):        # ruta, starea și inventarul acțiunilor confirmate independent: lipsa controlului e defect
            return dict(c, observat="(lipsă)", rezultat="0", motiv="controlul cerut lipsește (lipsă confirmată independent)")
        return neex("selectorul nu s-a găsit (lipsa locatorului nu dovedește defectul)")
    c["observat"] = json.dumps(m.get("observat"), ensure_ascii=False) if not isinstance(m.get("observat"), str) else m["observat"]
    if rand["criteriu"] == "Stabilitate" and m.get("consola_erori"):
        return dict(c, rezultat="0", motiv="erori în consolă: %s" % "; ".join(map(str, m["consola_erori"]))[:200])
    verdict, motiv = compara_asertiune(rand["operator"], rand["asteptat"], m.get("observat"))
    if verdict == "trece":
        return dict(c, rezultat="1", motiv="conform")
    return dict(c, rezultat="0", motiv="observat diferit de așteptat (%s %s): %s" % (rand["operator"], rand["asteptat"], motiv))


def rezumat(celule):
    """Pe cod: numărătoarea 1/0/- pe rezoluție, închiderea (12 × 1), scorul istoric pe primele cinci criterii (separat) și celulele care
    împiedică închiderea, numite."""
    out = {}
    for c in celule:
        r = out.setdefault(c["cod"], {"celule": 0, "pe_rezolutie": {z: {"1": 0, "0": 0, "-": 0} for z in REZOLUTII},
                                      "scor_istoric_5": 0, "blocante": []})
        r["celule"] += 1
        r["pe_rezolutie"][c["rezolutie"]][c["rezultat"]] += 1
        if c["criteriu"] in CRITERII_ISTORICE and c["rezultat"] == "1":
            r["scor_istoric_5"] += 1
        if c["rezultat"] != "1":
            r["blocante"].append("%s/%s/%s=%s (%s)" % (c["cod"], c["criteriu"], c["rezolutie"], c["rezultat"], c["motiv"]))
    for r in out.values():
        r["inchis"] = r["celule"] == 12 and not r["blocante"]
    return out


def judeca(inventar, director, commit, faza="candidat"):
    randuri = citeste_tsv(inventar) if isinstance(inventar, str) else inventar
    erori = valideaza_inventar(randuri)
    if erori:
        raise Refuz("inventar invalid: " + "; ".join(erori))
    manifest = _manifest(director)
    celule = [judeca_celula(r, director, commit, faza, manifest) for r in randuri]
    return celule, rezumat(celule)


def cod_iesire(celule):
    return 0 if celule and all(c["rezultat"] == "1" for c in celule) else 1


def masoara_celula(pagina, rand, director, commit, ctx=None):
    """Măsoară o celulă pe pagina vie (Playwright) și scrie martorul + captura + rândul din manifest. `ctx` = {firma, rol, ruta,
    stare, document_perioada, gest, dimensiune, ecran_desenat, lipsa_confirmata, consola_erori}: le pune parcursul care a făcut gestul
    (ruta observată, starea, ecranul desenat sunt ale parcursului, nu ale uneltei). Citirea: `verifica_pas.observa_pagina`."""
    from verifica_pas import observa_pagina
    ctx = dict(ctx or {})
    os.makedirs(director, exist_ok=True)
    nume = nume_martor(rand["cod"], rand["criteriu"], rand["rezolutie"])
    cap = nume[:-5] + ".png"
    observat, gasit = None, False
    try:
        if rand["cheie"].startswith("dom:"):     # selectorul lipsă = «-» (nu 0), oricare ar fi măsura (`activ` ar da false)
            sel = rand["cheie"][4:].rpartition("|")[0]
            if not pagina.evaluate("(s) => document.querySelectorAll(s).length", sel):
                raise LookupError("selectorul %s nu există pe pagină" % sel)
        gasit, observat = observa_pagina(pagina, rand["cheie"], director, rand["operator"])
        gasit = bool(gasit) and observat is not None and observat != [] and observat != ""
    except Exception as e:  # noqa: BLE001 — selectorul lipsă / pagina nedesenată: «-» cu motiv, nu verdict
        gasit, ctx["eroare_citire"] = False, str(e)[:200]
    pagina.screenshot(path=os.path.join(director, cap))
    m = {"cod": rand["cod"], "criteriu": rand["criteriu"], "rezolutie": rand["rezolutie"], "commit": commit,
         "firma": ctx.get("firma", rand.get("firma")), "rol": ctx.get("rol", rand.get("rol")), "ruta": ctx.get("ruta"),
         "stare": ctx.get("stare", rand.get("stare")), "document_perioada": ctx.get("document_perioada", rand.get("document_perioada")),
         "gest": ctx.get("gest", rand.get("gest")), "dimensiune": ctx.get("dimensiune", rand.get("dimensiune")),
         "ecran_desenat": bool(ctx.get("ecran_desenat")), "selector_gasit": gasit, "lipsa_confirmata": bool(ctx.get("lipsa_confirmata")),
         "observat": observat, "captura": {"cale": cap, "sha256": sha_fisier(os.path.join(director, cap))},
         "consola_erori": list(ctx.get("consola_erori") or []), "motiv_neexecutat": ctx.get("motiv_neexecutat") or ""}
    cale = os.path.join(director, nume)
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(director, "martori.sha256"), "a", encoding="utf-8") as f:
        f.write("%s  %s\n" % (sha_fisier(cale), nume))
    return m


def bilant(celule_baza, celule_retest, numitor):
    """Bilanțul pe numitor (codurile date, 12 chei fiecare): I0, I1, închise acum = I1 − I0, redeschise = I0 − I1, NET; pentru fiecare cod
    schimbat, celulele schimbate cu motivul și martorul; pierderea confirmării deosebește defectul probat (0) de martorul lipsă («-»)."""
    def idx(cel):
        return {(c["cod"], c["criteriu"], c["rezolutie"]): c for c in cel if c["cod"] in numitor}
    b, r = idx(celule_baza), idx(celule_retest)
    toate = [(cod, cr, z) for cod in sorted(numitor) for cr in CRITERII for z in REZOLUTII]
    lipsa = lambda k: {"cod": k[0], "criteriu": k[1], "rezolutie": k[2], "rezultat": "-", "motiv": "cheie nemăsurată", "martor": ""}
    b = {k: b.get(k) or lipsa(k) for k in toate}
    r = {k: r.get(k) or lipsa(k) for k in toate}
    inchise = lambda d: {cod for cod in numitor if all(d[(cod, cr, z)]["rezultat"] == "1" for cr in CRITERII for z in REZOLUTII)}
    i0, i1 = inchise(b), inchise(r)
    schimbari = []
    for k in toate:
        if b[k]["rezultat"] != r[k]["rezultat"]:
            fel = "pierdere: defect probat" if b[k]["rezultat"] == "1" and r[k]["rezultat"] == "0" else (
                "pierdere: martor lipsă" if b[k]["rezultat"] == "1" and r[k]["rezultat"] == "-" else "câștig" if r[k]["rezultat"] == "1" else "altă schimbare")
            schimbari.append({"celula": "/".join(k), "baza": b[k]["rezultat"], "retest": r[k]["rezultat"], "fel": fel,
                              "motiv_retest": r[k].get("motiv", ""), "martor_retest": r[k].get("martor", "")})
    numara = lambda d: {z: {v: sum(1 for k in toate if k[2] == z and d[k]["rezultat"] == v) for v in ("1", "0", "-")} for z in REZOLUTII}
    return {"numitor": len(numitor), "chei": len(toate), "I0": sorted(i0), "I1": sorted(i1), "inchise_acum": sorted(i1 - i0),
            "redeschise": sorted(i0 - i1), "NET": len(i1 - i0) - len(i0 - i1), "baza": numara(b), "retest": numara(r),
            "schimbari": schimbari}


def importa_q12(rezultate_q12, celule_q12, coduri, commit):
    """Adaptorul măsurării Q12 publicate (rezultate_17_5_Q12.tsv, 55 de celule cu martor și SHA): celulele ei intră cu rezultatul și
    martorul lor; celelalte chei ale codurilor ies «-» cu motivul (rezumatul istoric nu e măsurătoare pe Q12)."""
    rez = {(r["cod"], r["criteriu"], r["rezolutie"]): r for r in citeste_tsv(rezultate_q12)}
    obs = {(r["cod"], r["criteriu"], r["rezolutie"]): r for r in citeste_tsv(celule_q12)}
    out = []
    for cod in sorted(coduri):
        for cr in CRITERII:
            for z in REZOLUTII:
                k = (cod, cr, z)
                c = {x: "" for x in COLOANE_CELULA}
                c.update(cod=cod, criteriu=cr, rezolutie=z, versiune=commit, faza="masurare_Q12")
                if k in rez:
                    q = rez[k]
                    c.update(rezultat=q["rezultat"], observat=q.get("observatie", ""), martor=q.get("martor", ""), martor_sha256=q.get("sha256", ""),
                             asteptat=(obs.get(k) or {}).get("criteriu_de_acceptare", ""),
                             motiv="măsurarea Q12 pe %s" % q.get("commit", "")[:12] if q["rezultat"] != "-" else q.get("observatie", ""))
                    if q.get("commit") and q["commit"] != commit:
                        c["motiv"] += " (produs identic cu versiunea %s)" % commit[:12]
                else:
                    c.update(rezultat="-", motiv="neexecutat: fără măsurare detaliată pe Q12 (numai rezumatul istoric 24.11, care nu e măsurătoare)")
                out.append(c)
    return out


def main(a):
    try:
        if not a:
            raise Refuz("uz: valideaza | judeca | bilant | importa-q12 (vezi docstring)")
        if a[0] == "valideaza":
            erori = valideaza_inventar(citeste_tsv(a[1]))
            print("\n".join(erori) if erori else "inventar valid: %d celule" % len(citeste_tsv(a[1])))
            return 2 if erori else 0
        if a[0] == "judeca":
            faza = a[a.index("--faza") + 1] if "--faza" in a else "candidat"
            celule, rez = judeca(a[1], a[2], a[3], faza)
            scrie_tsv(a[4], COLOANE_CELULA, celule)
            if "--rezumat" in a:
                json.dump(rez, open(a[a.index("--rezumat") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            for cod, r in sorted(rez.items()):
                print("%s: %s · %s · scor istoric (5 criterii) %d/10 · %s" % (
                    cod, "ÎNCHIS" if r["inchis"] else "deschis", " ".join("%s 1=%d 0=%d -=%d" % (z, v["1"], v["0"], v["-"]) for z, v in r["pe_rezolutie"].items()),
                    r["scor_istoric_5"], "; ".join(r["blocante"]) or "fără celule blocante"))
            n0 = sum(1 for c in celule if c["rezultat"] == "0")
            nn = sum(1 for c in celule if c["rezultat"] == "-")
            print("REZULTAT: %s (%d celule, 0 = %d, neexecutat = %d)" % (
                "complet verde" if cod_iesire(celule) == 0 else "inventar valid, cu rezultate 0 sau neexecutate", len(celule), n0, nn))
            return cod_iesire(celule)
        if a[0] == "bilant":
            numitor = {l.strip() for l in open(a[a.index("--numitor") + 1], encoding="utf-8") if l.strip() and not l.startswith("#")}
            b = bilant(citeste_tsv(a[1]), citeste_tsv(a[2]), numitor)
            if "--iesire" in a:
                json.dump(b, open(a[a.index("--iesire") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("I0 = %s\nI1 = %s\nînchise acum = %s\nredeschise = %s\nNET = %d" % (b["I0"], b["I1"], b["inchise_acum"], b["redeschise"], b["NET"]))
            print("baza: %s\nretest: %s\nschimbări: %d" % (b["baza"], b["retest"], len(b["schimbari"])))
            for s in b["schimbari"]:
                print("  %s: %s -> %s (%s) %s %s" % (s["celula"], s["baza"], s["retest"], s["fel"], s["motiv_retest"], s["martor_retest"]))
            return 0
        if a[0] == "importa-q12":
            coduri = {l.strip() for l in open(a[3], encoding="utf-8") if l.strip() and not l.startswith("#")}
            scrie_tsv(a[5], COLOANE_CELULA, importa_q12(a[1], a[2], coduri, a[4]))
            print("scris %s" % a[5])
            return 0
        raise Refuz("subcomandă necunoscută: %s" % a[0])
    except Refuz as e:
        print("REFUZ: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
