# -*- coding: utf-8 -*-
"""Registrul-inventar (cod 14-1-2), al doilea dintre cele trei registre obligatorii.

DE UNDE VINE, citit la sursa (lista 3, 30.08.2026). **Legea 82/1991, art. 20**: *„Registrele de
contabilitate obligatorii sunt: Registrul-jurnal, Registrul-inventar si Cartea mare."* Continutul
e la **OMFP 2634/2015, Anexa 2, cod 14-1-2**, specificat integral: sase coloane.

**Ce nu se poate deriva, si de ce registrul are formular.** Coloana 3 (*valoarea contabila*) e
soldul din balanta — se deriva. **Coloana 4 (*valoarea de inventar*) nu se deriva din nimic**:
norma spune ca registrul se completeaza *pe baza listelor de inventariere si a proceselor-verbale*,
adica pe baza numararii faptice. Aplicatia nu poate sti cate bucati sunt in magazie.

**Cel mai periculos default posibil.** Daca `valoare_inventar` s-ar completa implicit cu
`valoare_contabila`, registrul ar iesi PERFECT: zero diferente, pe toate conturile, in fiecare an.
Ar arata exact ca o inventariere facuta bine — si ar fi o inventariere care nu s-a facut deloc. E
acelasi defect ca „un necunoscut rotunjit la «stiu ca nu»", dar cu miza mai mare: aici minciuna e
semnata. De-aia `valoare_inventar` e CERUTA, si de-aia nu are default nicaieri.
"""
from decimal import Decimal

from core.afirmatii import afirmatie
from core.common import Temei
from core.unde import Unde

MODUL = "registru_inventar"

#: Nomenclator INCHIS. Norma numeste exact trei ocazii la care se intocmeste registrul; nu e o
#: enumerare exemplificativa, e lista lor.
MOMENTE = ("inceput_activitate", "sfarsit_exercitiu", "incetare_activitate")

TEMEI_OBLIGATIE = Temei(
    "Lege", 82, 1991, art="20",
    data_in="1992-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/legea_82_1991_consolidat.txt",
    text_citat=("Registrele de contabilitate obligatorii sunt: Registrul-jurnal, Registrul-inventar "
                "si Cartea mare. Intocmirea, editarea si pastrarea registrelor de contabilitate se "
                "efectueaza conform normelor elaborate de Ministerul Finantelor Publice"))

TEMEI_CONTINUT = Temei(
    "OMFP", 2634, 2015, art="anexa 2", lit="14-1-2",
    data_in="2016-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt",
    text_citat=("Registrul-inventar serveste ca document contabil obligatoriu de inregistrare a "
                "rezultatelor inventarierii elementelor de natura activelor, datoriilor si "
                "capitalurilor proprii. Registrul-inventar se intocmeste la inceputul activitatii, "
                "la sfarsitul exercitiului financiar sau cu ocazia incetarii activitatii, fara "
                "stersaturi si fara spatii libere, pe baza datelor cuprinse in listele de "
                "inventariere si, respectiv, in procesele-verbale de inventariere a elementelor de "
                "natura activelor, datoriilor si capitalurilor proprii, prin gruparea acestora pe "
                "conturi sau grupe de conturi, dupa caz. In coloana 1 se inscrie numarul curent al "
                "operatiunilor inregistrate in ordine cronologica, de la deschiderea registrului "
                "pana la sfarsitul exercitiului financiar, sau incetarea activitatii. In coloana 2 "
                "vor fi recapitulate elementele inventariate, detaliat pe fiecare cont de activ si "
                "de pasiv, conturile de valori materiale putand fi defalcate pe gestiuni. In "
                "coloana 3 se inscrie valoarea contabila a elementelor inventariate. In coloana 4 "
                "se inscrie valoarea de inventar a elementelor de natura activelor, datoriilor si "
                "capitalurilor proprii, stabilita cu ocazia evaluarii la inventariere (pe baza "
                "listelor de inventariere si a proceselor-verbale de inventariere). In coloana 5 se "
                "trec diferentele din evaluare, calculate ca diferenta intre valoarea contabila si "
                "valoarea de inventar. In coloana 6 se mentioneaza cauzele diferentelor (deprecieri, "
                "dezmembrari, dezasortari, calamitati, terti neidentificati etc.)"))

#: Cele SASE coloane ale formularului, in ordinea din norma. `nr_curent` si `diferenta` NU se
#: primesc de la om: prima se deriva, a doua se calculeaza.
COLOANE = ("nr_curent", "element", "valoare_contabila", "valoare_inventar", "diferenta", "cauza")

#: Luna de referinta a soldurilor propuse. NU e un default de conveniență: registrul se intocmeste
#: *„la sfarsitul exercitiului financiar"*, iar exercitiul se incheie la 31 decembrie — deci luna e
#: o alegere din norma, si poarta temeiul ei lipit de valoare, nu ca o cheie-sora.
LUNA_SFARSIT_EXERCITIU = (12, Temei(
    "Lege", 82, 1991, art="27",
    data_in="1992-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/legea_82_1991_consolidat.txt",
    text_citat="Exercitiul financiar incepe la 1 ianuarie si se incheie la 31 decembrie"))

#: Ce se cere la INSCRIERE. `cauza` lipseste de aici fiindca e ceruta CONDITIONAT — vezi
#: `valideaza`. `cont` nu e o coloana a formularului, dar norma cere elementele *detaliat pe fiecare
#: cont de activ si de pasiv*, deci contul e ce face randul identificabil, nu o eticheta in plus.
CAMPURI_CERUTE = ("cont", "element", "valoare_contabila", "valoare_inventar")


class InregistrareIncompleta(ValueError):
    """Un camp cerut de norma lipseste. Poarta `camp` si `temei` ca DATE, nu doar in mesaj."""

    def __init__(self, mesaj, camp=None, temei=None):
        super().__init__(mesaj)
        self.camp = camp
        self.temei = temei


def _gol(v):
    return v is None or (isinstance(v, str) and not v.strip())


def _dec(v):
    return Decimal(str(v))


def diferenta(valoare_contabila, valoare_inventar):
    """Coloana 5, prin definitia din norma: *diferenta intre valoarea contabila si valoarea de
    inventar*. Se CALCULEAZA — stocata, ar putea sa le contrazica pe amandoua."""
    return _dec(valoare_contabila) - _dec(valoare_inventar)


def valideaza(date):
    """Ridica `InregistrareIncompleta` la primul camp cerut care lipseste.

    Doua reguli care nu sunt evidente din formular:

    1. **`valoare_inventar` e ceruta, si nu are default.** Completata implicit cu valoarea
       contabila, ar produce o inventariere perfecta care nu s-a facut.
    2. **`cauza` e ceruta CAND EXISTA o diferenta.** Norma zice *„in coloana 6 se mentioneaza
       cauzele diferentelor"* — o diferenta fara cauza e un minus pe care nu-l explica nimeni.
    """
    for c in CAMPURI_CERUTE:
        if _gol(date.get(c)):
            raise InregistrareIncompleta(
                "Registrul-inventar cere «%s», iar campul e gol. Norma: %s" % (c, TEMEI_CONTINUT),
                camp=c, temei=str(TEMEI_CONTINUT))
    if date.get("momentul") not in MOMENTE:
        raise InregistrareIncompleta(
            "moment necunoscut %r; norma numeste exact trei: %s"
            % (date.get("momentul"), ", ".join(MOMENTE)), camp="momentul",
            temei=str(TEMEI_CONTINUT))
    d = diferenta(date["valoare_contabila"], date["valoare_inventar"])
    if d != 0 and _gol(date.get("cauza")):
        raise InregistrareIncompleta(
            "randul are o diferenta de %s, iar coloana 6 cere cauza ei. O diferenta fara cauza e un "
            "plus sau un minus pe care nu-l explica nimeni. Norma: %s" % (d, TEMEI_CONTINUT),
            camp="cauza", temei=str(TEMEI_CONTINUT))
    return d


def adauga(conn, schema, exercitiu, date):
    """Inscrie un rand. `nr_curent` se DERIVA — norma il cere *in ordine cronologica, de la
    deschiderea registrului*, nu tastat."""
    valideaza(date)
    campuri = list(CAMPURI_CERUTE) + [c for c in ("gestiune", "cauza", "data_inventariere",
                                                  "document") if not _gol(date.get(c))]
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(nr_curent), 0) + 1 FROM {s}.registru_inventar "
                    "WHERE exercitiu = %s AND momentul = %s".format(s=schema),
                    (exercitiu, date["momentul"]))
        nr = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO {s}.registru_inventar (exercitiu, momentul, nr_curent, {c}) "
            "VALUES (%s, %s, %s, {p}) RETURNING id".format(
                s=schema, c=", ".join(campuri), p=", ".join(["%s"] * len(campuri))),
            [exercitiu, date["momentul"], nr] + [date.get(c) for c in campuri])
        iid = cur.fetchone()[0]
    conn.commit()
    return {"id": iid, "nr_curent": nr}


def randuri(conn, schema, exercitiu, momentul):
    from psycopg2.extras import RealDictCursor
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM {s}.registru_inventar WHERE exercitiu = %s AND momentul = %s "
                    "ORDER BY nr_curent".format(s=schema), (exercitiu, momentul))
        return [dict(r) for r in cur.fetchall()]


def _simplu(v):
    import datetime
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def solduri_de_pornire(conn, schema, an, luna=LUNA_SFARSIT_EXERCITIU[0]):
    """Coloana 3 PROPUSA, din balanta: contul, denumirea si soldul lui la finalul lunii.

    E o PROPUNERE pentru completare, nu un rand de registru. Nu atinge coloana 4 si nu creeaza
    nimic: valoarea de inventar ramane a omului care a numarat. Un ajutor care ar completa si
    coloana 4 ar transforma registrul in oglinda balantei — adica exact in documentul care nu
    dovedeste nimic.
    """
    from core import documente_api
    out = []
    for r in documente_api.balanta(conn, schema, an, luna):
        d, c = _dec(r.get("sf_d") or 0), _dec(r.get("sf_c") or 0)
        if d == 0 and c == 0:
            continue
        # `sens` merge alaturi de marime, nu se pierde in `abs()`: valoarea contabila a unei datorii
        # e un sold CREDITOR, iar un registru care arata doar cifra il face sa arate ca un activ.
        out.append({"cont": r["cont"], "element": r.get("denumire") or "",
                    "sens": "D" if d else "C",
                    "valoare_contabila": float(d if d else c)})
    return out


def registru(conn, schema, exercitiu, momentul="sfarsit_exercitiu"):
    """Registrul-inventar, ca AFIRMATIE — cu temeiul lui si cu ce NU acopera."""
    if momentul not in MOMENTE:
        raise ValueError("moment necunoscut: %r" % momentul)
    rs = []
    for r in randuri(conn, schema, exercitiu, momentul):
        r = {k: _simplu(v) for k, v in r.items()}
        r["diferenta"] = float(diferenta(r["valoare_contabila"], r["valoare_inventar"]))
        rs.append(r)
    return afirmatie(
        "fapt", tip="registru_inventar",
        motiv="Registrul-inventar (cod 14-1-2), tinut potrivit art. 20 din Legea 82/1991",
        temei_completitudine=(
            "toate randurile inscrise in `registru_inventar` pentru exercitiul %d, momentul %r, in "
            "ordinea numarului curent. **Cuprinde ce s-a inventariat si s-a inscris** — coloana 4 "
            "(valoarea de inventar) vine din numararea faptica, nu din balanta, deci un registru "
            "gol NU inseamna «nicio diferenta», inseamna «nicio inventariere inscrisa»"
            % (exercitiu, momentul)),
        an=exercitiu, luna=None, unde=Unde("registru", "inventar"),
        **{
        "momentul": momentul,
        "randuri": rs,
        "temei_obligatie": str(TEMEI_OBLIGATIE),
        "temei": str(TEMEI_CONTINUT),
        "coloane": list(COLOANE),
        "campuri_cerute": list(CAMPURI_CERUTE),
        "total_valoare_contabila": float(sum(_dec(r["valoare_contabila"]) for r in rs)),
        "total_valoare_inventar": float(sum(_dec(r["valoare_inventar"]) for r in rs)),
        "randuri_cu_diferenta": sum(1 for r in rs if r["diferenta"] != 0),
        })
