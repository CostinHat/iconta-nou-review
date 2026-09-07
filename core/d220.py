"""core/d220.py — D220: Declaratie privind venitul estimat / norma de venit (persoane fizice).

Persoana fizica declara venitul brut estimat, cheltuielile deductibile estimate si venitul net estimat pentru
anul curent (activitati independente, drepturi de proprietate intelectuala, cedarea folosintei bunurilor,
activitati agricole/silvicultura/piscicultura). Declaratie MANUALA - identitatea PF + estimarile vin din input.

NOTA DE CORPUS: D220 a fost INLOCUITA de Declaratia Unica (D212, OPANAF 888/2018) pentru depunerile curente
(vezi core/d212_engine.py). Validatorul D220Validator.jar ramane livrat si functional - se construieste pentru
cazuri istorice/reziduale (ultima structura = anul fiscal 2017).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D220Validator.jar). _dateVersionTable: ultima linie "2017-01
J2.1.0 1 2" -> sub-pachet validator v1/, Parameters_v2; namespace XML :v2 (pachet v1, ns v2 - nepotrivire ANAF).
  <declaratie220> (antet + identificare PF): luna, an, d_rec1, d_rec2, stat_pensie, d_rec, nume_declar,
    prenume_declar, functie_declar, totalPlata_A, nume, cif(CNP), adresa, telefon, fax, email, den_r, cif_r, ...
  <activitate> (1): categ_venit, contracte, nr_camere, det_venit, forma_org, CAEN, localitate, judet, sector,
    sediu, tip_doc, nr_doc, data_doc, data_I, data_F, data_S, nr_zile, data_CAS, venit3, chelt3, net3.
  <fisa> (0-1, cazare turistica) -> <camera> (1-5).

SEMANTICA/REGULI din ACT (anaf_surse/structura_D220_2017_09012018 + d220_20180108.xsd; OPANAF 3622/2015;
CF L227/2015 art.68/69/70 venituri activitati independente, art.83-85 cedarea folosintei):
  - luna = 12 (fix); an>=2016. stat_pensie se OMITE (categ_venit=8 pensii strainatate = ramura moarta in schema
    v1.02; validatorul respinge stat_pensie cand categ_venit in 1..7 - "nu trebuie sa existe aici").
  - net3 = venit3-chelt3 daca venit3>=chelt3, altfel 0. totalPlata_A = venit3+chelt3+net3 (suma de control).
  - d_rec = 1 daca d_rec1>0 sau d_rec2=1, altfel 0.
  - categ_venit 1-7 (1=comerciale, 2=profesii liberale, 3=drepturi PI, 4=agricole, 5=silvicultura,
    6=piscicultura, 7=cedarea folosintei); det_venit 0-3 (1=real, 2=cote forfetare, 3=norma); forma_org 0-4.
  - cazare turistica (categ_venit=7 & contracte=3 & det_venit=3): sectiunea <fisa> cu <camera> (nr = nr_camere).
  - sector obligatoriu daca judet=40 (Bucuresti). D220 NU are cod_bug (nu e obligatie de plata).

Contract dXXX: pull/erori_generare/calcul_d220/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind venitul estimat / norma de venit (persoane fizice)'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d220:declaratie:v2"
_NEDIGIT = re.compile(r"\D")


def _i(x, camp="D220"):
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _num(x):
    """Suprafata camera: N(6.2), pana la 2 zecimale."""
    d = Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return ("%d" % d) if d == d.to_integral_value() else ("%s" % d)


@dataclass
class Rezultat220:
    an: int
    total_plata_a: int = 0
    categ_venit: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d220(manual):
    act = manual.get("activitate") or {}
    venit3 = _i(act.get("venit_brut"))
    chelt3 = _i(act.get("cheltuieli"))
    net3 = (venit3 - chelt3) if venit3 >= chelt3 else 0
    total = venit3 + chelt3 + net3
    d_rec1 = int(manual.get("d_rec1") or 0)
    d_rec2 = int(manual.get("d_rec2") or 0)
    d_rec = 1 if (d_rec1 > 0 or d_rec2 == 1) else 0
    return {"venit3": venit3, "chelt3": chelt3, "net3": net3, "totalPlata_A": total,
            "d_rec1": d_rec1, "d_rec2": d_rec2, "d_rec": d_rec}


def pull(conn, schema, perioada):
    """Declarantul (fallback din firma_profil). D220 e a unei PERSOANE FIZICE - identitatea vine din manual."""
    with conn.cursor() as cur:
        cur.execute("SELECT declarant_nume, declarant_prenume, declarant_functie FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"declarant_nume": r[0], "declarant_prenume": r[1], "declarant_functie": r[2]}


def _declarant(prof, manual):
    return {
        "nume_declar": manual.get("nume_declar") or prof.get("declarant_nume"),
        "prenume_declar": manual.get("prenume_declar") or prof.get("declarant_prenume"),
        "functie_declar": manual.get("functie_declar") or prof.get("declarant_functie") or "TITULAR",
    }


def erori_generare(prof, manual):
    er = []
    d = _declarant(prof, manual)
    for c in ("nume_declar", "prenume_declar"):
        if not str(d.get(c) or "").strip():
            er.append("LIPSĂ %s (declarant/titular obligatoriu)." % c)
    if not _cif(manual.get("cif")):
        er.append("D220 cere cif (CNP persoana fizica).")
    if not str(manual.get("nume") or "").strip():
        er.append("LIPSĂ nume contribuabil (nume+prenume PF).")
    act = manual.get("activitate")
    if not isinstance(act, dict) or not act:
        er.append("D220 cere `manual.activitate` (categ_venit, det_venit, forma_org, venit_brut, cheltuieli).")
        return er
    cv = str(act.get("categ_venit") or "")
    if cv not in {str(n) for n in range(1, 8)}:
        er.append("activitate: categ_venit %r invalid (1..7)." % cv)
    if str(act.get("det_venit") or "") not in {"0", "1", "2", "3"}:
        er.append("activitate: det_venit invalid (0/1/2/3).")
    if str(act.get("forma_org") or "") not in {"0", "1", "2", "3", "4"}:
        er.append("activitate: forma_org invalid (0/1/2/3/4).")
    if _i(act.get("venit_brut")) < 0 or _i(act.get("cheltuieli")) < 0:
        er.append("activitate: venit_brut/cheltuieli trebuie >= 0.")
    if str(act.get("judet") or "") == "40" and not str(act.get("sector") or "").strip():
        er.append("activitate: sector obligatoriu pentru județ=40 (București).")
    # cazare turistica: fisa cu camere = nr_camere
    fisa = manual.get("fisa")
    if cv == "7" and str(act.get("contracte") or "") == "3" and str(act.get("det_venit") or "") == "3":
        if not isinstance(fisa, dict) or not (fisa.get("camere")):
            er.append("Cazare turistica (categ_venit=7, contracte=3, norma): cere `fisa` cu camere[].")
        else:
            nrc = int(act.get("nr_camere") or 0)
            if nrc and len(fisa.get("camere") or []) != nrc:
                er.append("fisa: numărul de camere (%d) trebuie să fie egal cu nr_camere (%d)." %
                          (len(fisa.get("camere")), nrc))
    return er


_ACT_OPT = [("contracte", "contracte"), ("nr_camere", "nr_camere"), ("caen", "CAEN"),
            ("localitate", "localitate"), ("judet", "judet"), ("sector", "sector"), ("sediu", "sediu"),
            ("tip_doc", "tip_doc"), ("nr_doc", "nr_doc"), ("data_doc", "data_doc"), ("data_i", "data_I"),
            ("data_f", "data_F"), ("data_s", "data_S"), ("nr_zile", "nr_zile"), ("data_cas", "data_CAS")]


def build_xml(prof, an, manual, calc):
    d = _declarant(prof, manual)
    act = manual.get("activitate") or {}
    a = []
    a.append('luna="12"')
    a.append('an="%d"' % int(an))
    a.append('d_rec1="%d"' % calc["d_rec1"])
    a.append('d_rec2="%d"' % calc["d_rec2"])
    # stat_pensie: numai pentru categ_venit=8 (pensii strainatate), ramura moarta in schema v1.02.
    # Validatorul RESPINGE stat_pensie cand categ_venit in 1..7 ("nu trebuie sa existe aici") -> se omite.
    a.append('d_rec="%d"' % calc["d_rec"])
    a.append('nume_declar="%s"' % _esc(d.get("nume_declar"), 75))
    a.append('prenume_declar="%s"' % _esc(d.get("prenume_declar"), 75))
    a.append('functie_declar="%s"' % _esc(d.get("functie_declar"), 50))
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    a.append('nume="%s"' % _esc(manual.get("nume"), 75))
    a.append('cif="%s"' % _cif(manual.get("cif")))
    for k, xa in (("adresa", "adresa"), ("telefon", "telefon"), ("fax", "fax"), ("email", "email")):
        if str(manual.get(k) or "").strip():
            a.append('%s="%s"' % (xa, _esc(manual.get(k), 200 if k in ("adresa", "email") else 15)))
    imp = manual.get("imputernicit") or {}
    if imp.get("cif_r") or imp.get("den_r"):
        a.append('den_r="%s"' % _esc(imp.get("den_r"), 75))
        a.append('cif_r="%s"' % _cif(imp.get("cif_r")))
        for k, xa in (("adresa_r", "adresa_r"), ("telefon_r", "telefon_r"), ("email_r", "email_r")):
            if str(imp.get(k) or "").strip():
                a.append('%s="%s"' % (xa, _esc(imp.get(k), 200)))
    linii = ['<declaratie220 xmlns="%s" %s>' % (NS, " ".join(a))]
    # activitate
    aa = ['categ_venit="%s"' % _esc(act.get("categ_venit"))]
    for k, xa in _ACT_OPT:
        if str(act.get(k) or "").strip():
            aa.append('%s="%s"' % (xa, _esc(act.get(k), 200)))
    aa.append('det_venit="%s"' % _esc(act.get("det_venit")))
    aa.append('forma_org="%s"' % _esc(act.get("forma_org")))
    aa.append('venit3="%d"' % calc["venit3"])
    aa.append('chelt3="%d"' % calc["chelt3"])
    aa.append('net3="%d"' % calc["net3"])
    fisa = manual.get("fisa")
    if isinstance(fisa, dict) and fisa.get("camere"):
        linii.append('  <activitate %s>' % " ".join(aa))
        fa = ['localitateF="%s"' % _esc(fisa.get("localitate"), 50),
              'judetF="%s"' % _esc(fisa.get("judet")),
              'adr_imobil="%s"' % _esc(fisa.get("adr_imobil"), 200),
              'mediu_imobil="%s"' % _esc(fisa.get("mediu_imobil")),
              'acces_imobil="%s"' % _esc(fisa.get("acces_imobil"))]
        if str(fisa.get("sector") or "").strip():
            fa.insert(2, 'sectorF="%s"' % _esc(fisa.get("sector")))
        linii.append('    <fisa %s>' % " ".join(fa))
        for idx, cam in enumerate(fisa.get("camere") or [], 1):
            ca = ['id_camera="%d"' % idx, 'supraf="%s"' % _num(cam.get("supraf") or 0),
                  'nrloc="%d"' % _i(cam.get("nrloc")), 'materiale="%s"' % _esc(cam.get("materiale") or "1"),
                  'apa="%s"' % _esc(cam.get("apa") or "1"), 'canalizare="%s"' % _esc(cam.get("canalizare") or "1"),
                  'electrice="%s"' % _esc(cam.get("electrice") or "1"),
                  'incalzire="%s"' % _esc(cam.get("incalzire") or "1"),
                  'sanitare="%s"' % _esc(cam.get("sanitare") or "1")]
            linii.append('      <camera %s/>' % " ".join(ca))
        linii.append('    </fisa>')
        linii.append('  </activitate>')
    else:
        linii.append('  <activitate %s/>' % " ".join(aa))
    linii.append('</declaratie220>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D220 nu se poate genera: " + " ".join(er))
    calc = calcul_d220(manual)
    xml = build_xml(prof, an, manual, calc)
    res = Rezultat220(an=an, total_plata_a=calc["totalPlata_A"],
                      categ_venit=str((manual.get("activitate") or {}).get("categ_venit") or ""))
    return xml, res
