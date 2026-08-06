# -*- coding: utf-8 -*-
"""core/test_garzi_tacere_ui.py — GARDURI STATICE anti tacere-la-esec + info-leak in UI (JS).

Nu exista harness JS (suita e pytest); gardul scaneaza SURSA static/js si asigura ca tiparul-bug
(clasa) e absent. RED pe sursa buggy, GREEN dupa fix, mutatie = reintroducerea tiparului pica.
Campanie C-5 fix bug-uri B1-B17 + info-leak (bug-uri, NU goluri de conformitate).
"""
import glob
import io
import re
import os
import pytest

_ECRANE = sorted(glob.glob("static/js/ecrane/*.js"))


def _read(f):
    return io.open(f, encoding="utf-8").read()


def _skip_daca_lipsa():
    if not _ECRANE:
        pytest.skip("static/js/ecrane absent (rulare in afara radacinii repo)")


def _fn_body(src, marker):
    """Corpul functiei top-level care incepe cu `marker`, pana la urmatoarea declaratie de functie."""
    i = src.index(marker)
    rest = src[i + len(marker):]
    m = re.search(r"\n(?:export\s+)?(?:async\s+)?function\s", rest)
    return src[i: i + len(marker) + (m.start() if m else len(rest))]


# ============================================================
#  INFO-LEAK: JSON.stringify (sau echivalent) al unui obiect de date intr-un mesaj vizibil
# ============================================================
def test_fara_payload_in_mesaj_utilizator():
    """Clasa: un obiect de date (payload cerere / avertisment) serializat in mesajul aratat userului =
    scurgere de informatie. Situri istorice: operatiuni_ecran:382 (arataMesaj + JSON.stringify(corpReq)),
    declaratii:219 si firme:846 (fallback || JSON.stringify(obj) in innerHTML). NICIUN mesaj-UI nu
    serializeaza un obiect. (Payload-urile legitime - body cerere, sessionStorage, URLSearchParams - NU
    sunt in acest tipar si raman permise.)"""
    _skip_daca_lipsa()
    reclamatii = []
    for f in _ECRANE:
        src = _read(f)
        for m in re.finditer(r"arataMesaj\([^;\n]*JSON\.stringify", src):
            reclamatii.append("%s: arataMesaj cu JSON.stringify (payload in mesaj)" % os.path.basename(f))
        for m in re.finditer(r"\|\|\s*JSON\.stringify\(", src):
            reclamatii.append("%s: fallback '|| JSON.stringify(obj)' (dump obiect in UI)" % os.path.basename(f))
    assert not reclamatii, "INFO-LEAK payload in mesaj utilizator: %s" % sorted(set(reclamatii))


# ============================================================
#  B7: handler de load care referea o variabila DOM nedeclarata in scope (ReferenceError)
# ============================================================
def test_b7_produse_load_fara_zona_nedeclarata():
    """B7: randeazaProduse (functia de load) referea `zona` - declarata doar in randeazaLista/
    formularAdauga, nu in ea -> ReferenceError, handler-ul crapa, iar codul continua la randarea listei
    goale (parea reusit). Fix: stare-goala cap.6 in `corp` + return. Gardul: functia de load NU mai
    referi `zona`. (Class-hunt: singurul sit arataMesaj(zona) out-of-scope; restul sunt closure-uri cu
    zona declarata in functia inconjuratoare.)"""
    _skip_daca_lipsa()
    src = _read("static/js/ecrane/produse_ecran.js")
    body = _fn_body(src, "export async function randeazaProduse")
    assert "arataMesaj(zona" not in body, "B7: randeazaProduse inca referi 'zona' nedeclarata (ReferenceError)"


# ============================================================
#  B8: camp obligatoriu (asterisc) nevalidat -> salveaza NULL/gol ca succes (minte ca a reusit)
# ============================================================
def test_b8_flux_concediu_valideaza_data_sfarsit():
    """B8: cm-sfarsit (marcat obligatoriu) nu era validat -> data_sfarsit=NULL salvat ca succes.
    Fix: validare preventiva (prezenta + ordine) cu msg-eroare cap.6 inainte de submit. Class: campuri
    cu asterisc care salveaza tacut default/NULL ca succes (vezi si etransport valoare_fara_tva,
    firme sn-salariu_brut - marcate in P6 Gap dir.2)."""
    _skip_daca_lipsa()
    src = _read("static/js/ecrane/flux_concediu.js")
    assert "if (!sfarsit)" in src, "B8: cm-sfarsit inca nevalidat (salveaza data_sfarsit=NULL ca succes)"


# ============================================================
#  B14: operatie secundara (upload) inghitita cu catch{} in timp ce primarul zice succes
# ============================================================
def test_b14_raporteaza_upload_esec_semnalat():
    """B14: urcaPoze inghitea esecul (catch{}) iar apelantul zicea 'Sesizare trimisa' -> atasamente
    pierdute tacut sub un succes fals. Fix: numara esecurile, mesaj de avertisment cap.6 la pierdere.
    Class: operatie secundara care esueaza tacut sub un mesaj de succes al primarului."""
    _skip_daca_lipsa()
    src = _read("static/js/ecrane/raporteaza.js")
    assert "} catch {}" not in src.split("urcaPoze", 1)[-1][:400], "B14: urcaPoze inca inghite upload-ul (catch{})"
    assert "nu s-au încărcat" in src, "B14: lipseste semnalarea imaginilor pierdute (succes fals)"


# ============================================================
#  B17 (backend): d406 arunca flag-ul _um_stiut -> UM necunoscuta devine H87 tacut
# ============================================================
def test_b17_d406_um_necunoscuta_numita():
    """B17: caller-ul arunca `_um_stiut` din uom_unece -> UM necunoscuta -> H87 tacut (aceeasi clasa cu
    bug-ul din iulie: unitati gresite in D406). Fix: flag consumat + avertisment care NUMESTE unitatile
    inlocuite (ca `strain`)."""
    from core.d406 import uom_unece, UOM_IMPLICIT
    assert uom_unece("unitate-inexistenta-xyz") == (UOM_IMPLICIT, False)
    assert uom_unece("KGM")[1] is True and uom_unece("")[1] is False
    src = _read("core/d406.py")
    assert "um_necunoscute" in src, "B17: flag-ul UM necunoscute nu e consumat (fallback H87 tacut)"


# ============================================================
#  B1-B3: catch gol care goleste panoul / seteaza gol tacut (esec indistinct de gol real)
# ============================================================
def test_b2_b3_declaratii_fara_panou_gol_tacut():
    """B2/B3: randeazaClasificareD390/D301 faceau `catch { zona.innerHTML=''; return; }` -> panou golit
    tacut la esec (arata ca gol real). Fix: stare-goala cap.6 cu cauza + reincarca."""
    _skip_daca_lipsa()
    src = _read("static/js/ecrane/declaratii.js")
    assert 'catch { zona.innerHTML = ""; return; }' not in src, "B2/B3: inca goleste panoul tacut la esec"


def test_b1_declaratii_distinge_eroare_de_gol():
    """B1: incarcaTipuri seta tipuri=[] tacut la esec -> confundat cu 'nicio declaratie'. Fix: flag
    S.tipuriEsuat distinge eroarea de golul real."""
    _skip_daca_lipsa()
    assert "S.tipuriEsuat" in _read("static/js/ecrane/declaratii.js"), "B1: nu distinge eroare de gol"


# ============================================================
#  B9: e.message inghite {mesaj} (api.js arunca {cod,mesaj}) -> mesaje specifice pierdute
# ============================================================
def test_b9_e_mesaj_inainte_de_e_message():
    """B9: handlere citeau `e.message` (undefined cand api.js arunca {cod,mesaj}) -> erorile specifice se
    pierdeau. Fix (clasa): `e.mesaj || e.message` peste tot. Guard: niciun `(e && e.message)` fara mesaj."""
    _skip_daca_lipsa()
    for f in ("migrare.js", "facturi_ecran.js"):
        src = _read("static/js/ecrane/%s" % f)
        assert "(e && e.message)" not in src, "B9: %s inca citeste e.message fara e.mesaj" % f
    assert "e.mesaj || e.message" in _read("static/js/ecrane/firme.js"), "B9: firme.js nu a fost aliniat"


# ============================================================
#  Lot 3 (item 8): B4-B6, B10-B13, B15-B16 - restul silentelor
# ============================================================
def test_b4_b5_main_notif_nu_inghitit():
    """B4/B5: notificarea pregatitorului dupa aproba/respinge era inghitita (except: pass). Fix: logata
    (observabil), nu tacut. (Actiunea primara reuseste; esecul notificarii se logheaza.)"""
    assert "notificare pregatitor esuata" in _read("main.py"), "B4/B5: notificarea inca inghitita tacut"


def test_b6_b12_load_esec_stare_de_eroare():
    """B6/B13 (admin_activitate) + B12 (control): `catch {}` la load -> panou golit / verdict fals-curat,
    indistinct de gol/curat real. Fix: stare-goala de eroare + return."""
    _skip_daca_lipsa()
    assert "Nu am putut încărca istoricul cabinetului" in _read("static/js/ecrane/admin_activitate.js"), "B6/B13 nereparat"
    assert "Nu am putut încărca controlul fiscal" in _read("static/js/ecrane/control.js"), "B12 nereparat"


def test_b10_b11_input_gol_cu_mesaj():
    """B10 (produse denumire) + B11 (portal solicitare): input obligatoriu gol -> no-op/focus tacit.
    Fix: mesaj cap.6 la submit gol."""
    _skip_daca_lipsa()
    assert "Completează denumirea produsului" in _read("static/js/ecrane/produse_ecran.js"), "B10 nereparat"
    p = _read("static/js/ecrane/portal.js")
    assert 'id="sol-msg"' in p and "Scrie solicitarea" in p, "B11 nereparat"


def test_b15_b16_actiune_esec_cu_mesaj():
    """B15 (admin_raportari inchide) + B16 (raporteaza raspuns-in-fir): `catch { btn.disabled=false }`
    reactiva butonul fara mesaj. Fix: mesaj inline la esec."""
    _skip_daca_lipsa()
    assert "Nu am putut închide sesizarea" in _read("static/js/ecrane/admin_raportari.js"), "B15 nereparat"
    assert "Nu am putut trimite răspunsul" in _read("static/js/ecrane/raporteaza.js"), "B16 nereparat"
