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
