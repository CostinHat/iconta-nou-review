# -*- coding: utf-8 -*-
"""core/migrare_extrabilant.py — evidența în afara bilanțului (clasa 8), într-o singură parte, și registrul obiectelor de inventar (lotul 13).

DE CE — comanda Costin 13.1, verbatim:
  507: „Evidența în afara bilanțului e înregistrată 8035 = 891 / 891 = 8035; 891 e «Bilanț de deschidere». Clasa 8 se înregistrează într-o
       singură parte (doar debit 8035 la dare, doar credit la scoatere) și nu intră în totalurile de rulaje (azi totalul ciornelor le
       include).”
  508: „Dare și scoatere din folosință nu sunt legate de obiecte: se poate da sau scoate orice sumă fără verificare. Obiectul se alege din
       cele existente, valoarea vine de la el.”
TEMEI: OMFP 1802/2014, planul de conturi, clasa 8 „Conturi speciale” — conturile în afara bilanțului (8035 „Alte valori în afara
bilanțului”, 8051 „Dobânzi de plătit”, 8011 / 8021 „Giruri și garanții”, 8038 „Bunuri primite în administrare, concesiune, cu chirie și
alte bunuri similare”) țin evidența într-o singură parte (debit la intrare, credit la ieșire); 891 „Bilanț de deschidere” e contul de
deschidere a exercițiului, nu o contrapartidă.

CE ADAUGĂ (oglindit în `tenant_template.sql`, peticul `l13_petice/ops_template.json`):
  - `evidenta_extrabilant` — rândul clasei 8 (D sau C, o singură parte), cu data și documentul lui: legat de nota operației care îl
    produce (darea în folosință, primirea în leasing — există cât există nota) sau de sine stătător, când operația n-are rânduri în
    bilanț (scoaterea din folosință, comodatul, garanția: numai documentul, de ex. procesul-verbal); nu intră în rândurile notelor, deci
    nici în totalurile rulajelor;
  - `obiecte_inventar` — obiectul de inventar ca obiect (denumire, valoare, furnizorul și factura lui, nota intrării), cu nota care îl
    dă în folosință și înregistrarea care îl scoate (C 8035); starea se citește din ele (o ciornă ștearsă desface singură legătura:
    `ON DELETE SET NULL`).
DATELE EXISTENTE: rândurile `8xxx = 891` / `891 = 8xxx` din CIORNE trec în `evidenta_extrabilant` și ies din notă (nota nevalidată se
poate corecta); notele VALIDATE nu se ating (OMFP 1802/2014 pct.69: o notă validată se corectează prin stornare) — se numără și se spun
în raportul lotului. Obiectele de inventar de dinainte n-au registru (nota nu le numea): registrul pornește gol.
"""
import sys

from core import db

_DDL = [
    'CREATE TABLE IF NOT EXISTS "{s}".evidenta_extrabilant ('
    ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
    ' inregistrare_id integer REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE,'
    ' data date NOT NULL,'
    ' document text,'
    " cont text NOT NULL CHECK (cont LIKE '8%%'),"
    " sens char(1) NOT NULL CHECK (sens IN ('D', 'C')),"
    ' suma numeric(14,2) NOT NULL CHECK (suma > 0),'
    ' explicatie text,'
    ' obiect_id integer,'
    ' mijloc_fix_id integer);',
    'CREATE INDEX IF NOT EXISTS evidenta_extrabilant_nota_idx ON "{s}".evidenta_extrabilant (inregistrare_id);',
    'CREATE TABLE IF NOT EXISTS "{s}".obiecte_inventar ('
    ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
    ' denumire text NOT NULL,'
    ' valoare numeric(14,2) NOT NULL CHECK (valoare > 0),'
    ' data_intrare date NOT NULL,'
    ' furnizor_cui text, furnizor_nume text, factura_numar text,'
    ' nota_intrare_id integer REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE,'
    ' factura_id integer,'
    ' nota_dare_id integer REFERENCES "{s}".inregistrari(id) ON DELETE SET NULL,'
    ' scoatere_id integer REFERENCES "{s}".evidenta_extrabilant(id) ON DELETE SET NULL,'
    ' creat_la timestamptz NOT NULL DEFAULT now());',
    # [lotul 13, garda CUI-ului fără „RO” (decizia Costin 10.3 pct.4)] codul furnizorului, normalizat în bază pe orice drum, cu funcția
    # creată de `migrare_cui_fara_ro` (ca toate coloanele de cod fiscal: core/test_lot11_p_cui.py); alt nume decât `trg_cui_fara_ro`, ca `migrare_cui_fara_ro.verifica`
    # (care numără triggerele lui, câte una pe tabelă din `COLOANE_FIRMA`) să rămână adevărată
    'DROP TRIGGER IF EXISTS trg_cui_fara_ro_l13 ON "{s}".obiecte_inventar;',
    'CREATE TRIGGER trg_cui_fara_ro_l13 BEFORE INSERT OR UPDATE OF furnizor_cui ON "{s}".obiecte_inventar FOR EACH ROW '
    'EXECUTE FUNCTION "{s}".cui_normalizeaza(\'furnizor_cui\');',
]


def aplica_ddl(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema).replace("%%", "%"))


def backfill(conn, schema):
    """Rândurile clasei 8 cu 891 din CIORNE -> `evidenta_extrabilant`; notele validate se numără (neatinse). {mutate, validate_neatinse}."""
    s = '"%s".' % schema
    with conn.cursor() as cur:
        cur.execute("SELECT l.id, l.inregistrare_id, l.cont_debit, l.cont_credit, l.suma, i.status FROM %sinregistrari_linii l "
                    "JOIN %sinregistrari i ON i.id = l.inregistrare_id WHERE (l.cont_debit LIKE '8%%' AND l.cont_credit = '891') "
                    "OR (l.cont_debit = '891' AND l.cont_credit LIKE '8%%')" % (s, s))
        mutate = validate = goale = blocate = 0
        for lid, nid, cd, cc, suma, status in cur.fetchall():
            if status == "validata":
                validate += 1
                continue
            cont, sens = (cd, "D") if cd.startswith("8") else (cc, "C")
            cur.execute("SELECT data, document_ref FROM %sinregistrari WHERE id = %%s" % s, (nid,))
            data, doc = cur.fetchone()
            # ciorna dintr-o lună închisă nu se schimbă (`trg_regula_linii_nota`: PERIOADA_BLOCATA) — rămâne cum e și se numără
            cur.execute("SELECT 1 FROM %sperioade_blocate WHERE an = %%s AND luna = %%s" % s, (data.year, data.month))
            if cur.fetchone():
                blocate += 1
                continue
            cur.execute("DELETE FROM %sinregistrari_linii WHERE id = %%s" % s, (lid,))
            cur.execute("SELECT count(*) FROM %sinregistrari_linii WHERE inregistrare_id = %%s" % s, (nid,))
            ramase = cur.fetchone()[0]
            cur.execute("INSERT INTO %sevidenta_extrabilant (inregistrare_id, data, document, cont, sens, suma, explicatie) "
                        "VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s)" % s,
                        (nid if ramase else None, data, doc, cont, sens, suma, "mutat din rândul %s = %s al ciornei (lotul 13, 507)" % (cd, cc)))
            mutate += 1
            if not ramase:   # ciorna avea numai rândul clasei 8: rămâne înregistrarea în afara bilanțului, cu documentul ei; nota goală iese
                cur.execute("DELETE FROM %sinregistrari WHERE id = %%s" % s, (nid,))
                goale += 1
    return {"mutate": mutate, "ciorne_goale_scoase": goale, "validate_neatinse": validate, "ciorne_in_luni_inchise_neatinse": blocate}


def aplica(conn, schema):
    aplica_ddl(conn, schema)
    return backfill(conn, schema)


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL",
                    ('"%s".evidenta_extrabilant' % schema, '"%s".obiecte_inventar' % schema))
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                n = aplica(conn, s)
                conn.commit()
            ok += 1
            if any(n.values()):
                print("  %s: %s" % (s, ", ".join("%s %d" % kv for kv in n.items() if kv[1])))
        except Exception as e:  # noqa: BLE001 — o firmă căzută nu le oprește pe celelalte; se raportează și ieșirea e 1
            esec.append((s, str(e)))
    print("migrare_extrabilant: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        sys.exit(1)


if __name__ == "__main__":
    _main()
