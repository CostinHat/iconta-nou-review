"""[715.1, comanda 14.3] Alerta de acces anormal ocolește numai cabinetele MARCATE „de test” (nu cele cu „test” în nume); marcajul îl pune superadminul."""
import json

import pytest

from core import alerta_acces as AA, erori, uc_admin
from core.test_lot11_t import conn_t  # noqa: F401 — fixtura schemei sintetice


def _cabinet(cur, nume, eticheta, de_test):
    cur.execute("INSERT INTO public.accounting_firms (nume, de_test) VALUES (%s, %s) RETURNING id", (nume, de_test))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO public.users (email, password_hash, nume, prenume, accounting_firm_id) VALUES (%s,'x','Ionescu','Ana',%s) RETURNING id",
                ("ztest7151_%s@exemplu.test" % eticheta, fid))
    uid = cur.fetchone()[0]
    for _ in range(400):
        cur.execute("INSERT INTO public.audit_log (user_id, actiune, detalii) VALUES (%s,'PUT /tenants/1/x',%s)", (uid, json.dumps({"status": 200})))
    return fid, uid


def test_exceptia_urmeaza_marcajul_nu_numele(conn_t):
    conn = conn_t
    with conn.cursor() as cur:
        _f1, u_marcat = _cabinet(cur, "Cabinet Oarecare Ztest7151 SRL", "a", True)          # fără „test” în nume, dar marcat
        _f2, u_nume = _cabinet(cur, "Cabinet Test Real Ztest7151 SRL", "b", False)          # „Test” în nume, dar NEmarcat
    semnalati = {u["user_id"] for u in AA.detecteaza(conn, 10, 8, 300)}
    assert u_marcat not in semnalati, "cabinetul marcat „de test” nu alertează"
    assert u_nume in semnalati, "un cabinet real cu „Test” în nume alertează (excepția nu se mai face după nume)"


def test_doar_superadminul_pune_marcajul_si_numai_booleeni(conn_t):
    with pytest.raises(erori.FaraDrept):
        uc_admin.admin_cabinet_de_test(1, True, {"rol": "admin_firma", "uid": 1})
    with pytest.raises(erori.DateInvalide):
        uc_admin.admin_cabinet_de_test(1, "da", {"rol": "superadmin", "uid": 1})
    with pytest.raises(erori.Inexistent):
        uc_admin.admin_cabinet_de_test(99999999, True, {"rol": "superadmin", "uid": 1})
