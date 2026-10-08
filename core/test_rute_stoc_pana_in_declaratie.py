# -*- coding: utf-8 -*-
"""Patru din cele opt rute cu clichet fiscal, probate PANA IN CIFRA DECLARATIEI.

DE UNDE VINE. `PREDARE_LANT.md` 0Z, lucrarea 3: *„cele 8 rute cu clichet care ating cifre de
declaratie"* — cele opt din cele 88 care scriu fara proba in suita SI ating tabele din care se ridica
declaratii. Predarea spune, tot ea, de ce n-aveau proba: *„fiecare cere o lume pregatita — de-aia
n-au proba, nu din uitare"*. Aici se pregateste lumea aia, o data, pentru patru dintre ele:

  POST /tenants/{id}/stocuri/iesire
  POST /tenants/{id}/stocuri/inventar
  POST /tenants/{id}/stocuri/reclasificare
  POST /tenants/{id}/reevaluare-imobilizare

CE INTREABA, si de ce NU codul HTTP. `core/test_rute_probate.py` spune despre subsetul asta:
*„o ruta de aici greseste intr-un FISIER DEPUS LA ANAF, nu pe un ecran. De-aia probele lui merg pana
in randul declaratiei, nu pana la 200."* Deci fiecare proba de mai jos face trei lucruri, in ordine:

  1. apasa RUTA, prin HTTP, cu jeton real si rol real;
  2. **valideaza nota** pe care ruta o produce — toate trei rutele de stoc scriu CIORNA, iar ciorna
     NU e evidenta: declaratia citeste numai note validate;
  3. citeste cifra din **declaratie** — rulajul contului din `d406`/`control_incrucisat`, adica exact
     sursa din care se ridica `GeneralLedgerEntries`.

CE NU DEMONSTREAZA, declarat: corectitudinea CMP-ului pe metode (aia e `core/test_stocuri_*.py`) si
structura XML a D406 (aia e `core/test_d406*.py`). Aici se probeaza ca efectul rutei **ajunge** acolo.

LUMEA, declarata: firma efemera din `tenant_template.sql`, un articol de marfa cu o intrare de
10 buc x 10,00 lei (CMP 10,00), si un mijloc fix de 6.000 lei pe 60 de luni. Toate scrierile stau
intr-o singura tranzactie, anulata la final — `db.get_conn` e intors spre aceeasi conexiune, tiparul
din `core/test_portal_bon.py`.
"""
from __future__ import annotations

import contextlib
from decimal import Decimal

import pytest

from core import db as _db

SCH = "ztest_rute_stoc"
AN, LUNA = 2026, 3
ZI = "%d-%02d-15" % (AN, LUNA)

# Lumea, in cifre (se refac cu creionul):
CANT_INTRARE = Decimal("10")
PRET_INTRARE = Decimal("10.00")        # CMP = 10,00
VAL_INTRARE = CANT_INTRARE * PRET_INTRARE   # 100,00
MF_VALOARE = Decimal("6000")
MF_DNF = 60


class _ConnProxy:
    """Conexiunea reala, cu `commit`/`rollback` inerte: totul ramane in tranzactia probei."""

    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def lume(monkeypatch):
    from core import auth_api, tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST RUTE STOC') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_rute_stoc@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT RUTE STOC','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

            # ── lumea pregatita ────────────────────────────────────────────────
            cur.execute('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) '
                        "VALUES ('Marfa proba','buc','371','607') RETURNING id" % SCH)
            aid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, '
                        "pret_unitar, valoare, document) "
                        "VALUES (%%s,%%s,'intrare',%%s,%%s,%%s,'NIR-proba')" % SCH,
                        (aid, "%d-%02d-01" % (AN, LUNA), CANT_INTRARE, PRET_INTRARE, VAL_INTRARE))
            cur.execute('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, '
                        "cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda) "
                        "VALUES ('MF-PROBA','Utilaj proba','2131','2813',%%s,0,%%s,%%s,'liniara') "
                        "RETURNING id" % SCH,
                        (MF_VALOARE, MF_DNF, "%d-01-15" % (AN - 1)))
            mfid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "conn": conn, "aid": aid, "mfid": mfid, "schema": SCH, "uid": uid,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(lume):
    return {"Authorization": "Bearer " + lume["tok"]}


def _rulaj(lume, cont):
    """Cifra DIN DECLARATIE: rulajul contului pe luna, prin `control_incrucisat.rulaje_luna` —
    sursa unica de rulaje din repo, chiar cea din care se ridica `GeneralLedgerEntries`.

    Citeste DOAR note validate. De-aia fiecare proba valideaza nota inainte de a citi aici: o ciorna
    nu e evidenta, iar o proba care ar citi ciorne ar spune ca efectul a ajuns in declaratie cand el
    de fapt n-a ajuns.
    """
    from core import control_incrucisat as _ci
    r = _ci.rulaje_luna(_ConnProxy(lume["conn"]), SCH, AN, LUNA, [cont])
    return r[cont]


def _valideaza_notele(lume, cl):
    """Valideaza TOATE ciornele firmei, prin ruta aplicatiei. Intoarce cate a validat.

    Prin RUTA, nu prin `UPDATE`: altfel proba ar sari peste chiar poarta care transforma o propunere
    in evidenta — si ar afirma despre declaratie ceva ce aplicatia nu face.
    """
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT id FROM \"%s\".inregistrari WHERE status='ciorna' ORDER BY id" % SCH)
        ids = [r[0] for r in cur.fetchall()]
    for i in ids:
        r = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume["tid"], i), json={}, headers=_H(lume))
        assert r.status_code == 200, (i, r.status_code, r.text[:200])
    return len(ids)


# ─────────────────────────── stocuri/iesire ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_IESIREA_de_stoc_ajunge_in_rulajul_contului_de_cheltuiala(lume):
    """`POST /tenants/{id}/stocuri/iesire` — 3 buc la CMP 10,00 -> nota `607 = 371`, 30,00.

    Se citesc AMANDOUA conturile: numai `607` ar trece si daca stocul nu s-ar fi descarcat.
    """
    with lume["conn"].cursor() as cur:   # [06.10.2026 §6.3] ieșirea pe articol e a firmei cantitativ-valorice (metoda explicită)
        cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, metoda_stoc) VALUES (1, \'TENANT\', \'14399840\', \'cantitativ_valoric\') '
                    "ON CONFLICT (id) DO UPDATE SET metoda_stoc = EXCLUDED.metoda_stoc" % SCH)
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/iesire" % lume["tid"],
                json={"articol_id": lume["aid"], "data": ZI, "cantitate": 3,
                      "document": "AVIZ-1"}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    # Pe VALOARE, nu pe sirul ei: ruta intoarce CMP-ul cu patru zecimale (`10.0000`), fiindca asa
    # il tine `miscari_stoc.pret_unitar`. Prima forma a probei astepta `10.00` — asteptarea era a
    # mea, nu a codului.
    assert Decimal(r.json()["cmp"]) == PRET_INTRARE, r.json()
    assert Decimal(r.json()["valoare"]) == Decimal("30.00"), r.json()

    # inainte de validare, declaratia NU vede nimic — ciorna nu e evidenta
    assert _rulaj(lume, "607")["debit"] == Decimal("0")
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "607")["debit"] == Decimal("30.00")
    assert _rulaj(lume, "371")["credit"] == Decimal("30.00")


# ─────────────────────────── stocuri/inventar ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_MINUSUL_de_inventar_ajunge_in_rulaj(lume):
    """`POST /tenants/{id}/stocuri/inventar` — faptic 8 fata de scriptic 10 -> minus de 2 buc.

    Temei: OMFP 1802/2014, functiunea conturilor 371/607 (minusul se scoate pe cheltuiala).
    """
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/inventar" % lume["tid"],
                json={"data": ZI, "linii": [{"articol_id": lume["aid"], "faptic": 8}]},
                headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert _valideaza_notele(lume, cl) >= 1
    assert _rulaj(lume, "607")["debit"] == Decimal("20.00"), "minusul de 2 x 10,00 n-a ajuns"
    assert _rulaj(lume, "371")["credit"] == Decimal("20.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_inventar_FARA_LINII_se_REFUZA(lume):
    """Directia cealalta, si e o regula scrisa: *„un inventar fara linii nu e o inventariere fara
    diferente — e o inventariere care nu s-a facut"*. Fara proba asta, `200` pe un corp gol ar
    arata identic cu o inventariere curata."""
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/inventar" % lume["tid"], json={"data": ZI, "linii": []},
                headers=_H(lume))
    # 422, nu 400: refuzul vine ca `DateInvalide`, iar harta `main._COD_EROARE` il duce acolo.
    # Asteptarea de 400 era a mea.
    assert r.status_code == 422, (r.status_code, r.text[:200])
    # Se cere sa EXISTE un motiv, nu un anumit CUVANT in el: calitatea mesajului are gardile ei
    # (diacritice, limbaj, `interactiune_scan`), iar un `"inventariere" in mesaj` scris aici ar pazi
    # formularea de langa lucru, nu lucrul — clichetul aserțiunilor pe text l-a si respins.
    assert (r.json().get("detail") or "").strip(), "refuz fara niciun motiv scris"
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "un inventar refuzat a lasat totusi o nota"


# ─────────────────────────── stocuri/reclasificare ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_RECLASIFICAREA_muta_soldul_intre_conturi_de_stoc(lume):
    """`POST /tenants/{id}/stocuri/reclasificare` — marfa 371 -> materie prima 301.

    Nota mută soldul la CMP (`301 = 371`, 100,00), iar **cantitatea nu se atinge**. Se verifica si
    ca articolul poarta contul nou: fara asta, o nota corecta peste un articol neschimbat ar trece.
    """
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/reclasificare" % lume["tid"],
                json={"articol_id": lume["aid"], "cont_stoc_nou": "301",
                      "cont_cheltuiala_nou": "601", "data": ZI}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "301")["debit"] == VAL_INTRARE
    assert _rulaj(lume, "371")["credit"] == VAL_INTRARE
    with lume["conn"].cursor() as cur:
        cur.execute('SELECT cont_stoc, cont_cheltuiala FROM "%s".articole WHERE id=%%s' % SCH,
                    (lume["aid"],))
        assert cur.fetchone() == ("301", "601")
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate ELSE -cantitate END),0) "
                    'FROM "%s".miscari_stoc WHERE articol_id=%%s' % SCH, (lume["aid"],))
        assert Decimal(str(cur.fetchone()[0])) == CANT_INTRARE, "reclasificarea a atins cantitatea"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_RECLASIFICAREA_pe_acelasi_cont_se_REFUZA(lume):
    """A doua directie: contul neschimbat nu e o reclasificare, si nu trebuie sa produca nota."""
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/reclasificare" % lume["tid"],
                json={"articol_id": lume["aid"], "cont_stoc_nou": "371", "data": ZI},
                headers=_H(lume))
    assert r.status_code == 400, r.status_code
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0


# ─────────────────────────── reevaluare-imobilizare ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_REEVALUAREA_ajunge_pe_registru_SI_in_rulaj_dupa_validare(lume):
    """`POST /tenants/{id}/reevaluare-imobilizare` — a patra ruta a subsetului.

    E aceeasi afirmatie ca `core/test_reevaluare_registru.py`, dar apasata **prin HTTP**: acolo se
    probeaza use-case-ul si lantul pe schema efemera, aici RUTA. *Clichetul fiscal scade doar cand
    ruta insasi are proba in suita — nu cand o are functia de sub ea.*

    Activ 6.000 / 60 de luni, PIF 15.01.<AN-1>: la 15.03.<AN> au trecut 14 luni x 100,00 = 1.400,00
    amortizare cumulata, deci valoarea neta e 4.600,00. Reevaluat la 5.000 -> diferenta 400,00.

    [R192, 17.09.2026] Lumea probei poarta acum si amortizarea INREGISTRATA. Pana la decizia lui
    Costin, proba asta trecea peste un cont `2813` gol — adica exact starea in care reevaluarea
    scadea o amortizare care nu s-a inregistrat niciodata. *Proba n-a fost slabita ca sa treaca
    noua regula: i s-a completat lumea cu ce ii lipsea.*
    """
    cl = _client()
    _inregistreaza_amortizarea(lume, Decimal("1400.00"))
    r = cl.post("/tenants/%d/reevaluare-imobilizare" % lume["tid"],
                json={"data": ZI, "operatie": "reevaluare", "mijloc_fix_id": lume["mfid"],
                      "valoare_justa": 5000}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    corp = r.json()
    assert corp["valoare_neta"] == "4600.00", corp
    assert corp["diferenta"] == "400.00", corp
    assert corp["amortizare_eliminata"] == "1400.00", corp

    def _valoare_registru():
        with lume["conn"].cursor() as cur:
            cur.execute('SELECT valoare FROM "%s".mijloace_fixe WHERE id=%%s' % SCH, (lume["mfid"],))
            return Decimal(str(cur.fetchone()[0]))

    assert _valoare_registru() == MF_VALOARE, "ciorna a miscat registrul"
    assert _valideaza_notele(lume, cl) == 1
    assert _valoare_registru() == Decimal("5000")
    # si in evidenta: eliminarea cumulatei (2813 = 2131) plus diferenta (2131 = 105)
    assert _rulaj(lume, "2813")["debit"] == Decimal("1400.00")
    assert _rulaj(lume, "105")["credit"] == Decimal("400.00")


# ─────────────────────────── mijloace-fixe/{id}/destinatie-cd ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_BIFA_CD_deschide_accelerata_si_activul_ajunge_in_D406_Assets(lume):
    """`PUT /tenants/{id}/mijloace-fixe/{mijloc_id}/destinatie-cd` (lot 19, defectul 11) — apasata PRIN HTTP, pana in
    cifra declaratiei: sectiunea Assets din D406 (`/d406-active`, din `repo_mijloace_fixe.active_pentru_d406`).

    CF art.20 alin.(1) lit.b): „aplicarea metodei de amortizare accelerată și în cazul aparaturii și echipamentelor
    destinate activităților de cercetare-dezvoltare”. Un echipament pe 2132 cu metoda accelerata: fara bifa, D406
    refuza activul (CF art.28 alin.(5) lit.c) — 422); cu bifa, il declara cu `DepreciationMethod` accelerata."""
    import xml.etree.ElementTree as ET
    with lume["conn"].cursor() as cur:
        cur.execute('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, '
                    "rezidual, dnf_luni, data_pif, metoda) VALUES ('MF-CD','Spectrometru C&D','2132','2813',60000,0,"
                    "60,%%s,'accelerata') RETURNING id" % SCH, ("%d-01-15" % AN,))
        cd = cur.fetchone()[0]
    cl = _client()
    inainte = cl.get("/tenants/%d/d406-active?an=%d" % (lume["tid"], AN), headers=_H(lume))
    assert inainte.status_code == 422, (inainte.status_code, inainte.text[:200])
    r = cl.put("/tenants/%d/mijloace-fixe/%d/destinatie-cd" % (lume["tid"], cd), json={"destinatie_cd": True},
               headers=_H(lume))
    assert r.status_code == 200 and r.json()["destinatie_cd"] is True, r.text[:200]
    dupa = cl.get("/tenants/%d/d406-active?an=%d" % (lume["tid"], AN), headers=_H(lume))
    assert dupa.status_code == 200, dupa.text[:300]
    # fragmentul SAF-T foloseste prefixul nsSAFT nedeclarat (se lipeste in fisierul complet) -> radacina care il declara
    rad = ET.fromstring('<r xmlns:nsSAFT="urn:saft">%s</r>' % dupa.text)
    ns = {"n": "urn:saft"}
    active = {a.findtext("n:AssetID", namespaces=ns): a for a in rad.iter() if a.tag.endswith("}Asset")}
    activ = active.get("MF-CD")
    assert activ is not None, sorted(active)
    metode = [e.text for e in activ.iter() if e.tag.endswith("}DepreciationMethod")]
    assert metode and set(metode) == {"accelerata"}, metode
    # [decizia Costin 04.10.2026] fără rol separat — schimbarea se jurnalizează: utilizatorul din token, data, veche -> nouă
    with lume["conn"].cursor() as cur:
        cur.execute('SELECT camp, valoare_veche, valoare_noua, user_id, la IS NOT NULL FROM "%s".mijloace_fixe_jurnal '
                    "WHERE mijloc_id = %%s ORDER BY id" % SCH, (cd,))
        assert cur.fetchall() == [("destinatie_cd", "false", "true", lume["uid"], True)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CHITANTA_FARA_COTA_clasificata_prin_HTTP_ajunge_in_D394_I2(lume):
    """`POST /tenants/{id}/chitante` + `PUT /tenants/{id}/chitante/{chitanta_id}/cota` (D394 Î2, deciziile Costin
    03.10.2026) — PRIN HTTP, până în cifra declarației: op2 Î2 din D394 (`d394.genereaza`, chitanțele din `chitante`).

    OUG 28/1999 art.1 alin.(1) / art.2; OPANAF 2194/2025 anexa 2 lit.G pct.15–17. O chitanță fără factură emisă cât
    firma nu era marcată exceptată e o încasare de creanță (5311=4111); după marcare, D394 o refuză numită până primește
    cota; cota se stabilește prin ruta nouă, iar nota ciornă devine 5311 = venit + 5311 = 4427."""
    import xml.etree.ElementTree as ET
    from core import d394
    from core.common import Perioada
    cl = _client()
    with lume["conn"].cursor() as cur:
        cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, '
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare, declarant_nume, declarant_prenume, "
                    "declarant_functie) VALUES (1,'TENANT RUTE STOC','14399840','Str Test 1','Bucuresti','B','4322',"
                    "'0722000000','BCR','RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR') "
                    "ON CONFLICT (id) DO NOTHING" % SCH)
    # [lotul 07.10 B, comanda Costin A.3] exceptarea AMEF n-are implicit: neleasă, prima chitanță fără factură o cere (prin HTTP)
    r0 = cl.post("/tenants/%d/chitante" % lume["tid"], json={"data": ZI, "suma": 242}, headers=_H(lume))
    assert (r0.status_code, r0.json()["detail"]["cod"], r0.json()["detail"]["ecran"]) == (400, "AMEF_EXCEPTARE_NEDECLARATA", "date_firma")
    with lume["conn"].cursor() as cur:
        cur.execute('UPDATE "%s".firma_profil SET activitate_exceptata_amef = false' % SCH)   # declarată „Nu” în Date firmă
    # [decizii 07.10 pct.5] seria chitanței: fără „CH” din oficiu — cerută la prima chitanță, cu trimitere în Date firmă
    # (OMFP 2634/2015 anexa 1 pct.24: seria „stabilit(ă) de entitate”)
    r1 = cl.post("/tenants/%d/chitante" % lume["tid"], json={"data": ZI, "suma": 242}, headers=_H(lume))
    assert (r1.status_code, r1.json()["detail"]["cod"], r1.json()["detail"]["ecran"]) == (400, "SERIE_CHITANTA_LIPSA", "date_firma")
    with lume["conn"].cursor() as cur:
        cur.execute('UPDATE "%s".firma_profil SET serie_chitanta = \'ZC\'' % SCH)   # aleasă de firmă în Date firmă
    r = cl.post("/tenants/%d/chitante" % lume["tid"], json={"data": ZI, "suma": 242}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    cid = r.json()["chitanta_id"]
    refuz = cl.post("/tenants/%d/chitante" % lume["tid"], json={"data": ZI, "suma": 121, "cota_tva": 21}, headers=_H(lume))
    assert (refuz.status_code, refuz.json()["detail"]["cod"]) == (400, "CHITANTA_VANZARE_FARA_EXCEPTARE_AMEF")
    with lume["conn"].cursor() as cur:
        cur.execute('UPDATE "%s".firma_profil SET activitate_exceptata_amef = true, activitate_amef = \'i\'' % SCH)
        cur.execute('SET search_path TO "%s", public' % SCH)   # generatorul citește necalificat
    with pytest.raises(ValueError):          # neclasificată -> refuz numit
        d394.genereaza(_ConnProxy(lume["conn"]), SCH, Perioada(AN, luna=LUNA))
    r = cl.put("/tenants/%d/chitante/%d/cota" % (lume["tid"], cid), json={"cota_tva": 21}, headers=_H(lume))
    assert (r.status_code, r.json().get("nota")) == (200, "5311=707 + 5311=4427"), r.text[:300]
    with lume["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
    xml, _res = d394.genereaza(_ConnProxy(lume["conn"]), SCH, Perioada(AN, luna=LUNA))
    ns = "{%s}" % d394.NS
    (o,) = [dict(e.attrib) for e in ET.fromstring(xml.split("?>", 1)[1]).iter(ns + "op2")]
    # 242 lei la 21%: baza 200, TVA 42 (suta mărită)
    assert (o["tip_op2"], o["total"], o["baza21"], o["TVA21"]) == ("I2", "242", "200", "42")


# ─────────────────────────── anti-vacuu pe lumea insasi ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_VACUU_lumea_chiar_e_pregatita(lume):
    """O lume goala ar face fiecare proba de mai sus sa treaca pe zerouri egale. *O comparatie
    intre doua zerouri nu discrimineaza nimic.*"""
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".articole" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".miscari_stoc WHERE tip='intrare'" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".mijloace_fixe" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "lumea porneste cu note — probele n-ar mai masura ce au produs"


def _inregistreaza_amortizarea(lume, suma):
    """Amortizarea deja INREGISTRATA in contul de amortizare, ca nota validata.

    E precondiția pe care reevaluarea o cere de la R192 incoace: nu se poate scoate din evidenta o
    amortizare pe care evidenta n-o contine."""
    with lume["conn"].cursor() as cur:
        cur.execute('INSERT INTO "%s".inregistrari (data, descriere, sursa, status) '
                    "VALUES (%%s,'amortizare cumulata proba','amortizare','validata') RETURNING id"
                    % SCH, ("%d-%02d-01" % (AN, LUNA),))
        iid = cur.fetchone()[0]
        cur.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, '
                    "cont_credit, suma) VALUES (%%s,'6811','2813',%%s)" % SCH, (iid, suma))


# ─────────────────────── R192: reevaluarea nu elimină ce nu s-a înregistrat ───────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_R192_reevaluarea_se_REFUZA_cand_amortizarea_nu_e_INREGISTRATA(lume):
    """[R192, decizia lui Costin — 17.09.2026] Reevaluarea porneste prin scoaterea din evidenta a
    amortizarii strange (`2813 = 2131`). Cifra aia vine din REGISTRU; soldul contului vine din
    NOTELE chiar inregistrate. Daca registrul o ia inainte, nota ar scadea din cont o amortizare
    care nu exista acolo — soldul trece pe minus, iar valoarea ramasa devine o **cifra valida si
    falsa**: se calculeaza, se afiseaza, pleaca in declaratie, si nimic n-o contrazice.

    In lumea probei, contul `2813` e GOL (nicio nota lunara), iar registrul spune 1.400,00 la
    15.03.2026. Deci reevaluarea trebuie REFUZATA.
    """
    cl = _client()
    r = cl.post("/tenants/%d/reevaluare-imobilizare" % lume["tid"],
                json={"data": ZI, "operatie": "reevaluare", "mijloc_fix_id": lume["mfid"],
                      "valoare_justa": 5000}, headers=_H(lume))
    assert r.status_code == 400, (r.status_code, r.text[:300])

    # CONTINUTUL refuzului se cere pe DATE, nu cautand cuvinte in sir (METODA §23). Judecata si
    # textul sunt PURE (`core/reevaluare.py`), deci proba poate calcula exact ce trebuie sa spuna
    # ruta si compara cu EGALITATE. *O aserțiune pe sub-sir ar pazi formularea; asta pazeste cifra.*
    from core import reevaluare as _rv
    div = _rv.divergenta_amortizare(Decimal("1400.00"), Decimal("0"))
    assert div == {"in_registru": Decimal("1400.00"), "in_cont": Decimal("0.00"),
                   "diferenta": Decimal("1400.00")}, div
    asteptat = _rv.mesaj_divergenta(div, "Utilaj proba", "2813", ZI)
    assert (r.json().get("detail") or "") == asteptat, r.json().get("detail")

    # si ca ruta chiar REFUZA pe conditia asta, nu din alta cauza: fara divergenta, judecata tace
    assert _rv.divergenta_amortizare(Decimal("1400.00"), Decimal("1400.00")) is None

    # si nu lasa nicio urma
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "un refuz a lasat totusi o nota"
        cur.execute("SELECT count(*) FROM \"%s\".reevaluari" % SCH)
        assert cur.fetchone()[0] == 0, "un refuz a consemnat totusi reevaluarea"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_R192_dupa_inregistrarea_amortizarii_reevaluarea_TRECE(lume):
    """A doua directie, si e cea care face refuzul util: dupa ce amortizarea lipsa e inregistrata,
    reevaluarea merge. *Un refuz care nu se poate ridica nu e o poarta, e un zid.*

    Se inregistreaza cele 14 luni (100,00 fiecare) prin nota de amortizare, validate — apoi aceeasi
    cerere trece, iar cifrele sunt cele din proba de deasupra.
    """
    cl = _client()
    _inregistreaza_amortizarea(lume, Decimal("1400.00"))
    r = cl.post("/tenants/%d/reevaluare-imobilizare" % lume["tid"],
                json={"data": ZI, "operatie": "reevaluare", "mijloc_fix_id": lume["mfid"],
                      "valoare_justa": 5000}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert r.json()["amortizare_eliminata"] == "1400.00", r.json()


# ── [lotul „Deciziile 07.10”, 07.10.2026] rutele noi care scriu, probate prin HTTP ────────────────────────────────────────
def test_ELEMENTELE_variabile_ale_salariului_prin_HTTP(lume):
    """S1 (retest Costin 07.10 seara): „Adaugă prime, sporuri și ore suplimentare, pe salariat și pe lună … Valori introduse de
    contabil, fără preselecție.” Ruta refuză elementul fără tip, cu câmpul numit (422), îl scrie complet (200), îl arată pe luna
    lui și îl șterge. Temei: CF art.76 alin.(1) (venit din salarii, oricare i-ar fi denumirea)."""
    cl = _client()
    with lume["conn"].cursor() as cur:
        cur.execute('INSERT INTO "%s".salariati (nume, prenume, cnp, data_angajare, ore_zi, judet_casa, functie_baza, '
                    "scutit_contrib_minim) VALUES ('POP','ION','1900101410011','2024-01-01',8,'B',true,false) RETURNING id" % SCH)
        sid = cur.fetchone()[0]
    url = "/tenants/%d/salariati/%d/elemente" % (lume["tid"], sid)
    r0 = cl.post(url, json={"an": AN, "luna": LUNA, "denumire": "prima", "suma": 500}, headers=_H(lume))
    assert r0.status_code == 422 and [x["camp"] for x in r0.json()["detail"]["erori_campuri"]] == ["tip"]
    r1 = cl.post(url, json={"an": AN, "luna": LUNA, "tip": "prima", "denumire": "prima de performanță", "suma": 500},
                 headers=_H(lume))
    assert r1.status_code == 200, r1.text[:300]
    g = cl.get(url + "?an=%d&luna=%d" % (AN, LUNA), headers=_H(lume)).json()
    assert ([e["denumire"] for e in g["elemente"]], g["total"]) == (["prima de performanță"], "500.00")
    d = cl.delete("/tenants/%d/salariati/%d/elemente/%d" % (lume["tid"], sid, r1.json()["id"]), headers=_H(lume))
    assert d.status_code == 200 and cl.get(url + "?an=%d&luna=%d" % (AN, LUNA), headers=_H(lume)).json()["elemente"] == []


def test_Z_FARA_MARFA_prin_HTTP_deblocheaza_validarea_la_cantitativ_valoric(lume):
    """D3 („Deciziile 07.10” pct.3): „Raportul Z la cantitativ-valoric: fără refuz. Descărcarea pe articol se cere explicit …;
    Z-ul nu se validează fără ea.” Prin HTTP: validarea Z-ului nedescărcat se refuză; declarația „fără marfă” trebuie să fie un
    da/nu explicit (un șir se refuză); după ea, Z-ul se validează."""
    from core import repo_contabilitate as rc
    cl = _client()
    with lume["conn"].cursor() as cur:
        cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, metoda_stoc) VALUES (1, \'TENANT\', \'14399840\', '
                    "'cantitativ_valoric') ON CONFLICT (id) DO UPDATE SET metoda_stoc = EXCLUDED.metoda_stoc" % SCH)
        zid = rc.nota_horeca_z_ciorna(cur, SCH, ZI, "Z-PROBA", "Raport Z", "Raport Z nr 1")[0]
        rc.adauga_linie_3(cur, SCH, zid, "5311", "707", 121)
        rc.adauga_z_amef(cur, SCH, zid, "8000000001", 3)
    v0 = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume["tid"], zid), headers=_H(lume))
    assert (v0.status_code, v0.json()["detail"]["cod"]) == (400, "Z_NEDESCARCAT")
    lst = cl.get("/tenants/%d/horeca/rapoarte-z?an=%d&luna=%d" % (lume["tid"], AN, LUNA), headers=_H(lume)).json()
    assert lst["descarcare_pe_articol"] is True and [(z["id"], z["iesiri"], z["fara_marfa"]) for z in lst["rapoarte"]] == [(zid, 0, None)]
    url = "/tenants/%d/horeca/raport-z/%d/fara-marfa" % (lume["tid"], zid)
    assert cl.post(url, json={"fara_marfa": "da"}, headers=_H(lume)).status_code == 400
    assert cl.post(url, json={"fara_marfa": True}, headers=_H(lume)).status_code == 200
    v1 = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume["tid"], zid), headers=_H(lume))
    assert v1.status_code == 200, v1.text[:300]


# ─────────────────────────── mijloace-fixe/{id}/cod-catalog ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CODUL_DIN_CATALOG_se_scrie_verificat_si_nu_misca_amortizarea_declarata(lume):
    """`PUT /tenants/{id}/mijloace-fixe/{mijloc_id}/cod-catalog` — [08.10.2026, decizia Costin W2] „Registrul mai afișează durata,
    codul din catalog și planul lunar de amortizare.” Scrie în `mijloace_fixe` (tabel citit de D406, secțiunea activelor), deci
    proba merge până în cifra declarată: amortizarea mijlocului (`amortizat_la_data`, aceeași din care se ridică D406) e ACEEAȘI
    înainte și după — codul e evidență (HG 2139/2004), nu un parametru de calcul.
    Un cod care nu e în catalog se refuză (422), fără scriere; unul cu durata în afara plajei se scrie, cu avertisment."""
    cl = _client()
    url = "/tenants/%d/mijloace-fixe" % lume["tid"]
    put = lambda cod: cl.put("/tenants/%d/mijloace-fixe/%d/cod-catalog" % (lume["tid"], lume["mfid"]), json={"cod_catalog": cod},
                             headers=_H(lume))
    inainte = {m["id"]: m for m in cl.get(url, headers=_H(lume)).json()["mijloace"]}[lume["mfid"]]
    r = put("9.9.9")
    assert r.status_code == 422 and r.json()["detail"]["cod"] == "COD_CATALOG_NECUNOSCUT", r.text[:300]
    r = put("2.1.1.1")
    assert r.status_code == 200 and r.json()["afirmatii"] == [], r.text[:300]    # HG 2139/2004: 2.1.1.1, plaja cuprinde 60 de luni
    r = put("2.1.17.2.1")
    assert r.status_code == 200 and [a["tip"] for a in r.json()["afirmatii"]] == ["durata_catalog"], r.text[:300]   # 12–18 ani
    dupa = {m["id"]: m for m in cl.get(url, headers=_H(lume)).json()["mijloace"]}[lume["mfid"]]
    assert (dupa["cod_catalog"], dupa["catalog"]["ani_min"]) == ("2.1.17.2.1", 12)
    assert (dupa["amortizat_teoretic"], dupa["ramas"]) == (inainte["amortizat_teoretic"], inainte["ramas"])
