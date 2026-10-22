# -*- coding: utf-8 -*-
"""459 (comanda Costin 11.3 pct.5, verbatim în DECIZII „Comanda 11.3”): „un CUI cu cifra de control greșită e acceptat la adăugarea
firmei; la schimbarea CUI-ului rămân datele celui vechi.”

(1) Pe TOATE drumurile care creează o firmă (ecranul „Adaugă firmă” prin `GET /public/verifica-cui` + `POST /tenants`, `provision_tenant`,
importul din Migrare cabinet, înregistrarea), un CUI care nu e valabil e refuzat ÎNAINTE de orice scriere, cu motivul, din aceeași funcție
(`tenant_provisioning.motiv_cui_firma_invalid`). (2) La corectura CUI-ului (Date firmă -> „Corectează CUI-ul”), ce venise de la ANAF pentru
CUI-ul vechi se înlocuiește cu datele ANAF ale CUI-ului nou, propuse câmp cu câmp în avertisment (ca la 444: „se spune și se propune
actualizarea”); fără date ANAF se spune ce rămâne de verificat, iar instantaneele ANAF ale CUI-ului vechi se uită.

Temeiul verificării: algoritmul cifrei de control a CUI (CLAUDE.md „Date de test — CUI/CNP”; cheia 753217532, suma × 10 mod 11, 10 -> 0),
verificat contra validatorului DUK în `core/identitate.py` (301111003 valid / 301111004 invalid). Regula „nimic din CUI-ul vechi tacit” e
de produs (comanda 11.3), nu fiscală.

CUI-urile de test: 459000010, 459000029, 459000037 au cifra de control calculată cu algoritmul (asertat în `_cui_ctrl`); 459000011 e
459000010 cu ultima cifră schimbată (control greșit). Datele de pornire în bază: un cabinet și un utilizator sintetici, în tranzacție
întoarsă (ROLLBACK) — nimic nu rămâne."""
import io
import os
import re
import types

import pytest

from core import db as _db
from core import tenant_provisioning as tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cui_ctrl(baza):
    """CUI din bază + cifra de control (algoritmul din CLAUDE.md „Date de test”)."""
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(baza).rjust(9, "0")
    r = (sum(int(c[i]) * ch[i] for i in range(9)) * 10) % 11
    return str(baza) + str(0 if r == 10 else r)


A, B, C = _cui_ctrl(45900001), _cui_ctrl(45900002), _cui_ctrl(45900003)
GRESIT = A[:-1] + str((int(A[-1]) + 1) % 10)
assert (A, B, C, GRESIT) == ("459000010", "459000029", "459000037", "459000011")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_cu_db = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ── (1) verificarea unică — pură ─────────────────────────────────────────────────────────────────────────────────
def test_459_verificarea_cui_de_firma_refuza_tot_ce_nu_e_un_cui_valabil():
    """MUTAȚIE: `if not c.isdigit(): return …` scos -> „RO-459000010” / „45900001A0” trec (cifrele lor au control corect) -> pică."""
    for bun in (A, "RO" + A, " ro " + A + " ", B):
        assert tp.motiv_cui_firma_invalid(bun) is None, bun
    assert tp.motiv_cui_firma_invalid(GRESIT) == tp.MESAJ_CUI_CONTROL % GRESIT   # cifra de control (algoritmul oficial)
    assert tp.MESAJ_CUI_CONTROL % GRESIT == ("CUI-ul 459000011 nu e valid: cifra de control nu corespunde — verifică CUI-ul. Un cod fiscal "
                                             "greșit îl respinge ANAF, la prima declarație depusă.")
    for rau, bucata in (("RO-" + A, "numai cifre"), ("45900001A0", "numai cifre"), ("0" + A, "nu începe cu 0"),
                        ("1", "între 2 și 10 cifre"), ("12345678901", "între 2 și 10 cifre"), ("", "Scrie CUI-ul"), (None, "Scrie CUI-ul")):
        m = tp.motiv_cui_firma_invalid(rau)
        assert m and bucata in m, (rau, m)
    assert tp.cui_valid(A) and not tp.cui_valid(GRESIT) and not tp.cui_valid("RO-" + A)
    with pytest.raises(tp.CuiInvalid) as e:
        tp.cere_cui_firma_valid(GRESIT)
    assert e.value.camp == "cui" and isinstance(e.value, ValueError)


def test_459_propunerea_anaf_numeste_fiecare_camp_care_se_schimba():
    acum = {"nume": "VECHE SRL", "adresa": "Str. Veche 1", "reg_com": "J40/1/2020", "caen": "4711", "oras": "Bucuresti", "judet": "B",
            "platitor_tva": True, "tva_la_incasare": False, "data_infiintare": None, "forma_juridica": "SRL"}
    d = {"denumire": "NOUA SRL", "adresa": "Str. Noua 2", "nr_reg_com": "J12/2/2021", "cod_caen": "6920", "localitate": "Cluj-Napoca",
         "judet": "CJ", "platitor_tva": False, "tva_la_incasare": False, "data_inregistrare": "2021-03-04", "forma_juridica": ""}
    sch = {s["camp"]: (s["acum"], s["anaf"]) for s in tp.propunere_anaf(acum, d)}
    assert sch == {"nume": ("VECHE SRL", "NOUA SRL"), "adresa": ("Str. Veche 1", "Str. Noua 2"), "reg_com": ("J40/1/2020", "J12/2/2021"),
                   "caen": ("4711", "6920"), "oras": ("Bucuresti", "Cluj-Napoca"), "judet": ("B", "CJ"), "platitor_tva": ("Da", "Nu"),
                   "data_infiintare": ("—", "04.03.2021")}, sch   # forma juridică: „NOUA SRL” -> SRL, aceeași; data în forma DS cap.4
    assert tp.propunere_anaf(dict(acum, nume="veche  srl"), dict(d, denumire="VECHE SRL"))[0]["camp"] != "nume"   # spații / majuscule


# ── (1) drumurile care creează o firmă ───────────────────────────────────────────────────────────────────────────
def test_459_adauga_firma_refuza_cui_gresit_langa_camp_inainte_de_orice_scriere(monkeypatch):
    """`POST /tenants` (`uc_tenants.tenant_creeaza`): refuzul pe câmpul `cui`, cu motivul, înainte de ANAF și de crearea firmei.
    MUTAȚIE: `_er.camp("cui", _m_cui)` scos -> cererea trece la provizionare -> pică (provizionarea e oprită aici cu o excepție-sondă)."""
    from core import uc_tenants, uc_comun, erori
    monkeypatch.setattr(uc_comun, "_TENANT_TEMPLATE", "-- sablon", raising=False)

    def _nu(*a, **k):
        raise AssertionError("CUI-ul greșit a ajuns la ANAF / la crearea firmei")
    monkeypatch.setattr(tp, "date_din_anaf", _nu)
    monkeypatch.setattr(tp, "provision_tenant", _nu)
    for rau in (GRESIT, "RO-" + A):
        date = types.SimpleNamespace(nume="Firma Proba 459 SRL", cui=rau, tip_firma="srl", email_client=None)
        with pytest.raises(erori.CerereGresita) as e:
            uc_tenants.tenant_creeaza(date, {"firm": -1, "uid": -1})
        d = e.value.detaliu
        assert [c["camp"] for c in d["erori_campuri"]] == ["cui"], d
        assert d["erori_campuri"][0]["mesaj"] == tp.motiv_cui_firma_invalid(rau), d


def test_459_verificarea_publica_spune_cui_gresit_si_nu_intreaba_anaf(monkeypatch):
    """`GET /public/verifica-cui/{cui}` (ecranul „Adaugă firmă”, la tastare): CUI-ul greșit -> {cui_invalid, motiv}, fără ANAF.
    MUTAȚIE: verificarea scoasă din ruta publică -> răspunsul vine de la ANAF („negăsit”), iar ecranul ar lăsa „completează manual” -> pică."""
    from fastapi.testclient import TestClient
    import main
    from core import anaf_api

    def _nu(*a, **k):
        raise AssertionError("CUI-ul greșit a plecat la ANAF")
    monkeypatch.setattr(anaf_api, "valideaza_cui", _nu)
    r = TestClient(main.app).get("/public/verifica-cui/" + GRESIT)
    assert r.status_code == 200, r.text
    assert r.json() == {"gasit": False, "cui_invalid": True, "cui": GRESIT, "camp": "cui", "motiv": tp.MESAJ_CUI_CONTROL % GRESIT}, r.json()


@_cu_db
def test_459_provizionarea_refuza_cui_gresit_si_nu_scrie_nimic(contor_schema_pastrat):
    """`provision_tenant` (sub toate drumurile de creare): `CuiInvalid` cu motivul, înaintea primei scrieri (nicio schemă, niciun rând).
    MUTAȚIE: `cui = cere_cui_firma_valid(cui)` înlocuit cu `cui = _cf.stocare(cui)` -> firma „RO-459000010” se creează -> pică."""
    c = _db.pool().getconn()
    try:
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('EF A459 CREARE') RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_a459_creare@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,))
            uid = cur.fetchone()[0]
            cur.execute("SELECT last_value FROM " + tp.SECVENTA_SCHEMA)
            seq = cur.fetchone()[0]
        for rau in (GRESIT, "RO-" + A, "0" + A):
            with pytest.raises(tp.CuiInvalid, match="nu e valid"):
                tp.provision_tenant(c, "EF A459 SRL", rau, fid, uid, "-- sablonul nu se atinge")
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.tenants WHERE accounting_firm_id = %s", (fid,))
            assert cur.fetchone()[0] == 0
            cur.execute("SELECT last_value FROM " + tp.SECVENTA_SCHEMA)
            assert cur.fetchone()[0] == seq, "refuzul a venit după contorul de scheme"
    finally:
        c.rollback()
        _db.pool().putconn(c)


@_cu_db
def test_459_importul_din_migrare_spune_cifra_de_control_nu_eroare_interna(monkeypatch):
    """`POST /migrare/importa` (`uc_migrare.migrare_importa`): CUI-ul greșit e respins pe rândul lui cu regula `cui_invalid` și motivul,
    înainte de provizionare (până azi `provision_tenant` ridica, iar `except Exception` îl spunea „eroare internă”).
    MUTAȚIE: verificarea scoasă din `migrare_importa` -> rândul iese „creare_esuata / eroare internă” -> pică."""
    from core import uc_migrare, uc_comun
    monkeypatch.setattr(uc_comun, "_TENANT_TEMPLATE", "-- sablon", raising=False)

    def _nu(*a, **k):
        raise AssertionError("CUI-ul greșit a ajuns la provizionare")
    monkeypatch.setattr(tp, "provision_tenant", _nu)
    date = types.SimpleNamespace(firme=[types.SimpleNamespace(cui=GRESIT, denumire="EF A459 MIGRARE SRL")])
    r = uc_migrare.migrare_importa(date, {"firm": -1, "uid": -1})
    assert r["creat"] == [] and len(r["erori"]) == 1, r
    e = r["erori"][0]
    assert (e.get("regula"), e.get("motiv")) == ("cui_invalid", tp.MESAJ_CUI_CONTROL % GRESIT), e


def test_459_inregistrarea_refuza_cui_gresit_inainte_de_cont():
    """`POST /auth/register` (`uc_auth._valideaza_formularul`): un CUI scris și greșit oprește formularul, înainte de cont (până azi contul
    se crea, iar firma proprie cădea după, cu „Firma proprie NU a putut fi adăugată”). MUTAȚIE: verificarea scoasă -> trece -> pică."""
    from core import uc_auth, erori
    date = types.SimpleNamespace(accept_termeni=True, parola="Parola-Buna-459!", email="ef_a459@exemplu.ro", nume_cabinet="Cabinet EF",
                                 telefon="", cui=GRESIT, nume="N", prenume="P")
    with pytest.raises(erori.CerereGresita) as e:
        uc_auth._valideaza_formularul(date)
    # o singură eroare (cea a CUI-ului): detaliul e chiar motivul ei (contractul celor patru refuzuri din `_valideaza_formularul`)
    assert e.value.detaliu == tp.MESAJ_CUI_CONTROL % GRESIT, e.value.detaliu
    date.cui = ""   # CUI-ul e opțional la înregistrare: gol trece mai departe
    try:
        uc_auth._valideaza_formularul(date)
    except erori.CerereGresita as e2:
        assert "CUI" not in str(e2.detaliu), e2.detaliu
    except erori.ServiciuIndisponibil:
        pass


def test_459_garda_drumurile_folosesc_verificarea_unica():
    """GARDA (clasa): niciun drum care creează o firmă sau îi corectează CUI-ul nu are verificarea lui proprie, și niciunul nu o ocolește.
    MUTAȚIE: un al doilea algoritm (cheia `[7, 5, 3, 2, 1, …]`) în `tenant_provisioning.py`, sau ecranul „Adaugă firmă” care trimite iar
    numai cifrele (`cui.value.replace(/\\D/g, "")` în `POST /tenants`) -> pică."""
    import ast
    import re
    src = lambda p: io.open(os.path.join(_RAD, p), encoding="utf-8").read()   # noqa: E731
    prov = src("core/tenant_provisioning.py")
    assert not re.search(r"7,\s*5,\s*3,\s*2,\s*1,\s*7", prov), "a doua implementare a cifrei de control în tenant_provisioning"
    # pe AST: în `provision_tenant`, `cui = cere_cui_firma_valid(cui)` (atribuirea, nu textul ei) — și înaintea primului `execute`
    fn = _functia(prov, "provision_tenant")
    verif = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Assign) and [ast.unparse(t) for t in n.targets] == ["cui"]
             and isinstance(n.value, ast.Call) and _nume_apel(n.value) == "cere_cui_firma_valid"
             and [ast.unparse(a) for a in n.value.args] == ["cui"]]
    scrieri = [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call) and _nume_apel(n) == "execute"]
    assert len(verif) == 1 and scrieri and verif[0] < min(scrieri), ("provision_tenant nu mai trece prin verificarea unică", verif, scrieri)
    for fis, funct in (("core/uc_tenants.py", "tenant_creeaza"), ("core/uc_tenants.py", "firma_cui_corectura"),
                       ("core/uc_tenants.py", "cui_firma_invalid"), ("core/firma_profil_api.py", "corecteaza_cui"),
                       ("core/uc_migrare.py", "migrare_importa"), ("core/uc_auth.py", "_valideaza_formularul"),
                       ("core/firma_profil_api.py", "salveaza_date")):
        apeluri = {_nume_apel(n) for n in ast.walk(_functia(src(fis), funct)) if isinstance(n, ast.Call)}
        assert apeluri >= {"motiv_cui_firma_invalid"}, "%s · %s nu trece prin `tenant_provisioning.motiv_cui_firma_invalid`" % (fis, funct)
    js = src("static/js/ecrane/firme.js")
    forma = js[js.index('nav.deschide("Adaugă firmă"'):js.index("const lista = container.querySelector(\"#firme-lista\")")]
    # obiectul trimis la `POST /tenants`, cheie cu cheie (nu prezența unui fragment): CUI-ul pleacă așa cum l-a scris omul
    corpuri = [_obiect_js(m.end(), forma) for m in re.finditer(r'api\.post\("/tenants", \{', forma)]
    assert len(corpuri) == 1, corpuri
    assert (corpuri[0].get("nume"), corpuri[0].get("cui")) == ("nume.value.trim()", "cuiScris()"), "„Adaugă firmă” nu mai trimite CUI-ul scris"
    # ramura `cui_invalid` a răspunsului de verificare: eroarea (motivul serverului) stă lângă câmpul CUI
    ramuri = re.findall(r"if \(r && r\.cui_invalid\) \{(.*?)\} else if", forma, re.S)
    assert len(ramuri) == 1, "ramura `r.cui_invalid` a dispărut sau s-a dublat"
    instr = {re.sub(r"\s+", " ", x).strip() for x in re.sub(r"//[^\n]*", "", ramuri[0]).split(";")}
    assert instr >= {'eroareCamp(corp, "fn-cui", r.motiv)'}, ("CUI-ul greșit nu se mai spune lângă câmp", instr)


def _nume_apel(n):
    return getattr(n.func, "attr", None) or getattr(n.func, "id", None)


def _functia(src, nume):
    import ast
    gasite = [n for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume]
    assert len(gasite) == 1, "funcția %s: %d definiții" % (nume, len(gasite))
    return gasite[0]


def _obiect_js(start, txt):
    """Literalul de obiect JS care începe la `start` (după `{`) -> {cheie: expresie}, despărțit pe virgulele de nivel 0 (în afara
    parantezelor / acoladelor / șirurilor), fără comentariile `/* */`."""
    adanc, sir, i, buc, cur = 0, None, start, [], ""
    while i < len(txt):
        ch = txt[i]
        if sir:
            cur += ch
            if ch == sir and txt[i - 1] != "\\":
                sir = None
        elif txt.startswith("/*", i):
            i = txt.index("*/", i) + 2
            continue
        elif ch in "\"'`":
            sir, cur = ch, cur + ch
        elif ch in "([{":
            adanc, cur = adanc + 1, cur + ch
        elif ch in ")]}":
            if adanc == 0:
                buc.append(cur)
                break
            adanc, cur = adanc - 1, cur + ch
        elif ch == "," and adanc == 0:
            buc.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    out = {}
    for b in buc:
        if b.strip():
            k, _s, v = b.partition(":")
            out[k.strip()] = re.sub(r"\s+", " ", v).strip()
    return out


# ── (2) corectura CUI-ului ────────────────────────────────────────────────────────────────────────────────────────
ANAF_A = {"cui": A, "denumire": "EF A459 VECHE SRL", "adresa": "Str. Veche 1", "nr_reg_com": "J40/1/2020", "cod_caen": "4711",
          "localitate": "Sector 1 Mun. Bucureşti", "judet": "B", "platitor_tva": True, "tva_la_incasare": True,
          "tva_data_inceput": "2020-01-01", "data_inregistrare": "2020-01-01", "forma_juridica": "",
          "tva_incasare_rtvai": {"status": True, "data_inceput": "2020-02-01", "data_sfarsit": None}, "gasit": True}
#: ANAF nu dă nr. de registru pentru B: golul înlocuiește valoarea veche (nu rămâne J40/1/2020 al lui A)
ANAF_B = {"cui": B, "denumire": "EF A459 NOUA SRL", "adresa": "Str. Noua 2", "nr_reg_com": "", "cod_caen": "6920",
          "localitate": "Cluj-Napoca", "judet": "CJ", "platitor_tva": False, "tva_la_incasare": False, "tva_data_inceput": None,
          "data_inregistrare": "2021-03-04", "forma_juridica": "", "tva_incasare_rtvai": None, "gasit": True}


@pytest.fixture()
def firma_a(contor_schema_pastrat):
    """O firmă creată cu CUI-ul A (al cabinetului — firma lui proprie) și precompletată cu datele ANAF ale lui A, în tranzacție întoarsă."""
    c = _db.pool().getconn()
    try:
        with c.cursor() as cur:
            for cui in (A, B, C):
                cur.execute("SELECT 1 FROM public.accounting_firms WHERE cui = %s", (cui,))
                assert not cur.fetchone(), "CUI-ul sintetic %s e deja al unui cabinet din baza de test" % cui
            cur.execute("INSERT INTO public.accounting_firms (nume, cui) VALUES ('EF A459 CABINET', %s) RETURNING id", (A,))
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                        "VALUES ('ef_a459_corectura@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (fid,))
            uid = cur.fetchone()[0]
        r = tp.provision_tenant(c, "EF A459 VECHE SRL", A, fid, uid, io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read())
        tp.precompleteaza_din_anaf(c, r["schema_name"], ANAF_A)
        with c.cursor() as cur:
            cur.execute('SET LOCAL search_path TO "%s", public' % r["schema_name"])
        yield dict(r, conn=c, fid=fid, uid=uid)
    finally:
        c.rollback()
        _db.pool().putconn(c)


def _profil(c):
    with c.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, reg_com, caen, oras, judet, platitor_tva, tva_la_incasare, data_infiintare::text, "
                    "platitor_tva_anaf FROM firma_profil WHERE id = 1")
        return cur.fetchone()


@_cu_db
def test_459_corectura_propune_si_inlocuieste_datele_cui_vechi_cu_cele_anaf(firma_a):
    """Avertismentul: datele ANAF ale CUI-ului nou, câmp cu câmp; confirmarea: le scrie (și golul), denumirea în ambele locuri, perioada
    TVA la încasare adusă din ANAF pentru CUI-ul vechi scoasă, CUI-ul cabinetului (firma lui proprie) corectat, totul în jurnal.
    MUTAȚIE: `_tp.inlocuieste_din_anaf(conn, _schema, anaf)` scos din `corecteaza_cui` -> adresa / CAEN / localitatea rămân ale lui A -> pică;
    `{c} = NULLIF(%s, '')` -> COALESCE (forma de la creare) -> nr. de registru al lui A rămâne -> pică."""
    from core import firma_profil_api as fp
    c, tid, uid = firma_a["conn"], firma_a["tenant_id"], firma_a["uid"]
    assert _profil(c) == ("EF A459 VECHE SRL", A, "Str. Veche 1", "J40/1/2020", "4711", "Sector 1 Mun. Bucureşti", "B", True, True,
                          "2020-01-01", True)   # precompletarea creării (acum și localitatea, județul)
    r = fp.corecteaza_cui(c, tid, "RO" + B, uid, anaf=ANAF_B)
    assert r["cod"] == "CONFIRMARE_CERUTA" and r["avertisment"] == fp.AVERTISMENT_CORECTURA_CUI % (A, B), r
    camp = {s["camp"] for s in r["anaf"]["schimbari"]}
    assert camp == {"nume", "adresa", "reg_com", "caen", "oras", "judet", "platitor_tva", "tva_la_incasare", "data_infiintare"}, r["anaf"]
    assert (r["anaf"]["gasit"], r["anaf"]["mesaj"]) == (True, "La ANAF, CUI-ul %s e al firmei „EF A459 NOUA SRL”. La confirmare, datele de "
                                                        "mai jos se înlocuiesc cu cele de la ANAF:" % B), r["anaf"]
    assert {"camp": "reg_com", "eticheta": "Nr. registrul comerțului", "acum": "J40/1/2020", "anaf": "— (ANAF nu dă)"} in r["anaf"]["schimbari"]
    assert _profil(c)[1] == A, "avertismentul nu scrie nimic"
    r2 = fp.corecteaza_cui(c, tid, "RO" + B, uid, confirmat=True, anaf=ANAF_B)
    assert r2["ok"] and r2["cui"] == B, r2
    assert _profil(c) == ("EF A459 NOUA SRL", B, "Str. Noua 2", None, "6920", "Cluj-Napoca", "CJ", False, False, "2021-03-04",
                          False), _profil(c)   # nr. de registru: ANAF nu-l dă -> gol (apare în „Profil incomplet”), nu al lui A
    with c.cursor() as cur:
        cur.execute("SELECT nume, cui, nume_anaf, nume_ales FROM public.tenants WHERE id = %s", (tid,))
        assert cur.fetchone() == ("EF A459 NOUA SRL", B, "EF A459 NOUA SRL", "anaf")
        cur.execute("SELECT cui FROM public.accounting_firms WHERE id = %s", (firma_a["fid"],))
        assert cur.fetchone()[0] == B, "firma proprie a cabinetului: CUI-ul cabinetului rămăsese al lui A"
        cur.execute("SELECT count(*) FROM tva_incasare_perioade")
        assert cur.fetchone()[0] == 0, "perioada TVA la încasare adusă din ANAF pentru A a rămas"
        cur.execute("SELECT camp FROM firma_profil_jurnal")
        jurnal = {x[0] for x in cur.fetchall()}
    assert jurnal >= {"cui", "nume", "adresa", "reg_com", "caen", "oras", "judet", "data_infiintare", "platitor_tva", "tva_la_incasare",
                      "tva_incasare_perioade"}, jurnal


@_cu_db
def test_459_corectura_fara_anaf_spune_ce_e_de_verificat_si_uita_anaf_vechi(firma_a):
    """ANAF n-are date pentru CUI-ul nou (sau nu răspunde): avertismentul și răspunsul spun ce rămâne de verificat; denumirea ANAF, starea
    TVA citită la ANAF și perioada TVA la încasare din ANAF ale CUI-ului vechi se șterg (nu mai rămân tacit).
    MUTAȚIE: ramura fără date din `inlocuieste_din_anaf` golită (`return False` direct) -> `nume_anaf` rămâne al lui A -> pică."""
    from core import firma_profil_api as fp
    c, tid, uid = firma_a["conn"], firma_a["tenant_id"], firma_a["uid"]
    r = fp.corecteaza_cui(c, tid, C, uid, anaf=None, anaf_eroare="ANAF nu răspunde acum la verificarea CUI.")
    # [lotul 11, AT] răspunsul ANAF e o afirmație tipată (`verificare_rupta`): câmpurile citite de ecran rămân
    assert (r["anaf"]["fel"], r["anaf"]["gasit"], r["anaf"]["schimbari"], r["anaf"]["mesaj"]) == (
        "verificare_rupta", False, [], "ANAF nu răspunde acum la verificarea CUI. " + fp.DE_VERIFICAT_FARA_ANAF), r["anaf"]
    r2 = fp.corecteaza_cui(c, tid, C, uid, confirmat=True, anaf=None)
    assert r2["ok"] and r2["anaf"]["mesaj"] == ("ANAF nu are date pentru CUI-ul %s (nu apare în registrul contribuabililor). " % C
                                                + fp.DE_VERIFICAT_FARA_ANAF), r2
    p = _profil(c)
    assert p[1] == C and p[2:7] == ("Str. Veche 1", "J40/1/2020", "4711", "Sector 1 Mun. Bucureşti", "B") and p[10] is None, p
    with c.cursor() as cur:
        cur.execute("SELECT nume_anaf, nume_anaf_la FROM public.tenants WHERE id = %s", (tid,))
        assert cur.fetchone() == (None, None)
        cur.execute("SELECT count(*) FROM tva_incasare_perioade WHERE sursa = 'anaf'")
        assert cur.fetchone()[0] == 0


@_cu_db
def test_459_corectura_refuza_cui_care_nu_e_valabil(firma_a):
    """Aceeași verificare ca la creare (până azi corectura folosea validatorul partenerilor, care primea și un CNP de 13 cifre și
    extrăgea cifrele din orice text). MUTAȚIE: `_tp.motiv_cui_firma_invalid` înlocuit cu validatorul partenerilor -> „RO-…” trece -> pică."""
    from core import firma_profil_api as fp
    c, tid, uid = firma_a["conn"], firma_a["tenant_id"], firma_a["uid"]
    for rau in (GRESIT, "RO-" + B, "1960523460016"):   # 1960523460016: CNP cu cifra de control corectă (cheia 279146358279)
        r = fp.corecteaza_cui(c, tid, rau, uid, confirmat=True, anaf=ANAF_B)
        assert (r["ok"], r["camp"], r["mesaj"]) == (False, "cui", tp.motiv_cui_firma_invalid(rau)), (rau, r)
    assert _profil(c)[1] == A


@_cu_db
def test_459_corectura_redeschide_intrebarea_denumirii_numai_cand_n_a_raspuns_ea(firma_a):
    """Corectura re-citește ANAF pentru o firmă EXISTENTĂ (a patra captare, `core/test_nume_anaf.py::_CAPTARI_ANAF`). Ecranul (`firme.js`)
    redeschide întrebarea denumirii când `nume_anaf_la` > `nume_ales_la`. Cu denumirea schimbată, corectura îi răspunde ea
    (`alege_denumirea("anaf")`: ambele momente egale -> închisă); cu denumirea ANAF egală fără majuscule, citirea nouă e mai nouă decât
    alegerea de ieri -> redeschisă (omul vede noua scriere ANAF). MUTAȚIE: `_tp.alege_denumirea(conn, tenant_id, "anaf", user_id)` scos ->
    prima ramură rămâne redeschisă, fără alegere -> pică."""
    from core import firma_profil_api as fp
    c, tid, uid = firma_a["conn"], firma_a["tenant_id"], firma_a["uid"]
    tp.alege_denumirea(c, tid, "aplicatie", uid)
    with c.cursor() as cur:   # alegerea veche, de ieri (datele de pornire ale probei; în tranzacția întoarsă)
        cur.execute("UPDATE public.tenants SET nume_ales_la = now() - interval '1 day' WHERE id = %s", (tid,))
    assert fp.corecteaza_cui(c, tid, B, uid, confirmat=True, anaf=ANAF_B)["ok"]
    with c.cursor() as cur:
        cur.execute("SELECT nume_ales, nume_anaf_la <= nume_ales_la FROM public.tenants WHERE id = %s", (tid,))
        assert cur.fetchone() == ("anaf", True), "denumirea schimbată: corectura a răspuns întrebării"
        cur.execute("UPDATE public.tenants SET nume_ales_la = now() - interval '1 day' WHERE id = %s", (tid,))
    assert fp.corecteaza_cui(c, tid, C, uid, confirmat=True, anaf=dict(ANAF_B, cui=C, denumire="ef a459 noua srl"))["ok"]
    with c.cursor() as cur:
        cur.execute("SELECT nume, nume_anaf, nume_anaf_la > nume_ales_la FROM public.tenants WHERE id = %s", (tid,))
        assert cur.fetchone() == ("EF A459 NOUA SRL", "ef a459 noua srl", True), "aceeași denumire: întrebarea se redeschide pe ecran"
