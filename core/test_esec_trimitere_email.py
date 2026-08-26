# -*- coding: utf-8 -*-
"""GARD [R73, 27.08.2026]: un eșec de trimitere a emailului nu se mai poate stinge tăcut.

DE UNDE VINE. Patru `_obs.trimite_email_html` stăteau sub `except Exception: pass`. Trei dintre
ele sunt **singura cale de intrare** — resetare de parolă, link de logare fără parolă, invitație
de asistent. Dacă serverul de mail pica, ecranul spunea *„ai primit linkul"* la fiecare cerere și
nimeni nu afla: nici clientul, nici cabinetul. Prin construcție nu se poate arăta că un eșec
**s-a** produs — chiar asta era problema. Reparat pe `cf945fc`: cele patru trec pe
`observare.esec_secundar`, cu `alerta=True` pe cele trei căi de acces.

DE CE UN GARD, dacă reparația e deja aplicată *(argumentul e al lui Costin, 27.08)*: **o lipsă
declarată rămâne lipsă.** Reparația e o schimbare de apel — o revenire la `except: pass` n-ar
pica nimic. Nici măcar n-ar arăta ca o revenire: forma subtilă (`except Exception: log(...)`)
arată **ca disciplină** și tace exact la fel.

CE FACE IMPOSIBIL:
  1. un `trimite_email_html` prins de un `try` al cărui `except` nu cheamă `esec_secundar`
     — indiferent dacă handlerul e gol, printează, sau loghează;
  2. una din cele trei căi de acces care pierde `alerta=True`;
  3. dispariția tăcută a domeniului: dacă subiectul unuia din cele patru emailuri se schimbă,
     gardul **pică** în loc să se uite în gol (anti-vacuu — [[gard-care-nu-se-verifica-pe-sine]]).

CE NU FACE, și e jumătate din onestitatea lui:
  - **niciun clichet pe cele 28 de `except …: pass` rămase** în producție. Costin, explicit:
    *„pe alea nu le-am măsurat și nu știm care sunt legitime."* Clasa măsurată pe 26.08 avea 32,
    din care 5 în jurul unei operațiuni spre exterior; 4 erau cele de email, 1 e **declarată**
    (`anaf_api.py:101`, unde eșecul are o valoare vizibilă în loc: `fallback`). Restul n-au fost
    citite unul câte unul, deci nu intră aici.
  - **nu verifică dacă emailul chiar pleacă.** Verifică doar că, dacă nu pleacă, rămâne urmă.
  - **nu vede un `esec_secundar` chemat pe o ramură condiționată** (`if x: esec_secundar(...)`):
    îl numără ca prezent. Un `alerta` care nu e literal e însă raportat, tocmai fiindcă de aici
    nu se poate citi ce valoare are la rulare.

DOMENIUL, măsurat pe 27.08.2026 înainte de a scrie regula: **17** apeluri `trimite_email_html`
în `main.py` + `core/` (fără teste). Din ele, **4** sunt prinse de un `try` cu `except` — exact
cele patru reparate. Douăsprezece lasă excepția să urce (deci zgomotoase prin construcție), iar
unul (`sinteza_zilnica.py:172`) stă într-un `try/finally` fără handler — nu înghite nimic.
De aceea regula 1 se aplică **peste tot, fără listă de excepții**: n-are niciuna azi.
"""
import ast
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cele patru trimiteri reparate pe 26.08 (`cf945fc`), identificate prin SUBIECTUL emailului —
# un argument al apelului protejat, nu un număr de linie și nu un comentariu.
# Valoarea = ce cere decizia (a) a lui Costin: alertă pe căile de ACCES, tăcere-cu-urmă pe politețe.
_CELE_PATRU = {
    "Resetare parola iConta.eu": True,
    "Link de logare iConta.eu": True,
    "Acces asistent iConta.eu": True,
    "Bine ai venit pe iConta.eu": False,
}


# ============================================================
#  Citirea: pe AST, nu pe text (METODA §23)
# ============================================================
def _nume(c):
    f = c.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def _alerta(c):
    """Valoarea argumentului `alerta` al unui apel `esec_secundar`, ca structură.

    `None` = nedat, deci implicit `False` (semnătura: `esec_secundar(eticheta, eroare, alerta=False)`).
    Un argument care nu e literal se întoarce ca **text**, ca să nu treacă drept `True`: de aici
    nu se poate ști ce valoare are la rulare.
    """
    for kw in c.keywords:
        if kw.arg == "alerta":
            return kw.value.value if isinstance(kw.value, ast.Constant) else ast.unparse(kw.value)
    if len(c.args) >= 3:
        a = c.args[2]
        return a.value if isinstance(a, ast.Constant) else ast.unparse(a)
    return None


def trimiteri(sursa):
    """Fiecare apel `trimite_email_html` din sursă, cu ce-l protejează.

    [{linia, subiect, protejat, handlere: [{linia, tip, esec_secundar, alerta}]}]
    `protejat=False` înseamnă că excepția urcă — zgomotos, deci în regulă.
    Un `try/finally` fără `except` dă `handlere=[]`: nu înghite nimic.
    """
    arb = ast.parse(sursa)
    tries = [n for n in ast.walk(arb) if isinstance(n, ast.Try)]
    out = []
    for n in ast.walk(arb):
        if not isinstance(n, ast.Call) or _nume(n) != "trimite_email_html":
            continue
        gazde = [t for t in tries
                 if any(any(x is n for x in ast.walk(s)) for s in t.body)]
        gazda = min(gazde, key=lambda t: n.lineno - t.lineno) if gazde else None
        subiect = (n.args[1].value
                   if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) else None)
        handlere = []
        for h in (gazda.handlers if gazda is not None else []):
            ap = [c for c in ast.walk(h)
                  if isinstance(c, ast.Call) and _nume(c) == "esec_secundar"]
            handlere.append({
                "linia": h.lineno,
                "tip": ast.unparse(h.type) if h.type else "<bare>",
                "esec_secundar": bool(ap),
                "alerta": _alerta(ap[0]) if ap else None,
            })
        out.append({"linia": n.lineno, "subiect": subiect,
                    "protejat": gazda is not None, "handlere": handlere})
    return out


# ============================================================
#  Regulile — funcții pure, ca să fie calibrabile pe surse mutante
# ============================================================
def incalcari_de_tacere(trims):
    """REGULA 1: un `except` care prinde o trimitere de email cheamă `esec_secundar`."""
    return ["%s:%s except %s — prinde `%s` și nu cheamă `esec_secundar`"
            % (t.get("fisier", "<sursă>"), h["linia"], h["tip"], t["subiect"])
            for t in trims for h in t["handlere"] if not h["esec_secundar"]]


def incalcari_de_alerta(trims):
    """REGULA 2: cele trei căi de ACCES alertează; politețea nu.

    Ambele direcții: o alertă lipsă pe o cale de acces ascunde un om blocat afară; o alertă pe
    fiecare bun-venit face alertele să fie ignorate, ceea ce ascunde tot un om blocat afară.
    """
    rele = []
    for t in trims:
        if t["subiect"] not in _CELE_PATRU:
            continue
        cerut = _CELE_PATRU[t["subiect"]]
        for h in t["handlere"]:
            if not h["esec_secundar"]:
                continue  # o raportează regula 1
            # `alerta` nedat = implicit `False`, conform semnăturii lui `esec_secundar`.
            efectiv = False if h["alerta"] is None else h["alerta"]
            if efectiv is not cerut:
                rele.append("%s:%s subiect %r — `alerta` ajunge %r, se cere %r"
                            % (t.get("fisier", "<sursă>"), h["linia"], t["subiect"],
                               efectiv, cerut))
    return rele


def _fisiere():
    fis = [os.path.join(_RAD, "main.py")]
    d = os.path.join(_RAD, "core")
    fis += [os.path.join(d, f) for f in sorted(os.listdir(d))
            if f.endswith(".py") and not f.startswith("test_")]
    return [f for f in fis if os.path.exists(f)]


def _toate():
    out = []
    for f in _fisiere():
        for t in trimiteri(io.open(f, encoding="utf-8").read()):
            t["fisier"] = os.path.relpath(f, _RAD)
            out.append(t)
    return out


# ============================================================
#  Gărzile pe codul real
# ============================================================
def test_o_trimitere_prinsa_de_try_nu_se_stinge_tacut():
    """REGULA, fără listă de excepții — măsurat 27.08: n-are niciuna."""
    rele = incalcari_de_tacere(_toate())
    assert not rele, (
        "trimiteri de email înghițite fără urmă:\n  " + "\n  ".join(rele)
        + "\n\nUn eșec fără urmă nu se poate diagnostica: ecranul afirmă că linkul a plecat, "
          "iar nimeni nu află că n-a plecat. Folosește "
          "`_obs.esec_secundar(eticheta, eroare, alerta=...)` — înghițit, dar nu tăcut.")


def test_cele_trei_cai_de_acces_alerteaza_iar_bun_venit_nu():
    rele = incalcari_de_alerta(_toate())
    assert not rele, (
        "\n  ".join(["decizia (a) de pe R73 nu mai e respectată:"] + rele)
        + "\n\nTăcerea pe o cale de acces are cost de ACCES — omul nu mai poate intra. "
          "Alerta pe un bun-venit are cost de atenție — alertele devin zgomot.")


def test_ANTI_VACUU_cele_patru_trimiteri_chiar_sunt_vazute():
    """Fără asta, o redenumire de subiect ar goli domeniul iar gardul ar rămâne verde."""
    toate = _toate()
    assert len(toate) >= 10, (
        "doar %d apeluri `trimite_email_html` citite — gardul s-ar uita în gol" % len(toate))
    gasite = {t["subiect"] for t in toate if t["subiect"] in _CELE_PATRU}
    lipsa = sorted(set(_CELE_PATRU) - gasite)
    assert not lipsa, (
        "subiecte din `_CELE_PATRU` negăsite în cod: %s — ori s-a redenumit emailul, ori "
        "trimiterea a dispărut. Actualizează harta DELIBERAT; până atunci gardul nu păzește "
        "nimic acolo." % lipsa)
    neprotejate = sorted(t["subiect"] for t in toate
                         if t["subiect"] in _CELE_PATRU and not t["handlere"])
    assert not neprotejate, (
        "cele patru trebuie să rămână prinse de un `try` cu `except`: %s n-are handler. "
        "Dacă excepția urcă acum deliberat, scoate subiectul din `_CELE_PATRU` cu motivul."
        % neprotejate)


# ============================================================
#  CALIBRARE — ambele direcții (METODA §22), pe surse mutante
# ============================================================
def _mutant(corp_handler, subiect="Link de logare iConta.eu"):
    return ("def cere_link():\n"
            "    try:\n"
            "        _obs.trimite_email_html(email, %r, html)\n"
            "    except Exception as _e:\n"
            "        %s\n" % (subiect, corp_handler))


def test_CALIBRARE_revenirea_la_except_pass_E_prinsa():
    assert incalcari_de_tacere(trimiteri(_mutant("pass")))


def test_CALIBRARE_forma_subtila_log_fara_esec_secundar_E_prinsa():
    """Arată ca disciplină și tace la fel. Cerută explicit de Costin la calibrare."""
    assert incalcari_de_tacere(trimiteri(_mutant('log("email esuat: %s" % _e)')))
    assert incalcari_de_tacere(trimiteri(_mutant('print("email esuat", _e)')))
    assert incalcari_de_tacere(trimiteri(_mutant('_obs.log_intern("email", _e)')))


def test_CALIBRARE_bare_except_cu_esec_secundar_NU_e_prins_de_regula_1():
    """Direcția «acuză pe nedrept»: regula 1 e despre urmă, nu despre forma lui `except`."""
    s = ("try:\n"
         "    _obs.trimite_email_html(e, 'Link de logare iConta.eu', h)\n"
         "except:\n"
         "    _obs.esec_secundar('email link de logare', None, alerta=True)\n")
    assert not incalcari_de_tacere(trimiteri(s))


def test_CALIBRARE_try_finally_fara_handler_NU_e_raportat():
    """Forma reală din `sinteza_zilnica.py`: un `try/finally` nu înghite nimic."""
    s = ("try:\n"
         "    ok = observare.trimite_email_html(catre, subiect, html)\n"
         "finally:\n"
         "    conn.close()\n")
    t = trimiteri(s)
    assert t and t[0]["handlere"] == []
    assert not incalcari_de_tacere(t)


def test_CALIBRARE_forma_reparata_NU_e_raportata():
    """Fără direcția asta, un detector care raportează tot ar trece primele două teste."""
    s = _mutant("_obs.esec_secundar('email link de logare', _e, alerta=True)")
    assert not incalcari_de_tacere(trimiteri(s))
    assert not incalcari_de_alerta(trimiteri(s))


def test_CALIBRARE_alerta_pierduta_pe_o_cale_de_acces_E_prinsa():
    assert incalcari_de_alerta(trimiteri(_mutant("_obs.esec_secundar('email', _e)")))
    assert incalcari_de_alerta(trimiteri(_mutant("_obs.esec_secundar('email', _e, alerta=False)")))


def test_CALIBRARE_alerta_necitibila_E_prinsa():
    """`alerta=e_productie()` nu se poate citi de aici — se raportează, nu se presupune `True`."""
    assert incalcari_de_alerta(
        trimiteri(_mutant("_obs.esec_secundar('email', _e, alerta=e_productie())")))


def test_CALIBRARE_alerta_pe_bun_venit_E_prinsa():
    """Cealaltă direcție a regulii 2: alertele care sună mereu nu mai sunt citite."""
    s = _mutant("_obs.esec_secundar('email bun venit cabinet', _e, alerta=True)",
                subiect="Bine ai venit pe iConta.eu")
    assert incalcari_de_alerta(trimiteri(s))


def test_CALIBRARE_redenumirea_subiectului_goleste_domeniul_si_SE_VEDE():
    """Proba anti-vacuului însuși: dacă subiectul se schimbă, harta nu mai găsește nimic."""
    s = _mutant("_obs.esec_secundar('email', _e, alerta=True)",
                subiect="Link de logare iConta.eu (v2)")
    gasite = {t["subiect"] for t in trimiteri(s) if t["subiect"] in _CELE_PATRU}
    assert not gasite, "subiectul mutat n-ar trebui recunoscut: %s" % gasite
