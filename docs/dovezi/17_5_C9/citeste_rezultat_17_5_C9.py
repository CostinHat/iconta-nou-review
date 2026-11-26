"""Judecă rularea REAL C9 (AC201, r2): XML-ul JUnit, codul pytest, măsurile celor două dimensiuni și capturile.

Folosire: citeste_rezultat_17_5_C9.py <E|C> <junit.xml> <director capturi> <rc pytest>
Faza E (baza): rc 1, iar eșecul e exact aserțiunea finală a testului (AssertionError: C9_EMITENT_SPV, pe linia ei din test);
roșu exact e.2, iar roșul e lipsa funcției pe ruta corectă: ciorna e în F1, cif_emitent e gol și câmpul «Furnizor» arată numai numele.
Faza C (candidatul): rc 0, toate verzi. În ambele faze măsurile descriu factura probei (identitățile fixturii) și sunt aceleași în
baza de date la ambele rezoluții.
"""

import importlib.util
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

ASERTIUNE = 'assert all(all(x.values()) for x in per_dim), "C9_EMITENT_SPV"'
CAI_TEST = ("frontend_test/e2e/e2e_fundatie_17_5_C9.py", "e2e_fundatie_17_5_C9.py")
CLASE = {"e2e_fundatie_17_5_C9", "frontend_test.e2e.e2e_fundatie_17_5_C9"}


def png(cale, dim):
    raw = cale.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or len(raw) < 45:
        raise ValueError(str(cale))
    pos = 8
    parts = []
    data = bytearray()
    canale = None
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
        or not parts
        or parts[0] != b"IHDR"
        or parts.count(b"IHDR") != 1
        or parts[-1] != b"IEND"
        or parts.count(b"IEND") != 1
        or canale is None
    ):
        raise ValueError("Structură PNG " + str(cale))
    pixels = zlib.decompress(data)
    linie = 1 + dim[0] * canale
    if len(pixels) != dim[1] * linie or any(x > 4 for x in pixels[::linie]):
        raise ValueError("Pixeli " + str(cale))


def sursa_test(here):
    path = here / "e2e_fundatie_17_5_C9.py"
    if not path.exists() and here.parts[-3:] == ("docs", "dovezi", "17_5_C9"):
        path = here.parents[2] / "frontend_test/e2e" / path.name
    return path


def modul_test(path):
    spec = importlib.util.spec_from_file_location("fundatie_c9", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cauza_esecului(fail, path):
    """Eșecul de bază e exact aserțiunea finală: mesajul pytest «AssertionError: C9_EMITENT_SPV» urmat de «assert False», linia
    sursei marcată cu «>» și ultima linie «<cale>:<linia aserțiunii>: AssertionError». Timeout, altă aserțiune, alt nod = refuz."""
    linii_sursa = path.read_text(encoding="utf-8").splitlines()
    nr = [i + 1 for i, linie in enumerate(linii_sursa) if linie.strip() == ASERTIUNE]
    if len(nr) != 1:
        raise ValueError("Aserțiunea finală nu e unică în test")
    mesaj = (fail.get("message") or "").split("\n")
    if mesaj[:2] != ["AssertionError: C9_EMITENT_SPV", "assert False"]:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (mesaj: %r)" % (fail.get("message") or "")[:80])
    text = [linie.rstrip() for linie in (fail.text or "").splitlines()]
    marcate = [linie for linie in text if linie.startswith(">")]
    if not marcate or marcate[-1][1:].strip() != ASERTIUNE:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (linia marcată în traseu)")
    if sum(1 for linie in text if re.fullmatch(r"E\s+AssertionError: C9_EMITENT_SPV", linie)) != 1:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (linia E)")
    ultima = [linie for linie in text if linie.strip()][-1] if any(linie.strip() for linie in text) else ""
    if ultima not in {"%s:%d: AssertionError" % (c, nr[0]) for c in CAI_TEST}:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (locul: %r)" % ultima[:80])


def citeste(faza, xml, cap, rc):
    here = Path(__file__).resolve().parent
    path = sursa_test(here)
    mod = modul_test(path)
    root = ET.parse(xml).getroot()
    if root.tag == "testsuite":
        suite = root
    elif root.tag == "testsuites" and len(root.findall("testsuite")) == 1:
        suite = root.find("testsuite")
    else:
        raise ValueError("Structură JUnit străină")
    nodes = root.findall(".//testcase")
    if len(nodes) != 1 or nodes != suite.findall("testcase") or nodes[0].get("classname") not in CLASE \
            or nodes[0].get("name") != "test_fundatie_17_5_C9":
        raise ValueError("Nod pytest greșit")
    if any(suite.get(k) != str(v) for k, v in {"tests": 1, "errors": 0, "skipped": 0, "failures": int(rc == 1)}.items()):
        raise ValueError("Sumarul JUnit nu corespunde nodului")
    node = nodes[0]
    if len(node.findall("failure")) != int(rc == 1):
        raise ValueError("Număr greșit de eșecuri")
    fail = node.find("failure")
    if node.find("error") is not None or node.find("skipped") is not None:
        raise ValueError("NEEXECUTAT")
    if faza not in ("E", "C") or rc != (1 if faza == "E" else 0) or (fail is not None) != (rc == 1):
        raise ValueError("Fază/rc/failure")
    if fail is not None:
        cauza_esecului(fail, path)
    d = Path(cap) / "17_5_C9"
    obs = json.loads((d / "masuri.json").read_bytes())
    if any(json.loads((d / n).read_text()) != {} for n in ("erori.json", "partiale.json")):
        raise ValueError("Ecran nemăsurat sau parcurs parțial")
    if set(obs) != set(mod.IDS):
        raise ValueError("Lipsesc identificatori")
    rosu = (here / "rosii_baza_17_5_C9.txt").read_text().split()
    if rosu != ["e2e_fundatie_17_5_C9.py", "e.2"]:
        raise ValueError("Contract roșu pe bază")
    dims = [f"{w}x{h}" for w, h in mod.DIM]
    for i in mod.IDS:
        if set(obs[i]) != set(dims):
            raise ValueError("Rezoluții incomplete")
    if any(obs["e.1"][z]["db"] != obs["e.1"][dims[0]]["db"] for z in dims):
        raise ValueError("Observațiile bazei de date diferă între rezoluții")
    rezultate = []
    for dim in mod.DIM:
        z = f"{dim[0]}x{dim[1]}"
        date = obs["e.1"][z]
        if any(obs[i][z] != date for i in mod.IDS):
            raise ValueError("Măsuri incompatibile")
        motive = mod.analiza(date, dim)
        rezultat = {i: not m for i, m in motive.items()}
        if faza == "E":
            unu = mod.rand(date["db"]["dupa_import"])
            if unu is None or unu["emitent"] != "" or date["ui"]["fereastra"]["furnizor"] != mod.FURNIZOR:
                raise ValueError("Roșul de bază nu e lipsa emitentului pe ruta corectă la " + z)
        asteptat = {"e.2"} if faza == "E" else set()
        rosii = {i for i in mod.IDS if not rezultat[i]}
        if rosii != asteptat:
            raise ValueError("Predicție diferită la %s: %s" % (z, "; ".join(
                "%s: %s" % (i, ", ".join(motive[i]) or "trece") for i in sorted(rosii ^ asteptat))))
        rezultate.append(rezultat)
        for i, poza in zip(mod.IDS, ("lista", "validare", "lista")):
            sursa = d / f"{poza}_{z}.png"
            png(sursa, dim)
            if (d / f"{i}_{z}.png").read_bytes() != sursa.read_bytes():
                raise ValueError("Captură diferită pentru " + i)
            if dim[0] == 1366 and (d / f"{i}.png").read_bytes() != sursa.read_bytes():
                raise ValueError("Alias diferit pentru " + i)
    for i in mod.IDS:
        print(i, "trece" if all(r[i] for r in rezultate) else "pica")


if __name__ == "__main__":
    citeste(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
