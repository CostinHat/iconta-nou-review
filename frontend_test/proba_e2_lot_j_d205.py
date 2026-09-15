# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL J — ultima unitate-nucleu: importul de asociați, până în D205.

Comanda (Costin, 15.09.2026): ordinea d300 → d394 → d112 → d406 → **restul**. „Restul" e una
singură: `POST /tenants/{}/asociati-import`, nucleul lui D205.

**AȘTEPTAREA, SCRISĂ ÎNAINTE, PE DOUĂ DIRECȚII.** Citit la sursă (`core/d205.py:315-332`,
`genereaza`): beneficiarii ies din `asociati` **cu cota > 0**, iar sumele vin din notele VALIDATE pe
contul 457 (`divid_D` = credit, `divid_P` = debit), **împărțite după cotă**. Deci un asociat nou:

| ce | așteptat | de ce |
|---|---|---|
| `nrben` | **+1** | e un beneficiar în plus în secțiune |
| `Tbaza` | **NESCHIMBAT** | totalul distribuit nu se schimbă — se împarte altfel |
| `Timp` | **NESCHIMBAT** | impozitul e pe același total |
| noul asociat | apare cu `baza1` **proporțional cu cota** | împărțirea pe cotă, `genereaza` |

**PRIMA FORMĂ A LANȚULUI A FOST GREȘITĂ, și refuzul aplicației m-a corectat** (al cincilea de azi):
trimisesem **doar** asociatul nou, cu cotă 1%. Ruta a răspuns `422`: *„cotele asociaților însumează
1.0%, nu 100%. Asociații și cotele lor intră în D205 (dividende) — cotele trebuie să dea exact
100%."* Deci importul **ÎNLOCUIEȘTE** lista, nu adaugă la ea, iar suma cotelor e o poartă. *Un refuz
care spune și CE e greșit și DE CE contează.* Lanțul trimite acum lista ÎNTREAGĂ: beneficiarii
existenți, aduși la 99% cumulat, plus al meu cu 1%.

*O probă care ar verifica numai prima linie n-ar deosebi „aplicația adaugă un beneficiar" de
„aplicația mai numără o dată același dividend". Cele două direcții împreună prind dublarea.*

SCENARIUL, DECLARAT: «Comert Micro TVA SRL» (`tenant_003`), anul **2026**. Asociatul poartă marca
`PROBA-E2-J-<rulare>`, cu CNP a cărui cifră de control e **calculată** cu validatorul aplicației, și
o cotă **mică** (1%), iar ceilalți aduși la 99% cumulat. **Nimic nu rămâne**: la capăt proba 
**desface** — reimportă lista de la pornire, cu cotele derivate din `baza1 / Tbaza × 100` —, și
**verifică** întoarcerea (`nrben`, `Tbaza`, `Timp` exact ca înainte). Fără desfacere, fiecare rulare
ar reîmpărți cotele celorlalți (100 → 99 → 49,5 → …), adică proba ar strica încet chiar datele pe
care se sprijină.

CE NU DEMONSTREAZĂ, declarat: cuantumul impozitului pe dividende (16% din 2026, Legea 141/2025) —
aia e treaba golden-urilor; aici se probează că asociatul introdus **ajunge** beneficiar, și că
totalul **nu** se dublează.
"""
import base64
import json
import re
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "ALFA MICRO SRL"   # firma cu dividende, aceeasi ca lotul E (D205); pe tenant_003 D205 refuza,
#: si pe drept: „D205 fara niciun beneficiar de venit - nu se genereaza declaratie fara conttinut."
AN = 2026
EMAIL = "fir-intrare@prisma-cont.test"   # cabinetul 4163, căruia îi e atribuită firma
MARCA = "PROBA-E2-J"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_lot_j_d205.json"

_ATR = re.compile(r'(\w+)="([^"]*)"')


def elemente(xml, nume):
    return [dict(_ATR.findall(m.group(1)))
            for m in re.finditer(r"<(?:\w+:)?%s\b([^>]*)/?>" % nume, xml or "")]


def d205(tok, tid):
    st, r = U.cere("POST", "/declaratii/d205", {"tenant_id": tid, "an": AN}, tok, timeout=240)
    if st != 200:
        return None, {"stare": st, "raspuns": str(r)[:400]}
    xml = r.get("xml") if isinstance(r, dict) else r
    if not xml and isinstance(r, dict) and r.get("xml_b64"):
        xml = base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    sect = elemente(xml, "sect_II")
    ben = elemente(xml, "benef")
    # ANTI-VACUU (lecția loturilor F–I): un cititor care nu găsește nimic trebuie să CADĂ.
    if not sect:
        raise SystemExit("ANTI-VACUU: D205 s-a generat (%d octeti) dar nu i s-a citit `sect_II` — "
                         "cititorul probei e orb, nu declarația e goală" % len(xml or ""))
    return {"xml": xml, "sect_II": sect[0], "beneficiari": ben}, \
           {"stare": st, "octeti_xml": len(xml or ""), "benef_citiți": len(ben)}


def cnp_valid(prefix):
    from core import identitate as _id
    for c in "0123456789":
        cand = prefix + c
        ok = _id.valideaza_cnp(cand)
        ok = ok[0] if isinstance(ok, tuple) else ok
        if ok:
            return cand
    raise SystemExit("niciun CNP valid pe prefixul %r" % prefix)


def main():
    # Firma e atribuită ALTUI cabinet (4163), deci se intră cu utilizatorul lui — ca la lotul
    # E. Fără asta ruta refuză: «Firma nu există în portofoliu sau nu ți-e atribuită», iar
    # REFUZUL ARE DREPTATE: e poarta de izolare între cabinete (R43). *Al cincilea refuz corect
    # al zilei care mi-a corectat proba.*
    # `e2_util.EMAIL` se citeste din mediu la IMPORT, deci punerea variabilei in `os.environ`
    # dupa import n-are efect — prima forma a probei a facut exact asta si a primit iar `404`.
    # Se pune pe MODUL, care e ce citeste `context()`.
    U.EMAIL = EMAIL
    tok, tid, schema = U.context(FIRMA)
    baza, meta0 = d205(tok, tid)
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema, "an": AN,
           "d205_la_pornire": meta0, "lanturi": []}
    if baza is None:
        rez["OPRIT"] = ("D205 nu se generează la pornire — proba n-are de unde măsura delta. "
                        "Motivul e în `d205_la_pornire`, nu presupus.")
        print(json.dumps(rez, indent=1, ensure_ascii=False))
        return 2

    s0 = baza["sect_II"]
    n0 = int(s0.get("nrben") or 0)
    tbaza0, timp0 = s0.get("Tbaza"), s0.get("Timp")
    rul = 1 + len([b for b in baza["beneficiari"] if MARCA in str(b.get("den1") or "")])
    cnp = cnp_valid(("19502%02d1511%d" % (rul % 12 + 1, rul % 10))[:12])

    i = {"lant": "1 · asociati-import: un asociat cu cotă 1%% → `nrben` +1, `Tbaza`/`Timp` NESCHIMBATE",
         "ruta": "POST /tenants/{}/asociati-import", "cnp": cnp, "rulare": rul,
         "inainte": {"nrben": n0, "Tbaza": tbaza0, "Timp": timp0}}
    # Lista ÎNTREAGĂ: cei existenți (citiți din chiar declarația de dinainte, nu din tabel — proba
    # nu se uită pe la spatele aplicației), aduși la 99% cumulat, plus al meu cu 1%.
    # ATRIBUTELE REALE sunt `den1` si `cifR`, nu `nume1`/`cif` — acelea sunt din DOCSTRINGUL lui
    # `d205.py:16`, iar generatorul emite altceva (`build_xml`). A doua formă a probei a citit pe
    # numele din docstring, a găsit gol, a pus un nume de rezervă și un CNP GOL, și a trimis lista la
    # un import care ÎNLOCUIEȘTE — suprascriind asociatul real al firmei. *Proza care descrie codul
    # poate fi falsă (R16), iar o probă care completează cu valori de rezervă ce n-a putut citi NU e
    # o probă, e o scriere.* De-aia, mai jos, un rând incomplet OPREȘTE proba în loc să fie trimis.
    existenti = baza["beneficiari"]
    randuri = []
    if existenti:
        cota_fiecare = round(99.0 / len(existenti), 2)
        rest = round(99.0 - cota_fiecare * (len(existenti) - 1), 2)
        for k, b in enumerate(existenti):
            nume_b = (b.get("den1") or "").strip()
            cnp_b = (b.get("cifR") or "").strip()
            if not nume_b or not cnp_b:
                i["OPRIT"] = (
                    "beneficiarul existent %d nu s-a putut citi întreg din declarație "
                    "(den1=%r, cifR=%r). NU se trimite un rând incomplet: importul ÎNLOCUIEȘTE "
                    "lista, deci ar suprascrie un asociat real cu unul gol — s-a întâmplat o dată, "
                    "azi, și a fost restaurat din artefactul lotului E." % (k, nume_b, cnp_b))
                i["OK"] = False
                rez["lanturi"].append(i)
                text = json.dumps(rez, indent=1, ensure_ascii=False)
                open(OUT, "w", encoding="utf-8").write(text)
                print(text)
                return 2
            randuri.append({"nume": nume_b, "cnp": cnp_b,
                            "cota": rest if k == len(existenti) - 1 else cota_fiecare,
                            "tip": "fizica", "cnp_valid": True, "cnp_motiv": "ok"})
    randuri.append({"nume": "%s Asociat %d" % (MARCA, rul), "cnp": cnp, "cota": 1,
                    "tip": "fizica", "cnp_valid": True, "cnp_motiv": "ok"})
    i["randuri_trimise"] = randuri
    st, r = U.cere("POST", "/tenants/%d/asociati-import" % tid, {"randuri": randuri}, tok)
    i["raspuns"] = {"stare": st, "corp": str(r)[:300]}
    dupa, meta1 = d205(tok, tid)
    i["d205"] = meta1
    if dupa is None:
        i["NEPROBAT"] = "D205 nu se mai generează după import — se scrie, nu se sare"
        i["OK"] = False
    else:
        s1 = dupa["sect_II"]
        i["dupa"] = {"nrben": int(s1.get("nrben") or 0), "Tbaza": s1.get("Tbaza"),
                     "Timp": s1.get("Timp")}
        i["al_meu"] = [b for b in dupa["beneficiari"] if str(b.get("cifR") or "") == cnp]
        nepotriviri = {}
        if i["dupa"]["nrben"] != n0 + 1:
            nepotriviri["nrben"] = {"asteptat": n0 + 1, "masurat": i["dupa"]["nrben"]}
        if i["dupa"]["Tbaza"] != tbaza0:
            nepotriviri["Tbaza"] = {"asteptat": tbaza0, "masurat": i["dupa"]["Tbaza"],
                                    "de_ce": "totalul distribuit nu se schimbă — se împarte altfel"}
        if i["dupa"]["Timp"] != timp0:
            nepotriviri["Timp"] = {"asteptat": timp0, "masurat": i["dupa"]["Timp"]}
        if not i["al_meu"]:
            nepotriviri["beneficiarul_meu"] = "absent din declarație"
        i["nepotriviri"] = nepotriviri
        i["OK"] = st in (200, 201) and not nepotriviri
    rez["lanturi"].append(i)

    # ── DESFACEREA, ca lotul B: ce s-a schimbat se pune la loc, iar întoarcerea se VERIFICĂ ──
    #    Fără ea, proba ar fi distructivă în timp: la fiecare rulare cotele celorlalți s-ar
    #    reîmpărți (100 → 99 → 49,5 → …). Cotele originale se DERIVĂ din declarația de la pornire —
    #    `cota = baza1 / Tbaza × 100` —, nu se presupun.
    desfacere = {"ce_face": "reimportă lista de asociați de la pornire, cu cotele derivate din "
                            "`baza1 / Tbaza × 100`"}
    try:
        tb = float(tbaza0 or 0)
        vechi = []
        for b in baza["beneficiari"]:
            nume_b, cnp_b = (b.get("den1") or "").strip(), (b.get("cifR") or "").strip()
            cota_b = round(float(b.get("baza1") or 0) / tb * 100, 2) if tb else 0
            if nume_b and cnp_b and cota_b > 0:
                vechi.append({"nume": nume_b, "cnp": cnp_b, "cota": cota_b,
                              "tip": "fizica", "cnp_valid": True, "cnp_motiv": "ok"})
        suma = round(sum(x["cota"] for x in vechi), 2)
        desfacere["randuri"] = vechi
        desfacere["suma_cotelor"] = suma
        if vechi and abs(suma - 100.0) < 0.01:
            st_d, r_d = U.cere("POST", "/tenants/%d/asociati-import" % tid,
                               {"randuri": vechi}, tok)
            desfacere["import"] = {"stare": st_d, "corp": str(r_d)[:200]}
            inapoi, meta_d = d205(tok, tid)
            s_inapoi = (inapoi or {}).get("sect_II") or {}
            desfacere["d205_dupa_desfacere"] = {
                "nrben": s_inapoi.get("nrben"), "Tbaza": s_inapoi.get("Tbaza"),
                "Timp": s_inapoi.get("Timp")}
            desfacere["revenit_exact"] = (
                str(s_inapoi.get("nrben")) == str(n0) and s_inapoi.get("Tbaza") == tbaza0
                and s_inapoi.get("Timp") == timp0)
        else:
            desfacere["NEFACUTA"] = ("cotele derivate nu însumează 100%% (%s) — NU se trimite o "
                                     "listă care ar fi refuzată sau, mai rău, acceptată strâmb"
                                     % suma)
    except Exception as e:  # noqa: BLE001
        desfacere["EROARE"] = "%s: %s" % (type(e).__name__, e)
    rez["desfacere"] = desfacere

    st_v, r_v = U.cere("POST", "/declaratii/d205/valideaza", {"tenant_id": tid, "an": AN},
                       tok, timeout=300)
    rez["duk"] = {"stare_http": st_v,
                  "stare": (r_v or {}).get("stare") if isinstance(r_v, dict) else str(r_v)[:200],
                  "erori": (r_v or {}).get("erori") if isinstance(r_v, dict) else None}

    text = json.dumps(rez, indent=1, ensure_ascii=False)
    open(OUT, "w", encoding="utf-8").write(text)
    print(text)
    nep = [x for x in rez["lanturi"] if not x.get("OK")]
    print("\nLANTURI: %d · CU NEPOTRIVIRI: %d" % (len(rez["lanturi"]), len(nep)))
    return 1 if nep else 0


if __name__ == "__main__":
    sys.exit(main())
