"""Cititor R pentru XML, măsuri și capturi ale aceluiași nod pytest."""
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET

def png_valid(p, dimensiuni):
    # Structura, CRC-urile și fluxul de pixeli. Schema lotului și dimensiunile așteptate țin de cititor.
    try:
        with open(p, "rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                return False
            date = bytearray()
            antet = None
            while True:
                n, tip = struct.unpack(">I4s", f.read(8))
                corp = f.read(n)
                if len(corp) != n or f.read(4) != struct.pack(">I", zlib.crc32(tip + corp)):
                    return False
                if antet is None:
                    if tip != b"IHDR" or n != 13:
                        return False
                    antet = struct.unpack(">IIBBBBB", corp)
                elif tip == b"IHDR":
                    return False
                elif tip == b"IDAT":
                    date.extend(corp)
                elif tip == b"IEND":
                    if n or f.read(1) or not date:
                        return False
                    break
        w, h, biti, culoare, compresie, filtru, intercalare = antet
        canale = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
        adancimi = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
        if (w,h) != dimensiuni or biti not in adancimi.get(culoare, ()) or compresie or filtru or intercalare not in (0, 1):
            return False
        treceri = ((0, 0, 1, 1),) if not intercalare else (
            (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
            (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))
        flux = zlib.decompressobj()
        pixeli = flux.decompress(date)
        if not flux.eof or flux.unused_data:
            return False
        pozitie = 0
        for x, y, dx, dy in treceri:
            if x >= w or y >= h:
                continue
            coloane, randuri = (w - x + dx - 1) // dx, (h - y + dy - 1) // dy
            lungime = 1 + (coloane * biti * canale[culoare] + 7) // 8
            sfarsit = pozitie + lungime * randuri
            if sfarsit > len(pixeli) or any(f > 4 for f in pixeli[pozitie:sfarsit:lungime]):
                return False
            pozitie = sfarsit
        return pozitie == len(pixeli)
    except (OSError, ValueError, struct.error, zlib.error):
        return False


def verifica_png(cale, dimensiuni):
    if not png_valid(cale, dimensiuni):
        raise ValueError(f"Captură PNG invalidă sau absentă: {cale.name}")


def citeste(faza, xml, capturi, rc):
    if faza not in ("E","C"):
        raise ValueError("faza trebuie să fie E sau C")
    director = Path(__file__).resolve().parent
    p = director / "e2e_ajutor_17_5_R2.py"
    if not p.is_file() and director.parts[-3:] == ("docs","dovezi","17_5_R2"):
        p = director.parents[2] / "frontend_test/e2e" / p.name
    spec=importlib.util.spec_from_file_location("probe_ajutor_R",p)
    test=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test)
    cazuri=ET.parse(xml).getroot().findall(".//testcase")
    if len(cazuri)!=1 or cazuri[0].get("name")!="test_ajutor_17_5_R2" or cazuri[0].get("classname","").split(".")[-1]!="e2e_ajutor_17_5_R2":
        raise ValueError("nod pytest diferit")
    caz=cazuri[0]
    if caz.find("error") is not None or caz.find("skipped") is not None:
        raise ValueError("NEEXECUTAT")
    d=Path(capturi)/"17_5_R2"
    def incarca(nume):
        return json.loads((d/f"{nume}.json").read_text(encoding="utf-8"),object_pairs_hook=test.unice)
    if incarca("erori")!={} or incarca("partiale")!={}: raise ValueError("martori parțiali")
    m=incarca("masuri")
    if set(m)!=set(test.IDS): raise ValueError("set de măsurători incomplet")
    fail=caz.find("failure")
    if rc!=(1 if faza=="E" else 0) or (faza=="E")!=(fail is not None):
        raise ValueError("rc, JUnit și faza diferă")
    if fail is not None and "R_PRODUS" not in (fail.get("message","")+" "+(fail.text or "")):
        raise ValueError("eșecul nu este aserțiunea de produs")
    for i in test.IDS:
        verifica_png(d/(i+".png"),(603,590) if i=="e.5" else (1366,768))
    for w,h in test.REZ:
        dim=f"{w}x{h}"
        for card in test.FER: verifica_png(d/f"{dim}_{card}.png",(w,h))
        if m["e.5"][dim]["asistenti"]["ajutor"]["titlu"]: verifica_png(d/f"{dim}_ajutor_F006.png",(w,h))
    obs={i:test.rezultat(i,m[i]) for i in test.IDS}
    for i,v in obs.items(): print(i,"trece" if v else "pica")
    if faza=="E":
        nume,ids=(director / "rosii_baza_17_5_R2.txt").read_text().strip().split()
        if nume!=p.name or set(ids.split(","))!={i for i,v in obs.items() if not v}:
            raise ValueError("observațiile diferă de contractul roșu")
    elif not all(obs.values()): raise ValueError("candidat cu aserțiuni picate")


if __name__=="__main__":
    citeste(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))
