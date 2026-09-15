# -*- coding: utf-8 -*-
"""Program de linie de comandă: aplică DDL-ul stării partajate (tabelele de stare între procese).

[E2b, 15.09.2026] Trăia în `core/stare_partajata.py`, care e DEPOZIT: toate funcțiile lui primesc cursorul
apelantului, iar singura conexiune proprie era aici, în `main()`. Un program are voie să-și
deschidă conexiunea — un depozit, nu. *Codul e mutat verbatim; ce face nu s-a schimbat.*

Rulare:  `./venv/bin/python scripts/stare_partajata_cli.py`
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import stare_partajata as _m  # noqa: E402


def main():
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        _m.aplica_ddl(conn)
    print("stare_partajata: gata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
