# -*- coding: utf-8 -*-
"""GARD — fiecare dintre cele nouă declarații ori își arată componentele, ori spune de ce nu poate.

DE CE EXISTĂ (30.08.2026, a patra poziție din lista 5). Pasul 1c a măsurat, pe răspunsul viu al
rutei și pe tot portofoliul: **0 din 92 de ieșiri își arată componentele**. Ruta întorcea `stare`,
`xml_b64` și `operatiuni` — **un contor**. *„Valid, 18 operațiuni"* nu se poate verifica; se poate
doar crede.

CE FACE IMPOSIBIL, și fiecare punct e un mod de eșec real, nu o ipoteză:

  1. **Ca o declarație din cele nouă să iasă din acoperire în tăcere.** Ori are hartă de componente,
     ori are motiv scris — a treia variantă, uitarea, nu există.
  2. **Ca harta să arate spre un atribut care nu există.** Ăsta e modul de eșec care doare: un
     atribut greșit nu crapă, întoarce **zero rânduri** — iar zero rânduri arată exact ca o
     declarație goală. Un gard care nu s-ar uita la asta ar păzi o lume pe care n-o vede. De aceea
     clasa de rezultat a fiecărui motor se citește **din modul**, nu se scrie aici: o hartă care
     numește `obligatii` acolo unde motorul are `obligatiii` cade.
  3. **Ca o coloană declarată MONETARĂ să nu existe printre coloanele produse** — atunci `bani()`
     nu s-ar aplica niciodată, iar sumele ar apărea brute pe ecran (DS cap.4).
  4. **Ca plafonul să taie tăcut.** O secțiune tăiată spune câte are cu totul.
  5. **Ca `fara_zero` să scoată și rânduri nenule** — ar ascunde componente reale.

CALIBRARE ÎN AMÂNDOUĂ DIRECȚIILE (METODA §22): pe rezultate CONSTRUITE, extragerea trebuie să
găsească rândurile puse acolo (pozitiv) **și** să nu inventeze rânduri unde nu sunt (negativ) — plus
proba că un atribut inexistent chiar dă zero, adică exact ce face punctul 2 necesar.

CE NU VERIFICĂ, declarat: dacă rândurile sunt cifrele CORECTE ale declarației (aia e treaba
motorului și a DUKIntegrator), și dacă ecranul le desenează — aia se măsoară viu.
"""
import dataclasses
import importlib

import pytest

from core import declaratii_componente as dc

# Cele nouă din verdictul 1d, lista 5. Scrise aici fiindcă lista e a VERDICTULUI, nu a codului:
# dacă mâine apare a zecea declarație, ea nu intră automat în datoria măsurată atunci.
CELE_NOUA = ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406")


def _clasa_rezultat(tip):
    """Clasa de rezultat a motorului, găsită MECANIC în modulul lui.

    Nu se scrie în test: o listă de nume de clase scrisă aici ar îmbătrâni exact ca harta pe care
    trebuie s-o verifice. Convenția din cod e `Rezultat…`, și e singura din fiecare modul.
    """
    modul = importlib.import_module("core.%s" % tip)
    clase = [o for n, o in vars(modul).items()
             if dataclasses.is_dataclass(o) and isinstance(o, type) and n.startswith("Rezultat")]
    return clase[0] if len(clase) == 1 else None


def test_toate_cele_noua_sunt_acoperite_ori_motivate():
    for tip in CELE_NOUA:
        acoperit = dc.COMPONENTE.keys() | dc.FARA_COMPONENTE.keys()
        assert acoperit >= {tip}, "%s a ieșit din acoperire fără să spună nimeni de ce" % tip
    assert not (set(dc.COMPONENTE) & set(dc.FARA_COMPONENTE)), (
        "un tip nu poate fi și mapat, și declarat imposibil")


def test_motivele_absentei_sunt_scrise_nu_goale():
    """Un motiv gol e tăcere cu altă formă.

    Registrul poate fi GOL — e chiar starea de după R105 —, dar mecanismul rămâne păzit: ce e
    înăuntru trebuie să spună ceva. Anti-vacuul s-a mutat pe hartă, care nu are voie să se golească.
    """
    assert len(dc.COMPONENTE) >= 9, (
        "ANTI-VACUU: harta de componente s-a golit (%d tipuri) — atunci toate probele de mai jos "
        "trec pe nimic" % len(dc.COMPONENTE))
    for tip, motiv in dc.FARA_COMPONENTE.items():
        assert len(motiv.strip()) > 60, "motivul lui %s e prea scurt ca să spună ceva: %r" % (tip, motiv)


def test_d112_isi_desface_acum_cifra():
    """[R105, 30.08.2026] Inversul testului care a stat aici până azi.

    Până la R105, D112 era singura din cele nouă fără componente, iar gardul cerea ca motivul să fie
    ADEVĂRAT: `core.d112` să NU aibă clasă de rezultat. Decizia lui Costin — *„motorul se schimbă"* —
    a făcut motivul fals, iar gardul a căzut, corect. Acum păzește starea nouă: motorul întoarce un
    rezultat, iar declarația e în hartă cu amândouă felurile ei de poziții.
    """
    assert dc.COMPONENTE.keys() >= {"d112"}, "D112 a ieșit din hartă"
    assert _clasa_rezultat("d112") is not None, (
        "`core.d112` n-are clasă de rezultat — R105 s-a întors, iar componentele D112 nu se mai pot citi")
    sectiuni = {s.atribut for s in dc.COMPONENTE["d112"]}
    assert sectiuni == {"obligatii", "asigurati"}, (
        "D112 are DOUĂ feluri de poziții — ce datorează angajatorul, și contribuțiile fiecărui "
        "asigurat; găsite: %s" % sorted(sectiuni))


def _prof_d112(**kw):
    p = {"cui": "14399840", "nume": "TEST SRL", "caen": "6202", "judet": "B",
         "declarant_nume": "POP", "declarant_prenume": "ION", "declarant_functie": "ADMIN"}
    p.update(kw)
    return p


def _sal_d112(**kw):
    b = {"brut": 3000, "cas": 750, "cass": 300, "impozit": 195, "cass_tichete": 0,
         "impozit_tichete": 0, "tichete_nominal": 0, "e83_masa": 0, "e83_vacanta": 0,
         "e83_cultural": 0, "e83_cresa": 0, "ore_zi": 8, "cm": [], "zile_cm": 0,
         "cnp": "1900101410011", "nume": "POPESCU", "prenume": "ION",
         "data_angajare": "2020-01-15"}
    b.update(kw)
    return b


def test_componentele_D112_se_CONFRUNTA_cu_cifra_declarata():
    """[R105] Proba că ce arată ecranul e chiar COMPOZIȚIA cifrei, nu un al doilea calcul.

    Asta e diferența dintre „ruta trimite niște rânduri" și „cifra își arată componentele": suma
    impozitului asiguraților trebuie să fie EXACT obligația 602 a angajatorului, iar suma CAS-ului
    exact obligația 412. Dacă cele două ar putea diverge, componentele n-ar explica nimic — ar fi o
    a doua părere despre aceeași lună.

    Verificat și pe date reale la scriere (30.08.2026): `tenant_005` 267 = 267, `tenant_013`
    204 = 204. Aici se ține închis pe intrări construite, ca să nu depindă de portofoliu.
    """
    from core import d112 as _d112
    _xml, res = _d112._d112_genereaza(
        _prof_d112(), [_sal_d112(), _sal_d112(brut=5000, cas=1250, cass=500, impozit=325,
                                             cnp="2900101410011", nume="IONESCU", prenume="ANA")],
        2026, 8)
    assert len(res.asigurati) == 2, res.asigurati
    obl = {o.cod_oblig: o.datorat for o in res.obligatii}
    assert sum(a.impozit for a in res.asigurati) == obl["602"], (res.asigurati, obl)
    assert sum(a.cas for a in res.asigurati) == obl["412"], (res.asigurati, obl)
    assert sum(a.cass for a in res.asigurati) == obl["432"], (res.asigurati, obl)


def test_confruntarea_ar_PICA_daca_ar_diverge():
    """Calibrarea probei de mai sus: dacă aserția ar fi adevărată orice s-ar întâmpla, n-ar dovedi
    nimic. Un asigurat în plus, nedeclarat în obligații, trebuie să rupă egalitatea."""
    from core import d112 as _d112
    _xml, res = _d112._d112_genereaza(_prof_d112(), [_sal_d112()], 2026, 8)
    obl = {o.cod_oblig: o.datorat for o in res.obligatii}
    fals = list(res.asigurati) + [_d112.AsiguratD112("FANTOMA", 1000, 1000, 250, 100, 65)]
    assert sum(a.impozit for a in fals) != obl["602"], (
        "egalitatea ține și cu un asigurat inventat — deci nu confruntă nimic")


def test_CNP_ul_nu_pleaca_in_componente():
    """Alegere scrisă, nu scăpare: componentele răspund la «din ce e făcută cifra», iar CNP-ul nu
    compune nicio sumă. Contează fiindcă `coada_api.randuri_din_res` PERSISTĂ obiectul ăsta în
    `public.declaratii_depuse.randuri` — deci ce intră aici se și păstrează."""
    import dataclasses as _dc
    from core import d112 as _d112
    campuri = {f.name for f in _dc.fields(_d112.AsiguratD112)}
    assert not (campuri & {"cnp", "CNP", "cod_numeric_personal"}), campuri


@pytest.mark.parametrize("tip", sorted(dc.COMPONENTE))
def test_harta_arata_spre_atribute_care_exista(tip):
    """Modul de eșec care nu crapă: un atribut greșit dă zero rânduri, adică arată ca «goală»."""
    clasa = _clasa_rezultat(tip)
    assert clasa is not None, "n-am găsit clasa de rezultat a lui %s" % tip
    campuri = {f.name for f in dataclasses.fields(clasa)}
    for sec in dc.COMPONENTE[tip]:
        assert sec.atribut in campuri, (
            "%s: secțiunea %r citește `%s`, care nu există în %s — ar întoarce zero rânduri, "
            "și zero rânduri arată identic cu o declarație goală"
            % (tip, sec.nume, sec.atribut, clasa.__name__))


@pytest.mark.parametrize("tip", sorted(dc.COMPONENTE))
def test_coloanele_monetare_exista_printre_coloanele_produse(tip):
    """O coloană monetară care nu se potrivește cu nicio coloană produsă = sume brute pe ecran."""
    clasa = _clasa_rezultat(tip)
    for sec in dc.COMPONENTE[tip]:
        if not sec.monetare:
            continue
        if sec.chei:
            disponibile = set(sec.chei) | set(sec.valori)
        else:
            # secțiune-listă: coloanele sunt câmpurile elementului, deci ale tipului din adnotare
            camp = next(f for f in dataclasses.fields(clasa) if f.name == sec.atribut)
            disponibile = _campuri_element(camp, tip, sec)
        lipsa = set(sec.monetare) - disponibile
        assert not lipsa, ("%s / %r: coloane declarate monetare care nu se produc: %s (produse: %s)"
                           % (tip, sec.nume, sorted(lipsa), sorted(disponibile)))


def _campuri_element(camp, tip, sec):
    """Câmpurile unui rând dintr-o secțiune-listă, luate din dataclass-ul elementului.

    Adnotarea e `list`, fără parametru, deci tipul elementului nu se poate citi din ea. Se ia din
    modul dataclass-ul al cărui set de câmpuri conține toate coloanele monetare declarate — iar dacă
    niciunul nu se potrivește, testul cade, ceea ce e chiar rezultatul dorit.
    """
    modul = importlib.import_module("core.%s" % tip)
    for _n, o in vars(modul).items():
        if dataclasses.is_dataclass(o) and isinstance(o, type) and not _n.startswith("Rezultat"):
            campuri = {f.name for f in dataclasses.fields(o)}
            # Proprietatile declarate sunt si ele coloane produse — vezi `Sectiune.proprietati`.
            for p in sec.proprietati:
                assert isinstance(getattr(o, p, None), property) or hasattr(o, p), (
                    "%s: proprietatea declarata %r nu exista pe %s" % (tip, p, _n))
            campuri |= set(sec.proprietati)
            if set(sec.monetare) <= campuri:
                return campuri
    return set()


# ── calibrarea extragerii, pe rezultate CONSTRUITE ────────────────────────────────────────────────

@dataclasses.dataclass
class _RandFals:
    cod: str = "101"
    suma: int = 0


class _ResFals:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_extrage_randurile_dintr_o_lista():
    sec = dc.Sectiune("Test", "lista", monetare=("suma",))
    randuri = dc._randuri(_ResFals(lista=[_RandFals("101", 500), _RandFals("102", 700)]), sec)
    assert randuri == [{"cod": "101", "suma": 500}, {"cod": "102", "suma": 700}]


def test_extrage_randurile_dintr_un_dictionar_cu_cheie_tuplu():
    sec = dc.Sectiune("Test", "d", chei=("tip", "țară"), valori=("bază", "TVA"))
    randuri = dc._randuri(_ResFals(d={("L", "DE"): [100, 19]}), sec)
    assert randuri == [{"tip": "L", "țară": "DE", "bază": 100, "TVA": 19}], randuri


def test_fara_zero_scoate_zerourile_si_pastreaza_restul():
    sec = dc.Sectiune("Test", "R", chei=("rând",), valori=("valoare",), fara_zero=True)
    randuri = dc._randuri(_ResFals(R={"R1": 0, "R2": 250, "R3": 0, "R4": -30}), sec)
    assert [r["rând"] for r in randuri] == ["R2", "R4"], randuri


def test_proprietatile_declarate_ajung_in_rand():
    """`dataclasses.asdict` NU vede `@property` — iar la D710 tocmai proprietatea e cifra care
    ajunge pe declarație (`suma_plata = suma_dat - suma_ded`). Fără rândul ăsta, compoziția ar fi
    arătat tot afară de ce contează."""
    from core.d710 import ObligatieRect
    o = ObligatieRect(cod_oblig="121", suma_dat_i=1000, suma_dat_c=800, suma_ded_i=300)
    rand = dc._rand_din_lista(o, ("suma_plata_i", "suma_plata_c"))
    assert rand["suma_plata_i"] == 700 and rand["suma_plata_c"] == 800, rand
    # și proba inversă: fără declarație, proprietatea NU apare — deci rândul de mai sus chiar testează ceva
    assert "suma_plata_i" not in dc._rand_din_lista(o)


def test_un_atribut_inexistent_da_zero_randuri():
    """Proba care justifică `test_harta_arata_spre_atribute_care_exista`: nu crapă, tace."""
    assert dc._randuri(_ResFals(), dc.Sectiune("Test", "nu_exista")) == []


def test_plafonul_se_declara_nu_taie_tacut():
    sec = dc.Sectiune("Test", "lista")
    res = _ResFals(lista=[_RandFals(str(i), i) for i in range(dc.LIMITA_RANDURI + 25)])
    dc.COMPONENTE["_test"] = (sec,)
    try:
        c = dc.componente("_test", res)
    finally:
        del dc.COMPONENTE["_test"]
    s = c["sectiuni"][0]
    assert s["total"] == dc.LIMITA_RANDURI + 25
    assert s["aratate"] == dc.LIMITA_RANDURI
    assert len(s["randuri"]) == dc.LIMITA_RANDURI
    assert s["aratate"] < s["total"], "tăierea trebuie să se VADĂ în răspuns"


def test_tip_nemapat_spune_ca_nu_stie_nu_intoarce_lista_goala():
    """O listă goală ar arăta identic cu «declarația n-are nimic» — exact rotunjirea interzisă."""
    c = dc.componente("dInexistent", _ResFals())
    assert c["acoperire"] == "necunoscuta"
    # `acoperire` e nomenclator ÎNCHIS — deci se poate asertă pe MULȚIME, nu pe text.
    assert set(dc.ACOPERIRE) >= {c["acoperire"]}
    # Și nicio proză în payload: motivul trăiește în cod, nu în răspuns (vezi `componente`).
    assert "motiv" not in c, c


def test_absenta_motivata_nu_arata_ca_o_declaratie_goala():
    """Mecanismul se probează pe o intrare SINTETICĂ, nu pe una vie.

    Până la R105 se proba pe `d112`, singura intrare reală — iar când ea a ieșit, proba a rămas fără
    obiect. E aceeași lecție ca METODA §29, pe alt gard: *o probă ancorată pe instanța care urmează
    să fie reparată dispare odată cu reparația.* Registrul e gol azi, dar mecanismul trebuie să
    rămână păzit pentru următorul tip care nu-și poate desface cifra.
    """
    dc.FARA_COMPONENTE["_test"] = ("motiv sintetic, destul de lung ca să treacă pragul de mai sus "
                                   "și să arate că un motiv scurt n-ar trece")
    try:
        c = dc.componente("_test", _ResFals())
    finally:
        del dc.FARA_COMPONENTE["_test"]
    assert c["acoperire"] == "absenta"
    assert c["sectiuni"] == [] and c["total"] == 0
    # Motivul NU pleacă în payload — dar există în cod, și e verificat de `test_motivele_absentei_...`.
    assert "motiv" not in c, "proza n-are ce căuta în răspunsul rutei (decizia din 21.08)"


def test_valorile_pleaca_serializabile():
    """`Decimal` și datele nu pot pleca așa cum sunt — D406 poartă amândouă."""
    import datetime
    import decimal
    import json
    sec = dc.Sectiune("Test", "lista")
    res = _ResFals(lista=[{"suma": decimal.Decimal("12.34"), "zi": datetime.date(2026, 8, 30)}])
    randuri = dc._randuri(res, sec)
    json.dumps(randuri)  # crapă dacă a rămas ceva neserializabil
    assert randuri == [{"suma": 12.34, "zi": "2026-08-30"}]
