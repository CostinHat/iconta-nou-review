# -*- coding: utf-8 -*-
"""Probele lotului de unelte 17.5-U2 (U2.1, U2.2): excepția numerică unică la „max hook” din scripts/publica_lot.py (recipisa exceptii_praguri_<lot>.txt, amprenta fixată în
RECIPISE_APROBATE, perechea rezolvată exact în jurnal, ID-ul scos numai din comparația `max hook`), publicarea prin verifica() pe o copie cu toate celelalte condiții satisfăcute și prin
fluxul main() care scrie raportul și ZIP-ul, plus generatorul pragurilor (scripts/praguri_automate.py) pe seria F6. Fără DB, fără 8019: un depozit git temporar, jurnal (LOT_JURNAL),
director al arhitectului (GHID_INCOMING) și „acasă” temporare; RAD / DEP / ACASA ale scriptului mutate pe copie (monkeypatch), raportul de timp oprit (ar scrie în ~ real)."""
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from contextlib import redirect_stdout

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import jurnal_lot as JL  # noqa: E402
import poarta_lib as L  # noqa: E402
import praguri_automate as PA  # noqa: E402
import publica_lot as PL  # noqa: E402

LOT = "17.5-F6"
LOTF = "17_5_F6"
ID_EXC = "2383537-1795837151686"
#: cele cinci măsurări hook reale ale lui 17.5-F6 (106 + 125 + 105 + 127 + 100 = 563 s); 127 s e rularea aprobată
HOOK_F6 = [("1997080-1795825085260", 106), ("1999009-1795825196588", 125), ("2235935-1795832845867", 105), (ID_EXC, 127), ("2391581-1795837283652", 100)]
PRAGURI = "unelte\nlot: 17.5-F6\nmax hook 126\nmax poarta_verificator 114\nmax poarta_pytest 695\nmax poarta_plasa 4063\n"
T0 = datetime.datetime(2026, 11, 28, 2, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))


def _ora(sec):
    return (T0 + datetime.timedelta(seconds=sec)).isoformat(timespec="seconds")


def _git(cwd, *a):
    r = subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class Copie:
    """Depozitul temporar al lotului 17.5-F6 cu toate condițiile verifica() satisfăcute (lot «unelte» al probei, cu rânduri `max`), în afara pragului hook: cele cinci măsurări reale."""

    def __init__(self, tmp, monkeypatch):
        self.tmp = str(tmp)
        self.dir = os.path.join(self.tmp, "dep")
        self.acasa = os.path.join(self.tmp, "acasa")
        self.ghid = os.path.join(self.tmp, "ghid")
        self.jurnal = os.path.join(self.tmp, "jurnal.log")
        for d in (self.dir, self.acasa, self.ghid, os.path.join(self.acasa, "backup_" + LOTF)):
            os.makedirs(d, exist_ok=True)
        _git(self.dir, "init", "-q", "-b", "main")
        os.makedirs(os.path.join(self.dir, "scripts"))
        open(os.path.join(self.dir, L.MANIFEST), "w").write("manifest\n")
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-q", "-m", "baza")
        self.baza = _git(self.dir, "rev-parse", "HEAD")
        _git(self.dir, "checkout", "-q", "-b", "lucru/lot17-5f6")
        open(os.path.join(self.dir, "scripts", "praguri_%s.txt" % LOTF), "w").write(PRAGURI)
        os.makedirs(os.path.join(self.dir, "docs", "dovezi", LOTF))
        json.dump({"antet": {"commit_baza": self.baza, "manifest_sha256": L.hash_fisier(os.path.join(self.dir, L.MANIFEST))}},
                  open(os.path.join(self.dir, "docs", "dovezi", LOTF, "baza.json"), "w"))
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-q", "-m", "C")
        self.c = _git(self.dir, "rev-parse", "HEAD")
        self.comun = os.path.join(self.dir, ".git")
        self.raport = os.path.join(self.acasa, "lot_%s_raport.md" % LOTF)
        self.zip = os.path.join(self.acasa, "lot_%s.zip" % LOTF)
        self.recipisa = os.path.join(self.ghid, "exceptii_praguri_%s.txt" % LOTF)
        open(os.path.join(self.acasa, "backup_" + LOTF, "CLAUDE.md"), "w").write("x\n")
        open(self.raport, "w", encoding="utf-8").write("# Raport %s\n\nC = %s\n\nRulări „intrerupt” pe fază: niciuna\n" % (LOT, self.c))
        json.dump({"complete": [{"sha": self.c, "data": "x", "curat": True}], "reluari": [], "regresii": [], "oprit": None, "infra": []},
                  open(os.path.join(self.comun, "lot_stare_%s.json" % LOTF), "w"))
        json.dump({"clase": {}}, open(os.path.join(self.comun, "lot_picate_%s.json" % LOTF), "w"))
        open(os.path.join(self.comun, "poarta_verdicte.log"), "w").write("VERDE %s lucru/lot17-5f6 %s completa curat\n" % (self.c, _ora(0)))
        for k, v in (("RAD", self.dir), ("DEP", self.dir), ("ACASA", self.acasa)):
            monkeypatch.setattr(PL, k, v)
        monkeypatch.setattr(L, "RAD", self.dir)
        monkeypatch.setattr(PL, "lucru_si_timp", lambda lot: [])
        monkeypatch.setenv("LOT_JURNAL", self.jurnal)
        monkeypatch.setenv("GHID_INCOMING", self.ghid)
        monkeypatch.setenv("LOT", LOT)
        self.mp = monkeypatch
        self.t = 0
        self.n = 0
        self.randuri = []
        h = L.hash_fisier(os.path.join(self.dir, "scripts", "praguri_%s.txt" % LOTF))
        self.pereche("pornire", 0, "ok", detalii_inc="praguri=praguri_%s.txt praguri_sha256=%s reconstituit" % (LOTF, h), id_="p-1")
        self.pereche("proba_contract", 0, "verde", id_="pc-1")
        for id_, sec in HOOK_F6:
            self.pereche("hook", sec, "verde", sha=self.c[:12] if id_ == ID_EXC else self.baza[:12], id_=id_)
        for faza, sec in (("poarta_verificator", 101), ("poarta_pytest", 606), ("poarta_plasa", 3182)):
            self.pereche(faza, sec, "verde", sha=self.c[:12])
        self.scrie()
        self.rand(LOT, "publicare", "inceput", _ora(self.t + 10000), self.c[:12], "-", "pub-1", str(os.getpid()), "")

    def rand(self, *campuri):
        with open(self.jurnal, "a", encoding="utf-8") as f:
            f.write("\t".join(campuri) + "\n")

    def pereche(self, faza, sec, rezultat, sha=None, id_=None, lot=LOT, detalii_inc="", fara_inceput=False, fara_sfarsit=False, scrie=False):
        self.n += 1
        id_ = id_ or "%d-%d" % (900000 + self.n, 1795000000000 + self.n)
        sha = sha or self.c[:12]
        self.t += 60
        if not fara_inceput:
            self.randuri.append([lot, faza, "inceput", _ora(self.t), sha, "-", id_, "1", detalii_inc])
        if not fara_sfarsit:
            self.randuri.append([lot, faza, "sfarsit", _ora(self.t + sec), sha, rezultat, id_, "1", ""])
        self.t += sec
        if scrie:
            self.scrie()
        return id_

    def scrie(self):
        for r in self.randuri:
            self.rand(*r)
        self.randuri = []

    def campuri(self, **sub):
        """Rândul recipisei pentru rularea aprobată (valorile reale ale formatului v1), cu înlocuirile date."""
        sf = next(r for r in JL.citeste_jurnal(self.jurnal) if r[6] == ID_EXC and r[2] == "sfarsit")[3]
        v = {"lot": LOT, "faza": "hook", "id": ID_EXC, "sfarsit": sf, "sha": self.c, "secunde": "127", "aprobator": "Costin",
             "aprobat_la": "2026-11-28T06:50:24+02:00", "referinta": "conversatia arhitectului 28.11.2026 (proba)", "motiv": "hook-ul tentativei refuzate de commit-msg: 127 s fata de 126 s"}
        v.update(sub)
        return "\t".join(v[k] for k in PL.CAMPURI_RECIPISA)

    def recipisa_scrie(self, text=None, aproba=True, octeti=None):
        octeti = octeti if octeti is not None else ((self.campuri() + "\n") if text is None else text).encode("utf-8")
        open(self.recipisa, "wb").write(octeti)
        if aproba:
            self.mp.setattr(PL, "RECIPISE_APROBATE", {LOT: {"sha256": hashlib.sha256(octeti).hexdigest(), "faza": "hook", "prag": 126, "aprobare": "proba 17.5-U2"}})

    def verifica(self, exceptie=None):
        PL.zip_lot(LOT, self.c, self.zip, self.recipisa if os.path.exists(self.recipisa) else None)
        return PL.verifica(LOT, self.c, self.comun, self.zip, exceptie)

    def publica(self):
        """Fluxul main(): decizia înaintea ZIP-ului, secțiunea în raport, ZIP-ul, verifica(), PASS / STOP. -> (ieșire, text)."""
        self.mp.setattr(sys, "argv", ["publica_lot.py"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = PL.main()
        return rc, buf.getvalue()


@pytest.fixture
def copie(tmp_path, monkeypatch):
    return Copie(tmp_path, monkeypatch)


def _hook_stop(stop):
    return [m for m in stop if m.startswith("pragul „hook”")]


# ── comportamentul vechi: fără recipisă ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_fara_recipisa_stop_la_127_ca_inainte(copie):
    stop = copie.verifica()
    assert stop == ["pragul „hook” depășit: 127s > 126s"]
    rc, out = copie.publica()
    assert rc == 1
    assert "OPRIT — gata: 17.5-F6 nepublicat, pragul „hook” depășit: 127s > 126s" in out
    assert "exceptie_hook" not in open(copie.raport, encoding="utf-8").read()
    assert "exceptie/" not in " ".join(zipfile.ZipFile(copie.zip).namelist())


# ── recipisa exactă: o excepție, maximul rămas 125 ───────────────────────────────────────────────────────────────────────────────────────────
def test_recipisa_exacta_o_exceptie_maxim_ramas_125_si_pass_prin_main(copie):
    copie.recipisa_scrie()
    rc, out = copie.publica()
    assert rc == 0, out
    assert "[publica_lot] PASS %s" % copie.c in out
    assert "excepție aprobată" in out and ID_EXC in out
    raport = open(copie.raport, encoding="utf-8").read()
    sec = PL.extrage_sectiune(raport)
    assert sec is not None
    for text in ("Număr: 1 (ID %s" % ID_EXC, "Durată / prag: 127 s / 126 s", "Aprobator: Costin", "înainte / după excepție: 127 s / 125 s", "Alte depășiri ale pragului „hook”: niciuna",
                 hashlib.sha256(open(copie.recipisa, "rb").read()).hexdigest(), "SHA-ul rulării: %s" % copie.c):
        assert text in sec, text
    z = zipfile.ZipFile(copie.zip)
    assert PL.extrage_sectiune(z.read(os.path.basename(copie.raport)).decode("utf-8")) == sec
    assert z.read("exceptie/" + os.path.basename(copie.recipisa)) == open(copie.recipisa, "rb").read()
    assert z.read("sha.txt").decode().strip() == copie.c
    assert sorted(z.read("fisiere_diff.txt").decode().split()) == sorted(["docs/dovezi/%s/baza.json" % LOTF, "scripts/praguri_%s.txt" % LOTF])
    d, s, rez, _ = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    assert s == [] and d["id"] == ID_EXC and rez["numar"] == 1 and rez["max_inainte"] == 127 and rez["max_dupa"] == 125 and rez["rulari"] == 5


def test_doua_invocari_succesive_aceeasi_decizie_recipisa_neconsumata_sectiune_unica(copie):
    copie.recipisa_scrie()
    octeti, mtime = open(copie.recipisa, "rb").read(), os.stat(copie.recipisa).st_mtime_ns
    assert copie.publica()[0] == 0
    prima = open(copie.raport, encoding="utf-8").read()
    assert copie.publica()[0] == 0
    a_doua = open(copie.raport, encoding="utf-8").read()
    assert prima == a_doua and a_doua.count(PL.MARCAJ_EXCEPTIE[0]) == 1
    assert open(copie.recipisa, "rb").read() == octeti and os.stat(copie.recipisa).st_mtime_ns == mtime
    d7 = PL.durate_cu_sha(LOT)
    assert PL.exceptie_hook(LOT, d7) == PL.exceptie_hook(LOT, d7)
    assert open(os.path.join(copie.comun, "publica_verdicte.log")).read().count("PASS %s" % copie.c) == 2


def test_al_doilea_hook_peste_126_pe_alt_sha_ramane_stop(copie):
    copie.pereche("hook", 130, "verde", sha="abcdef012345", scrie=True)
    copie.recipisa_scrie()
    stop = copie.verifica()
    assert _hook_stop(stop) == ["pragul „hook” depășit: 130s > 126s"]
    _, _, rez, sec = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    assert rez["alte_depasiri"] and rez["alte_depasiri"][0][1] == 130 and "= 130 s" in sec


def test_hook_dupa_poarta_pe_acelasi_sha_peste_126_ramane_stop(copie):
    copie.pereche("hook", 127, "verde", sha=copie.c[:12], scrie=True)
    copie.recipisa_scrie()
    assert _hook_stop(copie.verifica()) == ["pragul „hook” depășit: 127s > 126s"]


def test_egalitatea_cu_pragul_trece(copie):
    copie.pereche("hook", 126, "verde", sha="abcdef012345", scrie=True)
    copie.recipisa_scrie()
    rc, out = copie.publica()
    assert rc == 0, out
    assert "Alte depășiri ale pragului „hook”: niciuna" in PL.extrage_sectiune(open(copie.raport, encoding="utf-8").read())


# ── negativele: fiecare cheie modificată, aprobarea, amprenta ───────────────────────────────────────────────────────────────────────────────
MODIFICARI = {"lot": ("17.5-F7", "alt lot"), "faza": ("poarta_verificator", "altă fază"), "id": ("2383537-1795837151687", "ID orfan"),
              "sfarsit": ("2026-11-28T05:41:19+02:00", "sfârșitul din recipisă"), "sha": ("8d876246bd95255e4d936cec6ccc20c0f1b9761e", "nu începe cu prefixul"),
              "secunde": ("126", "durata nativă"), "aprobator": ("Arhitect", "aprobator neautorizat"), "aprobat_la": ("2026-11-28T01:00:00+02:00", "anterioară"),
              "referinta": ("alta", None), "motiv": ("alt motiv", None)}


@pytest.mark.parametrize("cheie", sorted(MODIFICARI))
def test_fiecare_cheie_modificata_stop(copie, cheie):
    valoare, motiv = MODIFICARI[cheie]
    original = copie.campuri() + "\n"
    copie.recipisa_scrie(original)          # amprenta aprobată = recipisa exactă
    open(copie.recipisa, "w", encoding="utf-8").write(copie.campuri(**{cheie: valoare}) + "\n")
    stop = copie.verifica()
    assert any("recipisa modificată" in m for m in stop), stop
    assert _hook_stop(stop) == ["pragul „hook” depășit: 127s > 126s"]   # excepția respinsă nu scoate nimic din comparație
    if motiv:   # aceeași modificare cu amprenta ei „aprobată”: motivul de conținut, nu numai amprenta
        copie.recipisa_scrie(copie.campuri(**{cheie: valoare}) + "\n")
        d, stop2 = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
        assert d is None and any(motiv in m for m in stop2), stop2
        assert all(m.startswith("excepția hook (17.5-F6, exceptii_praguri_17_5_F6.txt), rândul ") for m in stop2)


def test_aprobare_lipsa_sau_amprenta_invalida(copie, monkeypatch):
    copie.recipisa_scrie()
    monkeypatch.setattr(PL, "RECIPISE_APROBATE", {})
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("neautorizat" in m for m in stop)
    monkeypatch.setattr(PL, "RECIPISE_APROBATE", {LOT: {"sha256": "0" * 64, "faza": "hook", "prag": 126, "aprobare": "x"}})
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("recipisa modificată" in m for m in stop)
    assert "pragul „hook” depășit: 127s > 126s" in copie.verifica()


def test_prefix_scurt_nedeterminat_sau_ambiguu(copie):
    copie.recipisa_scrie()
    rows = JL.citeste_jurnal(copie.jurnal)
    d7 = PL.durate_cu_sha(LOT)
    for prefix, motiv in ((copie.c[:8], "prefix scurt"), ("-", "prefix scurt")):
        alt = [r[:4] + [prefix] + r[5:] if r[6] == ID_EXC and r[2] == "inceput" else r for r in rows]
        d, stop = PL.exceptie_hook(LOT, d7, rows=alt)
        assert d is None and any(motiv in m for m in stop), stop
    d, stop = PL.exceptie_hook(LOT, d7, rezolva=lambda p: None)   # git: prefix ambiguu sau nerezolvat
    assert d is None and any("nu se rezolvă neambiguu" in m for m in stop)
    d, stop = PL.exceptie_hook(LOT, d7)   # rezolvarea reală, în depozitul copiei
    assert stop == [] and d["sha"] == copie.c


def test_rand_dublat_rand_in_plus_gol_ilizibil(copie, tmp_path):
    rand = copie.campuri() + "\n"
    for text, motiv in ((rand + rand, "rând duplicat"), (rand + copie.campuri(motiv="altul") + "\n", "rând în plus"), ("", "recipisa goală"), ("\n\n", "recipisa goală"),
                        (rand.replace("\n", "\r\n"), "CR"), (rand.rsplit("\t", 1)[0] + "\n", "incomplet"), (rand.rstrip("\n") + "\tx\n", "câmp în plus"),
                        (copie.campuri(referinta=" ") + "\n", "câmpuri goale")):
        copie.recipisa_scrie(text)
        d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
        assert d is None and any(motiv in m for m in stop), (motiv, stop)
    copie.recipisa_scrie(octeti=b"\xff\xfe" + rand.encode())
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("nu e UTF-8" in m for m in stop)
    os.remove(copie.recipisa)
    os.makedirs(copie.recipisa)   # prezent, dar ilizibil
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("ilizibilă" in m for m in stop)
    assert "pragul „hook” depășit: 127s > 126s" in copie.verifica()


def test_id_dublat_fara_inceput_fara_sfarsit_alta_faza_alt_lot(copie):
    copie.recipisa_scrie()
    rows = JL.citeste_jurnal(copie.jurnal)
    inc = next(r for r in rows if r[6] == ID_EXC and r[2] == "inceput")
    sf = next(r for r in rows if r[6] == ID_EXC and r[2] == "sfarsit")
    d7 = PL.durate_cu_sha(LOT)
    cazuri = ((rows + [inc], "pereche ambiguă"), (rows + [sf], "pereche ambiguă"), ([r for r in rows if r is not inc], "nu are început"),
              ([r for r in rows if r is not sf], "nu are sfârșit"), (rows + [[LOT, "poarta_pytest"] + inc[2:]], "altă fază"),
              (rows + [["17.5-F7"] + inc[1:]], "potrivire diferită"), ([r for r in rows if r[6] != ID_EXC], "ID orfan"))
    for alt, motiv in cazuri:
        d, stop = PL.exceptie_hook(LOT, d7, rows=alt)
        assert d is None and any(motiv in m for m in stop), (motiv, stop)


@pytest.mark.parametrize("rezultat", ["intrerupt", "infra", "rosu_1"])
def test_statut_neeligibil(copie, rezultat):
    rows = [r[:5] + [rezultat] + r[6:] if r[6] == ID_EXC and r[2] == "sfarsit" else r for r in JL.citeste_jurnal(copie.jurnal)]
    open(copie.jurnal, "w").write("".join("\t".join(r) + "\n" for r in rows))
    copie.recipisa_scrie()
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("statut neeligibil" in m for m in stop), stop


def test_marcaj_infra_g2_pe_rularea_aprobata_e_pereche_ambigua(copie):
    sf = next(r for r in JL.citeste_jurnal(copie.jurnal) if r[6] == ID_EXC and r[2] == "sfarsit")
    copie.rand(*(sf[:5] + ["infra_g2"] + sf[6:8] + ["proba; durata_prima=127"]))
    copie.recipisa_scrie()
    d, stop = PL.exceptie_hook(LOT, PL.durate_cu_sha(LOT))
    assert d is None and any("pereche ambiguă" in m for m in stop)


def test_alt_lot_nu_foloseste_recipisa_f6(copie, monkeypatch):
    """Publicarea U2 (alt lot) nu citește și nu consumă recipisa F6: calea se construiește cu lot_fisier pentru lotul curent."""
    copie.recipisa_scrie()
    assert PL.cale_recipisa("17.5-U2").endswith("exceptii_praguri_17_5_U2.txt")
    assert PL.exceptie_hook("17.5-U2", []) == (None, [])
    assert os.path.exists(copie.recipisa)


def test_intrarile_schimbate_intre_decizie_si_verificare(copie):
    copie.recipisa_scrie()
    exceptie = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    PL.scrie_sectiune_raport(copie.raport, exceptie[3])
    copie.pereche("hook", 100, "verde", scrie=True)   # jurnalul se mișcă după decizie: altă serie, alt rezumat
    stop = copie.verifica(exceptie)
    assert any("intrările s-au schimbat" in m for m in stop)


def test_raportul_din_zip_fara_sectiune_stop(copie):
    copie.recipisa_scrie()
    stop = copie.verifica()   # raportul de pe disc fără secțiune (main() n-a rulat)
    assert any("raportul" in m and "secțiunea excepției" in m for m in stop)
    exceptie = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    PL.scrie_sectiune_raport(copie.raport, exceptie[3])
    assert copie.verifica(exceptie) == []


def test_pragul_hook_diferit_de_cel_aprobat(copie):
    p = os.path.join(copie.dir, "scripts", "praguri_%s.txt" % LOTF)
    open(p, "w").write(PRAGURI.replace("max hook 126", "max hook 140"))
    copie.recipisa_scrie()
    stop = copie.verifica()
    assert any("excepția e aprobată numai față de 126" in m for m in stop)


# ── AC197, candidatul oprit, întrerupt / infra / G2, poarta_verificator ─────────────────────────────────────────────────────────────────────
def test_ac197_sha_inlocuit_final_necunoscut_cu_exceptie(copie):
    copie.recipisa_scrie()
    copie.pereche("poarta_plasa", 5000, "verde", sha="0123456789ab", scrie=True)   # SHA cunoscut și înlocuit: nu judecă C
    exceptie = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    PL.scrie_sectiune_raport(copie.raport, exceptie[3])
    assert copie.verifica(exceptie) == []
    copie.pereche("poarta_plasa", 5000, "verde", sha="-", scrie=True)   # SHA nedeterminat: nu exclude
    assert "pragul „poarta_plasa” depășit: 5000s > 4063s" in copie.verifica()
    copie2_stop = PL.depasiri_praguri(PL.eligibile_sha_final([("poarta_plasa", "x", "", "", "verde", 5000, copie.c[:12])], copie.c), PRAGURI.splitlines(),
                                      exceptate={"hook": {ID_EXC}})[0]
    assert copie2_stop == ["pragul „poarta_plasa” depășit: 5000s > 4063s"]   # pe SHA-ul final


def test_candidatul_oprit_ramane_stop(copie):
    copie.recipisa_scrie()
    f = os.path.join(copie.comun, "lot_stare_%s.json" % LOTF)
    st = json.load(open(f))
    st["candidati_opriti"] = {copie.c: "poarta roșie"}
    json.dump(st, open(f, "w"))
    rc, out = copie.publica()
    assert rc == 1 and "candidatul %s a fost oprit" % copie.c[:12] in out


def test_poarta_verificator_peste_prag_pe_sha_eligibil_ramane_stop(copie):
    copie.pereche("poarta_verificator", 130, "verde", sha=copie.c[:12], scrie=True)
    copie.recipisa_scrie()
    rc, out = copie.publica()
    assert rc == 1 and "pragul „poarta_verificator” depășit: 130s > 114s" in out and "excepție aprobată" in out


def test_intrerupt_infra_g2_contabilizate_pe_seria_integrala(copie):
    copie.recipisa_scrie()
    copie.pereche("hook", 0, "x", fara_sfarsit=True, scrie=True)                      # început fără sfârșit, pid mort -> «intrerupt»
    copie.pereche("poarta_pytest", 900, "infra", scrie=True)                        # infra: nu se numără la prag
    gid = copie.pereche("poarta_pytest", 800, "verde", scrie=True)                  # prima măsurare peste prag, marcată G2, fără re-măsurare
    sf = next(r for r in JL.citeste_jurnal(copie.jurnal) if r[6] == gid and r[2] == "sfarsit")
    copie.rand(*(sf[:5] + ["infra_g2"] + sf[6:8] + ["incarcare; durata_prima=800"]))
    d7 = PL.durate_cu_sha(LOT)
    infra, g2 = {}, {}
    stop, intr = PL.depasiri_praguri(PL.eligibile_sha_final(d7, copie.c), PRAGURI.splitlines(), infra, g2, JL.marcaje_g2(LOT), {"hook": {ID_EXC}})
    assert intr.get("hook") == 1 and infra == {"poarta_pytest": 1} and g2 == {"poarta_pytest": 1}
    assert "faza poarta_pytest: marcată infra fără re-măsurare" in stop
    assert not [m for m in stop if "hook" in m]
    copie.pereche("poarta_pytest", 600, "verde", scrie=True)                        # re-măsurarea ≤ prag
    stop, _ = PL.depasiri_praguri(PL.eligibile_sha_final(PL.durate_cu_sha(LOT), copie.c), PRAGURI.splitlines(), {}, {}, JL.marcaje_g2(LOT), {"hook": {ID_EXC}})
    assert stop == []
    _, _, rez, _ = PL.decizie_exceptie(LOT, copie.c, PRAGURI.splitlines())
    assert rez["rulari"] == 5 and rez["max_dupa"] == 125   # întreruptul nu intră în serie, nu se numără ca depășire


def test_verifica_c_head_ramane_contractul_restrans(copie, monkeypatch):
    copie.recipisa_scrie()
    monkeypatch.chdir(copie.dir)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = PL.main_verifica(copie.c, copie.c, LOT)
    assert rc == 0 and "PASS C=%s" % copie.c in buf.getvalue()


# ── recipisa reală a lui 17.5-F6, pe jurnalul real (măsurările reale) ──────────────────────────────────────────────────────────────────────
def test_recipisa_reala_f6_pe_jurnalul_real(tmp_path):
    cale = os.path.join(os.path.expanduser("~"), "ghid_incoming", "exceptii_praguri_17_5_F6.txt")
    jurnal_real = os.path.join(os.path.expanduser("~"), "iconta_nou", ".lot_jurnal.log")
    if not (os.path.exists(cale) and os.path.exists(jurnal_real)):
        pytest.skip("recipisa sau jurnalul real lipsesc pe această mașină")
    assert hashlib.sha256(open(cale, "rb").read()).hexdigest() == PL.RECIPISE_APROBATE[LOT]["sha256"] == "3c6fbf70dad4e7a88878986cf392b69c1d65cc5a88aa42db938f0d43d8f7a538"
    jurnal = str(tmp_path / "jurnal.log")   # copie: durate_cu_sha marchează întreruptele (scrie), jurnalul real rămâne neatins
    open(jurnal, "w", encoding="utf-8").write(open(jurnal_real, encoding="utf-8").read())
    rows = JL.citeste_jurnal(jurnal)
    d7 = PL.durate_cu_sha(LOT, cale=jurnal)
    sha = "8d876246bd95255e4d936cec6ccc20c0f1b9761e"
    d, stop = PL.exceptie_hook(LOT, d7, rows=rows, cale=cale, rezolva=lambda p: sha if sha.startswith(p) else None)
    assert stop == [] and d["id"] == ID_EXC and d["secunde"] == 127 and d["sha"] == sha and d["sfarsit"] == "2026-11-28T05:41:18+02:00"
    hook = [x for x in d7 if x[0] == "hook" and x[4] == "verde"][:5]
    assert [x[5] for x in hook] == [106, 125, 105, 127, 100] and sum(x[5] for x in hook) == 563
    rez = PL.rezumat_exceptie(d, PL.eligibile_sha_final(d7, sha), ["max hook 126"])
    assert rez["max_inainte"] == 127 and rez["max_dupa"] == 125 and rez["numar"] == 1 and rez["alte_depasiri"] == []


# ── U2.2: generatorul pragurilor păstrează măsurarea 127 ───────────────────────────────────────────────────────────────────────────────────
def _rulari_lot(lot, durate, publicat=True, ora0=0):
    rows, t = [], ora0
    for i, sec in enumerate(durate):
        id_ = "%s-%d" % (lot, i)
        rows += [[lot, "hook", "inceput", _ora(t), "a" * 12, "-", id_, "1", ""], [lot, "hook", "sfarsit", _ora(t + sec), "a" * 12, "verde", id_, "1", ""]]
        t += sec + 10
    if publicat:
        rows.append([lot, "publicare", "sfarsit", _ora(t + 5), "a" * 12, "publicat", lot + "-p", "1", ""])
    return rows, t + 10


def test_generatorul_include_127_si_esantion_cu_maxim_mai_mare():
    rows, t = [], 0
    for lot, d in (("17.5-C9", [90, 99]), ("17.5-U2", [80])):
        r, t = _rulari_lot(lot, d, ora0=t)
        rows += r
    r, t = _rulari_lot(LOT, [106, 125, 105, 127, 100], publicat=False, ora0=t)
    rows += r
    assert LOT not in PA.selecteaza(rows)   # F6 oprit: nu intră încă în fereastra implicită
    rows.append([LOT, "publicare", "sfarsit", _ora(t + 5), "a" * 12, "publicat", "F6-p", "1", ""])
    sel = PA.selecteaza(rows)
    assert sel.count(LOT) == 1 and sel[-1] == LOT
    calc = PA.calculeaza(rows, sel, ["hook"])["hook"]
    assert calc["maxim"] == 127 and calc["lot"] == LOT and PA.prag(calc["maxim"]) == 153
    assert calc["complete"] == 2 + 1 + 5
    r2, _ = _rulari_lot("17.5-F7", [140], ora0=t + 100)
    calc2 = PA.calculeaza(rows + r2, PA.selecteaza(rows + r2), ["hook"])["hook"]
    assert calc2["maxim"] == 140 and PA.prag(140) == 168   # valoarea efectivă = maximul întregii ferestre
    assert PA.calculeaza(rows, [LOT], ["hook"])["hook"]["maxim"] == 127 and PA.prag(127) == 153   # proiecția pe seria F6
