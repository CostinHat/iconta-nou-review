"""
curs_bnr.py — curs valutar BNR pentru facturi in valuta.

REGULA LEGALA (verificata la sursa, art. 290 alin.2 Cod fiscal + Norme HG 1/2016 pct.35):
  Pentru o operatiune in valuta, baza de impozitare TVA se converteste in lei folosind
  "ultimul curs de schimb comunicat de BNR" = cursul comunicat in ziua anterioara,
  valabil pentru ziua urmatoare. In practica: pentru o factura cu data X, cursul folosit
  este cel mai recent curs BNR publicat cu data_cube <= X (ziua bancara anterioara/curenta).
  Cursul se fixeaza la emitere si NU se mai recalculeaza (nici la incasare, nici la regularizare).
  Art. 319: TVA colectata trebuie exprimata SI in lei pe factura, chiar daca restul e in valuta.

SURSA OFICIALA BNR (pentru programatori):
  - ultimele 10 zile: https://www.bnr.ro/nbrfxrates10days.xml
  - arhiva anuala:     https://www.bnr.ro/files/xml/years/nbrfxratesYYYY.xml
  - cursul zilei:      https://www.bnr.ro/nbrfxrates.xml
  XML namespace http://www.bnr.ro/xsd; Body/Cube[@date]/Rate[@currency, @multiplier?].
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

BNR_NS = "{http://www.bnr.ro/xsd}"
URL_10ZILE = "https://www.bnr.ro/nbrfxrates10days.xml"
URL_AN = "https://www.bnr.ro/files/xml/years/nbrfxrates{an}.xml"


class CursIndisponibil(Exception):
    """BNR inaccesibil / cursul nu a putut fi preluat. Frontend: reincearca sau manual."""


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
    body = root.find(f"{BNR_NS}Body")
    if body is None:
        return {}
    rezultat = {}
    for cube in body.findall(f"{BNR_NS}Cube"):
        d_txt = cube.get("date")
        if not d_txt:
            continue
        d = datetime.strptime(d_txt, "%Y-%m-%d").date()
        cursuri = {}
        for rate in cube.findall(f"{BNR_NS}Rate"):
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


def _salveaza_cache(conn, harta: dict):
    """Salveaza toate cursurile din harta in cache (idempotent, ON CONFLICT DO NOTHING)."""
    with conn.cursor() as cur:
        for d, cursuri in harta.items():
            for mon, c in cursuri.items():
                cur.execute(
                    "INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s,%s,%s) "
                    "ON CONFLICT (data, moneda) DO NOTHING",
                    (d, mon, c))
    conn.commit()


def curs_pentru(conn, moneda: str, data_factura: date):
    """
    Intoarce (curs: Decimal, data_curs: date, sursa: str) pentru factura in valuta.
      1. RON -> (1, data_factura, "ron")
      2. cache-first (public.curs_bnr_zilnic)
      3. daca lipseste: descarca XML BNR (10zile pt recent, arhiva anuala pt vechi),
         salveaza in cache, re-cauta.
      4. daca tot lipseste / retea pica -> ridica CursIndisponibil.
    """
    moneda = moneda.upper()
    if moneda == "RON":
        return Decimal("1"), data_factura, "ron"

    # 2) cache
    c, dc = _din_cache(conn, moneda, data_factura)
    if c is not None:
        return c, dc, "bnr"

    # 3) descarca + salveaza + re-cauta
    #    aleg sursa dupa vechime: date din ultimele ~10 zile -> 10days; altfel arhiva anuala.
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
            xml = _descarca(url)
            harta = parse_xml(xml)
            if harta:
                _salveaza_cache(conn, harta)
                for _zi in harta.values():
                    cotate.update(_zi)
                c, dc = curs_din_harta(harta, moneda, data_factura)
                if c is not None:
                    return c, dc, "bnr"
        except Exception as e:  # retea, timeout, IP blocat, parse
            ultima_eroare = e
            continue

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
