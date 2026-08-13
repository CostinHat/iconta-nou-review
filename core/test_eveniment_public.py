"""Garda de CONFIDENTIALITATE pentru analytics public (public.eveniment_public).

Invariantul care justifica absenta consimtamantului: tabela stocheaza DOAR evenimentul (ce/de unde/cand) si
NICIUN identificator de persoana. Daca cineva adauga vreodata un camp personal (ip, user_agent, cookie,
sesiune, amprenta, user_id), acest test cade - iar cu el, premisa 'fara date personale = fara consimtamant'.
"""
from core import migrare_eveniment_public as mig

# Nume de coloane care ar transforma tabela in date personale (interzise).
_INTERZISE = ("user_agent", "useragent", "cookie", "session", "sesiune", "amprenta", "fingerprint",
              "user_id", "adresa_ip", "ip_client", "ip_addr", "referer", "referrer", "device")


def test_ddl_nu_are_camp_personal():
    ddl = mig.DDL.lower()
    for camp in _INTERZISE:
        assert camp not in ddl, "DDL eveniment_public NU trebuie sa contina camp personal: %r" % camp
    # 'ip' ca sufix/cuvant separat (evita 'tip'): niciun ' ip ' sau '_ip ' sau '(ip '
    for tipar in (" ip ", "_ip ", "(ip ", " ip\t", "\nip "):
        assert tipar not in ddl, "DDL nu trebuie sa aiba o coloana IP (%r)" % tipar


def test_ddl_are_doar_coloanele_asteptate():
    ddl = mig.DDL.lower()
    assert "eveniment_public" in ddl
    for col in ("id", "tip", "pagina", "creat_la"):
        assert col in ddl, "lipseste coloana asteptata %r" % col


def test_coloane_live_fara_date_personale():
    """Confruntare cu schema REALA din DB (daca e disponibila): setul de coloane = exact cel anonim."""
    try:
        from core import db
        db.init_pool()
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name='eveniment_public'")
            cols = {r[0] for r in cur.fetchall()}
    except Exception:
        import pytest
        pytest.skip("baza indisponibila / tabela neaplicata in acest mediu")
    if not cols:
        import pytest
        pytest.skip("tabela eveniment_public inexistenta in acest mediu (migrare neaplicata)")
    assert cols == {"id", "tip", "pagina", "creat_la"}, "coloane neasteptate in eveniment_public: %r" % cols
