# -*- coding: utf-8 -*-
"""GARDA uneltei de dovadă pe copia firmelor de test (`scripts/dovada_firme_test.py`, comanda Costin 11.2 pct.3: „nimic nu e «rezolvat»
fără dovadă pe ecran pe firmele de test, inclusiv pe documentele create înainte de reparație”).

Unealta citește din PRODUCȚIE și scrie într-o bază de TEST. Cele două frontiere pe care le apără testele de aici:
  1. ținta scrierilor e o bază dovedită de test (`core.mediu_test.motive`) — altfel refuz ÎNAINTE de orice conexiune la producție;
  2. fiecare schemă copiată e a cabinetului de test „Cabinet Test Sesiunea B SRL”, nu a cabinetului pilot — altfel refuz ÎNAINTE de
     `pg_dump` (datele cabinetului real nu se citesc, regimul pilot pct.3).
Plus: numele schemei se înlocuiește numai ca identificator întreg, iar o coloană care arată a secret oprește copierea."""
import os
import re
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import dovada_firme_test as d  # noqa: E402

ENV_TEST = {"ICONTA_MEDIU": "test", "DATABASE_URL": "postgresql://iconta_test_user@localhost:5432/iconta_test"}


def _rand(schema, cabinet="Cabinet Test Sesiunea B SRL", cab_id=48765):
    return (105000 + int(schema[-3:]), schema, "Firma %s" % schema, cab_id, cabinet)


# ── 1. ținta ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("env, cod", [
    ({"DATABASE_URL": ENV_TEST["DATABASE_URL"]}, "MEDIU_NEDECLARAT"),                                     # tăcerea nu trece
    ({"ICONTA_MEDIU": "test", "DATABASE_URL": "postgresql://iconta_test_user@localhost:5432/iconta_v2"}, "BAZA_PRODUCTIE"),
    ({"ICONTA_MEDIU": "test", "DATABASE_URL": "postgresql://iconta_user@localhost:5432/iconta_test"}, "UTILIZATOR_PRODUCTIE"),
])
def test_refuza_tinta_care_nu_e_de_test(env, cod):
    """MUTAȚIE: `tinta_de_test` fără verificarea `mediu_test.motive` -> nu ridică -> pică."""
    with pytest.raises(d.Refuz) as e:
        d.tinta_de_test(env)
    assert e.value.cod == "TINTA_NU_E_DE_TEST" and cod in e.value.mesaj, (e.value.cod, e.value.mesaj)


def test_tinta_de_test_e_acceptata():
    assert d.tinta_de_test(ENV_TEST) == ENV_TEST["DATABASE_URL"]


def test_cloneaza_refuza_tinta_inainte_de_a_atinge_productia(monkeypatch):
    """O țintă care nu e de test oprește clonarea ÎNAINTE de conexiunea la producție și de orice proces (pg_dump / psql).
    MUTAȚIE: `tinta_de_test(env)` scos din `cloneaza` -> se deschide producția -> pică."""
    monkeypatch.setattr(d, "_env_test", lambda: {"DATABASE_URL": "postgresql://iconta_user@localhost:5432/iconta_v2"})
    monkeypatch.setattr(d, "_conexiune_productie", lambda: pytest.fail("producția s-a deschis înaintea verificării țintei"))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("un proces a pornit înaintea verificării țintei: %r" % (a,)))
    with pytest.raises(d.Refuz) as e:
        d.cloneaza([])
    assert e.value.cod == "TINTA_NU_E_DE_TEST"


# ── 2. sursele: numai cabinetul de test ────────────────────────────────────────────────────────────────────────────────────────────────
def test_sursele_cabinetului_de_test_sunt_acceptate():
    cab, surse = d.verifica_surse([_rand(s) for s in d.SURSE])
    assert cab == 48765 and sorted(surse) == sorted(d.SURSE)


def test_refuza_schema_altui_cabinet():
    """O schemă sursă a altui cabinet (cabinetul pilot) -> refuz, cu schema numită. MUTAȚIE: verificarea cabinetului scoasă din
    `verifica_surse` -> nu ridică -> pică."""
    randuri = [_rand(s) for s in d.SURSE]
    randuri[3] = _rand(d.SURSE[3], cabinet="Cabinetul pilot SRL", cab_id=1)
    with pytest.raises(d.Refuz) as e:
        d.verifica_surse(randuri)
    assert e.value.cod == "SCHEMA_ALTUI_CABINET" and d.SURSE[3] in e.value.mesaj, e.value.mesaj


def test_refuza_schema_lipsa_si_cabinete_diferite():
    with pytest.raises(d.Refuz) as e:
        d.verifica_surse([_rand(s) for s in d.SURSE[:-1]])
    assert e.value.cod == "SCHEMA_LIPSA" and d.SURSE[-1] in e.value.mesaj
    randuri = [_rand(s) for s in d.SURSE]
    randuri[0] = _rand(d.SURSE[0], cab_id=99)          # același nume de cabinet, alt cabinet
    with pytest.raises(d.Refuz) as e:
        d.verifica_surse(randuri)
    assert e.value.cod == "CABINETE_DIFERITE"


class _CursorFals:
    """Producția văzută de `cloneaza`: `public.tenants` cu o schemă a cabinetului pilot."""

    def __init__(self, randuri):
        self.randuri, self.cereri = randuri, []

    def execute(self, q, p=None):
        self.cereri.append(q)

    def fetchall(self):
        # pe CLAUZA FROM (tabelul numit după FROM), nu pe sub-șir al cererii
        return self.randuri if re.search(r"\bFROM\s+public\.tenants\b", self.cereri[-1]) else []

    def fetchone(self):
        return (None,)


class _ConexiuneFalsa:
    def __init__(self, cur):
        self.cur = cur

    def cursor(self):
        return self.cur


def test_cloneaza_refuza_schema_pilotului_inainte_de_pg_dump(monkeypatch):
    """Pe drumul întreg al clonării: o schemă a cabinetului pilot -> refuz înainte de `pg_dump` și de orice scriere în baza de test.
    MUTAȚIE: `verifica_surse` scos din `cloneaza` -> drumul ajunge la `pg_dump` / baza de test -> pică."""
    randuri = [_rand(s) for s in d.SURSE]
    randuri[0] = _rand(d.SURSE[0], cabinet="Cabinetul pilot SRL", cab_id=1)
    cur = _CursorFals(randuri)
    monkeypatch.setattr(d, "_env_test", lambda: dict(ENV_TEST))
    monkeypatch.setattr(d, "_conexiune_productie", lambda: ("postgresql://iconta_user@localhost:5432/iconta_v2", _ConexiuneFalsa(cur)))
    monkeypatch.setattr(d, "_lacat", lambda: pytest.fail("clonarea a trecut de verificarea surselor"))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("pg_dump / psql a pornit pe o schemă a pilotului: %r" % (a,)))
    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", lambda *a, **k: pytest.fail("baza de test s-a deschis pe o schemă a pilotului"))
    with pytest.raises(d.Refuz) as e:
        d.cloneaza([])
    assert e.value.cod == "SCHEMA_ALTUI_CABINET" and d.SURSE[0] in e.value.mesaj


def test_schema_copiei_numai_pentru_sursele_cunoscute():
    assert [d.schema_copie(s) for s in d.SURSE] == ["tenant_9049", "tenant_9050", "tenant_9051", "tenant_9052", "tenant_9053",
                                                    "tenant_9054", "tenant_9055"]
    with pytest.raises(d.Refuz):
        d.schema_copie("tenant_001")


# ── 3. redenumirea și secretele ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_redenumirea_atinge_numai_identificatorul_intreg():
    """MUTAȚIE: fără `\\b` -> `tenant_0490` / `tenant_049_x` devin `tenant_90490` / `tenant_9049_x` -> pică."""
    t = 'CREATE TABLE tenant_049.facturi (x int DEFAULT nextval(\'tenant_049.facturi_id_seq\'::regclass)); tenant_0490 tenant_049_x "tenant_049"'
    assert d.redenumeste(t, "tenant_049", "tenant_9049") == ('CREATE TABLE tenant_9049.facturi (x int DEFAULT nextval('
                                                             '\'tenant_9049.facturi_id_seq\'::regclass)); tenant_0490 tenant_049_x "tenant_9049"')


def test_coloana_care_arata_a_secret_e_semnalata():
    col = [("spv", "access_token"), ("firma", "parola_smtp"), ("cert", "pfx_b64"), ("x", "api_key"), ("artefacte_produse", "cheie"),
           ("concedii_medicale", "data_certificat_initial"), ("facturi", "numar")]
    assert d.coloane_secrete(col) == ["spv.access_token", "firma.parola_smtp", "cert.pfx_b64", "x.api_key"]


# ── 4. lista de dovezi ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lista_de_dovezi_are_forma_registrului():
    """Fiecare dovadă: numărul, o firmă a copiei, pași și verificări cunoscute de `frontend_test/dovada/pasi.py`, captura numită cum o
    cere registrul (`core/test_deficiente._RE_CAPTURA`: `<nr>_…_f<k>_….png`, aceeași expresie, importată — nu copiată). MUTAȚIE: o captură
    `C76_f1_x.png` (majusculă) sau un pas necunoscut în listă -> pică."""
    import json
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    from core.test_deficiente import _RE_CAPTURA
    dovezi = json.load(open(d.DOVEZI_IMPLICIT, encoding="utf-8"))
    copii = {d.schema_copie(s) for s in d.SURSE}
    rele = []
    for x in dovezi:
        if x["firma"] not in copii | set(d.SURSE):
            rele.append("%s: firma %r nu e în copie" % (x["nr"], x["firma"]))
        capturi = [x["captura"]] + [p["captura"] for p in x["pasi"] if p.keys() >= {"captura"}]
        rele += ["%s: captura %s nu are forma registrului" % (x["nr"], c) for c in capturi
                 if not re.match(_RE_CAPTURA % re.escape(x["nr"].lower()), "dovezi/lot11/" + c)]
        rele += ["%s: pas necunoscut %s" % (x["nr"], p) for p in x["pasi"] if not set(p) & set(pasi.PASI)]
        rele += ["%s: verificare necunoscută %s" % (x["nr"], v) for v in x["verifica"] if not set(v) & set(pasi.VERIFICARI)]
        if not x["verifica"]:
            rele.append("%s: fără verificări (o captură fără text verificat nu e dovadă)" % x["nr"])
    toate = [c for x in dovezi for c in [x["captura"]] + [p["captura"] for p in x["pasi"] if p.keys() >= {"captura"}]]
    assert len(dovezi) >= 13 and all(x["pasi"] for x in dovezi), "anti-vacuu: lista de dovezi e goală sau are dovezi fără pași"
    rele += ["captura %s apare de două ori" % c for c in set(toate) if toate.count(c) > 1]
    assert not rele, "\n".join(rele)
    numere = {x["nr"] for x in dovezi}
    assert {"428", "C76", "451", "452", "409", "429", "439", "443", "450", "C75", "442", "444", "C69"} <= numere, numere


# ── 5. argumentele, înainte de orice efect (ca `core/test_argumente_script.py`) ─────────────────────────────────────────────────────────
def _ruleaza(*argv):
    env = dict(os.environ, DATABASE_URL="postgresql://nimeni@127.0.0.1:1/nimic")
    return subprocess.run([sys.executable, os.path.join(RAD, "scripts", "dovada_firme_test.py"), *argv], cwd="/tmp", capture_output=True,
                          text=True, timeout=30, env=env)


def test_uzul_si_argumentele_necunoscute_nu_pornesc_nimic():
    r = _ruleaza("--help")
    assert r.returncode == 0 and "Uz:" in r.stdout, r.stderr[-300:]
    # primul rând EXACT al refuzului (urmat de uz), nu un sub-șir oriunde în stderr
    r = _ruleaza("--ajutor")
    assert (r.returncode, r.stderr.splitlines()[0]) == (2, "[dovada] argument necunoscut: --ajutor — nimic nu pornește."), r.stderr[-300:]
    o_actiune = "[dovada] o singură acțiune: --cloneaza, --capturi=DIR, --sterge sau --amprente=DIR — nimic nu pornește."
    r = _ruleaza()
    assert (r.returncode, r.stderr.splitlines()[0]) == (2, o_actiune), r.stderr[-300:]
    r = _ruleaza("--cloneaza", "--sterge")
    assert (r.returncode, r.stderr.splitlines()[0]) == (2, o_actiune), r.stderr[-300:]
    r = _ruleaza("--sterge", "--amprente=dovezi/lot11")
    assert (r.returncode, r.stderr.splitlines()[0]) == (2, o_actiune), r.stderr[-300:]


def test_scoaterea_copiei_trece_peste_randurile_legate_de_cabinet():
    """[lotul 11, găsit la a treia rulare a dovezilor] O dovadă de import (Import date) a scris `public.migrare_status` pentru cabinetul
    copiei, iar scoaterea copiei s-a oprit pe cheia străină (`migrare_status_accounting_firm_id_fkey`) — a doua clonare a eșuat și dovezile
    următoare au rulat pe copia veche. `_sterge_referintele` citește din catalog toate cheile spre cabinet / utilizatori / firme.
    MUTAȚIE: apelul pentru `accounting_firms` scos din `_sterge_copia` -> ForeignKeyViolation -> pică. Rulează pe baza de TEST, în
    ROLLBACK (cabinet sintetic cu marcajul copiei; nicio schemă nu se creează)."""
    from core import db, mediu_test
    if mediu_test.motive(os.environ):
        pytest.skip("numai pe baza de test")
    db.init_pool()
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id", ("Probă" + d.MARCAJ_CABINET,))
            cab = cur.fetchone()[0]
            cur.execute("INSERT INTO public.migrare_status (accounting_firm_id, strat) VALUES (%s, 'solduri')", (cab,))
            assert cab in d._sterge_copia(cur)
            cur.execute("SELECT count(*) FROM public.accounting_firms WHERE id = %s", (cab,))
            assert cur.fetchone()[0] == 0
        c.rollback()
