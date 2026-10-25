# -*- coding: utf-8 -*-
"""[deficiența 267, comanda Costin 15.10.2026 noaptea, verbatim în DECIZII „Lotul 5 — comanda 3”: „formularul «Înregistrează cabinetul
tău» pierde tot ce s-a completat dacă e închis sau dacă utilizatorul iese din pagină. Se păstrează și se reface la redeschidere, mai puțin
parolele; se șterge după crearea contului. Verifici clasa la formularele lungi.”]

Ciorna e `static/js/ciorna_formular.js` (`ciornaFormular`). Gărzi, pe sursă:
  · nicio parolă într-o ciornă: niciun id cu „parola” / „password” în lista câmpurilor, în niciun apel din `static/js`;
  · înregistrarea își șterge ciorna ÎNAINTEA tuturor celor trei ieșiri reușite (cererea liberă, contul fără firmă, intrarea în cont);
  · CLASA: fiecare formular lung de creare din `FORMULARE_LUNGI` (> 15 câmpuri scrise de om, sau numit în comandă) are ciorna lui.
    Emiterea facturii avea deja ciorna ei (`emitere_ecran.js`, liniile dinamice — `core/test_ciorna_factura.py`).
MUTAȚII: „reg-parola” pus în listă -> pică; `ciorna.sterge()` scos -> pică; ciorna scoasă din concediul medical -> pică.
Proba în browser: frontend_test/e2e/e2e_lot5_c3.py::test_def_267_*."""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: fișier -> prefixul cheii ciornei (formularele lungi de creare)
FORMULARE_LUNGI = {
    "static/js/ecrane/login.js": "iconta_ciorna_inregistrare",
    "static/js/ecrane/firme.js": "iconta_ciorna_salariat:",
    "static/js/ecrane/flux_concediu.js": "iconta_ciorna_cm:",
}
_APEL = re.compile(r"ciornaFormular\(\s*\w+\s*,\s*([^,]+?)\s*,\s*\[([^\]]*)\]", re.S)


def _src(cale):
    return open(os.path.join(RAD, cale), encoding="utf-8").read()


def _apeluri():
    out = []
    for dirp, _d, fis in os.walk(os.path.join(RAD, "static", "js")):
        for f in fis:
            if f.endswith(".js"):
                cale = os.path.relpath(os.path.join(dirp, f), RAD)
                for m in _APEL.finditer(_src(cale)):
                    out.append((cale, m.group(1), re.findall(r'"([\w-]+)"', m.group(2))))
    return out


def test_nicio_parola_in_ciorna():
    ap = _apeluri()
    assert len(ap) >= len(FORMULARE_LUNGI), ap
    parole = [(c, i) for c, _k, ids in ap for i in ids if re.search(r"parol|passw", i)]
    assert parole == [], "parolă păstrată în ciornă: %s" % parole


def test_formularele_lungi_au_ciorna():
    ap = _apeluri()
    lipsa = [f for f, cheie in FORMULARE_LUNGI.items() if not any(c == f and cheie in k for c, k, _ids in ap)]
    assert lipsa == [], "formular lung fără ciornă: %s" % lipsa


def test_inregistrarea_isi_sterge_ciorna_inainte_de_orice_iesire_reusita():
    src = _src("static/js/ecrane/login.js")
    corp = src[src.index("async function creeaza()"):]
    corp = corp[:corp.index('buton.addEventListener("click", creeaza)')]
    sterge = corp.index("ciorna.sterge()")
    # [lotul 12, 642] „cont creat, firma lipsă” nu mai există: contul și firma proprie se creează împreună sau deloc
    for iesire in ("randeazaVerificaEmail(", "sesiune.intra("):
        assert sterge < corp.index(iesire), "ciorna rămâne după %s" % iesire
