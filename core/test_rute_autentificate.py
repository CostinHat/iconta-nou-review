# -*- coding: utf-8 -*-
"""Garda: fiecare ruta HTTP declara o dependenta de autentificare.

DE CE (27.07.2026): auditul manual a gasit 375 de rute in main.py, dintre care 17 fara
`Depends` - toate public legitim. Curat, dar NIMIC nu impiedica o ruta noua nepazita sa
treaca neobservata. O ruta fara auth nu se vede in UI, nu strica niciun test si nu apare
in niciun log pana cand cineva o gaseste.

Acelasi audit a ratat 3 rute: core/spv_rute.py le declara cu @app.get INTERIORUL unei
functii (monteaza(app, ...)), pentru ca proiectul nu foloseste APIRouter. Garda scaneaza
ambele fisiere - o ruta ascunsa intr-o functie e tot o ruta.

CE VERIFICA: orice ruta care nu are Depends(...) in semnatura trebuie sa fie in lista
PUBLICE, explicit. Lista e o DECIZIE scrisa, nu o constatare - fiecare intrare e o ruta
despre care s-a hotarat ca e publica.

LIMITA DECLARATA: garda verifica PREZENTA unei dependente, nu CORECTITUDINEA ei. O ruta
de cabinet care cere din greseala `cere_client` trece. Gating-ul inconsecvent admin
(cere_rol("superadmin") vs cere_cabinet + garda inline) e task separat - vezi DE_FACUT.
Nu verifica nici IDOR (obiect din alt tenant) - alta clasa, alt gard.
"""
import ast
import pathlib

FISIERE = ("main.py", "core/spv_rute.py")
_METODE = ("get", "post", "put", "delete", "patch")

# Rute PUBLICE prin decizie. Fiecare linie = o hotarare, nu o constatare.
PUBLICE = {
    ("get",  "/"),                              # index (SPA shell)
    ("post", "/auth/login"),                    # autentificarea insasi
    ("post", "/auth/register"),                 # inregistrare cont nou
    ("get",  "/public/termeni"),                # T&C, obligatoriu public
    ("get",  "/public/config"),                 # config client (fara secrete)
    ("post", "/public/reset-parola/cere"),      # recuperare parola: userul nu e logat
    ("post", "/public/reset-parola/seteaza"),   # idem, cu token pe email
    ("post", "/public/magic-link"),             # login fara parola: cerere
    ("post", "/public/magic-login"),            # login fara parola: consum token
    ("post", "/public/activare"),               # activare cont din email
    ("get",  "/public/verifica-cui/{cui}"),     # verificare CUI la inregistrare (rate-limited)
    ("get",  "/public/plata/{ref}"),            # pagina de plata: platitorul NU e user
    ("post", "/public/plata/{ref}/confirma"),   # confirmare plata (ref = secret in URL)
    ("get",  "/ghid/{slug}"),                   # continut public (SEO)
    ("get",  "/ghid"),                          # index ghid
    ("get",  "/sitemap.xml"),                   # SEO
    ("get",  "/robots.txt"),                    # SEO
    ("get",  "/anaf/oauth/callback"),           # ANAF redirecteaza aici; nu are cum sa poarte
                                                # sesiunea noastra. Aparat de `state` semnat.
}


def _are_depends(fn):
    """True daca semnatura contine un apel Depends(...). Cauta in AST, nu in text:
    un regex pe semnatura se rupe la primul argument cu paranteze (lectia 27.07)."""
    a = fn.args
    noduri = list(a.defaults) + [x for x in a.kw_defaults if x is not None]
    for arg in a.posonlyargs + a.args + a.kwonlyargs:
        if arg.annotation is not None:
            noduri.append(arg.annotation)
    for nod in noduri:
        for sub in ast.walk(nod):
            if isinstance(sub, ast.Call):
                f = sub.func
                if isinstance(f, ast.Name) and f.id == "Depends":
                    return True
                if isinstance(f, ast.Attribute) and f.attr == "Depends":
                    return True
    return False


def _rute(rad=None):
    """[(metoda, cale, fisier, linie, are_depends)] pentru toate rutele HTTP."""
    rad = rad or pathlib.Path(__file__).resolve().parent.parent
    out = []
    for rel in FISIERE:
        src = (rad / rel).read_text(encoding="utf-8")
        for n in ast.walk(ast.parse(src)):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for d in n.decorator_list:
                if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and isinstance(d.func.value, ast.Name)
                        and d.func.value.id in ("app", "router")
                        and d.func.attr in _METODE):
                    continue
                if not (d.args and isinstance(d.args[0], ast.Constant)):
                    continue
                out.append((d.func.attr, d.args[0].value, rel, n.lineno, _are_depends(n)))
    return out


def test_exista_rute_de_verificat():
    """Daca scanarea nu mai gaseste rute, garda a devenit inerta - se repara, nu se ignora."""
    r = _rute()
    assert len(r) > 300, "doar %d rute gasite - scanarea s-a rupt" % len(r)


def test_orice_ruta_are_autentificare_sau_e_declarata_publica():
    lipsa = [(m, c, f, l) for m, c, f, l, dep in _rute()
             if not dep and (m, c) not in PUBLICE]
    assert not lipsa, (
        "rute fara autentificare si nedeclarate publice:\n" +
        "\n".join("  %-6s %-45s %s:%d" % (m.upper(), c, f, l) for m, c, f, l in lipsa) +
        "\n-> daca ruta TREBUIE sa fie publica, adaug-o in PUBLICE cu motivul pe linie."
    )


def test_lista_publice_nu_are_intrari_moarte():
    """O ruta stearsa sau care a primit auth trebuie scoasa din lista - altfel lista creste
    la nesfarsit si ajunge sa 'acopere' rute care nu mai exista."""
    fara_dep = {(m, c) for m, c, _f, _l, dep in _rute() if not dep}
    moarte = sorted(PUBLICE - fara_dep)
    assert not moarte, ("intrari in PUBLICE care nu mai corespund unei rute fara auth "
                        "(sterse sau au primit Depends): %s" % moarte)


def test_garda_prinde_o_ruta_noua_nepazita(tmp_path):
    """Mutatie: o ruta noua fara Depends trebuie sa iasa in lista, cu fisier si linie."""
    import textwrap
    (tmp_path / "core").mkdir()
    (tmp_path / "main.py").write_text(textwrap.dedent('''
        @app.get("/secret/date")
        def scurgere():
            return {}

        @app.post("/pazit")
        def pazit(ctx=Depends(cere_rol("admin"))):
            return {}
    ''').strip(), encoding="utf-8")
    (tmp_path / "core" / "spv_rute.py").write_text("", encoding="utf-8")
    r = _rute(tmp_path)
    fara = [(m, c) for m, c, _f, _l, dep in r if not dep]
    assert ("get", "/secret/date") in fara, "garda nu vede ruta nepazita"
    assert ("post", "/pazit") not in fara, "garda da fals-pozitiv pe ruta pazita"


def test_depends_cu_apel_imbricat_e_recunoscut(tmp_path):
    """Regresie pe lectia 27.07: un regex naiv se opreste la prima paranteza inchisa si
    rateaza Depends(cere_rol("a", "b")). AST-ul nu are problema asta - se dovedeste."""
    import textwrap
    (tmp_path / "core").mkdir()
    (tmp_path / "main.py").write_text(textwrap.dedent('''
        @app.get("/x")
        def x(tenant_id: int, date: dict = Body(...), ctx=Depends(cere_rol("a", "b"))):
            return {}
    ''').strip(), encoding="utf-8")
    (tmp_path / "core" / "spv_rute.py").write_text("", encoding="utf-8")
    assert all(dep for *_ , dep in _rute(tmp_path)), "Depends dupa un argument cu paranteze nu e vazut"
