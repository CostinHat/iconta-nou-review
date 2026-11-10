# -*- coding: utf-8 -*-
"""scripts/motiv_oprire.py — motivul opririi lotului pentru alerta lui Costin (17.5-U, U.5). Chemat de scripts/publica_lot.sh pe fișierul cu ieșirea lui scripts/publica_lot.py.

Uz:
  motiv_oprire.py <fișier> [<cod>]   tipărește motivul: textul de după «nepublicat, » din linia «OPRIT — gata: <lot> nepublicat, <motiv>» (scripts/publica_lot.py);
                                     fără o astfel de linie: «publica_lot.py a ieșit cu cod <cod> fără linie OPRIT»."""
import re
import sys

LINIE = re.compile(r"^OPRIT — gata: \S+ nepublicat, (.+)$", re.M)


def motiv_stop(text, cod="?"):
    """PURĂ. Motivul primei linii «OPRIT — gata: <lot> nepublicat, <motiv>» din `text`; fără ea, motivul de rezervă (cu codul de ieșire al lui publica_lot.py)."""
    m = LINIE.search(text)
    return m.group(1).strip() if m and m.group(1).strip() else "publica_lot.py a ieșit cu cod %s fără linie OPRIT" % cod


def main(argv):
    if len(argv) not in (1, 2) or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    try:
        text = open(argv[0], encoding="utf-8", errors="replace").read()
    except OSError:
        text = ""
    print(motiv_stop(text, argv[1] if len(argv) > 1 else "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
