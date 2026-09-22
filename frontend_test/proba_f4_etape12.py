# -*- coding: utf-8 -*-
"""F4 etapa 1-2: creare firma PFA sistem real (partida simpla, impozit pe venit, D212).
Idempotent: daca F4 exista deja (dupa CUI in cabinet), o gaseste si nu o recreeaza.
Cabinet A (48765), user 71507. Vezi asteptari_f4.md."""
import os
import sys

_RAD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/costin/iconta_nou")

from core import db as _db
from core import tenant_provisioning as _tp

CABINET = 48765
UID = 71507
NUME = "F4 PFA Sistem Real"


def _cui_valid_din(baza):
    """Completeaza cifra de control la un corp de CUI (algoritm oficial)."""
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp = str(baza).rjust(9, "0")[:9]
    s = sum(int(corp[i]) * ch[i] for i in range(9))
    r = (s * 10) % 11
    ctrl = 0 if r == 10 else r
    return corp.lstrip("0") + str(ctrl)


CUI = _cui_valid_din("4041000")  # PFA de test, cifra de control calculata


def main():
    _db.init_pool()
    with _db.get_conn() as conn:
        # idempotent: exista deja?
        with conn.cursor() as cur:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s",
                        (CUI, CABINET))
            r = cur.fetchone()
        if r:
            print("F4 exista deja: tenant_id=%s schema=%s CUI=%s" % (r[0], r[1], CUI))
            tid, sch = r[0], r[1]
        else:
            tmpl = open("/home/costin/iconta_nou/tenant_template.sql", encoding="utf-8").read()
            res = _tp.provision_tenant(conn, NUME, CUI, CABINET, UID, tmpl, tip_firma="pfa")
            conn.commit()
            tid, sch = res["tenant_id"], res["schema_name"]
            print("F4 CREATA: tenant_id=%s schema=%s CUI=%s tip=pfa" % (tid, sch, CUI))
        # vector/profil PFA sistem real (neplatitor TVA; impozit pe venit; partida simpla)
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % sch)
            cur.execute(
                "UPDATE firma_profil SET adresa=%s, oras=%s, judet=%s, caen=%s, platitor_tva=%s, "
                "declarant_nume=%s, declarant_prenume=%s, declarant_functie=%s, telefon=%s WHERE id=1",
                ("Str. Independentei 4", "Cluj-Napoca", "CJ", "6201", False,
                 "Ionescu", "Maria", "titular", "0700000004"))
        conn.commit()
        # verificare
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % sch)
            cur.execute("SELECT tip_firma, platitor_tva, cui, caen FROM firma_profil WHERE id=1")
            print("  vector:", cur.fetchone())
    print("F4 etapa 1-2 gata (schema %s)." % sch)


if __name__ == "__main__":
    main()
