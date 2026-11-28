# -*- coding: utf-8 -*-
"""[17.5-F5, funcția 501] Hotărârea AGA / decizia asociatului unic: documentul Word (OOXML) și PDF din propunerea comună, condițiile
datate și refuzurile (comanda 17.5-F5 pct.2–7). Așteptările se calculează independent, din intrările probei și din registrul datat
(`common.cota`), nu prin funcțiile testate. Fără bază de date: profilul, soldurile și rulajele se dau probei (monkeypatch)."""
import datetime as dt
import time
import io
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest

from core import common as C
from core import decontari_asociati as DA
from core import hotarare_dividende as H

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _q(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _bani(x):
    return "{:,.2f}".format(_q(x)).replace(",", "X").replace(".", ",").replace("X", ".")


def _date(asociati, brut, data_hot="2026-03-15", interimar=False, aprobare=True, an=2025, profit_an=None, interimare_an=Decimal("0"),
          data_sit=None, profit_interimar=None):
    """Datele documentului pentru `continut` / `docx` / `pdf`, cu repartizarea calculată independent: brut pe cotă, impozit cu cota
    registrului la data hotărârii (ROUND_HALF_UP), net = brut − impozit."""
    d = dt.date.fromisoformat(data_hot)
    cota = C.cota("impozit_dividend", d)[0] * 100
    rand = []
    for nume, pr in asociati:
        b = _q(Decimal(brut) * Decimal(pr) / 100)
        i = _q(b * cota / 100)
        q = Decimal(pr)
        rand.append({"nume": nume, "cota": "%s%%" % (str(int(q)) if q == q.to_integral_value() else str(q).replace(".", ",")),
                     "brut": b, "impozit": i, "net": b - i})
    return {"varianta": "C" if interimar else ("B" if len(asociati) == 1 else "A"), "unic": len(asociati) == 1, "interimar": interimar,
            "firma": {"nume": "Probă Dividende SRL", "cui": "123456", "reg_com": "J40/1/2026", "sediu": "Str. Probei 1, București",
                      "capital_subscris": Decimal("200.00"), "capital_varsat": Decimal("200.00")},
            "fel": H.FEL_UNIC if len(asociati) == 1 else H.FEL_AGA, "numar": "1", "data_hotarare": d, "asociati": rand,
            "brut": _q(brut), "impozit": sum(r["impozit"] for r in rand), "net": sum(r["net"] for r in rand),
            "cota": "%d%%" % int(cota), "sursa": "463" if interimar else "1171", "aprobare": aprobare and not interimar,
            "an_situatii": an if aprobare and not interimar else None, "data_situatii": data_sit, "termen_plata": d + dt.timedelta(days=31),
            "modalitate": "virament", "loc": "sediul societății", "convocare": None, "administrator": "Popescu Petru", "exemplare": len(asociati) + 1,
            "activ_net": Decimal("114800.00"), "jumatate": Decimal("100.00"), "capital": Decimal("200.00"), "data_referinta": d,
            "data_situatii_cerute": dt.date(an, 12, 31), "profit_an": profit_an, "interimare_an": interimare_an,
            "profit_interimar": profit_interimar, "disponibil_interimar": None}


T1 = (("Ion Test", "60"), ("Maria Test", "40"))


def _docx_text(continut):
    z = zipfile.ZipFile(io.BytesIO(continut))
    doc = ET.fromstring(z.read("word/document.xml"))
    corp = doc.find(W + "body")
    in_tabel = {id(p) for t in corp.iter(W + "tbl") for p in t.iter(W + "p")}
    par = ["".join(x.text or "" for x in p.iter(W + "t")) for p in corp.iter(W + "p") if id(p) not in in_tabel]
    tab = [[["".join(x.text or "" for x in c.iter(W + "t")) for c in r.findall(W + "tc")] for r in t.findall(W + "tr")] for t in corp.iter(W + "tbl")]
    return z, par, tab


def _pdf_text(continut):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "h.pdf"
        f.write_bytes(continut)
        r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(f), "-"], capture_output=True, check=True)
    return re.sub(r"\s+", " ", r.stdout.decode("utf-8"))


def test_t1_doi_asociati_word_si_pdf_au_aceleasi_valori_pe_beneficiar_si_totalurile():
    d = _date(T1, "50000")
    assert [(r["brut"], r["impozit"], r["net"]) for r in d["asociati"]] == [
        (Decimal("30000.00"), Decimal("4800.00"), Decimal("25200.00")), (Decimal("20000.00"), Decimal("3200.00"), Decimal("16800.00"))]
    _z, par, tab = _docx_text(H.docx(d))
    titluri = [t for t in tab if t and t[0][0] == "Asociatul"]
    assert len(titluri) == 1
    t = titluri[0]
    assert t[0] == ["Asociatul", "Cota din capitalul social", "Dividend brut (lei)", "Impozit pe dividende 16% (lei)", "Dividend net (lei)"]
    assert t[1:] == [["Ion Test", "60%", "30.000,00", "4.800,00", "25.200,00"], ["Maria Test", "40%", "20.000,00", "3.200,00", "16.800,00"],
                     ["Total", "100%", "50.000,00", "8.000,00", "42.000,00"]]
    text = " ".join(par)
    assert "HOTĂRÂREA ADUNĂRII GENERALE A ASOCIAȚILOR" in text and "nr. 1 din 15.03.2026" in text and "HOTĂRĂȘTE:" in text
    assert len(re.findall(r"Se împuternicește Popescu Petru, administrator al societății", text)) == 1
    assert len(re.findall(r"în 3 exemplare originale", text)) == 1
    assert "«" not in text and "[" not in text, "instrucțiunile editoriale și câmpurile goale ale modelului nu intră în document"
    pdf = _pdf_text(H.pdf(d))
    for x in ("nr. 1 din 15.03.2026", "Ion Test", "60%", "30.000,00", "4.800,00", "25.200,00", "Maria Test", "16.800,00",
              "50.000,00", "8.000,00", "42.000,00", "Se împuternicește Popescu Petru", "în 3 exemplare originale", "HOTĂRĂȘTE:"):
        assert x in pdf, x


def test_t1_articolele_se_renumeroteaza_fara_goluri():
    _z, par, _t = _docx_text(H.docx(_date(T1, "50000", aprobare=False)))
    nr = [int(m.group(1)) for p in par for m in [re.match(r"Art\. (\d+)\.", p)] if m]
    assert nr == list(range(1, len(nr) + 1)) and len(nr) >= 5
    assert not any("situațiile financiare anuale ale societății pentru exercițiul" in p for p in par), "fără aprobare, art. 1 lipsește"


def test_word_se_redeschide_se_editeaza_paragraf_si_celula_si_se_reciteste():
    """Pct.4: Word-ul se deschide, se citește textul și tabelul, se modifică un paragraf și o celulă, se salvează și se redeschide."""
    z, par, tab = _docx_text(H.docx(_date(T1, "50000")))
    assert z.testzip() is None
    tipuri = ET.fromstring(z.read("[Content_Types].xml"))
    assert any(o.get("PartName") == "/word/document.xml" for o in tipuri)
    rel = ET.fromstring(z.read("_rels/.rels"))
    assert any(r.get("Target") == "word/document.xml" and r.get("Type").endswith("/officeDocument") for r in rel)
    for p in z.namelist():
        if p.endswith(".xml") or p.endswith(".rels"):
            ET.fromstring(z.read(p))   # fiecare parte e XML valid
    assert not any(n.lower().endswith(".pdf") for n in z.namelist()) and b"altChunk" not in z.read("word/document.xml")
    assert b"documentProtection" not in z.read("word/document.xml")
    doc = ET.fromstring(z.read("word/document.xml"))
    prim = next(t for t in doc.iter(W + "t") if (t.text or "").startswith("Prezenta hotărâre"))
    prim.text = "Prezenta hotărâre, editată la probă."
    celula = [t for t in doc.iter(W + "t") if t.text == "30.000,00"][0]
    celula.text = "30.000,01"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z2:
        for n in z.namelist():
            z2.writestr(n, ET.tostring(doc, xml_declaration=True, encoding="UTF-8") if n == "word/document.xml" else z.read(n))
    _z3, par3, tab3 = _docx_text(buf.getvalue())
    assert "Prezenta hotărâre, editată la probă." in par3 and tab3[0][1][2] == "30.000,01"


def test_t2_asociat_unic_decizie_decid_semnatura_unica():
    d = _date((("Ion Unic", "100"),), "10000")
    _z, par, tab = _docx_text(H.docx(d))
    text = " ".join(par)
    assert "DECIZIA ASOCIATULUI UNIC" in text and "DECID:" in text and "HOTĂRĂȘTE" not in text
    assert "art. 196¹ alin. (2)" in text and "art. 196¹ alin. (1)" in text
    assert "cu votul" not in text and "Adunarea" not in text, "asociatul unic nu are vot de adunare"
    assert text.count("______________________________") == 1 and "Asociat unic," in text
    assert "prezenta decizie" in text and "Se aprobă distribuirea către asociatul unic" in text
    assert tab[0][-1] == ["Total", "100%", "10.000,00", "1.600,00", "8.400,00"]


def test_t3_interimar_c_trimestrul_regularizarea_si_restrictia_imprumuturilor():
    d = _date(T1, "6000", data_hot="2026-07-10", interimar=True, data_sit=dt.date(2026, 6, 30), profit_interimar=Decimal("20000.00"))
    d["data_situatii_cerute"] = dt.date(2026, 6, 30)
    _z, par, _t = _docx_text(H.docx(d))
    text = " ".join(par)
    assert "privind distribuirea de dividende interimare" in text and "trimestrului 2 al exercițiului financiar 2026" in text
    assert "în termen de 60 de zile" in text and "nu acordă împrumuturi asociaților sau altor persoane afiliate" in text
    assert "art. 67 alin. (2³)" in text and "art. 69¹ alin. (3)" in text
    du = _date((("Ion Unic", "100"),), "6000", data_hot="2026-07-10", interimar=True, data_sit=dt.date(2026, 6, 30),
               profit_interimar=Decimal("20000.00"))
    t2 = " ".join(_docx_text(H.docx(du))[1])
    assert "DECIZIA ASOCIATULUI UNIC" in t2 and "DECID:" in t2 and "prezenta decizie" in t2, "la unic, C preia antetul, formula și semnătura din B"


@pytest.mark.parametrize("interimar_an, sens", [(Decimal("8000"), "se plătește asociaților"), (Decimal("12000"), "se restituie societății"),
                                                 (Decimal("10000"), "este zero")])
def test_t3_regularizarea_anuala_in_ambele_sensuri_si_diferenta_zero(interimar_an, sens):
    d = _date(T1, "10000", interimare_an=interimar_an)
    text = " ".join(_docx_text(H.docx(d))[1])
    dif = abs(Decimal("10000") - interimar_an)
    assert "Diferența de %s lei %s" % (_bani(dif), sens) in text
    assert ("60 de zile" in text) == (dif != 0)


def test_t6_cota_e_cea_de_la_data_hotararii_nu_de_la_data_notei():
    """Hotărâre 20.12.2025, notă 05.01.2026: cota din registru la 20.12.2025 (10%) în tabel, Word și PDF; nota primește data hotărârii."""
    assert C.cota("impozit_dividend", dt.date(2025, 12, 20))[0] * 100 == 10
    assert C.cota("impozit_dividend", dt.date(2026, 1, 5))[0] * 100 == 16
    d = _date(T1, "50000", data_hot="2025-12-20", an=2024)
    assert d["cota"] == "10%"
    _z, _p, tab = _docx_text(H.docx(d))
    assert tab[0][0][3] == "Impozit pe dividende 10% (lei)" and tab[0][-1][3] == "5.000,00"
    pdf = _pdf_text(H.pdf(d))   # titlul celulei se rupe pe rânduri în PDF
    assert "Impozit pe" in pdf and "10% (lei)" in pdf and "16%" not in pdf and "5.000,00" in pdf
    src = Path(__file__).resolve().parents[1].joinpath("core", "uc_tenants.py").read_text(encoding="utf-8")
    assert "r = _da.nota_dividend(brut, data_hot, interimar" in src, "cota notei se ia la data hotărârii (pct.5 d)"


def test_t9_trei_asociati_restul_de_un_ban_ca_motorul():
    """33,33 / 33,33 / 33,34% la 10.000 lei: suma exactă pe beneficiar și beneficiarul restului, confruntate cu motorul."""
    struct = [("A", None, Decimal("33.33")), ("B", None, Decimal("33.33")), ("C", None, Decimal("33.34"))]
    parti = DA.imparte_dividend(Decimal("10000"), struct, Decimal("16"))
    assert sum(p["brut"] for p in parti) == Decimal("10000.00")
    # așteptarea independentă: părțile în ordinea cotelor descrescătoare, fiecare rotunjită la ban; la 10.000 nu rămâne rest
    assert [(p["cnp"], p["brut"]) for p in parti] == [("C", Decimal("3334.00")), ("A", Decimal("3333.00")), ("B", Decimal("3333.00"))]
    parti2 = DA.imparte_dividend(Decimal("10000.01"), struct, Decimal("16"))
    # 10.000,01: 3334,0033 / 3333,0033 / 3333,0033 -> 3334,00 / 3333,00 / 3333,00 = 10.000,00; restul de un ban -> cota cea mai mare (C)
    assert [(p["cnp"], p["brut"]) for p in parti2] == [("C", Decimal("3334.01")), ("A", Decimal("3333.00")), ("B", Decimal("3333.00"))]
    assert sum(p["brut"] for p in parti2) == Decimal("10000.01")
    d = _date((("A", "33.33"), ("B", "33.33"), ("C", "33.34")), "10000")
    _z, _p, tab = _docx_text(H.docx(d))
    assert tab[0][-1][2] == "10.000,00"


def _cur():
    return object()


def _cu_profil(monkeypatch, **profil):
    baza = {"nume": "Probă SRL", "cui": "1", "reg_com": "J1", "adresa": "Str. 1", "oras": "București", "judet": "B", "declarant_nume": "Pop",
            "declarant_prenume": "Ion", "patron_nume": "", "tip_firma": "srl", "forma_juridica": "SRL", "capital_subscris": Decimal("100000"),
            "capital_varsat": Decimal("100000")}
    baza.update(profil)
    monkeypatch.setattr(H, "profil_firma", lambda cur, schema: dict(baza))
    return baza


def _propunere(asociati=(("Ion Test", "1850101400017", "60"), ("Maria Test", "2870202400011", "40")), brut="50000", interimar=False):
    parti = [{"nume": n, "cnp": c, "cota": Decimal(p), "brut": _q(Decimal(brut) * Decimal(p) / 100)} for n, c, p in asociati]
    for x in parti:
        x["impozit"] = _q(x["brut"] * Decimal("0.16"))
        x["net"] = x["brut"] - x["impozit"]
    return {"nota": {"parti": parti, "impozit": sum(x["impozit"] for x in parti), "net": sum(x["net"] for x in parti)},
            "interimar": interimar, "brut": Decimal(brut), "cota_text": "16%", "cont_sursa": "1171"}


CORP = {"numar_hotarare": "1", "data_hotarare": "2026-03-15", "aprobare_anuala": "da", "an_situatii": "2025", "termen_plata": "2026-04-15",
        "modalitate_plata": "virament", "loc_adunare": "sediul societății", "prezenta": "toti", "vot": "unanimitate", "administrator": "Popescu Petru",
        "exemplare": "3"}


def _sold_activ_net(valoare):
    """Soldurile la data situațiilor: capitalurile proprii = activul net (active − datorii)."""
    return {"1012": (Decimal("0"), Decimal("100000")), "1171": (Decimal(100000) - valoare, Decimal("0")) if valoare < 100000 else
            (Decimal("0"), valoare - Decimal(100000))}


@pytest.mark.parametrize("activ, trece", [(Decimal("49999.99"), False), (Decimal("50000.00"), True), (Decimal("50000.01"), True)])
def test_t4_activul_net_fata_de_jumatate_din_capital(monkeypatch, activ, trece):
    from core import bilant_api
    _cu_profil(monkeypatch)
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, zi, ref="calculeaza": _sold_activ_net(activ))
    monkeypatch.setattr(H, "profit_exercitiu", lambda cur, schema, an: None)
    monkeypatch.setattr(H, "interimare_distribuite", lambda cur, schema, an: Decimal("0"))
    assert H.capitaluri_proprii(_sold_activ_net(activ)) == activ
    if trece:
        d = H.date_document(_cur(), "s", _propunere(), dict(CORP))
        assert d["activ_net"] == activ and d["jumatate"] == Decimal("50000.00")
    else:
        with pytest.raises(H.LipsaDate) as e:
            H.date_document(_cur(), "s", _propunere(), dict(CORP))
        assert "49.999,99 lei" in str(e.value) and "50.000,00 lei" in str(e.value) and "art. 69¹ alin. (2)" in str(e.value)


def test_t4_interimar_alin_3_si_situatii_lipsa_sau_data_nepotrivita(monkeypatch):
    from core import bilant_api
    _cu_profil(monkeypatch)
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, zi, ref="calculeaza": _sold_activ_net(Decimal("40000")))
    monkeypatch.setattr(H, "interimare_distribuite", lambda cur, schema, an: Decimal("0"))
    corp = dict(CORP, data_hotarare="2026-07-10", termen_plata="2026-08-10")
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(interimar=True, brut="1000"), corp)
    assert e.value.camp == "op-data_situatii"
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(interimar=True, brut="1000"), dict(corp, data_situatii="2026-05-31"))
    assert "nu e sfârșit de trimestru" in str(e.value)
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(interimar=True, brut="1000"), dict(corp, data_situatii="2026-06-30"))
    assert "art. 69¹ alin. (3)" in str(e.value)


def test_t3_a_doua_repartizare_interimara_peste_disponibilul_trimestrului_e_refuzata(monkeypatch):
    from core import bilant_api
    _cu_profil(monkeypatch)
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, zi, ref="calculeaza": _sold_activ_net(Decimal("120000")))
    monkeypatch.setattr(H, "rezultat_cumulat", lambda cur, schema, la: Decimal("20000"))
    monkeypatch.setattr(H, "interimare_distribuite", lambda cur, schema, an: Decimal("15000"))
    corp = dict(CORP, data_hotarare="2026-07-10", data_situatii="2026-06-30", termen_plata="2026-08-10")
    d = H.date_document(_cur(), "s", _propunere(interimar=True, brut="5000"), corp)   # 20.000 − 15.000 = 5.000: egalitatea trece
    assert d["disponibil_interimar"] == Decimal("5000")
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(interimar=True, brut="5000.01"), corp)
    assert "depășește disponibilul trimestrului" in str(e.value) and "15.000,00 lei" in str(e.value)


def test_t8_sa_refuzata_motivat(monkeypatch):
    _cu_profil(monkeypatch, forma_juridica="SA", tip_firma="sa")
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(), dict(CORP))
    assert "«SA»" in str(e.value) and "SRL" in str(e.value) and e.value.unde == "Date firmă → Profil"


@pytest.mark.parametrize("cnp", ["", "1234567890123", "RO12345678"])
def test_beneficiar_ambiguu_sau_pj_nu_produce_hotarare(monkeypatch, cnp):
    _cu_profil(monkeypatch)
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(asociati=(("Ion Test", "1850101400017", "60"), ("Alfa", cnp, "40"))), dict(CORP))
    assert "Alfa" in str(e.value) and "art. 43 alin. (4)" in str(e.value) and e.value.unde == "Date firmă → Asociați"
    # [17.5-F6, corecția 1 pct.1] un CUI valid e o persoană juridică, spusă ca atare; un CNP lipsă sau invalid rămâne beneficiar neidentificat
    assert ("e persoană juridică" in str(e.value)) is DA.persoana_juridica(cnp) and ("nu e identificat" in str(e.value)) is not DA.persoana_juridica(cnp)


def test_f6c_beneficiarul_pj_cu_cui_valid_refuza_hotararea_ca_persoana_juridica(monkeypatch):
    """[17.5-F6, corecția 1 pct.1] Asociatul cu CUI valid (14399840): hotărârea e refuzată cu motivul „persoană juridică”, nu „CNP invalid”."""
    _cu_profil(monkeypatch)
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(asociati=(("Ion Test", "1850101400017", "60"), ("Proba Holding SRL", "14399840", "40"))), dict(CORP))
    assert "«Proba Holding SRL» e persoană juridică (CUI 14399840)" in str(e.value) and "nu se calculează" in str(e.value)
    assert "art. 43 alin. (4)" in str(e.value) and e.value.unde == "Date firmă → Asociați" and "CNP" not in str(e.value)


@pytest.mark.parametrize("camp, lipsa", [("termen_plata", "op-termen_plata"), ("modalitate_plata", "op-modalitate_plata"),
                                         ("administrator", "op-administrator"), ("exemplare", "op-exemplare"),
                                         ("loc_adunare", "op-loc_adunare"), ("prezenta", "op-prezenta"), ("vot", "op-vot"),
                                         ("aprobare_anuala", "op-aprobare_anuala"), ("numar_hotarare", "op-numar_hotarare")])
def test_lipsa_unei_informatii_spune_ce_lipseste_si_unde(monkeypatch, camp, lipsa):
    _cu_profil(monkeypatch)
    corp = dict(CORP)
    corp.pop(camp)
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(), corp)
    assert e.value.camp == lipsa


def test_capitalul_lipsa_e_lipsa_de_date_nu_zero(monkeypatch):
    _cu_profil(monkeypatch, capital_subscris=None)
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(), dict(CORP))
    assert "capitalul social subscris" in str(e.value) and e.value.unde == "Date firmă → Profil"


def test_administratorul_si_exemplarele_sugerate_din_profil():
    assert H.administrator_sugerat({"patron_nume": "Popescu Petru", "declarant_nume": "X"}) == "Popescu Petru"
    assert H.administrator_sugerat({"patron_nume": "", "declarant_nume": "Ionescu", "declarant_prenume": "Ion"}) == "Ionescu Ion"


def test_tabel_lung_pe_mai_multe_pagini_pastreaza_capul_si_totalul():
    asoc = tuple(("Asociat %02d" % i, "5") for i in range(1, 21))
    d = _date(asoc, "100000")
    pdf = H.pdf(d)
    from pypdf import PdfReader
    assert len(PdfReader(io.BytesIO(pdf)).pages) >= 2
    text = _pdf_text(pdf)
    assert "Asociat 20" in text and "Total 100% 100.000,00 16.000,00 84.000,00" in text


def test_documentul_nu_atinge_baza():
    """Descărcarea nu scrie: modulul nu are INSERT / UPDATE / DELETE, iar ruta deschide numai citiri (rollback)."""
    src = Path(H.__file__).read_text(encoding="utf-8")
    assert not re.search(r"\b(INSERT|UPDATE|DELETE)\b", src)
    uc = Path(H.__file__).with_name("uc_tenants.py").read_text(encoding="utf-8")
    corp = uc[uc.index("def hotarare_dividende("):uc.index("def _date_iso(")]
    assert "conn.rollback()" in corp and "commit" not in corp


# ───────────────────────── [17.5-F6, pct.6 (501)] plafonul numerarului, verificat la alegerea plății în numerar ─────────────────────────
class _Trecut(Exception):
    """Santinela: verificarea plății a trecut și documentul a ajuns la condițiile datate."""


def test_f6_numerar_peste_plafonul_zilnic_catre_o_persoana_fizica_e_refuzat(monkeypatch):
    """Legea 70/2015 art. 4 alin. (1) (dividendele către persoane fizice, 10.000 lei/zi către o persoană, `casa.PLAFON_PF`) și alin. (2)
    (plata fragmentată interzisă). T1: neturile 25.200,00 și 16.800,00 depășesc plafonul -> refuz pe câmpul modalității, cu ambii
    beneficiari, valoarea observată, limita și articolul; virament -> trece de verificare."""
    from core import casa
    _cu_profil(monkeypatch)
    monkeypatch.setattr(H, "conditii", lambda *a, **k: (_ for _ in ()).throw(_Trecut()))
    corp = dict(CORP, modalitate_plata="numerar")
    with pytest.raises(H.LipsaDate) as e:
        H.date_document(_cur(), "s", _propunere(), corp)
    m = str(e.value)
    assert e.value.camp == "op-modalitate_plata"
    assert "Ion Test (25.200,00 lei)" in m and "Maria Test (16.800,00 lei)" in m and _bani(casa.PLAFON_PF) + " lei" in m
    assert "art. 4 alin. (1)" in m and "alin. (2)" in m
    with pytest.raises(_Trecut):
        H.date_document(_cur(), "s", _propunere(), dict(CORP, modalitate_plata="virament"))


@pytest.mark.parametrize("brut, refuzat", [("23809.52", False), ("23809.54", True)])
def test_f6_numerar_la_limita_plafonului(monkeypatch, brut, refuzat):
    """La egalitate plata în numerar e permisă (net = plafon), un ban peste e refuzat. Brutul unic 23.809,52 -> impozit 3.809,52 (16%),
    net 20.000,00; doi asociați 50/50 -> 10.000,00 fiecare."""
    from core import casa
    _cu_profil(monkeypatch)
    monkeypatch.setattr(H, "conditii", lambda *a, **k: (_ for _ in ()).throw(_Trecut()))
    prop = _propunere(asociati=(("Ion Test", "1850101400017", "50"), ("Maria Test", "2870202400011", "50")), brut=brut)
    nets = [x["net"] for x in prop["nota"]["parti"]]
    assert (max(nets) > casa.PLAFON_PF) == refuzat, nets
    corp = dict(CORP, modalitate_plata="numerar")
    if refuzat:
        with pytest.raises(H.LipsaDate) as e:
            H.date_document(_cur(), "s", prop, corp)
        assert e.value.camp == "op-modalitate_plata"
    else:
        with pytest.raises(_Trecut):
            H.date_document(_cur(), "s", prop, corp)


# ───────────────────────── [17.5-F6, pct.6 (501)] numărul hotărârii pe două conexiuni, pe copia de test ─────────────────────────
F2_TID = 105780


def _copia_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (F2_TID,))
            return cur.fetchone() is not None
    except Exception:   # noqa: BLE001
        return False


def _schema_f2():
    from core import db
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (F2_TID,))
        return cur.fetchone()[0]


def _note_cu(schema, text):
    from core import db
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('SELECT id FROM "%s".inregistrari WHERE document_ref LIKE %%s ORDER BY id' % schema, (text + "%",))
        return [r[0] for r in cur.fetchall()]


def _sterge_note(schema, ids):
    from core import db
    if not ids:
        return
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('DELETE FROM "%s".inregistrari_linii WHERE inregistrare_id = ANY(%%s)' % schema, (ids,))
        cur.execute('DELETE FROM "%s".inregistrari WHERE id = ANY(%%s) AND status <> %%s' % schema, (ids, "validata"))
        c.commit()


@pytest.mark.skipif(not _copia_ok(), reason="copia de test indisponibilă")
@pytest.mark.parametrize("cu_blocaj", [True, False])
def test_f6_doua_emiteri_concurente_ale_aceluiasi_numar_pe_doua_conexiuni(cu_blocaj):
    """Emiterea alocă atomic identitatea firmă / an / număr: conexiunea A ia blocajul identității (`documente_interne.blocheaza_identitatea`),
    verifică numărul 9901 și scrie ciorna cu hotărârea din 02.11.2026, fără commit; conexiunea B, cu același număr și altă dată (03.11.2026),
    așteaptă blocajul până la commitul lui A și e refuzată (două hotărâri distincte nu primesc aceeași identitate). Martorul fără blocaj
    (forma de dinainte de F6) arată cursa: B nu așteaptă și trece verificarea înaintea scrierii lui A."""
    import threading
    from core import db, uc_tenants, repo_contabilitate, erori
    sch = _schema_f2()
    text = "Hotărârea adunării generale a asociaților nr 9901 din "
    _sterge_note(sch, _note_cu(sch, text))
    rez = {}

    def b():
        t0 = time.monotonic()
        try:
            with db.get_conn() as cb:
                uc_tenants._cere_numar_liber(cb, sch, "9901", dt.date(2026, 11, 3), False, blocheaza=cu_blocaj)
                cb.rollback()
            rez["b"] = "trecut"
        except erori.DateInvalide as e:
            rez["b"] = "refuzat: %s" % e
        rez["astept"] = time.monotonic() - t0

    try:
        with db.get_conn() as ca:
            uc_tenants._cere_numar_liber(ca, sch, "9901", dt.date(2026, 11, 2), False, blocheaza=cu_blocaj)
            with ca.cursor() as cur:
                repo_contabilitate.nota_operatiune_ciorna(cur, sch, dt.date(2026, 11, 2), "proba F6 numar concurent", document_ref=text + "02.11.2026")
            fir = threading.Thread(target=b)
            fir.start()
            time.sleep(1.5)   # B a pornit înainte ca A să comită
            ca.commit()
        fir.join(30)
        if cu_blocaj:
            assert rez["b"].startswith("refuzat") and "02.11.2026" in rez["b"] and rez["astept"] >= 1.0, rez
        else:
            assert rez["b"] == "trecut" and rez["astept"] < 1.0, rez   # cursa pe care o închide blocajul
    finally:
        _sterge_note(sch, _note_cu(sch, text))


@pytest.mark.skipif(not _copia_ok(), reason="copia de test indisponibilă")
def test_f6_previzualizarea_si_descarcarea_nu_creeaza_note_si_nu_muta_numarul():
    """Pe F2 (doi asociați): tabelul propunerii și cele două descărcări (Word, PDF) ale aceleiași hotărâri, de două ori, nu creează note și nu
    mută numărul sugerat; observat pe o a doua conexiune (numărătoarea notelor înainte și după)."""
    from core import db, uc_tenants
    sch = _schema_f2()

    def numar_note():
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute('SELECT count(*), COALESCE(max(id), 0) FROM "%s".inregistrari' % sch)
            return cur.fetchone()
    ctx = {"uid": 71507}
    corp = {"operatie": "dividend", "brut": "100", "data": "2026-11-20", "data_hotarare": "2026-11-20", "numar_hotarare": "9902", "interimar": "0",
            "aprobare_anuala": "nu", "termen_plata": "2026-12-20", "modalitate_plata": "virament", "loc_adunare": "sediul societății", "prezenta": "toti",
            "vot": "unanimitate", "administrator": "Popescu Petru", "exemplare": "3"}
    n0 = numar_note()
    sug0 = uc_tenants.dividende_impartire(F2_TID, corp, ctx)
    for _ in range(2):
        for fel in ("docx", "pdf"):
            try:
                uc_tenants.hotarare_dividende(F2_TID, corp, ctx, fel)
            except Exception as e:   # noqa: BLE001 — un refuz al documentului pe datele copiei nu e o scriere; proba numără notele
                assert "Lipsesc date" in str(e) or "nu se poate" in str(e) or "Distribuirea" in str(e), e
    sug1 = uc_tenants.dividende_impartire(F2_TID, corp, ctx)
    assert numar_note() == n0
    assert (sug0.get("numar_sugerat"), sug0.get("asociati")) == (sug1.get("numar_sugerat"), sug1.get("asociati"))


# ───────────────────────── [17.5-F6, T7] Legea 31/1990 art. 67 alin. (2³)–(2⁴): împrumuturile asociaților ─────────────────────────
@pytest.mark.parametrize("activ, blocat", [(Decimal("49999.99"), True), (Decimal("50000.00"), False), (Decimal("50000.01"), False)])
def test_t7_restituirea_imprumutului_sub_jumatate_din_capital_e_blocata(monkeypatch, activ, blocat):
    """Capital 100.000: activul net din situațiile anuale la 31.12.2025 sub 50.000 blochează restituirea din 2026 (alin. (2⁴)); egalitatea și
    peste trec. Data dinaintea Legii 239/2025 (17.12.2025) nu e blocată; capitalul necompletat sau situațiile necunoscute nu se presupun."""
    from core import bilant_api
    _cu_profil(monkeypatch, capital_subscris=Decimal("100000"))
    cerute = []
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, la: (cerute.append(la), _sold_activ_net(activ))[1])
    m = H.restituirea_imprumutului_blocata(_cur(), "s", dt.date(2026, 3, 10))
    assert cerute == [dt.date(2025, 12, 31)]
    assert (m is not None) == blocat, m
    if blocat:
        assert "art. 67 alin. (2⁴)" in m and _bani(activ) + " lei" in m and "50.000,00 lei" in m and "31.12.2025" in m
    assert H.restituirea_imprumutului_blocata(_cur(), "s", dt.date(2025, 12, 17)) is None
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, la: None)
    assert H.restituirea_imprumutului_blocata(_cur(), "s", dt.date(2026, 3, 10)) is None
    _cu_profil(monkeypatch, capital_subscris=None)
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, la: _sold_activ_net(Decimal("1")))
    assert H.restituirea_imprumutului_blocata(_cur(), "s", dt.date(2026, 3, 10)) is None


@pytest.mark.skipif(not _copia_ok(), reason="copia de test indisponibilă")
def test_t7_apelul_direct_al_restituirii_e_refuzat_iar_primirea_trece(monkeypatch):
    """Pe ruta reală a notei (`uc_tenants.nota_asociati`, F2): cu capitalul subscris peste dublul activului net de la 31.12.2025, restituirea
    e refuzată pe server cu temeiul, lângă câmpul «Sens», fără notă; primirea unui împrumut de la asociat rămâne permisă (alin. (2⁴) privește
    numai restituirea). Situația anuală la 31.12.2025 e dată probei: copia n-o are. Acordarea unui împrumut către asociați sau afiliați (alin. (2³)) nu are operație în aplicație (Decontări asociați:
    primire / restituire; Credite bancare: numai creditul bancar): limita v1, fără flux nou."""
    from core import uc_tenants, erori, bilant_api, db
    sch = _schema_f2()
    # copia nu are situațiile anuale la 31.12.2025 pentru nicio firmă (soldurile preluate sunt din 2026): situația de la acea dată e dată
    # probei (capital 100.000, activ net 49.999,99), restul drumului — ruta, accesul, soldurile curente, refuzul, nota — e cel real
    real_sold, real_profil = bilant_api.sold_la, H.profil_firma
    monkeypatch.setattr(bilant_api, "sold_la", lambda cur, schema, la: _sold_activ_net(Decimal("49999.99")) if la == dt.date(2025, 12, 31)
                        else real_sold(cur, schema, la))
    monkeypatch.setattr(H, "profil_firma", lambda cur, schema: dict(real_profil(cur, schema), capital_subscris=Decimal("100000")))
    text = "proba F6 T7 %d" % int(time.time())
    corp = {"operatie": "imprumut", "fel": "restituire", "suma": "1", "dobanda": "0", "data": "2026-11-20", "descriere": text}
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.nota_asociati(F2_TID, corp, {"uid": 71507})
    d = e.value.args[0]
    assert isinstance(d, dict) and "art. 67 alin. (2⁴)" in d["mesaj"] and d["erori_campuri"][0]["camp"] == "op-fel", d
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".inregistrari WHERE descriere = %%s' % sch, (text,))
        assert cur.fetchone()[0] == 0
    try:
        r = uc_tenants.nota_asociati(F2_TID, dict(corp, fel="primire", descriere=text + " primire"), {"uid": 71507})
        assert r.get("inregistrare_id") or r.get("id") or r, r
    finally:
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute('SELECT id FROM "%s".inregistrari WHERE descriere LIKE %%s' % sch, (text + "%",))
            ids = [x[0] for x in cur.fetchall()]
        _sterge_note(sch, ids)


# ───────────────────────── [17.5-F6, corecția 1 pct.1] beneficiarul persoană juridică: regimul nu se calculează ─────────────────────────
@pytest.mark.parametrize("cod, pj", [("14399840", True), ("RO14399840", True), ("14399841", True), ("1850101400017", False), ("", False),
                                     ("1234567890123", False)])
def test_f6c_persoana_juridica_e_regula_ecranului_asociatilor(cod, pj):
    """Persoana juridică = aceeași regulă ca ecranul Date firmă → Asociați (`asociati_api._tip`): un cod nevid care nu e CNP de 13 cifre (CUI,
    cu sau fără RO, chiar cu cifra de control greșită); un CNP de 13 cifre, valid sau nu, și codul lipsă nu sunt persoană juridică."""
    from core import asociati_api
    assert DA.persoana_juridica(cod) is pj
    assert (asociati_api._tip(cod) == "juridica") is pj


@pytest.mark.skipif(not _copia_ok(), reason="copia de test indisponibilă")
def test_f6c_pj_propunerea_fara_impozit_net_si_total_iar_nota_refuzata(monkeypatch):
    """Pe F2 (ruta reală a propunerii și a notei), cu al doilea asociat persoană juridică (CUI 14399840, 40%): rândul lui nu are impozit și net,
    ci textul că regimul dividendelor către o persoană juridică nu se calculează; totalul impozitului și al netului nu se arată, cu motivul;
    rândul persoanei fizice păstrează impozitul cu cota registrului. Nota de dividende e refuzată cu motivul și nu se scrie nimic."""
    from core import uc_tenants, erori, db, repo_d205
    sch = _schema_f2()
    monkeypatch.setattr(repo_d205, "select_asociati", lambda cur: [{"nume": "Ion Test", "cnp": "1850101400017", "cota": Decimal("60")},
                                                                   {"nume": "Proba Holding SRL", "cnp": "14399840", "cota": Decimal("40")}])
    ctx = {"uid": 71507}
    text = "proba F6 PJ %d" % int(time.time())
    corp = {"operatie": "dividend", "brut": "100", "data": "2026-11-20", "data_hotarare": "2026-11-20", "numar_hotarare": "9903", "interimar": "0",
            "descriere": text}
    p = uc_tenants.dividende_impartire(F2_TID, corp, ctx)
    pf, pj = {a["nume"]: a for a in p["asociati"]}["Ion Test"], {a["nume"]: a for a in p["asociati"]}["Proba Holding SRL"]
    cota = C.cota("impozit_dividend", dt.date(2026, 11, 20))[0]
    assert pj["impozit"] is None and pj["net"] is None and pj["regim"] == DA.REGIM_PJ and pj["brut"] == "40.00", pj
    assert "persoană juridică nu se calculează" in pj["regim"]
    assert pf["impozit"] == str(_q(Decimal("60") * cota)) and pf["net"] == str(Decimal("60.00") - _q(Decimal("60") * cota)) and "regim" not in pf
    assert p["impozit"] is None and p["net"] is None and p["regim_total"] == DA.TOTAL_FARA_PJ and p["brut"] == "100.00", p
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.nota_asociati(F2_TID, corp, ctx)
    assert "«Proba Holding SRL» e persoană juridică" in str(e.value.args[0]) and "nu se generează" in str(e.value.args[0])
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".inregistrari WHERE descriere = %%s' % sch, (text,))
        assert cur.fetchone()[0] == 0
