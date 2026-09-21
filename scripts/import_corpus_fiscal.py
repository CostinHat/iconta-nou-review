# -*- coding: utf-8 -*-
"""scripts/import_corpus_fiscal.py — aduce actele din corpusul FISCAL urcat în anaf_surse/.

Decizie Costin 21.09.2026 (import TOT corpusul `import_fiscalos/active`): pentru fiecare poziție
a cărei identitate (tip, nr, an) se stabilește MECANIC din `opis_identity`, se copiază BYTES-II
OFICIALI (materialul principal, rol BASE/CUTOFF_VERSION, din `sources/<source_SHA256>.html` — NU
documentul canonic adaptat) în `anaf_surse/<tip>_<nr>_<an>.html`, cu:
  · `.sha256` sidecar (amprenta conținutului = verificarea din test_provenienta.test_un_act_adus_e_amprentat);
  · o intrare în `anaf_surse/PROVENIENTA.json` clasa ADUS, cu motiv structurat care păstrează
    proveniența VERIFICABILĂ: official_source (URL), accessed_at, POSITION_ID, V4_EVIDENCE.

NU importă:
  · pozițiile deja prezente în corpus (aceeași identitate SAU același nume de fișier) — fără dublură;
  · ordinele comune `nr1/nr2/an` — identitatea (tip,nr,an) nu se poate stabili mecanic; se RAPORTEAZĂ
    lista, nu se blochează lotul pe ele (decizie Costin).

Abort (fail-closed) dacă: conținutul copiat nu se potrivește cu source_SHA256 declarat, sau ar fi
byte-identic cu un fișier existent din corpus (ar aprinde test_niciun_act_nu_e_in_corpus_de_doua_ori).

  python -m scripts.import_corpus_fiscal            # DRY-RUN: doar raportează dispoziția
  python -m scripts.import_corpus_fiscal --scrie    # scrie fișierele + PROVENIENTA.json
"""
import hashlib
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA = os.path.join(RAD, "import_fiscalos", "active")
CORPUS = os.path.join(RAD, "anaf_surse")
PROV = os.path.join(CORPUS, "PROVENIENTA.json")

FAM = {"LEGE": "legea", "OUG": "oug", "OG": "og", "HG": "hg", "ORDIN": "ordin"}
PRINCIPAL = {"BASE", "CUTOFF_VERSION"}


def _sha256(cale):
    return hashlib.sha256(io.open(cale, "rb").read()).hexdigest()


def _manifest():
    return json.load(io.open(os.path.join(SURSA, "manifest.json"), encoding="utf-8"))


def _provenienta_act(pid):
    return json.load(io.open(os.path.join(SURSA, "provenance", pid + ".json"), encoding="utf-8"))


def _principal(pid):
    """Materialul principal (rol BASE/CUTOFF_VERSION, sursă .html) — bytes-ii oficiali ai actului."""
    for mm in _provenienta_act(pid)["materials"]:
        if mm.get("role") in PRINCIPAL and mm.get("source_path", "").endswith(".html"):
            return mm
    return None


def planifica():
    """(import, deja_prezente, ordine_comune, probleme) — dispoziția celor 71 de poziții.

    `import` = [{pid, opis, ident, target, src, source_sha, official_source, accessed_at, v4}]."""
    from core import ghid_poarta as gp
    existing_ident = gp.corpus_acte()
    existing_names = set(os.listdir(CORPUS))
    m = _manifest()
    imp, prezente, comune, probleme = [], [], [], []
    targets = {}
    for a in m["acts"]:
        pid = a["POSITION_ID"]
        opis = a["identity"].get("opis_identity", "").strip()
        mt = re.match(r"^([A-Z]+)\s+([\d/]+)$", opis)
        if not mt:
            probleme.append((pid, opis, "opis_identity neparsabil"))
            continue
        tip, nums = mt.group(1), mt.group(2).split("/")
        fam = FAM.get(tip)
        if not fam:
            probleme.append((pid, opis, "tip necunoscut"))
            continue
        if len(nums) != 2:
            comune.append((pid, opis))            # ordin comun nr1/nr2(/...)/an
            continue
        nr, an = nums
        ident = (fam, nr, an)
        princ = _principal(pid)
        if not princ:
            probleme.append((pid, opis, "fără material principal .html"))
            continue
        src = os.path.join(SURSA, "sources", princ["source_SHA256"] + ".html")
        if not os.path.exists(src):
            probleme.append((pid, opis, "sursa lipsă pe disc"))
            continue
        target = "%s_%s_%s.html" % (fam, nr, an)
        if ident in existing_ident or target in existing_names:
            prezente.append((pid, opis, ident))
            continue
        if target in targets:
            probleme.append((pid, opis, "coliziune de nume cu %s" % targets[target]))
            continue
        targets[target] = pid
        imp.append({"pid": pid, "opis": opis, "ident": ident, "target": target, "src": src,
                    "source_sha": princ["source_SHA256"],
                    "official_source": princ.get("official_source", ""),
                    "accessed_at": princ.get("accessed_at", ""),
                    "v4": _provenienta_act(pid).get("V4_EVIDENCE", "")})
    return imp, prezente, comune, probleme


def scrie(imp):
    """Copiază fișierele + sidecar + actualizează PROVENIENTA.json. Fail-closed pe discrepanță/dublu."""
    # amprentele existente, pentru garda anti-dublu byte-identic
    existente_hash = {}
    for f in os.listdir(CORPUS):
        c = os.path.join(CORPUS, f)
        if os.path.isfile(c) and not f.endswith((".sha256", ".json")):
            existente_hash.setdefault(_sha256(c), f)
    prov = json.load(io.open(PROV, encoding="utf-8"))
    fisiere = prov.setdefault("fisiere", {})
    scrise = []
    for it in imp:
        data = io.open(it["src"], "rb").read()
        h = hashlib.sha256(data).hexdigest()
        if h != it["source_sha"]:
            raise SystemExit("ABORT %s: hash copiat %s != source_SHA256 %s" % (it["pid"], h, it["source_sha"]))
        if h in existente_hash:
            raise SystemExit("ABORT %s: byte-identic cu %s (ar aprinde garda anti-dublu)"
                             % (it["pid"], existente_hash[h]))
        dest = os.path.join(CORPUS, it["target"])
        io.open(dest, "wb").write(data)
        io.open(dest + ".sha256", "w", encoding="utf-8").write(h + "\n")
        existente_hash[h] = it["target"]
        fisiere[it["target"]] = {
            "clasa": "ADUS",
            "motiv": "act oficial adus din corpusul FISCAL (%s), materialul principal; bytes oficiali legislatie.just.ro" % it["pid"],
            "official_source": it["official_source"],
            "accessed_at": it["accessed_at"],
            "POSITION_ID": it["pid"],
            "V4_EVIDENCE": it["v4"],
        }
        scrise.append(it["target"])
    io.open(PROV, "w", encoding="utf-8").write(json.dumps(prov, ensure_ascii=False, indent=2) + "\n")
    return scrise


def main():
    imp, prezente, comune, probleme = planifica()
    print("DISPOZIȚIE corpus FISCAL (71 poziții):")
    print("  de importat        : %d" % len(imp))
    print("  deja prezente      : %d" % len(prezente))
    print("  ordine comune      : %d (identitate tip/nr/an nestabilibilă mecanic)" % len(comune))
    print("  probleme           : %d" % len(probleme))
    if comune:
        print("\nORDINE COMUNE (raportate, NEimportate):")
        for pid, opis in comune:
            print("  %s  %s" % (pid, opis))
    if probleme:
        print("\nPROBLEME:")
        for x in probleme:
            print("  %s" % (x,))
    if "--scrie" in sys.argv:
        if probleme:
            raise SystemExit("Probleme nerezolvate — nu scriu.")
        scrise = scrie(imp)
        print("\nSCRIS: %d fișiere + sidecar + PROVENIENTA.json actualizat." % len(scrise))
    else:
        print("\n(DRY-RUN — rulează cu --scrie pentru a materializa.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
