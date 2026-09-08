# -*- coding: utf-8 -*-
"""GARD P1 (08.09.2026) — rezultatul persistat al supervizorului nu poate minți.

CE PAZEȘTE, și fiecare probă apără o cale de a strica contractul:

  PROSPEȚIMEA SE DERIVĂ   nu există coloană `stare`; `curent` ⇔ versiunea din care s-a calculat ==
                          versiunea sursei. O coloană ar fi a doua sursă de adevăr pentru aceeași
                          propoziție, și prima care rămâne în urmă.
  NIMIC VECHI TĂCUT       o schimbare de sursă face rezultatul `invalidat` **imediat**, iar citirea
                          îl arată etichetat, cu `calculat_la`. *Cerința: o stare „în recalculare"
                          declarată e acceptabilă; una veche și tăcută nu e.*
  IZOLARE ÎNTRE FIRME     o scriere într-o firmă nu invalidează rezultatul alteia. Fără asta,
                          mecanismul ar recalcula portofoliul la fiecare scriere — adică fix ce
                          înlocuiește.
  FAULT-CHECK             o scriere concurentă în timpul citirii nu produce o stare parțial
                          actualizată: rezultatul e o singură valoare `jsonb`, scrisă atomic, iar
                          citirea e o singură interogare într-o singură tranzacție.
  ABSENȚA SE DECLARĂ      o firmă fără rezultat întoarce `lipseste`, nu „fără constatări".
  VERSIUNEA SE IA ÎNAINTE recalcularea ștampilează versiunea citită ÎNAINTE de calcul; altfel un
                          calcul lung ar părea curent deși descrie date de dinaintea ultimei scrieri.
"""
import time

import pytest

from core import db as _db
from core import supervizor_cache as SC

TID_A, TID_B = 999101, 999102
AN, LUNA = 2026, 8


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def curat():
    if not _db_ok():
        pytest.skip("fara baza de date")
    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.supervizor_rezultat WHERE tenant_id = ANY(%s)",
                            ([TID_A, TID_B],))
                cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id = ANY(%s)",
                            ([TID_A, TID_B],))
            c.commit()
    sterge()
    yield
    sterge()


def _pune(tid, versiune_calc, versiune_sursa, constatari=0):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.supervizor_sursa (tenant_id, versiune) VALUES (%s,%s) "
                        "ON CONFLICT (tenant_id) DO UPDATE SET versiune = EXCLUDED.versiune",
                        (tid, versiune_sursa))
        SC.scrie_rezultat(c, tid, AN, LUNA,
                          {"tenant_id": tid, "constatari": [{"x": i} for i in range(constatari)]},
                          versiune_calc)
        c.commit()


def test_absenta_se_declara(curat):
    """[ANTI-VACUU] O firmă fără rezultat nu se confundă cu una fără constatări."""
    with _db.get_conn() as c:
        d = SC.citeste(c, [TID_A], AN, LUNA)
    assert d[TID_A]["stare"] == SC.LIPSESTE
    assert d[TID_A]["rezultat"] is None


def test_curent_cand_versiunile_coincid(curat):
    _pune(TID_A, versiune_calc=5, versiune_sursa=5, constatari=2)
    with _db.get_conn() as c:
        d = SC.citeste(c, [TID_A], AN, LUNA)
    assert d[TID_A]["stare"] == SC.CURENT
    assert len(d[TID_A]["rezultat"]["constatari"]) == 2


def test_o_valoare_veche_NU_se_arata_ca_fiind_curenta(curat):
    """Interdicția, verbatim. Rezultatul se ARATĂ — e ultima măsurătoare bună — dar ETICHETAT."""
    _pune(TID_A, versiune_calc=5, versiune_sursa=5, constatari=2)
    with _db.get_conn() as c:
        SC.marcheaza_schimbat(c, TID_A)      # sursa s-a schimbat
        c.commit()
        d = SC.citeste(c, [TID_A], AN, LUNA)
    assert d[TID_A]["stare"] == SC.INVALIDAT
    assert d[TID_A]["rezultat"] is not None, "valoarea veche se arată, dar etichetată"
    assert d[TID_A]["calculat_la"] is not None, "fără momentul calculului, eticheta n-ar spune nimic"
    assert d[TID_A]["versiune_sursa"] != d[TID_A]["versiune_curenta"]


def test_o_firma_nu_invalideaza_rezultatul_alteia(curat):
    _pune(TID_A, 5, 5)
    _pune(TID_B, 5, 5)
    with _db.get_conn() as c:
        SC.marcheaza_schimbat(c, TID_A)
        c.commit()
        d = SC.citeste(c, [TID_A, TID_B], AN, LUNA)
    assert d[TID_A]["stare"] == SC.INVALIDAT
    assert d[TID_B]["stare"] == SC.CURENT, "invalidarea s-a scurs la o firmă neatinsă"


def test_de_recalculat_le_gaseste_pe_cele_invalidate(curat):
    _pune(TID_A, 5, 5)
    _pune(TID_B, 5, 5)
    with _db.get_conn() as c:
        SC.marcheaza_schimbat(c, TID_A)
        c.commit()
        ids = SC.de_recalculat(c, AN, LUNA, limita=500)
    assert TID_A in ids
    assert TID_B not in ids


def test_FAULT_scriere_concurenta_nu_da_stare_partiala(curat):
    """FAULT-CHECK cerut: dacă sursa se schimbă în timp ce rezultatul e citit, cititorul nu primește
    o stare parțial actualizată.

    Se citește de N ori în timp ce, între citiri, sursa e mutată și rezultatul rescris. Se cere ca
    FIECARE citire să fie una dintre cele două stări COERENTE — niciodată „rezultat vechi, declarat
    curent". Perechea (rezultat, versiune) se citește într-o singură interogare, deci nu există
    fereastră în care jumătate din ea e nouă."""
    _pune(TID_A, versiune_calc=1, versiune_sursa=1, constatari=1)
    vazute = set()
    with _db.get_conn() as cr:
        for i in range(2, 12):
            d = SC.citeste(cr, [TID_A], AN, LUNA)[TID_A]
            n = len(d["rezultat"]["constatari"])
            # invariantul: CURENT ⇒ versiunile coincid. Niciodată vechi-declarat-curent.
            if d["stare"] == SC.CURENT:
                assert d["versiune_sursa"] == d["versiune_curenta"], (
                    "rezultat calculat pe versiunea %s arătat drept CURENT peste versiunea %s"
                    % (d["versiune_sursa"], d["versiune_curenta"]))
            vazute.add((d["stare"], n))
            # scriitorul avansează: mai întâi sursa, apoi rezultatul
            with _db.get_conn() as cw:
                SC.marcheaza_schimbat(cw, TID_A)
                cw.commit()
            d2 = SC.citeste(cr, [TID_A], AN, LUNA)[TID_A]
            assert d2["stare"] == SC.INVALIDAT, "sursa s-a mișcat, dar rezultatul se dă drept curent"
            _pune(TID_A, versiune_calc=i, versiune_sursa=i, constatari=i)
            time.sleep(0.005)
    assert len(vazute) > 1, "[anti-vacuu] proba n-a exercitat mai multe stări"


def test_versiunea_se_ia_INAINTE_de_calcul(curat):
    """Recalcularea ștampilează versiunea citită înainte de calcul. Dacă ar citi-o după, un calcul
    lung ar părea curent deși descrie date de dinaintea ultimei scrieri. Cel mai rău caz acceptabil
    e o invalidare în plus — eroarea se împinge spre «mai multă muncă», nu spre «minte»."""
    import inspect
    src = inspect.getsource(SC.recalculeaza_firma)
    i_versiune = src.index("versiune_sursa(c, tenant_id)")
    i_culege = src.index("_culege_firma")
    assert i_versiune < i_culege, "versiunea se citește DUPĂ calcul — rezultatul ar putea minți"
