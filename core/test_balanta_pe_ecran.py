# -*- coding: utf-8 -*-
"""GARD — balanța se poate CITI, nu doar descărca; iar „se închide" nu se afirmă pe gol.

DE CE EXISTĂ (30.08.2026, a treia poziție din lista 5). Balanța se închidea pe toate cele 13 firme
cu date, dar singura rută spre cifrele ei întorcea un **PDF**: ecranul avea titlu, navigare pe lună
și un buton „Descarcă PDF". *O cifră pe care n-o poți citi decât descărcând-o nu se poate verifica
pe ecran* — chiar criteriul listei 5.

CE FACE IMPOSIBIL:
  1. ca ruta de date să dispară, lăsând doar PDF-ul;
  2. ca totalurile să se adune a doua oară, altundeva — hârtia și ecranul s-ar despica în tăcere;
  3. ca **„nu s-a verificat nimic" să fie rotunjit la „se închide"**. O lună fără nicio înregistrare
     are toate cele trei perechi egale — 0 = 0 — deci o balanță goală ar trece drept închisă. Ăsta
     nu e un caz de margine, e chiar forma interdicției 32: *un necunoscut nu se rotunjește la ce
     știi*. De-aia starea are TREI valori, nu două.

CALIBRARE ÎN AMÂNDOUĂ DIRECȚIILE (METODA §22): un set echilibrat trebuie declarat închis, unul
dezechilibrat trebuie declarat deschis — iar toleranța trebuie să fie o toleranță, nu o amnistie:
sub un ban trece, peste un ban nu.

CE NU VERIFICĂ, declarat: dacă cifrele balanței sunt CORECTE pe datele unei firme (aia cere baza și
e o probă), și dacă JS-ul chiar desenează ce primește — aia se măsoară viu, cu
`scripts/scan_r97_livrat_tacut.py`.
"""
import ast
import io
import os

from core import documente_api as da

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rand(cont, si_d=0.0, si_c=0.0, rul_d=0.0, rul_c=0.0, sf_d=0.0, sf_c=0.0):
    return {"cont": cont, "denumire": "cont " + cont, "si_d": si_d, "si_c": si_c,
            "rul_d": rul_d, "rul_c": rul_c, "sf_d": sf_d, "sf_c": sf_c}


ECHILIBRATA = [_rand("5121", si_d=1000.0, rul_d=500.0, sf_d=1200.0),
               _rand("401", si_c=1000.0, rul_c=200.0, sf_c=700.0),
               _rand("607", rul_d=300.0, sf_d=500.0),
               _rand("707", rul_c=600.0, sf_c=1000.0)]


def test_o_balanta_echilibrata_e_declarata_inchisa():
    inc = da.inchidere_balanta(ECHILIBRATA)
    assert inc["stare"] == "se_inchide", inc
    assert all(p["inchisa"] for p in inc["perechi"])
    assert inc["randuri"] == 4


def test_o_balanta_dezechilibrata_e_declarata_deschisa_si_arata_unde():
    stricate = [dict(r) for r in ECHILIBRATA]
    stricate[0]["rul_d"] += 25.0
    inc = da.inchidere_balanta(stricate)
    assert inc["stare"] == "nu_se_inchide", inc
    pe_rulaje = next(p for p in inc["perechi"] if p["ce"] == "rulaje")
    assert not pe_rulaje["inchisa"]
    assert pe_rulaje["diferenta"] == 25.0, "diferența trebuie ARĂTATĂ, nu doar semnalată"
    # celelalte două perechi rămân închise: verdictul e pe pereche, nu pe balanță în bloc
    assert [p["inchisa"] for p in inc["perechi"]] == [True, False, True]


def test_balanta_goala_NU_se_inchide_ci_nu_are_ce_verifica():
    """Instanța pentru care există fișierul ăsta: 0 = 0 pe toate trei, deci verdictul naiv ar fi
    „se închide" — despre o lună în care nu s-a înregistrat nimic."""
    inc = da.inchidere_balanta([])
    assert inc["stare"] == "nimic_de_verificat", inc
    assert inc["stare"] != "se_inchide"
    assert inc["randuri"] == 0
    # perechile există și acolo: omul vede că toate trei sunt zero, nu o casetă goală
    assert len(inc["perechi"]) == 3


def test_toleranta_e_toleranta_nu_amnistie():
    """Sub un ban e zgomot de virgulă mobilă; peste un ban e o diferență, și se spune."""
    mic = [dict(r) for r in ECHILIBRATA]
    mic[0]["rul_d"] += 0.004
    assert da.inchidere_balanta(mic)["stare"] == "se_inchide"
    mare = [dict(r) for r in ECHILIBRATA]
    mare[0]["rul_d"] += 0.02
    assert da.inchidere_balanta(mare)["stare"] == "nu_se_inchide"


def test_totalurile_sunt_cele_sase_coloane_si_se_aduna():
    tot = da.totaluri_balanta(ECHILIBRATA)
    assert set(tot) == {"si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c"}
    assert tot["si_d"] == 1000.0 and tot["si_c"] == 1000.0
    assert tot["rul_d"] == 800.0 and tot["rul_c"] == 800.0
    assert tot["sf_d"] == 1700.0 and tot["sf_c"] == 1700.0


def _fn(cale, nume):
    arbore = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    return next(n for n in ast.walk(arbore)
                if isinstance(n, ast.FunctionDef) and n.name == nume)


def test_pdful_nu_isi_mai_aduna_singur_totalurile():
    """Sursa unică, apărată structural: dacă PDF-ul reîncepe să adune, ecranul poate arăta altceva."""
    fn = _fn("core/documente_api.py", "balanta_pdf")
    chemate = {n.func.id for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    # operator de MULȚIME, nu `in`: pe un șir crapă, în loc să treacă ca sub-șir
    assert chemate >= {"totaluri_balanta"}, "PDF-ul nu mai citește totalurile din sursa unică"


def test_ruta_de_date_exista_si_intoarce_cele_trei_parti():
    """Ruta se citește din AST, nu se caută ca șir: un nume găsit într-un comentariu n-ar dovedi
    că ruta există."""
    fn = _fn("main.py", "cabinet_balanta_date")
    chei = {k.value for nod in ast.walk(fn) if isinstance(nod, ast.Dict)
            for k in nod.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    assert chei >= {"randuri", "totaluri", "inchidere"}, chei
    # Și chiar e o rută GET, nu o funcție rămasă nelegată. Se citește NODUL decoratorului — un
    # `ast.unparse` ar da înapoi text, iar comparația ar păzi ghilimelele, nu ruta.
    ruta = next((d.args[0].value for d in fn.decorator_list
                 if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                 and d.func.attr == "get" and d.args
                 and isinstance(d.args[0], ast.Constant)), None)
    assert ruta == "/tenants/{tenant_id}/balanta", ruta


def test_cele_trei_perechi_sunt_cele_din_norma():
    """Perechile se citesc din constantă, ca mulțime — nu se caută un șir într-un text (METODA §23)."""
    assert {p[0] for p in da.PERECHI_BALANTA} == {"sold initial", "rulaje", "sold final"}
    assert {p[1] for p in da.PERECHI_BALANTA} == {"si_d", "rul_d", "sf_d"}
    assert {p[2] for p in da.PERECHI_BALANTA} == {"si_c", "rul_c", "sf_c"}
