# -*- coding: utf-8 -*-
"""GARD — Cartea mare ajunge la om, și fișa își poartă temeiul de completitudine.

DE CE EXISTĂ (30.08.2026, lista 3). `core/fisa_cont.py` produce Fișa de cont 14-6-22 — înlocuitorul
legal al Registrului Cartea mare (OMFP 2634/2015, Anexa 2, cod 14-1-3) — din iulie, **și producea pe
date reale**: măsurat azi, 6 firme cu mișcare și 43 de conturi în 2026. N-avea nici rută, nici ecran.
Artefactul se calcula și nu ajungea la nimeni: aceeași formă ca lista 5, pe alt artefact.

CE FACE IMPOSIBIL:

  1. **Ca ruta să dispară**, lăsând producătorul iar fără ieșire — și cu ea, cele trei părți pe care
     ecranul le consumă (`conturi`, `fisa`, `formular`).
  2. **Ca `temei_completitudine` să nu mai ajungă în răspuns.** Ăsta e punctul pentru care fișa e
     apărabilă la un control: *o fișă care omite o notă arată identic cu una completă*. Dacă
     producătorul încetează să-l emită, sau conversia la JSON îl pierde pe drum, gardul cade.
  3. **Ca `pentru_json` să lase în răspuns tipuri pe care un JSON nu le poate purta** — `Decimal`
     și `date` sunt exact ce produce motorul, iar `json.dumps` ar crăpa la runtime, pe ruta vie.
  4. **Ca lista de conturi să nu mai fie domeniul fișei.** Fișa cerută pe un cont fără mișcare iese
     goală; norma nu cere asta, iar controlul nu o acceptă.

CALIBRARE ÎN AMÂNDOUĂ DIRECȚIILE (METODA §22): conversia trebuie să schimbe ce trebuie schimbat
(`Decimal` → număr, `date` → șir) **și** să lase neatins ce e deja simplu — altfel „a convertit" n-ar
însemna nimic.

CE NU VERIFICĂ, declarat: dacă soldurile sunt CORECTE pe datele unei firme (aia e probă, nu gard) și
dacă ecranul chiar desenează ce primește — aia se măsoară viu, cu `scripts/scan_r97_livrat_tacut.py`.
"""
import ast
import datetime
import decimal
import io
import json
import os

from core import fisa_cont as fc

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fn(cale, nume):
    arbore = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    return next(n for n in ast.walk(arbore)
                if isinstance(n, ast.FunctionDef) and n.name == nume)


def test_ruta_exista_si_e_GET_pe_calea_asteptata():
    """Se citește NODUL decoratorului — un `ast.unparse` ar da text, iar comparația ar păzi
    ghilimelele, nu ruta."""
    fn = _fn("main.py", "cabinet_fisa_cont")
    ruta = next((d.args[0].value for d in fn.decorator_list
                 if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                 and d.func.attr == "get" and d.args
                 and isinstance(d.args[0], ast.Constant)), None)
    assert ruta == "/tenants/{tenant_id}/fisa-cont", ruta


def test_ruta_intoarce_cele_trei_parti_pe_care_le_consuma_ecranul():
    fn = _fn("main.py", "cabinet_fisa_cont")
    chei = {k.value for nod in ast.walk(fn) if isinstance(nod, ast.Dict)
            for k in nod.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    assert chei >= {"conturi", "fisa", "formular"}, chei


def test_ruta_cheama_producatorul_si_conversia_lui():
    """Sursa unică: ruta nu-și rescrie conversia, o cere modulului care știe tipurile."""
    fn = _fn("main.py", "cabinet_fisa_cont")
    chemate = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert chemate >= {"fisa_cont", "conturi_cu_miscare", "pentru_json"}, sorted(chemate)


def _fisa_falsa(cu_temei=True):
    """O fișă cu exact tipurile pe care le produce motorul: `Decimal`, `date`, `RandFisa`."""
    f = {
        "formular": fc.COD_FORMULAR,
        "cont": "5311",
        "an": 2026,
        "luna": None,
        "sold_initial": decimal.Decimal("100.00"),
        "sold_initial_declarat": True,
        "randuri": [fc.RandFisa(
            data=datetime.date(2026, 8, 30), cont_corespondent="4111",
            debit=decimal.Decimal("250.00"), credit=decimal.Decimal("0.00"),
            sold=decimal.Decimal("350.00"), sens_sold="D",
            document="12", explicatie="încasare", jurnal="casa")],
        "total_debit": decimal.Decimal("250.00"),
        "total_credit": decimal.Decimal("0.00"),
        "sold_final": decimal.Decimal("350.00"),
        "sens_sold_final": "D",
    }
    if cu_temei:
        f["temei_completitudine"] = "toate liniile care ating contul, pe note validate"
    return f


def test_conversia_scoate_tipurile_pe_care_un_JSON_nu_le_poate_purta():
    j = fc.pentru_json(_fisa_falsa())
    json.dumps(j)  # crapă dacă a rămas un Decimal sau un date
    assert j["sold_initial"] == 100.0 and isinstance(j["sold_initial"], float)
    assert j["randuri"][0]["data"] == "2026-08-30"
    assert j["randuri"][0]["debit"] == 250.0


def test_conversia_NU_atinge_ce_e_deja_simplu():
    """Direcția inversă: fără ea, „a convertit" ar putea însemna „a stricat tot"."""
    j = fc.pentru_json(_fisa_falsa())
    assert j["cont"] == "5311" and j["an"] == 2026 and j["luna"] is None
    assert j["sens_sold_final"] == "D" and j["sold_initial_declarat"] is True
    assert j["randuri"][0]["explicatie"] == "încasare"
    assert j["randuri"][0]["jurnal"] == "casa"


def test_temeiul_de_completitudine_ajunge_pana_in_raspuns():
    """Punctul pentru care fișa e apărabilă: o fișă care omite o notă arată identic cu una completă."""
    j = fc.pentru_json(_fisa_falsa())
    assert j.get("temei_completitudine"), j
    # și proba inversă: dacă producătorul nu-l mai emite, se vede — conversia nu-l inventează
    assert "temei_completitudine" not in fc.pentru_json(_fisa_falsa(cu_temei=False))


def test_producatorul_emite_fisa_ca_afirmatie_tipata_nu_ca_dict_de_proza():
    """`fisa_cont` cheamă `afirmatie(...)` — deci fișa are `fel`, `tip`, `motiv` și temeiul, iar
    câmpurile ei nu se pot rata la citire (decizia din 21.08)."""
    fn = _fn("core/fisa_cont.py", "fisa_cont")
    chemate = {n.func.id for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert chemate >= {"afirmatie"}, sorted(chemate)


def test_codul_formularului_e_cel_din_norma():
    """14-6-22 e fișa; 14-1-3 e registrul pe care îl înlocuiește. Se citește constanta, nu un text."""
    assert fc.COD_FORMULAR == "14-6-22"
