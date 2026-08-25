"""
core/migrare_artefacte.py — R45: un artefact produs se PĂSTREAZĂ.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
CREATE TABLE IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: `python3 -m core.migrare_artefacte`.

CE ADAUGA, si de ce exact campurile astea. Decizia lui Costin, 25.08.2026:
*"Se pastreaza, cu: artefactul insusi, momentul, autorul, amprenta continutului, si
numarul exemplarului. Iar daca e o declaratie, plus verdictul de validare cu amprenta
fisierului validat. Un artefact produs si nepastrat nu se poate apara. E chiar P4."*

  continut   — artefactul insusi. Fara el, restul e metadata despre nimic.
  produs_la  — momentul.
  produs_de_id / produs_de — autorul (P16: act cu efect extern, autor identificat).
  amprenta   — sha256 al continutului. CE s-a produs, nu ce s-ar produce acum daca s-ar
               regenera. Un artefact fara amprenta nu se poate confrunta cu o copie.
  exemplar   — P4: emiterea e idempotenta si REPETABILA, iar al doilea exemplar e un FAPT,
               nu o eroare. Numarul creste per (fel, cheie), nu global.
  verdict*   — DOAR la artefactele care se valideaza. Aceleasi patru campuri construite la
               R41, ca sa nu existe doua vocabulare pentru acelasi lucru.

DE CE IN SCHEMA FIRMEI, nu in `public`: e evidenta unei firme. `declaratii_coada` si
`declaratii_depuse` stau in public si de-aia stergerea unui cabinet le lasa in urma
(masurat 25.08: un rand orfan, plus 65 de randuri de audit). Nu repet forma aia.

FARA UNIQUE pe (fel, cheie): al doilea exemplar TREBUIE sa poata exista. Unicitatea e pe
(fel, cheie, exemplar) — adica nu se pot scrie doua exemplare cu acelasi numar.
"""
from core import db

# {s} = numele schemei (validat inainte). {{}} = acolade literale pentru .format().
DDL = """
CREATE TABLE IF NOT EXISTS "{s}".artefacte_produse (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fel text NOT NULL,
    cheie text NOT NULL,
    exemplar integer NOT NULL,
    continut text,
    amprenta text NOT NULL,
    produs_la timestamptz NOT NULL DEFAULT now(),
    produs_de_id integer,
    produs_de text,
    verdict text,
    verdict_la timestamptz,
    verdict_versiune text,
    verdict_amprenta text,
    CONSTRAINT artefacte_exemplar_unic UNIQUE (fel, cheie, exemplar)
);
CREATE INDEX IF NOT EXISTS artefacte_fel_cheie ON "{s}".artefacte_produse (fel, cheie);
"""


def aplica(conn, schema):
    """Aplica DDL-ul idempotent pe o schema. Ridica daca numele e invalid."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    """True daca schema are tabelul artefacte_produse."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".artefacte_produse",))
        return cur.fetchone()[0] is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
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
    print("Migrare artefacte_produse: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
