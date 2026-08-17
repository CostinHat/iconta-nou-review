"""core/d107.py — D107: Declaratie informativa privind beneficiarii sponsorizarilor / mecenatului / burselor private.

Firma platitoare de impozit pe profit (persoane juridice) sau pe veniturile microintreprinderilor declara, pe
fiecare beneficiar, sumele acordate: Suma (Val1), Suma reportata (Val2), Suma dedusa (Val3). Declaratie MANUALA -
lista de beneficiari + sumele vin din input (aplicatia nu are inca registru dedicat de sponsorizari incadrate pe
beneficiar). Se depune odata cu declaratia anuala de impozit (profit -> cu D101; micro).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D107Validator.jar, v1 in vigoare pentru an sfarsit exercitiu >=2024;
Validator.class: "2024-01 J2.0.0 1 0"). Elemente/atribute (bytecode v1 + structura ANAF); atentie la MAJUSCULE,
XML e case-sensitive iar validatorul e arbitrul:
  <d107> (identificare): d_rec, cod_oblig, luna_i, an_i, luna, an, d_PM, d_alte, Data_I, Data_S, scadenta, cod_bug,
    d_succ, cifS, cui, denC, adresaC, codpC, telC, emailC, denR, cifR, adresaR, codpR, telR, emailR, denS,
    totalPlata_A, Val2_NI, Val3_NI, TVal1, TVal2, TVal3.
  <entit> (1-n, beneficiar individualizat): denE, cifE, adrE, Val1, Val2, Val3.
  <entit1> (0-n, Anexa - beneficiari neindividualizati): denE_NI, cifE_NI, adrE_NI (obligatorii daca Val2_NI>0).

SEMANTICA/REGULI din ACT (anaf_surse/structura_D107_2024_010726 + D107_XML_2024_010726, OPANAF 355/04.03.2024):
  - cod_oblig (nomenclator): 102=plati anticipate impozit profit (banci); 103=impozit profit persoane juridice
    romane; 104=impozit profit anual (agric./ONG); 105=impozit profit persoane juridice straine; 121=impozit
    micro. Se ALEGE din regimul firmei / de contabil, nu se ghiceste (aici: micro->121, altfel 103; suprascriabil).
  - d_PM = 2 daca cod_oblig=121 (micro), altfel 1 (profit). Impus de validator.
  - Exercitiu financiar pe AN CALENDARISTIC (singurul suportat): Data_M=null -> Data_I=01.01.an_i, Data_S=31.12.an,
    luna_i=1, luna=12, an_i=an=anul de raportare. Exercitiul MODIFICAT (Data_M) / dizolvarea (Data_L/Data_B) NU e
    suportat -> se respinge cu eroare (nu se ghiceste o corelatie de date pe care contabilul nu a dat-o).
  - scadenta (ZZLLAAAA, ZZ=25, pe Data_S=31.12.an): formula ANAF - an<=2025 -> luna+6; an>2025 fara dizolvare ->
    cod_oblig=104 luna+2, {102,103,105} luna+3. (Formula ANAF nu enumera 121 in ramura an>2025 -> aliniat la
    grupul impozitului anual pe profit, +3; pe an<=2025 toate cod_oblig dau +6, fara ambiguitate.)
  - cod_bug: cont unic bugetar "5503XXXXXX" (X-uri LITERALE in lista validatorului, ca la D100/D101/D112;
    cont 5503 a inlocuit oficial 20470101 din 26.07.2018 pentru profit si micro deopotriva).
  - Totaluri (struct rd.38-44): TVal1=suma(Val1); TVal2=suma(Val2)+Val2_NI; TVal3=suma(Val3)+Val3_NI;
    totalPlata_A=TVal1+TVal2+TVal3 (suma de control).
  - Anexa entit1 (neindividualizati) exista DACA SI NUMAI DACA Val2_NI>0 (struct rd.55 + regula validator).

Contract dXXX: pull/erori_generare/calcul_d107/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d107:declaratie:v1"
_NEDIGIT = re.compile(r"\D")

_COD_OBLIG_VALIDE = {"102", "103", "104", "105", "121"}


def _i(x, camp="D107"):
    """Suma in bani -> intreg cu rotunjire ARITMETICA (half-up), nu bancara (ANAF cere half-up)."""
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _cod_oblig(prof, manual):
    """Codul de obligatie fiscala: din manual daca e dat, altfel din regimul firmei (micro->121, profit->103)."""
    co = str(manual.get("cod_oblig") or "").strip()
    if co:
        return co
    regim = (prof.get("regim_fiscal") or "").lower()
    return "121" if regim == "micro" else "103"


def _scadenta(an, cod_oblig):
    """scadenta = ZZLLAAAA (ZZ=25) pe Data_S=31.12.an (an calendaristic). Formula ANAF (structura rd.18)."""
    ll, aa = 12, int(an)
    if aa <= 2025:
        ll += 6
    elif cod_oblig == "104":
        ll += 2
    else:  # 102,103,105 (si 121 aliniat la impozitul anual pe profit)
        ll += 3
    if ll > 12:
        aa += 1
        ll -= 12
    return "25%02d%04d" % (ll, aa)


def _cod_bug(cod_oblig):
    # Cont unic bugetar 5503, cu X-uri LITERALE (in lista validatorului), la fel ca D100/D101/D112.
    return "5503XXXXXX"


@dataclass
class Rezultat107:
    an: int
    total_plata_a: int = 0
    nr_beneficiari: int = 0
    nr_neindividualizati: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d107(manual):
    """Totaluri (struct rd.42-44 + rd.38): TVal1=sum(Val1); TVal2=sum(Val2)+Val2_NI; TVal3=sum(Val3)+Val3_NI;
    totalPlata_A=TVal1+TVal2+TVal3."""
    benef = manual.get("beneficiari") or []
    tval1 = sum(_i(b.get("val1")) for b in benef)
    tval2_ind = sum(_i(b.get("val2")) for b in benef)
    tval3_ind = sum(_i(b.get("val3")) for b in benef)
    val2_ni = _i(manual.get("val2_ni"))
    val3_ni = _i(manual.get("val3_ni"))
    tval2 = tval2_ind + val2_ni
    tval3 = tval3_ind + val3_ni
    return {"TVal1": tval1, "TVal2": tval2, "TVal3": tval3, "Val2_NI": val2_ni, "Val3_NI": val3_ni,
            "totalPlata_A": tval1 + tval2 + tval3}


def pull(conn, schema, perioada):
    """Header firmei platitoare. Beneficiarii + sumele vin din `manual` (nu exista registru dedicat)."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, regim_fiscal, "
                    "declarant_nume, declarant_prenume, declarant_functie, telefon, email "
                    "FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    adresa = " ".join(x for x in (r[2], r[3], r[4]) if x)
    return {"den": r[0], "cui": r[1], "adresa": adresa, "regim_fiscal": r[5],
            "declarant_nume": r[6], "declarant_prenume": r[7], "declarant_functie": r[8],
            "telefon": r[9], "email": r[10]}


def erori_generare(prof, manual):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CUI firma plătitoare lipsă/invalid.")
    if not prof.get("den"):
        er.append("LIPSĂ denumire firma.")
    if not str(prof.get("adresa") or "").strip():
        er.append("LIPSĂ adresa firma.")
    for c in ("declarant_nume", "declarant_prenume"):
        if not str(prof.get(c) or "").strip():
            er.append("LIPSĂ %s (semnatar obligatoriu, denS)." % c)
    co = _cod_oblig(prof, manual)
    if co not in _COD_OBLIG_VALIDE:
        er.append("cod_oblig %r invalid (nomenclator: 102/103/104/105/121)." % co)
    # exercitiu modificat / dizolvare: nesuportat (nu se ghiceste corelatia de date)
    for k in ("data_m", "data_l", "data_b"):
        if str(manual.get(k) or "").strip():
            er.append("D107 aici suportă doar exercițiul pe an calendaristic; %s (an modificat/dizolvare) "
                      "nu e suportat." % k)
    benef = manual.get("beneficiari") or []
    if not benef:
        er.append("D107 cere cel puțin un beneficiar (beneficiari[]).")
    for i, b in enumerate(benef, 1):
        if not str(b.get("den") or "").strip():
            er.append("Beneficiar %d: lipsă denumire/nume (denE)." % i)
        if not _cif(b.get("cif")):
            er.append("Beneficiar %d: lipsă cod de identificare fiscala (cifE)." % i)
        if not str(b.get("adresa") or "").strip():
            er.append("Beneficiar %d: lipsă adresa (adrE)." % i)
        for camp in ("val1", "val2", "val3"):
            if _i(b.get(camp)) < 0:
                er.append("Beneficiar %d: %s trebuie >= 0." % (i, camp))
    # Anexa neindividualizati: exista DACA SI NUMAI DACA Val2_NI>0 (struct rd.55)
    val2_ni = _i(manual.get("val2_ni"))
    ni = manual.get("neindividualizati") or []
    if val2_ni > 0 and not ni:
        er.append("Val2_NI>0 cere secțiunea entit1 (beneficiari neindividualizati).")
    if val2_ni == 0 and ni:
        er.append("entit1 (neindividualizati) există doar dacă Val2_NI>0.")
    for i, n in enumerate(ni, 1):
        for camp, et in (("den", "denE_NI"), ("cif", "cifE_NI"), ("adresa", "adrE_NI")):
            v = _cif(n.get(camp)) if camp == "cif" else str(n.get(camp) or "").strip()
            if not v:
                er.append("Neindividualizat %d: lipsă %s (obligatoriu dacă Val2_NI>0)." % (i, et))
    return er


def build_xml(prof, an, manual, calc):
    co = _cod_oblig(prof, manual)
    d_pm = "2" if co == "121" else "1"
    a = []
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('cod_oblig="%s"' % co)
    a.append('luna_i="1"')
    a.append('an_i="%d"' % int(an))
    a.append('luna="12"')
    a.append('an="%d"' % int(an))
    a.append('d_PM="%s"' % d_pm)
    a.append('d_alte="0"')
    a.append('Data_I="01.01.%d"' % int(an))
    a.append('Data_S="31.12.%d"' % int(an))
    a.append('scadenta="%s"' % _scadenta(an, co))
    a.append('cod_bug="%s"' % _cod_bug(co))
    a.append('d_succ="0"')
    a.append('cui="%s"' % _cif(prof.get("cui")))
    a.append('denC="%s"' % _esc(prof.get("den"), 200))
    a.append('adresaC="%s"' % _esc(prof.get("adresa"), 1000))
    if prof.get("cod_postal"):
        a.append('codpC="%s"' % _esc(prof.get("cod_postal"), 6))
    if prof.get("telefon"):
        a.append('telC="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('emailC="%s"' % _esc(prof.get("email"), 200))
    denS = (_esc(prof.get("declarant_nume")) + " " + _esc(prof.get("declarant_prenume"))).strip()
    a.append('denS="%s"' % denS[:75])
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    a.append('Val2_NI="%d"' % calc["Val2_NI"])
    a.append('Val3_NI="%d"' % calc["Val3_NI"])
    a.append('TVal1="%d"' % calc["TVal1"])
    a.append('TVal2="%d"' % calc["TVal2"])
    a.append('TVal3="%d"' % calc["TVal3"])
    linii = ['<d107 xmlns="%s" %s>' % (NS, " ".join(a))]
    for b in manual.get("beneficiari") or []:
        ba = ['denE="%s"' % _esc(b.get("den"), 200), 'cifE="%s"' % _cif(b.get("cif")),
              'adrE="%s"' % _esc(b.get("adresa"), 1000),
              'Val1="%d"' % _i(b.get("val1")), 'Val2="%d"' % _i(b.get("val2")), 'Val3="%d"' % _i(b.get("val3"))]
        linii.append('  <entit %s/>' % " ".join(ba))
    for n in manual.get("neindividualizati") or []:
        na = ['denE_NI="%s"' % _esc(n.get("den"), 200), 'cifE_NI="%s"' % _cif(n.get("cif")),
              'adrE_NI="%s"' % _esc(n.get("adresa"), 1000)]
        linii.append('  <entit1 %s/>' % " ".join(na))
    linii.append('</d107>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D107 nu se poate genera: " + " ".join(er))
    calc = calcul_d107(manual)
    xml = build_xml(prof, an, manual, calc)
    res = Rezultat107(an=an, total_plata_a=calc["totalPlata_A"],
                      nr_beneficiari=len(manual.get("beneficiari") or []),
                      nr_neindividualizati=len(manual.get("neindividualizati") or []))
    return xml, res
