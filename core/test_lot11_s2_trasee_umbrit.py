# -*- coding: utf-8 -*-
"""[lotul 11, S2] A doua față a atribuirii false din `scripts/scan_trasee.py` („un nume legat LOCAL prin altceva decât un import nu mai e
alias de modul”, `core/test_trasee.py::test_CALIBRARE_un_nume_umbrit_local_NU_mai_e_alias_de_modul`) era reparată numai în învelișul din
`main.py`, nu și în CORPUL DELEGAT din `core/uc_*.py`. Instanța: ruta NIR (`uc_tenants.stocuri_adauga`) scrie `with conn.cursor() as _c`, iar
`_c` e `casa_api` în alte funcții ale lui `uc_tenants` -> ruta primea `casa_api` (și tabelele lui) în inventar. Măsurat la reparație: șase
rute cu un modul fals (NIR, `/tenants`, borderoul și stornarea lui, `nota-tva-incasare` <- `amortizare_lunii`, configurarea WooCommerce)."""
import importlib.util
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_MAIN = [
    "from core import uc_tenants as _uc_tenants",
    "",
    "@app.post('/tenants/{tenant_id}/umbrit')",
    "def umbrit(tenant_id: int):",
    "    try:",
    "        return _uc_tenants.umbrit(tenant_id)",
    "    except _erori.EroareDeDomeniu as e:",
    "        raise _http_din(e)",
    "",
    "@app.post('/tenants/{tenant_id}/liber')",
    "def liber(tenant_id: int):",
    "    try:",
    "        return _uc_tenants.liber(tenant_id)",
    "    except _erori.EroareDeDomeniu as e:",
    "        raise _http_din(e)",
]
_UC = [
    "def alta():",
    "    from core import casa_api as _c",
    "    return _c.sold(conn)",
    "",
    "def umbrit(tenant_id):",
    "    with conn.cursor() as _c:",
    "        _c.execute('SELECT 1')",
    "",
    "def liber(tenant_id):",
    "    from core import casa_api as _c",
    "    return _c.sold(conn)",
]


def _st():
    spec = importlib.util.spec_from_file_location("scan_trasee_s2", os.path.join(RAD, "scripts", "scan_trasee.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_CALIBRARE_cursorul_din_corpul_delegat_nu_e_alias_de_modul(tmp_path, monkeypatch):
    """MUTAȚIE: bucla `for nume_legat in _legate_local(n)` scoasă din `_corp_efectiv` -> ruta „umbrit” primește `casa_api` -> pică."""
    st = _st()
    os.makedirs(os.path.join(str(tmp_path), "core"))
    io.open(os.path.join(str(tmp_path), "main.py"), "w", encoding="utf-8").write("\n".join(_MAIN) + "\n")
    io.open(os.path.join(str(tmp_path), "core", "uc_tenants.py"), "w", encoding="utf-8").write("\n".join(_UC) + "\n")
    monkeypatch.setattr(st, "RAD", str(tmp_path))
    monkeypatch.setattr(st, "_UC_CACHE", {})
    rute = {r["cale"]: r for r in st.citeste_rute()}
    assert "casa_api" not in rute["/tenants/{tenant_id}/umbrit"]["module"], rute["/tenants/{tenant_id}/umbrit"]["module"]
    # cealaltă direcție: importul din corpul propriu se citește mai departe (reparația nu golește inventarul)
    assert set(rute["/tenants/{tenant_id}/liber"]["module"]) >= {"casa_api"}, rute["/tenants/{tenant_id}/liber"]["module"]
