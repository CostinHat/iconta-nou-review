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


def test_alegerea_are_AMANDOUA_ramurile_si_amandoua_SCRIU():
    """[R77] Costin: *„«a păstra pe a ta = a nu face nimic» nu e o alegere."* Deci și ramura
    „păstrez denumirea mea" trebuie să scrie ceva — altfel tăcerea arată identic cu o decizie."""
    from core import tenant_provisioning as tp
    assert set(tp.ALEGERI_NUME) == {"aplicatie", "anaf"}
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "alege_denumirea")
    sql = []
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            a = n.args[0]
            while isinstance(a, ast.BinOp):
                a = a.left
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                sql.append(" ".join(a.value.split()))
    consemnari = [s for s in sql if s.startswith("UPDATE public.tenants SET nume_ales=")]
    assert len(consemnari) == 1, (
        "alegerea nu se consemnează într-un singur loc, pentru AMBELE ramuri: %s" % sql)
    # consemnarea NU are voie să stea sub ramura „anaf"
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and ast.unparse(n.test).count("anaf"):
            corp = " ".join(ast.unparse(s) for s in n.body)
            assert corp.count("nume_ales=") == 0, (
                "consemnarea a ajuns sub ramura ANAF — atunci «păstrez denumirea mea» n-ar mai "
                "scrie nimic, iar tăcerea ar redeveni o decizie")


def test_o_citire_ANAF_mai_noua_REDESCHIDE_intrebarea():
    """Alegerea de azi nu acoperă o denumire schimbată la registru mâine. Regula trăiește în
    ecran: se compară `nume_anaf_la` cu `nume_ales_la`."""
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
