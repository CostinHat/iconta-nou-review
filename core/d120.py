"""core/d120.py - D120: Decont privind accizele.

Decont ANUAL al accizelor datorate (Codul fiscal, Titlul VIII - accize). Contribuabilul (antrepozitar /
destinatar inregistrat / expeditor / importator autorizat) declara pe categorii de produse accizabile
cantitatile, bazele si accizele datorate, plus deducerile aferente.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator / D120Validator.jar). Structura schemei in
vigoare (namespace declaratie:v5, pachet d120validator/v5) a fost CITITA din bytecode-ul validatorului
(clasele Declaratie120 / Accize v5) si PROBATA camp cu camp pe DUK. Constatari care BAT premisele initiale:

  - Radacina XML: <declaratie120>. O SINGURA sectiune <accize> (litere mici). NU e repetabila la nivel de
    element: al doilea <accize> => "sectiune gresit pozitionata". "Produsele accizabile" sunt RANDURILE
    (coloanele R0..R41 pe C1/C2/C3) din interiorul unicului element <accize>, nu elemente <accize> repetate.
  - totalPlata_A (suma de control din antet) TREBUIE sa fie 0 pentru D120 (regula validator:
    "Suma de control trebuie sa fie 0"). O valoare != 0 arunca ClassCastException in agregarea validatorului.
    Deci accizele se declara in coloanele R*/ded*; campul de control totalPlata_A ramane 0. (Premisa din
    sarcina - "totalPlata_A = suma sumelor de plata" - e infirmata de arbitru; pastram aritmetica documentata
    in calcul_d120 dar EMITEM 0, cf. validatorului.)
  - Antet OBLIGATORIU (probat pe DUK, "atributul trebuie sa existe"): luna, an, d_rec, cui, den, adresa,
    caen, nume_declar, prenume_declar, functie_declar, totalPlata_A. OPTIONALE: cifS, cifR, denR, adrR,
    telefon, fax, email, telR, faxR, emailR (reprezentant / contact).
  - Coloanele <accize> sunt SUME INTREGI si sunt supuse la reguli de agregare stricte, verificate CHIAR SI
    cand campul agregat lipseste (tratat ca 0): ex. R10_C3 = R0_C3+R2_C3+R5_C3+R8_C3+R9_C3;
    R33_C3 = R0_C3+R2_C3+R5_C3+R8_C3+R9_C3+R11_C3+R16_C3; R41_C3 = R33_C3+R40_C3; R1_C1<=R0_C1; etc.
    => VALORILE si consistenta lor vin din contabilitatea utilizatorului (manual['accize']); generatorul le
    transmite verbatim (pass-through), NU inventeaza niveluri de acciza / cote (actul nu e in corpus).
  - um1..um13 apar in bytecode dar NU sunt atribute XML ("atribut necunoscut") - campuri interne, excluse.

D120 NU are cod_bug / nr_evid (nu exista in clasele antet). d_rec (tip rectificativa) implicit "0".

Cazul minim valid = antet obligatoriu + <accize/> gol (toate zero) + totalPlata_A=0. Datele pe produse se
adauga prin manual['accize'] = {camp: suma}, doar campuri din whitelist-ul citit din validator.

Contract dXXX: NS, _cif/_esc, calcul_d120(manual), pull/erori_generare/build_xml/genereaza(conn,schema,perioada).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Decont privind accizele'
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d120:declaratie:v5"
_NEDIGIT = re.compile(r"\D")

# Atributele coloanelor <accize> v5 - whitelist citit din d120validator/v5/Accize.class (167 campuri).
# Toate sunt sume INTREGI. um1..um13 NU sunt atribute XML (respinse de validator), deci excluse.
ACCIZE_FIELDS = {
    "ded1_C1", "ded2_C1", "ded3_C1", "ded4_C1", "ded5_C1", "ded6_C1", "ded7_C1", "ded8_C1",
    "ded9_C1", "ded10_C1", "ded11_C1",
    "R0_C1", "R0_C2", "R0_C3", "R1_C1", "R1_C2", "R1_C3", "R2_C1", "R2_C2", "R2_C3",
    "R3_C1", "R3_C2", "R3_C3", "R4_C1", "R4_C2", "R4_C3", "R5_C1", "R5_C2", "R5_C3",
    "R6_C1", "R6_C2", "R6_C3", "R6_1_C1", "R6_1_C2", "R6_1_C3", "R6_2_C1", "R6_2_C2", "R6_2_C3",
    "R6_3_C1", "R6_3_C2", "R6_3_C3", "R7_C1", "R7_C2", "R7_C3", "R7_1_C1", "R7_1_C2", "R7_1_C3",
    "R8_C1", "R8_C2", "R8_C3", "R9_C1", "R9_C2", "R9_C3", "R9_1_C1", "R9_1_C2", "R9_1_C3",
    "R10_C3", "R11_C3",
    "R12_C1", "R12_C2", "R12_C3", "R13_C1", "R13_C2", "R13_C3", "R14_C1", "R14_C2", "R14_C3",
    "R15_C1", "R15_C2", "R15_C3", "R16_C3", "R17_C1", "R17_C2", "R17_C3", "R18_C1", "R18_C2", "R18_C3",
    "R19_C1", "R19_C2", "R19_C3", "R20_C1", "R20_C2", "R20_C3", "R20_1_C1", "R20_1_C2", "R20_1_C3",
    "R20_2_C1", "R20_2_C2", "R20_2_C3", "R21_C1", "R21_C2", "R21_C3", "R22_C1", "R22_C2", "R22_C3",
    "R23_C1", "R23_C2", "R23_C3", "R24_C1", "R24_C2", "R24_C3", "R25_C1", "R25_C2", "R25_C3",
    "R26_C1", "R26_C2", "R26_C3", "R27_C1", "R27_C2", "R27_C3", "R27_1_C1", "R27_1_C2", "R27_1_C3",
    "R27_2_C1", "R27_2_C2", "R27_2_C3", "R28_C1", "R28_C2", "R28_C3", "R28_1_C1", "R28_1_C2", "R28_1_C3",
    "R28_2_C1", "R28_2_C2", "R28_2_C3", "R29_C1", "R29_C2", "R29_C3", "R29_1_C1", "R29_1_C2", "R29_1_C3",
    "R29_2_C1", "R29_2_C2", "R29_2_C3", "R30_C1", "R30_C2", "R30_C3", "R31_C1", "R31_C2", "R31_C3",
    "R32_C1", "R32_C2", "R32_C3", "R33_C3", "R34_C1", "R34_C2", "R34_C3", "R35_C1", "R35_C2", "R35_C3",
    "R36_C1", "R36_C2", "R36_C3", "R37_C1", "R37_C2", "R37_C3", "R38_C1", "R38_C2", "R38_C3",
    "R39_C1", "R39_C2", "R39_C3", "R39_1_C1", "R39_1_C2", "R39_1_C3", "R40_C3", "R41_C3",
}

# Antet: atribute optionale (reprezentant / contact), emise doar cand apar in manual.
_HEADER_OPT = ("cifS", "cifR", "denR", "adrR", "telefon", "fax", "email", "telR", "faxR", "emailR")
_HEADER_OPT_LIM = {
    "cifS": 13, "cifR": 13, "denR": 200, "adrR": 200, "telefon": 15, "fax": 15,
    "email": 250, "telR": 15, "faxR": 15, "emailR": 250,
}


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _accize_dict(manual):
    """Coloanele unicei sectiuni <accize>. Accepta manual['accize'] dict; gol => sectiune vida (valida)."""
    a = manual.get("accize")
    if a is None:
        return {}
    if isinstance(a, (list, tuple)):
        # element <accize> NU e repetabil; daca vine lista, se accepta doar primul rand.
        a = a[0] if a else {}
    return dict(a or {})


def calcul_d120(manual):
    """Suma de control D120.

    Arbitrul (validatorul) impune totalPlata_A = 0 (regula "Suma de control trebuie sa fie 0"; o valoare != 0
    arunca ClassCastException). Accizele efective se declara in coloanele R*/ded* ale sectiunii <accize>.
    Pastram, documentar, aritmetica sumelor de plata din input (coloana C3 = accize de plata), dar EMITEM 0.
    """
    acc = _accize_dict(manual)
    suma_c3 = 0
    for k, v in acc.items():
        if k.endswith("_C3"):
            d = _cif(v)
            suma_c3 += int(d) if d else 0
    return {"totalPlata_A": 0, "_suma_plata_input_C3": suma_c3}


def pull(conn, schema, perioada):
    """D120 se completeaza din contabilitatea de accize a firmei (baze/sume pe produs), nu dintr-un registru
    standard al aplicatiei. Valorile vin prin `manual`. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not (2 <= len(_cif(manual.get("cif"))) <= 10):
        er.append("CIF firma (cif) invalid - aștept 2..10 cifre.")
    if not str(manual.get("den") or "").strip():
        er.append("Lipsă denumire contribuabil (den).")
    if not str(manual.get("adresa") or "").strip():
        er.append("Lipsă adresa contribuabil (adresa).")
    if not _cif(manual.get("caen")):
        er.append("Lipsă cod CAEN (caen).")
    if not str(manual.get("nume_declar") or "").strip():
        er.append("Lipsă nume declarant (nume_declar).")
    if not str(manual.get("prenume_declar") or "").strip():
        er.append("Lipsă prenume declarant (prenume_declar).")
    if not str(manual.get("functie_declar") or "").strip():
        er.append("Lipsă funcție declarant (functie_declar).")
    d_rec = str(manual.get("d_rec", "0")).strip()
    if d_rec not in ("0", "1"):
        er.append("d_rec (tip rectificativa) trebuie 0 sau 1.")
    acc = _accize_dict(manual)
    for k, v in acc.items():
        if k not in ACCIZE_FIELDS:
            er.append("Camp <accize> necunoscut: %s (nu e in schema v5)." % k)
            continue
        d = _cif(v)
        if v not in (None, "") and not d:
            er.append("Camp <accize> %s trebuie suma intreaga: %r." % (k, v))
    return er


def build_xml(prof, an, luna, manual):
    cif = _cif(manual.get("cif"))
    h = []
    h.append('luna="%d"' % int(luna))
    h.append('an="%d"' % int(an))
    h.append('d_rec="%s"' % (str(manual.get("d_rec", "0")).strip() or "0"))
    h.append('cui="%s"' % cif)
    h.append('den="%s"' % _esc(manual.get("den"), 200))
    h.append('adresa="%s"' % _esc(manual.get("adresa"), 200))
    h.append('caen="%s"' % _cif(manual.get("caen")))
    # cifS (CIF, apare in antetul D120) - implicit = cui daca nu e dat explicit.
    cifS = _cif(manual.get("cifS")) or cif
    h.append('cifS="%s"' % cifS)
    for k in _HEADER_OPT:
        if k == "cifS":
            continue
        val = manual.get(k)
        if val not in (None, ""):
            if k == "cifR":
                h.append('%s="%s"' % (k, _cif(val)))
            else:
                h.append('%s="%s"' % (k, _esc(val, _HEADER_OPT_LIM.get(k))))
    h.append('nume_declar="%s"' % _esc(manual.get("nume_declar"), 75))
    h.append('prenume_declar="%s"' % _esc(manual.get("prenume_declar"), 75))
    h.append('functie_declar="%s"' % _esc(manual.get("functie_declar"), 75))
    h.append('totalPlata_A="%d"' % calcul_d120(manual)["totalPlata_A"])

    acc = _accize_dict(manual)
    at = []
    for k in sorted(acc.keys()):
        if k in ACCIZE_FIELDS:
            d = _cif(acc[k])
            at.append('%s="%d"' % (k, int(d) if d else 0))
    accize_xml = ("  <accize %s/>\n" % " ".join(at)) if at else "  <accize/>\n"

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie120 xmlns="%s" %s>\n'
            '%s'
            '</declaratie120>\n' % (NS, " ".join(h), accize_xml))


@dataclass
class Rezultat120:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_randuri_accize: int = 0
    avertismente: list = field(default_factory=list)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D120 nu se poate genera: " + " ".join(er))
    total = calcul_d120(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    acc = _accize_dict(manual)
    res = Rezultat120(an=an, luna=luna, total_plata_a=total,
                      nr_randuri_accize=len([k for k in acc if k in ACCIZE_FIELDS]))
    return xml, res
