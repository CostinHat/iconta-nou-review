# -*- coding: utf-8 -*-
"""core/migrare_r81_denumiri.py — BLOC P: portofoliul se aliniază la denumirea FISCALĂ (R81).

DECIZIA lui Costin, 28.08.2026: *„Fiscala e cea deja probată pe declarații (A5/A6) — ea rămâne,
portofoliul se aliniază la ea."*

DE CE E O MIGRARE, și nu o reparație de cod. Simetria de scriere (`scrie_denumirea`) face imposibilă
**apariția** unei divergențe noi. Nu le desface pe cele existente: cele patru firme de la cabinetul
de test 4163 au azi `tenants.nume` fără forma juridică și `firma_profil.nume` cu ea, fiindcă au fost
adăugate manual prin ecran, iar profilul fiscal l-a scris un semănător din afara repo-ului. Un gard
care interzice clasa nu curăță trecutul; asta o face un act separat, scris.

CE SE PĂSTREAZĂ, ȘI DE CE. Valoarea veche din `tenants.nume` se scrie în `public.audit_log`
**înainte** de suprascriere. Fără ea, singura urmă că firma s-a numit altfel dispare odată cu
`UPDATE`-ul — iar întrebarea *„de unde vine denumirea asta"* n-ar mai avea răspuns. `user_id` rămâne
**NULL**: actul n-are utilizator interactiv, iar a-l trece pe seama cuiva ar fi o afirmație falsă.
Actorul e scris în `detalii`.

CUM SCRIE: prin **`tenant_provisioning.scrie_denumirea`**, adică prin exact scriitorul unic pe care
îl folosesc și cele patru căi ale aplicației. O migrare care și-ar scrie propriile `UPDATE`-uri ar fi
a cincea cale — și prima care ar putea rupe simetria pe care tocmai o instalează.

  python3 -m core.migrare_r81_denumiri            # arată ce ar face, nu scrie nimic
  python3 -m core.migrare_r81_denumiri --scrie    # aplică
"""
import json
import sys

from core import db, tenant_provisioning as tp

MOTIV = "migrare R81, aliniere la denumirea fiscală"


def _nrm(s):
    return " ".join(str(s or "").split()).lower()


def divergentele(conn):
    """[(tenant_id, schema, nume_portofoliu, nume_fiscal)] — toate firmele la care cele două
    denumiri diferă, pe TOATĂ populația. Migrarea nu exclude cabinete: excluderea e o unealtă de
    măsurătoare (H1), nu una de reparație — o divergență e la fel de reală oriunde ar fi."""
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, nume FROM public.tenants ORDER BY id")
        randuri = cur.fetchall()
        for tid, schema, nume in randuri:
            try:
                cur.execute('SELECT nume FROM "%s".firma_profil WHERE id = 1' % schema)
                r = cur.fetchone()
            except Exception:
                conn.rollback()
                continue
            fiscal = r[0] if r else None
            if fiscal and _nrm(nume) != _nrm(fiscal):
                out.append((tid, schema, nume, fiscal))
    return out


def aplica(conn, scrie=False):
    lista = divergentele(conn)
    for tid, schema, vechi, fiscal in lista:
        print("  %-6s %-12s %-24r -> %r" % (tid, schema, vechi, fiscal))
        if not scrie:
            continue
        with conn.cursor() as cur:
            # [P1] Urma, ÎNAINTE de suprascriere. `tenant_id` prin sub-interogare — aceeași formă
            # ca la R79: dacă firma n-ar mai exista, rândul rămâne cu `NULL`, nu devine orfan.
            cur.execute(
                "INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, "
                "entitate_id, detalii) VALUES (NULL, "
                "(SELECT id FROM public.tenants WHERE id = %s), 'redenumire', 'tenant', %s, %s)",
                (tid, tid, json.dumps({
                    "motiv": MOTIV,
                    "nume_vechi_portofoliu": vechi,
                    "nume_nou": fiscal,
                    "sursa": "core/migrare_r81_denumiri.py",
                    "decizie": "Costin, 28.08.2026 — simetrie de scriere; fiscala rămâne",
                }, ensure_ascii=False)))
        # [P2] Scrierea trece prin scriitorul unic — amândouă locurile, aceeași tranzacție. Pe
        # `firma_profil` valoarea e deja aia, deci acolo e o rescriere identică; ce contează e că
        # migrarea NU devine a cincea cale care atinge un singur loc.
        tp.scrie_denumirea(conn, tid, fiscal)
    if scrie:
        conn.commit()
    return lista


def main():
    scrie = "--scrie" in sys.argv
    db.init_pool()
    with db.get_conn() as conn:
        print("divergențe găsite (populația ÎNTREAGĂ):")
        lista = aplica(conn, scrie=scrie)
        if not lista:
            print("  niciuna")
        if not scrie:
            print("\n-- nimic scris. Rulează cu `--scrie` ca să aplice. --")
            return
        ramase = divergentele(conn)
        print("\ndupă migrare: %d divergențe rămase" % len(ramase))
        for r in ramase:
            print("  RĂMASĂ:", r)


if __name__ == "__main__":
    main()
