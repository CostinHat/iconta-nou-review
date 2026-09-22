# -*- coding: utf-8 -*-
"""F5 etapa 1-2: creare firma SRL cu salariati (D112, REGES-ONLINE). Idempotent.
Cabinet A (48765), user 71507. Vezi asteptari_f5.md."""
import sys
sys.path.insert(0, "/home/costin/iconta_nou")
from core import db as _db
from core import tenant_provisioning as _tp

CABINET = 48765
UID = 71507
NUME = "F5 SRL Salariati SRL"


def _cui_valid_din(baza):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp = str(baza).rjust(9, "0")[:9]
    s = sum(int(corp[i]) * ch[i] for i in range(9))
    r = (s * 10) % 11
    ctrl = 0 if r == 10 else r
    return corp.lstrip("0") + str(ctrl)


CUI = _cui_valid_din("4051000")


def main():
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s",
                        (CUI, CABINET))
            r = cur.fetchone()
        if r:
            print("F5 exista deja: tenant_id=%s schema=%s CUI=%s" % (r[0], r[1], CUI))
            tid, sch = r[0], r[1]
        else:
            tmpl = open("/home/costin/iconta_nou/tenant_template.sql", encoding="utf-8").read()
            res = _tp.provision_tenant(conn, NUME, CUI, CABINET, UID, tmpl, tip_firma="srl")
            conn.commit()
            tid, sch = res["tenant_id"], res["schema_name"]
            print("F5 CREATA: tenant_id=%s schema=%s CUI=%s tip=srl" % (tid, sch, CUI))
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % sch)
            cur.execute(
                "UPDATE firma_profil SET adresa=%s, oras=%s, judet=%s, caen=%s, regim_fiscal=%s, "
                "platitor_tva=%s, declarant_nume=%s, declarant_prenume=%s, declarant_functie=%s, telefon=%s WHERE id=1",
                ("Str. Muncii 5", "Cluj-Napoca", "CJ", "6201", "micro", False,
                 "Popa", "Andrei", "administrator", "0700000005"))
        conn.commit()
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % sch)
            cur.execute("SELECT tip_firma, regim_fiscal, platitor_tva, cui, caen FROM firma_profil WHERE id=1")
            print("  vector:", cur.fetchone())
    print("F5 etapa 1-2 gata (schema %s)." % sch)


if __name__ == "__main__":
    main()
