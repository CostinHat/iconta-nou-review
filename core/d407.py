"""core/d407.py - D407: Declaratie informativa privind persoanele si sumele/produsele
financiare ce fac obiectul schimbului automat de informatii (institutii financiare
raportoare - polite de asigurare de viata / detinatori de instrumente financiare).
Namespace mfp:anaf:dgti:d407:declaratie:v1, versiune D407_4 (versiuni.xml ANAF).

Declaratie INFORMATIVA depusa de institutia financiara raportoare. Doua tipuri de document
(atribut tipDoc): tipDoc=1 raportare polite (POLITA + ASIGURAT + EVENIMENT + BENEFICIARI),
tipDoc=2 lista de persoane cu instrumente financiare (LISTAPERSOANE). luna de raportare = 6
sau 12 (raportare semestriala / anuala).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator / D407Validator.jar).
Structura in vigoare (namespace declaratie:v1, pachet d407validator/v0) a fost CITITA din
bytecode-ul D407Validator.jar (clasele ValidatorImpl / D407 / POLITA / ASIGURAT / EVENIMENT /
BENEFICIARI / LISTAPERSOANE) si PROBATA camp cu camp pe validatorul oficial (DUK VALID).
Nu exista XSD public (validatorul e jar-only); nomenclatoarele judet/tara/valuta se incarca de
validator din baza DUK la rulare (nu sunt in jar) - deci nu se pot lista aici; DUK e arbitrul lor.

Radacina confirmata din bytecode (DECTag[0] = "D407", ValidatorImpl.insertD407): <D407>.
Ierarhie (min-max ocurente din DECTag): D407(1-1) > POLITA(0-n, doar tipDoc=1) > {ASIGURAT(0-10),
EVENIMENT(0-n), BENEFICIARI(1-n)}; D407 > LISTAPERSOANE(0-n, doar tipDoc=2).

Reguli probate (citari "DUK regula ..."):
  - R4  : totalPlata_A = suma cifrelor (a digitilor) CIF-ului declarant (cif). Nu e suma monetara;
          e suma de control pe cifrele CUI. (Confirmat: cif 12345678 -> totalPlata_A=36.)
  - RLuna: luna trebuie sa fie 6 sau 12.
  - an   : interval [2025, 2100] (an raportare).
  - R18/R19: cif reprezentant (cifR) / domiciliu reprezentant (adresaR) se completeaza numai daca
          denumire reprezentant (denR) este completat.
  - "Polita exista numai daca tip document este 1"; "ListaPersoane exista numai daca tip
          document este 2".
  - CIF (cif, cif_A, cif_benef, cif_d, ...) validat ca CUI/CNP de validator (nextAttributeAsCif;
          confirmat: CUI invalid respins).
Domenii enum (interval din bytecode): tipDoc[1,2], d_rec[0,1], status_polita[1,2],
clasa_asigurari[1,7], tip_persoana[1,3], tip_eveniment[1,7], mod_plata[1,11], tip_instrument[1,2],
toate bifa_*[0,1]. Date format ZZ.LL.AAAA (dd.mm.yyyy). Sume monetare: pattern zecimal (max 13).

Declaratie MANUALA: institutia raportoare furnizeaza TOATE datele prin `manual` (aplicatia nu are
registru de polite/detinatori). NU se fabrica valori. `conn` nu e folosit (pull returneaza {}),
deci genereaza(conn=None, ...) functioneaza.

NEPOPULAT deliberat (optional in validator, se completeaza de raportor la nevoie, aceeasi metoda):
antet - suma, nr_persoane, sector, denR/cifR/adresaR (reprezentant); POLITA - toate campurile
in afara de nr_polita/nr_contract/status_polita; ASIGURAT/EVENIMENT (sectiuni optionale);
LISTAPERSOANE - toate campurile (toate optionale in validator).

Contract dXXX: pull / erori_generare / calcul_d407 / build_xml / genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație informativă privind persoanele și sumele/produsele declarate de intermediari'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d407:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
_CUI_W = [7, 5, 3, 2, 1, 7, 5, 3, 2]  # cheia de control CUI ANAF

_STATUS_POLITA = frozenset((1, 2))
_CLASA_ASIG = frozenset(range(1, 8))          # [1,7]
_TIP_PERSOANA = frozenset((1, 2, 3))
_TIP_EVENIMENT = frozenset(range(1, 8))       # [1,7]
_MOD_PLATA = frozenset(range(1, 12))          # [1,11]
_TIP_INSTRUMENT = frozenset((1, 2))
_BIFA = frozenset((0, 1))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _sum_digits(cif):
    """DUK regula R4: totalPlata_A = suma cifrelor CIF-ului declarant."""
    return sum(int(c) for c in _cif(cif))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != 13 or cnp[0] == "0":
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _cui_valid(cui):
    cui = _cif(cui)
    if not (2 <= len(cui) <= 10) or cui[0] == "0":
        return False
    body = cui[:-1].rjust(9, "0")
    s = sum(int(body[i]) * _CUI_W[i] for i in range(9))
    c = (s * 10) % 11
    c = 0 if c == 10 else c
    return c == int(cui[-1])


def _cif_valid(x):
    """cif validat ca CUI sau CNP (nextAttributeAsCif din validator accepta ambele)."""
    return _cui_valid(x) or _cnp_valid(x)


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _dbl(x):
    """Suma monetara zecimala (pattern Dbl, max 13), rotunjire half-up (Decimal.quantize)."""
    if x in (None, ""):
        return None
    d = Decimal(str(x).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "%s" % d


_RE_ZLLA = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")
_RE_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")


def _parse_data(x):
    """Accepta ZZ.LL.AAAA, AAAA-LL-ZZ sau obiect date/datetime. Returneaza (an, luna, zi) sau None."""
    if x in (None, ""):
        return None
    if hasattr(x, "year") and hasattr(x, "month") and hasattr(x, "day"):
        y, mo, d = int(x.year), int(x.month), int(x.day)
    else:
        s = str(x).strip()
        m = _RE_ZLLA.match(s)
        if m:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = _RE_ISO.match(s)
            if not m:
                return None
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31 and 1000 <= y <= 9999):
        return None
    return (y, mo, d)


def _fmt_data(t):
    """(an, luna, zi) -> 'ZZ.LL.AAAA' (dd.mm.yyyy). Fara strftime."""
    return "%02d.%02d.%04d" % (t[2], t[1], t[0])


def _int_in(val, dom):
    try:
        return int(val) in dom
    except (TypeError, ValueError):
        return False


@dataclass
class Rezultat407:
    an: int
    luna: int
    tip_doc: int = 1
    total_plata_a: int = 0
    nr_polite: int = 0
    nr_persoane: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d407(manual):
    """DUK regula R4: totalPlata_A = suma cifrelor CIF-ului declarant (nu suma monetara)."""
    return {"totalPlata_A": _sum_digits(manual.get("cif"))}


def pull(conn, schema, perioada):
    """D407 e MANUALA: institutia raportoare furnizeaza politele/detinatorii. Aplicatia nu are
    registru; `conn` nu e folosit (merge conn=None)."""
    return {}


def _attr(name, val):
    return '%s="%s"' % (name, val)


def _add(parts, name, val, esc=True, lim=None):
    if val is None or (isinstance(val, str) and not val.strip()):
        return
    v = _esc(val, lim) if esc else val
    parts.append(_attr(name, v))


def erori_generare(prof, manual):
    er = []
    # --- perioada / tip document ---
    try:
        luna = int(prof.get("luna") or manual.get("luna") or 0)
    except (TypeError, ValueError):
        luna = 0
    if luna not in (6, 12):
        er.append("luna raportare trebuie să fie 6 sau 12 (DUK regula RLuna).")
    an = int(prof.get("an") or 0)
    if not (2025 <= an <= 2100):
        er.append("an raportare în afară intervalului [2025, 2100] (DUK regula an).")
    if not _int_in(manual.get("tip_doc"), (1, 2)):
        er.append("tipDoc (tip_doc) obligatoriu 1 (polite) sau 2 (lista persoane).")
    try:
        d_rec = int(manual.get("d_rec") or 0)
    except (TypeError, ValueError):
        d_rec = -1
    if d_rec not in (0, 1):
        er.append("d_rec obligatoriu 0 (initiala) sau 1 (rectificativa).")
    # --- antet declarant ---
    if not _cif_valid(manual.get("cif")):
        er.append("CIF declarant (cif) invalid - CUI sau CNP cu cheie de control "
                  "(DUK regula nextAttributeAsCif).")
    for camp, et in (("den", "Denumire declarant (den)"),
                     ("adresa", "Adresa declarant (adresa)"),
                     ("localitate", "Localitate (localitate)"),
                     ("forma_j", "Forma juridica (forma_j)"),
                     ("nume", "Nume declarant/semnatar (nume)"),
                     ("functia", "Funcția (funcția)")):
        if not str(manual.get(camp) or "").strip():
            er.append("Lipsa " + et + ".")
    try:
        int(manual.get("judet"))
    except (TypeError, ValueError):
        er.append("județ (cod numeric) obligatoriu (nomenclator DUK).")
    if not str(manual.get("tara_rap") or "").strip():
        er.append("tara_rap (cod țară) obligatoriu (nomenclator DUK).")
    # reprezentant: cifR/adresaR doar daca denR completat (R18/R19)
    denR = str(manual.get("den_r") or "").strip()
    if not denR:
        if str(manual.get("cif_r") or "").strip():
            er.append("cif reprezentant (cif_r) doar dacă denumire reprezentant (den_r) "
                      "completat (DUK regula R18).")
        if str(manual.get("adresa_r") or "").strip():
            er.append("domiciliu reprezentant (adresa_r) doar dacă den_r completat (DUK regula R19).")
    if manual.get("cif_r") and not _cif_valid(manual.get("cif_r")):
        er.append("cif reprezentant (cif_r) invalid.")

    tip = manual.get("tip_doc")
    if _int_in(tip, (1,)):
        polite = manual.get("polite") or []
        if not polite:
            er.append("tipDoc=1: cel putin o <POLITA> (polite) obligatorie.")
        for i, p in enumerate(polite, 1):
            pf = "polita #%d: " % i
            if not str(p.get("nr_polita") or "").strip():
                er.append(pf + "lipsă nr_polita.")
            if not str(p.get("nr_contract") or "").strip():
                er.append(pf + "lipsă nr_contract.")
            if not _int_in(p.get("status_polita"), _STATUS_POLITA):
                er.append(pf + "status_polita obligatoriu în [1,2].")
            if p.get("clasa_asigurari") is not None and not _int_in(p.get("clasa_asigurari"), _CLASA_ASIG):
                er.append(pf + "clasa_asigurari în [1,7].")
            if p.get("tip_persoana") is not None and not _int_in(p.get("tip_persoana"), _TIP_PERSOANA):
                er.append(pf + "tip_persoana în [1,3].")
            for db in ("data_inceput", "data_sfarsit", "data_incetare", "data_rascumparare",
                       "data_eveniment"):
                if p.get(db) and _parse_data(p.get(db)) is None:
                    er.append(pf + "%s format ZZ.LL.AAAA." % db)
            if p.get("cif_c") and not _cif_valid(p.get("cif_c")):
                er.append(pf + "cifC (cif_c) invalid.")
            if p.get("cif_benef2") and not _cif_valid(p.get("cif_benef2")):
                er.append(pf + "cif_benef2 invalid.")
            benef = p.get("beneficiari") or []
            if not benef:
                er.append(pf + "cel putin un <BENEFICIARI> (beneficiari) obligatoriu.")
            for j, b in enumerate(benef, 1):
                bf = pf + "beneficiar #%d: " % j
                if b.get("cif_benef") and not _cif_valid(b.get("cif_benef")):
                    er.append(bf + "cif_benef invalid.")
                for bx in ("bifa_a", "bifa_tp", "bifa_ms"):
                    if b.get(bx) is not None and not _int_in(b.get(bx), _BIFA):
                        er.append(bf + "%s în [0,1]." % bx)
            asig = p.get("asigurati") or []
            if len(asig) > 10:
                er.append(pf + "maxim 10 <ASIGURAT> pe polita.")
            for j, a in enumerate(asig, 1):
                if a.get("cif_a") and not _cif_valid(a.get("cif_a")):
                    er.append(pf + "asigurat #%d: cif_A invalid." % j)
            for j, ev in enumerate(p.get("evenimente") or [], 1):
                ef = pf + "eveniment #%d: " % j
                if ev.get("tip_eveniment") is not None and not _int_in(ev.get("tip_eveniment"), _TIP_EVENIMENT):
                    er.append(ef + "tip_eveniment în [1,7].")
                if ev.get("mod_plata") is not None and not _int_in(ev.get("mod_plata"), _MOD_PLATA):
                    er.append(ef + "mod_plata în [1,11].")
                if ev.get("data_producere") and _parse_data(ev.get("data_producere")) is None:
                    er.append(ef + "data_producere format ZZ.LL.AAAA.")
                if ev.get("cif_benef_1") and not _cif_valid(ev.get("cif_benef_1")):
                    er.append(ef + "cif_benef_1 invalid.")
    elif _int_in(tip, (2,)):
        persoane = manual.get("persoane") or []
        if not persoane:
            er.append("tipDoc=2: cel putin o <LISTAPERSOANE> (persoane) obligatorie.")
        for i, pp in enumerate(persoane, 1):
            lf = "persoana #%d: " % i
            if pp.get("cif_d") and not _cif_valid(pp.get("cif_d")):
                er.append(lf + "cif_d invalid.")
            if pp.get("tip_instrument") is not None and not _int_in(pp.get("tip_instrument"), _TIP_INSTRUMENT):
                er.append(lf + "tip_instrument în [1,2].")
    return er


def build_xml(prof, an, luna, manual):
    tip = int(manual.get("tip_doc"))
    total = calcul_d407(manual)["totalPlata_A"]
    h = []
    h.append(_attr("luna", "%d" % int(luna)))
    h.append(_attr("an", "%d" % int(an)))
    h.append(_attr("d_rec", "%d" % int(manual.get("d_rec") or 0)))
    h.append(_attr("tipDoc", "%d" % tip))
    h.append(_attr("totalPlata_A", "%d" % total))
    h.append(_attr("den", _esc(manual.get("den"), 200)))
    h.append(_attr("cif", _cif(manual.get("cif"))))
    h.append(_attr("adresa", _esc(manual.get("adresa"), 200)))
    h.append(_attr("localitate", _esc(manual.get("localitate"), 100)))
    h.append(_attr("judet", "%d" % int(manual.get("judet"))))
    h.append(_attr("tara_rap", _esc(str(manual.get("tara_rap")).upper(), 5)))
    h.append(_attr("forma_j", _esc(manual.get("forma_j"), 50)))
    h.append(_attr("nume", _esc(manual.get("nume"), 75)))
    h.append(_attr("functia", _esc(manual.get("functia"), 50)))
    if manual.get("sector") not in (None, ""):
        h.append(_attr("sector", _esc(manual.get("sector"), 10)))
    if manual.get("nr_persoane") not in (None, ""):
        h.append(_attr("nr_persoane", "%d" % int(manual.get("nr_persoane"))))
    if _dbl(manual.get("suma")) is not None:
        h.append(_attr("suma", _dbl(manual.get("suma"))))
    if str(manual.get("den_r") or "").strip():
        h.append(_attr("denR", _esc(manual.get("den_r"), 200)))
        if manual.get("cif_r"):
            h.append(_attr("cifR", _cif(manual.get("cif_r"))))
        if manual.get("adresa_r"):
            h.append(_attr("adresaR", _esc(manual.get("adresa_r"), 200)))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<D407 xmlns="%s" %s>' % (NS, " ".join(h))]

    if tip == 1:
        for p in manual.get("polite") or []:
            pa = []
            pa.append(_attr("nr_polita", _esc(p.get("nr_polita"), 50)))
            pa.append(_attr("nr_contract", _esc(p.get("nr_contract"), 50)))
            pa.append(_attr("status_polita", "%d" % int(p.get("status_polita"))))
            if p.get("clasa_asigurari") is not None:
                pa.append(_attr("clasa_asigurari", "%d" % int(p.get("clasa_asigurari"))))
            for dnum in ("data_inceput", "data_sfarsit", "data_incetare",
                         "data_rascumparare", "data_eveniment"):
                dt = _parse_data(p.get(dnum))
                if dt:
                    pa.append(_attr(dnum, _fmt_data(dt)))
            for bx in ("bifa_anuitate", "bifa_anuitate_pd", "bifa_st", "bifa_am", "transfer",
                       "rascumparare", "cesionare", "bifa_val", "bifa_altele", "bifa_necunoscut"):
                if p.get(bx) is not None:
                    pa.append(_attr(bx, "%d" % int(p.get(bx))))
            for snum, valn in (("suma_tranzactie1", "valuta1"), ("suma_tranzactie2", "valuta2"),
                               ("suma_tranzactie3", "valuta3"), ("suma_plata2", "valuta4")):
                if _dbl(p.get(snum)) is not None:
                    pa.append(_attr(snum, _dbl(p.get(snum))))
                if p.get(valn):
                    pa.append(_attr(valn, _esc(str(p.get(valn)).upper(), 5)))
            if p.get("tip_persoana") is not None:
                pa.append(_attr("tip_persoana", "%d" % int(p.get("tip_persoana"))))
            _add(pa, "denC", p.get("den_c"), lim=200)
            if p.get("cif_c"):
                pa.append(_attr("cifC", _cif(p.get("cif_c"))))
            _add(pa, "adresaC", p.get("adresa_c"), lim=200)
            _add(pa, "cif_rez", p.get("cif_rez"), lim=20)
            _add(pa, "tara_rez", p.get("tara_rez") and str(p.get("tara_rez")).upper(), lim=5)
            _add(pa, "den_benef2", p.get("den_benef2"), lim=200)
            if p.get("cif_benef2"):
                pa.append(_attr("cif_benef2", _cif(p.get("cif_benef2"))))
            _add(pa, "IBAN", p.get("iban"), lim=24)
            parts.append("  <POLITA %s>" % " ".join(pa))
            for a in p.get("asigurati") or []:
                aa = []
                _add(aa, "den_A", a.get("den_a"), lim=200)
                if a.get("cif_a"):
                    aa.append(_attr("cif_A", _cif(a.get("cif_a"))))
                _add(aa, "adresa_A", a.get("adresa_a"), lim=200)
                _add(aa, "cif_rezA", a.get("cif_reza"), lim=20)
                _add(aa, "tara_rezA", a.get("tara_reza") and str(a.get("tara_reza")).upper(), lim=5)
                parts.append("    <ASIGURAT %s/>" % " ".join(aa))
            for ev in p.get("evenimente") or []:
                ea = []
                if ev.get("tip_eveniment") is not None:
                    ea.append(_attr("tip_eveniment", "%d" % int(ev.get("tip_eveniment"))))
                dt = _parse_data(ev.get("data_producere"))
                if dt:
                    ea.append(_attr("data_producere", _fmt_data(dt)))
                if ev.get("mod_plata") is not None:
                    ea.append(_attr("mod_plata", "%d" % int(ev.get("mod_plata"))))
                if _dbl(ev.get("suma_platita")) is not None:
                    ea.append(_attr("suma_platita", _dbl(ev.get("suma_platita"))))
                _add(ea, "valuta_ev", ev.get("valuta_ev") and str(ev.get("valuta_ev")).upper(), lim=5)
                if _dbl(ev.get("anuitati_platite")) is not None:
                    ea.append(_attr("anuitati_platite", _dbl(ev.get("anuitati_platite"))))
                if _dbl(ev.get("anuitati_viitoare")) is not None:
                    ea.append(_attr("anuitati_viitoare", _dbl(ev.get("anuitati_viitoare"))))
                _add(ea, "den_benef_1", ev.get("den_benef_1"), lim=200)
                if ev.get("cif_benef_1"):
                    ea.append(_attr("cif_benef_1", _cif(ev.get("cif_benef_1"))))
                _add(ea, "IBAN2", ev.get("iban2"), lim=34)
                parts.append("    <EVENIMENT %s/>" % " ".join(ea))
            for b in p.get("beneficiari") or []:
                ba = []
                for bx in ("bifa_a", "bifa_tp", "bifa_ms"):
                    if b.get(bx) is not None:
                        ba.append(_attr(bx, "%d" % int(b.get(bx))))
                _add(ba, "den_benef", b.get("den_benef"), lim=200)
                if b.get("cif_benef"):
                    ba.append(_attr("cif_benef", _cif(b.get("cif_benef"))))
                _add(ba, "adresa_benef", b.get("adresa_benef"), lim=200)
                if b.get("cota") not in (None, ""):
                    ba.append(_attr("cota", _esc(b.get("cota"), 10)))
                parts.append("    <BENEFICIARI %s/>" % " ".join(ba))
            parts.append("  </POLITA>")
    else:
        for pp in manual.get("persoane") or []:
            la = []
            _add(la, "den_d", pp.get("den_d"), lim=200)
            if pp.get("cif_d"):
                la.append(_attr("cif_d", _cif(pp.get("cif_d"))))
            _add(la, "serie_act", pp.get("serie_act"), lim=50)
            _add(la, "adresa_d", pp.get("adresa_d"), lim=200)
            _add(la, "adresa_d_rez", pp.get("adresa_d_rez"), lim=200)
            if pp.get("tip_instrument") is not None:
                la.append(_attr("tip_instrument", "%d" % int(pp.get("tip_instrument"))))
            _add(la, "den_emitent", pp.get("den_emitent"), lim=200)
            _add(la, "simbol", pp.get("simbol"), lim=13)
            _add(la, "isin", pp.get("isin"), lim=13)
            if pp.get("cantitatea") not in (None, ""):
                la.append(_attr("cantitatea", _esc(pp.get("cantitatea"), 20)))
            _add(la, "informatii", pp.get("informatii"), lim=200)
            parts.append("  <LISTAPERSOANE %s/>" % " ".join(la))

    parts.append("</D407>")
    return "\n".join(parts) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = int(manual.get("luna") or perioada.luna)
    prof = pull(conn, schema, perioada)
    prof["an"] = an
    prof["luna"] = luna
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D407 nu se poate genera: " + " ".join(er))
    tip = int(manual.get("tip_doc"))
    total = calcul_d407(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat407(an=an, luna=luna, tip_doc=tip, total_plata_a=total,
                      nr_polite=len(manual.get("polite") or []),
                      nr_persoane=len(manual.get("persoane") or []))
    return xml, res
