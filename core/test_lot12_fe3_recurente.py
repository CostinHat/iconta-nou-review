# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fe3] Facturile recurente — comanda Costin 12.3, verbatim:
  pct.1 „C109: refuzul cronului ajunge la contabil prin notificare (clopoțel și email); pe șablon se vede și starea ultimei emiteri.”
  pct.9 „Da: cota și categoria pe linia șablonului recurent, ca la factură.”

C109: un refuz al emiterii automate (`facturi_recurente.emite_scadente`) rămânea numai în jurnalul jobului. Acum se scrie pe șablon
(`ultimul_refuz`, `ultimul_refuz_la`, `core/migrare_sablon_recurent_stare.py`) și intră, în aceeași tranzacție, în clopoțelul celor care
pregătesc pe firmă — tipul `factura_recurenta_refuzata`, bifat din oficiu, deci pleacă și pe email (mecanismul comun: `notificari_api.adauga`
+ cutia de ieșire `notificari.livreaza_in_asteptare`). Același refuz se anunță o dată pe lună (cronul reîncearcă zilnic). Găsit aici:
cursul BNR refuzat la emitere (`emite_factura` întoarce `{"ok": False}`) trecea șablonul drept emis în luna aceea, fără factură.
pct.9: cota și categoria de TVA pe linia șablonului, și categoria produsului la taxarea inversă (`categorie_331`), de la salvare până la
factura lunară; refuzul C160 al clientului din alt stat se ridică acolo unde linia are cota aleasă.

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt, citit la sursă):
  · CF art.310 alin.(10) lit.b — persoana care aplică regimul special de scutire „nu are voie să menționeze taxa pe factură sau pe alt
    document” (refuzul folosit ca refuz real al cronului: firma devenită neplătitoare, șablonul cu 21%);
  · CF art.278 alin.(2) — „Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva
    persoană care primește serviciile își are stabilit sediul activității sale economice” (linia 0% „serviciu_extern” către clientul din DE).
Categoriile și refuzurile lor nu se definesc aici: sunt ale emiterii (`categorii_tva.verifica_linii`, lotul 11 274b / 449).

Schemă efemeră din `tenant_template.sql` (+ migrarea pachetului, idempotentă), cabinet / utilizator / firmă sintetice în `public`, totul
într-o tranzacție anulată; perioade sintetice 2099. CUI firmei 14399840 (cifra de control verificată cu `cui_valid` din CLAUDE.md), clientul
din DE DE811907980 (cel al probelor C78 / C110 / C154 / C160)."""
import contextlib
import datetime
import io
import json
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "tenant_test_lot12_fe3"
AZI = datetime.date(2099, 3, 10)
LUNA_URM = datetime.date(2099, 4, 10)
CUI_CLIENT = "14399840"
COD_DE = "DE811907980"
LINIE = {"descriere": "Abonament mentenanta lunara", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}
#: refuzul real al emiterii pentru neplătitor (`facturi_api.creeaza_factura`, CF art.310 alin.(10) lit.b), întreg — comparat cu `==`
MOTIV_NEPLATITOR = ("Firma nu e plătitoare de TVA, deci factura nu poate purta TVA: linia 'Abonament mentenanta lunara' are cota 21%. Cota pe "
                    "liniile unui neplătitor e 0 (CF art.310 alin.(10) lit.b): persoana în regim special de scutire „nu are voie să menționeze "
                    "taxa pe factură sau pe alt document”).")
SERVICIU = {"descriere": "Servicii de consultanta IT", "cantitate": 1, "pret_unitar": 500, "cota_tva": 0, "categorie_tva": "serviciu_extern",
            "cont_venit": "704"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


class _Prox:
    """Conexiunea testului: commit / rollback nu închid tranzacția testului (totul se anulează la capăt)."""
    def __init__(self, c):
        object.__setattr__(self, "_c", c)

    def __getattr__(self, n):
        return getattr(self._c, n)

    def commit(self):
        pass

    def rollback(self):
        pass


@pytest.fixture
def mediu(monkeypatch):
    """Firmă SRL plătitoare de TVA (forma juridică, capitalul, seria „RC”), a unui cabinet cu un administrator: schema din
    `tenant_template.sql` + migrarea pachetului; cronul primește aceeași conexiune (`db.get_conn`); ANAF simulat; emailul notificărilor
    prins (nu pleacă)."""
    from core import facturi_api, notificari, uc_comun, uc_curs_bnr
    _db.init_pool()
    p = _db.pool()
    c = p.getconn()
    try:
        with c.cursor() as cur:
            cur.execute("UPDATE public.notificari SET de_livrat = false WHERE de_livrat")   # cutia de ieșire: numai rândurile probei
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            from core import migrare_sablon_recurent_stare as m
            m.aplica(c, SCH)
            from core import migrare_sablon_recurent_emitere as m2   # [lotul 13, 680] întrebările emiterii pe șablon
            m2.aplica(c, SCH)
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                        "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,metoda_stoc) VALUES (1,'Firma FE3 SRL',"
                        "%s,'Str 1','Cluj-Napoca','CJ','6202','BCR','RO49RNCB0000000000000001','micro',true,'L','Pop','Ion',"
                        "'administrator','SRL',200,'global_valoric')", (CUI_CLIENT,))
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST FE3 CABINET') RETURNING id")
            cab = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) VALUES "
                        "('ztest_fe3_admin@invalid','x','Admin','FE3','admin_firma',%s,true) RETURNING id", (cab,))
            uid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.tenants (schema_name, nume, activ, accounting_firm_id) VALUES (%s,'Firma FE3 SRL',true,%s) "
                        "RETURNING id", (SCH, cab))
            tid = cur.fetchone()[0]
        assert facturi_api.seteaza_numerotare(c, serie="RC", numar_start=1)["ok"]

        @contextlib.contextmanager
        def _gc(*a, **k):
            with c.cursor() as cur:
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            yield _Prox(c)
        monkeypatch.setattr(_db, "get_conn", _gc)
        monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: True)
        monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)
        emailuri = []
        monkeypatch.setattr(notificari._obs, "trimite_email_html_sau_semnaleaza",
                            lambda et, catre, subiect, html, **k: emailuri.append((catre, subiect, html)) or True)
        yield {"c": c, "uid": uid, "tid": tid, "emailuri": emailuri}
    finally:
        c.rollback()
        p.putconn(c)


def _sql(m, q, args=()):
    with m["c"].cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


def _adauga(m, **k):
    from core import facturi_recurente as fr
    corp = dict({"tert_nume": "Client Recurent SRL", "tert_cui": CUI_CLIENT, "zi_emitere": 5, "moneda": "RON", "linii": [dict(LINIE)],
                 "scadenta_zile": 15, "data_inceput": "2026-01-01", "valabil_pana": "oprire", "mod_emitere": "automata", "trimite_spv": False}, **k)   # [lotul 13, 680] întrebările emiterii
    with m["c"].cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
    return fr.adauga(_Prox(m["c"]), SCH, corp, azi=AZI)


def _pe_campuri(r):
    return [(x["camp"], x["mesaj"]) for x in r.get("erori_campuri") or []]


def _notificari(m):
    return _sql(m, "SELECT tip, text, de_livrat FROM public.notificari WHERE user_id = %s ORDER BY id", (m["uid"],))


def _stare(m, sid):
    return _sql(m, "SELECT ultima_emitere, ultimul_refuz, ultimul_refuz_la FROM facturi_recurente WHERE id = %s", (sid,))[0]


# ── C109 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c109_refuzul_cronului_ajunge_pe_sablon_in_clopotel_si_pe_email_o_data_pe_luna(mediu):
    """Șablonul 21% salvat; firma devine neplătitoare; cronul refuză (CF art.310 alin.(10) lit.b): refuzul e pe șablon (motivul, ziua),
    în clopoțelul administratorului (textul cu firma, clientul, motivul) și pleacă pe email (eticheta tipului, fără motiv — „fără conținut
    fiscal”). A doua rulare în aceeași zi: nicio notificare nouă. Luna următoare: încă una. Firma redevine plătitoare: factura se emite,
    refuzul consemnat se golește.
    MUTAȚII: `_consemneaza_refuzul` scos din ramura excepției -> nici stare, nici notificare -> ROȘU; `refuz_de_anuntat` întoarce mereu
    True -> a doua notificare în aceeași zi -> ROȘU; `"implicit": True` scos din tip -> emailul nu pleacă -> ROȘU."""
    from core import facturi_recurente as fr, notificari
    r = _adauga(mediu)
    assert set(r) == {"id"}, r
    sid = r["id"]
    _sql(mediu, "UPDATE firma_profil SET platitor_tva = false WHERE id = 1")
    e = fr.emite_scadente(SCH, AZI)
    assert [(x["sablon"], x.get("eroare")) for x in e if x.get("sablon")] == [(sid, MOTIV_NEPLATITOR)], e
    ultima, motiv, la = _stare(mediu, sid)
    # CF art.310 alin.(10) lit.b: neplătitorul „nu are voie să menționeze taxa pe factură” -> refuzul real al emiterii, consemnat
    assert ultima is None and la == AZI and motiv == MOTIV_NEPLATITOR, motiv
    assert _sql(mediu, "SELECT count(*) FROM facturi")[0][0] == 0
    n = _notificari(mediu)
    assert n == [(fr.TIP_REFUZ, fr.text_refuz("Firma FE3 SRL", {"tert_nume": "Client Recurent SRL"}, motiv, AZI), True)], n
    assert n[0][1] == ("Firma FE3 SRL: factura recurentă pentru Client Recurent SRL nu s-a emis (10.03.2099). Motivul: " + MOTIV_NEPLATITOR +
                       " Aplicația o încearcă din nou zilnic, până la sfârșitul lunii; motivul e și pe șablon, în Facturi → Facturi recurente."), n
    # emailul: cutia de ieșire comună, pe canalul omului (implicit email), cu eticheta tipului
    assert notificari.livreaza_in_asteptare() == {"email": 1}
    assert [(a, s) for a, s, _h in mediu["emailuri"]] == [("ztest_fe3_admin@invalid", "iConta.eu — o factură recurentă nu s-a emis")]
    assert "plătitoare" not in mediu["emailuri"][0][2]
    # a doua rulare a zilei: același refuz, nicio notificare nouă
    fr.emite_scadente(SCH, AZI)
    assert len(_notificari(mediu)) == 1 and _stare(mediu, sid)[2] == AZI
    # luna următoare: factura altei luni, refuzată din nou -> o notificare nouă
    fr.emite_scadente(SCH, LUNA_URM)
    assert len(_notificari(mediu)) == 2 and _stare(mediu, sid)[2] == LUNA_URM
    # firma redevine plătitoare: factura lunii se emite, refuzul consemnat se golește
    _sql(mediu, "UPDATE firma_profil SET platitor_tva = true WHERE id = 1")
    e = fr.emite_scadente(SCH, LUNA_URM)
    assert [bool(x.get("factura")) for x in e if x.get("sablon")] == [True], e
    assert _stare(mediu, sid) == (LUNA_URM, None, None)
    assert len(_notificari(mediu)) == 2


def test_def_c109_verificarile_drumului_si_cursul_bnr_refuzat_se_consemneaza(mediu, monkeypatch):
    """Două șabloane scrise direct (ca înainte): unul fără denumirea beneficiarului (`verificari_drum`), unul în EUR al cărui curs BNR e
    refuzat la emitere (`emite_factura` întoarce `{"ok": False}`). Amândouă: refuzul pe șablon, nicio factură — iar șablonul în EUR NU e
    trecut emis (înainte: `ultima_emitere` = ziua, deci luna aceea nu se mai încerca, fără niciun semn).
    MUTAȚIE: ramura `r.get("ok") is False` scoasă din `emite_scadente` -> `ultima_emitere` = AZI -> ROȘU."""
    from core import facturi_api, facturi_recurente as fr
    refuz_curs = {"ok": False, "cod": "CURS_PREA_VECHI", "mesaj": "Cursul BNR pentru EUR e prea vechi pentru data facturii."}
    monkeypatch.setattr(facturi_api, "curs_automat", lambda *a, **k: dict(refuz_curs))
    for i, (nume, moneda) in enumerate(((None, "RON"), ("Client Valuta SRL", "EUR")), 1):
        _sql(mediu, "INSERT INTO facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere, moneda) VALUES (%s,%s,%s,%s,1,%s)",
             (i, nume, CUI_CLIENT, json.dumps([LINIE]), moneda))
    e = fr.emite_scadente(SCH, AZI)
    assert sorted((x["sablon"], x.get("eroare")) for x in e if x.get("sablon")) == [(1, fr.MESAJ_BENEFICIAR), (2, refuz_curs["mesaj"])], e
    assert _stare(mediu, 1) == (None, fr.MESAJ_BENEFICIAR, AZI)
    assert _stare(mediu, 2) == (None, refuz_curs["mesaj"], AZI)
    assert _sql(mediu, "SELECT count(*) FROM facturi")[0][0] == 0
    assert [t for t, _x, _d in _notificari(mediu)] == [fr.TIP_REFUZ, fr.TIP_REFUZ]


def test_def_c109_caderea_aplicatiei_nu_ajunge_la_contabil_ca_text_tehnic(mediu, monkeypatch):
    """O excepție care nu e un refuz al emiterii (o cădere a aplicației): contabilul citește „a apărut o eroare neprevăzută…”, nu textul
    tehnic; operatorul e anunțat (`observare.esec_secundar`); jurnalul jobului păstrează textul întreg."""
    from core import facturi_api, facturi_recurente as fr, observare
    sid = _adauga(mediu)["id"]
    semnalate = []
    monkeypatch.setattr(observare, "esec_secundar", lambda et, e, **k: semnalate.append((et, str(e))))

    def _cade(*a, **k):
        raise RuntimeError("relation \"facturi\" does not exist")
    monkeypatch.setattr(facturi_api, "emite_factura", _cade)
    e = fr.emite_scadente(SCH, AZI)
    assert [x.get("eroare") for x in e if x.get("sablon")] == ['relation "facturi" does not exist'], e
    assert _stare(mediu, sid)[1] == fr.MESAJ_NEPREVAZUT
    assert semnalate == [("emiterea facturii recurente %s/%s" % (SCH, sid), 'relation "facturi" does not exist')], semnalate
    assert "does not exist" not in _notificari(mediu)[0][1]


def test_c109_refuzul_se_anunta_cand_e_nou_sau_din_alta_luna():
    """PURĂ: fără refuz consemnat -> se anunță; același motiv în aceeași lună -> nu; alt motiv -> da; aceeași motiv, altă lună -> da."""
    from core import facturi_recurente as fr
    d = datetime.date(2099, 3, 20)
    assert fr.refuz_de_anuntat({}, "M", d)
    assert not fr.refuz_de_anuntat({"ultimul_refuz": "M", "ultimul_refuz_la": "2099-03-10"}, "M", d)
    assert fr.refuz_de_anuntat({"ultimul_refuz": "M", "ultimul_refuz_la": "2099-03-10"}, "Alt motiv", d)
    assert fr.refuz_de_anuntat({"ultimul_refuz": "M", "ultimul_refuz_la": "2099-02-28"}, "M", d)


def test_c109_tipul_notificarii_e_al_celor_care_pregatesc_si_bifat_din_oficiu():
    """În Setări cont → Notificări, grupa „Facturi și SPV”: îl văd administratorul și asistentul cu „Poate pregăti”, bifat din oficiu;
    asistentul numai cu „Poate valida” și clientul nu-l văd. Eticheta e scurtă, fără cifre (pleacă pe email / WhatsApp)."""
    from core import facturi_recurente as fr, notificari as N
    t = N.TIPURI[fr.TIP_REFUZ]
    assert t["grup"] == "Facturi și SPV" and t["cine"] == "pregatire" and N.implicit(fr.TIP_REFUZ)
    assert N.dorit(fr.TIP_REFUZ, {}) and not N.dorit(fr.TIP_REFUZ, {fr.TIP_REFUZ: False})   # bifa omului decide (320)
    assert not N.implicit("factura_primita")                                               # celelalte tipuri ale grupei: neschimbate
    vede = lambda a: fr.TIP_REFUZ in [x["cheie"] for g in N.lista_pentru(a, None) for x in g["tipuri"]]   # noqa: E731
    assert vede({"rol": "admin_firma"}) and vede({"rol": "angajat", "poate_pregati": True})
    assert not vede({"rol": "angajat", "poate_valida": True}) and not vede({"rol": "client"})


def test_c109_notificarea_pe_conexiune_nu_comite_si_nu_anuleaza():
    """`notificari_termene.notifica_pe_conexiune` scrie în tranzacția apelantului: nici commit, nici rollback (firma fără cabinet -> 0)."""
    from core import notificari_termene as nt

    class _C:
        def __init__(s):
            s.acte = []

        def cursor(s):
            class _K:
                def __enter__(k):
                    return k

                def __exit__(k, *a):
                    return False

                def execute(k, *a):
                    s.acte.append(a[0][:30])

                def fetchone(k):
                    return None
            return _K()

        def commit(s):
            s.acte.append("COMMIT")

        def rollback(s):
            s.acte.append("ROLLBACK")
    c = _C()
    assert nt.notifica_pe_conexiune(c, "tenant_x", "factura_recurenta_refuzata", lambda n: n) == 0
    assert "COMMIT" not in c.acte and "ROLLBACK" not in c.acte, c.acte


# ── 12.3 pct.9 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_9_cota_si_categoria_liniei_trec_din_sablon_pe_factura_lunara(mediu):
    """Plătitorul, clientul din DE: linia 0% cu categoria „serviciu_extern” (CF art.278 alin.(2): locul prestării, la beneficiar) se
    salvează — înainte refuzată („în șablon nu se alege categoria”) — și factura lunară o poartă: linia cu categoria, țara DE, axa
    „servicii”. Linia cu 0% fără categorie: refuzată lângă câmpul categoriei, ca la emitere.
    MUTAȚIE: `categorie_331=` / categoria scoase din proba de salvare nu schimbă nimic aici; categoria scoasă din liniile trimise de ecran ->
    `core/test_lot12_fe3_ecrane.py` ROȘU; ramura plătitorului din `verificari_drum` repusă pe „nicio linie cu categorie” -> linia 21% de mai
    jos refuzată -> ROȘU."""
    from core import categorii_tva, facturi_recurente as fr
    r = _adauga(mediu, tert_cui=COD_DE, tert_nume="KUNDE GMBH", tert_tara="DE", linii=[dict(SERVICIU)])
    assert set(r) == {"id"}, r
    assert _sql(mediu, "SELECT linii->0->>'categorie_tva', categorie_331 FROM facturi_recurente WHERE id = %s", (r["id"],)) == [
        ("serviciu_extern", None)]
    e = fr.emite_scadente(SCH, AZI)
    assert [bool(x.get("factura")) for x in e if x.get("sablon")] == [True], e
    assert _sql(mediu, "SELECT f.tert_tara, f.axa_ic, l.cota_tva::int, l.categorie_tva FROM facturi f JOIN factura_linii l ON l.factura_id = f.id"
                ) == [("DE", "servicii", 0, "serviciu_extern")]
    rau = _adauga(mediu, tert_cui=COD_DE, tert_nume="KUNDE GMBH", tert_tara="DE", linii=[dict(SERVICIU, categorie_tva=None)])
    assert ("fr-l0-categorie", "Linia 1: categoria de TVA — " + categorii_tva.MESAJ_LIPSA) in _pe_campuri(rau), rau
    # [12.3 pct.9] cota ALEASĂ pe linie (21%) către clientul din DE: alegerea contabilului, ca la „Emite factură” — se salvează
    assert set(_adauga(mediu, tert_cui=COD_DE, tert_nume="KUNDE GMBH", tert_tara="DE", linii=[dict(LINIE)])) == {"id"}


def test_9_taxarea_inversa_cere_categoria_produsului_pe_sablon_si_o_duce_pe_factura(mediu):
    """Linia 0% cu „taxare_inversa” (clientul român): fără categoria produsului (codul D394) -> refuz lângă „Categoria produsului” a
    șablonului (`fr-c331`, nu un câmp al emiterii); cu ea -> salvat, iar factura lunară o poartă (`facturi.categorie_331`). O categorie
    trimisă fără nicio linie cu taxare inversă nu se păstrează (câmpul nu se arată atunci).
    MUTAȚIE: `categorie_331=s.get("categorie_331")` scos din `emite_scadente` -> factura lunară refuzată -> ROȘU; maparea `em-c331` ->
    `fr-c331` scoasă din `_camp_sablon` -> refuzul fără câmp -> ROȘU."""
    from core import facturi_recurente as fr, produse_api
    cod = sorted(produse_api.coduri_331())[0]
    linie = {"descriere": "Deseuri feroase", "cantitate": 1, "pret_unitar": 100, "cota_tva": 0, "categorie_tva": "taxare_inversa",
             "cont_venit": "707"}
    rau = _adauga(mediu, linii=[dict(linie)])
    assert [c for c, _m in _pe_campuri(rau)] == ["fr-c331"], rau
    r = _adauga(mediu, linii=[dict(linie)], categorie_331=cod)
    assert set(r) == {"id"}, r
    assert _sql(mediu, "SELECT categorie_331 FROM facturi_recurente WHERE id = %s", (r["id"],)) == [(cod,)]
    e = fr.emite_scadente(SCH, AZI)
    assert [bool(x.get("factura")) for x in e if x.get("sablon")] == [True], e
    assert _sql(mediu, "SELECT categorie_331 FROM facturi") == [(cod,)]
    r2 = _adauga(mediu, categorie_331=cod)   # linia 21%, fără taxare inversă
    assert _sql(mediu, "SELECT categorie_331 FROM facturi_recurente WHERE id = %s", (r2["id"],)) == [(None,)]


def test_9_sablonul_vechi_fara_cota_catre_clientul_strain_ramane_refuzat_la_cron(mediu):
    """Datele existente: un șablon al plătitorului către clientul din DE cu linia FĂRĂ cotă (cum îl putea scrie API-ul) nu se emite cu cota
    din nomenclator: refuzul lângă cota liniei, consemnat pe șablon și anunțat."""
    from core import facturi_recurente as fr
    _sql(mediu, "INSERT INTO facturi_recurente (id, tert_nume, tert_cui, tert_tara, linii, zi_emitere) VALUES (1,'KUNDE GMBH',%s,'DE',%s,1)",
         (COD_DE, json.dumps([dict(LINIE, cota_tva=None)])))
    e = fr.emite_scadente(SCH, AZI)
    assert [x.get("eroare") for x in e if x.get("sablon")] == [fr.MESAJ_STRAIN_FARA_COTA % (1, "DE")], e
    assert _stare(mediu, 1)[1] == fr.MESAJ_STRAIN_FARA_COTA % (1, "DE")
    assert _sql(mediu, "SELECT count(*) FROM facturi")[0][0] == 0


# ── structura ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_structura_starii_sablonului_si_migrarea():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_sablon_recurent_stare.bloc_template()`; migrarea e idempotentă
    și lasă șabloanele existente fără refuz consemnat (NULL)."""
    from core import migrare_sablon_recurent_stare as m
    assert m.bloc_template() in io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    _db.init_pool()
    p = _db.pool()
    c = p.getconn()
    try:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("ALTER TABLE %s.facturi_recurente DROP COLUMN IF EXISTS ultimul_refuz, DROP COLUMN IF EXISTS ultimul_refuz_la, "
                        "DROP COLUMN IF EXISTS categorie_331" % SCH)
            cur.execute("INSERT INTO %s.facturi_recurente (id, tert_nume, linii) VALUES (1, 'A SRL', '[]')" % SCH)
        assert not m.verifica(c, SCH)
        m.aplica(c, SCH)
        m.aplica(c, SCH)
        assert m.verifica(c, SCH)
        with c.cursor() as cur:
            cur.execute("SELECT ultimul_refuz, ultimul_refuz_la, categorie_331 FROM %s.facturi_recurente" % SCH)
            assert cur.fetchall() == [(None, None, None)]
    finally:
        c.rollback()
        p.putconn(c)
