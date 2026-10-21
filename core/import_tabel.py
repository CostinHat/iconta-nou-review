# -*- coding: utf-8 -*-
"""core/import_tabel.py — sursa UNICĂ a citirii unui fișier de import (migrare, preluarea dintr-o altă aplicație).

DE CE EXISTĂ (comanda Costin 14.10.2026, verbatim în DECIZII „Importul din SAGA”). Până azi fiecare parser de import avea copia
lui de citire și de potrivire a coloanelor — opt copii ale lui `_gaseste_col`, fiecare cu „prima coloană al cărei antet CONȚINE
cheia”. Trei defecte de clasă au ieșit din copia asta, toate tăcute:

- **C21** — o balanță de verificare completă (sold inițial, rulaje, sold final) se importa cu PRIMA pereche debit/credit, adică
  soldurile inițiale; balanța ieșea echilibrată, deci trecea;
- un subșir prinde alt cuvânt: „an” prindea „angajare”, „intrare” prindea „Data intrare” înaintea lui „Valoare intrare” (registrul
  de imobilizări SAGA), „ore” prindea „Ore pe lună” ca ore pe zi;
- **C27** — un CSV salvat în Windows-1250 (codarea implicită a programelor românești de pe Windows) se citea ca UTF-8 cu
  `errors="replace"`: diacriticele deveneau „�” și nimeni nu era anunțat.

CE FACE, în ordine:
1. `citeste` — CSV / TSV / TXT / XLSX / XLSM / XLS. Codarea textului: BOM UTF-8 sau UTF-16, apoi UTF-8 strict, apoi Windows-1250
   VERIFICAT (fiecare caracter din afara ASCII trebuie să fie o literă sau un semn plauzibil într-un export românesc). Dacă nu se
   poate citi sigur, **refuz cu mesaj** — diacriticele nu se strică în tăcere.
2. `gaseste_antet` — rândul de antet nu e neapărat primul: exporturile au deasupra titlul („Balanță de verificare”, firma, perioada).
   Un antet pe DOUĂ rânduri („Solduri finale” deasupra lui „Debit | Credit”) se unește într-unul („solduri finale debit”).
3. `norm` — antetul se compară fără diacritice (ș/ş, ț/ţ), fără majuscule și fără punctuație: „Dur.luni” = „dur luni”.
4. `coloana` — întâi EGALITATE cu un alias, apoi alias ca CUVINTE ÎNTREGI în antet (un cuvânt al aliasului terminat în `*` se
   potrivește ca început de cuvânt: `angaj*` prinde „angajării”). **Două coloane la fel de potrivite = refuz numit**, nu „prima
   câștigă”: alegerea tăcută a primei coloane e exact defectul C21.

Temei: N/A — citirea unui fișier (tooling). Antetele SAGA pe care le recunosc parserele sunt luate din manualul SAGA C
(`anaf_surse/saga_manual_topic*`), nu ghicite.
"""
from __future__ import annotations

import csv
import datetime
import io
import re
import unicodedata

FORMATE = (".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls")

MESAJ_FORMAT = ("Fișierul %s nu se poate citi: se așteaptă un CSV, TXT, XLSX sau XLS. Salvează exportul în unul din "
                "formatele astea și încarcă-l din nou.")

# Caracterele din afara ASCII care pot apărea într-un export românesc citit ca Windows-1250: literele românești (și cu
# virgulă, și cu sedilă), literele din numele străine uzuale în Europa Centrală și semnele tipografice. Un caracter din afara
# listei (ex. „ţ” citit greșit ca „ţ” e în listă, dar „Ă¤” nu) înseamnă că fișierul nu e în Windows-1250 — refuz, nu ghicit.
_PLAUZIBILE = set(
    "ăâîșțşţĂÂÎȘȚŞŢ"
    "áéíóúýöüőűäëïçčćďđěľĺňřšťžźżłńśÁÉÍÓÚÝÖÜŐŰÄËÏÇČĆĎĐĚĽĹŇŘŠŤŽŹŻŁŃŚ"
    "„”“‘’‚«»–—…°§€•·× "
)


class FisierNecitit(ValueError):
    """Fișierul nu se poate citi sigur (format, codare, antet). E un `ValueError`, ca rutele care prind `ValueError` și
    întorc 400 să-l arate omului neschimbat."""


# ── codarea ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def decodeaza(octeti, nume_fisier=""):
    """`(text, codare)`. Refuză (`FisierNecitit`) dacă textul nu se poate citi sigur.

    Ordinea: BOM (UTF-8 / UTF-16) -> UTF-8 strict -> Windows-1250 cu verificarea literelor. UTF-8 întâi: un fișier numai ASCII
    e valid în ambele, iar un text UTF-8 cu diacritice nu trece niciodată ca Windows-1250 plauzibil (octeții lui multi-octet
    dau „Ä…”, „Č™” — combinații pe care verificarea le respinge pe rând)."""
    if isinstance(octeti, str):
        return octeti, "text"
    b = bytes(octeti or b"")
    if b.startswith(b"\xef\xbb\xbf"):
        try:
            return b[3:].decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            raise FisierNecitit(_mesaj_codare(nume_fisier, "începe ca UTF-8, dar are octeți care nu sunt UTF-8"))
    if b.startswith(b"\xff\xfe") or b.startswith(b"\xfe\xff"):
        try:
            return b.decode("utf-16"), "utf-16"
        except UnicodeDecodeError:
            raise FisierNecitit(_mesaj_codare(nume_fisier, "începe ca UTF-16, dar nu se poate citi ca UTF-16"))
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        text = b.decode("cp1250")
    except UnicodeDecodeError:
        raise FisierNecitit(_mesaj_codare(nume_fisier, "nu e nici UTF-8, nici Windows-1250"))
    for nr, linie in enumerate(text.splitlines(), start=1):
        straine = sorted({ch for ch in linie if ord(ch) > 127 and ch not in _PLAUZIBILE})
        if straine:
            raise FisierNecitit(_mesaj_codare(
                nume_fisier, "nu e UTF-8, iar ca Windows-1250 rândul %d ar conține „%s”, care nu sunt litere românești"
                % (nr, "".join(straine[:5]))))
    return text, "windows-1250"


def _mesaj_codare(nume_fisier, motiv):
    return ("Fișierul %s nu se poate citi fără să se strice diacriticele: %s. Salvează exportul ca „CSV UTF-8” "
            "(sau XLSX) și încarcă-l din nou." % (_nume(nume_fisier), motiv))


def _nume(nume_fisier):
    return "«%s»" % nume_fisier if nume_fisier else "trimis"


# ── citirea ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def extensie(nume_fisier):
    n = (nume_fisier or "").lower().strip()
    for e in FORMATE:
        if n.endswith(e):
            return e
    return ""


def citeste(continut, nume_fisier=""):
    """Rândurile fișierului, ca liste de celule (`""` pentru celulă goală; numere și date rămân numere și date în XLSX/XLS).

    Ridică `FisierNecitit` pe un format necunoscut, pe o codare care nu se poate citi sigur sau pe un fișier Excel stricat."""
    ext = extensie(nume_fisier)
    if ext in (".csv", ".tsv", ".txt"):
        text, _cod = decodeaza(continut, nume_fisier)
        delim = "\t" if ext == ".tsv" else _delimitator(text)
        return [list(r) for r in csv.reader(io.StringIO(text), delimiter=delim)]
    if ext in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        try:
            wb = load_workbook(io.BytesIO(continut), read_only=True, data_only=True)
        except Exception:
            raise FisierNecitit("Fișierul %s nu se poate deschide ca XLSX (e stricat sau are altă extensie decât formatul "
                                "lui). Deschide-l în Excel și salvează-l din nou." % _nume(nume_fisier))
        try:
            return [["" if c is None else c for c in r] for r in wb.active.iter_rows(values_only=True)]
        finally:
            wb.close()
    if ext == ".xls":
        import xlrd
        try:
            wb = xlrd.open_workbook(file_contents=bytes(continut))
        except Exception:
            raise FisierNecitit("Fișierul %s nu se poate deschide ca XLS (Excel 97–2003). Deschide-l în Excel și salvează-l "
                                "ca XLSX." % _nume(nume_fisier))
        sh = wb.sheet_by_index(0)
        out = []
        for i in range(sh.nrows):
            rand = []
            for j in range(sh.ncols):
                c = sh.cell(i, j)
                if c.ctype == xlrd.XL_CELL_DATE:
                    rand.append(xlrd.xldate_as_datetime(c.value, wb.datemode))
                elif c.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                    rand.append("")
                else:
                    rand.append(c.value)
            out.append(rand)
        return out
    raise FisierNecitit(MESAJ_FORMAT % _nume(nume_fisier))


def _delimitator(text):
    """`;` / TAB / `,` — după primele linii nevide (titlul de deasupra antetului poate să n-aibă niciun separator)."""
    linii = [l for l in text.splitlines() if l.strip()][:15]
    scor = {d: sum(l.count(d) for l in linii) for d in (";", "\t", ",")}
    return max((";", "\t", ","), key=lambda d: (scor[d], d == ";"))


# ── antetul ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
_DIACRITICE = str.maketrans("ăâîșțşţĂÂÎȘȚŞŢ", "aaiststAAISTST")


def norm(v):
    """Antet comparabil: fără diacritice, litere mici, punctuația -> spațiu, spații unice. „Dur. rămasă” -> „dur ramasa”."""
    t = str(v if v is not None else "").translate(_DIACRITICE)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch)).lower()
    t = re.sub(r"[^0-9a-z%*]+", " ", t)
    return " ".join(t.split())


def _alias(a):
    return norm(a)


def _potriveste_cuvinte(antet, alias):
    """Aliasul apare în antet ca secvență de CUVINTE ÎNTREGI (un cuvânt al aliasului terminat în `*` = început de cuvânt)."""
    ha, aa = antet.split(), alias.split()
    if not aa or len(aa) > len(ha):
        return False
    for s in range(len(ha) - len(aa) + 1):
        ok = True
        for k, w in enumerate(aa):
            h = ha[s + k]
            if w.endswith("*"):
                if not h.startswith(w[:-1]):
                    ok = False
                    break
            elif h != w:
                ok = False
                break
        if ok:
            return True
    return False


class ColoaneAmbigue(FisierNecitit):
    pass


def coloana(antet, aliasuri, exclus=(), camp=""):
    """Indexul coloanei pentru `camp` sau -1. `antet` = lista de anteturi NORMALIZATE (`norm`).

    Aliasurile se încearcă ÎN ORDINE (primul e cel mai specific). Pentru fiecare: întâi egalitatea, apoi cuvintele întregi;
    un alias care începe cu `=` se potrivește NUMAI prin egalitate („=cont” nu prinde „Cont bancar”).
    Două coloane care se potrivesc la fel cu același alias -> `ColoaneAmbigue` (refuz numit), nu prima dintre ele."""
    exclus = {x for x in (exclus or ()) if x is not None and x >= 0}
    for a in aliasuri:
        numai_egal = str(a).startswith("=")         # „=cont”: numai antetul „Cont”, nu și „Cont bancar” / „Denumire cont”
        an = _alias(str(a).lstrip("="))
        if not an:
            continue
        egale = [j for j, h in enumerate(antet) if j not in exclus and "*" not in an and h == an]
        if len(egale) == 1:
            return egale[0]
        cuv = egale or ([] if numai_egal else
                        [j for j, h in enumerate(antet) if j not in exclus and _potriveste_cuvinte(h, an)])
        if len(cuv) == 1:
            return cuv[0]
        if len(cuv) > 1:
            raise ColoaneAmbigue(
                "Coloanele %s se potrivesc toate la „%s” — nu aleg una la întâmplare. Lasă în fișier una singură sau "
                "redenumește-le." % (", ".join("«%s»" % eticheta(antet, j) for j in cuv), (camp or a).replace("_", " ")))
    return -1


def _pare_subantet(rand):
    """Un rând de sub-antet are numai etichete scurte (Debit / Credit / D / C / Sold), fără numere și fără conturi."""
    celule = [norm(c) for c in rand if str(c if c is not None else "").strip()]
    if len(celule) < 2:
        return False
    for c in celule:
        if re.fullmatch(r"[\d ]+", c):
            return False
    return all(all(w in _SUBANTET or w.startswith(("debit", "credit")) for w in c.split()) for c in celule)


_SUBANTET = {"d", "c", "sold", "solduri", "sume", "suma", "lei", "ron"}


class Antet(list):
    """Antetul NORMALIZAT (pentru potriviri), cu `original` = textul din fișier, pentru ecran („Solduri finale Debit”, nu
    „solduri finale debit”)."""
    original = ()


def _antet(celule_originale):
    a = Antet(norm(c) for c in celule_originale)
    a.original = tuple(" ".join(str(c if c is not None else "").split()) for c in celule_originale)
    return a


def _unit(sus, jos):
    """Antetul pe două rânduri: eticheta grupului (de deasupra, întinsă peste celulele goale de după ea) + eticheta de jos."""
    n = max(len(sus), len(jos))
    out, grup = [], ""
    for j in range(n):
        s = sus[j] if j < len(sus) else ""
        if str(s if s is not None else "").strip():
            grup = s
        elif not str(jos[j] if j < len(jos) else "").strip():
            grup = ""
        d = jos[j] if j < len(jos) else ""
        out.append("%s %s" % (grup if str(d or "").strip() else s, d or ""))
    return _antet(out)


#: Câte rânduri de la începutul fișierului se cercetează după antet (titlurile exportului stau deasupra lui). OPERAȚIONAL, nu fiscal.
RANDURI_CAUTATE_ANTET = 20


def gaseste_antet(randuri, campuri, obligatorii=(), cauta=RANDURI_CAUTATE_ANTET, nume_fisier=""):
    """`(antet_normalizat, index_primul_rand_de_date)`.

    `campuri` = {camp: (aliasuri, ...)}. Se încearcă primele `cauta` rânduri, fiecare singur și unit cu rândul de dedesubt
    (dacă acela e un sub-antet); câștigă varianta care recunoaște cele mai multe câmpuri, iar la egalitate cea mai de sus.
    Fără niciun antet care să conțină toate câmpurile `obligatorii` -> `FisierNecitit` cu ce lipsește."""
    best = None
    for i in range(min(cauta, len(randuri))):
        variante = [(_antet(randuri[i]), i + 1)]
        if i + 1 < len(randuri) and _pare_subantet(randuri[i + 1]):
            variante.append((_unit(randuri[i], randuri[i + 1]), i + 2))
        for antet, start in variante:
            gasite = set()
            for camp, alias in campuri.items():
                try:
                    if coloana(antet, alias, camp=camp) >= 0:
                        gasite.add(camp)
                except ColoaneAmbigue:
                    gasite.add(camp)        # antetul e cel bun; ambiguitatea se raportează la citirea coloanei
            if not all(o in gasite for o in obligatorii):
                continue
            if best is None or len(gasite) > best[0]:
                best = (len(gasite), antet, start)
    if best is None:
        lipsa = ", ".join("„%s”" % o for o in obligatorii) or "niciun câmp cunoscut"
        raise FisierNecitit("Fișierul %s nu are un rând de antet recunoscut: lipsește coloana %s. Verifică dacă ai "
                            "încărcat fișierul potrivit pasului." % (_nume(nume_fisier), lipsa))
    return best[1], best[2]


# ── perechea debit / credit a soldului final (balanța, soldurile pe parteneri) ─────────────────────────────────────────
def _e_debit(h):
    return any(w.startswith("debit") for w in h.split()) or h.split()[-1:] == ["d"]


def _e_credit(h):
    return any(w.startswith("credit") for w in h.split()) or h.split()[-1:] == ["c"]


def pereche_sold_final(antet, nume_fisier=""):
    """`(i_debit, i_credit)` — perechea de SOLD FINAL.

    O balanță de deschidere are o pereche (Sold debitor / Sold creditor): aceea e. O balanță de verificare completă are mai
    multe (solduri inițiale, sume precedente, rulaje, total sume, solduri finale): se ia perechea marcată „final”. Fără o
    pereche „final” neechivocă -> REFUZ numit; niciodată prima pereche (defectul C21 — soldurile inițiale importate tăcut)."""
    deb = [j for j, h in enumerate(antet) if h and _e_debit(h)]
    cre = [j for j, h in enumerate(antet) if h and _e_credit(h)]
    if not deb and not cre:
        raise FisierNecitit("nu se găsesc coloane debit/credit - fișier nerecunoscut")
    if len(deb) <= 1 and len(cre) <= 1:
        return (deb[0] if deb else -1), (cre[0] if cre else -1)
    fin = lambda js: [j for j in js if any(w.startswith("final") for w in antet[j].split())]
    fd, fc = fin(deb), fin(cre)
    if len(fd) == 1 and len(fc) == 1:
        return fd[0], fc[0]
    raise FisierNecitit(
        "Balanța din fișierul %s are mai multe coloane de debit (%s) și de credit (%s), iar soldul final nu se poate "
        "deosebi neechivoc de celelalte. Numește perechea soldurilor finale „Sold final debitor” / „Sold final creditor” (sau "
        "„Solduri finale” deasupra lui „Debit / Credit”) și încarcă fișierul din nou."
        % ("«%s»" % nume_fisier if nume_fisier else "trimis",
           ", ".join("«%s»" % eticheta(antet, j) for j in deb), ", ".join("«%s»" % eticheta(antet, j) for j in cre)))


# ── celelalte perechi ale unei balanțe de verificare (deficiența 425, comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”) ──
# „Când fișierul are soldurile inițiale ale anului și rulajele, ele intră ca sold inițial și sume precedente, cu toate conturile care
# au rulaj.” Termenii grupurilor vin din manualul SAGA C, „Preluare date contabile” (anaf_surse/saga_manual_topic12_…): „Debit iniţial
# an” / „Credit iniţial an”, „Debit precedent” / „Credit precedent” = „rulajele cumulate (inclusiv soldurile iniţiale) - coloanele
# «Total Sume debitoare/creditoare» din balanţa lunii anterioare”. Balanța de verificare SAGA are cinci perechi: solduri inițiale an,
# sume precedente, rulaje (ale lunii), total sume, solduri finale.
#: grupul -> cum îl recunosc în antetul normalizat (cuvinte întregi / început de cuvânt). Ordinea contează: „final” întâi („Sold final”),
#: „precedent” înaintea lui „total” („Total sume precedente” = sume precedente), „total sume” / „cumulat” înaintea lui „rulaj”.
GRUPURI_BALANTA = (
    ("sf", "solduri finale", lambda w: any(x.startswith("final") for x in w)),
    ("sp", "sume precedente", lambda w: any(x.startswith("precedent") for x in w)),
    ("si", "solduri inițiale an", lambda w: any(x.startswith("initial") for x in w)),
    ("ts", "total sume", lambda w: (("total" in w and any(x.startswith(("sum", "rulaj")) for x in w))
                                    or any(x.startswith("cumulat") for x in w))),
    ("rl", "rulaje", lambda w: any(x.startswith(("rulaj", "curent")) for x in w)),
)


def perechi_balanta(antet, nume_fisier=""):
    """`{grup: (i_debit, i_credit)}` — perechile RECUNOSCUTE în afară de soldul final: `si` (solduri inițiale an), `sp` (sume
    precedente), `rl` (rulajele lunii), `ts` (total sume). Un grup are exact o coloană de debit și una de credit; o jumătate de
    pereche sau două coloane pentru același grup -> REFUZ numit (nu aleg una — defectul C21). O balanță cu o singură pereche
    (balanța de deschidere „Sold debitor / Sold creditor”) -> `{}`. O pereche nerecunoscută rămâne necitită (ca până acum)."""
    deb = [j for j, h in enumerate(antet) if h and _e_debit(h)]
    cre = [j for j, h in enumerate(antet) if h and _e_credit(h)]
    if len(deb) <= 1 and len(cre) <= 1:
        return {}

    def grup(h):
        w = h.split()
        for g, _et, potriveste in GRUPURI_BALANTA:
            if potriveste(w):
                return g
        return None

    out = {}
    for g, et, _p in GRUPURI_BALANTA:
        if g == "sf":
            continue
        d = [j for j in deb if grup(antet[j]) == g]
        c = [j for j in cre if grup(antet[j]) == g]
        if not d and not c:
            continue
        if len(d) != 1 or len(c) != 1:
            raise FisierNecitit(
                "Balanța din fișierul %s are pentru „%s” coloanele %s — se așteaptă exact una de debit și una de credit. "
                "Lasă în fișier perechea întreagă (sau scoate-o de tot) și încarcă-l din nou."
                % ("«%s»" % nume_fisier if nume_fisier else "trimis", et,
                   ", ".join("«%s»" % eticheta(antet, j) for j in d + c)))
        out[g] = (d[0], c[0])
    return out



# ── celulele ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def celula(rand, j):
    """Textul celulei `j` (gol dacă lipsește). Un număr întreg din Excel (`12.0`) iese `12`, nu `12.0`."""
    if j is None or j < 0 or j >= len(rand):
        return ""
    v = rand[j]
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()[:10]
    t = str(v).strip()
    # [388, lotul 9] celula scrisă ca text pentru Excel (`="2900215410011"` — forma din modelele descărcate, care păstrează CNP-ul / CUI-ul
    # întreg la deschiderea CSV-ului) se citește ca textul dinăuntru
    if len(t) >= 3 and t.startswith('="') and t.endswith('"'):
        t = t[2:-1].replace('""', '"')
    return t


def valoare(rand, j):
    """Valoarea brută a celulei `j` (numerele și datele din Excel rămân numere și date) sau `""`."""
    if j is None or j < 0 or j >= len(rand):
        return ""
    v = rand[j]
    return "" if v is None else v


#: formatele de dată acceptate în fișierele de import: zi înaintea lunii (forma românească) sau ISO. Forma americană (lună/zi) NU se
#: încearcă: „01/13/2026” nu e o dată românească, iar a o citi ca 13 ianuarie ar fi o înlocuire tăcută (comanda Costin 8.2 pct.4).
FORMATE_DATA = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


def data(v):
    """Data dintr-o celulă -> 'AAAA-LL-ZZ', sau None (celula goală SAU o dată imposibilă — „2026-13-01”, „31.02.2026”). Sursa unică pentru
    importuri (până la comanda 8.2: trei copii — salariați, mijloace fixe, istoric declarații — iar RIP-ul n-o avea deloc și trimitea
    textul la baza de date, deficiența 372). Cine are nevoie să deosebească golul de invalid compară cu `celula`."""
    if v is None or str(v).strip() == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    t = str(v).strip()
    for fmt in FORMATE_DATA:
        try:
            return datetime.datetime.strptime(t, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def rand_gol(rand):
    return not any(str(c if c is not None else "").strip() for c in rand)


def nr_rand(r, i):
    """Numărul rândului din FIȘIER pentru un rând extras (`rand_fisier`, pus de parser), altfel poziția `i` (convenția veche:
    antetul pe rândul 1). Cu titluri deasupra antetului („Balanță de verificare”, firma, perioada), „rândul 2” al convenției
    vechi arăta alt rând decât cel greșit."""
    try:
        v = int(r.get("rand_fisier") or 0)
    except (TypeError, ValueError, AttributeError):
        v = 0
    return v if v > 0 else i


def eticheta(antet, j):
    """Textul din fișier al coloanei `j` (pentru ecran); `""` dacă lipsește."""
    if j is None or j < 0:
        return ""
    orig = getattr(antet, "original", ()) or ()
    return orig[j].strip() if j < len(orig) and orig[j].strip() else (antet[j] if j < len(antet) else "")

