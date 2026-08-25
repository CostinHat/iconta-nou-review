# -*- coding: utf-8 -*-
"""core/cont_valid.py — un cont venit din CORPUL CERERII se confruntă cu planul firmei.

DECIZIA (Costin, 26.08.2026): **se refuză, nu se semnalează.** *„O notă cu cont inexistent nu e
evidență, e un rând care arată ca evidență. Nu se poate depune, nu se poate desface la control,
iar contabilul află abia când generează ceva."*

Argumentul contrar — că refuzul blochează un contabil care lucrează repede — se rezolvă altfel:
dacă vrea un cont nou, îl creează în plan. E o operațiune de câteva secunde **și e chiar decizia
pe care ar trebui s-o ia conștient.**

CE TREBUIE SĂ FACĂ REFUZUL, tot din decizie: să spună **CE** cont nu există și **UNDE** se
creează. Nu „cont invalid" — *„contul 7O7 nu există în planul firmei; îl adaugi din Plan de
conturi"*. Un cont scris greșit — `7O7` cu litera O în loc de `707` — devine vizibil imediat,
fiindcă refuzul îl numește.

TEMEIUL, în plan: `PLAN_ARHITECTURA.md` Partea III listează **planul de conturi** printre
Nomenclatoare, iar „Reguli de acces" spune *„Nimeni nu scrie o valoare din aceste categorii în
afara registrului"*. Regula lipsă — ce se face cu o intrare din AFARA nomenclatorului — a fost
adăugată acolo în aceeași zi, prin decizie.

DE CE E AICI ȘI NU ÎN `common.py`: `common` e pur, fără bază. Confruntarea cere planul firmei.
"""


def normalizeaza(v):
    """PURĂ. Ce rămâne dintr-un cont după curățare. `None`/gol/numai spații -> `""`.

    Prima jumătate a lui R54: tiparul `str(corp.get("cont_x") or "<implicit>")` lăsa `"   "` să
    treacă verbatim, iar acolo nu-l oprea nici `NOT NULL`, nici un `CHECK` pe șirul gol."""
    return str(v or "").strip()


def exista(conn, schema, cont):
    """Contul e în planul firmei? Citire, nimic altceva."""
    c = normalizeaza(cont)
    if not c:
        return False
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM %s.plan_conturi WHERE simbol = %%s LIMIT 1" % schema, (c,))
        return cur.fetchone() is not None


def apropiate(conn, schema, cont, n=3):
    """Conturi din plan care încep la fel — ca refuzul să poată sugera, nu doar să respingă.

    Nu ghicește ce a vrut omul; arată ce EXISTĂ în vecinătate. Pe `7O7` (cu litera O) nu
    găsește nimic, iar asta e informație: nu e o greșeală de o cifră, e alt caracter."""
    c = normalizeaza(cont)
    if not c:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT simbol, denumire FROM %s.plan_conturi WHERE simbol LIKE %%s "
                    "ORDER BY simbol LIMIT %%s" % schema, (c[:2] + "%", n))
        return [(r[0], r[1]) for r in cur.fetchall()]


def cere_cont(conn, schema, valoare, camp, implicit=None):
    """Contul curățat, DACĂ e în planul firmei. Altfel ridică `ValueError` cu ce lipsește.

    Rutele care o cheamă sunt în `try/except (ValueError, KeyError)` -> HTTP 422, deci refuzul
    ajunge la om ca mesaj, nu ca 500. Cine o cheamă din afara unui astfel de `try` trebuie s-o
    prindă singur — altfel ar transforma un refuz în defecțiune.

    `implicit` = contul folosit când câmpul lipsește din cerere. Se verifică ȘI el: un implicit
    care nu există în planul firmei ar fi exact aceeași greșeală, doar scrisă de noi."""
    c = normalizeaza(valoare) or normalizeaza(implicit)
    if not c:
        raise _fara_cont(camp)
    if exista(conn, schema, c):
        return c
    vecini = apropiate(conn, schema, c)
    if normalizeaza(valoare) or implicit is None:
        return _refuz(c, camp, vecini)
    # implicitul aplicației nu e în planul firmei — se spune că e al nostru, nu al omului
    return _refuz(c, camp + " (valoarea implicită a aplicației)", vecini)


UNDE_SE_CREEAZA = "Plan de conturi (Import date › Plan de conturi)"


class ContNecunoscut(ValueError):
    """Refuzul e o STRUCTURĂ, iar propoziția e randarea ei.

    [clichet 50 / METODA §23] Cerința lui Costin — *„să spună CE cont nu există și UNDE se
    creează"* — e despre text, deci un gard scris pe text ar fi fost singura variantă. Nu e:
    câmpurile trăiesc în `detalii`, garda le verifică pe ele, iar fraza se compune din ele
    într-un singur loc. Dintr-o frază cifrele și numele nu se pot compune înapoi (DS cap.13)."""

    def __init__(self, detalii):
        self.detalii = detalii
        super().__init__(randeaza(detalii))


def randeaza(d):
    """PURĂ. Propoziția, compusă din structura refuzului. Singurul loc unde se face."""
    if d["fel"] == "lipsa":
        return "Câmpul „%s” este obligatoriu: se completează cu un cont din planul firmei." % d["camp"]
    s = ""
    if d.get("apropiate"):
        s = " Conturi apropiate în plan: " + ", ".join(
            "%s (%s)" % (a, b) for a, b in d["apropiate"]) + "."
    return ("Contul %s nu există în planul firmei (câmpul „%s”).%s Îl adaugi din %s, apoi reia "
            "operațiunea." % (d["cont"], d["camp"], s, d["unde"]))


def _fara_cont(camp):
    return ContNecunoscut({"fel": "lipsa", "cont": None, "camp": camp, "unde": UNDE_SE_CREEAZA,
                           "apropiate": []})


def _refuz(c, camp, vecini, _de_unde=None):
    raise ContNecunoscut({"fel": "necunoscut", "cont": c, "camp": camp,
                          "unde": UNDE_SE_CREEAZA, "apropiate": list(vecini or [])})
