# -*- coding: utf-8 -*-
"""core/test_patru_ochi_efectiv.py — GARD: patru-ochi = politica x aplicabilitate, aceeasi in UI si in enforcement.

Audit tenant_006 / cabinet Prisma 1968 (20.08.2026), frontul I1. Pe un cabinet cu UN SINGUR
validator competent, `GET /eu/patru-ochi` intorcea doar flagul brut `{activ}`; UI-ul (validat.js,
cabinet.js) il citea ca atare, iar indicatorul din subbara afisa „Validarea in doi ✓" — MINCINOS:
enforcement-ul (`coada_api.aproba`) folosea deja `activ AND posibil`, deci auto-aprobarea era
permisa. Un cabinet care CREDE ca are control in doi si n-are e mai rau decat un buton lipsa.

Doua laturi gardate aici:
  (A) ADEVARUL INDICATORULUI — UI si enforcement consuma aceeasi stare `efectiv = activ AND posibil`
      din SURSA UNICA `coada_api.patru_ochi_stare`; „✓" nu apare decat pe `efectiv`.
  (B) APLICABILITATEA NU PRODUCE DEADLOCK — `posibil` cere >=2 VALIDATORI activi. Formula veche
      (>=1 pregatitor + >=1 validator + >=2 oameni) devenea True cand un cabinet solo angaja un
      asistent DOAR cu `poate_pregati`: lucrarile pregatite de unicul validator nu mai puteau fi
      aprobate de NIMENI.

Temei: DECIZII 20.08.2026 (patru-ochi: politica explicita x aplicabilitate automata x tranzitie
AFISATA); DS v2.56/v2.59 (no-silent-drop / no-silent-overwrite); DS v2.32 (nimic acceptat tacit);
DECIZII:1168 (capability gardata pe nr. validatori, calculata live).
"""
import io
import os
import re
import pytest

from core import db as _db
from core import coada_api


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _sursa(cale):
    return io.open(cale, encoding="utf-8").read() if os.path.exists(cale) else ""


# ==========================================================================================
#  (B) APLICABILITATE — pe DB reala, tranzactie anulata (ZERO poluare in public)
# ==========================================================================================
@pytest.fixture
def cab():
    """Cabinet efemer + 2 actori. Rollback la final: nimic nu ramane in public."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume, patru_ochi_activ) "
                        "VALUES ('ZTEST 4OCHI', true) RETURNING id")
            fid = cur.fetchone()[0]
            uids = []
            for e, preg, val in (("ztest_4o_patron@invalid", True, True),
                                 ("ztest_4o_asistent@invalid", True, False)):
                cur.execute(
                    "INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                    " accounting_firm_id,activ,poate_pregati,poate_valida,poate_depune) "
                    "VALUES (%s,'x','Z','T','angajat',%s,true,%s,%s,false) RETURNING id",
                    (e, fid, preg, val))
                uids.append(cur.fetchone()[0])
        yield conn, fid, uids
    finally:
        conn.rollback()
        p.putconn(conn)


def _set_valida(conn, uid, val):
    with conn.cursor() as cur:
        cur.execute("UPDATE public.users SET poate_valida=%s WHERE id=%s", (bool(val), uid))


def test_posibil_cere_doi_validatori_nu_doi_oameni(cab):
    """UN validator + UN pregatitor NU face patru-ochi posibil (ar bloca lucrarile validatorului)."""
    conn, fid, (patron, asistent) = cab
    # patron = pregatitor+validator, asistent = doar pregatitor -> 2 oameni, 1 singur validator
    assert coada_api.patru_ochi_posibil(conn, fid) is False, (
        "1 validator + 1 pregatitor da posibil=True -> declaratiile pregatite de unicul validator "
        "nu mai pot fi aprobate de nimeni (DEADLOCK). Vezi DECIZII 20.08.2026.")


def test_posibil_devine_adevarat_la_al_doilea_validator(cab):
    conn, fid, (patron, asistent) = cab
    _set_valida(conn, asistent, True)
    assert coada_api.patru_ochi_posibil(conn, fid) is True


def test_posibil_ignora_validatorii_inactivi(cab):
    conn, fid, (patron, asistent) = cab
    _set_valida(conn, asistent, True)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.users SET activ=false WHERE id=%s", (asistent,))
    assert coada_api.patru_ochi_posibil(conn, fid) is False, (
        "un validator DEZACTIVAT nu poate aproba nimic - nu conteaza la aplicabilitate")


def test_stare_efectiv_e_conjunctia_politica_x_aplicabilitate(cab):
    conn, fid, (patron, asistent) = cab
    st = coada_api.patru_ochi_stare(conn, fid)
    assert set(st) == {"activ", "posibil", "efectiv"}, "starea trebuie sa expuna toate 3 axele"
    assert st["activ"] is True and st["posibil"] is False and st["efectiv"] is False, st
    _set_valida(conn, asistent, True)
    st = coada_api.patru_ochi_stare(conn, fid)
    assert st["posibil"] is True and st["efectiv"] is True, st
    with conn.cursor() as cur:
        cur.execute("UPDATE public.accounting_firms SET patru_ochi_activ=false WHERE id=%s", (fid,))
    st = coada_api.patru_ochi_stare(conn, fid)
    assert st["posibil"] is True and st["activ"] is False and st["efectiv"] is False, st


def _verdict_valid(conn, cid):
    """[R41] «gata de aprobat» include de azi un verdict PROASPAT si VALID.

    Fixtura nu ocoleste poarta (n-ar avea voie: `motiv_trecere` ar consemna o trecere care nu s-a
    intamplat) — pune starea pe care testul o presupunea implicit. Amprenta se calculeaza pe
    payload-ul real al elementului, ca verdictul sa fie despre CONTINUTUL lui."""
    with conn.cursor() as cur:
        cur.execute("SELECT payload->>'xml' FROM public.declaratii_coada WHERE id=%s", (cid,))
        xml = (cur.fetchone() or [None])[0] or ""
    coada_api.scrie_verdict(conn, cid, {"stare": "valid", "erori": ""}, "test-validator", xml)


def test_enforcement_nu_produce_deadlock_pe_cabinet_cu_un_validator(cab):
    """Latura COMPORTAMENTALA: unicul validator isi poate aproba propria lucrare cat timp nimeni
    altcineva nu o poate aproba - altfel declaratia ramane inchisa in coada pentru totdeauna."""
    conn, fid, (patron, asistent) = cab
    with conn.cursor() as cur:
        # fixtura-sintetica-ok: tenant_id NEGATIV (spatiu de id-uri imposibil in productie) + an 2099
        # + tranzactia fixturii se face rollback -> zero risc de coliziune cu o depunere reala.
        cur.execute(
            "INSERT INTO public.declaratii_coada "
            "  (cabinet_id, tenant_id, tip, perioada, stare, creat_de, creat_de_id) "
            "VALUES (%s,-1,'d300','2099-01','la_senior',%s,%s) RETURNING id",
            (fid, str(patron), patron))
        cid = cur.fetchone()[0]
    _verdict_valid(conn, cid)
    r = coada_api.aproba(conn, cid, str(patron), aprobat_de_id=patron)
    assert r.get("ok") is True, (
        "auto-aprobarea refuzata desi NU exista al doilea validator -> declaratia e blocata "
        "definitiv: %r" % (r,))


def test_enforcement_blocheaza_auto_aprobarea_cand_e_efectiv(cab):
    """Reversul: cu doi validatori, pregatitorul NU-si mai aproba propria lucrare."""
    conn, fid, (patron, asistent) = cab
    _set_valida(conn, asistent, True)
    with conn.cursor() as cur:
        # fixtura-sintetica-ok: tenant_id NEGATIV (spatiu de id-uri imposibil in productie) + an 2099
        # + tranzactia fixturii se face rollback -> zero risc de coliziune cu o depunere reala.
        cur.execute(
            "INSERT INTO public.declaratii_coada "
            "  (cabinet_id, tenant_id, tip, perioada, stare, creat_de, creat_de_id) "
            "VALUES (%s,-1,'d300','2099-01','la_senior',%s,%s) RETURNING id",
            (fid, str(patron), patron))
        cid = cur.fetchone()[0]
    _verdict_valid(conn, cid)
    r = coada_api.aproba(conn, cid, str(patron), aprobat_de_id=patron)
    assert r.get("ok") is False and r.get("cod") == "PATRU_OCHI", r
    # dar al DOILEA validator o poate aproba - lucrarile din coada nu se blocheaza retroactiv
    r2 = coada_api.aproba(conn, cid, str(asistent), aprobat_de_id=asistent)
    assert r2.get("ok") is True, (
        "declaratiile deja in coada la trecerea posibil false->true trebuie sa devina aprobabile "
        "de al doilea validator, nu blocate: %r" % (r2,))


# ==========================================================================================
#  (A) ADEVARUL INDICATORULUI + sursa unica (browser-free, pe sursa)
# ==========================================================================================
def test_endpoint_intoarce_toate_trei_axele_din_sursa_unica():
    src = _sursa("main.py")
    assert src, "main.py absent"
    m = re.search(r"@app\.get\(\"/eu/patru-ochi\"\).*?\ndef eu_patru_ochi_stare.*?\n(?=@app\.)",
                  src, re.S)
    assert m, "ruta GET /eu/patru-ochi negasita"
    ruta = m.group(0)
    assert "patru_ochi_stare" in ruta, (
        "GET /eu/patru-ochi nu foloseste sursa unica coada_api.patru_ochi_stare -> poate diverge "
        "de enforcement")
    assert "SELECT patru_ochi_activ" not in ruta, (
        "ruta isi citeste singura flagul brut din DB (a doua definitie a starii)")


# Variabila care DECIDE ce se afiseaza trebuie sa vina din `efectiv`. Politica bruta `activ` se poate
# citi, dar doar intr-o variabila numita explicit ...Politica (folosita ca sa distingem „oprit" de
# „suspendat" in text) - nu ca sa comande ramurile.
_DECIZIE_DIN_ACTIV = re.compile(r"(\w+)\s*=\s*!!\(\s*(?:rpo|st)\s*&&\s*(?:rpo|st)\.activ\s*\)")
_DECIZIE_DIN_EFECTIV = re.compile(r"(\w+)\s*=\s*!!\(\s*(?:rpo|st)\s*&&\s*(?:rpo|st)\.efectiv\s*\)")


def test_frontend_decide_pe_efectiv_nu_pe_flagul_brut():
    """cabinet.js + validat.js decid ce ARATA pe `efectiv`, nu pe politica bruta `activ`."""
    rele = []
    for cale in ("static/js/ecrane/cabinet.js", "static/js/ecrane/validat.js"):
        src = _sursa(cale)
        assert src, "%s absent" % cale
        if not _DECIZIE_DIN_EFECTIV.search(src):
            rele.append("%s: variabila de decizie nu vine din `.efectiv`" % cale)
        for m in _DECIZIE_DIN_ACTIV.finditer(src):
            if not m.group(1).endswith("Politica"):
                rele.append("%s: `%s` decide pe politica bruta `.activ` (redenumeste-o ...Politica "
                            "daca e doar pentru text, sau citeste `.efectiv`)" % (cale, m.group(1)))
    assert not rele, "\n".join(rele)


def test_coada_distinge_oprit_de_suspendat():
    """„Patru-ochi e dezactivat" pe o politica doar SUSPENDATA contrazicea indicatorul din subbara
    si il lasa pe patron sa creada ca i s-a stins setarea."""
    src = _sursa("static/js/ecrane/validat.js")
    assert "patruOchiPolitica" in src, "validat.js nu distinge politica de aplicabilitate"
    assert "suspendat" in src.lower(), "coada n-are text pentru starea suspendata"


def test_indicatorul_nu_afiseaza_bifa_pe_stare_suspendata():
    """Defectul PRINCIPAL al frontului I1: „✓" pe un cabinet fara al doilea validator."""
    src = _sursa("static/js/ecrane/cabinet.js")
    assert src, "cabinet.js absent"
    m = re.search(r"async function _indicatorPatruOchi\(\).*?\n\}\n", src, re.S)
    assert m, "_indicatorPatruOchi negasit"
    ind = m.group(0)
    assert "efectiv" in ind, "indicatorul nu consulta `efectiv` - poate afisa 'activ' pe cabinet solo"
    assert "suspend" in ind.lower(), (
        "indicatorul n-are ramura pentru starea „pornit, dar suspendat: esti singurul validator"
        "\" - trecerea granitei ar fi TACUTA")
    # bifa apare o SINGURA data si numai pe ramura efectiva
    bif = [l for l in ind.splitlines() if "\\u2713" in l or "✓" in l]
    assert len(bif) == 1, "bifa apare pe %d linii - trebuie doar pe ramura efectiva" % len(bif)
    assert "posibil" in ind or "efectiv" in ind


# CITIREA multimii „validatori activi ai cabinetului" = un SELECT peste public.users filtrat pe
# poate_valida. (UPDATE-urile care SCRIU flagul - ex. migrarea B3 - nu sunt o a doua definitie.)
_CITIRE_VALIDATORI = re.compile(
    r"SELECT[^;]{0,300}?FROM public\.users[^;]{0,300}?poate_valida\s*=\s*true", re.S)


def test_o_singura_definitie_a_multimii_de_validatori():
    """Fara logica paralela: „cine poate aproba in acest cabinet" se intreaba intr-un singur loc.

    Era pusa in trei (coada_api pt aplicabilitate, asistenti_api pt educatie, notificari_api pt
    destinatari) - trei copii care puteau diverge tacit."""
    import glob
    surse = sorted(cale for cale in glob.glob("core/*.py") + ["main.py"]
                   if not os.path.basename(cale).startswith("test_")
                   and _CITIRE_VALIDATORI.search(_sursa(cale)))
    assert surse == ["core/coada_api.py"], (
        "multimea de validatori e citita din mai multe locuri (logica paralela, poate diverge "
        "tacit): %s" % surse)


def test_consumatorii_deriva_din_sursa_unica():
    """Educatia si notificarile nu-si mai fac interogarea proprie."""
    rele = []
    for cale, fn in (("core/asistenti_api.py", "_nr_validatori"),
                     ("core/notificari_api.py", "validatorii_cabinetului")):
        s = _sursa(cale)
        m = re.search(r"def %s\(.*?\n(?=\n\ndef |\n\n# )" % fn, s, re.S)
        assert m, "%s: %s negasita" % (cale, fn)
        if "validatori_activi" not in m.group(0):
            rele.append("%s.%s nu deriva din coada_api.validatori_activi" % (cale, fn))
    assert not rele, "\n".join(rele)


def test_tranzitia_in_vigoare_are_punct_de_actiune():
    """Reintrarea in vigoare nu se vede doar in cromul persistent: si ecranul care o produce
    (acordarea dreptului de validare) o anunta."""
    src = _sursa("core/asistenti_api.py")
    assert "patru_ochi_intra_in_vigoare" in src, (
        "set_permisiuni nu semnaleaza trecerea posibil false->true")
    js = _sursa("static/js/ecrane/asistenti.js")
    assert "patru_ochi_intra_in_vigoare" in js, (
        "ecranul Asistenti nu afiseaza intrarea in vigoare in punctul de actiune")
