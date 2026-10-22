"""
core/migrare_curs_precizie.py — cursul BNR se păstrează cu precizia dată de BNR (lotul 11, deficiența C88, găsită la 460).

DEFECTUL: coloanele de curs aveau 4 zecimale (`public.curs_bnr_zilnic.curs`, `facturi.curs_bnr`, `reevaluari_valuta.curs_vechi` /
`curs_nou` — numeric(12,4); `rip_operatiuni.curs_valutar` — numeric(10,4)). BNR cotează cinci monede la 100 de
unități (`<Rate currency="HUF" multiplier="100">1.4719</Rate>`), iar cursul pe unitate e valoarea / multiplicatorul (`curs_bnr.parse_xml`):
HUF 1,4719 / 100 = 0,014719 — coloana îl rotunjea la 0,0147. IDR 0,0256 / 100 = 0,000256 devenea 0,0003 (+17%).

MĂSURAT pe arhivele BNR (`curs.bnr.ro/files/xml/years/nbrfxrates2024/2025/2026.xml`, 22.10.2026): monedele cu `multiplier="100"` sunt
exact HUF, IDR, ISK, JPY, KRW (toți trei anii); valoarea din XML are cel mult 4 zecimale, deci cursul pe unitate cel mult 6; cel mai mic
curs pe unitate e IDR 0,00025 (2026); partea întreagă are cel mult 3 cifre (XAU). Pe baza de test, 1001 valori din cache difereau de
arhivă, toate rotunjirea la 4 zecimale a valorii exacte (HUF 200, IDR 202, ISK 200, JPY 198, KRW 201).

TIPUL NOU: `numeric` fără scală fixă — păstrează valoarea EXACT cum a fost scrisă: EUR rămâne 5.2409 (patru zecimale, cum îl dă BNR), HUF
devine 0.014719. `numeric(16,6)` ar fi cerut-o la fel de bine pentru BNR, dar ar fi umplut cu zerouri fiecare curs de 4 zecimale (5.240900)
în orice citire ca text (rapoarte, mesaje, teste), adică ar fi schimbat cum arată cursurile care erau deja corecte. Același tip îl are deja
`d301_operatiuni.curs`. Lărgirea `numeric(p,s)` -> `numeric` nu rescrie tabela (PostgreSQL: conversie binar-compatibilă).

DATELE:
  - cache-ul public (`public.curs_bnr_zilnic`, date BNR publice): valorile rotunjite se refac din arhiva anuală BNR — numai rândurile a căror
    valoare e EXACT rotunjirea la 4 zecimale a valorii din arhivă. Orice altă diferență (sau o zi absentă din arhivă) oprește migrarea pe
    cache, cu lista: o valoare care nu e a BNR nu se schimbă orbește. Arhiva nu se poate citi -> migrarea eșuează (se rulează din nou).
  - facturile / operațiunile / reevaluările deja înregistrate NU se recalculează: HG 1/2016 pct.35 alin.(2) — „cursul de schimb valutar
    utilizat [...] la data emiterii acestor facturi va rămâne neschimbat la data definitivării operațiunii”. Numai tipul coloanei se lărgește.

Idempotent: o coloană deja fără scală (sau cu scală >= 6) nu se atinge; o valoare deja exactă nu se rescrie. Sursa UNICĂ a structurii =
mirror în `tenant_template.sql` și `infra/bootstrap_public.sql`.
Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_curs_precizie.py`.
"""
from decimal import Decimal, ROUND_HALF_UP

from core import curs_bnr as _cb
from core import db

#: (tabela, coloana) — coloanele de curs valutar. Garda: `core/test_lot11_c88_curs_precizie.py` (orice coloană `curs*` numerică din
#: șablon / bootstrap cu scală sub `curs_bnr.ZECIMALE_CURS` pică).
COLOANE_PUBLIC = (("curs_bnr_zilnic", "curs"),)
COLOANE_FIRMA = (("facturi", "curs_bnr"), ("rip_operatiuni", "curs_valutar"), ("reevaluari_valuta", "curs_vechi"),
                 ("reevaluari_valuta", "curs_nou"))
TIP = "numeric"
_PATRU = Decimal("0.0001")


def _scala(cur, schema, tabela, coloana):
    """(există, scala) — scala None = `numeric` fără scală fixă."""
    cur.execute("SELECT numeric_scale FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND column_name = %s",
                (schema, tabela, coloana))
    r = cur.fetchone()
    return (False, None) if r is None else (True, r[0])


def largeste(conn, schema, coloane):
    """Lărgește coloanele cu scală fixă sub `curs_bnr.ZECIMALE_CURS` la `numeric`. -> [„tabela.coloana”] lărgite acum."""
    if schema != "public" and not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    facute = []
    with conn.cursor() as cur:
        for tabela, coloana in coloane:
            exista, scala = _scala(cur, schema, tabela, coloana)
            if not exista or scala is None or scala >= _cb.ZECIMALE_CURS:
                continue
            cur.execute('ALTER TABLE "%s".%s ALTER COLUMN %s TYPE %s' % (schema, tabela, coloana, TIP))
            facute.append("%s.%s" % (tabela, coloana))
    return facute


def ani_in_cache(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT extract(year FROM data)::int FROM public.curs_bnr_zilnic ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def arhive(ani, descarca=None):
    """{an: harta} — arhiva anuală BNR a fiecărui an, citită FĂRĂ nicio conexiune în mână. Rețea / format: ridică (migrarea se rulează
    din nou)."""
    descarca = descarca or _cb._descarca
    return {an: _cb.parse_xml(descarca(_cb.URL_AN.format(an=an))) for an in ani}


def refa_cache(conn, harti, ani=None):
    """Reface din arhivele BNR `harti` ({an: harta}, `arhive`) valorile cache-ului rotunjite la 4 zecimale, pe anii `ani` (implicit: toți
    anii din cache). -> {"refacute": n, "pe_moneda": {...}, "ani": [...]}. Ridică `ValueError` cu lista dacă o valoare din cache nu e nici
    cea din arhivă, nici rotunjirea ei, sau dacă un an n-are arhivă (nu se schimbă nimic)."""
    ani = ani_in_cache(conn) if ani is None else list(ani)
    fara = [an for an in ani if an not in harti]
    if fara:
        raise ValueError("cache-ul BNR are ani fără arhivă citită: %s" % fara)
    de_refacut, straine = [], []
    for an in ani:
        harta = harti[an]
        with conn.cursor() as cur:
            cur.execute("SELECT data, moneda, curs FROM public.curs_bnr_zilnic WHERE data BETWEEN %s AND %s ORDER BY data, moneda",
                        ("%d-01-01" % an, "%d-12-31" % an))
            for d, mon, v in cur.fetchall():
                exact = harta.get(d, {}).get(mon)
                if exact is not None and v == exact:
                    continue
                if exact is not None and v == exact.quantize(_PATRU, rounding=ROUND_HALF_UP):
                    de_refacut.append((d, mon, exact))
                else:
                    straine.append("%s %s: în cache %s, în arhiva BNR %s" % (d.isoformat(), mon, v, exact if exact is not None else "lipsă"))
    if straine:
        from core.common import cate as _cate
        raise ValueError("cache-ul BNR are %s care nu sunt ale arhivei BNR (nici rotunjirea lor la 4 zecimale) — nu se schimbă "
                         "nimic: %s" % (_cate(len(straine), "valoare", "valori"), "; ".join(straine[:20])))
    pe_moneda = {}
    with conn.cursor() as cur:
        for d, mon, exact in de_refacut:
            cur.execute("UPDATE public.curs_bnr_zilnic SET curs = %s WHERE data = %s AND moneda = %s", (exact, d, mon))
            pe_moneda[mon] = pe_moneda.get(mon, 0) + 1
    return {"refacute": len(de_refacut), "pe_moneda": dict(sorted(pe_moneda.items())), "ani": ani}


def aplica(conn, schema):
    """Coloanele firmei `schema` lărgite (datele existente neatinse — HG 1/2016 pct.35 alin.(2))."""
    return largeste(conn, schema, COLOANE_FIRMA)


def verifica(conn, schema):
    with conn.cursor() as cur:
        for tabela, coloana in COLOANE_FIRMA:
            exista, scala = _scala(cur, schema, tabela, coloana)
            if exista and scala is not None and scala < _cb.ZECIMALE_CURS:
                return False
    return True


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        ani = ani_in_cache(conn)
    harti = arhive(ani)                                   # descărcarea, fără conexiune în mână
    with db.get_conn() as conn:
        largite = largeste(conn, "public", COLOANE_PUBLIC)
        rez = refa_cache(conn, harti)
        conn.commit()
    print("migrare_curs_precizie: public %s; cache BNR refăcut din arhivă: %d valori %s (anii %s)"
          % (", ".join(largite) or "deja lărgit", rez["refacute"], rez["pe_moneda"], rez["ani"]))
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, coloane = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                coloane += len(aplica(conn, s))
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_curs_precizie: %d firme ok (%d coloane lărgite), %d esec" % (ok, coloane, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
