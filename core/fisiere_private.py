# -*- coding: utf-8 -*-
"""core/fisiere_private.py — depozitul privat al fișierelor trimise de cabinete (capturile sesizărilor, exporturile din alte
aplicații), în afara directorului servit public (comanda Costin 15.10.2026, deficiențele C36 și 270d, verbatim în DECIZII:
„Fișierele le vede doar echipa iConta, sunt izolate pe cabinet și cabinetul le poate șterge.”).

DE CE (C36). Până azi o captură atașată unei sesizări se scria în `<static>/raportari/` și se servea la `/static/raportari/<nume>`
— fără autentificare: oricine avea adresa o putea deschide, iar numele era ghicibil (`r<fir>_m<mesaj>_<8 hex>`). Două capturi
ajunseseră chiar în depozitul git (`static/raportari/r2_m3_….png`, `r4_m6_….png`), deci și pe toate copiile lui.

CE FACE:
- **Locul:** `~/iconta_date/fisiere/<cabinet>/` pe producție (alături de `~/iconta_date/bonuri`, `common.dir_bonuri`), în afara
  depozitului git și a directorului servit; plasa își dă directorul ei prin `ICONTA_FISIERE_DIR`, pe care un mediu care nu se
  dovedește de test îl refuză; pe un mediu de test fără `ICONTA_FISIERE_DIR` nu se scrie nimic (nu cade lângă fișierele reale).
  Un director din interiorul depozitului sau al celui servit e refuzat (`verifica_director`).
- **Tipul se citește din conținut**, nu din `content_type` sau din nume: semnătura PNG / JPEG / WEBP / XLS (OLE2) / ZIP (XLSX =
  ZIP cu `xl/workbook.xml`); CSV-ul n-are semnătură, deci se cere numele `.csv` ȘI un text care se citește sigur
  (`import_tabel.decodeaza`, fără octeți nuli). Limita: `MARIME_MAXIMA` pe fișier.
- **Metadatele** în `public.fisiere_private` (migrarea `core/migrare_fisiere_private.py`): cabinetul, autorul, mesajul sesizării,
  numele original, mărimea, tipul, calea relativă, data.
- **Accesul** (`al_firului`): echipa iConta (superadmin) și autorul sesizării, pe cabinetul lui; oricine altcineva primește „nu
  există” — filtrul e în SQL, nu numai în rută (ca `raportari_api.firul_complet`, izolare_raportari 09.08.2026). Ștergerea: autorul
  sesizării; scoate și fișierul de pe disc.

Tranzacția e a apelantului (`uc_raportari`): 0 get_conn / 0 commit aici.
Temei: N/A — păstrarea fișierelor (tooling), nicio valoare fiscală.
"""
from __future__ import annotations

import io
import os
import uuid
import zipfile

import psycopg2.extras as _E

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: limita unui fișier — aceeași ca a capturilor de până acum (8 MB), declarată și pe ecran
MARIME_MAXIMA = 8 * 1024 * 1024

#: capturile (sesizări și cereri de import) și exporturile (numai cererile de import)
CAPTURI = ("png", "jpg", "webp")
EXPORTURI = ("csv", "xls", "xlsx", "zip")

MIME = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp", "csv": "text/csv; charset=utf-8",
        "xls": "application/vnd.ms-excel", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "zip": "application/zip"}

NUME_TIP = {"png": "PNG", "jpg": "JPG", "webp": "WEBP", "csv": "CSV", "xls": "XLS", "xlsx": "XLSX", "zip": "ZIP"}


class FisierRefuzat(ValueError):
    """Fișierul nu se primește: `cod` = „format” (tipul nu e printre cele permise, după conținut) sau „marime”."""

    def __init__(self, cod, mesaj):
        super().__init__(mesaj)
        self.cod = cod


# ── locul ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def director():
    """Rădăcina depozitului. Producția: `~/iconta_date/fisiere`. Plasa: `ICONTA_FISIERE_DIR` (refuzat pe un mediu nedovedit de
    test). Un mediu dovedit de test fără `ICONTA_FISIERE_DIR` e refuzat: altfel o probă ar scrie lângă fișierele reale."""
    from core import mediu_test
    d = os.getenv("ICONTA_FISIERE_DIR")
    e_test = not mediu_test.motive()
    if d:
        if not e_test:
            raise RuntimeError("ICONTA_FISIERE_DIR e setat pe un mediu care nu e de test (%s)"
                               % ", ".join(x.cod for x in mediu_test.motive()))
    elif e_test:
        raise RuntimeError("pe mediul de test directorul fișierelor private se dă prin ICONTA_FISIERE_DIR — fără el, proba ar "
                           "scrie în ~/iconta_date/fisiere, lângă fișierele reale")
    else:
        d = os.path.expanduser("~/iconta_date/fisiere")
    return verifica_director(d)


def _dir_servit():
    from core import uc_comun
    return uc_comun._STATIC_DIR


def verifica_director(d, servit=None):
    """`d` absolut, dacă nu e în depozitul git și nici în directorul servit public; altfel `RuntimeError`."""
    d = os.path.realpath(os.path.expanduser(d))
    interzise = [_RAD] + [x for x in ((servit if servit is not None else _dir_servit()),) if x]
    for x in interzise:
        x = os.path.realpath(x)
        if d == x or d.startswith(x + os.sep):
            raise RuntimeError("depozitul fișierelor private (%s) nu are voie să stea în %s" % (d, x))
    return d


# ── tipul, după conținut ───────────────────────────────────────────────────────────────────────────────────────────────────
def tip_din_continut(octeti, nume):
    """`png` / `jpg` / `webp` / `xls` / `xlsx` / `zip` după semnătură, `csv` după nume + text citibil; altfel `None`."""
    b = bytes(octeti or b"")
    if b.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if b.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "webp"
    if b.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "xls"
    if b.startswith(b"PK\x03\x04") or b.startswith(b"PK\x05\x06"):
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                return "xlsx" if "xl/workbook.xml" in z.namelist() else "zip"
        except zipfile.BadZipFile:
            return None
    if (nume or "").lower().strip().endswith(".csv") and b and b"\x00" not in b:
        from core import import_tabel
        try:
            import_tabel.decodeaza(b, nume)
        except import_tabel.FisierNecitit:
            return None
        return "csv"
    return None


def verifica(octeti, nume, permise):
    """Tipul fișierului, dacă e printre `permise` și sub limită; altfel `FisierRefuzat` cu motivul în cuvinte."""
    if len(octeti or b"") > MARIME_MAXIMA:
        raise FisierRefuzat("marime", "Fișierul «%s» e prea mare: limita e %d MB." % (nume or "trimis", MARIME_MAXIMA // (1024 * 1024)))
    tip = tip_din_continut(octeti, nume)
    if tip not in permise:
        raise FisierRefuzat("format", "Fișierul «%s» nu e %s (se verifică după conținut, nu după nume)."
                            % (nume or "trimis", _enumera([NUME_TIP[t] for t in permise])))
    return tip


def _enumera(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " sau " + xs[-1]


# ── scrierea, citirea, ștergerea ───────────────────────────────────────────────────────────────────────────────────────────
def salveaza(conn, cabinet_id, autor_id, mesaj_id, nume_orig, octeti, permise):
    """Scrie fișierul în depozit și rândul lui; întoarce `{id, nume, tip, marime}`. Dacă rândul nu se scrie, fișierul se scoate."""
    tip = verifica(octeti, nume_orig, permise)
    rad = director()
    rel = os.path.join(str(cabinet_id) if cabinet_id is not None else "fara_cabinet", "%s.%s" % (uuid.uuid4().hex, tip))
    cale = os.path.join(rad, rel)
    os.makedirs(os.path.dirname(cale), mode=0o700, exist_ok=True)
    tmp = cale + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(octeti)
    os.chmod(tmp, 0o600)
    os.replace(tmp, cale)
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.fisiere_private (cabinet_id, autor_id, mesaj_id, nume_orig, marime, tip, cale) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                        (cabinet_id, autor_id, mesaj_id, (nume_orig or "fisier").strip()[:255], len(octeti), tip, rel))
            fid = cur.fetchone()[0]
    except Exception:
        os.remove(cale)
        raise
    return {"id": fid, "nume": (nume_orig or "fisier").strip()[:255], "tip": tip, "marime": len(octeti)}


_AL_FIRULUI = ("SELECT f.id, f.cale, f.nume_orig, f.tip, f.marime, f.cabinet_id, r.autor_id AS autor_fir "
               "  FROM public.fisiere_private f "
               "  JOIN public.raportari_mesaje m ON m.id = f.mesaj_id "
               "  JOIN public.raportari r ON r.id = m.raportare_id "
               " WHERE f.id = %s")


def al_firului(conn, fid, uid, cabinet_id, e_superadmin):
    """Fișierul, dacă cine cere îl poate vedea: echipa iConta (superadmin) sau autorul sesizării, pe cabinetul lui. Altfel `None`
    — nu se deosebește „nu există” de „nu e al tău”, ca absența să nu spună nimic despre alt cabinet."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        if e_superadmin:
            cur.execute(_AL_FIRULUI, (fid,))
        else:
            cur.execute(_AL_FIRULUI + " AND r.autor_id = %s AND f.cabinet_id IS NOT DISTINCT FROM %s", (fid, uid, cabinet_id))
        r = cur.fetchone()
    return dict(r) if r else None


def cale_pe_disc(rand):
    return os.path.join(director(), rand["cale"])


def sterge(conn, fid, uid, cabinet_id):
    """Scoate rândul (numai autorul sesizării, pe cabinetul lui) și întoarce calea fișierului de pe disc, de scos DUPĂ commit;
    `None` dacă fișierul nu e al lui."""
    rand = al_firului(conn, fid, uid, cabinet_id, e_superadmin=False)
    if not rand:
        return None
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.fisiere_private WHERE id = %s", (fid,))
    return cale_pe_disc(rand)


def ale_mesajelor(cur, mesaj_ids):
    """`{mesaj_id: [{id, nume, tip, marime}]}` — ce arată firul (numele, nu calea). `cur` e un cursor cu rânduri-dicționar."""
    out = {}
    if not mesaj_ids:
        return out
    cur.execute("SELECT id, mesaj_id, nume_orig, tip, marime FROM public.fisiere_private WHERE mesaj_id = ANY(%s) ORDER BY id",
                (list(mesaj_ids),))
    for r in cur.fetchall():
        out.setdefault(r["mesaj_id"], []).append({"id": r["id"], "nume": r["nume_orig"], "tip": r["tip"], "marime": r["marime"]})
    return out
