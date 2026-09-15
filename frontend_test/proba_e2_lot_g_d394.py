# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL G — cele trei unități-nucleu ale D394: fișa clientului nu rescrie istoria.

Comanda (Costin, 15.09.2026), ordinea cerută: d300 → **d394** → d112 → d406 → restul.

**PRIMA FORMĂ A LANȚULUI A FOST GREȘITĂ, și se scrie fiindcă e chiar lecția.** Voiam să probez
ramura de REZERVĂ din `d394.py:1015` (`cui = r["tert_cui"] or r["c_cui"]`), emițând o factură doar
pe `client_id`. Ruta a refuzat, de două ori, și amândouă refuzurile aveau dreptate:

  · *„Denumirea beneficiarului e obligatorie pe factură."*
  · *„Factura nu se poate salva fără codul fiscal al partenerului … Fără el, factura nu intră în
    D394 și nu se poate corela în VIES, iar codul nu mai poate fi completat mai târziu de altcineva
    decât cel care a emis-o (Cod fiscal art. 319 alin. 20)."*

**Deci ramura de rezervă e, pe date NOI, inaccesibilă** — și codul o spune deja în comentariul ei:
*„o factura veche fara `tert_cui`, emisa doar pe `client_id`, inainte de…"*. Fișa clientului nu
ajunge azi în D394; factura o poartă. *Perimetrul spune „poate ajunge", nu „ajunge" — limita e
declarată în `scan_lanturi_declaratie`, și asta e o instanță a ei.*

**AȘTEPTAREA, REFĂCUTĂ ÎNAINTE DE PROBĂ** — pe direcția care contează cu adevărat, decizia 47
(*„factura e autoritatea; istoria se corectează prin storno și reemitere, nu prin editarea fișei"*):

| # | unitatea | intrarea | așteptat | de unde |
|---|---|---|---|---|
| 1 | `POST /tenants/{}/clienti` | fișă nouă cu `CUI_1`; factură 400 @21% emisă cu `tert_cui = CUI_1` | în D394 apare `<op1 … cuiP="CUI_1" baza="400">` | `d394.py:1015`, ramura de pe factură |
| 2 | `PUT /tenants/{}/clienti/{}` | se schimbă CUI-ul **fișei** la `CUI_2` | declarația **NU se schimbă**: `cuiP` rămâne `CUI_1`, iar `CUI_2` nu apare nicăieri | decizia 47 — editarea fișei nu rescrie o factură emisă |
| 3 | `DELETE /tenants/{}/clienti/{}` | se șterge fișa | declarația **rămâne identică**: factura nu depinde de fișă | aceeași decizie, în oglindă |

*Lanțurile 2 și 3 sunt aserțiuni de NESCHIMBARE, și de-aia poartă fiecare un martor: dacă
declarația n-ar conține deloc `CUI_1` de la început, „nu s-a schimbat nimic" ar fi adevărat degeaba.
Lanțul 1 e chiar martorul.*

SCENARIUL, DECLARAT: «Comert Micro TVA SRL» (`tenant_003`), trimestrul **III/2026**. Intrările poartă
`PROBA-E2-G-<rulare>`, iar numărul rulării se derivă din câte facturi poartă marca (decizia 69: delta
se măsoară de fiecare dată). Fișa se șterge la pasul 3 — deci rulările nu lasă fișe în urmă, dar
lasă facturi, și asta se scrie.

CE NU DEMONSTREAZĂ, declarat: că regula „factura e autoritatea" e cea corectă fiscal (aia e decizia
47, luată de Costin) — doar că aplicația o aplică pe drumul pe care spune că o aplică. Și nu spune
nimic despre facturile ISTORICE fără `tert_cui`, pentru care ramura de rezervă chiar lucrează: nu
există pe firma de probă și nu se poate crea una prin aplicație.
"""
import base64
import json
import re
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Comert Micro TVA SRL"
AN, TRIM, LUNA = 2026, 3, 9
MARCA = "PROBA-E2-G"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_lot_g_d394.json"

#: Două CUI-uri cu cifra de control corectă (cerința `core/test_cui_cnp_test_valid.py`), luate din
#: portofoliul de test unde au fost deja verificate — nu inventate.
CUI_1 = "95687300"
CUI_2 = "95775518"

_OP1 = re.compile(r"<op1\b([^>]*)/?>")
_ATR = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"')


def d394(tok, tid):
    """[{atribute}] pentru fiecare `<op1>` — partenerul trăiește acolo, nu pe rădăcină."""
    st, r = U.cere("POST", "/declaratii/d394", {"tenant_id": tid, "an": AN, "trim": TRIM}, tok)
    if st != 200 or not isinstance(r, dict):
        return None, {"stare": st, "raspuns": str(r)[:300]}
    xml = r.get("xml") or r.get("continut") or ""
    if not xml and r.get("xml_b64"):
        xml = base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    ops = [dict(_ATR.findall(m.group(1))) for m in _OP1.finditer(xml)]
    # ANTI-VACUU (lecția lotului F): un cititor care nu găsește nimic trebuie să CADĂ. Firma are
    # facturi în trimestru (loturile A și F), deci zero `op1` înseamnă cititor orb, nu declarație goală.
    if not ops:
        raise SystemExit("ANTI-VACUU: D394 s-a generat (%d octeti) dar nu i s-a citit niciun `op1`"
                         % len(xml))
    return ops, {"stare": st, "octeti_xml": len(xml), "op1_citite": len(ops)}


def cu_cui(ops, cui):
    return [o for o in (ops or []) if (o.get("cuiP") or "").replace("RO", "") == cui]


def semnatura(ops):
    """Ce se compară între pași: mulțimea (cuiP, denP, cota, baza, tva) — structură, nu text."""
    return sorted((o.get("cuiP", ""), o.get("denP", ""), o.get("cota", ""),
                   o.get("baza", ""), o.get("tva", "")) for o in (ops or []))


def main():
    tok, tid, schema = U.context(FIRMA)
    st_f, r_f = U.cere("GET", "/tenants/%d/facturi?an=%d&luna=%d" % (tid, AN, LUNA), None, tok)
    lst = (r_f.get("facturi") if isinstance(r_f, dict) else r_f) or []
    rul = 1 + len([f for f in lst if str(f.get("numar") or "").startswith(MARCA)]) \
        if isinstance(lst, list) else 1
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema,
           "perioada": "%d-T%d" % (AN, TRIM), "rulare": rul, "lanturi": []}

    # ── 1. FIȘA se creează; factura o poartă pe ea, cu CUI-ul scris PE FACTURĂ ──
    intr = {"lant": "1 · clienti (creare) + factură 400 @21% pe `tert_cui=CUI_1` → `op1` în D394",
            "ruta": "POST /tenants/{}/clienti"}
    nume_client = "%s Client %d SRL" % (MARCA, rul)
    st1, r1 = U.cere("POST", "/tenants/%d/clienti" % tid,
                     {"nume": nume_client, "cui": CUI_1, "adresa": "Str. Probei nr. %d" % rul,
                      "oras": "Bucuresti", "judet": "Bucuresti"}, tok)
    cid = (r1 or {}).get("client_id") or (r1 or {}).get("id") if isinstance(r1, dict) else None
    intr["client"] = {"stare": st1, "id": cid, "corp": str(r1)[:200]}
    if not cid:
        intr["NEPROBAT"] = "fișa nu s-a creat (stare %s) — lanțul n-are subiect" % st1
        intr["OK"] = False
        rez["lanturi"].append(intr)
        print(json.dumps(rez, indent=1, ensure_ascii=False))
        return 2

    st_e, r_e = U.cere("POST", "/tenants/%d/facturi/emite" % tid,
                       {"tip": "factura", "data_emitere": "%d-%02d-24" % (AN, LUNA),
                        "client_id": cid, "tert_nume": nume_client, "tert_cui": CUI_1,
                        "linii": [{"descriere": "%s-%d factura pe fisa" % (MARCA, rul),
                                   "cantitate": 1, "pret_unitar": 400, "cota_tva": 21}]}, tok)
    fid = (r_e or {}).get("factura_id") if isinstance(r_e, dict) else None
    intr["factura"] = {"stare": st_e, "id": fid, "corp": str(r_e)[:200]}
    ops1, meta1 = d394(tok, tid)
    gasit1 = cu_cui(ops1, CUI_1)
    intr["d394"] = meta1
    intr["op1_cu_CUI_1"] = gasit1
    intr["OK"] = bool(fid) and bool(gasit1)
    rez["lanturi"].append(intr)
    sem1 = semnatura(ops1)

    # ── 2. EDITAREA FIȘEI nu rescrie o factură emisă (decizia 47) ────────────
    intr2 = {"lant": "2 · clienti (actualizare CUI pe fișă) → declarația NU se schimbă",
             "ruta": "PUT /tenants/{}/clienti/{}",
             "martor": "lanțul 1 a pus `CUI_1` în declarație; fără el, «nu s-a schimbat» n-ar spune nimic"}
    st2, r2 = U.cere("PUT", "/tenants/%d/clienti/%s" % (tid, cid), {"cui": CUI_2}, tok)
    ops2, meta2 = d394(tok, tid)
    sem2 = semnatura(ops2)
    intr2.update({"raspuns": {"stare": st2, "corp": str(r2)[:200]}, "d394": meta2,
                  "op1_cu_CUI_1_ramase": len(cu_cui(ops2, CUI_1)),
                  "op1_cu_CUI_2_aparute": len(cu_cui(ops2, CUI_2)),
                  "declaratia_identica": sem1 == sem2})
    intr2["OK"] = (st2 in (200, 201) and bool(gasit1) and sem1 == sem2
                   and not cu_cui(ops2, CUI_2))
    rez["lanturi"].append(intr2)

    # ── 3. ȘTERGEREA FIȘEI nu scoate factura din declarație ─────────────────
    intr3 = {"lant": "3 · clienti (ștergere) → declarația rămâne identică",
             "ruta": "DELETE /tenants/{}/clienti/{}"}
    st3, r3 = U.cere("DELETE", "/tenants/%d/clienti/%s" % (tid, cid), None, tok)
    ops3, meta3 = d394(tok, tid)
    sem3 = semnatura(ops3)
    motiv = json.dumps(r3, ensure_ascii=False) if isinstance(r3, dict) else str(r3)
    intr3.update({"raspuns": {"stare": st3, "corp": motiv[:300]}, "d394": meta3,
                  "op1_cu_CUI_1_ramase": len(cu_cui(ops3, CUI_1)),
                  "declaratia_identica": sem2 == sem3})
    if st3 >= 400:
        intr3["ce_s_a_intamplat"] = "REFUZ — acceptabil, dar trebuie MOTIVAT (nu 500)"
        intr3["OK"] = (st3 != 500 and len(motiv) > 20 and sem2 == sem3)
    else:
        intr3["ce_s_a_intamplat"] = "ȘTEARSĂ — factura trebuie să RĂMÂNĂ, cu CUI-ul ei de pe factură"
        intr3["OK"] = (sem2 == sem3 and bool(cu_cui(ops3, CUI_1)))
    rez["lanturi"].append(intr3)

    st_v, r_v = U.cere("POST", "/declaratii/d394/valideaza",
                       {"tenant_id": tid, "an": AN, "trim": TRIM}, tok, timeout=300)
    rez["duk"] = {"stare_http": st_v,
                  "stare": (r_v or {}).get("stare") if isinstance(r_v, dict) else str(r_v)[:200],
                  "erori": (r_v or {}).get("erori") if isinstance(r_v, dict) else None}

    text = json.dumps(rez, indent=1, ensure_ascii=False)
    open(OUT, "w", encoding="utf-8").write(text)
    print(text)
    nep = [x for x in rez["lanturi"] if not x.get("OK")]
    print("\nLANTURI: %d · CU NEPOTRIVIRI: %d" % (len(rez["lanturi"]), len(nep)))
    for x in nep:
        print("   ! %s" % x["lant"])
    return 1 if nep else 0


if __name__ == "__main__":
    sys.exit(main())
