# -*- coding: utf-8 -*-
"""GARD [R72, 27.08.2026]: calea de scoatere a unei firme nu poate rămâne în urma bazei.

DE UNDE VINE, și e o lecție despre LISTE, nu despre ștergere. `gdpr_sterge` — singura ștergere
din aplicație — curăța **2** din cele **13** tabele din `public` care poartă `tenant_id`. Nu
fiindcă cineva a ales cele două, ci fiindcă atâtea erau **când s-a scris**. Măsurat pe 25.08:
12 tabele. Măsurat pe 27.08: **13** — a treisprezecea, `schimbari_email`, fusese creată pe
**26.08 la 13:34** de reparația R62. *Lista se lungește la fiecare funcționalitate nouă, iar
calea de ștergere nu se uită la ea.*

CE FACE IMPOSIBIL:
  1. **o a paisprezecea tabelă cu `tenant_id` care intră fără să fie clasificată** — ori se
     curăță (`TABELE_TENANT`), ori se declară de ce nu (`NU_SE_STERG`). Lista din cod se
     confruntă cu `information_schema` la fiecare rulare, deci nu poate îmbătrâni tăcut;
  2. o tabelă rămasă în listă după ce a dispărut din bază (clichet în ambele direcții);
  3. **o a doua cale de ștergere a unei firme** — `gdpr_sterge` trebuie să cheme funcția asta,
     nu să-și țină propria listă. Structural, pe AST: se caută apelul, nu un comentariu;
  4. o firmă **cu evidență** ștearsă prin `scoatere_firma`;
  5. **urma ștearsă de propriul act** — `firme_scoase` nu are voie să intre în `TABELE_TENANT`;
  6. un `motiv` inventat, care ar ocoli și confirmarea, și verificarea evidenței.

CE NU FACE, declarat:
  - **nu șterge nimic ca să probeze**, și de-aia proba de capăt-la-capăt lipsește de aici.
    Suita rulează pe baza de PRODUCȚIE (R67) — un test care creează și șterge o firmă adevărată
    ar fi exact sonda-care-scrie din care am învățat deja o dată. Se probează **decizia**
    (`evidenta`, refuzul, clasificarea), nu efectul distructiv.
  - nu spune dacă definiția lui «are evidență» e cea POTRIVITĂ — aia e decizia lui Costin din
    27.08. Spune că e aplicată, și că nu se poate strecura pe lângă ea.
"""
import ast
import io
import os
import re

import pytest

from core import db, tenant_stergere as ts

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arbore(modul):
    return ast.parse(io.open(os.path.join(_RAD, "core", modul + ".py"), encoding="utf-8").read())


def _arbore_main():
    return ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())


def _functia(nume, modul="tenant_stergere"):
    return next(n for n in ast.walk(_arbore(modul))
                if isinstance(n, ast.FunctionDef) and n.name == nume)


def _sql_executat(nod):
    """SQL-ul fiecărui `…execute(…)` din arbore, în ordinea liniilor.

    Se ia ARGUMENTUL apelului — un nod — nu se caută șiruri în fișier. Pe un argument compus
    (`"…%s…" % x`) se coboară pe stânga, unde stă litera SQL-ului."""
    gasite = []
    for n in ast.walk(nod):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "execute" and n.args):
            continue
        a = n.args[0]
        while isinstance(a, ast.BinOp):
            a = a.left
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            gasite.append((n.lineno, " ".join(a.value.split())))
    return [s for _l, s in sorted(gasite)]


def _felul_operatiei(sql):
    """Ce fel de pas e o instrucțiune SQL, ca etichetă — ca ordinea să se poată compara."""
    if sql.startswith("INSERT INTO public.firme_scoase"):
        return "urma"
    if sql.startswith("DELETE FROM public.\"%s\" WHERE tenant_id"):
        return "public"
    if sql.startswith("DROP SCHEMA"):
        return "schema"
    if sql.startswith("DELETE FROM public.tenants WHERE id"):
        return "rand"
    if sql.startswith("UPDATE public.users SET activ=false"):
        return "clienti"
    return None


@pytest.fixture(scope="module")
def tabele_cu_tenant_id():
    """Ce poartă `tenant_id` în `public`, ACUM — citit din bază, nu dintr-o listă."""
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT c.table_name
                       FROM information_schema.columns c
                       JOIN information_schema.tables t
                         ON t.table_schema = c.table_schema AND t.table_name = c.table_name
                       WHERE c.table_schema = 'public' AND c.column_name = 'tenant_id'
                         AND t.table_type = 'BASE TABLE'""")
        return {r[0] for r in cur.fetchall()}


def test_ANTI_VACUU_chiar_se_vad_tabelele(tabele_cu_tenant_id):
    assert len(tabele_cu_tenant_id) >= 10, (
        "doar %d tabele cu `tenant_id` citite din bază — interogarea s-a rupt, iar gărzile de "
        "mai jos ar trece în gol" % len(tabele_cu_tenant_id))


def test_nicio_tabela_cu_tenant_id_neclasificata(tabele_cu_tenant_id):
    """Cazul real: `schimbari_email` a apărut pe 26.08 și n-a intrat în nicio cale de ștergere."""
    clasificate = set(ts.TABELE_TENANT) | set(ts.NU_SE_STERG)
    noi = sorted(tabele_cu_tenant_id - clasificate)
    assert not noi, (
        "tabele care poartă `tenant_id` și nu sunt nici curățate, nici declarate: %s\n"
        "Pune-le în `tenant_stergere.TABELE_TENANT`, sau în `NU_SE_STERG` cu motivul. "
        "O firmă ștearsă ar lăsa rânduri în ele, iar pe cele fără cheie străină nimic nu le-ar "
        "lega de nimic." % noi)


def test_lista_din_cod_nu_pastreaza_tabele_disparute(tabele_cu_tenant_id):
    disparute = sorted(set(ts.TABELE_TENANT) - tabele_cu_tenant_id)
    assert not disparute, (
        "tabele din `TABELE_TENANT` care nu mai poartă `tenant_id` (sau nu mai există): %s — "
        "scoate-le, altfel ștergerea ar crăpa pe prima firmă." % disparute)


def test_urma_nu_se_sterge_odata_cu_firma():
    """O urmă ștearsă de propriul act nu e o urmă. `firme_scoase` poartă `tenant_id` tocmai ca
    să se poată citi pe firmă — deci trebuie declarată explicit, nu uitată."""
    # Operator de mulțime, nu `in`: pe un `str` ajuns din greșeală în locul listei, `in` ar
    # trece ca sub-șir, iar `>=` crapă. (Modul de eșec al containerului, scan_garzi_pe_text.)
    assert set(ts.NU_SE_STERG) >= {"firme_scoase"}
    assert set(ts.TABELE_TENANT).isdisjoint({"firme_scoase"})
    assert len(ts.NU_SE_STERG["firme_scoase"]) > 30, (
        "declarația fără motiv scris e o scutire, nu o declarație")


def test_gdpr_sterge_foloseste_ACEEASI_cale():
    """Costin, 27.08: «altfel avem două căi de ștergere care se vor rupe separat — iar una din
    ele e deja ruptă». Structural, pe AST."""
    sursa = io.open(os.path.join(_RAD, "core", "gdpr_sterge.py"), encoding="utf-8").read()
    arb = ast.parse(sursa)
    cheama = [
        n for n in ast.walk(arb)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "sterge"
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "tenant_stergere"
    ]
    assert cheama, (
        "`gdpr_sterge` nu cheamă `tenant_stergere.sterge` — și-a refăcut propria listă de "
        "tabele. Aia e a doua cale de ștergere, care se va rupe separat.")
    motive = {a.value for c in cheama for a in c.args
              if isinstance(a, ast.Constant) and isinstance(a.value, str)}
    assert motive >= {"gdpr_cabinet"}, (
        "apelul din GDPR nu poartă motivul `gdpr_cabinet` — fără el, ștergerea ar cere "
        "confirmare pe CUI și ar refuza firmele cu evidență, adică exact ce GDPR trebuie să șteargă")
    # și nu mai are voie să-și țină propria listă de ștergeri pe firmă
    proprii = [s for s in _sql_executat(arb) if s.startswith("DELETE FROM public.tenants WHERE")]
    assert len(proprii) <= 1, (
        "`gdpr_sterge` mai are %d ștergeri proprii pe `tenants` — o singură plasă de siguranță "
        "e de ajuns" % len(proprii))


def test_cele_doua_motive_si_nimic_altceva():
    assert set(ts.MOTIVE) == {"scoatere_firma", "gdpr_cabinet"}
    with pytest.raises(ValueError):
        ts.sterge(None, 1, "orice_altceva", 1)


def test_evidenta_acopera_ce_a_decis_Costin():
    """Definiția, ca structură: declarații depuse · declarații în coadă · documente emise din
    schema firmei. Testul nu judecă alegerea; verifică să nu se subțieze tăcut."""
    public = {t for t, _ in ts.EVIDENTA_PUBLIC}
    schema = {t for t, _ in ts.EVIDENTA_SCHEMA}
    assert {"declaratii_depuse", "declaratii_coada"} <= public
    assert {"inregistrari", "facturi", "state_plata", "artefacte_produse"} <= schema, (
        "cele patru numite de Costin trebuie să rămână în definiție")


def test_o_firma_cu_documente_NU_se_poate_sterge_iar_una_goala_DA():
    """Pe date reale, în ambele direcții — fără să șteargă nimic (doar previzualizare)."""
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants ORDER BY id")
        firme = [r[0] for r in cur.fetchall()]
        assert firme, "nicio firmă în bază — proba n-ar discrimina nimic"
        verdicte = {}
        for tid in firme:
            p = ts.previzualizare(conn, tid)
            verdicte[tid] = p["se_poate_sterge"]
            if not p["se_poate_sterge"]:
                assert p["evidenta"]["motive"], (
                    "firma %s e refuzată fără să spună de ce — un refuz fără motiv nu se poate "
                    "verifica" % tid)
    assert any(verdicte.values()) and not all(verdicte.values()), (
        "toate firmele au același verdict (%s) — proba n-ar deosebi o regulă care merge de una "
        "care întoarce mereu același răspuns" % set(verdicte.values()))


def test_o_tabela_lipsa_din_schema_NU_se_numara_ca_zero():
    """Direcția care contează cel mai mult: dacă o tabelă de evidență ar fi redenumită, un `0`
    tăcut ar transforma o firmă cu documente într-una ștearsă fără urmă.

    Structural, nu pe text: se caută în arborele lui `evidenta` apelurile `<listă>.append`, și
    se cere ca amândouă listele să fie hrănite — cea care marchează tabela lipsă (`nedecis`) și
    cea care produce refuzul (`motive`). Dacă a doua dispare, `nedecis` ar rămâne o notă fără
    efect, iar ștergerea ar trece."""
    fn = _functia("evidenta")
    tinte = {(n.func.value.id, n.func.attr) for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and isinstance(n.func.value, ast.Name)}
    assert tinte >= {("nedecis", "append"), ("motive", "append")}, (
        "`evidenta` nu mai marchează tabelele lipsă sau nu mai produce motiv din ele — o "
        "redenumire de tabelă ar deveni un zero tăcut. Găsite: %s" % sorted(tinte))


def test_ordinea_ceruta_urma_public_schema_randul_firmei():
    """Costin, 27.08: «întâi cele 13 din public, apoi DROP SCHEMA. Dacă una eșuează, schema
    rămâne și se poate relua.» Plus urma, care se scrie prima: numele, CUI-ul și schema dispar
    odată cu rândul din `tenants`, deci o urmă scrisă după n-ar mai avea de unde lua ce scrie.

    Se citește ORDINEA operațiilor din arborele funcției — felul fiecărui `cur.execute`, în
    ordinea liniilor — nu textul fișierului."""
    ordine = [f for f in (_felul_operatiei(s) for s in _sql_executat(_functia("sterge"))) if f]
    assert ordine[:4] == ["urma", "public", "schema", "rand"], (
        "ordinea operațiilor din `sterge` nu mai e cea cerută: %s" % ordine)


def test_previzualizarea_numara_randurile_INAINTE():
    """R50 (c): *«previzualizarea numără rândurile înainte, ca omul să vadă ce dispare»*. O
    ștergere care spune doar «se șterge tot» nu se poate confrunta cu nimic după."""
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants ORDER BY id LIMIT 1")
        tid = cur.fetchone()[0]
        p = ts.previzualizare(conn, tid)
        assert set(p) >= {"randuri_de_sters", "tabele_curatate", "confirmare_ceruta",
                          "urme_de_pastrat"}, sorted(p)
        rd = p["randuri_de_sters"]
        assert set(rd).issubset(set(ts.TABELE_TENANT)), (
            "previzualizarea numără tabele care nu sunt în lista de curățat: %s"
            % sorted(set(rd) - set(ts.TABELE_TENANT)))
        # lista celor stricate, nu `all(...)`: pe un dicționar gol `all` ar trece fără să compare
        rele = [k for k, v in rd.items() if not isinstance(v, int) or v <= 0]
        assert not rele, (
            "numărătoarea trebuie să conțină doar tabelele NEGOALE, ca lista să însemne ceva: %s"
            % {k: rd[k] for k in rele})
        # și cabinetul, pe aceeași cale — altfel GDPR ar rămâne fără cifră
        from core import gdpr_sterge
        cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE id=%s", (tid,))
        cab = cur.fetchone()[0]
        if cab:
            assert set(gdpr_sterge.previzualizare(conn, cab)) >= {"randuri_de_sters"}


def test_niciun_cont_de_client_nu_ramane_fara_nicio_firma():
    """INVARIANT pe date, măsurat 27.08.2026: clasa e **goală** (0 conturi de client fără firmă).

    Un cont de client fără nicio firmă poate cere în continuare un link de logare, intră în portal
    și nu vede nimic. E orfanul din R44/R50 mutat pe un **om**. Prima ștergere de firmă i-ar fi
    produs pe primii doi — de aceea `sterge` îi dezactivează, iar aserțiunea asta ține clasa goală.
    """
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT u.id, u.email FROM public.users u
                       WHERE u.rol = 'client' AND u.activ
                         AND NOT EXISTS (SELECT 1 FROM public.user_tenants ut
                                         WHERE ut.user_id = u.id)""")
        orfani = cur.fetchall()
        cur.execute("SELECT count(*) FROM public.users WHERE rol='client'")
        total = cur.fetchone()[0]
    assert total > 0, "niciun cont de client în bază — invariantul n-ar discrimina nimic"
    assert not orfani, (
        "conturi de client ACTIVE fără nicio firmă: %s — pot cere un link de logare și intra "
        "într-un portal gol. Ori se leagă de o firmă, ori se dezactivează." % orfani)


def test_stergerea_dezactiveaza_clientul_ramas_fara_firma():
    """Structural, pe arborele lui `sterge`: rândul din `users` NU se șterge (identitatea nu e a
    firmei — R62), dar se trece pe `activ=false`. Și numai DUPĂ ce legăturile au fost rupte,
    altfel numărătoarea „câte firme mai are" ar fi cea de dinainte."""
    ordine = [f for f in (_felul_operatiei(s) for s in _sql_executat(_functia("sterge"))) if f]
    assert ordine == ["urma", "public", "schema", "rand", "clienti"], (
        "ordinea operațiilor din `sterge` nu mai e cea așteptată: %s" % ordine)
    sql = _sql_executat(_functia("sterge"))
    assert not [s for s in sql if s.startswith("DELETE FROM public.users")], (
        "`sterge` șterge rânduri din `users` — un cont de om nu e al firmei; se dezactivează")


def test_previzualizarea_numeste_conturile_care_raman_fara_firma():
    """Refuzul și consecința se văd ÎNAINTE de apăsare, cu numele lor — nu după."""
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants ORDER BY id LIMIT 1")
        p = ts.previzualizare(conn, cur.fetchone()[0])
        assert set(p) >= {"clienti_de_dezactivat"}, sorted(p)
        rele = [c for c in p["clienti_de_dezactivat"] if set(c) < {"id", "email"}]
        assert not rele, (
            "previzualizarea listează conturi fără email — omul n-ar ști pe cine dezactivează: %s"
            % rele)


def test_urmele_portalului_supravietuiesc_SCOATERII_dar_nu_stergerii_GDPR():
    """Cerut de Costin înainte de prima apăsare: *„cele 4 rânduri din `urme_portal` se păstrează.
    Sunt singura dovadă că traseul R62 a fost parcurs pe date."*

    Și jumătatea care nu se vede din cerere: urmele conțin **adrese de email**. La o ștergere
    **GDPR** nu se copiază nimic — acolo scopul actului e chiar dispariția datelor, iar un log
    care le-ar păstra ar anula ștergerea pe care o consemnează.

    Structural: în `sterge`, `urme_de_pastrat` se cheamă **condiționat de `motiv`**. Un apel
    necondiționat ar copia și la GDPR."""
    fn = _functia("sterge")
    apeluri = [n for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "urme_de_pastrat"]
    assert len(apeluri) == 1, (
        "aștept exact un apel la `urme_de_pastrat` în `sterge`, găsite %d" % len(apeluri))
    conditionate = [n for n in ast.walk(fn)
                    if isinstance(n, ast.IfExp) and any(a is apeluri[0] for a in ast.walk(n.body))]
    assert conditionate, (
        "`urme_de_pastrat` se cheamă NECONDIȚIONAT în `sterge` — atunci se copiază și la o "
        "ștergere GDPR, iar logul ar reintroduce exact ce trebuia să dispară")
    # condiția se citește ca NOD, nu ca text: `motiv == "scoatere_firma"`
    t = conditionate[0].test
    forma = (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name) and t.left.id == "motiv"
             and len(t.ops) == 1 and isinstance(t.ops[0], ast.Eq)
             and isinstance(t.comparators[0], ast.Constant)
             and t.comparators[0].value == "scoatere_firma")
    assert forma, (
        "condiția nu e `motiv == \"scoatere_firma\"`, ci %r — orice altă formă poate lăsa "
        "copierea să se producă și la GDPR" % ast.unparse(t))


def test_urma_pastrata_se_poate_CITI_de_om():
    """`public.firme_scoase` era, în ziua în care s-a construit, a doua instanță a clasei
    declarate dimineață la `urme-portal`: **scrisă, necitită de om**. Costin: *„o urmă pe care
    n-o poate deschide nimeni fără `psql` nu e urmă pentru cabinet, e urmă pentru administratorul
    serverului."* Aici se cere ca ruta de citire să existe; că e chemată dintr-un ecran o cere
    `core/test_ruta_fara_apelant.py`."""
    arb = _arbore_main()
    cai = set()
    for n in ast.walk(arb):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                    and d.args and isinstance(d.args[0], ast.Constant)):
                cai.add((d.func.attr.upper(), d.args[0].value))
    assert cai >= {("GET", "/firme-scoase")}, (
        "nu există nicio rută care citește `firme_scoase` — urma ar rămâne scrisă și necitită")


def test_auditul_nu_mai_produce_orfani_dupa_stergere():
    """[R79] Instanța: rândul de audit al cererii `DELETE` se scrie la ~78 ms **după** ce firma a
    dispărut — deci trimitea la o firmă inexistentă. Fiecare firmă scoasă lăsa exact un orfan.

    Reparat printr-o **sub-interogare** în chiar `INSERT`-ul care exista deja: `tenant_id` devine
    `NULL` când firma nu mai e, în același statement, fără drum dus-întors.

    De ce nu cheie străină cu `ON DELETE SET NULL` — măsurat 27.08, în ambele forme de coloană:
    pe cele **10** tabele cu `tenant_id NOT NULL` ar face ștergerea **imposibilă**
    (`NotNullViolation`), iar pe cele nullable ar **respinge** rândul de după ștergere, nu l-ar
    trece pe NULL: linia de audit ar **dispărea**, nu ar rămâne orfană.
    """
    sursa = io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    inserturi = [s for s in _sql_executat(ast.parse(sursa))
                 if s.startswith("INSERT INTO public.audit_log")]
    assert inserturi, "n-am găsit niciun INSERT în audit_log"
    fara_gard = [s[:90] for s in inserturi
                 if s.count("tenant_id") and not s.count("SELECT id FROM public.tenants WHERE id")]
    assert not fara_gard, (
        "scrieri în `audit_log` cu `tenant_id` direct, fără sub-interogarea care îl trece pe NULL "
        "când firma nu mai există:\n  %s\nFiecare ștergere ar lăsa din nou un orfan."
        % "\n  ".join(fara_gard))


# [R79 · G1] Clichetul pe date al orfanilor. Se citește în AMÂNDOUĂ direcțiile — vezi docstringul.
_ORFANI_CUNOSCUTI = 69


def test_niciun_orfan_NOU_dupa_ultima_stergere():
    """Clichet pe date: orfanii nu mai cresc. 69 la 27.08, după cele două ștergeri reale ale lui
    Costin — dintre care 67 sunt de dinainte (firme dispărute prin SQL ad-hoc, vezi R50) și 2 sunt
    chiar cei produși de ștergere, înainte de reparație.

    **Cifra 69 nu e o măsură a sănătății, e o constantă istorică.** (Costin, 27.08 seara, la
    decizia de a-i lăsa pe loc.) Cei 67 s-au produs **în afara aplicației**, într-o fereastră care
    nu mai există; nu se curăță, fiindcă ștergerea lor ar șterge singura urmă că firmele alea au
    existat. Diferența față de R79: acolo orfanul se producea **de-acum înainte**, deci trebuia
    oprit la sursă.

    **Deci informația nu e totalul, ci creșterea.** Dacă testul ăsta devine roșu, nu înseamnă
    „baza e mai murdară cu unu" — înseamnă că **o cale nouă scrie iar o referință care moare
    înaintea ei**, și aia se caută, nu se ridică pragul.

    **[G1, 28.08.2026] Și în cealaltă direcție.** Costin: *„un contor care poate doar să crească nu
    e contor. O scădere neexplicată e la fel de suspectă ca o creștere."* Până azi aserțiunea era
    `n <= 69` — o scădere trecea neobservată. Iar aici scăderea e chiar cea care doare: cei 67 de
    dinainte sunt **singura urmă** că firmele alea au existat (de-aia s-a decis să rămână pe loc).
    Dacă dispar, ceva i-a șters — o curățare retroactivă nedecisă, un `DELETE` de mână, o migrare
    care a măturat mai mult decât spunea. **Un registru care se subțiază singur nu e o reparație, e
    o pierdere de probe.** Când scăderea e voită, se coboară `_ORFANI_CUNOSCUTI` **deliberat**, cu
    motivul scris — exact ca la orice clichet."""
    db.init_pool()
    per_tabel = {}
    with db.get_conn() as conn, conn.cursor() as cur:
        for tabel in ts.TABELE_TENANT:
            cur.execute('SELECT count(*) FROM public."%s" x WHERE x.tenant_id IS NOT NULL '
                        'AND NOT EXISTS (SELECT 1 FROM public.tenants p WHERE p.id=x.tenant_id)'
                        % tabel)
            per_tabel[tabel] = cur.fetchone()[0]
    assert len(per_tabel) == len(ts.TABELE_TENANT) and len(per_tabel) > 5, (
        "[anti-vacuu] s-au numărat doar %d tabele — cifra ar coborî fiindcă instrumentul vede mai "
        "puțin, nu fiindcă baza s-ar fi curățat" % len(per_tabel))
    n = sum(per_tabel.values())
    detaliu = ", ".join("%s=%d" % (t, k) for t, k in sorted(per_tabel.items()) if k)
    assert n <= _ORFANI_CUNOSCUTI, (
        "orfanii au crescut de la %d la %d — o cale scrie iar o referință care moare înaintea ei "
        "(%s)" % (_ORFANI_CUNOSCUTI, n, detaliu))
    assert n >= _ORFANI_CUNOSCUTI, (
        "orfanii au SCĂZUT de la %d la %d (%s). Nu e o veste bună până nu se spune cine i-a scos: "
        "cei 67 de dinainte sunt singura urmă că firmele alea au existat. Caută actul care i-a "
        "șters; dacă a fost voit, coboară `_ORFANI_CUNOSCUTI` cu motivul scris."
        % (_ORFANI_CUNOSCUTI, n, detaliu or "niciun tabel cu orfani"))


def test_tabela_de_urma_exista_in_baza():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM information_schema.tables
                       WHERE table_schema='public' AND table_name='firme_scoase'""")
        assert cur.fetchone()[0] == 1, (
            "`public.firme_scoase` lipsește — rulează `python3 -m core.migrare_firme_scoase`. "
            "Fără ea, prima ștergere crapă la mijloc.")


# ── [G3, 28.08.2026] `firme_scoase.schema_name` — singura referință prin NUME de schemă ──────
#
# CE S-A MĂSURAT (27.08.2026, pe date): numele de schemă **se reciclează**. `urmator_schema_name`
# ia `max(NNN)+1` peste firmele **vii**, deci când cea mai mare e ștearsă, maximul coboară și
# numărul se refolosește. Azi `public.firme_scoase` are trei rânduri, iar **două** poartă
# `schema_name = 'tenant_019'` — două firme diferite. `tenant_018` e acum schema unei firme **vii**.
#
# DE CE NU E PIERDUTĂ URMA: rândul rămâne dezambiguizat de `tenant_id`, care vine dintr-o secvență
# și **nu se reciclează niciodată**. Toate celelalte 14 coloane de legătură din `public` sunt
# `tenant_id integer`. Deci `schema_name` e **informativ** — scrie ce schemă a purtat firma atunci —
# și **nicio citire nu se cheiază pe el**.
#
# CE PĂZEȘTE GARDUL DE MAI JOS: apariția unei citiri care s-ar cheia pe el. Pe `schema_name` singur,
# `tenant_019` trimite la două firme diferite: o astfel de interogare ar întoarce rândul greșit,
# **fără nicio eroare**, și ar arăta exact ca una corectă.
# Cuvintele-cheie care GUVERNEAZĂ o poziție. `IN`, `NOT`, `EXISTS`, `LIKE` lipsesc **deliberat**:
# sunt operatori în interiorul unui predicat, iar mersul înapoi trebuie să treacă peste ei până la
# `WHERE`/`AND`/`ON`.
_PREDICAT = {"WHERE", "AND", "OR", "ON", "USING", "HAVING"}
_GUVERNEAZA = _PREDICAT | {"SELECT", "INSERT", "INTO", "VALUES", "SET", "FROM", "JOIN", "GROUP",
                           "ORDER", "BY", "LIMIT", "OFFSET", "RETURNING", "UPDATE", "DELETE",
                           "DISTINCT", "UNION", "EXCEPT", "INTERSECT", "WITH", "CASE", "WHEN",
                           "THEN", "ELSE", "END", "CONFLICT", "DO", "NOTHING"}


def _pozitia_lui(sql, cuvant):
    """Pozițiile în care `cuvant` apare ca **cheie de căutare** — adică guvernat de un cuvânt-cheie
    de predicat. Se merge înapoi peste operanzi și operatori până la primul cuvânt-cheie SQL:
    `ON a.s = f.schema_name` e cheie, `SELECT id, schema_name FROM …` nu e, iar
    `WHERE x IN (SELECT schema_name …)` nu e (îl guvernează `SELECT`-ul din interior).

    Se citește pe **jetoane**, nu pe subșiruri: un `nume_schema_name_vechi` nu e `schema_name`, iar
    numele calificat `f.schema_name` e **același** lucru cu `schema_name` — de-aia se compară ultimul
    segment.

    **Limita, scrisă aici fiindcă gardul nu e un parser de SQL:** nu urmărește domenii de vizibilitate
    și nu deosebește o sub-interogare corelată de una independentă. Ce poate spune e ce poziție are
    cuvântul în frază; calibrarea de mai jos îi ține amândouă direcțiile.
    """
    jetoane = re.findall(r"[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*", sql)
    gasite = []
    for i, j in enumerate(jetoane):
        if j.split(".")[-1] != cuvant:
            continue
        for k in range(i - 1, -1, -1):
            g = jetoane[k].upper()
            if g not in _GUVERNEAZA:
                continue
            if g in _PREDICAT:
                gasite.append(i)
            break
    return gasite


def _sql_de_productie():
    """SQL-urile literale din `main.py` + `core/*.py`, fara teste. Refoloseste `_sql_executat` —
    o a doua extragere de SQL in acelasi fisier ar fi chiar tiparul „regula in doua locuri"."""
    out = []
    for rel in ["main.py"] + ["core/" + f for f in sorted(os.listdir(os.path.join(_RAD, "core")))
                              if f.endswith(".py") and not f.startswith("test_")]:
        sursa = io.open(os.path.join(_RAD, rel), encoding="utf-8").read()
        try:
            arb = ast.parse(sursa)
        except SyntaxError:      # pragma: no cover
            continue
        for s in _sql_executat(arb):
            out.append((rel, s))
    return out


def test_nicio_citire_nu_se_cheiaza_pe_NUMELE_schemei():
    """[G3] `firme_scoase.schema_name` e informativ. O interogare care caută pe el ar întoarce
    rândul greșit fără nicio eroare, fiindcă numele se reciclează."""
    toate = _sql_de_productie()
    assert len(toate) > 200, ("[anti-vacuu] doar %d interogări citite — scanul nu vede codul"
                              % len(toate))
    ating = [(r, s) for r, s in toate if re.search(r"\bfirme_scoase\b", s)]
    assert ating, "[anti-vacuu] nicio interogare nu mai atinge `firme_scoase`"
    rele = [(r, s[:110]) for r, s in ating if _pozitia_lui(s, "schema_name")]
    assert not rele, (
        "citiri cheiate pe `firme_scoase.schema_name` (%d):\n  %s\n"
        "Numele de schemă se reciclează — azi `tenant_019` trimite la două firme diferite. "
        "Cheia stabilă e `tenant_id`."
        % (len(rele), "\n  ".join("%s: %s" % x for x in rele)))


def test_CALIBRARE_gardul_deosebeste_o_COLOANA_de_o_CHEIE():
    """Modul de eșec propriu construcției: un `\"schema_name\" in sql` ar fi raportat toate cele
    trei interogări de azi, care doar **scriu** sau **listează** coloana. Ambele direcții."""
    cheie = ("SELECT id FROM public.firme_scoase WHERE schema_name = %s",
             "SELECT a.id FROM public.firme_scoase f JOIN x a ON a.s = f.schema_name",
             "SELECT id FROM public.firme_scoase WHERE (schema_name = %s AND id > 0)")
    for s in cheie:
        assert _pozitia_lui(s, "schema_name"), "n-a văzut cheia în: %s" % s
    coloana = ("SELECT id, tenant_id, nume, schema_name, motiv FROM public.firme_scoase WHERE id=%s",
               "INSERT INTO public.firme_scoase (tenant_id, nume, schema_name) VALUES (%s,%s,%s)",
               "UPDATE public.firme_scoase SET randuri_sterse=%s WHERE id=%s",
               "SELECT id FROM public.firme_scoase WHERE tenant_id IN "
               "(SELECT schema_name FROM x)")
    for s in coloana:
        assert not _pozitia_lui(s, "schema_name"), "a raportat pe nedrept: %s" % s


# ── [R79/T1, 28.08.2026] Numele de schemă nu se mai reciclează ───────────────
#
# DECIZIA lui Costin: *„oprim reciclarea numelui de schemă."* Contorul e o secvență Postgres,
# pornită de la **maximul istoric** (firme vii ∪ `firme_scoase` ∪ schemele din bază), nu de la cel
# viu — altfel primul nume generat ar fi fost chiar unul deja folosit de o firmă scoasă.
#
# CE FACE IMPOSIBIL: întoarcerea la `max(existente)+1`, dispariția secvenței, și o secvență rămasă
# în urma bazei (care ar produce o coliziune tăcută la următoarea firmă).
_SECVENTA = "public.tenant_schema_seq"


def test_contorul_NU_se_mai_calculeaza_din_firmele_vii():
    """Structural, pe AST: `urmator_schema_name` cheamă `nextval` și **nu** mai citește lista de
    scheme existente. Un `max(…)+1` reintrodus ar aduce înapoi reciclarea, iar suita ar fi verde:
    ea testează ce se întâmplă la ștergere, nu cum se alege numele următor."""
    from core import tenant_provisioning as tp
    sursa = io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()
    arb = ast.parse(sursa)
    fn = next(n for n in ast.walk(arb)
              if isinstance(n, ast.FunctionDef) and n.name == "urmator_schema_name")
    sql = " | ".join(_sql_executat(fn))
    assert re.search(r"\bnextval\b", sql), (
        "`urmator_schema_name` nu mai cheamă `nextval`: %s" % sql)
    assert not re.search(r"SELECT\s+schema_name\s+FROM\s+public\.tenants", sql, re.I), (
        "contorul citește iar firmele vii — de acolo venea reciclarea")
    assert not [n for n in ast.walk(fn)
                if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "max"], (
        "a reapărut un `max(…)` în calculul numelui de schemă")
    assert tp.SECVENTA_SCHEMA == _SECVENTA


def test_provizionarea_ia_numele_din_contor():
    fn = next(n for n in ast.walk(ast.parse(io.open(
        os.path.join(_RAD, "core", "tenant_provisioning.py"), encoding="utf-8").read()))
        if isinstance(n, ast.FunctionDef) and n.name == "provision_tenant")
    apeluri = {c.func.id for c in ast.walk(fn)
               if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    assert apeluri >= {"urmator_schema_name"}, (
        "`provision_tenant` nu mai ia numele din contor: %s" % sorted(apeluri))


def test_CALIBRARE_formatorul_e_pur_si_nu_mai_stie_de_lista():
    """Ce a rămas pur, a rămas pur — și nu mai poate primi o listă din greșeală."""
    from core import tenant_provisioning as tp
    assert tp.formeaza_schema_name(7) == "tenant_007"
    assert tp.formeaza_schema_name(20) == "tenant_020"
    assert tp.formeaza_schema_name(1234) == "tenant_1234"


def test_contorul_exista_si_nu_a_ramas_in_urma_bazei():
    """Pe date. O secvență în urma maximului istoric ar produce, la următoarea firmă, un nume care
    există deja — adică reciclarea, prin altă ușă."""
    from core.migrare_schema_seq import maxim_istoric
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM information_schema.sequences "
                        "WHERE sequence_schema='public' AND sequence_name='tenant_schema_seq'")
            assert cur.fetchone()[0] == 1, (
                "secvența %s lipsește — rulează `python3 -m core.migrare_schema_seq`" % _SECVENTA)
            cur.execute("SELECT last_value, is_called FROM %s" % _SECVENTA)
            last, chemat = cur.fetchone()
        curent = last if chemat else last - 1
        istoric = maxim_istoric(conn)
    assert curent >= istoric, (
        "contorul e la %d, iar maximul istoric e %d — următoarea firmă ar primi un nume deja "
        "folosit. Rulează `python3 -m core.migrare_schema_seq`." % (curent, istoric))
