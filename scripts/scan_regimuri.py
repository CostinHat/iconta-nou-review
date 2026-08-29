# -*- coding: utf-8 -*-
"""CÂTE REGIMURI FISCALE EXERCITĂ PORTOFOLIUL — prima operațiune din E1 (1a), 29.08.2026.

DE CE EXISTĂ. `PLAN_INVESTIGATII.md`, faza 1a, o cere textual: *„Pe regimurile REALE, nu pe trei
alese arbitrar. **Prima operațiune din E1 e să afli câte sunt** — micro/profit · plătitor/neplătitor
de TVA · lunar/trimestrial · plus cele speciale."* Iar criteriul de terminare al lui E1, din antetul
registrului, cere lista artefactelor **pe regimurile reale**. Până azi, cifra n-a fost măsurată
niciodată: planul o cerea ca primul pas, iar lucrul a mers mai departe fără ea.

CE E UN „REGIM", mecanic. Semnătura care schimbă **ce datorează** o firmă, din câmpuri declarate:
`regim_fiscal` (micro/real) · `platitor_tva` · `tip_decont` (L/T) · are salariați · `operatiuni_ic`.
Nu intră aici cele care schimbă **cum se calculează**, nu **ce se datorează** — `tva_la_incasare`,
`pro_rata`, `baza_contabila` — dar se numără separat, fiindcă tot schimbă artefactul.

REGIMURILE SPECIALE se citesc din DATE, nu din nume. Marja (turism art. 311 / second-hand art. 312)
n-are câmp pe profil: `main.jurnal_marja` o recunoaște după **marcajul din descrierea notei**, deci
acolo se caută. Taxarea inversă se citește din `facturi.taxare_inversa`. *Un regim al cărui modul
există dar pe care nicio firmă nu-l exercită e chiar semnalul cerut de plan: „există modulul" nu e
„produce artefactul".*

CE NU POATE MĂSURA, declarat: **agricultorul forfetar** și **construcțiile** n-au niciun marcaj — nici
câmp pe profil, nici marker în note. Nu se pot număra, și se spune; a le raporta „0" ar fi un zero
care nu deosebește „nicio firmă" de „nu știu să caut".

    ./venv/bin/python scripts/scan_regimuri.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db  # noqa: E402
from core.common import perioada_tva_tip  # noqa: E402

# Dimensiunile care schimbă CE se datorează — deci care fac un regim.
DIMENSIUNI = ("regim_fiscal", "platitor_tva", "tip_decont", "cu_salariati", "operatiuni_ic")
# Dimensiuni care schimbă CUM se calculează, nu ce se datorează. Numărate separat.
MODIFICATORI = ("tva_la_incasare", "pro_rata", "baza_contabila")
# Regimuri speciale și marcajul lor în date. `None` = nu există marcaj (nu se poate număra).
SPECIALE = {
    "marjă turism (art. 311)": ("nota", "art. 311"),
    "marjă second-hand (art. 312)": ("nota", "art. 312"),
    "taxare inversă (art. 331)": ("factura", None),
    "agricultor forfetar": (None, None),
    "construcții": (None, None),
}


def _profil(cur, schema):
    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, tva_la_incasare, "
                "pro_rata, baza_contabila FROM %s.firma_profil WHERE id=1" % schema)
    r = cur.fetchone()
    if not r:
        return None
    return dict(zip(("regim_fiscal", "platitor_tva", "tip_decont", "operatiuni_ic",
                     "tva_la_incasare", "pro_rata", "baza_contabila"), r))


def _numara(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]


def aduna(conn):
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name, nume FROM public.tenants WHERE activ ORDER BY schema_name")
        firme = cur.fetchall()
    for schema, nume in firme:
        with conn.cursor() as cur:
            try:
                p = _profil(cur, schema)
                if p is None:
                    conn.rollback()
                    out.append((schema, nume, None, {}))
                    continue
                p["cu_salariati"] = _numara(
                    cur, "SELECT COUNT(*) FROM %s.salariati" % schema) > 0
                special = {}
                for et, (unde, marker) in SPECIALE.items():
                    if unde == "nota":
                        special[et] = _numara(
                            cur, "SELECT COUNT(*) FROM %s.inregistrari WHERE descriere ILIKE '%%%s%%'"
                                 % (schema, marker))
                    elif unde == "factura":
                        special[et] = _numara(
                            cur, "SELECT COUNT(*) FROM %s.facturi WHERE taxare_inversa" % schema)
                    else:
                        special[et] = None
            except Exception as e:
                conn.rollback()
                out.append((schema, nume, "EROARE: %s" % str(e)[:60], {}))
                continue
        out.append((schema, nume, p, special))
    return out


def _decont(p):
    """Periodicitatea, NORMALIZATĂ prin sursa unică de parsare a codului.

    În date există patru scrieri pentru două lucruri — `L`, `lunar`, `T`, `trimestrial` —, moștenite
    din seeduri. **Nu e un defect**: `core.common.perioada_tva_tip` le parsează pe toate, iar
    motoarele fiscale trec prin ea. Prima formă a scanului le număra brut și raporta două firme cu
    aceeași periodicitate ca două regimuri diferite — o naivitate a instrumentului, nu a aplicației."""
    try:
        return perioada_tva_tip(p)
    except ValueError:
        return None


def semnatura(p):
    val = dict(p)
    val["tip_decont"] = _decont(p)
    return tuple("%s=%s" % (d, val.get(d)) for d in DIMENSIUNI)


def ruleaza():
    db.init_pool()
    with db.get_conn() as conn:
        lot = aduna(conn)
    assert lot, "domeniul e gol — nicio firmă activă"

    print("FIRME ACTIVE: %d\n" % len(lot))
    print("%-12s %-30s %-7s %-5s %-4s %-5s %-4s" % ("schemă", "firmă", "regim", "TVA", "dec",
                                                    "salar", "IC"))
    semnaturi, incomplete = {}, []
    for schema, nume, p, _s in lot:
        if not isinstance(p, dict):
            print("%-12s %-30s  %s" % (schema, (nume or "")[:30], p or "FĂRĂ PROFIL"))
            incomplete.append((schema, "fără profil"))
            continue
        print("%-12s %-30s %-7s %-5s %-4s %-5s %-4s"
              % (schema, (nume or "")[:30], p["regim_fiscal"], p["platitor_tva"], p["tip_decont"],
                 p["cu_salariati"], p["operatiuni_ic"]))
        lipsa = [d for d in DIMENSIUNI if p.get(d) is None]
        if lipsa:
            incomplete.append((schema, "dimensiuni nedeclarate: %s" % ", ".join(lipsa)))
        semnaturi.setdefault(semnatura(p), []).append(schema)

    brute = {}
    for _sc, _n, p, _s in lot:
        if isinstance(p, dict):
            brute.setdefault(tuple("%s=%s" % (d, p.get(d)) for d in DIMENSIUNI), []).append(1)
    print("\n═══ REGIMURI REALE (semnături distincte, periodicitatea NORMALIZATĂ): %d"
          % len(semnaturi))
    print("    *(pe scrierea BRUTĂ din bază ar ieși %d — diferența e vocabularul `L`/`lunar`,"
          % len(brute))
    print("      parsat corect de `common.perioada_tva_tip`. Nu e un regim în plus, e o scriere"
          " în plus.)*")
    for s, firme in sorted(semnaturi.items(), key=lambda x: (-len(x[1]), x[0])):
        print("  %2d firme · %s" % (len(firme), " · ".join(s)))
        print("            %s" % ", ".join(firme))

    print("\n═══ PROFILE INCOMPLETE — o dimensiune nedeclarată înseamnă că aplicația NU poate ști")
    print("    ce datorează firma: %d" % len(incomplete))
    for schema, ce in incomplete:
        print("  %-12s %s" % (schema, ce))

    print("\n═══ MODIFICATORI (schimbă CUM se calculează, nu CE se datorează)")
    for d in MODIFICATORI:
        n = sum(1 for _s, _n, p, _x in lot if isinstance(p, dict) and p.get(d))
        print("  %-18s pe %d firme" % (d, n))

    print("\n═══ REGIMURI SPECIALE — citite din DATE, nu din numele firmei")
    for et in SPECIALE:
        val = [s.get(et) for _sc, _n, p, s in lot if isinstance(p, dict)]
        if all(v is None for v in val):
            print("  %-30s NU SE POATE NUMĂRA — niciun marcaj în date (nici câmp, nici marker)"
                  % et)
            continue
        firme = [sc for sc, _n, p, s in lot if isinstance(p, dict) and (s.get(et) or 0) > 0]
        print("  %-30s %d firme%s" % (et, len(firme), (" — %s" % ", ".join(firme)) if firme else
                                      "  ← MODUL FĂRĂ FIRMĂ EXERCITATĂ (semnalul cerut de plan)"))
    return semnaturi, incomplete


if __name__ == "__main__":
    ruleaza()
