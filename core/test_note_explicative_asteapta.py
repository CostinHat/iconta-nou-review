# -*- coding: utf-8 -*-
"""GARDĂ DE AȘTEPTARE — notele explicative se întorc în lista 3 când devin delimitabile.

DE CE EXISTĂ, și de ce nu e o restanță (Costin, 30.08.2026): *„Notele explicative ies din lista 3 și
devin gardă cu condiție de deschidere scrisă. Nu e restanță, e imposibilitate temporară — se întoarce
singură când există o firmă cu două exerciții."*

**Imposibilitatea, cu mecanismul ei.** Conținutul notelor explicative depinde de **categoria de
mărime** a entității: OMFP 1802/2014 pct. 21 le cere entităților de la pct. 9 alin. (4) și celor de
interes public, iar microentitățile sunt scutite (pct. 20 alin. (1), cap. 12 „Scutiri pentru
microentități"). Categoria, la rândul ei, cere **două exerciții financiare consecutive** (pct. 13
alin. (2)-(3)) — vezi `core/categorie_marime.py`.

Măsurat pe 30.08.2026: **19 din 19 firme → `nedeterminata`**, fiindcă niciuna n-are două exerciții
consecutive cu rulaje. Deci nu se poate ști pentru NICIO firmă dacă notele sunt datorate — iar un
artefact pe care nu-l poți nici măcar delimita nu e o datorie, e o întrebare fără obiect.

**CE FACE GARDA ASTA, și e inversul unei gărzi obișnuite.** Nu apără un comportament: apără o
**absență motivată**. Cât timp niciun exercițiu-pereche nu există, trece. **În ziua în care apare o
firmă cu două exerciții consecutive, PICĂ** — și mesajul spune ce trebuie făcut: notele explicative
se întorc în lista 3, iar întrebarea „sunt datorate?" capătă, în sfârșit, un răspuns posibil.

*Adică motivul pentru care artefactul lipsește din listă e el însuși gardat. Fără asta, „nu se poate
delimita" ar fi o propoziție care rămâne adevărată în registru mult după ce a încetat să fie
adevărată în date — exact clasa pe care METODA §14 o numește doc-stătut.*

CE NU VERIFICĂ, declarat: nu spune dacă notele SUNT datorate (aia cere categoria, care azi nu iese),
și nu verifică conținutul lor — el nu s-a citit încă la sursă, tocmai fiindcă n-are pe ce se aplica.
"""
# FĂRĂ `skipif`. Prima formă sărea pe `PGHOST`/`PGDATABASE` — variabile care nici nu există aici
# (`~/.iconta/db.env` definește `DB_HOST`, `DB_NAME`, `DATABASE_URL`). Deci garda era **verde pe
# zero**: nu măsura nimic și nu spunea nimic. Un skip într-o gardă de AȘTEPTARE e mai rău decât în
# oricare alta — ea nu apără un comportament, ci supraveghează o condiție; sărită, condiția rămâne
# nesupravegheată exact cât timp e mai probabil să se schimbe. Poarta are întotdeauna baza (vezi
# PREDARE_LANT, „predarea nu se mai poate scrie fără acces la bază"), deci lipsa ei e o defecțiune,
# nu un caz de sărit.


def _firme_cu_doua_exercitii_consecutive():
    """[(schema, an_curent, an_precedent)] — firmele care AR PUTEA fi încadrate.

    Se folosesc aceleași rulaje din care se produce bilanțul (`bilant_api._rulaje_67`), ca să nu
    existe două răspunsuri la „exercițiul ăsta are mișcare?".
    """
    from psycopg2.extras import RealDictCursor

    from core import bilant_api as _ba
    from core import db

    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY id")
            scheme = [r[0] for r in cur.fetchall()]
    assert scheme, "ANTI-VACUU: zero firme active — garda ar trece pe o mulțime goală"

    gasite = []
    for schema in scheme:
        with db.get_conn(schema) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ani = []
                for an in range(2023, 2028):
                    try:
                        if _ba._rulaje_67(cur, schema, an):
                            ani.append(an)
                    except Exception:
                        break
        for a in ani:
            if a - 1 in ani:
                gasite.append((schema, a, a - 1))
    return scheme, gasite


def test_notele_explicative_sunt_inca_nedelimitabile():
    """Cât timp nicio firmă n-are două exerciții consecutive, notele nu se pot delimita — trece.

    **Când PICĂ, nu e o regresie: e semnalul că a devenit posibil ce nu era.**
    """
    scheme, gasite = _firme_cu_doua_exercitii_consecutive()
    assert not gasite, (
        "A APĂRUT o firmă cu DOUĂ exerciții financiare consecutive: %s.\n"
        "Asta ridică imposibilitatea temporară pentru care notele explicative au ieșit din lista 3 "
        "(decizia lui Costin, 30.08.2026).\n"
        "DE FĂCUT, în ordinea asta:\n"
        "  1. rulează `categorie_marime.categorie(conn, schema, an)` pe firma găsită — acum poate "
        "ieși altceva decât `nedeterminata`;\n"
        "  2. citește la sursă conținutul notelor (OMFP 1802/2014, cap. despre notele explicative) — "
        "n-a fost citit, tocmai fiindcă n-avea pe ce se aplica;\n"
        "  3. întoarce rândul în lista 3 din CONFORMITATE.md, cu A/B/C măsurate;\n"
        "  4. șterge garda asta — și-a făcut treaba.\n"
        "Măsurat pe %d firme active." % (gasite, len(scheme)))


def test_motivul_absentei_e_inca_adevarat_si_pe_categorie():
    """A doua față a aceleiași condiții, pe drumul prin care contează de fapt.

    Nu e o repetare: testul de sus întreabă „există date pentru două exerciții?", ăsta întreabă „iese
    o categorie?". Ele pot să difere — o firmă poate avea două exerciții și tot să nu se încadreze,
    dacă un criteriu nu se poate calcula. Ce ridică imposibilitatea e **al doilea**.
    """
    from core import categorie_marime as cm
    from core import db

    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY id")
            scheme = [r[0] for r in cur.fetchall()]
    assert scheme, "ANTI-VACUU: zero firme active"

    incadrate = []
    for schema in scheme:
        with db.get_conn(schema) as conn:
            try:
                a = cm.categorie(conn, schema, 2026)
            except Exception:
                continue
        if a["categorie"] != "nedeterminata":
            incadrate.append((schema, a["categorie"]))
    assert not incadrate, (
        "S-a încadrat o firmă: %s. Notele explicative pot fi acum delimitate — vezi mesajul "
        "celuilalt test din fișierul ăsta pentru ce se face mai departe." % incadrate)
