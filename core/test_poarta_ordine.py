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
