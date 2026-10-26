# -*- coding: utf-8 -*-
"""GARD — codul nu repornește pe producție înaintea migrării lui (comanda Costin 09.10.2026, pct.2: „Dacă un commit conține o migrare
nerulată pe producție, aplicația nu repornește. Nu procedură scrisă.”).

Drumurile (căutarea e în docstringul `core/migrari_registru.py`): (a) o migrare din HEAD fără rândul ei în `public.migrari_rulate`
(amprenta conținutului din HEAD) — și cea comisă într-un lot ANTERIOR, nerulată; (b) o tabelă / coloană din `tenant_template.sql`
lipsă într-o schemă de firmă. Plus: fail-closed când nu se poate ști, și drumul NOU — un fișier de migrare nerecunoscut ca migrare
(fără bloc `__main__`) ar scăpa registrului, deci orice `core/migrare_*.py` fără bloc trebuie numit aici.
Testele cu baza rulează într-o tranzacție anulată, pe nume sintetice (`core/migrare_zz_proba_*.py`): `public.migrari_rulate` e tabelă
partajată (CLAUDE.md: fixture pe tabel partajat = rollback).
"""
import glob
import os
import re

import pytest

from core import db as _db
from core import migrari_registru as mr

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: `core/migrare_*.py` care NU sunt migrări (n-au bloc `__main__`), fiecare cu motivul. Un fișier nou fără bloc pică testul de drum nou.
NU_SUNT_MIGRARI = {
    "core/migrare_api.py": "API-ul migrărilor la cerere (`asigura_tabel`), DDL `IF NOT EXISTS` la rulare",
    "core/migrare_supervizor_confirmari.py": "funcții chemate din alte module, fără rulare proprie",
}


def test_ce_e_o_migrare():
    assert mr.e_migrare("core/migrare_x.py", "def _main():\n    pass\n\nif __name__ == \"__main__\":\n    _main()\n")
    assert not mr.e_migrare("core/migrare_x.py", "def f():\n    pass\n")                 # fără bloc: nu se rulează ca program
    assert not mr.e_migrare("core/test_migrare_x.py", "if __name__ == '__main__':\n    pass\n")
    assert not mr.e_migrare("scripts/migrare_x.py", "if __name__ == '__main__':\n    pass\n")


def test_drum_nou_orice_fisier_de_migrare_e_recunoscut_sau_numit():
    """MUTAȚIE: `_RE_FISIER` restrâns -> migrări reale ies din registru -> pică."""
    head = mr.migrari_la_commit("HEAD")
    toate = {os.path.relpath(f, _RAD) for f in glob.glob(os.path.join(_RAD, "core", "migrare_*.py"))}
    necunoscute = sorted(f for f in toate if f not in NU_SUNT_MIGRARI
                         and not mr.e_migrare(f, open(os.path.join(_RAD, f), encoding="utf-8").read()))
    assert not necunoscute, "core/migrare_*.py fără bloc __main__, deci invizibile registrului: %s" % necunoscute
    assert len(head) >= 84, "anti-vacuu: doar %d migrări găsite în HEAD" % len(head)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    c = p.getconn()
    with c.cursor() as cur:            # registrul e PARTAJAT și are rânduri reale (baza, rulările): fiecare test pornește de la gol,
        mr._tabel(cur)                 # în tranzacția lui, anulată la final (CLAUDE.md: testele nu presupun gol un tabel partajat)
        cur.execute("DELETE FROM public.migrari_rulate")
    try:
        yield c
    finally:
        c.rollback()
        p.putconn(c)


def test_registrul_numara_amprenta_nu_numele(conn):
    """O migrare SCHIMBATĂ după rulare e din nou nerulată (amprenta conținutului). MUTAȚIE: comparația pe nume -> pică."""
    with conn.cursor() as cur:
        m = {"core/migrare_zz_proba_a.py": "a" * 64, "core/migrare_zz_proba_b.py": "b" * 64}
        mr.inregistreaza(cur, "core/migrare_zz_proba_a.py", "a" * 64, "rulata", "proba")
        assert mr.nerulate(cur, m) == [("core/migrare_zz_proba_b.py", "b" * 64)]
        mr.inregistreaza(cur, "core/migrare_zz_proba_b.py", "0" * 64, "rulata", "proba")   # versiunea veche a lui b
        assert mr.nerulate(cur, m) == [("core/migrare_zz_proba_b.py", "b" * 64)]
        with pytest.raises(Exception):                                                  # felul e o mulțime închisă
            mr.inregistreaza(cur, "core/migrare_zz_proba_c.py", "c" * 64, "presupusa", "proba")


def _registru(conn, head, fara=None):
    """Registrul exact = migrările din `head`, mai puțin `fara`. Din nou înaintea fiecărui `verifica` (acela anulează tranzacția)."""
    with conn.cursor() as cur:
        mr._tabel(cur)
        cur.execute("DELETE FROM public.migrari_rulate")
        for f, a in head.items():
            if f != fara:
                mr.inregistreaza(cur, f, a, "baza", "proba")


def test_verifica_opreste_pe_migrare_nerulata_si_trece_cand_toate_sunt_rulate(conn):
    """(a): HEAD cu toate migrările în registru -> 0; una lipsă (inclusiv dintr-un commit anterior) -> 1, numită, cu comanda.
    MUTAȚIE: `nerulate` întoarce [] -> restartul ar porni peste migrarea lipsă -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    cod, linii = mr.verifica("HEAD", conn=conn)
    assert (cod, linii) == (0, []), linii
    lipsa = sorted(head)[0]
    _registru(conn, head, fara=lipsa)
    cod, linii = mr.verifica("HEAD", conn=conn)
    assert cod == 1 and len(linii) == 1 and lipsa in linii[0] and "ruleaza --productie %s" % lipsa in linii[0], linii


def test_verifica_opreste_pe_schema_in_urma_sablonului(conn):
    """(b): o coloană din șablon lipsă într-o firmă (șablon schimbat fără migrare) -> 1, cu schema și coloana.
    MUTAȚIE: `drift_schema` întoarce {} -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1 LIMIT 1")
        s = cur.fetchone()[0]
        cur.execute('ALTER TABLE "%s".casa_operatiuni DROP COLUMN storno_de CASCADE' % s)   # exact cazul d0abd48f
    cod, linii = mr.verifica("HEAD", conn=conn)
    ale_ei = [ln for ln in linii if ln.startswith("schema %s " % s)]
    assert cod == 1 and ale_ei == ["schema %s e în urma șablonului: tabele lipsă -, coloane lipsă {'casa_operatiuni': ['storno_de']}, "
                                   "triggere lipsă -" % s], linii


def test_fail_closed_cand_nu_se_poate_sti(monkeypatch):
    """Baza de neatins / acreditare spre altă bază -> 2 (nu 0): restartul nu se face pe ghicite.
    MUTAȚIE: întoarcerea 0 la conexiune lipsă -> pică."""
    monkeypatch.setattr(mr, "_conexiune_productie", lambda: (None, "proba: baza nu răspunde"))
    cod, linii = mr.verifica("HEAD")
    assert cod == 2 and linii == ["NU SE POATE ȘTI dacă producția are migrările lui HEAD: proba: baza nu răspunde"], linii


def test_verifica_opreste_pe_trigger_lipsa(conn):
    """(b'): un trigger din șablon lipsă într-o firmă (o regulă de fond pusă în șablon fără migrare) -> 1, numit.
    MUTAȚIE: triggerele scoase din `audit_schema.are_drift_hard` -> pică."""
    head = mr.migrari_la_commit("HEAD")
    _registru(conn, head)
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1 LIMIT 1")
        s = cur.fetchone()[0]
        cur.execute('DROP TRIGGER IF EXISTS trg_verifica_perioada_blocata ON "%s".inregistrari' % s)
    cod, linii = mr.verifica("HEAD", conn=conn)
    ale_ei = [ln for ln in linii if ln.startswith("schema %s " % s)]
    assert cod == 1 and ale_ei == ["schema %s e în urma șablonului: tabele lipsă -, coloane lipsă -, triggere lipsă "
                                   "['inregistrari.trg_verifica_perioada_blocata']" % s], linii


#: migrările care au scris în note ÎNAINTEA gărzii, deja rulate pe producție — fiecare cu motivul (nu se mai adaugă nimic aici)
_SCRIU_IN_NOTE_ISTORIC = {
    "core/migrare_nota_corectie.py": "descrierea notelor de corecție (09.2026), rulată înaintea regulilor de fond (09.10.2026)",
    "core/migrare_retest2.py": "descrierea notelor de refacere NIR, „Retest 2” (09.10.2026), rulată pe producție",
    "core/migrare_retest_0810.py": "conturile notelor „Retest 08.10”, rulată pe producție înaintea regulilor de fond",
}

#: [lotul 11, 443 — datele existente; regula Costin 11.2 pct.3a: „Orice reparație acoperă și datele existente.”] migrările care rescriu
#: NUMAI ciorne (textul scris de aplicație) — admise pe nume, cu condiția verificată pe fiecare scriere: un UPDATE cu `status = 'ciorna'`,
#: fără DELETE / INSERT și fără rândurile notei. Nota validată rămâne neatinsă (OMFP 1802/2014 pct.69).
_SCRIU_NUMAI_IN_CIORNE = {
    "core/migrare_serie_nr_descrieri.py": "descrierea / documentul ciornelor scrise înainte de 443 cu seria lipită („Contare factura F61”)",
    # [lotul 12, 168] descrierea ciornei notei chitanței emise automat la încasarea din Casă (456), scrisă fără chitanță
    "core/migrare_descriere_nota_chitanta.py": "descrierea ciornelor notelor de chitanță scrise fără chitanță (168)",
    # [lotul 13, 618] explicația ciornelor raportului Z scrise cu data ISO („Raport Z 2026-10-20 casa …”), regula 3a
    "core/migrare_explicatie_raport_z.py": "explicația ciornelor raportului Z scrise cu data ISO (618)",
}


def test_nicio_migrare_noua_nu_scrie_in_notele_contabile():
    """[17.10.2026, poarta 1 a lotului 6] `migrare_casa_avans` punea `factura_id` pe notele chitanțelor de dinainte — pe copia producției
    a picat la `regula_nota` (o notă validată nu se mai modifică; corectura = stornare, OMFP 1802/2014 pct.69) și ar fi atins notele
    validate ale firmelor reale. O migrare schimbă SCHEMA; o notă contabilă se corectează numai prin contabil (stornare). MUTAȚIE:
    UPDATE-ul pus înapoi în `migrare_casa_avans._DDL` -> pică."""
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scrie = re.compile(r"(UPDATE|DELETE\s+FROM|INSERT\s+INTO)\s+[\"'{}A-Za-z_.@]*\binregistrari(_linii)?\b", re.I)
    scrieri = {os.path.relpath(f, rad): [s for s in _siruri_executate(open(f, encoding="utf-8").read()) if scrie.search(s)]
               for f in glob.glob(os.path.join(rad, "core", "migrare_*.py"))}
    gasite = {f for f, s in scrieri.items() if s}
    # anti-vacuu: fiecare migrare admisă pe ciorne CHIAR scrie (altfel lista e stale și verificarea de mai jos nu se execută)
    assert gasite >= set(_SCRIU_NUMAI_IN_CIORNE), sorted(set(_SCRIU_NUMAI_IN_CIORNE) - gasite)
    # admise numai pe ciorne, pe CLAUZE: verbul e UPDATE, tabelul e `inregistrari` (nu `_linii`), WHERE-ul cere `status = 'ciorna'`
    ciorna = re.compile(r"\bWHERE\b.*\bstatus\s*=\s*'ciorna'", re.I | re.S)
    rele = [(f, s) for f in sorted(_SCRIU_NUMAI_IN_CIORNE) for s in scrieri[f]
            if scrie.search(s).group(1).upper() != "UPDATE" or scrie.search(s).group(2) is not None or not ciorna.search(s)]
    assert rele == [], rele
    gasite -= set(_SCRIU_NUMAI_IN_CIORNE)
    assert gasite <= set(_SCRIU_IN_NOTE_ISTORIC), sorted(gasite - set(_SCRIU_IN_NOTE_ISTORIC))
    assert gasite == set(_SCRIU_IN_NOTE_ISTORIC), "lista istorică are un fișier care nu mai scrie în note: %s" % sorted(
        set(_SCRIU_IN_NOTE_ISTORIC) - gasite)


def _siruri_executate(src):
    """Șirurile din cod, fără docstringuri (un docstring care POMENEȘTE un `INSERT INTO inregistrari` nu scrie nimic)."""
    import ast
    arb = ast.parse(src)
    doc = {id(n.body[0].value) for n in ast.walk(arb)
           if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr)
           and isinstance(n.body[0].value, ast.Constant)}
    out = [n.value for n in ast.walk(arb) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc]
    # [lotul 11, 443] un f-string are bucăți separate („UPDATE ” / „.inregistrari SET …”): refăcut întreg, altfel scrierea nu se vede
    return out + ["".join(v.value if isinstance(v, ast.Constant) else "{}" for v in n.values) for n in ast.walk(arb)
                  if isinstance(n, ast.JoinedStr)]


_RE_TABELA = re.compile(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(?:[\w@{}%\"]+\.)?\"?(\w+)\"?\s*\(", re.I)
_RE_COLOANA = re.compile(r"ALTER TABLE\s+(?:IF EXISTS\s+)?(?:ONLY\s+)?(?:[\w@{}%\"]+\.)?\"?(\w+)\"?\s+ADD COLUMN\s+(?:IF NOT EXISTS\s+)?\"?(\w+)",
                         re.I)
_RE_FUNCTIE = re.compile(r"CREATE (?:OR REPLACE )?FUNCTION\s+(?:[\w@{}%\"]+\.)?\"?(\w+)\"?\s*\(", re.I)
_Q = r"(?:[\w@{}%\"]+\.)?\"?(\w+)\"?"
_RE_TRIGGER = re.compile(r"CREATE (?:CONSTRAINT )?TRIGGER\s+\w+[^;]*?\bON\s+" + _Q + r"[^;]*?EXECUTE (?:FUNCTION|PROCEDURE)\s+" + _Q, re.I)
_RE_CORP = re.compile(r"CREATE (?:OR REPLACE )?FUNCTION\s+" + _Q + r"\s*\(.*?\$(\w*)\$(.*?)\$\2\$", re.I | re.S)


def _date_python(src):
    """([{șirurile unui tuplu / unei liste}], {toate șirurile}) — SQL-ul compus din date: `("accounting_firms", ("cui", "cif_intocmit"))`."""
    import ast
    arb = ast.parse(src)

    def siruri(n):
        return {c.value for c in ast.walk(n) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    return [siruri(n) for n in ast.walk(arb) if isinstance(n, (ast.Tuple, ast.List))], siruri(arb)


def _ordinea_din_cod():
    """({migrare: SQL executat}, {(migrarea care folosește, migrarea care creează)}) — din SQL-ul EXECUTAT (fără docstringuri) al
    migrărilor de pe disc. Folosește = numește o tabelă sau o funcție creată de cealaltă, ori, în aceeași instrucțiune, tabela și
    coloana adăugată de cealaltă; ce creează și ea însăși (`IF NOT EXISTS`) nu e o dependență. [lotul 11, poarta 1] Și coloana folosită
    în SQL COMPUS din date sau din triggere, unde tabela și coloana nu stau în aceeași instrucțiune: (a) în același tuplu Python
    (`("accounting_firms", ("cui", "cif_intocmit"))`); (b) `NEW.col` / `OLD.col` în corpul funcției unui trigger creat `ON` tabela;
    (c) `NEW.col` / `OLD.col` într-o migrare care numește tabela ca șir Python (triggerul compus `ON %s.%s` din date). Pățit: copia
    cifrelor a rulat `migrare_cui_fara_ro` înaintea lui `migrare_intocmitor_bilant` (alfabetic) -> `cif_intocmit` lipsea."""
    sql, date = {}, {}
    for f in sorted(glob.glob(os.path.join(_RAD, "core", "migrare_*.py"))):
        cale, text = os.path.relpath(f, _RAD), open(f, encoding="utf-8").read()
        if mr.e_migrare(cale, text):
            sql[cale] = "\n".join(_siruri_executate(text))
            date[cale] = _date_python(text)

    def cuvant(nume, text):
        return re.search(r"\b%s\b" % re.escape(nume), text) is not None

    def fara_literale(s):   # [lotul 11] o coloană numită într-un literal SQL nu e o folosire: `CHECK (sursa IN ('propunere', 'manual'))`
        return re.sub(r"'[^']*'", "''", s)   # din `migrare_reevaluari_valuta` nu citește coloana `manual` a lui `migrare_reevaluare_partener`

    def din_trigger(col, text):
        return re.search(r"\b(?:NEW|OLD)\.%s\b" % re.escape(col), text) is not None

    def folosita_compus(b, tb, tab, col):
        grupuri, siruri = date[b]
        corp = {m.group(1): m.group(3) for m in _RE_CORP.finditer(tb)}
        return (any(tab in g and col in g for g in grupuri)
                or any(t == tab and din_trigger(col, corp.get(f, "")) for t, f in (m.groups() for m in _RE_TRIGGER.finditer(tb)))
                or (tab in siruri and din_trigger(col, tb)))

    def creeaza(text):
        return ({m.group(1) for m in _RE_TABELA.finditer(text)} | {m.group(1) for m in _RE_FUNCTIE.finditer(text)},
                {m.groups() for m in _RE_COLOANA.finditer(text)})
    perechi = set()
    for a, ta in sql.items():
        nume_a, coloane_a = creeaza(ta)
        for b, tb in sql.items():
            if b == a:
                continue
            nume_b, coloane_b = creeaza(tb)
            if any(cuvant(n, tb) for n in nume_a - nume_b) or any(
                    cuvant(tab, s) and cuvant(col, fara_literale(s)) for tab, col in coloane_a - coloane_b for s in tb.split(";")) or any(
                    folosita_compus(b, tb, tab, col) for tab, col in coloane_a - coloane_b):
                perechi.add((b, a))
    return sql, perechi


def test_ordinea_numeste_tot_ce_creeaza_alta_migrare():
    """[18.10.2026, poarta 1 a lotului 7] O migrare care folosește o tabelă, o coloană sau o funcție create de ALTĂ migrare se rulează după ea: `DUPA` le numește pe
    toate, exact (o pereche nouă nenumită sau una rămasă după o ștergere pică), iar ordinea rulării (`in_ordine`) le respectă pe toate,
    fără cicluri. Pățit: copia cifrelor F1–F5 a rulat `migrare_ciorne_proprii` înaintea lui `migrare_nr_curent_note` (alfabetic) și a
    picat; pe producție ar fi picat la fel. MUTAȚIE: perechea ciorne_proprii -> nr_curent_note scoasă din `DUPA` -> pică."""
    sql, din_cod = _ordinea_din_cod()
    declarate = {(b, a) for b, lista in mr.DUPA.items() for a in lista}
    assert declarate == din_cod, "nenumite în DUPA: %s; în DUPA fără temei în cod: %s" % (
        sorted(din_cod - declarate), sorted(declarate - din_cod))
    assert ("core/migrare_ciorne_proprii.py", "core/migrare_nr_curent_note.py") in din_cod, "anti-vacuu: perechea pățită nu mai e găsită"
    for compus in (("core/migrare_cui_fara_ro.py", "core/migrare_intocmitor_bilant.py"),          # (a) tuplul Python
                   ("core/migrare_reguli_fond_2.py", "core/migrare_declaratii_depuse_randuri.py"),  # (b) corpul funcției triggerului
                   ("core/migrare_cui_fara_ro.py", "core/migrare_tert_platitor_tva.py")):          # (c) triggerul compus din date
        assert compus in din_cod, "anti-vacuu: forma compusă %s nu mai e găsită" % (compus,)
    loc = {f: i for i, (f, _a) in enumerate(mr.in_ordine((f, "x") for f in sql))}
    assert len(loc) == len(sql)
    assert all(loc[a] < loc[b] for b, a in declarate), sorted((b, a) for b, a in declarate if loc[a] >= loc[b])


def test_nerulate_le_da_in_ordinea_rularii(conn):
    """`verifica` (comenzile tipărite) și copia cifrelor rulează nerulatele în ordinea întoarsă de `nerulate`: întâi cea care creează
    tabela. MUTAȚIE: `nerulate` întoarce iar `sorted(...)` -> ciorne_proprii înaintea lui nr_curent_note -> pică."""
    m = {"core/migrare_ciorne_proprii.py": "a" * 64, "core/migrare_nr_curent_note.py": "b" * 64, "core/migrare_zz_proba_c.py": "c" * 64}
    with conn.cursor() as cur:
        assert [f for f, _a in mr.nerulate(cur, m)] == [
            "core/migrare_nr_curent_note.py", "core/migrare_ciorne_proprii.py", "core/migrare_zz_proba_c.py"]


def test_ruleaza_refuza_migrarea_inaintea_celei_de_care_depinde(conn, monkeypatch):
    """Pe producție migrările se rulează de mână, una câte una: `ruleaza` refuză `migrare_ciorne_proprii` cât timp conținutul de azi al lui
    `migrare_nr_curent_note` n-are rândul lui în registrul aceleiași baze, și o lasă după. MUTAȚIE: verificarea scoasă din `main` ->
    rulatorul pornește migrarea -> pică (`run_path` e înlocuit, nu rulează nimic)."""
    import runpy
    cur = conn.cursor()
    monkeypatch.setattr(mr, "_cu_registrul", lambda scrie: scrie(cur))
    monkeypatch.setattr(runpy, "run_path", lambda *a, **k: (_ for _ in ()).throw(AssertionError("a pornit migrarea")))
    monkeypatch.setattr(mr, "_reporneste_daca_e_cazul", lambda productie: None)

    def rulata(f):
        mr.inregistreaza(cur, f, mr.amprenta(open(os.path.join(_RAD, f), encoding="utf-8").read()), "rulata", "proba")
    rulata("core/migrare_validare_note.py")             # cealaltă dinaintea ei (`creat_de_id`), rulată
    with pytest.raises(SystemExit) as e:
        mr.main(["ruleaza", "core/migrare_ciorne_proprii.py"])
    assert str(e.value) == ("core/migrare_ciorne_proprii.py se rulează după core/migrare_nr_curent_note.py, nerulată încă pe această "
                            "bază — rulează întâi: python -m core.migrari_registru ruleaza core/migrare_nr_curent_note.py")
    rulata("core/migrare_nr_curent_note.py")
    assert mr.inainte_nerulate(cur, "core/migrare_ciorne_proprii.py") == []
    with pytest.raises(AssertionError, match="a pornit migrarea"):
        mr.main(["ruleaza", "core/migrare_ciorne_proprii.py"])
