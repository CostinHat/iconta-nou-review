"""Consumator pentru rularea dedicată: E|C XML DIRECTOR_CAPTURI RC_PYTEST."""
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET

def verifica_png(cale, dimensiuni):
    with cale.open("rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Semnătură PNG invalidă: {cale.name}")
        tipuri = []
        while True:
            raw = f.read(8)
            if len(raw) != 8:
                raise ValueError(f"Structură PNG incompletă: {cale.name}")
            n, tip = struct.unpack(">I4s", raw)
            continut, crc = f.read(n), f.read(4)
            if len(continut) != n or crc != struct.pack(">I", zlib.crc32(tip+continut)):
                raise ValueError(f"CRC/lungime PNG invalidă: {cale.name}")
            if not tipuri and (tip != b"IHDR" or n != 13 or struct.unpack(">II",continut[:8]) != dimensiuni):
                raise ValueError(f"Dimensiuni PNG neașteptate: {cale.name}")
            tipuri.append(tip)
            if tip == b"IEND":
                if n or b"IDAT" not in tipuri or f.read(1):
                    raise ValueError(f"Final PNG invalid: {cale.name}")
                return



def incarca_test():
    modul = "e2e_ferestre_17_5_Q6"
    aici = Path(__file__).resolve().parent
    candidati = (aici / (modul + ".py"), aici.parent / "pachet" / (modul + ".py"),
                 Path.cwd() / "frontend_test" / "e2e" / (modul + ".py"))
    source = next((c for c in candidati if c.is_file()), None)
    if source is None:
        raise FileNotFoundError(modul + ".py lipsește lângă cititor, în ../pachet/ și în frontend_test/e2e/ din directorul curent")
    spec = importlib.util.spec_from_file_location(modul, source)
    e2e = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(e2e)
    return e2e


def verifica(faza, xml, capturi, rc):
    e2e = incarca_test()
    if faza not in ("E", "C"):
        raise ValueError("Faza trebuie să fie E sau C")
    root = ET.parse(xml).getroot()
    cases = root.findall(".//testcase")
    if len(cases) != 1 or cases[0].get("name") != "test_ferestre_17_5_Q6" or cases[0].get("classname", "").split(".")[-1] != e2e.__name__:
        raise ValueError("Se cere un singur nod dedicat Q6")
    case = cases[0]
    if case.find("skipped") is not None or case.find("error") is not None:
        raise ValueError("Nod neexecutat ori eroare în rulare")
    dest = Path(capturi) / "17_5_Q6"
    masuri = json.loads((dest / "masuri.json").read_text())
    if json.loads((dest / "erori.json").read_text()) or set(masuri) != {"e.1","e.2"}:
        raise ValueError("Martor lipsă ori eroare de parcurs")
    observate = {}
    for ident, dims in (("e.1",(603,590)),("e.2",(1366,768))):
        verifica_png(dest / (ident+".png"), dims)
        observate[ident] = e2e.rezultat(ident,masuri[ident])
        print(ident, "trece" if observate[ident] else "pica")
    vrea_verde = faza == "C"
    if rc != (0 if vrea_verde else 1) or (case.find("failure") is not None) != (not vrea_verde):
        raise ValueError("JUnit și rc nu corespund fazei")
    if not vrea_verde:
        esec = case.find("failure")
        detaliu = (esec.get("message","") + " " + (esec.text or "")).lower()
        if "assert" not in detaliu:
            raise ValueError("Eroarea de rulare nu este aserțiunea de produs a nodului")
    if any(x != vrea_verde for x in observate.values()):
        raise ValueError("Contractul de bază/candidat diferă de observațiile efective")
    return observate


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    verifica(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))
