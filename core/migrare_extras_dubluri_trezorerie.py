"""
core/migrare_extras_dubluri_trezorerie.py — liniile de extras importate înainte de reparația deficienței 479 (lotul 12).

DEFECTUL (Costin, comanda 12.1, grav): „Bancă: Linie dublă importată; notă 5121=5121 propusă.” Două cauze, reparate în cod:
  1. aceeași mișcare venită o dată din MT940 (cu contul băncii) și o dată dintr-un extras în tabel (fără cont) nu se recunoștea ca aceeași
     (limita declarată la 277) — se adăuga a doua oară, la contat (`reconciliere_api.probabil_aceeasi_miscare`);
  2. învățarea din validare reținea „debitul primei linii”: pe o încasare (5121 = 4111) asta e chiar banca, deci linia următoare cu aceeași
     descriere primea propunerea 5121 = 5121 (`ai_incredere.cont_de_invatat`).
DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”), pe liniile NECONTATE (status `nou`):
  a. nota propusă cu același cont pe debit și pe credit (5121 = 5121) se scoate, iar „sugestie învățată: …” se scoate din motivul rândului
     — linia rămâne „Fără potrivire”, cu „Alege facturile”;
  b. linia care e probabil dublura unei linii importate înaintea ei (aceeași dată, sumă și sens; contul băncii pe exact una din ele) se pune
     deoparte, exact ca la importul de acum: status `ignorat`, motivul pe rând și «readu» — vizibilă, nu ștearsă.
Liniile CONTATE nu se ating (nota lor e în Registrul jurnal: o dublură contată o vede și o corectează contabilul) — se numesc la rulare.
Idempotentă (a doua rulare nu mai găsește nimic). Rulare: `python -m core.migrari_registru ruleaza [--productie]
core/migrare_extras_dubluri_trezorerie.py`.
"""
import json

from core import db


def _fara_sugestie(motiv):
    """PURĂ. Motivul rândului fără partea „; sugestie învățată: …” (pusă de import lângă propunerea scoasă)."""
    m = str(motiv or "")
    i = m.find("; sugestie învățată")
    if i < 0:
        i = m.find("; sugestie invatata")
    return m if i < 0 else m[:i]


def aplica(conn, schema):
    """-> {"note_scoase": n, "dubluri": n, "contate": [(id, id_vechi)]} pentru schema `schema`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import reconciliere_api as _rec
    rez = {"note_scoase": 0, "dubluri": 0, "contate": []}
    with conn.cursor() as cur:
        # [lotul 12, 479 — dovada pe F1] și liniile IGNORATE: „readu” le aduce înapoi cu nota propusă (5121=5121 ar redeveni „Contează”)
        cur.execute('SELECT id, alocari FROM "%s".extras_linii WHERE status IN (\'nou\', \'ignorat\') AND nota_propusa IS NOT NULL '
                    "AND split_part(nota_propusa->>'debit', '.', 1) = split_part(nota_propusa->>'credit', '.', 1)" % schema)
        for lid, al in cur.fetchall():
            al = dict(al or {})
            al.pop("incredere", None)
            if al.get("motiv"):
                al["motiv"] = _fara_sugestie(al["motiv"])
            cur.execute('UPDATE "%s".extras_linii SET nota_propusa = NULL, alocari = %%s WHERE id = %%s' % schema, (json.dumps(al), lid))
            rez["note_scoase"] += 1
        cur.execute('SELECT id, data, suma, tip, cont_extras, fisier_sursa, status, alocari FROM "%s".extras_linii ORDER BY id' % schema)
        randuri = [{"id": r[0], "data": r[1], "suma": r[2], "tip": r[3], "cont": r[4], "fisier_sursa": r[5], "status": r[6],
                    "alocari": r[7]} for r in cur.fetchall()]
        perechi = {}   # linia mai veche -> dublura ei (o linie veche răspunde pentru o singură dublură)
        for i, n in enumerate(randuri):
            if (n["alocari"] or {}).get("dublura_de"):
                perechi[(n["alocari"] or {})["dublura_de"]] = n["id"]
                continue
            v = next((x for x in randuri[:i] if x["id"] not in perechi and x["id"] not in perechi.values()
                      and _rec.probabil_aceeasi_miscare(n, x)), None)
            if v is None:
                continue
            perechi[v["id"]] = n["id"]
            if n["status"] == "contat":
                rez["contate"].append((n["id"], v["id"]))
                continue
            if n["status"] not in ("nou", "ignorat"):
                continue
            # [lotul 12, 479] și dublura ignorată de contabil înainte de reparație își primește motivul (pe ecran: „pare aceeași mișcare…”)
            al = {"status_match": "rosu", "alocari": [], "motiv": _rec.motiv_dublura(v), "dublura_de": v["id"]}
            cur.execute('UPDATE "%s".extras_linii SET status = \'ignorat\', nota_propusa = NULL, alocari = %%s WHERE id = %%s' % schema,
                        (json.dumps(al), n["id"]))
            rez["dubluri"] += 1
    return rez


def verifica(conn, schema):
    """Nicio linie necontată cu nota propusă pe același cont la debit și la credit."""
    with conn.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".extras_linii WHERE status IN (\'nou\', \'ignorat\') AND nota_propusa IS NOT NULL '
                    "AND split_part(nota_propusa->>'debit', '.', 1) = split_part(nota_propusa->>'credit', '.', 1)" % schema)
        return cur.fetchone()[0] == 0


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, note, dubluri = 0, [], 0, 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            note += r["note_scoase"]
            dubluri += r["dubluri"]
            for nid, vid in r["contate"]:
                print("  %s: linia de extras #%s e probabil dublura liniei #%s și e deja contată — de verificat în Registrul jurnal"
                      % (s, nid, vid))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_extras_dubluri_trezorerie: %d ok, %d esec, %d note propuse pe același cont scoase, %d linii puse deoparte ca dubluri"
          % (ok, len(esec), note, dubluri))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
