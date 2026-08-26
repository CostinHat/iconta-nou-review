"""
core/migrare_portal.py — R62: schimbarea adresei se confirmă, iar cabinetul vede ce s-a întâmplat.

Sursa UNICĂ a DDL-ului (mirror în `infra/bootstrap_public.sql`). Idempotent:
`CREATE TABLE IF NOT EXISTS`. Amândouă tabelele stau în `public`, nu per-tenant, fiindcă
`users` e în `public`: identitatea unui om nu e a unei firme.

Rulare: `python3 -m core.migrare_portal`.

DE CE, cu instanța. Măsurat 26.08.2026, la verificarea lotului 7:

  `PUT /portal/acces-cont/email` făcea `UPDATE public.users SET email=%s` **imediat**. Fără
  confirmare pe adresa nouă, fără notificare pe cea veche, fără nicio urmă de la ce la ce. Iar
  adresa aia **este** identitatea de autentificare — intrarea se face prin magic-link pe email.
  Cine avea o sesiune deschisă muta contul, definitiv, dintr-un singur câmp.

  `POST /portal/acces-cont/acces` crea un utilizator **sub cabinet** (`accounting_firm_id` luat
  din `tenants`) fără ca acesta să afle: niciun rând de audit, nicio notificare. Singurul email
  pleca la cel invitat.

Decizia lui Costin, în ordinea pe care a cerut-o: **(2)** izolarea între cabinete întâi — un cont
de client dezactivat al **altui** cabinet se refuză, fiindcă e singura cale prin care date ale
unui cabinet ajung la altul, și aia nu e o chestiune de urmă, e **P12**; **(1)** apoi confirmarea
— *„clientul trebuie să-și poată schimba adresa, dar nu instant"*; **(3)** apoi urma.

CE PĂSTREAZĂ `schimbari_email`, și de ce exact câmpurile astea:
  email_vechi   — fără el, urma n-ar putea spune *de la ce*, iar aia e jumătatea care lipsea.
  email_nou     — ce se aplică la confirmare. Se confruntă din nou cu `users` la confirmare:
                  între cerere și confirmare, altcineva poate lua adresa.
  token_hash    — DOAR hash-ul, ca la magic-link (`token_hash_v1`): un dump nu permite preluarea.
  expira        — 48 de ore, ca la celelalte tokene.
  confirmat_la  — `NULL` cât timp e în așteptare. Nu se șterge rândul la confirmare: cererea
                  însăși e parte din urmă, chiar dacă n-a fost dusă până la capăt.

CE PĂSTREAZĂ `urme_portal`: `actiune` dintr-o listă închisă **în bază** (o urmă cu o acțiune
inventată n-ar putea fi citită de nimeni), `detaliu` neputând fi gol — *o urmă care nu spune nimic
nu e o urmă* — `autor_id`, `creat_la`. Append-only, ca orice urmă (P16).

CE NU FACE, declarat: nu rezolvă divergența dintre `users.email` (autentificare) și
`firma_profil.patron_email` (unde pleacă pachetul lunar). Aia e o constatare proprie, deschisă
separat — două identități ale aceleiași persoane, care se pot desincroniza fără ca nimeni să afle.
"""
import sys

DDL = """
CREATE TABLE IF NOT EXISTS public.schimbari_email (
    id             serial PRIMARY KEY,
    user_id        integer NOT NULL,
    tenant_id      integer NOT NULL,
    email_vechi    text NOT NULL,
    email_nou      text NOT NULL,
    token_hash     text NOT NULL,
    expira         timestamp with time zone NOT NULL,
    cerut_la       timestamp with time zone DEFAULT now() NOT NULL,
    confirmat_la   timestamp with time zone,
    CONSTRAINT schimbari_email_alta_adresa
        CHECK (lower(btrim(email_nou)) <> lower(btrim(email_vechi)))
);

CREATE INDEX IF NOT EXISTS schimbari_email_token_idx
    ON public.schimbari_email (token_hash);

CREATE TABLE IF NOT EXISTS public.urme_portal (
    id          serial PRIMARY KEY,
    tenant_id   integer NOT NULL,
    actiune     text NOT NULL,
    detaliu     text NOT NULL,
    autor_id    integer,
    creat_la    timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT urme_portal_actiune_cunoscuta
        CHECK (actiune IN ('email_cerut', 'email_confirmat', 'acces_dat', 'acces_retras')),
    CONSTRAINT urme_portal_detaliu_nevid
        CHECK (btrim(detaliu) <> '')
);

CREATE INDEX IF NOT EXISTS urme_portal_tenant_idx
    ON public.urme_portal (tenant_id, creat_la DESC);
"""


def aplica(conn):
    """Creează cele două tabele din `public`. Idempotent."""
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()


def main():
    sys.path.insert(0, "/home/costin/iconta_nou")
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.schimbari_email'), "
                        "to_regclass('public.urme_portal')")
            a, b = cur.fetchone()
    print("schimbari_email: %s · urme_portal: %s" % (a, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
