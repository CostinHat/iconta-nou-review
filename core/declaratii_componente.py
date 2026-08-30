# -*- coding: utf-8 -*-
"""Din ce e făcută cifra care pleacă la ANAF — componentele unei declarații.

DE CE EXISTĂ (30.08.2026, a patra poziție din lista 5 — de fapt nouă din douăsprezece). Pasul 1c a
măsurat, pe răspunsul VIU al rutei, pe tot portofoliul: **0 din 92 de ieșiri își arată
componentele**. Ruta care produce și validează întoarce `stare`, `xml_b64` și `operatiuni` — **un
NUMĂR**. Contabilul citește *„valid, 18 operațiuni"* și **nu poate vedea care 18**. Un contor nu e o
componentă: `{"operatiuni": 18}` nu se poate verifica, se poate doar crede.

CE S-A DOVEDIT LA CITIRE, și schimbă prețul poziției: componentele **există deja** pe obiectele de
rezultat ale motoarelor — `d100.obligatii`, `d205.beneficiari`, `d301.operatiuni`, `d300.R`,
`d101.P`, `d390.ops`, `d394.op1`, cele trei liste ale lui `d406`. Nu lipsea calculul, lipsea
**transportul**. De aceea nu se calculează nimic aici: se **citește** ce a produs motorul.

O SINGURĂ HARTĂ, nu nouă bucăți de cod. Fiecare tip de declarație spune, într-un singur loc, în ce
atribut stau componentele și cum se numesc coloanele. Alternativa — un serializator scris de mână
pentru fiecare — ar fi produs nouă liste care se pot despica de motorul lor în tăcere, exact clasa
pe care fluturașul a plătit-o deja (`stat_plata_api.rand_fluturas`).

CE NU POATE ARĂTA, și se spune în răspuns, nu se tace: `FARA_COMPONENTE`. Un tip care nu-și poate
desface cifra întoarce `acoperire="absenta"` **cu motivul scris**, ca ecranul să poată spune *ce nu
poate spune verificarea asta* (DS cap.25.4) — nu o listă goală, care ar arăta identic cu „declarația
n-are nimic în ea".

FĂRĂ PLAFON TĂCUT. O secțiune mai lungă decât `LIMITA_RANDURI` se taie, dar **spune** că s-a tăiat
și câte sunt cu totul (`total` vs `aratate`). O tăiere netiută s-ar citi ca „atât e tot".
"""
import dataclasses
import datetime
import decimal

# Peste atâtea rânduri o secțiune se taie — D406 poartă tot registrul-jurnal al lunii, iar un
# răspuns de zeci de mii de rânduri nu e o compoziție, e o descărcare. Tăierea se DECLARĂ.
LIMITA_RANDURI = 500


class Sectiune:
    """O secțiune de componente: din ce atribut se citește și cum se numesc coloanele.

    Trei forme, fiindcă atâtea produc motoarele:
      - `chei` gol -> atributul e o LISTĂ de rânduri (dataclass sau dict): fiecare rând e un rând;
      - `chei` dat -> atributul e un DICȚIONAR: cheia se desface în coloanele din `chei` (tuplu sau
        valoare simplă), iar valoarea în coloanele din `valori`.
    `fara_zero` scoate rândurile a căror singură valoare e 0 — pentru `d300.R` și `d101.P`, unde
    dicționarul poartă și pozițiile necompletate, iar alea nu sunt componente ale cifrei.
    """

    def __init__(self, nume, atribut, chei=(), valori=(), fara_zero=False, monetare=(),
                 proprietati=()):
        self.nume = nume
        self.atribut = atribut
        self.chei = tuple(chei)
        self.valori = tuple(valori)
        self.fara_zero = fara_zero
        # Care coloane sunt SUME. Se declara aici fiindca serverul stie, iar ecranul nu: un rand
        # generic e un dictionar, si un `1234` poate fi la fel de bine un cod bugetar. DS cap.4 cere
        # `bani()` pe orice suma afisata, iar ghicitul dupa numele coloanei ar fi o regula pe text.
        self.monetare = tuple(monetare)
        # `@property` de pe randul-dataclass. `dataclasses.asdict` NU le vede, iar la D710 tocmai
        # ele sunt cifra care ajunge pe declaratie (`suma_plata = suma_dat - suma_ded`, clamp la 0).
        # Se DECLARA, nu se descopera prin reflexie: o proprietate chemata din intamplare poate
        # calcula orice, iar aici se citeste un rezultat, nu se produce unul.
        self.proprietati = tuple(proprietati)


# HARTA. Numele coloanelor sunt pentru OM (deci cu diacritice); numele atributelor sunt ale codului.
COMPONENTE = {
    "d100": (Sectiune("Obligații de plată", "obligatii", monetare=("suma_dat",)),),
    # D710 nu e „D100 cu alt nume": `ObligatieRect` poarta suma INITIALA si cea CORECTATA, pe
    # fiecare latura, plus deducerile — iar suma care ajunge pe declaratie e o `@property`.
    "d710": (Sectiune("Obligații rectificate", "obligatii",
                      monetare=("suma_dat_i", "suma_dat_c", "suma_ded_i", "suma_ded_c",
                                "suma_plata_i", "suma_plata_c"),
                      proprietati=("suma_plata_i", "suma_plata_c")),),
    "d205": (Sectiune("Beneficiari", "beneficiari",
                      monetare=("baza1", "imp1", "castig1", "pierdere1", "divid_d", "divid_p")),),
    "d301": (Sectiune("Operațiuni", "operatiuni", monetare=("val_valuta", "baza", "tva")),),
    "d300": (Sectiune("Rânduri completate", "R",
                      chei=("rând",), valori=("valoare",), fara_zero=True,
                      monetare=("valoare",)),),
    "d101": (Sectiune("Poziții completate", "P",
                      chei=("poziție",), valori=("valoare",), fara_zero=True,
                      monetare=("valoare",)),),
    "d390": (Sectiune("Operațiuni intracomunitare", "ops",
                      chei=("tip", "țară", "cod partener", "denumire partener"),
                      valori=("bază",), monetare=("bază",)),),
    "d394": (Sectiune("Operațiuni pe partener și cotă", "op1",
                      chei=("tip", "tip partener", "cotă", "CUI partener", "denumire partener"),
                      valori=("număr facturi", "bază", "TVA"), monetare=("bază", "TVA")),
             Sectiune("Serii de facturi declarate", "serii"),),
    # D406 poarta structuri de SAF-T pe care nu le-am confruntat camp cu camp; coloanele monetare
    # nu se declara din presupunere - se lasa nemarcate, si se spune aici de ce.
    "d406": (Sectiune("Note contabile", "note"),
             Sectiune("Facturi de vânzare", "facturi_vanzare"),
             Sectiune("Facturi de cumpărare", "facturi_cumparare"),),
}

# Tipurile care NU-și pot desface cifra, fiecare cu motivul ȘI cu ce ar trebui făcut. Absența cu
# motiv nu e același lucru cu absența — interdicția 64, și cap.25.4 din Design System.
FARA_COMPONENTE = {
    "d112": ("generatorul (`core.d112._d112_genereaza`) întoarce `(xml, avertismente)` — nu există "
             "obiect de rezultat din care să se citească pozițiile. Componentele D112 sunt "
             "contribuțiile fiecărui salariat, iar ca să ajungă până aici generatorul trebuie să "
             "le ÎNTOARCĂ, nu doar să le scrie în XML. E o schimbare de motor, nu de rută, și nu "
             "se face pe furiș într-o tură de transport."),
}


def _simplu(v):
    """O valoare pe care o poate purta un JSON. `Decimal` și datele nu pot pleca așa cum sunt."""
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return {k: _simplu(x) for k, x in dataclasses.asdict(v).items()}
    if isinstance(v, dict):
        return {str(k): _simplu(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_simplu(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)


def _rand_din_lista(element, proprietati=()):
    if dataclasses.is_dataclass(element) and not isinstance(element, type):
        rand = {k: _simplu(v) for k, v in dataclasses.asdict(element).items()}
        for p in proprietati:
            rand[p] = _simplu(getattr(element, p))
        return rand
    if isinstance(element, dict):
        return {str(k): _simplu(v) for k, v in element.items()}
    return {"valoare": _simplu(element)}


def _rand_din_dict(cheie, valoare, sec):
    rand = {}
    parti = cheie if isinstance(cheie, tuple) else (cheie,)
    for i, nume in enumerate(sec.chei):
        rand[nume] = _simplu(parti[i]) if i < len(parti) else None
    vparti = valoare if isinstance(valoare, (list, tuple)) else (valoare,)
    for i, nume in enumerate(sec.valori):
        rand[nume] = _simplu(vparti[i]) if i < len(vparti) else None
    return rand


def _randuri(res, sec):
    sursa = getattr(res, sec.atribut, None)
    if not sursa:
        return []
    if sec.chei:
        randuri = [_rand_din_dict(k, v, sec) for k, v in sursa.items()]
        if sec.fara_zero:
            randuri = [r for r in randuri
                       if any(v not in (0, 0.0, None, "") for n, v in r.items()
                              if n in sec.valori)]
        return randuri
    return [_rand_din_lista(e, sec.proprietati) for e in sursa]


# Nomenclator INCHIS al acoperirii. E STRUCTURA, nu text: raspunsul rutei poarta unul din cele trei
# cuvinte, iar propozitia pentru om o scrie ECRANUL. Prima forma trimitea si un `motiv` in proza -
# adica exact ce interzice decizia din 21.08 (o afirmatie e un obiect, nu un sir), si a fost prinsa
# de `core/test_afirmatii_tipate.py` la prima rulare a suitei. Motivul TEHNIC nu s-a pierdut: sta in
# `FARA_COMPONENTE`, unde il citeste omul care repara, si unde il verifica gardul.
ACOPERIRE = ("completa", "absenta", "necunoscuta")


def componente(tip, res):
    """{"acoperire", "sectiuni", "total"} — din ce e făcută declarația.

    `acoperire`: `completa` (componentele sunt aici) · `absenta` (tipul nu le poate da; motivul
    tehnic e în `FARA_COMPONENTE`) · `necunoscuta` (tip nemapat — se spune, nu se tace).
    """
    t = (tip or "").lower()
    if t in FARA_COMPONENTE:
        return {"acoperire": "absenta", "sectiuni": [], "total": 0}
    if t not in COMPONENTE:
        return {"acoperire": "necunoscuta", "sectiuni": [], "total": 0}
    sectiuni, total = [], 0
    for sec in COMPONENTE[t]:
        randuri = _randuri(res, sec)
        total += len(randuri)
        sectiuni.append({"nume": sec.nume, "total": len(randuri),
                         "aratate": min(len(randuri), LIMITA_RANDURI),
                         "monetare": list(sec.monetare),
                         "randuri": randuri[:LIMITA_RANDURI]})
    return {"acoperire": "completa", "sectiuni": sectiuni, "total": total}
