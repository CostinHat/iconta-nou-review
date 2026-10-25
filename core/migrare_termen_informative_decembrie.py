"""
core/migrare_termen_informative_decembrie.py — termenul declarațiilor informative de 25 decembrie, în coadă (lotul 12, deficiența 639).

DEFECTUL. `scadente.termen_legal` aplica excepția CPF art.155 alin.(2) („Creanțele fiscale […] pentru care […] scadența și/sau termenul de
declarare se împlinesc la 25 decembrie, sunt scadente și/sau se declară până la data de 21 decembrie”) oricărui tip, deci și declarațiilor
informative (D390, D208 …), care nu declară o creanță: D390 pentru 11/2026 avea termen 21.12.2026 în loc de 28.12.2026 (CPF art.75 ->
Legea 134/2010 art.181 alin.(2), mutare DUPĂ). Acum excepția se aplică numai creanțelor (`scadente.declara_creanta`).

DATELE EXISTENTE. Coada își scrie termenul în `public.declaratii_coada.perioada` la intrare (`coada_api`), iar cheia elementului activ e
(firmă, tip, `perioada`) — indexul `ux_coada_activa`. Un element vechi al unui tip informativ, intrat cu termenul mutat înapoi, primește
termenul calculat de aceeași funcție ca la intrarea în coadă (`scadente.scadenta`), pe perioada declarată din payload (`_an`, `_luna`,
`_trim`). Se atinge NUMAI rândul al cărui termen e exact cel vechi (excepția aplicată greșit) — orice altă valoare rămâne. Un rând care ar
ciocni un element ACTIV deja existent pe același (firmă, tip, termen) se sare și se numește. Nimic altceva (payload, stare, XML). Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_termen_informative_decembrie.py`.
"""

from core import db

_RE_DATA = r"^[0-9]{2}\.[0-9]{2}\.[0-9]{4}$"
_STARI_INCHISE = ("respinsa", "depusa")   # ca indexul parțial ux_coada_activa (infra/bootstrap_public.sql)


def tipuri():
    from core import scadente
    return sorted(scadente.TEMEI_FARA_CREANTA)


def _termene(tip, an, luna, trim):
    """(termenul vechi — excepția aplicată —, termenul corect), ca „zz.ll.aaaa”; None dacă tipul n-are termen pe perioada asta."""
    from core import scadente
    from core.pdf_util import data_ro
    if not scadente.are_termen(tip, an, luna=luna, trim=trim):
        return None
    nominala = scadente._data_nominala(tip, an, luna=luna, trim=trim)
    return data_ro(scadente.termen_legal(nominala, creanta=True)), scadente.scadenta(tip, an, luna=luna, trim=trim)


def _de_corectat(cur):
    """[(id, tenant_id, tip, perioada, stare, termen_corect)] — rândurile cu termenul vechi, diferit de cel corect."""
    cur.execute("SELECT id, tenant_id, tip, perioada, stare, (payload->>'_an')::int, (payload->>'_luna')::int, (payload->>'_trim')::int "
                "FROM public.declaratii_coada WHERE tip = ANY(%s) AND perioada ~ %s AND payload ? '_an' ORDER BY id", (tipuri(), _RE_DATA))
    out = []
    for cid, tenant_id, tip, perioada, stare, an, luna, trim in cur.fetchall():
        t = _termene(tip, an, luna, trim) if an else None
        if t and t[0] != t[1] and perioada == t[0]:
            out.append((cid, tenant_id, tip, perioada, stare, t[1]))
    return out


def aplica(conn):
    """{"actualizate": n, "sarite": [(id, tip, perioada, motiv)]}."""
    rez = {"actualizate": 0, "sarite": []}
    with conn.cursor() as cur:
        for cid, tenant_id, tip, perioada, stare, termen in _de_corectat(cur):
            if stare not in _STARI_INCHISE:
                cur.execute("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND tip = %s AND perioada = %s "
                            "AND NOT (stare = ANY(%s)) AND id <> %s", (tenant_id, tip, termen, list(_STARI_INCHISE), cid))
                alt = cur.fetchone()
                if alt:
                    rez["sarite"].append((cid, tip, perioada, "elementul activ %s are deja termenul %s" % (alt[0], termen)))
                    continue
            cur.execute("UPDATE public.declaratii_coada SET perioada = %s WHERE id = %s", (termen, cid))
            rez["actualizate"] += 1
    return rez


def verifica(conn):
    """Câte rânduri au încă termenul vechi (în afara celor sărite, care se numesc)."""
    with conn.cursor() as cur:
        return len(_de_corectat(cur))


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        rez = aplica(conn)
    with db.get_conn() as conn:
        ramase = verifica(conn)
    print("Termenul declarațiilor informative de 25 decembrie în coadă: %d rânduri actualizate; %d rămase cu termenul vechi."
          % (rez["actualizate"], ramase))
    for cid, tip, perioada, motiv in rez["sarite"]:
        print("  sărit: elementul %s (%s, %s): %s" % (cid, tip.upper(), perioada, motiv))
    return ramase == len(rez["sarite"])


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
