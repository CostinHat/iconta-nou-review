"""
curs_bnr.py — curs valutar BNR pentru facturi in valuta.

REGULA LEGALA (verificata la sursa, art. 290 alin.2 Cod fiscal + Norme HG 1/2016 pct.35):
  Pentru o operatiune in valuta, baza de impozitare TVA se converteste in lei folosind
  "ultimul curs de schimb comunicat de BNR" = cursul comunicat in ziua anterioara,
  valabil pentru ziua urmatoare. In practica: pentru o factura cu data X, cursul folosit
  este cel mai recent curs BNR publicat cu data_cube <= X (ziua bancara anterioara/curenta).
  Cursul se fixeaza la emitere si NU se mai recalculeaza (nici la incasare, nici la regularizare).
  Art. 319: TVA colectata trebuie exprimata SI in lei pe factura, chiar daca restul e in valuta.

SURSA OFICIALA BNR — MUTATA pe `curs.bnr.ro` (verificat la sursa 04.09.2026, de pe server):
  - ultimele 10 zile: https://curs.bnr.ro/nbrfxrates10days.xml   (200, 10 zile BANCARE)
  - arhiva anuala:     https://curs.bnr.ro/files/xml/years/nbrfxratesYYYY.xml  (200)
  - cursul zilei:      https://curs.bnr.ro/nbrfxrates.xml        (200)
  - schema:            https://curs.bnr.ro/xsd/nbrfxrates.xsd    (200)
  Body/Cube[@date]/Rate[@currency, @multiplier?].

  **CE S-A MUTAT, si de ce nu era destul sa schimb gazda** (R130, masurat 03-04.09.2026):
  `www.bnr.ro/nbrfxrates10days.xml` raspunde `302` catre pagina de start (`HEAD` da `404`), iar
  ultima zi ajunsa in cache era **10.07.2026** — deci preluarea mergea si s-a oprit in tacere.
  Dar a doua schimbare era invizibila din URL: **namespace-ul XML a trecut de la `http://` la
  `https://www.bnr.ro/xsd`**. Masurat: pe continutul nou, `parse_xml` intorcea **0 zile** — adica
  exact felul de esec pe care campania il vaneaza, un gol care arata ca un raspuns. De-aia
  namespace-ul nu se mai PRESUPUNE: se **citeste din radacina**, iar un document a carui radacina
  nu e `DataSet` sau care n-are `Body` ridica `FormatNecunoscut`, in loc sa intoarca `{}`.
  Unele valute au multiplier=100 (HUF, JPY, KRW, ...) => curs real = valoare / multiplier.
  OrigCurrency=RON. BNR blocheaza IP-urile cu trafic repetat -> stocare locala obligatorie.

ARHITECTURA:
  - parsare/selectie = PURA (fara retea, fara DB) -> testabila.
  - preluare retea + cache DB (public.curs_bnr_zilnic) = la margine.
  - RON -> curs 1.0 fara apel BNR.
  - BNR inaccesibil -> ridica CursIndisponibil (frontend ofera: reincearca / manual).
"""

from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import xml.etree.ElementTree as ET

#: PRAGUL DE VECHIME al unui curs, in zile CALENDARISTICE, intre data cursului si data facturii.
#: **Decizie de produs, nu norma fiscala** — Costin, 04.09.2026, verbatim: *„pragul e 5 zile
#: calendaristice — acopera un weekend prelungit cu sarbatori legale; peste atat nu mai e pauza de
#: publicare, e flux rupt."* Nu e sursat cu `Temei` fiindca nu exista act care sa-l ceara: legea
#: (art. 290 alin.2 CF) spune sa se foloseasca *ultimul curs comunicat*, nu cat de vechi poate fi.
#: Cifra alege cat de departe de „ultimul comunicat" mai acceptam sa mergem in tacere.
PRAG_VECHIME_ZILE = 5

URL_10ZILE = "https://curs.bnr.ro/nbrfxrates10days.xml"
URL_AN = "https://curs.bnr.ro/files/xml/years/nbrfxrates{an}.xml"


class CursIndisponibil(Exception):
    """BNR inaccesibil / cursul nu a putut fi preluat. Frontend: reincearca sau manual."""


class CursPreaVechi(ValueError):
    """Cursul cel mai recent pe care BNR il are pentru data ceruta e mai vechi decat pragul.

    **NU e subclasa de `CursIndisponibil`**, deliberat: cele doua stari cer raspunsuri diferite, iar
    un `except CursIndisponibil` care ar inghiti-o i-ar da mesajul gresit („reincearca"). E subclasa
    de `ValueError`, deci apelantii care traduc deja `ValueError` in `422` (decontarea valutara,
    reevaluarea soldurilor) raspund omului, nu cu `500`.

    Poarta cursul GASIT, nu doar refuzul: contabilul care introduce cursul de mana trebuie sa vada
    de la ce porneste."""
    def __init__(self, moneda, data_curs, curs, vechime_zile, prag_zile):
        self.moneda, self.data_curs, self.curs = moneda, data_curs, curs
        self.vechime_zile, self.prag_zile = vechime_zile, prag_zile
        super().__init__(
            "Cel mai recent curs BNR pentru %s la data cerută e din %s — mai vechi cu %d zile decât "
            "pragul de %d. Peste atât nu mai e pauză de publicare, e flux întrerupt, iar TVA-ul în "
            "lei s-ar calcula cu o cifră care nu mai e a zilei. Cursul găsit: %s."
            % (moneda, data_curs.isoformat(), vechime_zile, prag_zile, curs))


class FormatNecunoscut(ValueError):
    """XML-ul adus nu e cel asteptat de la BNR — radacina nu e `DataSet`, sau n-are `Body`.

    **De ce ridica in loc sa intoarca `{}`** (R130, 04.09.2026): pana azi, un document cu alta
    forma dadea o harta goala, iar apelantul o citea ca „BNR n-are cursul" — adica o schimbare de
    format arata identic cu o zi fara cotatie. Chiar asta s-a intamplat: namespace-ul a trecut la
    `https://`, iar aplicatia a raportat luni intregi „cursul nu e disponibil momentan"."""


class MonedaNecotata(CursIndisponibil):
    """[probare invalid lot 2, 03.09.2026] Cursul lipseste fiindca MONEDA nu e cotata de BNR, nu
    fiindca reteaua a picat. Doua stari diferite care aveau acelasi raspuns — „nu e disponibil
    MOMENTAN" —, iar diferenta nu e de nuanta: pe prima, „reincearca mai tarziu" nu se va
    intampla niciodata, iar „introdu cursul manual" ar baga in contabilitate o factura intr-o
    moneda inexistenta. Subclasa, deci `except CursIndisponibil` de dinainte ramane valabil."""
    def __init__(self, moneda, cotate=()):
        self.moneda = moneda
        self.cotate = tuple(sorted(cotate))
        super().__init__(
            "Moneda %r nu e cotată de BNR, deci factura nu se poate exprima în lei. "
            "Verifică simbolul (trei litere, ex. EUR, USD). %s"
            % (moneda,
               ("Monedele din ultimul nomenclator citit de la BNR: "
                + ", ".join(self.cotate) + ".") if self.cotate
               else "Lista monedelor cotate n-a putut fi citită acum."))


# ============================================================
#  PUR — parsare XML BNR -> {data(date): {moneda: Decimal}}
# ============================================================
def parse_xml(continut: str) -> dict:
    """
    Parseaza un XML BNR (nbrfxrates / 10days / anual) si intoarce:
      { date(YYYY-MM-DD): { "EUR": Decimal("5.2438"), "HUF": Decimal("0.014727"), ... }, ... }
    Multiplier tratat: curs real = valoare / multiplier (HUF/JPY/... cotate la 100).
    """
    root = ET.fromstring(continut)
    # Namespace-ul se ia din RADACINA, nu dintr-o constanta: BNR l-a schimbat din `http://` in
    # `https://www.bnr.ro/xsd` odata cu mutarea pe `curs.bnr.ro`, iar o constanta scrisa de mana
    # ar fi trebuit sa afle asta de la cineva. Forma se verifica, insa: un document care nu e
    # `DataSet` cu `Body` nu e un flux BNR, si se spune.
    ns = root.tag[:root.tag.index("}") + 1] if root.tag.startswith("{") else ""
    if not root.tag.endswith("DataSet"):
        raise FormatNecunoscut("radacina XML-ului nu e `DataSet`, ci %r — nu e un flux BNR"
                               % (root.tag,))
    body = root.find(f"{ns}Body")
    if body is None:
        raise FormatNecunoscut("XML-ul BNR n-are `Body` (namespace citit: %r)" % (ns or "fara",))
    rezultat = {}
    for cube in body.findall(f"{ns}Cube"):
        d_txt = cube.get("date")
        if not d_txt:
            continue
        d = datetime.strptime(d_txt, "%Y-%m-%d").date()
        cursuri = {}
        for rate in cube.findall(f"{ns}Rate"):
            mon = rate.get("currency")
            val_txt = (rate.text or "").strip()
            if not mon or not val_txt:
                continue
            mult = Decimal(rate.get("multiplier") or "1")
            cursuri[mon] = (Decimal(val_txt) / mult)
        rezultat[d] = cursuri
    return rezultat


def curs_din_harta(harta: dict, moneda: str, data_ref: date):
    """
    PUR: din harta {data: {moneda: curs}}, intoarce (curs, data_curs) pentru regula legala:
    cel mai recent Cube cu data_cube <= data_ref care are moneda ceruta.
    Intoarce (None, None) daca nu exista niciun curs eligibil (ex. data prea veche pt XML dat).
    RON -> (Decimal(1), data_ref) fara cautare.
    """
    moneda = moneda.upper()
    if moneda == "RON":
        return Decimal("1"), data_ref
    zile = sorted((d for d in harta if d <= data_ref), reverse=True)
    for d in zile:
        c = harta[d].get(moneda)
        if c is not None:
            return c, d
    return None, None


def rotunjeste(x: Decimal, zecimale: int = 2) -> Decimal:
    q = Decimal(10) ** -zecimale
    return Decimal(x).quantize(q, rounding=ROUND_HALF_UP)


# ============================================================
#  MARGINE — retea + cache DB (se dovedeste pe server)
# ============================================================
def _descarca(url: str) -> str:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "iConta/1.0 (+https://iconta.eu)"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8")


def _monede_din_cache(conn):
    """Monedele pe care BNR le-a cotat vreodata, dupa cache-ul local.

    **DE CE nu doar din XML-ul proaspat** (masurat 03.09.2026): fluxul public al BNR nu mai
    raspunde de pe serverul asta — `nbrfxrates10days.xml` da `302` catre pagina de start, iar
    ultima zi din cache e 10.07.2026. Fara asta, deosebirea „moneda nu exista" / „cursul nu se
    poate lua acum" ar fi ramas scrisa in cod si moarta in fapt.

    **LIMITA, declarata:** o moneda pe care BNR ar incepe s-o coteze DUPA ce cache-ul s-a oprit
    ar fi luata drept necotata. Nu se pierde nimic prin asta — cursul ei tot n-ar putea fi luat,
    deci factura tot n-ar putea fi emisa; se schimba numai MOTIVUL scris in refuz, iar mesajul
    listeaza monedele cunoscute, deci omul vede singur pe ce se sprijina raspunsul."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT moneda FROM public.curs_bnr_zilnic")
            return {r[0] for r in cur.fetchall() if r[0]}
    except Exception:
        return set()


def _din_cache(conn, moneda: str, data_ref: date):
    """Cauta in public.curs_bnr_zilnic cel mai recent curs cu data <= data_ref."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT curs, data FROM public.curs_bnr_zilnic "
            "WHERE moneda = %s AND data <= %s ORDER BY data DESC LIMIT 1",
            (moneda.upper(), data_ref))
        row = cur.fetchone()
    if row:
        return Decimal(str(row[0])), row[1]
    return None, None


def _salveaza_cache(harta: dict):
    """Salveaza cursurile in cache (idempotent), pe o CONEXIUNE PROPRIE.

    **DE CE NU PE CONEXIUNEA APELANTULUI** (gasit apasand, 04.09.2026). Pana azi primea `conn` si
    facea `conn.commit()` pe el. Apelantul lui e `curs_pentru`, chemat din mijlocul emiterii unei
    facturi — deci commitul asta comitea FACTURA, in mijlocul actului. Consecinta, probata: un
    refuz de curs (`CURS_PREA_VECHI`) facea `rollback()` care nu mai avea ce anula, iar in baza
    ramanea o factura numerotata si contata, fara curs si fara TVA in lei.

    Cache-ul traieste in `public` si e o preocupare a APLICATIEI, nu a facturii; se scrie separat,
    ca sa se pastreze si cand actul care l-a declansat esueaza — altfel fiecare incercare ar
    re-descarca de la BNR, care blocheaza IP-urile cu trafic repetat."""
    from core import db as _db
    with _db.get_conn() as c2:
        with c2.cursor() as cur:
            for d, cursuri in harta.items():
                for mon, c in cursuri.items():
                    cur.execute(
                        "INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s,%s,%s) "
                        "ON CONFLICT (data, moneda) DO NOTHING",
                        (d, mon, c))
        c2.commit()


#: [P5 val 3, 11.09.2026] Ce a aflat ultima descarcare, ca `curs_pentru` sa poata da ACELEASI
#: mesaje de refuz ca inainte fara sa mai atinga reteaua. Cheiate pe (moneda, data) — o cerere
#: pentru alta pereche nu citeste ce a lasat alta.
_ULTIMA_EROARE = {}
_COTATE = {}


def asigura_cursul(moneda: str, data_factura: date, prag_zile: int = PRAG_VECHIME_ZILE):
    """Aduce de la BNR ce lipseste din cache — FARA conexiunea apelantului. Nu decide nimic.

    [P5 val 3, 11.09.2026] Se cheama INAINTEA tranzactiei care va emite factura. Descarcarea are
    termen de 10 s pe fiecare din cele (pana la) trei adrese, iar forma dinainte o facea din
    mijlocul lui `curs_pentru`, adica din mijlocul tranzactiei de emitere. Zece cereri de facturare
    in valuta goleau pool-ul pentru toata aplicatia.

    *Nu ia nicio decizie:* pragul de vechime, alegerea cursului si cele trei refuzuri raman in
    `curs_pentru`, unde erau, si se aplica pe cache-ul de ATUNCI — deci o harta adusa aici nu sare
    peste nicio verificare.
    """
    from core import db
    moneda = moneda.upper()
    if moneda == "RON":
        return
    with db.get_conn() as conn:                      # scurta, doar citirea cache-ului
        c, dc = _din_cache(conn, moneda, data_factura)
    if c is not None and (data_factura - dc).days <= prag_zile:
        return                                       # destul de proaspat: nimic de adus

    urls = []
    azi = date.today()
    if (azi - data_factura).days <= 9:
        urls.append(URL_10ZILE)
    urls.append(URL_AN.format(an=data_factura.year))
    if data_factura.year != azi.year:
        urls.append(URL_10ZILE)  # fallback

    ultima_eroare = None
    cotate = set()          # ce monede a cotat BNR in hartile pe care CHIAR le-am citit
    for url in urls:
        try:
            xml = _descarca(url)                     # FARA nicio conexiune in mana
            harta = parse_xml(xml)
            if harta:
                # Bucla DOAR aduce si salveaza. Nu intoarce cursul: pana la calibrare o facea, si
                # asa sarea peste pragul de vechime — un prag aplicat pe un singur drum din doua
                # nu e un prag. Decizia se ia intr-un singur loc, in `curs_pentru`.
                _salveaza_cache(harta)
                for _zi in harta.values():
                    cotate.update(_zi)
                if curs_din_harta(harta, moneda, data_factura)[0] is not None:
                    break
        except Exception as e:  # retea, timeout, IP blocat, parse
            ultima_eroare = e
            continue
    _ULTIMA_EROARE[(moneda, data_factura)] = ultima_eroare
    _COTATE[(moneda, data_factura)] = cotate


def curs_pentru(conn, moneda: str, data_factura: date, prag_zile: int = PRAG_VECHIME_ZILE):
    """
    Intoarce (curs: Decimal, data_curs: date, sursa: str) pentru factura in valuta.
      1. RON -> (1, data_factura, "ron")
      2. cache-first, **dar numai daca ce e in cache e in interiorul pragului**
      3. altfel: descarca XML BNR (10zile pt recent, arhiva anuala pt vechi), salveaza, re-cauta
      4. daca cel mai bun curs gasit e tot peste prag -> `CursPreaVechi`, cu cursul in ea
      5. daca nu exista niciunul -> `MonedaNecotata` / `CursIndisponibil`

    **DE CE CACHE-FIRST NU MAI E NECONDITIONAT** (R130, masurat 04.09.2026). Cu fluxul BNR mutat
    si nereparat, cache-ul se oprise la 10.07.2026 — iar `curs_pentru` gasea acolo un curs cu
    `data <= data_factura` si il intorcea, **fara sa mai incerce reteaua niciodata**. Probat pe EUR
    pentru 04.09: intorcea cursul din 10.07, vechime **56 de zile**, cu `sursa="bnr"`, ca si cum ar
    fi fost al zilei. Un cache care raspunde MEREU face inutila orice reparatie a sursei: chiar dupa
    ce am cablat gazda noua, drumul nu trecea pe-acolo. *Cache-ul e o scurtatura, nu o sursa — iar o
    scurtatura care nu se uita la vechime e o sursa care minte.*
    """
    moneda = moneda.upper()
    if moneda == "RON":
        return Decimal("1"), data_factura, "ron"

    # 2) cache, dar numai daca e destul de proaspat pentru data ceruta
    c, dc = _din_cache(conn, moneda, data_factura)
    if c is not None and (data_factura - dc).days <= prag_zile:
        return c, dc, "bnr"

    # 3) DECIZIA, pe cache. Descarcarea s-a facut (sau nu) in `asigura_cursul`, INAINTE de
    #    tranzactia apelantului — v. nota functiei aceleia. Aici nu mai atinge nimeni reteaua.
    ultima_eroare = _ULTIMA_EROARE.get((moneda, data_factura))
    cotate = _COTATE.get((moneda, data_factura)) or set()

    # Recitesc cache-ul, care poate a fost tocmai imbogatit. Daca ce iese e in interiorul pragului,
    # e un raspuns; daca e mai vechi, e un refuz care POARTA cursul. *Recitirea asta E revalidarea:
    # decizia se ia pe ce e in cache ACUM, nu pe ce a adus descarcarea.*
    c, dc = _din_cache(conn, moneda, data_factura)
    if c is not None:
        vechime = (data_factura - dc).days
        if vechime <= prag_zile:
            return c, dc, "bnr"
        raise CursPreaVechi(moneda, dc, c, vechime, prag_zile)

    # Am citit cel putin o harta BNR, si moneda nu e in NICIUNA: nu e o indisponibilitate, e o
    # moneda care nu exista in nomenclatorul BNR. Daca n-am citit nicio harta (`cotate` gol),
    # chiar nu se poate sti — si atunci raspunsul ramane cel de jos.
    cotate |= _monede_din_cache(conn)
    if cotate and moneda not in cotate:
        raise MonedaNecotata(moneda, cotate)

    raise CursIndisponibil(
        f"Cursul BNR pentru {moneda} la data {data_factura} nu e disponibil momentan."
        + (f" ({ultima_eroare})" if ultima_eroare else ""))


def converteste_tva(tva_valuta, curs) -> Decimal:
    """TVA in lei = round(tva_valuta * curs, 2), ROUND_HALF_UP (corect fiscal)."""
    return rotunjeste(Decimal(str(tva_valuta)) * Decimal(str(curs)), 2)
