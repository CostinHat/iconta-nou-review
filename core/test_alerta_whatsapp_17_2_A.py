# -*- coding: utf-8 -*-
"""Lotul 17.2-A (unelte) — alertele lanțului de loturi către Costin (C227) și pașii contului WhatsApp (C228): textul alertei, lanțul șablon–text–email,
linia de comandă, legarea în incheie_lot.sh și în pornire-coada, scripts/whatsapp_meta.py (garda de 72 de ore, PIN din mediu, webhook, șabloane).
Fără Chromium, fără 8019, fără baza de test, fără rețea: orice apel către Meta sau email e înlocuit; toate căile de scriere merg în directorul temporar.
Rădăcina verificată vine din ALERTA_RAD_17_2_A (implicit depozitul acesta); pe o rădăcină fără scripts/alerta_whatsapp.py toate cazurile cad."""
import datetime
import importlib.util
import json
import os
import stat
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAD_ALERTA = os.environ.get("ALERTA_RAD_17_2_A") or RAD
ACUM = datetime.datetime(2026, 11, 7, 10, 48)
SECRETE_FALSE = [("WHATSAPP_TOKEN", "TOKEN_FALS_17_2_A"), ("WHATSAPP_PIN", "123456"), ("WHATSAPP_VERIFY_TOKEN", "VERIF_FALS_17_2_A"),
                 ("WHATSAPP_APP_SECRET", "SECRET_FALS_17_2_A"), ("ALERTA_WA_CATRE", "+40700000123")]
DEST = "+40700000123"


def _incarca(cale, nume):
    """Încarcă un script din rădăcina verificată, cu nume unic și cu scripts/ al ei primul în sys.path."""
    scripts = os.path.join(RAD_ALERTA, "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location("%s_%s" % (nume, abs(hash(RAD_ALERTA))), os.path.join(scripts, cale))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        sys.path.remove(scripts)


class Falsuri:
    """Înlocuiește apelurile spre Meta și spre email; `program` = ce face fiecare cerere, în ordine: None = reușește, un șir = `wa.Refuzat` cu mesajul lui."""

    def __init__(self, wa):
        self.wa = wa
        self.cereri = []
        self.emailuri = []
        self.program = []
        self.email_rezultat = True

    def cere(self, cale, corp):
        self.cereri.append((cale, corp))
        pas = self.program.pop(0) if self.program else None
        if isinstance(pas, str):
            raise self.wa.Refuzat(pas)
        if isinstance(pas, Exception):
            raise pas
        return {"messages": [{"id": "wamid.ID%d" % len(self.cereri)}], "contacts": [{"wa_id": "999"}]}

    def email(self, catre, subiect, html, *a, **k):
        self.emailuri.append((catre, subiect, html))
        if isinstance(self.email_rezultat, Exception):
            raise self.email_rezultat
        return self.email_rezultat


@pytest.fixture
def amb(monkeypatch, tmp_path):
    """Mediu izolat: HOME și toate căile de scriere în directorul temporar, secrete false, rețeaua interzisă."""
    monkeypatch.setenv("HOME", str(tmp_path))
    for nume, cale in (("ALERTA_WA_LOG", "alerte.log"), ("WA_INCERCARI_LOG", "incercari.log"), ("WA_WEBHOOK_FISIER", "webhook.txt"),
                       ("ALERTA_WA_ENV", "mediu.env"), ("WA_SABLOANE_TRIMISE", "sabloane_trimise.txt")):
        monkeypatch.setenv(nume, str(tmp_path / cale))
    monkeypatch.setenv("OPRIT_DIR", str(tmp_path))
    monkeypatch.delenv("ICONTA_WHATSAPP_SIMULAT", raising=False)
    monkeypatch.delenv("ALERTA_CMD", raising=False)
    for nume, valoare in SECRETE_FALSE:
        monkeypatch.setenv(nume, valoare)
    monkeypatch.setenv("ICONTA_ALERTA_EMAIL", "alerta@exemplu.test")

    def fara_retea(*a, **k):
        raise AssertionError("cerere de rețea în test")
    monkeypatch.setattr(urllib.request, "urlopen", fara_retea)
    A = _incarca("alerta_whatsapp.py", "alerta")
    monkeypatch.setitem(sys.modules, "alerta_whatsapp", A)
    A.fals = Falsuri(A.wa)
    monkeypatch.setattr(A.wa, "_cere", A.fals.cere)
    monkeypatch.setattr(A.observare, "trimite_email_html", A.fals.email)
    A.tmp = tmp_path
    return A


def _rand_jurnal(A):
    cale = A.tmp / "alerte.log"
    return [l.split("\t") for l in cale.read_text(encoding="utf-8").splitlines()] if cale.exists() else []


def _canale(A):
    return [r[3] for r in _rand_jurnal(A)]


# ── (1)(2)(3) textul și numele lotului ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_compune_textul_fiecarei_stari(amb):
    A = amb
    ora = datetime.datetime(2026, 11, 7, 11, 40)
    assert A.compune("17.2", "PORNIT", "", "", datetime.datetime(2026, 11, 7, 10, 48)) == ("17.2", "PORNIT 10:48")
    assert A.compune("17.2", "publicat", "0123456789abcdef0123456789abcdef01234567", "", ora) == ("17.2", "publicat 01234567 11:40")
    assert A.compune("17.2", "publicat", "-", "", ora) == ("17.2", "publicat 11:40")
    assert A.compune("17.2", "nepublicat", "-", "poarta roșie", ora) == ("17.2", "OPRIT 11:40: poarta roșie")
    assert A.compune("17.2", "nepublicat", "-", "", ora) == ("17.2", "OPRIT 11:40: motiv nescris, vezi raportul lotului")


def test_compune_curata_spatiile_si_lungimea(amb):
    A = amb
    assert A.curata("a\nb\tc     d") == "a b c d"
    lung = A.curata("x" * 300)
    assert len(lung) == 160 and lung.endswith("…")
    v2 = A.compune("17.2", "nepublicat", "-", "y" * 300, ACUM)[1]
    assert len(v2) == 160 and v2.endswith("…") and "\n" not in v2


def test_compune_numele_lotului_acceptate_si_ignorate(amb):
    A = amb
    for lot in ("17.2", "17.2-A", "16.8-C1"):
        A.fals.cereri.clear()
        A.alerta(lot, "PORNIT", acum=ACUM)
        assert len(A.fals.cereri) == 1, lot
    A.fals.cereri.clear()
    for lot in ("PROBA-C3", "99.9x", "17.2-a", "../x"):
        A.alerta(lot, "PORNIT", acum=ACUM)
    assert A.fals.cereri == [] and A.fals.emailuri == []
    assert sum(1 for r in _rand_jurnal(A) if "lot ignorat" in r[-1]) == 4


# ── (4)–(9) lanțul ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lant_sablon_reusit(amb):
    A = amb
    A.alerta("17.2", "PORNIT", acum=ACUM)
    assert len(A.fals.cereri) == 1 and A.fals.emailuri == []
    corp = A.fals.cereri[0][1]
    assert corp["type"] == "template" and corp["to"] == DEST
    assert corp["template"]["name"] == "iconta_alerta_lot" and corp["template"]["language"]["code"] == "ro"
    assert corp["template"]["components"][0]["parameters"] == [{"type": "text", "text": "17.2"}, {"type": "text", "text": "PORNIT 10:48"}]
    assert _canale(A) == ["sablon"]
    assert "wamid.ID1" in _rand_jurnal(A)[0][4] and "contacts" not in _rand_jurnal(A)[0][4] and "999" not in _rand_jurnal(A)[0][4]


def test_lant_sablon_refuzat_text_reusit(amb):
    A = amb
    A.fals.program = ["Meta a refuzat cererea (HTTP 400, cod 132001): Template name does not exist", None]
    A.alerta("17.2", "PORNIT", acum=ACUM)
    assert [c[1]["type"] for c in A.fals.cereri] == ["template", "text"]
    assert A.fals.cereri[1][1]["text"]["body"] == "Lotul 17.2: PORNIT 10:48"
    assert A.fals.emailuri == []
    rand = _rand_jurnal(A)
    assert [r[3] for r in rand] == ["sablon", "text"] and "132001" in rand[0][4] and "wamid" in rand[1][4]


def test_lant_totul_refuzat_ajunge_la_email(amb):
    A = amb
    A.fals.program = ["Meta a refuzat cererea (HTTP 400, cod 132001): a", "Meta a refuzat cererea (HTTP 400, cod 131047): b"]
    A.alerta("17.2", "PORNIT", acum=ACUM)
    assert len(A.fals.emailuri) == 1 and A.fals.emailuri[0][1] == "[iConta.eu] Lotul 17.2: PORNIT 10:48"
    assert A.fals.emailuri[0][0] == "alerta@exemplu.test"
    assert _canale(A) == ["sablon", "text", "email"]


def test_lant_nepublicat_trimite_si_email_dupa_whatsapp(amb):
    A = amb
    A.alerta("17.2", "nepublicat", "-", "poarta roșie", acum=ACUM)
    assert len(A.fals.cereri) == 1 and len(A.fals.emailuri) == 1
    assert A.fals.emailuri[0][1] == "[iConta.eu] Lotul 17.2: OPRIT 10:48: poarta roșie"
    assert _canale(A) == ["sablon", "email"]


def test_lant_publicat_reusit_nu_trimite_email(amb):
    A = amb
    A.alerta("17.2", "publicat", "abcdef0123456789", acum=ACUM)
    assert len(A.fals.cereri) == 1 and A.fals.emailuri == []


@pytest.mark.parametrize("valoare,motiv", [("", "destinatar lipsă"), ("abc", "destinatar invalid")])
def test_lant_destinatar_lipsa_sau_invalid(amb, monkeypatch, valoare, motiv):
    A = amb
    monkeypatch.setenv("ALERTA_WA_CATRE", valoare)
    A.alerta("17.2", "PORNIT", acum=ACUM)
    assert A.fals.cereri == [] and len(A.fals.emailuri) == 1
    rand = _rand_jurnal(A)
    assert any(motiv in r[4] for r in rand) and _canale(A)[-1] == "email"
    if valoare:
        assert all(valoare != r[4] for r in rand)


@pytest.mark.parametrize("rezultat", [False, RuntimeError("smtp căzut")])
def test_lant_email_cazut_nu_ridica(amb, rezultat):
    A = amb
    A.fals.program = ["Meta a refuzat cererea (HTTP 400, cod 1): a", "Meta a refuzat cererea (HTTP 400, cod 2): b"]
    A.fals.email_rezultat = rezultat
    A.alerta("17.2", "PORNIT", acum=ACUM)
    ultimul = _rand_jurnal(A)[-1]
    assert ultimul[3] == "email" and "netrimis" in ultimul[4]


# ── (10) secretele ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lant_secretele_nu_apar_nicaieri(amb, capsys):
    A = amb
    M = _incarca("whatsapp_meta.py", "meta")
    A.fals.program = ["Meta a refuzat cererea (HTTP 400, cod 132001): destinatar %s token TOKEN_FALS_17_2_A" % DEST, "Meta a refuzat cererea (HTTP 400, cod 2): b"]
    A.alerta("17.2", "PORNIT", acum=ACUM)
    M.wa.inregistreaza_numarul = lambda pin: {"success": True}
    assert M.cli(["inregistreaza"]) == 0
    assert M.cli(["sabloane", "--trimite"]) == 0
    M._get = lambda url: (200, urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["hub.challenge"][0])
    assert M.cli(["webhook"]) == 0
    iesire = capsys.readouterr()
    text = iesire.out + iesire.err + "".join((A.tmp / n).read_text(encoding="utf-8") for n in ("alerte.log", "incercari.log"))
    for nume, valoare in SECRETE_FALSE:
        if nume != "WHATSAPP_PIN":
            assert valoare not in text, nume
    assert "123456" not in iesire.out + iesire.err
    fisier = A.tmp / "webhook.txt"
    assert "VERIF_FALS_17_2_A" in fisier.read_text(encoding="utf-8")
    assert stat.S_IMODE(os.stat(fisier).st_mode) == 0o600


# ── (11) linia de comandă sub pytest ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def _cli(amb, *argv):
    mediu = {k: v for k, v in os.environ.items() if k != "ICONTA_WHATSAPP_SIMULAT"}
    mediu["PYTEST_CURRENT_TEST"] = "test_cli"
    (amb.tmp / "mediu.env").write_text("WHATSAPP_TOKEN=TOKEN_FALS_17_2_A\nALERTA_WA_CATRE=%s\n" % DEST, encoding="utf-8")
    return subprocess.run([sys.executable, os.path.join(RAD_ALERTA, "scripts", "alerta_whatsapp.py"), *argv], env=mediu, capture_output=True, text=True, timeout=60)


def test_cli_sub_pytest_nu_trimite_pe_real(amb):
    r = _cli(amb, "lot", "17.2", "PORNIT")
    assert r.returncode == 0 and "REFUZ: sub pytest" in r.stdout
    assert not (amb.tmp / "alerte.log").exists()


def test_cli_stare_necunoscuta_sau_subcomanda_gresita_iese_cu_2(amb):
    assert _cli(amb, "lot", "17.2", "oprit").returncode == 2
    assert _cli(amb, "lot", "17.2").returncode == 2
    assert _cli(amb, "altceva").returncode == 2


# ── (12) fara-secrete ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_cli_fara_secrete_gaseste_valoarea_si_nu_o_tipareste(amb, capsys):
    A = amb
    f = A.tmp / "dovada.txt"
    f.write_text("rezultat: TOKEN_FALS_17_2_A aici\n", encoding="utf-8")
    assert A.fara_secrete([str(f)]) == 1
    iesire = capsys.readouterr().out
    assert "WHATSAPP_TOKEN" in iesire and str(f) in iesire and "TOKEN_FALS_17_2_A" not in iesire
    f.write_text("numărul 0700000123 și forma +40700000123\n", encoding="utf-8")
    assert A.fara_secrete([str(f)]) == 1 and "ALERTA_WA_CATRE" in capsys.readouterr().out


def test_cli_fara_secrete_director_curat_si_valori_goale(amb, monkeypatch, capsys):
    A = amb
    d = A.tmp / "dovezi"
    d.mkdir()
    (d / "a.txt").write_text("nimic aici\n", encoding="utf-8")
    (d / "b.txt").write_text("nici aici\n", encoding="utf-8")
    (d / "c.png").write_bytes(b"\x89PNG\0\0TOKEN_FALS_17_2_A")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "")
    assert A.fara_secrete([str(d)]) == 0
    assert "VERDE: 2 fișiere" in capsys.readouterr().out


def test_cli_fara_secrete_pin_izolat_nu_si_in_numar_mai_lung(amb, capsys):
    A = amb
    f = A.tmp / "x.txt"
    f.write_text("suma 1234567 lei, cod 9123456a\n", encoding="utf-8")
    assert A.fara_secrete([str(f)]) == 0
    f.write_text("PIN-ul este 123456.\n", encoding="utf-8")
    assert A.fara_secrete([str(f)]) == 1 and "WHATSAPP_PIN" in capsys.readouterr().out


# ── (13) incheie_lot.sh ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _incheie(amb, *argv, alerta=None, timeout_s=None):
    mediu = dict(os.environ)
    mediu["OPRIT_DIR"] = str(amb.tmp)
    mediu.pop("ALERTA_CMD", None)
    if alerta:
        mediu["ALERTA_CMD"] = alerta
    if timeout_s:
        mediu["ALERTA_TIMEOUT_S"] = str(timeout_s)
    return subprocess.run(["sh", os.path.join(RAD_ALERTA, "scripts", "incheie_lot.sh"), *argv], env=mediu, capture_output=True, text=True, timeout=60)


def _sonda(tmp, corp):
    s = tmp / "sonda.sh"
    s.write_text(corp, encoding="utf-8")
    return "sh %s" % s


ARGUMENTE = 'for a in "$@"; do printf "[%s]" "$a"; done > "$(dirname "$0")/argumente.txt"\n'


def test_incheie_fara_alerta_cand_oprit_dir_e_setat_fara_alerta_cmd(amb):
    r = _incheie(amb, "17.2-A", "publicat", "abc123")
    assert r.returncode == 0 and "[alerta]" not in r.stdout and not (amb.tmp / "alerte.log").exists()
    assert (amb.tmp / "OPRIT_17.2-A.txt").read_text(encoding="utf-8").startswith("OPRIT — gata: 17.2-A publicat abc123 ")


def test_incheie_cheama_alerta_cu_argumentele_fixe(amb):
    cmd = _sonda(amb.tmp, ARGUMENTE)
    assert _incheie(amb, "17.2-A", "publicat", "abc123", alerta=cmd).returncode == 0
    assert (amb.tmp / "argumente.txt").read_text(encoding="utf-8") == "[lot][17.2-A][publicat][abc123][]"
    assert _incheie(amb, "17.2-A", "nepublicat", "-", "motiv de test", alerta=cmd).returncode == 0
    assert (amb.tmp / "argumente.txt").read_text(encoding="utf-8") == "[lot][17.2-A][nepublicat][-][motiv de test]"


def test_incheie_alerta_cazuta_sau_lenta_nu_schimba_ieșirea(amb):
    r = _incheie(amb, "17.2-A", "publicat", "abc", alerta=_sonda(amb.tmp, "exit 7\n"))
    assert r.returncode == 0 and (amb.tmp / "OPRIT_17.2-A.txt").exists()
    (amb.tmp / "OPRIT_17.2-A.txt").unlink()
    t0 = time.time()
    r = _incheie(amb, "17.2-A", "publicat", "abc", alerta=_sonda(amb.tmp, "sleep 30\n"), timeout_s=1)
    assert r.returncode == 0 and time.time() - t0 < 10 and (amb.tmp / "OPRIT_17.2-A.txt").exists()


def test_incheie_lot_de_proba_nu_cheama_alerta(amb):
    r = _incheie(amb, "PROBA-C3", "publicat", "abc", alerta=_sonda(amb.tmp, ARGUMENTE))
    assert r.returncode == 0 and not (amb.tmp / "argumente.txt").exists()


def test_incheie_sintaxa_sh_curata():
    cale = os.path.join(RAD_ALERTA, "scripts", "incheie_lot.sh")
    assert subprocess.run(["sh", "-n", cale], capture_output=True).returncode == 0
    assert "alerta_whatsapp.py" in open(cale, encoding="utf-8").read()


# ── (14) pornire-coada ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _pornire(amb, monkeypatch, coada_reala, subprocess_run=None):
    JL = _incarca("jurnal_lot.py", "jl")
    tmp = amb.tmp
    depozit = tmp / ("dep%s" % ("1" if coada_reala else "0"))
    subprocess.run(["git", "init", "-q", "-b", "main", str(depozit)], check=True)
    jurnal, cheie, praguri = tmp / ("j%d.log" % coada_reala), tmp / "cheie.txt", tmp / "praguri.txt"
    cheie.write_text("cheie-de-proba\n", encoding="utf-8")
    praguri.write_text("unelte\n", encoding="utf-8")
    monkeypatch.chdir(depozit)
    monkeypatch.setenv("LOT_JURNAL", str(jurnal))
    if coada_reala:
        monkeypatch.setattr(JL, "_coada_reala", lambda p: True)
        real = subprocess.run

        def run(cmd, *a, **k):
            if any("alerta_whatsapp.py" in str(c) for c in cmd):
                return subprocess_run(cmd, *a, **k)
            return real(cmd, *a, **k)
        monkeypatch.setattr(JL.subprocess, "run", run)
    rez = JL.pornire_coada("99.9", str(praguri), str(cheie), "comanda_x.txt")
    rows = [(r[0], r[1], r[2], r[4], r[5]) for r in JL._citeste(str(jurnal))]
    return rez, rows


def test_coada_reala_doar_pentru_ghid_incoming(amb):
    JL = _incarca("jurnal_lot.py", "jl")
    assert JL._coada_reala(str(amb.tmp / "praguri_x.txt")) is False
    assert JL._coada_reala(os.path.join(os.path.expanduser("~"), "ghid_incoming", "praguri_x.txt")) is True


def test_coada_fara_coada_reala_nu_cheama_alerta(amb, monkeypatch, capsys):
    rez, rows = _pornire(amb, monkeypatch, 0)
    assert rez == 0 and len(rows) == 2


@pytest.mark.parametrize("exceptie", [subprocess.TimeoutExpired("x", 90), OSError("fără interpretor")])
def test_coada_alerta_cazuta_nu_schimba_rezultatul_nici_jurnalul(amb, monkeypatch, capsys, exceptie):
    rez0, rows0 = _pornire(amb, monkeypatch, 0)

    def cade(*a, **k):
        raise exceptie
    rez1, rows1 = _pornire(amb, monkeypatch, 1, cade)
    assert (rez1, rows1) == (rez0, rows0)
    assert "[jurnal_lot] alerta nu a plecat: %s" % type(exceptie).__name__ in capsys.readouterr().out


# ── (15) inregistreaza, aboneaza, garda de 72 de ore ─────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def meta(amb, monkeypatch):
    M = _incarca("whatsapp_meta.py", "meta")
    M.apeluri = []
    monkeypatch.setattr(M.wa, "inregistreaza_numarul", lambda pin: M.apeluri.append(("inregistreaza", pin)) or {"success": True})
    monkeypatch.setattr(M.wa, "aboneaza_aplicatia", lambda: M.apeluri.append(("aboneaza", None)) or {"success": True})
    M.amb = amb
    return M


def test_meta_inregistreaza_ia_pinul_din_mediu(meta):
    assert meta.cli(["inregistreaza"]) == 0
    assert meta.apeluri == [("inregistreaza", "123456")]


def test_meta_inregistreaza_cu_argument_se_refuza(meta, capsys):
    assert meta.cli(["inregistreaza", "123456"]) == 1
    assert meta.apeluri == [] and "REFUZ" in capsys.readouterr().out


@pytest.mark.parametrize("pin", [None, "12345"])
def test_meta_inregistreaza_pin_lipsa_sau_scurt(meta, monkeypatch, capsys, pin):
    if pin is None:
        monkeypatch.delenv("WHATSAPP_PIN")
    else:
        monkeypatch.setenv("WHATSAPP_PIN", pin)
    assert meta.cli(["inregistreaza"]) == 1
    iesire = capsys.readouterr().out
    assert meta.apeluri == [] and "REFUZ" in iesire and (pin is None or pin not in iesire)


def test_meta_garda_de_72_de_ore_pe_fiecare_actiune(meta, capsys):
    assert meta.cli(["inregistreaza"]) == 0
    prima = (meta.amb.tmp / "incercari.log").read_text(encoding="utf-8").split("\t")[0]
    capsys.readouterr()
    assert meta.cli(["inregistreaza"]) == 1
    assert prima in capsys.readouterr().out and len(meta.apeluri) == 1
    assert meta.cli(["aboneaza"]) == 0 and meta.cli(["aboneaza"]) == 1
    assert [a[0] for a in meta.apeluri] == ["inregistreaza", "aboneaza"]


def test_meta_garda_independenta_de_sabloane(meta, monkeypatch):
    trimise = []
    monkeypatch.setattr(meta.wa, "trimite_sablon_spre_aprobare", lambda s: trimise.append(s["name"]) or {"id": "1"})
    assert meta.cli(["inregistreaza"]) == 0
    assert meta.cli(["sabloane", "--trimite"]) == 0
    assert meta.cli(["sabloane", "--trimite"]) == 1 and len(trimise) == 3


def test_meta_incercarea_de_acum_73_de_ore_nu_blocheaza(meta):
    veche = (datetime.datetime.now().astimezone() - datetime.timedelta(hours=73)).isoformat(timespec="seconds")
    (meta.amb.tmp / "incercari.log").write_text("%s\tinregistreaza\tok\t{}\n" % veche, encoding="utf-8")
    assert meta.cli(["inregistreaza"]) == 0 and len(meta.apeluri) == 1


def test_meta_neconfigurat_nu_scrie_rand(meta, monkeypatch):
    def cade(pin):
        raise meta.wa.Neconfigurat("fără token")
    monkeypatch.setattr(meta.wa, "inregistreaza_numarul", cade)
    assert meta.cli(["inregistreaza"]) == 1
    assert not (meta.amb.tmp / "incercari.log").exists()


def test_meta_refuz_de_la_meta_scrie_rand_si_blocheaza_reincercarea(meta, monkeypatch):
    def refuza(pin):
        raise meta.wa.Refuzat("Meta a refuzat cererea (HTTP 400, cod 100): x")
    monkeypatch.setattr(meta.wa, "inregistreaza_numarul", refuza)
    assert meta.cli(["inregistreaza"]) == 1
    assert "\trefuz\t" in (meta.amb.tmp / "incercari.log").read_text(encoding="utf-8")
    assert meta.cli(["inregistreaza"]) == 1


# ── (16) șabloanele ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_meta_sablonul_alertei_si_ordinea_celor_trei(amb, monkeypatch):
    A = amb
    assert len(A.SABLOANE_ALERTA) == 1
    s = A.SABLOANE_ALERTA[0]
    assert (s["name"], s["language"], s["category"]) == ("iconta_alerta_lot", "ro", "UTILITY")
    assert len(s["components"]) == 1 and s["components"][0]["type"] == "BODY"
    assert "{{1}}" in s["components"][0]["text"] and "{{2}}" in s["components"][0]["text"]
    assert len(s["components"][0]["example"]["body_text"][0]) == 2
    M = _incarca("whatsapp_meta.py", "meta")
    assert M.cli(["sabloane"]) == 0 and A.fals.cereri == []
    assert M.cli(["sabloane", "--trimite"]) == 0
    assert [c[1]["name"] for c in A.fals.cereri] == ["iconta_alerta_lot", "iconta_cod_confirmare", "iconta_notificare"]
    assert all(c[0].endswith("/message_templates") for c in A.fals.cereri)


# ── (17) webhook ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_meta_webhook_verifica_local_si_public(meta, capsys):
    cereri = []

    def get(url):
        cereri.append(url)
        return 200, urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["hub.challenge"][0]
    meta._get = get
    assert meta.cli(["webhook"]) == 0
    iesire = capsys.readouterr().out
    assert "verificare locală: ok" in iesire and "verificare publică: ok" in iesire and "VERIF_FALS_17_2_A" not in iesire
    assert cereri[0].startswith("http://127.0.0.1:8010/whatsapp/webhook?") and cereri[1].startswith("https://iconta.eu/whatsapp/webhook?")
    assert "hub.mode=subscribe" in cereri[0]
    linii = (meta.amb.tmp / "webhook.txt").read_text(encoding="utf-8").splitlines()
    assert linii == ["https://iconta.eu/whatsapp/webhook", "VERIF_FALS_17_2_A"]


def test_meta_webhook_refuzat_si_token_lipsa(meta, monkeypatch, capsys):
    meta._get = lambda url: (403, "")
    assert meta.cli(["webhook"]) == 0
    iesire = capsys.readouterr().out
    assert "verificare locală: refuz 403" in iesire and "verificare publică: refuz 403" in iesire
    (meta.amb.tmp / "webhook.txt").unlink()
    monkeypatch.delenv("WHATSAPP_VERIFY_TOKEN")
    assert meta.cli(["webhook"]) == 1
    assert "REFUZ" in capsys.readouterr().out and not (meta.amb.tmp / "webhook.txt").exists()


# ── (18) trimiterea șabloanelor ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_meta_un_refuz_nu_opreste_celelalte_sabloane(meta, monkeypatch, capsys):
    trimise = []

    def trimite(s):
        trimise.append(s["name"])
        if s["name"] == "iconta_cod_confirmare":
            raise meta.wa.Refuzat("Meta a refuzat cererea (HTTP 400, cod 100/2388024): x")
        return {"id": "1"}
    monkeypatch.setattr(meta.wa, "trimite_sablon_spre_aprobare", trimite)
    assert meta.cli(["sabloane", "--trimite"]) == 0
    assert trimise == ["iconta_alerta_lot", "iconta_cod_confirmare", "iconta_notificare"]
    linii = (meta.amb.tmp / "sabloane_trimise.txt").read_text(encoding="utf-8").splitlines()
    assert linii == ["iconta_alerta_lot ok", "iconta_cod_confirmare refuz HTTP 400 cod 100/2388024", "iconta_notificare ok"]
    assert capsys.readouterr().out.splitlines()[-3:] == linii
