# -*- coding: utf-8 -*-
"""[lotul 11, 22.10.2026] CALIBRARE — cititorul de tabele din SQL (`scripts/scan_trasee.RE_W`, `scripts/scan_functionalitati.RE_R`).

Defectul (găsit la `core/test_atribuire_scrieri.py`, ruta „valideaza” a facturii primite „scria” 15 tabele): prefixul de schemă
`%\\(?\\w*\\)?s` era lacom și tăia numele tabelului lipit de prefix la ULTIMUL „s” („UPDATE %sstoc” -> „toc”, „%sinregistrari” ->
„trari”), iar „DO UPDATE SET” dădea tabelul „SET”. Citirea „FROM %sinregistrari” nu se vedea deloc (punctul era cerut). Tabelele
false umflau atribuirea, cele tăiate o goleau. MUTAȚIE: forma veche a prefixului repusă -> pică.
"""
import pytest

from scripts import scan_functionalitati as F
from scripts import scan_trasee as T


@pytest.mark.parametrize("sql, tabele", [
    ("UPDATE %sstoc SET a = 1", ["stoc"]),
    ("INSERT INTO %sinregistrari (a) VALUES (1)", ["inregistrari"]),
    ("DELETE FROM %(s)sfacturi WHERE id = 1", ["facturi"]),
    ('UPDATE "%s".nir SET a = 1', ["nir"]),
    ("UPDATE {schema}.facturi SET serie = serie", ["facturi"]),
    ("UPDATE public.tenants SET a = 1", ["tenants"]),
    ("INSERT INTO x (a) VALUES (1) ON CONFLICT (a) DO UPDATE SET a = 1", ["x"]),
    ("SELECT 1 FROM t WHERE id = 1 FOR UPDATE", []),
])
def test_scrierile_dau_numele_intreg_al_tabelului(sql, tabele):
    assert [m.group(2) for m in T.RE_W.finditer(sql)] == tabele


@pytest.mark.parametrize("sql, tabele", [
    ("SELECT a FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.id = i.id", ["inregistrari", "inregistrari_linii"]),
    ('SELECT a FROM "%s".facturi', ["facturi"]),
    ("SELECT a FROM public.tenants", ["tenants"]),
])
def test_citirile_dau_numele_intreg_al_tabelului(sql, tabele):
    assert [m.group(1) for m in F.RE_R.finditer(sql)] == tabele
