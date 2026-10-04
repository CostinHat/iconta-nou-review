"""core/drepturi.py — cine poate face ce, pe rol și pe bifă (decizia Costin 04.10.2026, varianta 2).

SURSA UNICĂ a regulii. Garda de rută (`main.cere_drept(nivel)`) o aplică; `GET /eu/drepturi` o citește din
aceleași gărzi ca să-i spună interfeței ce să NU afișeze. O a doua listă, scrisă în JS, s-ar fi învechit
la prima rută nouă — de aceea interfața nu știe niciun nivel, primește doar „ce ți se refuză".

Decizia (verbatim în DECIZII.md, 04.10.2026), mereu doar pe firmele alocate asistentului:
  - PREGATI  — „Poate pregăti”: munca curentă (facturi, chitanțe, importuri, note în ciornă, pontaj,
               mijloace fixe și calculul amortizării, export SAGA/WinMentor, e-Transport, pregătirea
               declarațiilor);
  - VALIDA   — „Poate valida”: validarea notelor și a declarațiilor, înregistrarea amortizării, blocarea
               perioadei (închiderea lunii);
  - DEPUNE   — „Poate depune”: depunerea la ANAF;
  - ADMIN    — doar administratorul cabinetului: firme (adăugare/import/scoatere), asistenți și drepturile
               lor, chei API, GDPR, abonament, datele cabinetului, deblocarea unei perioade închise;
  - CITIRE   — orice actor al cabinetului pe o firmă alocată, fără bifă: cererile care NU schimbă nimic,
               dar merg pe POST (previzualizarea portalului clientului).

Administratorul cabinetului (și superadmin) trece pe toate nivelurile — exact ca până azi pe rutele care
îi erau rezervate. Bifele lui proprii rămân citite acolo unde erau deja (coada de declarații, patru ochi).

Bifa asistentului se citește LIVE din `public.users`, nu din token: o bifă retrasă acționează la cererea
următoare, nu la următoarea autentificare.
"""
from __future__ import annotations

from core import erori as _erori
from core.mesaje import FARA_ACCES_TENANT

PREGATI = "poate_pregati"
VALIDA = "poate_valida"
DEPUNE = "poate_depune"
ADMIN = "admin_cabinet"
CITIRE = "citire"

NIVELURI = (PREGATI, VALIDA, DEPUNE, ADMIN, CITIRE)
BIFE = (PREGATI, VALIDA, DEPUNE)

# Refuzul în termenii contabilului: CE lipsește (dreptul, cu numele de pe ecranul Asistenți) și CINE îl dă.
# „Dreptul potrivit” (mesajul generic de până azi) trimitea omul să ceară ceva fără nume — iar pe acțiunile
# rezervate administratorului nu există nicio bifă de cerut.
MESAJ = {
    PREGATI: ("Munca pe firmă — facturi, chitanțe, importuri, note contabile, pontaj, mijloace fixe, declarații "
              "de pregătit — cere dreptul «Poate pregăti», pe care nu-l ai. Îl acordă administratorul "
              "cabinetului, din ecranul Asistenți."),
    VALIDA: ("Validarea — notele contabile, declarațiile, înregistrarea amortizării, închiderea lunii — cere "
             "dreptul «Poate valida», pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul "
             "Asistenți."),
    DEPUNE: ("Depunerea la ANAF cere dreptul «Poate depune», pe care nu-l ai. Îl acordă administratorul "
             "cabinetului, din ecranul Asistenți."),
    ADMIN: ("Asta o face doar administratorul cabinetului: adăugarea, importul și scoaterea firmelor, asistenții "
            "și drepturile lor, cheile API, GDPR, abonamentul, datele cabinetului, deblocarea unei perioade "
            "închise. Cere-i lui."),
}

_TREC_MEREU = ("superadmin", "admin_firma")


def bife_live(conn, uid):
    """Bifele asistentului, citite acum (nu din token) — prin `repo_utilizatori.permisiuni`, citirea care există deja
    (fără SQL în modulul ăsta: P7, stratul de date stă în repository)."""
    from core import repo_utilizatori
    with conn.cursor() as cur:
        r = repo_utilizatori.permisiuni(cur, uid)
    if not r:
        return {}
    return {PREGATI: bool(r[0]), VALIDA: bool(r[1]), DEPUNE: bool(r[2])}


def permis(rol, bife, nivel):
    """Răspunsul PUR: rolul + bifele trec nivelul? (Fără firmă — alocarea se verifică separat.)"""
    if nivel not in NIVELURI:
        raise ValueError("nivel de drept necunoscut: %r" % (nivel,))
    if rol in _TREC_MEREU:
        return True
    if rol != "angajat":
        return False
    if nivel == ADMIN:
        return False
    if nivel == CITIRE:
        return True
    return bool((bife or {}).get(nivel))


def verifica(conn, ctx, nivel, tenant_id=None):
    """Ridică refuzul de domeniu dacă cererea nu trece nivelul. Întoarce None dacă trece.

    Ordinea, la asistent: întâi FIRMA (o firmă nealocată primește același răspuns ca una inexistentă —
    `FARA_ACCES_TENANT`, 404, decizia Costin 03.09), apoi BIFA. Altfel un asistent fără „Poate pregăti”
    ar afla, din refuzul de bifă, că un `tenant_id` oarecare există."""
    rol = ctx.get("rol")
    if rol in _TREC_MEREU:
        return None
    if rol != "angajat":
        raise _erori.FaraDrept(MESAJ[ADMIN] if nivel == ADMIN else "clienții folosesc portalul, nu rutele de cabinet")
    if nivel == ADMIN:
        raise _erori.FaraDrept(MESAJ[ADMIN])
    if tenant_id is not None:
        from core import auth_api
        if not auth_api.schema_tenant(conn, ctx["uid"], int(tenant_id)):
            raise _erori.Inexistent(FARA_ACCES_TENANT)
    if nivel == CITIRE:
        return None
    if not bife_live(conn, ctx["uid"]).get(nivel):
        raise _erori.FaraDrept(MESAJ[nivel])
    return None


# ── DERIVAREA pentru interfață: ce gardă stă pe fiecare rută, citit din aplicația vie ─────────────────────
def _garda_din(call):
    """Descrierea unei dependențe care e gardă, sau None. Gărzile se descriu singure (atribute puse de
    fabricile lor în `main.py`), deci aici nu se repetă nicio listă de rute."""
    if getattr(call, "nivel_drept", None):
        return ("drept", call.nivel_drept)
    if getattr(call, "roluri", None):
        return ("rol", tuple(call.roluri))
    if getattr(call, "__name__", "") == "cere_client":
        return ("rol", ("client",))
    return None


def garzi_rute(app):
    """[(METODĂ, cale, gardă)] pentru fiecare rută a aplicației care poartă o gardă de rol sau de drept."""
    out = []

    def _plimba(dep, acc):
        for s in dep.dependencies:
            g = _garda_din(s.call)
            if g:
                acc.append(g)
            _plimba(s, acc)
        return acc

    for r in getattr(app, "routes", []):
        dep = getattr(r, "dependant", None)
        if dep is None:
            continue
        garzi = _plimba(dep, [])
        if not garzi:
            continue
        for m in sorted(getattr(r, "methods", ()) or ()):
            if m == "HEAD":
                continue
            for g in garzi:
                out.append((m, r.path, g))
    return out


def trece_garda(rol, bife, garda):
    fel, val = garda
    if fel == "drept":
        return permis(rol, bife, val)
    return rol == "superadmin" or rol in val


def interzise(rol, bife, garzi):
    """Acțiunile („METODĂ /cale”, cu calea ca ȘABLON — exact cum stă în `main.py`) pe care garda le refuză
    utilizatorului. Interfața ascunde orice element al cărui `data-actiune` e în listă."""
    return sorted({"%s %s" % (m, c) for m, c, g in garzi if not trece_garda(rol, bife, g)})
