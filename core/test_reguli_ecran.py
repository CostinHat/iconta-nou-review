# -*- coding: utf-8 -*-
"""GARD [28.08.2026]: cele două reguli de ecran scrise azi — E1 și E2 (`DESIGN_SYSTEM.md` cap.26/27).

  **E1** — *două lucruri diferite primesc două nume distincte.* Când aceeași entitate are un atribut
  în două locuri, ecranul nu alege tăcut între ele: le arată pe amândouă, cu etichete care spun de
  unde vine fiecare, iar când diferă spune **care produce efectul**.
  **E2** — *un act cu efect asupra unei entități se încheie cu o confirmare vizibilă care numește
  entitatea și consecința.* Demontarea ecranului nu e confirmare.

CE FACE IMPOSIBIL:
  1. un nod care declară o pereche E1 și nu spune care sursă produce efectul;
  2. un nod care declară o pereche și **tace** despre una din surse — nici arătată, nici declarată
     lipsă (forma din care s-a născut F1: caseta spunea că denumirea din portofoliu pleacă în
     documente, iar denumirea fiscală nici nu era pomenită);
  3. dispariția perechii de pe **toate** ecranele — anti-vacuu: gardul ar rămâne verde păzind nimic;
  4. creșterea numărului de acte de nivel firmă care se termină în tăcere, **și** scăderea lui
     netrecută prin clichet;
  5. golirea clasei de acte prin redenumirea unei rute — numărul actelor găsite e el însuși clichet.

CE NU FACE, declarat:
  - **nu judecă TEXTUL confirmării.** Regula cere ca mesajul să numească entitatea și consecința;
    gardul cere doar să existe. „Salvat" trece pe mecanică și pică la citire — iar citirea e a lui
    Costin, nu a instrumentului. (Aceeași limită ca la R82: *„nu spune nimic despre ecranele care
    confirmă cu un text prea slab, fiindcă acolo criteriul e altul."*)
  - **nu e un parser de JavaScript.** Vezi limita scrisă în `core/scan_ecran_reguli.py`.
  - **nu acoperă R63.** Cele două adrese de email trăiesc pe două ecrane diferite, prin decizia (c)
    a restanței; regula „același nod le arată pe amândouă" n-are ce asereze acolo, și se spune.
"""
import io
import os

from core import scan_ecran_reguli as s

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _coduri(lipsuri):
    """Codurile, nu frazele. O gardă care compară mesajul se rupe la prima reformulare — și se
    rupe în direcția comodă, fiindcă un mesaj schimbat nu mai e găsit și lista pare goală."""
    return sorted(cod for cod, _mesaj in lipsuri)


# ────────────────────────────────────────────────── clichetele, pe arborele real
def test_E1_niciun_nod_isi_declara_perechea_pe_jumatate():
    neconforme, _ner = s.scaneaza_e1()
    assert not neconforme, (
        "noduri care declară o pereche E1 și n-o duc până la capăt (%d):\n  %s"
        % (len(neconforme), "\n  ".join("%s:%d [%s] %s — %s" % r for r in neconforme)))


def test_E1_perechea_din_registru_chiar_se_randeaza_undeva():
    """Anti-vacuu. O pereche ștearsă din toate ecranele ar lăsa gardul verde despre o lume pe care
    n-o mai vede — chiar forma numită în [[gard-care-nu-se-verifica-pe-sine]]."""
    _nec, nerandate = s.scaneaza_e1()
    assert not nerandate, (
        "perechi declarate în `PERECHI` pe care niciun ecran nu le mai arată: %s — ori s-a șters "
        "un ecran, ori registrul a rămas în urmă. Gardul nu are voie să rămână verde pe niciuna."
        % nerandate)


def test_E2_actele_de_nivel_firma_nu_se_inmultesc_in_tacere():
    fara, toate = s.scaneaza_e2()
    assert len(fara) <= s.CLICHET_E2_FARA_CONFIRMARE, (
        "acte de nivel firmă care se termină fără confirmare vizibilă: %d, clichetul e %d.\n  %s\n"
        "Cu cât actul e mai puțin reversibil, cu atât confirmarea e mai obligatorie (DS cap.27)."
        % (len(fara), s.CLICHET_E2_FARA_CONFIRMARE,
           "\n  ".join("%s:%d %s %s" % r for r in fara)))
    assert len(toate) == s.CLICHET_E2_ACTE, (
        "[anti-vacuu] clasa actelor de nivel firmă are %d membri, nu %d — o rută redenumită ar goli "
        "clasa, iar clichetul ar coborî la zero arătând ca o reparație. Actele găsite:\n  %s"
        % (len(toate), s.CLICHET_E2_ACTE, "\n  ".join("%s:%d %s %s" % r[:4] for r in toate)))


def test_TOATE_actele_de_nivel_firma_CONFIRMA():
    """[R82, închisă 28.08.2026] Testul ăsta a înlocuit două: unul care număra actele tăcute în
    direcția „nu crește", și unul care pina **mulțimea** celor patru. Amândouă erau corecte cât timp
    clasa era nevidă; la zero, primul devine tautologie, iar al doilea n-are ce să pineze.

    Ce are conținut acum e afirmația inversă: **fiecare** act de nivel firmă confirmă, și se vede
    **cum**. Un act care ar pierde confirmarea reapare aici cu numele lui, nu ca o cifră care crește.
    """
    _fara, toate = s.scaneaza_e2()
    tacute = [(r[0], r[1], r[3]) for r in toate if not r[4]]
    assert not tacute, (
        "acte de nivel firmă care se termină în tăcere (%d):\n  %s\n"
        "Demontarea ecranului nu e confirmare (DS cap.27). Cu cât actul e mai puțin reversibil, cu "
        "atât confirmarea e mai obligatorie." % (len(tacute), "\n  ".join("%s:%d %s" % x for x in tacute)))


def test_cele_PATRU_acte_reparate_confirma_prin_BANNER_nu_prin_arataMesaj():
    """Cele patru se termină cu `nav.acasa()`, adică **ecranul lor dispare**. Un `arataMesaj`
    obișnuit scrie într-o zonă care e demontată odată cu el — deci ar fi trecut mecanic și n-ar fi
    fost văzut de nimeni. Confirmarea trebuie să supraviețuiască navigării, iar singurul mecanism
    care o face aici e banner-ul pe `document.body`.

    De-aia gardul cere **cum**, nu doar **dacă**: e chiar diferența dintre o confirmare și una care
    pare o confirmare."""
    _fara, toate = s.scaneaza_e2()
    reparate = {"/tenants/{}/nume-ales", "/tenants/{}", "/tenants/{}/activare"}
    interes = [r for r in toate if r[3] in reparate and r[2] in ("api.post", "api.del")
               and r[0].endswith("firme.js")]
    # cele patru + reactivarea (care confirma prin `arataMesaj`, si e legitim: ecranul ei NU se
    # demonteaza inainte de mesaj — asa a fost scrisa pe 26.08 si asa functioneaza)
    prin_banner = [r for r in interes if r[6].count("_bannerFirma")]
    assert len(prin_banner) >= 4, (
        "doar %d din actele de nivel firmă din `firme.js` confirmă printr-un banner care "
        "supraviețuiește navigării:\n  %s" % (len(prin_banner),
                                              "\n  ".join("%s:%d %s -> %s" % (r[0], r[1], r[3], r[5])
                                                          for r in interes)))
    assert all(r[4] for r in interes), "un act din firme.js nu mai confirmă deloc"


# ────────────────────────────────────────────────── calibrare: E1, ambele direcții
_E1_COMPLET = """
function f() {
  corp.innerHTML = `<div data-e1="denumire-firma">
      <b data-e1-sursa="portofoliu">${a}</b>
      <b data-e1-sursa="fiscal">${b}</b>
      <span data-e1-efect="fiscal">asta pleacă pe hârtie</span>
    </div>`;
}
"""


def test_CALIBRARE_E1_nodul_complet_NU_e_raportat():
    assert s.perechi_pe_ecran(_E1_COMPLET) == [(3, "denumire-firma", [])]


def test_CALIBRARE_E1_fara_efect_e_raportat():
    """Modul de eșec propriu regulii: arată amândouă și **nu spune care contează**."""
    sursa = _E1_COMPLET.replace('<span data-e1-efect="fiscal">asta pleacă pe hârtie</span>', "")
    (_ln, _ch, lipsuri), = s.perechi_pe_ecran(sursa)
    assert _coduri(lipsuri) == ["efect"], lipsuri


def test_CALIBRARE_E1_sursa_nepomenita_e_raportata_iar_una_DECLARATA_lipsa_nu():
    """Cele două forme se despart aici: tăcerea despre o sursă e defectul (F1), declararea ei
    lipsă e forma corectă pentru un ecran care n-are valoarea (lista de firme)."""
    tacere = _E1_COMPLET.replace('<b data-e1-sursa="fiscal">${b}</b>', "")
    (_ln, _ch, lipsuri), = s.perechi_pe_ecran(tacere)
    assert _coduri(lipsuri) == ["sursa-tacuta"], lipsuri

    declarata = _E1_COMPLET.replace('<b data-e1-sursa="fiscal">${b}</b>',
                                    '<span data-e1-absent="fiscal">nu se vede aici</span>')
    assert s.perechi_pe_ecran(declarata) == [(3, "denumire-firma", [])]


def test_CALIBRARE_E1_nodul_fara_nicio_valoare_e_raportat():
    sursa = """function f() { corp.innerHTML = `<div data-e1="denumire-firma">
        <span data-e1-absent="portofoliu">x</span><span data-e1-absent="fiscal">y</span>
        <i data-e1-efect="fiscal">z</i></div>`; }"""
    (_ln, _ch, lipsuri), = s.perechi_pe_ecran(sursa)
    assert _coduri(lipsuri) == ["fara-valoare"], lipsuri


def test_CALIBRARE_E1_pereche_nedeclarata_in_registru():
    sursa = _E1_COMPLET.replace('data-e1="denumire-firma"', 'data-e1="ceva-nou"')
    (_ln, cheie, lipsuri), = s.perechi_pe_ecran(sursa)
    assert (cheie, _coduri(lipsuri)) == ("ceva-nou", ["nedeclarata"])


def test_CALIBRARE_E1_un_marcaj_din_COMENTARIU_sau_din_SIR_nu_conteaza():
    """Direcția «raportează ce nu e»: gardul citește noduri de randare, nu text. Un exemplu scris
    într-un comentariu de documentare ar fi trecut la orice `"data-e1" in sursă`."""
    comentariu = '// exemplu: `<div data-e1="denumire-firma"></div>`\nvar x = 1;\n'
    assert s.perechi_pe_ecran(comentariu) == []
    sir = 'var ajutor = "<div data-e1=\\"denumire-firma\\"></div>";\n'
    assert s.perechi_pe_ecran(sir) == []


# ────────────────────────────────────────────────── calibrare: E2, ambele direcții
_DOMENIU = ("/tenants/{}/activare",)

_E2_TACUT = """
b.addEventListener("click", async () => {
  try {
    await api.post(`/tenants/${t.id}/activare`, { activ: false });
    nav.acasa();
  } catch (e) {
    arataMesaj(zm, "Nu am putut dezactiva firma.", "eroare");
  }
});
"""


def test_CALIBRARE_E2_confirmarea_din_CATCH_nu_confirma_nimic():
    """**Modul de eșec propriu construcției**, și chiar defectul din R82: toate patru actele tăcute
    au `arataMesaj` pe calea de eroare. Un gard care s-ar uita în handler, nu în blocul `try`, le-ar
    declara pe toate confirmate — și ar fi verde exact pe clasa pe care a fost construit s-o vadă."""
    (ln, apel, ruta, confirmat, in_try, _conf), = s.acte(_E2_TACUT, _DOMENIU)
    assert (apel, ruta, confirmat, in_try) == ("api.post", "/tenants/{}/activare", False, True)
    assert ln == 4


def test_CALIBRARE_E2_confirmarea_din_TRY_confirma():
    sursa = _E2_TACUT.replace("    nav.acasa();",
                              '    arataMesaj(zm, "«X» e din nou în portofoliu.", "ok");')
    (_ln, _apel, _ruta, confirmat, _t, _conf), = s.acte(sursa, _DOMENIU)
    assert confirmat is True


def test_CALIBRARE_E2_bannerul_conteaza_si_el_ca_confirmare():
    sursa = _E2_TACUT.replace("    nav.acasa();", "    _bannerFirmaCreata(nume);")
    (_ln, _apel, _ruta, confirmat, _t, _conf), = s.acte(sursa, _DOMENIU)
    assert confirmat is True


def test_CALIBRARE_E2_un_arataMesaj_din_COMENTARIU_nu_confirma():
    """A doua față a aceleiași greșeli: un `"arataMesaj" in bloc` ar fi trecut peste un comentariu
    care spune «aici ar trebui un arataMesaj»."""
    sursa = _E2_TACUT.replace("    nav.acasa();",
                              "    // de făcut: arataMesaj(zm, ...) după succes\n    nav.acasa();")
    (_ln, _apel, _ruta, confirmat, _t, _conf), = s.acte(sursa, _DOMENIU)
    assert confirmat is False


def test_CALIBRARE_E2_un_act_din_afara_domeniului_nu_se_numara():
    sursa = _E2_TACUT.replace("/activare", "/vector")
    assert s.acte(sursa, _DOMENIU) == []


def test_CALIBRARE_E2_un_act_FARA_try_e_vazut_si_marcat():
    sursa = """
b.addEventListener("click", async () => {
  await api.post(`/tenants/${t.id}/activare`, { activ: false });
  nav.acasa();
});
"""
    (_ln, _apel, _ruta, confirmat, in_try, _conf), = s.acte(sursa, _DOMENIU)
    assert (confirmat, in_try) == (False, False), "un act fără `try` n-are voie să treacă neluat"


# ────────────────────────────────────────────────── calibrare: tokenizatorul
def test_CALIBRARE_expresia_regulata_nu_deplaseaza_blocurile():
    """Punctul cel mai fragil al construcției: un `/` de expresie regulată luat drept împărțire
    (sau invers) ar muta capetele blocurilor, iar rezultatul ar arăta plauzibil. `{4}` din
    cuantificator e chiar acoladă."""
    sursa = """
try {
  const re = /^\\d{4}-\\d{2}$/;
  const cat = total / 2;
  await api.post(`/tenants/${id}/activare`, {});
} catch (e) { arataMesaj(z, "x", "eroare"); }
"""
    (_ln, _apel, _ruta, confirmat, in_try, _conf), = s.acte(sursa, _DOMENIU)
    assert (confirmat, in_try) == (False, True)


def test_CALIBRARE_sabloanele_imbricate_nu_rup_arborele():
    """`${cond ? `text ${x}` : ""}` — un șablon în interiorul interpolării altui șablon. Fără
    stivă, prima ghilimea inversă închisă ar închide șablonul de afară și tot restul fișierului
    ar deveni «cod»."""
    sursa = ('function f(){ corp.innerHTML = `<div data-e1="denumire-firma">'
             '${z ? `<i>${q}</i>` : ""}'
             '<b data-e1-sursa="portofoliu">${a}</b>'
             '<b data-e1-sursa="fiscal">${b}</b>'
             '<u data-e1-efect="fiscal">x</u></div>`; }')
    assert s.perechi_pe_ecran(sursa) == [(1, "denumire-firma", [])]


def test_CALIBRARE_acoladele_din_interpolare_nu_inchid_blocul():
    sursa = """
try {
  const x = `${lista.map((r) => { return r.n; }).join("")}`;
  await api.post(`/tenants/${id}/activare`, {});
} catch (e) { arataMesaj(z, "x", "eroare"); }
"""
    (_ln, _apel, _ruta, confirmat, in_try, _conf), = s.acte(sursa, _DOMENIU)
    assert (confirmat, in_try) == (False, True)


def test_ANTI_VACUU_scanul_chiar_vede_ecranele():
    fisiere = s._fisiere_ecran()
    assert len(fisiere) >= 10, "scanul vede doar %d ecrane — s-a rupt calea" % len(fisiere)
    assert all(io.open(f, encoding="utf-8").read() for f in fisiere)


def test_regula_e_SCRISA_unde_o_cauta_omul():
    """O regulă păzită și nescrisă e la fel de fragilă ca una scrisă și nepăzită (METODA §14):
    cine citește gardul trebuie să găsească regula, cu numărul ei de capitol."""
    ds = io.open(os.path.join(_RAD, "DESIGN_SYSTEM.md"), encoding="utf-8").read()
    capitole = {r.split(".")[0].strip() for r in ds.split("\n## ")[1:]}
    assert {"26", "27"} <= capitole, (
        "capitolele 26 (E1) și 27 (E2) nu mai sunt în DESIGN_SYSTEM.md: %s"
        % sorted(c for c in capitole if c.isdigit()))
