"""core/d401.py — D401: Declaratie informativa privind proprietatile imobiliare detinute de rezidenti ai altor state (schimb automat obligatoriu de informatii, DAC).

Declaratie MANUALA depusa de organul fiscal local / primarie. Raporteaza, catre ANAF (care le transmite
prin schimbul automat DAC — Directiva 2011/16/UE, transpusa in Codul de procedura fiscala, Titlul X / art.
291 CPF si OPANAF de aprobare a formularului 401), proprietatile imobiliare de pe raza UAT detinute de
persoane fizice/juridice rezidente in alte state membre. Aplicatia nu are registrul de rol nominal unic al
primariei; TOATE datele vin din `manual` (nu se fabrica).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator / D401Validator.jar). Namespace si
radacina, campurile si regulile au fost CITITE din bytecode (d401validator/v0: Declaratie401, Detinator,
Proprietate, Coproprietar) si probate pe validator. Radacina confirmata din bytecode: <declaratie401>,
namespace mfp:anaf:dgti:d401:declaratie:v1. Ierarhie (din ordinea de citire + procedurile insert_*):
  declaratie401 > detinator (repetabil) > proprietate (repetabil) > coproprietar (repetabil).

Atribute (casing exact din constant-pool):
  declaratie401: an, luna, d_rec, cif, Den_primarie, Judet_primarie, Sector_primarie, Localitate_primarie,
    Adresa_primarie, nume_declar, prenume_declar, functie_declar, nr_pers, totalPlata_A.
  detinator: id_detinator, Tip_detinator (1=PF, 2=PJ), Den_detinator, Stat_detinator, Localitate_SR,
    Strada_SR, Nr_SR, Codp_SR, CIF_SR, CIF_rom, Nationalitate, Data_nasterii, Act_id, codTVA,
    Den_repr, CIF_repr, Adr_repr.
  proprietate: id_proprietate, Tip_proprietate (1=cladire, 2=teren, 3=cladire+teren), Data_D, Act_nr_D,
    Act_emitent_D, Mod_D, Data_I, Act_nr_I, Act_emitent_I, Mod_I, Judet_prop, Sector_prop, Localitate_prop,
    Strada_prop, Nr_prop, Bloc_prop, Scara_prop, Etaj_prop, Apart_prop, Suprafata_cladire, Suprafata_teren,
    Destinatie_cladire, Val1..Val10, Moneda1..Moneda10, Alta_val, Tip_unic_coprop (1=unic, 2=coproprietari),
    Cota_proprietar.
  coproprietar: id_coproprietar, Den_coproprietar, CIF_rom_co, CIF_SR_co, Cota_coproprietar.

Reguli citite din validator (probate; prefix "DUK regula"):
  DUK regula nr_pers: nr_pers = numarul de elemente <detinator>.
  DUK regula totalPlata_A: totalPlata_A = suma tuturor Val1..Val10 din toate <proprietate>.
  DUK regula detinator-PF: daca Tip_detinator=1 (PF) cel putin unul din Data_nasterii, codTVA, CIF_rom,
    CIF_SR trebuie completat; Act_id si Nationalitate NUMAI pentru PF; Den_repr/CIF_repr/Adr_repr NUMAI PJ.
  DUK regula suprafata: Tip_proprietate=1 -> Suprafata_cladire >0 si Suprafata_teren necompletat;
    Tip_proprietate=2 -> Suprafata_teren >0 si Suprafata_cladire necompletat; Tip_proprietate=3 -> ambele >0.
  DUK regula destinatie: Destinatie_cladire se completeaza daca si numai daca Tip_proprietate <> 2.
  DUK regula Val6: Val6 (valoare de construire) doar pentru Tip_proprietate <> 2.
  DUK regula Val5: Val5 (valoare de inventar) doar pentru Tip_detinator=2 (PJ) si Tip_proprietate <> 2.
  DUK regula Moneda: daca ValN completat -> MonedaN obligatoriu.
  DUK regula valori: cel putin unul din Val1..Val10 <> 0.
  DUK regula data: an(Data_D) <= an raportare; an(Data_I) = an raportare; Data_D <= Data_I; Tip_proprietate=2
    -> Mod_D <> 1 (construire imobil).
  DUK regula coproprietari: Tip_unic_coprop=1 -> Cota_proprietar=100, fara <coproprietar>;
    Tip_unic_coprop=2 -> cel putin un <coproprietar>, suma cotelor in intervalul (99, 101); cota strict pozitiva.

Contract dXXX: pull/erori_generare/calcul_d401/build_xml/genereaza(conn, schema, perioada).
NEPOPULAT deliberat (nu se ghiceste): campuri de adresa optionale (Sector_*, Bloc/Scara/Etaj/Apart),
Act_nr_*/Act_emitent_*/Mod_I, Alta_val, Val2..Val10 (in afara valorii principale) — se dau prin `manual`.
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație informativă privind proprietățile imobiliare deținute de rezidenți ai altor state membre UE'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d401:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_MONEDE = {"RON", "EUR", "USD", "GBP", "CZK", "DKK", "HRK", "HUF", "PLN", "SEK", "SKK"}
_DATE_OK = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _int(x):
    """Intreg half-up din valoare (Decimal.quantize, nu bancara)."""
    s = str("" if x is None else x).replace(" ", "").replace(",", ".")
    if not s:
        return 0
    return int(Decimal(s).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cota(x):
    """Cota procentuala: pastreaza pana la 2 zecimale, half-up, fara zerouri inutile."""
    s = str("" if x is None else x).replace(" ", "").replace(",", ".")
    if not s:
        return ""
    d = Decimal(s).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    t = format(d, "f").rstrip("0").rstrip(".")
    return t


def _an_din_data(data):
    """an dintr-o data dd.MM.yyyy."""
    if _DATE_OK.match(str(data or "")):
        return int(str(data)[-4:])
    return None


def _valori(p):
    """Lista de (idx, valoare_int, moneda) pentru Val1..Val10 completate in proprietate."""
    out = []
    for i in range(1, 11):
        v = p.get("val%d" % i)
        if v in (None, ""):
            continue
        vi = _int(v)
        if vi == 0:
            continue
        out.append((i, vi, str(p.get("moneda%d" % i) or "").upper().strip()))
    return out


@dataclass
class Rezultat401:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_detinatori: int = 0
    nr_proprietati: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d401(manual):
    """DUK regula totalPlata_A: suma tuturor valorilor Val1..Val10 din toate proprietatile."""
    total = 0
    npr = 0
    for det in manual.get("detinatori") or []:
        for p in det.get("proprietati") or []:
            npr += 1
            for _, vi, _m in _valori(p):
                total += vi
    return {"totalPlata_A": total, "nr_proprietati": npr}


def pull(conn, schema, perioada):
    """D401 e MANUALA (organ fiscal local); aplicatia nu are rolul nominal al primariei. Contractul cere `pull`."""
    return {}


def _erori_detinator(idx, det):
    er = []
    tip = _int(det.get("tip_detinator"))
    if tip not in (1, 2):
        er.append("Detinator %d: Tip_detinator obligatoriu 1 (PF) sau 2 (PJ)." % idx)
    if not str(det.get("den_detinator") or "").strip():
        er.append("Detinator %d: lipsă Den_detinator." % idx)
    if tip == 1:
        # DUK regula detinator-PF: cel putin unul din Data_nasterii, codTVA, CIF_rom, CIF_SR
        if not any(str(det.get(k) or "").strip() for k in
                   ("data_nasterii", "cod_tva", "cif_rom", "cif_sr")):
            er.append("Detinator %d (PF): completează cel puțin unul din "
                      "Data_nasterii/codTVA/CIF_rom/CIF_SR (DUK regula detinator-PF)." % idx)
        for k, lbl in (("den_repr", "Den_repr"), ("cif_repr", "CIF_repr"), ("adr_repr", "Adr_repr")):
            if str(det.get(k) or "").strip():
                er.append("Detinator %d (PF): %s se completează numai pentru PJ." % (idx, lbl))
    if tip == 2:
        for k, lbl in (("act_id", "Act_id"), ("nationalitate", "Nationalitate")):
            if str(det.get(k) or "").strip():
                er.append("Detinator %d (PJ): %s se completează numai pentru PF." % (idx, lbl))
    if det.get("data_nasterii") and not _DATE_OK.match(str(det["data_nasterii"])):
        er.append("Detinator %d: Data_nasterii format zz.ll.aaaa." % idx)
    if not (det.get("proprietati")):
        er.append("Detinator %d: nicio proprietate." % idx)
    return er


def _erori_proprietate(di, pi, p, an_rap):
    er = []
    pre = "Detinator %d / proprietate %d:" % (di, pi)
    tip = _int(p.get("tip_proprietate"))
    if tip not in (1, 2, 3):
        er.append("%s Tip_proprietate obligatoriu 1/2/3." % pre)
    sc = p.get("suprafata_cladire")
    st = p.get("suprafata_teren")
    if tip in (1, 3) and not (sc and Decimal(str(sc).replace(",", ".")) > 0):
        er.append("%s Suprafata_cladire >0 obligatoriu (DUK regula suprafață)." % pre)
    if tip == 2 and sc:
        er.append("%s Suprafata_cladire nu se completează pentru teren (DUK regula suprafață)." % pre)
    if tip in (2, 3) and not (st and Decimal(str(st).replace(",", ".")) > 0):
        er.append("%s Suprafata_teren >0 obligatoriu (DUK regula suprafață)." % pre)
    if tip == 1 and st:
        er.append("%s Suprafata_teren nu se completează pentru clădire (DUK regula suprafață)." % pre)
    dc = str(p.get("destinatie_cladire") or "").strip()
    if tip == 2 and dc:
        er.append("%s Destinatie_cladire nu se completează pentru teren (DUK regula destinatie)." % pre)
    if tip in (1, 3) and not dc:
        er.append("%s Destinatie_cladire obligatoriu (DUK regula destinatie)." % pre)
    # acte dobandire (obligatorii, probat pe validator: "atributul trebuie sa existe")
    if not str(p.get("act_nr_d") or "").strip():
        er.append("%s Act_nr_D obligatoriu (DUK: atributul trebuie să existe)." % pre)
    if not str(p.get("act_emitent_d") or "").strip():
        er.append("%s Act_emitent_D obligatoriu (DUK: atributul trebuie să existe)." % pre)
    # date
    dd, di_ = p.get("data_d"), p.get("data_i")
    if not _DATE_OK.match(str(dd or "")):
        er.append("%s Data_D obligatoriu, format zz.ll.aaaa." % pre)
    else:
        if _an_din_data(dd) > an_rap:
            er.append("%s anul Data_D <= anul raportarii (%d)." % (pre, an_rap))
    if di_:
        if not str(p.get("act_nr_i") or "").strip():
            er.append("%s Act_nr_I obligatoriu cand există Data_I." % pre)
        if not str(p.get("act_emitent_i") or "").strip():
            er.append("%s Act_emitent_I obligatoriu cand există Data_I." % pre)
        if not _DATE_OK.match(str(di_)):
            er.append("%s Data_I format zz.ll.aaaa." % pre)
        else:
            if _an_din_data(di_) != an_rap:
                er.append("%s anul Data_I trebuie să fie = anul raportarii (%d)." % (pre, an_rap))
            if _DATE_OK.match(str(dd or "")) and dd and _cmp_data(dd) > _cmp_data(di_):
                er.append("%s Data_D <= Data_I." % pre)
    if tip == 2 and _int(p.get("mod_d")) == 1:
        er.append("%s pentru teren Mod_D trebuie să fie diferit de 1 (construire)." % pre)
    # valori / monede
    vals = _valori(p)
    if not vals:
        er.append("%s cel puțin un Val1..Val10 <> 0 (DUK regula valori)." % pre)
    for i, _vi, m in vals:
        if not m:
            er.append("%s Val%d completat -> Moneda%d obligatoriu (DUK regula Moneda)." % (pre, i, i))
        elif m not in _MONEDE:
            er.append("%s Moneda%d '%s' necunoscută (%s)." % (pre, i, m, ",".join(sorted(_MONEDE))))
    if tip == 2 and any(i == 6 for i, _v, _m in vals):
        er.append("%s Val6 (valoare de construire) nu se completează pentru teren (DUK regula Val6)." % pre)
    # coproprietari
    tuc = _int(p.get("tip_unic_coprop"))
    copro = p.get("coproprietari") or []
    if tuc not in (1, 2):
        er.append("%s Tip_unic_coprop obligatoriu 1 (unic) sau 2 (coproprietari)." % pre)
    if tuc == 1:
        if copro:
            er.append("%s proprietar unic -> fără coproprietari (DUK regula coproprietari)." % pre)
        if _cota(p.get("cota_proprietar")) not in ("100",):
            er.append("%s proprietar unic -> Cota_proprietar = 100 (DUK regula coproprietari)." % pre)
    if tuc == 2:
        if not copro:
            er.append("%s coproprietate -> cel puțin un coproprietar (DUK regula coproprietari)." % pre)
        s = Decimal(_cota(p.get("cota_proprietar")) or "0")
        for c in copro:
            s += Decimal(_cota(c.get("cota_coproprietar")) or "0")
        if not (Decimal("99") < s < Decimal("101")):
            er.append("%s suma cotelor (%s) trebuie în intervalul (99,101) (DUK regula coproprietari)." % (pre, s))
    if not (Decimal(_cota(p.get("cota_proprietar")) or "0") > 0):
        er.append("%s Cota_proprietar strict pozitiv (DUK regula coproprietari)." % pre)
    return er


def _cmp_data(d):
    return (d[6:10], d[3:5], d[0:2])


def erori_generare(prof, manual):
    er = []
    an_rap = _int(manual.get("an"))
    if not (1900 < an_rap < 2100):
        er.append("an raportare invalid (%s)." % manual.get("an"))
    for k, lbl in (("cif", "cif"), ("den_primarie", "Den_primarie"),
                   ("localitate_primarie", "Localitate_primarie"), ("adresa_primarie", "Adresa_primarie"),
                   ("nume_declar", "nume_declar"), ("prenume_declar", "prenume_declar"),
                   ("functie_declar", "functie_declar")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsă %s." % lbl)
    if not _cif(manual.get("cif")):
        er.append("cif primarie invalid (cifre).")
    det = manual.get("detinatori") or []
    if not det:
        er.append("Nicio pozitie detinator (detinatori).")
    for i, d in enumerate(det, 1):
        er += _erori_detinator(i, d)
        for j, p in enumerate(d.get("proprietati") or [], 1):
            er += _erori_proprietate(i, j, p, an_rap)
    return er


def _attr(name, val):
    return ' %s="%s"' % (name, val)


def build_xml(prof, an, luna, manual):
    calc = calcul_d401(manual)
    det = manual.get("detinatori") or []
    h = []
    h.append(_attr("an", int(an)))
    h.append(_attr("luna", int(luna)))
    h.append(_attr("d_rec", _int(manual.get("d_rec"))))
    h.append(_attr("cif", _cif(manual.get("cif"))))
    h.append(_attr("Den_primarie", _esc(manual.get("den_primarie"), 200)))
    if manual.get("judet_primarie"):
        h.append(_attr("Judet_primarie", _esc(manual.get("judet_primarie"), 10)))
    if manual.get("sector_primarie"):
        h.append(_attr("Sector_primarie", _int(manual.get("sector_primarie"))))
    h.append(_attr("Localitate_primarie", _esc(manual.get("localitate_primarie"), 100)))
    h.append(_attr("Adresa_primarie", _esc(manual.get("adresa_primarie"), 200)))
    h.append(_attr("nume_declar", _esc(manual.get("nume_declar"), 75)))
    h.append(_attr("prenume_declar", _esc(manual.get("prenume_declar"), 75)))
    h.append(_attr("functie_declar", _esc(manual.get("functie_declar"), 75)))
    h.append(_attr("nr_pers", len(det)))
    h.append(_attr("totalPlata_A", calc["totalPlata_A"]))
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<declaratie401 xmlns="%s"%s>' % (NS, "".join(h)))
    for di, d in enumerate(det, 1):
        out.append("  " + _det_xml(di, d))
    out.append("</declaratie401>")
    return "\n".join(out) + "\n"


def _det_xml(di, d):
    tip = _int(d.get("tip_detinator"))
    a = [_attr("id_detinator", di), _attr("Tip_detinator", tip),
         _attr("Den_detinator", _esc(d.get("den_detinator"), 200))]
    if d.get("stat_detinator"):
        a.append(_attr("Stat_detinator", _esc(d.get("stat_detinator"), 2).upper()))
    for k, name, lim in (("localitate_sr", "Localitate_SR", 100), ("strada_sr", "Strada_SR", 200),
                         ("nr_sr", "Nr_SR", 20), ("codp_sr", "Codp_SR", 20),
                         ("cif_sr", "CIF_SR", 30), ("cif_rom", "CIF_rom", 13)):
        if d.get(k):
            a.append(_attr(name, _esc(d.get(k), lim)))
    if tip == 1:
        if d.get("nationalitate"):
            a.append(_attr("Nationalitate", _esc(d.get("nationalitate"), 2).upper()))
        if d.get("data_nasterii"):
            a.append(_attr("Data_nasterii", _esc(d.get("data_nasterii"), 10)))
        if d.get("act_id"):
            a.append(_attr("Act_id", _esc(d.get("act_id"), 50)))
    if d.get("cod_tva"):
        a.append(_attr("codTVA", _esc(d.get("cod_tva"), 30)))
    if tip == 2:
        for k, name, lim in (("den_repr", "Den_repr", 200), ("cif_repr", "CIF_repr", 30),
                             ("adr_repr", "Adr_repr", 200)):
            if d.get(k):
                a.append(_attr(name, _esc(d.get(k), lim)))
    props = d.get("proprietati") or []
    inner = "".join("\n    " + _prop_xml(pi, p) for pi, p in enumerate(props, 1))
    return "<detinator%s>%s\n  </detinator>" % ("".join(a), inner)


def _prop_xml(pi, p):
    tip = _int(p.get("tip_proprietate"))
    a = [_attr("id_proprietate", pi), _attr("Tip_proprietate", tip),
         _attr("Data_D", _esc(p.get("data_d"), 10))]
    for k, name, lim in (("act_nr_d", "Act_nr_D", 50), ("act_emitent_d", "Act_emitent_D", 200)):
        if p.get(k):
            a.append(_attr(name, _esc(p.get(k), lim)))
    if p.get("mod_d") not in (None, ""):
        a.append(_attr("Mod_D", _int(p.get("mod_d"))))
    if p.get("data_i"):
        a.append(_attr("Data_I", _esc(p.get("data_i"), 10)))
        for k, name, lim in (("act_nr_i", "Act_nr_I", 50), ("act_emitent_i", "Act_emitent_I", 200)):
            if p.get(k):
                a.append(_attr(name, _esc(p.get(k), lim)))
        if p.get("mod_i") not in (None, ""):
            a.append(_attr("Mod_I", _int(p.get("mod_i"))))
    for k, name, lim in (("judet_prop", "Judet_prop", 10), ("localitate_prop", "Localitate_prop", 100),
                         ("strada_prop", "Strada_prop", 200), ("nr_prop", "Nr_prop", 20),
                         ("bloc_prop", "Bloc_prop", 20), ("scara_prop", "Scara_prop", 20),
                         ("etaj_prop", "Etaj_prop", 20), ("apart_prop", "Apart_prop", 20)):
        if p.get(k):
            a.append(_attr(name, _esc(p.get(k), lim)))
    if p.get("sector_prop"):
        a.append(_attr("Sector_prop", _int(p.get("sector_prop"))))
    if p.get("suprafata_cladire"):
        a.append(_attr("Suprafata_cladire", _cota(p.get("suprafata_cladire"))))
    if p.get("suprafata_teren"):
        a.append(_attr("Suprafata_teren", _cota(p.get("suprafata_teren"))))
    if str(p.get("destinatie_cladire") or "").strip():
        a.append(_attr("Destinatie_cladire", _esc(p.get("destinatie_cladire"), 100)))
    for i, vi, m in _valori(p):
        a.append(_attr("Val%d" % i, vi))
        a.append(_attr("Moneda%d" % i, m))
    if p.get("alta_val"):
        a.append(_attr("Alta_val", _esc(p.get("alta_val"), 200)))
    tuc = _int(p.get("tip_unic_coprop"))
    a.append(_attr("Tip_unic_coprop", tuc))
    a.append(_attr("Cota_proprietar", _cota(p.get("cota_proprietar"))))
    copro = p.get("coproprietari") or []
    inner = "".join("\n      " + _copro_xml(ci, c) for ci, c in enumerate(copro, 1))
    if inner:
        return "<proprietate%s>%s\n    </proprietate>" % ("".join(a), inner)
    return "<proprietate%s/>" % "".join(a)


def _copro_xml(ci, c):
    a = [_attr("id_coproprietar", ci), _attr("Den_coproprietar", _esc(c.get("den_coproprietar"), 200))]
    if c.get("cif_rom_co"):
        a.append(_attr("CIF_rom_co", _esc(c.get("cif_rom_co"), 13)))
    if c.get("cif_sr_co"):
        a.append(_attr("CIF_SR_co", _esc(c.get("cif_sr_co"), 30)))
    a.append(_attr("Cota_coproprietar", _cota(c.get("cota_coproprietar"))))
    return "<coproprietar%s/>" % "".join(a)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(manual.get("an") or perioada.an)
    luna = int(manual.get("luna") or perioada.luna)
    manual.setdefault("an", an)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D401 nu se poate genera: " + " ".join(er))
    calc = calcul_d401(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat401(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_detinatori=len(manual.get("detinatori") or []),
                      nr_proprietati=calc["nr_proprietati"])
    return xml, res
