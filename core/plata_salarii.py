# -*- coding: utf-8 -*-
"""
core/plata_salarii.py — [F134 step 2] fisierul de plata a salariilor pe card.

Format: SEPA / ISO 20022 pain.001.001.03 (CustomerCreditTransferInitiation) - decizie STOP
20.07.2026 (DECIZII), ales fata de formatele proprietare pe banca fiindca e standard PUBLICAT
verificabil la sursa (XSD in sepa_surse/pain.001.001.03.xsd, de pe iso20022.org) si acceptat de
importul corporate al bancilor RO pentru plati RON multiple - un singur format, nu N parsere.

SUMA platita pe card = NET-ul cash al salariatului (ce ajunge in contul lui). Tichetele (masa/
vacanta/cadou) merg pe CARD DE BENEFICII SEPARAT (alt emitent), NU in acest transfer bancar -> nu
se aduna aici. Sursa net-ului = acelasi stat_plata care alimenteaza D112 (o singura cifra).

Un IBAN gresit trimite banii altcuiva: fisierul se genereaza DOAR pentru salariatii cu IBAN valid
(mod-97, verificat la introducere); cei fara IBAN sunt EXCLUSI si RAPORTATI (meta['fara_iban']),
nu platiti tacit. Firma fara IBAN in firma_profil -> eroare clara, nu fisier gol.

GARANTIA: XML-ul generat se valideaza pe XSD-ul oficial INAINTE de a fi intors (valideaza=True).
Daca nu trece schema, refuzam sa intoarcem un fisier pe care banca l-ar respinge.
"""
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import os
import re
from lxml import etree

from core import stat_plata_api as _sp
from core import salariati_api as _sa

MODUL = "plata_salarii"
NS = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
XSD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "sepa_surse", "pain.001.001.03.xsd")

# translit charset SEPA (Latin restrans): diacriticele romanesti -> ASCII de baza. Banca respinge
# caractere in afara setului SEPA; numele se transliterează, nu se trimit cu ă/î/ș/ț.
_TRANS = {
    "ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t",
    "Ă": "A", "Â": "A", "Î": "I", "Ș": "S", "Ş": "S", "Ț": "T", "Ţ": "T",
}


def _sepa_text(s, maxlen=140):
    """Curata un text pentru charset-ul SEPA: translit diacritice, pastreaza doar caractere permise
    (litere/cifre/ /-?:().,'+), colapseaza spatiile, trunchiaza la maxlen."""
    s = "".join(_TRANS.get(c, c) for c in str(s or ""))
    s = re.sub(r"[^A-Za-z0-9/\-?:().,'+ ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:maxlen] or "NA"


def _q2(v):
    """Suma cu 2 zecimale, punct zecimal, rotunjire aritmetica (HALF_UP)."""
    return str(Decimal(str(v or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _profil_firma(conn, schema):
    """(nume, iban) din firma_profil (id=1). iban gol -> None (blocant)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT nume, iban FROM {schema}.firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return None, None
    return r[0], (r[1] or "").strip()


def genereaza_pain001(conn, schema, an, luna, data_executie=None, acum=None, nume_firma_fallback=""):
    """Genereaza fisierul SEPA pain.001.001.03 de plata a salariilor NET pe luna (an, luna).
    Intoarce (xml_bytes, meta). meta = {nr_plati, total, fara_iban:[nume], fisier}.
    Ridica ValueError daca firma nu are IBAN sau daca niciun salariat nu are IBAN valid."""
    acum = acum or datetime.now()
    data_executie = data_executie or date.today()

    nume_firma, iban_firma = _profil_firma(conn, schema)
    nume_firma = nume_firma or nume_firma_fallback
    if not iban_firma:
        raise ValueError("Firma nu are IBAN completat — e necesar ca ordonator al plății. "
                         "Completează-l la Date firmă.")
    if not _sa.iban_valid(iban_firma):
        raise ValueError("IBAN-ul firmei e invalid — corectează-l la Date firmă înainte de a "
                         "genera fișierul de plată.")

    stat = _sp.stat_plata(conn, schema, an, luna)
    plati, fara_iban = [], []
    for s in stat:
        net = Decimal(str(s.get("net") or 0))
        if net <= 0:
            continue  # fara net cash de platit (ex. luna integral in CM)
        iban = (s.get("iban") or "").strip()
        if not iban or not _sa.iban_valid(iban):
            fara_iban.append(s.get("nume") or ("salariat %s" % s.get("id")))
            continue
        plati.append({"id": s["id"], "nume": s.get("nume") or "", "iban": iban, "net": net})

    if not plati:
        raise ValueError("niciun salariat cu IBAN valid si net > 0 pe luna aceasta - nimic de platit "
                         "(salariati fara IBAN: %s)" % (", ".join(fara_iban) or "-"))

    total = sum(p["net"] for p in plati)
    nr = len(plati)
    stamp = acum.strftime("%Y%m%d%H%M%S")
    msg_id = ("SAL%02d%04d-%s" % (luna, an, stamp))[:35]

    E = lambda tag: etree.SubElement  # noqa (helper local)
    doc = etree.Element("{%s}Document" % NS, nsmap={None: NS})
    cti = etree.SubElement(doc, "{%s}CstmrCdtTrfInitn" % NS)

    # --- GrpHdr ---
    gh = etree.SubElement(cti, "{%s}GrpHdr" % NS)
    etree.SubElement(gh, "{%s}MsgId" % NS).text = msg_id
    etree.SubElement(gh, "{%s}CreDtTm" % NS).text = acum.strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(gh, "{%s}NbOfTxs" % NS).text = str(nr)
    etree.SubElement(gh, "{%s}CtrlSum" % NS).text = _q2(total)
    ip = etree.SubElement(gh, "{%s}InitgPty" % NS)
    etree.SubElement(ip, "{%s}Nm" % NS).text = _sepa_text(nume_firma)

    # --- PmtInf (un singur bloc, toate platile) ---
    pi = etree.SubElement(cti, "{%s}PmtInf" % NS)
    etree.SubElement(pi, "{%s}PmtInfId" % NS).text = msg_id
    etree.SubElement(pi, "{%s}PmtMtd" % NS).text = "TRF"
    etree.SubElement(pi, "{%s}NbOfTxs" % NS).text = str(nr)
    etree.SubElement(pi, "{%s}CtrlSum" % NS).text = _q2(total)
    etree.SubElement(pi, "{%s}ReqdExctnDt" % NS).text = data_executie.strftime("%Y-%m-%d")
    dbtr = etree.SubElement(pi, "{%s}Dbtr" % NS)
    etree.SubElement(dbtr, "{%s}Nm" % NS).text = _sepa_text(nume_firma)
    dbtr_acct = etree.SubElement(pi, "{%s}DbtrAcct" % NS)
    etree.SubElement(etree.SubElement(dbtr_acct, "{%s}Id" % NS), "{%s}IBAN" % NS).text = iban_firma
    dbtr_agt = etree.SubElement(pi, "{%s}DbtrAgt" % NS)
    othr = etree.SubElement(etree.SubElement(dbtr_agt, "{%s}FinInstnId" % NS), "{%s}Othr" % NS)
    etree.SubElement(othr, "{%s}Id" % NS).text = "NOTPROVIDED"  # IBAN-only (banca deduce din IBAN)
    etree.SubElement(pi, "{%s}ChrgBr" % NS).text = "SLEV"

    for p in plati:
        tx = etree.SubElement(pi, "{%s}CdtTrfTxInf" % NS)
        pmtid = etree.SubElement(tx, "{%s}PmtId" % NS)
        etree.SubElement(pmtid, "{%s}EndToEndId" % NS).text = ("SAL%02d%04d-%s" % (luna, an, p["id"]))[:35]
        amt = etree.SubElement(tx, "{%s}Amt" % NS)
        instd = etree.SubElement(amt, "{%s}InstdAmt" % NS, Ccy="RON")
        instd.text = _q2(p["net"])
        cdtr = etree.SubElement(tx, "{%s}Cdtr" % NS)
        etree.SubElement(cdtr, "{%s}Nm" % NS).text = _sepa_text(p["nume"])
        cdtr_acct = etree.SubElement(tx, "{%s}CdtrAcct" % NS)
        etree.SubElement(etree.SubElement(cdtr_acct, "{%s}Id" % NS), "{%s}IBAN" % NS).text = p["iban"]
        rmt = etree.SubElement(tx, "{%s}RmtInf" % NS)
        etree.SubElement(rmt, "{%s}Ustrd" % NS).text = _sepa_text("Salariu %02d/%04d" % (luna, an), 140)

    xml = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", pretty_print=True)

    # GARANTIA: validare pe XSD-ul oficial inainte de a intoarce fisierul
    schema_xsd = etree.XMLSchema(etree.parse(XSD_PATH))
    if not schema_xsd.validate(etree.fromstring(xml)):
        raise ValueError("XML pain.001 generat NU trece XSD-ul oficial: %s" % schema_xsd.error_log)

    meta = {
        "nr_plati": nr,
        "total": float(total),
        "fara_iban": fara_iban,
        "fisier": "plata_salarii_%04d_%02d.xml" % (an, luna),
    }
    return xml, meta
