# -*- coding: utf-8 -*-
"""GARD B3: proprietarul cabinetului (admin_firma creat la înregistrare) primește drepturile
operaționale (pregătire/validare/depunere) la creare. Altfel e blocat să depună pe cont propriu,
fără nimeni deasupra care să i le acorde — deadlock de bootstrap (fostul F163)."""
import io
import re


def test_owner_admin_primeste_drepturi_la_creare():
    src = io.open("core/auth_api.py", encoding="utf-8").read()
    # INSERT-ul de creare a proprietarului cabinetului (admin_firma) acordă cele trei drepturi
    m = re.search(r"INSERT INTO public\.users[\s\S]{0,300}?admin_firma[\s\S]{0,120}?RETURNING id", src)
    assert m, "nu găsesc INSERT-ul de creare admin_firma în auth_api.py"
    blob = m.group(0)
    for drept in ("poate_pregati", "poate_valida", "poate_depune"):
        assert drept in blob, "INSERT-ul proprietarului nu acordă %s (B3 regres)" % drept
    assert "true,true,true" in blob.replace(" ", ""), \
        "drepturile operaționale nu sunt setate true la crearea proprietarului"
