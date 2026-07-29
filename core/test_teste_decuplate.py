# -*- coding: utf-8 -*-
"""Garda PERMANENTA (29.07.2026): niciun test nu depinde de o firma PERSISTENTA din baza.

DE CE: probele fiscale care rulau pe tenant_001/002/003 testau PREZENTA firmei, nu logica. Dupa
un wipe (0 firme) sareau tacit sau picau. Regula: un test care atinge baza isi CONSTRUIESTE
subiectul - schema efemera din tenant_template (COMISA + DROP pentru scriitori care isi deschid
propria conexiune; ROLLBACK pentru cititori care primesc conn) sau fake cursor - si nu depinde de
nicio firma din baza.

CLASA STRUCTURALA, nu simptom (vezi DECIZII 29.07): un grep naiv dupa "tenant_00X" da fals-pozitive
(numele pasat ca STRING unei functii pure de audit de schema). Semnatura REALA a cuplarii e
ATINGEREA bazei pe o schema persistenta:
  (a) get_conn("tenant_00X")                                    - sesiune legata de schema persistenta
  (b) SQL FROM/INTO/JOIN/UPDATE/DELETE FROM tenant_00X.<tabela> - interogare pe date persistente
Numele efemere (ztest_*) si argumentele-string catre functii pure NU sunt cuplare.
"""
import pathlib
import re

_RAD = pathlib.Path(__file__).resolve().parent
_ACEST_FISIER = pathlib.Path(__file__).name

# (a) conexiune pe schema tenant persistenta; (b) SQL calificat pe o schema tenant persistenta.
_CUPLARE = re.compile(
    r'get_conn\(\s*["\']tenant_0\d\d["\']'
    r'|(?:FROM|INTO|JOIN|UPDATE|DELETE\s+FROM)\s+tenant_0\d\d\.',
    re.IGNORECASE)


def _linii_cuplate(text):
    gasite = []
    for nr, linie in enumerate(text.split("\n"), 1):
        if linie.strip().startswith("#"):     # comentariile mentioneaza legitim "decuplat de tenant_00X"
            continue
        if _CUPLARE.search(linie):
            gasite.append((nr, linie.strip()))
    return gasite


def test_niciun_test_nu_depinde_de_firma_persistenta():
    vinovati = []
    for f in sorted(_RAD.glob("test_*.py")):
        if f.name == _ACEST_FISIER:
            continue
        for nr, s in _linii_cuplate(f.read_text(encoding="utf-8")):
            vinovati.append("%s:%d  %s" % (f.name, nr, s))
    assert not vinovati, (
        "teste cuplate la o firma PERSISTENTA (construieste-ti subiectul: schema efemera din "
        "tenant_template sau fake cursor; tipar in test_spv_receive / test_control_incrucisat):\n"
        + "\n".join(vinovati))


def test_garda_chiar_prinde_cuplarea():
    """Mutatie: garda ar fi inutila daca regex-ul nu prinde nimic. Dovada pe AMBELE semnaturi si
    dovada ca NU da fals-pozitiv pe nume ca argument-string (functie pura), efemer sau comentariu."""
    assert _linii_cuplate('    with db.get_conn("tenant_002") as c:')                 # (a)
    assert _linii_cuplate('        cur.execute("SELECT * FROM tenant_003.facturi")')  # (b)
    assert not _linii_cuplate('    sug = a.sugereaza_alter("tenant_003", d, ref)')    # pur: bare, fara verb SQL
    assert not _linii_cuplate("    a._norm_default(\"nextval('tenant_002.t_id_seq')\", \"tenant_002\")")  # pur
    assert not _linii_cuplate('    r = ap.verifica_rip(cs, "ztest_audit_rip")')       # schema efemera
    assert not _linii_cuplate('    # DECUPLAT de tenant_002 (mentiune in comentariu)')  # comentariu
