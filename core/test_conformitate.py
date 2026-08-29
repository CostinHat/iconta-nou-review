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


# [METODA §25] Cate restante DESCHISE deblocate de DECIZIE inca nu spun unde au cautat in plan.
# Coboara pe masura ce fiecare e confruntata cu planul - NU se umple prin copiere.
_CLICHET_FARA_PLAN = 5


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

# `pasul curent` a intrat pe 22.08: sectiunea B a raportului se DERIVA din antet
# (`scripts/raport_b.py`), iar ea cere si pasul, nu doar etapa. Un camp de care depinde
# un raport, dar pe care nimic nu-l cere, dispare la prima rescriere.
ANTET_CAMPURI = ("etapa", "pasul curent", "criteriul de terminare", "ce lipsește",
                 "decizii care blochează", "avertisment la cifre", "ultima actualizare")

CAP_ANTET = "## ANTET DE ETAPĂ"

# `pasul curent` PLAFONAT (23.08.2026, decizia lui Costin). De doua ori in doua zile antetul a ramas
# in urma corpului, si de fiecare data pe partea NUMARABILA. Regula scrisa in registru: daca o
# propozitie se poate confrunta cu o cifra, nu e a antetului - e a derivatorului. Plafonul e gardul
# care NU citeste proza si totusi o disciplineaza: nu judeca ce scrie, face imposibila acumularea.
LIMITA_PAS_CURENT = 300

# `felul limitei` pe PARTIAL (23.08.2026). PARTIAL acoperea DOUA lucruri diferite: o regiune cunoscuta
# lasata afara (DOMENIU) si un instrument fara calibrare pe propriul mod de esec (ORBIRE). Al doilea e
# mai grav. NU e o stare noua - cele patru stari descriu ce s-a intamplat cu MASURATOAREA, iar orbirea
# e o proprietate a INSTRUMENTULUI. Motivul pentru care nu ajunge sa fie scris in proza sectiunii:
# proza nu se numara, si tocmai de asta nu s-a vazut ca sunt doua populatii.
FELURI_LIMITA = ("DOMENIU", "ORBIRE")


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


# ─────────────────────────────────────────────────────────────────── RESTANȚE
#
# Cerute de Costin, 22.08.2026: *„dacă restanțele nu apar nicăieri în B, B spune că nimic nu
# blochează."* Consecința era vizibilă chiar în raportul care a produs observația: antetul spunea
# „decizii care blochează: niciuna" într-un moment în care categoria de mărime bloca o familie
# întreagă din 1a. Formal corect — e restanță, nu decizie — și tocmai de aceea invizibil.
#
# CE FACE IMPOSIBIL: o restanță fără felul blocajului · fără condiție de deblocare scrisă · cu o stare
# din afara celor două · REZOLVATĂ fără să spună pe ce commit · un `deschisă pe commit` inventat.
#
# CE NU FACE, declarat: nu judecă dacă felul ales e cel potrivit, nici dacă condiția de deblocare e
# realistă. Verifică forma și existența. Contorul nu se verifică deloc — se DERIVĂ din git, în
# `scripts/raport_b.py`, tocmai ca să nu existe un număr scris de mână care poate rămâne în urmă.

FELURI = ("SURSĂ", "VERIFICARE", "ARTEFACT")
STARI_RESTANTA = ("DESCHISĂ", "REZOLVATĂ")
CAMPURI_RESTANTA = ("felul", "cine deblochează", "unde intră", "reluări", "stare",
                    "deschisă pe commit", "ce blochează", "condiția de deblocare")


def _restante(t=None):
    """{cod: (titlu, corp)} pentru blocurile `### R<n> — <titlu>` din secțiunea RESTANȚE."""
    if t is None:
        t = io.open(CONF, encoding="utf-8").read()
    m = re.search(r"^## RESTANȚE[ \t]*$(.*?)^## ", t, re.M | re.S)
    if m is None:
        return {}
    buc = re.split(r"^### (R\d+)\s*[—-]\s*(.+)$", m.group(1), flags=re.M)
    return {buc[k]: (buc[k + 1].strip(), buc[k + 2]) for k in range(1, len(buc), 3)}


def test_cititorul_de_restante_chiar_vede_restante():
    """ANTI-VACUU. Un regex rupt ar face toate testele de mai jos să treacă pe zero restanțe."""
    fals = "## RESTANȚE\n\n### R9 — proba\n- **felul**: SURSĂ\n\n## E1 — x\n"
    r = _restante(fals)
    assert list(r) == ["R9"], "parsarea restanțelor s-a rupt: %r" % list(r)
    assert _camp(r["R9"][1], "felul") == "SURSĂ"
    assert _restante("fără secțiune\n") == {}


def test_registrul_are_sectiunea_de_restante():
    r = _restante()
    assert r, (
        "CONFORMITATE.md n-are secțiunea `## RESTANȚE`. Fără ea, secțiunea B a raportului spune că "
        "nimic nu blochează, chiar când o familie întreagă din 1a e blocată.")


def _aproape(corp, camp):
    """Dacă în corp există un rând care ÎNCEPE cu eticheta dar nu se potrivește, îl arată.

    [27.08.2026] Cauza reală a trei eșecuri într-o singură zi, toate ale mele: un sufix strecurat
    ÎNTRE etichetă și cele două puncte — `- **condiția de deblocare** *(atunci)*: …`. Cititorul
    cere eticheta exactă, deci vede câmpul ca **absent**, iar mesajul spunea „lipsește sau e gol"
    pe un rând care era acolo, sub ochi. Un mesaj care numește cauza costă cinci rânduri și scade
    de trei ori căutarea.
    """
    for linie in corp.splitlines():
        s = linie.strip()
        if s.startswith("- **" + camp) and not s.startswith("- **" + camp + "**:"):
            return (" — dar există un rând care începe cu eticheta și NU se potrivește: %r. "
                    "Forma cerută e `- **%s**: …`; orice sufix între etichetă și cele două "
                    "puncte face câmpul invizibil." % (s[:90], camp))
    return ""


def test_fiecare_restanta_e_completa():
    rele = []
    for cod, (_titlu, corp) in sorted(_restante().items()):
        for camp in CAMPURI_RESTANTA:
            v = _camp(corp, camp)
            # `reluări` e NUMERIC: „0" e un răspuns complet, deși are un caracter. Se verifică
            # separat, în test_fiecare_restanta_spune_unde_intra_si_de_cate_ori_a_fost_reluata.
            prag = 1 if camp == "reluări" else 3
            if v is None or len(v.strip("*—- ")) < prag:
                rele.append("  %s: câmpul `%s` lipsește sau e gol%s"
                            % (cod, camp, _aproape(corp, camp)))
        # felul se verifica in test_felurile_de_blocaj_sunt_cele_patru (patru, nu trei)
        st = (_camp(corp, "stare") or "").strip("* ").split("(")[0].strip()
        if st and st not in STARI_RESTANTA:
            rele.append("  %s: stare %r — cele două sunt: %s" % (cod, st, ", ".join(STARI_RESTANTA)))
        if st == "REZOLVATĂ" and not _camp(corp, "rezolvată pe commit"):
            rele.append("  %s: REZOLVATĂ fără `rezolvată pe commit`" % cod)
    assert not rele, "restanțe incomplete:\n" + "\n".join(rele)


def test_commiturile_restantelor_exista():
    """O restanță ancorată pe un commit inventat n-are contor, deci n-are vechime."""
    rele = []
    for cod, (_titlu, corp) in sorted(_restante().items()):
        for camp in ("deschisă pe commit", "rezolvată pe commit"):
            v = (_camp(corp, camp) or "").strip("`*— ")
            if not v:
                continue
            if _git("cat-file", "-e", "%s^{commit}" % v).returncode != 0:
                rele.append("  %s: `%s` = %r nu există în istoric" % (cod, camp, v))
    assert not rele, "commituri inexistente în restanțe:\n" + "\n".join(rele)


# ──────────────────────── ORDINE, `unde intră`, `reluări`, și închiderea etapei
#
# Cerute de `PLAN_LUCRU.md` („Restanțele"), secțiunea scrisă de Costin. Au stat opt commituri
# neimplementate fiindcă secțiunea a intrat în repo într-un `git add` fără citirea diff-ului — vezi
# acolo, „De unde vin cele două". Gardul e reparația clasei, nu doar a instanței.

FELURI_4 = ("SURSĂ", "VERIFICARE", "ARTEFACT", "ORDINE")
CINE_VALIDE = ("EXTERN", "INTERN", "DECIZIE")
ETAPE = ("E1", "E2", "E3", "E4", "E5")


def test_felurile_de_blocaj_sunt_cele_patru():
    rele = []
    for cod, (_t, corp) in sorted(_restante().items()):
        fel = (_camp(corp, "felul") or "").strip("* ")
        if fel not in FELURI_4:
            rele.append("  %s: felul %r — cele patru sunt %s" % (cod, fel, ", ".join(FELURI_4)))
    assert not rele, "feluri de blocaj nevalide:\n" + "\n".join(rele)


def test_fiecare_restanta_spune_unde_intra_si_de_cate_ori_a_fost_reluata():
    """`unde intră` face posibilă garda de mai jos; `reluări` face vizibilă condiția scrisă greșit."""
    rele = []
    for cod, (_t, corp) in sorted(_restante().items()):
        u = _camp(corp, "unde intră")
        if not u or not any(e in u for e in ETAPE):
            rele.append("  %s: `unde intră` = %r — trebuie să numească o etapă din %s"
                        % (cod, u, ", ".join(ETAPE)))
        r = (_camp(corp, "reluări") or "").strip("* ")
        if not re.fullmatch(r"\d+", r):
            rele.append("  %s: `reluări` = %r — se scrie ca număr" % (cod, r))
    assert not rele, "restanțe fără etapă sau fără contorul de reluări:\n" + "\n".join(rele)


def test_trei_reluari_fara_rezultat_cer_rescrierea_conditiei():
    """«O restanță reluată de trei ori și tot nerezolvată: condiția e scrisă greșit, nu restanța e
    grea.» A patra reluare pe aceeași condiție nu trece."""
    rele = []
    for cod, (_t, corp) in sorted(_restante().items()):
        if "DESCHISĂ" not in (_camp(corp, "stare") or ""):
            continue
        r = int((_camp(corp, "reluări") or "0").strip("* ") or 0)
        if r >= 3 and "condiție rescrisă" not in corp.lower():
            rele.append("  %s: %d reluări fără rezultat, iar condiția n-a fost rescrisă" % (cod, r))
    assert not rele, ("restanțe reluate de ≥3 ori pe aceeași condiție:\n" + "\n".join(rele)
                      + "\nSe rescrie condiția, prin decizie, și se notează «condiție rescrisă».")


def _etape_declarate_terminate(a):
    """Etapele pe care ANTETUL le declară încheiate, oricare ar fi cuvântul folosit."""
    gasit = set()
    for m in re.finditer(r"\b(E[1-5])\b[^.\n]{0,80}?\b(TERMINAT[ĂA]?|ÎNCHEIAT[ĂA]?|ÎNCHIS[ĂA]?|GATA)\b",
                         a, re.I):
        gasit.add(m.group(1))
    return gasit


def test_o_etapa_nu_se_inchide_peste_restantele_ei():
    """`PLAN_LUCRU.md`: «o etapă nu se poate declara terminată dacă are restanțe deschise care îi
    aparțin». Fără gardă, pragul de la închiderea lui 1b ar fi o intenție."""
    a = _antet()
    inchise = _etape_declarate_terminate(a)
    rele = []
    for cod, (_t, corp) in sorted(_restante().items()):
        if "DESCHISĂ" not in (_camp(corp, "stare") or ""):
            continue
        u = _camp(corp, "unde intră") or ""
        for e in inchise:
            if re.search(r"\b%s\b" % e, u):
                rele.append("  %s (deschisă) aparține lui %s, dar antetul îl declară terminat" % (cod, e))
    assert not rele, "etape declarate terminate peste restanțe deschise:\n" + "\n".join(rele)


def test_cititorul_de_etape_terminate_chiar_vede():
    """ANTI-VACUU: fără el, garda de mai sus trece pe orice antet, fiindcă azi nicio etapă nu e
    declarată terminată — adică pe zero rânduri."""
    assert _etape_declarate_terminate("etapa E1 e TERMINATĂ") == {"E1"}
    assert _etape_declarate_terminate("E3 — încheiată") == {"E3"}
    assert _etape_declarate_terminate("etapa E1 — SETUL COMPLET, în lucru") == set()


def test_o_restanta_EXTERN_are_cerere_specifica():
    """Ultima dintre cele patru cerințe din `PLAN_LUCRU.md` („Ce se gardează"), rămasă neimplementată
    după împăcarea taxonomiilor: *«o restanță cu blocaj EXTERN fără cerere specifică formulată nu
    trece»*. A devenit gardabilă în momentul în care nota „cine deblochează" a devenit CÂMP.

    O cerere specifică are trei elemente: **ce trebuie · de unde · pentru ce**. Fără ele, „aștept ceva
    din afară" nu e o restanță blocată, e o restanță nescrisă."""
    rele = []
    for cod, (_t, corp) in sorted(_restante().items()):
        cine = (_camp(corp, "cine deblochează") or "").strip("* ")
        if cine not in CINE_VALIDE:
            rele.append("  %s: `cine deblochează` = %r — cele trei sunt %s"
                        % (cod, cine, ", ".join(CINE_VALIDE)))
            continue
        if cine != "EXTERN":
            continue
        cond = (_camp(corp, "condiția de deblocare") or "").lower()
        lipsa = [e for e, chei in (("ce trebuie", ("trebuie", "cere", "lipsește")),
                                   ("de unde", ("de la", "din ", "de unde")),
                                   ("pentru ce", ("blochează", "pentru ", "ca să")))
                 if not any(k in cond for k in chei)]
        if lipsa:
            rele.append("  %s: EXTERN fără cerere specifică — lipsește: %s" % (cod, ", ".join(lipsa)))
    assert not rele, "restanțe cu blocaj nedeclarat sau EXTERN fără cerere:\n" + "\n".join(rele)


def test_gardul_EXTERN_chiar_ar_prinde():
    """ANTI-VACUU. Azi nicio restanță nu e EXTERN, deci garda de mai sus trece pe zero rânduri —
    exact interdicția 19. Proba se face pe un corp sintetic."""
    corp = ("- **cine deblochează**: EXTERN\n"
            "- **condiția de deblocare**: se rezolvă cândva.\n")
    cond = (_camp(corp, "condiția de deblocare") or "").lower()
    lipsa = [e for e, chei in (("ce trebuie", ("trebuie", "cere", "lipsește")),
                               ("de unde", ("de la", "din ", "de unde")),
                               ("pentru ce", ("blochează", "pentru ", "ca să")))
             if not any(k in cond for k in chei)]
    assert lipsa == ["ce trebuie", "de unde", "pentru ce"], (
        "tiparul nu prinde o cerere goală: %s" % lipsa)
    assert _camp(corp, "cine deblochează").strip() == "EXTERN"


def test_antetul_nu_spune_niciuna_cand_corpul_are_o_decizie():
    """COERENȚĂ INTERNĂ, nu doar prezență. Cerută 23.08.2026, după a doua instanță în două zile:
    antetul a scris „decizii care blochează: **niciuna deschisă**" în chiar commitul care adăuga o
    decizie în corp — iar secțiunea B a raportului se DERIVĂ din antet, deci minciuna s-ar fi repetat
    la fiecare citire.

    Gardul de până acum cerea ca fiecare câmp să EXISTE și să nu fie gol. Un câmp plin și fals trecea.
    Aici se compară două locuri care vorbesc despre același lucru: marcajul canonic **Decizie cerută.**
    din corp, și câmpul din antet. Nu poate verifica dacă o decizie e „reală" — verifică doar că cele
    două nu se contrazic, ceea ce e chiar clasa care a scăpat de două ori."""
    corp = io.open(CONF, encoding="utf-8").read().split("## ANTET DE ETAPĂ", 1)[-1]
    antet, restul = corp.split("\n---", 1) if "\n---" in corp else (corp, "")
    camp = ""
    for linie in antet.splitlines():
        if linie.startswith("- **decizii care blochează**:"):
            camp = linie
            break
    assert camp, "antetul n-are câmpul «decizii care blochează»"
    cereri = restul.count("**Decizie cerută.**")
    # VERDICTUL se citeste de la INCEPUTUL campului, nu din proza lui. Prima forma a gardei cauta
    # „niciuna" oriunde si a picat pe un camp corect, fiindca explicatia continea „niciuna dintre cele
    # trei instante". O garda de coerenta care nu-si distinge verdictul de justificare e chiar clasa
    # pe care o pazeste.
    val = camp.split(":", 1)[1].strip()
    spune_niciuna = val.startswith("**niciuna")
    assert spune_niciuna or "DESCHISĂ" in val.split(".")[0], (
        "câmpul «decizii care blochează» nu începe cu un verdict citibil mecanic: aștept «**niciuna...» "
        "sau un «... DESCHISĂ» în prima propoziție. Găsit: %s" % val[:80])
    assert not (cereri and spune_niciuna), (
        "ANTETUL SE CONTRAZICE CU CORPUL: câmpul spune «niciuna», dar corpul are %d marcaj(e) "
        "«**Decizie cerută.**». Raportul derivă B din antet, deci ar repeta afirmația falsă." % cereri)
    assert not (spune_niciuna is False and cereri == 0), (
        "antetul anunță o decizie deschisă, dar corpul n-are niciun marcaj «**Decizie cerută.**» — "
        "atunci decizia nu se poate găsi de cine citește registrul")


def test_deciziile_numite_in_antet_sunt_DESCHISE():
    """Ce n-a putut prinde garda de coerență de mai sus, și s-a întâmplat azi: antetul numea `R49`
    la «decizii care blochează» după ce R49 se închisese. Marcajul `**Decizie cerută.**` rămăsese în
    paragraful ei istoric, deci numărătoarea trecea — iar secțiunea B a raportului se derivă din
    antet, deci ar fi repetat o decizie rezolvată la fiecare citire.

    Aici se compară NUMELE din antet cu STAREA restanței numite. E a patra oară într-o singură zi
    când proza antetului rămâne în urma cifrelor; proza nu se poate deriva, deci se păzește."""
    text = io.open(CONF, encoding="utf-8").read()
    corp = text.split("## ANTET DE ETAPĂ", 1)[-1]
    antet = corp.split(chr(10) + "---", 1)[0]
    camp = next((l for l in antet.splitlines()
                 if l.startswith("- **decizii care blochează**:")), "")
    assert camp, "antetul n-are câmpul «decizii care blochează»"
    numite = sorted(set(re.findall(r"\bR(\d+)\b", camp)))
    if not numite:
        return                      # „niciuna" — acoperit de garda precedentă
    stari = {cod: (_camp(c, "stare") or "").strip()
             for cod, (_t, c) in _restante().items()}
    rele = []
    for n in numite:
        cod = "R" + n
        st = stari.get(cod)
        if st is None:
            rele.append("  %s: numită în antet, dar nu există în registru" % cod)
        elif not st.startswith("DESCHIS"):
            rele.append("  %s: numită ca decizie care blochează, dar e %s" % (cod, st))
    assert not rele, ("antetul numește ca decizii care blochează restanțe care nu blochează:"
                      + chr(10) + chr(10).join(rele))


def test_restanta_care_cere_decizie_a_citit_planul():
    """GARD [METODA §25, 25.08.2026]: o restanță DESCHISĂ pe care o deblochează o DECIZIE trebuie să
    spună unde a căutat răspunsul în plan.

    Instanța: ierarhia surselor era scrisă în PLAN_ARHITECTURA, Partea 0, Pasul 4 — *„validatorul e
    constrângere, nu sursă"* — iar restanța a cerut decizia cinci ture la rând. Costin: *„problema nu
    e condiția restanței, e că restanța nu citește planul."*

    Câmpul `- **planul**:` are două forme legitime: locul din plan care RĂSPUNDE (și atunci restanța
    se închide pe el, nu se mai cere), sau `NEACOPERIT` cu ce s-a citit. A treia formă — absența —
    e chiar defectul. Clichet, fiindcă cele existente cer citirea planului una câte una: se coboară,
    nu se umple prin copiere (o citire copiată e mai rea decât absența — trece verde)."""
    fara = []
    for cod, (_t, corp) in sorted(_restante().items(), key=lambda x: int(x[0][1:])):
        stare = (_camp(corp, "stare") or "").strip()
        cine = (_camp(corp, "cine deblochează") or "").strip()
        if not stare.startswith("DESCHIS") or cine != "DECIZIE":
            continue
        plan = _camp(corp, "planul")
        if not plan or len(plan.strip()) < 40:
            fara.append(cod)
    assert len(fara) <= _CLICHET_FARA_PLAN, (
        "restanțe DESCHISE deblocate de DECIZIE care nu spun unde au căutat în plan "
        "(clichet %d, acum %d): %s" % (_CLICHET_FARA_PLAN, len(fara), fara))
    assert len(fara) == _CLICHET_FARA_PLAN, (
        "clichetul e depășit — coboară-l la %d" % len(fara))


def test_decizie_ceruta_nu_ramane_intr_o_restanta_inchisa():
    """Perechea gardului de antet: marcajul `**Decizie cerută.**` rămas în corpul unei restanțe
    ÎNCHISE e chiar ce a făcut numărătoarea să treacă verde în timp ce antetul repeta o decizie
    rezolvată. Într-o restanță închisă, cererea de atunci se scrie ca istorie: `[atunci]`."""
    rele = []
    for cod, (_t, corp) in sorted(_restante().items(), key=lambda x: int(x[0][1:])):
        stare = (_camp(corp, "stare") or "").strip()
        if stare.startswith("DESCHIS"):
            continue
        if re.search(r"\*\*Decizie cerută\.\*\*", corp):
            rele.append(cod)
    assert not rele, (
        "restanțe ÎNCHISE care mai poartă «Decizie cerută» în corp (scrie-l ca istorie, "
        "`**Decizie cerută [atunci].**`): %s" % rele)


def test_pasul_curent_nu_devine_naratiune():
    """Plafon MECANIC pe `pasul curent`. Nu citește proza: numără caractere.

    CE FACE IMPOSIBIL: ca antetul să acumuleze o narațiune care repetă cifre derivabile și
    îmbătrânește. CE NU FACE: nu verifică dacă ce scrie e adevărat — plafonul e o limită de formă.
    """
    text = io.open(CONF, encoding="utf-8").read()
    corp = text.split(CAP_ANTET, 1)[-1]
    linie = ""
    for l in corp.splitlines():
        if l.startswith("- **pasul curent**:"):
            linie = l
            break
    assert linie, "antetul n-are câmpul «pasul curent» — plafonul ar trece pe zero rânduri"
    val = linie.split(":", 1)[1].strip()
    assert val, "«pasul curent» e gol"
    assert len(val) <= LIMITA_PAS_CURENT, (
        "«pasul curent» are %d caractere, plafonul e %d. Regula: dacă o propoziție se poate "
        "confrunta cu o cifră, nu e a antetului — e a derivatorului (scripts/raport_b.py). "
        "Mută-o în secțiunea ei." % (len(val), LIMITA_PAS_CURENT))


def test_partialele_declara_FELUL_limitei(conf):
    """O stare PARȚIAL spune că măsurătoarea nu e completă; nu spune DE CE. Cele două motive au
    consecințe diferite: o regiune cunoscută lăsată afară se poate acoperi cu efort (DOMENIU), un
    instrument necalibrat pe propriul mod de eșec nu știe nici măcar ce ratează (ORBIRE).

    CE FACE IMPOSIBIL: ca cele două să rămână amestecate sub aceeași etichetă, unde nu se pot
    număra. CE NU FACE: nu judecă dacă felul ales e cel potrivit — aia e o citire de om.
    """
    rele, vazute = [], 0
    for n, (_titlu, corp) in sorted(conf.items()):
        if "PARȚIAL" not in (_camp(corp, "stare") or ""):
            continue
        vazute += 1
        brut = (_camp(corp, "felul limitei") or "").strip("* ")
        val = brut.split("—")[0].split("-")[0].strip()
        if val not in FELURI_LIMITA:
            rele.append("  #%d: `felul limitei` = %r — cele două sunt: %s"
                        % (n, val or "(lipsă)", ", ".join(FELURI_LIMITA)))
    assert vazute, "nicio secțiune PARȚIAL — garda ar raporta verde pe zero rânduri"
    assert not rele, "PARȚIAL fără felul limitei declarat:\n" + "\n".join(rele)

