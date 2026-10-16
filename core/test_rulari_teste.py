# -*- coding: utf-8 -*-
"""`core.rulari_teste.in_curs` recunoaște rulările de teste după linia de comandă (pe un `/proc` de probă): pytest, plasa, uneltele
vizuale, aplicația de probă pe 8019 — și NU producția (uvicorn pe 8010) sau un proces oarecare.
MUTAȚII: `SEMNE` fără `pytest` -> pică; portul aplicației de probă scos -> pică; producția socotită probă -> pică."""
import os

from core import rulari_teste as rt


def _proc(tmp_path, procese):
    for pid, argv in procese.items():
        d = tmp_path / str(pid)
        d.mkdir()
        (d / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")
    (tmp_path / "self").mkdir()
    return str(tmp_path)


def test_rularile_de_teste_se_vad_productia_nu(tmp_path):
    proc = _proc(tmp_path, {
        11: ["/srv/productie/venv/bin/python", "-m", "pytest", "-q", "-n", "3"],
        12: ["/home/costin/iconta_lucru/venv/bin/python", "scripts/e2e_poarta.py", "--arbore"],
        13: ["/home/costin/iconta_lucru/venv/bin/python", "-m", "uvicorn", "main:app", "--port", "8019"],
        14: ["/srv/productie/venv/bin/python", "-m", "uvicorn", "main:app", "--port", "8010"],
        15: ["/usr/sbin/nginx", "-g", "daemon off;"],
        16: ["/home/costin/iconta_lucru/venv/bin/python", "frontend_test/vizual/axe_scan.py"],
    })
    assert sorted(pid for pid, _c in rt.in_curs(proc)) == [11, 12, 13, 16]


def test_fara_proc_nu_crapa():
    assert rt.in_curs(os.path.join("/", "nu-exista-proc")) == []
