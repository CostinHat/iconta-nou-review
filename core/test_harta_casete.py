# -*- coding: utf-8 -*-
"""GARD — COMPARATORUL. Confruntă ce s-a randat cu ce spune harta că trebuie randat.

Cele trei acte, separate deliberat (DECIZII 20.08 — calea a doua):
  observația  = frontend_test/vizual/scan_casete.py  -> casete_control_fiscal.json (fapte, fără verdict)
  așteptarea  = frontend_test/vizual/harta_casete.py (scrisă ÎNAINTE, din codul de randare)
  comparația  = fișierul ăsta

DE CE CONTEAZĂ SEPARAREA. Verificarea vizuală de până acum le prăbușea în unul singur: mă uitam și,
în același timp, jucam comparator cu o așteptare nescrisă. Așa se ajunge să raportezi „curat" pe un
ecran față de care nu ai, de fapt, nicio așteptare cu care să compari.

CE NU ACOPERĂ, declarat: vezi `harta_casete.LIMITE`. Pe scurt — cifrele din confruntarea
declarație↔contabilitate sunt încorporate în proză, nu sunt câmpuri, deci niciun comparator nu le
poate atinge; iar antetul (pastila, „n datorate") e pus de apelant, nu de renderer.
"""
import json
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VIZ = os.path.join(_RAD, "frontend_test", "vizual")
if _VIZ not in sys.path:
    sys.path.insert(0, _VIZ)

_ARTEFACT = os.path.join(_VIZ, "casete_control_fiscal.json")
_ECRAN = "control_fiscal"


def _harta():
    import harta_casete
    return harta_casete


def _art():
    if not os.path.exists(_ARTEFACT):
        pytest.skip("artefact absent — rulează frontend_test/vizual/scan_casete.py")
    with open(_ARTEFACT, encoding="utf-8") as f:
        return json.load(f)


def _casete():
    return _harta().STRUCTURA[_ECRAN]["casete"]


def _randate(a):
    return {s["titlu"]: s for s in a["randat"]["sectiuni"]}


def _asteptata_sa_apara(c, p):
    """Evaluează `conditie` pe payload. Întoarce True/False, sau None dacă nu se poate decide."""
    cond, cheie = c["conditie"], c.get("cheie")
    if cond == "intotdeauna":
        return True
    if cond == "stare_verde":
        return p["stare"] == "verde"
    if cond == "lista_nevida":
        return p["lungimi"].get(cheie, 0) > 0
    if cond == "lista_nevida_dupa_filtrare":
        return None            # cere lista DEJA_IN_INCRUCISAT din JS — nu o am în artefact
    if cond == "vc_prezent":
        return cheie in p["vc_chei_prezente"]
    if cond == "vc_cu_constatari":
        return cheie in p["vc_cu_constatari"]
    if cond == "vc_oricare_cu_constatari":
        return any(k in p["vc_cu_constatari"] for k in cheie.split("|"))
    return None


# ─────────────────────────── anti-vacuu ───────────────────────────

def test_gardul_vede_harta_si_artefactul():
    """Dacă harta se golește sau artefactul se rupe, testele de mai jos ar trece pe GOL."""
    c = _casete()
    assert len(c) >= 10, "doar %d casete în hartă — s-a rupt ceva" % len(c)
    a = _art()
    assert a["randat"]["sectiuni"], "artefactul n-are nicio secțiune randată"
    assert set(a["payload"]["lungimi"]), "artefactul n-are lungimile payload-ului"


def test_fiecare_caseta_are_conditie_citibila():
    """O casetă fără `conditie` cunoscută ar fi sărită tăcut de comparator."""
    stiute = {"lista_nevida", "lista_nevida_dupa_filtrare", "vc_prezent", "vc_cu_constatari",
              "vc_oricare_cu_constatari", "stare_verde", "intotdeauna"}
    rele = [c["id"] for c in _casete() if c.get("conditie") not in stiute]
    assert not rele, "casete cu condiție necunoscută (ar fi sărite tăcut): %s" % rele


# ─────────────────────────── sensul 1: DOM -> hartă ───────────────────────────

def test_nicio_caseta_randata_fara_intrare_in_harta():
    a = _art()
    titluri = {c["titlu"] for c in _casete()}
    straine = sorted({s["titlu"] for s in a["randat"]["sectiuni"]} - titluri)
    assert not straine, (
        "Secțiuni randate pe ecran care NU există în hartă: %s. Ori s-a adăugat o casetă fără s-o "
        "declari, ori titlul s-a schimbat. Harta e așteptarea — dacă ecranul o depășește, nimeni "
        "nu mai știe ce ar trebui să fie acolo." % straine)


# ─────────────────────────── sensul 2: hartă -> DOM ───────────────────────────

def test_fiecare_caseta_asteptata_chiar_apare():
    a = _art()
    p, r = a["payload"], _randate(a)
    lipsa, nedecis = [], []
    for c in _casete():
        vrea = _asteptata_sa_apara(c, p)
        if vrea is None:
            nedecis.append(c["id"]); continue
        if vrea and c["titlu"] not in r:
            lipsa.append("%s (condiție: %s pe %r)" % (c["titlu"], c["conditie"], c.get("cheie")))
    assert not lipsa, (
        "Casete pe care payload-ul le cere, dar care NU s-au randat: %s. Asta e absența — "
        "singurul lucru pe care privitul nu-l poate găsi niciodată." % lipsa)


def test_acoperirea_e_declarata_nu_presupusa():
    """M0: un raport care nu spune CÂTE casete a putut atinge în starea asta ascunde că restul
    n-au fost verificate. «Curat» pe o casetă care nu s-a randat nu înseamnă nimic."""
    a = _art()
    p, r = a["payload"], _randate(a)
    atinse = [c["id"] for c in _casete() if c["titlu"] in r]
    neatinse = [c["id"] for c in _casete() if c["titlu"] not in r]
    assert atinse, "nicio casetă atinsă — starea firmei nu exercită acest ecran deloc"
    print("\nACOPERIRE pe %s (tid %s, stare=%s): %d/%d casete atinse."
          % (a["firma"], a["tenant_id"], p["stare"], len(atinse), len(_casete())))
    print("   atinse:   %s" % ", ".join(atinse))
    print("   neatinse: %s  <- NEVERIFICATE in starea asta, nu «curate»" % ", ".join(neatinse))


# ─────────────────────────── constrângeri [COD] ───────────────────────────

def test_contorul_din_titlu_egal_cu_lungimea_sursei():
    a = _art()
    p, r = a["payload"], _randate(a)
    rele = []
    for c in _casete():
        if not c["numarata"] or c["titlu"] not in r:
            continue
        n_afisat = r[c["titlu"]]["contor"]
        n_real = p["lungimi"].get(c.get("cheie"))
        if n_real is None:
            continue
        if n_afisat != n_real:
            rele.append("%s: titlul spune (%s), sursa are %s" % (c["titlu"], n_afisat, n_real))
    assert not rele, "Contor afișat ≠ lungimea sursei: %s" % rele


def test_randurile_randate_egal_cu_randurile_din_sursa():
    a = _art()
    p, r = a["payload"], _randate(a)
    rele = []
    for c in _casete():
        if c["titlu"] not in r or not c.get("cheie") or c["conditie"] != "lista_nevida":
            continue
        n_dom = r[c["titlu"]]["randuri"]
        n_src = p["lungimi"].get(c["cheie"])
        if n_dom is not None and n_src is not None and n_dom != n_src:
            rele.append("%s: %s rânduri randate, %s în sursă" % (c["titlu"], n_dom, n_src))
    assert not rele, "Rânduri pierdute sau dublate la randare: %s" % rele


def test_verde_exclude_restantele():
    a = _art()
    r = _randate(a)
    if not a["randat"]["are_gata"]:
        pytest.skip("firma nu e pe verde în starea scanată")
    rele = [t for t in ("Restanțe", "De urmărit") if t in r]
    assert not rele, "«Totul depus la zi» apare simultan cu %s" % rele


def test_stare_coerenta_cu_grupurile_randate():
    a = _art()
    p, r = a["payload"], _randate(a)
    if p["stare"] == "rosu":
        assert "Restanțe" in r, "stare=rosu dar nu s-a randat nicio restanță"
    if p["stare"] == "verde":
        assert "Restanțe" not in r and "De urmărit" not in r, "stare=verde cu restanțe randate"


def test_fara_dublare_intre_verificari_si_incrucisat():
    """O etichetă filtrată prin DEJA_IN_INCRUCISAT nu poate apărea în ambele secțiuni."""
    a = _art()
    r = _randate(a)
    if "Verificări contabile" not in r or "Declarație vs contabilitate" not in r:
        pytest.skip("una din cele două secțiuni nu s-a randat în starea asta")
    n_contabil = r["Verificări contabile"]["contor"]
    assert n_contabil is not None and n_contabil > 0, \
        "«Verificări contabile» randată cu contor gol - filtrarea a golit-o, dar secțiunea a rămas"


# ─────────────────────────── constrângeri [TU] ───────────────────────────

def test_fiecare_constrangere_are_o_stare_cunoscuta():
    """Un marcaj singur minte: [COD] spune cine decide, nu dacă ceva chiar verifică."""
    stiute = {"verifica", "datorie", "neexercitat", "asteapta_decizie"}
    rele = [c["id"] for c in _harta().CONSTRANGERI if c.get("stare") not in stiute]
    assert not rele, "constrângeri fără stare cunoscută (ar părea acoperite): %s" % rele


def test_ce_nu_verifica_nimic_e_strigat_la_fiecare_rulare():
    """Anti-vacuu pe LISTA: o constrângere decisă dar care nu pune nimic la încercare NU are voie să
    se confunde cu una care trece. Le numește pe toate trei felurile, la fiecare rulare."""
    h = _harta()
    grupe = {}
    for c in h.CONSTRANGERI:
        grupe.setdefault(c["stare"], []).append(c["id"])
    print("\nCONSTRÂNGERI — ce face fiecare AZI:")
    for st in ("verifica", "datorie", "neexercitat", "asteapta_decizie"):
        if grupe.get(st):
            print("   %-18s %s" % (st + ":", ", ".join(grupe[st])))
    nimic = grupe.get("neexercitat", []) + grupe.get("asteapta_decizie", [])
    assert grupe.get("verifica"), "NICIO constrângere nu verifică ceva — lista e decor"
    print("   -> %d din %d constrângeri nu pun nimic la încercare pe datele curente."
          % (len(nimic), len(h.CONSTRANGERI)))


@pytest.mark.xfail(strict=True, reason=(
    "DATORIE 20.08.2026 (R1'): anatomia rândului nu poartă cheia de identificare a entității randate. "
    "public.declaratii_depuse o definește prin cheia primară (tenant_id, an, luna, tip, nr_depunere); "
    "rândurile poartă din ea doar `tip` și, uneori, `perioada`. Efect: o rectificativă și inițiala "
    "aceleiași luni ar arăta identic, iar două constatări distincte pe același tip (D100 pe 2025 și pe "
    "2026, Startup Partial) arată ca un rând dublat. Cade când payload-ul poartă cheia întreagă."))
def test_randurile_poarta_cheia_de_identificare():
    # [corectie 20.08] DOAR categoriile care sunt DEPUNERI. `lipsa`/`urmarit` sunt obligatii nedepuse -
    # n-au cum sa poarte nr_depunere, iar a-l cere acolo ar impinge spre reparatia gresita (un numar
    # fara sens pe o obligatie neonorata). Vezi harta_casete.ANATOMII["decl"].nota.
    DEPUNERI = ("confirmate", "cu_intarziere")
    a = _art()
    p = a["payload"]
    fara = []
    for lista in DEPUNERI:
        for chei in p["randuri_decl"].get(lista, []):
            if "nr_depunere" not in chei:
                fara.append("%s: rând fără nr_depunere (chei: %s)" % (lista, chei))
    if not any(p["randuri_decl"].get(l) for l in DEPUNERI):
        import pytest as _p
        _p.skip("firma scanată n-are nicio obligație stinsă — constrângerea n-ar discrimina nimic")
    assert not fara, "Rânduri de depunere fără cheia de identificare completă: %s" % fara[:6]


@pytest.mark.xfail(strict=True, reason=(
    "DECIS 20.08.2026 (R2), NEIMPLEMENTAT (20.08.2026): fiecare rând de anatomie `motiv` trebuie să poarte perioada "
    "sau intervalul la care se referă. Azi intrările din d.neclar au doar {tip, motiv}, iar textul lor "
    "afirmă «pentru restanțele trecute» — un domeniu pe care datele nu-l poartă. Efect pe ecran: D300 "
    "apare și în «De urmărit · iul», și în «Nu pot verifica» fără perioadă, deci cele două par să se "
    "contrazică deși vorbesc despre luni diferite. Lăsat DELIBERAT neredus: garda trebuie să-l prindă "
    "ea, nu eu — altfel am probat doar că l-am văzut. Cade singur când payload-ul poartă domeniul."))
def test_randurile_motiv_poarta_domeniul():
    a = _art()
    p = a["payload"]
    fara = []
    for lista, randuri in p["randuri_motiv"].items():
        for chei in randuri:
            if not ({"perioada", "an", "interval"} & set(chei)):
                fara.append("%s: rând cu cheile %s" % (lista, chei))
    assert not fara, "Rânduri `motiv` fără domeniu declarat: %s" % fara


def test_depuse_numara_obligatii_stinse_nu_depuneri():
    """[R3] Pastila trebuie să numere același fel de lucru pe ambele părți: OBLIGAȚII.
    ANTI-VACUU: pe o firmă fără nicio depunere, 0 == 0 trece fără să discrimineze nimic — deci se
    SARE cu motiv, nu se raportează ca verificat. Defectul e cunoscut pe Constructii Profit Trim
    («0 datorate · 1 depuse»), unde `depuse` numără toată istoria iar `datorate` doar fereastra."""
    a = _art()
    p = a["payload"]
    stinse = {tuple(x) for k in ("confirmate", "cu_intarziere")
              for x in p["perechi_tip_perioada"].get(k, [])}
    depuse = a["payload"].get("depuse")
    if depuse is None:
        pytest.skip("artefactul nu poartă `depuse` — scanerul trebuie extins")
    if not stinse and not depuse:
        pytest.skip("firma scanată n-are nicio obligație stinsă și nicio depunere — "
                    "constrângerea ar trece 0==0 fără să discrimineze (vezi harta_casete.LIMITE)")
    assert depuse == len(stinse), (
        "«n depuse» = %s dar obligațiile stinse sunt %d %s. Cele două părți ale pastilei numără "
        "lucruri diferite." % (depuse, len(stinse), sorted(stinse)))
