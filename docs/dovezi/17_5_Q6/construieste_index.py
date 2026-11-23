# -*- coding: utf-8 -*-
"""17.5-Q6 — index_matrice.tsv din martorii colectați pe E și pe C (protocol §2, formatul index_matrice_model.tsv).
    python construieste_index.py RAD_DOVEZI DIR_E DIR_C SHA_E SHA_C MOTIVE.tsv IESIRE.tsv
DIR_E / DIR_C sunt directoare RELATIVE la RAD_DOVEZI, cu fișierele colectorului (masuri_/sursa_/captura_<scenariu>_<caz>_<rez>);
e.1 și e.2 vin din masuri.json al rulării dedicate a testului înghețat (DIR_*/e12/…), cu originalul scris de `extrage_e12`.
Starea fiecărui rând o dă predicatul livrat (oracol_reparatii / rezultat din testul înghețat) pe E și pe C: pică pe E și trece pe C = «reparat»;
trece pe ambele = «trece pe E»; trece pe E și pică pe C sau pică pe ambele = «deschis» (cu motivul cauzei); lipsă martor = rândul din MOTIVE.tsv
(stare + motiv). Nu scrie nimic în afara IESIRE."""
import csv
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oracol_reparatii_17_5_Q6 import judeca  # noqa: E402
from citeste_rezultat_Q6 import incarca_test  # noqa: E402

COL = "scenariu caz rezolutie stare motiv commit_E masuri_E sha256_masuri_E sursa_E sha256_sursa_E captura_E sha256_captura_E commit_C masuri_C sha256_masuri_C sursa_C sha256_sursa_C captura_C sha256_captura_C".split()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tabel(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def verdict(scenariu, m):
    if scenariu in ("e.1", "e.2"):
        return bool(incarca_test().rezultat(scenariu, m))
    return bool(judeca(scenariu, m))


def main(rad, dir_e, dir_c, sha_e, sha_c, motive, iesire):
    rad = Path(rad)
    matrice = Path(__file__).with_name("matrice_probe_17_5_Q6.tsv")
    chei = [(r["scenariu"], caz, rez) for r in tabel(matrice) for caz in r["cazuri"].split(",") for rez in r["rezolutii"].split(",")]
    mot = {(r["scenariu"], r["caz"], r["rezolutie"]): r for r in tabel(motive)}
    randuri = []
    for (sc, caz, rez) in chei:
        k = f"{sc}_{caz}_{rez}"
        rand = dict.fromkeys(COL, "")
        rand.update(scenariu=sc, caz=caz, rezolutie=rez)
        faze = {}
        for faza, d, commit in (("E", dir_e, sha_e), ("C", dir_c, sha_c)):
            m, s = rad / d / f"masuri_{k}.json", rad / d / f"sursa_{k}.json"
            cap = rad / d / f"captura_{k}.png"
            if m.is_file() and s.is_file() and cap.is_file():
                faze[faza] = (commit, m, s, cap)
        if set(faze) == {"E", "C"}:
            rez_v = {f: verdict(sc, json.loads(faze[f][1].read_text(encoding="utf-8"))) for f in faze}
            for f, (commit, m, s, cap) in faze.items():
                rand.update({f"commit_{f}": commit, f"masuri_{f}": str(m.relative_to(rad)), f"sha256_masuri_{f}": sha(m),
                             f"sursa_{f}": str(s.relative_to(rad)), f"sha256_sursa_{f}": sha(s),
                             f"captura_{f}": str(cap.relative_to(rad)), f"sha256_captura_{f}": sha(cap)})
            if not rez_v["E"] and rez_v["C"]:
                rand["stare"] = "reparat"
            elif rez_v["E"] and rez_v["C"]:
                rand["stare"] = "trece pe E"
            else:
                rand["stare"] = "deschis"
                rand["motiv"] = (mot.get((sc, caz, rez)) or {}).get("motiv") or ("predicatul pică pe C (E %s, C pică)" % ("trece" if rez_v["E"] else "pică"))
                for c in COL[5:]:
                    rand[c] = ""
        else:
            m = mot.get((sc, caz, rez))
            if not m:
                raise SystemExit(f"fără martor și fără motiv: {sc} {caz} {rez}")
            rand.update(stare=m["stare"], motiv=m["motiv"])
        randuri.append(rand)
    with open(iesire, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COL, delimiter="\t")
        w.writeheader()
        w.writerows(randuri)
    st = {}
    for r in randuri:
        st[r["stare"]] = st.get(r["stare"], 0) + 1
    print(json.dumps(st, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 8:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
