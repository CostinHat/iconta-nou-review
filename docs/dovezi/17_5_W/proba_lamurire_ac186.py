# -*- coding: utf-8 -*-
"""[17.5-W, AC186] Lămurirea a două cifre din analiza poziției «F031» (D300 10/2026, F1 Comert Stoc SRL, tenant_9049): R10 = 99 și factura F1A13
fără notă. NUMAI CITIRE (tranzacție READ ONLY), pe baza de test restaurată; nu repară nimic.

  ./venv/bin/python docs/dovezi/17_5_W/proba_lamurire_ac186.py > docs/dovezi/17_5_W/lamurire_ac186.txt

Tipărește: (a) R10_1 / R10_2 ale D300 pe 10/2026 și, pe fiecare sursă de TVA la 11%, ce intră în decont (facturile emise din `select_facturi_4`,
rapoartele Z validate din `select_rapoarte_z`, F1A13 cu clauza `_nu_din_bon`); (b) pentru F1A13: bon_fiscal_nr, numărul notelor, `e_din_bon_fiscal`, motivul
refuzului de contare (EMISA_DIN_BON) și căutarea facturilor emise fără bon și fără notă în octombrie 2026 (0 așteptat) și în tot schema (o singură
așteptată: soldul preluat, status importata)."""
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RAD)
for linie in open(os.path.expanduser("~/.iconta/test.env"), encoding="utf-8"):   # conexiunea de test; nimic din ea nu se tipărește
    m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$", linie)
    if m:
        os.environ[m.group(1)] = m.group(2).strip().strip("'\"")

import psycopg2.extras as _E  # noqa: E402

from core import d300 as _d300, db as _db, facturi as _fc, repo_d300 as _repo  # noqa: E402
from core.common import Perioada  # noqa: E402
from core.raport_z import SURSE as _SURSE_Z  # noqa: E402

SCHEMA = "tenant_9049"
DE, PANA = "2026-10-01", "2026-11-01"
F1A13_ID = 64


def _tva_11(baza):
    return (Decimal(str(baza)) * Decimal("0.11")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def main():
    _db.init_pool()
    with _db.get_conn(SCHEMA) as conn:
        cur0 = conn.cursor()
        cur0.execute("SET TRANSACTION READ ONLY")
        print("== AC186 — lămurire (numai citire, tranzacție READ ONLY, %s, fereastra %s … %s) ==" % (SCHEMA, DE, PANA))

        # (a) R10 al D300 pe 10/2026
        _xml, res = _d300.genereaza(conn, SCHEMA, Perioada(2026, luna=10))
        r = res.R
        print("\n(a) D300 10/2026 (core/d300.py, genereaza): R10_1 = %s, R10_2 = %s" % (r.get("R10_1"), r.get("R10_2")))
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            facturi = {}
            for x in _repo.select_facturi_4(cur, _d300._STATUS_FINAL, _d300._exig_d300(), DE, PANA):
                if x["directie"] == "emisa" and x["cota_tva"] is not None and Decimal(str(x["cota_tva"])) == 11:
                    baza = x["valoare_neta"] if x["valoare_neta"] is not None else Decimal(str(x["cantitate"])) * Decimal(str(x["pret_unitar"]))
                    f = facturi.setdefault(x["id"], {"numar": x["numar"], "baza": Decimal(0), "tva": Decimal(0)})
                    f["baza"] += Decimal(str(baza))
                    f["tva"] += _tva_11(baza)
            print("  facturi emise care INTRĂ în decont (select_facturi_4, `_nu_din_bon(\"f\")`), linii cu cota 11%:")
            for fid, f in sorted(facturi.items()):
                print("    id %s, nr. %s: baza %s, TVA 11%% %s" % (fid, f["numar"], f["baza"], f["tva"]))
            if not facturi:
                print("    (niciuna)")
            z11 = {}
            for x in _repo.select_rapoarte_z(cur, _SURSE_Z, DE, PANA):
                if x["cota"] is not None and Decimal(str(x["cota"])) == 11:
                    z11[x["numar"]] = (x["data"].isoformat(), Decimal(str(x["baza"])), Decimal(str(x["tva"])))
            print("  rapoarte Z VALIDATE cu cota 11% care intră în decont (select_rapoarte_z):")
            for numar, (data, baza, tva) in sorted(z11.items()):
                print("    %s din %s: baza %s, TVA 11%% %s" % (numar, data, baza, tva))
            if not z11:
                print("    (niciunul)")
            cur.execute("SELECT id, numar, bon_fiscal_nr, directie, tip, status, data_emitere, total, tva FROM facturi WHERE id = %s", (F1A13_ID,))
            f13 = cur.fetchone()
            ids_intra = set(facturi)
            print("  F1A13 (id %s) intră în D300: %s (clauza `_nu_din_bon`: bon_fiscal_nr IS NULL; are bon_fiscal_nr = %r)" % (
                F1A13_ID, "DA" if F1A13_ID in ids_intra else "NU", f13["bon_fiscal_nr"]))
            print("  suma TVA 11%% din decont (facturi + Z validate) = %s; baza facturilor la 11%% = %s" % (
                sum((f["tva"] for f in facturi.values()), Decimal(0)) + sum((v[2] for v in z11.values()), Decimal(0)),
                sum((f["baza"] for f in facturi.values()), Decimal(0))))
            print("  Z-8000000001-0050 intră în decont: %s; Z-8000000001-0042 (în ciornă) intră: %s" % (
                "DA" if "Z-8000000001-0050" in z11 else "NU", "DA" if "Z-8000000001-0042" in z11 else "NU"))
            cur.execute("SELECT numar, data, status, (SELECT tva FROM rapoarte_z_cote z WHERE z.inregistrare_id = i.id AND z.cota = 11) AS tva_11 "
                        "FROM inregistrari i WHERE i.sursa = ANY(%s) AND i.data >= %s AND i.data < %s ORDER BY i.data, i.numar", (list(_SURSE_Z), DE, PANA))
            print("  toate rapoartele Z din octombrie 2026 (număr, data, starea notei, TVA 11%):")
            for x in cur.fetchall():
                print("    %s  %s  %s  %s" % (x["numar"], x["data"], x["status"], x["tva_11"]))

            # (b) F1A13
            print("\n(b) F1A13 (id %s): număr %s, tip %s, status %s, emisă la %s, total %s, TVA %s, directie %s, bon_fiscal_nr = %r" % (
                F1A13_ID, f13["numar"], f13["tip"], f13["status"], f13["data_emitere"], f13["total"], f13["tva"], f13["directie"], f13["bon_fiscal_nr"]))
            cur.execute("SELECT count(*) AS n FROM inregistrari WHERE factura_id = %s", (F1A13_ID,))
            print("  note cu factura_id = %s: %s" % (F1A13_ID, cur.fetchone()["n"]))
            print("  core.facturi.e_din_bon_fiscal(F1A13) = %s" % _fc.e_din_bon_fiscal(dict(f13)))
            print("  motivul refuzului de contare (core/contare_facturi.py, RefuzContare EMISA_DIN_BON): factura e emisă pe baza bonului fiscal %s — "
                  "vânzarea e deja înregistrată din raportul Z, deci nu primește o a doua notă de vânzare" % _fc.mentiune_bon(dict(f13)))
            cur.execute("SELECT f.id, f.numar, f.tip, f.status, f.data_emitere FROM facturi f WHERE f.directie = 'emisa' AND f.bon_fiscal_nr IS NULL "
                        "AND NOT EXISTS (SELECT 1 FROM inregistrari i WHERE i.factura_id = f.id) AND f.data_emitere >= %s AND f.data_emitere < %s "
                        "ORDER BY f.id", (DE, PANA))
            gol = cur.fetchall()
            print("  facturi emise FĂRĂ bon_fiscal_nr și FĂRĂ notă, cu data_emitere în octombrie 2026: %d (0 așteptat)" % len(gol))
            for x in gol:
                print("    id %s nr. %s tip %s status %s din %s" % (x["id"], x["numar"], x["tip"], x["status"], x["data_emitere"]))
            cur.execute("SELECT f.id, f.numar, f.tip, f.status, f.data_emitere FROM facturi f WHERE f.directie = 'emisa' AND f.bon_fiscal_nr IS NULL "
                        "AND NOT EXISTS (SELECT 1 FROM inregistrari i WHERE i.factura_id = f.id) ORDER BY f.id")
            toata = cur.fetchall()
            print("  în tot schema (orice dată): %d: %s (un sold preluat, status importata, e așteptat și nu e eroare)" % (
                len(toata), "; ".join("id %s nr. %r tip %s status %s din %s" % (x["id"], x["numar"], x["tip"], x["status"], x["data_emitere"]) for x in toata)))

            # concluzia mecanică
            r10 = Decimal(str(r.get("R10_2") or 0))
            din_surse = sum((f["tva"] for f in facturi.values()), Decimal(0)) + sum((v[2] for v in z11.values()), Decimal(0))
            print("\nVerificări mecanice:")
            tva_f = sum((f["tva"] for f in facturi.values()), Decimal(0))
            tva_z = sum((v[2] for v in z11.values()), Decimal(0))
            print("  [1] R10_2 = %s; TVA 11%% din facturile care intră + TVA 11%% din Z validate = %s + %s = %s, rotunjit la leu = %s" % (
                r10, tva_f, tva_z, tva_f + tva_z, din_surse.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
            print("  [2] F1A13 intră și în D300 (dublă numărare cu un raport Z): %s" % ("DA" if F1A13_ID in ids_intra else "NU"))
            print("  [3] factură emisă fără bon și fără notă în octombrie 2026: %d" % len(gol))
            print("  [4] limita: schema nu leagă un bon fiscal de un raport Z (nu există coloană): de care raport Z ține bonul %s nu se poate stabili din date." % f13["bon_fiscal_nr"])
            eroare = (F1A13_ID in ids_intra) or bool(gol) or (din_surse.quantize(Decimal("1"), rounding=ROUND_HALF_UP) != r10)
            print("\nConcluzie: %s" % ("eroare de cod (vezi verificările [1], [2] și [3])" if eroare else
                                       "lămurit: comportament prin decizia A, nu eroare"))


if __name__ == "__main__":
    main()
