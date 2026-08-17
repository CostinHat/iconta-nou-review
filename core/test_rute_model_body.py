# -*- coding: utf-8 -*-
"""core/test_rute_model_body.py — GARD: un model Pydantic pe un handler e BODY, nu query.

BUG (audit vizual tenant_005, 17.08.2026): `class PlanContIn` era definit la main.py:4798, DUPA
handlerul care-l folosea (main.py:1719). Cu `from __future__ import annotations` (PEP 563) adnotarea
`date: PlanContIn` e un STRING pe care @app.post il rezolva la IMPORT, in ordinea sursei. Modelul
fiind definit mai jos, FastAPI nu-l recunostea ca model de body -> trata `date` ca QUERY param ->
ORICE adaugare de cont in Plan de conturi pica cu HTTP 422 "date required". Adaugarea de cont
(scopul stratului) era complet nefunctionala. Fix: PlanContIn mutat inainte de handler.

Gard general: dupa import (cand toate modelele SUNT definite), get_type_hints rezolva adnotarile;
daca un param pe care FastAPI l-a clasificat ca QUERY (dependant.query_params, inghetat la import)
are tipul un BaseModel -> a fost misclasificat (model definit dupa handler). Clichet la 0.
RED-probat: mut PlanContIn inapoi dupa handler -> gardul pica.
"""
import pytest


def test_niciun_model_body_clasificat_ca_query():
    from typing import get_type_hints
    from pydantic import BaseModel
    try:
        import main
        from fastapi.routing import APIRoute
    except Exception as e:
        pytest.skip("main neimportabil: %s" % e)
    rele = []
    for r in main.app.routes:
        if not isinstance(r, APIRoute):
            continue
        try:
            hints = get_type_hints(r.endpoint)
        except Exception:
            continue
        for p in r.dependant.query_params:
            ann = hints.get(p.name)
            if isinstance(ann, type) and issubclass(ann, BaseModel):
                rele.append("%s %s: param %r tip %s clasificat ca QUERY (model definit dupa handler?)"
                            % (sorted(r.methods), r.path, p.name, ann.__name__))
    assert not rele, ("Model de body clasificat ca query (request-ul pica cu 422 'field required'):\n  "
                      + "\n  ".join(rele))
