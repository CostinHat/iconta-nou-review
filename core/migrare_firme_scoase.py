# -*- coding: utf-8 -*-
"""
core/migrare_firme_scoase.py — R72: urma unei firme scoase din portofoliu.

Sursa UNICĂ a DDL-ului (mirror în `infra/bootstrap_public.sql`). Idempotent:
`CREATE TABLE IF NOT EXISTS`. Rulare: `python3 -m core.migrare_firme_scoase`.

DE CE EXISTĂ. Ștergerea unei firme îi ia toate cele 13 tabele din `public`, inclusiv
`audit_log`. Deci urma nu poate sta în audit: ar fi ștearsă chiar de actul pe care îl
consemnează. Aceeași formă ca `gdpr_stergeri` pentru cabinet — *logul supraviețuiește*.

CE PĂSTREAZĂ, și de ce exact câmpurile astea:
  tenant_id       — id-ul firmei dispărute. **Deliberat FĂRĂ cheie străină**: ținta nu mai
                    există în momentul în care rândul devine util.
  nume, cui       — fără ele, urma n-ar putea spune CARE firmă. Iar `cui` e cel care
                    deosebește: instanța care a produs restanța sunt două firme cu ACELAȘI
                    nume și CUI-uri diferite.
  schema_name     — ce schemă a fost aruncată. Un `DROP SCHEMA` nu lasă altă dovadă.
  cabinet_id      — al cui portofoliu s-a schimbat.
  motiv           — `scoatere_firma` sau `gdpr_cabinet`. Cele două căi sunt aceeași funcție;
                    fără câmpul ăsta n-ai putea spune care dintre ele a rulat.
  randuri_sterse  — jsonb, câte rânduri au ieșit din fiecare tabelă. E singura măsurătoare
                    care se poate face DUPĂ ștergere; fără ea, „am curățat tot" e o afirmație
                    fără cifră.
  scos_de_user_id — cine. Fără FK din același motiv ca `tenant_id`: la GDPR dispare și userul.
  scos_la         — când.

CE NU E AICI, declarat: **nicio dată personală** din firmă (nici sold, nici salariat, nici
partener). Urma spune *că s-a șters* și *ce s-a șters ca volum*, nu *ce conținea*. Aceeași
regulă ca la `gdpr_stergeri`: logul unei ștergeri GDPR n-are voie să reintroducă ce s-a șters.

TABELA ASTA NU SE ȘTERGE ODATĂ CU FIRMA, deși poartă `tenant_id` — e declarată în
`tenant_stergere.NU_SE_STERG` cu motivul, iar garda din `core/test_tenant_stergere.py`
verifică declarația. O urmă ștearsă de propriul act nu e o urmă.
"""
import sys

DDL = """
CREATE TABLE IF NOT EXISTS public.firme_scoase (
    id              bigserial PRIMARY KEY,
    tenant_id       integer     NOT NULL,
    nume            text        NOT NULL,
    cui             text,
    schema_name     text        NOT NULL,
    cabinet_id      integer,
    motiv           text        NOT NULL,
    randuri_sterse  jsonb,
    scos_de_user_id integer,
    scos_la         timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT firme_scoase_motiv_ck
        CHECK (motiv IN ('scoatere_firma', 'gdpr_cabinet')),
    CONSTRAINT firme_scoase_nume_nevid_ck
        CHECK (btrim(nume) <> '')
);
CREATE INDEX IF NOT EXISTS idx_firme_scoase_cabinet ON public.firme_scoase (cabinet_id, scos_la DESC);
CREATE INDEX IF NOT EXISTS idx_firme_scoase_tenant  ON public.firme_scoase (tenant_id);
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    return True


def main():
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    print("firme_scoase: gata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
