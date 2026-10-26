# -*- coding: utf-8 -*-
"""core/migrare_explicatie_raport_z.py — explicația notelor raportului Z scrise cu data ISO (lotul 13, deficiența 618).

DEFICIENȚA (comanda Costin 13.1, verbatim): „618: Raport Z | Titlul notei cu data ISO («Raport Z 2026-10-20»)”. Cele două drumuri ale Z-ului
scriau explicația notei cu data cum vine din formular / din fișierul AMEF:
  * scris de mână (`uc_tenants.horeca_raport_z`): „Raport Z 2026-10-20 casa 8000000001 nr 0042”;
  * importat din AMEF (`uc_tenants.horeca_import_amef`): „Raport Z 2026-10-20 AMEF 8000000001 nr 0042 (12 bonuri) - de verificat cu Z tiparit”.
Reparația de cod: `jurnal_api.explicatie_raport_z` (sursa unică, data românească). Regula 3a („Orice reparație acoperă și datele existente”):

CE FACE: rescrie explicația notelor CIORNĂ ale raportului Z (`sursa` în `raport_z.SURSE`) scrise în forma veche, cu aceeași funcție ca
drumurile de scriere — numai când textul întreg se potrivește formei vechi (casa, numărul, data și bonurile se citesc din el; un text
scris de altcineva nu se atinge).
CE NU FACE: nota VALIDATĂ nu se modifică — e evidență (regula de fond `trg_regula_nota`: „Nota … e validată, deci nu se mai modifică.
Corectura se face prin stornare (OMFP 1802/2014 pct.69)”); migrarea o numește la rulare. O ciornă dintr-o lună blocată rămâne și se
numește (regula `trg_verifica_perioada_blocata`).
Idempotentă (a doua rulare nu mai găsește forma veche). Rulare: `python -m core.migrari_registru ruleaza [--productie]
core/migrare_explicatie_raport_z.py`.
"""
import re

from core import db

#: forma veche a explicației, pe cele două drumuri (textul ÎNTREG, ca un text scris de om să nu fie atins)
_RE_MANA = re.compile(r"^Raport Z (\d{4}-\d{2}-\d{2}) casa (\S+) nr (\S+)$")
_RE_AMEF = re.compile(r"^Raport Z (\d{4}-\d{2}-\d{2}) AMEF (\S+) nr (\S+) \((\d+) (?:de )?(?:bon|bonuri)\) - de verificat cu Z tiparit$")


def explicatia_noua(descriere):
    """PURĂ. Explicația în forma de acum pentru o explicație veche a Z-ului, sau None (alt text: nu se atinge)."""
    from core import jurnal_api as _j
    m = _RE_MANA.match(descriere or "")
    if m:
        return _j.explicatie_raport_z(m.group(1), m.group(2), m.group(3))
    m = _RE_AMEF.match(descriere or "")
    if m:
        return _j.explicatie_raport_z(m.group(1), m.group(2), m.group(3), int(m.group(4)), amef=True)
    return None


def aplica(conn, schema):
    """-> {"rescrise": [id], "validate": [id], "ramase": [(id, motiv)]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import raport_z as _rz
    rez = {"rescrise": [], "validate": [], "ramase": []}
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".inregistrari' % schema,))
        if cur.fetchone()[0] is None:
            return rez
        cur.execute('SELECT id, status, descriere FROM "%s".inregistrari WHERE sursa = ANY(%%s) AND descriere LIKE %%s ORDER BY id' % schema,
                    (list(_rz.SURSE), "Raport Z %"))
        for iid, status, descriere in cur.fetchall():
            nou = explicatia_noua(descriere)
            if nou is None:
                continue
            if status != "ciorna":
                rez["validate"].append(iid)
                continue
            cur.execute("SAVEPOINT explicatie_z")
            try:
                cur.execute(f'UPDATE "{schema}".inregistrari SET descriere = %s WHERE id = %s AND status = \'ciorna\' '
                            'AND descriere IS NOT DISTINCT FROM %s', (nou, iid, descriere))
            except Exception as e:  # noqa: BLE001 — refuzul unei reguli de fond (luna blocată), numit
                cur.execute("ROLLBACK TO SAVEPOINT explicatie_z")
                rez["ramase"].append((iid, str(e).strip().split("\n")[0]))
                continue
            cur.execute("RELEASE SAVEPOINT explicatie_z")
            rez["rescrise"].append(iid)
    return rez


def verifica(conn, schema):
    """Nu mai rămâne nicio ciornă a Z-ului cu explicația în forma veche (una dintr-o lună blocată rămâne, și verificarea o arată)."""
    from core import raport_z as _rz
    with conn.cursor() as cur:
        cur.execute('SELECT descriere FROM "%s".inregistrari WHERE sursa = ANY(%%s) AND status = %%s AND descriere LIKE %%s' % schema,
                    (list(_rz.SURSE), "ciorna", "Raport Z %"))
        return not [d for (d,) in cur.fetchall() if explicatia_noua(d)]


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
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            n += len(r["rescrise"])
            if r["rescrise"]:
                print("  %s: explicația ciornelor Z %s rescrisă cu data românească" % (s, r["rescrise"]))
            for iid in r["validate"]:
                print("  %s: nota Z VALIDATĂ #%s păstrează explicația scrisă atunci — o notă validată nu se modifică" % (s, iid))
            for iid, motiv in r["ramase"]:
                print("  %s: ciorna Z #%s rămâne — %s" % (s, iid, motiv))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_explicatie_raport_z: %d ok, %d esec, %d ciorne rescrise" % (ok, len(esec), n))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
