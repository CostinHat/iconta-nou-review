# -*- coding: utf-8 -*-
"""GARD P2 — matricea de dependențe acoperă și RAMURILE pe care portofoliul de azi nu le atinge.

**CE PROBLEMĂ REZOLVĂ.** `scripts/scan_dependente.py` măsoară ce citește fiecare aspect — dar numai
pe drumurile pe care le exercită datele firmelor existente. Dacă nicio firmă din portofoliu nu ține
stoc, scanul nu vede `miscari_stoc`; registrul și scanul pot fi *egale și amândouă incomplete*.
*„Nicio firmă actuală n-a atins tabela X, deci X nu e necesară" nu e o măsurătoare, e o presupunere
despre datele de azi.*

**CUM SE DERIVĂ RAMURILE, și de ce nu din citirea codului.** Se măsoară ce atinge o firmă
**goală**, construită din `tenant_template.sql` cu vector fiscal complet, și se scade din ce declară
registrul. Diferența E lista ramurilor — tabelele pe care calculul le citește numai pe anumite
drumuri. Măsurat la 09.09.2026: din 27 de surse ale lui `control_fiscal`, **24 se citesc
necondiționat**, iar trei sunt sub ramuri: `miscari_stoc`, `pontaj`, `salariu_istoric`.
`termene` n-are niciuna — cele 5 surse ale lui se citesc de fiecare dată.

**CUM SE PROBEAZĂ.** Setup-urile se aplică **cumulativ** pe aceeași firmă, iar după fiecare se
măsoară din nou. *Delta* arată ce a deschis chiar setup-ul acela. Ordinea contează și e declarată:
un setup nu poate „fura" o sursă deschisă de unul anterior, fiindcă delta lui ar fi goală și proba
lui ar pica.

**DOUĂ AFIRMAȚII, nu una:**
  1. fiecare ramură cunoscută chiar se deschide (altfel fixtura n-o exercită, deci nu dovedește nimic);
  2. **nicio măsurătoare nu scoate o sursă NEDECLARATĂ.** A doua e cea care apără: un tabel citit și
     nedeclarat înseamnă o scriere care nu invalidează nimic, adică o valoare veche arătată `curent`.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import scan_dependente as SD  # noqa: E402
from core import db as _db  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402
from core import tenant_provisioning as TP  # noqa: E402
from core.common import azi_ro  # noqa: E402

SCHEMA = "proba_ramuri_p2"
TEMPLATE = os.path.join(_RAD, "tenant_template.sql")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ============================================================================
#  SETUP-URILE — fiecare deschide o ramură, cumulativ
# ============================================================================
def _nimic(cur, schema):
    pass


def _gol(cur, schema, tabela):
    """Cheia primară e `IDENTITY GENERATED ALWAYS` peste tot: id-urile se PRIMESC, nu se aleg.
    Setup-urile trebuie să fie și idempotente — `_stoc` se rulează din nou în proba de mutație."""
    cur.execute('SELECT count(*) FROM "%s".%s' % (schema, tabela))
    return cur.fetchone()[0] == 0


def _salariat(cur, schema):
    """Un salariat ACTIV, **cu tichete de masă**. `termene` întreabă dacă firma are salariați (deci
    dacă datorează D112), iar `control_fiscal` intră pe verificările de salarii.

    **Ramura care citește `pontaj` cere DOUĂ condiții deodată, și niciuna nu e evidentă.**
    `pontaj` se citește într-un singur loc din tot lanțul — `pontaj.zile_fara_tichet`, chemată din
    `d112` și `stat_plata_api` **numai când `tichet_masa_valoare > 0`**. Iar cu un rând mai sus,
    `d112` RIDICĂ `PerioadaNeconfirmata` dacă luna nu e confirmată pe domeniul `pontaj`
    (HG 1045/2018 art.10(3): tichetele cer pontaj confirmat) — deci fără confirmare, calculul se
    oprește ÎNAINTE de citire.

    Fixtura a fost construită în trei pași, fiecare cerut de garda care a refuzat pasul anterior:
    salariat activ (`pontaj` neatins) → salariat cu tichete (`pontaj` tot neatins) → **plus luna
    confirmată**. *O fixtură care activează „salarii" în general nu activează ramura care citește
    pontajul, iar o gardă care s-ar fi mulțumit cu prima formă ar fi declarat o acoperire
    inexistentă.*"""
    if not _gol(cur, schema, "salariati"):
        return
    cur.execute('INSERT INTO "%s".salariati (nume, data_angajare, tichet_masa_valoare) '
                "VALUES ('PROBA SALARIAT', CURRENT_DATE - 365, 40) RETURNING id" % schema)
    sid = cur.fetchone()[0]
    cur.execute('INSERT INTO "%s".salariu_istoric (salariat_id, valabil_din, salariu_brut) '
                "VALUES (%%s, CURRENT_DATE - 365, 4050)" % schema, (sid,))
    cur.execute('INSERT INTO "%s".pontaj (salariat_id, zi, stare) '
                "VALUES (%%s, CURRENT_DATE - 1, 'lucrata')" % schema, (sid,))
    # luna curentă ȘI cea precedentă: `control_fiscal` se uită și în urmă
    for delta in (0, 1):
        cur.execute(
            'INSERT INTO "%s".perioada_confirmata (an, luna, domeniu) '
            "SELECT EXTRACT(YEAR FROM d)::int, EXTRACT(MONTH FROM d)::int, 'pontaj' "
            "  FROM (SELECT (date_trunc('month', CURRENT_DATE) - (%%s || ' month')::interval) AS d) t "
            "ON CONFLICT DO NOTHING" % schema, (delta,))


def _stoc(cur, schema):
    """Articol cu mișcare de stoc — ramura pe care 18 din cele 20 de firme reale n-o ating."""
    if not _gol(cur, schema, "miscari_stoc"):
        return
    cur.execute('INSERT INTO "%s".articole (denumire) VALUES (%%s) RETURNING id' % schema,
                ("PROBA ARTICOL",))
    aid = cur.fetchone()[0]
    cur.execute('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, valoare) '
                "VALUES (%%s, CURRENT_DATE - 10, 'intrare', 5, 500)" % schema, (aid,))


def _facturi(cur, schema):
    if not _gol(cur, schema, "facturi"):
        return
    cur.execute('INSERT INTO "%s".facturi (numar, data_emitere, directie, total, tva) '
                "VALUES ('PR-1', CURRENT_DATE - 5, 'emisa', 1190, 190)" % schema)


def _vector_pfa_profit(cur, schema):
    """Alt regim: PFA pe partidă simplă, neplătitor de TVA, fără operațiuni intracomunitare."""
    cur.execute('UPDATE "%s".firma_profil SET tip_firma=%%s, regim_fiscal=%%s, platitor_tva=%%s, '
                "  operatiuni_ic=%%s, tip_decont=NULL WHERE id=1" % schema,
                ("pfa", "profit", False, False))


def _vector_trimestrial_art317(cur, schema):
    cur.execute('UPDATE "%s".firma_profil SET tip_firma=%%s, regim_fiscal=%%s, platitor_tva=%%s, '
                "  operatiuni_ic=%%s, tip_decont=%%s, inreg_art317=%%s, tva_la_incasare=%%s "
                " WHERE id=1" % schema,
                ("srl", "profit", True, True, "T", True, True))


#: ORDINEA E PARTE DIN PROBĂ. Fiecare rând declară ce TREBUIE să se deschidă la pasul lui.
RAMURI = (
    {"nume": "baza_vector_complet", "setup": _nimic, "asteapta": ()},
    {"nume": "salarii", "setup": _salariat, "asteapta": ("pontaj", "salariu_istoric")},
    {"nume": "stoc", "setup": _stoc, "asteapta": ("miscari_stoc",)},
    {"nume": "facturi_emise", "setup": _facturi, "asteapta": ()},
    {"nume": "vector_pfa_profit_neplatitor", "setup": _vector_pfa_profit, "asteapta": ()},
    {"nume": "vector_trimestrial_art317_tva_incasare", "setup": _vector_trimestrial_art317,
     "asteapta": ()},
)

ASPECTE_MASURATE = ("termene", "control_fiscal")


def test_registrul_de_ramuri_e_acelasi_in_proba_si_in_document():
    """O SINGURĂ definiție a ramurilor. Setup-urile trăiesc aici (au nevoie de bază), dar CE
    trebuie să deschidă fiecare stă în `scan_dependente.RAMURI_ACOPERIRE`, de unde se generează și
    blocul din `DEPENDENTE_P2.md`. Dacă cele două liste divergeau, documentul ar fi descris o
    acoperire pe care proba n-o verifică."""
    aici = {p["nume"]: tuple(sorted(p["asteapta"])) for p in RAMURI}
    acolo = {x["nume"]: tuple(sorted(x["deschide"])) for x in SD.RAMURI_ACOPERIRE}
    assert aici == acolo, ("registrul ramurilor diferă între probă și instrument:\n  probă:      "
                           "%s\n  instrument: %s" % (aici, acolo))


# ============================================================================
#  FIRMA DE PROBĂ — schemă REALĂ, din chiar template-ul de provisionare
# ============================================================================
@pytest.fixture(scope="module")
def firma():
    if not _db_ok():
        pytest.skip("fara baza de date")
    if not os.path.exists(TEMPLATE):
        pytest.skip("tenant_template.sql lipsește")
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()

    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id FROM public.tenants WHERE schema_name=%s", (SCHEMA,))
                r = cur.fetchone()
                if r:
                    for t in ("firma_rezumat", "firma_sursa_versiune", "supervizor_sursa",
                              "firma_tip"):
                        cur.execute("DELETE FROM public.%s WHERE tenant_id=%%s" % t, (r[0],))
                    cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id=%s", (r[0],))
                    cur.execute("DELETE FROM public.tenants WHERE id=%s", (r[0],))
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA)
            c.commit()

    sterge()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            # cabinetul unei firme reale: `_ctx_admin` are nevoie de un administrator CU ACCES,
            # altfel două sub-verificări cad pe 404 și ramurile lor n-ar fi măsurate deloc
            cur.execute("SELECT accounting_firm_id FROM public.tenants "
                        " WHERE activ AND accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
            r = cur.fetchone()
            if not r:
                pytest.skip("niciun cabinet real")
            fid = r[0]
        TP.creeaza_schema(c, SCHEMA, tpl)
        with c.cursor() as cur:
            cur.execute("INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, "
                        "  activ) VALUES (%s,'PROBA RAMURI P2',NULL,%s,true) RETURNING id",
                        (SCHEMA, fid))
            tid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, serie_factura, '
                        '  urmator_numar_factura, tip_firma, regim_fiscal, platitor_tva, '
                        "  tip_decont, operatiuni_ic, inreg_art317) "
                        "VALUES (1,'PROBA RAMURI P2','12345678','PR',1,'srl','micro',true,'L',"
                        "        true,false) ON CONFLICT (id) DO NOTHING" % SCHEMA)
        FR.leaga_triggerele_firma(c, SCHEMA, tid)
        c.commit()
    yield tid, SCHEMA
    sterge()


def _masoara(tid, schema, aspect):
    """Sursele din schema firmei atinse de `aspect`, măsurate cu instrumentul de dependențe."""
    r = SD._masoara_aspect(aspect, tid, schema, azi_ro(), [schema, "public"], False)
    assert r["instructiuni"] > 0, "aspectul %s n-a executat nimic — măsurătoarea e goală" % aspect
    return ({t[1] for t in r["plan"] if t[0] == schema},
            {t[1] for t in r["plan"] if t[0] == "public"}, r)


@pytest.fixture(scope="module")
def acoperire(firma):
    """Aplică setup-urile CUMULATIV și măsoară după fiecare. `{ramura: {aspect: (ten, pub)}}`."""
    tid, schema = firma
    out = {}
    for pas in RAMURI:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                pas["setup"](cur, schema)
            c.commit()
        out[pas["nume"]] = {a: _masoara(tid, schema, a)[:2] for a in ASPECTE_MASURATE}
    return out


def _tot(acoperire, ramura=None):
    surse = set()
    for nume, pe_aspect in acoperire.items():
        if ramura and nume != ramura:
            continue
        for ten, _pub in pe_aspect.values():
            surse |= ten
    return surse


# ============================================================================
#  (1) FIECARE RAMURĂ CHIAR SE DESCHIDE
# ============================================================================
@pytest.mark.parametrize("pas", [p for p in RAMURI if p["asteapta"]],
                         ids=lambda p: p["nume"])
def test_ramura_deschide_sursele_ei(acoperire, pas):
    """Delta față de pasul anterior trebuie să conțină chiar sursele pe care ramura le declară.

    Dacă fixtura n-ar activa ramura, delta ar fi goală — iar o probă care „trece" pe o ramură
    neexercitată e chiar forma de acoperire falsă pe care garda asta o repară."""
    ordine = [p["nume"] for p in RAMURI]
    i = ordine.index(pas["nume"])
    inainte = set()
    for nume in ordine[:i]:
        inainte |= _tot(acoperire, nume)
    acum = _tot(acoperire, pas["nume"])
    noi = acum - inainte
    lipsa = [t for t in pas["asteapta"] if t not in acum]
    assert not lipsa, ("ramura %r n-a deschis %s — fixtura n-o exercită, deci nu dovedește nimic"
                       % (pas["nume"], lipsa))
    assert set(pas["asteapta"]) <= noi, (
        "ramura %r n-a adus nimic NOU din %s (delta: %s) — sursele erau deja deschise de un pas "
        "anterior, deci proba ei e goală" % (pas["nume"], pas["asteapta"], sorted(noi)))


def test_ramurile_acopera_tot_ce_declara_registrul(acoperire):
    """Reuniunea peste ramuri trebuie să atingă FIECARE sursă declarată.

    O sursă declarată și neatinsă de nicio ramură e ori moartă, ori are o ramură pe care n-am
    construit-o — și în al doilea caz nu știm dacă lista ei e completă."""
    atinse = _tot(acoperire)
    declarate = set(FR.tabele_urmarite())
    neatinse = sorted(declarate - atinse)
    assert not neatinse, (
        "surse declarate pe care nicio ramură nu le atinge: %s\n"
        "Ori sunt de scos din registru, ori lipsește fixtura care le exercită." % neatinse)


# ============================================================================
#  (2) NICIO SURSĂ OBSERVATĂ ȘI NEDECLARATĂ — direcția care apără
# ============================================================================
def test_nicio_sursa_observata_nu_lipseste_din_registru(acoperire):
    """`MASURAT - DECLARAT` trebuie să fie GOL, pe fiecare ramură și pe fiecare aspect.

    Un tabel citit și nedeclarat = o scriere care nu invalidează nimic = o valoare veche arătată
    drept curentă, tăcut. E chiar defectul pentru care s-a redeschis P2."""
    nedeclarate = {}
    for nume, pe_aspect in acoperire.items():
        for aspect, (ten, pub) in pe_aspect.items():
            decl = set(FR.ASPECTE[aspect]["tabele"])
            lipsa = ten - decl
            if lipsa:
                nedeclarate.setdefault(nume, {})[aspect] = sorted(lipsa)
    assert not nedeclarate, (
        "surse OBSERVATE și NEDECLARATE: %s\n"
        "Adaugă-le în `ASPECTE[<aspect>]['tabele']` și rerulează `scan_dependente --doc`."
        % nedeclarate)


def test_sursele_publice_observate_sunt_clasificate(acoperire):
    """La fel, pentru `public`: ori urmărită, ori declarată neurmărită, cu motiv."""
    urmarite = set(FR.tabele_publice_urmarite())
    neurmarite = set(FR.NEURMARITE_PUBLIC)
    neclasificate = {}
    for nume, pe_aspect in acoperire.items():
        for aspect, (_ten, pub) in pe_aspect.items():
            rest = pub - urmarite - neurmarite - set(SD.CONTABILITATE_PROPRIE)
            if rest:
                neclasificate.setdefault(nume, {})[aspect] = sorted(rest)
    assert not neclasificate, "surse din `public` neclasificate: %s" % neclasificate


# ============================================================================
#  (3) PROBELE NUMITE ÎN COMANDA DE REMEDIERE
# ============================================================================
#: Sursele cerute nominal de comanda de remediere (3A–3D). Se citesc DIN REGISTRU, nu se scriu
#: aici: o probă care poartă numele tabelei ca literal verifică memoria mea despre registru, nu
#: registrul. Dacă una dintre ele iese din registru, `parametrize` rămâne fără cazul ei — iar
#: `test_ramurile_acopera_tot_ce_declara_registrul` acoperă restul.
_CERUTE_TENANT = tuple(t for t in ("salariati", "articole", "miscari_stoc")
                       if t in FR.tabele_urmarite())
_CERUTE_PUBLIC = tuple(FR.tabele_publice_urmarite())


@pytest.mark.parametrize("tabela", _CERUTE_TENANT)
def test_3ABC_sursa_ceruta_de_audit_e_exercitata(acoperire, tabela):
    """3A · 3B · 3C — fiecare e atinsă de cel puțin o ramură construită deliberat.

    `miscari_stoc` e cazul care contează: 18 din cele 20 de firme reale n-o ating, deci fără
    fixtura de stoc nimic n-ar fi exercitat-o."""
    assert tabela in _tot(acoperire), (
        "sursa %r e declarată în registru, dar nicio ramură n-o exercită" % tabela)


@pytest.mark.parametrize("tabela", _CERUTE_PUBLIC)
def test_3D_sursa_publica_e_exercitata(acoperire, tabela):
    pub = set()
    for pe_aspect in acoperire.values():
        for _ten, p in pe_aspect.values():
            pub |= p
    assert tabela in pub


# ============================================================================
#  (4) MUTAȚIE — garda chiar prinde o omisiune
# ============================================================================
def test_3F_garda_pica_daca_o_sursa_iese_din_registru(firma, monkeypatch):
    """Se scoate `miscari_stoc` din registru, cu ramura de stoc ACTIVĂ. Verificarea „observat ⊆
    declarat" TREBUIE să pice.

    Fără proba asta, toate cele de mai sus ar putea fi tautologii: un `⊆` între două mulțimi
    calculate din aceeași sursă trece oricând."""
    tid, schema = firma
    with _db.get_conn() as c:                       # ramura de stoc, activată explicit
        with c.cursor() as cur:
            _stoc(cur, schema)
        c.commit()

    # sursa mutată se ia din registrul ramurilor, nu se scrie aici
    tinta = SD.RAMURI_ACOPERIRE[[x["nume"] for x in SD.RAMURI_ACOPERIRE].index("stoc")]["deschide"][0]
    ten, _pub, _r = _masoara(tid, schema, "control_fiscal")
    assert tinta in ten, "ramura de stoc nu e activă — mutația n-ar demonstra nimic"

    ciuntit = dict(FR.ASPECTE["control_fiscal"])
    ciuntit["tabele"] = tuple(t for t in ciuntit["tabele"] if t != tinta)
    monkeypatch.setitem(FR.ASPECTE, "control_fiscal", ciuntit)

    lipsa = ten - set(FR.ASPECTE["control_fiscal"]["tabele"])
    assert lipsa == {tinta}, (
        "cu %r scos din registru, verificarea NU l-a raportat ca nedeclarat — garda e "
        "tautologică și n-ar prinde o omisiune reală" % tinta)


def test_3E_o_ramura_noua_ar_aduce_sursa_ei(acoperire):
    """Proba că metoda e extensibilă: dacă un setup deschide o sursă, ea apare în delta lui.
    Se verifică pe ramura de salarii, unde delta a fost NEGOALĂ și numită."""
    salarii = _tot(acoperire, "salarii")
    baza = _tot(acoperire, "baza_vector_complet")
    assert salarii - baza, "niciun setup n-a schimbat nimic — metoda n-ar putea descoperi o ramură"
