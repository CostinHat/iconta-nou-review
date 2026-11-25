"""Acoperirea probelor candidatului și comparațiile măsurabile pe documentele lotului."""

import csv
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

DIM = ("1366x768", "603x590")


def cere(ok, mesaj):
    if not ok:
        raise ValueError(mesaj)


def martor(root, ref):
    cale = Path(ref["dovada"])
    p = (root / cale).resolve()
    cere(
        not cale.is_absolute()
        and p.is_relative_to(root)
        and p.is_file()
        and p.stat().st_size > 0,
        "Cale martor",
    )
    cere(
        hashlib.sha256(p.read_bytes()).hexdigest() == ref["sha256"]
        and ref["localizare"].strip(),
        "Identitate martor " + str(p),
    )
    return p


def dec(x):
    d = Decimal(str(x))
    cere(d.is_finite(), "Sumă nevalidă")
    return d


def banca_afisata(formate_vizibile, eroare):
    return formate_vizibile is True and eroare == ""


def verifica_baza(dosar):
    """Rejudecă profilul cunoscut al F012 din șase referințe de captură ale măsurării pe E_Q9."""
    director = (Path(dosar) / "dovezi" / "F012").resolve()
    original = martor(
        director,
        {
            "dovada": "F012_masuri_4.json",
            "sha256": "7ff58642595adc56971a1014a2b37ba4e1c7ff87640f7d36ce16faa485355e84",
            "localizare": "masuri",
        },
    )
    date = json.loads(original.read_bytes())
    cere(
        date["cod"] == "F012"
        and date["commit_servit"] == "830d7c55845a90a1b911e54470b1c9e9863e32b5",
        "Sursă F012",
    )
    pasi = {
        "1366x768": (
            "banca_F2_1366",
            "reimport_xlsx_1366",
            "banca_F2_reimport2_1366_raf",
        ),
        "603x590": (
            "banca_F2_deschis_603_raf",
            "banca_F2_reimport1_603_raf",
            "banca_F2_reimport2_603_raf",
        ),
    }
    for rezolutie, secventa in pasi.items():
        for numar, pas in enumerate(secventa):
            m = date["masuri"][f"F012@{rezolutie}#{pas}"]
            cere(
                m["raf"] is True
                and m["vizibilitate"] == "visible"
                and f"{m['W']}x{m['H']}" == rezolutie,
                "Cadru sau rezoluție F012",
            )
            cap = m["captura"]
            fisier = martor(
                director,
                {"dovada": cap["fisier"], "sha256": cap["sha256"], "localizare": pas},
            )
            cere(fisier.stat().st_size == cap["octeti"], "Captură F012 incompletă")
            text = m["text"]
            formate = "Formate acceptate" in text
            eroare = (
                "Nu s-au putut încărca liniile."
                if "Nu s-au putut încărca liniile." in text
                else ""
            )
            cere(
                formate == (numar == 0)
                and bool(eroare) == (rezolutie == "603x590" and numar == 2),
                "Profil F012 diferit",
            )
            ok = banca_afisata(formate, eroare)
            cere(ok == (numar == 0), "Verdict diferit pentru afișarea băncii")
            print(
                rezolutie,
                pas,
                "trece" if ok else "pică",
                "|",
                eroare or "fără mesaj de eroare",
            )
    print("Profilul istoric F012 a fost reprodus la ambele rezoluții.")


def antet_corect(m, latime):
    complet = m["cabinet"] + " · " + m["utilizator"]
    # Coordonate după stabilizarea cadrului. Intervale pozitive în interiorul ferestrei.
    veriga, cautare, iesire = [
        m[n] for n in ("dreptunghi_veriga", "dreptunghi_cautare", "dreptunghi_iesire")
    ]

    def vizibil(r):
        x, y, dreapta, jos = map(dec, r)
        return 0 <= x < dreapta <= latime and 0 <= y < jos <= m["inaltime_viewport"]

    def distincte(a, b):
        return a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]

    return (
        m["cabinet"].strip()
        and m["utilizator"].strip()
        and m["text"] == complet
        and m["titlu_integral"] == complet
        and m["linii"] == 1
        and m["text_overflow"] == "ellipsis"
        and m["overflow_x"] in {"hidden", "clip"}
        and (
            latime != 603
            or dec(m["text_scroll_width"]) > dec(m["text_client_width"]) > 0
        )
        and m["latime_document"] == latime
        and m["latime_viewport"] == latime
        and all(vizibil(r) for r in (veriga, cautare, iesire))
        and distincte(veriga, cautare)
        and distincte(veriga, iesire)
        and distincte(cautare, iesire)
        and m["hit_cautare"] is True
        and m["hit_iesire"] is True
    )


def note_lot(caz, m):
    if caz == "AC189":
        return (
            m["firma"] == "F1"
            and dec(m["introduceri"]["suma_api"])
            == dec(m["introduceri"]["procent_api"])
            == 0
            and m["introduceri"]["text_dom"] == "0,00 lei (0%)"
            and dec(m["expedieri"]["suma_api"]) == 4000
            and dec(m["expedieri"]["procent_api"]) == dec("0.4")
            and m["expedieri"]["text_dom"] == "4.000,00 lei (0,4%)"
        )
    if caz == "AC190":
        return (
            len(m["status_protejate"]) >= 2
            and set(m["status_protejate"]) == {401}
            and m["reveniri_login"] == 1
            and m["login_vizibil"] is True
            and m["motiv_vizibil"] is True
            and "expirat" in m["text_motiv"].casefold()
            and m["reveniri_la_403"] == 0
            and m["reveniri_la_eroare_retea"] == 0
            and m["bucla_la_login_invalid"] is False
            and m["dupa_reautentificare"] == 200
        )
    if caz == "X02":
        return (
            m["rol"] == "asistent junior"
            and m["poarta_prima"] is True
            and m["poarta_dupa_configurare"] is False
            and m["poarta_a_doua"] is False
            and m["deschideri_automate"] == [0, 0]
            and m["deschidere_manuala"] == [True, True]
            and m["inchideri"]
            == {"x": True, "esc": True, "buton_jos": True, "esc_dupa_inapoi": True}
        )
    raise ValueError("Control necunoscut " + caz)


def verificari(caz, m):
    if caz in {"AC189", "AC190", "X02"}:
        return note_lot(caz, m)
    if caz == "banca":
        ids = m["iduri_api"]
        return (
            bool(ids)
            and len(ids) == len(set(ids))
            and len(m["redesenari"]) == 2
            and all(
                s["http"] == 200
                and banca_afisata(s["formate_vizibile"], s["eroare"])
                and sorted(s["iduri_dom"]) == sorted(ids)
                and s["cautare_utilizabila"] is True
                and bool(s["cipuri_api"])
                and s["cipuri_dom"] == s["cipuri_api"]
                for s in m["redesenari"]
            )
        )
    if caz == "ubl":
        return (
            dec(m["tax_total"]) == 147
            and sorted(map(dec, m["subtotaluri"])) == [22, 105]
            and dec(m["net"]) == 700
            and dec(m["net"]) + sum(map(dec, m["subtotaluri"])) == dec(m["brut"]) == 827
            and m["semnal_inainte"] is True
            and m["note_la_refuz"] == 0
            and m["nir_inainte_de_confirmare"] is True
            and m["control_coerent_contabilizat"] is True
        )
    if caz == "spv":
        return (
            m["cui_firma"] == "55229657"
            and m["pozitiv"]["cui_xml"] == m["cui_firma"]
            and bool(m["pozitiv"]["index"])
            and m["pozitiv"]["ciorne_dupa_doua_citiri"] == 1
            and set(m["refuzuri"]) == {"absent", "ambiguu", "strain"}
            and all(
                v["scrieri"] == 0 and v["importate_ui"] == 0 and v["motiv"].strip()
                for v in m["refuzuri"].values()
            )
        )
    if caz == "reconciliere":
        conturi = m["conturi"]
        return set(conturi) == {"4426", "4427"} and all(
            bool(v["documente"])
            and len({r["id"] for r in v["documente"]}) == len(v["documente"])
            and all(
                r["id"] and r["legatura_verificata"] is True for r in v["documente"]
            )
            and dec(v["decont"]) - dec(v["balanta"])
            == sum(dec(r["diferenta_semnata"]) for r in v["documente"])
            for v in conturi.values()
        )
    if caz == "cadru":
        return (
            m["animatie_activa"] is True
            and dec(m["timp_cadru_initial_ms"]) == 0
            and all(
                0 < dec(m[k]) <= 1 for k in ("opacitate_overlay", "opacitate_fereastra")
            )
            and m["fiscal_vizibil"] is True
            and m["click_pe_principala"] is True
            and m["salut_pe_pagina"] is True
        )
    if caz == "eligibilitate":
        return (
            m["exclus_id"] == 73
            and re.search(r"F1A\s*(?:nr\.?\s*)?17(?!\d)", m["motiv_exclus"]) is not None
            and m["refuz_http"] == 422
            and type(m["eligibil_id"]) is int
            and m["eligibil_id"] > 0
            and m["eligibil_id"] != 73
            and m["eligibil_admis"] is True
            and m["eligibil_fara_blocant"] is True
        )
    raise ValueError("Caz necunoscut " + caz)


def citeste(dosar, candidat):
    cere(
        re.fullmatch("[0-9a-f]{40}", candidat)
        and candidat != "830d7c55845a90a1b911e54470b1c9e9863e32b5",
        "Identitate candidat",
    )
    base = Path(__file__).resolve().parent
    with (base / "acceptare_17_5_Q10.tsv").open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    tinta = {(r["cod"], r["criteriu"], r["rezolutie"]) for r in rows}
    gasit = set()
    speciale = set()
    root = Path(dosar).resolve()
    surse = {root / "masuri_ds.json", root / "probe_fluxuri.json"}
    for src in sorted(surse):
        payload = json.loads(src.read_bytes())
        for r in payload["celule"] + payload["controale"]:
            refs = {martor(root, r[k]) for k in ("observat", "sursa_independenta")}
            cere(
                len(refs) == 2
                and not refs & surse
                and r["observat"]["sha256"] != r["sursa_independenta"]["sha256"],
                "Martori circulari sau identici",
            )
            cere(r["commit"] == candidat, "Alt candidat")
        for r in payload["celule"]:
            k = (r["cod"], r["criteriu"], r["rezolutie"])
            cere(
                k in tinta and k not in gasit, "Celulă duplicată sau străină " + str(k)
            )
            cere(
                (src.name == "masuri_ds.json") == (k[1] in {"Aspect", "Design"}),
                "Familie greșită",
            )
            cere(
                r["stare"] in {"trece", "document_lipsa", "postpublicare"}
                and r["observatie"].strip(),
                "Probă lipsă sau roșie " + str(k),
            )
            if r["stare"] == "document_lipsa":
                cere(k[0] == "F026", "Excepție documentară")
            if r["stare"] == "postpublicare":
                cere(
                    k[0] == "F179" or (k[0], k[1]) == ("X02", "Funcțional"),
                    "Excepție externă",
                )
            gasit.add(k)
        for r in payload["controale"]:
            caz, z = r["caz"], r["rezolutie"]
            cere(
                (caz, z) not in speciale
                and (z in DIM or (caz, z) == ("AC188", "1920x1080")),
                "Identitate control",
            )
            cere(
                (src.name == "masuri_ds.json") == (caz in {"cadru", "AC188"}),
                "Familie control",
            )
            if caz == "AC188":
                w, h = map(int, z.split("x"))
                ok = r["masuri"]["inaltime_viewport"] == h and antet_corect(
                    r["masuri"], w
                )
            else:
                ok = verificari(caz, r["masuri"])
            cere(ok, "Control neconform " + caz + " " + z)
            speciale.add((caz, z))
    cere(gasit == tinta, "Celule lipsă " + str(sorted(tinta - gasit)))
    cere(
        speciale
        == {
            (c, z)
            for c in (
                "banca",
                "ubl",
                "spv",
                "reconciliere",
                "cadru",
                "eligibilitate",
                "AC188",
                "AC189",
                "AC190",
                "X02",
            )
            for z in DIM
        }
        | {("AC188", "1920x1080")},
        "Controale lipsă",
    )
    print(
        "Probe candidat verificate:",
        len(gasit),
        "celule,",
        len(speciale),
        "controale. Închiderea Pilotului se judecă după publicare.",
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Utilizare: oracol_probe_Q10.py --baza DOSAR_REMASURARE | DOSAR_CANDIDAT SHA_C"
        )
    if sys.argv[1] == "--baza":
        verifica_baza(sys.argv[2])
    else:
        citeste(sys.argv[1], sys.argv[2])
