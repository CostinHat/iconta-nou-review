# -*- coding: utf-8 -*-
"""core/test_verificator_design_17_5_Z.py — garda PERMANENTĂ a opririi sigure a serverului de lucru (lotul 17.5-Z, unelte).

Numai mock-uri și spy-uri: nicio procesare reală, niciun socket, nici 8019, nici baza de date, nici /tmp comun; fiecare test lucrează în `tmp_path`.
Sistemul (`ss`, /proc, pidfd, Popen, e2e_poarta) e simulat de `Sis`; orice `os.kill` / `os.killpg` pe număr de PID pică testul (semnalele merg numai prin pidfd).
Fiecare scenariu ambiguu verifică: cod nenul / refuz, ZERO semnale, ZERO ștergeri."""
import fcntl
import json
import os
import signal
import subprocess
import sys
import types

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PID = 41001


def antet(*randuri):
    return "State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess\n" + "".join(r + "\n" for r in randuri)


def rand(pid=PID, port=8019):
    proc = ' users:(("python",pid=%d,fd=3))' % pid if pid else ""
    return "LISTEN 0      2048       127.0.0.1:%d      0.0.0.0:*%s" % (port, proc)


class Sis:
    """Sistemul simulat: procese (identități din /proc), starea lui `ss`, pidfd-urile și semnalele trimise."""

    def __init__(self, vd, tmp_path):
        self.vd, self.tmp = vd, tmp_path
        self.unelte = str(tmp_path / "unelte")
        self.prod = str(tmp_path / "prod")
        os.makedirs(self.unelte + "/arb", exist_ok=True)
        self.procs = {}
        self.pid_exit = set()
        self.ss = "auto"            # "auto" = derivat din procese; altfel (rc, out, err) sau o listă de astfel de valori consumate pe rând
        self.semnale = []           # (pid, SIGNAL)
        self.opriri_la = {}         # pid -> semnalul care îl oprește (None = nu se oprește niciodată)
        self.dupa_deschidere = {}   # pid -> identitate returnată la citirile de după pidfd_open
        self.pidfd_eroare = None
        self.citiri = {}
        self.port_tinut_dupa_oprire = False
        self.adauga(PID)

    def adauga(self, pid, **kw):
        i = {"pid": pid, "start": "777", "pgid": pid, "sid": pid, "cwd": self.unelte + "/arb",
             "cmd": "/x/venv/bin/python -m uvicorn main:app --port 8019", "boot_id": "boot-1"}
        i.update(kw)
        self.procs[pid] = i
        self.opriri_la.setdefault(pid, signal.SIGTERM)
        return i

    # -- ce vede codul
    def rul_ss(self, port, cu_procese):
        if self.ss != "auto":
            if isinstance(self.ss, list):
                return self.ss.pop(0) if len(self.ss) > 1 else self.ss[0]
            return self.ss
        vii = sorted(p for p in self.procs if p not in self.pid_exit and self.procs[p].get("tine_portul", True))
        if not vii and not self.port_tinut_dupa_oprire:
            return 0, antet(), ""
        return 0, antet(*[rand(p, port) for p in (vii or [PID])]), ""

    def identitate(self, pid):
        self.citiri[pid] = self.citiri.get(pid, 0) + 1
        if pid in self.pid_exit or pid not in self.procs:
            return None
        if self.citiri[pid] > 2 and pid in self.dupa_deschidere:
            return dict(self.procs[pid], **self.dupa_deschidere[pid])
        return dict(self.procs[pid])

    def pidfd_open(self, pid):
        if self.pidfd_eroare:
            raise self.pidfd_eroare
        if pid in self.pid_exit or pid not in self.procs:
            raise ProcessLookupError(pid)
        self.dupa_deschidere_activ = True
        for p in self.dupa_deschidere:
            self.citiri[p] = 2
        return 1000 + pid

    def trimite(self, fd, sem, info=None, flags=0):
        pid = fd - 1000
        self.semnale.append((pid, sem))
        if getattr(self, "esec_semnal", None) == sem:
            raise PermissionError(1, "Operation not permitted")
        if self.opriri_la.get(pid) == sem or (sem == signal.SIGKILL and self.opriri_la.get(pid) is not None):
            self.pid_exit.add(pid)

    def a_iesit(self, fd, secunde):
        return (fd - 1000) in self.pid_exit

    def kill_interzis(self, *a, **k):
        raise AssertionError("os.kill / os.killpg pe un număr de PID e interzis: %r" % (a,))


@pytest.fixture
def S(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(os.path.join(RAD, "scripts"))
    import verificator_design as vd
    s = Sis(vd, tmp_path)
    monkeypatch.setattr(vd, "TEMP", str(tmp_path / "vd_temp"))
    monkeypatch.setattr(vd, "STARE", str(tmp_path / "vd_temp" / "stare.json"))
    monkeypatch.setattr(vd, "STARE_COPIE", str(tmp_path / "copie"))
    monkeypatch.setattr(vd, "LACAT_VD", str(tmp_path / "lacat"))
    monkeypatch.setattr(vd, "LACAT_ASTEAPTA", 0)
    monkeypatch.setattr(vd.time, "sleep", lambda *_a: None)
    monkeypatch.setattr(vd, "_rul_ss", s.rul_ss)
    monkeypatch.setattr(vd, "identitate", s.identitate)
    monkeypatch.setattr(vd, "_pornit", lambda pid: "2026-01-01T00:00:00")
    monkeypatch.setattr(vd, "_asteapta_iesire", s.a_iesit)
    monkeypatch.setattr(vd, "_inchide_fd", lambda fd: None)
    monkeypatch.setattr(vd, "_jurnal", lambda lot, detalii, rezultat: s.__dict__.setdefault("jurnal", []).append((detalii, rezultat)))
    monkeypatch.setattr(vd, "radacini_unelte", lambda: [s.unelte, vd.TEMP])
    monkeypatch.setattr(vd, "radacini_productie", lambda: [s.prod])
    monkeypatch.setattr(os, "pidfd_open", s.pidfd_open)
    monkeypatch.setattr(signal, "pidfd_send_signal", s.trimite)
    monkeypatch.setattr(os, "kill", s.kill_interzis)
    monkeypatch.setattr(os, "killpg", s.kill_interzis)
    return s


def _temp(S, cu_marcaj=True, stare=None):
    os.makedirs(S.vd.TEMP, mode=0o700, exist_ok=True)
    os.chmod(S.vd.TEMP, 0o700)
    (open(os.path.join(S.vd.TEMP, "dovada.txt"), "w")).write("x")
    if cu_marcaj:
        open(os.path.join(S.vd.TEMP, S.vd.MARCAJ_TEMP), "w").write("1\n")
    if stare is not None:
        open(os.path.join(S.vd.TEMP, "stare.json"), "w").write(stare if isinstance(stare, str) else json.dumps(stare))


def _stare_buna(S, **kw):
    i = S.procs[PID]
    d = {"pid": PID, "start": i["start"], "pgid": i["pgid"], "sid": i["sid"], "cwd": i["cwd"], "cmd": i["cmd"], "boot_id": i["boot_id"], "sha": "abc"}
    d.update(kw)
    return d


def _fara_semnale(S):
    assert S.semnale == []


# ── sonda portului: fail-closed (§2.2) ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_ss_reusit_fara_rand_e_liber_si_cu_rand_e_ocupat(S):
    S.ss = (0, antet(), "")
    assert S.vd.stare_port(8019)[0] == "liber" and not S.vd.port_ocupat(8019)
    S.ss = (0, antet(rand()), "")
    assert S.vd.stare_port(8019, cu_procese=True) == ("ocupat", [PID], "") and S.vd.port_ocupat(8019)


@pytest.mark.parametrize("ss", [
    (1, "", "ss: eroare"),                                    # cod nenul
    (1, antet(), ""),                                         # cod nenul, ieșire aparent liberă și fără stderr: numai codul îl trădează
    (None, "", "FileNotFoundError: ss"),                      # nu rulează
    (0, "", ""),                                              # ieșire goală (fără antet)
    (0, "State Recv-Q", ""),                                  # trunchiată
    (0, antet("LISTEN 0 2048"), ""),                          # rând incomplet
    (0, antet(rand().replace("127.0.0.1:8019", "127.0.0.1:9999")), ""),   # alt port
    (0, antet(rand()), "RTNETLINK answers: Operation not permitted"),     # stderr relevant, permisiuni
    (0, antet(rand()[:-3]), ""),                              # rând tăiat în users:(
    (0, "garbage\nLISTEN", ""),
])
def test_ss_eșuat_sau_neinterpretabil_nu_e_niciodata_liber(S, ss):
    S.ss = ss
    assert S.vd.stare_port(8019)[0] == "necunoscut" and S.vd.port_ocupat(8019) is True
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "necunoscut" in motiv
    _fara_semnale(S)
    assert S.vd.proprietari_port(8019)[0]["pid"] is None


def test_proprietar_invizibil_e_strain_si_nu_se_semnaleaza(S):
    S.ss = (0, antet(rand(pid=None)), "")
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "invizibil" in motiv
    _fara_semnale(S)


# ── elibereaza_port: server propriu și refuzurile (§2.1, §2.4, §2.7) ───────────────────────────────────────────────────────────────────
def test_server_propriu_se_opreste_numai_prin_pidfd_cu_sigterm_si_portul_ramane_liber(S):
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert (ok, motiv) == (True, "") and S.semnale == [(PID, signal.SIGTERM)]
    assert S.jurnal and S.jurnal[0][1] == "ok" and ("pid %d" % PID) in S.jurnal[0][0]


def test_sigkill_prin_acelasi_pidfd_numai_daca_procesul_trăieste_dupa_sigterm(S):
    S.opriri_la[PID] = signal.SIGKILL
    ok, _ = S.vd.elibereaza_port(8019, lot="L")
    assert ok and S.semnale == [(PID, signal.SIGTERM), (PID, signal.SIGKILL)]


def test_sigkill_esuat_da_refuz_si_dovezile_raman(S):
    S.opriri_la[PID] = signal.SIGKILL
    S.esec_semnal = signal.SIGKILL
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "SIGKILL" in motiv and not hasattr(S, "jurnal")


def test_sigterm_esuat_da_refuz_fara_sigkill(S):
    S.esec_semnal = signal.SIGTERM
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and S.semnale == [(PID, signal.SIGTERM)]


def test_portul_ramas_ocupat_dupa_oprire_e_refuz_fara_alte_semnale(S):
    S.port_tinut_dupa_oprire = True
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "ocupat" in motiv and {s for _p, s in S.semnale} == {signal.SIGTERM}


@pytest.mark.parametrize("camp,valoare", [
    ("pgid", PID + 1), ("sid", PID + 1), ("start", None),
    ("cwd", "PROD"), ("cwd", None), ("cmd", "python -m http.server"), ("cwd", "ALTUNDEVA"),
])
def test_proces_necorespunzator_e_strain_zero_semnale(S, camp, valoare):
    if valoare == "PROD":
        valoare = S.prod + "/iconta_nou"
        os.makedirs(valoare, exist_ok=True)
    if valoare == "ALTUNDEVA":
        valoare = str(S.tmp)
    S.procs[PID][camp] = valoare
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "ocupat de pid" in motiv
    _fara_semnale(S)


def test_procesul_curent_sau_parintele_nu_se_semnaleaza(S, monkeypatch):
    for pid in (os.getpid(), os.getppid()):
        S.procs.clear()
        S.adauga(pid)
        ok, _m = S.vd.elibereaza_port(8019, lot="L")
        assert not ok
    _fara_semnale(S)


def test_pid_refolosit_intre_identificare_si_pidfd_open_e_refuz_zero_semnale(S):
    S.dupa_deschidere[PID] = {"start": "99999"}      # starttime schimbat după pidfd_open: alt proces
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "schimbat" in motiv
    _fara_semnale(S)


def test_pid_mort_cu_grup_refolosit_nu_se_semnaleaza(S):
    S.pidfd_eroare = ProcessLookupError(PID)
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "pidfd_open" in motiv
    _fara_semnale(S)


def test_pidfd_indisponibil_e_stop_fara_semnale(S):
    S.pidfd_eroare = OSError(38, "Function not implemented")
    ok, _m = S.vd.elibereaza_port(8019, lot="L")
    assert not ok
    _fara_semnale(S)


def test_proprietar_nou_al_portului_dupa_pidfd_open_e_refuz_zero_semnale(S):
    S.ss = [(0, antet(rand()), ""), (0, antet(rand()), ""), (0, antet(rand(PID + 7)), "")]
    ok, motiv = S.vd.elibereaza_port(8019, lot="L")
    assert not ok and "proprietatea portului" in motiv
    _fara_semnale(S)


def test_doi_proprietari_ai_portului_dintre_care_unul_nelider_e_refuz(S):
    S.adauga(PID + 1, pgid=PID)                       # worker în grupul liderului
    ok, _m = S.vd.elibereaza_port(8019, lot="L")
    assert not ok
    _fara_semnale(S)


def test_ruta_cu_sonda_si_oprire_injectate_ramane_neschimbata(S):
    opriri = []
    assert S.vd.elibereaza_port(8019, sonda=lambda: True, opreste_fn=lambda: opriri.append(1)) == (True, "") and opriri == [1]
    assert S.vd.elibereaza_port(8019, sonda=lambda: False, opreste_fn=lambda: opriri.append(1)) == (True, "") and opriri == [1]
    _fara_semnale(S)


# ── opreste: cu stare.json (§2.3) ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_opreste_cu_stare_valida_opreste_prin_pidfd_apoi_sterge_temp(S):
    _temp(S, stare=_stare_buna(S))
    assert S.vd.opreste() == 0
    assert S.semnale == [(PID, signal.SIGTERM)] and not os.path.exists(S.vd.TEMP)


@pytest.mark.parametrize("stare", [
    "{\"pid\": 41001, \"sta",                        # trunchiat
    "nu e json",                                     # corupt
    "[]",                                            # alt tip
    json.dumps({"pid": PID, "sha": "abc"}),          # câmpuri lipsă (formatul vechi)
    json.dumps({"pid": True, "start": "777", "pgid": 1, "sid": 1, "cwd": "/", "cmd": "x", "sha": "a"}),
])
def test_opreste_cu_stare_invalida_zero_semnale_zero_stergeri(S, stare):
    _temp(S, stare=stare)
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.isdir(S.vd.TEMP) and os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


@pytest.mark.parametrize("modif", [
    {"start": "123"},                    # PID refolosit
    {"pgid": PID + 5},                   # alt grup
    {"sid": PID + 5},
    {"cwd": "/altundeva"},
    {"cmd": "python altceva.py"},
    {"boot_id": "alt-boot"},
])
def test_opreste_cu_identitate_diferita_de_stare_zero_semnale_zero_stergeri(S, modif):
    _temp(S, stare=_stare_buna(S, **modif))
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_pid_mort_din_stare_zero_semnale_zero_stergeri(S):
    _temp(S, stare=_stare_buna(S))
    S.pid_exit.add(PID)
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_stare_a_unui_proces_al_productiei_sau_propriu_e_refuz(S):
    os.makedirs(S.prod + "/iconta_nou", exist_ok=True)
    S.procs[PID]["cwd"] = S.prod + "/iconta_nou"
    _temp(S, stare=_stare_buna(S, cwd=S.prod + "/iconta_nou"))
    assert S.vd.opreste() == 1
    S.procs.clear()
    eu = os.getpid()
    S.adauga(eu)
    i = S.procs[eu]
    _temp(S, stare={"pid": eu, "start": i["start"], "pgid": eu, "sid": eu, "cwd": i["cwd"], "cmd": i["cmd"], "boot_id": i["boot_id"], "sha": "abc"})
    assert S.vd.opreste() == 1
    _fara_semnale(S)


def test_opreste_cu_alt_proprietar_al_portului_decat_cel_din_stare_zero_semnale(S):
    _temp(S, stare=_stare_buna(S))
    S.ss = (0, antet(rand(PID + 9)), "")
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_ss_eșuat_zero_semnale_zero_stergeri(S):
    _temp(S, stare=_stare_buna(S))
    S.ss = (1, "", "boom")
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_proces_viu_din_stare_care_nu_tine_portul_nu_il_opreste_si_pastreaza_temp(S):
    _temp(S, stare=_stare_buna(S))
    S.procs[PID]["tine_portul"] = False
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_port_ramas_ocupat_pastreaza_temp(S):
    _temp(S, stare=_stare_buna(S))
    S.port_tinut_dupa_oprire = True
    assert S.vd.opreste() == 1
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


# ── opreste: fără stare.json (§2.3, §2.4, U.1 c / incidentul 17.5-E) ──────────────────────────────────────────────────────────────────────
def test_opreste_fara_stare_port_liber_si_fara_temp_e_idempotent(S):
    S.procs.clear()
    assert S.vd.opreste() == 0
    _fara_semnale(S)


def test_opreste_fara_stare_cu_server_al_uneltelor_pe_port_il_opreste_prin_pidfd_si_curata_temp_propriu(S):
    _temp(S)                                           # TEMP propriu (marcajul uneltei), stare.json ștearsă
    assert S.vd.opreste() == 0
    assert S.semnale == [(PID, signal.SIGTERM)] and not os.path.exists(S.vd.TEMP)


def test_opreste_fara_stare_cu_proces_strain_pe_port_nu_semnaleaza_si_pastreaza_temp(S):
    _temp(S)
    S.procs[PID]["cwd"] = str(S.tmp)
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_fara_stare_cu_temp_nepropriu_si_port_liber_il_pastreaza_cu_rc_nenul(S):
    S.procs.clear()
    _temp(S, cu_marcaj=False)
    assert S.vd.opreste() == 1
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_opreste_cu_temp_legatura_simbolica_nu_sterge_tinta(S):
    S.procs.clear()
    tinta = S.tmp / "tinta"
    tinta.mkdir()
    (tinta / "important.txt").write_text("x")
    (tinta / S.vd.MARCAJ_TEMP).write_text("1\n")       # chiar cu marcajul uneltei în țintă: o legătură simbolică nu e niciodată TEMP propriu
    os.symlink(tinta, S.vd.TEMP)
    assert S.vd.opreste() == 1
    assert (tinta / "important.txt").exists() and os.path.islink(S.vd.TEMP)


def test_lstat_care_arata_o_legatura_simbolica_cu_mod_si_proprietar_buni_tot_nu_e_temp_propriu(S, monkeypatch):
    _temp(S)                                           # director real cu marcajul uneltei; numai lstat-ul îl declară legătură simbolică
    real = os.lstat

    def lstat(cale, *a, **k):
        if cale == S.vd.TEMP:
            return os.stat_result((0o120700, 1, 1, 1, os.getuid(), os.getgid(), 0, 0, 0, 0))
        return real(cale, *a, **k)
    monkeypatch.setattr(os, "lstat", lstat)
    assert S.vd._temp_proprietar()[0] == "nesigur"


def test_opreste_fara_stare_cu_ss_eșuat_e_refuz(S):
    S.ss = (1, "", "boom")
    assert S.vd.opreste() == 1
    _fara_semnale(S)


# ── lacătul (§2.5) ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _tine_lacatul(S):
    fd = os.open(S.vd.LACAT_VD, os.O_RDWR | os.O_CREAT, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def test_doua_opriri_simultane_a_doua_nu_trece_de_lacat(S):
    _temp(S, stare=_stare_buna(S))
    fd = _tine_lacatul(S)
    try:
        assert S.vd.opreste() == 1
        ok, motiv = S.vd.elibereaza_port(8019, lot="L")
        assert not ok and "lacătul" in motiv
    finally:
        os.close(fd)
    _fara_semnale(S)
    assert os.path.exists(os.path.join(S.vd.TEMP, "dovada.txt"))


def test_pornire_in_timpul_unei_opriri_e_refuzata_de_lacat(S, monkeypatch):
    fd = _tine_lacatul(S)
    try:
        assert S.vd.porneste() == 1
    finally:
        os.close(fd)
    _fara_semnale(S)


def test_lacatul_e_reentrant_in_acelasi_proces_si_se_elibereaza_la_sfarsit(S):
    with S.vd._lacat():
        with S.vd._lacat():
            assert S.vd._LACAT_STARE["adancime"] == 2
        assert S.vd._LACAT_STARE["adancime"] == 1 and S.vd._LACAT_STARE["fd"] is not None
    assert S.vd._LACAT_STARE["adancime"] == 0 and S.vd._LACAT_STARE["fd"] is None
    fd = _tine_lacatul(S)                              # liber din nou: a putut fi luat de altcineva
    assert fd is not None
    os.close(fd)


# ── porneste (§2.5, §2.6) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class FakePopen:
    def __init__(self, S, *a, **k):
        self.S, self.pid, self.returncode, self.waited = S, PID, None, 0
        S.popen = self
        S.popen_args = (a, k)

    def poll(self):
        if self.pid in self.S.pid_exit and self.returncode is None:
            self.returncode = -15
        return self.returncode

    def wait(self, timeout=None):
        self.waited += 1
        if self.poll() is None:
            if self.S.ramane_viu:
                raise subprocess.TimeoutExpired("x", timeout or 0)
            self.returncode = 0
        return self.returncode


@pytest.fixture
def P(S, monkeypatch, tmp_path):
    """Mediul lui `porneste()`: copia firmelor, e2e_poarta și dovada_firme_test false, subprocess și Popen simulate."""
    vd = S.vd
    os.makedirs(vd.STARE_COPIE, exist_ok=True)
    open(os.path.join(vd.STARE_COPIE, "stare.json"), "w").write("{}")
    S.procs.clear()
    S.exporturi, S.popen, S.ramane_viu = [], None, False

    def exporta(din_arbore):
        S.exporturi.append(din_arbore)
        arb = os.path.join(vd.TEMP, "iconta_nou")
        import shutil
        shutil.rmtree(vd.TEMP, ignore_errors=True)
        os.makedirs(arb)
        return arb

    e2e = types.ModuleType("e2e_poarta")
    e2e.TEMP = vd.TEMP
    e2e._exporta = exporta
    e2e._env_test = lambda: {k: str(tmp_path / k) for k in ("ICONTA_AI_SIMULAT", "ICONTA_ANAF_SIMULAT", "ICONTA_BON_DIR")}
    dft = types.ModuleType("dovada_firme_test")
    dft.tinta_de_test = lambda env: None
    monkeypatch.setitem(sys.modules, "e2e_poarta", e2e)
    monkeypatch.setitem(sys.modules, "dovada_firme_test", dft)
    monkeypatch.setattr(vd.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "abc123\n", ""))
    monkeypatch.setattr(vd.subprocess, "Popen", lambda *a, **k: FakePopen(S, *a, **k))
    monkeypatch.setattr(vd, "_raspunde", lambda port=None: True)

    def cand_exista_copil():                           # procesul copil apare pe port când pornește Popen
        S.adauga(PID)
    S.pornire = cand_exista_copil
    orig = vd.subprocess.Popen

    def popen(*a, **k):
        p = orig(*a, **k)
        S.pornire()
        return p
    monkeypatch.setattr(vd.subprocess, "Popen", popen)
    S.e2e = e2e
    return S


def test_porneste_reusit_scrie_stare_cu_identitatea_si_marcajul_fara_semnale(P):
    assert P.vd.porneste() == 0
    st = json.load(open(P.vd.STARE))
    assert st["pid"] == PID and st["start"] == "777" and st["pgid"] == PID and st["sid"] == PID and st["boot_id"] == "boot-1" and st["cmd"] and st["cwd"]
    assert os.path.exists(os.path.join(P.vd.TEMP, P.vd.MARCAJ_TEMP)) and P.exporturi == [False]
    _fara_semnale(P)


def test_porneste_cu_ss_eșuat_nu_porneste_nimic_si_nu_exporta(P):
    P.ss = (1, "", "boom")
    assert P.vd.porneste() == 1
    assert P.exporturi == [] and P.popen is None


def test_porneste_cu_port_ocupat_refuza(P):
    P.adauga(PID + 3)
    P.ss = "auto"
    assert P.vd.porneste() == 1 and P.exporturi == [] and P.popen is None


def test_porneste_cu_temp_legatura_simbolica_refuza_inainte_de_export_si_nu_sterge_tinta(P):
    tinta = P.tmp / "tinta"
    tinta.mkdir()
    (tinta / "important.txt").write_text("x")
    (tinta / P.vd.MARCAJ_TEMP).write_text("1\n")
    os.symlink(tinta, P.vd.TEMP)
    assert P.vd.porneste() == 4
    assert P.exporturi == [] and (tinta / "important.txt").exists()


def test_porneste_cu_temp_strain_sau_folosit_refuza_inainte_de_export(P):
    _temp(P, cu_marcaj=False)
    assert P.vd.porneste() == 4 and P.exporturi == [] and os.path.exists(os.path.join(P.vd.TEMP, "dovada.txt"))
    P.adauga(PID, tine_portul=False)
    _temp(P, stare=_stare_buna(P))                      # propriu, dar cu un proces viu în stare.json
    assert P.vd.porneste() == 4 and P.exporturi == [] and os.path.exists(os.path.join(P.vd.TEMP, "dovada.txt"))


def test_porneste_cu_temp_al_altui_proprietar_sau_cu_drept_de_scriere_pentru_altii_refuza(P):
    _temp(P)
    os.chmod(P.vd.TEMP, 0o777)
    assert P.vd.porneste() == 4 and P.exporturi == []


def test_porneste_cu_ss_eșuat_la_revalidarea_dinaintea_exportului_nu_exporta(P):
    P.ss = [(0, antet(), ""), (1, "", "boom")]
    assert P.vd.porneste() == 4 and P.exporturi == [] and P.popen is None


def test_porneste_cu_e2e_temp_diferit_de_temp_refuza_inainte_de_export(P):
    P.e2e.TEMP = "/tmp/altceva"
    assert P.vd.porneste() == 4 and P.exporturi == []


def test_porneste_cu_eroare_la_export_e_cod_nenul_fara_copil(P):
    def prost(_d):
        raise OSError("disc plin")
    P.e2e._exporta = prost
    assert P.vd.porneste() == 3 and P.popen is None


def test_timeout_la_pornire_opreste_copilul_prin_pidfd_chiar_daca_nu_a_ajuns_pe_port(P):
    P.vd._raspunde = lambda port=None: False
    P.pornire = lambda: P.adauga(PID, tine_portul=False)        # copilul NU apare niciodată în ss
    assert P.vd.porneste() == 3
    assert P.semnale == [(PID, signal.SIGTERM)] and P.popen.waited >= 1
    assert not os.path.exists(P.vd.STARE)


def test_esec_la_scrierea_starii_opreste_copilul_si_nu_da_pass(P, monkeypatch):
    def prost(_s):
        raise OSError("disc plin")
    monkeypatch.setattr(P.vd, "_scrie_stare", prost)
    assert P.vd.porneste() == 3
    assert P.semnale == [(PID, signal.SIGTERM)] and not os.path.exists(P.vd.STARE)


def test_port_ocupat_de_altcineva_in_timpul_pornirii_opreste_numai_copilul_propriu(P):
    P.ss = [(0, antet(), ""), (0, antet(), ""), (0, antet(), ""), (0, antet(rand(PID + 50)), "")]
    assert P.vd.porneste() == 3
    assert P.semnale == [(PID, signal.SIGTERM)]                 # niciun semnal către PID + 50
    assert not os.path.exists(P.vd.STARE)


def test_copil_iesit_inainte_de_pidfd_open_nu_primeste_semnal_si_e_recoltat(P):
    P.pornire = lambda: P.pid_exit.add(PID) or P.adauga(PID)
    P.pid_exit.add(PID)
    P.pidfd_eroare = ProcessLookupError(PID)
    assert P.vd.porneste() == 3
    _fara_semnale(P)
    assert P.popen.waited >= 1


def test_identitate_copil_neputand_fi_stabilita_e_stop_fara_semnale(P):
    P.vd.identitate = lambda pid: None
    assert P.vd.porneste() == 3
    _fara_semnale(P)


def test_copil_cu_grup_diferit_de_pid_nu_e_acceptat_si_nu_se_semnaleaza(P):
    P.pornire = lambda: P.adauga(PID, pgid=PID - 1)
    assert P.vd.porneste() == 3
    _fara_semnale(P)
    assert not os.path.exists(P.vd.STARE)


def test_scrierea_starii_e_atomica(P, monkeypatch):
    inlocuiri = []
    real = os.replace
    monkeypatch.setattr(os, "replace", lambda a, b: (inlocuiri.append((a, b)), real(a, b))[1])
    assert P.vd.porneste() == 0
    assert inlocuiri and inlocuiri[0][1] == P.vd.STARE and inlocuiri[0][0].endswith(".tmp")
