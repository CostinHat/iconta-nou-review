"""core/d318.py - D318: Cerere de rambursare a TVA pentru persoane impozabile stabilite in Romania,
pentru TVA achitata in alt stat membru UE (Directiva 2008/9/CE).

Persoana impozabila stabilita in Romania cere rambursarea TVA platita in ALT stat membru UE (statul de
rambursare) pentru achizitii/importuri de bunuri si servicii facute acolo. Se depune electronic la ANAF
(care o transmite statului de rambursare) pana la 30 septembrie a anului urmator perioadei de rambursare.
Declaratie MANUALA / la cerere: aplicatia nu tine registru de facturi straine - facturile, furnizorii UE,
contul bancar de rambursare si semnatarul vin din `manual`.

BAZA LEGALA: art. 302 alin. (2) Cod fiscal (Legea 227/2015, fostul art. 147^2 alin. (2)); Directiva
2008/9/CE (norme de rambursare TVA transfrontaliera); OPANAF 2810/2016 (aproba modelul D318). Perioada de
rambursare: minim un trimestru, maxim un an calendaristic (o cerere anuala are lunaInceput=1, lunaSfarsit=12).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D318Validator.jar, pachet d318validator/v0), CITITA din
bytecode (numele campurilor pe clasele D318 / Applicant / Representative / BusinessDescription /
PurchaseInformation / EuSupplier / GoodsDescriptionP / ImportInformation / Supplier / GoodsDescriptionI /
DocumentCopy) si PROBATA la DUKIntegrator. Radacina XML: <D318> (numele sectiunii radacina din tabelul
DECTag al validatorului - NU <declaratie>, desi namespace-ul contine ...:declaratie:v1). Namespace:
mfp:anaf:dgti:d318:declaratie:v1.

Structura (element -> atribute):
  <D318> (radacina): an, lunaInceput, lunaSfarsit, annual, cui, d_rec, sumaControl, referenceNumber,
      refundingCountryCode, language, ownerName, ownerType, iban, bic, currency, amount, anulPro, prorata,
      declarant, functie.
  <Applicant> (1, solicitantul RO): firstName, street, postCode, telephoneNumber, emailaddress.
  <Representative> (0-1, imputernicit): firstName, street, postCode, telephoneNumber, emailAddress,
      countryCode, issuedBy, representativeID, identificationType.
  <BusinessDescription> (1-n, activitatea): businessActivity (cod NACE), textualDescription, language.
  <PurchaseInformation> (0-n, facturi de achizitie): simplifiedInvoice, sequenceNumber, referenceNumber,
      issuingDate, taxableAmount, currency_ta, vatAmount, currency_va, deductibleVATAmount, currency_dva,
      prorataRate; contine <EuSupplier> (1) + <GoodsDescriptionP> (1-n).
  <EuSupplier>: firstName, street, vatIdentificationNumber, countryCode, telephoneNumber, issuedBy_Vin,
      taxReferenceNumber.
  <GoodsDescriptionP>: code (1-10), subCode, freeText, language.
  <ImportInformation> (0-n, facturi de import): sequenceNumber, referenceNumber, referenceInformation,
      issuingDate, taxableAmount, currency_ta, vatAmount, currency_va, deductibleVATAmount, currency_dva,
      prorataRate; contine <Supplier> (1) + <GoodsDescriptionI> (1-n).
  <Supplier>: firstName, street, countryCode, telephoneNumber.
  <GoodsDescriptionI>: code, subCode, freeText, language.
  <DocumentCopy> (0-n, copii documente): fileType, fileName, fileDescription.

REGULI din validator (probate):
  R5.1: annual=1 => lunaInceput=1 si lunaSfarsit=12. R5.2: annual=0 => lunaInceput<>1 sau lunaSfarsit<>12.
  R9.1: declaratie initiala (d_rec=0) NU poate contine referenceNumber. R9.2: referenceNumber incepe cu 'RO'.
  R9.3: declaratie rectificativa (d_rec=1) trebuie sa contina referenceNumber.
  R50.1/R80.1 (per factura): taxableAmount, vatAmount, deductibleVATAmount au acelasi semn; vatAmount<=taxableAmount;
      issuingDate in perioada de rambursare (an lunaInceput - an lunaSfarsit).
  factura simplificata (simplifiedInvoice=1) => referenceNumber + EuSupplier.vatIdentificationNumber obligatorii.
  import fara referenceNumber => referenceInformation obligatoriu.
  refundingCountryCode / EuSupplier.countryCode din lista tarilor UE (GB scos din 01.03.2021). iban validat structural.

NEPOPULAT deliberat (optionale cu semantica din alt stat membru, nu se ghicesc): prorata/anulPro (numai daca
solicitantul aplica pro-rata), Representative (numai depunere prin imputernicit), DocumentCopy (copii facturi
cerute de unele state), subCode / freeText goods (subcodurile difera per stat de rambursare).

Contract dXXX: pull/erori_generare/calcul_d318/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d318:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_DATA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DATA_RO = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")


def _data(x):
    """Data calendaristica in formatul cerut de validatorul DEC: dd.MM.yyyy.
    Accepta intrare yyyy-mm-dd sau dd.mm.yyyy."""
    s = str(x or "").strip()
    m = _DATA_ISO.match(s)
    if m:
        return "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return s


def _data_ok(x):
    s = str(x or "").strip()
    return bool(_DATA_ISO.match(s) or _DATA_RO.match(s))


def _cif(x):
    """CUI/CIF numeric (fara prefix RO, fara separatori)."""
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _sum2(x):
    """Suma monetara, rotunjire half-up la 2 zecimale (Decimal.quantize), string cu punct zecimal."""
    if x in (None, ""):
        return None
    d = Decimal(str(x).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(d, "f")


def _dec(x):
    if x in (None, ""):
        return Decimal("0")
    return Decimal(str(x).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _attr(name, val):
    return ' %s="%s"' % (name, val)


@dataclass
class Rezultat318:
    an: int
    luna_inceput: int
    luna_sfarsit: int
    tara_rambursare: str = ""
    total_deductibil: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")
    nr_achizitii: int = 0
    nr_importuri: int = 0
    avertismente: list = field(default_factory=list)


def _linii(manual):
    return list(manual.get("achizitii") or []), list(manual.get("importuri") or [])


def calcul_d318(manual):
    """amount = suma TVA deductibila ceruta la rambursare (deductibleVATAmount) din toate facturile de
    achizitie + import (suma din input, half-up la 2 zecimale); implicit = suma calculata, dar poate fi
    data explicit. sumaControl = 0 FIX: validatorul DEC (DUK regula R8) cere ca atributul sumaControl al D318
    sa fie intotdeauna 0 - nu acumuleaza nicio suma de detaliu pentru aceasta declaratie. `total_deductibil`
    e pastrat doar pentru raportare/reconciliere interna."""
    achizitii, importuri = _linii(manual)
    total = Decimal("0")
    for f in achizitii + importuri:
        total += _dec(f.get("deductible_vat", f.get("deductibleVATAmount")))
    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    amount = manual.get("amount")
    amount = _dec(amount) if amount not in (None, "") else total
    return {"sumaControl": 0, "amount": amount, "total_deductibil": total}


def pull(conn, schema, perioada):
    """D318 e MANUALA / la cerere: facturile straine si contul de rambursare nu exista in registrele firmei."""
    return {}


def _b(x):
    return 1 if str(x).strip() in ("1", "true", "True", "da", "Da") else 0


def erori_generare(prof, manual):
    er = []
    try:
        an = int(manual.get("an"))
    except (TypeError, ValueError):
        an = 0
        er.append("Lipsă/invalid an perioada de rambursare (an).")
    try:
        li = int(manual.get("luna_inceput"))
        ls = int(manual.get("luna_sfarsit"))
    except (TypeError, ValueError):
        li = ls = 0
        er.append("Lipsă/invalid luna_inceput / luna_sfarsit.")
    annual = _b(manual.get("annual"))
    if annual == 1 and not (li == 1 and ls == 12):
        er.append("annual=1 cere luna_inceput=1 și luna_sfarsit=12 (R5.1).")
    if annual == 0 and (li == 1 and ls == 12):
        er.append("annual=0 cere luna_inceput<>1 sau luna_sfarsit<>12 (R5.2).")
    if li and ls and not (1 <= li <= ls <= 12):
        er.append("Interval luni invalid (1<=luna_inceput<=luna_sfarsit<=12).")
    if not (2 <= len(_cif(manual.get("cui"))) <= 10):
        er.append("CUI solicitant (cui) invalid.")
    d_rec = _b(manual.get("d_rec"))
    ref = str(manual.get("reference_number") or "").strip()
    if d_rec == 1 and not ref:
        er.append("Declarație rectificativa (d_rec=1) cere reference_number (R9.3).")
    if d_rec == 0 and ref:
        er.append("Declarație initiala (d_rec=0) nu poate contine reference_number (R9.1).")
    if ref and not ref.upper().startswith("RO"):
        er.append("reference_number trebuie să înceapă cu 'RO' (R9.2).")
    if not str(manual.get("refunding_country") or "").strip():
        er.append("Lipsă cod stat de rambursare (refunding_country).")
    if not str(manual.get("iban") or "").strip():
        er.append("Lipsă IBAN cont de rambursare (iban).")
    if not str(manual.get("owner_name") or "").strip():
        er.append("Lipsă titular cont (owner_name, obligatoriu).")
    if str(manual.get("owner_type") or "").strip() not in ("A", "R"):
        er.append("owner_type obligatoriu: 'A' (solicitant) sau 'R' (reprezentant).")
    if not str(manual.get("bic") or "").strip():
        er.append("Lipsă BIC/SWIFT cont de rambursare (bic, obligatoriu).")
    if not str(manual.get("declarant") or "").strip():
        er.append("Lipsă declarant.")
    if not str(manual.get("functie") or "").strip():
        er.append("Lipsă funcție/calitate declarant (funcție, obligatoriu).")
    sol = manual.get("solicitant") or {}
    if not str(sol.get("denumire") or sol.get("firstName") or "").strip():
        er.append("Lipsă denumire solicitant (solicitant.denumire).")
    if not str(sol.get("strada") or sol.get("street") or "").strip():
        er.append("Lipsă adresa solicitant (solicitant.strada, obligatoriu).")
    if not str(sol.get("email") or sol.get("emailaddress") or "").strip():
        er.append("Lipsă email solicitant (solicitant.email, obligatoriu).")
    if not (manual.get("activitati") or manual.get("descriere_activitate")):
        er.append("Lipsă descriere activitate (activități / businessActivity NACE).")
    achizitii, importuri = _linii(manual)
    if not achizitii and not importuri:
        er.append("Cel puțin o factura de achiziție sau de import (achiziții / importuri).")
    for i, f in enumerate(achizitii, 1):
        ta = _dec(f.get("taxable_amount", f.get("taxableAmount")))
        va = _dec(f.get("vat_amount", f.get("vatAmount")))
        dv = _dec(f.get("deductible_vat", f.get("deductibleVATAmount")))
        semne = {(x > 0) - (x < 0) for x in (ta, va, dv) if x != 0}
        if len(semne) > 1:
            er.append("Achiziție %d: taxableAmount/vatAmount/deductibleVATAmount cu semne diferite (R50.1)." % i)
        if abs(va) > abs(ta):
            er.append("Achiziție %d: vatAmount (%s) > taxableAmount (%s)." % (i, va, ta))
        if not str(f.get("reference_number") or "").strip():
            er.append("Achiziție %d: lipsă reference_number (număr factura, obligatoriu - DUK regula R48)." % i)
        fz = f.get("furnizor") or {}
        if not str(fz.get("denumire") or fz.get("firstName") or "").strip():
            er.append("Achiziție %d: lipsă furnizor UE (furnizor.denumire)." % i)
        if not str(fz.get("strada") or fz.get("street") or "").strip():
            er.append("Achiziție %d: lipsă adresa furnizor UE (furnizor.strada)." % i)
        if _b(f.get("simplified_invoice", f.get("simplifiedInvoice"))) == 1:
            if not str(fz.get("vat_id") or fz.get("vatIdentificationNumber") or "").strip():
                er.append("Achiziție %d simplificata: furnizorul cere vatIdentificationNumber." % i)
        if not _data_ok(f.get("issuing_date", f.get("issuingDate"))):
            er.append("Achiziție %d: issuing_date invalid (aștept yyyy-mm-dd sau dd.mm.yyyy)." % i)
    for i, f in enumerate(importuri, 1):
        if not str(f.get("reference_number") or "").strip() and \
                not str(f.get("reference_information", f.get("referenceInformation")) or "").strip():
            er.append("Import %d: fără reference_number cere reference_information." % i)
        if not _data_ok(f.get("issuing_date", f.get("issuingDate"))):
            er.append("Import %d: issuing_date invalid (aștept yyyy-mm-dd sau dd.mm.yyyy)." % i)
    return er


def _goods_xml(tag, bunuri):
    out = []
    for g in (bunuri or []):
        a = _attr("code", _esc(g.get("code")))
        if g.get("subcode", g.get("subCode")) not in (None, ""):
            a += _attr("subCode", _esc(g.get("subcode", g.get("subCode"))))
        if g.get("freetext", g.get("freeText")) not in (None, ""):
            a += _attr("freeText", _esc(g.get("freetext", g.get("freeText")), 500))
        if g.get("limba", g.get("language")) not in (None, ""):
            a += _attr("language", _esc(g.get("limba", g.get("language"))))
        out.append("      <%s%s/>" % (tag, a))
    return out


def _amt_attrs(f):
    """Atribute monetare comune facturilor de achizitie/import."""
    a = ""
    a += _attr("taxableAmount", _sum2(f.get("taxable_amount", f.get("taxableAmount"))) or "0.00")
    a += _attr("currency_ta", _esc(f.get("currency_ta", f.get("currency")) or "EUR"))
    a += _attr("vatAmount", _sum2(f.get("vat_amount", f.get("vatAmount"))) or "0.00")
    a += _attr("currency_va", _esc(f.get("currency_va", f.get("currency")) or "EUR"))
    a += _attr("deductibleVATAmount", _sum2(f.get("deductible_vat", f.get("deductibleVATAmount"))) or "0.00")
    a += _attr("currency_dva", _esc(f.get("currency_dva", f.get("currency")) or "EUR"))
    if f.get("prorata_rate", f.get("prorataRate")) not in (None, ""):
        a += _attr("prorataRate", _sum2(f.get("prorata_rate", f.get("prorataRate"))))
    return a


def build_xml(prof, manual):
    an = int(manual.get("an"))
    li = int(manual.get("luna_inceput"))
    ls = int(manual.get("luna_sfarsit"))
    annual = _b(manual.get("annual"))
    d_rec = _b(manual.get("d_rec"))
    calc = calcul_d318(manual)
    h = ""
    h += _attr("an", an)
    h += _attr("lunaInceput", li)
    h += _attr("lunaSfarsit", ls)
    h += _attr("annual", annual)
    h += _attr("cui", _cif(manual.get("cui")))
    h += _attr("d_rec", d_rec)
    h += _attr("sumaControl", 0)
    if d_rec == 1 and str(manual.get("reference_number") or "").strip():
        h += _attr("referenceNumber", _esc(manual.get("reference_number")))
    h += _attr("refundingCountryCode", _esc(manual.get("refunding_country")))
    h += _attr("language", _esc(manual.get("language") or "RO"))
    if manual.get("owner_name"):
        h += _attr("ownerName", _esc(manual.get("owner_name"), 200))
    if manual.get("owner_type") not in (None, ""):
        h += _attr("ownerType", _esc(manual.get("owner_type")))
    h += _attr("iban", _esc(str(manual.get("iban") or "").replace(" ", "").upper()))
    if manual.get("bic"):
        h += _attr("bic", _esc(str(manual.get("bic") or "").replace(" ", "").upper()))
    h += _attr("currency", _esc(manual.get("currency") or "EUR"))
    h += _attr("amount", _sum2(calc["amount"]))
    if manual.get("anul_prorata", manual.get("anulPro")) not in (None, ""):
        h += _attr("anulPro", int(manual.get("anul_prorata", manual.get("anulPro"))))
    if manual.get("prorata") not in (None, ""):
        h += _attr("prorata", _sum2(manual.get("prorata")))
    h += _attr("declarant", _esc(manual.get("declarant"), 75))
    if manual.get("functie"):
        h += _attr("functie", _esc(manual.get("functie"), 75))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<D318 xmlns="%s"%s>' % (NS, h))

    sol = manual.get("solicitant") or {}
    ap = _attr("firstName", _esc(sol.get("denumire", sol.get("firstName")), 200))
    if sol.get("strada", sol.get("street")):
        ap += _attr("street", _esc(sol.get("strada", sol.get("street")), 200))
    if sol.get("cod_postal", sol.get("postCode")):
        ap += _attr("postCode", _esc(sol.get("cod_postal", sol.get("postCode"))))
    if sol.get("telefon", sol.get("telephoneNumber")):
        ap += _attr("telephoneNumber", _esc(sol.get("telefon", sol.get("telephoneNumber"))))
    if sol.get("email", sol.get("emailaddress")):
        ap += _attr("emailaddress", _esc(sol.get("email", sol.get("emailaddress")), 250))
    lines.append("  <Applicant%s/>" % ap)

    rep = manual.get("reprezentant") or manual.get("representative")
    if rep:
        rp = _attr("firstName", _esc(rep.get("denumire", rep.get("firstName")), 200))
        for k, x in (("street", "strada"), ("postCode", "cod_postal"), ("telephoneNumber", "telefon"),
                     ("emailAddress", "email"), ("countryCode", "tara"), ("issuedBy", "emis_de"),
                     ("representativeID", "id"), ("identificationType", "tip_id")):
            v = rep.get(x, rep.get(k))
            if v not in (None, ""):
                rp += _attr(k, _esc(v))
        lines.append("  <Representative%s/>" % rp)

    activ = manual.get("activitati")
    if not activ:
        da = manual.get("descriere_activitate") or {}
        activ = [da] if da else []
    for a in activ:
        bd = _attr("businessActivity", _esc(a.get("activitate", a.get("businessActivity"))))
        if a.get("descriere", a.get("textualDescription")) not in (None, ""):
            bd += _attr("textualDescription", _esc(a.get("descriere", a.get("textualDescription")), 500))
        if a.get("limba", a.get("language")) not in (None, ""):
            bd += _attr("language", _esc(a.get("limba", a.get("language"))))
        lines.append("  <BusinessDescription%s/>" % bd)

    achizitii, importuri = _linii(manual)
    for idx, f in enumerate(achizitii, 1):
        pa = _attr("simplifiedInvoice", _b(f.get("simplified_invoice", f.get("simplifiedInvoice"))))
        pa += _attr("sequenceNumber", f.get("sequence", f.get("sequenceNumber", idx)))
        if str(f.get("reference_number") or "").strip():
            pa += _attr("referenceNumber", _esc(f.get("reference_number")))
        pa += _attr("issuingDate", _data(f.get("issuing_date", f.get("issuingDate"))))
        pa += _amt_attrs(f)
        lines.append("  <PurchaseInformation%s>" % pa)
        fz = f.get("furnizor") or {}
        es = _attr("firstName", _esc(fz.get("denumire", fz.get("firstName")), 200))
        if fz.get("strada", fz.get("street")):
            es += _attr("street", _esc(fz.get("strada", fz.get("street")), 200))
        if str(fz.get("vat_id", fz.get("vatIdentificationNumber")) or "").strip():
            es += _attr("vatIdentificationNumber", _esc(fz.get("vat_id", fz.get("vatIdentificationNumber"))))
        es += _attr("countryCode", _esc(fz.get("tara", fz.get("countryCode")) or manual.get("refunding_country")))
        if fz.get("telefon", fz.get("telephoneNumber")):
            es += _attr("telephoneNumber", _esc(fz.get("telefon", fz.get("telephoneNumber"))))
        if fz.get("issued_by_vin", fz.get("issuedBy_Vin")) not in (None, ""):
            es += _attr("issuedBy_Vin", _esc(fz.get("issued_by_vin", fz.get("issuedBy_Vin"))))
        if fz.get("tax_ref", fz.get("taxReferenceNumber")) not in (None, ""):
            es += _attr("taxReferenceNumber", _esc(fz.get("tax_ref", fz.get("taxReferenceNumber"))))
        lines.append("    <EuSupplier%s/>" % es)
        lines += _goods_xml("GoodsDescriptionP", f.get("bunuri", f.get("goods")))
        lines.append("  </PurchaseInformation>")

    for idx, f in enumerate(importuri, len(achizitii) + 1):
        ia = _attr("sequenceNumber", f.get("sequence", f.get("sequenceNumber", idx)))
        if str(f.get("reference_number") or "").strip():
            ia += _attr("referenceNumber", _esc(f.get("reference_number")))
        if str(f.get("reference_information", f.get("referenceInformation")) or "").strip():
            ia += _attr("referenceInformation", _esc(f.get("reference_information", f.get("referenceInformation"))))
        ia += _attr("issuingDate", _data(f.get("issuing_date", f.get("issuingDate"))))
        ia += _amt_attrs(f)
        lines.append("  <ImportInformation%s>" % ia)
        fz = f.get("furnizor") or {}
        sp = _attr("firstName", _esc(fz.get("denumire", fz.get("firstName")), 200))
        if fz.get("strada", fz.get("street")):
            sp += _attr("street", _esc(fz.get("strada", fz.get("street")), 200))
        sp += _attr("countryCode", _esc(fz.get("tara", fz.get("countryCode")) or manual.get("refunding_country")))
        if fz.get("telefon", fz.get("telephoneNumber")):
            sp += _attr("telephoneNumber", _esc(fz.get("telefon", fz.get("telephoneNumber"))))
        lines.append("    <Supplier%s/>" % sp)
        lines += _goods_xml("GoodsDescriptionI", f.get("bunuri", f.get("goods")))
        lines.append("  </ImportInformation>")

    for doc in (manual.get("documente") or manual.get("documents") or []):
        dc = _attr("fileType", _esc(doc.get("file_type", doc.get("fileType"))))
        dc += _attr("fileName", _esc(doc.get("file_name", doc.get("fileName"))))
        if doc.get("file_description", doc.get("fileDescription")) not in (None, ""):
            dc += _attr("fileDescription", _esc(doc.get("file_description", doc.get("fileDescription")), 500))
        lines.append("  <DocumentCopy%s/>" % dc)

    lines.append("</D318>")
    return "\n".join(lines) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    manual.setdefault("an", getattr(perioada, "an", None))
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D318 nu se poate genera: " + " ".join(er))
    calc = calcul_d318(manual)
    achizitii, importuri = _linii(manual)
    xml = build_xml(prof, manual)
    res = Rezultat318(
        an=int(manual.get("an")),
        luna_inceput=int(manual.get("luna_inceput")),
        luna_sfarsit=int(manual.get("luna_sfarsit")),
        tara_rambursare=str(manual.get("refunding_country") or ""),
        total_deductibil=calc["total_deductibil"],
        amount=calc["amount"],
        nr_achizitii=len(achizitii),
        nr_importuri=len(importuri),
    )
    return xml, res
