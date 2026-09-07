"""core/d213.py — Formular 213: Declaratie privind veniturile realizate de persoana fizica si/sau
juridica din INSTRAINAREA, prin vanzare, a PACHETULUI DE CONTROL al persoanelor juridice care au in
proprietate unul sau mai multe TERENURI AGRICOLE situate in EXTRAVILAN.

ACT: Ordin ANAF 216/2023 (MO 165/27.02.2023), Procedura de stabilire a impozitului pe veniturile din
instrainarea terenurilor agricole extravilan / pachetului de control; temei Legea 17/2014 art. 42
(salvat in anaf_surse/opanaf_216_2023_formular_213_instrainare_pachet_control_terenuri_agricole_
extravilan.{html,txt}). NU e declaratie de "norme de venit" - aceea e alt formular; SURSA (validatorul
oficial + Ordinul 216/2023) BATE denumirea generica din sarcina.

Se completeaza de PF/PJ care instraineaza prin vanzare pachetul de control (>25% din activ) al unei PJ
ce detine teren agricol extravilan, in max. 8 ani de la dobandire. Venitul impozabil = diferenta
valorica POZITIVA intre valoarea de instrainare si cea de dobandire, defalcata pe fiecare UAT unde e
situat terenul (`valoare` per `dateTeren`). Baza (`bazaImpozit`) = suma acestor diferente. Impozitul e
STABILIT de organul fiscal (nu de declarant) -> suma de control `totalPlata_A` = 0. Aplicatia nu are
registru de terenuri -> totul vine din `manual`; NU se hardcodeaza cote/valori (se dau ca `valoare`).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator / D213Validator.jar), namespace
`mfp:anaf:dgti:d213:declaratie:v1`, pachet `d213validator/v0`. Structura + regulile au fost CITITE din
bytecode (clasele D213 = elementul RADACINA <D213>, DateTeren = elementul copil repetat) si PROBATE
camp cu camp pe validator pana la rezultat VALID ("ok").

Radacina reala = <D213> (NU `declaratie` / `declaratie213` - respinse "sectiune necunoscuta").
Atribute radacina OBLIGATORII (probate): d_rec (0..1), cifContribuabil (CNP), an (interval 2023..2100),
luna (1..12), numeContribuabil, adresaContribuabil, totalPlata_A (=0), taraRezidenta (cod ISO-3166
numeric, ex. 642=Romania), actInstrainare, dataAct (dd.mm.yyyy), bazaImpozit (>0, =suma valorilor),
numeD, functieD. Conditional: index_init (DOAR la rectificativa, d_rec=1). Optionale: telC, faxC, emailC,
denR, cifR, adresaR, telR, faxR, emailR.
Element copil `dateTeren` (1..n) = teren agricol pe UAT: judet (cod numeric jude din lista
validatorului: 2..46,51,52), uat (cod localitate/UAT, interval 0..100), cifUat (cod de identificare
fiscala al UAT), valoare (>0 = diferenta valorica pozitiva instrainare-dobandire pe acel UAT).

Reguli citite din validator (probate):
  - DUK regula R_bazaImpozit_pozitiv: "bazaImpozit trebuie sa fie mai mare ca 0".
  - DUK regula R_bazaImpozit_suma: "bazaImpozit trebuie sa fie egal cu suma tuturor valorilor".
  - DUK regula R_valoare_pozitiv: "valoare trebuie sa fie mai mare ca 0" (pe fiecare dateTeren).
  - DUK regula R_totalPlata: "Suma de control trebuie sa fie 0" (ANAF determina impozitul).
  - DUK regula R_index_init: "index_init trebuie completat daca si numai daca d_rec este 1".
  - DUK regula R8: "Daca cifContribuabil este un NIF atunci taraRezidenta trebuie completat".
    NOTA: validatorul trateaza CNP-urile drept NIF -> `taraRezidenta` se emite INTOTDEAUNA
    (implicit 642 = Romania), altfel R8 pica.

Contract dXXX: pull/erori_generare/calcul_d213/build_xml/genereaza(conn, schema, perioada, manual).
D213 e MANUALA: `pull` intoarce {} si `genereaza` merge cu conn=None (nu se trage nimic din firma).
NEPOPULAT deliberat (optionale, se emit doar daca sunt in `manual`, nu se ghicesc): telC/faxC/emailC
(contact contribuabil) si blocul imputernicit denR/cifR/adresaR/telR/faxR/emailR.
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind veniturile realizate de persoana fizică și/sau asocierea fără personalitate juridică'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d213:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
# Coduri de judet acceptate de validator (Parameters_v0._listaCodJud).
_JUDETE = set(range(2, 47)) | {51, 52}
_DATA_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != 13:
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _suma(x):
    """Rotunjire half-up pe suma (lei intregi) cu Decimal.quantize(ROUND_HALF_UP). nu bancara."""
    try:
        d = Decimal(str(x).replace(",", ".").strip() or "0")
    except Exception:
        return 0
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _int(x, dflt=None):
    try:
        return int(str(x).strip())
    except (TypeError, ValueError):
        return dflt


def _terenuri(manual):
    """Normalizeaza lista de terenuri din `manual` (cheie 'terenuri' sau 'dateTeren')."""
    raw = manual.get("terenuri")
    if raw is None:
        raw = manual.get("dateTeren")
    return list(raw or [])


@dataclass
class Rezultat213:
    an: int
    luna: int
    baza_impozit: int = 0
    total_plata_a: int = 0
    nr_terenuri: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d213(manual):
    """bazaImpozit = suma tuturor `valoare` (diferentele valorice pozitive pe UAT-uri;
    DUK regula R_bazaImpozit_suma). totalPlata_A = 0 (DUK regula R_totalPlata: suma de control 0,
    impozitul e stabilit de organul fiscal, nu de declarant)."""
    baza = sum(_suma(t.get("valoare")) for t in _terenuri(manual))
    return {"bazaImpozit": baza, "totalPlata_A": 0}


def pull(conn, schema, perioada):
    """D213 e MANUALA pe persoana fizica; firma nu are registru de terenuri agricole.
    Contractul dXXX cere `pull`; nu exista date de tras din firma_profil -> {}. conn poate fi None."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsă nume contribuabil (nume_c).")
    if not str(manual.get("adresa_c") or "").strip():
        er.append("Lipsă adresa contribuabil (adresa_c).")
    cif = _cif(manual.get("cif_c"))
    if not (_cnp_valid(cif) or (2 <= len(cif) <= 13)):
        er.append("cif_c (CNP/NIF contribuabil) invalid.")
    # declarant / semnatar (numeD + functieD obligatorii pe validator)
    if not str(manual.get("nume_d") or "").strip():
        er.append("Lipsă nume declarant/semnatar (nume_d).")
    if not str(manual.get("functie_d") or "").strip():
        er.append("Lipsă funcție declarant/semnatar (functie_d).")
    # act de instrainare (actInstrainare + dataAct obligatorii pe validator)
    if not str(manual.get("act_instrainare") or "").strip():
        er.append("Lipsă act de instrainare (act_instrainare).")
    da = str(manual.get("data_act") or "").strip()
    if not _DATA_RE.match(da):
        er.append("data_act obligatorie, format zz.ll.aaaa.")
    tara = _cif(manual.get("tara_rezidenta")) or "642"
    if len(tara) != 3:
        er.append("tara_rezidenta trebuie cod ISO-3166 numeric din 3 cifre (642=Romania).")
    d_rec = _int(manual.get("d_rec"), 0)
    if d_rec not in (0, 1):
        er.append("d_rec trebuie 0 (initiala) sau 1 (rectificativa).")
    if d_rec == 1 and not str(manual.get("index_init") or "").strip():
        er.append("Rectificativa (d_rec=1) cere index_init (DUK regula R_index_init).")
    if d_rec == 0 and str(manual.get("index_init") or "").strip():
        er.append("index_init se completează doar la rectificativa (DUK regula R_index_init).")
    an = _int(manual.get("an"))
    if an is None or not (2023 <= an <= 2100):
        er.append("an trebuie în intervalul 2023..2100.")
    luna = _int(manual.get("luna"))
    if luna is None or not (1 <= luna <= 12):
        er.append("luna trebuie în intervalul 1..12.")
    ter = _terenuri(manual)
    if not ter:
        er.append("Lipsă terenuri (cel puțin un dateTeren cu județ/cif_uat/uat/valoare).")
    for i, t in enumerate(ter, 1):
        if _int(t.get("judet")) not in _JUDETE:
            er.append("teren #%d: județ (cod din 2..46,51,52) invalid." % i)
        if not _cif(t.get("cif_uat")):
            er.append("teren #%d: lipsă cif_uat (codul fiscal UAT)." % i)
        u = _int(t.get("uat"))
        if u is None or not (0 <= u <= 100):
            er.append("teren #%d: uat (cod UAT) trebuie în intervalul 0..100." % i)
        if _suma(t.get("valoare")) <= 0:
            er.append("teren #%d: valoare trebuie > 0 (DUK regula R_valoare_pozitiv)." % i)
    if not er and calcul_d213(manual)["bazaImpozit"] <= 0:
        er.append("bazaImpozit (suma valorilor) trebuie > 0 (DUK regula R_bazaImpozit_pozitiv).")
    return er


def _attr(name, val):
    return ' %s="%s"' % (name, val)


def build_xml(prof, an, luna, manual):
    c = calcul_d213(manual)
    d_rec = _int(manual.get("d_rec"), 0)
    tara = _cif(manual.get("tara_rezidenta")) or "642"
    h = []
    h.append(_attr("d_rec", d_rec))
    if d_rec == 1 and str(manual.get("index_init") or "").strip():
        h.append(_attr("index_init", _esc(manual.get("index_init"))))
    h.append(_attr("cifContribuabil", _cif(manual.get("cif_c"))))
    h.append(_attr("an", int(an)))
    h.append(_attr("luna", int(luna)))
    h.append(_attr("numeContribuabil", _esc(manual.get("nume_c"), 205)))
    h.append(_attr("adresaContribuabil", _esc(manual.get("adresa_c"), 205)))
    h.append(_attr("totalPlata_A", c["totalPlata_A"]))
    h.append(_attr("taraRezidenta", tara))
    h.append(_attr("actInstrainare", _esc(manual.get("act_instrainare"), 205)))
    h.append(_attr("dataAct", _esc(manual.get("data_act"))))
    h.append(_attr("bazaImpozit", c["bazaImpozit"]))
    # contact contribuabil (optional)
    for cheie, atr, lim in (("tel_c", "telC", 30), ("fax_c", "faxC", 30),
                            ("email_c", "emailC", 100)):
        if str(manual.get(cheie) or "").strip():
            h.append(_attr(atr, _esc(manual.get(cheie), lim)))
    # imputernicit / reprezentant (optional)
    for cheie, atr, lim in (("den_r", "denR", 205), ("cif_r", "cifR", 13),
                            ("adresa_r", "adresaR", 205), ("tel_r", "telR", 30),
                            ("fax_r", "faxR", 30), ("email_r", "emailR", 100)):
        v = manual.get(cheie)
        if str(v or "").strip():
            v = _cif(v) if atr == "cifR" else _esc(v, lim)
            h.append(_attr(atr, v))
    # declarant / semnatar (obligatoriu)
    h.append(_attr("numeD", _esc(manual.get("nume_d"), 205)))
    h.append(_attr("functieD", _esc(manual.get("functie_d"), 205)))
    linii = []
    for t in _terenuri(manual):
        linii.append('  <dateTeren judet="%d" cifUat="%s" uat="%d" valoare="%d"/>' % (
            int(t.get("judet")), _cif(t.get("cif_uat")), int(t.get("uat")),
            _suma(t.get("valoare"))))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D213 xmlns="%s"%s>\n%s\n</D213>\n' % (NS, "".join(h), "\n".join(linii)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = _int(manual.get("an"), None)
    if an is None and perioada is not None:
        an = int(perioada.an)
        manual["an"] = an
    luna = _int(manual.get("luna"), None)
    if luna is None and perioada is not None:
        luna = int(perioada.luna)
        manual["luna"] = luna
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D213 nu se poate genera: " + " ".join(er))
    c = calcul_d213(manual)
    xml = build_xml(prof, int(manual["an"]), int(manual["luna"]), manual)
    res = Rezultat213(an=int(manual["an"]), luna=int(manual["luna"]),
                      baza_impozit=c["bazaImpozit"], total_plata_a=c["totalPlata_A"],
                      nr_terenuri=len(_terenuri(manual)))
    return xml, res
