# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 14.4] GARD: adaugarea MANUALA de cont in plan NU suprascrie tacut un simbol existent.

Provocarea stratului de import 'plan_conturi' (Adauga cont: simbol + denumire) a scos o mutatie tacuta
PERICULOASA: handler-ul facea INSERT ... ON CONFLICT (simbol) DO UPDATE SET denumire=EXCLUDED.denumire.
Un contabil care 'adauga' simbolul '101' cu alta denumire REDENUMEA tacut contul OMFP standard 'Capital'
(seed-uit la crearea firmei), fara avertisment - corupere de date. Calea bulk (solduri_api) foloseste corect
ON CONFLICT DO NOTHING; doar calea manuala era outlierul. Acum refuza explicit, cu denumirea existenta.
Ratchet pe sursa (fara DB) impotriva revenirii la upsert tacut.
"""
from core import scan_sql_efectiv as _efectiv


def _handler_src():
    # [P7 · valul use-case] Corpul handler-ului traieste in `core/uc_tenants.py`; in `main.py` a
    # ramas poarta. Intrebarile de mai jos sunt despre ce FACE handler-ul, deci se pun pe corp.
    return _efectiv.sursa_functiei("tenant_plan_conturi_adauga")


def test_handler_gasit():
    assert _handler_src(), "handler tenant_plan_conturi_adauga negasit (redenumit?)"


def test_manual_add_nu_face_upsert_tacut():
    body = _handler_src()
    # semnatura defectului = upsert-ul care suprascrie (ON CONFLICT ... DO UPDATE); 'ON CONFLICT' singur
    # poate aparea legitim intr-un comentariu care descrie calea bulk (DO NOTHING).
    assert "DO UPDATE" not in body, "calea manuala inca face upsert (suprascrie tacut un cont existent)"


def test_manual_add_refuza_duplicatul_cu_mesaj():
    body = _handler_src()
    # [P7 · V1, 13.09.2026] SELECT-ul a plecat în repository; apelul se cere pe STRUCTURĂ.
    import ast as _ast
    # [P7 · valul use-case] Corpul rutei traieste in `core/uc_*.py`; in `main.py` a ramas
    # invelisul. Intrebarea e neatinsa — se pune pe nodul care poarta munca.
    _ruta = [_efectiv.functia("tenant_plan_conturi_adauga")[1]]
    assert _ruta, "handler-ul `tenant_plan_conturi_adauga` nu mai exista"
    _apelate = {getattr(c.func, "attr", None) for c in _ast.walk(_ruta[0]) if isinstance(c, _ast.Call)}
    assert _apelate >= {"denumirea_contului"}, \
        "handler-ul nu mai verifica existenta simbolului inainte de INSERT"
    assert "există deja" in body, "handler-ul nu mai refuza duplicatul cu mesaj de contabil"
    # [P7 · valul use-case] Intrebarea se despica in doua si devine mai TARE: use-case-ul refuza
    # cu un `Conflict` de domeniu, iar stratul HTTP traduce `Conflict` in 409. Se cer amandoua —
    # inainte, un `409` scris oriunde in corp trecea.
    assert "_erori.Conflict" in body, "refuzul duplicatului nu mai e un conflict de domeniu"
    assert _efectiv.cod_http("Conflict") == 409, "harta HTTP nu mai scoate conflictul ca 409"


def test_citirea_din_repository_intreaba_de_simbolul_existent():
    """Perechea probei de mai sus, cu sursa EI: verificarea chiar întreabă baza de simbol.

    Ruptă în două fiindcă o probă care citește două fișiere nu-și mai poate rezolva ancorele
    (v. `core/test_ancore_in_cod.py`).
    """
    _f = open("core/repo_contabilitate.py", encoding="utf-8").read()
    _f = _f.split("def denumirea_contului")[1][:400]
    assert "SELECT denumire FROM plan_conturi WHERE simbol" in _f, \
        "citirea din repository nu mai intreaba de simbolul existent"
