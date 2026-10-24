"""
curs_bnr.py — curs valutar BNR pentru facturi in valuta.

REGULA LEGALA — DOUA REGULI, verificate verbatim (lotul 11, decizia Costin din 10.3: „Cursul BNR: aplici textul legal în vigoare
(CF art. 290, HG 1/2016 pct. 35), verificat verbatim”; `anaf_surse/cod_fiscal_227_2015_consolidat.txt` forma consolidata 08.08.2026,
`anaf_surse/hg_1_2016_norme_cod_fiscal.txt` forma consolidata 31.03.2026, `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
  1. OPERATIUNEA (`REGULA_OPERATIUNE`: factura emisa / primita, previzualizarea din formular, decontarea).
     CF art.290 alin.(2): „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...]
     valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”.
     HG 1/2016 pct.35 alin.(1): „prin ultimul curs de schimb comunicat de Banca Națională a României se înțelege cursul de schimb
     comunicat de respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se vor desfășura în ziua următoare.”
     Data cubului BNR (`Cube date`) e ziua COMUNICARII (= `PublishingDate`, verificat pe `nbrfxrates.xml` 21.10.2026). Deci operatiunea
     din ziua Z ia cel mai recent curs cu data_cube < Z (strict). Pana la lotul 11 se lua data_cube <= Z, adica si cursul comunicat
     chiar in ziua operatiunii (F1A8 din 19.10.2026, pe productie: cursul din 19.10 in loc de cel din 16.10).
     Cursul se fixeaza la emitere si NU se mai recalculeaza (HG 1/2016 pct.35 alin.(2): „va rămâne neschimbat la data definitivării
     operațiunii”). Art. 319: TVA colectata trebuie exprimata SI in lei pe factura, chiar daca restul e in valuta.
  2. REEVALUAREA LUNARA (`REGULA_SFARSIT_LUNA`, `curs_sfarsit_luna`). OMFP 1802/2014 pct.325 alin.(2) lit.b: „cursul de schimb al
     pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii în cauză, pentru evaluarea creanțelor și
     datoriilor în valută, a disponibilităților în valută [...]”. Deci cel mai recent curs cu data_cube <= ultima zi a lunii.
     (Aceeasi norma, lit.a, pentru tranzactiile din ultima zi: „din ultima zi bancară anterioară operațiunii” — regula 1.)

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
import collections
import time as _time
from core.cache_declarat import Declaratie as _Dec
from core.common import cate as _cate
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data pentru om, sursa unică
from core import scadente as _sc

#: PRAGUL DE VECHIME al unui curs, in zile CALENDARISTICE, intre data cursului si data facturii.
#: **Decizie de produs, nu norma fiscala** — Costin, 04.09.2026, verbatim: *„pragul e 5 zile
#: calendaristice — acopera un weekend prelungit cu sarbatori legale; peste atat nu mai e pauza de
#: publicare, e flux rupt."* Nu e sursat cu `Temei` fiindca nu exista act care sa-l ceara: legea
#: (art. 290 alin.2 CF) spune sa se foloseasca *ultimul curs comunicat*, nu cat de vechi poate fi.
#: Cifra alege cat de departe de „ultimul comunicat" mai acceptam sa mergem in tacere.
PRAG_VECHIME_ZILE = 5

#: Cele doua reguli de alegere a cursului (v. antetul modulului). Nomenclator INCHIS.
REGULA_OPERATIUNE = "operatiune"        # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): comunicat INAINTEA zilei operatiunii
REGULA_SFARSIT_LUNA = "sfarsit_luna"    # OMFP 1802/2014 pct.325 alin.(2) lit.b: comunicat in ultima zi bancara a lunii (<= ziua)
REGULI = (REGULA_OPERATIUNE, REGULA_SFARSIT_LUNA)


def _strict(regula):
    """True = numai cursurile comunicate INAINTEA zilei (operatiunea); False = si cel comunicat chiar in ziua (sfarsitul lunii)."""
    if regula not in REGULI:
        raise ValueError("regula cursului BNR necunoscută: %r (alege: %s)" % (regula, ", ".join(REGULI)))
    return regula == REGULA_OPERATIUNE


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
            "Cel mai recent curs BNR pentru %s la data cerută e din %s — mai vechi cu %s decât "
            "pragul de %d. Peste atât nu mai e pauză de publicare, e flux întrerupt, iar TVA-ul în "
            "lei s-ar calcula cu o cifră care nu mai e a zilei. Cursul găsit: %s."
            % (moneda, _data_ro(data_curs), _cate(vechime_zile, "zi", "zile"), prag_zile, curs))


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
        raise FormatNecunoscut("fișierul primit de la BNR nu are forma cunoscută (începe cu %r, nu cu DataSet)"
                               % (root.tag,))
    body = root.find(f"{ns}Body")
    if body is None:
        raise FormatNecunoscut("fișierul primit de la BNR nu are secțiunea Body (spațiul de nume citit: %r)" % (ns or "fara",))
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


def curs_din_harta(harta: dict, moneda: str, data_ref: date, regula: str = REGULA_OPERATIUNE):
    """
    PUR: din harta {data: {moneda: curs}}, intoarce (curs, data_curs) pentru regula legala:
    `REGULA_OPERATIUNE` — cel mai recent Cube cu data_cube < data_ref (comunicat in ziua anterioara, HG 1/2016 pct.35 alin.(1));
    `REGULA_SFARSIT_LUNA` — cel mai recent Cube cu data_cube <= data_ref (ultima zi bancara a lunii, OMFP 1802/2014 pct.325).
    Intoarce (None, None) daca nu exista niciun curs eligibil (ex. data prea veche pt XML dat).
    RON -> (Decimal(1), data_ref) fara cautare.
    """
    strict = _strict(regula)
    moneda = moneda.upper()
    if moneda == "RON":
        return Decimal("1"), data_ref
    zile = sorted((d for d in harta if (d < data_ref if strict else d <= data_ref)), reverse=True)
    for d in zile:
        c = harta[d].get(moneda)
        if c is not None:
            return c, d
    return None, None


def ziua_bancara_asteptata(zi: date, regula: str = REGULA_OPERATIUNE):
    """PUR. [460] Ziua in care BNR a comunicat cursul pe care il cere `regula` pentru `zi`: operatiunea — ultima zi bancara DINAINTEA
    ei (HG 1/2016 pct.35 alin.(1): „comunicat de respectiva bancă în ziua anterioară”); sfarsitul lunii — ultima zi bancara <= `zi`
    (OMFP 1802/2014 pct.325 alin.(2) lit.b: „din ultima zi bancară a lunii în cauză”).

    Zilele bancare = zilele lucratoare din `scadente.e_zi_lucratoare` (L–V fara sarbatorile legale, art.139 Codul muncii). MASURAT pe
    arhivele BNR (`nbrfxrates2024/2025/2026.xml`, 22.10.2026): zilele cu curs sunt EXACT zilele lucratoare — 252/252, 248/248, 202/202
    (pana la 21.10.2026), nicio zi lucratoare fara curs si niciun curs intr-o zi nelucratoare.

    `None` = nu se poate sti (an neacoperit de calendar): apelantii cad atunci pe pragul de vechime, ca inainte."""
    d = zi - timedelta(days=1) if _strict(regula) else zi
    try:
        for _ in range(15):
            if _sc.e_zi_lucratoare(d):
                return d
            d -= timedelta(days=1)
    except ValueError:      # `scadente.sarbatori_legale`: an in afara calendarului
        return None
    return None


#: [lotul 12, decizia Costin „cursul vechi la validare (a)”] actul care fixează cursul facturii, cum îl spune anunțul: emiterea (factura emisă
#: în aplicație) sau validarea (factura primită, din XML sau introdusă de mână)
ACT_FIXARE = {"emitere": ("factura emisă acum", "se fixează la emitere"),
              "validare": ("factura validată acum", "se fixează la validare")}


def cursul_zilei_lipsa(zi: date, data_curs: date, azi: date = None, act: str = "emitere"):
    """PUR. [460] Pentru operatiunea (factura) din `zi`: `None` daca `data_curs` e chiar ultimul curs comunicat inaintea ei (sau nu se
    poate sti); altfel ce lipseste si ce se foloseste, cu mesajul pentru contabil: {"asteptat", "folosit", "mesaj"} (datele ISO).

    [lotul 11, AT] Lipsa e o AFIRMATIE TIPATA (`afirmatii.afirmatie`, decizia 21.08.2026): `absenta_observatie` — cursul nu e intr-o sursa
    NUMITA (cursurile BNR preluate in aplicatie), ca refuzul reevaluarii fara cursul lunii (`uc_reevaluare`). `motiv` = acelasi text ca
    `mesaj` (pe care il citeste ecranul, `emitere_ecran.js`).

    [lotul 12, decizia Costin „cursul vechi la validare (a)”: „anunțul la validare, ca la emitere”] `act` = „emitere” sau „validare”
    (`ACT_FIXARE`): la factura primită în valută cursul se fixează la validare, iar anunțul o spune."""
    asteptata = ziua_bancara_asteptata(zi, REGULA_OPERATIUNE)
    if asteptata is None or data_curs is None or data_curs >= asteptata:
        return None
    azi = azi or date.today()
    de_ce = ("BNR îl comunică abia azi" if asteptata == azi else
             "BNR nu l-a comunicat încă" if asteptata > azi else
             "preluarea lui de la BNR n-a reușit încă; aplicația reîncearcă singură")
    cine, cand = ACT_FIXARE[act]
    m = ("Cursul BNR comunicat pe %s (ultimul înaintea datei facturii, %s) lipsește din aplicație: %s. Până atunci se folosește cursul "
         "din %s, iar %s îl păstrează (%s)." % (_data_ro(asteptata), _data_ro(zi), de_ce, _data_ro(data_curs), cine, cand))
    from core import afirmatii as _af
    return _af.afirmatie("absenta_observatie", "curs BNR al zilei", m,
                         surse_consultate="cursurile BNR preluate în aplicație, pentru ziua bancară dinaintea datei facturii",
                         asteptat=asteptata.isoformat(), folosit=data_curs.isoformat(), mesaj=m)


#: [C88, lotul 11] PRECIZIA cursului pe unitate, cum o da BNR: valoarea din XML are cel mult 4 zecimale, iar cinci monede sunt cotate la 100
#: de unitati (`multiplier="100"`: HUF, IDR, ISK, JPY, KRW — masurat pe arhivele 2024/2025/2026, 22.10.2026), deci cursul pe unitate are
#: cel mult 6 zecimale (HUF 1,4719 / 100 = 0,014719; IDR 0,0256 / 100 = 0,000256). Nu e norma fiscala, e forma datelor BNR. Pana la C88
#: coloanele de curs aveau 4 zecimale: HUF 0,014719 se pastra 0,0147 (v. `core/migrare_curs_precizie.py`).
CURS_Q = Decimal("0.000001")
#: Cursul se scrie cu cel putin 4 zecimale (forma BNR pentru monedele cotate la unitate: 5,2409).
CQ_MIN = Decimal("0.0001")
ZECIMALE_CURS = -CURS_Q.as_tuple().exponent
#: Monedele cotate de BNR la 100 de unitati (`multiplier="100"`), MASURAT pe arhivele 2024, 2025, 2026 (aceleasi cinci in toti anii).
#: Folosit NUMAI pentru precizia unui curs CALCULAT (lei / valuta, cursul din evidenta la reevaluare): cursul BNR insusi vine exact din
#: `parse_xml`, oricare ar fi multiplicatorul. Garda: `core/test_lot11_c88_curs_precizie.py` (pe XML-ul real al arhivei).
MONEDE_COTATE_LA_100 = frozenset({"HUF", "IDR", "ISK", "JPY", "KRW"})


def curs_derivat(x, moneda: str) -> Decimal:
    """PUR. [C88] Un curs CALCULAT (ex. sold in lei / sold in valuta) rotunjit (ROUND_HALF_UP) la precizia cursului BNR al monedei — 6
    zecimale la monedele cotate la 100, 4 la celelalte: EUR 1906,98 / 363 -> 5,2534; HUF 14719 / 1000000 -> 0,014719 (cu 4 zecimale ar
    fi fost 0,0147)."""
    q = CURS_Q if (moneda or "").upper() in MONEDE_COTATE_LA_100 else CQ_MIN
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


def curs_text(x) -> str:
    """PUR. [C88] Cursul pentru om (PDF, mesaje), in forma romaneasca, cu precizia BNR: cel mult `ZECIMALE_CURS` zecimale (ROUND_HALF_UP),
    cel putin 4, fara zerourile de prisos dintre ele — „5,2409”, „0,014719”, „0,01472” (5.240900 -> „5,2409”)."""
    q = Decimal(str(x)).quantize(CURS_Q, rounding=ROUND_HALF_UP).normalize()
    if q.as_tuple().exponent > CQ_MIN.as_tuple().exponent:
        q = q.quantize(CQ_MIN, rounding=ROUND_HALF_UP)   # numai completează zerourile până la 4 zecimale
    return format(q, "f").replace(".", ",")


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


def _din_cache(conn, moneda: str, data_ref: date, regula: str = REGULA_OPERATIUNE):
    """Cauta in public.curs_bnr_zilnic cel mai recent curs eligibil dupa `regula` (operatiunea: data < data_ref; sfarsitul lunii:
    data <= data_ref) — aceeasi regula ca `curs_din_harta`."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT curs, data FROM public.curs_bnr_zilnic "
            "WHERE moneda = %s AND data " + ("<" if _strict(regula) else "<=") + " %s ORDER BY data DESC LIMIT 1",
            (moneda.upper(), data_ref))
        row = cur.fetchone()
    if row:
        return Decimal(str(row[0])), row[1]
    return None, None


def zile_bancare_lipsa(conn, pana_la: date):
    """[460] Zilele bancare ale anului lui `pana_la`, de la 1 ianuarie pana la `pana_la` inclusiv, fara niciun curs in cache — golurile
    de umplut din arhiva anuala BNR. Zilele bancare = `ziua_bancara_asteptata` (zilele lucratoare; v. masuratoarea de acolo). Un an
    neacoperit de calendar -> [] (nu se poate sti)."""
    zile, d = [], date(pana_la.year, 1, 1)
    try:
        while d <= pana_la:
            if _sc.e_zi_lucratoare(d):
                zile.append(d)
            d += timedelta(days=1)
    except ValueError:
        return []
    if not zile:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT data FROM public.curs_bnr_zilnic WHERE data BETWEEN %s AND %s", (zile[0], pana_la))
        are = {r[0] for r in cur.fetchall()}
    return [z for z in zile if z not in are]


def stare_curs_zilei(conn, azi: date = None):
    """[460] Pentru sanatatea aplicatiei: cursul de care au nevoie operatiunile de AZI (comunicat in ultima zi bancara dinaintea ei,
    HG 1/2016 pct.35 alin.(1)) e in cache? -> {"asteptat", "ultima_zi" (cea mai recenta zi din cache), "lipsa" (bool | None = nu se
    poate sti), "zile_lipsa" (golurile anului, ISO)}."""
    azi = azi or date.today()
    asteptata = ziua_bancara_asteptata(azi)
    with conn.cursor() as cur:
        cur.execute("SELECT max(data) FROM public.curs_bnr_zilnic WHERE data < %s", (azi,))
        ultima = cur.fetchone()[0]
    goluri = zile_bancare_lipsa(conn, asteptata) if asteptata else []
    return {"asteptat": asteptata.isoformat() if asteptata else None, "ultima_zi": ultima.isoformat() if ultima else None,
            "lipsa": None if asteptata is None else (ultima is None or ultima < asteptata),
            "zile_lipsa": [z.isoformat() for z in goluri]}


# [E2b, 15.09.2026] ACTUL (`asigura_cursul` / `_salveaza_cache`) a plecat in
# `core/uc_curs_bnr.py`: isi deschide conexiunea lui — deliberat, decizia din
# 04.09.2026 — iar un DEPOZIT n-are voie s-o faca. Depozitul a ramas aici:
# `curs_pentru` primeste conexiunea apelantului si decide.


#: [P5 val 3, 11.09.2026 · P6 val 2, 12.09.2026] Ce a aflat ultima descarcare, ca `curs_pentru`
#: sa poata da ACELEASI mesaje de refuz ca inainte fara sa mai atinga reteaua.
#:
#: ERAU DOUA DICTIONARE, `_ULTIMA_EROARE` si `_COTATE`. Cheiate identic, scrise in aceeasi linie,
#: citite in aceeasi linie: erau un singur lucru tinut in doua locuri. Contopite la valul 2.
#:
#: SI N-AVEAU NICIO INVALIDARE — cresteau cu fiecare (moneda, data) vazuta vreodata de proces, iar
#: o intrare lasata de o cerere putea fi citita de alta, ore mai tarziu. Acum au doua plafoane,
#: amandoua scrise: un TERMEN, fiindca predarea e de la `asigura_cursul` catre `curs_pentru` din
#: ACEEASI cerere, iar bugetul descarcarii e de cel mult 3 x 10 s; si un PLAFON DE CHEI.
#: O intrare expirata sau evacuata nu produce un curs gresit — produce exact raspunsul de dinainte
#: de orice descarcare, adica diagnosticul mai sarac, niciodata unul fals.
_PREDARE_TTL_SEC = 60
_PREDARE_MAX = 256
_PREDARE = collections.OrderedDict()
_PREDARE_DECLARATIE = _Dec(
    rol="ce a aflat descarcarea BNR (eroarea de retea, monedele cotate in hartile CHIAR citite), "
        "predat de la `asigura_cursul` la `curs_pentru`, care nu mai are voie sa atinga reteaua",
    sursa="reteaua BNR. NU e cache-ul cursului — acela e in baza, in `curs_bnr_cache`, si el ramane "
          "singura sursa a DECIZIEI; aici sta doar de ce n-a mers, ca refuzul sa spuna acelasi "
          "lucru ca inainte de P5",
    motiv="descarcarea s-a mutat in afara tranzactiei apelantului (P5 val 3, clasa C5); fara "
          "predarea asta, mesajele de refuz si-ar fi pierdut continutul",
    invalidare="TERMEN de 60 s (predarea e intre doi pasi ai aceleiasi cereri) SI plafon de 256 chei, "
               "cu evacuarea celei mai vechi. O intrare cazuta degradeaza la comportamentul de "
               "dinainte de descarcare, niciodata la un curs gresit",
    dovada="core/test_cache_declarat.py::test_predarea_bnr_se_reconstruieste_identic",
)


def _preda(moneda, data_factura, eroare, cotate):
    """Lasa pentru `curs_pentru` ce a aflat descarcarea. Cu plafon, ca sa nu creasca la nesfarsit."""
    _PREDARE[(moneda, data_factura)] = (_time.monotonic(), eroare, cotate)
    _PREDARE.move_to_end((moneda, data_factura))
    while len(_PREDARE) > _PREDARE_MAX:
        _PREDARE.popitem(last=False)


def _preluare(moneda, data_factura):
    """Ce a aflat descarcarea ACESTEI cereri. Ce a ramas de la alta, expirat, nu se citeste."""
    x = _PREDARE.get((moneda, data_factura))
    if x is None or _time.monotonic() - x[0] > _PREDARE_TTL_SEC:
        return None, set()
    return x[1], (x[2] or set())


# [E2b, 15.09.2026] ACTUL (`asigura_cursul` / `_salveaza_cache`) a plecat in
# `core/uc_curs_bnr.py`: isi deschide conexiunea lui — deliberat, decizia din
# 04.09.2026 — iar un DEPOZIT n-are voie s-o faca. Depozitul a ramas aici:
# `curs_pentru` primeste conexiunea apelantului si decide.


def curs_sfarsit_luna(conn, moneda: str, zi: date, prag_zile: int = PRAG_VECHIME_ZILE):
    """Cursul reevaluarii lunare (OMFP 1802/2014 pct.325 alin.(2) lit.b): comunicat in ultima zi bancara a lunii, adica cel mai recent
    curs cu data <= `zi` (ultima zi a lunii). Aceleasi refuzuri ca `curs_pentru`."""
    return curs_pentru(conn, moneda, zi, prag_zile=prag_zile, regula=REGULA_SFARSIT_LUNA)


def curs_pentru(conn, moneda: str, data_factura: date, prag_zile: int = PRAG_VECHIME_ZILE, regula: str = REGULA_OPERATIUNE):
    """
    Intoarce (curs: Decimal, data_curs: date, sursa: str) pentru operatiunea in valuta din ziua `data_factura` — cursul comunicat de
    BNR INAINTEA zilei (CF art.290 alin.(2), HG 1/2016 pct.35 alin.(1)); cu `regula=REGULA_SFARSIT_LUNA`, cursul din ultima zi
    bancara a lunii (`curs_sfarsit_luna`).
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
    _strict(regula)
    moneda = moneda.upper()
    if moneda == "RON":
        return Decimal("1"), data_factura, "ron"

    # 2) cache, dar numai daca e destul de proaspat pentru data ceruta
    c, dc = _din_cache(conn, moneda, data_factura, regula)
    if c is not None and (data_factura - dc).days <= prag_zile:
        return c, dc, "bnr"

    # 3) DECIZIA, pe cache. Descarcarea s-a facut (sau nu) in `asigura_cursul`, INAINTE de
    #    tranzactia apelantului — v. nota functiei aceleia. Aici nu mai atinge nimeni reteaua.
    ultima_eroare, cotate = _preluare(moneda, data_factura)

    # Recitesc cache-ul, care poate a fost tocmai imbogatit. Daca ce iese e in interiorul pragului,
    # e un raspuns; daca e mai vechi, e un refuz care POARTA cursul. *Recitirea asta E revalidarea:
    # decizia se ia pe ce e in cache ACUM, nu pe ce a adus descarcarea.*
    c, dc = _din_cache(conn, moneda, data_factura, regula)
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
        f"Cursul BNR pentru {moneda} la data {_data_ro(data_factura)} nu e disponibil momentan."
        + (f" ({ultima_eroare})" if ultima_eroare else ""))


def converteste_tva(tva_valuta, curs) -> Decimal:
    """TVA in lei = round(tva_valuta * curs, 2), ROUND_HALF_UP (corect fiscal)."""
    return rotunjeste(Decimal(str(tva_valuta)) * Decimal(str(curs)), 2)
