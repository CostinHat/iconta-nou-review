# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (verbatim în DECIZII „Comanda 12.2”), pachetul `stoc2`: 409.1, 619, 450.1, 628 (partea de date).
  * 619 (pct.10) — „Validarea unui document se face împreună cu notele lui (contare, ieșire din stoc, stornare, retur). Azi:
    stornarea/returul (−27,50) s-a validat înaintea documentului stornat, aflat în ciornă, deci 607 e negativ în evidența validată”.
    Pe Registrul jurnal și în „De validat”: stornarea cu retur nu intră în evidență înaintea facturii stornate aflate în ciornă; refuzul
    numește factura și ce e de făcut; după factură, stornarea se validează.
  * 409.1 (pct.1) — „nota 8 e stornată de două ori, ieșirea e dublată, titlul notei 30 e stricat. Cerut: o stornare, o ieșire, titlu
    corect.” Corecția dublată (reparația 409 rulată de două ori pe F1) se scoate cu `scripts/stoc2_409_1_dubluri_corectie.py`.
  * 450.1 (pct.4) + 628 (pct.15) — „Stocuri pe F1 arată tot două rânduri «grau» (200 + 10 kg). Un articol, un rând.”; „două deschideri
    consecutive arată liste diferite; borderourile scriu «buc» la grâu (kg)”. Datele vechi: migrările lotului 12 (`migrare_articole_dublate`,
    `migrare_um_borderou`), chemate cum le cheamă publicarea.
Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`). DATE DE PORNIRE fără ecran
(declarate): notele reparației vechi 409 (fără mișcare de stoc, fără autor), articolele „grau” dublate și borderourile pe „buc” se scriu cu
INSERT — aplicația de acum nu le mai produce (exact asta repară lotul), deci starea de dinainte se reface numai așa. Clientul DANTE
INTERNATIONAL SA, CUI 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md).
Temei 619: OMFP 1802/2014 pct.69 (stornarea „prin corectarea cu semnul minus a operațiunii inițiale”), interpretare cu temei pentru
ordine (`core/coada_api.py`, `MESAJ_STORNAT_IN_CIORNA`). 409.1 / 450.1 / 628: N/A — reguli de produs (CLAUDE.md §9)."""
import datetime as _dt
import importlib.util
import os
import re

import pytest

from conftest import sql
from e2e_bloc_a import ARTICOL, _api, _ok, articol_in_stoc, emite_api, pregateste_firma
from e2e_bloc_b import _de_validat, _jurnal, ana, ana_cont  # noqa: F401 — fixture (ana, ana_cont)

AZI = _dt.date.today()
LUNA = (AZI.year, AZI.month)
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _gata(patron, firma):
    pregateste_firma(patron, firma)   # Date firmă (stocul cantitativ-valoric), vectorul fiscal, seria, nomenclatorul — idempotent


def _factura_cu_marfa(e, firma, aid):
    """Factura emisă de `e` cu articolul din stoc, „Pleacă marfa acum: Da” (contarea + ieșirea 607 = 371, ciorne)."""
    return emite_api(e, firma, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                       "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)


def _note_facturii(firma, fid):
    """(contarea, ieșirea / returul) — notele facturii: contarea (`factura_id`) și nota mișcării ei de stoc."""
    s = firma["schema"]
    contare = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\'' % s, (fid,))[0][0]
    stoc = sql('SELECT DISTINCT inregistrare_id FROM "%s".miscari_stoc WHERE factura_id = %%s AND inregistrare_id IS NOT NULL' % s, (fid,))
    return contare, stoc[0][0]


def _stari(firma, ids):
    return dict(sql('SELECT id, status FROM "%s".inregistrari WHERE id = ANY(%%s)' % firma["schema"], (list(ids),)))


def _eticheta_factura(firma, fid):
    from conftest import _db
    from core import eticheta_nota as et
    with _db().get_conn(firma["schema"]) as c, c.cursor() as cur:
        return et.factura(cur, firma["schema"], fid)


def _stornare_cu_retur(e, firma, fid):
    """„Stornează” -> „Da, marfa se întoarce în stoc” (ruta butonului `fd-storno-ok`, `retur: true`)."""
    return _ok(_api(e, "POST", "/tenants/%d/facturi/%d/storno" % (firma["tenant_id"], fid), {"retur": True}), "stornarea")["factura_id"]


# ── 619 — Registrul jurnal ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_619_jurnalul_refuza_stornarea_inaintea_facturii_stornate(patron, firma_e2e):
    """619. Pașii: contabilul-șef emite o factură cu un articol din stoc („Pleacă marfa: Da”) și o stornează cu retur („Da, marfa se
    întoarce”) -> Registru jurnal -> „Validează” pe returul în stoc: refuzul spune că stornarea intră în evidență numai după factura
    stornată și o numește („validează întâi Factură … apoi stornarea”), iar returul rămâne ciornă -> „Validează” pe ieșirea facturii
    (documentul se validează cu toate notele lui: și contarea) -> „Validează” pe retur: acum trece, cu contarea stornării.
    MUTAȚIE: `refuz_stornare_inaintea_documentului` fără documentul stornat (`d = None`) -> returul se validează primul -> ROȘU."""
    _gata(patron, firma_e2e)
    aid = articol_in_stoc(patron, firma_e2e, cantitate=20, pret=10)
    fid = _factura_cu_marfa(patron, firma_e2e, aid)["factura_id"]
    sid = _stornare_cu_retur(patron, firma_e2e, fid)
    contare, iesire = _note_facturii(firma_e2e, fid)
    contare_s, retur = _note_facturii(firma_e2e, sid)
    eticheta = _eticheta_factura(firma_e2e, fid)
    pg = patron.pg
    _jurnal(patron, firma_e2e, LUNA)
    pg.locator("[data-val='%d']" % retur).scroll_into_view_if_needed()
    with pg.expect_response(lambda r: ("/jurnal/%d/valideaza" % retur) in r.url, timeout=30000) as rr:
        pg.click("[data-val='%d']" % retur)
    assert rr.value.status >= 400, rr.value.text()
    pg.wait_for_function("(t) => document.body.innerText.includes(t)", arg="validează întâi %s, apoi stornarea" % eticheta, timeout=20000)
    patron.captura("refuzul_stornarii")
    assert _stari(firma_e2e, [retur, contare_s, iesire, contare]) == {retur: "ciorna", contare_s: "ciorna", iesire: "ciorna",
                                                                     contare: "ciorna"}
    with pg.expect_response(lambda r: ("/jurnal/%d/valideaza" % iesire) in r.url, timeout=30000) as rr:
        pg.click("[data-val='%d']" % iesire)
    assert rr.value.status == 200, rr.value.text()
    pg.wait_for_function("(i) => !document.querySelector(`[data-val='${i}']`)", arg=iesire, timeout=20000)
    with pg.expect_response(lambda r: ("/jurnal/%d/valideaza" % retur) in r.url, timeout=30000) as rr:
        pg.click("[data-val='%d']" % retur)
    assert rr.value.status == 200, rr.value.text()
    pg.wait_for_function("(i) => !document.querySelector(`[data-val='${i}']`)", arg=retur, timeout=20000)
    patron.captura("stornarea_dupa_factura")
    assert set(_stari(firma_e2e, [retur, contare_s, iesire, contare]).values()) == {"validata"}


# ── 619 — „De validat” ───────────────────────────────────────────────────────────────────────────────────────────────────────
def _rand_coada(e, coada_id):
    """Rândul din „Note de validat” care poartă elementul de coadă (după `data-coada-ids`, nu după text)."""
    pg = e.pg
    pg.wait_for_function("(i) => [...document.querySelectorAll('#val-note tbody.tn-nota')].some(t => "
                         "(t.dataset.coadaIds || '').split(',').includes(String(i)))", arg=coada_id, timeout=20000)
    idx = pg.evaluate("(i) => [...document.querySelectorAll('#val-note tbody.tn-nota')].findIndex(t => "
                      "(t.dataset.coadaIds || '').split(',').includes(String(i)))", coada_id)
    return pg.locator("#val-note tbody.tn-nota").nth(idx)


def test_def_619_coada_refuza_stornarea_inaintea_facturii_stornate(ana, patron, firma_e2e):
    """619, drumul cozii. Pașii: Ana (asistent) emite factura cu marfă și o stornează cu retur -> două documente în „De validat” ->
    contabilul-șef: „Validează” pe stornare întâi: mesajul spune „validează întâi Factură …, apoi stornarea”, iar nimic nu intră în
    evidență -> „Validează” pe factură -> „Validează” pe stornare: amândouă validate, cu toate notele lor.
    MUTAȚIE: `coada_api.aproba` cu notele înghețate (`_jurnal.valideaza` pe fiecare membru, nu `valideaza_documentul`) -> stornarea se
    validează înaintea facturii -> ROȘU."""
    _gata(patron, firma_e2e)
    aid = articol_in_stoc(patron, firma_e2e, cantitate=20, pret=10)
    fid = _factura_cu_marfa(ana, firma_e2e, aid)["factura_id"]
    sid = _stornare_cu_retur(ana, firma_e2e, fid)
    note = _note_facturii(firma_e2e, fid) + _note_facturii(firma_e2e, sid)
    tid = firma_e2e["tenant_id"]
    el = dict(sql("SELECT payload->>'grup', min(id) FROM public.declaratii_coada WHERE tenant_id = %s AND stare = 'la_senior' "
                  "AND payload->>'grup' IN (%s, %s) GROUP BY 1", (tid, "factura-%d" % fid, "factura-%d" % sid)))
    assert set(el) == {"factura-%d" % fid, "factura-%d" % sid}, el
    eticheta = _eticheta_factura(firma_e2e, fid)
    pg = patron.pg
    _de_validat(patron)
    _rand_coada(patron, el["factura-%d" % sid]).locator(".val-aproba").click()
    pg.wait_for_function("(t) => (document.querySelector('#val-eroare') || {innerText: ''}).innerText.includes(t)",
                         arg="validează întâi %s, apoi stornarea" % eticheta, timeout=20000)
    patron.captura("refuzul_stornarii")
    assert set(_stari(firma_e2e, note).values()) == {"ciorna"}
    for grup in ("factura-%d" % fid, "factura-%d" % sid):
        _rand_coada(patron, el[grup]).locator(".val-aproba").click()
        pg.wait_for_function("(i) => ![...document.querySelectorAll('#val-note tbody.tn-nota')].some(t => "
                             "(t.dataset.coadaIds || '').split(',').includes(String(i)))", arg=el[grup], timeout=30000)
    patron.captura("validate_in_ordine")
    assert set(_stari(firma_e2e, note).values()) == {"validata"}


# ── 409.1 — corecția dublată ─────────────────────────────────────────────────────────────────────────────────────────────────
def _script(nume):
    spec = importlib.util.spec_from_file_location(nume.replace(".py", ""), os.path.join(RAD, "scripts", nume))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _corectie_veche(patron, firma, descriere, document, suma):
    """O notă a reparației vechi 409: sursa „stocuri”, fără mișcare, fără autor, validată (pe ruta „Validează”)."""
    s = firma["schema"]
    # date-de-pornire: nota scrisă de scriptul reparației 409 (loturile 9 și 10), fără autor — aplicația n-o mai poate produce
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, \'stocuri\', \'ciorna\', %%s) '
              'RETURNING id' % s, (AZI.isoformat(), descriere, document))[0][0]
    # date-de-pornire: rândul notei de mai sus (607 = 371), cum l-a scris reparația
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'607\', \'371\', %%s)' % s,
        (nid, suma))
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid)), "validarea corecției")
    return nid


def test_def_409_1_corectia_dublata_se_scoate_iar_stornarea_ramasa_are_titlul_corect(patron, firma_e2e):
    """409.1. Starea F1 (date de pornire): ieșirea facturii validată (nr. 8), apoi reparația vechi de două ori: stornare + ieșire, stornare
    + ieșire (30–33, prima stornare cu titlul stricat „Stornare: n (…)ota nr. crt. …”). `scripts/stoc2_409_1_dubluri_corectie.py` (rulat
    cum îl rulează publicarea, pe schema firmei) -> Registru jurnal: o singură stornare, cu titlul „Stornare: nota nr. crt. … (…) — …”,
    și o singură ieșire pe factură în plus față de nota inițială; nicăieri „Stornare: n (”.
    MUTAȚIE: în script, `len(stornari) < 2` -> `< 3` -> corecția dublată rămâne -> ROȘU."""
    from conftest import _db
    _gata(patron, firma_e2e)
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    aid = articol_in_stoc(patron, firma_e2e, cantitate=20, pret=10)
    fid = _factura_cu_marfa(patron, firma_e2e, aid)["factura_id"]
    contare, iesire = _note_facturii(firma_e2e, fid)
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, iesire)), "factura, validată")
    et = sql('SELECT "%s".eticheta_nota(%%s)' % s, (iesire,))[0][0]
    descr = sql('SELECT descriere FROM "%s".inregistrari WHERE id = %%s' % s, (iesire,))[0][0]
    doc_f = _eticheta_factura(firma_e2e, fid)
    suma = sql('SELECT suma FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s, (iesire,))[0][0]
    zi = AZI.strftime("%d.%m.%Y")
    s1 = _corectie_veche(patron, firma_e2e, "Stornare: n (descărcarea facturii, scrisă fără document)ota %s" % et,
                         "Nota %s" % et, -suma)
    r1 = _corectie_veche(patron, firma_e2e, descr, doc_f, suma)
    s2 = _corectie_veche(patron, firma_e2e, "Stornare: nota din %s (%s) — descărcarea facturii, scrisă fără document" % (zi, descr),
                         "Nota din %s" % zi, -suma)
    r2 = _corectie_veche(patron, firma_e2e, descr, doc_f, suma)
    with _db().get_conn(s) as c:
        rez = _script("stoc2_409_1_dubluri_corectie.py").repara(c, s)
        c.commit()
    assert [(g["stornari"], g["inlocuiri"]) for g in rez] == [([s1, s2], [r1, r2])], rez
    pg = patron.pg
    _jurnal(patron, firma_e2e, LUNA)
    pg.locator("[data-nota-id='%d']" % s1).scroll_into_view_if_needed()
    patron.captura("o_stornare_o_iesire")
    txt = " ".join(patron.fereastra().split())
    assert "Stornare: nota %s (%s) — descărcarea facturii, scrisă fără document" % (et, descr) in txt, txt[:600]
    assert "Stornare: n (" not in txt
    assert pg.locator("[data-nota-id='%d']" % s2).count() == 0 and pg.locator("[data-nota-id='%d']" % r2).count() == 0
    assert pg.locator("[data-nota-id='%d']" % r1).count() == 1


# ── 450.1 + 628 — „grau” de două ori, borderourile pe „buc” ──────────────────────────────────────────────────────────────────
def _situatia(e):
    """Rândurile situației stocului: [(articol, UM, cantitate)]."""
    pg = e.pg
    pg.wait_for_selector(".fereastra:last-of-type #s-situatie-tabel", timeout=30000)
    return pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('#s-situatie-tabel tbody tr')]"
                       ".map((r) => [r.cells[0].innerText.trim(), r.cells[1].innerText.trim(), r.cells[2].innerText.trim()])")


def _stocuri(e, firma):
    e.firma(firma["nume"])
    e.pg.click("#fa-stocuri")
    return _situatia(e)


def test_def_450_1_stocuri_arata_un_rand_grau_si_borderourile_kg(patron, firma_e2e):
    """450.1 + 628. Starea F1 (date de pornire): „grau e2e 450” de două ori (200 kg din BA-2, 10 kg din BA-3, create tacit de borderou
    înainte de 450), liniile borderourilor pe „buc”. Stocuri: două rânduri -> migrările lotului 12 (cum le rulează publicarea) -> Stocuri:
    un rând, kg, 210; deschis a doua oară: aceeași listă (628) -> „Borderou de achiziție”: BA-2 / BA-3 cu „kg”.
    MUTAȚIE: `migrare_articole_dublate.grupuri` cu `len(g) > 2` -> două rânduri „grau” rămân -> ROȘU."""
    from conftest import _db
    from core import migrare_articole_dublate as dubl, migrare_um_borderou as um
    _gata(patron, firma_e2e)
    s, den = firma_e2e["schema"], "grau e2e 450"
    if not sql('SELECT 1 FROM "%s".articole WHERE denumire = %%s' % s, (den,)):
        for cant, numar in ((200, "BA-2 E2E 450"), (10, "BA-3 E2E 450")):
            # date-de-pornire: articolul creat tacit de borderoul de dinainte de 450 (aplicația de acum nu-l mai dublează)
            aid = sql('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES (%%s, \'kg\', \'371\', \'607\') '
                      'RETURNING id' % s, (den,))[0][0]
            # date-de-pornire: borderoul vechi, cu linia pe „buc” (C115)
            bid = sql('INSERT INTO "%s".facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip) VALUES '
                      '(%%s, %%s, \'primita\', %%s, 0, \'Maria Ionescu\', \'\', \'importata\', \'borderou\') RETURNING id' % s,
                      (numar, AZI.isoformat(), cant))[0][0]
            # date-de-pornire: linia borderoului vechi
            sql('INSERT INTO "%s".factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, um) VALUES '
                '(%%s, %%s, %%s, 1, 0, \'buc\')' % s, (bid, den, cant))
            # date-de-pornire: intrarea în stoc a borderoului vechi, pe articolul lui
            sql('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, factura_id) VALUES '
                '(%%s, %%s, \'intrare\', %%s, 1, %%s, %%s, %%s)' % s, (aid, AZI.isoformat(), cant, cant, numar, bid))
    inainte = [r for r in _stocuri(patron, firma_e2e) if r[0] == den]
    patron.captura("vechi_doua_randuri")
    assert len(inainte) == 2, inainte
    with _db().get_conn() as c:
        dubl.aplica(c, s)
        um.aplica(c, s)
        c.commit()
    dupa = [r for r in _stocuri(patron, firma_e2e) if r[0] == den]
    patron.captura("un_rand")
    assert len(dupa) == 1 and dupa[0][1] == "kg" and re.match(r"^210(,0+)?$", dupa[0][2]), dupa
    assert [r for r in _stocuri(patron, firma_e2e) if r[0] == den] == dupa      # 628: a doua deschidere, aceeași listă
    pg = patron.pg
    pg.click(".fereastra:last-of-type #s-borderou")
    pg.wait_for_selector("#ba-lista .pf-frand", timeout=30000)
    lista = " ".join(pg.inner_text("#ba-lista").split())
    patron.captura("borderouri_kg")
    assert "200 kg" in lista and "10 kg" in lista and "200 buc" not in lista and "10 buc" not in lista, lista
