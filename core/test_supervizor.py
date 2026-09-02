# -*- coding: utf-8 -*-
"""GARD [01.09.2026]: supervizorul — cele două tării, și confirmarea care rămâne scrisă.

**CE PĂZEȘTE, în ordinea în care s-ar putea strica:**

  1. **Tăria nu se deduce.** Costin o dă, pe tip. Un tip fără tărie atribuită **nu are niciun
     efect** — nu cade pe `EURISTICA` (ar tăcea o constatare certă) și nici pe `CERTA` (ar cere
     confirmări pe care nimeni nu le-a decis). Un tip **necunoscut** ridică.
  2. **Mecanismul funcționează deja**, probat pe un tip **sintetic** cu tărie atribuită — altfel
     gardul ar fi verde fiindcă azi nimic nu e confirmat, iar în ziua în care Costin atribuie prima
     tărie nimic n-ar fi fost verificat.
  3. **Confirmarea acoperă CIFRELE, nu tipul.** O reformulare nu invalidează o confirmare; o cifră
     schimbată o invalidează. Fără asta, „confirmare explicită" ar fi devenit o bifă permanentă.
  4. **Supervizorul nu blochează nimic**, niciodată — nici pe certe.

**MUTAȚIA pe care o cere fiecare:** dacă `cere_confirmare` ar întoarce `True` pe tăria neatribuită,
(1) cade. Dacă amprenta ar include mesajul, (3a) cade; dacă ar ignora cifrele, (3b) cade. Dacă
`_stampileaza` din `control_incrucisat` ar uita o cale de retur, (5) cade — iar supervizorul ar sări
constatarea **tăcut**, care e chiar felul de tăcere care arată ca un răspuns.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import control_incrucisat as _ci  # noqa: E402
from core import supervizor as S  # noqa: E402

#: Constatare-etalon: cifrele care intră în amprentă, fără proză.
_C = {"tip_constatare": "D390_VS_D300_IC", "eticheta": "IC livrări", "stare": "rosu",
      "declarat_d390": 1000, "declarat_d300": 0, "diferenta": 1000}


# ── 1. TĂRIA NU SE DEDUCE ──────────────────────────────────────────────────────────────────────

def test_un_tip_NECUNOSCUT_ridica_nu_cade_pe_implicit():
    """MIEZUL primei reguli. O constatare fără tărie declarată n-are voie să circule: cine o citește
    n-ar putea ști dacă cere confirmare sau doar semnalează."""
    with pytest.raises(S.TipNecunoscut):
        S.tarie("TIP_CARE_NU_EXISTA")
    with pytest.raises(S.TipNecunoscut):
        S.amprenta({"tip_constatare": "TIP_CARE_NU_EXISTA"})
    with pytest.raises(S.TipNecunoscut):
        S.amprenta({"eticheta": "fără tip"})


def test_un_tip_NEATRIBUIT_nu_cere_confirmare_si_nu_tace():
    """Cele două direcții ale aceleiași reguli: un tip pe care Costin nu l-a împărțit încă **se
    vede** (tăria e `None`, nu absentă), dar **nu produce niciun efect**. Propunerea mea din
    `motiv_propunere` n-are voie să devină regulă prin trecerea timpului.

    **[01.09.2026, după R115] TESTUL ĂSTA S-A GOLIT, și era să treacă verde pe nimic.** Cât timp
    singurul tip n-avea tărie, bucla de mai jos avea ce parcurge. La atribuire, `tipuri_neatribuite()`
    a devenit **vidă** — iar un `for` pe o mulțime goală trece. *Aceeași clasă pe care o repar de
    două ture: un gard care raportează verde despre o lume pe care n-o mai vede.* De-aia proba
    înregistrează acum un tip **sintetic** neatribuit: regula se probează chiar când tabelul real e
    complet, iar tipul următor pe care Costin nu l-a împărțit încă găsește gardul viu."""
    tip_probă = _cu_tip_sintetic(None, False)
    S.TIPURI[tip_probă]["propus"] = S.CERTA
    try:
        neatribuite = S.tipuri_neatribuite()
        assert tip_probă in neatribuite, (
            "[anti-vacuu] tipul sintetic neatribuit nu apare între cele neatribuite — "
            "`tipuri_neatribuite()` nu mai măsoară ce credem")
        for tip in neatribuite:
            assert S.tarie(tip) is None
            assert S.cere_confirmare(tip) is False, (
                "tipul %r n-are tărie atribuită, dar cere confirmare — un implicit s-a strecurat"
                % tip)
            assert S.TIPURI[tip].get("propus") in S.TARII, (
                "tipul %r n-are nici măcar o propunere, deci Costin n-are ce confirma" % tip)
    finally:
        del S.TIPURI[tip_probă]


def test_o_TARIE_ATRIBUITA_poarta_motivul_ei_scris():
    """**Criteriul lui Costin (R115) trăiește ca DATE, nu ca proză într-un antet.**

    *„Tăria se dă după dacă diferența admite o explicație legitimă, nu după cine sunt cele două
    părți."* Un tip care primește o tărie fără să scrie cum s-a aplicat criteriul ar putea s-o
    primească **prin analogie cu vecinul din tabel** — adică exact greșeala pe care am făcut-o eu
    propunând CERTA: m-am uitat la cine sunt părțile."""
    cu_tarie = [t for t, v in S.TIPURI.items() if v.get("tarie") is not None]
    assert cu_tarie, "[anti-vacuu] niciun tip cu tărie — regula de mai jos n-ar fi probată"
    rele = [t for t in cu_tarie if not (S.TIPURI[t].get("motiv_tarie") or "").strip()]
    assert not rele, (
        "tipuri cu tărie atribuită și fără `motiv_tarie` scris: %s — criteriul s-a aplicat undeva "
        "și nu se mai poate citi de nimeni" % rele)


def test_perechea_reala_e_EURISTICA_deci_nu_cere_NICIODATA_confirmare():
    """R115, răspunsul, probat pe tipul REAL — nu pe cel sintetic. *„Semnalează, nu opresc
    niciodată"*: nici măcar confirmată, o euristică nu cere confirmare, deci nu atinge depunerea."""
    assert S.tarie(_ci.TIP_D390_VS_D300) == S.EURISTICA
    assert S.TIPURI[_ci.TIP_D390_VS_D300]["confirmat"] is True
    assert S.cere_confirmare(_ci.TIP_D390_VS_D300) is False, (
        "o EURISTICĂ cere confirmare — «semnalează, nu opresc niciodată» s-a rupt")
    assert not S.tipuri_neatribuite(), (
        "R115 e închisă, deci niciun tip nu mai așteaptă tăria; dacă apare unul nou, "
        "restanța se redeschide cu el, nu tăcut")


def test_o_tarie_NEVALIDA_nu_trece():
    """Nomenclatorul e ÎNCHIS: o a treia tărie ar fi o decizie de arhitectură, nu o valoare nouă."""
    tip = next(iter(S.TIPURI))
    vechi = S.TIPURI[tip].get("tarie")
    try:
        S.TIPURI[tip]["tarie"] = "APROAPE_CERTA"
        with pytest.raises(ValueError):
            S.tarie(tip)
    finally:
        S.TIPURI[tip]["tarie"] = vechi


# ── 2. MECANISMUL, probat pe un tip SINTETIC ───────────────────────────────────────────────────

def _cu_tip_sintetic(tarie, confirmat):
    """Înregistrează un tip de probă. Fără el, tot fișierul ar fi verde pe o mulțime în care nimic
    nu e încă atribuit — iar în ziua atribuirii nimic n-ar fi fost verificat (METODA §29)."""
    S.TIPURI["_PROBA_SINTETICA"] = {
        "axa": "ORIZONTALA", "ce": "probă", "identitate": "probă",
        "sursa_stanga": "probă", "sursa_dreapta": "probă",
        "tarie": tarie, "confirmat": confirmat, "propus": S.CERTA, "motiv_propunere": "probă",
    }
    return "_PROBA_SINTETICA"


def test_o_CERTA_CONFIRMATA_chiar_cere_confirmare():
    """Direcția care contează: mecanismul nu e mort, doar neatribuit."""
    tip = _cu_tip_sintetic(S.CERTA, True)
    try:
        assert S.tarie(tip) == S.CERTA
        assert S.cere_confirmare(tip) is True
    finally:
        del S.TIPURI[tip]


def test_o_EURISTICA_nu_cere_NICIODATA_confirmare():
    """*„semnalează, nu opresc niciodată"* — nici confirmată, nici neconfirmată."""
    for confirmat in (True, False):
        tip = _cu_tip_sintetic(S.EURISTICA, confirmat)
        try:
            assert S.cere_confirmare(tip) is False
        finally:
            del S.TIPURI[tip]


def test_o_CERTA_NECONFIRMATA_nu_are_efect():
    """O tărie propusă dar neconfirmată e o propunere, nu o regulă."""
    tip = _cu_tip_sintetic(S.CERTA, False)
    try:
        assert S.cere_confirmare(tip) is False
    finally:
        del S.TIPURI[tip]


# ── 3. AMPRENTA: pe cifre, nu pe proză ─────────────────────────────────────────────────────────

def test_amprenta_NU_se_schimba_la_rescrierea_prozei():
    a = S.amprenta(_C)
    for camp, val in (("mesaj", "cu totul altă frază"), ("temei", "alt temei"),
                      ("remediu", {"fel": "sugerat"})):
        assert S.amprenta(dict(_C, **{camp: val})) == a, (
            "amprenta s-a mutat la schimbarea lui %r — o reformulare ar invalida o confirmare bună"
            % camp)


def test_amprenta_SE_SCHIMBA_la_orice_cifra():
    """Cealaltă direcție, și e cea care apără sensul confirmării."""
    a = S.amprenta(_C)
    for camp in ("declarat_d390", "declarat_d300", "diferenta"):
        alt = dict(_C)
        alt[camp] = _C[camp] + 1
        assert S.amprenta(alt) != a, (
            "cifra %r s-a schimbat, amprenta NU — o confirmare veche ar acoperi tăcut o divergență "
            "nouă, iar «confirmare explicită» ar deveni o bifă permanentă" % camp)
    assert S.amprenta(dict(_C, stare="gri")) != a


# ── 4. SUPERVIZORUL NU BLOCHEAZĂ ───────────────────────────────────────────────────────────────

def test_nicio_cale_nu_intoarce_un_blocaj():
    """Contractul, scris în `PLAN_LUCRU`: produce constatări, nu blocaje. Nu există în tot modulul
    vreo valoare care să însemne «oprește-te»; certele cer o **confirmare**, pe care poarta de
    depunere o citește — supervizorul nu e a doua poartă."""
    import inspect
    sursa = inspect.getsource(S)
    for cuv in ("raise HTTPException", "blocheaza", "abort("):
        assert cuv not in sursa, "supervizorul conține %r — a devenit poartă" % cuv


def test_confirmarea_cere_MOTIV_scris():
    """*«iar confirmarea rămâne scrisă»* — o bifă fără motiv nu se poate citi peste șase luni."""
    class _ConnFals:
        def cursor(self):
            raise AssertionError("nu trebuia să ajungă la baza de date: motivul lipsește")
    for motiv in (None, "", "   "):
        with pytest.raises(ValueError):
            S.scrie_confirmare(_ConnFals(), 1, 2026, 9, dict(_C, amprenta="x"), "cine", 1, motiv)


# ── 5. ETICHETA DE TIP, pe TOATE căile de retur ────────────────────────────────────────────────

def test_perechea_orizontala_e_stampilata_pe_TOATE_caile():
    """Dacă o cale de retur pierde eticheta, supervizorul sare constatarea **tăcut**. Se probează
    toate cele patru ieșiri ale comparației, nu una."""
    cazuri = [
        ("fără D300 depus", _ci.compara_d390_vs_d300({"L": 0, "A": 0}, False, None)),
        ("depus fără rânduri", _ci.compara_d390_vs_d300({"L": 0, "A": 0}, True, None)),
        ("divergență", _ci.compara_d390_vs_d300({"L": 1000, "A": 0}, True, {"R": {}})),
        # AMBELE ZERO e TĂCUT prin construcție (fără subiect, nu verde fals) — proba
        # cere cifre egale și NENULE, altfel n-ar exercita calea verde deloc.
        ("coincid", _ci.compara_d390_vs_d300({"L": 1000, "A": 0}, True, {"R": {"R1_1": 1000}})),
    ]
    for eticheta, cs in cazuri:
        assert cs, "[anti-vacuu] cazul %r n-a produs nicio constatare" % eticheta
        fara = [c for c in cs if not c.get("tip_constatare")]
        assert not fara, "cazul %r a produs constatări fără tip: %d" % (eticheta, len(fara))
        assert all(c["tip_constatare"] in S.TIPURI for c in cs), (
            "cazul %r poartă un tip neînregistrat în `TIPURI`" % eticheta)


def test_ANTI_VACUU_exista_cel_putin_o_pereche_ORIZONTALA():
    orizontale = [t for t, v in S.TIPURI.items() if v.get("axa") == "ORIZONTALA"]
    assert orizontale, ("[anti-vacuu] niciun tip orizontal — supervizorul n-ar avea obiect, "
                        "fiindcă gaura măsurată e chiar axa orizontală")


def test_fiecare_tip_isi_declara_cele_doua_surse():
    """O pereche orizontală care nu spune ce compară cu ce nu se poate citi de nimeni."""
    rele = [t for t, v in S.TIPURI.items()
            if not (v.get("sursa_stanga") and v.get("sursa_dreapta") and v.get("identitate"))]
    assert not rele, "tipuri fără cele două surse sau fără identitatea verificată: %s" % rele


# ── 6. A CINCEA CALE — cea care traia un nivel mai sus ─────────────────────────────────────────
# [01.09.2026] Gardul de la pct.5 probeaza cele PATRU cai ale functiei PURE `compara_d390_vs_d300`.
# Comparatia orizontala avea insa CINCI iesiri: a cincea — *nicio depunere D300 prin aplicatie* —
# traia in corpul lui `verifica_d390` si chema `_absenta_libera` DIRECT, fara `_stampileaza`.
# MASURAT pe cele 19 firme ale portofoliului: supervizorul vedea 3 constatari orizontale si pierdea
# TACUT 13. Reparatie structurala: `orizontal_d390_vs_d300` — o singura iesire, un singur invelis.
import ast          # noqa: E402
import inspect      # noqa: E402

from core import db as _db                     # noqa: E402
from core import tenant_provisioning as _tp    # noqa: E402


def _conn():
    _db.init_pool()
    return _db.pool().getconn()


def test_a_cincea_cale_FARA_NICIO_DEPUNERE_e_stampilata_si_supervizorul_o_VEDE():
    """Firma exista, D390 se poate calcula, dar nu s-a depus NICIUN D300 prin aplicatie.

    Inainte de reparatie constatarea iesea fara `tip_constatare`, iar supervizorul o socotea
    verticala si o sarea — deci raporta *zero constatari* pentru firma, ceea ce se citeste
    „n-am ce semnala" cand adevarul e „comparatia nici nu e posibila". **Tacere care arata ca un
    raspuns** — chiar clasa numita in antetul lui `_stampileaza`.

    DECUPLAT: schema efemera din `tenant_template`, tenant sintetic, tot in ROLLBACK.
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS ztest_sv_a5 CASCADE")
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), "ztest_sv_a5"))
            cur.execute(
                "INSERT INTO ztest_sv_a5.firma_profil (id, nume, cui, platitor_tva, tip_decont, "
                "declarant_nume, declarant_prenume, declarant_functie) "
                "VALUES (1, 'PROBA SV', '14399840', true, 'L', 'Popescu', 'Ion', 'ADMINISTRATOR')")
            # fixtura-sintetica-ok: tenant_id sintetic. TREBUIE fabricat — fara rand in
            # public.tenants, `_d300_depus_recent` ar intoarce None din ALT motiv (firma
            # nemapata), iar testul ar trece pe motivul gresit.
            cur.execute("INSERT INTO public.tenants (schema_name, nume) "
                        "VALUES ('ztest_sv_a5', 'PROBA SV') RETURNING id")
            tid = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id = %s", (tid,))
            assert cur.fetchone()[0] == 0, "[anti-vacuu] firma de proba nu trebuie sa aiba depuneri"
            cur.execute("SET LOCAL search_path TO ztest_sv_a5, public")
            # AXA, chemata direct — etalonul. NU se filtreaza dupa eticheta: un filtru pe text ar
            # pazi formularea, nu faptul (METODA §23). Cate constatari produce axa, atatea trebuie
            # sa iasa TIPATE din `verifica_d390` si sa ajunga la supervizor.
            etalon = _ci.orizontal_d390_vs_d300(conn, "ztest_sv_a5", "L", 2026, 7)
            brute = _ci.verifica_d390(conn, "ztest_sv_a5", 2026, 7)["constatari"]
            vazute = S.constatari_firma(conn, "ztest_sv_a5", 2026, 7)
    finally:
        conn.rollback(); _db.pool().putconn(conn)

    assert len(etalon) == 1, (
        "[anti-vacuu] a cincea cale n-a produs exact o constatare (%d) — testul n-ar masura nimic"
        % len(etalon))
    assert all(c.get("tip_constatare") == _ci.TIP_D390_VS_D300 for c in etalon)
    # „cu temei" (Costin, despre ce vede contabilul): fiecare constatare isi poarta temeiul, altfel
    # ecranul ar arata o afirmatie despre datele firmei fara sa spuna pe ce se sprijina.
    assert all((c.get("temei") or "").strip() for c in etalon), (
        "o constatare fara temei — ecranul ar arata o afirmatie fara sprijin")
    tipate = [c for c in brute if c.get("tip_constatare")]
    assert len(tipate) == len(etalon), (
        "axa orizontala a produs %d constatari, dar din `verifica_d390` ies %d tipate — restul "
        "sunt netipate, iar supervizorul le sare TACUT: firma apare cu zero constatari, ceea ce se "
        "citeste ca «nimic de semnalat»" % (len(etalon), len(tipate)))
    vazute_d390 = [c for c in vazute if c["tip_constatare"] == _ci.TIP_D390_VS_D300]
    assert len(vazute_d390) == len(etalon), (
        "supervizorul NU vede a cincea cale — filtrul pe tip a inghitit-o")
    # R115 inchisa: perechea D390 e EURISTICA, si o euristica NU cere confirmare niciodata.
    assert all(c["tarie"] == S.EURISTICA for c in vazute_d390)
    # [02.09.2026] Firma de proba n-are D101 depus, deci perechile ANUALE ies ca ABSENTA (gri).
    # Sunt CERTE, dar o certa cere confirmare doar pe ROSU — o absenta nu e o nepotrivire.
    anuale = [c for c in vazute if c["tip_constatare"].startswith("D101_")]
    assert anuale, "[anti-vacuu] perechile anuale n-au produs nimic — proba nu le-ar acoperi"
    assert all(c["tarie"] == S.CERTA for c in anuale)
    assert all(c["stare"] == "gri" for c in anuale)
    # [02.09.2026] verificarea de DERIVA D300<->D394: firma de proba n-are nicio perioada cu
    # ambele depuse, deci iese ca ABSENTA. E EURISTICA, deci nu cere confirmare niciodata.
    deriva = [c for c in vazute if c["tip_constatare"] == _ci.TIP_D300_VS_D394_TI]
    assert len(deriva) == 1, "[anti-vacuu] perechea de deriva n-a produs nimic"
    assert deriva[0]["tarie"] == S.EURISTICA and deriva[0]["stare"] == "gri"
    ef = [c for c in vazute if c["tip_constatare"] == _ci.TIP_EFACTURA_VS_D394]
    assert len(ef) == 1, "[anti-vacuu] perechea e-Factura n-a produs nimic"
    assert ef[0]["tarie"] == S.EURISTICA and ef[0]["stare"] == "gri"
    # NICIUNA nu cere confirmare: euristicele niciodata, certele doar pe rosu.
    assert all(c["cere_confirmare"] is False for c in vazute)


def test_corpul_orizontal_nu_se_poate_chema_OCOLIND_invelisul():
    """CEALALTA DIRECTIE, si e cea care tine reparatia in picioare. Un test care doar probeaza a
    cincea cale ar trece si daca maine cineva adauga a sasea chemand corpul direct. Structural, pe
    AST — nu pe text (METODA §23): singurul apel al corpului e din invelisul care stampileaza."""
    arb = ast.parse(inspect.getsource(_ci))
    invelis = [n for n in ast.walk(arb)
               if isinstance(n, ast.FunctionDef) and n.name == "orizontal_d390_vs_d300"]
    assert len(invelis) == 1, "[anti-vacuu] invelisul nu mai exista sub numele asta"
    inauntru = {id(n) for n in ast.walk(invelis[0])}
    apeluri = [n for n in ast.walk(arb)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "_orizontal_d390_vs_d300"]
    assert len(apeluri) == 1, "[anti-vacuu] corpul nu e chemat nicaieri — invelisul e mort"
    assert id(apeluri[0]) in inauntru, (
        "corpul axei orizontale e chemat OCOLIND invelisul care pune `tip_constatare` — "
        "constatarile ies netipate, iar supervizorul le sare tacut")
    # si invelisul chiar stampileaza: un `return` care ar uita `_stampileaza` reface defectul
    stamp = [n for n in ast.walk(invelis[0])
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "_stampileaza"]
    assert len(stamp) == 1, "invelisul nu mai stampileaza — a cincea cale redevine tacuta"


# ── 7. DOMENIUL: o firmă nu poate dispărea dintr-o cifră ───────────────────────────────────────
# [01.09.2026] Criteriul de prioritate dat de Costin — *ce poate produce o cifră validă și falsă*.
# Un parcurgător de portofoliu scris firesc întoarce „19 firme, 0 constatări", strângând la un loc
# trei lucruri care nu seamănă: nimic găsit · nimic de comparat · **n-a rulat deloc**. Tiparul nu e
# presupus: `core/alerte_control_fiscal.ruleaza()` incrementează `tot["firme"]` DUPĂ succes, deci o
# firmă care ridică nu apare în niciun contor al dicționarului întors.
import contextlib   # noqa: E402


def _rezultat_d390(constatari, rulat=True):
    """Ce ar întoarce `verifica_d390` — inclusiv câmpul care spune dacă axa s-a atins."""
    return {"an": 2026, "luna": 8, "fereastra": "08/2026", "stare": "gri",
            "orizontal_rulat": rulat, "constatari": constatari}


def _deschide_fals(ridica_pe=()):
    @contextlib.contextmanager
    def deschide(schema):
        if schema in ridica_pe:
            raise RuntimeError("conexiune imposibilă pe %s" % schema)
        yield object()
    return deschide


_FIRME = [{"tenant_id": 1, "schema": "s_gasit", "nume": "CU CONSTATARE SRL"},
          {"tenant_id": 2, "schema": "s_gol", "nume": "FARA SUBIECT SRL"},
          {"tenant_id": 3, "schema": "s_nerulat", "nume": "AXA N-A RULAT SRL"},
          {"tenant_id": 4, "schema": "s_rupt", "nume": "CONEXIUNE MOARTA SRL"}]

_PLAN = {
    "s_gasit": _rezultat_d390([dict(_C)]),
    "s_gol": _rezultat_d390([]),
    # axa n-a rulat: ce iese e o constatare VERTICALĂ (fără tip), exact ca la ieșirea timpurie reală
    "s_nerulat": _rezultat_d390([{"stare": "gri", "eticheta": "Intracomunitar",
                                  "mesaj": "D390 nu se poate calcula (profil incomplet)."}],
                                rulat=False),
}


def _cu_plan(monkeypatch):
    monkeypatch.setattr(_ci, "verifica_d390",
                        lambda conn, schema, an, luna: _PLAN[schema])
    # perechile ANUALE ale D101 cer o conexiune reală; probele astea măsoară parcurgerea
    # portofoliului, nu perechile — deci se tac explicit, nu se lasă să ridice din altă cauză
    monkeypatch.setattr(_ci, "orizontal_d101", lambda conn, schema, an: [])
    monkeypatch.setattr(_ci, "orizontal_d300_vs_d394", lambda conn, schema: [])
    monkeypatch.setattr(_ci, "orizontal_efactura_vs_d394", lambda conn, schema: [])


def test_TOATE_CELE_TREI_rezultate_apar_si_SUMA_lor_e_domeniul(monkeypatch):
    """MIEZUL. Cele patru firme acoperă toate cele trei rezultate ȘI amândouă felurile de
    neverificat (axa n-a rulat · conexiunea a murit). Invariantul e ce face imposibilă cifra validă
    și falsă: o firmă care nu intră în niciun contor ar rupe suma."""
    _cu_plan(monkeypatch)
    r = S.ruleaza_portofoliu(2026, 8, firme=_FIRME, deschide=_deschide_fals(("s_rupt",)),
                             domeniu="domeniu de probă")
    rez, pe_schema = r["rezumat"], {x["schema"]: x for x in r["firme"]}

    assert pe_schema["s_gasit"]["rezultat"] == S.CONSTATARI
    assert pe_schema["s_gol"]["rezultat"] == S.FARA_SUBIECT
    assert pe_schema["s_nerulat"]["rezultat"] == S.NEVERIFICAT
    assert pe_schema["s_rupt"]["rezultat"] == S.NEVERIFICAT
    # [anti-vacuu] dacă un rezultat n-ar apărea deloc, invariantul ar trece pe o lume incompletă
    assert set(x["rezultat"] for x in r["firme"]) == set(S.REZULTATE), (
        "proba nu exercită toate cele trei rezultate — invariantul de mai jos n-ar dovedi nimic")

    assert sum(rez[k] for k in S.REZULTATE) == rez["firme_in_domeniu"] == len(_FIRME), (
        "o firmă a dispărut dintre cele trei rezultate — exact clasa din cronul de alerte, unde "
        "contorul se incrementează după succes și firma care ridică nu apare nicăieri")


def test_o_firma_care_RIDICA_e_NUMITA_nu_tacuta(monkeypatch):
    """Cealaltă direcție a aceleiași reguli: nu e destul să fie numărată — trebuie să se poată
    spune CARE și DE CE, altfel «3 neverificate» e tot o cifră fără adresă."""
    _cu_plan(monkeypatch)
    r = S.ruleaza_portofoliu(2026, 8, firme=_FIRME, deschide=_deschide_fals(("s_rupt",)),
                             domeniu="domeniu de probă")
    rupt = [x for x in r["firme"] if x["schema"] == "s_rupt"][0]
    assert rupt["nume"] == "CONEXIUNE MOARTA SRL"
    # pe CÂMPURI, nu pe textul erorii: felul e dat ca date tocmai ca nimeni să nu-l citească din proză
    assert rupt["neverificat"]["fel"] == "verificare_rupta"
    assert rupt["neverificat"]["felul_neverificarii"] == S.EXCEPTIE
    assert rupt["neverificat"]["eroare"], "`eroare` e obligatorie — fără ea nimeni n-o poate repara"
    nerulat = [x for x in r["firme"] if x["schema"] == "s_nerulat"][0]
    assert nerulat["neverificat"]["felul_neverificarii"] == S.AXA_NU_A_RULAT
    assert nerulat["neverificat"]["eroare"], "axa n-a rulat și nimeni nu spune de ce"
    # cele DOUĂ feluri nu se confundă: unul se repară completând profilul, celălalt e defect de cod
    assert rupt["neverificat"]["felul_neverificarii"] != nerulat["neverificat"]["felul_neverificarii"]


def test_FARA_SUBIECT_nu_se_poate_citi_ca_VERIFICAT_SI_CURAT(monkeypatch):
    """«Zero constatări» pe tot portofoliul NU e «totul e verde». Dacă cele două ar cădea în același
    contor, raportul ar afirma ceva ce nimeni n-a verificat."""
    _cu_plan(monkeypatch)
    doar_goale = [f for f in _FIRME if f["schema"] == "s_gol"] * 3
    r = S.ruleaza_portofoliu(2026, 8, firme=doar_goale, deschide=_deschide_fals(),
                             domeniu="domeniu de probă")
    assert r["rezumat"]["constatari_total"] == 0
    assert r["rezumat"][S.CONSTATARI] == 0
    assert r["rezumat"][S.FARA_SUBIECT] == 3, (
        "firmele fără subiect au căzut în alt contor — «0 constatări» ar deveni «am verificat 3 "
        "firme și sunt curate», ceea ce nimeni n-a verificat")


def test_domeniul_se_DECLARA_in_raspuns():
    """Fără criteriul scris în răspuns, «19» se citește ca «toate firmele care există»."""
    r = S.ruleaza_portofoliu(2026, 8, firme=[], deschide=_deschide_fals(), domeniu="probă")
    assert r["domeniu"] == "probă"
    assert r["rezumat"]["firme_in_domeniu"] == 0


def test_un_domeniu_INJECTAT_fara_nume_RIDICA_nu_imprumuta_criteriul_portofoliului():
    """**Cealaltă direcție, și e cea care apără sensul câmpului.** `DOMENIU` spune, în text, «nu se
    filtrează pe cabinet». Ruta la cerere rulează pe firmele CABINETULUI apelantului — dacă ar căra
    mai departe constanta, răspunsul ar afirma despre o populație pe care n-a parcurs-o. *Un domeniu
    nedeclarat se citește ca «toate firmele»; unul declarat GREȘIT se citește ca o afirmație
    verificată, ceea ce e mai rău.*"""
    for gol in (None, "", "   "):
        with pytest.raises(ValueError):
            S.ruleaza_portofoliu(2026, 8, firme=[], deschide=_deschide_fals(), domeniu=gol)
    # implicit (fără injecție) domeniul rămâne al portofoliului — probat pe funcția PURĂ,
    # ca să nu ceară baza și să nu depindă de portofoliul zilei
    assert S._domeniu_efectiv(None, None) == S.DOMENIU
    assert S._domeniu_efectiv(None, "altul") == "altul"
    assert S._domeniu_efectiv([], "al meu") == "al meu"


def test_campul_ORIZONTAL_RULAT_lipsa_RIDICA_nu_cade_pe_implicit(monkeypatch):
    """A treia oară aceeași regulă în modulul ăsta (după tăria neatribuită și tipul necunoscut): un
    implicit ar alege tăcut între «n-am verificat» și «e curat»."""
    monkeypatch.setattr(_ci, "verifica_d390",
                        lambda conn, schema, an, luna: {"constatari": []})
    monkeypatch.setattr(_ci, "orizontal_d101", lambda conn, schema, an: [])
    monkeypatch.setattr(_ci, "orizontal_d300_vs_d394", lambda conn, schema: [])
    monkeypatch.setattr(_ci, "orizontal_efactura_vs_d394", lambda conn, schema: [])
    with pytest.raises(ValueError):
        S._culege_firma(object(), "s", 2026, 8)


def test_supervizorul_pe_portofoliu_NU_SCRIE_nimic():
    """Contractul modulului, la nivel de portofoliu: produce constatări, nu efecte."""
    import inspect
    sursa = inspect.getsource(S.ruleaza_portofoliu) + inspect.getsource(S._culege_firma)
    for cuv in ("INSERT", "UPDATE", "DELETE", "commit("):
        assert cuv not in sursa, "parcurgerea portofoliului conține %r — a devenit scriitor" % cuv


# ── 8. DECLANȘAREA și IEȘIREA (01.09.2026) ─────────────────────────────────────────────────────
# Costin, verbatim: *„Declanșare: extinde cronul de 08:00 care există. Plus rulare la cerere. Nu
# construi al doilea mecanism."* · *„Ce vede contabilul: constatările deschise pe firmele lui, cu
# temei, în ecran propriu. Clopoțelul rămâne roșu agregat, nu o notificare pe constatare."*


def _sursa(nume):
    import io as _io
    import os as _os
    return _io.open(_os.path.join(_RAD, nume), encoding="utf-8").read()


def test_supervizorul_NU_e_un_al_doilea_mecanism_de_cron():
    """**Prima jumătate a lui «nu construi al doilea mecanism».** Modulul n-are voie să devină el
    însuși punct de intrare — fără `__main__`, fără `cron.ruleaza`. Structural, pe AST: o căutare de
    șir ar păzi formularea, nu faptul."""
    arb = ast.parse(_sursa("core/supervizor.py"))
    # [01.09.2026] Prima formă a acestei aserțiuni greșea în DOUĂ feluri deodată, și le-a prins
    # `test_garzi_pe_text`: căuta șirul „__name__" în `ast.dump` — deci ancorată pe TEXT (METODA
    # §23) — și trecea pe o mulțime goală, fiindcă un `for` fără niciun `If` nu asertează nimic.
    # Acum: premisă anti-vacuu, apoi potrivire pe FORMA nodului.
    functii = [n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)]
    assert functii, "[anti-vacuu] modulul n-are nicio funcție — n-am parsat ce cred că am parsat"
    poarta_main = [n for n in ast.walk(arb)
                   if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                   and isinstance(n.test.left, ast.Name) and n.test.left.id == "__name__"]
    assert not poarta_main, "supervizorul are poarta de `__main__` — a devenit al doilea cron"
    apeluri = [n for n in ast.walk(arb) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "ruleaza"
               and isinstance(n.func.value, ast.Name) and n.func.value.id == "cron"]
    assert not apeluri, "supervizorul cheamă `cron.ruleaza` — și-a făcut propriul mecanism"


def test_declansarea_sta_pe_slotul_de_08_care_EXISTA():
    """**A doua jumătate.** Cronul de 08:00 (`notificari_scadenta`) îl cheamă — deci declanșatorul e
    o EXTINDERE, nu o linie nouă de crontab. Dacă apelul dispare, supervizorul redevine nelegat, iar
    `test_module_nelegate` n-ar prinde-o: acolo `main.py` îl ține legat prin rută."""
    arb = ast.parse(_sursa("core/notificari_scadenta.py"))
    apeluri = [n for n in ast.walk(arb) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "ruleaza_portofoliu"]
    assert apeluri, ("cronul de 08:00 nu mai cheamă `ruleaza_portofoliu` — supervizorul și-a "
                     "pierdut declanșatorul propriu")


def test_supervizorul_NU_impinge_nimic_in_clopotel():
    """*„Clopoțelul rămâne roșu agregat, nu o notificare pe constatare."* Se respectă **neatingând**
    nimic: clopoțelul e cablat deja, fiindcă o constatare orizontală roșie face `verifica_d390` să
    întoarcă `stare='rosu'`, iar `alerte_control_fiscal` îl duce agregat pe firmă. Un push de aici ar
    fi fost exact al doilea mecanism."""
    arb = ast.parse(_sursa("core/supervizor.py"))
    nume = {n.id for n in ast.walk(arb) if isinstance(n, ast.Name)}
    nume |= {n.attr for n in ast.walk(arb) if isinstance(n, ast.Attribute)}
    for interzis in ("notificari_api", "adauga_multi", "alerteaza", "trimite"):
        assert interzis not in nume, (
            "supervizorul atinge %r — a început să notifice pe cont propriu" % interzis)


def test_ruta_la_cerere_NU_scapa_schema_si_isi_NUMESTE_domeniul(monkeypatch):
    """Ruta rulează pe firmele CABINETULUI, nu pe portofoliu — deci n-are voie să poarte criteriul
    portofoliului. Și `schema` e detaliu intern de stocare: nu iese pe rută (nici semaforul n-o dă).

    Firma sintetică trimite la o schemă inexistentă: culegerea RIDICĂ, iar proba arată că firma
    **e numită** în răspuns, nu dispare — aceeași regulă ca la portofoliu, dar pe calea rutei."""
    import main
    from core import auth_api
    _db.init_pool()
    monkeypatch.setattr(auth_api, "tenantii_userului",
                        lambda conn, uid: [{"id": 999001, "nume": "FIRMĂ DE PROBĂ SRL"}])
    monkeypatch.setattr(auth_api, "schema_tenant",
                        lambda conn, uid, tid: "ztest_schema_inexistenta_9999")
    r = main.supervizor_la_cerere(ctx={"uid": 1, "firm": 1})

    assert r["firme"], "[anti-vacuu] ruta n-a întors nicio firmă — proba n-ar măsura nimic"
    assert all("schema" not in f for f in r["firme"]), "numele schemei a ieșit pe rută"
    assert (r["domeniu"] or "").strip(), "ruta n-a numit domeniul"
    assert r["domeniu"] != S.DOMENIU, (
        "ruta a împrumutat criteriul ÎNTREGULUI portofoliu («nu se filtrează pe cabinet») pentru o "
        "mulțime filtrată pe cabinet — răspunsul ar afirma despre firme pe care nu le-a parcurs")
    f = r["firme"][0]
    assert f["nume"] == "FIRMĂ DE PROBĂ SRL"
    assert f["rezultat"] == S.NEVERIFICAT
    assert f["neverificat"]["felul_neverificarii"] == S.EXCEPTIE
    assert f["neverificat"]["eroare"]


# ── 9. PERECHILE ANUALE ALE D101 — pe surse INDEPENDENTE (02.09.2026) ──────────────────────────
# Costin: *„Continuă cu perechile orizontale care confruntă surse independente — perechea de azi nu
# o face, și tu ai scris de ce."* Identitățile sunt verificate VERBATIM în corpus, înainte de cod:
#   · rd.50 — OPANAF 206/2099: «declarate trimestrial prin formularul 100, la rândul Suma de plată»
#   · rd.48 — OPANAF 206/2099: «impozitul pe profit anual datorat»
#   · contul 691 — OMFP 1802/2014: «Cheltuieli cu impozitul pe profit» (698 e impozit pe VENIT)
#
# CALIBRARE: portofoliul viu n-are nicio depunere D101 cu rânduri, deci fără subiect fabricat
# perechile astea n-ar fi probate niciodată. Se fabrică, în ROLLBACK.
import psycopg2.extras as _E   # noqa: E402


def _schema_efemera(cur, nume):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % nume)
    cur.execute(_tp.parametrizeaza_template(
        open("tenant_template.sql", encoding="utf-8").read(), nume))
    cur.execute(
        "INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, tip_decont, declarant_nume, "
        "declarant_prenume, declarant_functie) VALUES (1, 'PROBA D101', '14399840', true, 'L', "
        "'Popescu', 'Ion', 'ADMINISTRATOR')" % nume)
    cur.execute("INSERT INTO public.tenants (schema_name, nume) VALUES (%s, 'PROBA D101') "
                "RETURNING id", (nume,))
    return cur.fetchone()[0]


def _pune_d101(cur, tid, an, P, d_grup=0):
    # fixtura-sintetica-ok: anul vine ca PARAMETRU, deci scanerul nu-l poate vedea; toti apelantii
    # dau 2099, iar tenant_id-ul e sintetic (rand nou in public.tenants, in rollback).
    cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, "
                "nr_depunere) VALUES (%s, %s, 12, 'd101', '<x/>', %s, 1)",
                (tid, an, _E.Json({"an": an, "P": P, "d_grup": d_grup})))


def _pune_d100(cur, tid, an, luna, suma, cod="103"):
    # fixtura-sintetica-ok: idem — anul e parametru, toti apelantii dau 2099, tenant_id sintetic.
    cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, "
                "nr_depunere) VALUES (%s, %s, %s, 'd100', '<x/>', %s, 1)",
                (tid, an, luna, _E.Json({"an": an, "luna": luna,
                                         "obligatii": [{"cod_oblig": cod, "suma_dat": suma,
                                                        "suma_plata": suma}]})))


def _perechi(conn, schema, tip):
    return [c for c in _ci.orizontal_d101(conn, schema, 2026) if c["tip_constatare"] == tip]


def test_pereche_D101_vs_D100_COINCID_da_verde_si_DIVERG_da_rosu():
    """CALIBRARE ÎN AMÂNDOUĂ DIRECȚIILE, pe subiect fabricat. Un test care ar proba doar verdele
    n-ar dovedi că perechea poate spune vreodată nu."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101a")
            # fixtura-sintetica-ok: tenant_id sintetic, in rollback
            _pune_d101(cur, tid, 2099, {"P48": 10000, "P50": 3000})
            # TOATE cele trei trimestre — altfel perechea spune, pe drept, ca nu vede tot anul
            _pune_d100(cur, tid, 2099, 3, 1000)
            _pune_d100(cur, tid, 2099, 6, 1500)
            _pune_d100(cur, tid, 2099, 9, 500)
            cur.execute("SET LOCAL search_path TO ztest_sv_d101a, public")
            coincid = _perechi(conn, "ztest_sv_d101a", _ci.TIP_D101_VS_D100)
            # acum stricam o singura latura: inca o depunere pe luna 12 -> suma devine 3500
            _pune_d100(cur, tid, 2099, 12, 500)
            diverg = _perechi(conn, "ztest_sv_d101a", _ci.TIP_D101_VS_D100)
    finally:
        conn.rollback(); _db.pool().putconn(conn)

    assert len(coincid) == 1, "[anti-vacuu] perechea n-a produs nicio constatare pe cazul coincident"
    assert coincid[0]["stare"] == "verde", coincid[0]["mesaj"]
    assert coincid[0]["declarat_d101"] == 3000 and coincid[0]["declarat_d100"] == 3000

    assert len(diverg) == 1
    assert diverg[0]["stare"] == "rosu", (
        "1.000 + 2.000 + 500 = 3.500 față de 3.000 declarat, și perechea NU spune roșu — "
        "atunci n-ar putea spune niciodată nu")
    assert diverg[0]["diferenta"] == -500
    assert diverg[0]["remediu"]["fel"] == "sugerat"


def test_pereche_D101_vs_691_COINCID_da_verde_si_DIVERG_da_rosu():
    """Aceeași calibrare pe latura contabilă: nota de impozit se scrie în evidență, nu se fabrică
    în declarație."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101b")
            _pune_d101(cur, tid, 2099, {"P48": 4000, "P50": 0})
            cur.execute("INSERT INTO ztest_sv_d101b.inregistrari (data, status, descriere) "
                        "VALUES ('2099-12-31', 'validata', 'impozit profit') RETURNING id")
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO ztest_sv_d101b.inregistrari_linii "
                        "(inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s, '691', '441', 4000)", (nid,))
            cur.execute("SET LOCAL search_path TO ztest_sv_d101b, public")
            coincid = _perechi(conn, "ztest_sv_d101b", _ci.TIP_D101_VS_691)
            # a doua nota, tot VALIDATA -> 691 urca la 4.600, declaratia ramane 4.000
            cur.execute("INSERT INTO ztest_sv_d101b.inregistrari (data, status, descriere) "
                        "VALUES ('2099-12-31', 'validata', 'inca una') RETURNING id")
            nid2 = cur.fetchone()[0]
            cur.execute("INSERT INTO ztest_sv_d101b.inregistrari_linii "
                        "(inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s, '691', '441', 600)", (nid2,))
            diverg = _perechi(conn, "ztest_sv_d101b", _ci.TIP_D101_VS_691)
    finally:
        conn.rollback(); _db.pool().putconn(conn)

    assert len(coincid) == 1, "[anti-vacuu] perechea n-a produs nicio constatare pe cazul coincident"
    assert coincid[0]["stare"] == "verde", coincid[0]["mesaj"]
    assert coincid[0]["inregistrat_691"] == 4000
    assert len(diverg) == 1 and diverg[0]["stare"] == "rosu"
    assert diverg[0]["diferenta"] == -600


def test_o_nota_in_CIORNA_pe_691_face_perechea_sa_TACA_nu_sa_acuze():
    """**Miezul unei constatări CERTE, aplicând criteriul lui Costin:** *tăria se dă după dacă
    diferența admite o explicație legitimă*. O notă de regularizare încă în ciornă e chiar o
    explicație legitimă — deci, cât timp există, perechea NU are voie să afirme o eroare."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101c")
            _pune_d101(cur, tid, 2099, {"P48": 4000, "P50": 0})
            cur.execute("INSERT INTO ztest_sv_d101c.inregistrari (data, status, descriere) "
                        "VALUES ('2099-12-31', 'ciorna', 'regularizare, inca ciorna') RETURNING id")
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO ztest_sv_d101c.inregistrari_linii "
                        "(inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s, '691', '441', 4000)", (nid,))
            cur.execute("SET LOCAL search_path TO ztest_sv_d101c, public")
            cs = _perechi(conn, "ztest_sv_d101c", _ci.TIP_D101_VS_691)
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1, "[anti-vacuu] perechea n-a produs nimic — proba n-ar masura nimic"
    assert cs[0]["stare"] == "gri", (
        "nota de regularizare e in CIORNA, deci diferenta are o explicatie legitima — perechea "
        "acuza o eroare pe care n-o poate sustine")


def test_un_MEMBRU_DE_GRUP_fiscal_nu_e_confruntat_pe_randurile_care_nu_se_completeaza():
    """OPANAF 206/2099, verbatim: *„În cazul membrilor unui grup fiscal în domeniul impozitului pe
    profit, rândurile 41.2, 48, 50, 52 și 53 din formular nu se completează."* Deci pe `d_grup=1`
    perechile TAC — nu sunt verzi (n-au verificat nimic) și nu sunt roșii (n-au ce compara)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101d")
            _pune_d101(cur, tid, 2099, {"P48": 0, "P50": 0}, d_grup=1)
            _pune_d100(cur, tid, 2099, 3, 9999)
            cur.execute("SET LOCAL search_path TO ztest_sv_d101d, public")
            toate = _ci.orizontal_d101(conn, "ztest_sv_d101d", 2026)
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    anuale = [c for c in toate if c["tip_constatare"].startswith("D101")]
    assert anuale == [], (
        "un membru de grup a primit constatări pe rânduri pe care ordinul spune că nu le "
        "completează: %s" % [c.get("mesaj") for c in anuale])


def test_o_depunere_D100_FARA_randuri_nu_se_numara_ca_ZERO():
    """*O depunere fără rânduri persistate nu e o depunere cu zero.* Dacă s-ar aduna ca zero, suma
    din dreapta ar fi mai mică decât realitatea, iar perechea ar numi divergență propria ei orbire."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101e")
            _pune_d101(cur, tid, 2099, {"P48": 0, "P50": 3000})
            _pune_d100(cur, tid, 2099, 3, 3000)
            _pune_d100(cur, tid, 2099, 9, 0)
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, "
                        "randuri, nr_depunere) VALUES (%s, 2099, 6, 'd100', '<x/>', NULL, 1)", (tid,))
            cur.execute("SET LOCAL search_path TO ztest_sv_d101e, public")
            cs = _perechi(conn, "ztest_sv_d101e", _ci.TIP_D101_VS_D100)
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1
    assert cs[0]["stare"] == "gri", (
        "o depunere D100 fără rânduri a fost socotită ZERO, iar perechea a tras o concluzie din "
        "propria ei orbire")


def test_perechile_anuale_NU_se_ancoreaza_pe_anul_CURENT():
    """D101 se depune pentru anul ÎNCHEIAT. O pereche ancorată pe anul curent ar fi GRI PERMANENT
    prin construcție — capcana pe care perechea D390 a rezolvat-o deja cu `_d300_depus_recent`."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101f")
            _pune_d101(cur, tid, 2099, {"P48": 0, "P50": 3000})
            _pune_d100(cur, tid, 2099, 3, 1000)
            _pune_d100(cur, tid, 2099, 6, 1000)
            _pune_d100(cur, tid, 2099, 9, 1000)
            cur.execute("SET LOCAL search_path TO ztest_sv_d101f, public")
            # se cere anul 2026 (curent), dar depunerea e pe 2099 -> trebuie evaluat 2099
            cs = _perechi(conn, "ztest_sv_d101f", _ci.TIP_D101_VS_D100)
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1 and cs[0]["stare"] == "verde", (
        "perechea s-a ancorat pe anul cerut, nu pe anul ultimei depuneri — ar fi gri pe vecie")
    assert "2099" in cs[0]["eticheta"]


def test_un_TRIMESTRU_NEVAZUT_da_GRI_nu_ROSU():
    """**Regula lui Costin, 02.09.2026, verbatim:** *„Tăria descrie identitatea, nu calitatea
    datelor noastre. Unde nu poți stabili că vezi tot, spui gri."*

    Un D100 depus în afara aplicației nu e o diferență legitimă între laturi — identitatea din ordin
    ține oricum. E o **lipsă de vizibilitate** pe latura dreaptă. Deci perechea rămâne CERTĂ, dar nu
    are voie să acuze: spune gri și numește trimestrul pe care nu-l vede.

    *Fără regula asta, perechea ar fi produs un roșu care e al orbirii mele, nu al declarației — iar
    o cifră validă și falsă e chiar criteriul pe care se aleg lucrurile de făcut.*"""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d101g")
            _pune_d101(cur, tid, 2099, {"P48": 0, "P50": 3000})
            _pune_d100(cur, tid, 2099, 3, 1000)     # lipseste trimestrul II SI III
            cur.execute("SET LOCAL search_path TO ztest_sv_d101g, public")
            cs = _perechi(conn, "ztest_sv_d101g", _ci.TIP_D101_VS_D100)
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1, "[anti-vacuu] perechea n-a produs nimic — proba n-ar masura nimic"
    assert cs[0]["stare"] == "gri", (
        "3.000 declarat fata de 1.000 vazut ar fi dat ROSU — dar doua trimestre nu se vad deloc, "
        "deci diferenta ar fi a orbirii mele, nu a declaratiei")
    # si TARIA ramane CERTA: lipsa de vizibilitate nu coboara taria, raspunde cu gri
    assert S.tarie(_ci.TIP_D101_VS_D100) == S.CERTA


# ── 10. D300 ↔ D394, VERIFICARE DE DERIVĂ (02.09.2026) ─────────────────────────────────────────
# Costin: *„motivul e roșul, nu verdele: două declarații depuse care nu se potrivesc între ele e
# expunere reală la ANAF, iar corelația e una dintre cele pe care ANAF le rulează."* Deci proba
# principală e că perechea **poate spune roșu** — verdele ei e slab prin construcție.
import json as _json   # noqa: E402


def _pune_d300(cur, tid, an, luna, baza_ti):
    # fixtura-sintetica-ok: anul e parametru, toti apelantii dau 2099, tenant_id sintetic.
    cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, "
                "nr_depunere) VALUES (%s, %s, %s, 'd300', '<x/>', %s, 1)",
                (tid, an, luna, _E.Json({"an": an, "luna": luna, "R": {"R12_1": baza_ti}})))


def _pune_d394(cur, tid, an, luna, op1):
    # fixtura-sintetica-ok: anul e parametru, toti apelantii dau 2099, tenant_id sintetic.
    cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, "
                "nr_depunere) VALUES (%s, %s, %s, 'd394', '<x/>', %s, 1)",
                (tid, an, luna, _E.Json({"an": an, "luna": luna, "op1": op1})))


def _op1(tip, baza, cui="RO123", den="Partener SRL", cota=21, tp=1, nr=1):
    """Cheia lui `op1` e un TUPLU serializat ca JSON — v. `coada_api._chei_serializabile`."""
    return {_json.dumps([tip, tp, cota, cui, den]): [nr, baza, 0]}


def test_deriva_D300_D394_COINCID_da_verde_SLAB_si_DIVERG_da_ROSU():
    """**Proba care contează e roșul.** Verdele e slab prin construcție (ambele laturi vin din
    aceleași facturi), iar temeiul trebuie s-o spună — se asertează și asta, fiindcă un verde citit
    ca «am verificat la sursă» e mai rău decât niciun verde."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d394a")
            _pune_d300(cur, tid, 2099, 6, 5000)
            _pune_d394(cur, tid, 2099, 6, _op1("C", 5000))
            cur.execute("SET LOCAL search_path TO ztest_sv_d394a, public")
            coincid = _ci.orizontal_d300_vs_d394(conn, "ztest_sv_d394a")
            # perioada mai NOUA, cu divergenta -> perechea se muta pe ea
            _pune_d300(cur, tid, 2099, 9, 5000)
            _pune_d394(cur, tid, 2099, 9, _op1("C", 4200))
            diverg = _ci.orizontal_d300_vs_d394(conn, "ztest_sv_d394a")
    finally:
        conn.rollback(); _db.pool().putconn(conn)

    assert len(coincid) == 1, "[anti-vacuu] perechea n-a produs nimic pe cazul coincident"
    assert coincid[0]["stare"] == "verde", coincid[0]["mesaj"]
    assert coincid[0]["verde_slab"] is True, (
        "verdele nu-și declară slăbiciunea ca FAPT — ar fi citit ca «am verificat la sursă», iar o "
        "gardă pe formulare ar păzi textul, nu proprietatea")

    assert len(diverg) == 1
    assert diverg[0]["stare"] == "rosu", (
        "5.000 față de 4.200 pe două declarații DEPUSE și perechea nu spune roșu — dar exact roșul "
        "e motivul pentru care există")
    assert diverg[0]["diferenta"] == 800
    assert diverg[0]["remediu"]["fel"] == "sugerat"
    assert (diverg[0]["an"], diverg[0]["luna"]) == (2099, 9), (
        "perechea n-a luat perioada cea mai recentă cu ambele depuse")


def test_deriva_numara_DOAR_achizitiile_cu_taxare_inversa():
    """Tipul «C» e achiziția cu taxare inversă. O livrare («V») sau o achiziție normală («A») în
    aceeași perioadă n-au ce căuta în sumă — altfel perechea ar acuza o divergență pe care chiar ea
    a fabricat-o."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d394b")
            op1 = {}
            op1.update(_op1("C", 5000, cui="RO1"))
            op1.update(_op1("A", 9000, cui="RO2"))     # achizitie NORMALA — nu intra
            op1.update(_op1("V", 7000, cui="RO3"))     # livrare cu taxare inversa — nu intra
            _pune_d300(cur, tid, 2099, 6, 5000)
            _pune_d394(cur, tid, 2099, 6, op1)
            cur.execute("SET LOCAL search_path TO ztest_sv_d394b, public")
            cs = _ci.orizontal_d300_vs_d394(conn, "ztest_sv_d394b")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1
    assert cs[0]["declarat_d394"] == 5000, (
        "suma a inclus si operatiuni care nu sunt achizitii cu taxare inversa: %s" % cs[0])
    assert cs[0]["stare"] == "verde"


def test_o_cheie_op1_NECITIBILA_da_GRI_nu_divergenta():
    """Regula lui Costin: *unde nu poți stabili că vezi tot, spui gri*. O cheie pe care n-o pot citi
    înseamnă operațiuni pe care nu le văd — iar o sumă parțială ar numi divergență propria mea
    vedere incompletă."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_d394c")
            op1 = {"cheie care nu e JSON": [1, 5000, 0]}
            _pune_d300(cur, tid, 2099, 6, 5000)
            _pune_d394(cur, tid, 2099, 6, op1)
            cur.execute("SET LOCAL search_path TO ztest_sv_d394c, public")
            cs = _ci.orizontal_d300_vs_d394(conn, "ztest_sv_d394c")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1 and cs[0]["stare"] == "gri", (
        "o cheie necitibilă a fost trecută cu vederea, iar perechea a tras o concluzie din propria "
        "ei orbire")


def test_serializarea_unui_D394_cu_operatiuni_NU_MAI_RIDICA():
    """PRAG 1, reparat: `randuri_din_res` ridica `TypeError` pe cheile TUPLU ale D394, iar apelul din
    `POST /coada` e negardat — deci un D394 **cu operațiuni** nu putea fi trimis în coadă deloc.
    Se aprindea exact pe firmele care aveau ce declara: pe `op1` gol serializarea trecea."""
    import dataclasses
    from core import coada_api as _ca

    @dataclasses.dataclass
    class _R:
        an: int = 2099
        op1: dict = dataclasses.field(default_factory=dict)

    r = _R(op1={("C", 1, 21, "RO1", "Partener | cu bara"): [1, 5000, 0]})
    out = _ca.randuri_din_res(r)
    assert out is not None, "serializarea a picat — D394 n-ar putea intra în coadă"
    (cheie,) = list(out["op1"])
    assert _json.loads(cheie)[0] == "C", (
        "cheia nu se mai poate citi înapoi: %r — cine confruntă două declarații n-ar putea "
        "întreba ce tip de operațiune e" % cheie)
    # separatorul nu e o convenție fragilă: denumirea partenerului conține chiar `|`
    assert _json.loads(cheie)[4] == "Partener | cu bara"


# ── 11. e-FACTURA ↔ D394 — singura pereche pe surse INDEPENDENTE (R119, 02.09.2026) ────────────
# Costin: *„e singura pereche care confruntă surse independente: ce a plecat la ANAF prin e-Factura
# față de ce s-a declarat în D394. Verdele ei ar însemna ceva, spre deosebire de cele patru
# existente."* Și constrângerea, tot a lui: *„Nu reimplementa regulile de eligibilitate — două
# motoare care se despart în tăcere e chiar clasa care produce cifra validă și falsă."*


def _pune_d394_cu_facturi(cur, tid, an, luna, incluse, manuale=0):
    # fixtura-sintetica-ok: anul e parametru, toti apelantii dau 2099, tenant_id sintetic.
    cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, "
                "nr_depunere) VALUES (%s, %s, %s, 'd394', '<x/>', %s, 1)",
                (tid, an, luna, _E.Json({"an": an, "luna": luna,
                                         "facturi_incluse": incluse,
                                         "manuale_fara_factura": manuale})))


def _factura_trimisa(cur, schema, data, stare="ok", mediu="prod"):
    """Inserează o factură emisă + trimiterea ei, și întoarce id-ul DAT DE BAZĂ.

    `facturi.id` e `GENERATED ALWAYS`, deci nu se poate alege din test. Bine că e așa: id-urile
    scrise de mână ar fi fost o convenție care se sparge la prima schemă cu alt contor."""
    cur.execute("INSERT INTO %s.facturi (numar, directie, data_emitere, total, tva) "
                "VALUES (%%s, 'emisa', %%s, 119, 19) RETURNING id" % schema,
                ("FP-" + str(data).replace("-", "") + "-" + stare + "-" + mediu, data))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO %s.efactura_trimiteri (factura_id, mediu, stare, xml_sha256) "
                "VALUES (%%s, %%s, %%s, %%s)" % schema,
                (fid, mediu, stare, "0" * 64))
    return fid


def test_o_factura_TRANSMISA_si_NEDECLARATA_da_ROSU_si_o_NUMESTE():
    """**Miezul lui R119.** O factură care a plecat la ANAF și nu apare în D394 e expunere reală —
    iar constatarea trebuie să spună CARE, altfel e un reproș fără adresă."""
    conn = _conn()
    f2 = None
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_ef_a")
            cur.execute("UPDATE ztest_sv_ef_a.firma_profil SET tip_decont='L' WHERE id=1")
            f1 = _factura_trimisa(cur, "ztest_sv_ef_a", "2099-06-10")
            f2 = _factura_trimisa(cur, "ztest_sv_ef_a", "2099-06-11")
            # D394 a inclus DOAR prima
            _pune_d394_cu_facturi(cur, tid, 2099, 6, {'["L", 1, 21, "RO1", "X"]': [f1]})
            cur.execute("SET LOCAL search_path TO ztest_sv_ef_a, public")
            cs = _ci.orizontal_efactura_vs_d394(conn, "ztest_sv_ef_a")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1, "[anti-vacuu] perechea n-a produs nimic"
    assert cs[0]["stare"] == "rosu", cs[0]["mesaj"]
    assert cs[0]["nedeclarate"] == 1 and cs[0]["facturi_nedeclarate"] == [f2], (
        "constatarea nu NUMEȘTE factura lipsă — ar fi un reproș fără adresă")
    assert str(f2) in (cs[0]["remediu"]["facturi"] or [])


def test_toate_transmise_si_declarate_da_VERDE_si_verdele_ASTA_inseamna_ceva():
    """Spre deosebire de celelalte patru perechi, verdele de aici NU e slab: cele două laturi nu se
    derivă una din cealaltă. De-aia constatarea **nu** poartă `verde_slab`."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_ef_b")
            cur.execute("UPDATE ztest_sv_ef_b.firma_profil SET tip_decont='L' WHERE id=1")
            f1 = _factura_trimisa(cur, "ztest_sv_ef_b", "2099-06-10")
            _pune_d394_cu_facturi(cur, tid, 2099, 6, {'["L", 1, 21, "RO1", "X"]': [f1]})
            cur.execute("SET LOCAL search_path TO ztest_sv_ef_b, public")
            cs = _ci.orizontal_efactura_vs_d394(conn, "ztest_sv_ef_b")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1 and cs[0]["stare"] == "verde", cs[0]
    assert "verde_slab" not in cs[0], (
        "verdele ăsta a fost marcat slab — dar el chiar afirmă ceva, fiindcă laturile sunt "
        "independente; a-l slăbi ar șterge exact diferența pentru care perechea a fost cerută")


def test_o_trimitere_pe_TEST_sau_NEACCEPTATA_nu_conteaza_ca_plecata():
    """`mediu='test'` n-a plecat nicăieri, iar o stare care nu e `ok` n-are recipisă. Dacă ar
    conta, perechea ar acuza firma pentru facturi care n-au ajuns niciodată la ANAF."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_ef_c")
            cur.execute("UPDATE ztest_sv_ef_c.firma_profil SET tip_decont='L' WHERE id=1")
            _factura_trimisa(cur, "ztest_sv_ef_c", "2099-06-10", mediu="test")
            _factura_trimisa(cur, "ztest_sv_ef_c", "2099-06-10", stare="nok")
            _pune_d394_cu_facturi(cur, tid, 2099, 6, {})
            cur.execute("SET LOCAL search_path TO ztest_sv_ef_c, public")
            cs = _ci.orizontal_efactura_vs_d394(conn, "ztest_sv_ef_c")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert cs == [], (
        "o trimitere pe TEST sau neacceptată a fost socotită «plecată la ANAF»: %s"
        % [c.get("mesaj") for c in cs])


def test_operatiunile_MANUALE_dau_GRI_nu_rosu():
    """Regula lui Costin: *unde nu poți stabili că vezi tot, spui gri*. O operațiune manuală n-are
    factură în spate, deci o factură transmisă ar putea fi acoperită de ea fără să pot ști."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _schema_efemera(cur, "ztest_sv_ef_d")
            cur.execute("UPDATE ztest_sv_ef_d.firma_profil SET tip_decont='L' WHERE id=1")
            _factura_trimisa(cur, "ztest_sv_ef_d", "2099-06-10")
            _pune_d394_cu_facturi(cur, tid, 2099, 6, {}, manuale=2)
            cur.execute("SET LOCAL search_path TO ztest_sv_ef_d, public")
            cs = _ci.orizontal_efactura_vs_d394(conn, "ztest_sv_ef_d")
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    assert len(cs) == 1 and cs[0]["stare"] == "gri", (
        "o factură transmisă a fost declarată nedeclarată, deși există operațiuni manuale care ar "
        "putea s-o acopere — roșul ar fi al vederii mele")


def test_ELIGIBILITATEA_ramane_a_generatorului_nu_se_reimplementeaza():
    """**Constrângerea pe care Costin a numit-o explicit.** `facturi_incluse` se umple din ACELEAȘI
    apeluri care compun declarația, deci o factură pe care generatorul o EXCLUDE nu poate apărea
    printre cele incluse. Dacă cineva ar reimplementa eligibilitatea în altă parte, cele două s-ar
    despărți **în tăcere** — chiar clasa care produce cifra validă și falsă."""
    from core import d394 as _d394
    from core.common import Perioada
    prof = {"cui": "14399840", "nume": "PROBA", "platitor_tva": True,
            "declarant_nume": "P", "declarant_prenume": "I", "declarant_functie": "ADMIN"}
    facturi = [
        # intra: livrare catre partener RO cu CUI, cota 21
        {"cui": "14399840", "nume": "Client SRL", "directie": "emisa", "taxare_inversa": False,
         "platitor_tva": True, "cota": 21, "baza": 1000, "tva": 210, "nrFact": 1, "factura_id": 11},
        # NU intra, si e IMPORTANT ca excluderea trece prin `del op1[k]`, nu printr-un filtru de
        # dinainte: achizitie cu taxare inversa FARA categorie art.331 -> op11 n-are cod -> operatiunea
        # se sterge din declaratie. Asta e calea pe care dictionarul paralel TREBUIE curatat.
        {"cui": "14399840", "nume": "Furnizor SRL", "directie": "primita", "taxare_inversa": True,
         "platitor_tva": True, "cota": 21, "baza": 500, "tva": 105, "nrFact": 1, "factura_id": 12,
         "categorie_331": None},
    ]
    res = _d394.calcul_d394(prof, Perioada(2099, luna=6),
                            {"facturi": facturi, "serii": {}, "nr_facturi": 1}, None)
    toate = set()
    for v in res.facturi_incluse.values():
        toate.update(v)
    assert 11 in toate, "[anti-vacuu] factura eligibilă n-a fost înregistrată ca inclusă"
    assert 12 not in toate, (
        "o factură pe care generatorul a EXCLUS-O apare printre cele incluse — confruntarea ar "
        "afirma că s-a declarat ceva ce nu s-a declarat")
