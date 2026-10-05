# -*- coding: utf-8 -*-
"""GARD — drepturile pe rol și bifă (decizia Costin 04.10.2026, „varianta 2”; DECIZII 04.10.2026).

Decizia, verbatim în DECIZII.md, mereu doar pe firmele alocate asistentului:
  „Poate pregăti” = munca curentă · „Poate valida” = validarea notelor și declarațiilor, înregistrarea
  amortizării, blocarea perioadei · „Poate depune” = depunerea la ANAF · doar administratorul = firme,
  asistenți, chei API, GDPR, abonament, datele cabinetului, deblocarea unei perioade închise.

CE FACE IMPOSIBIL
  1. o rută de SCRIERE pe o firmă (`{tenant_id}`) fără drept declarat — un CLIENT de portal le putea chema pe
     11 dintre ele (`cere_context`: facturi recurente, pontaj, model factură, respingerea unei facturi primite);
  2. mutarea tăcută a unei acțiuni pe alt nivel decât cel decis (pinii pe nume, cu decizia lângă);
  3. un asistent care trece garda fără bifă, pe o firmă nealocată, sau pe o acțiune a administratorului;
  4. o bifă citită din token (ar rămâne valabilă după retragere) — se probează schimbând bifa între două cereri;
  5. o derivare pentru interfață (`/eu/drepturi`) care diverge de gărzi.
"""
from __future__ import annotations

import ast
import contextlib
import io
import os

import pytest

from core import auth_api
from core import db as _db
from core import drepturi as D
from core import erori as _erori

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 1. regula pură ───────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("rol,bife,nivel,asteptat", [
    ("admin_firma", {}, D.ADMIN, True),        # decizia: administratorul face tot ce făcea (DECIZII, consecința 1)
    ("admin_firma", {}, D.VALIDA, True),
    ("superadmin", {}, D.ADMIN, True),
    ("angajat", {D.PREGATI: True, D.VALIDA: True, D.DEPUNE: True}, D.ADMIN, False),  # „Doar administratorul…”
    ("angajat", {}, D.PREGATI, False),         # fără bifă, nici munca curentă
    ("angajat", {D.PREGATI: True}, D.PREGATI, True),
    ("angajat", {D.PREGATI: True}, D.VALIDA, False),   # „Poate valida” e separat de pregătire
    ("angajat", {D.VALIDA: True}, D.VALIDA, True),
    ("angajat", {D.PREGATI: True, D.VALIDA: True}, D.DEPUNE, False),  # „Poate depune: depunerea la ANAF”
    ("angajat", {D.DEPUNE: True}, D.DEPUNE, True),
    ("angajat", {}, D.CITIRE, True),           # previzualizarea portalului nu schimbă nimic
    ("client", {D.PREGATI: True}, D.PREGATI, False),   # clientul are portalul, nu rutele de cabinet
    ("client", {}, D.CITIRE, False),
])
def test_regula_pura(rol, bife, nivel, asteptat):
    assert D.permis(rol, bife, nivel) is asteptat


def test_nivel_necunoscut_ridica():
    with pytest.raises(ValueError):
        D.permis("admin_firma", {}, "poate_orice")


# ── 2. gărzile rutelor, citite pe AST ────────────────────────────────────────────────────────────────
def _garzi():
    import sys
    sys.path.insert(0, os.path.join(RAD, "scripts"))
    import scan_drepturi_ui as s
    return s.garzi_din_main()


# Rute de scriere pe firmă care NU stau pe `cere_drept`, fiecare cu motivul. Lista nu poate crește tăcut.
_FARA_DREPT_PE_FIRMA = {
    ("POST", "/api/v1/firme/{tenant_id}/facturi"):
        "API-ul public pentru integrări: se autentifică prin CHEIA API a cabinetului (`cere_api_key`), nu prin "
        "sesiunea unui om — nu există rol sau bifă de citit; cheia o emite doar administratorul (ADMIN)",
}


def test_nicio_ruta_de_scriere_pe_firma_fara_drept():
    """Imposibilul 1: o rută care schimbă ceva pe o firmă declară dreptul. `cere_cabinet` / `cere_context` NU
    mai sunt destul pe o firmă: primul lasă orice asistent fără bifă, al doilea lasă și clientul de portal."""
    lipsa = sorted((m, c) for (m, c), g in _garzi().items()
                   if m != "GET" and {"{tenant_id}"} <= set(c.split("/")) and (not g or g[0] != "drept")
                   and (m, c) not in _FARA_DREPT_PE_FIRMA)
    assert not lipsa, "rute de scriere pe firmă fără `cere_drept` (%d): %s" % (len(lipsa), lipsa)


def test_exceptiile_au_motiv_si_exista():
    g = _garzi()
    for k, motiv in _FARA_DREPT_PE_FIRMA.items():
        assert k in g, "excepția %s nu mai e rută — scoate-o" % (k,)
        assert len(motiv) > 60, "excepția %s fără motiv scris" % (k,)


def test_ANTI_VACUU_gaseste_gardurile():
    niveluri = [g[1] for g in _garzi().values() if g and g[0] == "drept"]
    assert len(niveluri) >= 200, "detectorul vede doar %d rute pe drept — s-a stricat?" % len(niveluri)
    assert {"PREGATI", "VALIDA", "DEPUNE", "ADMIN", "CITIRE"} <= set(niveluri)


# Pinii deciziei: acțiunea -> nivelul, cu fragmentul de decizie care îl cere. O mutare cere schimbarea AICI,
# la vedere, cu decizia — nu se poate întâmpla din neatenție.
_PINI = {
    ("POST", "/tenants"): ("ADMIN", "„adăugare/import/scoatere firme”"),
    ("DELETE", "/tenants/{tenant_id}"): ("ADMIN", "„scoatere firme”"),
    ("POST", "/tenants/{tenant_id}/activare"): ("ADMIN", "„scoatere firme” (dezactivarea e scoaterea reversibilă)"),
    ("POST", "/migrare/importa"): ("ADMIN", "„import … firme”"),
    ("GET", "/firme-scoase"): ("ADMIN", "„scoatere firme” + „mereu doar pe firmele alocate”: istoricul e al întregului cabinet"),
    ("POST", "/asistenti"): ("ADMIN", "„asistenți și drepturile lor”"),
    ("POST", "/asistenti/{uid}/permisiuni"): ("ADMIN", "„asistenți și drepturile lor”"),
    ("POST", "/cabinet/api-chei"): ("ADMIN", "„chei API”"),
    ("POST", "/gdpr/cerere-stergere"): ("ADMIN", "„GDPR”"),
    ("POST", "/eu/cabinet"): ("ADMIN", "„datele cabinetului”"),
    ("DELETE", "/tenants/{tenant_id}/perioade-blocate"): ("ADMIN", "„deblocarea unei perioade închise”"),
    ("POST", "/tenants/{tenant_id}/perioade-blocate"): ("VALIDA", "„blocarea perioadei (închiderea lunii)”"),
    ("POST", "/tenants/{tenant_id}/jurnal/{nota_id}/valideaza"): ("VALIDA", "„validarea notelor contabile”"),
    ("POST", "/coada/{coada_id}/aproba"): ("VALIDA", "„validarea … declarațiilor”"),
    ("POST", "/tenants/{tenant_id}/amortizare"): ("VALIDA", "„înregistrarea amortizării”"),
    ("POST", "/coada/{coada_id}/depune"): ("DEPUNE", "„depunerea la ANAF”"),
    ("POST", "/tenants/{tenant_id}/facturi/emite"): ("PREGATI", "„emitere/storno facturi”"),
    ("POST", "/tenants/{tenant_id}/facturi/{factura_id}/storno"): ("PREGATI", "„emitere/storno facturi”"),
    ("POST", "/tenants/{tenant_id}/chitante"): ("PREGATI", "„chitanțe”"),
    ("POST", "/tenants/{tenant_id}/import-efactura"): ("PREGATI", "„importuri (… e-Factura …)”"),
    ("POST", "/tenants/{tenant_id}/solduri"): ("PREGATI", "„importuri (… Import date)”"),
    ("POST", "/tenants/{tenant_id}/jurnal"): ("PREGATI", "„note contabile în ciornă”"),
    # (pontajul nu se pinează pe cale aici: `scan_scrieri_declaratii` ar socoti ruta „probată” doar fiindcă e NUMITĂ într-un
    #  test — orbirea D3 din `core/test_rute_probate.py`; nivelul lui îl apără testul de mai jos pe toate rutele de firmă)
    ("POST", "/tenants/{tenant_id}/facturi/export-saga"): ("PREGATI", "„export SAGA/WinMentor”"),
    ("POST", "/tenants/{tenant_id}/etransport/trimite"): ("PREGATI", "„e-Transport”"),
    ("POST", "/coada"): ("PREGATI", "„pregătirea declarațiilor”"),
    # decizii mai vechi care rămân în vigoare (DECIZII 04.10.2026, consecințele 4)
    # R52 RĂSTURNAT (PIVOT DECIZII 04.10.2026, Costin): „Asistentul cu «Poate pregăti» vede, pe firmele alocate, PDF-ul
    # chitanței, fotografia bonului și fluturașul”. (REGES trimitere/răspunsuri -> DEPUNE: pinate în `scan_rol_pe_efect`,
    # nu aici — o cale de scriere numită într-un test ar trece drept „probată”, orbirea D3.)
    ("GET", "/tenants/{tenant_id}/fluturas/{salariat_id}"): ("PREGATI", "„vede … fluturașul” (R52 răsturnat)"),
    ("GET", "/tenants/{tenant_id}/chitante/{chitanta_id}/pdf"): ("PREGATI", "„vede … PDF-ul chitanței” (R52 răsturnat)"),
    ("GET", "/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}"): ("PREGATI", "„vede … fotografia bonului” (R52 răsturnat)"),
    ("PUT", "/tenants/{tenant_id}/woocommerce/config"): ("ADMIN", "R56: credențiale ale unui sistem extern"),
    ("POST", "/tenants/{tenant_id}/horeca/raport-z"): ("VALIDA", "R55: scrie notă `validata` direct"),
}


@pytest.mark.parametrize("cheie", sorted(_PINI))
def test_actiunea_sta_pe_nivelul_decis(cheie):
    nivel, temei = _PINI[cheie]
    g = _garzi().get(cheie)
    assert g == ("drept", nivel), "%s %s stă pe %s, decizia cere %s — %s" % (cheie[0], cheie[1], g, nivel, temei)


# REGES (PIVOT DECIZII 04.10.2026). Costin: „configurarea credențialelor doar la administrator; trimiterea și răspunsurile
# trec la «Poate depune» (depunere la o autoritate, ca la ANAF), pe firmele alocate.” Pinat pe NUMELE funcției rutei, nu pe
# cale: o cale de scriere numită într-un test ar trece drept „probată” (orbirea D3 din `core/test_rute_probate.py`).
_PINI_PE_FUNCTIE = {
    "reges_config": ("ADMIN", "„configurarea credențialelor doar la administrator”"),
    "reges_trimite_salariat": ("DEPUNE", "„trimiterea … trec la «Poate depune»”"),
    "reges_poll": ("DEPUNE", "„… și răspunsurile trec la «Poate depune»”"),
}


@pytest.mark.parametrize("functie", sorted(_PINI_PE_FUNCTIE))
def test_reges_sta_pe_nivelul_decis(functie):
    from core import scan_rol_pe_efect as _sre
    chei = [k for k, fn in _sre.rute().items() if fn.name == functie]
    assert len(chei) == 1, "ruta cu funcția %s: %s (trebuie exact una)" % (functie, chei)
    nivel, temei = _PINI_PE_FUNCTIE[functie]
    g = _garzi().get(chei[0])
    assert g == ("drept", nivel), "%s stă pe %s, decizia cere %s — %s" % (functie, g, nivel, temei)


# ── 3–5. proba pe aplicația vie (TestClient), cu actori sintetici, în ROLLBACK ────────────────────────
SCH = "ztest_drepturi_rol"


class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def cabinet(monkeypatch):
    """Un cabinet sintetic: administrator, asistent („Poate pregăti”, o firmă alocată din două) și un client
    de portal al firmei alocate. Totul într-o conexiune anulată la final (tabele partajate -> date sintetice)."""
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT DREPTURI ROL') RETURNING id")
            firm = cur.fetchone()[0]

            def _user(email, rol, preg=False, val=False, dep=False):
                cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,"
                            "activ,poate_pregati,poate_valida,poate_depune) VALUES (%s,'x','ZT','DR',%s,%s,true,%s,%s,%s) "
                            "RETURNING id", (email, rol, firm, preg, val, dep))
                return cur.fetchone()[0]
            uid_admin = _user("zt_dr_admin@invalid", "admin_firma", True, True, True)
            uid_asist = _user("zt_dr_asist@invalid", "angajat", True, False, False)
            uid_client = _user("zt_dr_client@invalid", "client")
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"),
                                                         encoding="utf-8").read(), SCH))
            # CUI-uri cu cifră de control verificată (CLAUDE.md): 14399840 e folosit de suita, 14837428 la fel
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT DR alocata','14399840',%s,true) RETURNING id", (SCH, firm))
            tid_alocat = cur.fetchone()[0]
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT DR nealocata','14837428',%s,true) RETURNING id", (SCH + "_b", firm))
            tid_strain = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s,%s),(%s,%s)",
                        (uid_asist, tid_alocat, uid_client, tid_alocat))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        tok = lambda uid, rol: auth_api.emite_token({"id": uid, "rol": rol, "accounting_firm_id": firm})
        yield {"conn": conn, "tid": tid_alocat, "tid_strain": tid_strain, "uid_asist": uid_asist,
               "admin": tok(uid_admin, "admin_firma"), "asist": tok(uid_asist, "angajat"),
               "client": tok(uid_client, "client")}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _cl():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(t):
    return {"Authorization": "Bearer " + t}


def _seteaza_bife(env, **bife):
    with env["conn"].cursor() as c:
        c.execute("SET search_path TO public")
        for k, v in bife.items():
            c.execute("UPDATE public.users SET %s = %%s WHERE id = %%s" % k, (v, env["uid_asist"]))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_asistentul_nu_adauga_firme_si_refuzul_e_in_termenii_contabilului(cabinet):
    """Comanda Costin pct.1+2: asistentul apasă „Adaugă firma” -> 403 cu mesajul care spune CINE o face."""
    r = _cl().post("/tenants", headers=_H(cabinet["asist"]), json={"nume": "ZT", "cui": "14399840"})
    assert r.status_code == 403, r.text
    assert r.json()["detail"] == D.MESAJ[D.ADMIN]   # mesajul care numește cine o face (core/drepturi.MESAJ)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_asistentul_nu_scoate_firme(cabinet):
    for metoda, cale in (("post", "/tenants/%d/activare"), ("delete", "/tenants/%d")):
        r = getattr(_cl(), metoda)(cale % cabinet["tid"], headers=_H(cabinet["asist"]))
        assert r.status_code == 403, (cale, r.status_code, r.text)
        assert r.json()["detail"] == D.MESAJ[D.ADMIN]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pregatirea_trece_validarea_nu(cabinet):
    """Pe firma alocată: munca curentă trece garda; validarea notei cere „Poate valida”."""
    cl = _cl()
    r = cl.post("/tenants/%d/facturi-recurente" % cabinet["tid"], headers=_H(cabinet["asist"]), json={})
    assert r.status_code not in (401, 403), "munca curentă refuzată unui asistent cu «Poate pregăti»: %s" % r.text
    r = cl.post("/tenants/%d/jurnal/1/valideaza" % cabinet["tid"], headers=_H(cabinet["asist"]))
    assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.VALIDA], r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_firma_nealocata_se_refuza_ca_inexistenta(cabinet):
    """„Mereu doar pe firmele alocate”: același răspuns ca pentru o firmă inexistentă (decizia Costin 03.09)."""
    r = _cl().post("/tenants/%d/facturi-recurente" % cabinet["tid_strain"], headers=_H(cabinet["asist"]), json={})
    assert r.status_code == 404, r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bifa_se_citeste_live_nu_din_token(cabinet):
    """Același token, bifa retrasă între două cereri -> a doua e refuzată."""
    cl = _cl()
    _seteaza_bife(cabinet, poate_pregati=False)
    r = cl.post("/tenants/%d/facturi-recurente" % cabinet["tid"], headers=_H(cabinet["asist"]), json={})
    assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.PREGATI], r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_clientul_de_portal_nu_mai_scrie_pe_rutele_de_cabinet(cabinet):
    """Gaura găsită pe drum: 11 rute de scriere pe firmă stăteau pe `cere_context`, iar clientul trecea prin
    `user_tenants`. Pe codul de dinainte, cererea de mai jos crea o factură recurentă din portal."""
    r = _cl().post("/tenants/%d/facturi-recurente" % cabinet["tid"], headers=_H(cabinet["client"]), json={})
    assert r.status_code == 403, r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_eu_drepturi_derivat_si_live(cabinet):
    cl = _cl()
    ia = lambda tok: set(cl.get("/eu/drepturi", headers=_H(tok)).json()["interzise"])
    adm, asi = ia(cabinet["admin"]), ia(cabinet["asist"])
    # operatori de mulțime (nu `in`): crapă dacă lista ar deveni vreodată un șir (vezi core/scan_garzi_pe_text)
    assert asi >= {"POST /tenants", "POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza", "POST /coada/{coada_id}/depune"}
    assert not (adm & {"POST /tenants"})
    assert not (asi & {"POST /tenants/{tenant_id}/facturi/emite"})
    _seteaza_bife(cabinet, poate_pregati=False, poate_valida=True)
    asi2 = ia(cabinet["asist"])
    assert asi2 >= {"POST /tenants/{tenant_id}/facturi/emite"}, "bifa retrasă nu se vede în listă"
    assert not (asi2 & {"POST /tenants/{tenant_id}/jurnal/{nota_id}/valideaza"})


def test_derivarea_vie_coincide_cu_citirea_statica():
    """Imposibilul 5: interfața (din `garzi_rute(app)`) și gardul static (AST) citesc aceleași niveluri."""
    import main
    vie = {(m, c): g[1] for m, c, g in D.garzi_rute(main.app) if g[0] == "drept"}
    stat = {k: g[1] for k, g in _garzi().items() if g and g[0] == "drept"}
    nume = {"PREGATI": D.PREGATI, "VALIDA": D.VALIDA, "DEPUNE": D.DEPUNE, "ADMIN": D.ADMIN, "CITIRE": D.CITIRE}
    stat = {k: nume[v] for k, v in stat.items()}
    assert vie == stat


def test_verifica_firma_INAINTE_de_bifa():
    """Ordinea din `verifica`: un asistent fără bifă, pe o firmă care nu e a lui, primește 404 (firma), nu 403
    (bifa) — altfel refuzul de bifă i-ar confirma că `tenant_id`-ul există."""
    src = io.open(os.path.join(RAD, "core", "drepturi.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "verifica")
    corp = ast.unparse(fn)
    assert corp.index("schema_tenant") < corp.index("bife_live")
    assert issubclass(_erori.Inexistent, _erori.EroareDeDomeniu)


# ── PIVOT DECIZII 04.10.2026 (răspunsurile lui Costin la confirmări): căile se iau din NUMELE funcției rutei, nu se scriu ──
def _cale(functie, **param):
    import main
    return main.app.url_path_for(functie, **{k: str(v) for k, v in param.items()})


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_r52_rasturnat_pregatirea_vede_documentele_de_tert(cabinet):
    """Costin: „Asistentul cu «Poate pregăti» vede, pe firmele alocate, PDF-ul chitanței, fotografia bonului și fluturașul.”
    Documentele cerute nu există (id-uri sintetice) — se probează GARDA: nu 401/403; fără bifă -> refuzul „Poate pregăti”."""
    cl, t = _cl(), cabinet["tid"]
    cai = [_cale("tenant_fluturas", tenant_id=t, salariat_id=999999), _cale("chitanta_pdf", tenant_id=t, chitanta_id=999999),
           _cale("cabinet_bon_imagine", tenant_id=t, bon_id=999999, n=0)]
    for c in cai:
        r = cl.get(c, params={"an": 2099, "luna": 1}, headers=_H(cabinet["asist"]))
        assert r.status_code not in (401, 403), "%s refuzat asistentului cu «Poate pregăti»: %s" % (c, r.text)
    _seteaza_bife(cabinet, poate_pregati=False)
    for c in cai:
        r = cl.get(c, params={"an": 2099, "luna": 1}, headers=_H(cabinet["asist"]))
        assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.PREGATI], (c, r.text)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reges_trimiterea_si_raspunsurile_cer_poate_depune_configurarea_administratorul(cabinet):
    """Costin: „REGES: configurarea credențialelor doar la administrator; trimiterea și răspunsurile trec la «Poate depune»”."""
    cl, t = _cl(), cabinet["tid"]
    poll, trimite, cfg = (_cale("reges_poll", tenant_id=t), _cale("reges_trimite_salariat", tenant_id=t),
                          _cale("reges_config", tenant_id=t))
    for c in (poll, trimite):
        r = cl.post(c, headers=_H(cabinet["asist"]), json={})
        assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.DEPUNE], (c, r.text)
    _seteaza_bife(cabinet, poate_depune=True)
    for c in (poll, trimite):
        r = cl.post(c, headers=_H(cabinet["asist"]), json={})
        assert r.status_code not in (401, 403), "%s refuzat asistentului cu «Poate depune»: %s" % (c, r.text)
    r = cl.post(cfg, headers=_H(cabinet["asist"]), json={"username": "x", "parola": "y", "mediu": "test"})
    assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.ADMIN], r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_regimul_tva_schimbat_de_asistent_se_jurnalizeaza_cu_el(cabinet, monkeypatch):
    """Costin: „Regimul de TVA la «Poate pregăti»: confirmat, cu jurnalizarea fiecărei schimbări (utilizator, dată, vechi →
    nou)”. Pe ruta vie: asistentul schimbă regimul -> un rând cu ID-ul LUI (din token), nu al altcuiva și nu gol."""
    from core import uc_comun
    monkeypatch.setattr(uc_comun, "_anaf_tva_check", lambda cui, v: (None, None, None))   # fără apel la ANAF din test
    with cabinet["conn"].cursor() as c:
        c.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva) VALUES (1,'ZT','14399840',false)" % SCH)
    r = _cl().post(_cale("firma_profil_regim_tva", tenant_id=cabinet["tid"]), headers=_H(cabinet["asist"]),
                   json={"platitor_tva": True})
    assert r.status_code == 200, r.text
    with cabinet["conn"].cursor() as c:
        c.execute("SELECT camp, valoare_veche, valoare_noua, user_id FROM %s.firma_profil_jurnal ORDER BY id" % SCH)
        assert c.fetchall() == [("platitor_tva", "false", "true", cabinet["uid_asist"])]


# ── comanda Costin 05.10.2026 (testarea ca asistent, 2): povestea lunii, motivul acțiunilor ascunse, administratorul ─────────
# Pct.2: „generarea, editarea și ciorna rămân la «Poate pregăti»; «Aprobă» și «Trimite» cer «Poate valida» (textul pleacă la
# client în numele cabinetului)”. Pinat pe NUMELE funcției (căile de scriere numite într-un test ar trece drept „probate”, D3).
_PINI_POVESTE = {
    "pachet_genereaza": ("PREGATI", "„generarea … rămân la «Poate pregăti»”"),
    "pachet_poveste_set": ("PREGATI", "„editarea și ciorna rămân la «Poate pregăti»”"),
    "pachet_poveste_aproba": ("VALIDA", "„«Aprobă» … cer «Poate valida»”"),
    "pachet_trimite": ("VALIDA", "„… și «Trimite» cer «Poate valida»”"),
}


@pytest.mark.parametrize("functie", sorted(_PINI_POVESTE))
def test_povestea_sta_pe_nivelul_decis(functie):
    from core import scan_rol_pe_efect as _sre
    chei = [k for k, fn in _sre.rute().items() if fn.name == functie]
    assert len(chei) == 1, "ruta cu funcția %s: %s" % (functie, chei)
    nivel, temei = _PINI_POVESTE[functie]
    assert _garzi().get(chei[0]) == ("drept", nivel), "%s stă pe %s, decizia cere %s — %s" % (
        functie, _garzi().get(chei[0]), nivel, temei)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_aprobarea_si_trimiterea_povestii_cer_poate_valida(cabinet):
    """Asistentul cu „Poate pregăti”: ciorna trece garda; `status=aprobat` pe ruta de ciornă -> refuz numit (altfel aprobarea
    ar fi trecut pe pregătire); ruta de aprobare și trimiterea -> refuzul „Poate valida”. Cu „Poate valida” trec garda."""
    from core import uc_pachete
    cl, t, q = _cl(), cabinet["tid"], {"an": 2099, "luna": 1}
    r = cl.post(_cale("pachet_poveste_set", tenant_id=t), params=q, headers=_H(cabinet["asist"]),
                json={"text": "ZT", "status": "aprobat"})
    assert r.status_code == 400 and r.json()["detail"] == uc_pachete.MESAJ_APROBARE_PE_RUTA_EI, r.text
    for f in ("pachet_poveste_aproba", "pachet_trimite"):
        r = cl.post(_cale(f, tenant_id=t), params=q, headers=_H(cabinet["asist"]), json={"text": "ZT"})
        assert r.status_code == 403 and r.json()["detail"] == D.MESAJ[D.VALIDA], (f, r.text)
    _seteaza_bife(cabinet, poate_valida=True)
    r = cl.post(_cale("pachet_poveste_aproba", tenant_id=t), params=q, headers=_H(cabinet["asist"]), json={"text": "ZT"})
    assert r.status_code not in (401, 403), r.text


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_eu_drepturi_spune_si_de_ce(cabinet):
    """Pct.3: interfața arată motivul acțiunilor ascunse — nivelul vine de la server, cu numele de pe ecranul Asistenți."""
    import main
    d = _cl().get("/eu/drepturi", headers=_H(cabinet["asist"])).json()
    cale = [r.path for r in main.app.routes if getattr(r, "name", "") == "pachet_poveste_aproba"][0]
    assert d["motive"]["POST " + cale] == D.VALIDA
    assert d["motive"]["POST /tenants"] == D.ADMIN
    assert d["nume_niveluri"] == {D.PREGATI: "Poate pregăti", D.VALIDA: "Poate valida", D.DEPUNE: "Poate depune"}
    assert set(d["motive"]) == set(d["interzise"]), "fiecare acțiune refuzată are motivul ei"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bifele_administratorului_nu_se_schimba(cabinet):
    """Pct.4: administratorul are toate drepturile (B3). Pe producție, contabil.b ajunsese cu „Poate valida” scos prin ecran —
    afișat fără drept, deși garda îl lasă, și nenumărat printre validatori."""
    from core.mesaje import MESAJ_COD
    with cabinet["conn"].cursor() as c:
        c.execute("SET search_path TO public")
        c.execute("SELECT id FROM public.users WHERE email='zt_dr_admin@invalid'")
        uid_admin = c.fetchone()[0]
    r = _cl().post(_cale("asistenti_permisiuni", uid=uid_admin), headers=_H(cabinet["admin"]),
                   json={"poate_pregati": True, "poate_valida": False, "poate_depune": True})
    assert r.status_code == 400 and r.json()["detail"] == MESAJ_COD["ADMIN_TOATE_DREPTURILE"], r.text
    r = _cl().post(_cale("asistenti_permisiuni", uid=cabinet["uid_asist"]), headers=_H(cabinet["admin"]),
                   json={"poate_pregati": True, "poate_valida": True, "poate_depune": False})
    assert r.status_code == 200, "bifele unui asistent trebuie să se poată schimba în continuare: %s" % r.text
