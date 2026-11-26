"""17.5-Q12 — din brut.json al probei candidatului: rezultatul fiecăruia din cele 55 de rânduri (cod, criteriu, rezoluție, commit, rezultat, observație,
martor, sha256). Martorul unui rând e un fișier JSON în directorul probei, cu extrasul măsurătorii, capturile (cu SHA-256) și judecata pe criteriu.
Uz: construieste_rezultate_q12.py <director_proba> <sha_candidat> <iesire.tsv>
Celulele «-» (dependențe nominale) rămân «-», cu motivul, fără martor. O celulă 0 devine 1 numai când judecata de mai jos e adevărată pe măsurătoare."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

AICI = Path(__file__).resolve().parent
MINUS = "−"
DEP = {
    ("F026", "Conformitate"): "document_lipsa: balanța originală F1 la 31.07.2026 (707, rulaj creditor 1.000) nu e în aplicație; refuzul explicat rămâne, funcția deschisă (numai Costin reclasifică)",
    ("F026", "Funcțional"): "document_lipsa: balanța originală F1 la 31.07.2026 nu e în aplicație; D100 T3/2026 pasul 2 păstrează refuzul explicat",
    ("F043", "Simplitate"): "dependență: UBL coerent, validat, cu opțiunea NIR înainte de confirmare — fără documentul autentic (original de probă și hash) nu se închide; DNT-UBL-090 rămâne refuzat cu diferența spusă",
    ("F179", "Funcțional"): "postpublicare: factura nouă de furnizor la CUI 55229657 și intervalul de cel mult 30 de minute — acțiunea lui Costin (FINAL.11), după publicare",
    ("X02", "Funcțional"): "postpublicare: prima și a doua autentificare a contului junior cu timpii livrării — acțiunea lui Costin (FINAL.11), după publicare",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def g(d, *chei):
    for k in chei:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def judeca(brut, cod, crit, z):
    """-> (rezultat '1'|'0', observație, extras, capturi)."""
    s = lambda k: brut.get(k) or {}
    if cod == "F015":
        c, i = g(s("F015"), "casa", z) or {}, g(s("F015"), "istoric", z) or {}
        texte = [c.get("previz_refuz") or "", c.get("refuz_camp") or ""]
        fara_cratima = all(t and not re.search(r"(^|[\s(«„])-\d", t) and (MINUS + "9") in t for t in texte)
        ist = [x for x in (i.get("sume") or []) if x.startswith(MINUS)]
        ok = fara_cratima and bool(ist) and not any(re.match(r"^-\d", x) for x in (i.get("sume") or []))
        return ok, "refuz: %r; Istoric: %s" % (texte[0][:160], ", ".join(ist[:3])), {"casa": c, "istoric": i}, [c.get("captura"), i.get("captura")]
    if cod == "F017":
        j = g(s("F017"), "jurnal", z) or {}
        t = (j.get("rand") or {}).get("text") or ""
        ok = "soldul preluat la 31.08.2026 (din soldurile partenerilor, la preluarea firmei)" in t and "factura Sold la" not in t and bool((j.get("rand") or {}).get("original"))
        return ok, "explicația: %r; original păstrat: %s" % (t[:200], bool((j.get("rand") or {}).get("original"))), j, [j.get("captura")]
    if cod == "F018":
        p = s("F018").get(z) or {}
        pdf = p.get("pdf") or {}
        prim = p.get("principale") or []
        ok = (pdf.get("vizibil") and pdf.get("activ") and pdf.get("clicabil") and "buton-secundar" in (pdf.get("clase") or [])
              and (p.get("dupa_clic") or {}).get("tiparit") == 1 and len(prim) == 1 and prim[0][1] == "+ Fișă de partener" and prim[0][2])
        return bool(ok), "principal: %s; PDF secundar: %s; tipărire: %s" % (prim, pdf.get("clase"), p.get("dupa_clic")), p, [p.get("captura")]
    if cod in ("F022", "F169"):
        x = s("F022_F169").get(z) or {}
        o, sep = x.get("2026-10") or {}, x.get("2026-9") or {}
        if cod == "F022":
            t = o.get("coerenta") or ""
            ok = all(k in t for k in ("Balanța la", "D300", "rd.19", "rd.30", "perioadele dinainte")) and "perioade diferite sau diferență de regularizat" not in t
            return ok, "Coerență TVA: %r; septembrie: %r" % (t[:300], (sep.get("coerenta") or "")[:160]), {"10": o.get("coerenta"), "09": sep.get("coerenta"), "api": o.get("api_tva")}, [o.get("captura"), sep.get("captura")]
        inc = [c for c in (o.get("api_incrucisat") or []) if c.get("cont") in ("4427", "4426")]
        t = o.get("incrucisat") or ""
        ok = (all(c.get("reconciliere_ciorne") and c.get("ciorne") and all(n.get("nota_id") and n.get("fel") for n in c["ciorne"]) for c in inc) and inc
              and len(o.get("note") or []) >= 5 and "rotunjirea decontului" in t and (x.get("link_nota") or {}).get("evidentiata"))
        return bool(ok), "reconciliere: %s; legătura: %s" % ([c.get("reconciliere_ciorne", "")[:160] for c in inc], x.get("link_nota")), {"10": inc, "link": x.get("link_nota")}, [o.get("captura"), (x.get("link_nota") or {}).get("captura")]
    if cod == "F023":
        p = s("F023").get(z) or {}
        a, m = p.get("dupa_cantitate") or {}, p.get("manual") or {}
        ok = (p.get("dupa_articol") or {}).get("afisat") == "100,00" and a.get("valoare") == "100.00" and a.get("total") and a.get("total") == m.get("total")
        return bool(ok), "afișat %r, valoare %r, total %r / manual %r" % ((p.get("dupa_articol") or {}).get("afisat"), a.get("valoare"), a.get("total"), m.get("total")), p, [p.get("captura")]
    if cod == "F028":
        p = s("F028").get(z) or {}
        n9, n10 = p.get("09") or {}, p.get("10") or {}
        ok = ("09/2026" in (n9.get("titlu") or "") and any("(luna 09/2026)" in r for r in n9.get("rezumat") or []) and "10/2026" in (n10.get("titlu") or "")
              and not any("luna 9/2026" in r for r in n9.get("rezumat") or []))
        return bool(ok), "titlu %r; rezumat %r" % (n9.get("titlu"), (n9.get("rezumat") or [""])[:1]), p, [n9.get("captura"), n10.get("captura")]
    if cod == "F031":
        p = s("F031").get(z) or {}
        t = p.get("fata_de_balanta") or ""
        ok = all(k in t for k in ("4427", "4426", "4423", "rotunjirea decontului", "factură exclusă din decont")) and bool(p.get("legaturi_note")) and (p.get("link") or {}).get("fereastra")
        return bool(ok), "față de contabilitate: %r; legături: %d" % (t[:300], len(p.get("legaturi_note") or [])), p, [p.get("captura"), (p.get("link") or {}).get("captura")]
    if cod == "F034":
        b = s("F034")
        i, d = g(b, "inainte", z) or {}, g(b, "dupa", z) or {}
        cor = b.get("corectare") or {}
        if crit == "Design":
            sc = i.get("texte_scurte") or []
            ok = any("EXCLUSE" in t for t in sc) and not any(re.search(r"(ex|nr)\.\s*$", t.strip(" …")) for t in sc)
            return bool(ok), "rezumate: %s" % sc[:3], {"texte_scurte": sc}, [i.get("captura")]
        if crit == "Aspect":
            der = [x for k in ("derulari", "derulari_la_capat", "derulari_detalii_deschise") for x in (i.get(k) or {}).get("derulari") or [] if not x.get("xml")]
            ok = bool(der) and all(x.get("corp") for x in der)   # o singură derulare, a corpului, deschis, la capăt și cu detaliile deschise (numai XML-ul are derulare internă)
            return ok, "derulări (fără XML): %s" % der, i.get("derulari"), [i.get("captura")]
        ok = (len(d.get("op_N") or []) == 3 and "1001" in " ".join(d.get("op_N")) and "1005" in " ".join(d.get("op_N"))
              and all(g(cor, nr, "corectare", "status") == 200 for nr in ("BA-2", "BA-3")) and all(g(cor, nr, "refuz_fara_date", "status") == 422 for nr in ("BA-2", "BA-3")))
        return bool(ok), "op N în XML: %d; corectări %s; refuz fără date %s" % (len(d.get("op_N") or []), [g(cor, n, "corectare", "status") for n in ("BA-2", "BA-3")],
                                                                            [g(cor, n, "refuz_fara_date", "status") for n in ("BA-2", "BA-3")]), {"corectare": cor, "dupa": d}, [d.get("captura")]
    if cod == "F045":
        p = s("F045").get(z) or {}
        fc, fa = p.get("fara_cui") or {}, p.get("fara_adresa") or {}
        cas = fc.get("caseta") or {}
        if crit == "Conformitate":
            ok = "adresa beneficiarului" in (fa.get("camp") or "") and "emis" not in (fa.get("rezultat") or "").lower().split("nu s-a emis")[0][-5:]
            return bool(ok), "refuz adresă: %r" % (fa.get("camp") or "")[:160], fa, [fa.get("captura")]
        ok = bool(cas) and cas.get("deasupra_barei") and cas.get("in_viewport") and "codul fiscal" in (cas.get("text") or "") and "adresa beneficiarului" in (fa.get("camp") or "")
        return bool(ok), "caseta fără CUI: %s" % {k: cas.get(k) for k in ("caseta", "bara", "deasupra_barei", "in_viewport")}, p, [fc.get("captura"), fa.get("captura")]
    if cod == "F070":
        p = s("F070").get(z) or {}
        t = " ".join(p.get("temeiuri_pe_rand") or [])
        ok = "Pâinea albă este aliment" in t and "fără zahăr adăugat" in t and "Painea alba" not in t and p.get("produse_inainte") == p.get("produse_dupa")
        return bool(ok), "temei: %r; produse %s → %s" % (t[:200], p.get("produse_inainte"), p.get("produse_dupa")), p, [p.get("captura")]
    if cod == "F078":
        p = s("F078").get("603x590") or {}
        der = p.get("derulari") or []
        ok = bool(p.get("refuz")) and len(der) <= 1
        return bool(ok), "derulări: %s" % der, p, [p.get("captura")]
    if cod == "F085":
        p = s("F085").get(z) or {}
        t = json.dumps(p.get("tabel"), ensure_ascii=False) if p.get("tabel") else (p.get("text") or "")
        ok = "66: 09.08.2026" in t and "71: termen necunoscut" in t
        return bool(ok), "tabel: %s" % t[:300], p, [p.get("captura")]
    if cod == "F126":
        b = s("F126")
        a, zz = b.get("1366x768") or {}, b.get("1366x768_zoom125") or {}
        ok = (a.get("randuri") and not a.get("suprapuneri") and zz.get("randuri") and not zz.get("suprapuneri")
              and any(r["rand"][3] - r["rand"][1] > 50 for r in a.get("randuri") or []))
        return bool(ok), "100%%: %d rânduri, suprapuneri %s; 125%%: suprapuneri %s" % (len(a.get("randuri") or []), a.get("suprapuneri"), zz.get("suprapuneri")), b, [a.get("captura"), zz.get("captura")]
    if cod == "F139":
        p = s("F139").get("1366x768") or {}
        th = [t for t in p.get("antete") or [] if t["text"] in ("Transport și taxe repartizate", "Cost unitar final") or t["text"].replace("\n", " ") in ("Transport și taxe repartizate", "Cost unitar final")]
        ok = len(th) == 2 and all(t["sw"] <= t["cw"] + 1 for t in th)
        return bool(ok), "antete: %s" % [(t["text"], t["sw"], t["cw"]) for t in th], p, [p.get("captura")]
    if cod == "F179":
        p = s("F179").get(z) or {}
        t = p.get("text") or p.get("fereastra") or ""
        ok = all(k in t for k in ("4 mesaje găsite", "importată", "deja în listă", "refuzată"))
        return bool(ok), "mesajul citirii: %r" % t[:300], p, [p.get("captura")]
    if cod == "F183":
        p = s("F183").get(z) or {}
        cl = [p.get(k) for k in ("clic_0", "clic_1") if p.get(k)]
        pasi = {b[0].replace("Deschide ", ""): b[1] for b in p.get("butoane") or []}
        ok = (len(cl) == 2 and all(c.get("fereastra") in ("Mijloace fixe", "Articole și stoc inițial") for c in cl)
              and all(c.get("dupa_inapoi") == "Control fiscal" for c in cl) and bool(p.get("rerulare")) and (p.get("rerulare") or {}).get("butoane_dupa", 0) >= 1
              and all(("lei" in b[2]) for b in p.get("butoane") or [] if b[1] in ("Mijloace fixe", "Articole și stoc inițial")))   # sumele divergențelor 2131/2813/371 păstrate pe rând
        return bool(ok), "clic: %s; rerulare: %s" % ([c.get("fereastra") for c in cl], bool(p.get("rerulare"))), p, [p.get("captura_audit")] + [c.get("captura") for c in cl]
    if cod == "F252":
        p = s("F252").get("603x590") or {}
        a, b = p.get("inainte") or {}, p.get("dupa_derulare") or {}
        ok = all(x.get("titlu") and x["titlu"].get("hit") and len(x.get("semne") or []) >= 2 and all(q.get("hit") for q in x["semne"]) for x in (a, b))
        return bool(ok), "înainte: titlu %s semne %s; după: titlu %s semne %s" % ((a.get("titlu") or {}).get("hit"), [q.get("hit") for q in a.get("semne") or []],
                                                                              (b.get("titlu") or {}).get("hit"), [q.get("hit") for q in b.get("semne") or []]), p, p.get("capturi") or []
    return False, "fără judecată pentru %s %s" % (cod, crit), {}, []


def main(director, commit, iesire):
    director = Path(director).resolve()
    brut = json.loads((director / "brut.json").read_text(encoding="utf-8"))
    contract = list(csv.DictReader(open(AICI / "celule_17_5_Q12.tsv", encoding="utf-8"), delimiter="\t"))
    md = director / "martori"
    md.mkdir(exist_ok=True)
    rows = []
    for r in contract:
        cod, crit, rez = r["cod"], r["criteriu"], r["rezolutie"]
        z = rez.replace("x", "x")
        if r["E11"] == "-":
            rows.append(dict(cod=cod, criteriu=crit, rezolutie=rez, commit=commit, rezultat="-", observatie=DEP.get((cod, crit), "dependență nominală"), martor="", sha256=""))
            continue
        ok, obs, extras, capturi = judeca(brut, cod, crit, z)
        cap = [{"fisier": c, "sha256": sha(director / c)} for c in capturi if c and (director / c).exists()]
        m = {"cod": cod, "criteriu": crit, "rezolutie": rez, "commit": commit, "criteriu_de_acceptare": r["criteriu_de_acceptare"],
             "precizare_Costin_Q12": r.get("precizare_Costin_Q12", ""), "rezultat": "1" if ok else "0", "observatie": obs, "capturi": cap, "masura": extras}
        f = md / ("%s_%s_%s.json" % (cod, crit, rez))
        f.write_text(json.dumps(m, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        rows.append(dict(cod=cod, criteriu=crit, rezolutie=rez, commit=commit, rezultat="1" if ok else "0", observatie=obs.replace("\t", " ").replace("\n", " ")[:900],
                         martor=str(f.relative_to(director)), sha256=sha(f)))
    with open(iesire, "w", encoding="utf-8", newline="") as o:
        w = csv.DictWriter(o, fieldnames=["cod", "criteriu", "rezolutie", "commit", "rezultat", "observatie", "martor", "sha256"], delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    n = {k: sum(1 for x in rows if x["rezultat"] == k) for k in ("1", "0", "-")}
    print("rezultate: %s" % n)
    for x in rows:
        if x["rezultat"] == "0":
            print("  0: %s %s %s — %s" % (x["cod"], x["criteriu"], x["rezolutie"], x["observatie"][:200]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
