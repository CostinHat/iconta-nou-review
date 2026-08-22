# -*- coding: utf-8 -*-
"""GARDĂ: fiecare interdicție din plan are secțiune în CONFORMITATE.md, completă. (22.08.2026)

DE CE (Costin): «Cifrele confruntării nu au voie să existe doar în raport. Raportul se citește o
dată; registrul rămâne.» Prima confruntare a produs opt cifre care au trăit doar într-un mesaj — dacă
nimeni nu le mai citea, munca de măsurare se pierdea și s-ar fi refăcut de la zero.

CE FACE IMPOSIBIL:
  - o interdicție din `PLAN_ARHITECTURA.md` fără secțiune în `CONFORMITATE.md`;
  - o secțiune cu un câmp OBLIGATORIU gol — «un câmp gol nu e permis: dacă nu se poate măsura, scrie
    NEMĂSURABILĂ cu motivul»;
  - o stare din afara celor patru. «Investigată» NU e o stare;
  - o secțiune orfană, pentru o interdicție care nu există în plan;
  - o interdicție NOUĂ adăugată în plan fără secțiune — cazul care motivează gardul cel mai tare,
    fiindcă planul crește (25 -> 48 într-o zi).

CE NU FACE, declarat: nu verifică dacă cifra e CORECTĂ, nici dacă măsurătoarea a fost bine făcută.
Verifică forma și completitudinea. Adevărul unei cifre se probează prin calibrare, nu prin gardă.

CITIREA CÂMPURILOR, cu motivul (22.08, după RED-proof): valoarea unui câmp se citește cu `[ \t]*`,
NU cu `\\s*`, fiindcă `\\s` cuprinde și linia nouă. Prima formă a gardului lăsa un câmp golit să
împrumute textul rândului URMĂTOR — mutația «câmp obligatoriu gol» a trecut. Un gard care citește
peste marginea rândului măsoară alt fișier decât cel scris.
"""
import datetime
import io
import os
import re
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(RAD, "PLAN_ARHITECTURA.md")
CONF = os.path.join(RAD, "CONFORMITATE.md")

STARI = ("MĂSURATĂ", "NEMĂSURABILĂ", "PARȚIAL", "NEÎNCEPUTĂ")

# Câmpurile cerute de Costin. Fiecare trebuie să existe ȘI să aibă conținut.
CAMPURI = ("stare", "cifra", "instanțe", "calibrare", "ce nu vede", "unde ajunge efectul")

CAP_TABEL = "CE E INTERZIS PRIN CONSTRUCȚIE"


def _camp(corp, nume):
    """Valoarea câmpului `nume`, sau None dacă lipsește. Se oprește la capătul RÂNDULUI."""
    m = re.search(r"^[ \t]*[-*]?[ \t]*\*\*%s\*\*[ \t]*:[ \t]*(.*)$" % re.escape(nume),
                  corp, re.M | re.I)
    return None if m is None else m.group(1).strip()


def _interdictii_din_plan():
    """{numar: text} din tabelul PARTEA VI. Se citește din plan, nu dintr-o listă copiată aici —
    altfel gardul ar apăra o lume pe care planul a părăsit-o."""
    t = io.open(PLAN, encoding="utf-8").read()
    # Nu `.index`: un ValueError ar spune «substring not found», nu CE s-a rupt.
    assert CAP_TABEL in t, (
        "în PLAN_ARHITECTURA.md nu mai există capul de tabel %r. Ori s-a redenumit secțiunea, ori "
        "planul s-a rescris — gardul NU poate citi interdicțiile, deci nu are ce apăra. Se repară "
        "aici, nu se ocolește." % CAP_TABEL)
    i = t.index(CAP_TABEL)
    j = t.index("\n# ", i)
    out = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|", t[i:j], re.M):
        out[int(m.group(1))] = m.group(2).replace("**", "").strip()
    return out


def _sectiuni_din_conformitate():
    """{numar: (titlu, corp)} — o secțiune începe cu `## N — <titlu>`."""
    t = io.open(CONF, encoding="utf-8").read()
    buc = re.split(r"^## (\d+)\s*[—-]\s*(.+)$", t, flags=re.M)
    out = {}
    for k in range(1, len(buc), 3):
        out[int(buc[k])] = (buc[k + 1].strip(), buc[k + 2])
    return out


@pytest.fixture(scope="module")
def plan():
    return _interdictii_din_plan()


@pytest.fixture(scope="module")
def conf():
    return _sectiuni_din_conformitate()


def test_planul_chiar_se_citeste(plan):
    """ANTI-VACUU. Dacă parsarea planului se strică, toate testele de mai jos ar trece pe zero
    interdicții — exact interdicția 19 („o gardă care raportează favorabil pe zero rânduri")."""
    assert len(plan) >= 25, (
        "doar %d interdicții citite din plan — parsarea s-a rupt, nu planul s-a golit" % len(plan))
    assert 1 in plan and "registru" in plan[1].lower()


def test_citirea_campurilor_se_opreste_la_capatul_randului():
    """ANTI-VACUU pe INSTRUMENT, nu pe date. Cazul real din RED-proof: un câmp golit care împrumută
    rândul următor. Fără proba asta, `test_niciun_camp_obligatoriu_gol` trece pe un fișier golit."""
    corp = "- **cifra**: \n- **instanțe**: 3 apeluri\n"
    assert _camp(corp, "cifra") == "", "un câmp gol trebuie citit GOL, nu cu textul rândului următor"
    assert _camp(corp, "instanțe") == "3 apeluri"
    assert _camp(corp, "calibrare") is None


def test_fiecare_interdictie_are_sectiune(plan, conf):
    lipsa = sorted(set(plan) - set(conf))
    assert not lipsa, (
        "interdicții din plan FĂRĂ secțiune în CONFORMITATE.md: %s.\n"
        "O interdicție nouă în plan cere secțiune — chiar și NEÎNCEPUTĂ. Așa se vede de la început "
        "cât e de făcut, nu se descoperă pe parcurs." % lipsa)


def test_nicio_sectiune_orfana(plan, conf):
    """Direcția inversă: o secțiune pentru o interdicție care nu mai există în plan e o măsurătoare
    despre o lume care s-a schimbat."""
    orfane = sorted(set(conf) - set(plan))
    assert not orfane, "secțiuni în CONFORMITATE.md fără interdicție în plan: %s" % orfane


def test_starea_e_dintre_cele_patru(conf):
    """«Investigată» nu e o stare."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        val = _camp(corp, "stare")
        if val is None:
            rele.append("  #%d: fără câmpul `stare`" % n)
            continue
        val = val.strip("*").split("—")[0].split("(")[0].split(",")[0].strip()
        if val not in STARI:
            rele.append("  #%d: stare %r — cele patru sunt: %s" % (n, val, ", ".join(STARI)))
    assert not rele, "stări nevalide:\n" + "\n".join(rele)


def test_niciun_camp_obligatoriu_gol(conf):
    """«Un câmp gol nu e permis: dacă nu se poate măsura, scrie NEMĂSURABILĂ cu motivul.»"""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        for camp in CAMPURI:
            val = _camp(corp, camp)
            if val is None:
                rele.append("  #%d: lipsește câmpul `%s`" % (n, camp))
            elif len(val.strip("*—- ")) < 3:
                rele.append("  #%d: câmpul `%s` e GOL" % (n, camp))
    assert not rele, ("câmpuri obligatorii lipsă sau goale (%d):\n" % len(rele)) + "\n".join(rele[:20])


def test_masuratele_au_cifra_si_calibrare(conf):
    """O stare MĂSURATĂ fără cifră sau fără calibrare e o afirmație fără probă. Calibrarea trebuie să
    numească ce caz cunoscut a fost GĂSIT — altfel cifra nu se poate crede."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        st = _camp(corp, "stare") or ""
        if "MĂSURATĂ" not in st:
            continue
        cif = _camp(corp, "cifra") or ""
        if not re.search(r"\d", cif):
            rele.append("  #%d: MĂSURATĂ fără cifră" % n)
        if "găsit" not in (_camp(corp, "calibrare") or "").lower():
            rele.append("  #%d: MĂSURATĂ fără caz de calibrare GĂSIT" % n)
    assert not rele, "măsurători fără probă:\n" + "\n".join(rele)


def test_partialele_spun_ca_cifra_e_plafon(conf):
    """O stare PARȚIAL fără declararea limitei se citește ca un total. Cifra unei măsurători pe o
    formă declarată e un PLAFON INFERIOR, iar asta trebuie scris, nu subînțeles."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        if "PARȚIAL" not in (_camp(corp, "stare") or ""):
            continue
        text = ((_camp(corp, "ce nu vede") or "") + " " + (_camp(corp, "cifra") or "")).lower()
        if "plafon" not in text and "nu e un total" not in text:
            rele.append("  #%d: PARȚIAL fără să spună că cifra e un plafon inferior" % n)
    assert not rele, "\n".join(rele)


def test_nemasurabilele_spun_de_ce(conf):
    """O stare NEMĂSURABILĂ fără motiv e o scuză."""
    rele = []
    for n, (_titlu, corp) in sorted(conf.items()):
        if "NEMĂSURABILĂ" in (_camp(corp, "stare") or ""):
            if "motiv" not in corp.lower():
                rele.append("  #%d: NEMĂSURABILĂ fără motivul scris" % n)
    assert not rele, "\n".join(rele)


def test_se_vede_cat_e_de_facut(plan, conf):
    """Rostul fișierului: «așa se vede de la început cât e de făcut, nu se descoperă pe parcurs».
    Dacă toate ar fi NEÎNCEPUTE, cifra n-ar mai spune nimic."""
    stari = [(_camp(corp, "stare") or "?").split()[0] for _n, (_t, corp) in conf.items()]
    assert stari.count("NEÎNCEPUTĂ") < len(stari), "nimic măsurat — fișierul e o listă, nu un registru"
    assert len(conf) == len(plan)


# ────────────────────────────────────────────────────────── ANTETUL DE ETAPĂ
#
# Cerut de `PLAN_LUCRU.md` («Unde suntem»): starea trăiește într-un singur loc, iar acel loc spune
# etapa și ce o termină. Motivul pentru care e GARDAT, scris de Costin: «un antet cu date vechi e mai
# rău decât niciunul».
#
# CE FACE IMPOSIBIL: un antet lipsă · un câmp obligatoriu gol · o etapă din afara lui E1..E5 · un
# registru modificat față de HEAD al cărui antet poartă o dată mai veche decât azi · un antet rămas în
# urma ultimului commit care a atins fișierul.
#
# CE NU FACE, declarat: nu verifică dacă ce scrie în antet e ADEVĂRAT — că etapa e chiar cea în care
# suntem, sau că „ce lipsește" e complet. Aia e o citire umană. Garda apără doar prospețimea și forma:
# face imposibil ca antetul să MINTĂ DESPRE DATĂ, nu ca el să mintă.

ANTET_CAMPURI = ("etapa", "criteriul de terminare", "ce lipsește", "decizii care blochează",
                 "ultima actualizare")

CAP_ANTET = "## ANTET DE ETAPĂ"


def _antet(t=None):
    """Blocul dintre capul de antet și primul separator `---`. None dacă antetul lipsește."""
    if t is None:
        t = io.open(CONF, encoding="utf-8").read()
    m = re.search(r"^%s[ \t]*$(.*?)^---[ \t]*$" % re.escape(CAP_ANTET), t, re.M | re.S)
    return None if m is None else m.group(1)


def _git(*a):
    return subprocess.run(["git", "-C", RAD] + list(a), capture_output=True, text=True)


def test_cititorul_de_antet_chiar_vede_antetul():
    """ANTI-VACUU pe INSTRUMENT. Fără proba asta, un regex rupt ar face toate testele de mai jos să
    treacă pe un antet inexistent — exact interdicția 19."""
    bun = "%s\n\n- **etapa**: E1 — ceva\n- **ultima actualizare**: 2026-01-02\n\n---\n## 1 — x\n" % CAP_ANTET
    assert _camp(_antet(bun), "etapa") == "E1 — ceva"
    assert _antet("fără antet\n\n---\n") is None, "un fișier fără antet trebuie citit ca FĂRĂ antet"


def test_antetul_exista_si_e_complet():
    a = _antet()
    assert a is not None, (
        "CONFORMITATE.md nu are `%s`. PLAN_LUCRU.md îl cere: «un singur loc» care spune unde suntem. "
        "Fără el, starea se împrăștie în rapoarte care se citesc o dată." % CAP_ANTET)
    rele = []
    for camp in ANTET_CAMPURI:
        val = _camp(a, camp)
        if val is None:
            rele.append("  lipsește câmpul `%s`" % camp)
        elif len(val.strip("*—- ")) < 3:
            rele.append("  câmpul `%s` e GOL" % camp)
    assert not rele, "antetul de etapă e incomplet:\n" + "\n".join(rele)


def test_etapa_e_dintre_cele_cinci():
    """E1..E5 din PLAN_LUCRU.md. «În lucru» nu e o etapă, la fel cum «investigată» nu e o stare."""
    val = _camp(_antet(), "etapa") or ""
    assert re.match(r"^\*{0,2}E[1-5]\b", val.strip()), (
        "etapa %r nu e dintre E1..E5 — cele cinci sunt scrise în PLAN_LUCRU.md, fiecare cu criteriul "
        "ei de terminare" % val)


def test_criteriul_si_ce_lipseste_nu_sunt_aceeasi_fraza():
    """Criteriul spune CÂND se termină; «ce lipsește» spune CE MAI E de făcut ca să se termine. Dacă
    sunt același text, unul dintre ele n-a fost scris — a fost copiat."""
    a = _antet()
    c = (_camp(a, "criteriul de terminare") or "").strip()
    l = (_camp(a, "ce lipsește") or "").strip()
    assert c != l, "«criteriul de terminare» și «ce lipsește» sunt același text — unul e copiat"


def test_antetul_nu_e_stale():
    """«Un antet cu date vechi e mai rău decât niciunul.» Data se verifică contra istoricului git, NU
    contra mtime — mtime se schimbă la checkout și ar da un verde fals.

    Două ramuri, fiindcă gardul trebuie să prindă ÎNAINTE de commit, nu după:
      - registrul e modificat față de HEAD  -> antetul poartă data de AZI (se scrie în tura asta);
      - registrul e curat                   -> data >= ziua ultimului commit care l-a atins.
    """
    val = _camp(_antet(), "ultima actualizare") or ""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", val)
    assert m, ("«ultima actualizare» = %r — se scrie ca dată ISO (2026-08-22), altfel nu se poate "
               "compara cu nimic" % val)
    d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    azi = datetime.date.today()
    assert d <= azi, "antetul poartă o dată din viitor (%s)" % d

    r = _git("diff", "--quiet", "HEAD", "--", "CONFORMITATE.md")
    assert r.returncode in (0, 1), (
        "git nu poate spune dacă CONFORMITATE.md e modificat (cod %d) — gardul anti-stale nu are pe ce "
        "sta, deci nu se ocolește, se repară" % r.returncode)
    if r.returncode == 1:
        assert d == azi, (
            "CONFORMITATE.md e modificat față de HEAD, dar antetul poartă %s, iar azi e %s. Registrul "
            "se atinge în tura asta, deci antetul se actualizează în tura asta." % (d, azi))
        return
    at = _git("log", "-1", "--format=%at", "--", "CONFORMITATE.md").stdout.strip()
    if at:
        ultim = datetime.date.fromtimestamp(int(at))
        assert d >= ultim, (
            "ultimul commit care a atins CONFORMITATE.md e din %s, iar antetul spune %s — registrul "
            "s-a schimbat de sub antet" % (ultim, d))


# ──────────────────────────────────────── CÂND, ȘI DE PE CE COD (câmpurile (c))
#
# Cerut de Costin, 22.08.2026: «Fără ele, o cifră adevărată azi se citește peste două săptămâni ca
# stare curentă, deși codul s-a mișcat. Nu e o afirmație greșită — e una care îmbătrânește, iar data
# o face vizibilă.»
#
# CE FACE IMPOSIBIL: o secțiune fără cele două câmpuri · o cifră MĂSURATĂ sau PARȚIAL fără dată și
# fără commit · o secțiune NEÎNCEPUTĂ care pretinde totuși o măsurătoare · un hash care nu există în
# istoric (o cifră ancorată pe un commit inventat e mai rea decât una neancorată) · un antet care
# numește alt commit decât cel mai vechi din registru.
#
# CE NU FACE, declarat: nu verifică dacă măsurătoarea a fost CHIAR făcută la acea dată și pe acel
# arbore. Data e o declarație; garda o face verificabilă și comparabilă, nu adevărată. Și nu se
# aprinde când distanța față de HEAD crește — vechimea se CITEȘTE, nu se blochează: un prag ar
# transforma harta în poartă și ar opri lucrul tocmai când e mai mult de făcut.

CAMPURI_MASURARE = ("măsurat la", "pe commit")
GOL = "—"


def _val(corp, nume):
    v = _camp(corp, nume)
    return None if v is None else v.strip().strip("`").strip("*").strip()


def test_fiecare_sectiune_are_cand_si_de_pe_ce_cod(conf):
    rele = []
    for n, (_t, corp) in sorted(conf.items()):
        for camp in CAMPURI_MASURARE:
            v = _val(corp, camp)
            if v is None:
                rele.append("  #%d: lipsește câmpul `%s`" % (n, camp))
            elif not v:
                rele.append("  #%d: câmpul `%s` e GOL — pentru o secțiune nemăsurată se scrie %s"
                            % (n, camp, GOL))
    assert not rele, ("câmpuri de măsurare lipsă sau goale (%d):\n" % len(rele)) + "\n".join(rele[:20])


def test_o_cifra_poarta_data_si_commitul(conf):
    """O cifră fără dată și fără commit se citește peste două săptămâni ca stare curentă."""
    rele = []
    for n, (_t, corp) in sorted(conf.items()):
        st = _camp(corp, "stare") or ""
        if "MĂSURATĂ" not in st and "PARȚIAL" not in st:
            continue
        d = _val(corp, "măsurat la") or ""
        h = _val(corp, "pe commit") or ""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            rele.append("  #%d: `măsurat la` = %r — se scrie ca dată ISO" % (n, d))
        if not re.match(r"^[0-9a-f]{7,40}$", h):
            rele.append("  #%d: `pe commit` = %r — se scrie hash-ul de la care e cifra" % (n, h))
    assert not rele, "cifre fără ancoră în timp:\n" + "\n".join(rele)


def test_neinceputa_nu_pretinde_masuratoare(conf):
    """Direcția inversă: o secțiune NEÎNCEPUTĂ care poartă dată și commit afirmă o măsurătoare care
    n-a avut loc — exact felul de verde fals pe care registrul trebuie să-l facă imposibil."""
    rele = []
    for n, (_t, corp) in sorted(conf.items()):
        if "NEÎNCEPUTĂ" not in (_camp(corp, "stare") or ""):
            continue
        for camp in CAMPURI_MASURARE:
            if (_val(corp, camp) or GOL) != GOL:
                rele.append("  #%d: NEÎNCEPUTĂ, dar `%s` = %r" % (n, camp, _val(corp, camp)))
    assert not rele, "măsurători pretinse fără măsurătoare:\n" + "\n".join(rele)


def _commituri(conf):
    out = {}
    for n, (_t, corp) in conf.items():
        h = _val(corp, "pe commit") or GOL
        if h != GOL:
            out[n] = h
    return out


def test_commiturile_din_registru_exista(conf):
    """Un hash inventat ancorează cifra în neant și arată exact ca unul adevărat."""
    c = _commituri(conf)
    assert c, "niciun `pe commit` completat — registrul n-are nicio cifră ancorată"
    rele = [("  #%d: `%s` nu există în istoric" % (n, h)) for n, h in sorted(c.items())
            if _git("cat-file", "-e", "%s^{commit}" % h).returncode != 0]
    assert not rele, "commituri inexistente:\n" + "\n".join(rele)


def test_antetul_numeste_cel_mai_vechi_commit(conf):
    """Rândul din antet e util doar dacă e CHIAR cel mai vechi: altfel harta pare mai proaspătă
    decât e, ceea ce e mai rău decât să n-aibă rândul deloc."""
    val = _camp(_antet(), "cel mai vechi commit din registru")
    assert val, "antetul nu numește cel mai vechi commit din registru"
    m = re.search(r"`([0-9a-f]{7,40})`", val)
    assert m, "rândul nu conține un hash între apostrofuri inverse: %r" % val[:120]

    perechi = []
    for n, h in _commituri(conf).items():
        r = _git("log", "-1", "--format=%ct", h)
        assert r.returncode == 0, "nu se poate citi data commitului %s (#%d)" % (h, n)
        perechi.append((int(r.stdout.strip()), h, n))
    perechi.sort()
    cel_mai_vechi = perechi[0]
    ales = _git("rev-parse", m.group(1)).stdout.strip()
    real = _git("rev-parse", cel_mai_vechi[1]).stdout.strip()
    assert ales == real, (
        "antetul spune `%s`, dar cel mai vechi `pe commit` din registru e `%s` (secțiunea #%d). "
        "Un antet care numește un commit mai nou face harta să pară mai proaspătă decât e."
        % (m.group(1), cel_mai_vechi[1], cel_mai_vechi[2]))


def test_efectul_e_al_interdictiei_nu_al_grupului(conf):
    """Defectul, gasit de Costin pe 22.08: campul «unde ajunge efectul» fusese completat pe GRUPURI
    de principii, nu per interdictie — 13 poarta efectul lui 15, 14 pe al lui 2. Auditul complet a
    scos 13 grupuri de text partajat plus doua sectiuni cu text-substituent.

    PROXY-UL MECANIC: doua sectiuni cu EXACT acelasi efect. Nu prinde o parafrazare, deci cifra lui e
    un plafon inferior — dar prinde chiar forma prin care s-a produs clasa: copierea.

    CE NU FACE, declarat: nu verifica daca efectul scris e ADEVARAT pentru interdictia lui. Aia e o
    citire umana; gardul apara doar ca nu e al altcuiva prin copiere."""
    vazute = {}
    rele = []
    for n, (_t, corp) in sorted(conf.items()):
        v = (_camp(corp, "unde ajunge efectul") or "").strip()
        if len(v) < 20:
            continue
        cheie = re.sub(r"\s+", " ", v.lower())
        if cheie in vazute:
            rele.append("  #%d poarta acelasi efect ca #%d" % (n, vazute[cheie]))
        else:
            vazute[cheie] = n
    assert not rele, (
        "«unde ajunge efectul» copiat intre interdictii (%d):\n%s\n"
        "Campul spune unde ajunge efectul ACESTEI interdictii. Doua interdictii din acelasi grup de "
        "principii au efecte diferite — daca n-au, una dintre ele nu era nevoie sa existe."
        % (len(rele), "\n".join(rele)))
