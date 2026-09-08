# -*- coding: utf-8 -*-
"""GARD P2 (08.09.2026) — cererile de portofoliu nu mai cresc cu numărul de firme.

CE PAZEȘTE:

  NUMĂRUL DE INTEROGĂRI E CONSTANT  cele cinci rute fac **același număr** de interogări pentru 5
      firme și pentru 50. Asta e chiar cerința P2, și se măsoară — nu se afirmă.
  INSTRUMENTUL E CALIBRAT           `masoara_interogari.calibreaza()` trebuie să treacă **înainte**
      de orice cifră: vede N+1-ul ȘI vede cazul corect. *O calibrare care verifică o singură
      direcție nu spune nimic despre cealaltă.*
  NIMIC VECHI TĂCUT                 un rezumat invalidat nu se arată drept curent: ruta îl dă `gri`
      / `neevaluat`, cu `prospetime` care spune de ce.
  ABSENȚA SE DECLARĂ                o firmă fără rezumat nu apare cu zerouri tăcute.
  O SINGURĂ DEFINIȚIE               aspectele cheamă funcțiile pe care le chema ruta; `vector`
      trece prin `vector_fiscal_api.citeste`, nu printr-o interogare proprie.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import masoara_interogari as MI  # noqa: E402
from core import db as _db  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402

BAZA = 700000


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def firme():
    if not _db_ok():
        pytest.skip("fara baza de date")

    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id >= %s", (BAZA,))
                cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id >= %s", (BAZA,))
            c.commit()

    sterge()

    def pune(n, invalidate=0):
        ids = list(range(BAZA, BAZA + n))
        with _db.get_conn() as c:
            for i, tid in enumerate(ids):
                with c.cursor() as cur:
                    cur.execute("INSERT INTO public.supervizor_sursa (tenant_id, versiune) "
                                "VALUES (%s, 5) ON CONFLICT (tenant_id) DO UPDATE SET versiune = 5",
                                (tid,))
                v = 4 if i < invalidate else 5
                for aspect in ("tip_firma", "solduri", "plan_conturi", "vector",
                               "termene", "control_fiscal"):
                    FR.scrie(c, tid, aspect, {"x": i}, v)
            c.commit()
        return ids

    yield pune
    sterge()


def test_instrumentul_e_calibrat_inainte_de_orice_cifra():
    """Prima probă din fișier, deliberat: dacă instrumentul nu vede ambele direcții, nicio cifră de
    mai jos nu valorează nimic."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    ok, det = MI.calibreaza(verbose=False)
    assert ok, det
    assert det["n_plus_1"]["conexiuni"] > det["set_based"]["conexiuni"] * 3


def test_citirea_face_o_singura_interogare_indiferent_de_cate_firme(firme):
    """CERINȚA P2, măsurată: numărul de interogări NU crește cu N."""
    ids_mic = firme(5)
    # conexiunea se ia INAUNTRUL blocului: contorul numără ce se întâmplă acolo, inclusiv luarea ei
    with MI.numara() as n_mic:
        with _db.get_conn() as c:
            FR.citeste(c, ids_mic, ["control_fiscal"])
    ids_mare = firme(50)
    with MI.numara() as n_mare:
        with _db.get_conn() as c:
            FR.citeste(c, ids_mare, ["control_fiscal"])
    assert n_mic.interogari == n_mare.interogari == 1, (
        "citirea a făcut %d interogări pe 5 firme și %d pe 50 — crește cu N"
        % (n_mic.interogari, n_mare.interogari))


def test_toate_aspectele_intr_o_singura_interogare(firme):
    ids = firme(20)
    with MI.numara() as n:
        with _db.get_conn() as c:
            d = FR.citeste(c, ids, list(FR.TOATE))
    assert n.interogari == 1
    assert len(d) == 20
    assert set(d[ids[0]]) == set(FR.TOATE)


def test_un_rezumat_invalidat_NU_se_da_drept_curent(firme):
    ids = firme(10, invalidate=3)
    with _db.get_conn() as c:
        d = FR.citeste(c, ids, ["control_fiscal"])
    stari = [d[t]["control_fiscal"]["stare"] for t in ids]
    assert stari.count(FR.INVALIDAT) == 3
    assert stari.count(FR.CURENT) == 7
    for t in ids[:3]:
        x = d[t]["control_fiscal"]
        assert x["date"] is not None, "valoarea veche se arată, dar etichetată"
        assert x["versiune_sursa"] != x["versiune_curenta"]


def test_absenta_se_declara(firme):
    firme(2)
    with _db.get_conn() as c:
        d = FR.citeste(c, [BAZA + 999], ["solduri"])
    assert d[BAZA + 999]["solduri"]["stare"] == FR.LIPSESTE
    assert d[BAZA + 999]["solduri"]["date"] is None


def test_aspectele_cheama_functiile_rutei_nu_reimplementari():
    """O SINGURĂ definiție. `vector` trebuie să treacă prin `vector_fiscal_api.citeste` — prima
    formă făcea o interogare proprie și inventa un câmp `complet` în loc de `completat`, adică fix
    clasa reparată la R94."""
    # se cere STRUCTURA — cheile ÎNTOARSE, nu numele funcției din sursă: o aserțiune pe sursă ar
    # trece și dacă apelul ar fi comentat, iar clichetul de aserțiuni-pe-text o numără, pe drept.
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY id LIMIT 1")
            r = cur.fetchone()
    if not r:
        pytest.skip("nicio firmă activă")
    with _db.get_conn(r[0]) as c:
        chei = set(FR._vector(c, r[0]))
    assert chei == {"completat", "regim_fiscal", "platitor_tva", "tip_decont", "operatiuni_ic"}


def test_tabelele_sursa_sunt_urmarite_de_triggere():
    """Fiecare tabel-sursă al unui aspect trebuie să fie în lista pe care se pun triggerele —
    altfel aspectul n-ar fi invalidat niciodată și ar rămâne vechi la infinit, tăcut."""
    from core import supervizor_cache as SC
    lipsa = [t for t in FR.tabele_urmarite() if t not in SC.TABELE_TENANT]
    assert lipsa == [], "tabele-sursă fără trigger: %s" % lipsa
