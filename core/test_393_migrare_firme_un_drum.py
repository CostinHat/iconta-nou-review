# -*- coding: utf-8 -*-
"""[deficiența 393, retestul Costin 19.10.2026] Import firme: CUI-urile din fișier și cele lipite trec pe ACELAȘI drum
(`uc_migrare.migrare_valideaza`: cifra de control înainte de ANAF, portofoliul) — până azi `/migrare/incarca` și `/migrare/fisier` le
trimiteau direct la ANAF; remediul spune unde e codul („în fișier” / „în lista lipită”)."""
import ast
import inspect
import textwrap

import main
from core import uc_migrare


def test_rutele_de_fisier_trec_prin_aceeasi_validare():
    def apeluri(f):
        """{(obiect.functie, argumente)} din arborele sintactic al rutei — nu sub-șiruri din sursă."""
        out = set()
        for n in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(f)))):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name):
                out.add(("%s.%s" % (n.func.value.id, n.func.attr),
                         tuple(a.id for a in n.args if isinstance(a, ast.Name)),
                         tuple((k.arg, getattr(k.value, "value", None)) for k in n.keywords)))
        return out
    for f in (main.migrare_incarca, main.migrare_fisier):
        ap = apeluri(f)
        assert {c for c, _a, kw in ap if c == "_uc_migrare.cui_de_trimis" and ("din_fisier", True) in kw} == {"_uc_migrare.cui_de_trimis"}, f.__name__
        assert {c for c, _a, _k in ap} >= {"_uc_migrare.rezultate_validare"}, f.__name__
        # numai codurile cu cifra de control bună ajung la ANAF
        assert {a for c, a, _k in ap if c == "anaf_api.valideaza_cui"} == {("de_intrebat",)}, f.__name__


def test_remediul_spune_unde_e_codul(monkeypatch):
    monkeypatch.setattr("core.anaf_api.valideaza_cui", lambda cuis: [])
    monkeypatch.setattr("core.auth_api.tenantii_userului", lambda conn, uid: [])
    for din_fisier, unde in ((False, "în lista lipită"), (True, "în fișier")):
        r = uc_migrare.migrare_valideaza(["14399841"], {"uid": 0}, din_fisier=din_fisier)["rezultate"]
        assert len(r) == 1 and r[0]["cui_invalid"] and ("corectează-l %s" % unde) in r[0]["motiv"], r
