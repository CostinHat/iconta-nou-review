# -*- coding: utf-8 -*-
"""GARD [R62, 26.08.2026]: portalul nu mută identitatea fără confirmare, nu trece un cont dintr-un
cabinet în altul, și nu face niciuna din ele fără ca cabinetul să vadă.

De unde vine. Din cele trei întrebări pe care Costin le-a pus la lotul 7 despre
`POST /portal/acces-cont/acces` — *accesul nu depășește pe al celui care îl dă · o adresă
existentă nu leagă un cont străin · cabinetul vede că s-a întâmplat*. Prima avea răspunsul **da**,
prin construcție. Celelalte două, **nu**.

Ordinea reparației e a lui, și motivul ei: **(2) izolarea între cabinete întâi**, fiindcă *„e
singura cale prin care date ale unui cabinet ajung la altul, iar aia nu e o chestiune de urmă, e
izolarea din P12"* · **(1)** apoi confirmarea adresei, fiindcă *„clientul trebuie să-și poată
schimba adresa, dar nu instant"* · **(3)** apoi urma.

CE FACE IMPOSIBIL: reactivarea unui cont de client al altui cabinet, pe **oricare** din cele două
căi (a clientului și a cabinetului — gardul repară clasa, nu instanța) · scrierea adresei de
autentificare din ruta de portal · o confirmare care aplică adresa fără s-o reconfrunte · un act
de acces sau de identitate fără urmă.

CUM ASERTEAZĂ: pe **apeluri din AST** și pe **mulțimea de tabele scrise**, derivată cu chiar
instrumentul inventarului (`scan_trasee`). Nicăieri nu se caută un șir într-un text — nici măcar
în SQL, fiindcă întrebarea *„scrie în `users`?"* are o formă structurată gata măsurată.

CE NU FACE, declarat: nu probează pe date. `principal_client_id` e completat pe **0 din 17** firme,
deci niciuna din rutele astea nu se poate exercita azi — punctul orb e firma, nu ecranul. Și nu
verifică ce vede cabinetul pe ECRAN: urma se scrie și se poate citi, dar dacă un ecran o arată e
altă întrebare.
"""
import ast
import importlib.util
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_trasee.py")

# rutele care pot LEGA un cont existent de o firmă: amândouă căile, nu doar cea a clientului
_LEAGA = ("portal_adauga_acces", "client_acces_creeaza")
# actele de acces sau de identitate: fiecare lasă urmă
_CU_URMA = ("portal_adauga_acces", "portal_revoca_acces", "client_acces_creeaza",
            "client_acces_revoca", "portal_schimba_email", "portal_confirma_email")


def _functii(sursa):
    return {n.name: n for n in ast.walk(ast.parse(sursa))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _apeluri(fn):
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


@pytest.fixture(scope="module")
def fns():
    return _functii(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())


@pytest.fixture(scope="module")
def scrie():
    """{cale: {tabelă: verbe}} — scrierile proprii ale fiecărei rute, derivate cu instrumentul
    inventarului. Întrebarea „ruta scrie în `users`?" are astfel o formă STRUCTURATĂ, în loc să
    fie o căutare de șir în SQL."""
    spec = importlib.util.spec_from_file_location("scan_trasee", _SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {r["cale"]: r["scrie_inline"] for r in m.citeste_rute()}


def test_ANTI_VACUU_toate_rutele_se_gasesc(fns, scrie):
    lipsa = (set(_LEAGA) | set(_CU_URMA)) - set(fns)
    assert not lipsa, "rute negăsite în main.py: %s — gardul s-ar uita în gol" % sorted(lipsa)
    fara_inventar = {"/portal/acces-cont/email", "/public/confirma-email"} - set(scrie)
    assert not fara_inventar, (
        "rute dispărute din inventar: %s — gardul n-ar avea ce măsura" % sorted(fara_inventar))


def test_izolarea_intre_cabinete_e_ceruta_pe_AMANDOUA_caile(fns):
    """P12. Un cont de client dezactivat al altui cabinet nu se reactivează, nici din portal,
    nici din cabinet."""
    rele = [r for r in _LEAGA if not _apeluri(fns[r]) >= {"_cere_acelasi_cabinet"}]
    assert not rele, (
        "rute care pot lega un cont existent fără să verifice cabinetul lui: %s — "
        "un cont al cabinetului A ar căpăta acces la o firmă a cabinetului B" % rele)


def test_ruta_de_portal_nu_mai_scrie_adresa_de_autentificare(scrie):
    """Adresa e identitatea (intrarea se face prin magic-link pe email). Scrierea ei dintr-o
    sesiune deschisă era chiar defectul: cine avea sesiunea muta contul."""
    tabele = set(scrie["/portal/acces-cont/email"])
    assert not tabele >= {"users"}, (
        "`PUT /portal/acces-cont/email` scrie iar în `users` — confirmarea a fost ocolită")
    assert tabele >= {"schimbari_email"}, (
        "cererea nu mai ajunge în `schimbari_email` — atunci ce confirmă ruta de confirmare? "
        "scrie: %s" % sorted(tabele))


def test_confirmarea_aplica_schimbarea_si_reconfrunta_adresa(fns, scrie):
    """Între cerere și confirmare pot trece 48 de ore. Dacă altcineva a luat adresa între timp,
    o scriere făcută pe nevăzute ar sparge unicitatea. Întrebarea are UN loc — `_adresa_e_libera`
    — chemat din amândouă rutele, ca asertarea să fie pe apel, nu pe forma interogării."""
    assert set(scrie["/public/confirma-email"]) >= {"users"}, (
        "confirmarea nu mai aplică schimbarea — scrie: %s"
        % sorted(scrie["/public/confirma-email"]))
    rele = [r for r in ("portal_schimba_email", "portal_confirma_email")
            if not _apeluri(fns[r]) >= {"_adresa_e_libera"}]
    assert not rele, "rute care nu mai verifică dacă adresa e liberă: %s" % rele


def test_fiecare_act_de_acces_sau_de_identitate_lasa_urma(fns):
    rele = [r for r in _CU_URMA if not _apeluri(fns[r]) >= {"_urma_portal"}]
    assert not rele, (
        "acte de acces sau de identitate fără urmă pentru cabinet: %s — "
        "cabinetul n-ar afla că s-au întâmplat" % rele)


_O_CALE_GARDATA = chr(10).join([
    "def portal_adauga_acces(date, ctx=None):",
    "    ex = gaseste(date.email)",
    "    creeaza(ex)",
    "",
    "def client_acces_creeaza(date, ctx=None):",
    "    _ex = gaseste(date.email)",
    "    _cere_acelasi_cabinet(_ex, ctx['firm'])",
    "    creeaza(_ex)",
])


def test_CALIBRARE_gardul_prinde_calea_lasata_deschisa():
    """Calibrare negativă (interdicția 76) pe forma exactă a greșelii de reparat: **una** din cele
    două căi gardată, cealaltă nu. Un gard scris doar pe ruta din care a ieșit constatarea ar fi
    trecut verde pe fișierul ăsta — și exact așa arată o reparație de instanță în loc de clasă."""
    fns = _functii(_O_CALE_GARDATA)
    rele = [r for r in _LEAGA if not _apeluri(fns[r]) >= {"_cere_acelasi_cabinet"}]
    assert rele == ["portal_adauga_acces"], (
        "calibrarea nu mai deosebește calea gardată de cea negardată: %s" % rele)
