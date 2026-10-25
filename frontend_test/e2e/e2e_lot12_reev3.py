# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.3 pct.2 (verbatim în DECIZII), pachetul `reev3`: C137.

  * C137 — clasa 216 la reevaluarea în valută. Decizia: „C137: fără marcă nouă acum; notele de reevaluare folosesc tipul de document
    existent.” Nota de reevaluare scrisă înainte ca luna ei să se încheie (cum o scria codul de dinainte de `_cere_luna_incheiata` în
    `uc_reevaluare`) se semnalează în Registrul jurnal ca nota de salarii (C127), iar ciorna ei o scoate migrarea publicării; o altă notă
    de calcul (aceeași sursă „operațiunile speciale”, același tip de document „Notă de calcul”), fără rânduri de reevaluare, nu.

DATE DE PORNIRE fără ecran (declarate): notele de reevaluare se scriu cu funcțiile generatorului (`repo_contabilitate.nota_operatiune_ciorna`
— documentul intern „Notă de calcul” —, `reevaluare_valuta.consemneaza` — rândurile din `reevaluari_valuta`) datate în luna în curs și în
luna viitoare, adică exact starea pe care aplicația de azi n-o mai poate produce (generarea pe o lună neîncheiată e refuzată); validarea
notei vechi se scrie cu UPDATE, ca la C127. Migrarea e chemată cum o cheamă publicarea (`aplica` pe schema firmei).

Temei: OMFP 1802/2014 pct.325 alin.(1) („La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul […] comunicat de
Banca Națională a României din ultima zi bancară a lunii în cauză”); OMFP 1802/2014 pct.69 (nota validată nu se modifică)."""
import calendar as _cal
import datetime as _dt

import pytest

from conftest import firma_noua, sql

AZI = _dt.date.today()
SF_AZI = AZI.replace(day=_cal.monthrange(AZI.year, AZI.month)[1])
_U = (AZI.replace(day=1) + _dt.timedelta(days=32)).replace(day=1)
SF_URM = _U.replace(day=_cal.monthrange(_U.year, _U.month)[1])


@pytest.fixture(scope="module")
def firma_reev3_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_reev3(patron, firma_reev3_noua):
    """Firma nouă, cu Date firmă, vectorul fiscal, seria și nomenclatorul (idempotent)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_reev3_noua, platitor=True, regim_fiscal="profit")
    return firma_reev3_noua


def _nota_reevaluare(cur, s, data, descr, reevaluare=True):
    """Nota scrisă cum o scrie generatorul reevaluării (`uc_reevaluare.reevaluare_valuta_genereaza`): ciornă „operatiuni” cu documentul
    intern „Notă de calcul”, linia 5124 = 765 și (pentru reevaluare) rândul ei din `reevaluari_valuta`."""
    from core import reevaluare_valuta as rv, repo_contabilitate as rc
    iid = rc.nota_operatiune_ciorna(cur, s, data, descr)[0]
    rc.adauga_linie_partener(cur, s, iid, "5124", "765", 30, None, None)
    if reevaluare:
        rv.consemneaza(cur, s, iid, data, [{"factura_id": None, "cont": "5124", "moneda": "EUR", "sold_valuta": 1000,
                                             "curs_evidenta": "4.97", "curs_bnr": "5.0000", "diferenta": 30}])
    return iid


def test_def_c137_vechi_nota_de_reevaluare_scrisa_inainte_de_incheierea_lunii_e_semnalata(patron, firma_reev3):
    """C137, datele de dinainte de reparație: o notă de reevaluare VALIDATĂ datată la sfârșitul lunii viitoare și o ciornă de reevaluare
    a lunii în curs, scrise azi, plus o notă de calcul a dividendelor (aceeași sursă și același tip de document), validată, scrisă azi.
    Pașii: migrarea publicării (`migrare_note_luna_neincheiata.aplica`): ciorna de reevaluare se scoate, nota validată rămâne -> Registru
    jurnal -> „luna →”: rândul notei de reevaluare are caseta „Nota a fost scrisă pe …, înainte ca luna … să se încheie … soldurile în
    valută … cursul BNR …”; rândul dividendelor n-o are -> „← luna”: ciorna de reevaluare a lunii în curs nu mai e."""
    from core import migrare_note_luna_neincheiata as mig
    from conftest import _db
    from e2e_bloc_b import _deschide_rand, _jurnal, _mergi_la_luna, _nota_jn
    s = firma_reev3["schema"]
    d_v, d_c, d_div = "Reevaluare E2E C137 validată", "Reevaluare E2E C137 ciornă", "Dividende E2E C137"
    db = _db()
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % s, (d_v,)):
        with db.get_conn() as c, c.cursor() as cur:
            vid = _nota_reevaluare(cur, s, SF_URM, d_v)
            _nota_reevaluare(cur, s, SF_AZI, d_c)
            div = _nota_reevaluare(cur, s, SF_URM, d_div, reevaluare=False)
            c.commit()
        for iid in (vid, div):
            # date-de-pornire: validarea notei vechi datate în luna viitoare (starea lăsată de codul de dinainte de 216 / C137)
            sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (iid,))
    with db.get_conn() as c:
        r = mig.aplica(c, s)
        c.commit()
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE descriere = %%s' % s, (d_c,)) == [(0,)], r
    vid = sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % s, (d_v,))[0][0]
    div = sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % s, (d_div,))[0][0]
    _jurnal(patron, firma_reev3, (SF_URM.year, SF_URM.month))
    pg = patron.pg
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % vid, timeout=30000)
    _deschide_rand(patron, _nota_jn(patron, vid))
    pg.wait_for_selector("#jn-inainte-%d" % vid, timeout=30000)
    t = " ".join(pg.inner_text("#jn-inainte-%d" % vid).split())
    patron.captura("vechi_nota_reevaluare_semnalata")
    assert t.startswith("Nota a fost scrisă pe ") and ("înainte ca luna %02d/%d să se încheie" % (SF_URM.month, SF_URM.year)) in t, t
    assert "soldurile în valută de la sfârșitul lunii și de cursul BNR din ultima ei zi bancară" in t, t
    assert "nota validată nu se modifică" in t, t
    # nota dividendelor: același document („Notă de calcul”), aceeași sursă — fără rânduri de reevaluare, nu e semnalată
    _deschide_rand(patron, _nota_jn(patron, div))
    assert pg.locator("#jn-inainte-%d" % div).count() == 0
    patron.captura("nota_de_calcul_dividende_nesemnalata")
    _mergi_la_luna(patron, AZI.year, AZI.month)
    assert d_c not in patron.fereastra()
    patron.captura("vechi_ciorna_reevaluare_scoasa")
