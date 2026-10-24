# -*- coding: utf-8 -*-
"""core/migrare_asistenti_fara_firme.py — [C123, lotul 12] datele existente: asistenții rămași deja fără nicio firmă.

DEFECTUL. „Scoate firma” (`tenant_stergere.sterge`) lua rândurile din `public.user_tenants`, dar nu aplica regula „zero firme” a
cabinetului (`asistenti_api.aplica_regula_zero_firme`: competențele se golesc, contul de asistent se dezactivează, rămâne în istoric) —
regula se aplica numai când administratorul scotea firmele din ecranul colegului. Un asistent care lucra numai firma scoasă a rămas
activ, cu competențe, pe nicio firmă. Reparația din `tenant_stergere.sterge` oprește cazurile NOI; migrarea de aici le închide pe cele
făcute înainte (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”).

CE FACE: pentru fiecare cont ACTIV cu `rol='angajat'` care nu mai are niciun rând în `user_tenants`, aceeași regulă, prin aceeași funcție
(`aplica_regula_zero_firme`) — nu o a doua implementare. Administratorii (`admin_firma`) și clienții nu se ating. Contul NU se șterge:
administratorul îl reactivează din Asistenți, cu firmele și competențele alese din nou. Idempotentă (a doua rulare nu mai găsește nimic).
Ieșirea numără conturile, fără adrese (datele cabinetelor nu se scriu în jurnal).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_asistenti_fara_firme.py`.
"""
from core import db

SQL_RAMASI = ("SELECT u.id, u.accounting_firm_id FROM public.users u WHERE u.rol = 'angajat' AND u.activ "
              "AND u.accounting_firm_id IS NOT NULL "
              "AND NOT EXISTS (SELECT 1 FROM public.user_tenants ut WHERE ut.user_id = u.id) ORDER BY u.id")


def ramasi(conn):
    """[(user_id, cabinet_id)] — asistenții activi fără nicio firmă."""
    with conn.cursor() as cur:
        cur.execute(SQL_RAMASI)
        return [tuple(r) for r in cur.fetchall()]


def aplica(conn):
    """Regula „zero firme” pe fiecare asistent activ fără firme. Nu comite. -> numărul conturilor dezactivate."""
    from core import asistenti_api as _asist
    n = 0
    for uid, cabinet_id in ramasi(conn):
        r = _asist.aplica_regula_zero_firme(conn, cabinet_id, uid)
        if not (r.get("ok") and r.get("dezactivat")):
            raise RuntimeError("regula „zero firme” nu s-a aplicat contului %s: %r" % (uid, r))
        n += 1
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        n = aplica(conn)
        conn.commit()
        ramas = len(ramasi(conn))
    print("migrare_asistenti_fara_firme: %d conturi de asistent fără nicio firmă dezactivate (competențele golite); rămase active: %d"
          % (n, ramas))
    if ramas:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
