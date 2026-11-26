"""Judecă XML, codul pytest, măsurile celor două dimensiuni și capturile REAL."""

import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import struct
import zlib


def png(cale, dim):
    raw = cale.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or len(raw) < 45:
        raise ValueError(str(cale))
    pos = 8
    parts = []
    data = bytearray()
    while pos + 12 <= len(raw):
        n = int.from_bytes(raw[pos : pos + 4], "big")
        tag = raw[pos + 4 : pos + 8]
        body = raw[pos + 8 : pos + 8 + n]
        crc = raw[pos + 8 + n : pos + 12 + n]
        if len(crc) != 4 or zlib.crc32(tag + body) != int.from_bytes(crc, "big"):
            raise ValueError("CRC " + str(cale))
        parts.append(tag)
        if tag == b"IHDR":
            if len(body) != 13 or struct.unpack(">IIBBBBB", body) not in [
                (*dim, 8, 2, 0, 0, 0),
                (*dim, 8, 6, 0, 0, 0),
            ]:
                raise ValueError("Format sau dimensiune greșită " + str(cale))
            canale = 3 if body[9] == 2 else 4
        if tag == b"IDAT":
            data.extend(body)
        pos += n + 12
    if (
        pos != len(raw)
        or parts[0] != b"IHDR"
        or parts.count(b"IHDR") != 1
        or parts[-1] != b"IEND"
        or parts.count(b"IEND") != 1
    ):
        raise ValueError("Structură PNG " + str(cale))
    pixels = zlib.decompress(data)
    linie = 1 + dim[0] * canale
    if len(pixels) != dim[1] * linie or any(x > 4 for x in pixels[::linie]):
        raise ValueError("Pixeli " + str(cale))


def citeste(faza, xml, cap, rc):
    here = Path(__file__).resolve().parent
    path = here / "e2e_fundatie_17_5_Q12.py"
    if not path.exists() and here.parts[-3:] == ("docs", "dovezi", "17_5_Q12"):
        path = here.parents[2] / "frontend_test/e2e" / path.name
    spec = importlib.util.spec_from_file_location("fundatie_q12", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root = ET.parse(xml).getroot()
    if root.tag == "testsuite":
        suite = root
    elif root.tag == "testsuites" and len(root.findall("testsuite")) == 1:
        suite = root.find("testsuite")
    else:
        raise ValueError("Structură JUnit străină")
    nodes = root.findall(".//testcase")
    if (
        len(nodes) != 1
        or nodes != suite.findall("testcase")
        or nodes[0].get("classname") not in {
            "e2e_fundatie_17_5_Q12", "frontend_test.e2e.e2e_fundatie_17_5_Q12"
        }
        or nodes[0].get("name") != "test_fundatie_17_5_Q12"
    ):
        raise ValueError("Nod pytest greșit")
    if any(suite.get(k) != str(v) for k, v in {
        "tests": 1, "errors": 0, "skipped": 0, "failures": int(rc == 1)
    }.items()):
        raise ValueError("Sumarul JUnit nu corespunde nodului")
    node = nodes[0]
    if len(node.findall("failure")) != int(rc == 1):
        raise ValueError("Număr greșit de eșecuri")
    fail = node.find("failure")
    if node.find("error") is not None or node.find("skipped") is not None:
        raise ValueError("NEEXECUTAT")
    if (
        faza not in ("E", "C")
        or rc != (1 if faza == "E" else 0)
        or (fail is not None) != (rc == 1)
    ):
        raise ValueError("Fază/rc/failure")
    if fail is not None and "Q12_F018_IERARHIE" not in fail.get("message", ""):
        raise ValueError("Alt eșec")
    d = Path(cap) / "17_5_Q12"

    obs = json.loads((d / "masuri.json").read_bytes())
    if any(json.loads((d / n).read_text()) != {} for n in ("erori.json", "partiale.json")):
        raise ValueError("Ecran nemăsurat sau parcurs parțial")
    if set(obs) != set(mod.IDS):
        raise ValueError("Lipsesc identificatori")
    rosu = (here / "rosii_baza_17_5_Q12.txt").read_text().split()
    if rosu != ["e2e_fundatie_17_5_Q12.py", "e.2"]:
        raise ValueError("Contract roșu pe bază")
    dims = {f"{w}x{h}" for w, h in mod.DIM}
    for i in mod.IDS:
        if set(obs[i]) != dims:
            raise ValueError("Rezoluții incomplete")
    rezultate = []
    for dim in mod.DIM:
        z = f"{dim[0]}x{dim[1]}"
        date = obs["e.1"][z]
        if any(obs[i][z] != date for i in mod.IDS):
            raise ValueError("Măsuri incompatibile")
        rezultat = mod.valideaza(date, dim)
        if faza == "E" and not all(mod.contract_fereastra(date[n], n, True) for n, *_ in mod.ECRANE):
            raise ValueError("Martorul de bază nu reproduce harta E11 la " + z)
        if {i for i in mod.IDS if not rezultat[i]} != ({"e.2"} if faza == "E" else set()):
            raise ValueError("Predicție diferită la " + z)
        rezultate.append(rezultat)
        for i, ecran in zip(mod.IDS, mod.ECRANE):
            poza = d / f"{ecran[0]}_{z}.png"
            png(poza, dim)
            if (d / f"{i}_{z}.png").read_bytes() != poza.read_bytes():
                raise ValueError("Captură diferită pentru " + i)
            if dim[0] == 1366 and (d / f"{i}.png").read_bytes() != poza.read_bytes():
                raise ValueError("Alias diferit pentru " + i)
    for i in mod.IDS:
        print(i, "trece" if all(r[i] for r in rezultate) else "pica")


if __name__ == "__main__":
    citeste(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
