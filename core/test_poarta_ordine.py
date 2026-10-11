# -*- coding: utf-8 -*-
"""GARDA deciziei Costin 08.10.2026, pct.3: „Verificarea commit-msg rulează înaintea pytest, nu după. Intră în acest lot, nu
separat.” (verbatim în DECIZII 08.10.2026)

DE CE. Git rulează `pre-commit` ÎNAINTEA mesajului. Cât timp suita (pytest, ~55 de minute) stătea în `pre-commit`, un mesaj fără
`# diff-citit:` era respins DUPĂ o rulare verde — pe 06.10 și din nou pe 08.10. Regula „treci mesajul întâi manual” a fost
ignorată de două ori; ce n-a ținut ca disciplină devine ordine în hook-uri:

    pre-commit: ruff  ->  commit-msg: verifica-mesaj (oprește aici)  ->  poarta-suita (pytest + verificatorul)

CE FACE IMPOSIBIL:
  * ca suita să ruleze înaintea verificării mesajului (structural: `pre-commit` nu cheamă nici pytest, nici verificatorul;
    `commit-msg` cheamă `verifica-mesaj` ÎNAINTEA `poarta-suita`, fiecare cu `|| exit 1`);
  * ca un mesaj greșit să pornească suita (funcțional, pe hook-ul adevărat: respins în secunde, fără „[poarta] pytest”);
  * ca suita să dispară din drum (funcțional: un mesaj bun ajunge la „[poarta] pytest”).

CE NU FACE, declarat: nu rulează suita adevărată (depozitul de probă e gol, deci pytest nu găsește teste și poarta respinge —
exact ce trebuie să facă o poartă fără teste verzi).
"""
import os
import shlex
import subprocess
import tempfile
import time

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HOOKS = os.path.join(_RAD, "scripts", "githooks")


def _linii_cod(nume):
    """Liniile de cod ale unui script `sh` (fără comentarii), ca liste de cuvinte."""
    out = []
    with open(os.path.join(_HOOKS, nume), encoding="utf-8") as f:
        for linie in f:
            try:
                t = shlex.split(linie, comments=True)
            except ValueError:
                continue
            if t:
                out.append(t)
    return out


def test_pre_commit_nu_mai_porneste_suita():
    """Suita e după mesaj; în `pre-commit` mesajul nu există. MUTAȚIE: linia `"$PY" -m pytest -q` pusă înapoi în `pre-commit`
    -> pică."""
    cuvinte = [w for t in _linii_cod("pre-commit") for w in t]
    assert cuvinte.count("pytest") == 0 and sum(w.count("verificator_conformitate") for w in cuvinte) == 0, cuvinte
    assert sum(w.count("RUFF") for w in cuvinte) >= 1, "ruff a dispărut din pre-commit"


def test_commit_msg_verifica_mesajul_inainte_de_suita():
    """Ordinea, ca structură. MUTAȚIE: cele două linii din `commit-msg` inversate -> pică."""
    linii = _linii_cod("commit-msg")
    def _poz(nume):
        p = [i for i, t in enumerate(linii) if any(w.endswith("/" + nume) for w in t)]
        assert len(p) == 1, "%s trebuie chemat o dată din commit-msg: %r" % (nume, linii)
        return p[0]
    m, s = _poz("verifica-mesaj"), _poz("poarta-suita")
    assert m < s, "suita e chemată înaintea verificării mesajului"
    for i in (m, s):
        assert linii[i][-3:] == ["||", "exit", "1"], "un eșec nu mai oprește commitul: %r" % linii[i]
    suita = [w for t in _linii_cod("poarta-suita") for w in t]
    assert suita.count("pytest") >= 1 and suita.count("verificator_conformitate.py") >= 1


def _ruleaza(continut):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", "."], cwd=d, check=True, capture_output=True)
        with open(os.path.join(d, "MSG"), "wb") as f:
            f.write(continut)
        t0 = time.monotonic()
        r = subprocess.run(["sh", os.path.join(_HOOKS, "commit-msg"), "MSG"], cwd=d, capture_output=True, text=True,
                           timeout=300)
        return r.returncode, (r.stdout or "") + (r.stderr or ""), time.monotonic() - t0


def test_mesajul_respins_nu_porneste_suita():
    """Ordinea, ca efect, pe hook-ul adevărat: un mesaj cu octet de control e respins de `verifica-mesaj`, iar suita nici nu
    pornește. MUTAȚIE: ordinea inversată în `commit-msg` -> apare „[poarta] pytest” -> pică."""
    cod, iesire, _dur = _ruleaza(b"mesaj\n\ncu octet \x08 in el\n")
    assert cod == 1 and iesire.count("OCTETI DE CONTROL") >= 1, iesire
    assert iesire.count("[poarta] pytest") == 0, "suita a pornit înaintea verificării mesajului:\n%s" % iesire


def test_mesajul_bun_ajunge_la_suita():
    """Suita n-a dispărut din drum: un mesaj bun trece de `verifica-mesaj` și pornește pytest (care, pe depozitul gol, n-are teste
    și respinge). MUTAȚIE: linia `poarta-suita` scoasă din `commit-msg` -> commitul trece fără suită -> pică."""
    cod, iesire, _dur = _ruleaza("Reparație mică, cu diacritice: șțăîâ\n".encode("utf-8"))
    assert iesire.count("[poarta] pytest") == 1, iesire
    assert cod == 1, "pe un depozit fără teste poarta trebuia să respingă:\n%s" % iesire


def test_poarta_ruleaza_toata_suita_in_paralel_fara_selectie():
    """[11.10.2026, comanda Costin pct.4e: „Fă poarta mai rapidă fără să scoți niciun test”] Poarta rulează pytest în paralel
    (pytest-xdist, `--dist loadfile`) pe TOATĂ suita: linia lui pytest n-are cale, `-k`, `-m`, `--deselect`, `--ignore` sau `-x` —
    nimic care să lase un test pe dinafară. MUTAȚIE: `--ignore=frontend_test` (sau `-k "not lent"`) pe linia pytest -> pică;
    `-n` scos (rulare serială, poarta înapoi la ~82 de minute) -> pică."""
    import io
    import re as _re
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    linii = [x for x in t.splitlines() if _re.match(r'^"\$PY" -m pytest\b', x)]
    assert len(linii) == 1, linii
    arg = linii[0].split(">")[0].split()[3:]
    assert arg[:1] == ["-q"] and arg.count("-n") == 1 and arg.count("--dist") == 1 and arg[arg.index("--dist") + 1] == "loadfile", arg
    straine = [a for a in arg if a not in ("-q", "-n", '"$NW"', "--dist", "loadfile")]
    assert straine == [], "pytest-ul porții alege teste: %s" % straine


def test_plasa_porneste_numai_dupa_verdictul_pytest():
    """[11.10.2026, măsurat] Plasa e2e pornește aplicația pe ACEEAȘI bază de test pe care rulează pytest, iar pornirea aplicației
    reface triggerele fiecărei firme. Suprapuse (proba din 11.10, 22:16): deadlock, pool-ul aplicației epuizat, plasa agățată două ore.
    Deci în poartă rularea plasei vine DUPĂ `asteapta_pytest` și după verdictul lui (`RC=$RC_PYTEST`), nu în timpul lui. MUTAȚIE: blocul
    plasei mutat înaintea așteptării lui pytest -> pică."""
    import io
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    linii = t.splitlines()
    porneste = next(i for i, x in enumerate(linii) if x.startswith('"$PY" -m pytest '))
    plasa = next(i for i, x in enumerate(linii) if x.startswith('"$PY" scripts/e2e_poarta.py'))
    asteapta = [i for i, x in enumerate(linii) if x.strip() == "asteapta_pytest"]
    verdict = [i for i, x in enumerate(linii) if x.strip() == "RC=$RC_PYTEST"]
    assert asteapta and verdict, (asteapta, verdict)
    assert porneste < min(asteapta) < min(verdict) < plasa, (porneste, asteapta, verdict, plasa)
