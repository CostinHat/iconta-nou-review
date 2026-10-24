# -*- coding: utf-8 -*-
"""core/migrare_motiv_scutire.py — salariații scutiți de contribuția minimă fără motivul scutirii (lotul 12, C133).

DEFECTUL (C133). Ecranul „Salariat nou” nu avea câmpul „Motivul scutirii”, iar importul salariaților nu-l citea: un salariat scutit
intra cu `motiv_exceptare` gol. D112 îl declara atunci `asigExc` 0 (neexceptat), deși statul nu-i calcula contribuția minimă.
TEMEI: OPANAF 605/2026 anexa 2, secțiunea „Date de identificare ale asiguratului”, pct.12: „Motivul exceptării - se completează în cazul
în care caseta de la pct.11 a fost completată cu valoarea «1»” (motivele 1–5 = CF art.146 alin.(5^7) lit.a–e).

CE FACE (datele existente): marchează „de verificat” (`de_verificat` += „motiv_exceptare”) fiecare salariat scutit fără motiv — în Stat
de plată apare avertismentul și butonul „De verificat”, de unde contabilul alege motivul (`salariati_api.actualizeaza_salariat` scoate
marcajul la salvare). Motivul NU se presupune; nimic altceva nu se schimbă. D112 refuză până atunci, numind salariatul (`d112.genereaza`).
Idempotentă. Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_motiv_scutire.py`.
"""
from core import db

SQL = ("UPDATE \"{s}\".salariati SET de_verificat = array_append(de_verificat, 'motiv_exceptare') "
       "WHERE scutit_contrib_minim AND motiv_exceptare IS NULL AND NOT ('motiv_exceptare' = ANY(de_verificat)) RETURNING id")


def aplica(conn, schema):
    """-> [id-urile salariaților marcați]."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".salariati' % schema,))
        if cur.fetchone()[0] is None:
            return []
        cur.execute(SQL.format(s=schema))
        return [r[0] for r in cur.fetchall()]


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".salariati' % schema,))
        if cur.fetchone()[0] is None:
            return True
        cur.execute('SELECT count(*) FROM "%s".salariati WHERE scutit_contrib_minim AND motiv_exceptare IS NULL '
                    "AND NOT ('motiv_exceptare' = ANY(de_verificat))" % schema)
        return cur.fetchone()[0] == 0


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, n = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                ids = aplica(conn, s)
                conn.commit()
            ok += 1
            n += len(ids)
            if ids:
                print("  %s: salariații %s marcați „de verificat” — motivul scutirii lipsește" % (s, ids))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_motiv_scutire: %d ok, %d esec, %d salariați marcați" % (ok, len(esec), n))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
