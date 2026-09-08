# -*- coding: utf-8 -*-
"""GARD P2 (08.09.2026, remediat) — modelul de citire al portofoliului.

CE PAZEȘTE, și de ce fiecare rând e aici:

  NUMĂRUL DE INTEROGĂRI E CONSTANT   cele cinci rute fac **același număr** de interogări pentru 5
      firme și pentru 50. Cerința P2, măsurată — nu afirmată.
  INSTRUMENTUL E CALIBRAT            `masoara_interogari.calibreaza()` trebuie să treacă **înainte**
      de orice cifră. *O calibrare care verifică o singură direcție nu spune nimic despre cealaltă.*
  INVALIDAREA E ȚINTITĂ              o scriere într-o sursă invalidează aspectele care o citesc —
      **și numai pe ele**. Ambele direcții, per aspect. Prima formă avea un contor per firmă, deci
      o factură nouă invalida tot; garda de atunci n-ar fi văzut diferența, fiindcă verifica doar
      că invalidarea SE ÎNTÂMPLĂ.
  DEPENDENȚELE SUNT CELE MĂSURATE    registrul din cod se confruntă cu ce a măsurat
      `scripts/scan_dependente.py`. Lista scrisă din memorie a fost greșită o dată (8 tabele din 27);
      de-aia nu se mai crede pe cuvânt.
  TIMPUL E O DEPENDENȚĂ              un verdict de zi calculat ieri NU e curent azi, deși nicio
      sursă nu s-a atins.
  O EROARE NU E UN REZULTAT          calculul care ridică nu produce o stare `curent`.
  UN ASPECT LIPSĂ E VĂZUT            `de_recalculat` pleacă de la (firme × aspecte): o firmă cu 3
      aspecte din 5 nu mai poate rămâne cu celelalte 2 lipsă pe veci.
  DOUĂ TURE NU LUCREAZĂ ACEEAȘI FIRMĂ blocaj consultativ, neblocant.
  NIMIC VECHI TĂCUT                  un rezumat neactualizat nu se dă drept curent, în nicio stare.
  O SINGURĂ DEFINIȚIE                aspectele cheamă funcțiile pe care le chema ruta.
"""
import datetime
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import masoara_interogari as MI  # noqa: E402
from core import db as _db  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402

BAZA = 700000
SCHEMA_PROBA = "proba_p2_rezumat"
TENANT_PROBA = 799001


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _curata_model(c, tid_de_la=BAZA):
    with c.cursor() as cur:
        cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id >= %s", (tid_de_la,))
        cur.execute("DELETE FROM public.firma_sursa_versiune WHERE tenant_id >= %s", (tid_de_la,))
        cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id >= %s", (tid_de_la,))
        cur.execute("DELETE FROM public.firma_tip WHERE tenant_id >= %s", (tid_de_la,))


# ============================================================================
#  FIXTURI
# ============================================================================
@pytest.fixture
def firme():
    """Firme SINTETICE, doar în tabelele modelului: pentru măsurarea căii de citire.

    Nu au schemă și nu au rând în `public.tenants` — n-au nevoie: ce se măsoară aici e forma
    interogării de citire, iar aia nu deschide nicio schemă."""
    if not _db_ok():
        pytest.skip("fara baza de date")

    def sterge():
        with _db.get_conn() as c:
            _curata_model(c)
            c.commit()

    sterge()

    def pune(n, invalidate=0, azi=None):
        azi = azi or datetime.date.today()
        ids = list(range(BAZA, BAZA + n))
        # o sursă a fiecărui aspect primește contor 5; rezumatul se scrie cu versiunea potrivită
        # (curent) sau cu una mai mică (invalidat) — exact ce face recalcularea reală
        with _db.get_conn() as c:
            with c.cursor() as cur:
                for tid in ids:
                    for tabela in FR.tabele_urmarite():
                        cur.execute(
                            "INSERT INTO public.firma_sursa_versiune (tenant_id, tabela, versiune) "
                            "VALUES (%s, %s, 5) ON CONFLICT (tenant_id, tabela) "
                            "DO UPDATE SET versiune = 5", (tid, tabela))
            v = FR.versiuni_aspecte(c, ids[0], list(FR.TOATE)) if ids else {}
            for i, tid in enumerate(ids):
                for aspect in FR.TOATE:
                    vv = v[aspect] - 1 if i < invalidate else v[aspect]
                    FR.scrie(c, tid, aspect, {"x": i}, vv,
                             epoca=FR.epoca_pentru(aspect, azi))
            c.commit()
        return ids

    yield pune
    sterge()


@pytest.fixture
def firma_reala():
    """O firmă cu SCHEMĂ ADEVĂRATĂ și triggere legate, ștearsă la final.

    Invalidarea nu se poate proba pe firme sintetice: triggerul e mecanismul, iar un trigger are
    nevoie de un tabel real în care să se scrie. *O gardă care sare peste mecanism păzește o
    poveste despre el.*"""
    if not _db_ok():
        pytest.skip("fara baza de date")

    # `public.tenants.id` e IDENTITY GENERATED ALWAYS — id-ul se primește, nu se alege. Curățenia
    # pleacă de la `schema_name`, care e al probei, nu de la un id ghicit.
    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (SCHEMA_PROBA,))
                r = cur.fetchone()
                if r:
                    for t in ("firma_rezumat", "firma_sursa_versiune", "supervizor_sursa",
                              "firma_tip"):
                        cur.execute("DELETE FROM public.%s WHERE tenant_id = %%s" % t, (r[0],))
                    cur.execute("DELETE FROM public.tenants WHERE id = %s", (r[0],))
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA_PROBA)
            c.commit()

    sterge()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('CREATE SCHEMA "%s"' % SCHEMA_PROBA)
            # tabelele-sursă de care are nevoie proba; cele care lipsesc sunt sărite de
            # `leaga_triggerele_firma`, deci lipsa lor s-ar citi greșit ca „fără invalidare"
            for t in ("facturi", "solduri_initiale", "plan_conturi", "salariati", "articole"):
                cur.execute('CREATE TABLE "%s".%s (id serial PRIMARY KEY, x integer)'
                            % (SCHEMA_PROBA, t))
            cur.execute('CREATE TABLE "%s".firma_profil (id integer PRIMARY KEY, tip_firma text)'
                        % SCHEMA_PROBA)
            cur.execute('INSERT INTO "%s".firma_profil (id, tip_firma) VALUES (1, %%s)'
                        % SCHEMA_PROBA, ("srl",))
            cur.execute("INSERT INTO public.tenants (schema_name, nume, activ) "
                        "VALUES (%s, 'PROBA P2', true) RETURNING id", (SCHEMA_PROBA,))
            tid = cur.fetchone()[0]
        FR.leaga_triggerele_firma(c, SCHEMA_PROBA, tid)
        c.commit()

    yield tid, SCHEMA_PROBA
    sterge()


def _scrie_toate_curente(tid, azi=None):
    """Pune rezumate CURENTE pentru toate aspectele, la versiunile de acum."""
    azi = azi or datetime.date.today()
    with _db.get_conn() as c:
        v = FR.versiuni_aspecte(c, tid, list(FR.TOATE))
        for a in FR.TOATE:
            FR.scrie(c, tid, a, {"proba": True}, v[a], epoca=FR.epoca_pentru(a, azi))
        c.commit()


def _stari(tid, azi=None):
    with _db.get_conn() as c:
        d = FR.citeste(c, [tid], list(FR.TOATE), azi=azi)
    return {a: d[tid][a]["stare"] for a in FR.TOATE}


# ============================================================================
#  INSTRUMENTUL, ÎNAINTE DE ORICE CIFRĂ
# ============================================================================
def test_instrumentul_e_calibrat_inainte_de_orice_cifra():
    """Prima probă din fișier, deliberat: dacă instrumentul nu vede ambele direcții, nicio cifră de
    mai jos nu valorează nimic."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    ok, det = MI.calibreaza(verbose=False)
    assert ok, det
    assert det["n_plus_1"]["conexiuni"] > det["set_based"]["conexiuni"] * 3


# ============================================================================
#  CITIREA — o interogare, indiferent de N
# ============================================================================
def test_citirea_face_o_singura_interogare_indiferent_de_cate_firme(firme):
    """CERINȚA P2, măsurată: numărul de interogări NU crește cu N."""
    ids_mic = firme(5)
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


# ============================================================================
#  INVALIDAREA E ȚINTITĂ — ambele direcții, per aspect
# ============================================================================
#: (tabela atinsă, aspectele care TREBUIE să se invalideze). Derivat din registru, nu scris —
#: dacă registrul se schimbă, proba se mută cu el, iar o dependență nouă nu poate rămâne nepăzită.
_PROBE_INVALIDARE = ("solduri_initiale", "plan_conturi", "facturi", "salariati", "articole")


@pytest.mark.parametrize("tabela", _PROBE_INVALIDARE)
def test_o_sursa_invalideaza_exact_aspectele_care_o_citesc(firma_reala, tabela):
    """AMBELE DIRECȚII, într-o singură probă: ce trebuie invalidat E, ce nu trebuie NU E.

    Direcția a doua e cea care lipsea. Cu un contor per firmă, orice scriere invalida orice aspect,
    iar o gardă care verifica doar „s-a invalidat" trecea verde pe un model care nu deosebea nimic."""
    tid, schema = firma_reala
    asteptate = set(FR.aspecte_ale_tabelei(tabela))
    assert asteptate, "proba nu are obiect: %s nu e sursă pentru niciun aspect" % tabela
    neasteptate = set(FR.TOATE) - asteptate
    assert neasteptate, ("proba n-ar putea eșua: %s e sursă pentru TOATE aspectele, deci direcția "
                         "a doua n-are ce verifica" % tabela)

    _scrie_toate_curente(tid)
    assert all(s == FR.CURENT for s in _stari(tid).values()), "punct de plecare necurat"

    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".%s (x) VALUES (1)' % (schema, tabela))
        c.commit()

    stari = _stari(tid)
    invalidate = {a for a, s in stari.items() if s != FR.CURENT}
    assert invalidate == asteptate, (
        "scrierea în %s a invalidat %s, dar sursele ei sunt ale aspectelor %s"
        % (tabela, sorted(invalidate), sorted(asteptate)))


def test_o_scriere_intr_o_sursa_a_altui_aspect_nu_atinge_solduri(firma_reala):
    """Instanța numită în comandă, scrisă separat fiindcă e chiar defectul raportat:
    *o factură nouă nu are voie să invalideze un aspect care nu citește facturi.*"""
    tid, schema = firma_reala
    _scrie_toate_curente(tid)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".facturi (x) VALUES (1)' % schema)
        c.commit()
    stari = _stari(tid)
    assert stari["solduri"] == FR.CURENT
    assert stari["plan_conturi"] == FR.CURENT
    assert stari["vector"] == FR.CURENT
    assert stari["control_fiscal"] == FR.INVALIDAT
    assert stari["termene"] == FR.INVALIDAT


def test_contorul_creste_o_data_per_INSTRUCTIUNE_nu_per_rand(firma_reala):
    """STATEMENT-level: un import de 5.000 de facturi ridică contorul o dată, nu de 5.000 de ori."""
    tid, schema = firma_reala
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT versiune FROM public.firma_sursa_versiune "
                        " WHERE tenant_id=%s AND tabela='facturi'", (tid,))
            r = cur.fetchone()
            inainte = r[0] if r else 0
            cur.execute('INSERT INTO "%s".facturi (x) SELECT generate_series(1, 500)' % schema)
        c.commit()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT versiune FROM public.firma_sursa_versiune "
                        " WHERE tenant_id=%s AND tabela='facturi'", (tid,))
            dupa = cur.fetchone()[0]
    assert dupa == inainte + 1, "500 de rânduri au ridicat contorul cu %d" % (dupa - inainte)


# ============================================================================
#  TIMPUL E O DEPENDENȚĂ
# ============================================================================
def test_un_verdict_de_zi_calculat_ieri_nu_e_curent_azi(firma_reala):
    """Fără nicio scriere în bază: doar s-a schimbat ziua.

    Aspectele grele primesc `azi` și răspund „la termen / întârziat" **relativ la el**. Prima formă
    n-avea nicio dependență de ceas, deci un rezultat de ieri se arăta `curent` la nesfârșit."""
    tid, _schema = firma_reala
    ieri = datetime.date.today() - datetime.timedelta(days=1)
    _scrie_toate_curente(tid, azi=ieri)

    stari_ieri = _stari(tid, azi=ieri)
    assert stari_ieri["termene"] == FR.CURENT
    assert stari_ieri["control_fiscal"] == FR.CURENT

    stari_azi = _stari(tid, azi=datetime.date.today())
    assert stari_azi["termene"] == FR.INVALIDAT, "termenele de ieri se dau drept curente azi"
    assert stari_azi["control_fiscal"] == FR.INVALIDAT


def test_aspectele_fara_dependenta_de_timp_NU_se_invalideaza_la_schimbarea_zilei(firma_reala):
    """Direcția a doua: numărul de conturi din plan nu se învechește fiindcă a trecut miezul nopții.

    Fără proba asta, „totul se invalidează zilnic" ar trece la fel de verde ca modelul corect — și
    ar face lucrătorul să recalculeze tot portofoliul în fiecare noapte, degeaba."""
    tid, _schema = firma_reala
    ieri = datetime.date.today() - datetime.timedelta(days=1)
    _scrie_toate_curente(tid, azi=ieri)
    stari = _stari(tid, azi=datetime.date.today())
    assert stari["solduri"] == FR.CURENT
    assert stari["plan_conturi"] == FR.CURENT
    assert stari["vector"] == FR.CURENT


def test_epoca_e_declarata_per_aspect_nu_ghicita():
    """Granularitatea temporală e o proprietate SCRISĂ a aspectului, iar cele grele o au."""
    assert FR.epoca_pentru("solduri", datetime.date(2026, 9, 8)) == ""
    assert FR.epoca_pentru("termene", datetime.date(2026, 9, 8)) == "2026-09-08"
    assert FR.epoca_pentru("control_fiscal", datetime.date(2026, 9, 8)) == "2026-09-08"
    for a in FR.ASPECTE_GRELE:
        assert FR.ASPECTE[a]["timp"] is not None, (
            "%s primește `azi` la calcul, deci trebuie să declare o granularitate de timp" % a)


# ============================================================================
#  O EROARE NU E UN REZULTAT CURENT
# ============================================================================
def test_o_eroare_de_calcul_nu_devine_stare_curenta(firma_reala):
    tid, _schema = firma_reala
    with _db.get_conn() as c:
        v = FR.versiuni_aspecte(c, tid, ["solduri"])
        FR.scrie(c, tid, "solduri", {"eroare": "ZeroDivisionError: proba"}, v["solduri"],
                 epoca=FR.epoca_pentru("solduri", datetime.date.today()),
                 stare_calcul=FR.CALCUL_EROARE, incercari=1)
        c.commit()
    with _db.get_conn() as c:
        d = FR.citeste(c, [tid], ["solduri"])
    x = d[tid]["solduri"]
    assert x["stare"] == FR.EROARE, "eroarea s-a dat drept %r" % x["stare"]
    assert x["stare"] != FR.CURENT
    assert x["incercari"] == 1


def test_o_eroare_e_reincercata_dar_nu_imediat(firma_reala):
    """Pas crescător: o eroare trecătoare nu devine definitivă, dar nici nu arde tura la nesfârșit."""
    tid, _schema = firma_reala
    acum = datetime.datetime.now(datetime.timezone.utc)
    with _db.get_conn() as c:
        v = FR.versiuni_aspecte(c, tid, ["solduri"])
        FR.scrie(c, tid, "solduri", {"eroare": "proba"}, v["solduri"],
                 epoca=FR.epoca_pentru("solduri", datetime.date.today()),
                 stare_calcul=FR.CALCUL_EROARE, incercari=1,
                 urmatoarea_incercare=acum + datetime.timedelta(minutes=5))
        c.commit()
        perechi_acum = FR.de_recalculat(c, 500, acum=acum)
        perechi_dupa = FR.de_recalculat(c, 500, acum=acum + datetime.timedelta(minutes=10))
    assert (tid, "solduri") not in perechi_acum, "reîncercată imediat, fără pas"
    assert (tid, "solduri") in perechi_dupa, "nu mai e reîncercată niciodată"


def test_pasul_de_reincercare_creste():
    a = FR._urmatoarea_incercare(1)
    b = FR._urmatoarea_incercare(3)
    assert b > a, "pasul nu crește: o firmă care crapă ar fi reîncercată la fel de des la infinit"


# ============================================================================
#  LUCRĂTORUL
# ============================================================================
def test_de_recalculat_vede_un_aspect_lipsa_nu_doar_o_firma_lipsa(firma_reala):
    """DEFECTUL raportat: join-ul pe `tenant_id` singur.

    O firmă cu rânduri pentru unele aspecte producea numai acele rânduri, toate cu versiunea
    potrivită — deci firma nu ieșea deloc, iar aspectele lipsă rămâneau `lipseste` pe veci."""
    tid, _schema = firma_reala
    _scrie_toate_curente(tid)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat "
                        " WHERE tenant_id = %s AND aspect = %s", (tid, "plan_conturi"))
        c.commit()
        perechi = FR.de_recalculat(c, 5000)
    assert (tid, "plan_conturi") in perechi, (
        "aspectul lipsă nu e văzut; celelalte fiind curente, firma n-ar mai fi recalculată niciodată")
    assert (tid, "solduri") not in perechi, "aspectele curente nu se recalculează degeaba"


def test_de_recalculat_pleaca_de_la_firme_nu_de_la_contoare(firma_reala):
    """O firmă în care nu s-a scris NICIODATĂ n-are rând de contor — și tocmai ea e necalculată."""
    tid, _schema = firma_reala
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
            cur.execute("DELETE FROM public.firma_sursa_versiune WHERE tenant_id = %s", (tid,))
        c.commit()
        perechi = FR.de_recalculat(c, 5000)
    lipsa = {a for t, a in perechi if t == tid}
    assert lipsa == set(FR.TOATE), "firma fără niciun contor a rămas invizibilă: %s" % sorted(lipsa)


def test_doua_ture_nu_recalculeaza_aceeasi_firma(firma_reala):
    """Blocaj consultativ, NEBLOCANT: a doua tură sare firma, nu așteaptă după ea."""
    tid, _schema = firma_reala
    with _db.get_conn() as c1:
        with c1.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s, %s)", (FR.CHEIE_BLOCAJ, tid))
            assert cur.fetchone()[0] is True
        try:
            r = FR.recalculeaza_lot(limita=5000)
            assert r["sarite_blocate"] >= 1, "a doua tură a intrat peste firma blocată"
        finally:
            with c1.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s, %s)", (FR.CHEIE_BLOCAJ, tid))
            c1.commit()


def test_oprirea_e_curata_si_se_raporteaza(firma_reala):
    """La cerere de oprire, tura se încheie și SPUNE că s-a oprit. Ce n-a apucat rămâne invalidat,
    deci tura următoare îl ia — starea din bază e singurul jurnal de care are nevoie."""
    tid, _schema = firma_reala
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    r = FR.recalculeaza_lot(limita=5000, opreste=lambda: True)
    assert r["oprit"] is True
    assert r["recalculate"] == 0
    with _db.get_conn() as c:
        perechi = FR.de_recalculat(c, 5000)
    assert any(t == tid for t, _a in perechi), "munca nefăcută s-a pierdut"


def test_lotul_margineste_tura_iar_restul_se_raporteaza(firma_reala):
    """Un backlog mare nu se face într-o tură — dar nici nu dispare din vedere.

    Backlogul se PRODUCE aici (cele 5 aspecte ale firmei de probă, șterse), ca proba să nu depindă
    de cât de în urmă e portofoliul real în clipa rulării. *O probă care se sare când portofoliul e
    la zi e o gaură care se deschide singură exact când totul merge bine.*"""
    tid, _schema = firma_reala
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
        tot = FR.de_recalculat(c, 100000)
        ale_mele = [p for p in tot if p[0] == tid]
        assert len(ale_mele) == len(FR.TOATE), "backlogul produs nu se vede întreg"
        assert len(FR.de_recalculat(c, 3)) == 3, "lotul nu mărginește tura"
        assert len(FR.de_recalculat(c, 1)) == 1
    assert len(tot) > 3, "restul rămâne vizibil pentru turele următoare"


# ============================================================================
#  REGISTRUL SE CONFRUNTĂ CU MĂSURĂTOAREA
# ============================================================================
def test_fiecare_tabela_sursa_are_trigger_pe_o_firma_reala(firma_reala):
    """Anti-vacuu: nu se întreabă lista din cod despre ea însăși, ci BAZA despre firmă."""
    tid, schema = firma_reala
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "SELECT c.relname FROM pg_trigger t "
                "  JOIN pg_class c ON c.oid = t.tgrelid "
                "  JOIN pg_namespace n ON n.oid = c.relnamespace "
                " WHERE n.nspname = %s AND t.tgname LIKE 'trg_sursa_%%' AND NOT t.tgisinternal",
                (schema,))
            au = {r[0] for r in cur.fetchall()}
            cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", (schema,))
            exista = {r[0] for r in cur.fetchall()}
    trebuie = set(FR.tabele_cu_trigger()) & exista
    assert trebuie, "proba n-are obiect: schema de probă n-are niciun tabel-sursă"
    assert trebuie - au == set(), "tabele-sursă fără trigger: %s" % sorted(trebuie - au)


def test_aspectele_grele_isi_declara_sursele():
    """Prima formă nu declara NICIUNA pentru cele două aspecte grele — deci nimic nu le invalida.
    `control_fiscal` citește 27 de tabele, măsurat."""
    for a in FR.ASPECTE_GRELE:
        assert FR.ASPECTE[a]["tabele"], "%s nu declară nicio sursă" % a
    assert len(FR.ASPECTE["control_fiscal"]["tabele"]) >= 25, (
        "control_fiscal declară %d tabele; măsurătoarea a găsit 27"
        % len(FR.ASPECTE["control_fiscal"]["tabele"]))


def test_sursele_publice_sunt_urmarite():
    """Sursele din `public` sunt ale MAI MULTOR firme, deci `tenant_id` nu se poate fixa la crearea
    triggerului: se citește din rând, cu trigger ROW-level.

    Se pleacă de la ce DECLARĂ aspectele, nu de la un nume scris aici: un literal ar verifica
    memoria mea despre registru, nu registrul."""
    declarate = {t for a in FR.ASPECTE_GRELE for t in FR.ASPECTE[a]["tabele_public"]}
    assert declarate, "aspectele grele nu declară nicio sursă în `public` — proba n-ar putea eșua"
    assert declarate <= set(FR.tabele_publice_urmarite())
    if not _db_ok():
        pytest.skip("fara baza de date")
    fara_trigger = []
    with _db.get_conn() as c:
        for t in sorted(declarate):
            with c.cursor() as cur:
                cur.execute(
                    "SELECT count(*) FROM pg_trigger tg JOIN pg_class cl ON cl.oid = tg.tgrelid "
                    "  JOIN pg_namespace n ON n.oid = cl.relnamespace "
                    " WHERE n.nspname = 'public' AND cl.relname = %s "
                    "   AND tg.tgname = %s AND NOT tg.tgisinternal",
                    (t, "trg_sursa_pub_%s" % t))
                if cur.fetchone()[0] != 1:
                    fara_trigger.append(t)
    assert not fara_trigger, "surse publice fără trigger: %s" % fara_trigger


def test_ce_nu_se_urmareste_e_o_alegere_scrisa():
    """`tenants`/`users`/`accounting_firms` sunt citite, dar poartă denumirea, nu faptele. Absența
    lor din registru trebuie să fie DECLARATĂ, nu o omisiune."""
    for t in FR.NEURMARITE_PUBLIC:
        assert t not in FR.tabele_publice_urmarite()
        assert FR.aspecte_ale_tabelei(t) == []


# ============================================================================
#  O SINGURĂ DEFINIȚIE
# ============================================================================
def test_aspectele_cheama_functiile_rutei_nu_reimplementari():
    """O SINGURĂ definiție. `vector` trebuie să treacă prin `vector_fiscal_api.citeste`."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ "
                        "  AND schema_name LIKE 'tenant_%' ORDER BY id LIMIT 1")
            r = cur.fetchone()
    if not r:
        pytest.skip("nicio firmă activă")
    with _db.get_conn(r[0]) as c:
        chei = set(FR._vector(c, r[0]))
    assert chei == {"completat", "regim_fiscal", "platitor_tva", "tip_decont", "operatiuni_ic"}


def test_tip_firma_nu_mai_e_aspect_ci_proiectie():
    """Retras deliberat: ca aspect avea o fereastră de învechire, iar `tenantii_userului` cădea în
    ea pe bucla O(N). Ca proiecție întreținută de trigger, fereastra nu există."""
    assert "tip_firma" not in FR.ASPECTE
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.tenants t "
                        "  LEFT JOIN public.firma_tip ft ON ft.tenant_id = t.id "
                        " WHERE t.activ AND ft.tenant_id IS NULL")
            fara = cur.fetchone()[0]
    assert fara == 0, "%d firme active fără proiecție `tip_firma` — lista lor ar arăta gol" % fara
