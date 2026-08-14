"""core/d212.py - D212: Declaratia unica privind impozitul pe venit si contributiile sociale
datorate de persoanele fizice (cea mai complexa declaratie ANAF; ns v11, pachet validator v9).

Declaratie MANUALA (persoana fizica): aplicatia nu are registru de persoane fizice, nici
veniturile/contributiile lor. Toate datele vin din dict-ul `manual`. Firma (conn/schema) NU
contine sursa - `pull` intoarce {} (contractul dXXX cere metoda).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul), D212Validator.jar. Structura in vigoare
pentru anul de raportare 2025 a fost CITITA din bytecode si PROBATA camp cu camp pe DUKIntegrator:
  - Radacina reala = element <d212> (NU <declaratie>; acela era ns:v1, invechit). Namespace v11.
  - Selectia versiunii (d212validator/Validator._dateVersionTable): randul
    '2025-01 J13.0.1 9 7 2025-01-15' => pachet validator v9 + Parameters_v7 => namespace v11.
  - Copii (elemente lowercase): cap11, cap12, cap14, oblig_realizat, oblig_estimat, coasigurat.
  - Atribute OBLIGATORII pe radacina (flag mandatory=1 in checkTag), probate ca lipsa/necesare:
    d_rec, rectif1, rectif2, totalPlata_A, luna_r(=12 fix, interval [12,12]), an_r(interval
    [2025,2100]), bifa_succesor, anulare_litA, anulare_litB, bifa_conformare, bifa111, bifa112,
    bifa113, bifa121, bifa122, bifa131, bifa132, bifa14, bifa15, nerezident + identificare
    (cif, nume_c, adresa_c). bifa16/bifa18 optionale.
  - DUK regula R4: totalPlata_A (suma de control) = suma sumelor 'de plata'; cand nu exista nimic
    de plata (0), egaleaza suma cifrelor CNP (marcaj de control nenul). Probat: CNP ...1144 => 25.

CAZUL PRINCIPAL ACOPERIT + PROBAT DUK VALID: declaratie de identificare (fara obligatii de plata
- nula / rectificativa / doar identificare), cu toate bifele pe 0. Este cazul MINIM care trece
validatorul si nucleul garantat-VALID al generatorului.

EXTENSIBIL (structura mapata integral din bytecode, se emite din `manual` cand e furnizata):
capitolele de venit realizat (cap11 sistem real, cap12 norma de venit, cap14 strainatate) si
contributiile (oblig_realizat CAS/CASS, oblig_estimat, coasigurat). Pentru un capitol POPULAT,
apelantul furnizeaza valorile deja calculate (venituri, baze, impozit, CAS, CASS) intr-un sub-dict
per element; generatorul le emite ca atribute si NU recalculeaza cotele/plafoanele (interzis sa
hardcodam cote de impozit/CAS/CASS). Regulile de consistenta interne (impozit=venit*cota, baze la
plafon, R-uri CAS/CASS) raman in sarcina datelor de intrare - vezi field-reference in `_CAMPURI`.

Contract dXXX: NS, _cif/_cnp_valid/_esc, calcul_d212, pull(conn,schema,perioada)->{},
erori_generare, build_xml, genereaza(conn, schema, perioada, manual=None). conn=None este acceptat
(pull nu atinge baza).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d212:declaratie:v11"

_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

# Luna de raportare - constanta structurala a schemei (interval [12,12] in validator), nu o cota.
_LUNA_R = "12"

# Elementele-copil in ordinea din initializareDocument (validatorul accepta atributele dupa nume,
# ordinea nu e critica; o pastram pentru lizibilitate).
_COPII = ["oblig_realizat", "oblig_estimat", "cap11", "cap12", "cap14", "coasigurat"]

# Referinta campurilor pe element (numele de atribut XML = numele campului fara '_' din bytecode).
# Emitem DOAR chei din aceste seturi (o cheie necunoscuta e respinsa de validator ca atribut strain).
_CAMPURI = {
    "cap11": {"scutire", "reg", "categ_venit", "det_ven_net", "forma_org", "mod_forma_org",
              "caen", "descriere_sediu_bun", "nr_doc_autoriz", "data_doc_autoriz",
              "data_incep", "data_sf", "nr_zile_scutite", "venit_brut", "chelt_deduc",
              "venit_net_anual", "pierdere", "pierdere_precedenta", "pierdere_compensata",
              "venit_recalculat", "venit_redus", "impozit11"},
    "cap12": {"norma_forma_org", "norma_caen", "norma_descriere_sediu_bun", "norma_nr_doc_autoriz",
              "norma_data_doc_autoriz", "norma_data_incep", "norma_data_sf", "norma_data_susp",
              "norma_nr_zile_scutite", "real_norma_venit", "real_ajustare",
              "real_venit_net_anual", "real_venit_impozit", "real_impozit"},
    "cap14": {"str_stat_realiz_v", "str_categ_venit", "dubla_impunere", "str_data_incep",
              "str_data_sf", "str_venit_brut", "str_chelt_deduc", "str_venit_net_anual",
              "str_pierdere_anuala", "str_pierdere_precedenta", "str_pierdere_compensata",
              "str_venit_recalculat", "str_impozit_datorat_Ro", "str_impozit_platit",
              "str_credit_fiscal", "str_dif_impozit_datorat"},
    "oblig_estimat": {"bifa_optiune", "situatie_optiune", "baza_optiune", "cass_optiune",
                      "bifa_optiune_coasigurat", "totalCassDatorat", "totalCassDatoratCoasigurat"},
    "coasigurat": {"tipCoasigurat", "numeCoasigurat", "cnpCoasigurat", "bazaCassCoasigurat",
                   "cassDatoratCoasigurat"},
    # oblig_realizat: ~90 campuri CAS/CASS/impozit. Set larg; valorile vin gata calculate din manual.
    "oblig_realizat": {
        "real_camere_inchiriere", "real_venit_inchiriere", "real_impozit_inchiriere",
        "str_cas_baza", "str_cas_datorat", "str_cass_baza", "str_cass_datorat",
        "bifa_cas_real", "cas_total_ven", "cas_baza", "cas_datorat", "cas_retinut_platitor",
        "cas_dif_plus", "bifa_cass_datorat_ai", "bifa_cass_datorat_dpi", "cass_total_ven_ai",
        "baza_cass_datorat_ai", "cass_datorat_ai", "cass_ret_plat_alin6_ai", "cass_dif_plus_ai",
        "cass_dif_minus6_ai", "cass_ret_plat_alin7_ai", "cass_dif_minus8_ai", "bifa_cass_real",
        "cass_ven_dpi", "cass_ven_asc", "cass_ven_cfb", "cass_ven_inv", "cass_ven_asp",
        "cass_ven_alt", "cass_total_ven", "cass_baza", "cass_datorat", "cass_retinut",
        "cass_dif_plus", "real_venit_net_recalculat_ai", "real_cas_deduc_ai",
        "real_cass_deductibil_ai", "real_venit_net_impozabil_ai", "real_venit_net_imp_redus_ai",
        "real_impozit_datorat_ai", "real_cas_venit_net_ai", "real_cas_total_ven_ai",
        "real_cas_pondere_ai", "real_cas_datorata_ai", "real_cas_deductibila_ai",
        "real_cass_venit_net_ai", "real_cass_total_ven_ai", "real_cass_pondere_ai",
        "real_cass_datorata_ai", "real_cass_calculata_ai", "real_cass_deductibila_ai",
        "real_venit_net_recalc_dpi", "real_cas_dpi", "real_venit_net_impozabil_dpi",
        "real_venit_net_imp_redus_dpi", "real_impozit_datorat_dpi", "real_cas_venit_net_dpi",
        "real_cas_total_ven_dpi", "real_cas_pondere_dpi", "real_cas_datorata_dpi",
        "real_cas_deductibila_dpi", "real_diferenta_CASS", "real_impozit_diferenta_CASS",
        "oblimpoz_real_total", "oblimpoz_real_anticipat", "oblimpoz_real_dif_deplata",
        "oblimpoz_real_dif_restituit", "oblcas_real_difPlus", "oblcas_real_str",
        "oblcass_real_difPlus_ai", "oblcass_real_difMinus_ai", "oblcass_real_difMinus_174",
        "oblcass_real_difPlus_dpi", "oblcass_real_str", "impozit_venit_plus",
        "impozit_venit_minus", "cas_plus", "cass_plus", "cass_minus", "dif_de_plata",
        "dif_de_restituit", "oblimpozit_real_bonif", "oblcas_real_bonif", "oblcass_real_bonif"},
}

# Flag-uri (bife) de pe radacina, implicit 0, suprascriabile din `manual`.
_BIFE = ["bifa_succesor", "anulare_litA", "anulare_litB", "bifa_conformare", "bifa111",
         "bifa112", "bifa113", "bifa121", "bifa122", "bifa131", "bifa132", "bifa14", "bifa15"]
_BIFE_OPT = ["bifa16", "bifa18"]  # optionale


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != len(_CNP_W) + 1:
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(len(_CNP_W)))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[len(_CNP_W)])


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _lei(x):
    """Rotunjire half-up la leu intreg (D212 lucreaza in lei intregi; campurile _f sunt long)."""
    if x in (None, ""):
        return 0
    q = Decimal(str(x).replace(",", ".")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(q)


def _suma_cifre_cnp(cnp):
    cnp = _cif(cnp)
    return sum(int(d) for d in cnp)


def calcul_d212(manual):
    """totalPlata_A = suma de control (DUK regula R4).

    = suma sumelor 'de plata' furnizate (manual['sume_de_plata'] = lista de valori lei) rotunjite;
    daca suma e 0 (nimic de plata), = suma cifrelor CNP (marcaj de control nenul, cerut de R4).
    Apelantul poate impune direct manual['totalPlata_A'] (cand a calculat el suma de control)."""
    if manual.get("totalPlata_A") not in (None, ""):
        return {"totalPlata_A": _lei(manual.get("totalPlata_A"))}
    s = sum(_lei(v) for v in (manual.get("sume_de_plata") or []))
    if s == 0:
        s = _suma_cifre_cnp(manual.get("cif"))
    return {"totalPlata_A": s}


def pull(conn, schema, perioada):
    """D212 e MANUALA pe persoana fizica; firma nu are registru PF. conn poate fi None."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsa nume/denumire contribuabil (nume_c).")
    if not str(manual.get("adresa_c") or "").strip():
        er.append("Lipsa adresa contribuabil (adresa_c).")
    nerez = str(manual.get("nerezident") or "0").strip()
    if nerez == "1":
        if not _cif(manual.get("cif_str")):
            er.append("Nerezident: lipsa cod fiscal strain (cif_str).")
    else:
        if not _cnp_valid(manual.get("cif")):
            er.append("CNP contribuabil (cif) invalid (13 cifre + cifra de control).")
    an = int(manual.get("an_r") or getattr(prof, "an", 0) or 0)
    if an and an < 2025:
        er.append("an_r %d sub anul minim acceptat de validator (2025)." % an)
    for nume in _COPII:
        cap = manual.get(nume)
        if cap:
            straine = set(cap) - _CAMPURI[nume]
            if straine:
                er.append("Capitol %s: campuri necunoscute (respinse de validator): %s"
                          % (nume, ", ".join(sorted(straine))))
    return er


def _attr(nume, val, lim=None):
    return '%s="%s"' % (nume, _esc(val, lim))


def build_xml(prof, an, luna, manual, calc=None):
    calc = calc or calcul_d212(manual)
    nerez = str(manual.get("nerezident") or "0").strip()
    h = []
    h.append(_attr("d_rec", manual.get("d_rec", "0")))
    h.append(_attr("rectif1", manual.get("rectif1", "0")))
    h.append(_attr("rectif2", manual.get("rectif2", "0")))
    h.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    h.append(_attr("luna_r", _LUNA_R))
    h.append('an_r="%d"' % int(an))
    for b in _BIFE:
        h.append('%s="%s"' % (b, _esc(manual.get(b, "0"))))
    for b in _BIFE_OPT:
        if manual.get(b) is not None:
            h.append('%s="%s"' % (b, _esc(manual.get(b))))
    if manual.get("bifa_succesor") == "1" and manual.get("cif_succesor"):
        h.append(_attr("cif_succesor", _cif(manual.get("cif_succesor"))))
    # identificare
    h.append(_attr("nume_c", manual.get("nume_c"), 250))
    h.append(_attr("adresa_c", manual.get("adresa_c"), 200))
    for opt, lim in (("telefon_c", 15), ("fax_c", 15), ("email_c", 250)):
        if manual.get(opt):
            h.append(_attr(opt, manual.get(opt), lim))
    h.append(_attr("nerezident", nerez))
    if nerez == "1":
        if manual.get("cif"):
            h.append(_attr("cif", _cif(manual.get("cif"))))
        h.append(_attr("stat_rezidenta", manual.get("stat_rezidenta")))
        h.append(_attr("cif_str", manual.get("cif_str")))
    else:
        h.append(_attr("cif", _cif(manual.get("cif"))))
    if manual.get("cont_bancar"):
        h.append(_attr("cont_bancar", str(manual.get("cont_bancar")).replace(" ", "").upper(), 24))
    # imputernicit / reprezentant (optional)
    if manual.get("den_i"):
        h.append(_attr("den_i", manual.get("den_i"), 250))
        h.append(_attr("cif_i", _cif(manual.get("cif_i"))))
        for opt, lim in (("adresa_i", 200), ("telefon_i", 15), ("fax_i", 15), ("email_i", 250)):
            if manual.get(opt):
                h.append(_attr(opt, manual.get(opt), lim))
    # elemente-copil (capitole), emise cand sunt furnizate in manual
    copii = []
    for nume in _COPII:
        cap = manual.get(nume)
        if not cap:
            continue
        a = [_attr(k, cap[k]) for k in _CAMPURI[nume] if k in cap and cap[k] is not None]
        copii.append("  <%s %s/>" % (nume, " ".join(a)))
    corp = ("\n" + "\n".join(copii) + "\n") if copii else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<d212 xmlns="%s" %s>%s</d212>\n' % (NS, " ".join(h), corp))


@dataclass
class Rezultat212:
    an: int
    total_plata_a: int = 0
    capitole: list = field(default_factory=list)
    avertismente: list = field(default_factory=list)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(getattr(perioada, "an", None) or manual.get("an_r"))
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D212 nu se poate genera: " + " ".join(er))
    calc = calcul_d212(manual)
    xml = build_xml(prof, an, None, manual, calc)
    capitole = [n for n in _COPII if manual.get(n)]
    return xml, Rezultat212(an=an, total_plata_a=calc["totalPlata_A"], capitole=capitole)
