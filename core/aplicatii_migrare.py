# -*- coding: utf-8 -*-
"""core/aplicatii_migrare.py — registrul aplicațiilor din care se migrează: pentru fiecare aplicație, pe fiecare pas al
migrării, ce export se scoate din ea și cine îl citește în iConta.eu (comanda Costin 15.10.2026, deficiența 270, verbatim în
DECIZII: „«Migrare cabinet» are sus câte un buton pentru fiecare aplicație: SAGA, WinMentor, Ciel, SmartBill. Activ e doar butonul
unei aplicații ale cărei exporturi iConta le citește deja (azi SAGA) … Celelalte butoane sunt inactive și devin active fără alte
modificări de ecran când iConta începe să le citească exportul.”).

UN SINGUR LOC. Ecranul nu știe nimic despre aplicații: primește registrul de la `GET /migrare/aplicatii` și desenează butoanele și
pașii din el. Ca o aplicație să devină activă se adaugă aici, pe pasul ei, exportul și cititorul — nimic pe ecran.

„ACTIV” E DERIVAT, nu scris: o aplicație e activă dacă are cel puțin un pas CITIT, iar un pas e citit dacă are un cititor (funcția
de import care primește exportul aplicației). Nu există un câmp „activ” de bifat de mână — un buton activ fără cititor în spate e
imposibil prin construcție. Gard: `core/test_aplicatii_migrare.py` (cititorul se rezolvă la o funcție, și citește un export al
aplicației din probă; un cititor fără export descris e refuzat).

CHEILE PAȘILOR sunt cele din `migrare_api.STRATURI` (aceleași ca în `static/js/ecrane/migrare.js`); un pas lipsă dintr-o aplicație =
neacoperit (ecranul oferă modelul CSV, ca până acum).

SURSA EXPORTURILOR SAGA: manualul SAGA C salvat în `anaf_surse/saga_manual_topic*` (cu amprentele lor); drumul din meniu e cel din
cuprinsul manualului (Situații › Contabile › Balanțe etc.), formatele din „Considerații generale” (topic 5: butonul de export
„exportă datele din ecranul curent, în format XLS(Excel), CSV, TXT sau XML”) — XML nu e printre formatele citite de
`core.import_tabel`, deci nu se cere. Pentru WinMentor, Ciel și SmartBill nu avem nici manualul exporturilor, nici un cititor: niciun
pas, deci inactive.

Temei: N/A — registru de ecran (tooling), nicio valoare fiscală.
"""
from __future__ import annotations

import collections
import importlib

#: un pas acoperit: ce export scoate omul (text pentru ecran, după „Scoate din <aplicație>: ”), de unde e luat (manualul) și
#: funcția care îl citește (`modul:funcție`, aceeași pe care o cheamă ruta de încărcare a pasului)
Pas = collections.namedtuple("Pas", "export sursa cititor")

Aplicatie = collections.namedtuple("Aplicatie", "cheie nume pasi")

_FORMATE = "în format XLS, CSV sau TXT"

APLICATII = (
    Aplicatie("saga", "SAGA", {
        "solduri": Pas(
            "balanța de verificare analitică (Situații › Contabile › Balanțe, cu „Analitica” bifată), pe luna dinaintea preluării, "
            + _FORMATE,
            "anaf_surse/saga_manual_topic52_balante.txt",
            "core.solduri_api:extrage_balanta_detaliat"),
        "solduri_parteneri": Pas(
            "situația clienților și, separat, a furnizorilor (Situații › Comerciale, pagina „Situație generală”, cu coloana "
            "„Neachitat final”), " + _FORMATE,
            "anaf_surse/saga_manual_topic60_situatii_clienti_furnizori.txt",
            "core.solduri_parteneri_api:extrage"),
        "salariati": Pas(
            "lista salariaților (Nomenclatoare › Salariați), " + _FORMATE,
            "anaf_surse/saga_manual_topic25_salariati.txt",
            "core.salariati_import_api:extrage"),
        "mijloace_fixe": Pas(
            "lista imobilizărilor (Operații › Imobilizări, pagina „Lista imobilizărilor”), " + _FORMATE,
            "anaf_surse/saga_manual_topic34_imobilizari.txt",
            "core.mijloace_fixe_import_api:extrage"),
    }),
    Aplicatie("winmentor", "WinMentor", {}),
    Aplicatie("ciel", "Ciel", {}),
    Aplicatie("smartbill", "SmartBill", {}),
)


def cititor(referinta):
    """Funcția din `modul:funcție`. Ridică (ImportError / AttributeError) dacă nu există — un pas declarat citit fără funcție în
    spate nu se rotunjește la „citit”."""
    modul, functie = referinta.split(":", 1)
    return getattr(importlib.import_module(modul), functie)


def pas_citit(pas):
    """Un pas e citit dacă are un cititor; exportul descris e condiția lui (fără el omul n-ar ști ce să scoată)."""
    return bool(pas.cititor) and bool((pas.export or "").strip())


def activa(aplicatie):
    """DERIVAT: activă = cel puțin un pas citit."""
    return any(pas_citit(p) for p in aplicatie.pasi.values())


def registru():
    """Ce primește ecranul: aplicațiile, în ordinea butoanelor, fiecare cu `activa` derivat și pașii citiți
    (`{cheie_pas: {"export": ...}}`). Pașii neciți nu se trimit: ecranul îi arată ca până acum, cu modelul CSV."""
    return [{"cheie": a.cheie, "nume": a.nume, "activa": activa(a),
             "pasi": {k: {"export": p.export} for k, p in a.pasi.items() if pas_citit(p)}}
            for a in APLICATII]
