# -*- coding: utf-8 -*-
"""core/migrare_mf_note.py — mijlocul fix ȚINUT PE ACTIV în note și activul schimbat de o notă numai prin VALIDAREA ei (lotul 13).

DE CE — comanda Costin 13.1, verbatim:
  519: „După ștergerea ciornei de casare, MF-001 rămâne «casat», fără acțiuni și fără cifre în registru. Ștergerea notei readuce activul
       la «activ». La fel la Plus mijloc fix din inventar: activul intră în registru din ciornă și rămâne după ștergerea ei. Regula: un
       activ adăugat sau schimbat de o notă există în registru numai după validarea ei și dispare la ștergere. De refăcut pe F2: MF-001
       activ, MF-PLUS scos.”
  522: „Coloana «Înregistrat» se citește pe cont (2813), nu pe activ. Cu MF-001 «casat», întreaga amortizare a lui (4.000) apare la
       MF-PLUS […] Amortizarea înregistrată se ține pe fiecare activ.”

CE ADAUGĂ (oglindit în `tenant_template.sql`, peticul `l13_petice/ops_template.json`):
  - `mf_linii (linie_id, mijloc_fix_id)` — rândul notei și activul lui (amortizarea lunii, casarea, reevaluarea, plusul de inventar,
    subvenția): amortizarea înregistrată a unui activ = rândurile LUI pe contul de amortizare, nu soldul contului. Tabel ALĂTURAT, nu
    coloană pe `inregistrari_linii`: rândurile notelor validate nu se mai schimbă (`trg_regula_linii_nota`, OMFP 1802/2014 pct.69), iar
    legarea rândurilor vechi de activ (pasul 1 de mai jos) nu atinge rândul — nici contul, nici suma, nici data;
  - `mf_note (inregistrare_id, mijloc_fix_id, fel)` — nota care aduce activul în registru (`intrare`: plus de inventar, achiziția
    necorporală, bunul primit în leasing) sau îl scoate (`iesire`: casarea);
  - triggerul `trg_mf_nota_status` (după schimbarea stării notei): la VALIDARE activul intrării devine activ, cel al ieșirii inactiv —
    pe ORICE drum de validare (Registrul jurnal, coada cabinetului), fiindcă stă în bază, nu într-un apelant; triggerul
    `trg_mf_nota_sterge` (înaintea ștergerii notei): activul pe care l-ar fi adus o ciornă ștearsă dispare din registru; o ieșire
    ștearsă nu mai are nimic de desfăcut (activul n-a fost scos decât la validare).

DATELE EXISTENTE (regula 3a, „Orice reparație acoperă și datele existente”), pe fiecare firmă, idempotent:
  1. rândurile de amortizare 68xx = 28xx (din notele tabloului lunii, `sursa = 'amortizare'`, și din notele manuale de amortizare —
     firmele care țineau amortizarea prin notă manuală): fiecare rând primește activul a cărui rată din luna notei (metoda lui,
     `d406_active.amortizare_luna`) e chiar suma rândului, pe contul lui de amortizare; rate egale — în ordinea registrului (aceeași
     sumă, deci aceeași cifră pe activ); un rând fără potrivire rămâne fără activ (registrul îl arată „pe cont, nealocat”);
  2. notele de reevaluare (`reevaluari.inregistrare_id`) și de casare („Casare <denumire> …”, conturile activului): rândurile pe
     conturile activului primesc activul;
  3. activul scos din evidență (`activ = false`) fără nicio notă VALIDATĂ care să-l scoată (credit pe contul activului cu valoarea lui):
     casarea lui a rămas ciornă (se leagă ca ieșire în așteptare) sau a fost ștearsă — activul redevine activ (F2: MF-001);
  4. activul adus de o operațiune (codurile date de aplicație: `MF-PLUS…`, `NEC-…`): nota lui de intrare ciornă -> intrare în așteptare
     (activul iese din registru până la validare); nota ștearsă -> activul se scoate, dacă nimic nu-l mai citește (F2: MF-PLUS).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_mf_note.py` (după `migrare_partener_linie`).
"""
import sys

from core import db

_DDL = [
    'CREATE TABLE IF NOT EXISTS "{s}".mf_linii ('
    ' linie_id integer PRIMARY KEY REFERENCES "{s}".inregistrari_linii(id) ON DELETE CASCADE,'
    ' mijloc_fix_id integer NOT NULL REFERENCES "{s}".mijloace_fixe(id) ON DELETE CASCADE);',
    'CREATE INDEX IF NOT EXISTS mf_linii_mijloc_idx ON "{s}".mf_linii (mijloc_fix_id);',
    'CREATE TABLE IF NOT EXISTS "{s}".mf_note ('
    ' inregistrare_id integer PRIMARY KEY REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE,'
    ' mijloc_fix_id integer NOT NULL REFERENCES "{s}".mijloace_fixe(id) ON DELETE CASCADE,'
    " fel text NOT NULL CHECK (fel IN ('intrare', 'iesire')));",
    'CREATE INDEX IF NOT EXISTS mf_note_mijloc_idx ON "{s}".mf_note (mijloc_fix_id);',
    'CREATE OR REPLACE FUNCTION "{s}".mf_nota_status() RETURNS trigger AS $$\n'
    'BEGIN\n'
    "  IF NEW.status = 'validata' AND OLD.status IS DISTINCT FROM 'validata' THEN\n"
    '    UPDATE "{s}".mijloace_fixe m SET activ = (n.fel = \'intrare\') FROM "{s}".mf_note n\n'
    '     WHERE n.inregistrare_id = NEW.id AND n.mijloc_fix_id = m.id;\n'
    "  ELSIF OLD.status = 'validata' AND NEW.status IS DISTINCT FROM 'validata' THEN\n"
    '    UPDATE "{s}".mijloace_fixe m SET activ = (n.fel = \'iesire\') FROM "{s}".mf_note n\n'
    '     WHERE n.inregistrare_id = NEW.id AND n.mijloc_fix_id = m.id;\n'
    '  END IF;\n'
    '  RETURN NEW;\n'
    'END $$ LANGUAGE plpgsql;',
    'DROP TRIGGER IF EXISTS trg_mf_nota_status ON "{s}".inregistrari;',
    'CREATE TRIGGER trg_mf_nota_status AFTER UPDATE OF status ON "{s}".inregistrari '
    'FOR EACH ROW EXECUTE FUNCTION "{s}".mf_nota_status();',
    'CREATE OR REPLACE FUNCTION "{s}".mf_nota_sterge() RETURNS trigger AS $$\n'
    'BEGIN\n'
    '  DELETE FROM "{s}".mijloace_fixe m USING "{s}".mf_note n\n'
    "   WHERE n.inregistrare_id = OLD.id AND n.fel = 'intrare' AND n.mijloc_fix_id = m.id AND NOT m.activ;\n"
    '  RETURN OLD;\n'
    'END $$ LANGUAGE plpgsql;',
    'DROP TRIGGER IF EXISTS trg_mf_nota_sterge ON "{s}".inregistrari;',
    'CREATE TRIGGER trg_mf_nota_sterge BEFORE DELETE ON "{s}".inregistrari '
    'FOR EACH ROW EXECUTE FUNCTION "{s}".mf_nota_sterge();',
]


def aplica_ddl(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def _mfs(cur, schema):
    """Toate mijloacele fixe (active sau nu), ca dicționarele motorului de amortizare."""
    from core import mf_registru as _mfr, repo_mijloace_fixe as _rmf
    cur.execute('SET LOCAL search_path TO "%s", public' % schema)
    return [_mfr._mf_dict(r) for r in _rmf.toate(cur)]


def _rata(mf, an, luna):
    from decimal import Decimal
    from core import d406_active as _a
    try:
        return Decimal(str(_a.amortizare_luna(mf, an, luna))).quantize(Decimal("0.01"))
    except (ValueError, KeyError, TypeError):
        return None


def backfill(conn, schema):
    """Pașii 1–4 din antet. Întoarce {pas: număr} — ce s-a schimbat (0 la a doua rulare)."""
    from decimal import Decimal
    n = {"amortizare": 0, "reevaluare": 0, "casare": 0, "reactivate": 0, "iesiri_in_asteptare": 0, "intrari_in_asteptare": 0,
         "scoase": 0}
    s = '"%s".' % schema
    with conn.cursor() as cur:
        mfs = _mfs(cur, schema)
        # 1. amortizarea lunii, pe activ
        cur.execute("SELECT i.id, i.data, l.id, l.cont_credit, l.suma FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE NOT EXISTS (SELECT 1 FROM %smf_linii ml WHERE ml.linie_id = l.id) AND l.cont_debit LIKE '68%%' "
                    "AND l.cont_credit LIKE '28%%' ORDER BY i.id, l.id" % (s, s, s))
        folosite = {}
        for nid, data, lid, cont, suma in cur.fetchall():
            luat = folosite.setdefault(nid, set())
            cand = [m for m in mfs if m["cont_amortizare"] == cont and m["data_pif"] and m["dnf_luni"] and m["id"] not in luat
                    and _rata(m, data.year, data.month) == Decimal(str(suma))]
            if cand:
                luat.add(cand[0]["id"])
                cur.execute("INSERT INTO %smf_linii (linie_id, mijloc_fix_id) VALUES (%%s, %%s)" % s, (lid, cand[0]["id"]))
                n["amortizare"] += 1
        # 2. reevaluările: rândurile pe conturile activului
        cur.execute("INSERT INTO %smf_linii (linie_id, mijloc_fix_id) SELECT DISTINCT ON (l.id) l.id, r.mijloc_fix_id "
                    "FROM %sinregistrari_linii l JOIN %sreevaluari r ON r.inregistrare_id = l.inregistrare_id "
                    "JOIN %smijloace_fixe m ON m.id = r.mijloc_fix_id "
                    "WHERE (l.cont_debit IN (m.cont_imobilizare, m.cont_amortizare) OR l.cont_credit IN (m.cont_imobilizare, m.cont_amortizare)) "
                    "ORDER BY l.id, r.id ON CONFLICT (linie_id) DO NOTHING" % (s, s, s, s))
        n["reevaluare"] = cur.rowcount
        # 3. casările: „Casare <denumire> (PV comisie…”, rândurile pe conturile activului
        pe_nume = {}
        for m in mfs:
            pe_nume.setdefault(m["denumire"], []).append(m)
        cur.execute("SELECT id, descriere, status FROM %sinregistrari WHERE sursa = 'operatiuni' AND descriere LIKE 'Casare %%' ORDER BY id" % s)
        casari = {}
        for nid, descr, status in cur.fetchall():
            den = descr[len("Casare "):].split(" (PV comisie")[0]
            for m in pe_nume.get(den, []):
                cur.execute("INSERT INTO %smf_linii (linie_id, mijloc_fix_id) SELECT l.id, %%s FROM %sinregistrari_linii l "
                            "WHERE l.inregistrare_id = %%s AND (l.cont_credit IN (%%s, %%s) OR l.cont_debit IN (%%s, %%s)) "
                            "ON CONFLICT (linie_id) DO NOTHING" % (s, s),
                            (m["id"], nid, m["cont_imobilizare"], m["cont_amortizare"], m["cont_imobilizare"], m["cont_amortizare"]))
                n["casare"] += cur.rowcount
                casari.setdefault(m["id"], []).append((nid, status))
        # 4. starea activelor scoase: scoase de o notă VALIDATĂ (credit pe contul activului cu toată valoarea lui) sau nu
        for m in [x for x in mfs if not x["activ"]]:
            cur.execute("SELECT 1 FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id WHERE i.status = 'validata' "
                        "AND l.cont_credit = %%s GROUP BY i.id HAVING SUM(l.suma) >= %%s LIMIT 1" % (s, s), (m["cont_imobilizare"], m["valoare"]))
            if cur.fetchone():
                continue
            ciorna = next((nid for nid, st in casari.get(m["id"], []) if st != "validata"), None)
            if ciorna:
                cur.execute("INSERT INTO %smf_note (inregistrare_id, mijloc_fix_id, fel) VALUES (%%s, %%s, 'iesire') ON CONFLICT DO NOTHING" % s,
                            (ciorna, m["id"]))
                n["iesiri_in_asteptare"] += cur.rowcount
            cur.execute("UPDATE %smijloace_fixe SET activ = true WHERE id = %%s" % s, (m["id"],))
            n["reactivate"] += 1
        # 5. activele aduse de o operațiune (codurile aplicației): nota lor de intrare
        cur.execute("SELECT inregistrare_id FROM %smf_note" % s)
        legate = {r[0] for r in cur.fetchall()}
        for m in [x for x in mfs if str(x["cod"] or "").startswith(("MF-PLUS", "NEC-"))]:
            contra = "4754" if str(m["cod"]).startswith("MF-PLUS") else "404"
            cur.execute("SELECT 1 FROM %smf_note WHERE mijloc_fix_id = %%s AND fel = 'intrare'" % s, (m["id"],))
            if cur.fetchone():
                continue
            cur.execute("SELECT i.id, i.status FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                        "WHERE l.cont_debit = %%s AND l.cont_credit = %%s AND l.suma = %%s ORDER BY i.id" % (s, s),
                        (m["cont_imobilizare"], contra, m["valoare"]))
            note = [(nid, st) for nid, st in cur.fetchall() if nid not in legate]
            if note:
                nid, st = note[0]
                legate.add(nid)
                cur.execute("INSERT INTO %smf_note (inregistrare_id, mijloc_fix_id, fel) VALUES (%%s, %%s, 'intrare')" % s, (nid, m["id"]))
                cur.execute("INSERT INTO %smf_linii (linie_id, mijloc_fix_id) SELECT l.id, %%s FROM %sinregistrari_linii l "
                            "WHERE l.inregistrare_id = %%s AND l.cont_debit = %%s ON CONFLICT (linie_id) DO NOTHING" % (s, s),
                            (m["id"], nid, m["cont_imobilizare"]))
                if st != "validata":
                    cur.execute("UPDATE %smijloace_fixe SET activ = false WHERE id = %%s" % s, (m["id"],))
                    n["intrari_in_asteptare"] += 1
                continue
            cur.execute("SELECT (SELECT count(*) FROM %smf_linii WHERE mijloc_fix_id = %%s) + "
                        "(SELECT count(*) FROM %sreevaluari WHERE mijloc_fix_id = %%s)" % (s, s), (m["id"], m["id"]))
            if cur.fetchone()[0] == 0:   # nota lui a fost ștearsă și nimic nu-l mai citește: activul n-a intrat niciodată în evidență
                cur.execute("DELETE FROM %smijloace_fixe WHERE id = %%s" % s, (m["id"],))
                n["scoase"] += 1
    return n


def aplica(conn, schema):
    aplica_ddl(conn, schema)
    return backfill(conn, schema)


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL AND EXISTS (SELECT 1 FROM pg_trigger t "
                    "JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_namespace ns ON ns.oid = c.relnamespace WHERE ns.nspname = %s "
                    "AND t.tgname = 'trg_mf_nota_status')", ('"%s".mf_note' % schema, '"%s".mf_linii' % schema, schema))
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
    print("migrare_mf_note: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        sys.exit(1)


if __name__ == "__main__":
    _main()
