# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.3 pct.1 — deficiența 460 (verbatim): „cursul BNR nu s-a mai actualizat din 19.10; factura din 22.10 propune
cursul de pe 19.10. Repară preluarea, completează zilele lipsă și pune alertă când cursul zilei lipsește.”

CAUZA (producție, numai citire, 22.10.2026): preluarea se făcea NUMAI la cerere (`uc_curs_bnr.asigura_cursul`, chemat de emitere /
previzualizare), iar cererea se oprea dacă cache-ul avea ORICE curs din pragul de vechime (5 zile): pe 22.10 cache-ul avea 19.10 (vechime 3),
deci nu se mai descărca nimic, iar factura din 22.10 primea cursul din 19.10 — deși BNR comunicase 20.10 și 21.10 (verificat cu `curl` de pe
server: `nbrfxrates10days.xml` 200, cu 21.10 și 20.10). Aceeași cauză a lăsat golul 07.09–05.10 (21 de zile bancare) în `public.curs_bnr_zilnic`.

Temei (verbatim, `anaf_surse/`):
  CF art.290 alin.(2): „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...] valabil la
  data la care intervine exigibilitatea taxei pentru operațiunea în cauză”.
  HG 1/2016 pct.35 alin.(1): „prin ultimul curs de schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de
  respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se vor desfășura în ziua următoare.”
  HG 1/2016 pct.35 alin.(2): cursul folosit la emiterea facturii „va rămâne neschimbat la data definitivării operațiunii”.
  OMFP 1802/2014 pct.325 alin.(2) lit.b: „cursul de schimb [...] comunicat de Banca Națională a României, din ultima zi bancară a lunii”.

Zilele de test sunt SINTETICE (2099; `public.curs_bnr_zilnic` e partajat). Descărcarea (`curs_bnr._descarca`) se înlocuiește cu o arhivă
construită aici — fără rețea. Rândurile 2099 scrise (cu conexiunea proprie a cache-ului, care comite) se șterg la final.
"""
import datetime as _dt
import re
from decimal import Decimal as D

import pytest

from core import curs_bnr as cb
from core import scadente as sc

Z = _dt.date


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ── pur ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ziua_bancara_asteptata_e_ultima_zi_lucratoare_dinaintea_operatiunii():
    # HG 1/2016 pct.35 alin.(1): „comunicat de respectiva bancă în ziua anterioară” — factura din joi 22.10.2026 -> cursul de miercuri 21.10
    assert cb.ziua_bancara_asteptata(Z(2026, 10, 22)) == Z(2026, 10, 21)
    # luni 26.10.2026 -> vineri 23.10 (sâmbăta și duminica BNR nu comunică)
    assert cb.ziua_bancara_asteptata(Z(2026, 10, 26)) == Z(2026, 10, 23)
    # miercuri 02.12.2026: 01.12 și 30.11 sunt sărbători legale (art.139 Codul muncii), 28–29.11 weekend -> vineri 27.11
    assert cb.ziua_bancara_asteptata(Z(2026, 12, 2)) == Z(2026, 11, 27)
    # OMFP 1802/2014 pct.325 alin.(2) lit.b: „din ultima zi bancară a lunii” — 31.10.2026 e sâmbătă -> vineri 30.10
    assert cb.ziua_bancara_asteptata(Z(2026, 10, 31), cb.REGULA_SFARSIT_LUNA) == Z(2026, 10, 30)
    assert cb.ziua_bancara_asteptata(Z(2026, 10, 30), cb.REGULA_SFARSIT_LUNA) == Z(2026, 10, 30)
    # un an în afara calendarului de sărbători: nu se poate ști (apelanții cad pe pragul de vechime, ca înainte)
    assert cb.ziua_bancara_asteptata(Z(2020, 3, 4)) is None


def test_cursul_zilei_lipsa_spune_ce_lipseste_si_ce_se_foloseste():
    # factura din 22.10.2026 cu cursul din 19.10 (cazul raportat): lipsește cel comunicat pe 21.10
    r = cb.cursul_zilei_lipsa(Z(2026, 10, 22), Z(2026, 10, 19), azi=Z(2026, 10, 22))
    assert r["asteptat"] == "2026-10-21" and r["folosit"] == "2026-10-19", r
    # mesajul întreg (câmpul citit de ecran): ce zi lipsește, de ce (preluarea n-a reușit, nu „încă necomunicat”) și ce curs se folosește
    assert r["mesaj"] == ("Cursul BNR comunicat pe 21.10.2026 (ultimul înaintea datei facturii, 22.10.2026) lipsește din aplicație: preluarea "
                          "lui de la BNR n-a reușit încă; aplicația reîncearcă singură. Până atunci se folosește cursul din 19.10.2026, iar "
                          "factura emisă acum îl păstrează (se fixează la emitere)."), r["mesaj"]
    # cursul corect nu e o lipsă: F1A12 din 20.10.2026 (producție) cu cursul comunicat pe 19.10 (CF art.290 alin.(2) + pct.35 alin.(1))
    assert cb.cursul_zilei_lipsa(Z(2026, 10, 20), Z(2026, 10, 19)) is None
    assert cb.cursul_zilei_lipsa(Z(2026, 10, 22), Z(2026, 10, 21)) is None
    # o factură datată mâine: cursul de azi încă nu e comunicat — se spune asta, nu „n-a reușit”
    r = cb.cursul_zilei_lipsa(Z(2026, 10, 23), Z(2026, 10, 21), azi=Z(2026, 10, 22))
    assert r["asteptat"] == "2026-10-22" and r["mesaj"] == (
        "Cursul BNR comunicat pe 22.10.2026 (ultimul înaintea datei facturii, 23.10.2026) lipsește din aplicație: BNR îl comunică abia azi. "
        "Până atunci se folosește cursul din 21.10.2026, iar factura emisă acum îl păstrează (se fixează la emitere)."), r


# ── cu baza de test ────────────────────────────────────────────────────────────────────────────────────────────────────────────
AN = 2099
INTERVAL = (Z(AN, 1, 1), Z(AN, 6, 30))


def _lucratoare(de_la, pana_la):
    d, out = de_la, []
    while d <= pana_la:
        if sc.e_zi_lucratoare(d):
            out.append(d)
        d += _dt.timedelta(days=1)
    return out


def _curs(d):
    """Un curs sintetic diferit pe fiecare zi, ca să se vadă ce zi s-a ales."""
    return (D("4.0000") + D(d.timetuple().tm_yday) / D("10000")).quantize(D("0.0001"))


def _xml(zile):
    cuburi = "".join('<Cube date="%s"><Rate currency="EUR">%s</Rate><Rate currency="HUF" multiplier="100">1.4719</Rate></Cube>'
                     % (d.isoformat(), _curs(d)) for d in zile)
    return ('<?xml version="1.0" encoding="utf-8"?><DataSet xmlns="https://www.bnr.ro/xsd"><Header><Publisher>National Bank of Romania'
            '</Publisher></Header><Body><Subject>Reference rates</Subject><OrigCurrency>RON</OrigCurrency>%s</Body></DataSet>' % cuburi)


def _sql(q, args=()):
    from core import db
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


@pytest.fixture()
def cache_2099(monkeypatch):
    """Cache-ul 2099: zilele lucrătoare din `zile` scrise (comise, ca de `_salveaza_cache`), descărcarea înlocuită cu arhiva `arhiva`
    (setată de test), rezervarea completării liberă. La final: rândurile 2099 și rezervarea, șterse."""
    from core import uc_curs_bnr as uc
    stare = {"arhiva": [], "descarcari": [], "eroare": None}

    def _descarca(url):
        stare["descarcari"].append(url)
        if stare["eroare"]:
            raise stare["eroare"]
        return _xml(stare["arhiva"])
    monkeypatch.setattr(cb, "_descarca", _descarca)
    monkeypatch.setattr(uc, "_azi", lambda: Z(AN, 6, 30))     # „azi” în anul sintetic: completarea nu caută după azi

    def scrie(zile):
        uc._salveaza_cache({d: {"EUR": _curs(d)} for d in zile})
    curata = lambda: (_sql("DELETE FROM public.curs_bnr_zilnic WHERE data BETWEEN %s AND %s", INTERVAL),  # noqa: E731
                      _sql("DELETE FROM public.alerte_cooldown WHERE categorie = %s", (uc.CATEGORIE_COMPLETARE,)))
    curata()
    stare["scrie"] = scrie
    yield stare
    curata()


@DB
def test_def_460_factura_din_prag_primeste_ultimul_curs_comunicat_nu_unul_mai_vechi(cache_2099):
    """Cazul raportat, pe zile 2099: cache-ul are cursuri până vineri 27.03.2099, BNR a comunicat și 30.03, 31.03; factura din miercuri
    01.04.2099. Codul vechi: cursul din 27.03 (vechime 5 <= prag 5 -> nicio descărcare). Acum: golul se umple, cursul e cel din 31.03.
    MUTAȚIE: în `asigura_cursul`, `completeaza(asteptata)` scos -> (cursul din 27.03) -> pică."""
    from core import db, uc_curs_bnr as uc
    assert [sc.e_zi_lucratoare(d) for d in (Z(AN, 3, 27), Z(AN, 3, 30), Z(AN, 3, 31), Z(AN, 4, 1))] == [True] * 4
    cache_2099["scrie"](_lucratoare(Z(AN, 1, 1), Z(AN, 3, 27)))
    cache_2099["arhiva"] = _lucratoare(Z(AN, 1, 1), Z(AN, 4, 1))
    uc.asigura_cursul("EUR", Z(AN, 4, 1))
    with db.get_conn() as conn:
        # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): „comunicat de respectiva bancă în ziua anterioară” -> 31.03.2099
        assert cb.curs_pentru(conn, "EUR", Z(AN, 4, 1)) == (_curs(Z(AN, 3, 31)), Z(AN, 3, 31), "bnr")
    assert cache_2099["descarcari"] == [cb.URL_AN.format(an=AN)], cache_2099["descarcari"]


@DB
def test_def_460_golurile_anului_se_umplu_din_arhiva_idempotent(cache_2099):
    """„completează zilele lipsă”: un gol în mijlocul anului (ca 07.09–05.10.2026 pe producție) și ultimele zile se umplu dintr-o singură
    descărcare a arhivei anuale; a doua chemare nu mai descarcă nimic. MUTAȚIE: `_salveaza_cache(harta)` scos din `completeaza` -> pică."""
    from core import uc_curs_bnr as uc
    toate = _lucratoare(Z(AN, 1, 1), Z(AN, 4, 30))
    gol = [d for d in toate if Z(AN, 2, 9) <= d <= Z(AN, 2, 20)] + toate[-2:]
    cache_2099["scrie"]([d for d in toate if d not in gol])
    cache_2099["arhiva"] = toate
    r = uc.completeaza(toate[-1])
    assert r["lipsa_inainte"] == [d.isoformat() for d in gol] and r["adus"] == len(gol) and r["lipsa"] == [], r
    assert r["descarcat"] is True and len(cache_2099["descarcari"]) == 1
    zile = {x[0] for x in _sql("SELECT data FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data BETWEEN %s AND %s", INTERVAL)}
    assert set(toate) <= zile
    # idempotent: nimic lipsă -> nicio descărcare, nicio scriere
    r2 = uc.completeaza(toate[-1])
    assert r2["lipsa_inainte"] == [] and r2["descarcat"] is False and len(cache_2099["descarcari"]) == 1, r2
    # valorile adevărate, cu multiplicatorul (HUF la 100): arhiva le dă, cache-ul le păstrează
    assert _sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data = %s", (gol[0],))[0][0] == _curs(gol[0])


@DB
def test_def_460_completarea_e_rezervata_si_nu_ridica_la_bnr_cazut(cache_2099):
    """BNR nu răspunde: completarea spune ce lipsește, nu ridică; a doua încercare din fereastra de 10 minute nu mai descarcă (BNR
    blochează IP-urile cu trafic repetat). MUTAȚIE: `rezerva_alerta(...)` -> `True` -> a doua încercare descarcă din nou -> pică."""
    from core import uc_curs_bnr as uc
    toate = _lucratoare(Z(AN, 1, 1), Z(AN, 3, 31))
    cache_2099["scrie"](toate[:-1])
    cache_2099["eroare"] = OSError("BNR: timeout")
    r = uc.completeaza(toate[-1])
    assert r["descarcat"] is False and r["lipsa"] == [toate[-1].isoformat()] and len(cache_2099["descarcari"]) == 1, r
    r2 = uc.completeaza(toate[-1])
    assert r2["amanat"] is True and len(cache_2099["descarcari"]) == 1, r2


@DB
def test_def_460_starea_cursului_zilei_pentru_sanatate(cache_2099):
    """Administratorul platformei: `stare_curs_zilei` spune dacă lipsește cursul de care au nevoie operațiunile zilei și golurile anului.
    MUTAȚIE: `"lipsa": ... ultima < asteptata` -> `False` -> pică."""
    from core import db
    toate = _lucratoare(Z(AN, 1, 1), Z(AN, 3, 31))
    cache_2099["scrie"](toate[:-1])
    with db.get_conn() as conn:
        st = cb.stare_curs_zilei(conn, Z(AN, 4, 1))
    assert st == {"asteptat": "2099-03-31", "ultima_zi": toate[-2].isoformat(), "lipsa": True, "zile_lipsa": ["2099-03-31"]}, st
    cache_2099["scrie"](toate[-1:])
    with db.get_conn() as conn:
        st = cb.stare_curs_zilei(conn, Z(AN, 4, 1))
    assert st["lipsa"] is False and st["zile_lipsa"] == [], st


@DB
def test_def_460_bucla_de_sanatate_completeaza_si_alerteaza(cache_2099, monkeypatch):
    """Preluarea nu mai așteaptă o factură: `main._verifica_curs_bnr` (bucla de sănătate) cheamă completarea, apoi spune dacă tot lipsește
    cursul zilei; rândul de alertă are acțiunea lui (`alerta_load.ACTIUNI["curs_bnr"]`). MUTAȚIE: `_uc_cb_s.completeaza()` scos ->
    golul rămâne -> pică."""
    import main
    from core import alerta_load as al
    toate = _lucratoare(Z(AN, 1, 1), Z(AN, 3, 31))
    cache_2099["scrie"](toate[:-1])
    cache_2099["arhiva"] = toate
    monkeypatch.setattr(cb, "ziua_bancara_asteptata", lambda zi, regula=cb.REGULA_OPERATIUNE, _f=cb.ziua_bancara_asteptata:
                        _f(Z(AN, 4, 1), regula))   # „azi” = 01.04.2099
    _st = cb.stare_curs_zilei
    monkeypatch.setattr(cb, "stare_curs_zilei", lambda conn, azi=None: _st(conn, Z(AN, 4, 1)))
    assert main._verifica_curs_bnr() is None                       # golul s-a umplut în ciclu: nimic de alertat
    assert len(cache_2099["descarcari"]) == 1
    _sql("DELETE FROM public.curs_bnr_zilnic WHERE data = %s", (toate[-1],))
    cache_2099["eroare"] = OSError("BNR: timeout")
    _sql("DELETE FROM public.alerte_cooldown WHERE categorie = 'bnr_completare'")
    msg = main._verifica_curs_bnr()
    # constatarea întreagă: ziua care lipsește după completarea eșuată și ultima zi din aplicație
    assert msg == ("Cursul BNR comunicat pe 2099-03-31 (de care au nevoie facturile în valută de azi) lipsește din aplicație; ultimul curs "
                   "din aplicație e din %s" % toate[-2].isoformat()), msg
    # rândul de alertă poartă acțiunea categoriei, iar acțiunea numește arhiva BNR (gazda URL-ului, citită ca URL, nu ca sub-șir)
    import urllib.parse
    assert al.rand("curs_bnr", msg) == "%s — Ce faci: %s." % (msg, al.ACTIUNI["curs_bnr"])
    url = re.findall(r"https?://\S+", al.ACTIUNI["curs_bnr"])
    assert [urllib.parse.urlsplit(u).hostname for u in url] == ["curs.bnr.ro"], url


@DB
def test_def_460_previzualizarea_spune_ca_lipseste_cursul_zilei(monkeypatch):
    """Contabilul care emite în valută vede, sub curs, că lipsește cel comunicat înaintea datei facturii și ce se folosește
    (`facturi/previzualizare-lei` -> `curs_zilei_lipsa`). MUTAȚIE: adăugarea `out["curs_zilei_lipsa"]` scoasă -> pică."""
    import contextlib
    from core import facturi_api, uc_comun, uc_tenants
    monkeypatch.setattr(uc_comun, "_preincalzeste_cursul", lambda *a: None)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, t: "tenant_x")
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(None))
    monkeypatch.setattr(facturi_api, "previzualizare_lei", lambda conn, m, d, l: {"ok": True, "moneda": m, "curs": "4.9800",
                                                                                   "data_curs": "2099-03-27", "sursa": "bnr"})
    r = uc_tenants.facturi_previzualizare_lei(1, {"moneda": "EUR", "data_emitere": "2099-04-01"}, {})
    assert r["curs_zilei_lipsa"]["asteptat"] == "2099-03-31" and r["curs_zilei_lipsa"]["folosit"] == "2099-03-27", r
    monkeypatch.setattr(facturi_api, "previzualizare_lei", lambda conn, m, d, l: {"ok": True, "moneda": m, "curs": "4.9800",
                                                                                   "data_curs": "2099-03-31", "sursa": "bnr"})
    assert uc_tenants.facturi_previzualizare_lei(1, {"moneda": "EUR", "data_emitere": "2099-04-01"}, {})["curs_zilei_lipsa"] is None


def test_garda_prospetimea_nu_opreste_preluarea_fara_ziua_asteptata():
    """Gardă: în `asigura_cursul`, ramura „cursul e în prag” nu se mai poate întoarce fără să compare cu ziua bancară așteptată și fără
    completare — exact forma care a oprit preluarea din 19.10. Pe AST. MUTAȚIE: ramura redusă la `return` -> pică."""
    import ast
    import inspect
    from core import uc_curs_bnr as uc
    fn = ast.parse(inspect.getsource(uc.asigura_cursul)).body[0]
    def _nume(n):
        return n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else None

    # ramurile pragului = `if`-urile al căror test folosește NUMELE `prag_zile` (nod Name / Attribute, nu textul testului)
    ramuri = [n for n in ast.walk(fn) if isinstance(n, ast.If) and {_nume(x) for x in ast.walk(n.test)} >= {"prag_zile"}]
    assert ramuri, "ramura pragului nu mai există — garda trebuie refăcută pe noua formă"
    # fiecare ramură cheamă (nod Call) și ziua bancară așteptată, și completarea — lista întreagă, ca să nu treacă pe zero ramuri
    apeluri = [{_nume(x.func) for c in r.body for x in ast.walk(c) if isinstance(x, ast.Call)} >= {"ziua_bancara_asteptata", "completeaza"}
               for r in ramuri]
    assert apeluri == [True] * len(ramuri), [ast.unparse(r) for r in ramuri]


@DB
def test_def_460_completarea_nu_cauta_dupa_azi(cache_2099, monkeypatch):
    """O factură datată în viitor nu cere arhivei BNR o zi care n-a venit: `pana_la` se reduce la azi. MUTAȚIE: reducerea scoasă ->
    golul „viitor” rămâne -> pică."""
    from core import uc_curs_bnr as uc
    toate = _lucratoare(Z(AN, 1, 1), Z(AN, 3, 31))
    cache_2099["scrie"](toate)
    cache_2099["arhiva"] = toate
    monkeypatch.setattr(uc, "_azi", lambda: Z(AN, 3, 31))
    r = uc.completeaza(Z(AN, 4, 3))
    assert r["pana_la"] == "2099-03-31" and r["lipsa_inainte"] == [] and cache_2099["descarcari"] == [], r
