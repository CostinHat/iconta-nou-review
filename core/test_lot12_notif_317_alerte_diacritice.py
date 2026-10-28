# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 317, partea „Emailul de alertă e fără diacritice („sanatate”, „in ultimele”)”] — pe CLASĂ.

Lotul 8 a scris cu diacritice emailul de sănătate a serverului; celelalte alerte către administratorul platformei rămăseseră fără:
„Esec pe cale secundara: …” / „Operatia principala a continuat, dar '…' a esuat” (`observare.esec_secundar`), „Job de fundal esuat” și
„Urmatoarele joburi n-au mai raportat o rulare reusita” (`cron`), „Refresh token SPV esuat” (`spv_refresh`), „O valoare fiscala n-a mai fost
confirmata in pragul ei” (`expirare_cote`), „Cerere de stergere cont” (`gdpr_cerere`), „Acces anormal: user … tenanti, … actiuni”
(`alerta_acces`).

GARDA: toate apelurile care trimit o alertă pe canalul operatorului (`observare.alerteaza`, `alerteaza_in_fundal`, `_trimite_brevo` și
trimiterea injectabilă a lui `alerta_acces`), în `core/`, `main.py` și `scripts/`: textul lor — literalii argumentelor, cu numele locale /
de modul și funcțiile din același modul care îl compun urmărite până la șiruri — trece prin dicționarul de diacritice al ecranelor
(`core.limba_ecran.defecte`, felul „diacritice”). Anti-vacuu: numărul de apeluri găsite și cele șapte texte de mai sus, prinse ca
fragmente urmărite. LIMITĂ declarată: un text venit din afara modulului (argumentul unei funcții publice) nu se urmărește — atunci intră
în proba apelantului lui.

Temei: N/A — limba textelor aplicației (CLAUDE.md §9: „cu diacritice”).
"""
import ast
import os
import re

from core import limba_ecran

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: funcțiile care trimit pe canalul de alertă al operatorului (numele apelului) -> câte argumente de text (subiect, mesaj) au
CANAL = {"alerteaza": (1, 2), "alerteaza_in_fundal": (1, 2), "_trimite_brevo": (0, 1), "_alerteaza": (1, 2)}
#: trimiterea injectabilă (`trimite = trimite or observare._trimite_brevo`), apelată prin numele local
INJECTATE = {("core/alerta_acces.py", "trimite"): (0, 1), ("scripts/verifica_duk_publicat.py", "alerta"): (1, 2)}
#: textul primit ca parametru, compus în același modul: (fișier, funcție, parametru) -> numele de modul din care se compune
PARAMETRI = {("core/gdpr_cerere.py", "anunta_echipa", "anunt"): ("SUBIECT_ANUNT", "corp_anunt")}


def _fisiere():
    out = ["main.py"]
    for d in ("core", "scripts"):
        out += ["%s/%s" % (d, f) for f in sorted(os.listdir(os.path.join(RAD, d))) if f.endswith(".py") and not f.startswith("test_")]
    return out


def _nume_apel(c):
    f = c.func
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)


class _Modul:
    def __init__(self, arb, rel):
        self.rel = rel
        self.functii = {n.name: n for n in arb.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.globale = {}
        for n in arb.body:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.globale.setdefault(t.id, []).append(n.value)

    def fragmente(self, nod, fn, vazute):
        """Șirurile din care se compune expresia `nod` (în funcția `fn`)."""
        out = []
        for x in ast.walk(nod):
            if isinstance(x, ast.Constant) and isinstance(x.value, str):
                out.append(x.value)
            elif isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) and (fn, x.id) not in vazute:
                vazute.add((fn, x.id))
                locale = [a.value for a in ast.walk(fn) if isinstance(a, ast.Assign)
                          for t in a.targets for n in ast.walk(t) if isinstance(n, ast.Name) and n.id == x.id] if fn else []
                for v in locale or self.globale.get(x.id, []):
                    out += self.fragmente(v, fn, vazute)
                for sursa in PARAMETRI.get((self.rel, getattr(fn, "name", None), x.id), ()):
                    out += self.fragmente(ast.parse(sursa + ("()" if sursa in self.functii else ""), mode="eval").body, None, vazute)
            elif isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id in self.functii and x.func.id not in vazute:
                vazute.add(x.func.id)
                g = self.functii[x.func.id]
                for r in ast.walk(g):
                    if isinstance(r, ast.Return) and r.value is not None:
                        out += self.fragmente(r.value, g, vazute)
        return out


def _alerte():
    """[(fisier:linie, text)] pentru fiecare apel pe canalul de alertă."""
    out = []
    for rel in _fisiere():
        arb = ast.parse(open(os.path.join(RAD, rel), encoding="utf-8").read())
        m = _Modul(arb, rel)
        for fn in [n for n in ast.walk(arb) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for c in ast.walk(fn):
                if not isinstance(c, ast.Call):
                    continue
                nume = _nume_apel(c)
                poz = INJECTATE.get((rel, nume)) if isinstance(c.func, ast.Name) and (rel, nume) in INJECTATE else CANAL.get(nume)
                if poz is None or (rel == "core/observare.py" and fn.name in ("alerteaza", "alerteaza_in_fundal")):
                    continue        # înăuntrul canalului: textul e al apelantului
                fr = []
                for i in poz:
                    if i < len(c.args):
                        fr += m.fragmente(c.args[i], fn, set())
                out.append(("%s:%d" % (rel, c.lineno), " ".join(fr)))
    return out


def test_def_317_alertele_operatorului_au_diacritice():
    """MUTAȚIE: corpul alertei de job căzut (`cron`) înapoi la „a esuat la %s, dupa …” -> pică: „alerte către operator fără diacritice:
    [('core/cron.py:66', ['esuat', 'dupa'])]”; subiectul „Eșec pe cale secundară” înapoi fără diacritice -> pică (anti-vacuu)."""
    alerte = _alerte()
    assert len(alerte) >= 13, ("[anti-vacuu] prea puține apeluri pe canalul de alertă: %d" % len(alerte), alerte)
    toate = " ".join(t for _, t in alerte)
    for fragment in ("Eșec pe cale secundară", "Job de fundal eșuat", "Următoarele joburi", "Reîmprospătarea accesului SPV a eșuat",
                     "O valoare fiscală n-a mai fost confirmată", "Cerere de ștergere cont", "Acces anormal:", "acțiuni în %s min"):
        assert fragment in toate, ("[anti-vacuu] textul nu mai e urmărit până la apel: %s" % fragment)
    # căile și comenzile din alertă (`POST /gdpr/sterge-cabinet/…`, `%s/*.log`) sunt nume tehnice, nu text: se scot înainte de judecată
    gresite = [(loc, [w for fel, w in limba_ecran.defecte(re.sub(r"\S*/\S*", " ", t)) if fel == "diacritice"]) for loc, t in alerte]
    gresite = [(loc, w) for loc, w in gresite if w]
    assert not gresite, "alerte către operator fără diacritice: %s" % gresite
