# -*- coding: utf-8 -*-
"""GARD — „Nu ai voie să slăbești, să ocolești sau să ștergi un test ca să treacă poarta” (comanda Costin 11.2, forma a doua, regula 3d,
verbatim în DECIZII „Comanda 11.2, forma a doua”).

Verbatim: *„Lotul se duce până la capăt fără oprire. Dacă poarta pică, repari codul și o rulezi din nou, până trece. Nu ai voie să
slăbești, să ocolești sau să ștergi un test ca să treacă poarta. Te oprești doar dacă reparația ar cere schimbarea unui comportament deja
decis sau o operație care nu se poate anula.”*

DE CE MECANIC: regula 3d scoate limita de două rulări pe lot — poarta se reia până la verde. Fără gardă, cea mai scurtă cale spre verde
devine slăbirea testului roșu (pe 31.07 poarta „pytest && git commit” a fost ocolită prin subset; CLAUDE.md, CICLUL DE NECONFORMITATE).

CE COMPARĂ: fiecare test care exista la INTRAREA LOTULUI (`git merge-base HEAD main` — ce e publicat) față de arborele de acum, numai pe
fișierele de test schimbate de atunci (`git diff --name-status`):
  (1) testul există încă (în același fișier sau, mutat, oriunde în arbore — cu același nume);
  (2) n-a pierdut aserțiuni: numărul de `assert` + `pytest.raises` / `pytest.fail` / `pytest.warns` din corp nu scade;
  (3) n-a primit `skip` / `skipif` / `xfail` / `pytest.skip()` / `pytest.xfail()` / `pytest.importorskip()` pe care nu-l avea;
  (4) nicio ocolire a colectării: `collect_ignore`, `pytest_collection_modifyitems`, `pytest_ignore_collect`, `--deselect`, `--ignore`,
      `-k ` în conftest-uri / configurarea pytest / `scripts/githooks/poarta-suita` nu cresc față de intrare.
EXCEPȚIA: o intrare în `MOTIVATE` de mai jos, `"<fișier>::<test>": "<motiv>"` — de ex. testul unei rute scoase prin decizia lui Costin,
cu decizia numită. Motivul stă AICI, într-un singur loc, vizibil în diff; o excepție fără abatere (stale) pică și ea.

LIMITĂ DECLARATĂ: (a) numărarea e statică — un `assert` mutat într-o funcție ajutătoare se vede ca aserțiune scoasă (fals pozitiv, se
motivează), iar o aserțiune înlocuită cu una mai slabă (`==` -> `in`, o toleranță mărită) nu se vede; (b) cazurile scoase dintr-un
`parametrize` nu se numără; (c) un test redenumit apare ca șters (se motivează cu numele nou). COLLECTED-ul real (rulat) rămâne în
raportul porții (CLAUDE.md §2.2 sect.2).
"""
import ast
import io
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RE_TEST = re.compile(r"(^|/)(test_[^/]*|e2e_[^/]*|conftest)\.py$")
CONFIG = ("pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini", "scripts/githooks/poarta-suita")
_RE_OCOLIRE = re.compile(r"collect_ignore|pytest_collection_modifyitems|pytest_ignore_collect|--deselect|--ignore\b|(?<![\w-])-k ")
_SLABIRI = {"skip", "skipif", "xfail", "importorskip"}
_ASERTIUNI = {"raises", "fail", "warns"}
#: [regula 3d] excepțiile motivate: {"<fișier>::<test>": "<motiv, cu decizia / deficiența numită>"}
MOTIVATE = {
    "core/test_cai_creare_factura.py::test_o_factura_se_naste_din_EXACT_doua_locuri_in_productie":
        "redenumit, nu scos: a treia cale declarată, preluarea documentelor deschise (252, `solduri_parteneri_api._scrie_documente`, "
        "numai `tip='preluata'`); aceeași aserțiune, pe trei căi: core/test_cai_creare_factura.py::"
        "test_o_factura_se_naste_din_EXACT_trei_locuri_in_productie, plus test_calea_preluarii_scrie_numai_facturi_preluate",
    "frontend_test/e2e/e2e_lot11_x.py::test_def_c78_vanzarea_intracomunitara_are_o_singura_nota":
        "funcție scoasă: livrarea intracomunitară de BUNURI din Operațiuni (decizia Costin C84 (b), 23.10.2026, DECIZII „Comanda 12.1”); "
        "testul păstrează nota unică pe servicii, iar bunurile sunt acoperite de frontend_test/e2e/e2e_lot12_emit.py::test_def_c84_…",
    "core/test_lot11_x_c78_vanzare_ic.py::test_def_c78_vanzarea_ic_de_bunuri_are_o_singura_nota":
        "funcție scoasă: livrarea intracomunitară de BUNURI din Operațiuni (decizia Costin C84 (b), 23.10.2026); înlocuit de "
        "core/test_lot11_x_c78_vanzare_ic.py::test_def_c84_livrarea_ic_de_bunuri_se_face_din_emite_factura (refuzul numit) și "
        "test_def_c78_prestarea_ic_de_servicii_are_o_singura_nota (nota unică)",
    "core/test_garda_main.py::test_cu_aprobarea_sha_ului_trece_si_se_consuma":
        "funcție scoasă: aprobarea scrisă APROBARE_MAIN radiată (CLAUDE.md §6, 23.10.2026; DECIZII „Comanda 12.1”); înlocuit de "
        "core/test_garda_main.py::test_cu_poarta_verde_main_se_muta_fara_aprobare_scrisa",
    "core/test_temei_termene.py::test_datoria_ramasa_e_numita":
        "înlocuit, nu slăbit: testul număra datoria R4 rămasă (D100, D101, D112, D205, D394, D406 fără temeiul termenului în corpus) și "
        "cerea, în propria aserțiune, să fie șters când lista se golește („toate tipurile sunt sursate — ridică pragul și șterge testul "
        "ăsta”). Deficiența 639 (comanda Costin 12.2, pachetul reev2) a sursat toate tipurile cu termen calculat, deci lista e goală; "
        "aserțiunea inversă o ține acum core/test_temei_termene.py::test_toate_tipurile_cu_termen_calculat_sunt_sursate (lista datoriei "
        "== []), iar citatele 639 sunt verificate verbatim de test_temeiurile_mutarii_termenului_sunt_verbatim_in_corpus",
    "core/test_garda_main.py::test_aprobarea_fara_text_nu_ajunge":
        "funcție scoasă: aprobarea scrisă APROBARE_MAIN radiată (CLAUDE.md §6, 23.10.2026; DECIZII „Comanda 12.1”); verdictul cerut de "
        "garda pe main rămâne păzit de core/test_garda_main.py::test_aprobarea_fara_poarta_verde_a_sha_ului_nu_ajunge",
}
# [lotul 12, integrarea I3] cele patru teste ale lui `valideaza_lic`, scoase de pachetul fisc3 odată cu funcția
_LIC = ("funcție scoasă: `intracomunitar.valideaza_lic` (apelată numai de livrarea de BUNURI din Operațiuni, scoasă la C84 (b), decizia "
        "Costin 23.10.2026, DECIZII „Comanda 12.1”), iar refuzul ei „fără dovada transportului” a devenit avertisment la emitere (decizia "
        "Costin 12.3 pct.7: „C84: livrarea intracomunitară de bunuri fără dovada transportului primește avertisment la emitere, nu refuz.”). ")
MOTIVATE.update({
    "test_intracomunitar.py::test_lic_ok": _LIC + (
        "Mențiunea scutirii pe livrarea din „Emite factură” e a categoriei `livrare_ic`: core/test_274b_categorii_tva.py::"
        "test_274b_livrarea_intracomunitara_are_livrarea_si_codul_de_tva_al_clientului"),
    "test_intracomunitar.py::test_lic_fara_transport": _LIC + (
        "Înlocuit de core/test_lot12_fisc3_c84_dovada_transport.py::test_c84_fara_dovada_factura_se_emite_cu_avertisment_nu_refuz și, pe "
        "drumul fără întrebare (factura recurentă), de core/test_lot12_int3_c197_recurenta_lic.py::test_c197_avertismentul_c84_pe_fiecare_raspuns"),
    "test_intracomunitar.py::test_lic_client_ro": _LIC + (
        "Clientul din România pe livrarea intracomunitară e refuzat de categoria liniei (CATEGORIE_TVA_TARA): core/test_274b_categorii_tva.py::"
        "test_274b_categoria_se_potriveste_cu_tara_clientului[livrare_ic-RO-False]"),
    "test_intracomunitar.py::test_lic_cod_invalid": _LIC + (
        "Codul de TVA invalid în VIES se vede pe ecranul „Emite factură” (Verifică -> răspunsul negativ, lotul 12 C166); emiterea însăși nu "
        "cere VIES pe server — limită raportată de integrarea I3 ca deficiență nouă (codul valabil e condiția din CF art.294 alin.(2) lit.a)"),
})

# [lotul 13, comanda 13.1] testele scoase / rescrise de deficiențele lotului, fiecare cu decizia și testul care o păzește acum
_660 = ("funcție scoasă: formularele D200, D201, D220, D221, D223, D600 sunt înlocuite de Declarația unică (deficiența 660, comanda Costin "
        "13.1; CF art.122 alin.(1), art.120 „Abrogat.”) — scoase din dispecer, selector și generare (`declaratii_api.FORMULARE_INLOCUITE`). ")
_660_TESTE = ("Înlocuit de core/test_%s_formular.py::test_%s_nu_se_mai_ofera_formular_inlocuit_de_declaratia_unica (cererea, chiar "
              "completă, primește motivul cu textul legii) și core/test_lot13_decl_logica.py::test_660_*")
_507 = ("schimbare decisă: clasa 8 se înregistrează într-o singură parte, fără 891 și în afara rândurilor notei (deficiența 507, comanda "
        "Costin 13.1: „Clasa 8 se înregistrează într-o singură parte (doar debit 8035 la dare, doar credit la scoatere)”). ")
MOTIVATE.update({
    "core/test_cashflow.py::test_aloca_noi_intai":
        "funcție scoasă: `cashflow.aloca_sold` (soldul balanței împărțit pe facturi „de la cele mai noi”) înlocuit de `cashflow.din_facturi` "
        "(deficiențele 553 + 559, comanda Costin 13.1: facturile deschise validate, fiecare la scadența ei). Înlocuit de "
        "core/test_cashflow.py::test_din_facturi_fiecare_la_scadenta_ei",
    "core/test_cashflow.py::test_aloca_partial":
        "funcție scoasă: `cashflow.aloca_sold` (553 + 559). Partea de sold peste facturi o păzește "
        "core/test_cashflow.py::test_din_facturi_soldul_peste_facturi_intra_o_data_numit",
    "core/test_cashflow.py::test_aloca_zero":
        "funcție scoasă: `cashflow.aloca_sold` (553 + 559). Cazul gol îl păzește core/test_cashflow.py::test_din_facturi_fara_sold_in_plus",
    "core/test_d200_formular.py::test_d200_nu_e_doar_api": _660 + _660_TESTE % ("d200", "d200"),
    "core/test_d200_formular.py::test_d200_cerere_goala_refuza_la_api": _660 + _660_TESTE % ("d200", "d200"),
    "core/test_d201_formular.py::test_d201_nu_e_doar_api": _660 + _660_TESTE % ("d201", "d201"),
    "core/test_d201_formular.py::test_d201_cerere_goala_refuza_la_api": _660 + _660_TESTE % ("d201", "d201"),
    "core/test_d221_formular.py::test_d221_nu_e_doar_api": _660 + _660_TESTE % ("d221", "d221"),
    "core/test_d221_formular.py::test_d221_cerere_goala_refuza_la_api": _660 + _660_TESTE % ("d221", "d221"),
    "core/test_d223_formular.py::test_d223_nu_e_doar_api": _660 + _660_TESTE % ("d223", "d223"),
    "core/test_d223_formular.py::test_d223_cerere_goala_refuza_la_api": _660 + _660_TESTE % ("d223", "d223"),
    "core/test_d600_formular.py::test_d600_nu_e_doar_api": _660 + _660_TESTE % ("d600", "d600"),
    "core/test_d600_formular.py::test_d600_cerere_goala_refuza_la_api": _660 + _660_TESTE % ("d600", "d600"),
    "core/test_formulare_operatiuni_campuri.py::test_conturile_vin_precompletate_cu_sugestia_standard":
        "PIVOT decis: deficiența 504 (comanda Costin 13.1: „Câmpurile nu au voie să arate valori gri sau precompletate care induc în eroare "
        "[…] Câmpul rămâne gol.”) răstoarnă regula lotului 07.10 B (conturile precompletate cu sugestia). Înlocuit de "
        "core/test_formulare_operatiuni_campuri.py::test_niciun_camp_nu_vine_precompletat_sau_cu_text_gri",
    "core/test_formulare_operatiuni_campuri.py::test_CALIBRARE_cont_fara_sugestie_sau_motor_cu_placeholder_e_prins":
        "PIVOT decis (504, ca mai sus): calibrarea regulii vechi nu mai are obiect. Înlocuit de "
        "core/test_formulare_operatiuni_campuri.py::test_CALIBRARE_valoarea_sau_textul_gri_e_prins (valoarea sau textul gri puse la loc -> "
        "prinse)",
    "frontend_test/e2e/e2e_bloc_c.py::test_def_78_conturile_vin_precompletate_si_modificabile":
        "redenumit după PIVOT-ul 504 (aceeași deficiență 78, regula inversă: conturile pornesc goale, contul uzual stă în explicația "
        "câmpului): frontend_test/e2e/e2e_bloc_c.py::test_def_78_conturile_pornesc_goale_cu_contul_uzual_in_explicatie",
    "core/test_import_saga.py::test_contul_de_doua_ori_se_refuza_numit_nu_la_scriere":
        "schimbare decisă: deficiența 582 (comanda Costin 13.1: „Verificarea dublurilor oprește tot înainte de celelalte verificări”) — "
        "partenerul dublat nu mai oprește citirea fișierului; `pytest.raises` + aserțiunea pe text s-au înlocuit cu o singură aserțiune de "
        "egalitate pe rândurile respinse (`verifica_randuri` -> [(2, partener_dublat), (3, partener_dublat)]), mai strictă",
    "core/test_lot10_dividende.py::test_430a_din_117_preluat_fara_analitic_nota_debiteaza_117_cu_avertisment":
        "redenumit după deficiența 527 (comanda Costin 13.1: nota trece întâi suma dividendului pe analitic, 117 = 1171, și repartizează din "
        "1171): core/test_lot10_dividende.py::test_430a_din_117_preluat_fara_analitic_nota_reclasifica_pe_1171_cu_avertisment (5 aserțiuni)",
    "core/test_stocuri_situatie.py::test_situatia_stocului_e_prima_si_formularele_la_cerere":
        "schimbare decisă: deficiența 673 (comanda Costin 13.1: acțiunile deschid fereastră nouă) — formularele Stocurilor nu mai stau "
        "ascunse în pagină (`#cv-zona` hidden + click care îl arăta = două aserțiuni) ci se deschid în fereastra lor; o singură aserțiune "
        "cere că nu sunt desenate la deschidere, iar așteptarea ferestrei după click e `wait_for_selector` (eșuează la lipsă)",
    "test_comodat_chirii.py::test_chirie_incasata":
        "funcție scoasă: `comodat_chirii.nota_chirie_incasata` — chiria încasată e factură către chiriaș, din Facturi emise, cu cota după "
        "bun și opțiune (deficiența 531, comanda Costin 13.1; CF art.292 alin.(2) lit.e). Înlocuit de "
        "core/test_lot13_ops_chirie.py::test_def_531_chiria_unui_imobil_fara_optiune_e_scutita și e2e "
        "frontend_test/e2e/e2e_lot13_ops.py::test_def_531_chiria_unui_imobil_fara_optiune_e_scutita",
    "test_comodat_chirii.py::test_refacturare":
        "schimbare decisă: deficiența 530 (comanda Costin 13.1; CF art.271 alin.(2)) — factura furnizorului e întreagă achiziție proprie, "
        "fără 461; cele cinci aserțiuni de apartenență (`in`) s-au înlocuit cu două de EGALITATE pe listele întregi, mai stricte",
    "test_obiecte_inventar.py::test_dare_folosinta": _507 + "Cele două aserțiuni de apartenență (`in`) au devenit una de EGALITATE pe "
        "rezultatul întreg (rândul 603 = 303 și înregistrarea 8035 D în `extrabilant`), mai strictă",
    "test_productie.py::test_vanzare_cu_repartizare":
        "funcție scoasă: `productie.nota_vanzare` — vânzarea produselor trece prin factură, care descarcă produsul (deficiența 510, comanda "
        "Costin 13.1); aici rămâne repartizarea diferențelor (OMFP 1802/2014 pct.286 alin.(4)): test_productie.py::"
        "test_diferente_repartizate_asupra_iesirii, plus core/test_lot13_ops_productie.py::"
        "test_def_510_vanzarea_e_factura_descarca_produsul_si_repartizeaza_348",
    "test_productie.py::test_vanzare_coef_favorabil":
        "funcție scoasă: `productie.nota_vanzare` (510, ca mai sus); coeficientul favorabil (348 = 711) e păzit de "
        "test_productie.py::test_diferente_repartizate_asupra_iesirii",
})


def _git(*a):
    return subprocess.run(("git",) + a, cwd=_RAD, capture_output=True, text=True)


def baza_lotului():
    """SHA-ul de intrare al lotului: ce e publicat (`main`) și strămoș al lui HEAD."""
    p = _git("merge-base", "HEAD", "main")
    assert p.returncode == 0, "intrarea lotului (merge-base HEAD main) nu se poate afla: %s" % p.stderr.strip()
    return p.stdout.strip()


def _pytest_attr(n):
    """`pytest.X` / `pytest.mark.X` -> X (altfel None)."""
    if isinstance(n, ast.Call):
        n = n.func
    if isinstance(n, ast.Attribute):
        v = n.value
        if isinstance(v, ast.Name) and v.id == "pytest":
            return n.attr
        if isinstance(v, ast.Attribute) and v.attr == "mark" and isinstance(v.value, ast.Name) and v.value.id == "pytest":
            return n.attr
    return None


def functii_test(src):
    """PURĂ. {nume: {"aserturi": n, "slabiri": n}} — testele unui fișier (funcții `test_*` și metodele claselor `Test*`)."""
    out = {}
    try:
        t = ast.parse(src)
    except SyntaxError:
        return None

    def ia(fn, pref=""):
        aserturi = slabiri = 0
        for d in fn.decorator_list:
            if _pytest_attr(d) in _SLABIRI:
                slabiri += 1
        for n in (x for st in fn.body for x in ast.walk(st)):   # numai corpul: decoratorii s-au numărat mai sus
            if isinstance(n, ast.Assert):
                aserturi += 1
            elif isinstance(n, ast.Call):
                a = _pytest_attr(n)
                if a in _ASERTIUNI:
                    aserturi += 1
                elif a in _SLABIRI:
                    slabiri += 1
        out[pref + fn.name] = {"aserturi": aserturi, "slabiri": slabiri}

    modul_slab = 0
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_"):
            ia(n)
        elif isinstance(n, ast.ClassDef) and n.name.startswith("Test"):
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test_"):
                    ia(m, n.name + ".")
        elif isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "pytestmark" for x in n.targets):
            modul_slab += sum(1 for x in ast.walk(n.value) if _pytest_attr(x) in _SLABIRI)
        elif isinstance(n, ast.Expr) and _pytest_attr(n.value) in _SLABIRI:
            modul_slab += 1   # pytest.skip(..., allow_module_level=True) / importorskip la nivel de modul
    if modul_slab:
        for v in out.values():
            v["slabiri"] += modul_slab
    return out


def ocoliri(text):
    """PURĂ. Câte mecanisme de ocolire a colectării apar în text."""
    return len(_RE_OCOLIRE.findall(text))


def abateri(vechi, nou, oriunde, ocoliri_vechi, ocoliri_noi, motivate):
    """PURĂ. vechi / nou: {fișier: {test: {...}}} (fișierele de test schimbate); oriunde: {test: [(fișier, {...})]} (tot arborele);
    ocoliri_*: {fișier: n}. -> [abateri nemotivate], [excepții stale]."""
    rele, folosite = [], set()
    for f, tv in sorted(vechi.items()):
        tn = nou.get(f) or {}
        for nume, v in sorted(tv.items()):
            cheie = "%s::%s" % (f, nume)
            acum = tn.get(nume)
            if acum is None:
                alt = [x for x in oriunde.get(nume, []) if x[0] != f]
                acum = alt[0][1] if len(alt) == 1 else None
            ce = []
            if acum is None:
                ce.append("testul a fost șters")
            else:
                if acum["aserturi"] < v["aserturi"]:
                    ce.append("aserțiuni %d -> %d" % (v["aserturi"], acum["aserturi"]))
                if acum["slabiri"] > v["slabiri"]:
                    ce.append("skip / xfail nou (%d -> %d)" % (v["slabiri"], acum["slabiri"]))
            if not ce:
                continue
            if cheie in motivate:
                folosite.add(cheie)
                continue
            rele.append("%s: %s — regula 3d: nu se slăbește, nu se ocolește, nu se șterge un test ca să treacă poarta; dacă e o "
                        "schimbare decisă, motivul intră în MOTIVATE din core/test_poarta_fara_slabire.py" % (cheie, "; ".join(ce)))
    for f in sorted(set(ocoliri_vechi) | set(ocoliri_noi)):
        if ocoliri_noi.get(f, 0) > ocoliri_vechi.get(f, 0):
            cheie = "%s::<colectare>" % f
            if cheie in motivate:
                folosite.add(cheie)
            else:
                rele.append("%s: ocolire a colectării nouă (collect_ignore / deselect / ignore / -k: %d -> %d)"
                            % (f, ocoliri_vechi.get(f, 0), ocoliri_noi[f]))
    return rele, sorted(set(motivate) - folosite)


def masoara():
    baza = baza_lotului()
    dif = _git("diff", "--name-status", "--no-renames", baza).stdout.splitlines()
    schimbate = sorted({ln.split("\t")[-1] for ln in dif if ln.strip()})
    vechi, nou, ov, on = {}, {}, {}, {}
    for f in schimbate:
        # numai fișierele pe care le măsoară garda: un fișier binar schimbat (o imagine din `static/`) nu e text și nu e test
        if not (_RE_TEST.search(f) or f in CONFIG or f.endswith("conftest.py")):
            continue
        p = _git("show", "%s:%s" % (baza, f))
        text_v = p.stdout if p.returncode == 0 else None
        cale = os.path.join(_RAD, f)
        text_n = io.open(cale, encoding="utf-8").read() if os.path.isfile(cale) else None
        if _RE_TEST.search(f) and text_v is not None:
            tv = functii_test(text_v)
            if tv:
                vechi[f] = tv
                nou[f] = (functii_test(text_n) or {}) if text_n is not None else {}
        if f in CONFIG or f.endswith("conftest.py"):
            ov[f] = ocoliri(text_v or "")
            on[f] = ocoliri(text_n or "")
    oriunde = {}
    fis = _git("ls-files", "--cached", "--others", "--exclude-standard").stdout.splitlines()
    for f in fis:
        if _RE_TEST.search(f) and os.path.isfile(os.path.join(_RAD, f)):
            for nume, v in (functii_test(io.open(os.path.join(_RAD, f), encoding="utf-8").read()) or {}).items():
                oriunde.setdefault(nume, []).append((f, v))
    return baza, vechi, nou, oriunde, ov, on


def test_niciun_test_slabit_ocolit_sau_sters_fata_de_intrarea_lotului():
    """Regula 3d. MUTAȚIE: un `assert` scos / un `@pytest.mark.skip` adăugat / un test șters într-un fișier de test existent -> pică."""
    baza, vechi, nou, oriunde, ov, on = masoara()
    rele, stale = abateri(vechi, nou, oriunde, ov, on, MOTIVATE)
    assert not rele, "față de intrarea lotului %s:\n%s" % (baza[:8], "\n".join(rele))
    assert not stale, "excepții MOTIVATE fără abatere (scoate-le): %s" % stale


def test_garda_slabirii_nu_e_vida():
    """Anti-vacuu: pică pe fragmente sintetice rele, trece pe unul bun; excepția motivată acoperă, cea stale e semnalată."""
    bun = ("import pytest\n\ndef test_a():\n    assert 1\n    with pytest.raises(ValueError):\n        int('x')\n\n"
           "class TestB:\n    def test_c(self):\n        assert 2\n")
    tv = functii_test(bun)
    assert tv == {"test_a": {"aserturi": 2, "slabiri": 0}, "TestB.test_c": {"aserturi": 1, "slabiri": 0}}, tv
    v = {"core/test_x.py": tv}

    def ab(src, mot=None, oriunde=None, ov=None, on=None):
        return abateri(v, {"core/test_x.py": functii_test(src)}, oriunde or {}, ov or {}, on or {}, mot or {})

    assert ab(bun) == ([], [])
    assert ab(bun + "\ndef test_nou():\n    pytest.skip('x')\n") == ([], []), "un test NOU nu e slăbirea unui test existent"
    rele = {
        "assert scos": bun.replace("    assert 1\n", "    pass\n"),
        "raises scos": bun.replace("    with pytest.raises(ValueError):\n        int('x')\n", ""),
        "skip decorator": bun.replace("def test_a", "@pytest.mark.skip(reason='x')\ndef test_a"),
        "skipif decorator": bun.replace("def test_a", "@pytest.mark.skipif(True, reason='x')\ndef test_a"),
        "xfail decorator": bun.replace("def test_a", "@pytest.mark.xfail\ndef test_a"),
        "pytest.skip în corp": bun.replace("    assert 1\n", "    pytest.skip('x')\n    assert 1\n"),
        "pytestmark pe modul": bun.replace("import pytest\n", "import pytest\npytestmark = pytest.mark.skip\n"),
        "skip la nivel de modul": bun.replace("import pytest\n", "import pytest\npytest.skip('x', allow_module_level=True)\n"),
        "test șters": bun.replace("class TestB:\n    def test_c(self):\n        assert 2\n", ""),
    }
    for ce, src in rele.items():
        assert ab(src)[0], "garda trece pe o slăbire: %s" % ce
    sters = rele["test șters"]
    assert ab(sters, oriunde={"TestB.test_c": [("core/test_y.py", {"aserturi": 1, "slabiri": 0})]}) == ([], []), "testul mutat"
    assert ab(sters, mot={"core/test_x.py::TestB.test_c": "ruta scoasă prin decizia X"}) == ([], [])
    assert ab(bun, mot={"core/test_x.py::test_a": "motiv"})[1] == ["core/test_x.py::test_a"], "excepția stale"
    assert ocoliri('addopts = -q --deselect core/test_x.py::test_a\n') == 1
    assert ocoliri("collect_ignore = ['x']\ndef pytest_collection_modifyitems(items): pass\n") == 2
    assert ocoliri('"$PY" -m pytest -q -k "not lent"\n') == 1 and ocoliri("pytest -q -n 3 --dist loadfile\n") == 0
    assert ab(bun, ov={"conftest.py": 0}, on={"conftest.py": 1})[0], "ocolirea colectării trecută"
