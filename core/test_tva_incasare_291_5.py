# -*- coding: utf-8 -*-
"""Garda R151 — cele două ramuri ale art. 291 alin. (5) se CER, nu se ghicesc.

CE APARA. Art. 291 alin. (5) are două ramuri: cota e a faptului generator, *cu excepția* cazului în
care factura ori avansul au precedat livrarea, când e a documentului. R149 a reparat prima ramură. A
doua nu era modelată — corpul cererii nu purta niciun indiciu despre care caz e —, iar decizia lui
Costin (05.09.2026) a fost limpede: **se cere de la contabil, nu se derivă**, fiindcă *„a ghici ar
produce o cifră validă și falsă"*.

TREI SUPRAFEȚE, fiindcă un default tăcut poate sta în oricare:
  - **regula** (`core/cota_tva_incasare`) — modul PUR, deci se probează pe COMPORTAMENT: se cheamă
    și se citește ce întoarce. Nicio aserțiune pe forma codului acolo unde se poate rula codul.
  - **ruta** — trebuie să CHEME regula și să folosească data pe care o dă ea; altfel modulul poate fi
    impecabil și nefolosit.
  - **ecranul** — un `select` obligatoriu se randează cu prima opțiune deja aleasă, deci ar răspunde
    în locul omului. `neales` pune o opțiune goală pe primul loc. *Un default fiscal tăcut îmbrăcat în
    interfață e tot un default fiscal tăcut, și nu se vede din Python.*

STRUCTURA, NU TEXT (METODA §23): ruta se citește ca AST; ecranul se **parsează** într-un dicționar de
câmpuri cu atribute, iar aserțiunile se fac pe apartenență în container, nu pe „șir în sursă". O
căutare în sursă trece la fel de bine pe un comentariu, pe altă operațiune din același fișier, sau pe
cuvântul rămas dintr-un câmp șters — adică exact pe lucrurile care nu sunt câmpul căutat.
"""
import ast
import io
import os
import re

import pytest

from core import cota_tva_incasare as m

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")
_ECRAN = os.path.join(_RAD, "static", "js", "ecrane", "operatiuni_ecran.js")

LIVRARE = "2025-09-10"
DOCUMENT = "2025-07-15"


def _corp(**kw):
    return dict({"data_fapt_generator": LIVRARE}, **kw)


# ══ regula, pe COMPORTAMENT ════════════════════════════════════════════════
def test_nomenclatorul_ramurilor_e_inchis():
    """Norma numește exact două situații, nu o listă exemplificativă."""
    assert set(m.RAMURI) == {"fapt_generator", "factura_avans"}


def test_data_cotei_se_muta_cu_ramura():
    """MIEZUL. Aceleași date, altă ramură — altă dată a cotei.

    Instanța apărată: până la R151 data cotei era ÎNTOTDEAUNA cea a faptului generator, deci ramura
    de excepție producea o cotă corectă ca formă și greșită ca fond. Dacă cele două ar da aceeași
    dată, reparația ar fi doar un câmp în plus.
    """
    gen = m.alegerea(_corp(ramura_291_5="fapt_generator"))
    exc = m.alegerea(_corp(ramura_291_5="factura_avans", data_factura_avans=DOCUMENT))
    assert gen.data_cotei == LIVRARE
    assert exc.data_cotei == DOCUMENT
    assert gen.data_cotei != exc.data_cotei, "data cotei nu se mișcă cu situația aleasă"
    assert gen.data_fapt_generator == exc.data_fapt_generator == LIVRARE
    assert gen.data_document is None and exc.data_document == DOCUMENT


@pytest.mark.parametrize("corp,cod", [
    ({}, "fara_fapt_generator"),
    ({"data_fapt_generator": LIVRARE}, "ramura_nealeasa"),
    (_corp(ramura_291_5=""), "ramura_nealeasa"),
    (_corp(ramura_291_5="altceva"), "ramura_nealeasa"),
    (_corp(ramura_291_5="factura_avans"), "fara_data_document"),
    (_corp(ramura_291_5="factura_avans", data_factura_avans=LIVRARE), "document_dupa_livrare"),
    (_corp(ramura_291_5="factura_avans", data_factura_avans="2025-11-01"), "document_dupa_livrare"),
])
def test_fiecare_fel_de_a_nu_sti_primeste_refuzul_POTRIVIT(corp, cod):
    """Nu „a picat", ci „a picat DIN MOTIVUL ĂSTA".

    GĂSIT DE PROPRIA MUTAȚIE: prima formă a testului cerea doar `pytest.raises(ValueError)`, iar
    scoțând verificarea ramurii garda a rămas **verde** — o ramură nealeasă cădea prin `else` pe
    ramura de excepție și era refuzată acolo, pentru lipsa datei documentului. Rezultat corect,
    motiv greșit. *Un test care acceptă orice refuz nu apără motivul refuzului.*
    """
    with pytest.raises(m.RefuzAlegere) as e:
        m.alegerea(corp)
    assert e.value.cod == cod, "refuz din alt motiv: %s (%s)" % (e.value.cod, e.value)


def test_codurile_refuzului_sunt_un_nomenclator_inchis():
    """Un cod nou fără loc în listă e o cale de refuz pe care n-o știe nimeni."""
    assert set(m.RefuzAlegere.CODURI) == {
        "fara_fapt_generator", "ramura_nealeasa", "fara_data_document", "document_dupa_livrare"}


def test_documentul_din_ziua_livrarii_nu_e_exceptie():
    """Calibrare pe MARGINE: norma cere «înainte de», nu «cel târziu la».

    Fără testul ăsta, un `>` în loc de `>=` ar trece, iar o factură emisă chiar în ziua livrării ar
    fi tratată ca excepție — cu cota unei zile care e aceeași, deci fără efect vizibil azi și cu
    efect exact în ziua în care se schimbă o cotă.
    """
    with pytest.raises(ValueError):
        m.alegerea(_corp(ramura_291_5="factura_avans", data_factura_avans=LIVRARE))
    ok = m.alegerea(_corp(ramura_291_5="factura_avans", data_factura_avans="2025-09-09"))
    assert ok.data_cotei == "2025-09-09"


@pytest.mark.parametrize("corp", [
    {},
    {"data_fapt_generator": LIVRARE},
    _corp(ramura_291_5="factura_avans"),
    _corp(ramura_291_5="factura_avans", data_factura_avans="2025-11-01"),
])
def test_fiecare_refuz_isi_numeste_temeiul(corp):
    """Interdicția 77: un refuz în numele unei norme numește norma. Aici, pe fiecare cale."""
    with pytest.raises(m.RefuzAlegere) as e:
        m.alegerea(corp)
    assert str(e.value).endswith("(%s)" % m.TEMEI_291_5), str(e.value)[-120:]
    assert e.value.temei is m.TEMEI_291_5


def test_temeiul_e_structurat_si_verificat_la_sursa():
    """Nu o propoziție despre lege, ci un `Temei` cu câmpuri — citabil mecanic la o schimbare."""
    t = m.TEMEI_291_5
    assert (t.art, t.alin) == ("291", "5")
    assert t.nivel_sursa == "MO" and t.url and t.verificat_la, (t.nivel_sursa, t.url)
    assert t.text_citat and t.text_citat.startswith("În cazul operațiunilor supuse sistemului")


def test_descrierea_leaga_cota_de_motivul_ei():
    """Peste șase luni, nota trebuie să spună singură de ce cota e aia."""
    gen = m.descrierea(m.alegerea(_corp(ramura_291_5="fapt_generator")))
    exc = m.descrierea(m.alegerea(_corp(ramura_291_5="factura_avans", data_factura_avans=DOCUMENT)))
    assert LIVRARE in gen and gen != exc
    assert DOCUMENT in exc and LIVRARE in exc, exc


# ══ ruta CHEAMĂ regula ═════════════════════════════════════════════════════
def test_ruta_deleaga_si_foloseste_data_data_de_regula():
    """Modulul poate fi impecabil și nefolosit — asta se vede numai din rută.

    Pe AST: ruta cheamă `alegerea(...)` și trimite mai departe `.data_cotei`, nu vreo dată aleasă
    de ea. Instanța apărată e chiar cea de dinainte de R151: ruta își alegea singură data.
    """
    arb = ast.parse(io.open(_MAIN, encoding="utf-8").read())
    fn = next((n for n in ast.walk(arb)
               if isinstance(n, ast.FunctionDef) and n.name == "nota_tva_incasare"), None)
    assert fn is not None, "ruta `nota_tva_incasare` a dispărut — garda ar fi vidă"
    apeluri = {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert {"alegerea"} <= apeluri, (
        "ruta nu mai cheamă regula: și-ar alege iar singură data cotei")
    atribute = {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    assert {"data_cotei"} <= atribute, "ruta nu folosește data întoarsă de regulă"


# ══ ecranul, PARSAT ════════════════════════════════════════════════════════
_C = re.compile(r'C\(\s*"(?P<nume>[^"]+)"\s*,\s*"(?P<eticheta>(?:[^"\\]|\\.)*)"'
                r'(?:\s*,\s*"(?P<tip>[^"]+)")?(?P<extra>.*?)\)\s*,\s*(?=C\(|\]|$)', re.DOTALL)


def _campuri(cheie="tva_incasare"):
    """Câmpurile unei operațiuni, ca DICȚIONAR de obiecte cu atribute.

    Aici se face trecerea de la text la structură: mai jos nu se mai caută niciun șir în sursă, se
    citesc câmpuri dintr-un container. Pică dacă operațiunea nu mai e în registru.
    """
    src = io.open(_ECRAN, encoding="utf-8").read()
    # Comentariile pe linie proprie se scot ÎNAINTE de parsare. Fără asta, câmpul dinaintea unui
    # comentariu îl înghite pe următorul: separatorul dintre câmpuri e „`),` urmat de `C(`", iar un
    # comentariu între ele îl rupe, deci regexul se întinde peste ambele. Găsit de
    # `test_parserul_chiar_vede_campurile_stiute` — calibrarea pozitivă a instrumentului, care a
    # spus „nu văd un câmp pe care ÎL ȘTIU" în loc să lase testele să arate ca un defect de ecran.
    # LIMITA, declarată: se scot doar comentariile care ocupă linia întreagă; unul pus la capătul
    # unei linii de câmp ar rămâne, iar parserul ar rata iar un câmp — dar ar rata ZGOMOTOS.
    src = re.sub(r"(?m)^\s*//.*$", "", src)
    i = src.find('cheie: "%s"' % cheie)
    assert i > 0, "operațiunea `%s` nu mai e în REGISTRU — garda ar fi vidă" % cheie
    j = src.find('cheie: "', i + 10)
    bloc = src[i:j if j > 0 else len(src)]

    out = {}
    for x in _C.finditer(bloc):
        extra = x.group("extra") or ""
        cond = re.search(r'cond:\s*\{\s*camp:\s*"([^"]+)"\s*,\s*val:\s*"([^"]+)"', extra)
        out[x.group("nume")] = {
            "eticheta": x.group("eticheta"),
            "tip": x.group("tip") or "numar",
            "chei": set(re.findall(r"(?:\{|,)\s*(\w+)\s*:", extra)),
            "optiuni": [v for v, _e in re.findall(r'\["([^"]+)",\s*"((?:[^"\\]|\\.)*)"\]', extra)],
            "cond": {"camp": cond.group(1), "val": cond.group(2)} if cond else None,
            "ajutor": " ".join(re.findall(r'ajutor:\s*(.*?)(?:\}|,\s*\w+:)', extra, re.DOTALL)),
        }
    assert out, "niciun câmp parsat din operațiunea `%s` — parserul e orb, nu ecranul gol" % cheie
    return out


def test_parserul_chiar_vede_campurile_stiute():
    """Calibrare POZITIVĂ a instrumentului: câmpurile vechi, cunoscute, sunt găsite.

    Fără ea, un parser care nu potrivește nimic ar face toate testele de mai jos să pice pe
    „lipsește câmpul" — adică ar arăta ca un defect de aplicație, când e unul de instrument.
    """
    c = _campuri()
    for stiut in ("data", "sens", "suma_incasata", "data_fapt_generator", "cota"):
        assert stiut in c, "parserul nu vede câmpul cunoscut `%s`" % stiut
    assert c["sens"]["optiuni"] == ["incasare", "plata"]
    assert c["cota"]["chei"] >= {"optional", "sugestie"}


def test_ecranul_cere_alegerea_si_nu_o_preselecteaza():
    """`neales` e ce împiedică interfața să răspundă în locul contabilului."""
    c = _campuri()
    camp = c.get("ramura_291_5")
    assert camp, "câmpul de alegere lipsește din operațiunea `tva_incasare`"
    assert camp["tip"] == "select"
    assert {"neales"} <= camp["chei"], (
        "`ramura_291_5` n-are `neales`: prima situație ar veni preselectată, iar alegerea juridică "
        "ar fi făcută de aplicație, nu de om")
    assert "optional" not in camp["chei"], (
        "alegerea nu poate fi opțională — fără ea cota nu se poate stabili")
    assert camp["optiuni"] == list(m.RAMURI), (
        "opțiunile ecranului nu sunt exact ramurile regulii: %s" % camp["optiuni"])


def test_randarea_da_efect_lui_neales():
    """`neales` nu e doar declarat: randarea produce o opțiune goală, selectată, pe primul loc."""
    src = io.open(_ECRAN, encoding="utf-8").read()
    i = src.find("const gol =")
    assert i > 0, "randarea nu mai are ramura `gol` — `neales` ar fi un câmp fără efect"
    tokeni = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", src[i:i + 400]))
    assert {"neales", "selected"} <= tokeni, sorted(tokeni)[:20]
    assert "gol" in set(re.findall(r"\$\{(\w+)", src[i:i + 900])), (
        "opțiunea goală se calculează, dar nu se pune în `<select>`")


def test_data_documentului_apare_doar_pe_ramura_de_exceptie():
    """Condiționarea e pe RAMURĂ: în situația generală câmpul n-are ce căuta pe ecran."""
    c = _campuri()
    assert {"data_factura_avans"} <= set(c), "câmpul datei documentului lipsește"
    assert c["data_factura_avans"]["cond"] == {"camp": "ramura_291_5", "val": "factura_avans"}, (
        c["data_factura_avans"]["cond"])
    assert c["data_factura_avans"]["tip"] == "data"


def test_ambele_ramuri_sunt_explicate_omului():
    """Costin a cerut explicit «explicația scurtă a celor două ramuri»."""
    ajutor = _campuri()["ramura_291_5"]["ajutor"]
    assert ajutor, "alegerea n-are explicație — omul ar trebui să deschidă codul fiscal"
    cuvinte = set(re.findall(r"\w+", ajutor.lower()))
    lipsesc = [c for c in ("291", "livrare", "factura", "avansul") if c not in cuvinte]
    assert not lipsesc, "explicația nu numește %s — v. `ajutor`: %s" % (lipsesc, ajutor[:160])


@pytest.mark.parametrize("cheie", ["ramura_291_5", "data_factura_avans"])
def test_campurile_noi_ajung_in_corpul_cererii(cheie):
    """Colectarea trimite exact ce e în `opCurenta.campuri`.

    Un câmp scos de acolo dispare tăcut din cerere, iar ruta ar începe să refuze fiecare operațiune
    fără ca nimeni să poată vedea de ce.
    """
    assert {cheie} <= set(_campuri()), (
        "câmpul `%s` nu mai e în registrul ecranului, deci n-ar mai ajunge în cerere" % cheie)
