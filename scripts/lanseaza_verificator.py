# -*- coding: utf-8 -*-
"""scripts/lanseaza_verificator.py — lansatorul verificatorului independent (comanda 16.1-C3, pct.2; creat ca unealtă aici, 16.2 doar îl folosește).
Pornește subagentul Haiku 5.5 (`claude -p --model claude-haiku-5-5`) cu fișierele date — scenariul, pasi_<lot>.txt al arhitectului, formatele — copiate într-un director temporar fără
depozit git (fără diff, fără sursele lotului), și îi dă o singură unealtă: un înveliș `verifica.sh` care cheamă scripts/verifica_pas.py cu `--lot`, `--pasi` și verificator="Haiku 5.5 (lanseaza_verificator)"
FIXE. Pașii se execută deci prin verifica_pas.py, iar verdictul vine din compararea operator + valoare (oracolul), nu din ce spune agentul. Ia lacătul pe iconta_test și 8019
(scripts/lacat_test.py) înainte de orice și refuză dacă îl ține altcineva. Nu are acces la diff: refuză fișierele de tip .diff/.patch și căile din .git.
  lanseaza_verificator.py --lot <lot> --scenariu <fișier> --pasi-txt <fișier> --pasi-json <fișier> [--formate <fișier>...] [--iesire <fișier>]
Limită declarată (CLAUDE.md): „fără acces la diff” = directorul de lucru nu e depozit și nu conține diff; agentul rulează ca utilizatorul, pe același server, deci e o izolare de proces, nu o barieră.
CLAUDE_BIN (calibrare) înlocuiește executabilul `claude`."""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import lacat_test as LT  # noqa: E402

RAD = os.path.dirname(AICI)
MODEL = "claude-haiku-5-5"
VERIFICATOR = "Haiku 5.5 (lanseaza_verificator)"
INSTRUCTIUNE = ("Rulează scenariul de mai jos în aplicație, pe mediul de test, exact cum e scris, cu uneltele de capăt la capăt existente. Nu modifici cod. Răspunzi doar cu: TRECE sau NU TRECE, "
                "pașii făcuți, ce ai văzut la fiecare pas, capturile de ecran, și orice abatere de la scenariu. Fiecare pas îl execuți numai prin ./verifica.sh "
                "(--pas <pas> --actiune <text> --json-url <cale> --asertiune <id> [--pagina <cale>]); verdictul îl scrie scriptul.")


def refuzuri_fisiere(cai):
    """Fișierele date agentului: niciun diff și nimic din .git. -> motivele de refuz."""
    ref = []
    for c in cai:
        if not os.path.isfile(c):
            ref.append("%s: nu există" % c)
        elif c.lower().endswith((".diff", ".patch")) or "/.git/" in os.path.abspath(c) + "/":
            ref.append("%s: diff sau cale din .git — agentul nu are acces la diff" % c)
    return ref


def main(a):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lot", required=True)
    ap.add_argument("--scenariu", required=True)
    ap.add_argument("--pasi-txt", required=True)
    ap.add_argument("--pasi-json", required=True)
    ap.add_argument("--formate", nargs="*", default=[])
    ap.add_argument("--iesire", default=None)
    o = ap.parse_args(a)
    cai = [o.scenariu, o.pasi_txt, o.pasi_json] + o.formate
    ref = refuzuri_fisiere(cai)
    if ref:
        print("[lanseaza_verificator] REFUZ: " + "; ".join(ref))
        return 1
    if LT.ia(os.getpid(), "lanseaza_verificator.py"):   # refuz cu pid-ul care ține lacătul (mesajul îl tipărește lacat_test)
        return 1
    os.environ["LACAT_TEST_PID"] = str(os.getpid())
    lucru = tempfile.mkdtemp(prefix="verificator_")
    try:
        for c in cai:
            shutil.copy(c, os.path.join(lucru, os.path.basename(c)))
        py = os.path.join(RAD, "venv", "bin", "python")
        py = py if os.path.exists(py) else sys.executable
        env_sh = os.path.join(lucru, "verifica.sh")
        open(env_sh, "w", encoding="utf-8").write('#!/bin/sh\nexec "%s" "%s/verifica_pas.py" --lot "%s" --pasi "%s/%s" --verificator "%s" "$@"\n' % (
            py, AICI, o.lot, lucru, os.path.basename(o.pasi_json), VERIFICATOR))
        os.chmod(env_sh, 0o755)
        prompt = INSTRUCTIUNE + "\n\n== SCENARIUL (%s) ==\n%s\n\n== PASII (pasi_%s.txt) ==\n%s\n" % (
            os.path.basename(o.scenariu), open(o.scenariu, encoding="utf-8").read(), o.lot, open(o.pasi_txt, encoding="utf-8").read())
        for f in o.formate:
            prompt += "\n== FORMAT (%s) ==\n%s\n" % (os.path.basename(f), open(f, encoding="utf-8").read())
        cmd = [os.environ.get("CLAUDE_BIN", "claude"), "-p", "--model", MODEL, "--allowedTools", "Bash(%s:*)" % env_sh,
               "--disallowedTools", "Read", "Edit", "Write", "Grep", "Glob", "WebFetch", "WebSearch", "NotebookEdit", "Agent"]
        r = subprocess.run(cmd, input=prompt, cwd=lucru, capture_output=True, text=True)
        iesire = r.stdout + (("\n[stderr]\n" + r.stderr) if r.stderr.strip() else "")
        if o.iesire:
            open(o.iesire, "w", encoding="utf-8").write(iesire)
        print(iesire)
        return r.returncode
    finally:
        shutil.rmtree(lucru, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
