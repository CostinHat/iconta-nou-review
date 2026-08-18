"""core/d207.py — D207: Declaratie informativa privind impozitul retinut la sursa pe beneficiari nerezidenti.

Platitorul de venit (firma) declara, pe fiecare beneficiar nerezident, venitul platit si impozitul retinut,
pe tipuri de venit. Declaratie MANUALA - lista de beneficiari vine din input (aplicatia nu are inca registru
de plati catre nerezidenti).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D207Validator.jar, arbitrul peste anexe). In vigoare = v2
(pachet d207validator/v1; tabelul Validator.class: 2021-12+ -> index 1). Campurile citite din bytecode:
  Declaratie207: cui, den, adresa, nume_decl/prenume_decl/functie_decl, luna, an, d_rec, totalPlata_A.
  Sect_II (1-n, unic pe tip_venit): tip_venit, nrben, Tbaza, Tscutit, Timp, Timps.
  Benef (1-n): id_inreg, tip_venit1, den1, Stat_R, cifR, cifS, baza1, imp1, imps1, Act_N.
Timps/imps1 OBLIGATORII - confirmate de validator (mesaj "atributul trebuie sa existe"); extragerea din
bytecode le ratase, dar mesajele de eroare ale validatorului sunt sursa definitiva (arbitrul).

SEMANTICA/REGULI din ACT (anaf_surse/structura_D207_2025 + OPANAF_179_2022_D207, in corpus):
  - tip_venit: cod C(2) din nomenclatorul naturii veniturilor (01=dividende art.223(1)a, 02=dobanzi, 03=redevente, ...
    22=dividende cf. conventii; 12-21=venituri SCUTITE). Codul se ALEGE de contabil din nomenclator - modulul NU-l
    ghiceste, il primeste ca input; valideaza doar ca e in (01..25, 26; fara 09).
  - impozabil vs scutit: tip_venit1 in 01-11 si 22 -> impozabil (baza -> Tbaza, imp1>=0);
    tip_venit1 in 12-21 -> scutit (baza -> Tscutit, imp1=0).
  - Sect_II per tip_venit: nrben=nr beneficiari, Tbaza=suma(baza1 impozabile), Tscutit=suma(baza1 scutite), Timp=suma(imp1).
  - totalPlata_A = suma pe toate Sect_II de (nrben + Tscutit + Tbaza + Timp + Timps).  (suma de control, struct rd.16)
  - Act_N in (1,2,3) = actul normativ (Cod fiscal / conventie / directiva) - primit ca input, din nomenclatorul actului.

Contract dXXX: pull/erori_generare/calcul_d207/build_xml/genereaza(conn, schema, perioada).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d207:declaratie:v2"
_NEDIGIT = re.compile(r"\D")

# tip_venit valide (nomenclator, struct): 01..25, 26; fara 09
_TIP_VALIDE = {"%02d" % n for n in range(1, 26)} | {"26"}
_TIP_VALIDE.discard("09")
# impozabile (baza -> Tbaza, imp permis): 01..11 si 22; scutite (baza -> Tscutit, imp=0): 12..21
_TIP_SCUTIT = {"%02d" % n for n in range(12, 22)}


def _i(x):
    """Suma in bani -> intreg cu rotunjire ARITMETICA (half-up), nu bancara (ANAF cere half-up)."""
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, "D207").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat207:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_beneficiari: int = 0
    avertismente: list = field(default_factory=list)


def _sectiuni(benef):
    """Grupeaza beneficiarii pe tip_venit -> Sect_II cu agregate (struct rd.17-23)."""
    sec = {}
    for b in benef:
        tv = str(b.get("tip_venit") or "").zfill(2)
        s = sec.setdefault(tv, {"tip_venit": tv, "nrben": 0, "Tbaza": 0, "Tscutit": 0, "Timp": 0, "Timps": 0})
        s["nrben"] += 1
        baza = _i(b.get("baza"))
        if tv in _TIP_SCUTIT:
            s["Tscutit"] += baza
        else:
            s["Tbaza"] += baza
            s["Timp"] += _i(b.get("imp"))
            s["Timps"] += _i(b.get("imp_suportat"))
    return [sec[k] for k in sorted(sec)]


def calcul_d207(manual):
    """totalPlata_A = suma pe Sect_II de (nrben + Tscutit + Tbaza + Timp + Timps) (struct rd.16)."""
    sec = _sectiuni(manual.get("beneficiari") or [])
    total = sum(s["nrben"] + s["Tscutit"] + s["Tbaza"] + s["Timp"] + s["Timps"] for s in sec)
    return {"sectiuni": sec, "totalPlata_A": total}


def pull(conn, schema, perioada):
    """Header firmei platitoare. Beneficiarii nerezidenti vin din `manual` (nu exista registru de plati)."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"den": r[0], "cui": r[1], "adresa": r[2], "declarant_nume": r[3],
            "declarant_prenume": r[4], "declarant_functie": r[5], "telefon": r[6], "email": r[7]}


def erori_generare(prof, manual):
    # Mesaje in limba CONTABILULUI (ce lipseste + unde se corecteaza), fara nume interne de camp/atribut XML.
    _ET_DECL = {"declarant_nume": "numele declarantului", "declarant_prenume": "prenumele declarantului",
                "declarant_functie": "funcția declarantului"}
    er = []
    if not _cif(prof.get("cui")):
        er.append("Lipsește codul fiscal (CUI) al firmei plătitoare de venit — completează-l în Date firmă.")
    if not (prof.get("den")):
        er.append("Lipsește denumirea firmei plătitoare de venit — completeaz-o în Date firmă.")
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("Completează %s (obligatoriu) în Date firmă." % _ET_DECL[c])
    benef = manual.get("beneficiari") or []
    if not benef:
        er.append("D207 nu are ce genera: adaugă în formular cel puțin un beneficiar nerezident căruia i-ai "
                  "plătit venituri cu reținere la sursă (dividende, dobânzi, redevențe etc.).")
    for i, b in enumerate(benef, 1):
        tv = str(b.get("tip_venit") or "").zfill(2)
        if tv not in _TIP_VALIDE:
            er.append("Beneficiarul %d: alege tipul de venit plătit din listă (dividende, dobânzi, redevențe, "
                      "servicii, premii etc.)." % i)
        if not str(b.get("den") or "").strip():
            er.append("Beneficiarul %d: completează numele sau denumirea beneficiarului nerezident." % i)
        if not str(b.get("stat") or "").strip():
            er.append("Beneficiarul %d: completează statul de rezidență (codul de țară din 2 litere)." % i)
        if not (_cif(b.get("cif_ro")) or str(b.get("cif_strain") or "").strip()):
            er.append("Beneficiarul %d: completează codul de identificare fiscală — cel din România sau cel "
                      "din străinătate (măcar unul)." % i)
        if str(b.get("act_n") or "") not in ("1", "2", "3"):
            er.append("Beneficiarul %d: alege actul normativ aplicabil (Codul fiscal, convenția de evitare a dublei "
                      "impuneri sau acordul internațional)." % i)
        if tv in _TIP_SCUTIT and _i(b.get("imp")):
            er.append("Beneficiarul %d: venitul este scutit de impozit — impozitul reținut trebuie să fie 0." % i)
    return er


def build_xml(prof, an, luna, manual, calc):
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie"), 75))
    a.append('cui="%s"' % _cif(prof.get("cui")))
    a.append('den="%s"' % _esc(prof.get("den"), 200))
    a.append('adresa="%s"' % _esc(prof.get("adresa"), 200))
    if prof.get("telefon"):
        a.append('telefon="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('mail="%s"' % _esc(prof.get("email"), 200))
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<declaratie207 xmlns="%s" %s>' % (NS, " ".join(a))]
    # Sectiunea II - agregate pe tip_venit
    for s in calc["sectiuni"]:
        linii.append('  <sect_II tip_venit="%s" nrben="%d" Tbaza="%d" Tscutit="%d" Timp="%d" Timps="%d"/>'
                     % (s["tip_venit"], s["nrben"], s["Tbaza"], s["Tscutit"], s["Timp"], s["Timps"]))
    # Beneficiari
    for idx, b in enumerate(manual.get("beneficiari") or [], 1):
        tv = str(b.get("tip_venit") or "").zfill(2)
        baza = _i(b.get("baza"))
        imp = 0 if tv in _TIP_SCUTIT else _i(b.get("imp"))
        imps = 0 if tv in _TIP_SCUTIT else _i(b.get("imp_suportat"))
        ba = ['id_inreg="%d"' % idx, 'tip_venit1="%s"' % tv,
              'den1="%s"' % _esc(b.get("den"), 100), 'Stat_R="%s"' % _esc(b.get("stat"), 2),
              'baza1="%d"' % baza, 'imp1="%d"' % imp, 'imps1="%d"' % imps, 'Act_N="%s"' % _esc(b.get("act_n"), 1)]
        if _cif(b.get("cif_ro")):
            ba.append('cifR="%s"' % _cif(b.get("cif_ro")))
        if b.get("cif_strain"):
            ba.append('cifS="%s"' % _esc(b.get("cif_strain"), 20))
        linii.append('  <benef %s/>' % " ".join(ba))
    linii.append('</declaratie207>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D207 nu se poate genera: " + " ".join(er))
    calc = calcul_d207(manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat207(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_beneficiari=len(manual.get("beneficiari") or []))
    return xml, res
