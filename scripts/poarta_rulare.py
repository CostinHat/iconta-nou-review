# -*- coding: utf-8 -*-
"""scripts/poarta_rulare.py — poarta de publicare (comanda 16.1, pct.1): rularea COMPLETĂ finală și reluarea după roșu. Pornită numai de scripts/poarta_lot.sh.
  (fără opțiuni)   rularea completă: verificator, pytest (nucleul + testele atinse de lot), plasa e2e din manifest; baza restaurată înainte de pytest și înainte de plasa;
                   toate treptele rulează, fără oprire la prima roșie; clasificarea față de docs/dovezi/<lot>/baza.json (scripts/poarta_clasifica.py). Cel mult două pe lot.
                   Numai ea scrie VERDE în <git-common-dir>/poarta_verdicte.log.
  --reia           reluarea după roșu: numai numele picate + testele fișierelor schimbate de la commitul roșu; cel mult două pe lot; nu e rulare completă și nu scrie VERDE.
Refuzuri (ieșire 1, cu numele): fără POARTA_PLASA_FIX=scripts/plasa_16_2.manifest, manifest nepotrivit, lipsa baza.json, baza care nu e merge-base cu main sau cu alt hash de
manifest, arbore murdar, SHA deja judecat, lot oprit, a treia rulare completă / a treia reluare, la reluare un fișier în afara celor permise (git diff --name-only <roșu>..HEAD).
Ieșire: 0 = curat, 1 = refuz sau roșu, 3 = oprire (baza s-a mișcat / a doua regresie nouă / infrastructură)."""
import datetime
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402
import poarta_clasifica as C  # noqa: E402
import poarta_lib as L  # noqa: E402

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


def main(argv):
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
    if subprocess.run(["sh", "scripts/verifica_plasa_pilot.sh"], cwd=RAD, capture_output=True).returncode:
        return refuz("verifica_plasa_pilot (poziții pilot ok fără test).")
    cb = os.path.join(RAD, "docs", "dovezi", L.lot_fisier(L.lot_baza(lot)), "baza.json")   # un lot de corecție (16.1-C2) folosește baza lotului de bază
    if not os.path.exists(cb):
        return refuz("lipsește %s (se produce cu `sh scripts/poarta_lot.sh --baza`)." % os.path.relpath(cb, RAD))
    baza = json.load(open(cb, encoding="utf-8"))
    an = baza["antet"]
    if git("merge-base", "HEAD", "main") != an["commit_baza"]:
        return refuz("sha-ul din baza.json (%s) nu e merge-base cu main (%s)." % (an["commit_baza"][:8], git("merge-base", "HEAD", "main")[:8]))
    if an["manifest_sha256"] != L.hash_fisier(os.path.join(RAD, L.MANIFEST)):
        # 16.1-C2 pct.1: manifestul poate crește numai cu rânduri pentru fișiere de test noi (prezente în diff, absente pe main)
        ref = L.manifest_refuzuri(RAD, an["commit_baza"])
        if ref:
            return refuz("manifestul curent diferă de cel din baza.json altfel decât prin fișiere noi: " + "; ".join(ref))
    if git("status", "--porcelain", "--untracked-files=normal"):
        return refuz("arborele nu e curat — poarta judecă commitul lotului.")
    if stare["oprit"]:
        return refuz("lotul e OPRIT: %s." % stare["oprit"])
    jv = os.path.join(comun, "poarta_verdicte.log")
    if os.path.exists(jv) and any(ln.split()[1:2] == [sha] and ln.split()[0] in ("VERDE", "ROSU") for ln in open(jv, encoding="utf-8")):
        return refuz("%s are deja verdict." % sha[:8])
    fisiere_lot = set(lista("diff", "--name-only", an["commit_baza"], "HEAD"))
    detalii = "scripturi_poarta: " + JL.hash_scripturi(RAD)
    T0 = time.time()
    bt = baza["teste"]
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
        trepte, cand = L.ruleaza_trepte(RAD, J, lot, ids, e2e, detalii=detalii)
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
        trepte, cand = L.ruleaza_trepte(RAD, J, lot, nucleu + atinse, None, detalii=detalii)
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
        _, din_nou = L.ruleaza_trepte(RAD, J, lot, ids, e2e, detalii=detalii, verificator=False)
        nume_noi = {t["nume"] for t in din_nou}
        cand = [t for t in cand if t["nume"] not in nume_noi and not t["nume"].endswith("::sesiune")] + din_nou
        rez = C.clasifica(cand, bt, fisiere_lot, RAD, complet)
    picate_acum = sorted(t["nume"] for t in cand if t["rezultat"] == "pica")
    noi = [n for n in picate_acum if reia and n not in picate and not any(n in r for r in rez["restanta"])]
    oprire = None
    if rez["infra"]:
        oprire = "eroare de infrastructură rămasă după o reluare: " + ", ".join(rez["infra"][:5])
    elif rez["baza_mutata"]:
        oprire = "test roșu și pe bază, nenumerotat în inventar (baza s-a mișcat): " + ", ".join(rez["baza_mutata"][:5])
    elif noi:
        oprire = "picături noi la reluare: " + ", ".join(noi[:5])
    elif stare["regresii"] and set(rez["regresie"] + rez["nou_regresie"]) - set(stare["regresii"]):
        oprire = "a doua regresie de lot nouă: " + ", ".join(sorted(set(rez["regresie"] + rez["nou_regresie"]) - set(stare["regresii"]))[:5])
    stare["regresii"] = sorted(set(stare["regresii"]) | set(rez["regresie"]) | set(rez["nou_regresie"]))
    curat = C.este_curat(rez)
    if reia:
        stare["reluari"].append({"din": rosu, "la": sha, "data": datetime.datetime.now().isoformat(timespec="seconds"), "curat": curat})
    else:
        stare["complete"].append({"sha": sha, "data": datetime.datetime.now().isoformat(timespec="seconds"), "curat": curat})
    stare["oprit"] = oprire or stare["oprit"]
    json.dump(stare, open(f_stare, "w"), indent=1)
    json.dump({"sha": sha, "picate": picate_acum, "clase": rez}, open(f_picate, "w"), indent=1, ensure_ascii=False)
    v = ("VERDE" if curat else "ROSU") if not reia else ("REIA_CURAT" if curat else "REIA_ROSU")
    dur = " · ".join("%s %ss" % (k, round(x)) for k, x in trepte.items()) + " · total %ds" % (time.time() - T0)
    mh = L.hash_fisier(os.path.join(RAD, L.MANIFEST))
    if not reia:
        open(jv, "a", encoding="utf-8").write("%s %s %s %s manifest=%s completa lot=%s\n" % (v, sha, ram, datetime.datetime.now().astimezone().isoformat(timespec="seconds"), mh, lot))
    up = os.path.join(RAD, "scripts", "poarta_ultima.txt")
    if curat and not reia:
        os.path.exists(up) and os.remove(up)
    elif not curat:
        open(up, "w").write(sha + "\n")
    open(os.path.join(RAD, ".poarta_jurnal.log"), "a", encoding="utf-8").write("    DURATE: %s %s · poarta %s · teste %d · %s · %s\n" % (
        datetime.datetime.now().astimezone().isoformat(timespec="seconds"), v, "reluare" if reia else "completă", len(cand), C.rezumat(rez), dur))
    print("[poarta] %s %s (%s) · %d teste · %s · %s" % (v, sha, ram, len(cand), C.rezumat(rez), dur))
    for k in C.CURAT:
        for n in rez[k][:20]:
            print("    %s: %s" % (k, n))
    if oprire:
        print("[poarta] OPRIT: " + oprire)
        return 3
    return 0 if curat else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
