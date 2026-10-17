"""
core/migrare_canal_notificari.py — telefonul și canalul de notificare al fiecărui utilizator; codul de confirmare; jurnalul notificărilor.

Comanda Costin 17.10.2026, lotul 7 pct.2.1–2.2 (verbatim în DECIZII „Lotul 6 închis”): „Notificări WhatsApp [...]: mesaj scurt, fără
conținut fiscal, cu link în aplicație. Emailul rămâne pentru confirmarea contului, resetarea parolei, linkul de logare și ca rezervă când
WhatsApp nu livrează.” și „în Setări cont, fiecare utilizator își pune numărul și alege WhatsApp sau email (implicit email). WhatsApp se
activează numai după confirmarea numărului printr-un cod trimis pe WhatsApp și bifa de acord pentru mesaje.”

- `public.users`: `telefon` (forma internațională, +40…), `telefon_confirmat_la` (NULL = neconfirmat; se golește la schimbarea numărului),
  `canal_notificari` ('email' | 'whatsapp', implicit 'email'), `acord_whatsapp_la` (momentul bifei de acord; NULL = fără acord).
  CHECK: canalul 'whatsapp' cere numărul confirmat și acordul — o scriere care le-ar ocoli e refuzată de bază.
- `public.telefon_coduri`: codul de confirmare în curs, unul pe utilizator (hash, expirare, încercări) — codul în clar nu se păstrează.
- `public.notificari.de_livrat`: cutia de ieșire a clopoțelului (scrisă de `notificari_api.adauga`, golită de livrare).
- `public.notificari_jurnal`: fiecare notificare trimisă (tipul, canalul, id-ul mesajului WhatsApp, starea raportată de Meta, rezerva pe
  email) — din el webhook-ul află ce notificare n-a fost livrată și o trimite pe email.
Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_canal_notificari.py`.
"""
from core import db

DDL = """
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS telefon text;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS telefon_confirmat_la timestamptz;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS canal_notificari text NOT NULL DEFAULT 'email';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS acord_whatsapp_la timestamptz;
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_canal_notificari_check;
ALTER TABLE public.users ADD CONSTRAINT users_canal_notificari_check CHECK (
    canal_notificari = 'email'
    OR (canal_notificari = 'whatsapp' AND telefon IS NOT NULL AND telefon_confirmat_la IS NOT NULL AND acord_whatsapp_la IS NOT NULL));
ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_telefon_forma_check;
ALTER TABLE public.users ADD CONSTRAINT users_telefon_forma_check CHECK (telefon IS NULL OR telefon ~ '^\\+[1-9][0-9]{7,14}$');

-- telefonul opțional din formularul de înregistrare liberă, purtat de cerere până la confirmarea emailului (atunci trece pe utilizator)
ALTER TABLE public.inregistrari_in_asteptare ADD COLUMN IF NOT EXISTS telefon text;

CREATE TABLE IF NOT EXISTS public.telefon_coduri (
    user_id integer PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    telefon text NOT NULL,
    cod_hash text NOT NULL,
    expira_la timestamptz NOT NULL,
    incercari integer NOT NULL DEFAULT 0,
    creat_la timestamptz NOT NULL DEFAULT now()
);

-- cutia de ieșire: o notificare de clopoțel scrisă de acum încolo pleacă și pe canalul omului (`core/notificari.py`); rândurile de dinainte
-- primesc valoarea implicită (false) și nu pleacă retroactiv
ALTER TABLE public.notificari ADD COLUMN IF NOT EXISTS de_livrat boolean NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS notificari_de_livrat_idx ON public.notificari (id) WHERE de_livrat;

CREATE TABLE IF NOT EXISTS public.notificari_jurnal (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    notificare_id integer REFERENCES public.notificari(id) ON DELETE SET NULL,
    user_id integer REFERENCES public.users(id) ON DELETE SET NULL,
    tip text NOT NULL,
    canal text NOT NULL CHECK (canal IN ('email', 'whatsapp')),
    link text,
    mesaj_id text,
    stare text NOT NULL CHECK (stare IN ('trimis', 'livrat', 'citit', 'esuat', 'netrimis')),
    rezerva_email boolean NOT NULL DEFAULT false,
    detaliu text,
    creat_la timestamptz NOT NULL DEFAULT now(),
    actualizat_la timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS notificari_jurnal_mesaj_uq ON public.notificari_jurnal (mesaj_id) WHERE mesaj_id IS NOT NULL;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 4 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' "
                    "AND column_name IN ('telefon', 'telefon_confirmat_la', 'canal_notificari', 'acord_whatsapp_la')")
        coloane = bool(cur.fetchone()[0])
        cur.execute("SELECT to_regclass('public.telefon_coduri') IS NOT NULL AND to_regclass('public.notificari_jurnal') IS NOT NULL "
                    "AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'notificari' "
                    "AND column_name = 'de_livrat')")
        return coloane and bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_canal_notificari: %s" % ("aplicată" if verifica(conn) else "INCOMPLETĂ"))


if __name__ == "__main__":
    _main()
