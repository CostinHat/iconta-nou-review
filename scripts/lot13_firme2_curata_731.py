# -*- coding: utf-8 -*-
"""scripts/lot13_firme2_curata_731.py — datele existente ale deficienței 589 (lotul 13, comanda Costin 13.1, verbatim: „589: Plan de conturi |
Contul sintetic 731 (în afara planului legal) a fost adăugat manual; avertismentul apare după salvare; contul nu se poate șterge. Adăugarea
manuală doar pentru analitice sub sintetic legal. De curățat de Code: 731 «Test cont nelegal» pe F6.”).

CE FACE. Scoate din planul de conturi al firmei numite contul 731 „Test cont nelegal” — numai dacă e EXACT acel cont (simbolul 731 și
denumirea „Test cont nelegal”, scris de mână la retest) și numai dacă regula ștergerii din aplicație (`uc_tenants.motiv_nestergere`,
aceeași ca butonul „Șterge” din Plan de conturi) îl lasă: fără rulaj în note, fără sold inițial, fără analitice, cont din afara planului
legal al normei firmei. Altfel nu scrie nimic și spune motivul. Nu atinge nicio notă și niciun alt cont.

DE CE UN SCRIPT, NU O MIGRARE. E o curățenie pe o singură firmă de test (F6, cabinetul de test), nu o regulă pentru toate firmele: un 731
pus de mână pe altă firmă e alegerea contabilului ei (iar de acum aplicația nu-l mai lasă să-l adauge). Se rulează de sesiunea principală,
după backup, pe producție (`--productie`), pe schema F6 (`tenant_055`; copia de dovadă: `tenant_9055`).
Uz: ./venv/bin/python scripts/lot13_firme2_curata_731.py [--productie] (--proba | --scrie) --schema tenant_055
  --proba: totul într-o tranzacție anulată (nimic scris), aceeași tipărire. Idempotent: a doua rulare spune că nu mai e nimic de scos."""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

SIMBOL = "731"
DENUMIRE = "Test cont nelegal"


def curata(conn, schema):
    """-> (scos: bool, mesaj). Scrie numai în tranzacția apelantului."""
    from core import db, plan_legal as _pl, repo_contabilitate as _rc
    from core.uc_tenants import motiv_nestergere
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute('SET LOCAL search_path TO "%s", public' % schema)
        den = _rc.denumirea_contului(cur, SIMBOL)
        if not den:
            return False, "contul %s nu e în planul firmei: nimic de scos" % SIMBOL
        if den[0] != DENUMIRE:
            return False, "contul %s are denumirea %r, nu %r: nu e contul de test, nu se atinge" % (SIMBOL, den[0], DENUMIRE)
        motiv = motiv_nestergere(SIMBOL, _rc.conturi_folosite(cur, [SIMBOL]), _rc.conturi_cu_sold_initial(cur, [SIMBOL]),
                                 set(_pl.in_afara(cur, schema, [SIMBOL])), [r[0] for r in _rc.toate_conturile(cur)])
        if motiv:
            return False, "contul %s nu se scoate: %s" % (SIMBOL, motiv)
        if not _pl.in_afara(cur, schema, [SIMBOL]):
            return False, "contul %s e în planul legal al normei firmei: nu e contul greșit, nu se atinge" % SIMBOL
        n = _rc.sterge_cont_din_plan(cur, SIMBOL)
        return bool(n), "contul %s „%s” scos din planul firmei (%d rând)" % (SIMBOL, DENUMIRE, n)


def main(argv):
    proba, scrie = "--proba" in argv, "--scrie" in argv
    scheme = [argv[i + 1] for i, a in enumerate(argv) if a == "--schema" and i + 1 < len(argv)]
    if proba == scrie or len(scheme) != 1:
        print(__doc__)
        return 2
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    from core import db
    db.init_pool()
    with db.get_conn(scheme[0]) as conn:
        _scos, mesaj = curata(conn, scheme[0])
        print("%s: %s" % (scheme[0], mesaj))
        conn.rollback() if proba else conn.commit()
    print("(proba: nimic scris)" if proba else "(scris)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
