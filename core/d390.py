"""
Modul D390 — Declarație recapitulativă VIES privind livrările/achizițiile/
prestările intracomunitare (ANAF v3, OPANAF 705/11.03.2020).

REFĂCUT DE LA ZERO după ANAF structura D390 2020_180320 (structura_D390_2020_180320).

Separare strictă:
  - CALCUL PUR : calcul_d390(prof, an, luna, facturi, manual=None) -> Rezultat
  - VALIDARE   : valideaza(rezultat) -> listă erori
  - XML        : build_xml(rezultat) -> str
  - CITIRE DB  : pull(conn, schema, an, luna) -> (prof, facturi)
  - ORCHESTRARE: genereaza(conn, schema, an, luna) -> (xml, rezultat)

Tipuri operațiune (oficial):
  L = livrări intracomunitare de bunuri
  T = livrări în cadrul unei operațiuni triunghiulare
  A = achiziții intracomunitare de bunuri
  P = prestări intracomunitare de servicii
  S = achiziții intracomunitare de servicii
  R = livrări intracomunitare de bunuri în regim special pentru agricultori

Mapare automată din facturi: emisă->L (bunuri), primită->A (bunuri).
Serviciile (P/S) și triangulația (T/R) = clasificare manuală de contabil (prin `manual`).

totalPlata_A = nrOPI + bazaL + bazaT + bazaA + bazaP + bazaS + bazaR (formula oficială).
"""

from core.common import text_anaf as _t  # limita 75 car. ANAF (27.07.2026)
import re
import datetime
from core import common as c
from dataclasses import dataclass, field
from decimal import Decimal

NS = "mfp:anaf:dgti:d390:declaratie:v3"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
# CUI UE: prefix 2 litere + cod
_CUI_UE = re.compile(r"^([A-Z]{2})([0-9A-Z]+)$")

# Nomenclator oficial țări (cod TVA -> cod ANAF în XML). Atenție: Croația HR -> CR în XML.
TARI_UE = {
    "AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
    "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK",
    "ES", "SE", "HU", "XI",  # XI = Irlanda de Nord (post-Brexit, VIES)
}
# prefixul de TVA HR (Croația) se scrie CR în nomenclatorul ANAF
_TARA_XML = {"HR": "CR"}

TIPURI = ("L", "T", "A", "P", "S", "R")


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    """Baza D390 in lei intregi, rotunjire ARITMETICA (half-up).

    27.07.2026 - trecut de la `round()` (BANCARA) la ROUND_HALF_UP. Rationament:
      (a) VERIFICAT LA SURSA: OPANAF 705/2020 si instructiunile de completare NU prevad o
          regula de rotunjire pentru D390 - deci nu se interzice cea aritmetica;
      (b) CONSECVENTA: d390 era SINGURUL din cele 10 generatoare cu rotunjire bancara;
          d112/d300/d406/d710/d100/d101/d205 folosesc toate ROUND_HALF_UP;
      (c) RISC ASIMETRIC: la D112 ANAF cere EXPLICIT rotunjire aritmetica si a RESPINS-o pe
          cea bancara prin validator (DUK regula A91b, CAM 112 cerut 113). Daca aceeasi asteptare
          exista si la D390, bancara produce declaratii gresite; invers, aritmetica nu strica
          nimic - nicio sursa n-o interzice.
    Diferenta apare doar la .5 exact (112.5: bancar 112, aritmetic 113). Pe datele actuale
    nu se manifesta (toate bazele sunt rotunde), dar asta e noroc, nu garantie.

    MASCA SCOASA 27.07.2026: numar_fiscal ridica pe valoare invalida (vezi core/numere.py).
    """
    from decimal import Decimal, ROUND_HALF_UP
    from core.numere import numar_fiscal
    return int(numar_fiscal(x, "D390").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _tara_xml(t):
    return _TARA_XML.get(t, t)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    ops: dict = field(default_factory=dict)        # (tip,tara,cod,den) -> baza int
    rezumat: dict = field(default_factory=dict)    # {L,T,A,P,S,R: int}
    nr_opi: int = 0
    total_baza: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def _facturi_ic(facturi):
    """Facturile INTRACOMUNITARE valide -> [{directie, tara, cod, den, baza}] + (skip_nocui,
    skip_dom). Latura auto, FĂRĂ tip încă (tipul se decide separat: default L/A + reclasificare).
    Sursa unică a filtrului IC — folosit și de calcul_d390 și de operatiuni_auto (fără dublură)."""
    out = []
    skip_nocui = skip_dom = 0
    for f in facturi:
        raw = (f.get("cui") or "").strip().upper().replace(" ", "").replace("-", "")
        m = _CUI_UE.match(raw)
        if not m:
            skip_nocui += 1
            continue
        tara, cod = m.group(1), m.group(2)[:12]
        if tara == "RO" or tara not in TARI_UE:
            skip_dom += 1
            continue
        out.append({"directie": f.get("directie"), "tara": tara, "cod": cod,
                    "den": (f.get("nume") or "")[:200],
                    "baza": Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0))})
    return out, skip_nocui, skip_dom


def operatiuni_auto(facturi, reclasificari=None):
    """[F125] Pentru UI: operațiunile auto-derivate din facturi, agregate pe (directie, tara, cod,
    den), cu tipul curent (default L/A sau reclasificat). Contabilul le vede și le reclasifică."""
    recl = reclasificari or {}
    ic, _, _ = _facturi_ic(facturi)
    agg = {}
    for o in ic:
        k = (o["directie"], o["tara"], o["cod"], o["den"])
        agg[k] = agg.get(k, Decimal("0")) + o["baza"]
    out = []
    for (directie, tara, cod, den), b in agg.items():
        tip_def = "L" if directie == "emisa" else "A"
        out.append({"directie": directie, "tara": tara, "cod": cod, "den": den,
                    "baza": _int(b), "tip_default": tip_def,
                    "tip_curent": recl.get((directie, tara, cod), tip_def)})
    return sorted(out, key=lambda x: (x["directie"], x["tara"], x["cod"]))


def calcul_d390(prof, an, luna, facturi, manual=None, reclasificari=None):
    """Calcul PUR. facturi: dict cu cui, nume, directie, total, tva.
    manual: listă opțională de dict-uri {tip, tara, cod, den, baza} introduse de contabil
            (linii pur manuale, fără factură în sistem).
    reclasificari: dict {(directie, tara, cod): tip} — override-ul tipului unei operațiuni
            auto-derivate (emisă implicit L, primită implicit A). RECLASIFICĂ, nu adaugă →
            fără dublă numărare a facturilor de servicii (F125). Vezi DECIZII 21.07."""
    ops = {}
    recl = reclasificari or {}
    ic, skip_nocui, skip_dom = _facturi_ic(facturi)
    for o in ic:
        tip_def = "L" if o["directie"] == "emisa" else "A"       # implicit: bunuri
        tip = recl.get((o["directie"], o["tara"], o["cod"]), tip_def)  # override contabil
        if tip not in TIPURI:
            tip = tip_def
        k = (tip, o["tara"], o["cod"], o["den"])
        ops[k] = ops.get(k, Decimal("0")) + o["baza"]

    # operațiuni manuale (P/S/T/R)
    for op in (manual or []):
        tip = op.get("tip")
        if tip not in TIPURI:
            # [GARD CLASA] operatiune manuala a contabilului cu tip gresit -> eroare vizibila, nu drop tacit.
            raise ValueError("D390: operatiune manuala cu tip necunoscut %r (acceptate: %s). Un tip introdus "
                             "de contabil care nu e in lista trebuie sa produca eroare vizibila, nu sa dispara "
                             "tacut din declaratie." % (tip, ", ".join(map(str, TIPURI))))
        tara = (op.get("tara") or "").upper()
        cod = (op.get("cod") or "")[:12]
        den = (op.get("den") or "")[:200]
        k = (tip, tara, cod, den)
        ops[k] = ops.get(k, Decimal("0")) + Decimal(str(op.get("baza") or 0))

    rez = {t: Decimal("0") for t in TIPURI}
    for (tip, _, _, _), b in ops.items():
        rez[tip] += b
    bz = {t: _int(rez[t]) for t in TIPURI}
    nr_opi = len(ops)
    tot = _int(sum(rez.values()))
    # formula oficială totalPlata_A
    total_plata = nr_opi + bz["L"] + bz["T"] + bz["A"] + bz["P"] + bz["S"] + bz["R"]

    ops_int = {k: _int(v) for k, v in ops.items()}
    res = Rezultat(an=an, luna=luna, prof=prof, ops=ops_int, rezumat=bz,
                   nr_opi=nr_opi, total_baza=tot, total_plata_a=total_plata)
    if skip_dom:
        res.avertismente.append("%d facturi cu parteneri RO/non-UE — excluse (D390 e doar intracomunitar)." % skip_dom)
    if skip_nocui:
        res.avertismente.append("%d facturi fără CUI UE valid (prefix țară) — excluse." % skip_nocui)
    if not ops:
        res.avertismente.append("Nicio operațiune intracomunitară în lună — D390 se depune doar dacă există operațiuni.")
    res.avertismente.append("Mapare automată: emisă->L, primită->A (bunuri). Servicii (P/S) și triangulație (T/R) = clasificare manuală.")
    return res


def valideaza(res):
    """Verifică regulile ANAF. Întoarce listă de erori."""
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    if res.an >= 2020 and res.luna < 2 and res.an == 2020:
        erori.append("Pentru an=2020, luna >= 2.")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI firmă (obligatoriu).")
    if not (prof.get("nume")):
        erori.append("LIPSĂ denumire firmă.")
    # codO obligatoriu pentru L,T,P,R
    for (tip, tara, cod, den) in res.ops:
        if tip in ("L", "T", "P", "R") and not cod:
            erori.append("Operatorul %s/%s (tip %s) nu are cod — obligatoriu pentru L,T,P,R." % (tara, den, tip))
        if tara and tara not in TARI_UE:
            erori.append("Țara %s nu e în nomenclatorul UE." % tara)
    # totalPlata_A coerent
    calc = (res.nr_opi + res.rezumat["L"] + res.rezumat["T"] + res.rezumat["A"]
            + res.rezumat["P"] + res.rezumat["S"] + res.rezumat["R"])
    if calc != res.total_plata_a:
        erori.append("totalPlata_A incoerent (calcul=%d, stocat=%d)." % (calc, res.total_plata_a))
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip()
    tel = prof.get("telefon") or ""
    mail = prof.get("email") or ""
    bz = res.rezumat
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie390 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D390.xsd" '
           'luna="%d" an="%d" d_rec="0" nume_declar="%s" prenume_declar="%s" '
           'functie_declar="%s" cui="%s" den="%s" adresa="%s"'
           % (NS, NS, res.luna, res.an,
              _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR")),
              _esc(_t(prof.get("declarant_prenume") or "-")),
              _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR")),
              _esc(cui), _esc(_t(den)), _esc(_t(adr))))
    if tel:
        hdr += ' telefon="%s"' % _esc(tel)
    if mail:
        hdr += ' mail="%s"' % _esc(mail)
    # CORECTAT 16.07.2026, dupa verificare la sursa oficiala (static.anaf.ro,
    # structura_D390_2020_180320.pdf, OPANAF 705/2020): <rezumat> EXISTA, e element
    # separat, 1 aparitie obligatorie. Fix-ul de 15.07.2026 il scosese ("REZUMATUL E
    # INLINE PE RADACINA") pe baza unui `strings` pe binarul validatorului care n-a
    # gasit clasa/tag "rezumat" acolo - concluzie gresita: absenta dintr-un extras nu
    # inseamna absenta. Sursa oficiala arata clar "<rezumat> 1 aparitie", cu campurile
    # nr_pag/nrOPI/bazaL/bazaT/bazaA/bazaP/bazaS/bazaR/total_baza in interiorul lui,
    # nu pe radacina.
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    H.append('  <rezumat nr_pag="1" nrOPI="%d" bazaL="%d" bazaT="%d" bazaA="%d" '
             'bazaP="%d" bazaS="%d" bazaR="%d" total_baza="%d"/>'
             % (res.nr_opi, bz["L"], bz["T"], bz["A"], bz["P"], bz["S"], bz["R"],
                res.total_baza))
    # operațiuni ordonate (tip, tara, cod)
    for (tip, tara, cod, den) in sorted(res.ops.keys(), key=lambda k: (k[0], k[1], k[2])):
        H.append('  <operatie tip="%s" tara="%s" codO="%s" denO="%s" baza="%d"/>'
                 % (tip, _tara_xml(tara), _esc(cod), _esc(den), res.ops[(tip, tara, cod, den)]))
    H.append("</declaratie390>")
    return "\n".join(H)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT f.id, f.tert_nume, f.tert_cui, c.nume AS c_nume, c.cui AS c_cui, "
                    "f.directie, f.total, f.tva "
                    "FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                    "WHERE f.data_emitere >= %s AND f.data_emitere < %s ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    # CUI-ul: intai clientul din nomenclator (c.cui), altfel tert_cui de pe factura.
    # Bug dovedit 16.07.2026 prin audit pe date reale: se citea DOAR c.cui, legat de
    # client_id. Facturile create direct (fara fisa de client) si TOATE facturile
    # PRIMITE (care n-au niciodata client_id - ala e pentru clienti, nu furnizori)
    # aveau cui="" -> respinse tacit de calcul_d390 la primul filtru CUI. D390
    # genera mereu "0 operatiuni" chiar si cu facturi UE reale in luna.
    facturi = [{"cui": (r["c_cui"] or r["tert_cui"] or "").strip(),
                "nume": (r["c_nume"] or r["tert_nume"] or "").strip(),
                "directie": r["directie"],
                "total": r["total"] if r["total"] is not None else 0,
                "tva": r["tva"] if r["tva"] is not None else 0} for r in rows]
    return prof, facturi


def pull_manual(conn, schema, an, luna):
    """[F125] Liniile pur manuale D390 pentru luna (introduse de contabil, fără factură)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT tip, tara, cod, den, baza FROM {schema}.d390_manual "
                    f"WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        return [{"tip": t, "tara": ta, "cod": c, "den": d, "baza": b}
                for (t, ta, c, d, b) in cur.fetchall()]


def pull_reclasificari(conn, schema, an, luna):
    """[F125] Override-urile de tip pe operațiuni auto-derivate: {(directie, tara, cod): tip}."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT directie, tara, cod, tip FROM {schema}.d390_reclasificare "
                    f"WHERE an=%s AND luna=%s", (an, luna))
        return {(dir_, ta, c): t for (dir_, ta, c, t) in cur.fetchall()}


def d390_are_operatiuni(conn, schema, an, luna, azi=None):
    """Fapt per-luna: exista operatiuni intracomunitare in (an, luna)? -> True | False | None.
      True/False = perioada INCHISA (luna incheiata inainte de azi): fapt STABILIT din facturi IC
                   (_facturi_ic) + d390_manual (liniile manuale F125) - sursele D390 ale unui PLATITOR.
      None       = perioada DESCHISA (curenta/viitoare): exigibilitatea nu se poate stabili inca.
    Se apeleaza DOAR pentru platitori (art. 316) - poarta din obligatii_datorate. NU citeste d301_operatiuni
    (acela e artefact D301 / NEplatitori, irelevant pentru D390 al unui platitor, si lipseste la unele scheme
    vechi de partida simpla -> ar crapa). Temei: D390 se depune NUMAI pentru lunile in care ia nastere
    exigibilitatea operatiunilor IC (instr. completare D390, anexa OPANAF 705/2020; principiu identic OPANAF
    394/2017 pct.1.2 la D394). NU e obligatie lunara fixa. Vezi DECIZII 23.07."""
    azi = azi or c.azi_ro()
    prima_urm = datetime.date(an + 1, 1, 1) if luna == 12 else datetime.date(an, luna + 1, 1)
    if prima_urm > azi:
        return None                         # luna nu s-a incheiat -> perioada deschisa
    _prof, facturi = pull(conn, schema, an, luna)
    ic, _s1, _s2 = _facturi_ic(facturi)
    if ic:
        return True
    if pull_manual(conn, schema, an, luna):
        return True
    return False


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSA CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSA denumire firma.")
    return erori


def calculeaza(conn, schema, an, luna, manual=None, reclasificari=None):
    """Calculul D390, FARA poarta fiscala. Intoarce doar `res`.

    Separat de `genereaza` pe 27.07.2026: EMITEREA are o poarta (D390 nu se depune pe zero,
    OPANAF 705/2020 pct. 1.2), dar CALCULUL nu trebuie s-o aiba. Verificatorii incrucisati
    (control_incrucisat.verifica_d390) au nevoie de bazele IC ca sa compare cu evidenta si cu
    D300 depus - iar acolo "zero operatiuni" e un raspuns legitim (baza 0), nu o eroare.

    Fara separarea asta, poarta de la emitere transforma orice luna fara operatiuni intr-un
    verdict GRI pe intreg verificatorul, ascunzand sub-verificarea D-vs-D. Regresie reala,
    prinsa de suita imediat dupa adaugarea portii.
    """
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, facturi = pull(conn, schema, an, luna)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D390 nu se poate genera: " + " ".join(_er))
    # [F125] dacă nu s-au dat explicit (ex. în teste), se iau din evidența persistată — ca toate
    # căile (wizard, pachet, control încrucișat) să vadă ACELEAȘI clasificări.
    if manual is None:
        manual = pull_manual(conn, schema, an, luna)
    if reclasificari is None:
        reclasificari = pull_reclasificari(conn, schema, an, luna)
    res = calcul_d390(prof, an, luna, facturi, manual, reclasificari)
    return res


def genereaza(conn, schema, an, luna, manual=None, reclasificari=None):
    """Genereaza XML-ul D390. Refuza luna fara operatiuni (vezi poarta de mai jos)."""
    res = calculeaza(conn, schema, an, luna, manual, reclasificari)
    # POARTA FISCALA (27.07.2026, verificat la sursa): D390 NU se depune pe zero.
    # OPANAF 705/2020, Instructiuni pct. 1.2: "Persoanele impozabile inregistrate in scopuri
    # de TVA depun declaratia recapitulativa NUMAI pentru lunile calendaristice in care ia
    # nastere exigibilitatea taxei" (art. 325 Cod fiscal, Legea 227/2015). O luna fara
    # operatiuni intracomunitare NU produce obligatie de depunere.
    #
    # Validatorul ANAF confirma regula structural: cu zero <operatie> respinge cu "lipsa
    # sectiune obligatorie"; cu o singura operatiune, acelasi XML e valid (dovedit pe
    # tenant_001/iunie 2026). Deci sectiunea <operatie> e minOccurs=1 - structura oglindeste
    # regula fiscala.
    #
    # Inainte de asta generatorul emitea un XML gol pe care ANAF il respingea, iar contabilul
    # primea un mesaj de structura in loc de "nu ai ce depune". Acelasi tipar ca la d205
    # ("D205 fara niciun beneficiar de venit").
    if res.nr_opi == 0:
        raise ValueError(
            "D390 nu se depune pe zero: luna %02d/%d nu are nicio operatiune intracomunitara. "
            "Declaratia recapitulativa se depune NUMAI pentru lunile in care ia nastere "
            "exigibilitatea taxei (OPANAF 705/2020 pct. 1.2; art. 325 Cod fiscal). "
            "Daca ar fi trebuit sa existe operatiuni, verifica daca facturile UE sunt "
            "introduse si daca partenerii au cod de TVA valid." % (luna, an))
    return build_xml(res), res
