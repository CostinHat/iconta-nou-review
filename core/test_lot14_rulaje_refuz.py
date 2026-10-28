# -*- coding: utf-8 -*-
"""[lotul 14, deficiențele 683 + 695] Declarația sau situația a cărei perioadă începe înainte de preluare se REFUZĂ (nu doar se avertizează),
cu trimitere la Import date › Solduri inițiale; după import, bilanțul, D101 și D100 pe profit folosesc rulajele importate.

Comanda Costin 14.1, verbatim: „La 683 și 695 nu e nevoie de import nou: Import date › Solduri inițiale primește deja rulajele anului.
Dovedește cu un test pe o balanță importată că, după import, bilanțul și D100 pe perioade dinainte de preluare folosesc rulajele importate.”
· 683: „după 31.12 bilanțul pe 2026 ar ieși doar cu sept.–dec., fără avertisment. Trebuie refuz cu trimitere la Import date › Solduri
inițiale; după import, bilanțul folosește rulajele importate.” · 695: „F1, D100 T3/2026 (iul–sep): baza = 707 1.000 (doar septembrie),
impozit 10 lei la 1%, validat și gata de «Pune în De depus», fără niciun avertisment că veniturile din iulie–august lipsesc. Orice
declarație sau situație a cărei perioadă începe înainte de preluare trebuie refuzată (sau completată cu rulajele importate)”.

Fixtura e a lui 425 (`core/test_lot10_rulaje_preluate.py`): balanța SAGA la 30.09.2026 (707 = 180.000 de la 1 ianuarie, închis lunar în 121),
o notă validată în octombrie (707 + 10.000). `cu_rulaje` = balanța cu soldurile inițiale ale anului și rulajele; `fara_rulaje` = numai
soldurile finale. Regula ferestrei (`rulaje_preluate`): rulajele importate intră numai într-o fereastră care cuprinde întreg intervalul
[01.01, 30.09] — anul (bilanț, D101) și cumulul D100 pe profit; D100 micro pe un trimestru care începe după 1 ianuarie nu le poate folosi
(un cumul nu se împarte pe luni), deci rămâne refuzat.
MUTAȚII (în fiecare test): refuzul scos din `d100.genereaza` / `d101.genereaza` / `bilant_api.coloana_curenta_f10`; regula ferestrei
(`lipsa_in_fereastra`) care ignoră importul.
"""
import datetime
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant as _b, bilant_api as ba, d100, d101, db as _db, rulaje_preluate as rp
from core.common import Perioada
from core.erori import RefuzGenerare
from core.test_lot10_rulaje_preluate import SCH, cu_rulaje, fara_rulaje  # noqa: F401 — fixturile lotului 10 (425)


def _genereaza(fn, perioada, regim="micro"):
    """Generatorul `fn` (d100.genereaza / d101.genereaza) pe firma de probă, cu regimul dat; întoarce rezultatul sau excepția."""
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET regim_fiscal = %s WHERE id = 1", (regim,))
        try:
            return fn(conn, SCH, perioada)
        except Exception as e:  # noqa: BLE001 — testul examinează excepția
            return e
        finally:
            conn.rollback()


def test_683_bilantul_fara_rulaje_preluate_se_refuza_cu_trimitere_la_import(fara_rulaje):
    """683: balanța importată are numai soldurile finale la 30.09.2026 — bilanțul pe 2026 ar ieși numai cu octombrie–decembrie. Refuz cu
    motivul „Rulajele anului până la preluare”, cu intervalul lipsă și trimiterea la Import date › Solduri inițiale. MUTAȚIE: motivul scos
    din `coloana_curenta_f10` -> pică."""
    with _db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(_b.BilantOprit) as e:
                ba.coloana_curenta_f10(cur, SCH, 2026, "s1005")
        conn.rollback()
    m = str(e.value)
    assert "începe înainte de preluarea firmei" in m and "de la 01.01.2026 până la 30.09.2026" in m, m
    assert "Import date › Solduri inițiale" in m, m


def test_683_dupa_import_bilantul_foloseste_rulajele_importate(cu_rulaje):
    """683, după import: fereastra anului cuprinde întreg intervalul preluat, deci nu mai lipsește nimic; F20 are cifra de afaceri din rulajele
    importate (707 = 180.000 + 10.000 din octombrie), nu numai octombrie. MUTAȚIE: `_rp.rulaje` scos din `bilant_api.rulaje_67` -> 707 =
    10.000 -> pică."""
    with _db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            lipsa = rp.lipsa_in_fereastra(cur, SCH, datetime.date(2026, 1, 1), datetime.date(2027, 1, 1))
            rl = ba._rulaje_67(cur, SCH, 2026)
            try:
                ba.coloana_curenta_f10(cur, SCH, 2026, "s1005")
                motive = ""
            except _b.BilantOprit as e:    # alte motive (clase 6 / 7 neînchise înainte de 31.12) pot exista; nu cel al rulajelor
                motive = str(e)
        conn.rollback()
    assert lipsa is None and rl["707"] == (Decimal(0), Decimal(190000)), (lipsa, rl["707"])
    assert "începe înainte de preluarea firmei" not in motive and "Rulajele anului până la preluare" not in motive, motive


def test_695_d100_micro_pe_trimestrul_cu_luni_dinainte_de_preluare_se_refuza(fara_rulaje):
    """695: D100 micro T3/2026 (iul–sep) cu evidența de la 01.10 (preluare 30.09 în fixtură: T3 e întreg dinainte). Refuz, nu un D100 pe 0.
    T4 (începe după preluare) se generează. MUTAȚIE: refuzul scos din `d100.genereaza` -> T3 se generează -> pică."""
    r3 = _genereaza(d100.genereaza, Perioada(2026, trim=3))
    assert isinstance(r3, RefuzGenerare), r3
    assert "începe înainte de preluarea firmei" in str(r3) and "Import date › Solduri inițiale" in str(r3), str(r3)
    r4 = _genereaza(d100.genereaza, Perioada(2026, trim=4))
    assert isinstance(r4, tuple) and "<declaratie100" in r4[0], r4      # începe după preluare: se generează (octombrie 10.000)


def test_695_d100_micro_cu_import_ramane_refuzat_pe_trimestrul_care_nu_incepe_la_1_ianuarie(cu_rulaje):
    """695, după import: rulajele sunt un cumul 01.01–30.09 și nu se pot împărți pe luni — T3 micro nu se poate calcula din ele, deci se
    refuză, cu motivul numit (nu cu „importă”, care ar trimite omul în cerc). MUTAȚIE: `cu_import` ignorat în `text_lipsa` -> pică."""
    r3 = _genereaza(d100.genereaza, Perioada(2026, trim=3))
    assert isinstance(r3, RefuzGenerare), r3
    assert "nu se poate împărți pe luni" in str(r3) and "Depune-o din evidența de dinainte de preluare" in str(r3), str(r3)


def test_695_d100_pe_profit_foloseste_rulajele_importate(cu_rulaje):
    """695, D100 pe profit (cumulul 01.01–sfârșitul trimestrului): după import fereastra T3 cuprinde [01.01, 30.09], deci NU se refuză și
    impozitul cumulat pleacă de la rulajele importate (180.000 venituri); T2 (până la 30.06) nu le poate folosi și se refuză. MUTAȚIE:
    `lipsa_in_fereastra` care ignoră importul -> T3 refuzat -> pică."""
    r3 = _genereaza(d100.genereaza, Perioada(2026, trim=3), regim="profit")
    assert isinstance(r3, tuple) and "<declaratie100" in r3[0], r3
    # rezultatul contabil cumulat 01.01–30.09 din rulajele importate = 180.000 − 136.675 = 43.325; minus rezerva legală (5%, plafon 20% din
    # capitalul de 10.000 = 2.000, CF art.26 alin.(1) lit.a) = 41.325; × 16% = 6.612. Fără rulajele importate ar fi fost 0 (numai octombrie).
    assert r3[1].profit["cumulat"] == 6612, r3[1].profit["cumulat"]
    r2 = _genereaza(d100.genereaza, Perioada(2026, trim=2), regim="profit")
    assert isinstance(r2, RefuzGenerare), r2


def test_695_d100_pe_profit_fara_import_se_refuza(fara_rulaje):
    """695, fără import: D100 pe profit T3 cumulează de la 01.01 și n-are rulajele — refuz cu trimiterea la import."""
    r3 = _genereaza(d100.genereaza, Perioada(2026, trim=3), regim="profit")
    assert isinstance(r3, RefuzGenerare) and "Import date › Solduri inițiale" in str(r3), r3


def test_d101_anul_cu_preluare_la_mijloc_se_refuza_fara_import_si_se_genereaza_dupa(fara_rulaje):
    """D101 pe 2026: fără rulajele anului se refuză (nu doar avertisment); cu ele (fixtura `cu_rulaje`, testul lui 425) se generează.
    MUTAȚIE: refuzul scos din `d101.genereaza` -> pică."""
    r = _genereaza(d101.genereaza, Perioada(2026), regim="profit")
    assert isinstance(r, RefuzGenerare) and "Import date › Solduri inițiale" in str(r), r
