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
_CLICHET = {"MECANIC": 27, "PARTIAL": 3, "MANUAL": 5}
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
