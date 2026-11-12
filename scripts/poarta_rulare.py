# -*- coding: utf-8 -*-
"""scripts/poarta_rulare.py — poarta de publicare (comanda 16.1, pct.1): rularea COMPLETĂ finală și reluarea după roșu. Pornită numai de scripts/poarta_lot.sh.
  (fără opțiuni)   rularea completă: verificator, pytest (nucleul + testele atinse de lot), plasa e2e din manifest; baza restaurată înainte de pytest și înainte de plasa;
                   toate treptele rulează, fără oprire la prima roșie; clasificarea față de docs/dovezi/<lot>/baza.json (scripts/poarta_clasifica.py). Cel mult două pe lot.
                   Numai ea scrie VERDE în <git-common-dir>/poarta_verdicte.log.
  --reia           reluarea după roșu: numai numele picate + testele fișierelor schimbate de la commitul roșu; cel mult două pe lot; nu e rulare completă și nu scrie VERDE.
Refuzuri (ieșire 1, cu numele): fără POARTA_PLASA_FIX=scripts/plasa_16_2.manifest, manifest nepotrivit, lipsa baza.json, baza care nu e merge-base cu main sau cu alt hash de
manifest, arbore murdar, SHA deja judecat, lot oprit, a treia rulare completă / a treia reluare, la reluare un fișier în afara celor permise (git diff --name-only <roșu>..HEAD).
Ieșire: 0 = curat, 1 = refuz sau roșu, 3 = oprire (baza s-a mișcat / a doua regresie nouă / infrastructură / a treia încercare infra consecutivă), 4 = încercare infra [17.5-U].
Încercare infra (U.2): după reluarea unică, clasa infra are numai nume `<treapta>::sesiune` (nicio probă n-a rulat), iar celelalte clase sunt goale în afară de regresiile «(a dispărut din rulare)».
Ea nu consumă o rulare: nu intră în stare[complete] / stare[reluari] / stare[regresii], nu scrie lot_picate_<lot>.json, nu setează stare[oprit] și nu scrie VERDE / ROSU, ci rândul
`INFRA <sha> <ramura> <data> lot=<lot> <motiv>` în poarta_verdicte.log și o intrare în stare[infra]. Blocul `__main__` o reia singur, în același proces și sub același lacăt, pe aceeași sha,
în același mod, după `elibereaza_port`, de cel mult 3 ori; a treia încercare consecutivă pune stare[oprit] = «infra ×3: <motiv>» și iese cu 3. Decizia e în `decide` (funcție pură)."""
import copy
import datetime
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import infra_g2 as IG  # noqa: E402
import jurnal_lot as JL  # noqa: E402
import poarta_clasifica as C  # noqa: E402
import poarta_lib as L  # noqa: E402
import publica_lot as PL  # noqa: E402

RAD = L.RAD
J = os.environ.get("POARTA_JURNALE", "/tmp")


def git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True).stdout.strip()


def lista(*a):
    return [x for x in git(*a).splitlines() if x]


def refuz(motiv):
    print("[poarta] REFUZ: " + motiv)
    return 1


def excepții(lotf):
    """Rândurile din ~/ghid_incoming/exceptii_<lot>.txt: (fișier, motiv) și hash; un rând fără motiv = None."""
    cale = os.path.expanduser("~/ghid_incoming/exceptii_%s.txt" % lotf)
    if not os.path.exists(cale):
        return {}, "lipsa"
    rez = {}
    for ln in open(cale, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        p = [x.strip() for x in (ln.split("\t") if "\t" in ln else ln.split(" | ", 1))]
        if len(p) < 2 or not p[1]:
            return None, L.hash_fisier(cale)
        rez[p[0]] = p[1]
    return rez, L.hash_fisier(cale)


def motiv_refuz_reluare(rad, baza, rosu, picate, ex, bt):
    """Refuzul mecanic al reluării (pct.1c): două `git diff --name-only`, fără variabilă de ocolire. -> motivul sau None.
    Permise: fișierele din diff-ul lotului la commitul roșu, fișierele testelor picate, fișierele din exceptii; la testele picate, aserțiunile nu pot scădea față de bază."""
    g = lambda *a: [x for x in subprocess.run(["git", *a], cwd=rad, capture_output=True, text=True).stdout.splitlines() if x]   # noqa: E731
    permise = set(g("diff", "--name-only", baza, rosu)) | {L.cheie_asertiuni(n)[0] for n in picate} | set(ex)
    straine = [x for x in g("diff", "--name-only", rosu, "HEAD") if x not in permise]
    if straine:
        return "reluarea atinge fișiere care nu erau în diff-ul lotului la commitul roșu, nici ale testelor picate, nici în exceptii: " + ", ".join(straine)
    for n in picate:
        fis, k = L.cheie_asertiuni(n)
        if L.asertiuni(rad, fis).get(k, 0) < next((t.get("asertiuni", 0) for t in bt if L.cheie_asertiuni(t["nume"]) == (fis, k)), 0):
            return "numărul de aserțiuni din %s a scăzut față de bază." % n
    return None


def prag_faza(rad, lotf, faza):
    """Rândul `max <faza> <secunde>` din scripts/praguri_<lot>.txt al lotului curent (T.5): secundele sau None (un lot fără rând `max`, cum e 17.5-T, nu are ce depăși)."""
    try:
        for ln in open(os.path.join(rad, "scripts", "praguri_%s.txt" % lotf), encoding="utf-8"):
            m = re.match(r"max\s+(\S+)\s+(\d+)", ln)
            if m and m.group(1) == faza:
                return int(m.group(2))
    except OSError:
        pass
    return None


def log_incarcare(lotf):
    """Textul fișierului ~/ghid_incoming/incarcare_poarta_<lot>.log al veghei arhitectului (POARTA_LOG_INCARCARE îl mută numai în probe) sau None când lipsește."""
    cale = os.environ.get("POARTA_LOG_INCARCARE") or os.path.expanduser("~/ghid_incoming/incarcare_poarta_%s.log" % lotf)
    try:
        return open(cale, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def remasoara_g2(lot, lotf, rad, faza, f):
    """[17.5-T, T.5] Chemată de `poarta_lib.ruleaza_trepte` la sfârșitul treptelor poarta_pytest / poarta_plasa (`f["id"]` = rularea din jurnal). Dacă durata depășește rândul `max <faza>` al lotului și
    `infra_g2.decide` spune «infra» (încărcare străină susținută în fereastră, dovedită în log), prima măsurare se marchează în jurnal (rând «sfarsit» «infra_g2», motiv și durata ei) și se întoarce
    True = poarta re-măsoară numai acea treaptă, o singură dată (nimic în stare[complete] / stare[reluari], nimic în poarta_verdicte.log sau poarta_ultima.txt). Altfel False: depășirea rămâne STOP la publicare."""
    prag = prag_faza(rad, lotf, faza)
    if prag is None:
        return False
    rl = next((x for x in JL.rulari(JL._citeste(JL.cale_jurnal()), lot) if x["id"] == f.get("id")), None)
    if not rl or rl["secunde"] is None:
        return False
    dec = IG.decide(faza, rl["secunde"], prag, rl["inceput"], rl["sfarsit"], log_incarcare(lotf))
    if dec["decizie"] != "infra":
        return False
    JL.marcheaza_infra_g2(lot, f["id"], dec["motiv"], rl["secunde"])
    print("[poarta] %s: %ss > %ss, %s (ora %s, cpu %d%% pe interval): prima măsurare marcată «infra_g2», re-măsurare" % (
        faza, rl["secunde"], prag, dec["motiv"], dec["dovada"]["ora"], dec["dovada"]["cpu"]))
    return True


def e_rulare_infra(rez):
    """«Rulare infra» (U.2): clasa infra nu e goală și are numai nume terminate în `::sesiune`, iar nicio altă clasă din `poarta_clasifica.CURAT` nu are intrări, în afară de regresiile cu sufixul
    «(a dispărut din rulare)» (consecința unei trepte fără raport). Cazul mixt (o picătură reală, o regresie fără sufix, o picătură infra cu raport) NU e rulare infra."""
    if not rez["infra"] or not all(n.endswith("::sesiune") for n in rez["infra"]):
        return False
    for k in C.CURAT:
        if k == "infra":
            continue
        if k == "regresie":
            if any(not n.endswith("(a dispărut din rulare)") for n in rez[k]):
                return False
        elif rez[k]:
            return False
    return True


def decide(stare, rez, reia, noi, sha, acum, motiv_infra="", rosu=None, tip_infra=""):
    """Funcția pură a deciziei de după o rulare (U.2d): ce se numără, ce se scrie, ce cod iese. Nu scrie nimic; `main` scrie numai ce cere ea.
    -> {infra, curat, oprit (valoarea finală a lui stare[oprit]), stare (copia nouă), scrie_picate, verdict (VERDE|ROSU|REIA_CURAT|REIA_ROSU|INFRA), linie (rândul din poarta_verdicte.log sau None),
    ultima (scrie|sterge|None pentru scripts/poarta_ultima.txt), cod}. `noi` = picăturile noi la o reluare, `rosu` = commitul roșu al reluării."""
    st = copy.deepcopy(stare)
    st.setdefault("infra", [])
    if e_rulare_infra(rez):
        st["infra"].append({"sha": sha, "data": acum, "motiv": motiv_infra, "tip": tip_infra})
        trei = len(st["infra"]) >= 3
        if trei:
            # [17.5-T, T.6f] trei căderi ale probei de mediu cu <failure> și același prim rând de mesaj = regresie probabilă, nu mediu
            ultimele = st["infra"][-3:]
            if all(x.get("tip") == "aserțiune" and x["motiv"] == ultimele[0]["motiv"] for x in ultimele):
                st["oprit"] = "infra ×3: aserțiune repetată, regresie probabilă: " + motiv_infra
            else:
                st["oprit"] = "infra ×3: " + motiv_infra
        return {"infra": True, "curat": False, "oprit": st.get("oprit"), "stare": st, "scrie_picate": False, "verdict": "INFRA", "linie": "INFRA", "ultima": None, "cod": 3 if trei else 4}
    oprire = None
    if rez["infra"]:
        oprire = "eroare de infrastructură rămasă după o reluare: " + ", ".join(rez["infra"][:5])
    elif rez["baza_mutata"]:
        oprire = "test roșu și pe bază, nenumerotat în inventar (baza s-a mișcat): " + ", ".join(rez["baza_mutata"][:5])
    elif noi:
        oprire = "picături noi la reluare: " + ", ".join(noi[:5])
    elif st["regresii"] and set(rez["regresie"] + rez["nou_regresie"]) - set(st["regresii"]):
        oprire = "a doua regresie de lot nouă: " + ", ".join(sorted(set(rez["regresie"] + rez["nou_regresie"]) - set(st["regresii"]))[:5])
    st["regresii"] = sorted(set(st["regresii"]) | set(rez["regresie"]) | set(rez["nou_regresie"]))
    curat = C.este_curat(rez)
    if reia:
        st["reluari"].append({"din": rosu, "la": sha, "data": acum, "curat": curat})
    else:
        st["complete"].append({"sha": sha, "data": acum, "curat": curat})
    st["oprit"] = oprire or st["oprit"]
    st["infra"] = []                         # o rulare care nu e infra golește încercările consecutive
    v = ("VERDE" if curat else "ROSU") if not reia else ("REIA_CURAT" if curat else "REIA_ROSU")
    ultima = "sterge" if curat and not reia else ("scrie" if not curat else None)
    return {"infra": False, "curat": curat, "oprit": oprire, "stare": st, "scrie_picate": True, "verdict": v, "linie": None if reia else v, "ultima": ultima,
            "cod": 3 if oprire else (0 if curat else 1)}


def scrie_stare(d, f_stare, f_picate, sha, picate_acum, rez):
    """Scrie fișierele de stare cerute de `decide`: lot_stare_<lot>.json întotdeauna, lot_picate_<lot>.json numai când `scrie_picate` (o încercare infra nu îl scrie)."""
    json.dump(d["stare"], open(f_stare, "w"), indent=1)
    if d["scrie_picate"]:
        json.dump({"sha": sha, "picate": picate_acum, "clase": rez}, open(f_picate, "w"), indent=1, ensure_ascii=False)


def _o_linie(text, lungime=300):
    """Text pe o singură linie, fără tab și fără caractere de control (rândul INFRA din poarta_verdicte.log)."""
    return re.sub(r"[\x00-\x1f\x7f]", " ", text).strip()[:lungime]


def main(argv):
    """`_main` plus oprirea cerută de o treaptă (`poarta_lib.OprirePoarta`, ex. proba de mediu căzută în re-măsurarea G2): stare[oprit] = motivul, ieșire 3, fără VERDE / ROSU / INFRA."""
    try:
        return _main(argv)
    except L.OprirePoarta as e:
        lotf = L.lot_fisier(JL.lot_curent())
        f_stare = os.path.join(git("rev-parse", "--path-format=absolute", "--git-common-dir"), "lot_stare_%s.json" % lotf)
        stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {"complete": [], "reluari": [], "regresii": [], "oprit": None}
        stare["oprit"] = str(e)
        json.dump(stare, open(f_stare, "w"), indent=1)
        print("[poarta] OPRIT: " + str(e))
        return 3


def _main(argv):
    reia = "--reia" in argv
    lot = JL.lot_curent()
    lotf = L.lot_fisier(lot)
    comun = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    f_stare, f_picate = os.path.join(comun, "lot_stare_%s.json" % lotf), os.path.join(comun, "lot_picate_%s.json" % lotf)
    stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {"complete": [], "reluari": [], "regresii": [], "oprit": None}
    ram, sha = git("symbolic-ref", "--short", "HEAD"), git("rev-parse", "HEAD")
    if not ram or ram == "main":
        return refuz("poarta de publicare rulează pe ramura lotului (acum: %s)." % (ram or "HEAD detașat"))
    manifest = os.environ.get("POARTA_PLASA_FIX", "")
    if not manifest or os.path.abspath(os.path.join(RAD, manifest)) != os.path.join(RAD, L.MANIFEST):
        return refuz("fără POARTA_PLASA_FIX=%s nu există publicare (selecția veche rămâne doar diagnostic: POARTA_DIAGNOSTIC=1)." % L.MANIFEST)
    if subprocess.run(["./venv/bin/python", "scripts/genereaza_manifest_plasa.py", "--verifica", L.MANIFEST], cwd=RAD).returncode:
        return refuz("manifestul nu se potrivește cu fișierele (vezi mai sus).")
    if subprocess.run(["./venv/bin/python", "scripts/inventar_restante.py", "valideaza"], cwd=RAD).returncode:
        return refuz("inventarul scripts/poarta_e2e_restante.txt are rânduri fără ID, clasă sau număr.")
    inv_ref = C.manifest_invalide(os.path.join(RAD, L.MANIFEST))
    if inv_ref:
        return refuz("manifestul conține teste invalide după inventar (16.1-C3, pct.5): " + "; ".join(inv_ref))
    if subprocess.run(["sh", "scripts/verifica_plasa_pilot.sh"], cwd=RAD, capture_output=True).returncode:
        return refuz("verifica_plasa_pilot (poziții pilot ok fără test).")
    cb = os.path.join(RAD, "docs", "dovezi", L.lot_fisier(L.lot_baza(lot)), "baza.json")   # lotul își are baza lui (16.1-C3) sau, ca un lot de corecție (16.1-C2), moștenește baza lotului de bază
    if not os.path.exists(cb):
        return refuz("lipsește %s (se produce cu `sh scripts/poarta_lot.sh --baza`)." % os.path.relpath(cb, RAD))
    baza = json.load(open(cb, encoding="utf-8"))
    an = baza["antet"]
    if git("merge-base", "HEAD", "main") != an["commit_baza"]:
        return refuz("sha-ul din baza.json (%s) nu e merge-base cu main (%s)." % (an["commit_baza"][:8], git("merge-base", "HEAD", "main")[:8]))
    if an["manifest_sha256"] != L.hash_fisier(os.path.join(RAD, L.MANIFEST)):
        # 16.1-C2 pct.1: manifestul poate crește numai cu rânduri pentru fișiere de test noi (prezente în diff, absente pe main)
        ref = L.manifest_refuzuri(RAD, an["commit_baza"], modificabile=L.plasa_modificabile(RAD, lotf))
        if ref:
            return refuz("manifestul curent diferă de cel din baza.json altfel decât prin fișiere noi: " + "; ".join(ref))
    if git("status", "--porcelain", "--untracked-files=normal"):
        return refuz("arborele nu e curat — poarta judecă commitul lotului.")
    ref_contract = PL.proba_contract(RAD, lot)   # [17.5-T, T.8] contractul dovezilor la începutul oricărei rulări, pe HEAD: roșu = refuz înainte de prima treaptă și de T0, fără INFRA și fără scriere în lot_stare
    if ref_contract:
        return refuz("proba_contract: " + "; ".join(ref_contract))
    if stare["oprit"]:
        return refuz("lotul e OPRIT: %s." % stare["oprit"])
    jv = os.path.join(comun, "poarta_verdicte.log")
    if os.path.exists(jv) and any(ln.split()[1:2] == [sha] and ln.split()[0] in ("VERDE", "ROSU") for ln in open(jv, encoding="utf-8")):
        return refuz("%s are deja verdict." % sha[:8])
    fisiere_lot = set(lista("diff", "--name-only", an["commit_baza"], "HEAD"))
    detalii = "scripturi_poarta: " + JL.hash_scripturi(RAD)
    T0 = time.time()
    bt = baza["teste"]
    cb_g2 = lambda faza, f: remasoara_g2(lot, lotf, RAD, faza, f)   # noqa: E731
    if reia:
        if len(stare["reluari"]) >= 2:
            return refuz("a treia reluare pe lot (cel mult două).")
        rosu = open(os.path.join(RAD, "scripts", "poarta_ultima.txt")).read().strip() if os.path.exists(os.path.join(RAD, "scripts", "poarta_ultima.txt")) else ""
        if not rosu or subprocess.run(["git", "merge-base", "--is-ancestor", rosu, "HEAD"], cwd=RAD).returncode:
            return refuz("nu există commit roșu strămoș al lui HEAD (scripts/poarta_ultima.txt).")
        picate = json.load(open(f_picate))["picate"]
        ex, hex_ = excepții(lotf)
        if ex is None:
            return refuz("un rând din exceptii_%s.txt nu are motiv." % lotf)
        if stare.get("exceptii_sha") not in (None, hex_):
            return refuz("hash-ul exceptiilor s-a schimbat de la prima reluare (%s -> %s)." % (stare["exceptii_sha"][:12], hex_[:12]))
        stare.setdefault("exceptii_sha", hex_)
        json.dump(stare, open(f_stare, "w"), indent=1)   # hash-ul de la prima reluare rămâne fixat
        with L.faza(lot, "exceptii", "exceptii_sha256=%s" % hex_) as f:
            f["rezultat"] = "ok"
        motiv = motiv_refuz_reluare(RAD, an["commit_baza"], rosu, picate, ex, bt)
        if motiv:
            return refuz(motiv)
        # testele fișierelor schimbate de la commitul roșu (derivate din cod, nivelul „direct”), numai cele comparabile cu baza (nucleul sau fișiere din diff-ul lotului)
        import perimetru as P
        import poarta_scurta as S
        P.BAZA = rosu
        derivate, _incerte, *_ = S.selectie(P.atinse_din_git(), "direct")
        comparabile = set(L.fisiere_nucleu(RAD)) | fisiere_lot
        man = {os.path.basename(x) for x in L.fisiere_manifest(RAD)}
        ids = sorted({n for n in picate if not n.startswith(("verificator", "pytest::")) and "e2e_" not in n} | {t for t in derivate if t in comparabile})
        e2e = sorted({os.path.basename(L.cheie_asertiuni(n)[0]) for n in picate if "e2e_" in n} | {os.path.basename(x) for x in fisiere_lot if os.path.basename(x) in man})
        trepte, cand = L.ruleaza_trepte(RAD, J, lot, ids, e2e, detalii=detalii, dupa_treapta=cb_g2)
        complet = False
    else:
        if len(stare["complete"]) >= 2:
            # 16.1-C1 pct.4: a treia rulare completă numai cu rândul „rulare_completa 3 | motiv: …” din exceptii_<lot>.txt (scris de arhitect); hash-ul intră în jurnal
            ex, hex_ = excepții(lotf)
            if len(stare["complete"]) > 2 or not ex or not ex.get("rulare_completa 3", "").startswith("motiv:") or stare.get("rulare3_exceptii_sha"):
                return refuz("a treia rulare completă pe lot (cel mult două: prima și finala; a treia numai cu rândul „rulare_completa 3 | motiv: …” din exceptii_%s.txt, o singură dată)." % lotf)
            stare["rulare3_exceptii_sha"] = hex_
            json.dump(stare, open(f_stare, "w"), indent=1)
            with L.faza(lot, "exceptii", "rulare_completa_3 exceptii_sha256=%s" % hex_) as f:
                f["rezultat"] = "ok"
        nucleu = L.fisiere_nucleu(RAD)
        atinse = sorted(x for x in fisiere_lot if x.endswith(".py") and os.path.basename(x).startswith("test_") and x not in nucleu and os.path.exists(os.path.join(RAD, x)))
        trepte, cand = L.ruleaza_trepte(RAD, J, lot, nucleu + atinse, None, detalii=detalii, dupa_treapta=cb_g2)
        complet = True
    # infrastructură: o singură reluare a testelor afectate
    rez = C.clasifica(cand, bt, fisiere_lot, RAD, complet)
    if rez["infra"]:
        print("[poarta] infrastructură (reluare unică): " + ", ".join(rez["infra"][:10]))
        ids = [n for n in rez["infra"] if "e2e_" not in n and not n.endswith("::sesiune")]
        e2e = sorted({os.path.basename(L.cheie_asertiuni(n)[0]) for n in rez["infra"] if "e2e_" in n and not n.endswith("::sesiune")})
        if any(n == "pytest::sesiune" for n in rez["infra"]):
            ids = L.fisiere_nucleu(RAD)
        if any(n == "plasa_e2e::sesiune" for n in rez["infra"]):
            e2e = [os.path.basename(x) for x in L.fisiere_manifest(RAD)]
        _, din_nou = L.ruleaza_trepte(RAD, J, lot, ids, e2e, detalii=detalii, verificator=False, dupa_treapta=cb_g2)
        nume_noi = {t["nume"] for t in din_nou}
        cand = [t for t in cand if t["nume"] not in nume_noi and not t["nume"].endswith("::sesiune")] + din_nou
        rez = C.clasifica(cand, bt, fisiere_lot, RAD, complet)
    picate_acum = sorted(t["nume"] for t in cand if t["rezultat"] == "pica")
    noi = [n for n in picate_acum if reia and n not in picate and not any(n in r for r in rez["restanta"])]
    acum = datetime.datetime.now().isoformat(timespec="seconds")
    motiv_infra = _o_linie("; ".join("%s: %s" % (t["nume"], t.get("mesaj", "")) for t in cand if t["nume"] in rez["infra"]))
    tip_infra = next((t["tip"] for t in cand if t["nume"] in rez["infra"] and t.get("tip")), "")
    d = decide(stare, rez, reia, noi, sha, acum, motiv_infra, rosu if reia else None, tip_infra)
    stare = d["stare"]
    curat, v, oprire = d["curat"], d["verdict"], d["oprit"] if not d["infra"] else None
    scrie_stare(d, f_stare, f_picate, sha, picate_acum, rez)
    dur = " · ".join("%s %ss" % (k, round(x)) for k, x in trepte.items()) + " · total %ds" % (time.time() - T0)
    mh = L.hash_fisier(os.path.join(RAD, L.MANIFEST))
    data_v = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    if d["linie"] == "INFRA":
        open(jv, "a", encoding="utf-8").write("INFRA %s %s %s lot=%s %s\n" % (sha, ram, data_v, lot, motiv_infra))
    elif d["linie"]:
        open(jv, "a", encoding="utf-8").write("%s %s %s %s manifest=%s completa lot=%s\n" % (v, sha, ram, data_v, mh, lot))
    up = os.path.join(RAD, "scripts", "poarta_ultima.txt")
    if d["ultima"] == "sterge":
        os.path.exists(up) and os.remove(up)
    elif d["ultima"] == "scrie":
        open(up, "w").write(sha + "\n")
    open(os.path.join(RAD, ".poarta_jurnal.log"), "a", encoding="utf-8").write("    DURATE: %s %s · poarta %s · teste %d · %s · %s\n" % (
        datetime.datetime.now().astimezone().isoformat(timespec="seconds"), v, "reluare" if reia else "completă", len(cand), C.rezumat(rez), dur))
    print("[poarta] %s %s (%s) · %d teste · %s · %s" % (v, sha, ram, len(cand), C.rezumat(rez), dur))
    for k in C.CURAT:
        for n in rez[k][:20]:
            print("    %s: %s" % (k, n))
    if d["infra"]:
        print("[poarta] INFRA (încercarea %d, nu consumă o rulare): %s" % (len(stare["infra"]), motiv_infra))
        if d["cod"] == 3:
            print("[poarta] OPRIT: " + stare["oprit"])
        return d["cod"]
    if oprire:
        print("[poarta] OPRIT: " + oprire)
    return d["cod"]


if __name__ == "__main__":
    incercari = 0
    while True:
        rc = main(sys.argv[1:])
        incercari += 1
        if rc != 4:
            break
        if incercari >= 3:      # a treia încercare infra consecutivă iese cu 3 din `decide`; plasa de siguranță
            rc = 3
            break
        import verificator_design as VD
        VD.elibereaza_port(8019, lot=JL.lot_curent())      # între încercări (U.1)
        print("[poarta] relansare după încercarea infra %d, pe aceeași sha, în același mod" % incercari)
    sys.exit(rc)
