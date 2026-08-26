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

import pytest

from core import db, tenant_stergere as ts

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _arbore(modul):
    return ast.parse(io.open(os.path.join(_RAD, "core", modul + ".py"), encoding="utf-8").read())


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
    assert ordine == ["urma", "public", "schema", "rand"], (
        "ordinea operațiilor din `sterge` nu mai e cea cerută: %s" % ordine)


def test_tabela_de_urma_exista_in_baza():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM information_schema.tables
                       WHERE table_schema='public' AND table_name='firme_scoase'""")
        assert cur.fetchone()[0] == 1, (
            "`public.firme_scoase` lipsește — rulează `python3 -m core.migrare_firme_scoase`. "
            "Fără ea, prima ștergere crapă la mijloc.")
