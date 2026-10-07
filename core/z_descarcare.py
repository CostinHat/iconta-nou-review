# -*- coding: utf-8 -*-
"""core/z_descarcare.py — raportul Z la firma cu stocul CANTITATIV-VALORIC (lotul „Deciziile 07.10”, D3).

Decizia Costin (07.10.2026, pct.3), verbatim: „Raportul Z la cantitativ-valoric: fără refuz. Descărcarea pe articol se cere
explicit (manual sau prin rețetă); Z-ul nu se validează fără ea.”

  · Z-ul se înregistrează (fără refuz), dar la cantitativ-valoric ca CIORNĂ: validarea trece pe unicul drum
    (`jurnal_api.valideaza` — jurnalul și coada), unde stă poarta de mai jos.
  · Descărcarea = ieșiri pe articol LEGATE de Z (`miscari_stoc.z_inregistrare_id`): manual (`stocuri_cv_api.iesire`) sau prin
    rețetă (`retete_api.descarca`), cu `z_id`. Z-ul n-are articole (casa de marcat nu le dă), deci ce s-a vândut din stoc
    spune omul — aplicația nu ghicește.
  · Z-ul în care nu s-a vândut marfă din stoc (numai servicii) se declară EXPLICIT „fără marfă” (`rapoarte_z_amef.fara_marfa`);
    nimic nu e presupus.
Temei: OMFP 1802/2014 pct.287 alin.(1)-(2) — „Metoda aleasă trebuie aplicată cu consecvență” (la cantitativ-valoric ieșirile se
evaluează pe articol, la CMP — `stocuri_cv`); la global-valoric Z-ul rămâne pe descărcarea lunară cu K (neschimbat).
"""
from psycopg2.extras import RealDictCursor

MESAJ_NEDESCARCAT = ("Raportul Z (nota #%s) nu se validează fără descărcarea mărfii vândute: la stocul cantitativ-valoric ieșirea "
                     "se face pe articol. Pe ecranul Raport Z, la acest raport: „Ieșire pe articol” sau „Consum pe rețetă” — ori, "
                     "dacă n-a vândut marfă din stoc, „Fără marfă din stoc”.")
COD_NEDESCARCAT = "Z_NEDESCARCAT"


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def e_z(cur, schema, nota_id):
    cur.execute("SELECT 1 FROM %srapoarte_z_amef WHERE inregistrare_id = %%s" % _p(schema), (int(nota_id),))
    return cur.fetchone() is not None


def stare(cur, schema, nota_id):
    """{"iesiri": n (ieșiri VII legate de Z), "fara_marfa": True/False/None}."""
    p = _p(schema)
    cur.execute(f"""SELECT (SELECT count(*) FROM {p}miscari_stoc m WHERE m.z_inregistrare_id = z.inregistrare_id
                              AND m.anuleaza_id IS NULL AND NOT EXISTS (SELECT 1 FROM {p}miscari_stoc r WHERE r.anuleaza_id = m.id)),
                           z.fara_marfa
                    FROM {p}rapoarte_z_amef z WHERE z.inregistrare_id = %s""", (int(nota_id),))
    r = cur.fetchone()
    if not r:
        return None
    r = tuple(r.values()) if isinstance(r, dict) else r
    return {"iesiri": int(r[0]), "fara_marfa": r[1]}


def refuz_validare(cur, schema, nota_id):
    """Mesajul refuzului (sau None): nota e un raport Z, firma e cantitativ-valorică, iar Z-ul n-are nici ieșiri legate, nici
    declarația „fără marfă”. Apelat din `jurnal_api.valideaza` — unicul drum de validare."""
    from core import metoda_stoc as _ms
    st = stare(cur, schema, nota_id)
    if st is None or st["iesiri"] > 0 or st["fara_marfa"] is True:
        return None
    if _ms.citeste(cur, schema) != _ms.CV:
        return None
    return MESAJ_NEDESCARCAT % nota_id


def cere_z(cur, schema, z_id):
    """Z-ul de care se leagă o ieșire: există, e raport Z, e încă ciornă (un Z validat nu mai primește descărcări). Întoarce
    id-ul sau ridică ValueError cu motivul."""
    try:
        zid = int(z_id)
    except (TypeError, ValueError):
        raise ValueError("Raportul Z ales nu e valid.")
    cur.execute("SELECT status FROM %sinregistrari WHERE id = %%s" % _p(schema), (zid,))
    r = cur.fetchone()
    st = (r["status"] if isinstance(r, dict) else r[0]) if r else None
    if st is None or not e_z(cur, schema, zid):
        raise ValueError("Raportul Z ales nu există.")
    if st != "ciorna":
        raise ValueError("Raportul Z #%s e deja validat: descărcarea se leagă numai de un Z nevalidat." % zid)
    return zid


def marcheaza_fara_marfa(conn, schema, nota_id, fara_marfa):
    """Declarația explicită: în Z nu s-a vândut marfă din stoc (True) / retrasă (None). Numai pe un Z nevalidat."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        zid = cere_z(cur, schema, nota_id)
        st = stare(cur, schema, zid)
        if fara_marfa and st["iesiri"]:
            raise ValueError("Raportul Z are deja %d ieșiri din stoc legate de el — nu poate fi „fără marfă”." % st["iesiri"])
        cur.execute("UPDATE %srapoarte_z_amef SET fara_marfa = %%s WHERE inregistrare_id = %%s" % _p(schema),
                    (True if fara_marfa else None, zid))
    return {"ok": True, "nota_id": zid, "fara_marfa": True if fara_marfa else None}


def lista_luna(conn, schema, an, luna):
    """Rapoartele Z ale lunii, cu starea descărcării (pentru ecranul Raport Z)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT i.id, i.data, i.numar, i.status, z.nui, z.nr_bonuri, z.fara_marfa,
                               (SELECT COALESCE(SUM(l.suma), 0) FROM {_p(schema)}inregistrari_linii l
                                 WHERE l.inregistrare_id = i.id AND l.cont_credit = '707' AND l.cont_debit <> '707') AS incasat
                        FROM {_p(schema)}inregistrari i JOIN {_p(schema)}rapoarte_z_amef z ON z.inregistrare_id = i.id
                        WHERE date_trunc('month', i.data) = %s ORDER BY i.data, i.id""", ("%d-%02d-01" % (int(an), int(luna)),))
        out = []
        for r in cur.fetchall():
            st = stare(cur, schema, r["id"])
            out.append({"id": r["id"], "data": r["data"].isoformat(), "numar": r["numar"], "status": r["status"], "nui": r["nui"],
                        "nr_bonuri": r["nr_bonuri"], "incasat": str(r["incasat"]), "iesiri": st["iesiri"],
                        "fara_marfa": st["fara_marfa"]})
    return out
