# -*- coding: utf-8 -*-
"""core/test_post_token_fara_conexiune.py — rotatia tokenului nu mai tine o conexiune din pool.

**Ce s-a mutat, si e o schimbare de CONTRACT, nu doar de pool.** Contractul P4 de dinainte spunea ca
*limita apartine use-case-ului*: `apel_anaf` deschidea conexiunea, deci el hotara cand se comite.
Consecinta era ca apelul `/token` — termen **30 s**, cel mai lung din val — se executa cu o
conexiune in mana pe toate cele sapte cai. Decizia arhitectului din 11.09.2026: **rotatia detine
tranzactia scurta de persist+commit, de dupa HTTP.**

Garantia P4 ramane, si se probeaza aici: perechea noua e COMISA inainte ca apelantul sa poata
continua sau sa poata esua. Iar regresia de care avertiza P4 — doua conexiuni concurente pe acelasi
rand — e imposibila prin constructie: fiecare bloc se inchide inainte ca urmatorul sa se deschida.

**Proba care conteaza cel mai mult e A**: in timpul apelului la ANAF se NUMARA conexiunile scoase
din pool. Zero. Nu se deduce din forma codului — se masoara pe pool, in timpul apelului.
"""
from __future__ import annotations

import ast
import io
import os
import time

import psycopg2
import pytest

from core import db as _db
from core import spv_conector as s

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRM_TEST = 990101
TENANT_TEST = 990102
PRIN_FIRM = s.principal_firm(FIRM_TEST)


def _jwt(serial, exp):
    import base64
    import json
    cap = base64.urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
    corp = base64.urlsafe_b64encode(
        json.dumps({"serial_number": serial, "exp": exp}).encode()).rstrip(b"=").decode()
    return "%s.%s.x" % (cap, corp)


@pytest.fixture
def baza():
    """Conexiune care COMITE + pool initializat. Curata dupa ea, marginit pe principalii de test."""
    try:
        c = psycopg2.connect(_db.dsn_din_config(_db.config_din_env()))
    except Exception as e:                       # noqa: BLE001
        pytest.skip("DB indisponibil: %s" % e)
    try:
        _db.pool()
    except Exception:                            # noqa: BLE001
        _db.init_pool()
    c.autocommit = True
    try:
        yield c
    finally:
        try:
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.spv_token WHERE accounting_firm_id=%s "
                            "   OR tenant_id=%s", (FIRM_TEST, TENANT_TEST))
        finally:
            c.close()


def _pune_token(c, access_expira_delta=90 * 86400):
    acum = int(time.time())
    return s.salveaza_token(c, PRIN_FIRM, {
        "access_token": "acc-vechi", "refresh_token": "ref-vechi",
        "serial_certificat": "SER-T",
        "access_expira": s.datetime.fromtimestamp(acum + access_expira_delta, tz=s.timezone.utc),
        "refresh_expira": s.datetime.fromtimestamp(acum + 365 * 86400, tz=s.timezone.utc)})


def _raspuns_nou(serial="SER-T"):
    acum = int(time.time())
    return {"access_token": _jwt(serial, acum + 90 * 86400),
            "refresh_token": "ref-NOU", "expires_in": 90 * 86400}


def _conexiuni_scoase():
    """Cate conexiuni sunt SCOASE din pool acum. `_used` e registrul pool-ului psycopg2."""
    return len(getattr(_db.pool(), "_used", {}))


# ============================================================
#  A — HTTP-ul ruleaza FARA conexiune in mana (masurat, nu dedus)
# ============================================================
def test_A_httpul_ruleaza_fara_nicio_conexiune_scoasa(baza, monkeypatch):
    _pune_token(baza)
    tok = s.ia_token_activ(baza, PRIN_FIRM)
    vazute = []

    def _fals(_rt):
        vazute.append(_conexiuni_scoase())      # CAT TIMP „vorbim cu ANAF"
        return _raspuns_nou()

    monkeypatch.setattr(s, "reimprospateaza_pereche", _fals)
    s.reimprospateaza_token(tok)
    assert vazute == [0], (
        "in timpul apelului `/token` erau %r conexiuni scoase din pool — termenul e 30 s, iar "
        "pool-ul are 10" % vazute)


def test_A_calibrare_masuratoarea_CHIAR_vede_o_conexiune_scoasa(baza):
    """ANTI-VACUUM pentru proba de mai sus: daca `_conexiuni_scoase()` ar intoarce mereu 0, ea ar
    trece si pe codul stricat."""
    inainte = _conexiuni_scoase()
    with _db.get_conn() as _c:
        assert _conexiuni_scoase() == inainte + 1, "masuratoarea nu vede o conexiune scoasa"
    assert _conexiuni_scoase() == inainte


# ============================================================
#  B / E — succes si esec HTTP
# ============================================================
def test_B_succes_tokenul_nou_e_COMIS(baza, monkeypatch):
    _pune_token(baza)
    tok = s.ia_token_activ(baza, PRIN_FIRM)
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda _rt: _raspuns_nou())
    s.reimprospateaza_token(tok)
    # citit de pe ALTA conexiune decat cea a rotatiei: daca n-ar fi comis, n-ar fi vizibil
    with _db.get_conn() as alta:
        dupa = s.ia_token_activ(alta, PRIN_FIRM)
    assert dupa["refresh_token"] == "ref-NOU", "perechea noua nu e vizibila -> nu a fost comisa"


def test_E_esec_HTTP_nu_scrie_token_nou_si_dezactiveaza(baza, monkeypatch):
    _pune_token(baza)
    tok = s.ia_token_activ(baza, PRIN_FIRM)

    def _cade(_rt):
        raise s.EroareSpv("HTTP 400 la /token")

    monkeypatch.setattr(s, "reimprospateaza_pereche", _cade)
    with pytest.raises(s.EroareSpvRefreshEsuat):
        s.reimprospateaza_token(tok)
    with _db.get_conn() as alta:
        assert s.ia_token_activ(alta, PRIN_FIRM) is None, "tokenul mort a ramas activ"


# ============================================================
#  D — persistarea cade: NU se raporteaza succes
# ============================================================
def test_D_daca_persistarea_cade_operatia_NU_raporteaza_succes(baza, monkeypatch):
    _pune_token(baza)
    tok = s.ia_token_activ(baza, PRIN_FIRM)
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda _rt: _raspuns_nou())

    def _cade(*a, **k):
        raise RuntimeError("scrierea a picat")

    monkeypatch.setattr(s, "salveaza_token", _cade)
    with pytest.raises(RuntimeError):
        s.reimprospateaza_token(tok)
    with _db.get_conn() as alta:
        ramas = s.ia_token_activ(alta, PRIN_FIRM)
    assert ramas["refresh_token"] == "ref-vechi", "s-a raportat altceva decat esec"


# ============================================================
#  C / G — apelantul cade DUPA rotatie; si calea de 401
# ============================================================
def test_C_tokenul_rotit_ramane_comis_cand_apelantul_cade_dupa(baza, monkeypatch):
    """Chiar garantia P4, pe calea reala: `apel_anaf` roteste, apoi apelul propriu-zis cade."""
    _pune_token(baza, access_expira_delta=-60)          # EXPIRAT: cere rotatie
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda _rt: _raspuns_nou())

    def _request_cade(*a, **k):
        raise RuntimeError("reteaua a cazut dupa rotatie")

    monkeypatch.setattr(s.requests, "request", _request_cade)
    with pytest.raises(RuntimeError):
        s.apel_anaf(PRIN_FIRM, "GET", "https://exemplu/x")
    with _db.get_conn() as alta:
        dupa = s.ia_token_activ(alta, PRIN_FIRM)
    assert dupa is not None and dupa["refresh_token"] == "ref-NOU", (
        "perechea rotita s-a pierdut cand apelul de dupa a cazut — ANAF o considera singura valida")


def test_G_pe_401_rotatia_pastreaza_aceeasi_regula(baza, monkeypatch):
    _pune_token(baza)                                   # NEexpirat: rotatia vine din 401
    monkeypatch.setattr(s, "reimprospateaza_pereche", lambda _rt: _raspuns_nou())
    raspunsuri = []

    class _R:
        def __init__(self, cod):
            self.status_code = cod

    def _request(*a, **k):
        raspunsuri.append(1)
        return _R(401 if len(raspunsuri) == 1 else 200)

    monkeypatch.setattr(s.requests, "request", _request)
    r = s.apel_anaf(PRIN_FIRM, "GET", "https://exemplu/x")
    assert r.status_code == 200 and len(raspunsuri) == 2, "retry-ul de 401 nu s-a facut o data"
    with _db.get_conn() as alta:
        assert s.ia_token_activ(alta, PRIN_FIRM)["refresh_token"] == "ref-NOU"


# ============================================================
#  F / I — STRUCTURAL: HTTP-ul nu se reintroduce sub conexiune
# ============================================================
def _apeluri_sub_conexiune():
    """Apelurile catre `_post_token` si invelisurile lui, care stau LEXICAL intr-un
    `with ...get_conn(...)`. Se asertează pe pozitii in arbore, nu pe text."""
    tinte = {"_post_token", "schimba_cod_pe_token", "reimprospateaza_pereche"}
    out, total = [], 0
    fisiere = [os.path.join(RADACINA, "main.py")]
    core = os.path.join(RADACINA, "core")
    for f in sorted(os.listdir(core)):
        if f.endswith(".py") and not f.startswith("test_"):
            fisiere.append(os.path.join(core, f))
    for cale in fisiere:
        arbore = ast.parse(io.open(cale, encoding="utf-8").read())
        parinte = {}
        for n in ast.walk(arbore):
            for c in ast.iter_child_nodes(n):
                parinte[c] = n
        for n in ast.walk(arbore):
            if not isinstance(n, ast.Call):
                continue
            f_ = n.func
            ident = (f_.attr if isinstance(f_, ast.Attribute)
                     else f_.id if isinstance(f_, ast.Name) else None)
            if ident not in tinte:
                continue
            total += 1
            p, sub = parinte.get(n), False
            while p is not None:
                if isinstance(p, ast.With):
                    for it in p.items:
                        e = it.context_expr
                        if (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                                and e.func.attr.startswith("get_conn")):
                            sub = True
                p = parinte.get(p)
            if sub:
                out.append("%s:%d" % (os.path.relpath(cale, RADACINA), n.lineno))
    return out, total


def test_I_niciun_apel_de_token_nu_sta_sub_o_conexiune():
    """CLICHET 0. Prinde si al cincilea loc, cel scris maine.

    **CE NU VEDE, declarat.** Garda asta e LEXICALA: prinde un apel pus intr-un `with get_conn` din
    aceeasi functie. NU prinde cazul in care conexiunea e tinuta de APELANT, cu doua functii mai
    sus — si chiar asta era forma defectului reparat azi, motiv pentru care proba de fata trece si
    pe baseline-ul `6b971f36`. Cazul acela e acoperit de proba `A`, care numara conexiunile scoase
    din pool IN TIMPUL apelului, si de inventarul P5, care urmareste lantul.
    """
    sub, _total = _apeluri_sub_conexiune()
    assert sub == [], ("apeluri `/token` executate cu o conexiune din pool in mana: %s" % sub)


def test_I_anti_vacuum_scanul_chiar_vede_apelurile():
    _sub, total = _apeluri_sub_conexiune()
    assert total >= 4, "scanul vede doar %d apeluri — domeniu prea mic, clichetul 0 ar fi vid" % total


def test_F_rotatia_nu_deschide_o_conexiune_peste_alta():
    """Regresia de care avertiza P4: doua conexiuni concurente pe acelasi rand. Structural —
    in `reimprospateaza_token`, niciun `with get_conn` nu contine un alt `with get_conn`."""
    arbore = ast.parse(io.open(os.path.join(RADACINA, "core", "spv_conector.py"),
                               encoding="utf-8").read())
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "reimprospateaza_token")

    def _e_get_conn(w):
        return any(isinstance(it.context_expr, ast.Call)
                   and isinstance(it.context_expr.func, ast.Attribute)
                   and it.context_expr.func.attr.startswith("get_conn") for it in w.items)

    blocuri = [w for w in ast.walk(fn) if isinstance(w, ast.With) and _e_get_conn(w)]
    assert blocuri, "rotatia nu mai deschide nicio conexiune — reciteste proba"
    for a in blocuri:
        for b in blocuri:
            if a is b:
                continue
            assert not (a.lineno < b.lineno and b.end_lineno <= a.end_lineno), (
                "un bloc de conexiune il contine pe altul (liniile %d..%d si %d..%d) — exact "
                "regresia pe care P4 a prins-o" % (a.lineno, a.end_lineno, b.lineno, b.end_lineno))


def test_H_jobul_de_fundal_nu_mai_tine_conexiune_peste_rotatie():
    """`spv_refresh` cheama rotatia DIN AFARA oricarui bloc de conexiune."""
    arbore = ast.parse(io.open(os.path.join(RADACINA, "core", "spv_refresh.py"),
                               encoding="utf-8").read())
    parinte = {}
    for n in ast.walk(arbore):
        for c in ast.iter_child_nodes(n):
            parinte[c] = n
    apeluri = [n for n in ast.walk(arbore) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "reimprospateaza_token"]
    assert apeluri, "jobul nu mai cheama rotatia — reciteste proba"
    for n in apeluri:
        p = parinte.get(n)
        while p is not None:
            if isinstance(p, ast.With):
                for it in p.items:
                    e = it.context_expr
                    assert not (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                                and e.func.attr.startswith("get_conn")), (
                        "jobul tine o conexiune peste rotatie, linia %d" % n.lineno)
            p = parinte.get(p)
