# -*- coding: utf-8 -*-
"""GARD onboarding_ux: fereastra de bun venit (salut inaintea Suportului, firul spune unde se face
fiecare pas), Solduri initiale (model descarcabil, blocare pe neechilibru, transparenta conturi noi),
si descoperibilitatea importului in masa de firme din lista de firme. Q4-Q7, Q10."""
import io


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_bun_venit_salut_inaintea_suportului():
    js = _read("static/js/ecrane/ansamblu.js")
    poz_salut = js.find("Bun venit")
    poz_suport = js.find("cardul Suport")
    assert poz_salut > 0 and poz_suport > 0, "lipsesc blocurile salut/Suport"
    assert poz_salut < poz_suport, "salutul nu mai vine inaintea Suportului (Q6)"


def test_firul_spune_unde_se_face_fiecare_pas():
    js = _read("static/js/ecrane/ansamblu.js")
    assert "ans-fir-unde" in js, "firul de intrare nu spune UNDE se face fiecare pas (Q5)"


def test_pas_stivuit():
    js = _read("static/js/ecrane/ansamblu.js")
    assert "ans-pas-titlu" in js and "ans-pas-desc" in js, "pasii nu sunt stivuiti titlu/descriere (Q7)"


def test_solduri_model_descarcabil():
    js = _read("static/js/ecrane/migrare.js")
    assert "descarcaModelSolduri" in js, "lipseste modelul descarcabil de solduri (Q10)"
    assert 'a.download = "model_solduri_initiale.csv"' in js, "modelul nu se descarca"


def test_solduri_blocheaza_neechilibrul_inainte_de_click():
    js = _read("static/js/ecrane/migrare.js")
    assert "else if (!echilibrat)" in js, "Salveaza nu e blocat pe balanta neechilibrata (Q10)"


def test_solduri_transparenta_conturi_noi():
    js = _read("static/js/ecrane/migrare.js")
    assert "nu sunt respinse" in js, "nu spune ce se intampla cu conturile inexistente (Q10)"


def test_import_in_masa_descoperibil_din_firme():
    js = _read("static/js/ecrane/firme.js")
    assert "firme-import-masa" in js, "importul in masa nu e descoperibil din lista de firme (Q4)"
    assert "randeazaMigrare" in js, "butonul de import in masa nu deschide migrarea cabinetului"
