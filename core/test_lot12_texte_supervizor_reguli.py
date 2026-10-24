# -*- coding: utf-8 -*-
"""GARD [lotul 12, C132] — rezultatul persistat al supervizorului urmează CODUL, nu numai datele.

C132: textele axei D101 („Nu ma pronunt inca: D101 declara…”) au fost reparate în `control_incrucisat.py`, dar ecranul Supervizor citește
rezultatul PERSISTAT (`public.supervizor_rezultat`), invalidat până azi numai de o scriere în datele firmei. O firmă fără scrieri noi ar fi
arătat, „curent”, textul vechi oricât timp — reparația n-ar fi ajuns la datele existente. Acum rezultatul poartă amprenta codului
(`versiune_reguli` = `firma_rezumat.COD`, aceeași amprentă ca rezumatele portofoliului, deficiențele 156/173): alta decât a codului de
acum -> `invalidat`, iar lucrătorul îl ia la recalculat.

Firmele probei sunt sintetice (tenant_id 999201/999202, fără firmă în `public.tenants`), scoase la final; perioada e 2099/12."""
import pytest

from core import db as _db
from core import firma_rezumat as FR
from core import supervizor_cache as SC

TID_VECHI, TID_NOU = 999201, 999202
AN, LUNA = 2099, 12


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
                cur.execute("DELETE FROM public.supervizor_rezultat WHERE tenant_id = ANY(%s)", ([TID_VECHI, TID_NOU],))
                cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id = ANY(%s)", ([TID_VECHI, TID_NOU],))
            c.commit()
    sterge()
    yield
    sterge()


def _pune(tid, rezultat_brut=None):
    """Un rezultat calculat pe aceeași versiune a DATELOR ca sursa (deci „curent” după vechea regulă). `rezultat_brut` = rândul scris
    direct, ca de codul de dinainte (fără `versiune_reguli`)."""
    with _db.get_conn() as c:
        SC.marcheaza_schimbat(c, tid)
        v = SC.versiune_sursa(c, tid)
        if rezultat_brut is None:
            SC.scrie_rezultat(c, tid, AN, LUNA, {"constatari": [], "rezultat": "FARA_SUBIECT"}, v)
        else:
            import json
            with c.cursor() as cur:
                cur.execute("INSERT INTO public.supervizor_rezultat (tenant_id, an, luna, rezultat, versiune_sursa) "
                            "VALUES (%s, %s, %s, %s::jsonb, %s)", (tid, AN, LUNA, json.dumps(rezultat_brut), v))
        c.commit()


def test_amprenta_regulilor_e_amprenta_codului_portofoliului():
    """O singură amprentă a codului în aplicație (nu a doua): cea a rezumatelor portofoliului."""
    assert SC.VERSIUNE_REGULI == FR.COD


def test_rezultatul_codului_vechi_e_invalidat_si_recalculat(curat):
    """Rezultatul scris de codul de dinainte (fără `versiune_reguli`, cu textul vechi) nu se mai arată ca „curent” și intră la lucrător;
    cel scris de codul de acum e „curent” și nu intră. MUTAȚIE: condiția pe `versiune_reguli` scoasă din `citeste` -> rezultatul vechi
    iese `curent` -> pică; scoasă din `de_recalculat` -> lucrătorul nu-l mai ia -> pică."""
    _pune(TID_VECHI, {"constatari": [{"mesaj": "Nu ma pronunt inca: D101 declara 1.000,00 lei"}], "rezultat": "CONSTATARI"})
    _pune(TID_NOU)
    with _db.get_conn() as c:
        stari = SC.citeste(c, [TID_VECHI, TID_NOU], AN, LUNA)
        de_facut = set(SC.de_recalculat(c, AN, LUNA, limita=100000)) & {TID_VECHI, TID_NOU}
    assert {t: stari[t]["stare"] for t in (TID_VECHI, TID_NOU)} == {TID_VECHI: SC.INVALIDAT, TID_NOU: SC.CURENT}
    assert de_facut == {TID_VECHI}
    assert stari[TID_NOU]["rezultat"]["versiune_reguli"] == SC.VERSIUNE_REGULI
