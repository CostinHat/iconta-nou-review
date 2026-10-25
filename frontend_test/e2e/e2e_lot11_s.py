# -*- coding: utf-8 -*-
"""Lotul 11, subagentul S (comanda Costin 11.1, verbatim în DECIZII „Comanda 11.1”): 451 (ciornele depășite), 452 (motivul fals la returul
din stornare), C75 (borderourile vechi), pct.23 („sursa: facturile” pe nota borderoului). Pașii contabilului pe aplicația din index, pe
baza de TEST, pe firme NOI de test.

DATELE DE PORNIRE care NU vin de pe drumul aplicației, declarate (aplicația de azi nu le mai poate produce — tocmai ele sunt deficiența):
  · 451: ciorna ieșirii de pe Z, scrisă cum o scria codul de dinainte de 438 — documentul „Bon de consum nr 1 din <azi>” în locul
    documentului Z-ului (`UPDATE … document_ref`, pe nota scrisă de aplicație la „Ieșire pe articol”);
  · C75: borderoul scris înainte de lotul 9 — tipul implicit „factura” (exact apelurile de atunci: `creeaza_factura` fără `tip` +
    `nota_facturi_cu_factura`, `creat_la` înainte de 20.10.2026 05:06:34), apoi migrarea (`migrare_borderou_tip_vechi.aplica`, ce face
    rulatorul migrărilor la publicare).
Tot restul (Z-ul, descărcarea, factura, stornarea cu retur, borderoul nou, validarea, refacerea) e pe ecrane / rutele aplicației."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_b import _deschide_rand, _nota_jn
from e2e_bloc_c import firma_cv  # noqa: F401 — fixtura modulului (firma cantitativ-valorică, „Marfa A <n>” în stoc)
from e2e_lot10b_raport_z import _articol, _genereaza, _iesire

AZI = _dt.date.today()


@pytest.fixture(scope="module")
def firma_noua_s():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_stoc(patron, firma_noua_s):
    """Firma nouă, cu Date firmă (stocul la cost), vectorul fiscal, seria și nomenclatorul (pregătirea e idempotentă)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_noua_s)
    return firma_noua_s


def _jurnal(e, firma):
    from e2e_bloc_a import _card
    e.firma(firma["nume"])
    _card(e, "jurnal", "#j-nota-noua")
    return e.pg


def _rand(e, nid):
    """Textul rândului notei din Registrul jurnal, cu detaliul deschis ([lotul 12, 617] tabelul de note: documentul justificativ, sursa,
    liniile și mesajele notei — caseta „depășită” — stau în detaliul rândului, deschis la clic, cum îl deschide contabilul)."""
    return " ".join(_deschide_rand(e, _nota_jn(e, nid)).inner_text().split())


def _iesire_z_veche(patron, f, nr):
    """Z nr. `nr` generat + „Ieșire pe articol” 2 buc (drumul aplicației); apoi ciorna ieșirii rescrisă cum o scria codul de dinainte de
    438 (bonul de consum în locul documentului Z-ului) — data de pornire declarată în antet. Întoarce (id-ul notei, documentul Z-ului,
    id-ul Z-ului)."""
    pg, zid = _genereaza(patron, f, nr)
    _iesire(pg, zid, _articol(f), 2)
    pg.wait_for_function("() => (document.querySelector('#zd-rez') || {innerText: ''}).innerText.includes('Ieșire înregistrată')",
                         timeout=20000)
    s = f["schema"]
    (nid, doc_z), = sql('SELECT i.id, i.document_ref FROM "%s".miscari_stoc m JOIN "%s".inregistrari i ON i.id = m.inregistrare_id '
                        "WHERE m.z_inregistrare_id = %%s" % (s, s), (zid,))
    # date-de-pornire: ciorna ieșirii rescrisă cum o scria codul de dinainte de 438 (451: documentul creat înainte de reparație)
    sql('UPDATE "%s".inregistrari SET document_ref = %%s WHERE id = %%s' % s, ("Bon de consum nr 1 din %s" % AZI.strftime("%d.%m.%Y"), nid))
    # date-de-pornire: fișa de magazie a aceleiași ieșiri, cum o lăsa codul de dinainte de 438 (fără documentul Z-ului)
    sql('UPDATE "%s".miscari_stoc SET document = NULL WHERE inregistrare_id = %%s' % s, (nid,))
    return nid, doc_z, zid


# ================================================================ 451 — Registrul jurnal
def test_def_451_ciorna_depasita_se_arata_pe_rand_se_reface_din_sursa_si_se_valideaza(patron, firma_cv):
    """451. „ciornele generate înainte de o reparație rămân validabile cu regula veche. Cazuri: ieșirea Marfa A din Z 0042 cu «Bon de
    consum nr 1», F1 […]”. Pașii: Raport Z nr. 4511 -> „Generează notă” -> Marfa A, 2 buc -> „Ieșire pe articol” (ciorna, rescrisă cum
    o scria codul vechi — antetul) -> Registru jurnal: pe rândul ciornei, caseta „a fost generată … după o regulă care s-a schimbat … acum
    raportul Z ar scrie documentul justificativ «Raport Z nr 4511 …»”, „Validează” inactiv -> „Refă nota din mișcarea de stoc”: confirmarea
    „Nota a fost refăcută din raportul Z”, nota nouă are documentul Z-ului și se validează (Validată)."""
    f = firma_cv
    nid, doc_z, zid = _iesire_z_veche(patron, f, "4511")
    pg = _jurnal(patron, f)
    _deschide_rand(patron, _nota_jn(patron, nid))                   # [617] caseta „depășită” stă în detaliul rândului: deschis întâi
    pg.wait_for_selector("#jn-depasita-%d" % nid, timeout=20000)
    t = _rand(patron, nid)
    patron.captura("depasita")
    assert "după o regulă care s-a schimbat" in t and ("«%s»" % doc_z) in t and "Bon de consum nr 1" in t, t
    assert pg.is_disabled("[data-val='%d']" % nid)
    pg.click("[data-reface='%d']" % nid)
    pg.wait_for_function("() => (document.querySelector('#j-mesaj') || {innerText: ''}).innerText.includes('Nota a fost refăcută din raportul Z')",
                         timeout=20000)
    s = f["schema"]
    (nou, doc), = sql('SELECT i.id, i.document_ref FROM "%s".miscari_stoc m JOIN "%s".inregistrari i ON i.id = m.inregistrare_id '
                      "WHERE m.z_inregistrare_id = %%s" % (s, s), (zid,))
    assert doc == doc_z and nou != nid and sql('SELECT count(*) FROM "%s".inregistrari WHERE id = %%s' % s, (nid,)) == [(0,)]
    assert pg.locator("#jn-depasita-%d" % nou).count() == 0
    patron.captura("refacuta")
    pg.click("[data-val='%d']" % nou)
    pg.wait_for_function("(id) => { const r = document.querySelector(`tbody.tn-nota[data-nota-id='${id}']`); return r && r.innerText.includes('Validată'); }",
                         arg=nou, timeout=20000)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (nou,)) == [("validata",)]


# ================================================================ 451 — De validat
def test_def_451_de_validat_refuza_ciorna_depasita_si_ofera_refacerea(patron, asistent, firma_cv):
    """451, validarea din coadă. Pașii: asistentul descarcă pe articol un Z nevalidat (ruta ecranului „Ieșire pe articol”); ciorna lui e
    rescrisă cum o scria codul vechi (antetul) și intră în coadă -> contabilul-șef: De validat -> „Validează” pe ea: refuzul „nu se poate
    valida: … după o regulă care s-a schimbat …”, iar sub el „Refă nota din mișcarea de stoc” -> apăsat: confirmarea „Nota a fost refăcută
    din raportul Z … O găsești în Registrul jurnal”, ciorna veche nu mai e în coadă."""
    from e2e_bloc_a import _api, _ok
    from e2e_bloc_d import _atribuie_asistentului, _coada, _in_coada
    f = firma_cv
    try:
        _atribuie_asistentului(f)
    except AssertionError:
        pass   # deja atribuită
    pg, zid = _genereaza(patron, f, "4512")
    asistent.firma(f["nume"])
    r = _ok(_api(asistent, "POST", "/tenants/%d/stocuri/iesire" % f["tenant_id"],
                 {"articol_id": _articol(f), "cantitate": 1, "data": AZI.isoformat(), "z_id": zid}), "ieșirea asistentului")
    nid = r["inregistrare_id"]
    s = f["schema"]
    # date-de-pornire: ciorna asistentului rescrisă cum o scria codul de dinainte de 438 (451: documentul creat înainte de reparație)
    sql('UPDATE "%s".inregistrari SET document_ref = %%s WHERE id = %%s' % s, ("Bon de consum nr 2 din %s" % AZI.strftime("%d.%m.%Y"), nid))
    _in_coada(f, notifica=False)
    _coada(patron)
    pg = patron.pg
    card = pg.locator("#val-note tbody.tn-nota", has_text="Ieșire stoc").filter(has_text="Bon de consum").first   # [622] rândul notei
    card.wait_for(timeout=20000)
    card.locator(".val-aproba").click()
    pg.wait_for_selector("#val-eroare .val-reface", timeout=20000)
    t = " ".join(pg.inner_text("#val-eroare").split())
    patron.captura("refuz")
    assert "după o regulă care s-a schimbat" in t and "Raport Z nr 4512" in t, t
    pg.click("#val-eroare .val-reface")
    pg.wait_for_function("() => document.body.innerText.includes('Nota a fost refăcută din raportul Z')", timeout=20000)
    patron.captura("refacuta")
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE id = %%s' % s, (nid,)) == [(0,)]
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE fel = 'nota' AND perioada = %s AND stare = 'la_senior'",
               ("nota-%d" % nid,)) == [(0,)]


# ================================================================ 452 — returul din stornare se validează
def test_def_452_returul_din_stornare_se_valideaza_fara_motivul_fals(patron, firma_stoc):
    """452. „nota «Retur în stoc Marfa B × 1 buc (stornare)» de pe F1 e refuzată la validare cu un motiv fals («documentul ei a fost
    respins»).” Pașii: articol în stoc -> factură cu 1 buc, „Pleacă marfa acum: Da” -> stornare cu retur -> Registru jurnal: nota „Retur
    în stoc … (stornare)” și contarea facturii de stornare -> „Validează” pe factura stornată, apoi pe retur (619: stornarea după documentul
    stornat; returul și contarea stornării se validează împreună): Validată, fără „documentul ei a fost respins”."""
    from e2e_bloc_a import ARTICOL, _api, _ok, articol_in_stoc, emite_api
    f = firma_stoc
    tid, s = f["tenant_id"], f["schema"]
    aid = articol_in_stoc(patron, f, cantitate=22, pret=10)
    fa = emite_api(patron, f, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                      "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)
    st = _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, fa["factura_id"]), {"retur": True}), "storno cu retur")
    (retur,), = sql('SELECT id FROM "%s".inregistrari WHERE descriere LIKE %%s ORDER BY id DESC LIMIT 1' % s, ("Retur în stoc %(stornare)",))
    (contare_storno,), = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = %%s' % s, (st["factura_id"], "facturi"))
    (contare_orig,), = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = %%s' % s, (fa["factura_id"], "facturi"))
    pg = _jurnal(patron, f)
    # [lotul 12, 619 / clasa 80] „Validează” validează DOCUMENTUL, cu toate notele lui, iar stornarea intră în evidență numai după documentul
    # stornat (`coada_api.refuz_stornare_inaintea_documentului`): întâi factura (contarea + ieșirea din stoc), apoi returul — factura de
    # stornare și returul ei sunt același document, deci „Validează” pe retur le validează pe amândouă
    for nid in (contare_orig, retur):
        pg.wait_for_selector("[data-val='%d']" % nid, timeout=20000)
        assert pg.is_enabled("[data-val='%d']" % nid), _rand(patron, nid)
        pg.click("[data-val='%d']" % nid)
        pg.wait_for_function("(id) => { const r = document.querySelector(`tbody.tn-nota[data-nota-id='${id}']`); return r && r.innerText.includes('Validată'); }",
                             arg=nid, timeout=20000)
    pg.wait_for_function("(id) => { const r = document.querySelector(`tbody.tn-nota[data-nota-id='${id}']`); return r && r.innerText.includes('Validată'); }",
                         arg=contare_storno, timeout=20000)
    patron.captura()
    assert "documentul ei a fost respins" not in pg.inner_text("body")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id IN (%%s, %%s) ORDER BY id' % s, (retur, contare_storno)) == [("validata",), ("validata",)]


# ================================================================ pct.23 — sursa notei borderoului
def test_def_23_nota_borderoului_arata_sursa_borderoul_nu_facturile(patron, firma_stoc):
    """pct.23 („«sursa: facturile» pe nota borderoului”). Pașii: Stocuri -> „Borderou de achiziție” (ruta formularului) -> Registru
    jurnal: rândul notei borderoului spune „sursa: borderoul de achiziție”, nu „sursa: facturile”."""
    from e2e_lot10b_stoc import _borderou_api
    f = firma_stoc
    r = _borderou_api(patron, f, furnizor_nume="Ion Sursa", articol="porumb E2E", cantitate=50)
    pg = _jurnal(patron, f)
    nid = r["inregistrare_id"]
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % nid, timeout=20000)
    t = _rand(patron, nid)                                          # [617] „sursa: …” stă în detaliul rândului
    patron.captura()
    assert "sursa: borderoul de achiziție" in t and "sursa: facturile" not in t, t


# ================================================================ C75 — borderourile vechi
def test_def_c75_borderoul_vechi_e_borderou_iar_urmatorul_primeste_numarul_urmator(patron, firma_stoc):
    """C75 („DA. Migrează borderourile vechi pe toate firmele”). Pașii: un borderou scris înainte de lotul 9 (BA-7, tipul „factura” —
    antetul) -> migrarea -> Registru jurnal: nota lui spune „sursa: borderoul de achiziție” și „Borderou de achiziție BA-7 din …” -> un
    borderou nou din formular, fără număr: primește BA-8 (numerotarea îl vede pe cel vechi), nu un număr deja dat."""
    from core import db, facturi_api, migrare_borderou_tip_vechi as m, repo_contabilitate as rc, tranzactie
    from e2e_lot10b_stoc import _borderou_api
    f = firma_stoc
    s = f["schema"]
    descr = "Achizitie de la neinregistrat - Ion Vechi"
    with db.get_conn(s) as c:
        with c.cursor() as cur:
            tranzactie.fixeaza_schema(cur, s)
        fid = facturi_api.creeaza_factura(c, numar="BA-7", data_emitere=AZI.isoformat(), directie="primita",
                                          linii=[{"descriere": descr, "cantitate": 1, "pret_unitar": "120", "cota_tva": 0}],
                                          tert_nume="Ion Vechi", tert_cui="", status="importata", tert_platitor_tva=False, tert_pf=True)["factura_id"]
        with c.cursor() as cur:
            nid = rc.nota_facturi_cu_factura(cur, s, AZI.isoformat(), fid, descr)[0]
            rc.adauga_linie_furnizor(cur, s, nid, "371", 120)
            # date-de-pornire: borderoul scris înainte de lotul 9 (creat_la în trecut — ora nu se poate produce pe drumul aplicației)
            cur.execute('UPDATE "%s".facturi SET creat_la = %%s WHERE id = %%s' % s, ("2026-10-19 13:39+03", fid))
        c.commit()
    with db.get_conn() as c:
        r = m.aplica(c, s)
        c.commit()
    assert [x["id"] for x in r["convertite"]] == [fid], r
    pg = _jurnal(patron, f)
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % nid, timeout=20000)
    t = _rand(patron, nid)                                          # [617] „sursa: …” și documentul justificativ, în detaliul rândului
    patron.captura("vechi")
    assert "sursa: borderoul de achiziție" in t and "Borderou de achiziție BA-7 din" in t, t
    nou = _borderou_api(patron, f, furnizor_nume="Maria Noua", articol="porumb E2E", cantitate=20)
    assert sql('SELECT numar FROM "%s".facturi WHERE id = %%s' % s, (nou["factura_id"],)) == [("BA-8",)]
