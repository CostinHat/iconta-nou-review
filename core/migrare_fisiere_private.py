"""
core/migrare_fisiere_private.py — depozitul privat al fișierelor și cererea de import din altă aplicație (comanda Costin 15.10.2026,
deficiențele C36 și 270d, verbatim în DECIZII).

- `public.fisiere_private` — metadatele fișierelor trimise de cabinete (capturi, exporturi), păstrate în afara directorului servit
  (`core/fisiere_private.py`): cabinetul, autorul, mesajul sesizării de care țin, numele original, mărimea, tipul (după conținut),
  calea relativă în depozit, data.
- `public.raportari.tip` (`sesizare` / `cerere_import`, implicit `sesizare` — sesizările de până azi) și `public.raportari.aplicatie`
  (aplicația din care migrează cabinetul, numai la cererea de import).
- **Mutarea atașamentelor vechi:** fiecare rând din `public.raportari_atasamente` (capturi scrise până azi în `<static>/raportari/`,
  servite fără autentificare — C36) se copiază în depozit și primește rândul lui în `fisiere_private`; tabela veche se scoate, iar
  fișierele vechi se șterg din directorul PUBLICAT (niciodată din depozitul git — acolo le scoate commitul). Un fișier care nu se
  găsește pe disc OPREȘTE migrarea, cu lista lor, fără să scrie nimic: o captură nu dispare tăcut.
  Unde se caută: `ICONTA_RAPORTARI_VECHI` (directoare separate prin „:”), altfel — numai pe un mediu care nu e de test — directorul
  publicat (`../iconta_publicat/static/raportari`) și `static/raportari` din depozit. Pe baza de test, fără variabilă, nu se caută
  nicăieri (directorul publicat de lângă worktree e al producției).
Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_fisiere_private.py`. Pe producție o
aprobă Costin la publicare: atașamentele pot fi ale cabinetului pilot.
"""
import os
import shutil
import uuid

from core import db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DDL = """
CREATE TABLE IF NOT EXISTS public.fisiere_private (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cabinet_id  integer,
    autor_id    integer,
    mesaj_id    bigint NOT NULL REFERENCES public.raportari_mesaje(id) ON DELETE CASCADE,
    nume_orig   text NOT NULL,
    marime      integer NOT NULL,
    tip         text NOT NULL CHECK (tip IN ('png', 'jpg', 'webp', 'csv', 'xls', 'xlsx', 'zip')),
    cale        text NOT NULL UNIQUE,
    creat_la    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS fisiere_private_mesaj ON public.fisiere_private (mesaj_id);
CREATE INDEX IF NOT EXISTS fisiere_private_cabinet ON public.fisiere_private (cabinet_id);
ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS tip text NOT NULL DEFAULT 'sesizare';
ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS aplicatie text;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'raportari_tip_check' AND connamespace = 'public'::regnamespace) THEN
    ALTER TABLE public.raportari ADD CONSTRAINT raportari_tip_check CHECK (tip IN ('sesizare', 'cerere_import'));
  END IF;
END $$;
"""


def surse_vechi():
    """Directoarele în care pot sta capturile vechi."""
    env = os.environ.get("ICONTA_RAPORTARI_VECHI")
    if env:
        return [d for d in env.split(":") if d]
    from core import mediu_test
    if not mediu_test.motive():
        return []
    return [os.path.join(os.path.dirname(_RAD), "iconta_publicat", "static", "raportari"), os.path.join(_RAD, "static", "raportari")]


def _gaseste(nume, surse):
    for d in surse:
        c = os.path.join(d, nume)
        if os.path.isfile(c):
            return c
    return None


def muta_atasamentele(conn, surse):
    """Copiază atașamentele vechi în depozit, în tranzacția apelantului. Întoarce `(mutate, de_sters)` — `de_sters` = fișierele
    vechi de scos DUPĂ commit (numai cele din afara depozitului git). Ridică `RuntimeError` cu lista celor negăsite / nerecunoscute,
    înainte de a scrie ceva."""
    from core import fisiere_private as fp
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.raportari_atasamente') IS NOT NULL")
        if not cur.fetchone()[0]:
            return 0, []
        cur.execute("SELECT a.id, a.cale, a.nume_orig, m.id, m.autor_id, r.cabinet_id "
                    "  FROM public.raportari_atasamente a "
                    "  JOIN public.raportari_mesaje m ON m.id = a.mesaj_id "
                    "  JOIN public.raportari r ON r.id = m.raportare_id ORDER BY a.id")
        randuri = cur.fetchall()
    gasite, lipsa = [], []
    for aid, cale, nume_orig, mid, autor, cab in randuri:
        sursa = _gaseste(os.path.basename(cale or ""), surse)
        if not sursa:
            lipsa.append("%s (negăsit)" % cale)
            continue
        octeti = open(sursa, "rb").read()
        tip = fp.tip_din_continut(octeti, sursa)
        if tip not in fp.CAPTURI:
            lipsa.append("%s (nu e o captură PNG / JPG / WEBP)" % cale)
            continue
        gasite.append((aid, sursa, nume_orig, mid, autor, cab, tip, len(octeti)))
    if lipsa:
        raise RuntimeError("migrare_fisiere_private: %d atașamente nu se pot muta, nimic scris: %s"
                           % (len(lipsa), "; ".join(lipsa)))
    if not gasite:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE public.raportari_atasamente")
        return 0, []
    rad = fp.director()
    copiate = []
    try:
        with conn.cursor() as cur:
            for aid, sursa, nume_orig, mid, autor, cab, tip, marime in gasite:
                rel = os.path.join(str(cab) if cab is not None else "fara_cabinet", "%s.%s" % (uuid.uuid4().hex, tip))
                dest = os.path.join(rad, rel)
                os.makedirs(os.path.dirname(dest), mode=0o700, exist_ok=True)
                shutil.copyfile(sursa, dest)
                os.chmod(dest, 0o600)
                copiate.append(dest)
                cur.execute("INSERT INTO public.fisiere_private (cabinet_id, autor_id, mesaj_id, nume_orig, marime, tip, cale) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            (cab, autor, mid, (nume_orig or os.path.basename(sursa))[:255], marime, tip, rel))
            cur.execute("DROP TABLE public.raportari_atasamente")
    except Exception:
        for c in copiate:
            os.remove(c)
        raise
    rad_git = os.path.realpath(_RAD) + os.sep
    de_sters = [s for _a, s, *_r in gasite if not os.path.realpath(s).startswith(rad_git)]
    return len(gasite), de_sters


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    return muta_atasamentele(conn, surse_vechi())


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.fisiere_private') IS NOT NULL "
                    "AND to_regclass('public.raportari_atasamente') IS NULL "
                    "AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'raportari' "
                    "            AND column_name = 'tip') "
                    "AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'raportari' "
                    "            AND column_name = 'aplicatie')")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        mutate, de_sters = aplica(conn)
        conn.commit()
        for c in de_sters:
            os.remove(c)
        print("migrare_fisiere_private: %d atașamente mutate în depozit, %d fișiere vechi scoase din directorul publicat; "
              "structura %s" % (mutate, len(de_sters), "există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
