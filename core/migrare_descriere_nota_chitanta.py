# -*- coding: utf-8 -*-
"""core/migrare_descriere_nota_chitanta.py — notele chitanțelor scrise înainte de reparație fără chitanță în descriere (lotul 12, deficiența
168; regula Costin 11.2 pct.3a, verbatim: „Orice reparație acoperă și datele existente.”).

168 (retest 08.10 pct.19, verbatim): „Nota chitanței (F1, nr. crt. 17): descrierea e doar numele clientului; trebuie să conțină chitanța și
factura stinsă.” Lotul 08.10 a reparat „Emite chitanță”; drumul adăugat în lotul 11 (456: încasarea facturii din Casă emite singură chitanța,
`uc_tenants.chitante_pe_incasare`) scria nota ÎNAINTE de chitanță, deci descrierea ei spunea „Încasare de la client — factura … — Client”,
fără chitanță. De acum nota o numește (`casa_api.nota_numeste_chitanta`, aceeași funcție pe ambele drumuri).

CE RESCRIE: descrierea CIORNEI notei unei chitanțe nenulate, pe încasarea de la client (factura stinsă sau avansul), numai când e textul
scris de APLICAȚIE (numele partenerului — forma de dinainte de 08.10 —, eticheta categoriei sau o descriere `casa_api.descriere_nota`, care
începe cu „Încasare de la client”); forma nouă din aceeași funcție ca la scriere (`casa_api.nota_numeste_chitanta`).
CE NU RESCRIE (și raportează):
  · NOTELE VALIDATE: nota validată nu se modifică (OMFP 1802/2014 pct.69; triggerul `regula_nota`). Decizia Costin 09.10.2026 („Nota 118
    rămâne neschimbată”, verbatim în DECIZII) — Registrul jurnal le arată chitanța ca document și factura stinsă, derivat
    (`jurnal_api.facturi_stinse`);
  · ciornele din LUNA ÎNCHISĂ (`contare_facturi.luna_blocata`; triggerul perioadei blocate le-ar refuza);
  · textul scris de om pe ciornă (alt text decât cel al aplicației) — CLAUDE.md §8: datele contabilului nu se ating.
Idempotentă (a doua rulare nu mai găsește nimic: descrierea nouă e chiar forma calculată). Fiecare firmă se comite separat și se raportează.
Pe uscat (numai citire): `python -m core.migrare_descriere_nota_chitanta --uscat`.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_descriere_nota_chitanta.py`.
"""
import sys

from core import db
from core.common import cate as _cate


def _s(schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    return '"%s"' % schema


def _scrisa_de_aplicatie(text, partener):
    """Descrierea e a aplicației: numele partenerului (forma de dinainte de 08.10), eticheta categoriei sau `descriere_nota`."""
    from core import casa_api as _c
    t = (text or "").strip()
    eticheta = _c.ETICHETE_CATEGORIE["incasare_client"]
    return not t or t == (partener or "").strip() or t == eticheta or t.startswith(eticheta + " — ")


def plan(cur, schema):
    """Ce ar face migrarea, FĂRĂ să scrie: {"ciorne": [(op, nota, vechi, nou, chitanța)], "validate": [(nota, vechi, nou)],
    "lasate": [(nota, vechi, motiv)]}."""
    from core import casa_api as _c, contare_facturi as _cf
    s = _s(schema)
    gol = {"ciorne": [], "validate": [], "lasate": []}
    cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL", ("%s.chitante" % s, "%s.casa_operatiuni" % s))
    if not cur.fetchone()[0]:
        return gol
    cur.execute(f"""SELECT ch.casa_operatiune_id, ch.serie, ch.numar, o.partener FROM {s}.chitante ch
                      JOIN {s}.casa_operatiuni o ON o.id = ch.casa_operatiune_id
                     WHERE NOT ch.anulata AND ch.inregistrare_id IS NOT NULL ORDER BY ch.id""")
    for op_id, serie, numar, partener in cur.fetchall():
        r = _c.nota_numeste_chitanta(cur, s, op_id, "%s-%s" % (serie, numar), scrie=False)
        if not r or r[2] == r[3]:
            continue
        nid, status, vechi, nou, data_n = r
        if status == "validata":
            gol["validate"].append((nid, vechi, nou))
        elif status != "ciorna":
            gol["lasate"].append((nid, vechi, "nota are starea %r, nu e ciornă" % status))
        elif not _scrisa_de_aplicatie(vechi, partener):
            gol["lasate"].append((nid, vechi, "descrierea e scrisă de om"))
        elif _cf.luna_blocata(cur, schema, data_n):
            gol["lasate"].append((nid, vechi, "luna %02d/%d e închisă" % (data_n.month, data_n.year)))
        else:
            gol["ciorne"].append((op_id, nid, vechi, nou, "%s-%s" % (serie, numar)))
    return gol


def aplica(conn, schema):
    """Scrie planul în tranzacția `conn` (fără commit): numai ciorne (`status = 'ciorna'` în condiția UPDATE-ului) și numai peste textul
    văzut la plan; descrierea nouă e cea calculată de `casa_api.nota_numeste_chitanta` (aceeași formulă ca la scriere). Întoarce planul."""
    s = _s(schema)
    with conn.cursor() as cur:
        p = plan(cur, schema)
        for _op, nid, vechi, nou, _ch in p["ciorne"]:
            cur.execute(f"UPDATE {s}.inregistrari SET descriere = %s WHERE id = %s AND status = 'ciorna' AND descriere IS NOT DISTINCT FROM %s",
                        (nou, nid, vechi))
    return p


def verifica(conn, schema):
    """După rulare: nicio ciornă rescriptibilă rămasă."""
    with conn.cursor() as cur:
        return not plan(cur, schema)["ciorne"]


def text_raport(schema, r):
    lin = ["%s: %s, %s, %s" % (schema, _cate(len(r["ciorne"]), "ciornă rescrisă", "ciorne rescrise"),
                               _cate(len(r["validate"]), "notă validată lăsată", "note validate lăsate"),
                               _cate(len(r["lasate"]), "ciornă lăsată", "ciorne lăsate"))]
    lin += ["  ciornă %s: «%s» -> «%s»" % (n, v, x) for _o, n, v, x, _ch in r["ciorne"]]
    lin += ["  validată %s, lăsată (decizia 09.10): «%s»" % (n, v) for n, v, _x in r["validate"]]
    lin += ["  ciornă %s lăsată: «%s» — %s" % (n, v, m) for n, v, m in r["lasate"]]
    return "\n".join(lin)


def _main(uscat=False):
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                if uscat:
                    with conn.cursor() as cur:
                        r = plan(cur, s)
                    conn.rollback()
                else:
                    r = aplica(conn, s)
                    conn.commit()
            ok += 1
            if any(r.values()):
                print(text_raport(s, r))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_descriere_nota_chitanta%s: %d ok, %d esec" % (" (pe uscat, nimic scris)" if uscat else "", ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main(uscat="--uscat" in sys.argv[1:])
