"""Judecă rularea REAL 17.5-F6 (fișa r1; cititorul calificat al F5, 806e0074…, adus la lotul F6 și la e.9): XML-ul JUnit, codul pytest, măsurile, capturile și fișierele recitite.

Folosire: citeste_rezultat_17_5_F6.py <E|C> <junit.xml> <director capturi> <rc pytest>
Faza E (baza C9): rc 1, iar eșecul este exact aserțiunea finală a testului (AssertionError: F6_FUNDATIE, pe linia ei).
Roșii exact e.2, e.4, e.6, e.8, e.9, fiecare pe cauza prezisă (e.9: pagina cabinetului desenată, cu cele șase carduri de sus, pe sesiunea
contului de probă cu firme, și fără nicio secțiune, cheie sau titlu de consultanță):
  e.2: propunerea T1 confirmată (e.1 trece), iar formularul nu are niciunul dintre butoanele #op-descarca-docx / #op-descarca-pdf și nicio descărcare;
  e.4: meniul F1, rolul și grupul „Contabilitate” confirmate (e.3 trece), iar cardul 502 lipsește după identificator și după titlu;
  e.6: titlul „Bancă” confirmat (e.5 trece) are exact trei semne, F011, F012, F073, cu title și aria-label generice;
  e.8: țintele confirmate (e.7 trece); cele 16 clicuri sunt valide, continue și legate de ținte și de documentul lor, iar motivele sunt exact
       comutările perechilor în care C9 diferă de cerință, cu profilul măsurat pe C9 (comanda, pct. 1, e.8).
Faza C (candidatul F6): rc 0, toate verzi.
Independent de măsurile scrise de test, cititorul recitește: capturile (lista obligatorie, dedusă din fază, traseu și rezoluție; registrul
capturi.json, amprenta, formatul și conținutul fiecăreia, scena),
documentele Word și PDF (structura și T1, recalculate din conținut), registrul FUNCTIONALITATI.csv servit (amprenta C9, secțiunile așteptate)
și modulul ds_piese.js încărcat în documentele probei (E: fișierul C9; C: sursa C2 calificată cu tokenul nativ al lui api.js).
Pe ieșire: numai rânduri «<id> <verdict>», în ordinea identificatorilor.
"""

import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

ASERTIUNE = 'assert all(verdicte.values()), "F6_FUNDATIE"'
CAI_TEST = ("frontend_test/e2e/e2e_fundatie_17_5_F6.py", "e2e_fundatie_17_5_F6.py")
CLASE = {"e2e_fundatie_17_5_F6", "frontend_test.e2e.e2e_fundatie_17_5_F6"}
ROSII = ("e.2", "e.4", "e.6", "e.8", "e.9")
CAUZA = {"e.2": ["descarcari_lipsa"], "e.4": ["card_502_lipsa"], "e.6": ["semne_3"], "e.9": ["sectiune_consultanta_lipsa"]}
DS_C9 = "991d8dadf1ef53ac8e1d1ff4fa2422bdb92a7610e08cdb849128ab5683e3dcc6"   # static/js/ds_piese.js la publicarea C9
DS_C2 = "f47beff6324293abb5ec908bd000daac6db933128d60f3eab75e8f9314473e39"   # sursa C2 calificată pe 8019 (comanda, pct. 18)
IMPORT_API_C2 = "./api.js?v=a84ae6966b"
FUNC_C9 = "00ce8431921f0c9ac24ce7d46da20b37b5da9ca120197a11231f645cf2a123f3"  # FUNCTIONALITATI.csv la publicarea C9 (AC202 nu-l schimbă)
SURSA_C2 = "ds_piese_C2_calificat.js"
BANCA = ("F012", "F011", "F073")
TOKEN = re.compile(r"""\?v=[^"'`\s)]*""")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def defiltreaza(date, w, h, bpp):
    """Scanliniile PNG fără filtre (None, Sub, Up, Average, Paeth): octeții pixelilor, rând după rând."""
    linie, out, prev, p = w * bpp, bytearray(), bytes(w * bpp), 0
    for _ in range(h):
        f, cur = date[p], bytearray(date[p + 1:p + 1 + linie])
        p += 1 + linie
        if f == 1:
            for i in range(bpp, linie):
                cur[i] = (cur[i] + cur[i - bpp]) & 255
        elif f == 2:
            for i in range(linie):
                cur[i] = (cur[i] + prev[i]) & 255
        elif f == 3:
            for i in range(linie):
                cur[i] = (cur[i] + (((cur[i - bpp] if i >= bpp else 0) + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(linie):
                a, b, c = (cur[i - bpp], prev[i], prev[i - bpp]) if i >= bpp else (0, prev[i], 0)
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out += cur
        prev = cur
    return bytes(out)


def png(cale, dim, fara_pil=False):
    """PNG valid (semnătură, CRC-uri, IHDR, IEND, filtre) la exact dimensiunea ferestrei. -> pixelii decodați, RGBA, 4 octeți pe pixel.
    Decodarea e a cititorului (zlib + defiltrare); dacă biblioteca PIL există, face ea aceeași decodare, mai repede."""
    raw = cale.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or len(raw) < 45:
        raise ValueError("PNG invalid " + cale.name)
    pos, data, canale, sfarsit = 8, bytearray(), None, False
    while pos + 12 <= len(raw):
        n = int.from_bytes(raw[pos:pos + 4], "big")
        tag, body, crc = raw[pos + 4:pos + 8], raw[pos + 8:pos + 8 + n], raw[pos + 8 + n:pos + 12 + n]
        if len(crc) != 4 or zlib.crc32(tag + body) != int.from_bytes(crc, "big"):
            raise ValueError("CRC " + cale.name)
        if tag == b"IHDR":
            w, h = int.from_bytes(body[0:4], "big"), int.from_bytes(body[4:8], "big")
            if (w, h) != tuple(dim) or body[8] != 8 or body[9] not in (2, 6) or body[12] != 0:
                raise ValueError("Format sau dimensiune greșită " + cale.name)
            canale = 3 if body[9] == 2 else 4
        elif tag == b"IDAT":
            data.extend(body)
        elif tag == b"IEND":
            sfarsit = pos + 12 == len(raw)
            break
        pos += 12 + n
    if canale is None or not sfarsit:
        raise ValueError("PNG trunchiat sau fără IHDR/IEND " + cale.name)
    try:
        filtrat = zlib.decompress(bytes(data))
    except zlib.error:
        raise ValueError("Pixeli necomprimabili " + cale.name)
    linie = 1 + dim[0] * canale
    if len(filtrat) != dim[1] * linie or any(x > 4 for x in filtrat[::linie]):
        raise ValueError("Pixeli " + cale.name)
    rgba = None
    if not fara_pil:
        try:
            from PIL import Image
            rgba = Image.open(io.BytesIO(raw)).convert("RGBA").tobytes()
        except ImportError:
            pass
    if rgba is None:
        px = defiltreaza(filtrat, dim[0], dim[1], canale)
        if canale == 3:
            rgba = bytearray(b"\xff") * (dim[0] * dim[1] * 4)
            rgba[0::4], rgba[1::4], rgba[2::4] = px[0::3], px[1::3], px[2::3]
            rgba = bytes(rgba)
        else:
            rgba = px
    lat = 4 * dim[0]
    if len({rgba[i:i + lat] for i in range(0, len(rgba), lat)}) < 8 or len(set(memoryview(rgba).cast("I"))) < 4:
        raise ValueError("Imagine uniformă, fără conținut de ecran (pixelii decodați): " + cale.name)
    return rgba


def sursa_test(here):
    path = here / "e2e_fundatie_17_5_F6.py"
    if not path.exists() and here.parts[-3:] == ("docs", "dovezi", "17_5_F6"):
        path = here.parents[2] / "frontend_test/e2e" / path.name
    return path


def modul_test(path):
    spec = importlib.util.spec_from_file_location("fundatie_f6", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cauza_esecului(fail, path):
    """Eșecul bazei este exact aserțiunea finală; un timeout, o altă aserțiune sau o eroare de navigare înseamnă refuz."""
    linii = path.read_text(encoding="utf-8").splitlines()
    nr = [i + 1 for i, linie in enumerate(linii) if linie.strip() == ASERTIUNE]
    if len(nr) != 1:
        raise ValueError("Aserțiunea finală nu e unică în test")
    mesaj = (fail.get("message") or "").split("\n")
    if mesaj[:2] != ["AssertionError: F6_FUNDATIE", "assert False"]:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (mesaj: %r)" % (fail.get("message") or "")[:80])
    text = [linie.rstrip() for linie in (fail.text or "").splitlines()]
    marcate = [linie for linie in text if linie.startswith(">")]
    if not marcate or marcate[-1][1:].strip() != ASERTIUNE:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (linia marcată)")
    if sum(1 for linie in text if re.fullmatch(r"E\s+AssertionError: F6_FUNDATIE", linie)) != 1:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (linia E)")
    ultima = [linie for linie in text if linie.strip()][-1] if any(linie.strip() for linie in text) else ""
    if ultima not in {"%s:%d: AssertionError" % (c, nr[0]) for c in CAI_TEST}:
        raise ValueError("Cauza eșecului nu e aserțiunea finală (locul: %r)" % ultima[:80])


def obligatorii(mod, faza):
    """Capturile pe care rularea trebuie să le aibă, deduse din fază, traseu și rezoluție: {fișier: (zona, scena, rezoluția, etapa, ținta, clicul)}.
    Pe candidat se cer în plus fereastra 502, ajutorul deschis și secțiunea «Consultanță» a cabinetului desfăcută, la ambele rezoluții; pe bază ele nu pot exista."""
    out = {}
    for w, h in mod.DIM:
        z = "%dx%d" % (w, h)
        out["dividend_%s.png" % z] = ("dividend", "formular", z, None, None, None)
        out["meniu_%s.png" % z] = ("meniu", "meniu", z, None, None, None)
        out["banca_%s.png" % z] = ("banca", "banca", z, None, None, None)
        out["cabinet_%s.png" % z] = ("cabinet", "cabinet", z, None, None, None)
        if faza == "C":
            out["cabinet_deschis_%s.png" % z] = ("cabinet", "cabinet_deschis", z, None, None, None)
            out["consultanta_%s.png" % z] = ("meniu", "consultanta", z, None, None, None)
            out["ajutor_%s.png" % z] = ("banca", "ajutor", z, None, None, None)
    for w, h in mod.DIM_DETALII:
        z = "%dx%d" % (w, h)
        for e in mod.ORDINE_ETAPE:
            out[mod.fis("detalii", e, "inainte", z) + ".png"] = ("detalii", "etapa", z, e, None, None)
        for e, tinta in mod.PERECHI:
            for nr in (1, 2):
                out[mod.fis("detalii", e, tinta, "clic%d" % nr, z) + ".png"] = ("detalii", "clic", z, e, tinta, nr)
    return out


def referinte(mod, masuri):
    """{fișier: (zona, scena, rezoluția, etapa, ținta, clicul)} pentru fiecare captură numită în măsuri; o captură numită de două ori e refuz."""
    ref = {}

    def pune(nume, *scena):
        if not isinstance(nume, str) or "/" in nume or not nume.endswith(".png"):
            raise ValueError("Captură numită greșit la %s %s" % (scena[0], scena[2]))
        if nume in ref:
            raise ValueError("Captură folosită de două ori: " + nume)
        ref[nume] = scena
    for i in ("e.1", "e.3", "e.5", "e.7", "e.9"):
        for z, m in masuri[i].items():
            zona = m["zona"]
            if zona == "cabinet":
                pune(m["captura"], zona, "cabinet", z, None, None, None)
                if "captura_deschis" in m:
                    pune(m["captura_deschis"], zona, "cabinet_deschis", z, None, None, None)
            elif zona == "dividend":
                pune(m["captura"], zona, "formular", z, None, None, None)
            elif zona == "meniu":
                pune(m["captura"], zona, "meniu", z, None, None, None)
                if "captura_502" in m:
                    pune(m["captura_502"], zona, "consultanta", z, None, None, None)
            elif zona == "banca":
                pune(m["captura"], zona, "banca", z, None, None, None)
                for p in (m["ajutor"].get("pasi", []) if isinstance(m.get("ajutor"), dict) else []):
                    if "captura" in p:
                        pune(p["captura"], zona, "ajutor", z, None, None, None)
            else:
                for e in m["etape"]:
                    pune(e["captura"], zona, "etapa", z, e["etapa"], None, None)
                for c in m["clicuri"]:
                    if not c.get("absent"):
                        pune(c["captura"], zona, "clic", z, c["etapa"], c["tinta"], c["clic"])
    return ref


def stare_scena(nume, scena, s, masuri):
    """Starea navigatorului consemnată la captură este a scenei: firma și fereastra ei; fereastra 502 deschisă; ajutorul deschis peste Bancă."""
    zona, sc, z = scena[:3]
    antet = s.get("antet") or ""
    if sc in ("cabinet", "cabinet_deschis"):   # pagina cabinetului, fără nicio fereastră deschisă peste ea
        return s.get("active") == 0
    if sc == "formular":
        return "F2 Profit Amortizare SRL" in antet and "Decontări asociați" in antet
    if sc in ("meniu", "banca"):
        return "F1 Comert Stoc SRL" in antet and (sc == "meniu" or "Bancă" in antet)
    if sc in ("etapa", "clic"):
        return "F1 Comert Stoc SRL" in antet and ("Declarații" if scena[3] == "Declarații" else "Control fiscal") in antet
    if sc == "consultanta":
        return "Consultanță fiscală" in (s.get("h2") or "") and "F1 Comert Stoc SRL" in (s.get("antet") or "")
    if sc == "ajutor":
        n0 = masuri["e.5"][z]["ecran"].get("nivel")
        return str(n0).isdigit() and str(s.get("nivel")) == str(int(n0) + 1) and "Ajutor" in (s.get("antet") or "") and s.get("active") == 1
    return True


def capturi(mod, faza, d, masuri):
    """Capturile: măsurile numesc exact lista obligatorie a fazei, registrul capturi.json are exact aceleași rânduri (scena, etapa, ținta, clicul,
    rezoluția, amprenta, starea navigatorului), fiecare fișier are amprenta consemnată, e PNG valid la rezoluția scenei și are conținut de ecran.
    Conținutul se judecă pe pixelii decodați: imaginea nu e uniformă; două clicuri ale aceleiași perechi cu stări finale diferite au pixeli
    diferiți; fereastra 502 diferă de meniu, iar ajutorul de Bancă. Două capturi cu aceeași stare vizibilă pot avea aceiași pixeli.
    Amprenta SHA-256 a fișierului păzește integritatea, iar aliasul e.N.png e copia exactă, pe octeți, a capturii desemnate."""
    ob, ref = obligatorii(mod, faza), referinte(mod, masuri)
    if ref != ob:
        lipsa, plus = sorted(set(ob) - set(ref)), sorted(set(ref) - set(ob))
        raise ValueError("Capturile din măsuri nu sunt cele obligatorii în faza %s: lipsesc %s; în plus sau cu altă scenă %s" % (
            faza, lipsa[:4], (plus or sorted(k for k in ob if k in ref and ref[k] != ob[k]))[:4]))
    reg, pixeli = json.loads((d / "capturi.json").read_text(encoding="utf-8")), {}
    if set(reg) != set(ob):
        raise ValueError("Registrul capturilor diferă de lista obligatorie: %s" % sorted(set(reg) ^ set(ob))[:4])
    for nume, scena in ob.items():
        r = reg[nume]
        if (r.get("zona"), r.get("scena"), r.get("rezolutie"), r.get("etapa"), r.get("tinta"), r.get("clic")) != scena:
            raise ValueError("Captura %s nu e a scenei măsurate" % nume)
        if not (d / nume).is_file() or sha((d / nume).read_bytes()) != r.get("sha256"):
            raise ValueError("Captura %s lipsește sau nu are amprenta consemnată" % nume)
        pixeli[nume] = png(d / nume, tuple(int(x) for x in scena[2].split("x")))
        if not stare_scena(nume, scena, r.get("stiva") or {}, masuri):
            raise ValueError("Captura %s nu arată starea deschisă a scenei ei" % nume)
    for z, m in masuri["e.7"].items():   # deosebirea vizuală se judecă pe pixelii decodați, nu pe octeții fișierului
        for k, (c1, c2) in mod.perechi(m).items():
            if c1 and c2 and c1.get("stare_dupa") != c2.get("stare_dupa") and pixeli[c1["captura"]] == pixeli[c2["captura"]]:
                raise ValueError("Capturile perechii %s %s au aceiași pixeli, deși stările diferă" % k)
    if faza == "C":
        for w, h in mod.DIM:
            z = "%dx%d" % (w, h)
            if pixeli["consultanta_%s.png" % z] == pixeli["meniu_%s.png" % z] or pixeli["ajutor_%s.png" % z] == pixeli["banca_%s.png" % z]:
                raise ValueError("Captura 502 sau a ajutorului la %s are aceiași pixeli ca ecranul din care se deschide" % z)
            if pixeli["cabinet_deschis_%s.png" % z] == pixeli["cabinet_%s.png" % z]:
                raise ValueError("Captura secțiunii «Consultanță» desfăcute la %s are aceiași pixeli ca secțiunea pliată" % z)
    for i in mod.IDS:
        z = "%dx%d" % mod.DIM_ID[i][0]
        m = masuri[i][z]
        sursa = m["clicuri"][-1]["captura"] if i == "e.8" else m["captura"]
        if (d / ("%s.png" % i)).read_bytes() != (d / sursa).read_bytes():
            raise ValueError("Alias diferit pentru " + i)


def documente(mod, d, masuri):
    """Documentele descărcate (faza C), recitite: amprenta, apoi concluziile recalculate din conținut = concluziile consemnate."""
    for z, m in masuri["e.2"].items():
        for tip, x in (m.get("documente") or {}).items():
            f = d / str(x.get("fisier"))
            if x.get("fisier") != "hotarare_%s.%s" % (z, tip) or not f.is_file() or sha(f.read_bytes()) != x.get("sha256"):
                raise ValueError("Documentul %s la %s nu corespunde măsurii" % (tip, z))
            if mod.judeca_document(tip, f.read_bytes()) != x.get("judecata"):
                raise ValueError("Documentul %s la %s: concluziile recalculate diferă de măsură" % (tip, z))


def registru_ajutor(text):
    """Secțiunile Bancă din registru, calculate aici: numele (coloana Functionalitate) și rândurile nevide ale coloanei ajutor, fără «## »."""
    r = {x["ID"]: x for x in csv.DictReader(io.StringIO(text))}
    n = lambda s: re.sub(r"\s+", " ", s or "").strip()  # noqa: E731
    return [{"id": i, "titlu": n(r[i]["Functionalitate"]), "linii": [x for x in (n(y[3:] if y.startswith("## ") else y) for y in r[i]["ajutor"].split("\n")) if x]}
            for i in BANCA]


def registrul(d, masuri):
    """FUNCTIONALITATI.csv servit are amprenta C9; secțiunile folosite la e.6 sunt cele calculate aici din el."""
    b = (d / "FUNCTIONALITATI.csv").read_bytes()
    if sha(b) != FUNC_C9:
        raise ValueError("FUNCTIONALITATI.csv servit nu e cel din C9")
    ast = registru_ajutor(b.decode("utf-8"))
    if any(m["arbore"].get("functionalitati_sha256") != FUNC_C9 for m in masuri["e.8"].values()):
        raise ValueError("Registrul arborelui servit diferă de copia lui")
    for z, m in masuri["e.6"].items():
        a = m.get("ajutor")
        if isinstance(a, dict) and a.get("registru") != ast:
            raise ValueError("Secțiunile așteptate din măsuri diferă de registru la " + z)


def token(text):
    return hashlib.sha1(TOKEN.sub("", text).encode("utf-8")).hexdigest()[:10]


def modulul(faza, here, d, masuri):
    """Modulul ds_piese.js încărcat în cele două documente ale probei = fișierul exportat al arborelui servit; E: C9; C: sursa C2 cu tokenul nativ."""
    exp, api = (d / "exportat_ds_piese.js").read_bytes(), (d / "exportat_api.js").read_bytes()
    for z, m in masuri["e.8"].items():
        if m["arbore"].get("ds_piese_sha256") != sha(exp) or m["arbore"].get("api_sha256") != sha(api):
            raise ValueError("Fișierele exportate diferă de arborele măsurat la " + z)
        for x in m["module"]:
            s = (d / x["fisier"]).read_bytes()
            if x["fisier"] != "servit_ds_piese_%d.js" % x["document"] or sha(s) != x["sha256"] or s != exp:
                raise ValueError("Modulul încărcat în documentul %s nu e fișierul exportat" % x.get("document"))
            if x["url"] != "/static/js/ds_piese.js?v=" + token(exp.decode("utf-8")):
                raise ValueError("URL-ul versionat al modulului nu are tokenul nativ")
    if faza == "E":
        if sha(exp) != DS_C9:
            raise ValueError("Pe bază, modulul servit nu e ds_piese.js din C9")
        return
    c2 = (here / SURSA_C2).read_bytes()   # lângă cititor: în ghid (lanțul) și în docs/dovezi/17_5_F6/ (lotul)
    if sha(c2) != DS_C2 or c2.count(IMPORT_API_C2.encode()) != 1 or c2.count(b"?v=") != 1:
        raise ValueError("Sursa C2 calificată nu e cea din pct. 18")
    asteptat = c2.replace(IMPORT_API_C2.encode(), ("./api.js?v=" + token(api.decode("utf-8"))).encode())
    if asteptat != exp:
        raise ValueError("ds_piese.js al candidatului nu e sursa C2 cu tokenul nativ al lui api.js")


def restaurarea(d):
    r = json.loads((d / "restaurare.json").read_text(encoding="utf-8"))
    if r != {"abateri": [], "ramase": []}:
        raise ValueError("Datele de probă nu au fost refăcute: %r" % r)


def rosu_prezis(mod, masuri, rez):
    """Cauza fiecărui roșu de bază, pe fiecare dimensiune măsurată. La e.8 cauza e exact lista perechilor în care profilul C9 diferă de
    comutarea cerută (un clic deschide, următorul închide); orice alt motiv (gest, țintă, document, stare imposibilă) nu e roșul prezis."""
    perechi_rosii = ["comutari_%s_%s" % k for k in mod.PERECHI if mod.PROFIL_BAZA[k] != ((1, "deschis"), (1, "închis"))]
    for i, motive in dict(CAUZA, **{"e.8": perechi_rosii}).items():
        for z, m in rez[i].items():
            if m != motive:
                raise ValueError("Roșul de bază %s nu are cauza prezisă la %s: %s" % (i, z, ", ".join(m)))
    for z, m in masuri["e.2"].items():
        f = m["formular"]
        if f["butoane_descarcare"] or any(f["butoane"][k].get("exista") for k in ("docx", "pdf")) or m.get("documente"):
            raise ValueError("Pe bază există descărcări în formular la " + z)
    for z, m in masuri["e.4"].items():
        me = m["meniu"]
        if me.get("id_502_in_fereastra") or me.get("titlu_502_in_fereastra") or "consultanta" in m:
            raise ValueError("Pe bază există intrarea 502 la " + z)
    for z, m in masuri["e.6"].items():
        s = m["banca"]["semne"]
        if [x.get("id") for x in s] != list(mod.SEMNE_BAZA) or any((x.get("title"), x.get("aria")) != mod.GENERIC or not x.get("vizibil") for x in s) \
                or "ajutor" in m:
            raise ValueError("Semnele bazei nu sunt cele trei semne generice F011, F012, F073 la " + z)
    for z, m in masuri["e.9"].items():
        c = m["cabinet"]
        if set(c["chei_pagina"]) & set(mod.CHEI_CONS) or c.get("titluri_consultanta") or mod.sectiuni_consultanta(c) \
                or "deschis" in m or "inchis" in m or "captura_deschis" in m:
            raise ValueError("Pe bază există secțiunea sau cardurile de consultanță ale cabinetului la " + z)
    for z, m in masuri["e.8"].items():
        if mod.profil_detalii(m) != mod.PROFIL_BAZA:
            raise ValueError("Alt profil al bazei la %s: %r" % (z, mod.profil_detalii(m)))


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
            or nodes[0].get("name") != "test_fundatie_17_5_F6":
        raise ValueError("Nod pytest greșit")
    if any(suite.get(k) != str(v) for k, v in {"tests": 1, "errors": 0, "skipped": 0, "failures": int(rc == 1)}.items()):
        raise ValueError("Sumarul JUnit nu corespunde nodului")
    node = nodes[0]
    if len(node.findall("failure")) != int(rc == 1):
        raise ValueError("Număr greșit de eșecuri")
    if node.find("error") is not None or node.find("skipped") is not None:
        raise ValueError("NEEXECUTAT")
    fail = node.find("failure")
    if faza not in ("E", "C") or rc != (1 if faza == "E" else 0) or (fail is not None) != (rc == 1):
        raise ValueError("Fază/rc/failure")
    if fail is not None:
        cauza_esecului(fail, path)
    d = Path(cap) / mod.LOT
    if any(json.loads((d / n).read_text(encoding="utf-8")) != {} for n in ("erori.json", "partiale.json")):
        raise ValueError("Ecran nemăsurat sau parcurs parțial")
    restaurarea(d)
    masuri = json.loads((d / "masuri.json").read_text(encoding="utf-8"))
    # contractul roșiilor de bază, în forma citită de dovada_baza.sh și de ajustare_plasa.py: «<test.py> id,id,…» pe un singur rând
    if (here / "rosii_baza_17_5_F6.txt").read_text(encoding="utf-8").split() != ["e2e_fundatie_17_5_F6.py", ",".join(ROSII)]:
        raise ValueError("Contract roșu pe bază")
    rez = mod.analiza(masuri)
    capturi(mod, faza, d, masuri)
    registrul(d, masuri)
    modulul(faza, here, d, masuri)
    documente(mod, d, masuri)
    verdict = {i: all(not motive for motive in rez[i].values()) for i in mod.IDS}
    rosii = {i for i in mod.IDS if not verdict[i]}
    asteptat = set(ROSII) if faza == "E" else set()
    if rosii != asteptat:
        raise ValueError("Predicție diferită: %s" % "; ".join(
            "%s: %s" % (i, " | ".join("%s %s" % (z, ", ".join(m) or "trece") for z, m in sorted(rez[i].items())))
            for i in sorted(rosii ^ asteptat)))
    if faza == "E":
        rosu_prezis(mod, masuri, rez)
    for i in mod.IDS:
        print(i, "trece" if verdict[i] else "pica")


if __name__ == "__main__":
    citeste(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
