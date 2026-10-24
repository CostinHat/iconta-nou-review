# -*- coding: utf-8 -*-
"""core/migrare_note_luna_neincheiata.py — ciornele de salarii / amortizare scrise înainte ca luna lor să se încheie (lotul 12, C127).

DEFECTUL (C127, găsit la 216). Reparația 216 (10.10.2026, `uc_comun._cere_luna_incheiata`) oprește numai notele NOI ale unei luni
neîncheiate; notele scrise înainte au rămas. Pe F5: ciorna „Salariile lunii 10/2026” (scrisă pe 08.10.2026) și nota VALIDATĂ „Stat de
plata 11/2026” (scrisă pe 06.10.2026).

CE FACE, pe notele de salarii și de amortizare scrise înainte de încheierea lunii lor (`inchidere_luna.note_contate_inainte`, aceeași
regulă ca semnalul de pe ecran):
  * CIORNA se scoate (`note_derivate.sterge_ciorna_inlocuita`: liniile cad cu ea, elementul ei din coadă la fel). Nu era evidență: o
    ciornă nevalidată e o propunere, iar propunerea făcută pe o lună neîncheiată poate să nu cuprindă tot. După ce luna se încheie, nota
    se scrie din nou din statul de plată / registrul mijloacelor fixe, cu cifrele întregi.
  * Nota VALIDATĂ NU se atinge: e evidență (o notă validată nu se șterge și nu se modifică — se corectează printr-o notă de corecție).
    Ecranul o semnalează cu mesajul lui `note_contate_inainte`, iar migrarea o numește la rulare.
  * Luna blocată se respectă: regula de fond a bazei refuză ștergerea, iar ciorna rămâne și se numește.
Fiecare ciornă scoasă lasă urma în `public.audit_log` (data, descrierea, documentul, liniile), ca să se poată reface.
Idempotentă. Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_note_luna_neincheiata.py`.
"""
import json

from core import db

MOTIV = "lotul 12, C127 — ciornă de salarii / amortizare scrisă înainte de încheierea lunii ei (216)"


def aplica(conn, schema):
    """-> {"scoase": [id], "validate": [(id, luna)], "ramase": [(id, motiv)]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import inchidere_luna as _il, note_derivate as _nd
    rez = {"scoase": [], "validate": [], "ramase": []}
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".inregistrari' % schema,))
        if cur.fetchone()[0] is None:
            return rez
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        r = cur.fetchone()
        tenant_id = r[0] if r else None
        for iid, info in sorted(_il.note_contate_inainte(cur, schema).items()):
            if info["status"] != "ciorna":
                rez["validate"].append((iid, info["luna_an"]))
                continue
            cur.execute('SELECT data::text, descriere, document_ref, sursa FROM "%s".inregistrari WHERE id = %%s' % schema, (iid,))
            data, desc, dref, sursa = cur.fetchone()
            cur.execute('SELECT cont_debit, cont_credit, suma::text FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s ORDER BY id'
                        % schema, (iid,))
            linii = [list(x) for x in cur.fetchall()]
            cur.execute("SAVEPOINT nota_luna_neincheiata")
            try:
                if not _nd.sterge_ciorna_inlocuita(cur, schema, iid):
                    raise RuntimeError("ciorna nu s-a scos")
                cur.execute("INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, entitate_id, detalii) "
                            "VALUES (NULL, %s, 'stergere_ciorna_luna_neincheiata', 'inregistrare', %s, %s)",
                            (tenant_id, iid, json.dumps({"motiv": MOTIV, "sursa": "core/migrare_note_luna_neincheiata.py", "schema": schema,
                                                         "data": data, "descriere": desc, "document_ref": dref, "sursa_notei": sursa,
                                                         "scrisa_la": info["scrisa_la"], "linii": linii}, ensure_ascii=False)))
            except Exception as e:  # noqa: BLE001 — refuzul unei reguli de fond (luna blocată), numit
                cur.execute("ROLLBACK TO SAVEPOINT nota_luna_neincheiata")
                rez["ramase"].append((iid, str(e).strip().split("\n")[0]))
                continue
            cur.execute("RELEASE SAVEPOINT nota_luna_neincheiata")
            rez["scoase"].append(iid)
    return rez


def verifica(conn, schema):
    """Nu mai rămâne nicio ciornă scrisă înainte de încheierea lunii ei (una dintr-o lună blocată rămâne, și verificarea o arată)."""
    from core import inchidere_luna as _il
    with conn.cursor() as cur:
        return not [i for i, x in _il.note_contate_inainte(cur, schema).items() if x["status"] == "ciorna"]


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
            n += len(r["scoase"])
            if r["scoase"]:
                print("  %s: ciornele %s scoase (scrise înainte de încheierea lunii lor)" % (s, r["scoase"]))
            for iid, luna in r["validate"]:
                print("  %s: nota VALIDATĂ #%s (luna %s) a fost scrisă înainte de încheierea lunii — nu se atinge; ecranul o semnalează" % (s, iid, luna))
            for iid, motiv in r["ramase"]:
                print("  %s: ciorna #%s rămâne — %s" % (s, iid, motiv))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_note_luna_neincheiata: %d ok, %d esec, %d ciorne scoase" % (ok, len(esec), n))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
