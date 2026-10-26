# -*- coding: utf-8 -*-
"""GARDĂ — previzualizarea comună a importurilor de migrare (`static/js/ecrane/migrare.js`), lotul 13, comanda Costin 13.1:

  * 581 „La mărimea normală a ecranului, casetele roșii fixe strâng tabelul rândurilor într-o bară albă și acoperă câmpul de dată la
    derulare; rândurile și motivele se văd doar micșorând pagina. Etichetele «1 rând cu observație» nu se pot apăsa. La toate straturile.”
  * 667 „Tabelul are derulare proprie și capul acoperă primele rânduri (clasa 285); textul explicativ și avertismentul sunt paragrafe lungi”
  * 624 „Importuri, audit, casă, bancă la forma din 617/622; observații la clic; respinsele grupate”

CE FACE IMPOSIBIL (citind sursa, ca gărzile ecranelor din lotul 11): (a) o casetă (firma din fișier, înlocuirea, confruntarea cu balanța,
rândurile ignorate, notele balanței, avertismentul rulajelor) în rezumatul LIPIT sus al vreuneia din cele nouă previzualizări — acolo stau
numai titlul, totalurile și banda; (b) caseta refuzurilor pusă în bara lipită jos (lângă buton), unde creștea până strângea tabelul;
(c) banda stărilor ca text care nu se poate apăsa — fiecare grup e un buton de filtru; (d) lista refuzurilor negrupată.
LIMITA: garda citește sursa, nu ecranul; așezarea pe ecran o probează e2e-ul `frontend_test/e2e/e2e_lot13_migr.py::test_def_581_…`.
TEMEI: N/A — reguli de produs (comanda 13.1; CLAUDE.md §9: „Fereastra încape pe ecran fără derulare; acțiunea principală și mesajele de
eroare se văd mereu.”).
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js", "ecrane", "migrare.js")
CASETE = ("_casetaFirma", "_casetaInlocuire", "casetaIgnorate", "casetaReconciliere", "_notaCititeBalanta", "mig-rulaje", "caseta-atentie",
          "NOTA_FACTURI_PRELUATE", "recHtml")


def _sursa():
    return open(JS, encoding="utf-8").read()


def rezumate_lipite(src):
    """PURĂ: primul argument (rezumatul lipit sus) al fiecărui apel `_cadruPrev(`…`, …)` din sursă."""
    out = []
    for m in re.finditer(r"_cadruPrev\(`", src):
        j = m.end()
        out.append(src[j:src.index("`,\n", j)])
    return out


def test_581_667_rezumatul_lipit_al_fiecarei_previzualizari_n_are_casete():
    rez = rezumate_lipite(_sursa())
    assert len(rez) == 9, "cele nouă previzualizări ale importurilor (balanță, parteneri, salariați, asociați, mijloace fixe, istoric, " \
                          "rețete, articole, RIP): %d găsite" % len(rez)
    rele = [(i, c) for i, s in enumerate(rez) for c in CASETE if c in s]
    assert not rele, "casete în rezumatul lipit sus (îl lungesc până acoperă tabelul — 581 / 667): %s" % rele


def test_581_refuzurile_stau_in_pagina_deasupra_tabelului_nu_in_bara_de_jos():
    src = _sursa()
    for fn in ("gateazaPreview", "gateazaPartial"):
        corp = src[src.index("function %s(" % fn):]
        corp = corp[:corp.index("\n}\n")]
        assert "_puneRefuzul(" in corp and "insertBefore(bloc, buton)" not in corp, fn
        assert "listaRefuzuri(erori)" in corp, "%s: refuzurile grupate pe motiv (624)" % fn


def test_581_624_banda_starilor_e_din_butoane_de_filtru():
    src = _sursa()
    banda = src[src.index("function bandaStari("):]
    banda = banda[:banda.index("\n}\n")]
    assert banda.count('data-filtru-stare="${stare}"') == 1 and "<button" in banda and "<span" not in banda
    assert "_filtreazaStare(b)" in src


def test_624_lista_refuzurilor_grupeaza_acelasi_motiv(tmp_path):
    """Același motiv o singură dată, cu toate rândurile lui — citit din sursă și rulat în Node, dacă există."""
    import shutil
    import subprocess
    src = _sursa()
    fn = src[src.index("const undeE = "):]
    fn = fn[:fn.index("\n// [lotul 13, deficiența 581")]
    if not shutil.which("node"):
        return
    p = tmp_path / "proba.mjs"
    p.write_text("const esc = (s) => String(s);\n" + fn + "\nconsole.log(listaRefuzuri([{rand: 3, mesaj: 'M'}, {rand: 5, mesaj: 'M'}, "
                 "{rand: 4, mesaj: 'N'}]));\n", encoding="utf-8")
    out = subprocess.run(["node", str(p)], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    assert "<li>rândurile 3, 5: M</li>" in out.stdout and "<li>rândul 4: N</li>" in out.stdout, out.stdout
