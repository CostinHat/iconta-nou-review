# -*- coding: utf-8 -*-
"""core/migrare_nr_curent_note.py — „Nr. crt.” al notei contabile se dă la validare și nu se mai schimbă (deficiența 302, comanda Costin
17.10.2026 7.2 pct.5, verbatim în DECIZII: „302: confirmă cum se dă «Nr. crt.» și dacă numărul unei note validate se poate schimba; dacă
da, repară astfel încât să nu se mai schimbe.”).

Ce era: numărul nu era păstrat nicăieri. Se calcula la fiecare citire — locul notei în anul ei după (data, id), ORICE stare
(`repo_contabilitate.jurnal_pe_an`, `eticheta_nota`, `repo_control_incrucisat`). O notă nouă cu o dată mai veche (sau o ciornă ștearsă)
muta numărul tuturor notelor de după ea, validate sau nu: „nr. crt. 25” spus într-un mesaj despre ciorna F1A5 (17.10) a devenit numărul
încasării bancare din 16.10, introdusă după.

Ce e acum, în baza fiecărei firme:
- `registru_jurnal_numere` (inregistrare_id, an, nr_curent) — numărul din Registrul-jurnal, în anul notei. Îl primește NOTA VALIDATĂ, în
  momentul validării (sau la scrierea ei direct validată): următorul număr al anului, sub un lacăt pe (schemă, an), deci două validări
  simultane nu iau același număr. Tabelă proprie, nu o coloană a notei: o migrare nu scrie în note (`core/test_migrari_registru.py`), iar
  numărul e al registrului, nu conținutul notei; nota ștearsă (numai ciorna, sau în tranzacția care a creat-o) își ia numărul cu ea.
  Registrul-jurnal cuprinde înregistrările din evidență, în ordinea în care intră în ea (OMFP 2634/2015, Registrul-jurnal cod 14-1-1:
  „numărul curent al operațiunilor înregistrate”); ciorna nu e încă înregistrată, deci n-are număr — se numește „ciorna din ZZ.LL.AAAA”.
- odată dat, numărul nu se mai schimbă: o scriere care l-ar schimba e refuzată (`REGULA_CONTABILA`), iar unicitatea pe (an, număr) face
  imposibilă o dublă.
- la migrare, fiecare notă validată își păstrează numărul pe care îl arată azi (locul ei de acum în an, orice stare): niciun număr deja
  văzut pe o notă validată nu se schimbă. Numerele de acum ale ciornelor dispar (ciornele n-au număr); la validare primesc următorul număr.

Ordinea: înaintea lui `core/migrare_ciorne_proprii.py` (`eticheta_nota` citește tabela) — declarată în `core.migrari_registru.DUPA`. Oglinda din `tenant_template.sql` e generată de
`sql(...)` și păzită de `core/test_302_nr_curent.py`. Idempotentă. Rulare:
`python -m core.migrari_registru ruleaza --productie core/migrare_nr_curent_note.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [nr_curent_v1, 17.10.2026] numărul notei dat la validare (deficiența 302) — SURSA: core/migrare_nr_curent_note.py"
MARCAJ_SFARSIT = "-- [nr_curent_v1] sfârșit"


def sql(s):
    """DDL-ul pentru schema `s` (numele exact, sau `TENANT_PLACEHOLDER` pentru șablon)."""
    return """@INC@
CREATE TABLE IF NOT EXISTS @S@.registru_jurnal_numere (
    inregistrare_id integer PRIMARY KEY REFERENCES @S@.inregistrari(id) ON DELETE CASCADE,
    an integer NOT NULL,
    nr_curent integer NOT NULL,
    dat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registru_jurnal_numere_unic UNIQUE (an, nr_curent)
);
INSERT INTO @S@.registru_jurnal_numere (inregistrare_id, an, nr_curent)
SELECT x.id, x.an, x.rn
  FROM (SELECT id, status, EXTRACT(YEAR FROM data)::int AS an,
               ROW_NUMBER() OVER (PARTITION BY date_trunc('year', data) ORDER BY data, id) AS rn FROM @S@.inregistrari) x
 WHERE x.status = 'validata' AND NOT EXISTS (SELECT 1 FROM @S@.registru_jurnal_numere);

CREATE OR REPLACE FUNCTION @S@.nr_curent_la_validare() RETURNS trigger AS $$
DECLARE
  an_nota integer := EXTRACT(YEAR FROM NEW.data)::int;
BEGIN
  IF NEW.status = 'validata' AND NOT EXISTS (SELECT 1 FROM @S@.registru_jurnal_numere WHERE inregistrare_id = NEW.id) THEN
    PERFORM pg_advisory_xact_lock(hashtext('nr_curent:' || TG_TABLE_SCHEMA || ':' || an_nota::text));
    INSERT INTO @S@.registru_jurnal_numere (inregistrare_id, an, nr_curent)
    SELECT NEW.id, an_nota, COALESCE(MAX(nr_curent), 0) + 1 FROM @S@.registru_jurnal_numere WHERE an = an_nota;
  END IF;
  RETURN NULL;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_nr_curent_la_validare ON @S@.inregistrari;
CREATE TRIGGER trg_nr_curent_la_validare AFTER INSERT OR UPDATE OF status ON @S@.inregistrari
  FOR EACH ROW EXECUTE FUNCTION @S@.nr_curent_la_validare();

CREATE OR REPLACE FUNCTION @S@.nr_curent_neschimbat() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'REGULA_CONTABILA: Nota nr. crt. % din % e în Registrul-jurnal: numărul ei nu se mai schimbă.', OLD.nr_curent, OLD.an;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_nr_curent_neschimbat ON @S@.registru_jurnal_numere;
CREATE TRIGGER trg_nr_curent_neschimbat BEFORE UPDATE ON @S@.registru_jurnal_numere
  FOR EACH ROW EXECUTE FUNCTION @S@.nr_curent_neschimbat();
@SF@""".replace("@INC@", MARCAJ_INCEPUT).replace("@SF@", MARCAJ_SFARSIT).replace("@S@", s)


def aplica(conn, schema):
    """True dacă a aplicat; None dacă schema n-are tabela notelor (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = 'inregistrari'", (schema,))
        if cur.fetchone()[0] < 1:
            return None
        cur.execute(sql('"%s"' % schema))
    return True


def _main():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    n = 0
    for s in scheme:
        with db.get_conn() as conn:
            if aplica(conn, s):
                n += 1
            conn.commit()
    print("nr. crt. la validare: aplicat pe %d / %d scheme" % (n, len(scheme)))


if __name__ == "__main__":
    _main()
