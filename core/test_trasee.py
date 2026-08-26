# -*- coding: utf-8 -*-
"""GARD: inventarul traseelor nu îmbătrânește tăcut, iar instrumentul lui nu minte.

`TRASEE.md` spune pe unde trece un document. Până azi era proză: o rută nouă putea
apărea fără ca vreun traseu s-o cuprindă, iar cifrele („câte trasee", „câte se pot
scrie din cod") erau amintiri. `scripts/scan_trasee.py` le calculează; testul ăsta nu
lasă rezultatul lui să se strice.

Ce ține:
  1. ACOPERIREA — fiecare rută din `main.py` intră fie într-un traseu, fie într-o
     suprafață declarată ca ne-documentară. Zero orfane.
  2. Fiecare rută într-un SINGUR traseu (altfel cifrele se numără de două ori).
  3. Clichetul pe clase — MECANIC/PARȚIAL/MANUAL. Nu se poate muta un traseu dintr-o
     clasă în alta fără să se schimbe cifra aici, deliberat.
  4. Calibrare NEGATIVĂ, două direcții (METODA §22): instrumentul trebuie să vadă o
     rută nouă orfană ȘI să nu inventeze una când nu e.

Ce NU ține, scris ca să nu se creadă altceva: că un traseu e CORECT. Testul spune că
harta acoperă codul, nu că drumul e bun.
"""
import importlib.util
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_trasee.py")

# Clichet la 25.08.2026, pe commitul care introduce inventarul. Se schimbă DELIBERAT.
_CLICHET = {"MECANIC": 30, "PARTIAL": 0, "MANUAL": 5}
_TRASEE_TOTAL = 35


def _scan():
    spec = importlib.util.spec_from_file_location("scan_trasee", _SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def st():
    return _scan()


@pytest.fixture(scope="module")
def d(st):
    return st.construieste(cu_db=False)


def test_nicio_ruta_in_afara_inventarului(d):
    assert not d["orfane"], (
        "rute care nu aparțin niciunui traseu și nici unei suprafețe declarate "
        "ne-documentare: %s. Adaugă ruta la traseul ei în scripts/scan_trasee.py:TRASEE, "
        "sau la NEDOCUMENTARE cu eticheta ei." % d["orfane"])


def test_nicio_ruta_in_doua_trasee(d):
    assert not d["dublate"], (
        "rute prinse de tiparele a două trasee — cifrele s-ar număra de două ori: %s"
        % d["dublate"])


def test_numarul_de_trasee_e_clichet(d):
    assert len(d["trasee"]) == _TRASEE_TOTAL, (
        "inventarul de trasee s-a schimbat (%d, clichet %d). Dacă e deliberat, schimbă "
        "clichetul ȘI scrie traseul nou în TRASEE.md."
        % (len(d["trasee"]), _TRASEE_TOTAL))


def test_clasele_sunt_clichet(d):
    from collections import Counter
    c = Counter(t["clasa"] for t in d["trasee"])
    acum = {k: c.get(k, 0) for k in _CLICHET}
    assert acum == _CLICHET, (
        "clasificarea traseelor s-a schimbat: %s (clichet %s). Un traseu care trece din "
        "PARȚIAL în MECANIC înseamnă că s-a construit persistența — se scrie în TRASEE.md."
        % (acum, _CLICHET))


def test_fiecare_traseu_are_cel_putin_o_ruta(d):
    """Anti-vacuu: un traseu cu zero rute nu măsoară nimic și ar trece verde degeaba."""
    goale = [t["id"] for t in d["trasee"] if t["rute"] == 0]
    assert not goale, ("trasee fără nicio rută — tiparele nu mai potrivesc nimic: %s"
                       % goale)


def test_marginile_declarate_exista(st):
    """Lista de module-margine e scrisă cu mâna (cu motivul lângă fiecare). Dacă un modul
    din ea dispare din `core/`, lista minte — și `module_margine` trebuie să cadă."""
    mod = st.citeste_module()
    lipsa = sorted(set(st.MARGINI) - set(mod))
    assert not lipsa, "MARGINI numește module care nu mai există în core/: %s" % lipsa


def test_nemarginile_declarate_exista(st):
    mod = st.citeste_module()
    lipsa = sorted(set(st.NEMARGINI) - set(mod))
    assert not lipsa, "NEMARGINI numește module care nu mai există în core/: %s" % lipsa


def test_calibrare_negativa_vede_o_ruta_orfana(st):
    """RED-proof, direcția «ratează»: o cale care nu seamănă cu niciun traseu TREBUIE să
    iasă ca orfană. Fără proba asta, `orfane == []` poate însemna «n-am căutat»."""
    falsa = {"metoda": "POST", "cale": "/inventat/pe-nicaieri",
             "norm": "/inventat/pe-nicaieri", "fn": "x", "linie": 0,
             "garzi": [], "roluri": [], "fine": [], "module": [],
             "scrie_inline": {}, "refuzuri": 0}
    _, orfane, _, _ = st.acoperire([falsa])
    assert orfane == [("POST", "/inventat/pe-nicaieri")], (
        "instrumentul NU vede o rută în afara inventarului — deci un «zero orfane» pe "
        "cod real nu dovedește nimic. Rezultat: %s" % orfane)


def test_calibrare_negativa_nu_inventeaza_orfane(st):
    """RED-proof, direcția «raportează fals»: o cale care aparține clar unui traseu NU
    trebuie să apară ca orfană. Un instrument care greșește în AMBELE direcții n-are
    niciun plafon (METODA §22)."""
    buna = {"metoda": "POST", "cale": "/tenants/{tenant_id}/casa/operatiuni",
            "norm": "/tenants/{}/casa/operatiuni", "fn": "x", "linie": 0,
            "garzi": ["cere_cabinet"], "roluri": [], "fine": [], "module": [],
            "scrie_inline": {}, "refuzuri": 0}
    per, orfane, dublate, _ = st.acoperire([buna])
    assert not orfane and not dublate and per["T09"], (
        "o rută care aparține traseului casei a fost raportată greșit: orfane=%s "
        "dublate=%s" % (orfane, dublate))


def test_aliasul_local_bate_pe_cel_de_modul(st):
    """Mutația pe propriul mod de eșec al instrumentului. Ruta de NIR își importă modulul
    ÎN CORP (`from core import stocuri_api as _s`), iar `_s` e refolosit de zeci de ori
    în main.py pentru module diferite. Prima formă a instrumentului atribuia rutei de NIR
    modulul `salarizare` — o atribuire FALSĂ, mai rea decât o absență."""
    rute = st.citeste_rute()
    nir = [r for r in rute if r["norm"] == "/tenants/{}/stocuri/nir"
           and r["metoda"] == "POST"]
    assert nir, "ruta POST /tenants/{}/stocuri/nir a dispărut din main.py"
    assert set(nir[0]["module"]) == {"stocuri_api"}, (
        "ruta de NIR nu mai e legată exact de `stocuri_api`, ci de %s — harta aliasurilor "
        "locale s-a stricat" % sorted(nir[0]["module"]))

_FALS_UMBRIT = [
    "from core import casa_api as _c",
    "",
    "@app.post('/tenants/{tenant_id}/umbrit')",
    "def umbrit(tenant_id: int):",
    "    with conn.cursor() as _c:",
    "        _c.execute('SELECT 1')",
    "    return {}",
    "",
    "@app.post('/tenants/{tenant_id}/liber')",
    "def liber(tenant_id: int):",
    "    return _c.pull(conn)",
]


def test_CALIBRARE_un_nume_umbrit_local_NU_mai_e_alias_de_modul(st, tmp_path, monkeypatch):
    """A doua față a atribuirii false (25.08.2026), găsită fiindcă a produs-o chiar codul meu.

    `main.py` are, la nivel de modul, `from core import casa_api as _c`. O rută care scrie
    `with conn.cursor() as _c:` primea `casa_api` în lista ei de module — și, prin el, trei tabele
    în care nu scrie. Testul de deasupra nu prindea cazul: acolo numele e legat de un IMPORT local,
    aici de o variabilă.

    Măsurat la reparație: **două** atribuiri false în inventar — a mea, și una mai veche
    (`rapoarte_comerciale_api`, cu tabela `rapoarte_salvate`, pe traseul statului de plată).
    O absență ar fi fost vizibilă; o atribuire falsă trece verde și intră în document."""
    io.open(os.path.join(str(tmp_path), "main.py"), "w", encoding="utf-8").write(
        chr(10).join(_FALS_UMBRIT) + chr(10))
    monkeypatch.setattr(st, "RAD", str(tmp_path))
    rute = {r["cale"]: r for r in st.citeste_rute()}

    assert not {"casa_api"} <= set(rute["/tenants/{tenant_id}/umbrit"]["module"]), (
        "`_c` e legat local de un cursor, nu de modul — atribuirea lui `casa_api` e FALSĂ")

    # Cealaltă direcție: fără umbrire, aliasul de modul trebuie să funcționeze. Fără proba asta, o
    # reparație care ar scoate TOATE aliasurile ar trece testul de sus și ar goli inventarul.
    assert {"casa_api"} <= set(rute["/tenants/{tenant_id}/liber"]["module"]), (
        "aliasul de modul nu mai e citit deloc — reparația a mers prea departe")


_UMBRIT_DIN_ALT_CORP = [
    "from core import cont_valid as _cv",
    "",
    "@app.post('/tenants/{tenant_id}/de_sus')",
    "def de_sus(tenant_id: int):",
    "    return _cv.cere_cont(conn, 's', 1, 'c')",
    "",
    "@app.post('/tenants/{tenant_id}/cu_import_local')",
    "def cu_import_local(tenant_id: int):",
    "    from core import stocuri_cv_api as _cv",
    "    return _cv.adauga(conn)",
]


def test_CALIBRARE_un_import_din_ALT_corp_nu_umbreste_aliasul_de_modul(st, tmp_path, monkeypatch):
    """A TREIA față a atribuirii false (26.08.2026, R60). Primele două sunt deasupra.

    Aici numele nu e legat local nici de un import (prima), nici de o variabilă (a doua) — e
    legat corect la nivel de modul, iar stricăciunea vine din corpul ALTEI funcții. Harta de
    aliasuri se construia cu `ast.walk(tree)`, care intră și în corpuri: `from core import
    stocuri_cv_api as _cv` dintr-o rută îl suprascria pe `from core import cont_valid as _cv`
    de la linia 30, iar cele 14 rute care se bazau pe importul de sus primeau modulul altcuiva.

    Direcția tăcută contează mai mult decât cea zgomotoasă: pe cele 14 se ADAUGĂ tabele
    inexistente și se vede, dar ruta care chiar cheamă `stocuri_cv_api` primea răspunsul corect
    dintr-un ACCIDENT — iar un accident nu e o măsurătoare. METODA §22."""
    io.open(os.path.join(str(tmp_path), "main.py"), "w", encoding="utf-8").write(
        chr(10).join(_UMBRIT_DIN_ALT_CORP) + chr(10))
    monkeypatch.setattr(st, "RAD", str(tmp_path))
    rute = {r["cale"]: r for r in st.citeste_rute()}

    assert set(rute["/tenants/{tenant_id}/de_sus"]["module"]) == {"cont_valid"}, (
        "ruta se bazează pe importul de la nivel de modul; a primit %s — un import din corpul "
        "ALTEI funcții i-a umbrit aliasul"
        % sorted(rute["/tenants/{tenant_id}/de_sus"]["module"]))

    # Cealaltă direcție: importul local trebuie să funcționeze mai departe. Fără proba asta, o
    # reparație care ar citi DOAR nivelul de modul ar trece testul de sus și ar goli inventarul
    # rutelor care își importă modulul în corp — adică exact prima față, întoarsă.
    assert set(rute["/tenants/{tenant_id}/cu_import_local"]["module"]) == {"stocuri_cv_api"}, (
        "importul din corpul PROPRIU nu mai e citit; a primit %s — reparația a mers prea departe"
        % sorted(rute["/tenants/{tenant_id}/cu_import_local"]["module"]))


def _importuri_core(nod, st):
    """Modulele din `core` importate de nodurile date, ca mulțime de nume reale."""
    import ast
    out = set()
    for n in nod:
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
            out |= {al.name for al in n.names}
        elif isinstance(n, ast.Import):
            out |= {al.name.split(".")[-1] for al in n.names if al.name.startswith("core.")}
    return out


_DOCSTRING_CU_SQL = [
    "@app.post('/tenants/{tenant_id}/proza')",
    "def proza(tenant_id: int):",
    '    """Nu scrie nimic. Aici doar POVESTESC ca un UPDATE tabela_de_proba orb ar strica ceva."""',
    "    return {}",
    "",
    "@app.post('/tenants/{tenant_id}/chiar_scrie')",
    "def chiar_scrie(tenant_id: int):",
    '    """Asta chiar scrie."""',
    "    with conn.cursor() as cur:",
    "        cur.execute('UPDATE tabela_de_proba SET numar=1')",
    "    return {}",
]


def test_CALIBRARE_docstringul_nu_e_citit_ca_SQL(st, tmp_path, monkeypatch):
    """Instanța, 26.08.2026: docstringul rutei de confirmare a adresei spunea *„o scriere făcută
    pe nevăzute ar sparge unicitatea"* — în prima formă, *„un UPDATE orb"*. Instrumentul a extras
    din proza aia o tabelă pe care a numit-o `oarb`, și a scris-o în inventar ca scriere proprie
    a rutei.

    E aceeași clasă cu regula pe care o ține gardul rutei de raport Z — *un comentariu care
    pomenește INSERT n-are voie să treacă drept scriere* — doar că acolo era în gard, iar aici
    în instrumentul pe care stau toate celelalte măsurători.

    Direcția e zgomotoasă (adaugă o tabelă), deci se vede — **atâta timp cât numele inventat nu
    seamănă cu unul real**. `oarb` sărea în ochi; `facturi` n-ar fi sărit.

    Ambele direcții, ca la celelalte calibrări: proza NU produce tabelă, iar SQL-ul din corp
    produce. Fără a doua, o reparație care ar tăia toate șirurile ar trece prima și ar goli
    inventarul de scrieri proprii."""
    io.open(os.path.join(str(tmp_path), "main.py"), "w", encoding="utf-8").write(
        chr(10).join(_DOCSTRING_CU_SQL) + chr(10))
    monkeypatch.setattr(st, "RAD", str(tmp_path))
    rute = {r["cale"]: r for r in st.citeste_rute()}

    assert not rute["/tenants/{tenant_id}/proza"]["scrie_inline"], (
        "proza din docstring a devenit scriere: %s"
        % rute["/tenants/{tenant_id}/proza"]["scrie_inline"])
    assert set(rute["/tenants/{tenant_id}/chiar_scrie"]["scrie_inline"]) >= {"tabela_de_proba"}, (
        "SQL-ul din CORP nu mai e văzut — reparația a mers prea departe și golește inventarul")


def test_ANTI_VACUU_modulul_atribuit_unei_rute_e_VIZIBIL_ei(st):
    """Invariantul din care s-a născut R60, verificat pe `main.py` REAL, nu pe un fișier sintetic.

    Un modul atribuit unei rute trebuie să fie importat undeva de unde ruta îl poate vedea: la
    nivel de modul, sau în propriul ei corp. Orice altceva înseamnă că numele a fost rezolvat
    prin harta altcuiva.

    Testul de deasupra probează mecanismul pe două rute inventate; ăsta măsoară dacă mecanismul
    ține pe toate cele ~200. Sub rezolvarea veche pica: `POST /tenants/{}/decontare-valuta`
    primea `stocuri_cv_api`, care nu e nici importat la nivel de modul, nici în corpul ei."""
    import ast
    src = io.open(os.path.join(st.RAD, "main.py"), encoding="utf-8").read()
    tree = ast.parse(src)

    nivel = _importuri_core(st._noduri_nivel_modul(tree), st)
    local = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            local[(fn.name, fn.lineno)] = _importuri_core(ast.walk(fn), st)

    rute = st.citeste_rute()
    assert len(rute) > 150, (
        "anti-vacuu: doar %d rute citite din main.py — testul ar fi trecut pe o mulțime "
        "aproape goală" % len(rute))

    rele = []
    for r in rute:
        vizibile = nivel | local.get((r["fn"], r["linie"]), set())
        lipsa = sorted(set(r["module"]) - vizibile)
        if lipsa:
            rele.append("%s %s <- %s" % (r["metoda"], r["cale"], ", ".join(lipsa)))
    assert not rele, (
        "%d rute au primit un modul pe care nu-l pot vedea — harta de aliasuri s-a stricat "
        "din nou:%s%s" % (len(rele), chr(10), chr(10).join(rele)))


_DOC_PREDAT = ("content-disposition", "application/pdf", "fileresponse",
               "application/vnd.openxmlformats", "application/zip", "image/")

# [R52] Clichet pe rutele care PREDAU un document fara verificare de rol. Poate scadea, niciodata
# creste.
#
# CONFRUNTAREA CELOR DOUA INSTRUMENTE, scrisa fiindca cifrele NU coincid. Masuratoarea din R52
# (25.08.2026) a dat 25 de rute care predau un document, 17 fara rol. Gardul asta, cu ACELEASI
# marcaje dar citind doar CORPUL rutei, gaseste 18 si 8. Diferenta nu e un progres - e raza:
# masuratoarea a urmarit si ce livreaza modulele chemate, gardul se opreste la ruta. Deci:
#   - clichetul e 8, cifra pe care gardul o poate reproduce de fiecare data;
#   - restul de pana la 17 NU sunt pazite aici, si asta se scrie, nu se tace.
# Un clichet pe o cifra pe care instrumentul n-o poate recalcula ar fi o amintire, nu o masuratoare.
_CLICHET_DOC_FARA_ROL = 8


def _rute_care_predau_document(st):
    """Rutele al caror corp livreaza un fisier catre om. Se citeste din CORPUL rutei (antet
    Content-Disposition, tip MIME, FileResponse), nu din numele ei: `documente/balanta` si
    `d406-active` n-au «pdf» in cale si totusi predau un fisier."""
    import ast
    import os
    src = io.open(os.path.join(st.RAD, "main.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in fn.decorator_list:
            if not isinstance(dec, ast.Call) or getattr(dec.func, "attr", None) not in st.METODE:
                continue
            if not dec.args or not isinstance(dec.args[0], ast.Constant):
                continue
            corp = ast.unparse(fn).lower()
            if not any(m in corp for m in _DOC_PREDAT):
                continue
            _g, roluri, fine = st._garzi_si_rol(fn, dec)
            out.append((dec.func.attr.upper(), dec.args[0].value, bool(roluri or fine)))
    return out


def test_ANTI_VACUU_se_gasesc_rutele_care_predau_un_document(st):
    """Daca detectorul nu mai vede nicio ruta, clichetul de mai jos ar raporta 0 si ar parea
    progres. Cifra masurata pe 25.08: 25 de rute predau un document."""
    r = _rute_care_predau_document(st)
    assert len(r) >= 15, "detectorul vede doar %d rute care predau un document — s-a stricat?" % len(r)


def test_clichet_documente_predate_fara_rol(st):
    """[R52] Un document care ajunge la un om poate pleca pe un GET, iar acolo nu se verifica
    niciun rol. Toate masuratorile mele de rol de pana atunci numarasera doar rutele care SCRIU —
    punctul orb: *«iese catre un om» nu e totuna cu «scrie ceva»*.

    Decizia lui Costin (25.08.2026) a fost aplicata; clichetul e ce ramane, ca numarul sa nu poata
    creste tacut. O ruta noua care preda un document fara rol pica aici."""
    fara = sorted(c for _m, c, are_rol in _rute_care_predau_document(st) if not are_rol)
    assert len(fara) <= _CLICHET_DOC_FARA_ROL, (
        "au aparut rute care predau un document fara verificare de rol (clichet %d, acum %d):%s  %s"
        % (_CLICHET_DOC_FARA_ROL, len(fara), chr(10), (chr(10) + "  ").join(fara)))
    assert len(fara) == _CLICHET_DOC_FARA_ROL, (
        "clichetul e depasit — coboara-l la %d" % len(fara))


def test_cele_TREI_documente_cu_date_de_tert_au_rol(st):
    """Cealalta directie: clichetul singur ar trece si daca cele trei si-ar pierde rolul, atata
    timp cat totalul nu creste (o alta ruta ar putea capata rol in schimb). Criteriul lui Costin
    numeste exact trei, deci exact trei se asertaza pe nume."""
    dupa_cale = {c: are_rol for _m, c, are_rol in _rute_care_predau_document(st)}
    for c in ("/tenants/{tenant_id}/fluturas/{salariat_id}",
              "/tenants/{tenant_id}/chitante/{chitanta_id}/pdf",
              "/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}"):
        assert c in dupa_cale, "ruta %s a disparut — reciteste decizia inainte s-o repari" % c
        assert dupa_cale[c], (
            "%s poarta datele unui tert si nu mai cere rol — decizia lui Costin, 25.08.2026" % c)


def _db_pentru_tabele():
    try:
        from core import db as _db
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def test_fiecare_pas_din_loturi_spune_CE_face(st):
    """[Costin, 25.08.2026] *«Se verifica prin efect» spune ca EXISTA un efect, nu care e.*

    Un pas fara efect descris e un pas la care nu se poate scrie verificarea. Clichetul e ZERO:
    la prima masuratoare erau cinci, si toate cinci s-au rezolvat - doua fiindca fisierul de
    tabele cunoscute era invechit (vezi testul urmator), trei fiindca efectul se deriva din ce
    INTOARCE ruta, nu doar din ce scrie.

    Daca reapare unul, nu e o nota de subsol: e o cifra."""
    pasi = st.pasii_ordonati()
    assert len(pasi) >= 150, "instrumentul vede doar %d pasi - s-a stricat?" % len(pasi)
    fara = sorted("%s %s" % (m, c) for _t, _n, m, c, ce, _g in pasi if "NU SE POATE DERIVA" in ce)
    assert not fara, (
        "pasi fara efect derivabil (%d) - la ei nu se poate scrie o verificare:%s  %s"
        % (len(fara), chr(10), (chr(10) + "  ").join(fara)))


def test_toate_loturile_acopera_toti_pasii(st):
    """Lotizarea nu poate pierde pe drum. Suma loturilor = numarul de pasi, fara suprapuneri."""
    pasi = st.pasii_ordonati()
    vazuti, n = [], 1
    while True:
        text = st.redare_lot(n)
        if text.startswith("lot inexistent"):
            break
        vazuti += [l for l in text.split(chr(10)) if l.startswith("- **`")]
        n += 1
    assert len(vazuti) == len(pasi), (
        "loturile arata %d pasi, dar inventarul are %d" % (len(vazuti), len(pasi)))
    assert len(set(vazuti)) == len(vazuti), "un pas apare in doua loturi"


@pytest.mark.skipif(not _db_pentru_tabele(), reason="DB indisponibil")
def test_fisierul_de_tabele_cunoscute_nu_imbatraneste(st):
    """Instanta (25.08.2026): `artefacte_produse` exista in baza din 25.08, dar
    `scripts/trasee_tabele.json` fusese generat inainte. Filtrul care taie numele inventate de
    regexul de SQL taia si o tabela REALA - iar doua rute de bilant apareau ca si cum n-ar scrie
    nimic. Un filtru invechit nu produce zgomot, produce TACERE, si aia nu se vede.

    Gardul compara fisierul cu baza: orice tabela in care codul chiar scrie si care exista in DB
    trebuie sa fie in fisier. Regenerare: `scan_trasee.py --tabele`."""
    import json
    cunoscute = set(json.load(io.open(st.CALE_TABELE, encoding="utf-8"))["tabele"])
    scrise = set()
    for r in st.citeste_rute():
        scrise.update(r["scrie_inline"])
    for info in st.citeste_module().values():
        scrise.update(info["scrie"])
    from core import db as _db
    _db.init_pool()
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema IN ('public', 'tenant_001')")
        in_db = {r[0] for r in cur.fetchall()}
    lipsa = sorted((scrise & in_db) - cunoscute)
    assert not lipsa, (
        "tabele REALE, in care codul scrie, taiate de filtrul invechit: %s%s  "
        "regenereaza: ./venv/bin/python scripts/scan_trasee.py --tabele" % (lipsa, chr(10)))


def test_fiecare_loc_de_verificare_spune_CE_face_pasul(st):
    """Descrierea efectului sta unde se SCRIE verificarea, nu doar in lotul care se citeste.

    Loturile sunt o ordine de citire; TRASEE_VERIFICARI.md e fisierul in care se scrie. Daca
    descrierea ar sta doar in lot, ar fi in fata ochilor cand se alege pasul si absenta cand se
    scrie propozitia. Aici se cere ca fiecare pas sa aiba randul `*ce face: ...*`.

    Un pas nou apare intai FARA el (scheletul `--verificari` nu-l genereaza), deci gardul spune
    exact ce lipseste. NU se repara prin regenerare: regenerarea sterge ce s-a scris."""
    doc = io.open(os.path.join(_RAD, "TRASEE_VERIFICARI.md"), encoding="utf-8").read()
    blocuri = doc.split(chr(10) + "### ")[1:]
    assert len(blocuri) >= 150, "TRASEE_VERIFICARI.md are doar %d locuri - s-a golit?" % len(blocuri)
    fara = []
    for b in blocuri:
        cap = b.split(chr(10), 1)[0].strip()
        corp = b.split(chr(10) + "- [ ]")[0]
        if "*ce face:" not in corp:
            fara.append(cap)
    assert not fara, (
        "locuri de verificare fara descrierea efectului (%d) - la ele nu se poate scrie ce trebuie "
        "sa fie adevarat:%s  %s" % (len(fara), chr(10), (chr(10) + "  ").join(fara[:12])))


def test_adnotarea_din_TRASEE_VERIFICARI_e_IDENTICA_cu_ce_masoara_instrumentul(st):
    """doc↔cod, a doua oară. Rândul `*ce face:*` e derivat din cod, ca blocul din `TRASEE.md` —
    dar până azi nimic nu-l compara cu instrumentul: testul de deasupra cere doar să EXISTE.

    Măsurat la construcție (26.08.2026): **121 din 192 difereau**. Patru din reparația R60;
    117 rămase din ziua în care `scrie X` s-a despărțit de `poate atinge, prin modul X` fără ca
    fișierul în care se SCRIU verificările să fie regenerat. Adică verificările se scriau
    uitându-se la un rând care spunea *„ruta scrie în T"* acolo unde instrumentul măsurase
    *„un modul chemat de ea scrie în T"* — o afirmație mai tare decât măsurătoarea, exact
    inversul a ce apără cuvântul PLAFON.

    De ce e o gardă și nu o regenerare la fiecare rulare: regenerarea din schelet ȘTERGE
    verificările scrise. Se repară cu un patch care atinge doar rândul, iar gardul spune când."""
    import re
    canonic = {(m, c): ce for _t, _n, m, c, ce, _g in st.pasii_ordonati()}
    assert len(canonic) > 150, "anti-vacuu: doar %d pași canonici" % len(canonic)

    linii = io.open(os.path.join(_RAD, "TRASEE_VERIFICARI.md"), encoding="utf-8").read().split(chr(10))
    cap_re = re.compile(r"^### `([A-Z]+) (/.*)`\s*$")
    diferite, lipsa, vazute = [], [], 0
    for i, ln in enumerate(linii):
        m = cap_re.match(ln)
        if not m:
            continue
        cheie = (m.group(1), m.group(2))
        if cheie not in canonic:
            continue
        vazute += 1
        rand = None
        for j in range(i + 1, len(linii)):
            if linii[j].startswith("### ") or linii[j].startswith("## "):
                break
            if linii[j].startswith("*ce face:"):
                rand = linii[j]
                break
        if rand is None:
            lipsa.append("%s %s" % cheie)
        elif rand != "*ce face: %s*" % canonic[cheie]:
            diferite.append("%s %s" % cheie)

    assert vazute > 150, (
        "anti-vacuu: doar %d capete de pas regăsite în TRASEE_VERIFICARI.md — formatul "
        "titlurilor s-a schimbat și gardul se uită în gol" % vazute)
    assert not lipsa and not diferite, (
        "adnotări care nu mai spun ce măsoară instrumentul: %d diferite, %d lipsă.%s%s%s"
        "Verificările scrise sub ele stau pe o descriere a efectului care nu mai e adevărată."
        % (len(diferite), len(lipsa), chr(10), chr(10).join((diferite + lipsa)[:12]), chr(10)))


def test_blocul_din_TRASEE_e_identic_cu_ce_genereaza_instrumentul(st):
    """doc↔cod. Partea XII din `TRASEE.md` e GENERATĂ (`--md`). Dacă cineva o editează cu
    mâna, sau dacă inventarul se schimbă și documentul rămâne, cele două diverg — și
    atunci documentul descrie o aplicație care nu mai există. Regenerarea:
    `./venv/bin/python scripts/scan_trasee.py --md` + rescrierea blocului dintre marcaje."""
    doc = io.open(os.path.join(_RAD, "TRASEE.md"), encoding="utf-8").read()
    assert st.MARCA_START in doc and st.MARCA_STOP in doc, (
        "TRASEE.md n-are marcajele blocului generat — Partea XII a fost ștearsă?")
    a = doc.index(st.MARCA_START)
    b = doc.index(st.MARCA_STOP) + len(st.MARCA_STOP)
    din_doc = doc[a:b]
    generat = st.redare_md()
    if din_doc != generat:
        ld, lg = din_doc.split(chr(10)), generat.split(chr(10))
        prima = next((i for i in range(max(len(ld), len(lg)))
                      if (ld[i] if i < len(ld) else None) != (lg[i] if i < len(lg) else None)),
                     0)
        raise AssertionError(
            "blocul din TRASEE.md diferă de ce generează scan_trasee.py --md, "
            "prima diferență la linia %d a blocului:%s  doc:     %r%s  generat: %r%s"
            "Regenerează: ./venv/bin/python scripts/scan_trasee.py --md"
            % (prima + 1, chr(10), ld[prima] if prima < len(ld) else "(lipsește)", chr(10),
               lg[prima] if prima < len(lg) else "(lipsește)", chr(10)))


def test_datele_de_firme_exista_si_acopera_toate_firmele(st):
    """Anti-vacuu pe sursa numerelor de firme. Un fișier absent ar face redarea să tacă
    despre precondiții, iar tăcerea s-ar citi ca «nu s-a măsurat» — sau, mai rău, ca zero."""
    f = st.firme_cunoscute()
    assert f, ("scripts/trasee_firme.json lipsește sau e gol — regenerează cu "
               "`scripts/scan_trasee.py --firme`")
    assert len(f) >= 17, ("datele acoperă doar %d firme; instalarea are cel puțin 17. "
                          "Fișierul e stătut." % len(f))
    goale = [s for s, n in f.items() if not any(n.values())]
    assert not goale, ("firme fără niciun rând în nicio tabelă: %s — fie măsurătoarea "
                       "n-a văzut schema, fie firma chiar e goală; ambele merită privite"
                       % goale)


def test_traseele_fara_tabela_proprie_nu_raporteaza_ZERO_firme(st):
    """Interdicția 32 aplicată instrumentului: un traseu fără tabelă proprie NU poate
    spune «nicio firmă» — nu se poate ști din date. Un necunoscut rotunjit la zero ar
    umfla cifra care contează („câte trasee nu se pot parcurge")."""
    d = st.construieste()
    rele = [t["id"] for t in d["trasee"]
            if not t["tabele_declarate"] and t.get("firme_nr") is not None]
    assert not rele, ("trasee fără tabelă proprie care raportează totuși un număr de "
                      "firme: %s — necunoscutul s-a rotunjit" % rele)

def test_fiecare_pas_care_schimba_ceva_are_LOC_de_verificare(st):
    """`TRASEE_VERIFICARI.md` e singurul document care NU se generează: conținutul lui e scris
    de om. Instrumentul păzește un singur lucru — **niciun pas care schimbă ceva să nu rămână
    fără loc**. O rută nouă apare aici ca lipsă; nu se suprascrie nimic.

    De ce doar pașii care schimbă: pe un `GET`, «ce trebuie să fie adevărat după» e vid prin
    construcție — n-a schimbat nimic. Citirile rămân listate ca context, fără slot."""
    cale = os.path.join(_RAD, "TRASEE_VERIFICARI.md")
    assert os.path.isfile(cale), (
        "TRASEE_VERIFICARI.md lipsește. Se generează O DATĂ cu "
        "`scripts/scan_trasee.py --verificari > TRASEE_VERIFICARI.md`, apoi se completează de mână")
    doc = io.open(cale, encoding="utf-8").read()
    rute = st.citeste_rute()
    per, _, _, _ = st.acoperire(rute)
    lipsa = []
    for tid, _nume, _tip, _tab in st.TRASEE:
        for r in per[tid]:
            if r["metoda"] == "GET":
                continue
            cap = "### `%s %s`" % (r["metoda"], r["cale"])
            if cap not in doc:
                lipsa.append("  %s: %s %s" % (tid, r["metoda"], r["cale"]))
    assert not lipsa, (
        "pași care schimbă ceva și n-au loc de verificare în TRASEE_VERIFICARI.md (%d): %s "
        "— adaugă-i cu mâna. Regenerarea peste fișier ȘTERGE ce s-a scris în el."
        % (len(lipsa), " · ".join(x.strip() for x in lipsa[:12])))


def test_locurile_de_verificare_nu_dispar(st):
    """Anti-vacuu în cealaltă direcție: un fișier golit ar trece testul de mai sus doar dacă
    și inventarul s-ar goli. Aici se cere ca numărul de locuri să fie cel puțin cât numărul
    de pași care schimbă ceva — altfel cineva a șters secțiuni."""
    doc = io.open(os.path.join(_RAD, "TRASEE_VERIFICARI.md"), encoding="utf-8").read()
    rute = st.citeste_rute()
    per, _, _, _ = st.acoperire(rute)
    acte = sum(1 for tid, _n, _t, _tb in st.TRASEE
               for r in per[tid] if r["metoda"] != "GET")
    locuri = doc.count("- [ ]") + doc.count("- [x]")
    assert locuri >= acte, (
        "TRASEE_VERIFICARI.md are %d locuri pentru %d pași care schimbă ceva — s-au șters "
        "secțiuni" % (locuri, acte))
