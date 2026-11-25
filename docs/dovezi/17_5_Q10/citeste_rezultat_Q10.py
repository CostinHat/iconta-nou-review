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
    path = here / "e2e_fundatie_17_5_Q10.py"
    if not path.exists() and here.parts[-3:] == ("docs", "dovezi", "17_5_Q10"):
        path = here.parents[2] / "frontend_test/e2e" / path.name
    spec = importlib.util.spec_from_file_location("fundatie_q10", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    nodes = ET.parse(xml).findall(".//testcase")
    if (
        len(nodes) != 1
        or nodes[0].get("classname", "").split(".")[-1] != "e2e_fundatie_17_5_Q10"
        or nodes[0].get("name") != "test_fundatie_17_5_Q10"
    ):
        raise ValueError("Nod pytest greșit")
    node = nodes[0]
    fail = node.find("failure")
    if node.find("error") is not None or node.find("skipped") is not None:
        raise ValueError("NEEXECUTAT")
    if (
        faza not in ("E", "C")
        or rc != (1 if faza == "E" else 0)
        or (fail is not None) != (rc == 1)
    ):
        raise ValueError("Fază/rc/failure")
    if fail is not None and "Q10_F018" not in fail.get("message", ""):
        raise ValueError("Alt eșec")
    d = Path(cap) / "17_5_Q10"
    obs = json.loads((d / "masuri.json").read_bytes())
    if any(
        json.loads((d / f"{k}.json").read_bytes()) != {} for k in ("erori", "partiale")
    ):
        raise ValueError("Parcurs incomplet")
    if set(obs) != set(mod.IDS) or any(
        set(obs[i]) != {"1366x768", "603x590"} for i in mod.IDS
    ):
        raise ValueError("Rezoluții")
    pred = (here / "rosii_baza_17_5_Q10.txt").read_text().split()
    if pred != ["e2e_fundatie_17_5_Q10.py", "e.2"]:
        raise ValueError("Contract de bază")
    for dim in mod.DIM:
        z = "%dx%d" % dim
        m = {}
        for i in mod.IDS:
            if set(obs[i][z]) != set(mod.CAMPURI[i]):
                raise ValueError("Structură martori " + i + " " + z)
            m.update(obs[i][z])
        if m["latime"] != dim[0]:
            raise ValueError("Lățime")
        result = mod.valideaza(m)
        for i in mod.IDS:
            png(d / f"{i}_{z}.png", dim)
            if (
                dim[0] == 1366
                and (d / f"{i}.png").read_bytes() != (d / f"{i}_{z}.png").read_bytes()
            ):
                raise ValueError("Captură alias")
        if result["e.2"]:
            for k in ("nume", "cui"):
                png(d / f"filtru_{k}_{z}.png", dim)
        if {i for i, v in result.items() if not v} != (
            {"e.2"} if faza == "E" else set()
        ):
            raise ValueError("Predicție " + z)
    for i in mod.IDS:
        print(i, "pica" if faza == "E" and i == "e.2" else "trece")


if __name__ == "__main__":
    citeste(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
