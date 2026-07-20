# -*- coding: utf-8 -*-
"""
cor_incarca.py — [F137] incarca nomenclatorul COR oficial in public.cor_ocupatii.

Sursa: cor_surse/cor2024.xml — fisierul oficial de pe data.gov.ro (dataset "Clasificarea
Ocupatiilor din Romania", lista alfabetica, Ordin 573/180/2024). Fisierul e un document Word
exportat ca "Flat OPC" XML (pkg:package / Word.Document): lista traieste in partea
/word/document.xml ca paragrafe care alterneaza COD (6 cifre) -> DENUMIRE.

Idempotent: sterge si reincarca (nomenclatorul e o versiune intreaga, nu increment). Ruleaza:
  set -a; source ~/.iconta/db.env; set +a
  /opt/iconta/venv/bin/python3 cor_incarca.py
"""
import os
import re
import sys
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import db, cor_api  # noqa: E402

PKG = "http://schemas.microsoft.com/office/2006/xmlPackage"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FISIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cor_surse", "cor2024.xml")
_COD = re.compile(r"^\d{6}$")


def extrage_perechi(cale=FISIER):
    """Parseaza fisierul Word Flat OPC -> [(cod, denumire)]. Verifica structura asteptata."""
    t = etree.parse(cale)
    part = next((p for p in t.getroot()
                 if p.get("{%s}name" % PKG) == "/word/document.xml"), None)
    if part is None:
        raise ValueError("structura neasteptata: lipseste partea /word/document.xml (nu e doc Word COR?)")
    body = part.find(".//{%s}xmlData" % PKG)[0]

    def txt(p):
        return "".join(n.text or "" for n in p.findall(".//{%s}t" % W)).strip()

    linii = [x for x in (txt(p) for p in body.findall(".//{%s}p" % W)) if x]
    perechi, i = [], 0
    while i < len(linii):
        if _COD.match(linii[i]):
            den = linii[i + 1] if (i + 1 < len(linii) and not _COD.match(linii[i + 1])) else ""
            if den:
                perechi.append((linii[i], den))
                i += 2
                continue
        i += 1
    return perechi


def main():
    perechi = extrage_perechi()
    coduri = [c for c, _ in perechi]
    if not perechi:
        raise SystemExit("EROARE: 0 perechi extrase - format neasteptat, nu incarc nimic.")
    if not all(_COD.match(c) for c in coduri):
        raise SystemExit("EROARE: exista coduri care nu-s pe 6 cifre - refuz incarcarea.")
    if len(set(coduri)) != len(coduri):
        raise SystemExit("EROARE: coduri duplicate - refuz incarcarea.")
    print("perechi valide extrase: %d (coduri unice, toate 6 cifre)" % len(perechi))

    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE public.cor_ocupatii")
            cur.executemany(
                "INSERT INTO public.cor_ocupatii (cod, denumire, denumire_cauta) VALUES (%s,%s,%s)",
                [(c, d, cor_api.normalizeaza(d)) for c, d in perechi])
        conn.commit()
        print("incarcat in public.cor_ocupatii: %d ocupatii" % cor_api.nr_ocupatii(conn))


if __name__ == "__main__":
    main()
