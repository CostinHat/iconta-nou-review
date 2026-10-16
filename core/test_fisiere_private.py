# -*- coding: utf-8 -*-
"""core/test_fisiere_private.py — gardurile depozitului privat al fișierelor (C36 și 270d, comanda Costin 15.10.2026, verbatim în DECIZII:
„Fișierele le vede doar echipa iConta, sunt izolate pe cabinet și cabinetul le poate șterge.”).

Ce fac imposibil:
- o captură / un export servit fără autentificare: nicio scriere a aplicației în directorul servit (`test_nimeni_nu_scrie_in_static`) și
  depozitul refuză un director din depozitul git sau din cel servit;
- un fișier al altui cabinet descărcat sau șters: 404 la HTTP, cu filtrul în SQL (`al_firului`), nu numai în rută;
- un tip ghicit după nume sau după `content_type`: semnătura conținutului decide (un HTML numit `.png` e refuzat);
- o probă care scrie lângă fișierele reale: pe mediul de test fără `ICONTA_FISIERE_DIR` depozitul refuză;
- mutarea atașamentelor vechi care pierde tăcut o captură: un fișier negăsit oprește migrarea fără să scrie nimic.
Efemer: firme / utilizatori / fire pe o conexiune din pool, `get_conn` înlocuit cu ea (commit = nimic), rollback la final; fișierele în
`tmp_path`. Temei: N/A — păstrarea fișierelor (tooling).
"""
import ast
import contextlib
import io
import os
import zipfile

import pytest

from core import auth_api, db as _db, fisiere_private as fp, raportari_api
from core.mesaje import mesaj_din_cod

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + b"\x00" * 20
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 20
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 20
XLS = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 40
CSV = "Simbol cont;Denumirea contului;Sold final debitor\n5311;Casa în lei;300\n".encode("utf-8")


def _zip(nume):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n in nume:
            z.writestr(n, "x")
    return b.getvalue()


XLSX = _zip(["[Content_Types].xml", "xl/workbook.xml"])
ZIP = _zip(["balanta.csv", "parteneri.csv"])


# ── tipul după conținut ─────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("octeti, nume, tip", [
    (PNG, "captura.png", "png"), (JPG, "captura.jpg", "jpg"), (WEBP, "c.webp", "webp"), (XLS, "balanta.xls", "xls"),
    (XLSX, "balanta.xlsx", "xlsx"), (ZIP, "export.zip", "zip"), (CSV, "balanta.csv", "csv"),
    (PNG, "balanta.csv", "png"),                                   # conținutul decide, nu numele
    (b"<html><script>alert(1)</script></html>", "captura.png", None),   # un HTML numit .png nu e o captură
    (CSV, "balanta.exe", None),                                     # textul fără nume .csv nu e un CSV
    (b"a;b\x00c\n", "x.csv", None),                                 # octeți nuli: nu e text
    (b"PK\x03\x04stricat", "x.zip", None),                          # ZIP stricat
    (b"Furnizor \x81\x83\x88", "x.csv", None),                       # nici UTF-8, nici Windows-1250 plauzibil
], ids=lambda v: "octeti" if isinstance(v, bytes) else str(v))   # [Lotul 5] id-uri STABILE: un ZIP poartă ora creării, deci un id
#   făcut din octeți diferea între procesele xdist („Different tests were collected”) și poarta (`-n 3`) nu pornea
def test_tipul_se_citeste_din_continut(octeti, nume, tip):
    """MUTAȚIA: semnătura PNG scoasă din `tip_din_continut` -> „captura.png” nu mai e png -> ROȘU."""
    assert fp.tip_din_continut(octeti, nume) == tip


def test_permise_si_limita():
    assert fp.verifica(PNG, "c.png", fp.CAPTURI) == "png"
    with pytest.raises(fp.FisierRefuzat) as e:
        fp.verifica(CSV, "b.csv", fp.CAPTURI)                       # un export pe un fir de sesizare
    assert (e.value.cod, str(e.value)) == ("format", "Fișierul «b.csv» nu e PNG, JPG sau WEBP (se verifică după conținut, nu după nume).")
    with pytest.raises(fp.FisierRefuzat) as e:
        fp.verifica(PNG + b"\x00" * fp.MARIME_MAXIMA, "c.png", fp.CAPTURI)
    assert (e.value.cod, str(e.value)) == ("marime", "Fișierul «c.png» e prea mare: limita e 8 MB.")


# ── locul ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_depozitul_nu_sta_in_git_nici_in_directorul_servit(tmp_path):
    """MUTAȚIA: `verifica_director` care nu verifică directorul servit -> ROȘU."""
    servit = tmp_path / "iconta_publicat" / "static"
    with pytest.raises(RuntimeError):
        fp.verifica_director(os.path.join(RAD, "static", "fisiere"), servit=str(servit))
    with pytest.raises(RuntimeError):
        fp.verifica_director(str(servit / "raportari"), servit=str(servit))
    assert fp.verifica_director(str(tmp_path / "fisiere"), servit=str(servit)) == os.path.realpath(str(tmp_path / "fisiere"))


def test_pe_mediul_de_test_depozitul_se_da_explicit(monkeypatch, tmp_path):
    """Pe mediul de test, fără `ICONTA_FISIERE_DIR`, nu se scrie în ~/iconta_date/fisiere; pe un mediu nedovedit de test, variabila e
    refuzată (ca `ICONTA_BON_DIR`)."""
    monkeypatch.delenv("ICONTA_FISIERE_DIR", raising=False)
    with pytest.raises(RuntimeError, match="ICONTA_FISIERE_DIR"):
        fp.director()
    monkeypatch.setenv("ICONTA_FISIERE_DIR", str(tmp_path))
    assert fp.director() == os.path.realpath(str(tmp_path))
    monkeypatch.setenv("ICONTA_MEDIU", "productie")
    with pytest.raises(RuntimeError, match="nu e de test"):
        fp.director()
    monkeypatch.delenv("ICONTA_FISIERE_DIR")
    assert fp.director() == os.path.realpath(os.path.expanduser("~/iconta_date/fisiere"))


def test_nimeni_nu_scrie_in_static():
    """Singurul cititor al directorului servit din `core/` (în afara definiției din `uc_comun`) e garda depozitului privat. Fostul drum
    (`uc_raportari` scria capturile în `<static>/raportari`, servite fără autentificare — C36) nu poate reveni. MUTAȚIA: un
    `os.path.join(_uc_comun._STATIC_DIR, "raportari")` repus în `uc_raportari` -> ROȘU."""
    rele = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        src = open(os.path.join(RAD, "core", f), encoding="utf-8").read()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, (ast.Name, ast.Attribute)) and getattr(n, "id", getattr(n, "attr", None)) == "_STATIC_DIR":
                rele.append((f, n.lineno))
    rele = [x for x in rele if x[0] not in ("uc_comun.py", "fisiere_private.py")]
    assert not rele, "directorul servit folosit în afara depozitului privat: %s" % rele


# ── izolarea, la HTTP ───────────────────────────────────────────────────────────────────────────────────────────────────────
class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass


def _user(cur, email, rol, firm):
    cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) "
                "VALUES (%s,'x','N','N',%s,%s,true) RETURNING id", (email, rol, firm))
    return cur.fetchone()[0]


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("ICONTA_FISIERE_DIR", str(tmp_path / "fisiere"))
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST FIS A') RETURNING id")
            fa = cur.fetchone()[0]
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST FIS B') RETURNING id")
            fb = cur.fetchone()[0]
            u = {"patron_a": (_user(cur, "ztest_fis_pa@invalid", "admin_firma", fa), "admin_firma", fa),
                 "asist_a": (_user(cur, "ztest_fis_aa@invalid", "angajat", fa), "angajat", fa),
                 "patron_b": (_user(cur, "ztest_fis_pb@invalid", "admin_firma", fb), "admin_firma", fb),
                 "echipa": (_user(cur, "ztest_fis_sa@invalid", "superadmin", None), "superadmin", None)}

        @contextlib.contextmanager
        def _fake(schema=None):
            yield _ConnProxy(conn)
        monkeypatch.setattr(_db, "get_conn", _fake)
        tok = {k: auth_api.emite_token({"id": i, "rol": r, "accounting_firm_id": f}) for k, (i, r, f) in u.items()}
        yield {"conn": conn, "tok": tok, "u": u, "fa": fa, "dir": tmp_path / "fisiere", "mp": monkeypatch}
    finally:
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _h(env, cine):
    return {"Authorization": "Bearer " + env["tok"][cine]}


def _fisiere_pe_disc(d):
    return sorted(os.path.relpath(os.path.join(r, f), d) for r, _s, fs in os.walk(d) for f in fs) if os.path.isdir(d) else []


def test_cererea_de_import_fisierele_vazute_doar_de_echipa_si_autor(env):
    """270d / C36: cererea de import cu un CSV și o captură -> autorul și echipa iConta le descarcă; alt cabinet și colegul din același
    cabinet primesc 404 (și la ștergere); autorul șterge -> rândul și fișierul de pe disc dispar. Nimic în directorul servit.
    MUTAȚIA: filtrul pe autor scos din `al_firului` -> cabinetul B primește 200 -> ROȘU."""
    from core import uc_comun
    servit = str(env["dir"].parent / "servit")          # directorul servit, mutat lângă probă: nu se citește cel al producției
    os.makedirs(servit)
    cl = _client()                                      # întâi `main` (își pune directorul servit la import), apoi mutarea lui
    env["mp"].setattr(uc_comun, "_STATIC_DIR", servit)
    r = cl.post("/raportari", json={"tip": "cerere_import", "aplicatie": "WinMentor"}, headers=_h(env, "patron_a"))
    assert r.status_code == 200, r.text
    mid = r.json()["mesaj_id"]
    ids = {}
    for nume, octeti in (("balanta.csv", CSV), ("meniu_export.png", PNG)):
        r = cl.post("/raportari/mesaj/%d/fisier" % mid, files={"fisier": (nume, octeti, "application/octet-stream")},
                    headers=_h(env, "patron_a"))
        assert r.status_code == 200, r.text
        ids[nume] = r.json()["id"]
    assert len(_fisiere_pe_disc(env["dir"])) == 2 and _fisiere_pe_disc(servit) == []
    assert all(x.startswith("%d/" % env["fa"]) for x in _fisiere_pe_disc(env["dir"]))      # izolate pe cabinet și pe disc
    fid = ids["balanta.csv"]
    for cine, cod in (("patron_a", 200), ("echipa", 200), ("patron_b", 404), ("asist_a", 404)):
        r = cl.get("/raportari/fisiere/%d" % fid, headers=_h(env, cine))
        assert r.status_code == cod, (cine, r.status_code, r.text)
        if cod == 200:
            assert r.content == CSV and r.headers["content-disposition"].split(";")[0] == "attachment"
            assert r.headers["x-content-type-options"] == "nosniff"
    assert cl.get("/raportari/fisiere/%d" % fid).status_code == 401                      # fără autentificare
    fir = cl.get("/raportari/eu", headers=_h(env, "patron_a")).json()["raportari"][0]
    assert (fir["tip"], fir["aplicatie"]) == ("cerere_import", "WinMentor")
    assert [(a["nume"], a["tip"]) for a in fir["mesaje"][0]["atasamente"]] == [("balanta.csv", "csv"), ("meniu_export.png", "png")]
    assert "cale" not in fir["mesaje"][0]["atasamente"][0]                                 # numele, nu calea de pe disc
    assert cl.delete("/raportari/fisiere/%d" % fid, headers=_h(env, "patron_b")).status_code == 404
    assert cl.delete("/raportari/fisiere/%d" % fid, headers=_h(env, "patron_a")).status_code == 200
    assert len(_fisiere_pe_disc(env["dir"])) == 1
    assert cl.get("/raportari/fisiere/%d" % fid, headers=_h(env, "echipa")).status_code == 404


def test_exporturile_numai_pe_cererea_de_import_capturile_dupa_continut(env):
    """Pe o sesizare se primesc numai capturi (și pe ruta nouă); pe cererea de import, ruta capturilor nu primește un CSV; un HTML numit
    `.png` e refuzat oriunde. MUTAȚIA: `permise` fără condiția pe felul firului -> CSV-ul intră pe sesizare -> ROȘU."""
    cl = _client()
    uid = env["u"]["patron_a"][0]
    s = raportari_api.creeaza_raportare(env["conn"], uid, env["fa"], None, "ceva nu merge")       # sesizare (fără triajul AI)
    r = cl.post("/raportari/mesaj/%d/fisier" % s["mesaj_id"], files={"fisier": ("b.csv", CSV, "text/csv")}, headers=_h(env, "patron_a"))
    assert r.status_code == 415, r.text
    r = cl.post("/raportari/mesaj/%d/imagine" % s["mesaj_id"], files={"fisier": ("c.png", PNG, "text/plain")}, headers=_h(env, "patron_a"))
    assert r.status_code == 200, r.text                                                     # content_type minte, conținutul decide
    r = cl.post("/raportari/mesaj/%d/imagine" % s["mesaj_id"], files={"fisier": ("c.png", b"<html></html>", "image/png")},
                headers=_h(env, "patron_a"))
    assert r.status_code == 415, r.text
    c = cl.post("/raportari", json={"tip": "cerere_import", "aplicatie": "Ciel"}, headers=_h(env, "patron_a")).json()
    r = cl.post("/raportari/mesaj/%d/imagine" % c["mesaj_id"], files={"fisier": ("b.csv", CSV, "text/csv")}, headers=_h(env, "patron_a"))
    assert r.status_code == 415, r.text
    r = cl.post("/raportari/mesaj/%d/fisier" % c["mesaj_id"], files={"fisier": ("b.csv", CSV, "text/csv")}, headers=_h(env, "patron_b"))
    assert r.status_code == 403, r.text                                                     # pe firul altuia nu încarci
    r = cl.post("/raportari", json={"tip": "cerere_import", "aplicatie": "  "}, headers=_h(env, "patron_a"))
    assert (r.status_code, r.json()["detail"]) == (400, mesaj_din_cod("APLICATIE_LIPSA")), r.text


def test_registrul_aplicatiilor_la_ruta(env):
    from core import aplicatii_migrare
    cl = _client()
    r = cl.get("/migrare/aplicatii", headers=_h(env, "asist_a"))
    assert r.status_code == 200 and r.json() == {"aplicatii": aplicatii_migrare.registru()}, r.text
    assert cl.get("/migrare/aplicatii").status_code == 401


# ── mutarea atașamentelor vechi ─────────────────────────────────────────────────────────────────────────────────────────────
def _fir_cu_atasament(cur, uid, fa, nume):
    cur.execute("CREATE TABLE public.raportari_atasamente (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, mesaj_id bigint NOT NULL, "
                "cale text NOT NULL, nume_orig text, creat_la timestamptz NOT NULL DEFAULT now())")
    cur.execute("INSERT INTO public.raportari (autor_id, cabinet_id) VALUES (%s,%s) RETURNING id", (uid, fa))
    rid = cur.fetchone()[0]
    cur.execute("INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text) VALUES (%s,%s,'utilizator','x') "
                "RETURNING id", (rid, uid))
    mid = cur.fetchone()[0]
    cur.execute("INSERT INTO public.raportari_atasamente (mesaj_id, cale, nume_orig) VALUES (%s,%s,'captura.png')",
                (mid, "/static/raportari/" + nume))
    return mid


def test_migrarea_muta_capturile_vechi_in_depozit(env, tmp_path):
    """Captura veche din `<static>/raportari` intră în depozit, cu rândul ei; tabela veche dispare; fișierul vechi e de scos după commit.
    O captură negăsită oprește migrarea fără să scrie nimic. MUTAȚIA: negăsitele sărite în tăcere -> ROȘU."""
    from core import migrare_fisiere_private as m
    conn = env["conn"]
    vechi = tmp_path / "publicat_raportari"
    vechi.mkdir()
    (vechi / "r1_m1_abcd.png").write_bytes(PNG)
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT lipsa")
        _fir_cu_atasament(cur, env["u"]["patron_a"][0], env["fa"], "r9_m9_lipsa.png")
    with pytest.raises(RuntimeError, match="r9_m9_lipsa.png"):
        m.muta_atasamentele(conn, [str(vechi)])
    with conn.cursor() as cur:
        cur.execute("ROLLBACK TO SAVEPOINT lipsa")
        mid = _fir_cu_atasament(cur, env["u"]["patron_a"][0], env["fa"], "r1_m1_abcd.png")
    mutate, de_sters = m.muta_atasamentele(conn, [str(vechi)])
    assert (mutate, de_sters) == (1, [str(vechi / "r1_m1_abcd.png")])
    with conn.cursor() as cur:
        cur.execute("SELECT cabinet_id, nume_orig, tip, cale FROM public.fisiere_private WHERE mesaj_id = %s", (mid,))
        cab, nume, tip, cale = cur.fetchone()
        cur.execute("SELECT to_regclass('public.raportari_atasamente')")
        assert cur.fetchone()[0] is None
    assert (cab, nume, tip) == (env["fa"], "captura.png", "png")
    assert open(os.path.join(fp.director(), cale), "rb").read() == PNG
