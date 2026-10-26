# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 598] „La eșecul WhatsApp, mesajul îi cere contabilului să-și verifice numărul și arată termeni tehnici; trebuie spus
că WhatsApp nu e disponibil și notificările vin pe email.” Clasa (comanda 12.1, cum a definit-o sesiunea principală): TOATE mesajele de
eșec ale canalelor externe (WhatsApp, email, SPV) arătate contabilului — fără coduri / termeni tehnici, cu ce face aplicația în loc.

Ce era (22.10.2026, Meta: „Account not registered”): „Codul nu a putut pleca pe WhatsApp (Meta a refuzat cererea (HTTP 400, cod 133010):
…). Verifică numărul și încearcă din nou.” La fel, pe SPV: „exceptie upload: HTTPSConnectionPool(…)”, „403 fara drept SPV: 403 ANAF: …”
(„vezi mesajul” din detaliul facturii, răspunsul „Trimite în SPV”), „principalul Principal(kind='firm', id=3) nu are token SPV activ” /
„ANAF n-a răspuns la timp (ReadTimeout)” (citirea din SPV: „ANAF a răspuns: …”, Conectare SPV), „File is not a zip file” (Import manual XML).

Ce se păzește:
  1. WhatsApp: refuzul Meta -> textul pentru om (`MESAJ_WA_ESUAT`), detaliul în jurnal + alertă;
  2. SPV: `spv_conector.mesaj_pentru_contabil` pe fiecare fel de eșec, fără textul excepției; încărcarea facturii (`efactura_trimitere`)
     și citirea (`spv_receive`) scriu textul acesta pe ecran și în `error_message`;
  3. GARDA de clasă (AST, `core/` + `main.py`): într-un `except` care prinde o eroare a unui canal extern (WhatsApp, SPV, rețea) — sau
     orice eroare, în modulele canalelor — variabila excepției nu ajunge într-un refuz (`raise _erori.*` / `HTTPException`), într-o cheie
     `mesaj` / `eroare` / `error_message` / `raspuns`, într-un nume `eroare` / `errmsg` / `mesaj` sau într-un `return`; voie are numai
     prin traducătoare (`mesaj_pentru_contabil`) și spre jurnal (`print`, `esec_secundar`, `detaliu=`). LIMITĂ declarată: excepția
     transformată întâi în altă variabilă (`t = str(e)`, apoi `mesaj = t`) nu se urmărește.

Temei: N/A — textele aplicației (CLAUDE.md §9: „fără termeni de programator”), nu o regulă fiscală.
"""
import ast
import os
import re

import pytest
import requests

from core import spv_conector as C
from core import whatsapp as W
from core.test_notificari_canal import _D, _db_ok, baza  # noqa: F401 — fixture-ul `baza` (tranzacție anulată, `get_conn` falsificat)

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEHNIC = re.compile(r"HTTP|\b\d{3}\b|133010|Meta|Exception|Error|Timeout|Pool|Principal|token|state|zip file", re.I)


# Textul pentru om se citește pe BUCĂȚILE lui (propozițiile și membrii lor, întregi) și pe butoanele numite între ghilimele — nu prin
# „șirul apare undeva” (`core/test_garzi_pe_text.py`): aici chiar textul e lucrul verificat (598: ce i se spune contabilului).
def _bucati(text):
    return [b.strip() for b in re.split(r"[,;:]|\.(?=\s|$)", text) if b.strip()]


def _butoane(text):
    return set(re.findall(r"„([^”]+)”", text))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_598_esecul_whatsapp_spune_ca_notificarile_vin_pe_email(baza, monkeypatch):
    """MUTAȚIE: `MESAJ_WA_ESUAT` înapoi la „Codul nu a putut pleca pe WhatsApp (%s). Verifică numărul…” % e -> pică."""
    from core import erori, observare, uc_cont_notificari as U
    ctx = {"uid": baza["uid"]}
    jurnal = []
    monkeypatch.setenv("WHATSAPP_TOKEN", "t")
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, alerta=False: jurnal.append((et, str(e), alerta)))

    def refuz(tel, cod):
        raise W.Refuzat("Meta a refuzat cererea (HTTP 400, cod 133010): Account not registered")
    monkeypatch.setattr(W, "trimite_cod", refuz)
    U.telefon_seteaza(_D(telefon="0759 638 499"), ctx)
    with pytest.raises(erori.Conflict) as e:
        U.cere_cod(_D(acord=True), ctx)
    m = e.value.detaliu["mesaj"]
    assert m == U.MESAJ_WA_ESUAT, m
    assert set(_bucati(m)) >= {"WhatsApp nu e disponibil acum", "Notificările îți vin în continuare pe email"}, _bucati(m)
    assert "număr" not in m and not TEHNIC.search(m), m
    assert e.value.detaliu["cod"] == U.COD_WA_INDISPONIBIL
    # detaliul Meta ajunge la echipa iConta.eu (jurnal + alertă), nu la contabil
    assert jurnal == [("whatsapp: codul de confirmare", "Meta a refuzat cererea (HTTP 400, cod 133010): Account not registered", True)]
    # rețeaua căzută: același text
    monkeypatch.setattr(W, "trimite_cod", lambda tel, cod: (_ for _ in ()).throw(OSError("timed out")))
    monkeypatch.setattr(U, "PAUZA_COD_SEC", 0)
    with pytest.raises(erori.Conflict) as e:
        U.cere_cod(_D(acord=True), ctx)
    assert e.value.detaliu["mesaj"] == U.MESAJ_WA_ESUAT


def test_def_598_spv_fiecare_esec_are_textul_lui_fara_exceptie():
    ce = "Factura nu a plecat în SPV și rămâne netrimisă."
    cazuri = [
        (C.EroareSpvNeconectat("principalul Principal(kind='firm', id=3) nu are token SPV activ"), "nu e conectat la SPV"),
        (C.EroareSpvRefreshEsuat("refresh eșuat pentru token 12 — principalul reconecteaza SPV"), "a expirat"),
        (C.EroareSpvFaraDrept("403 ANAF: certificatul nu are drept (CIF/serviciu)"), "nu are drept"),
        (requests.exceptions.ReadTimeout("HTTPSConnectionPool(host='api.anaf.ro', port=443): Read timed out."), "ANAF nu a răspuns"),
        (requests.exceptions.ConnectionError("Max retries exceeded"), "ANAF nu a răspuns"),
        (C.EroareSpv("HTTP 500 la /token: <html>"), "eroare a aplicației"),
        (KeyError("access_token"), "eroare a aplicației"),
    ]
    for exc, asteptat in cazuri:
        m = C.mesaj_pentru_contabil(exc, ce)
        assert asteptat in m and ce in m, (exc, m)
        assert str(exc) not in m and not TEHNIC.search(m.replace("SPV", "")), (exc, m)


def test_def_598_motivul_aplicatiei_nu_se_citeaza_ca_raspuns_anaf():
    """Starea SPV a firmei (`spv_stare.js`) citează „a primit de la ANAF: …” numai pentru răspunsul ANAF; motivul aplicației îl spune ca
    atare (`stare_firma` -> `eroare_de_la_anaf`). MUTAȚIE: `e_motivul_aplicatiei` -> `False` -> pică."""
    from core.spv_receive import MESAJ_ANAF_FARA_RASPUNS, MESAJ_NECITITE
    for e in (C.EroareSpvNeconectat(), C.EroareSpvRefreshEsuat(), C.EroareSpvFaraDrept(), requests.exceptions.ReadTimeout(), KeyError()):
        assert C.e_motivul_aplicatiei(C.mesaj_pentru_contabil(e, MESAJ_NECITITE)), e
    assert C.e_motivul_aplicatiei(MESAJ_ANAF_FARA_RASPUNS) and C.e_motivul_aplicatiei(C.MESAJ_CITIRE_NECONECTAT)
    for anaf in ("Nu aveti drept in SPV pentru CIF=14399840", "CIF introdus nu este un numar", "Nu exista mesaje in ultimele 60 zile", "",
                 None):
        assert not C.e_motivul_aplicatiei(anaf), anaf


def test_def_598_incarcarea_in_spv_cazuta_scrie_textul_pentru_om(monkeypatch):
    """Încărcarea facturii: excepția conectorului nu mai ajunge în `error_message` / `raspuns` (ce arată „vezi mesajul” și răspunsul
    butonului „Trimite în SPV”); porțile 0–3 trec pe date simulate. MUTAȚIE: `mesaj = spv_conector.mesaj_pentru_contabil(e, ...)` ->
    `mesaj = "exceptie upload: %s" % e` -> pică."""
    import contextlib
    from core import efactura_trimitere as T
    from core import observare
    scrise = []

    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _Conn:
        def cursor(self, *a, **k):
            return _Cur()

    monkeypatch.setattr(T.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(observare, "esec_secundar", lambda *a, **k: None)
    monkeypatch.setattr(T, "refuz_din_efactura", lambda conn, schema, fid: None)
    monkeypatch.setattr(T.spv_conector, "ia_token_activ", lambda conn, p: {"id": 1})
    monkeypatch.setattr(T._repo, "cui_emitent", lambda cur, schema: ("14399840",))
    monkeypatch.setattr(T.spv_conector, "stare_firma", lambda conn, p, cif: {})
    monkeypatch.setattr(T, "incarca_factura", lambda conn, schema, fid: ({"tert_tara": "RO"}, [], {}, {}))
    monkeypatch.setattr(T, "completeaza_client_ro", lambda c: c)
    monkeypatch.setattr(T._ef, "genereaza_xml", lambda *a: "<Invoice/>")
    monkeypatch.setattr(T._ef, "valideaza", lambda xml: (True, []))
    monkeypatch.setattr(T._repo, "trimitere_in_curs", lambda *a: None)
    monkeypatch.setattr(T._repo, "trimitere_vie", lambda *a: None)
    monkeypatch.setattr(T._repo, "insereaza_trimitere_pregatita", lambda *a: (7,))
    monkeypatch.setattr(T._repo, "rezultatul_trimiterii", lambda cur, schema, stare, index, ex, errmsg, tid: scrise.append((stare, errmsg)))
    for exc in (requests.exceptions.ReadTimeout("HTTPSConnectionPool(host='api.anaf.ro'): Read timed out."),
                C.EroareSpvNeconectat("principalul Principal(kind='firm', id=3) nu are token SPV activ"),
                C.EroareSpvFaraDrept("403 ANAF: certificatul nu are drept (CIF/serviciu)")):
        def upload(*a, _e=exc, **k):
            raise _e
        monkeypatch.setattr(T._ef, "upload_ubl", upload)
        rez = T.trimite("tenant_x", 1, C.principal_firm(1), mediu="prod")
        stare, errmsg = scrise[-1]
        assert stare == "eroare_upload" == rez["stare"] and errmsg == rez["raspuns"], (stare, errmsg, rez)
        assert str(exc) not in errmsg and "exceptie" not in errmsg and "403" not in errmsg and "Principal(" not in errmsg, errmsg


# ── emailul (canalul email, aceeași clasă) ─────────────────────────────────────────────────────────────────────────────────────
def test_def_598_invitatia_asistentului_neplecata_nu_spune_trimisa(monkeypatch):
    """Invitația colegului: emailul n-a plecat -> ecranul nu mai spune „Invitație trimisă”, ci ce face administratorul. MUTAȚIE: ramura
    `email_trimis: False` scoasă (întoarce mereu `{"ok": True, "user_id": uid}`) -> pică."""
    import contextlib
    import types
    from core import nucleu, uc_asistenti as ua

    class _C:
        def cursor(self, **_k):
            return contextlib.nullcontext(types.SimpleNamespace(execute=lambda *a, **k: None))
    monkeypatch.setattr(ua.db, "get_conn", lambda schema=None: contextlib.nullcontext(_C()))
    monkeypatch.setattr(nucleu, "hash_parola", lambda p: "x")
    monkeypatch.setattr(ua.repo_utilizatori, "contul_dupa_email", lambda cur, e: None)
    monkeypatch.setattr(ua.repo_utilizatori, "creeaza_cont_asistent", lambda *a: {"id": 99})
    monkeypatch.setattr(ua._asist, "atribuie_firma", lambda conn, cab, uid, tid: {"ok": True})
    monkeypatch.setattr(ua._uc_comun, "_pune_token", lambda cur, tok, uid, ttl: None)
    from core import repo_cabinet
    monkeypatch.setattr(repo_cabinet, "nume_cabinet", lambda cur, firm_id: "Cabinet Probă")   # [lotul 13, 560] numele în email, fără bază
    monkeypatch.setattr(ua._obs, "trimite_email_html_sau_semnaleaza", lambda *a, **k: False)   # Brevo n-a primit cererea
    date = types.SimpleNamespace(email="zt.598@exemplu.ro", nume="ZT", poate_pregati=True, poate_valida=False, poate_depune=False,
                                 firme=[1])
    r = ua.asistent_creeaza(date, {"rol": "admin_firma", "firm": 7, "uid": 1})
    assert r == {"ok": True, "user_id": 99, "email_trimis": False, "mesaj": ua.MESAJ_INVITATIE_NETRIMISA % "zt.598@exemplu.ro"}, r
    assert set(_bucati(r["mesaj"])) >= {"dar emailul cu linkul de activare nu a plecat acum (serviciul de email nu a răspuns)",
                                        "primește pe email un link nou"}, _bucati(r["mesaj"])
    assert _butoane(r["mesaj"]) == {"Am uitat parola"} and not TEHNIC.search(r["mesaj"].replace(date.email, "")), r["mesaj"]


def test_def_598_raportul_lunar_neplecat_spune_ce_face_contabilul(monkeypatch):
    import contextlib
    from core import erori, uc_pachete as up
    monkeypatch.setattr(up._uc_comun, "_pachet_schema", lambda ctx, tid: "tenant_x")
    monkeypatch.setattr(up.db, "get_conn", lambda schema=None: contextlib.nullcontext(object()))
    monkeypatch.setattr(up._pachete, "semnatura_cabinet", lambda *a: None)
    monkeypatch.setattr(up._pachete, "pregateste", lambda *a, **k: {})
    monkeypatch.setattr(up._pachete, "trimite_pregatit", lambda p: {"ok": False, "cod": "EMAIL_ESUAT"})
    with pytest.raises(erori.CerereGresita) as e:
        up.pachet_trimite(1, 2026, 9, {"uid": 1, "firm": 1})
    m = e.value.detaliu
    assert isinstance(m, str), m
    assert set(_bucati(m)) >= {"Emailul cu raportul lunar nu a plecat acum", "Raportul rămâne aprobat"} and _butoane(m) == {"Trimite"}, m


# ── garda de clasă ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
EXT = {"Refuzat", "Neconfigurat", "RequestException", "URLError", "HTTPError", "Timeout", "ReadTimeout", "ConnectionError", "OSError"}
CANALE = {"whatsapp.py", "notificari.py", "uc_cont_notificari.py", "spv_conector.py", "spv_rute.py", "spv_receive.py", "spv_poll.py",
          "spv_refresh.py", "efactura_trimitere.py", "etransport_send.py", "efactura_send.py"}
CHEI = {"mesaj", "eroare", "error_message", "raspuns"}
NUME = {"eroare", "errmsg", "mesaj"}
#: pe unde excepția are voie să treacă: traducătoarele și jurnalul
VOIE = {"mesaj_pentru_contabil", "mesaj_indisponibil", "esec_secundar", "_semnaleaza", "print", "isinstance"}


def _nume_tip(t):
    return [n.id if isinstance(n, ast.Name) else n.attr for n in ast.walk(t) if isinstance(n, (ast.Name, ast.Attribute))]


def _prinde_canal(h, fis):
    if h.type is None:
        return fis in CANALE
    nn = _nume_tip(h.type)
    return any(x in EXT or x.startswith("EroareSpv") for x in nn) or (fis in CANALE and any(x in ("Exception", "BaseException") for x in nn))


def _foloseste(nod, var):
    """Variabila excepției apare în `nod`, în afara traducătoarelor / jurnalului / `detaliu=`."""
    if isinstance(nod, ast.Call):
        f = nod.func
        if (f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)) in VOIE:
            return False
        return any(_foloseste(a, var) for a in nod.args) or any(_foloseste(k.value, var) for k in nod.keywords if k.arg != "detaliu") \
            or _foloseste(f, var)
    if isinstance(nod, ast.Name):
        return nod.id == var
    return any(_foloseste(c, var) for c in ast.iter_child_nodes(nod))


def _spre_om(exc):
    f = exc.func if isinstance(exc, ast.Call) else exc
    s = ast.unparse(f)
    return "erori" in s or "HTTPException" in s


def scurgeri():
    out = []
    fis = ["main.py"] + ["core/" + f for f in sorted(os.listdir(os.path.join(RAD, "core"))) if f.endswith(".py") and not f.startswith("test_")]
    for rel in fis:
        b = os.path.basename(rel)
        for h in ast.walk(ast.parse(open(os.path.join(RAD, rel), encoding="utf-8").read())):
            if not (isinstance(h, ast.ExceptHandler) and h.name and _prinde_canal(h, b)):
                continue
            v = h.name
            for n in ast.walk(ast.Module(body=h.body, type_ignores=[])):
                if isinstance(n, ast.Raise) and n.exc is not None and _spre_om(n.exc) and _foloseste(n.exc, v):
                    out.append((rel, n.lineno, ast.unparse(n)))
                elif isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value in CHEI and _foloseste(x, v)
                                                      for k, x in zip(n.keys, n.values)):
                    out.append((rel, n.lineno, ast.unparse(n)))
                elif isinstance(n, ast.Assign) and _foloseste(n.value, v) and any(
                        isinstance(x, ast.Name) and x.id in NUME for t in n.targets for x in ast.walk(t)):
                    out.append((rel, n.lineno, ast.unparse(n)))
                elif isinstance(n, ast.Return) and n.value is not None and _foloseste(n.value, v):
                    out.append((rel, n.lineno, ast.unparse(n)))
    return out


def test_def_598_garda_nicio_exceptie_a_unui_canal_extern_nu_ajunge_pe_ecran():
    """MUTAȚIE: `mesaje, eroare = [], str(e)` pus înapoi în `spv_receive.citeste_firma` -> pică (locul numit)."""
    gasite = scurgeri()
    assert not gasite, "textul excepției unui canal extern ajunge la contabil:\n  " + "\n  ".join("%s:%d %s" % g for g in gasite)


def test_def_598_garda_vede_scurgerea_pe_o_proba_sintetica(tmp_path):
    """Anti-vacuu: aceeași garda, pe un modul sintetic cu cele patru forme ale scurgerii, le prinde pe toate."""
    (tmp_path / "core").mkdir()
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    (tmp_path / "core" / "spv_receive.py").write_text(
        "def a():\n    try:\n        x()\n    except EroareSpv as e:\n        raise _erori.Conflict(str(e))\n"
        "def b():\n    try:\n        x()\n    except Exception as e:\n        return {'mesaj': 'nu: %s' % e}\n"
        "def c():\n    try:\n        x()\n    except OSError as e:\n        eroare = str(e)\n"
        "def d():\n    try:\n        x()\n    except OSError as e:\n        print(e); eroare = mesaj_pentru_contabil(e, 'x')\n",
        encoding="utf-8")
    global RAD
    vechi, RAD = RAD, str(tmp_path)
    try:
        g = scurgeri()
    finally:
        RAD = vechi
    assert sorted({x[1] for x in g}) == [5, 10, 15], g


def test_simulatorul_meta_al_plasei_porneste_numai_cu_raspunsul_pregatit(tmp_path, monkeypatch):
    """Plasa e2e nu are tokenul și nu trimite nimic la Meta (`e2e_poarta.CHEI_TRIMITERE`); `whatsapp.CHEIE_SIMULAT` dă răspunsul Meta
    pregătit de test. Fără fișierul răspunsului, WhatsApp rămâne „neconfigurat” (testele 335 / 336 văd tot ce vedeau)."""
    monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
    monkeypatch.setenv(W.CHEIE_SIMULAT, str(tmp_path))
    assert not W.configurat()
    (tmp_path / "whatsapp.json").write_text('{"http": 400, "error": {"message": "Account not registered", "code": 133010}}',
                                            encoding="utf-8")
    assert W.configurat()
    with pytest.raises(W.Refuzat) as e:
        W.trimite_cod("+40700000000", "123456")
    assert str(e.value) == "Meta a refuzat cererea (HTTP 400, cod 133010): Account not registered"
