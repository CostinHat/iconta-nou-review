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

MATERIALELE (02.10.2026, comanda Costin lot 19 pct.3). Portalul publică multe ordine în MAI MULTE documente:
ordinul (BASE/CUTOFF_VERSION) și anexa integrală consolidată separat (INTEGRAL_ANNEX/ANNEX), plus facsimilele
formularelor (FACSIMILE/ASSET, imagini). Faza de mai sus aducea DOAR materialul principal; la Pachetul FiscalOS §1
înlocuirea a adus, invers, doar anexa (OPANAF 2594/2015, 878/2022). Ambele = act incomplet în corpus.
`planifica_materiale()` ia fiecare act al manifestului PREZENT în corpus și aduce fiecare document lipsă:
  anaf_surse/<tip>_<nr>_<an>__<rol>_<id>.<ext>   rol ∈ {baza, anexa, facsimil}
„Prezent” = un fișier din corpus are deja materialul (după id-ul de portal declarat în PROVENIENTA, după
amprentă, sau după nume). BASE_HISTORY_VIEW (altă randare a aceluiași BASE) se aduce DOAR dacă are articole pe
care BASE-ul din corpus nu le acoperă (`core.corpus_continut`) — altfel ar fi o dublură de conținut.

  python -m scripts.import_corpus_fiscal --materiale            # DRY-RUN materiale
  python -m scripts.import_corpus_fiscal --materiale --scrie    # le scrie
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


ROL_FISIER = {"BASE": "baza", "CUTOFF_VERSION": "baza", "INTEGRAL_ANNEX": "anexa", "ANNEX": "anexa",
              "FACSIMILE": "facsimil", "ASSET": "facsimil", "BASE_HISTORY_VIEW": "istoric"}


def _id_material(mm):
    """Id-ul de portal (DetaliiDocument/<id>) sau numele imaginii (ImaginiDinActe/<nume>.jpg)."""
    u = (mm.get("official_source") or "").rstrip("/").split("/")[-1]
    return os.path.splitext(u)[0] if "." in u else u


def _prezente_in_corpus():
    """(ids_portal -> fișier, sha -> fișier, pid -> fișier) — ce are deja corpusul, după PROVENIENTA și amprente."""
    prov = json.load(io.open(PROV, encoding="utf-8")).get("fisiere", {})
    ids, pids = {}, {}
    for f, v in prov.items():
        if not os.path.isfile(os.path.join(CORPUS, f)):
            continue                                  # o declarație nu ține loc de fișier (un document șters = lipsă)
        txt = json.dumps(v, ensure_ascii=False)
        for m in re.finditer(r"id_portal (\d+)|DetaliiDocument(?:Afis)?/(\d+)|ImaginiDinActe/([^\"/]+?)\.\w+\"", txt):
            ids.setdefault(m.group(1) or m.group(2) or m.group(3), f)
        if isinstance(v, dict) and v.get("POSITION_ID") and v.get("motiv", "").startswith("act oficial adus"):
            pids.setdefault(v["POSITION_ID"], f)
    shas = {}
    for f in os.listdir(CORPUS):
        c = os.path.join(CORPUS, f)
        if os.path.isfile(c) and not f.endswith((".sha256", ".json")):
            shas.setdefault(_sha256(c), f)
    return ids, shas, pids


def _stem_act(f):
    """`<fam>_<nr>_<an>` al fișierului din corpus (familia normalizată ca în ghid_poarta), sau None."""
    from core import ghid_poarta as gp
    if re.match(r"^cpf(_|\d)", f.lower()):
        return "legea_207_2015"
    if re.match(r"^cf(_|\d)", f.lower()):
        return "legea_227_2015"
    m = gp._NUME_FISIER.match(f)
    return "%s_%s_%s" % (gp._PREFIX_FAMILIE[m.group(1).lower()], m.group(2), m.group(3)) if m else None


def _continut_acoperit(cc, src, frati):
    """Articolele/anexele documentului `src` sunt toate în `frati`; un document fără unități marcate (procedură pe
    puncte) se judecă pe textul întreg (acoperire >= pragul modulului)."""
    if cc.unitati(src):
        return not cc.pierderi_act(src, frati)
    text = "\n".join(cc.text_integral(f) for f in frati)
    return cc.acoperire({"text": cc.text_integral(src)}, text) >= cc.PRAG_ACOPERIRE


def planifica_materiale():
    """(import, acoperite, probleme). `import` = [{pid, opis, rol, id, target, src, source_sha, official_source,
    accessed_at}] — documentele lipsă ale actelor din manifest prezente în corpus."""
    from core import ghid_poarta as gp
    from core import corpus_continut as cc
    ident_corpus = gp.corpus_acte()
    ids, shas, pids = _prezente_in_corpus()
    nume = set(os.listdir(CORPUS))
    imp, acoperite, probleme = [], [], []
    for a in _manifest()["acts"]:
        pid = a["POSITION_ID"]
        mt = re.match(r"^([A-Z]+)\s+(\d+)/(\d{4})$", a["identity"].get("opis_identity", "").strip())
        if not mt or mt.group(1) not in FAM:
            continue                                  # ordin comun / neparsabil: nu e în corpus (faza 1 l-a raportat)
        stem = "%s_%s_%s" % (FAM[mt.group(1)], mt.group(2), mt.group(3))
        mats = _provenienta_act(pid)["materials"]
        in_corpus = (FAM[mt.group(1)], mt.group(2), mt.group(3)) in ident_corpus or pid in pids or any(
            _id_material(mm) in ids for mm in mats)
        if not in_corpus:
            continue
        for mm in mats:
            rol = ROL_FISIER.get(mm.get("role"))
            if rol is None:
                probleme.append((pid, mm.get("role"), "rol necunoscut"))
                continue
            idm = _id_material(mm)
            src = os.path.join(SURSA, mm["source_path"].replace("corpus/fiscal/active/", "", 1))
            ext = os.path.splitext(src)[1]
            target = "%s__%s_%s%s" % (stem, rol, idm, ext)
            if mm.get("role") in PRINCIPAL and pids.get(pid):
                acoperite.append((pid, idm, pids[pid]))
                continue
            # shas include și materialele deja PLANIFICATE în rularea asta: portalul folosește uneori aceeași imagine
            # sub două nume (OPANAF 3845/2015: A347 = A372, byte-identice) — a doua e acoperită de prima.
            gasit = ids.get(idm) or shas.get(mm["source_SHA256"]) or (target if target in nume else None)
            if gasit:
                acoperite.append((pid, idm, gasit))
                continue
            if not os.path.exists(src):
                probleme.append((pid, idm, "sursa lipsă pe disc"))
                continue
            # Pe CONȚINUT, nu pe octeți: un document text al cărui conținut e deja în fișierele actului din corpus
            # (altă consolidare / altă randare a aceluiași document — ex. corpusul avea actul din MO sau din alt id
            # de versiune) nu se aduce a doua oară. Imaginile nu au conținut comparabil: doar id/amprentă/nume.
            if ext in (".html", ".htm"):
                frati = [os.path.join(CORPUS, f) for f in sorted(nume) if _stem_act(f) == stem
                         and f.endswith((".html", ".htm", ".txt")) and "__facsimil_" not in f]
                if frati and _continut_acoperit(cc, src, frati):
                    acoperite.append((pid, idm, "conținut acoperit de %s" % ", ".join(os.path.basename(x) for x in frati)))
                    continue
            shas[mm["source_SHA256"]] = target
            imp.append({"pid": pid, "opis": a["identity"]["opis_identity"], "rol": rol, "role": mm.get("role"),
                        "id": idm, "target": target, "src": src, "source_sha": mm["source_SHA256"],
                        "official_source": mm.get("official_source", ""), "accessed_at": mm.get("accessed_at", "")})
    return imp, acoperite, probleme


def scrie_materiale(imp):
    """Copiază documentele lipsă + sidecar + PROVENIENTA. Fail-closed pe SHA diferit sau dublură byte-identică."""
    _ids, shas, _pids = _prezente_in_corpus()
    prov = json.load(io.open(PROV, encoding="utf-8"))
    fisiere = prov.setdefault("fisiere", {})
    # TOT lotul se validează ÎNAINTE de prima scriere: un abort la mijloc lăsa fișiere fără PROVENIENTA (pățit
    # 02.10.2026 — 78 de documente orfane, șterse și rescrise).
    date_lot = []
    for it in imp:
        data = io.open(it["src"], "rb").read()
        h = hashlib.sha256(data).hexdigest()
        if h != it["source_sha"]:
            raise SystemExit("ABORT %s/%s: hash %s != source_SHA256 %s" % (it["pid"], it["id"], h, it["source_sha"]))
        if h in shas:
            raise SystemExit("ABORT %s/%s: byte-identic cu %s" % (it["pid"], it["id"], shas[h]))
        shas[h] = it["target"]
        date_lot.append((it, data, h))
    scrise = []
    for it, data, h in date_lot:
        dest = os.path.join(CORPUS, it["target"])
        io.open(dest, "wb").write(data)
        io.open(dest + ".sha256", "w", encoding="utf-8").write(h + "\n")
        fisiere[it["target"]] = {
            "clasa": "ADUS",
            "motiv": "material %s (%s) al actului %s din corpusul FISCAL (%s), document separat pe portal; bytes "
                     "oficiali legislatie.just.ro; adus 02.10.2026 (act incomplet in corpus, lot 19 pct.3)"
                     % (it["rol"], it["role"], it["opis"], it["pid"]),
            "official_source": it["official_source"],
            "accessed_at": it["accessed_at"],
            "POSITION_ID": it["pid"],
        }
        scrise.append(it["target"])
    io.open(PROV, "w", encoding="utf-8").write(json.dumps(prov, ensure_ascii=False, indent=2) + "\n")
    return scrise


def main_materiale():
    imp, acoperite, probleme = planifica_materiale()
    print("MATERIALE (documente separate pe portal) ale actelor din manifest prezente în corpus:")
    print("  deja în corpus : %d" % len(acoperite))
    print("  de adus        : %d" % len(imp))
    print("  probleme       : %d" % len(probleme))
    for it in imp:
        print("  + %-8s %-10s %s" % (it["rol"], it["pid"], it["target"]))
    for x in probleme:
        print("  ! %s" % (x,))
    if "--scrie" in sys.argv:
        if probleme:
            raise SystemExit("Probleme nerezolvate — nu scriu.")
        print("\nSCRIS: %d documente + sidecar + PROVENIENTA.json." % len(scrie_materiale(imp)))
    return 0


def main():
    if "--materiale" in sys.argv:
        return main_materiale()
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
