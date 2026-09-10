# -*- coding: utf-8 -*-
"""Import Raport Z din fisier AMEF (p7b sau XML) - OPANAF 146/2018, anexa 2, sectiunea II.7.
Structura verificata la sursa (static.anaf.ro/OPANAF_146_2018.pdf):
<msj idM><rB idR nrB totB totTva totTaxe totNet ... monRef>
  <pl tipP valPl monPl/>  (nomenclator: 1=Card, 3=Numerar, 4=Tichete masa, 5=Bonuri, 6=Voucher, 7=Credit, 8=Moderne, 9=Alte)
  <coteZ cota valOp tva/> (per cota TVA: valoare operatiuni + TVA)
  <av data/>
</rB></msj>
p7b = XML semnat PKCS#7 (SHA-256/RSA) cu continut atasat - XML-ul e plaintext in interior."""
import re
import subprocess
import xml.etree.ElementTree as ET
from decimal import Decimal

TIP_PLATA = {1: "card", 3: "numerar", 4: "tichete_masa", 5: "bonuri_valorice",
             6: "voucher", 7: "credit", 8: "moderne", 9: "alte"}


def extrage_xml(continut: bytes) -> str:
    """Extrage XML-ul dintr-un fisier AMEF: XML curat, sau p7b (PKCS#7 attached)."""
    text = continut.decode("utf-8", errors="ignore")
    if text.lstrip().startswith("<?xml") or text.lstrip().startswith("<msj"):
        return text
    # p7b: incearca openssl cms (DER apoi PEM), fara verificarea lantului (certificat AMEF)
    for inform in ("DER", "PEM"):
        try:
            r = subprocess.run(
                ["openssl", "cms", "-verify", "-noverify", "-inform", inform],
                input=continut, capture_output=True, timeout=15)
            if r.returncode == 0 and b"<msj" in r.stdout:
                return r.stdout.decode("utf-8", errors="ignore")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        try:
            r = subprocess.run(
                ["openssl", "smime", "-verify", "-noverify", "-inform", inform],
                input=continut, capture_output=True, timeout=15)
            if r.returncode == 0 and b"<msj" in r.stdout:
                return r.stdout.decode("utf-8", errors="ignore")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    # fallback: XML-ul atasat e plaintext in structura ASN.1 - extragere directa
    m = re.search(rb"<\?xml.*?</msj>|<msj.*?</msj>", continut, re.S)
    if m:
        return m.group(0).decode("utf-8", errors="ignore")
    raise ValueError("Nu am găsit niciun raport Z în fișier — nici într-un p7b semnat, nici "
                     "ca XML simplu. Încarcă fișierul exportat de casa de marcat.")


def parseaza_raport_z(xml_text: str) -> dict:
    """Parseaza sectiunea II.7 (rB). Intoarce datele necesare notei contabile."""
    root = ET.fromstring(xml_text)
    rb = root.find("rB") if root.tag != "rB" else root
    if rb is None:
        raise ValueError("Fișierul conține un XML, dar nu un raport Z de uz general: lipsește "
                         "eticheta «rB» cerută de OPANAF 146/2018 secțiunea II.7.")
    a = rb.attrib
    idr = a.get("idR", "")
    # idR: 10 NUI + AAAALLZZHHMMSS + 4 nr raport
    data = None
    nui, nr_raport = None, None
    if len(idr) >= 28:
        nui = idr[:10]
        data = f"{idr[10:14]}-{idr[14:16]}-{idr[16:18]}"
        nr_raport = idr[24:28]
    cote = [{"cota": c.attrib.get("cota"),
             "valoare": Decimal(c.attrib.get("valOp", "0")),
             "tva": Decimal(c.attrib.get("tva", "0"))}
            for c in rb.findall("coteZ")]
    plati = [{"tip": TIP_PLATA.get(int(p.attrib.get("tipP", "9")), "alte"),
              "suma": Decimal(p.attrib.get("valPl", "0"))}
             for p in rb.findall("pl")]
    return {
        "nui": nui, "data": data, "nr_raport": nr_raport,
        "total": Decimal(a.get("totB", "0")),
        "total_tva": Decimal(a.get("totTva", "0")),
        "scutite": Decimal(a.get("totNet", "0")),
        "alte_taxe": Decimal(a.get("totTaxe", "0")),
        "nr_bonuri": int(a.get("nrB", "0")),
        "cote": cote, "plati": plati,
    }


def _test():
    # XML construit strict dupa spec (sectiunea II.7): 2 cote, plati card+numerar
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<msj idM="8000000001202607041930120042">'
           '<rB idR="8000000001202607041930120042" nrAv="0" nrB="35" totB="2450.00"'
           ' nrBC="2" totBC="300.00" nrA="0" totA="0" nrR="0" totR="0" nrM="0" totM="0"'
           ' totTva="405.37" totTvaC="0" totTaxes="0" totTaxe="0" totNet="0"'
           ' sume_serv_in="200.00" sume_serv_out="150.00" monRef="RON">'
           '<pl tipP="1" valPl="1450.00" monPl="RON"/>'
           '<pl tipP="3" valPl="1000.00" monPl="RON"/>'
           '<coteZ cota="21" valOp="2100.00" tva="364.46"/>'
           '<coteZ cota="11" valOp="350.00" tva="34.68"/>'
           '</rB></msj>')
    r = parseaza_raport_z(xml)
    # Totalul asteptat se DERIVA din XML-ul de mai sus, nu se copiaza ca literal: un auto-test care
    # compara parserul cu un numar scris de mana verifica mai putin decat unul care il compara cu
    # propria intrare — iar la o schimbare a datelor de proba, literalul ar minti in tacere.
    _total_xml = sum(Decimal(v) for v in re.findall(r'valOp="([0-9.]+)"', xml))
    _plati_xml = sum(Decimal(v) for v in re.findall(r'valPl="([0-9.]+)"', xml))
    assert r["nui"] == "8000000001"
    assert r["data"] == "2026-07-04"
    assert r["nr_raport"] == "0042"
    assert r["total"] == _total_xml
    assert len(r["cote"]) == 2 and r["cote"][0]["cota"] == "21"
    assert {p["tip"] for p in r["plati"]} == {"card", "numerar"}
    assert sum(p["suma"] for p in r["plati"]) == _plati_xml
    # extrage_xml pe XML curat
    assert "<msj" in extrage_xml(xml.encode())
    # fallback regex pe p7b simulat (XML atasat in binar)
    fals_p7b = b"\x30\x82\x01\x00" + xml.encode() + b"\x00\x01"
    assert "<msj" in extrage_xml(fals_p7b)
    print("TESTE OK")


if __name__ == "__main__":
    _test()
