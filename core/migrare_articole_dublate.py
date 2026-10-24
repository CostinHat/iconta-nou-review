# -*- coding: utf-8 -*-
"""core/migrare_articole_dublate.py — articolele de stoc dublate de drumurile care creau tacit un al doilea articol (lotul 12, 475).

DEFECTUL (deficiența 475, „Stocuri: Același articol «grau» de două ori în stoc”). Până la lotul 11 (450) borderoul de achiziție și intrarea
manuală creau un articol nou ori de câte ori primeau numai denumirea, iar până la lotul 12 două linii cu aceeași marfă pe aceeași factură
primită sau pe același NIR creau două articole (`stocuri_cv_api.articol_pentru_intrare` le închide acum pe toate). Articolele create așa
au rămas în nomenclator: pe F1, „grau” nr. 5 (200 kg, BA-2) și „grau” nr. 6 (10 kg, BA-3) — situația stocului arăta marfa de două ori,
fiecare cu fișa ei.

CE FACE (datele existente — „Orice reparație acoperă și datele existente”, comanda Costin 11.2 pct.3). Grupează articolele după cheia
nomenclatorului (`produse_api.cheie_denumire`, aceeași cu care aplicația decide acum că două denumiri sunt același articol). Într-un grup
păstrează articolul cel mai vechi și îi trece mișcările, liniile de NIR, de factură și de rețetă ale celorlalte, apoi le șterge — NUMAI
dacă unirea nu schimbă nicio sumă scrisă și nu amestecă două lucruri diferite:
  * aceeași unitate de măsură, același cont de stoc și același cont de cheltuială (altfel ar fi două lucruri, sau o fișă în două unități);
  * nicio ieșire pe niciun articol al grupului (o ieșire are valoarea calculată la CMP-ul articolului ei; unite, fișa ar arăta alt CMP
    decât cel din nota deja scrisă). Intrările se mută cu prețul și valoarea lor, deci nota și fișa rămân aceleași, la ban;
  * cel mult un cod de bare în grup (codul de bare identifică un singur articol).
Un grup care nu îndeplinește condițiile NU se atinge: se numește la rulare, cu motivul — unirea lui e a contabilului.
Fiecare unire lasă urma în `public.audit_log` (articolul păstrat, cele unite, mișcările mutate), ca să se poată reface invers.
Notele contabile, declarațiile și sumele nu se ating. Idempotentă (după rulare nu mai rămâne niciun grup unibil).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_articole_dublate.py`.
"""
import json

from core import db

MOTIV = "lotul 12, deficiența 475 — articol de stoc dublat de crearea tacită, unit în cel mai vechi cu aceeași denumire"
# Tabelele care țin `articol_id`: mișcările (fișa de magazie), liniile de NIR, de factură și de rețetă.
REFERINTE = ("miscari_stoc", "nir_linii", "factura_linii", "retete_linii")


def _nrm(x):
    return " ".join(str(x or "").split()).lower()


def grupuri(cur, schema):
    """[[{id, denumire, um, cont_stoc, cont_cheltuiala, barcode, iesiri}]] — articolele cu aceeași cheie de denumire, câte două sau mai
    multe, fiecare grup în ordinea id-ului (primul = cel păstrat)."""
    from core import produse_api as _pa
    cur.execute('SELECT a.id, a.denumire, a.um, a.cont_stoc, a.cont_cheltuiala, a.barcode, a.nivel_minim, '
                '(SELECT count(*) FROM "%s".miscari_stoc m WHERE m.articol_id = a.id AND m.tip <> \'intrare\') AS iesiri '
                'FROM "%s".articole a ORDER BY a.id' % (schema, schema))
    pe_cheie = {}
    for r in cur.fetchall():
        a = dict(zip(("id", "denumire", "um", "cont_stoc", "cont_cheltuiala", "barcode", "nivel_minim", "iesiri"), r))
        k = _pa.cheie_denumire(a["denumire"])
        if k:
            pe_cheie.setdefault(k, []).append(a)
    return [g for g in pe_cheie.values() if len(g) > 1]


def motiv_neunibil(grup):
    """PURĂ. De ce grupul NU se unește automat (text pentru contabil), sau None dacă unirea nu schimbă nicio sumă."""
    p = grup[0]
    for a in grup[1:]:
        if _nrm(a["um"]) != _nrm(p["um"]):
            return "unități de măsură diferite (%s / %s)" % (p["um"], a["um"])
        if _nrm(a["cont_stoc"]) != _nrm(p["cont_stoc"]) or _nrm(a["cont_cheltuiala"]) != _nrm(p["cont_cheltuiala"]):
            return "conturi diferite (%s/%s față de %s/%s)" % (p["cont_stoc"], p["cont_cheltuiala"], a["cont_stoc"], a["cont_cheltuiala"])
    if any(a["iesiri"] for a in grup):
        return "are ieșiri din stoc, evaluate la costul mediu al fiecărui articol — unite, fișa ar arăta alt cost decât nota scrisă"
    if len({a["barcode"] for a in grup if a["barcode"]}) > 1:
        return "articolele au coduri de bare diferite"
    return None


def aplica(conn, schema):
    """Unește grupurile unibile. -> {"unite": [(păstrat, [unite], mișcări mutate)], "neunite": [(denumire, [id-uri], motiv)]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    rez = {"unite": [], "neunite": []}
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".articole' % schema,))
        if cur.fetchone()[0] is None:
            return rez
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        r = cur.fetchone()
        tenant_id = r[0] if r else None
        for g in grupuri(cur, schema):
            motiv = motiv_neunibil(g)
            if motiv:
                rez["neunite"].append((g[0]["denumire"], [a["id"] for a in g], motiv))
                continue
            pastrat, unite = g[0], [a["id"] for a in g[1:]]
            mutate = {}
            # Regulile de fond ale bazei rămân în picioare (mișcarea unui document contat nu se modifică; luna blocată nu se atinge):
            # dacă una refuză unirea, grupul se lasă cum e și se numește, cu refuzul ei.
            cur.execute("SAVEPOINT unire_articole")
            try:
                _uneste(cur, schema, tenant_id, g, mutate)
            except Exception as e:  # noqa: BLE001 — refuzul unei reguli de fond a bazei, numit mai jos
                cur.execute("ROLLBACK TO SAVEPOINT unire_articole")
                rez["neunite"].append((pastrat["denumire"], [a["id"] for a in g], "baza a refuzat unirea: %s" % str(e).strip().split("\n")[0]))
                continue
            cur.execute("RELEASE SAVEPOINT unire_articole")
            rez["unite"].append((pastrat["id"], unite, sum(len(v) for v in mutate.values())))
    return rez


def _uneste(cur, schema, tenant_id, g, mutate):
    """Mută referințele articolelor `g[1:]` pe `g[0]`, le șterge și lasă urma în `public.audit_log`."""
    pastrat, unite = g[0], [a["id"] for a in g[1:]]
    for tabel in REFERINTE:
        cur.execute("SELECT to_regclass(%s)", ('"%s".%s' % (schema, tabel),))
        if cur.fetchone()[0] is None:
            continue
        cur.execute('UPDATE "%s".%s SET articol_id = %%s WHERE articol_id = ANY(%%s) RETURNING id' % (schema, tabel),
                    (pastrat["id"], unite))
        mutate[tabel] = [x[0] for x in cur.fetchall()]
    cod = next((a["barcode"] for a in g if a["barcode"]), None)
    nivel = next((a["nivel_minim"] for a in g if a["nivel_minim"] is not None), None)
    cur.execute('DELETE FROM "%s".articole WHERE id = ANY(%%s)' % schema, (unite,))
    cur.execute('UPDATE "%s".articole SET barcode = COALESCE(barcode, %%s), nivel_minim = COALESCE(nivel_minim, %%s) '
                'WHERE id = %%s' % schema, (cod, nivel, pastrat["id"]))
    cur.execute("INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, entitate_id, detalii) "
                "VALUES (NULL, %s, 'unire_articole', 'articol', %s, %s)",
                (tenant_id, pastrat["id"], json.dumps({
                    "motiv": MOTIV, "sursa": "core/migrare_articole_dublate.py", "schema": schema,
                    "pastrat": {"id": pastrat["id"], "denumire": pastrat["denumire"]},
                    "unite": [{"id": a["id"], "denumire": a["denumire"], "um": a["um"], "barcode": a["barcode"],
                               "nivel_minim": None if a["nivel_minim"] is None else str(a["nivel_minim"])} for a in g[1:]],
                    "randuri_mutate": mutate}, ensure_ascii=False)))


def verifica(conn, schema):
    """Nu mai rămâne niciun grup unibil."""
    with conn.cursor() as cur:
        return not [g for g in grupuri(cur, schema) if motiv_neunibil(g) is None]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, n_unite = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            for pastrat, unite, n in r["unite"]:
                n_unite += len(unite)
                print("  %s: articolele %s unite în articolul %s (%d rânduri mutate)" % (s, unite, pastrat, n))
            for den, ids, motiv in r["neunite"]:
                print("  %s: „%s” (articolele %s) NU s-a unit — %s; unirea e a contabilului" % (s, den, ids, motiv))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_articole_dublate: %d ok, %d esec, %d articole dublate unite" % (ok, len(esec), n_unite))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
