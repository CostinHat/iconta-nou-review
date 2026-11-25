"""Cititor Q7 pentru XML, măsuri și capturi ale aceluiași nod pytest."""
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


def citeste(faza,xml,capturi,rc):
    here=Path(__file__).resolve().parent
    test=here/"e2e_fundatie_17_5_Q9.py"
    if not test.is_file() and here.parts[-3:]==("docs","dovezi","17_5_Q9"):
        test=here.parents[2]/"frontend_test"/"e2e"/test.name
    spec=importlib.util.spec_from_file_location("fundatie",test)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    if faza not in ("E","C"): raise ValueError("Fază invalidă")
    nodes=ET.parse(xml).findall(".//testcase")
    if len(nodes)!=1 or nodes[0].get("classname","").split(".")[-1]!="e2e_fundatie_17_5_Q9" or nodes[0].get("name")!="test_fundatie_17_5_Q9":
        raise ValueError("Nod pytest greșit")
    node=nodes[0];fail=node.find("failure")
    if node.find("error") is not None or node.find("skipped") is not None:raise ValueError("NEEXECUTAT")
    if rc not in (0,1) or (fail is not None)!=(rc==1) or (faza=="C" and rc):raise ValueError("rc sau fază incompatibilă")
    if fail is not None and "Q7_FUNDATIE" not in ((fail.get("message") or "")+(fail.text or "")):raise ValueError("Eroare străină probei")
    d=Path(capturi)/"17_5_Q9"
    def load(n):return json.loads((d/(n+".json")).read_text())
    if load("erori")!={} or load("partiale")!={}:raise ValueError("Martori parțiali")
    obs=load("masuri")
    for w,h in m.DIM:
        for k in m.IDS:
            verifica_png(d/f"{k}_{w}x{h}.png",(w,h))
            if w==1366 and (d/f"{k}.png").read_bytes()!=(d/f"{k}_{w}x{h}.png").read_bytes():
                raise ValueError("Captura aserțiunii diferă de captura parcursului: "+k)
    for k in m.IDS:verifica_png(d/(k+".png"),(1366,768))
    if set(obs) != set(m.IDS):
        raise ValueError("Măsurile trebuie să aibă câte o intrare pentru fiecare aserțiune")
    for w,h in m.DIM:
        z = f"{w}x{h}"
        r = obs["e.4"][z]
        for prefix in ("e.4_text_ascuns_", "e.4_text_restabilit_"):
            verifica_png(d/(prefix+z+".png"),(w,h))
        if m.martor_luna(d, [w,h], r["zone_text"]) != r["pixeli_text"]:
            raise ValueError("Martorul de pixeli nu reproduce măsura e.4 la "+z)
    values={k:m.verdict(k,obs[k]) for k in m.IDS}
    for k, agregat in values.items():
        ambele = m.pe_rezolutii(k, obs[k])
        if any(rezultat != agregat for rezultat in ambele):
            raise ValueError("Rezoluțiile au rezultate diferite pentru " + k)
        print(k, "trece" if agregat else "pica")
    red={k for k,v in values.items() if not v}
    if bool(red)!=(rc==1):raise ValueError("Rezultatele măsurate contrazic pytest")
    if faza=="E":
        nod,ids=(here/"rosii_baza_17_5_Q9.txt").read_text().split()
        if nod!=test.name or red!=(set() if ids=="-" else set(ids.split(","))):raise ValueError("Contract roșu diferit")
    elif red:raise ValueError("Candidat cu abateri")
if __name__=="__main__":
    citeste(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))
