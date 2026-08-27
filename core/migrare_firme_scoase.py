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
  urme_pastrate   — urmele portalului (`urme_portal` + `schimbari_email`) ale firmei, copiate
                    la scoatere. **Numai pe `scoatere_firma`, NU pe `gdpr_cabinet`** — vezi mai jos.

CE NU E AICI, declarat: **nicio dată personală** din firmă (nici sold, nici salariat, nici
partener). Urma spune *că s-a șters* și *ce s-a șters ca volum*, nu *ce conținea*.

**SINGURA EXCEPȚIE, și de-aia e condiționată de `motiv`: `urme_pastrate`.** Urmele portalului
conțin adrese de email — deci date personale. Se copiază **numai** când firma e scoasă din
portofoliu de către cabinet (`scoatere_firma`), unde ele sunt evidența cabinetului despre cine a
primit acces la datele lui. La o ștergere **GDPR** (`gdpr_cabinet`) **nu se copiază nimic**: acolo
scopul actului e chiar dispariția datelor, iar un log care le păstrează ar anula ștergerea.
Aceeași regulă ca la `gdpr_stergeri`, dusă un pas mai departe: *logul unei ștergeri GDPR n-are voie
să reintroducă ce s-a șters.*

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
    schema_name     text        NOT NULL,   -- [G3, 28.08.2026] INFORMATIV. NUMELE SE RECICLEAZA:
        -- `urmator_schema_name` ia max(NNN)+1 peste firmele VII, deci cand cea mai mare e stearsa,
        -- numarul se refoloseste. Masurat 27.08.2026: doua randuri din trei poarta 'tenant_019',
        -- pentru doua firme diferite, iar 'tenant_018' e acum schema unei firme VII.
        -- NICIO CITIRE NU SE CHEIAZA PE COLOANA ASTA. Randul ramane dezambiguizat de `tenant_id`,
        -- care vine dintr-o secventa si nu se recicleaza niciodata; celelalte 14 coloane de
        -- legatura din `public` sunt tot `tenant_id integer`. O interogare cheiata pe `schema_name`
        -- ar intoarce randul gresit FARA nicio eroare -> gard:
        -- core/test_tenant_stergere.py::test_nicio_citire_nu_se_cheiaza_pe_NUMELE_schemei
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

-- [27.08.2026] Urmele portalului supravietuiesc scoaterii firmei. Cerut de Costin inainte de
-- prima apasare: "sunt singura dovada ca traseul R62 a fost parcurs pe date. Registrul spune ce
-- am facut; alea arata ce a inregistrat aplicatia."
ALTER TABLE public.firme_scoase ADD COLUMN IF NOT EXISTS urme_pastrate jsonb;
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
