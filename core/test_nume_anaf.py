# -*- coding: utf-8 -*-
"""GARD [27.08.2026]: denumirea de la ANAF se păstrează lângă cea editabilă, cu data ei.

DE UNDE VINE. Întrebarea lui Costin — *„de ce se poate schimba denumirea unei firme cu CUI validat
la ANAF?"* — a scos că premisa nu ținea: `precompleteaza_din_anaf` scria în `firma_profil`, iar
`seteaza_nume=True` apărea **într-un singur loc** (firma proprie a cabinetului). Deci
`public.tenants.nume` — numele din portofoliu, cel care s-a duplicat — **nu era scris de ANAF pe
nicio cale**. Câmpul era editabil fiindcă **n-a fost niciodată sursat**.

DECIZIA lui, varianta (b): numele rămâne editabil, dar instantaneul ANAF se păstrează cu data lui,
iar divergența se arată. *„E precedent, nu invenție"* — `platitor_tva` lângă `platitor_tva_anaf` +
`platitor_tva_anaf_data`, deja în aplicație. Iar (a), câmp needitabil, ar fi blocat firmele pe care
ANAF nu le întoarce: *„un câmp needitabil care nu se poate completa e mai rău decât unul editabil
greșit."*

CE FACE IMPOSIBIL: dispariția captării (`nume_anaf` scris pe TOATE căile, nu doar unde numele vine
de la ANAF) · dispariția coloanelor · o listă de firme care nu mai poartă cele două câmpuri, adică
un ecran care n-ar avea din ce arăta divergența.

CE NU FACE, declarat:
  - **nu cere alegerea.** Slotul T36 cere ca la divergență *„se arată amândouă și se cere
    alegerea"*. Azi se arată amândouă și se oferă **o** acțiune (ia denumirea de la ANAF); a
    păstra pe a ta = a nu face nimic, iar divergența rămâne vizibilă. Jumătatea „se cere" nu e
    construită, și se scrie ca lipsă, nu se trece drept făcută.
  - **nu reîmprospătează** instantaneul: `nume_anaf_la` îmbătrânește până la următoarea verificare
    de CUI. Peste 180 de zile ecranul nu mai spune „divergență", spune „citire veche" — regula lui
    Costin: *„o denumire ANAF veche de un an nu e divergență, e o măsurătoare veche."*
  - **nu se aplică retroactiv**: firmele existente n-au `nume_anaf` până la o nouă precompletare.
"""
import ast
import io
import os
import re

from core import db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_coloanele_exista_in_baza():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema='public' AND table_name='tenants'
                         AND column_name IN ('nume_anaf','nume_anaf_la')""")
        gasite = {r[0] for r in cur.fetchall()}
    assert gasite == {"nume_anaf", "nume_anaf_la"}, (
        "lipsesc coloanele instantaneului ANAF: %s — rulează DDL-ul din infra/bootstrap_public.sql"
        % sorted({"nume_anaf", "nume_anaf_la"} - gasite))


def test_captarea_e_pe_TOATE_caile_nu_doar_unde_numele_vine_de_la_ANAF():
    """`seteaza_nume` decide ce se AFIȘEAZĂ; instantaneul se păstrează oricum. Structural: `UPDATE
    public.tenants SET nume_anaf` trebuie să fie în afara ramurii `if seteaza_nume`."""
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "precompleteaza_din_anaf")
    sql = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            a = n.args[0]
            while isinstance(a, ast.BinOp):
                a = a.left
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                sql.append(" ".join(a.value.split()))
    captare = [s for s in sql if s.startswith("UPDATE public.tenants SET nume_anaf")]
    assert len(captare) == 1, (
        "instantaneul ANAF nu se mai captează în `precompleteaza_din_anaf`: %s" % sql)
    # și NU sub `if seteaza_nume`
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and ast.unparse(n.test).strip() == "seteaza_nume":
            corp = " ".join(ast.unparse(s) for s in n.body)
            assert corp.count("nume_anaf") == 0, (
                "captarea a ajuns sub `if seteaza_nume` — atunci la add-firm și la import nu s-ar "
                "mai păstra nimic, adică exact starea de dinainte")


def test_lista_de_firme_poarta_cele_doua_campuri():
    """Fără ele în răspuns, ecranul n-ar avea din ce arăta divergența."""
    sursa = io.open(os.path.join(_RAD, "core", "auth_api.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "tenantii_userului")
    interogari = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            a = n.args[0]
            while isinstance(a, ast.BinOp):
                a = a.left
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                interogari.append(" ".join(a.value.split()))
    # numai SELECT-urile care aduc firme; `SAVEPOINT`-urile din bucla de `tip_firma` nu sunt
    # interogari de lista si n-au ce cauta in clasa (prins de propria rulare)
    lista = [q for q in interogari
             if q.upper().startswith("SELECT") and q.count("public.tenants") > 0]
    assert lista, "n-am găsit nicio interogare de listă în `tenantii_userului`: %s" % interogari
    fara = [q[:60] for q in lista if "nume_anaf" not in q]
    assert not fara, (
        "ramuri de rol care nu mai întorc instantaneul ANAF: %s — divergența ar dispărea tăcut "
        "pentru rolurile alea" % fara)


def test_REDENUMIREA_libera_e_si_ea_o_alegere_consemnata():
    """[R77, partea a doua] Costin, 27.08 seara: *„editarea liberă, fără să treacă prin întrebare,
    nu mai are rost… `PUT /tenants/{id}` cu denumire diferită de `nume_anaf` trece prin aceeași
    alegere — nu se refuză, dar se consemnează ca alegere deliberată, cu autor."*

    Deci cele două căi de a alege — **butonul** și **tastatura** — trebuie să scrie prin
    **aceeași** funcție. Dacă `actualizeaza_tenant` și-ar face propria consemnare, ar fi două
    reguli care se pot despărți în tăcere; instanța din care s-a învățat asta e R62 (*„regula era
    în două locuri și diferită"*).
    """
    from core import tenant_provisioning as tp
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    arb = ast.parse(sursa)
    fn = {n.name: n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)}
    assert set(fn) >= {"_consemneaza_alegerea", "alege_denumirea", "actualizeaza_tenant"}, (
        "consemnarea n-are un loc propriu, sau una din cele două căi a dispărut")

    def cheama(nume_fn, tinta):
        return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                   and c.func.id == tinta for c in ast.walk(fn[nume_fn]))

    for cale in ("alege_denumirea", "actualizeaza_tenant"):
        assert cheama(cale, "_consemneaza_alegerea"), (
            "`%s` nu trece prin consemnarea comună — a doua cale de a alege ar deveni tăcută, "
            "sau ar scrie după alte reguli" % cale)

    # Consemnarea din redenumire NU are voie să fie necondiționată: o firmă fără `nume_anaf`
    # n-are cu ce să difere, iar o alegere între o denumire și nimic n-ar fi o alegere.
    # Condiția se citește ca NOD (un nume `nume_anaf` în testul lui `if`), nu ca text al lui:
    # `ast.unparse` ar trece la fel de bine peste un comentariu sau peste un șir.
    def numeste(nod, tinta):
        return any((isinstance(x, ast.Name) and x.id == tinta)
                   or (isinstance(x, ast.Attribute) and x.attr == tinta)
                   for x in ast.walk(nod))

    sub_if = False
    for n in ast.walk(fn["actualizeaza_tenant"]):
        if isinstance(n, ast.If) and numeste(n.test, "nume_anaf"):
            if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                   and c.func.id == "_consemneaza_alegerea" for c in ast.walk(n)):
                sub_if = True
    assert sub_if, (
        "redenumirea consemnează o alegere necondiționat — deci și pe firmele fără `nume_anaf`, "
        "unde nu există a doua denumire cu care să difere")

    # Autorul nu e opțional în fapt: ruta trebuie să-l dea. Citit ca ARGUMENT CU NUME în apel,
    # nu căutat ca șir în `main.py` — un `user_id=ctx["uid"]` scris într-un comentariu ar fi
    # trecut, iar unul reformatat pe două rânduri ar fi picat. Amândouă greșite.
    ruta = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    apeluri = [c for c in ast.walk(ruta)
               if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
               and c.func.attr == "actualizeaza_tenant"]
    assert len(apeluri) == 1, "%d apeluri către `actualizeaza_tenant` în main.py" % len(apeluri)
    kw = {k.arg: k.value for k in apeluri[0].keywords}
    assert set(kw) >= {"user_id"}, (
        "ruta de redenumire nu duce autorul mai departe — o alegere fără autor nu e o alegere")
    v = kw["user_id"]
    assert isinstance(v, ast.Subscript) and isinstance(v.value, ast.Name) and v.value.id == "ctx", (
        "autorul nu vine din contextul cererii, ci de altundeva: %s" % ast.unparse(v))
    assert set(tp.ALEGERI_NUME) == {"aplicatie", "anaf"}


def test_alegerea_are_AMANDOUA_ramurile_si_amandoua_SCRIU():
    """[R77] Costin: *„«a păstra pe a ta = a nu face nimic» nu e o alegere."* Deci și ramura
    „păstrez denumirea mea" trebuie să scrie ceva — altfel tăcerea arată identic cu o decizie."""
    from core import tenant_provisioning as tp
    assert set(tp.ALEGERI_NUME) == {"aplicatie", "anaf"}
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    toate = {n.name: n for n in ast.walk(ast.parse(sursa)) if isinstance(n, ast.FunctionDef)}

    def _sql(fn):
        out = []
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "execute" and n.args):
                a = n.args[0]
                while isinstance(a, ast.BinOp):
                    a = a.left
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    out.append(" ".join(a.value.split()))
        return out

    # [27.08 seara] Consemnarea s-a mutat din `alege_denumirea` în `_consemneaza_alegerea`, ca să
    # fie UNA pentru amândouă căile de a alege (butonul și tastatura). Gardul își urmează
    # intenția, nu locul: cere să existe **exact un** loc care scrie `nume_ales`, oriunde ar fi.
    scriu = {nume: [s for s in _sql(f) if s.startswith("UPDATE public.tenants SET nume_ales=")]
             for nume, f in toate.items()}
    locuri = [nume for nume, s in scriu.items() if s]
    assert locuri == ["_consemneaza_alegerea"] and len(scriu["_consemneaza_alegerea"]) == 1, (
        "alegerea nu se consemnează într-un singur loc, pentru toate căile: %s" % locuri)

    fn = toate["alege_denumirea"]
    assert any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
               and c.func.id == "_consemneaza_alegerea" for c in ast.walk(fn)), (
        "`alege_denumirea` nu mai consemnează nimic")
    # consemnarea NU are voie să stea sub ramura „anaf"
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and ast.unparse(n.test).count("anaf"):
            corp = " ".join(ast.unparse(s) for s in n.body)
            assert corp.count("_consemneaza_alegerea") == 0, (
                "consemnarea a ajuns sub ramura ANAF — atunci «păstrez denumirea mea» n-ar mai "
                "scrie nimic, iar tăcerea ar redeveni o decizie")


def test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea():
    """**GARDĂ PE CALE MOARTĂ.** Ramura pe care o păzește e corectă și **nedeclanșabilă azi.**

    Alegerea de azi nu acoperă o denumire schimbată la registru mâine. Regula trăiește în ecran: se
    compară `nume_anaf_la` cu `nume_ales_la`, iar dacă citirea e mai nouă decât alegerea, caseta
    reapare.

    **[G2, 28.08.2026] De ce se marchează.** `nume_anaf` și `nume_anaf_la` se scriu într-un singur
    loc — `precompleteaza_din_anaf` —, chemat din **trei** rute, **toate pe o firmă abia
    provizionată**; importul în masă respinge un CUI existent înainte să ajungă acolo. **Nicio rută
    nu re-citește ANAF pentru o firmă existentă.** Deci condiția `nume_anaf_la > nume_ales_la` n-are
    cum să devină adevărată, iar testul ăsta e **verde pe vecie fără să demonstreze nimic** —
    aceeași familie cu semaforul permanent verde. Costin, 28.08: *nu îl șterge; marchează-l acolo
    unde se citește, cu condiția care l-ar învia.*

    **CONDIȚIA CARE ÎL ÎNVIE**, și e una singură: o cale prin care ANAF se re-citește pentru o firmă
    **care există deja** — o reîmprospătare periodică, un buton „verifică la ANAF", o revalidare de
    CUI la redenumire. În ziua în care apare, marcajul ăsta se **scoate**, iar testul redevine o
    gardă vie. Până atunci, ce îl ține onest e `test_calea_care_ar_REDESCHIDE_intrebarea_e_INCA_moarta`,
    care numără chiar căile: dacă apare a patra, poarta cade și cere scoaterea marcajului.
    """
    js = io.open(os.path.join(_RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    assert js.count("nume_ales_la") >= 2, (
        "ecranul nu mai știe dacă întrebarea a primit răspuns — ori nu se mai pune niciodată, "
        "ori se pune la infinit")
    assert js.count("dn-pastrez") >= 2, (
        "butonul «Păstrez denumirea mea» a dispărut — rămâne o singură ramură, adică nicio alegere")


def test_ecranul_stie_cand_o_citire_e_VECHE_nu_divergenta():
    """Regula lui Costin, în ecran: peste prag, nu mai e divergență, e o măsurătoare veche."""
    js = io.open(os.path.join(_RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    assert js.count("_NUME_ANAF_ZILE_STATUT") >= 2, (
        "pragul de vechime a dispărut din ecran — o denumire ANAF de acum un an ar fi arătată ca "
        "divergență")
    assert js.count('fel: "veche"') >= 0 and js.count('"veche"') >= 2, (
        "ramura «citire veche» nu mai există în ecran")


# ── [G2, 28.08.2026] Cât timp calea rămâne moartă ────────────────────────────
# Cele trei căi de captare a instantaneului ANAF, toate pe o firmă **abia provizionată**:
#   `main.py` — `POST /auth/register`, `POST /tenants` (adăugare firmă), `POST /migrare/importa`.
# Numărul e clichet în AMÂNDOUĂ direcțiile, și nu fiindcă trei ar fi o cifră bună: cât timp e
# **exact** mulțimea de la creare, marcajul „gardă pe cale moartă" de mai sus e adevărat. A patra
# cale e chiar evenimentul care îl face fals.
_CAPTARI_ANAF = 3


def _apeluri_catre(nume_functie):
    """Apelurile către `nume_functie` din codul de producție, ca (fișier, linie). Se citește
    APELUL din AST, nu numele scris în text: o pomenire într-un comentariu n-are voie să conteze,
    iar un apel scris pe două rânduri n-are voie să scape."""
    gasite = []
    for rel in ["main.py"] + ["core/" + f for f in sorted(os.listdir(os.path.join(_RAD, "core")))
                              if f.endswith(".py") and not f.startswith("test_")]:
        sursa = io.open(os.path.join(_RAD, rel), encoding="utf-8").read()
        try:
            arb = ast.parse(sursa)
        except SyntaxError:      # pragma: no cover
            continue
        for c in ast.walk(arb):
            if not isinstance(c, ast.Call):
                continue
            n = c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)
            if n == nume_functie:
                gasite.append((rel, c.lineno))
    return sorted(gasite)


def test_calea_care_ar_REDESCHIDE_intrebarea_e_INCA_moarta():
    """[G2] Marcajul de mai sus e o afirmație despre cod, deci poate deveni fals mâine. Asta îl ține."""
    ap = _apeluri_catre("precompleteaza_din_anaf")
    assert len(ap) <= _CAPTARI_ANAF, (
        "au apărut căi noi care citesc ANAF: %s. Dacă vreuna se aplică unei firme care EXISTĂ deja, "
        "`nume_anaf_la` poate depăși `nume_ales_la` — adică ramura de redeschidere devine "
        "declanșabilă, iar marcajul «gardă pe cale moartă» din "
        "`test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea` devine FALS și se scoate." % ap)
    assert len(ap) >= _CAPTARI_ANAF, (
        "captarea ANAF se face acum din %d locuri, nu din %d (%s) — dacă o cale s-a scos "
        "deliberat, coboară `_CAPTARI_ANAF`; altfel instantaneul nu se mai păstrează pe undeva"
        % (len(ap), _CAPTARI_ANAF, ap))


# ── [F4, 28.08.2026] Ce ține textul reparat de pe ecran ──────────────────────
def _tabelele_din(arb, nume_functie):
    """Tabelele în care scrie funcția, citite din SQL-ul dat lui `execute` — un NOD, nu un șir
    căutat în fișier. Pe un SQL compus (`'… "%s".t …' % schema`) se coboară pe stânga, unde stă
    litera; de-aia se vede și o scriere într-o schemă de tenant, unde schema e interpolată."""
    fn = next((n for n in ast.walk(arb)
               if isinstance(n, ast.FunctionDef) and n.name == nume_functie), None)
    assert fn is not None, "funcția `%s` nu mai există" % nume_functie
    out = set()
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            a = n.args[0]
            while isinstance(a, ast.BinOp):
                a = a.left
            if not (isinstance(a, ast.Constant) and isinstance(a.value, str)):
                continue
            sql = " ".join(a.value.split())
            m = re.match(r'^(?:INSERT INTO|UPDATE|DELETE FROM)\s+(?:"?[^\s(]+"?\.)?([A-Za-z_]\w*)',
                         sql, re.I)
            if m:
                out.add(m.group(1))
    return out


def _tabelele_scrise(nume_functie):
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    return _tabelele_din(ast.parse(sursa), nume_functie)


def test_alegerea_de_denumire_ATINGE_AMANDOUA_denumirile():
    """[F4, rescris de decizia R81 — 28.08.2026]

    Testul ăsta se numea ieri `test_alegerea_de_denumire_NU_atinge_denumirea_FISCALA` și cerea
    **exact pe dos**: că ramura `anaf` nu scrie în `firma_profil`. Era corect atunci — ecranul
    spunea că alegerea schimbă numai eticheta din portofoliu, iar testul ținea textul lipit de
    comportament. Docstringul lui de atunci scria, cuvânt cu cuvânt: *„nu e o interdicție: R81 nu e
    decisă, iar dacă decizia e să scrie, se scrie — se schimbă atunci și textul, și testul,
    împreună."* **Decizia a venit, și s-au schimbat amândouă.**

    Ce cere acum: alegerea de denumire ajunge **pe hârtie**. `alege_denumirea` trece prin
    `scrie_denumirea`, care atinge amândouă locurile în aceeași tranzacție. Dacă cineva scoate
    apelul, butonul redevine o etichetă — iar ecranul, care de azi spune că denumirea aplicată e
    cea de pe documente, ar minti în cealaltă direcție."""
    from core import scan_simetrie_denumire as _s
    arb = ast.parse(io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"),
                            encoding="utf-8").read())
    fn = {n.name: n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)}
    assert set(fn) >= {"alege_denumirea", "scrie_denumirea"}, sorted(fn)

    def cheama(nume_fn, tinta):
        return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == tinta
                   for c in ast.walk(fn[nume_fn]))

    assert cheama("alege_denumirea", "scrie_denumirea"), (
        "ramura ANAF nu mai trece prin scriitorul unic — alegerea ar redeveni o etichetă, iar pe "
        "declarații ar pleca mai departe cealaltă denumire (chiar defectul probat pe 27.08)")
    scrise = _tabelele_din(arb, "scrie_denumirea")
    assert scrise == {"tenants", "firma_profil"}, (
        "scriitorul unic nu mai atinge amândouă tabelele: %s" % sorted(scrise))
    assert not _s.asimetrii(), "au apărut scrieri asimetrice: %s" % (_s.asimetrii(),)


def test_CALIBRARE_F4_o_scriere_in_firma_profil_chiar_s_ar_vedea():
    """Direcția inversă, pe forma exactă a schimbării care ar face textul fals: un `UPDATE` într-o
    schemă de tenant, compus la rulare. Un extractor care s-ar uita la literalul întreg n-ar vedea
    numele tabelei, fiindcă schema e interpolată — iar absența lui ar arăta ca o dovadă."""
    fals = ast.parse(
        'def alege_denumirea(conn, tid):\n'
        '    with conn.cursor() as cur:\n'
        '        cur.execute(\'UPDATE "%s".firma_profil SET nume=%%s\' % schema, (n,))\n')
    assert _tabelele_din(fals, "alege_denumirea") == {"firma_profil"}
