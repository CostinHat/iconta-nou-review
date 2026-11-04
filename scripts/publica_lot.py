# -*- coding: utf-8 -*-
"""scripts/publica_lot.py — contractul de publicare (comanda 16.1, pct.4); chemat numai de scripts/publica_lot.sh. Ordinea: începutul fazei „publicare”, ZIP-ul, verificările
(raport, poartă, jurnal, perimetru, bază, reluări, jurnalul verificării), verdictul PASS/STOP calculat din jurnal față de scripts/praguri_<lot>.txt, `PASS <sha>` în
<git-common-dir>/publica_verdicte.log. Fără PASS nu se mută `main` (scripts/githooks/reference-transaction) și nu se împinge pe main (scripts/githooks/pre-push),
iar restartul din post-commit refuză. Sfârșitul fazei „publicare” îl scrie publica_lot.sh după push.
Regula strămoșului (16.1-C1, 16.1-C2 pct.4): verdictul VERDE al rulării complete finale și rândurile din jurnal_verificare.csv sunt produse pe un commit C (ultima rulare completă din
starea lotului) și rămân valabile pentru HEAD numai dacă C e strămoș al lui HEAD și diff-ul C..HEAD atinge numai căile din `ancestor_refuzuri`. Apelabilă separat, fără publicare:
  publica_lot.py --verifica <C> <HEAD> [lot]   (lotul din LOT sau din ramura curentă; hook-urile reference-transaction și pre-push o chemă cu lotul din rândul PASS)
Ieșire: 0 = PASS, 1 = STOP (nepublicat, cu cifra sau motivul)."""
import csv
import json
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402
import poarta_clasifica as C  # noqa: E402
import poarta_lib as L  # noqa: E402

RAD = L.RAD
ACASA = os.path.expanduser("~")
#: fișierele porții și ale contractului: nu se ating în afara loturilor marcate „unelte” în scripts/praguri_<lot>.txt
PAZITE = ("scripts/poarta_lot.sh", "scripts/publica_lot.sh", "scripts/baza_test.sh", "scripts/poarta_nucleu.txt", "conftest.py")
FRAZA_RISC = ("confinarea la fișiere deja atinse nu dovedește că fiecare modificare e legată de testul picat; "
              "poarta finală dovedește comportamentul din manifest, nu justificarea fiecărei linii")


#: depozitul în care se judecă commiturile; `--verifica` din hook-uri îl ia din directorul curent al hook-ului (None = worktree-ul scriptului)
DEP = None


def git(*a):
    return subprocess.run(["git", *a], cwd=DEP or RAD, capture_output=True, text=True).stdout.strip()


def _git_brut(*a):
    return subprocess.run(["git", *a], cwd=DEP or RAD, capture_output=True, text=True)


def _fisier_la(commit, cale):
    r = _git_brut("show", "%s:%s" % (commit, cale))
    return r.stdout.splitlines() if r.returncode == 0 else None


def ancestor_refuzuri(c, head, lotf):
    """Regula strămoșului: -> (refuzuri, fișierele din diff); refuzuri goale = verdictul și rândurile produse pe C sunt valabile pentru HEAD."""
    if _git_brut("cat-file", "-e", c + "^{commit}").returncode or _git_brut("cat-file", "-e", head + "^{commit}").returncode:
        return ["C (%s) sau HEAD (%s) nu e commit" % (c[:12], head[:12])], []
    if _git_brut("merge-base", "--is-ancestor", c, head).returncode:
        return ["C (%s) nu e strămoș al lui HEAD (%s)" % (c[:12], head[:12])], []
    dovezi = "docs/dovezi/%s/" % lotf
    csv_cale = dovezi + "jurnal_verificare.csv"
    # CLAUDE.md nu e permis (16.1-C2 pct.4): regulile se schimbă înainte de C sau în lotul următor
    exacte = {csv_cale, dovezi + "registre_%s.md" % lotf, "DEFICIENTE.md", "DECIZII.md", "PREDARE_LANT.md"}
    iesire = _git_brut("diff", "--raw", "-z", "--no-renames", c, head).stdout.split("\0")
    refuzuri, fisiere = [], []
    for meta, cale in zip(iesire[0::2], iesire[1::2]):
        mod_vechi, mod_nou, _, _, stare = meta.lstrip(":").split()
        fisiere.append(cale)
        capturi = cale.startswith(dovezi + "capturi/") and cale.endswith(".png") and "/" not in cale[len(dovezi + "capturi/"):]
        if cale not in exacte and not capturi:
            refuzuri.append("%s: cale în afara listei permise" % cale)
        elif stare not in ("A", "M"):
            refuzuri.append("%s: schimbare %s (numai adăugare sau modificare)" % (cale, stare))
        elif mod_nou != "100644" or (stare == "M" and mod_vechi != mod_nou):
            refuzuri.append("%s: mod %s -> %s (fișier obișnuit, mod neschimbat)" % (cale, mod_vechi, mod_nou))
    if csv_cale in fisiere:
        vechi, nou = _fisier_la(c, csv_cale) or [], _fisier_la(head, csv_cale) or []
        if nou[:len(vechi)] != vechi:
            refuzuri.append("%s: un rând existent la C a fost modificat sau șters" % csv_cale)
    return refuzuri, fisiere


def pornire_stop(pornire, lot, unelte):
    """Proveniența pornirii (16.1-C2 pct.2): un singur rând „pornire”; marcaj de coadă valid sau, numai într-un lot „unelte” fără alt rând „pornire”, „reconstituit”. -> motivele de STOP."""
    if not pornire:
        return ["lipsă pornire"]
    if len(pornire) > 1:
        return ["jurnalul are %d rânduri „pornire” pentru lot (se cere unul singur)" % len(pornire)]
    if "reconstituit" in pornire[0][8]:
        return [] if unelte else ["rândul „pornire” e reconstituit, dar lotul nu e „unelte” (un lot de produs pornește numai din coadă)"]
    if not JL.marca_valida(pornire[0], lot):
        return ["rândul „pornire” nu are marcajul de proveniență al cozii (un lot de produs pornește numai din coadă)"]
    return []


def jurnal_verificare_stop(rr, pasi, c, baza, mx, rad=None):
    """Jurnalul verificării pe pas (16.1-C2 pct.3): rândurile pe alt sha decât C sunt ignorate; rândurile pe C trebuie „trece” cu captură existentă, iar fiecare pas are rând pe C;
    rundele verificatorului independent (sha distincte, ≠ baza, cu verificator=Haiku, pe pașii „după”) nu depășesc `mx`. -> motivele de STOP."""
    stop = []
    pe_c = [r for r in rr if r["commit"] == c]
    for r in pe_c:
        if r["verdict"] != "trece":
            stop.append("rândul %s din jurnal_verificare.csv (pe C): %s" % (r["pas"], r["verdict"]))
        if not os.path.exists(r["captura"] if os.path.isabs(r["captura"]) else os.path.join(rad or RAD, r["captura"])):
            stop.append("rândul %s: captura lipsește" % r["pas"])
    stop += ["pasul „%s” nu are rând pe C în jurnal_verificare.csv" % p for p in pasi if p not in {r["pas"] for r in pe_c}]
    runde = {r["commit"] for r in rr if "haiku" in r["verificator"].lower() and r["commit"] != baza and (not pasi or r["pas"] in pasi)}
    if len(runde) > mx:
        stop.append("rundele verificatorului: %d > runde_verificator_max %d (cheie lipsă = 0)" % (len(runde), mx))
    return stop


def verifica(lot, sha, comun, sirul_zip):
    """-> listă de motive de STOP (goală = PASS)."""
    lotf = L.lot_fisier(lot)
    stop = []
    # praguri: fișierul există, hash-ul = cel din jurnal la „pornire”
    praguri = os.path.join(RAD, "scripts", "praguri_%s.txt" % lotf)
    rows = [r for r in JL._citeste(JL.cale_jurnal()) if r[0] == lot and len(r) > 8]
    pornire = [r for r in rows if r[1] == "pornire" and r[2] == "inceput"]
    if not pornire:
        return ["lipsă pornire"]
    if not os.path.exists(praguri) or "lipsa_praguri" in [r[5] for r in rows if r[1] == "pornire" and r[2] == "sfarsit"]:
        return ["lipsă praguri"]
    if "praguri_sha256=%s" % L.hash_fisier(praguri) not in pornire[-1][8]:
        stop.append("pragurile s-au modificat după pornire (hash diferit de cel din jurnal)")
    unelte = open(praguri, encoding="utf-8").readline().strip().lower() == "unelte"
    stop += pornire_stop(pornire, lot, unelte)
    # poarta: VERDE pe HEAD, rulare completă finală, zero regresii, lot neoprit
    f_stare = os.path.join(comun, "lot_stare_%s.json" % lotf)
    stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {}
    if not stare or stare.get("oprit") or not stare["complete"] or not stare["complete"][-1]["curat"]:
        stop.append("starea lotului nu arată o rulare completă curată (oprit=%s)" % stare.get("oprit"))
    c = stare["complete"][-1]["sha"] if stare and stare["complete"] else sha
    refuzuri, fisiere_c = ancestor_refuzuri(c, sha, lotf)
    stop += ["regula strămoșului: " + m for m in refuzuri]
    # raportul
    raport = os.path.join(ACASA, "lot_%s_raport.md" % lotf)
    if not os.path.exists(raport) or not os.path.getsize(raport):
        stop.append("lipsește raportul %s" % raport)
    else:
        text = open(raport, encoding="utf-8").read()
        if c not in text:
            stop.append("raportul nu conține sha-ul lui C (%s)" % c)
        if c != sha and (sha in text or sha[:8] in text):
            stop.append("raportul conține sha-ul lui HEAD (%s); numește numai C" % sha[:8])
    jv = os.path.join(comun, "poarta_verdicte.log")
    if not any(ln.startswith("VERDE %s " % c) and " completa " in ln for ln in open(jv, encoding="utf-8")) if os.path.exists(jv) else True:
        stop.append("lipsește verdictul VERDE al rulării complete finale pe %s" % c[:8])
    try:
        clase = json.load(open(os.path.join(comun, "lot_picate_%s.json" % lotf)))["clase"]
        for k in C.CURAT:
            if clase.get(k):
                stop.append("clasificarea porții are %d × %s" % (len(clase[k]), k))
    except OSError:
        stop.append("lipsește clasificarea porții")
    # faze obligatorii în jurnal
    for faza in JL.FAZE_OBLIGATORII:
        ev = [r for r in rows if r[1] == faza]
        if faza == "publicare":
            if not any(r[2] == "inceput" for r in ev):
                stop.append("faza „publicare” nu are început")
            continue
        sf = {r[6]: r for r in ev if r[2] == "sfarsit"}
        ultimul = [r for r in ev if r[2] == "inceput"][-1:]
        if not ultimul:
            stop.append("faza „%s” lipsește din jurnal" % faza)
        elif ultimul[0][6] not in sf or sf[ultimul[0][6]][5] == "intrerupt":
            stop.append("faza „%s” e fără sfârșit sau întreruptă" % faza)
    # perimetrul uneltelor
    cb = os.path.join(RAD, "docs", "dovezi", L.lot_fisier(L.lot_baza(lot)), "baza.json")
    baza = git("merge-base", sha, "main")
    diff = git("diff", "--name-only", baza, sha).splitlines()
    if not unelte:
        atinse = [f for f in PAZITE if f in diff]
        if atinse:
            stop.append("lotul nu e marcat „unelte”, dar atinge: " + ", ".join(atinse))
    # manifestul (16.1-C2 pct.1): poate crește numai cu rânduri pentru fișiere de test noi (prezente în diff, absente pe main); orice altă diferență = refuz cu numele
    if os.path.exists(cb):
        ab = json.load(open(cb, encoding="utf-8"))["antet"]
        if ab["manifest_sha256"] != L.hash_fisier(os.path.join(RAD, L.MANIFEST)):
            stop += ["manifestul: " + m for m in L.manifest_refuzuri(DEP or RAD, ab["commit_baza"])]
    # baza
    if not os.path.exists(cb):
        stop.append("lipsește baza.json")
    else:
        an = json.load(open(cb, encoding="utf-8"))["antet"]
        if an["commit_baza"] != baza:
            stop.append("baza.json e pentru %s, nu pentru %s" % (an["commit_baza"][:8], baza[:8]))
    # reluări
    if stare.get("reluari") and "diff-ul reluărilor" not in (open(raport, encoding="utf-8").read() if os.path.exists(raport) else ""):
        stop.append("a existat reluare, dar raportul nu are secțiunea „diff-ul reluărilor”")
    if stare.get("reluari") and FRAZA_RISC not in open(raport, encoding="utf-8").read():
        stop.append("raportul nu are fraza de risc rezidual a reluărilor")
    # jurnalul verificării pe pas (16.1-C2 pct.3): rândurile pe alt sha decât C rămân în fișier și sunt ignorate; numai rândurile pe C trebuie „trece”, iar fiecare pas are rând pe C
    cv = os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    if os.path.exists(cv):
        pasi_f = os.path.join(RAD, "docs", "dovezi", lotf, "pasi.txt")
        pasi = [ln.strip() for ln in open(pasi_f, encoding="utf-8") if ln.strip()] if os.path.exists(pasi_f) else []
        rr = list(csv.DictReader(open(cv, encoding="utf-8")))
        mx = 0
        for ln in open(praguri, encoding="utf-8"):
            m = re.search(r"runde_verificator_max:\s*(\d+)", ln)
            if m:
                mx = int(m.group(1))
        stop += jurnal_verificare_stop(rr, pasi, c, baza, mx)
    elif not unelte:
        stop.append("lipsește jurnal_verificare.csv")
    # backup-ul uneltelor
    if unelte and not os.path.exists(os.path.join(ACASA, "backup_%s" % lotf, "CLAUDE.md")):
        stop.append("lipsește backup-ul ~/backup_%s/ (scripts/ și CLAUDE.md)" % lotf)
    # ZIP-ul
    if not os.path.exists(sirul_zip):
        stop.append("lipsește ZIP-ul %s" % sirul_zip)
    else:
        z = zipfile.ZipFile(sirul_zip)
        if z.read("sha.txt").decode().strip() != sha:
            stop.append("ZIP-ul nu conține sha-ul publicat")
        if sorted(z.read("fisiere_diff.txt").decode().split()) != sorted(diff):
            stop.append("lista fișierelor din ZIP diferă de diff-ul față de main")
    # praguri numerice: `max <faza> <secunde>`; în lotul de unelte nu sunt
    for ln in open(praguri, encoding="utf-8"):
        m = re.match(r"max\s+(\S+)\s+(\d+)", ln)
        if m:
            d = [x[5] for x in JL.durate(lot) if x[0] == m.group(1) and x[5] != ""]
            if d and max(d) > int(m.group(2)):
                stop.append("pragul „%s” depășit: %ss > %ss" % (m.group(1), max(d), m.group(2)))
    return stop


def zip_lot(lot, sha, cale):
    baza = git("merge-base", sha, "main")
    diff = git("diff", "--name-only", baza, sha).splitlines()
    lotf = L.lot_fisier(lot)
    with zipfile.ZipFile(cale, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("sha.txt", sha + "\n")
        z.writestr("fisiere_diff.txt", "\n".join(diff) + "\n")
        for f in diff:
            if os.path.exists(os.path.join(RAD, f)):
                z.write(os.path.join(RAD, f), "fisiere/" + f)
        for extra in (os.path.join(ACASA, "lot_%s_raport.md" % lotf),):
            if os.path.exists(extra):
                z.write(extra, os.path.basename(extra))
        z.writestr("jurnal_lot.txt", "\n".join("%-20s %-10s %s -> %s  %ss" % (f, r, b, s, sec) for f, i, b, s, r, sec in JL.durate(lot)) + "\n")


def main_verifica(c, head, lot=None):
    """`--verifica <C> <HEAD> [lot]`: numai regula strămoșului, fără publicare, fără scrieri; judecă depozitul din directorul curent (hook-urile git o chemă de aici)."""
    global DEP
    DEP = os.getcwd()
    lotf = L.lot_fisier(lot or JL.lot_curent())
    head = git("rev-parse", head)
    c = git("rev-parse", c)
    refuzuri, fisiere = ancestor_refuzuri(c, head, lotf)
    for m in refuzuri:
        print("[publica_lot --verifica] REFUZ: " + m)
    if refuzuri:
        return 1
    print("[publica_lot --verifica] PASS C=%s HEAD=%s fisiere=%s" % (c, head, ",".join(fisiere) or "-"))
    return 0


def main():
    if len(sys.argv) in (4, 5) and sys.argv[1] == "--verifica":
        return main_verifica(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else None)
    lot = JL.lot_curent()
    lotf = L.lot_fisier(lot)
    sha = git("rev-parse", "HEAD")
    comun = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    sirul_zip = os.path.join(ACASA, "lot_%s.zip" % lotf)
    zip_lot(lot, sha, sirul_zip)
    stop = verifica(lot, sha, comun, sirul_zip)
    f_stare = os.path.join(comun, "lot_stare_%s.json" % lotf)
    stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {}
    c = stare["complete"][-1]["sha"] if stare.get("complete") else sha
    if stop:
        for m in stop:
            print("[publica_lot] STOP: " + m)
        print("OPRIT — gata: %s nepublicat, %s" % (lot, stop[0]))
        return 1
    with open(os.path.join(comun, "publica_verdicte.log"), "a", encoding="utf-8") as f:
        f.write("PASS %s %s %s C=%s fisiere=%s\n" % (sha, lot, JL._acum(), c, ",".join(ancestor_refuzuri(c, sha, lotf)[1]) or "-"))
    print("[publica_lot] PASS %s (lot %s); ZIP %s" % (sha, lot, sirul_zip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
