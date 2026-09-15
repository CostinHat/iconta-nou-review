# -*- coding: utf-8 -*-
"""Program de linie de comandă: ce se vede acum despre instanțele vii — pentru om și pentru hook.

[E2b, 15.09.2026] Trăia în `core/instante.py`, care e DEPOZIT: toate funcțiile lui primesc cursorul
apelantului, iar singura conexiune proprie era aici, în `main()`. Un program are voie să-și
deschidă conexiunea — un depozit, nu. *Codul e mutat verbatim; ce face nu s-a schimbat.*

Rulare:  `./venv/bin/python scripts/instante_cli.py`
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import instante as _m  # noqa: E402


def main():
    """`python3 -m core.instante` — ce se vede acum. Pentru om si pentru hook."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        _m.aplica_ddl(conn)
        for g, p, c, t in _m.vii(conn):
            print("%s pid=%-7d commit=%s  pornit %s" % (g, p, (c or "?")[:8], t))
        print("lider sanatate: %s" % (_m.cine_e_lider(conn, "sanatate"),))
    return 0


if __name__ == "__main__":
    sys.exit(main())
