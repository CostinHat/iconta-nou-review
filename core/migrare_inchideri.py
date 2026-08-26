"""
core/migrare_inchideri.py — R58: închiderea și redeschiderea unei perioade lasă URMĂ.

Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotent:
CREATE TABLE IF NOT EXISTS. Se aplică pe:
  - tenanți NOI: prin tenant_template.sql (la provisionare);
  - tenanți EXISTENȚI: `python3 -m core.migrare_inchideri`.

DE CE, cu instanța. Măsurat 26.08.2026: `DELETE /tenants/{id}/perioade-blocate` **ștergea
rândul** din `perioade_blocate`. Odată cu el dispăreau `blocat_de`, `blocat_la` și însuși faptul
că perioada fusese vreodată închisă. Tabela n-are coloană de motiv, deci nici motivul n-avea unde
sta. Asta e **interdicția 36** („o redeschidere de perioadă fără motiv consemnat") și **P15**
(„închiderea e act deliberat, cu autor · redeschiderea e act consemnat, cu motiv") — direct, nu
prin analogie. Aici planul nu cerea o decizie: o spunea deja.

DE CE O TABELĂ SEPARATĂ, și nu coloane noi pe `perioade_blocate`. `_cere_luna_deschisa` întreabă
`SELECT 1 FROM perioade_blocate WHERE an=%s AND luna=%s` la **fiecare** scriere de notă. Dacă
rândul ar rămâne pe loc cu un marcaj de „redeschis", poarta ar trebui să înceapă să citească acel
marcaj — o schimbare într-un drum cald, pentru o cerință de istoric. Aici: poarta rămâne
neatinsă, iar istoricul e append-only lângă ea. Urma e o **evidență**, nu o stare.

CE PĂSTREAZĂ, și de ce exact câmpurile astea:
  actiune   — `inchisa` / `redeschisa`. Fără ea, două rânduri consecutive n-ar spune ce s-a
              întâmplat, doar că s-a atins ceva.
  motiv     — obligatoriu la redeschidere (interdicția 36). La închidere e opțional: închiderea
              e actul normal, redeschiderea e cea care cere justificare.
  cine_id   — P16: act cu efect asupra evidenței, autor identificat.
  cand      — momentul.
Append-only: nu se șterge și nu se editează, ca orice urmă (P16, stratul URMA din Partea II).
"""
from core import db

# {s} = numele schemei (validat înainte). {{}} = acolade literale pentru .format().
DDL = """
CREATE TABLE IF NOT EXISTS "{s}".perioade_inchideri (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    an integer NOT NULL,
    luna integer NOT NULL,
    actiune text NOT NULL,
    motiv text,
    cine_id integer,
    cand timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT perioade_inchideri_actiune CHECK (actiune IN ('inchisa', 'redeschisa')),
    CONSTRAINT perioade_inchideri_motiv_la_redeschidere
        CHECK (actiune <> 'redeschisa' OR btrim(coalesce(motiv, '')) <> '')
);
CREATE INDEX IF NOT EXISTS perioade_inchideri_perioada
    ON "{s}".perioade_inchideri (an, luna, cand);
"""


def aplica(conn, schema):
    """Aplică DDL-ul idempotent pe o schemă. Ridică dacă numele e invalid."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    """True dacă schema are tabelul `perioade_inchideri`."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".perioade_inchideri",))
        return cur.fetchone()[0] is not None


def scrie(conn, schema, an, luna, actiune, cine_id, motiv=None):
    """Consemnează actul. Constrângerea de motiv e în BAZĂ, nu doar aici — o urmă care se poate
    scrie fără motiv de pe altă cale n-ar fi o urmă."""
    with conn.cursor() as cur:
        cur.execute('INSERT INTO "%s".perioade_inchideri (an, luna, actiune, motiv, cine_id) '
                    "VALUES (%%s,%%s,%%s,%%s,%%s)" % schema,
                    (an, luna, actiune, (motiv or None), cine_id))


def istoric(conn, schema, an=None, luna=None):
    """Actele consemnate, cronologic. Fără filtru: toate."""
    unde, arg = "", ()
    if an is not None and luna is not None:
        unde, arg = "WHERE an=%s AND luna=%s", (an, luna)
    with conn.cursor() as cur:
        cur.execute('SELECT an, luna, actiune, motiv, cine_id, cand FROM "%s".perioade_inchideri '
                    "%s ORDER BY cand" % (schema, unde), arg)
        return [{"an": r[0], "luna": r[1], "actiune": r[2], "motiv": r[3],
                 "cine_id": r[4], "cand": r[5]} for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
        scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                    print("  OK  %s" % s)
                else:
                    esec.append(s)
                    print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s)
            print("  ESEC %s: %s" % (s, e))
    print("Migrare perioade_inchideri: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
