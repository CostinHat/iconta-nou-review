# -*- coding: utf-8 -*-
"""GARD [R42, cele patru decizii ale lui Costin, 25.08.2026].

Criteriul dat pe 25.08 — *„tot ce iese din aplicație către o autoritate sau către un om, plus tot
ce închide sau redeschide o perioadă"* — a decis 28 de rute în trei aplicări. Patru întrebări nu
le decidea singur. Răspunsurile, și ce păzește fiecare aici:

  (a) **O notă contabilă NU e ceva emis.** Rămâne înăuntru, deci NU cere `admin_firma`. Dar nu e
      nici liberă: *„o notă care a intrat în evidență nu se șterge, se stornează."* Deci P15 —
      dacă perioada e închisă, nu se modifică. Gardul cere ca fiecare rută care CREEAZĂ o notă pe
      traseul T05 să verifice perioada; până azi era păzită doar editarea unei note existente.

  (b) **O completare manuală e parte din declarație DUPĂ generare, pregătire ÎNAINTE.** Deci
      ștergerea cere `admin_firma` dacă declarația e generată — condiție pe STAREA datelor, nu pe
      rută, deci verificare în corp.

  (c) **Trecerea de regim cere `admin_firma`**, pe un criteriu NOU: *ce schimbă ce datorează firma*.

  (d) **Pornirea și oprirea unui canal către client cer `admin_firma`.**

De ce gardul e pe STRUCTURĂ și nu pe listă de nume (METODA §23): o rută nouă de notă adăugată mâine
n-ar apărea într-o listă scrisă de mână. Aici se descoperă din AST toate rutele care scriu în
`inregistrari` și se cere fiecăreia verificarea.
"""
import ast
import io
import pathlib
import re

import pytest

RAD = pathlib.Path(__file__).resolve().parent.parent
MAIN = RAD / "main.py"
_SRC = io.open(MAIN, encoding="utf-8").read()
_TREE = ast.parse(_SRC)

_METODE = ("post", "put", "patch", "delete")


def _rute():
    """{nume_functie: (metoda, cale, nod)} pentru fiecare rută care schimbă ceva."""
    out = {}
    for n in _TREE.body:
        if not isinstance(n, ast.FunctionDef):
            continue
        for d in n.decorator_list:
            if isinstance(d, ast.Call) and getattr(d.func, "attr", "") in _METODE:
                cale = d.args[0].value if d.args and isinstance(d.args[0], ast.Constant) else ""
                out[n.name] = (d.func.attr, cale, n)
    return out


def _cheama(nod, nume):
    return any(isinstance(x, ast.Call) and getattr(x.func, "id", "") == nume for x in ast.walk(nod))


def _garzi(nod):
    """Numele dependenței din fiecare `Depends(...)` al rutei, cu argumentele când e `cere_rol`."""
    g = []
    for a in list(nod.args.args) + list(nod.args.kwonlyargs):
        pass
    for d in nod.args.defaults + [x for x in nod.args.kw_defaults if x is not None]:
        if isinstance(d, ast.Call) and getattr(d.func, "id", "") == "Depends" and d.args:
            arg = d.args[0]
            if isinstance(arg, ast.Name):
                g.append((arg.id, ()))
            elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                g.append((arg.func.id, tuple(c.value for c in arg.args if isinstance(c, ast.Constant))))
    return g


_RE_FROM = re.compile(r"\bfrom\s+(?:\{[^}]*\}\.|public\.)?([a-z_][a-z0-9_]*)")


def _tabele_citite(nod):
    """SETUL tabelelor din care CITEȘTE funcția, extras din `FROM ...`.

    Nu e o căutare de șir: se extrag numele și se compară mulțimi. Într-un f-string `{schema}` e un
    `FormattedValue`, nu text, deci prefixul se consumă cu un tipar care îl acceptă absent."""
    buc = []
    for x in ast.walk(nod):
        if isinstance(x, ast.Constant) and isinstance(x.value, str):
            buc.append(x.value)
        elif isinstance(x, ast.JoinedStr):
            buc.append("".join(v.value for v in x.values if isinstance(v, ast.Constant)))
    return set(_RE_FROM.findall(" ".join(" ".join(buc).split()).lower()))


_SCRIU_IN_INREGISTRARI = None


def _roluri(nod):
    """SETUL rolurilor cerute de rută prin `cere_rol(...)`.

    Un set, nu o listă în care se caută un șir: `"admin_firma" in args` ar trece și dacă `args` ar
    fi un șir care îl conține, și n-ar spune nimic despre un `args` gol (METODA §23)."""
    out = set()
    for g, args in _garzi(nod):
        if g == "cere_rol":
            out.update(args)
    return out


def _scrie_nota(nume_fn):
    """Ruta INSEREAZĂ ea însăși în `inregistrari`?

    Răspunsul NU se caută ca șir în SQL: `scripts/scan_trasee.py` calculează deja, pentru fiecare
    rută, `scrie_inline` — un dicționar `tabelă -> verbe`, extras cu regexul lui de SQL și **filtrat
    pe tabelele care există în baza de date**. Deci întrebarea e o căutare de CHEIE într-un dicționar.

    Câștigul care contează nu e că trece gardul de structură: e că inventarul de trasee și gardul
    ăsta folosesc **aceeași** definiție a lui «ruta scrie în `inregistrari`», nu două care pot
    diverge. Prima formă căuta `insert into {schema}.inregistrari` și vedea ZERO — într-un f-string
    `{schema}` nu e text."""
    global _SCRIU_IN_INREGISTRARI
    if _SCRIU_IN_INREGISTRARI is None:
        import importlib.util
        cale = RAD / "scripts" / "scan_trasee.py"
        spec = importlib.util.spec_from_file_location("scan_trasee_gard", str(cale))
        st = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(st)
        _SCRIU_IN_INREGISTRARI = {r["fn"] for r in st.citeste_rute()
                                  if {"inregistrari"} <= set(r["scrie_inline"])}
    return nume_fn in _SCRIU_IN_INREGISTRARI


# ── (a) nota contabilă ───────────────────────────────────────────────────────

_CAI_T05 = None


def _cai_traseu_nota():
    """Căile traseului T05, luate din INVENTAR. `scripts/scan_trasee.py` declară traseul, iar
    `core/test_trasee.py` îl gardează — deci există o singură definiție a lui «rută de notă».
    Prima formă potrivea prefixul `/nota-` pe cale: o a doua definiție, care putea diverge."""
    global _CAI_T05
    if _CAI_T05 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "scan_trasee_t05", str(RAD / "scripts" / "scan_trasee.py"))
        st = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(st)
        per, _o, _d, _n = st.acoperire(st.citeste_rute())
        _CAI_T05 = {r["cale"] for r in per["T05"]}
    return _CAI_T05


# Excepțiile, fiecare cu motivul scris — aceeași formă ca `_ROL_PE_ALT_CRITERIU` de mai jos, și din
# același motiv: o listă care poate crește tăcut e o gardă care se stinge singură, dar una în care
# fiecare intrare poartă propoziția care o justifică nu poate crește din neatenție.
#
# (Până la 30.08.2026 era un `set` cu o singură intrare, iar gardul cerea `len == 1`. A doua intrare
# a arătat că «exact una» era un proxy pentru «nicio creștere tăcută» — pe care forma cu motiv îl
# păzește mai bine, fiindcă spune și DE CE, nu doar CÂTE.)
_FARA_PERIOADA = {
    "/tenants/{tenant_id}/plan-conturi":
        "un cont din planul de conturi n-are dată, deci n-are perioadă. E în traseul T05 fiindcă "
        "nota se sprijină pe el, nu fiindcă ar fi o notă",
    "/tenants/{tenant_id}/registru-inventar":
        "[30.08.2026] rândul de registru-inventar n-are `data`: e adresat prin `exercitiu` + "
        "`momentul`. E în T05 fiindcă acolo stau cele trei registre obligatorii ale art. 20 din "
        "Legea 82/1991, nu fiindcă ar fi o notă contabilă. Iar normativ NU poate cere lună "
        "deschisă: OMFP 2634/2015 cere registrul *la sfârșitul exercițiului financiar*, întocmit "
        "pe baza listelor de inventariere — adică, în practică, după ce lunile exercițiului s-au "
        "închis. O gardă de lună deschisă l-ar face imposibil de completat exact la momentul în "
        "care norma îl cere",
}


def _rute_care_creeaza_note():
    """REUNIUNEA a două criterii, fiindcă niciunul singur nu acoperă clasa:

    - ce inserează DIRECT în `inregistrari` (prinde o rută de notă botezată oricum);
    - ce e rută de notă după cale (prinde cele care deleagă inserarea unui modul din `core` —
      leasing, credite, provizioane; SQL-ul nu e în rută, deci primul criteriu nu le vede).

    A doua jumătate nu e o listă scrisă de mână: e chiar definiția traseului T05 din
    `scripts/scan_trasee.py`, inventariată și gardată separat."""
    out = {}
    for nume, (m, c, n) in _rute().items():
        if m != "post":
            continue
        if _scrie_nota(nume) or c in _cai_traseu_nota():
            out[nume] = (m, c, n)
    return out


def test_ANTI_VACUU_se_gasesc_rutele_care_creeaza_note():
    """Dacă detectorul se strică și nu mai vede nicio rută, testul de mai jos ar trece vid — «zero
    rute nepăzite» ar fi adevărat despre o lume pe care gardul n-o vede (gard-care-nu-se-verifică)."""
    r = _rute_care_creeaza_note()
    assert len(r) >= 20, "detectorul vede doar %d rute care creează note — s-a stricat?" % len(r)


def test_o_nota_noua_nu_se_scrie_intr_o_luna_inchisa():
    """(a) Fiecare rută care creează o notă verifică perioada. P15: după închidere nu se modifică.

    Ce lipsea până azi: `_cere_perioada_deschisa` păzea editarea, ștergerea și validarea unei note
    care EXISTĂ. Crearea intra pe altă ușă. O notă nouă datată într-o lună închisă e tot o
    modificare a perioadei închise."""
    nepazite = sorted(c for nume, (_m, c, n) in _rute_care_creeaza_note().items()
                      if c not in _FARA_PERIOADA
                      and not (_cheama(n, "_cere_luna_deschisa") or _cheama(n, "_cere_perioada_deschisa")))
    assert not nepazite, (
        "rute care creează o notă fără să verifice dacă luna e închisă (%d):\n  %s"
        % (len(nepazite), "\n  ".join(nepazite)))


def test_fiecare_exceptie_de_la_perioada_ARE_motiv_si_exista():
    """O listă de excepții care poate crește e o gardă care se stinge singură — dar plafonul pe
    NUMĂR nu era protecția reală: era un proxy. Protecția e ca fiecare intrare să poarte propoziția
    care o justifică, iar propoziția să nu poată fi un cuvânt.

    (Redenumit 30.08.2026, când a apărut a doua excepție. `len == 1` ar fi cerut fie o minciună —
    să nu declar excepția — fie o gardă ștearsă. A treia cale: aceeași formă cu motiv scris pe care
    fișierul ăsta o folosea deja pentru `_ROL_PE_ALT_CRITERIU`.)"""
    cai = {c for _n, (_m, c, _x) in _rute().items()}
    for c, motiv in _FARA_PERIOADA.items():
        assert c in cai, "excepția %s nu mai există ca rută — scoate-o" % c
        assert len(motiv) > 60, (
            "excepția %s are un motiv prea scurt ca să fie o justificare: %r" % (c, motiv))


# Rutele din traseul notei care au totuși `admin_firma` — și NU pe criteriul lui R42, ci pe altul,
# scris. O listă de excepții care poate crește e o gardă care se stinge singură (vezi
# `_FARA_PERIOADA` mai sus), deci fiecare intrare poartă decizia care o justifică.
_ROL_PE_ALT_CRITERIU = {
    "/tenants/{tenant_id}/jurnal/{nota_id}/valideaza":
        "R55, decizia lui Costin 26.08.2026: «validarea unei note e ce transformă o ciornă în "
        "evidență». Criteriul e «ce schimbă ce datorează firma», nu «e artefact predat» — deci nu "
        "contrazice R42, care spune doar că nota nu primește rol pentru că ar fi PREDATĂ. "
        "Crearea, editarea și ștergerea rămân fără rol: citite la sursă, ating doar ciorne",
    "/tenants/{tenant_id}/plan-conturi":
        "R55, aceeași decizie: «cine adaugă un cont poate anula orice refuz» — ruta extinde "
        "nomenclatorul pe care stă refuzul din R54, deci schimbă ce poate înregistra firma. "
        "Nu e nota însăși; e nomenclatorul din care se scrie nota",
    "/tenants/{tenant_id}/jurnal/{nota_id}/dezleaga":
        "R90, 29.08.2026: dezlegarea unei note de plată de factura ei face factura să REAPARĂ ca "
        "neîncasată — `reconciliere_api.facturi_deschise` calculează soldul chiar din notele legate "
        "prin `factura_id`. Deci actul schimbă ce are firma de încasat sau de plătit, adică e pe "
        "axa R55, nu pe cea a lui R42: nota tot nu e artefact predat. Iar actul deschide drumul "
        "către ștergerea facturii, care e `admin_firma` prin R42",
}


def test_nota_contabila_NU_cere_admin_firma():
    """Cealaltă direcție a deciziei, la fel de importantă: nota NU e artefact predat, deci NU se
    strecoară pe `admin_firma` PE CRITERIUL ĂSTA. Fără proba asta, „am păzit nota" ar putea
    însemna și că am restricționat-o — adică exact ce Costin a spus să nu fac.

    [26.08.2026] Garda a prins o contradicție reală între două decizii ale lui, și a avut
    dreptate s-o prindă. Rezolvarea nu e s-o relax: R42 și R55 vorbesc despre **axe diferite** —
    una despre *ce se predă*, alta despre *ce schimbă starea*. Garda încoda doar prima, deci
    acum o spune, iar excepțiile pe cealaltă axă sunt numite una câte una, cu decizia lor."""
    rele = []
    for nume, (_m, cale, n) in _rute().items():
        if cale not in _cai_traseu_nota() or cale in _ROL_PE_ALT_CRITERIU:
            continue
        if _roluri(n) & {"admin_firma"}:
            rele.append(cale)
    assert not rele, ("rute de notă trecute pe admin_firma, deși decizia spune că nota rămâne "
                      "înăuntru și nu e artefact predat: %s — dacă rolul stă pe ALT criteriu "
                      "scris, intră în _ROL_PE_ALT_CRITERIU cu decizia care îl justifică" % rele)


def test_exceptiile_de_pe_alta_axa_sunt_reale_si_motivate():
    """Clichet bidirecțional pe lista de excepții: o intrare care nu mai are rolul, sau care nu mai
    e rută, e o amintire — se scoate. Iar una fără motiv scris ar face lista o listă de tolerat."""
    rute = _rute()
    cai = {c: n for _nume, (_m, c, n) in rute.items()}
    for cale, motiv in _ROL_PE_ALT_CRITERIU.items():
        assert len(motiv) > 80, "%s e în listă fără decizia care o justifică" % cale
        assert cale in cai, "%s nu mai e rută — scoate-o din listă" % cale
        assert _roluri(cai[cale]) & {"admin_firma"}, (
            "%s nu mai cere admin_firma — dacă rolul s-a scos, se scoate și excepția" % cale)


# ── (b) completarea manuală ──────────────────────────────────────────────────

_MANUAL_STERGE = ("d390_manual_sterge", "d300_manual_sterge")


@pytest.mark.parametrize("nume", _MANUAL_STERGE)
def test_stergerea_unei_completari_manuale_cere_admin_daca_declaratia_e_generata(nume):
    """(b) Condiția e pe STAREA datelor, nu pe rută, deci verificarea e în corp — o dependență
    statică ar cere admin_firma și înainte de generare, unde decizia spune explicit că nu."""
    r = _rute()
    assert nume in r, "ruta %s nu mai există" % nume
    _m, _c, n = r[nume]
    assert _cheama(n, "_declaratie_generata"), "%s nu întreabă dacă declarația e generată" % nume
    assert _cheama(n, "_cere_admin_firma"), "%s nu cere admin_firma pe ramura aia" % nume


@pytest.mark.parametrize("nume", _MANUAL_STERGE)
def test_completarea_manuala_ramane_libera_INAINTE_de_generare(nume):
    """Calibrarea în cealaltă direcție: ruta NU are `cere_rol("admin_firma")` ca dependență. Dacă
    ar avea, ar cere administratorul și pentru pregătire — jumătatea deciziei care spune «nu»."""
    _m, _c, n = _rute()[nume]
    assert not _roluri(n) & {"admin_firma"}, (
        "%s cere admin_firma pe TOATE cazurile, deși decizia îl cere doar după generare" % nume)


def test_declaratie_generata_se_uita_SI_in_coada_SI_in_depuse():
    """O declarație generată dar nedepusă e tot generată. Dacă ajutorul s-ar uita doar în
    `declaratii_depuse`, ștergerea ar fi liberă exact în fereastra în care contează cel mai mult:
    între generare și depunere."""
    fn = next((n for n in _TREE.body
               if isinstance(n, ast.FunctionDef) and n.name == "_declaratie_generata"), None)
    assert fn is not None
    citite = _tabele_citite(fn)
    assert {"declaratii_coada", "declaratii_depuse"} <= citite, (
        "se uită doar în %s — o declarație generată și nedepusă trăiește în coadă, iar fereastra "
        "dintre generare și depunere e exact cea în care ștergerea contează"
        % (sorted(citite) or "nicio tabelă"))


# ── (c) și (d) ───────────────────────────────────────────────────────────────

_CER_ADMIN = {
    "firma_profil_regim_tva": "(c) trecerea de regim: schimbă CE DATOREAZĂ firma",
    "wc_config": "(d) cheile canalului: cu ele pline canalul e pornit, golite îl oprește",
}


@pytest.mark.parametrize("nume,de_ce", sorted(_CER_ADMIN.items()))
def test_rutele_decise_cer_admin_firma(nume, de_ce):
    r = _rute()
    assert nume in r, "ruta %s nu mai există (a fost redenumită? actualizează registrul)" % nume
    _m, cale, n = r[nume]
    assert _roluri(n) & {"admin_firma"}, "%s (%s) nu cere admin_firma — %s" % (cale, nume, de_ce)


def test_CALIBRARE_detectorul_de_garda_vede_si_nevede():
    """Modul de eșec propriu al gardului (interdicția 76): `_garzi` citește dependențele din
    valorile implicite ale argumentelor. Dacă s-ar strica, testele de mai sus ar trece raportând
    «are admin_firma» despre rute care n-au — sau invers. Se probează pe două rute cunoscute."""
    r = _rute()
    _m, _c, n = r["firma_profil_model"]        # cunoscut FĂRĂ rol: font/culoare/logo
    assert not [1 for g, a in _garzi(n) if g == "cere_rol"], (
        "detectorul raportează un rol pe o rută care n-are")
    _m, _c, n = r["vector_salveaza"]           # cunoscut CU admin_firma, dinainte de tura asta
    assert _roluri(n) & {"admin_firma"}, "detectorul nu vede un rol care există"


def test_ce_a_RAMAS_fara_rol_pe_traseele_atinse_e_o_cifra_nu_o_impresie():
    """Ce NU s-a schimbat, numărat. Cele 7 operațiuni din T29 (vânzare în marjă, achiziție de la
    agricultor ș.a.) rămân la `cere_cabinet`: sunt INTRODUCERE, iar criteriul lui Costin spune
    explicit că introducerea o poate face un asistent. `firma-profil/model` (font, culoare, logo) și
    `firma-profil/date` (nume, CUI, CAEN, adresă) rămân tot acolo — datele identifică firma, nu
    schimbă ce datorează. Cifra stă aici ca să nu devină impresie."""
    cai = {c for _n, (_m, c, _x) in _rute().items()}
    for c in ("/tenants/{tenant_id}/vanzare-marja",
              "/tenants/{tenant_id}/firma-profil/model",
              "/tenants/{tenant_id}/firma-profil/date"):
        assert c in cai, "ruta %s a dispărut — recitește decizia înainte s-o repari" % c
    # Cele șapte, scrise: un filtru pe cuvinte-cheie prindea șase — `vanzare-aur-investitii` n-are
    # niciun cuvânt din listă. O potrivire fragilă care raportează o cifră mai mică e mai rea decât
    # o listă explicită: ar fi arătat progres acolo unde nu era nicio schimbare.
    SAPTE = ["vanzare-marja", "vanzare-marja-turism", "vanzare-aur-investitii",
             "achizitie-agricultor", "vanzare-agricultor",
             "import-extracomunitar", "export-extracomunitar"]
    r = _rute()
    cu_rol = []
    for s7 in SAPTE:
        cale = "/tenants/{tenant_id}/" + s7
        nod = next((n for _x, (m, c, n) in r.items() if c == cale), None)
        assert nod is not None, "ruta %s a dispărut" % cale
        if [1 for g, a in _garzi(nod) if g == "cere_rol"]:
            cu_rol.append(cale)
    assert not cu_rol, (
        "operațiuni de regim special trecute pe rol, deși criteriul spune că INTRODUCEREA o poate "
        "face un asistent: %s — dacă e intenționat, scoate-le din listă cu motivul scris" % cu_rol)


# ── PROBA FUNCȚIONALĂ: verificarea chiar refuză ─────────────────────────────
#
# Testele de mai sus asertează pe STRUCTURĂ — că rutele CHEAMĂ verificarea. Asta nu spune că
# verificarea funcționează. Un `_cere_luna_deschisa` care nu ridică niciodată ar trece toate
# gărzile de sus și n-ar păzi nimic (METODA §24: proba care confirmă ipoteza fiindcă jumătate
# din reparație nu rulează).

import importlib  # noqa: E402

from core import db as _db  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402

SCHEMA_PROBA = "ztest_r42_perioada"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_PROBA)
                cur.execute(_tp.parametrizeaza_template(
                    io.open(RAD / "tenant_template.sql", encoding="utf-8").read(), SCHEMA_PROBA))
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_VACUU_schema_de_proba_are_perioade_blocate(conn):
    """Fără tabelă, toate probele de mai jos ar trece pe gol."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ("%s.perioade_blocate" % SCHEMA_PROBA,))
        assert cur.fetchone()[0], "lipsește perioade_blocate din schema de test"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_verificarea_REFUZA_o_data_din_luna_inchisa(conn):
    m = importlib.import_module("main")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO %s.perioade_blocate (an, luna) VALUES (2026, 3)" % SCHEMA_PROBA)
    with pytest.raises(Exception) as e:
        m._cere_luna_deschisa(conn, SCHEMA_PROBA, "2026-03-15")
    assert getattr(e.value, "status_code", None) == 423, (
        "refuzul trebuie să fie 423 (perioada închisă), nu %r" % e.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_verificarea_LASA_o_data_din_luna_deschisa(conn):
    """Cealaltă direcție (METODA §22). Fără ea, un `_cere_luna_deschisa` care refuză MEREU ar
    trece testul de sus — și ar bloca toată contabilitatea."""
    m = importlib.import_module("main")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO %s.perioade_blocate (an, luna) VALUES (2026, 3)" % SCHEMA_PROBA)
    m._cere_luna_deschisa(conn, SCHEMA_PROBA, "2026-04-01")   # luna următoare: deschisă
    m._cere_luna_deschisa(conn, SCHEMA_PROBA, "2026-02-28")   # luna dinainte: deschisă


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_data_poarta_REFUZA_nu_lasa_sa_treaca(conn):
    """[R146, 05.09.2026] Linia care lipsește de mai sus era `_cere_luna_deschisa(conn, SCHEMA, None)`,
    cu motivul scris în comentariu: *„fără dată: nu se afirmă nimic"*. Exact asta s-a răsturnat prin
    decizie (`DECIZII.md` 33): data operațiunii decide ce cote și ce plafoane sunt legale, deci o
    operațiune fără dată **nu e una despre care nu se afirmă nimic — e una care nu se poate verifica
    deloc**.

    Măsurat înainte de schimbare: 19 rute treceau de poartă și cădeau apoi cu `KeyError: 'data'` la
    `INSERT`, adică `500`. Poarta vedea absența și o lăsa să treacă spre o cădere."""
    m = importlib.import_module("main")
    with pytest.raises(Exception) as e:
        m._cere_luna_deschisa(conn, SCHEMA_PROBA, None)
    assert getattr(e.value, "status_code", None) == 422, (
        "o dată lipsă trebuie refuzată cu 422, nu lăsată să treacă: %r" % e.value)
    assert "dat" in str(getattr(e.value, "detail", "")).lower()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_marginile_lunii_inchise_sunt_INCLUSE(conn):
    """Prima și ultima zi a lunii închise sunt tot în ea. O comparație scrisă pe `>` în loc de
    `>=` ar lăsa exact zilele de la margine să treacă — clasa de defect cea mai greu de văzut."""
    m = importlib.import_module("main")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO %s.perioade_blocate (an, luna) VALUES (2026, 3)" % SCHEMA_PROBA)
    for zi in ("2026-03-01", "2026-03-31"):
        with pytest.raises(Exception) as e:
            m._cere_luna_deschisa(conn, SCHEMA_PROBA, zi)
        assert getattr(e.value, "status_code", None) == 423, "ziua %s a scăpat" % zi
