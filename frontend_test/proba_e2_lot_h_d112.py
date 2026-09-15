# -*- coding: utf-8 -*-
"""ETAPA 2, LOTUL H — cele șapte unități-nucleu ale D112 rămase neprobate individual.

Comanda (Costin, 15.09.2026), ordinea cerută: d300 → d394 → **d112** → d406 → restul.

**AȘTEPTAREA, SCRISĂ ÎNAINTE — fiecare regulă citită la sursă:**

| # | unitatea | intrarea | așteptat | de unde |
|---|---|---|---|---|
| 1 | `POST /tenants/{}/salariati-import` | un salariat, CNP cu cifra de control **calculată**, cod COR din nomenclator | `+1 <asigurat>`, cu CNP-ul lui | asigurații ies din `salariati` |
| 2 | `PUT /tenants/{}/salariati/{}/pontaj` | o zi lucrătoare pusă `absent_nemotivat` | declarația **se schimbă** pe asiguratul meu | `migrare_pontaj.STARI` + `pontaj.seteaza` |
| 3a | `PUT /tenants/{}/salariati/{}/beneficiu-lunar` | cadou **300** lei, Crăciun | declarația **NU se schimbă** — `PLAFON_CADOU = 300`, neimpozabil | `beneficii_api.PLAFON_CADOU` |
| 3b | aceeași rută | cadou **500** lei | declarația **se schimbă** — 200 peste plafon | același loc |
| 4 | `POST /tenants/{}/salariati/{}/concedii` | certificat CM cod 01 | declarația se schimbă pe asiguratul meu | `salariati_api.salveaza_concediu` |
| 5 | `DELETE /tenants/{}/salariati/{}/concedii/{}` | se șterge certificatul | declarația revine **exact** la starea de dinainte de 4 | simetric |
| 6 | `POST /tenants/{}/istoric-declaratii-import` | o depunere ISTORICĂ (07/2026) | declarația lunii 08 **NU se schimbă** — istoricul e evidență, nu intrare de calcul | `IstoricDeclRand` |
| 7 | `POST /coada/{}/depune` | id inexistent | **refuz motivat**, nu `500` și nu tăcere | — |

**Perechile sunt dinadins.** 3a+3b: o probă care arată doar că beneficiul crește baza n-ar deosebi
*„aplicația aplică plafonul"* de *„aplicația adună orice"* — plafonul se vede numai din cele două
împreună. 4+5: al doilea e **martorul** primului. 6 e o aserțiune de **NEschimbare**, iar martorul ei
sunt lanțurile de dinainte, care au arătat că declarația chiar se mișcă atunci când trebuie.

SCENARIUL, DECLARAT: «Panificatie Salarii Speciale SRL» (`tenant_001`), luna **08/2026** — firma de
salarii, aceeași ca lotul D. Salariatul poartă `PROBA-E2-H-<rulare>`; **CNP-ul nu e scris de mână**:
se ia prefixul și se caută cifra de control pe care o acceptă chiar validatorul aplicației
(`core.identitate`) — o a doua copie a algoritmului ar fi începutul unei divergențe.

CE NU DEMONSTREAZĂ, declarat: corectitudinea FISCALĂ a cuantumurilor (aia e treaba golden-urilor din
`core/test_d112*.py`) — aici se probează că valoarea introdusă de om **ajunge** unde spune codul, și
că **nu se mișcă** acolo unde codul spune că nu trebuie.
"""
import base64
import hashlib
import json
import re
import sys

sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")
sys.path.insert(0, "/home/costin/iconta_nou")

import e2_util as U  # noqa: E402

FIRMA = "Panificatie Salarii Speciale SRL"
AN, LUNA = 2026, 8
MARCA = "PROBA-E2-H"
OUT = "/home/costin/iconta_nou/frontend_test/proba_e2_lot_h_d112.json"
BRUT = 5000

_ATR = re.compile(r'(\w+)="([^"]*)"')


def elemente(xml, nume):
    return [dict(_ATR.findall(m.group(1)))
            for m in re.finditer(r"<%s\b([^>]*)/?>" % nume, xml or "")]


def d112(tok, tid):
    """(stare, meta). `stare` poartă XML-ul, asigurații și amprenta lui — comparațiile se fac pe
    amprentă, nu pe text: „s-a schimbat / nu s-a schimbat" e o întrebare despre CONȚINUT."""
    st, r = U.cere("POST", "/declaratii/d112", {"tenant_id": tid, "an": AN, "luna": LUNA},
                   tok, timeout=240)
    if st != 200:
        return None, {"stare": st, "raspuns": str(r)[:400]}
    xml = r.get("xml") if isinstance(r, dict) else r
    if not xml and isinstance(r, dict) and r.get("xml_b64"):
        xml = base64.b64decode(r["xml_b64"]).decode("utf-8", "replace")
    asig = elemente(xml, "asigurat")
    # ANTI-VACUU (lecția lotului F): un cititor care nu găsește nimic trebuie să CADĂ, nu să
    # întoarcă gol — altfel toate comparațiile de mai jos devin „0 == 0" și trec orice.
    if not asig:
        raise SystemExit("ANTI-VACUU: D112 s-a generat (%d octeti) dar nu i s-a citit niciun "
                         "`asigurat` — cititorul probei e orb" % len(xml or ""))
    return {"xml": xml, "asigurat": asig,
            "amprenta": hashlib.sha256((xml or "").encode()).hexdigest()[:16]}, \
           {"stare": st, "octeti_xml": len(xml or ""), "asigurati": len(asig)}


def cnp_valid(prefix):
    """CNP cu cifra de control CALCULATĂ — verificată cu validatorul APLICAȚIEI, nu rescris aici."""
    from core import identitate as _id
    for c in "0123456789":
        cand = prefix + c
        ok = _id.valideaza_cnp(cand)
        ok = ok[0] if isinstance(ok, tuple) else ok
        if ok:
            return cand
    raise SystemExit("niciun CNP valid pe prefixul %r" % prefix)


def alege_cor():
    from core import db
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT cod FROM public.cor_ocupatii ORDER BY cod LIMIT 1")
        r = cur.fetchone()
        conn.rollback()
    return r[0] if r else None


def main():
    tok, tid, schema = U.context(FIRMA)
    st_l, r_l = U.cere("GET", "/tenants/%d/salariati" % tid, None, tok)
    lista = (r_l.get("salariati") if isinstance(r_l, dict) else r_l) or []
    rul = 1 + len([s for s in lista if MARCA in str(s.get("nume") or "")]) \
        if isinstance(lista, list) else 1
    cnp = cnp_valid("19001%02d1511%d" % (LUNA, rul % 10))[:12] + ""
    cnp = cnp_valid(("19001%02d1511%d" % (LUNA, rul % 10))[:12])
    cor = alege_cor()
    rez = {"firma": FIRMA, "tenant_id": tid, "schema": schema, "perioada": "%d-%02d" % (AN, LUNA),
           "rulare": rul, "cnp": cnp, "cor": cor, "lanturi": []}

    baza, meta0 = d112(tok, tid)
    rez["d112_la_pornire"] = meta0
    if baza is None:
        rez["OPRIT"] = "D112 nu se generează la pornire — proba n-are de unde măsura delta"
        print(json.dumps(rez, indent=1, ensure_ascii=False))
        return 2
    n0, amp0 = len(baza["asigurat"]), baza["amprenta"]

    def scrie(intr):
        rez["lanturi"].append(intr)

    # ── 1. IMPORT DE SALARIAȚI ───────────────────────────────────────────────
    intr = {"lant": "1 · salariati-import → +1 `<asigurat>` cu CNP-ul importat",
            "ruta": "POST /tenants/{}/salariati-import"}
    st1, r1 = U.cere("POST", "/tenants/%d/salariati-import" % tid,
                     {"randuri": [{"nume": "%s Salariat" % MARCA, "prenume": "Rularea%d" % rul,
                                   "cnp": cnp, "data_angajare": "%d-%02d-01" % (AN, LUNA),
                                   "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": BRUT,
                                   "persoane_intretinere": 0, "judet_casa": "", "cor": cor,
                                   "cnp_valid": True, "cnp_motiv": "ok"}]}, tok)
    intr["raspuns"] = {"stare": st1, "corp": str(r1)[:300]}
    s1, m1 = d112(tok, tid)
    intr["d112"] = m1
    # ATRIBUTUL E `cnpAsig`, nu `cnp` (`d112.py:566`). Prima formă a probei a căutat `cnp`, n-a
    # găsit nimic și S-A OPRIT declarat — n-a raportat delte de zero. *A treia oară în trei loturi
    # când cititorul probei e cel greșit; de-aia fiecare lanț compară pe o cheie citită la sursă.*
    al_meu = [a for a in (s1 or {}).get("asigurat", []) if a.get("cnpAsig") == cnp]
    intr["asigurati"] = {"inainte": n0, "dupa": len((s1 or {}).get("asigurat", []))}
    intr["asiguratul_meu"] = al_meu[:1]
    intr["OK"] = bool(al_meu) and intr["asigurati"]["dupa"] == n0 + 1
    scrie(intr)

    st_s, r_s = U.cere("GET", "/tenants/%d/salariati" % tid, None, tok)
    lst = (r_s.get("salariati") if isinstance(r_s, dict) else r_s) or []
    sid = next((s.get("id") for s in lst if s.get("cnp") == cnp), None)
    rez["salariat_id"] = sid
    if not intr["OK"] or not sid:
        intr["NOTA"] = ("fără salariatul importat, lanțurile 2–5 n-au subiect: se opresc AICI, "
                        "declarat, în loc să raporteze delte de zero")
        text = json.dumps(rez, indent=1, ensure_ascii=False)
        open(OUT, "w", encoding="utf-8").write(text)
        print(text)
        return 1
    amp1 = s1["amprenta"]

    def pas(nume, ruta, metoda, cale, corp, trebuie_sa_schimbe, ref):
        """Un lanț care afirmă SCHIMBARE sau NESCHIMBARE, pe amprenta declarației."""
        i = {"lant": nume, "ruta": ruta}
        st, r = U.cere(metoda, cale, corp, tok)
        i["raspuns"] = {"stare": st, "corp": str(r)[:250]}
        s, m = d112(tok, tid)
        i["d112"] = m
        i["amprenta"] = {"inainte": ref, "dupa": (s or {}).get("amprenta")}
        # DEOSEBIREA care lipsea: dacă declarația NU SE MAI GENEREAZĂ, aia nu e „s-a schimbat".
        # Prima formă compara amprenta cu `None` și raporta „schimbat" — adică a citit o BLOCARE ca
        # pe un efect. S-a întâmplat: o zi de pontaj marcată absent blochează D112 până la
        # confirmarea pontajului (HG 1045/2018), iar proba a raportat verde. *Un `!=` cu o absență
        # nu e o măsurătoare.*
        if s is None:
            i["NU_SE_MAI_GENEREAZA"] = m
            i["ce_s_a_cerut"] = ("SE SCHIMBĂ" if trebuie_sa_schimbe else "NU se schimbă") \
                + " — dar declarația nu se mai generează, deci nu s-a măsurat nimic"
            i["OK"] = False
            scrie(i)
            return ref, r
        s_a_schimbat = s["amprenta"] != ref
        i["s_a_schimbat"] = s_a_schimbat
        i["ce_s_a_cerut"] = "SE SCHIMBĂ" if trebuie_sa_schimbe else "NU se schimbă"
        i["OK"] = (st in (200, 201)) and (s_a_schimbat == trebuie_sa_schimbe)
        scrie(i)
        return (s or {}).get("amprenta"), r

    # ── 2. PONTAJ: poarta de autoritate, apoi revenirea ─────────────────────
    #    AȘTEPTAREA REFĂCUTĂ, după ce prima formă a citit o BLOCARE ca pe o schimbare. Comportamentul
    #    real, și e corect: o zi atinsă face pontajul lunii NECONFIRMAT, iar D112 se BLOCHEAZĂ —
    #    „datele sunt informative, nu autoritative (HG 1045/2018 art.10(3))". Deci lanțul probează
    #    trei lucruri, nu unul: (a) poarta se închide, cu temei; (b) confirmarea o deschide;
    #    (c) valoarea introdusă a ajuns în declarație (amprenta diferă de cea de la început).
    i2 = {"lant": "2 · pontaj: o zi `absent_nemotivat` → D112 se BLOCHEAZĂ cu temei (HG 1045/2018), "
                  "iar confirmarea îl deblochează",
          "ruta": "PUT /tenants/{}/salariati/{}/pontaj"}
    st2, r2 = U.cere("PUT", "/tenants/%d/salariati/%s/pontaj" % (tid, sid),
                     {"zi": "%d-%02d-12" % (AN, LUNA), "stare": "absent_nemotivat"}, tok)
    i2["raspuns"] = {"stare": st2, "corp": str(r2)[:200]}
    s_blocat, m_blocat = d112(tok, tid)
    i2["a_blocat"] = {"declaratia_se_genereaza": s_blocat is not None, "meta": m_blocat}
    _motiv = str((m_blocat or {}).get("raspuns") or "")
    i2["temeiul_blocarii"] = ("HG 1045/2018" in _motiv and "CONFIRMAT" in _motiv)
    st_c, r_c = U.cere("POST", "/tenants/%d/pontaj/confirma" % tid, {"an": AN, "luna": LUNA}, tok)
    i2["confirmare"] = {"stare": st_c, "corp": str(r_c)[:200]}
    s_dupa, m_dupa = d112(tok, tid)
    i2["dupa_confirmare"] = {"declaratia_se_genereaza": s_dupa is not None, "meta": m_dupa}
    i2["cifrele_s_au_schimbat"] = bool(s_dupa) and s_dupa["amprenta"] != amp1
    # A TREIA CONDIȚIE ERA A MEA, nu a aplicației. Pontajul mișcă **tichetele de masă** — chiar asta
    # spune mesajul porții („Tichetele de masa (D112)… HG 1045/2018") —, iar salariatul probei n-are
    # tichete configurate. Deci o zi absentă NU are de ce să schimbe cifrele lui: salariul e lunar,
    # contribuțiile la fel. Ce se cere e poarta și revenirea; schimbarea cifrelor se MĂSOARĂ și se
    # scrie, nu se pretinde.
    i2["de_ce_nu_se_schimba_cifrele"] = (
        "salariatul probei n-are tichete de masă configurate, iar pontajul intră în D112 prin ele; "
        "salariul e lunar, deci o zi absentă nu mișcă bazele. Se consemnează ca măsurătoare, nu ca "
        "nepotrivire.") if not i2["cifrele_s_au_schimbat"] else None
    i2["OK"] = (st2 in (200, 201) and s_blocat is None and i2["temeiul_blocarii"]
                and st_c in (200, 201) and s_dupa is not None)
    scrie(i2)
    amp2 = (s_dupa or {}).get("amprenta") or amp1

    # ── 3a. BENEFICIU SUB PLAFON — nu se schimbă ────────────────────────────
    amp3a, _ = pas("3a · cadou 300 lei (= PLAFON_CADOU) → declarația NU se schimbă",
                   "PUT /tenants/{}/salariati/{}/beneficiu-lunar", "PUT",
                   "/tenants/%d/salariati/%s/beneficiu-lunar" % (tid, sid),
                   {"an": AN, "luna": LUNA, "tip": "cadou", "valoare": 300,
                    "eveniment": "craciun"}, False, amp2)

    # ── 3b. BENEFICIU PESTE PLAFON — se schimbă ─────────────────────────────
    amp3b, _ = pas("3b · cadou 500 lei (200 peste plafon) → declarația SE schimbă",
                   "PUT /tenants/{}/salariati/{}/beneficiu-lunar", "PUT",
                   "/tenants/%d/salariati/%s/beneficiu-lunar" % (tid, sid),
                   {"an": AN, "luna": LUNA, "tip": "cadou", "valoare": 500,
                    "eveniment": "craciun"}, True, amp3a)

    # ── 4. CONCEDIU MEDICAL ─────────────────────────────────────────────────
    amp4, r4 = pas("4 · certificat CM cod 01, 3 zile → declarația SE schimbă",
                   "POST /tenants/{}/salariati/{}/concedii", "POST",
                   "/tenants/%d/salariati/%s/concedii" % (tid, sid),
                   {"serie": "PB", "numar": "%d%02d%d" % (AN, LUNA, rul), "cod": "01",
                    "data_acordare": "%d-%02d-05" % (AN, LUNA),
                    "data_inceput": "%d-%02d-05" % (AN, LUNA),
                    "data_sfarsit": "%d-%02d-07" % (AN, LUNA),
                    # CODUL NUMERIC, nu textul: prima formă a trimis „ambulatoriu" și a scos
                    # **R189** — ruta scurgea mesajul lui `int()`. Se trimite `1`, care e chiar
                    # valoarea pe care codul o folosește ca implicit (`int(... or 1)`), deci nu e un
                    # cod inventat de mine; nomenclatorul închis al lui `D_10` rămâne de scris când
                    # se deschide structura D112 la sursă (datoria numită în R189).
                    "loc_prescriere": 1,
                    # `diagnostic` e un COD de cel mult 3 caractere (`D_23` în XSD), nu proză: prima
                    # formă a trimis „proba lant" (10 caractere), iar generatorul a refuzat, numind
                    # câmpul, lungimea primită ȘI maximul. Se trimite `999`, chiar valoarea pe care
                    # o folosește generatorul ca implicit — nu un cod inventat.
                    "diagnostic": "999",
                    "spitalizare": False, "zile_cm": 3,
                    "venituri_6_luni": BRUT * 6, "zile_6_luni": 126,
                    "an": AN, "luna": LUNA}, True, amp3b)

    # ── 5. ȘTERGEREA CM — declarația revine EXACT ───────────────────────────
    cmid = (r4 or {}).get("id") or ((r4 or {}).get("rand") or {}).get("id") \
        if isinstance(r4, dict) else None
    i5 = {"lant": "5 · ștergerea CM → declarația revine EXACT la amprenta de dinainte de 4",
          "ruta": "DELETE /tenants/{}/salariati/{}/concedii/{}", "cm_id": cmid}
    if not cmid:
        i5["NEPROBAT"] = ("răspunsul lui `cm_salveaza` n-a purtat id-ul certificatului, deci "
                          "ștergerea n-are subiect; se scrie, nu se sare")
        i5["OK"] = False
    else:
        st5, r5 = U.cere("DELETE", "/tenants/%d/salariati/%s/concedii/%s" % (tid, sid, cmid),
                         None, tok)
        s5, m5 = d112(tok, tid)
        i5.update({"raspuns": {"stare": st5, "corp": str(r5)[:200]}, "d112": m5,
                   "amprenta": {"dinainte_de_4": amp3b, "dupa_stergere": (s5 or {}).get("amprenta")},
                   "OK": st5 in (200, 204) and (s5 or {}).get("amprenta") == amp3b})
    scrie(i5)
    amp5 = i5.get("amprenta", {}).get("dupa_stergere") or amp4

    # ── 6. IMPORT DE ISTORIC — nu atinge declarația lunii ───────────────────
    pas("6 · istoric-declaratii-import (o depunere din 07/2026) → declarația lunii 08 NU se schimbă",
        "POST /tenants/{}/istoric-declaratii-import", "POST",
        "/tenants/%d/istoric-declaratii-import" % tid,
        {"randuri": [{"tip": "D112", "an": AN, "luna": LUNA - 1,
                      "data_depunere": "%d-%02d-20" % (AN, LUNA), "tip_cunoscut": True,
                      "avertisment": [], "ok": True}]}, False, amp5)

    # ── 7. DEPUNEREA DIN COADĂ, pe un id inexistent ─────────────────────────
    i7 = {"lant": "7 · coada/{}/depune pe id inexistent → refuz MOTIVAT, nu 500",
          "ruta": "POST /coada/{}/depune"}
    st7, r7 = U.cere("POST", "/coada/999999999/depune", {}, tok)
    motiv = json.dumps(r7, ensure_ascii=False) if isinstance(r7, dict) else str(r7)
    i7["raspuns"] = {"stare": st7, "corp": motiv[:300]}
    i7["NEPROBAT_pe_date_valide"] = (
        "depunerea reală cere un element în coadă ȘI canalul SPV; precondiția nu se poate construi "
        "prin aplicație pe firma de probă. Se exercită refuzul, care trebuie să fie motivat.")
    i7["OK"] = (st7 >= 400 and st7 != 500 and len(motiv) > 20)
    scrie(i7)

    # ── DESFACEREA pontajului: ziua se scoate, iar luna se re-confirmă ──────
    #    Fără ea, firma rămâne cu D112 blocat până când cineva confirmă — s-a întâmplat o dată, iar
    #    deblocarea a cerut un act separat. *Ce atinge o poartă o repune la loc.*
    st_d1, r_d1 = U.cere("PUT", "/tenants/%d/salariati/%s/pontaj" % (tid, sid),
                         {"zi": "%d-%02d-12" % (AN, LUNA), "stare": None}, tok)
    st_d2, r_d2 = U.cere("POST", "/tenants/%d/pontaj/confirma" % tid, {"an": AN, "luna": LUNA}, tok)
    s_fin, m_fin = d112(tok, tid)
    rez["desfacere_pontaj"] = {
        "ziua_scoasa": {"stare": st_d1, "corp": str(r_d1)[:120]},
        "luna_reconfirmata": {"stare": st_d2, "corp": str(r_d2)[:120]},
        "d112_se_genereaza_la_final": s_fin is not None, "meta": m_fin,
        "de_ce": "o zi atinsă blochează D112 până la confirmare; proba nu lasă firma blocată"}

    # ── ÎNCHEIEREA declarată: salariatul primește dată de încetare, ca lunile următoare să nu-l
    #    mai poarte. Se face prin ruta aplicației (probată în lotul D), nu prin `UPDATE` pe tabel.
    st_i, r_i = U.cere("PUT", "/tenants/%d/salariati/%s" % (tid, sid),
                       {"data_incetare": "%d-%02d-31" % (AN, LUNA)}, tok)
    rez["incheiere"] = {"stare": st_i, "corp": str(r_i)[:200],
                        "de_ce": "fără ea, fiecare rulare ar lăsa un salariat activ în D112-urile "
                                 "următoare ale firmei"}

    st_v, r_v = U.cere("POST", "/declaratii/d112/valideaza",
                       {"tenant_id": tid, "an": AN, "luna": LUNA}, tok, timeout=300)
    rez["duk"] = {"stare_http": st_v,
                  "stare": (r_v or {}).get("stare") if isinstance(r_v, dict) else str(r_v)[:200]}

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
