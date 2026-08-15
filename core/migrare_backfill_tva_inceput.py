# -*- coding: utf-8 -*-
"""core/migrare_backfill_tva_inceput.py — completeaza tva_data_inceput (platitor_tva_anaf_inceput) pentru
firmele EXISTENTE din ANAF v9, cum face onboarding-ul pentru firme noi.

Motorul de control fiscal are nevoie de data inregistrarii in scopuri de TVA ca sa poata DEMONSTRA obligatia
D300/D394/D406 pe lunile trecute (regula 4: fara data -> gri "necunoscut", nu restanta). Onboarding-ul o ia
din ANAF v9 (inregistrare_scop_Tva.perioade_TVA[].data_inceput_ScpTVA), dar firmele existente inainte de
mecanism au campul NULL. Aceasta rutina reinteroghaza ANAF pe CUI si completeaza data unde ANAF o intoarce.
NU fabrica si NU deduce - doar preia de la ANAF. Ce ramane fara data (ANAF gasit=False / CUI fictiv / firma
fara istoric TVA) se cere explicit contabilului in ecranul de profil."""
from core import db, anaf_api
from core import firma_profil_api as _fp


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    completate, ramase, sarite = 0, [], 0
    for s in scheme:
        with db.get_conn(s) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT cui, platitor_tva, platitor_tva_anaf_inceput FROM firma_profil WHERE id=1")
                r = cur.fetchone()
        if not r:
            continue
        cui, platitor, data = r
        if not platitor or data is not None:
            sarite += 1
            continue
        # platitor fara data -> incearca ANAF
        try:
            rez = anaf_api.valideaza_cui([cui])
        except Exception as e:
            print("  ANAF eroare %s (%s): %s" % (s, cui, str(e)[:80])); ramase.append(s); continue
        di = rez[0].get("tva_data_inceput") if rez else None
        if di:
            with db.get_conn(s) as conn:
                _fp.seteaza_snapshot_tva(conn, True, di)
                conn.commit()
            completate += 1
            print("  OK  %s (cui %s) -> tva_data_inceput=%s" % (s, cui, di))
        else:
            ramase.append(s)
            print("  --  %s (cui %s): ANAF nu are data (gasit=%s)" % (s, cui, rez[0].get("gasit") if rez else "?"))
    print("=" * 60)
    print("backfill tva_data_inceput: %d completate din ANAF, %d raman fara data, %d sarite (neplatitor/deja au)"
          % (completate, len(ramase), sarite))
    if ramase:
        print("Raman fara data (de cerut contabilului):", ramase)


if __name__ == "__main__":
    _main()
