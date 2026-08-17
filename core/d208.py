"""core/d208.py — D208: Declaratie informativa privind impozitul pe veniturile din
transferul proprietatilor imobiliare din patrimoniul personal (depusa de NOTARI).

Periodicitate SEMESTRIALA (luna de raportare 6 sau 12). D208 e INFORMATIVA: biroul
notarial raporteaza tranzactii deja incheiate cu sumele DEJA stabilite in acte. Modulul
NU fabrica cote de impozit din act - valorile-frunza (valoare imobil, baza, impozit pe
beneficiar) vin din `manual`; modulul doar le AGREGA (totalurile antetului = sumele din
liste), garantand egalitatile pe care le verifica validatorul.

SURSA STRUCTURII = VALIDATORUL OFICIAL (D208Validator.jar, pachet d208validator/v6,
namespace declaratie:v1). Citita din bytecode SI PROBATA pe DUKIntegrator (fisier VALID).
Structura reala (arborele, confirmat empiric) - `beneficiari` si `parti` sunt copii ai lui
`imobile`, NU ai tranzactiei, iar ordinea sectiunilor din `imobile` este beneficiari->parti:

  declaratie208(luna,an,dRec, nume,cif,domiciuliuFiscal,nume_Intocmit,functia_intocmit[,telefon,fax,email],
                val_tranzactii_T,val_piata_T,baza_calcul_T,impozit_T,impozit_scutit_T,nr_beneficiari,totalPlata_A)
    tranzactie(nr_act_notarial, mod_transfer[,alt_mod_transfer], nuda_proprietate,
               val_tranzactie, val_piata, baza_calcul, taxa_notar)                    [repetabil]
      imobile(judet, localitate, codSIRUTA, tip_nr_cadastral, nr_cadastral,
              tip_imobil_teren, tip_imobil_cladire, tip_imobil_unitate,
              val_tranzactie_imobil, val_piata_imobil)                                [repetabil]
        beneficiari(cui_beneficiar, nume_beneficiar, cota_beneficiar, cotaImpozit_beneficiar,
                    baza_calcul_beneficiar, impozit_beneficiar, impozit_scutit_beneficiar) [repetabil, obligatoriu]
        parti(cui_parte, nume_parte, cota_parte)                                      [repetabil, obligatoriu]

Reguli probate (v6, coduri DUK): R26 tranzactie.baza_calcul = Sigma baza_calcul_beneficiar;
R13 nr_beneficiari = numarul de beneficiari; R17 impozit_T = Sigma impozit_beneficiar; totalurile
_T = sumele; Sigma cota_beneficiar pe imobil = 100; Sigma cota_parte pe imobil = 100;
cotaImpozit_beneficiar in {0,1,3}. Atribute antet OBLIGATORII: domiciuliuFiscal, nume_Intocmit,
functia_intocmit, totalPlata_A; pe imobil: codSIRUTA + toate cele trei bife tip_imobil_*.

Contract dXXX: NS, _cif/_esc, calcul_d208(manual), pull (return {}), erori_generare, build_xml,
genereaza(conn, schema, perioada, manual=None).
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d208:declaratie:v1"
_NEDIGIT = re.compile(r"\D")


def _cif(x):
    """Doar cifrele (CUI/CNP fara prefix RO, fara separatori)."""
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _int(x):
    """Intreg tolerant (accepta '1.234', virgula, None)."""
    s = _cif(x)
    return int(s) if s else 0


def _num(x):
    """Numar (cota %) - int daca e intreg, altfel float."""
    if x in (None, ""):
        return 0
    try:
        f = float(str(x).replace(",", "."))
    except ValueError:
        return 0
    return int(f) if f == int(f) else f


def _fmtnum(x):
    n = _num(x)
    return str(int(n)) if float(n) == int(n) else ("%s" % n)


def _tranzactii(manual):
    """Normalizeaza `manual` la o lista de tranzactii. Accepta manual['tranzactii'] sau
    forma minimala plata: manual['imobile'] = o singura tranzactie."""
    tz = manual.get("tranzactii")
    if tz:
        return list(tz)
    if manual.get("imobile"):
        return [{
            "nr_act_notarial": manual.get("nr_act_notarial"),
            "mod_transfer": manual.get("mod_transfer", "1"),
            "taxa_notar": manual.get("taxa_notar", 0),
            "imobile": manual.get("imobile", []),
        }]
    return []


def _imobile(t):
    """Imobilele unei tranzactii. Comoditate: daca exista un singur imobil fara
    beneficiari/parti proprii, mosteneste listele de la nivel de tranzactie."""
    imob = list(t.get("imobile", []))
    if len(imob) == 1:
        im = dict(imob[0])
        if not im.get("beneficiari") and t.get("beneficiari"):
            im["beneficiari"] = t.get("beneficiari")
        if not im.get("parti") and t.get("parti"):
            im["parti"] = t.get("parti")
        imob = [im]
    return imob


def _rollup_imobil(im):
    ben = im.get("beneficiari", [])
    return {
        "val": _int(im.get("val_tranzactie_imobil")),
        "val_piata": _int(im.get("val_piata_imobil") or im.get("val_tranzactie_imobil")),
        "baza": sum(_int(b.get("baza_calcul")) for b in ben),
        "impozit": sum(_int(b.get("impozit")) for b in ben),
        "scutit": sum(_int(b.get("impozit_scutit")) for b in ben),
        "nben": len(ben),
    }


def _rollup_tranzactie(t):
    r = [_rollup_imobil(im) for im in _imobile(t)]
    return {
        "val_tranzactie": sum(x["val"] for x in r),
        "val_piata": sum(x["val_piata"] for x in r),
        "baza_calcul": sum(x["baza"] for x in r),
        "impozit": sum(x["impozit"] for x in r),
        "impozit_scutit": sum(x["scutit"] for x in r),
        "nr_benef": sum(x["nben"] for x in r),
    }


def calcul_d208(manual):
    """Suma de control = sumele din liste (rollup imobil -> tranzactie -> antet)."""
    r = [_rollup_tranzactie(t) for t in _tranzactii(manual)]
    return {
        "val_tranzactii_T": sum(x["val_tranzactie"] for x in r),
        "val_piata_T": sum(x["val_piata"] for x in r),
        "baza_calcul_T": sum(x["baza_calcul"] for x in r),
        "impozit_T": sum(x["impozit"] for x in r),
        "impozit_scutit_T": sum(x["impozit_scutit"] for x in r),
        "nr_beneficiari": sum(x["nr_benef"] for x in r),
    }


def pull(conn, schema, perioada):
    """D208 e informativa, alimentata din acte notariale introduse manual; firma nu are
    registru de tranzactii imobiliare ale tertilor. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume") or "").strip():
        er.append("Lipsă denumire birou notarial / notar (nume).")
    if not (2 <= len(_cif(manual.get("cif") or manual.get("cui"))) <= 10):
        er.append("CIF birou notarial (cif) invalid.")
    if not str(manual.get("domiciliu") or manual.get("domiciuliuFiscal") or "").strip():
        er.append("Lipsă domiciliu fiscal (domiciliu).")
    if not str(manual.get("nume_intocmit") or manual.get("nume_Intocmit") or "").strip():
        er.append("Lipsă nume intocmitor (nume_intocmit).")
    if not str(manual.get("functia_intocmit") or "").strip():
        er.append("Lipsă funcție intocmitor (functia_intocmit).")
    tz = _tranzactii(manual)
    if not tz:
        er.append("Nicio tranzacție (macar 1 tranzacție cu >=1 imobil).")
    for k, t in enumerate(tz, 1):
        pre = "Tranzacția %d: " % k
        if not str(t.get("nr_act_notarial") or "").strip():
            er.append(pre + "lipsă nr_act_notarial (identificatorul tranzactiei).")
        imob = _imobile(t)
        if not imob:
            er.append(pre + "niciun imobil.")
        for j, im in enumerate(imob, 1):
            ipre = pre + "imobil %d: " % j
            if not str(im.get("nr_cadastral") or "").strip():
                er.append(ipre + "lipsă nr_cadastral.")
            benef = im.get("beneficiari", [])
            parti = im.get("parti", [])
            if not benef:
                er.append(ipre + "niciun beneficiar (obligatoriu).")
            if not parti:
                er.append(ipre + "nicio cealalta parte contractanta (obligatoriu).")
            for b in benef:
                if not (1 <= len(_cif(b.get("cui"))) <= 13):
                    er.append(ipre + "CUI/CNP beneficiar invalid.")
                if _num(b.get("cotaImpozit", 0)) not in (0, 1, 3):
                    er.append(ipre + "cotaImpozit beneficiar poate fi doar 0, 1 sau 3.")
            s_ben = sum(_num(b.get("cota")) for b in benef)
            if benef and round(s_ben, 2) != 100:
                er.append(ipre + "suma cotelor beneficiarilor = %s (trebuie 100)." % _fmtnum(s_ben))
            s_p = sum(_num(p.get("cota")) for p in parti)
            if parti and round(s_p, 2) != 100:
                er.append(ipre + "suma cotelor cealalta parte = %s (trebuie 100)." % _fmtnum(s_p))
    return er


def _beneficiar_xml(b):
    a = ['cui_beneficiar="%s"' % _cif(b.get("cui")),
         'nume_beneficiar="%s"' % _esc(b.get("nume"), 75),
         'cota_beneficiar="%s"' % _fmtnum(b.get("cota")),
         'cotaImpozit_beneficiar="%s"' % _fmtnum(b.get("cotaImpozit", 0)),
         'baza_calcul_beneficiar="%d"' % _int(b.get("baza_calcul")),
         'impozit_beneficiar="%d"' % _int(b.get("impozit")),
         'impozit_scutit_beneficiar="%d"' % _int(b.get("impozit_scutit"))]
    return "        <beneficiari %s/>" % " ".join(a)


def _parte_xml(p):
    a = ['cui_parte="%s"' % _cif(p.get("cui")),
         'nume_parte="%s"' % _esc(p.get("nume"), 75),
         'cota_parte="%s"' % _fmtnum(p.get("cota"))]
    return "        <parti %s/>" % " ".join(a)


def _imobil_xml(im):
    roll = _rollup_imobil(im)
    a = ['judet="%s"' % _esc(im.get("judet"), 2),
         'localitate="%s"' % _esc(im.get("localitate"), 100),
         'codSIRUTA="%s"' % _cif(im.get("codSIRUTA") or im.get("siruta")),
         'tip_nr_cadastral="%s"' % _esc(im.get("tip_nr_cadastral", "1"), 1),
         'nr_cadastral="%s"' % _esc(im.get("nr_cadastral"), 50)]
    # cele trei bife de tip imobil sunt TOATE obligatorii; una = 1, restul = 0
    tip = str(im.get("tip_imobil", "teren")).strip().lower()
    teren = "1" if tip.startswith("ter") else "0"
    cladire = "1" if tip.startswith("clad") else "0"
    unitate = "1" if tip.startswith("unit") else "0"
    a.append('tip_imobil_teren="%s"' % teren)
    a.append('tip_imobil_cladire="%s"' % cladire)
    a.append('tip_imobil_unitate="%s"' % unitate)
    if cladire == "1" and im.get("nr_cadastral_cladire"):
        a.append('nr_cadastral_cladire="%s"' % _esc(im.get("nr_cadastral_cladire"), 50))
    if unitate == "1" and im.get("nr_cadastral_unitate"):
        a.append('nr_cadastral_unitate="%s"' % _esc(im.get("nr_cadastral_unitate"), 50))
    a.append('val_tranzactie_imobil="%d"' % roll["val"])
    a.append('val_piata_imobil="%d"' % roll["val_piata"])
    lines = ["      <imobile %s>" % " ".join(a)]
    # ordinea sectiunilor din imobil: beneficiari -> parti (impusa de validator)
    for b in im.get("beneficiari", []):
        lines.append(_beneficiar_xml(b))
    for p in im.get("parti", []):
        lines.append(_parte_xml(p))
    lines.append("      </imobile>")
    return "\n".join(lines)


def _tranzactie_xml(t):
    roll = _rollup_tranzactie(t)
    a = ['nr_act_notarial="%s"' % _esc(t.get("nr_act_notarial"), 50),
         'mod_transfer="%s"' % _esc(t.get("mod_transfer", "1"), 2)]
    if t.get("alt_mod_transfer"):
        a.append('alt_mod_transfer="%s"' % _esc(t.get("alt_mod_transfer"), 250))
    a.append('nuda_proprietate="%s"' % _esc(t.get("nuda_proprietate", "0"), 1))
    a.append('val_tranzactie="%d"' % roll["val_tranzactie"])
    a.append('val_piata="%d"' % roll["val_piata"])
    a.append('baza_calcul="%d"' % roll["baza_calcul"])
    a.append('taxa_notar="%d"' % _int(t.get("taxa_notar")))  # obligatoriu
    lines = ["    <tranzactie %s>" % " ".join(a)]
    for im in _imobile(t):
        lines.append(_imobil_xml(im))
    lines.append("    </tranzactie>")
    return "\n".join(lines)


def build_xml(prof, an, luna, manual):
    tot = calcul_d208(manual)
    h = ['luna="%d"' % int(luna), 'an="%d"' % int(an),
         'dRec="%s"' % _esc(manual.get("dRec", "0"), 1),
         'nume="%s"' % _esc(manual.get("nume"), 200),
         'cif="%s"' % _cif(manual.get("cif") or manual.get("cui")),
         'domiciuliuFiscal="%s"' % _esc(manual.get("domiciliu") or manual.get("domiciuliuFiscal"), 200),
         'nume_Intocmit="%s"' % _esc(manual.get("nume_intocmit") or manual.get("nume_Intocmit"), 75),
         'functia_intocmit="%s"' % _esc(manual.get("functia_intocmit"), 75)]
    if manual.get("telefon"):
        h.append('telefon="%s"' % _esc(manual.get("telefon"), 15))
    if manual.get("fax"):
        h.append('fax="%s"' % _esc(manual.get("fax"), 15))
    if manual.get("email"):
        h.append('email="%s"' % _esc(manual.get("email"), 250))
    h.append('val_tranzactii_T="%d"' % tot["val_tranzactii_T"])
    h.append('val_piata_T="%d"' % tot["val_piata_T"])
    h.append('baza_calcul_T="%d"' % tot["baza_calcul_T"])
    h.append('impozit_T="%d"' % tot["impozit_T"])
    h.append('impozit_scutit_T="%d"' % tot["impozit_scutit_T"])
    h.append('nr_beneficiari="%d"' % tot["nr_beneficiari"])
    h.append('totalPlata_A="%d"' % tot["impozit_T"])  # suma de control = total impozit
    body = "\n".join(_tranzactie_xml(t) for t in _tranzactii(manual))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie208 xmlns="%s" %s>\n%s\n</declaratie208>\n'
            % (NS, " ".join(h), body))


@dataclass
class Rezultat208:
    an: int
    luna: int
    val_tranzactii_T: int = 0
    baza_calcul_T: int = 0
    impozit_T: int = 0
    nr_beneficiari: int = 0
    avertismente: list = field(default_factory=list)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D208 nu se poate genera: " + " ".join(er))
    tot = calcul_d208(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat208(an=an, luna=luna, val_tranzactii_T=tot["val_tranzactii_T"],
                      baza_calcul_T=tot["baza_calcul_T"], impozit_T=tot["impozit_T"],
                      nr_beneficiari=tot["nr_beneficiari"])
    return xml, res
