# -*- coding: utf-8 -*-
"""core/migrare_ciorne_proprii.py — asistentul nu modifică, nu șterge și nu trimite la validare ciorna ALTUI utilizator (deficiența 246,
comanda Costin 14.10.2026, verbatim în DECIZII „Lotul 3”: „Un asistent nu modifică, nu șterge și nu trimite la validare notele altui
utilizator; le poate doar vedea. Verifică aceeași regulă pe toate ecranele cu documente-ciornă.”).

DE CE ÎN BAZĂ, ca regulile de fond (`core/migrare_reguli_fond.py`): o ciornă a altuia se poate schimba pe ~12 drumuri — editarea și
ștergerea din jurnal, ștergerea operațiunii de casă (cu nota ei), recontabilizarea facturii, refacerea NIR-ului, descărcarea stocului,
înlocuirea notei statului de plată, cota chitanței, raportul Z „fără marfă”, propunerea notei de închidere, legarea de factură
(căutate cu `grep` pe „inregistrari SET” și „DELETE FROM … inregistrari”, plus harta din DECIZII). O regulă în fiecare use-case ar rata drumul de
mâine; triggerul le prinde pe toate, ca `REGULA_CONTABILA:`. Trimiterea la validare nu atinge nota (scrie în coadă), deci o verifică
`coada_api.retrimite_nota` cu ACEEAȘI funcție, iar jurnalul o folosește ca să nu mai arate butoanele (aceeași regulă ca refuzul).

REGULA (o singură definiție, `ciorna_altui(autor, utilizator)`): dacă utilizatorul cererii (`iconta.utilizator`, scris de `db.get_conn`
în cererile de modificare) are rolul `angajat` (asistent) și nota NEVALIDATĂ are alt autor (`creat_de_id`) -> refuz `DREPT_CIORNA:`
(handlerul global din `main.py` îl dă ca 403, cu textul). Trec: administratorul cabinetului și superadminul (rol), autorul însuși, nota
fără autor (scrisă în afara unei cereri — import, cron), nota validată (o păzește R1), și DECIZIA VALIDATORULUI: o schimbare a stării
făcută de un asistent cu „Poate valida” (validarea e treaba lui; `jurnal_api.valideaza` scrie numai starea). *INTERPRETARE:* „asistent”
= orice cont `angajat`, cu sau fără „Poate valida” — textul deciziei spune „un asistent”, fără excepție pentru senior; de reconfirmat.
Pe `rip_operatiuni` (registrul de încasări și plăți, autorul în `creat_de`) aceeași regulă.

[deficiența 258, 15.10.2026] Refuzul numește nota cum o vede contabilul („Nota nr. crt. 5 din 12.03.2026”, `eticheta_nota`), nu id-ul
intern („Nota #24”): o SINGURĂ definiție a etichetei, aici, folosită și de triggerele din `core/migrare_reguli_fond.py` (plpgsql o
rezolvă la rulare) și de mesajele din Python (`core/eticheta_nota.py`). Operațiunea RIP: „plata din ZZ.LL.AAAA de 150,00 RON”.

Idempotentă (CREATE OR REPLACE + DROP/CREATE TRIGGER). Oglinda din `tenant_template.sql` e generată de `sql(...)` și păzită de
`core/test_ciorne_proprii.py`. Rulare: `python -m core.migrari_registru ruleaza --productie core/migrare_ciorne_proprii.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [ciorne_proprii_v1, 15.10.2026] ciorna altui utilizator (deficiența 246) — SURSA: core/migrare_ciorne_proprii.py"
MARCAJ_SFARSIT = "-- [ciorne_proprii_v1] sfârșit"


def sql(s):
    """DDL-ul regulii pentru schema `s` (numele exact, sau `TENANT_PLACEHOLDER` pentru șablon)."""
    return """@INC@
CREATE OR REPLACE FUNCTION @S@.eticheta_nota(nid integer) RETURNS text AS $$
  -- [deficiența 258] numele notei cum îl vede contabilul în Registrul jurnal: „nr. crt. N din ZZ.LL.AAAA”. [deficiența 302, 17.10.2026]
  -- N = `registru_jurnal_numere.nr_curent`, dat la validare și neschimbat după (core/migrare_nr_curent_note.py); nota nevalidată n-are număr: „din ZZ.LL.AAAA”
  -- („Nota din 07.10.2026 e ciorna lui …”; starea o spune fraza în care stă eticheta). NULL dacă nota nu există. Python o cheamă prin `core/eticheta_nota.py`, ca textul din
  -- bază și cel din aplicație să fie unul (paritatea cu Registrul jurnal: core/test_eticheta_nota.py).
  SELECT CASE WHEN r.nr_curent IS NOT NULL THEN 'nr. crt. ' || r.nr_curent || ' din ' || to_char(n.data, 'DD.MM.YYYY')
              ELSE 'din ' || to_char(n.data, 'DD.MM.YYYY') END
    FROM @S@.inregistrari n LEFT JOIN @S@.registru_jurnal_numere r ON r.inregistrare_id = n.id WHERE n.id = nid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.eticheta_rip(oid integer) RETURNS text AS $$
  -- [deficiența 258] operațiunea din registrul de încasări și plăți cum o arată rândul ei: „plata din ZZ.LL.AAAA de 1.234,50 RON”
  SELECT CASE WHEN r.tip = 'plata' THEN 'plata' ELSE 'încasarea' END || ' din ' || to_char(r.data_operatiune, 'DD.MM.YYYY') || ' de '
         || translate(to_char(r.suma, 'FM999,999,999,990.00'), ',.', '.,') || ' ' || r.valuta
    FROM @S@.rip_operatiuni r WHERE r.id = oid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.ciorna_altui(autor integer, utilizator integer) RETURNS text AS $$
  -- numele autorului dacă `utilizator` e asistent (`angajat`) și ciorna e a ALTUI utilizator; NULL altfel (fără autor, fără utilizator,
  -- autorul însuși, administratorul / superadminul)
  SELECT COALESCE(NULLIF(btrim(concat_ws(' ', a.prenume, a.nume)), ''), a.email)
    FROM public.users u JOIN public.users a ON a.id = autor
   WHERE u.id = utilizator AND u.rol = 'angajat' AND autor <> utilizator
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.utilizatorul_cererii() RETURNS integer AS $$
  SELECT NULLIF(current_setting('iconta.utilizator', true), '')::integer
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.decizia_validatorului() RETURNS boolean AS $$
  SELECT COALESCE((SELECT poate_valida FROM public.users WHERE id = @S@.utilizatorul_cererii()), false)
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION @S@.regula_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  autor text;
BEGIN
  IF OLD.status = 'validata' THEN
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
  END IF;
  autor := @S@.ciorna_altui(OLD.creat_de_id, @S@.utilizatorul_cererii());
  IF autor IS NOT NULL AND NOT (TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status AND @S@.decizia_validatorului())
     AND (TG_OP = 'DELETE' OR (NEW.data, NEW.numar, NEW.factura_id, NEW.document_ref, NEW.descriere, NEW.sursa, NEW.status)
                              IS DISTINCT FROM (OLD.data, OLD.numar, OLD.factura_id, OLD.document_ref, OLD.descriere, OLD.sursa, OLD.status)) THEN
    RAISE EXCEPTION 'DREPT_CIORNA: Nota % e ciorna lui %: o poți vedea, dar n-o modifici, n-o ștergi și n-o trimiți la validare. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', @S@.eticheta_nota(OLD.id), autor, autor;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_ciorna_proprie ON @S@.inregistrari;
CREATE TRIGGER trg_regula_ciorna_proprie BEFORE UPDATE OR DELETE ON @S@.inregistrari
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_ciorna_proprie();

CREATE OR REPLACE FUNCTION @S@.regula_linii_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  nid integer; st text; aut integer; autor text;
BEGIN
  FOREACH nid IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.inregistrare_id END,
                            CASE WHEN TG_OP <> 'DELETE' THEN NEW.inregistrare_id END] LOOP
    CONTINUE WHEN nid IS NULL;
    SELECT status, creat_de_id INTO st, aut FROM @S@.inregistrari WHERE id = nid;
    CONTINUE WHEN st IS NULL OR st = 'validata';
    autor := @S@.ciorna_altui(aut, @S@.utilizatorul_cererii());
    IF autor IS NOT NULL THEN
      RAISE EXCEPTION 'DREPT_CIORNA: Nota % e ciorna lui %: o poți vedea, dar n-o modifici, n-o ștergi și n-o trimiți la validare. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', @S@.eticheta_nota(nid), autor, autor;
    END IF;
  END LOOP;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_linii_ciorna_proprie ON @S@.inregistrari_linii;
CREATE TRIGGER trg_regula_linii_ciorna_proprie BEFORE INSERT OR UPDATE OR DELETE ON @S@.inregistrari_linii
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_linii_ciorna_proprie();

CREATE OR REPLACE FUNCTION @S@.regula_rip_ciorna_proprie() RETURNS trigger AS $$
DECLARE
  autor text;
BEGIN
  IF OLD.status = 'validata' THEN
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
  END IF;
  autor := @S@.ciorna_altui(OLD.creat_de, @S@.utilizatorul_cererii());
  IF autor IS NOT NULL AND NOT (TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status AND @S@.decizia_validatorului()) THEN
    RAISE EXCEPTION 'DREPT_CIORNA: În registrul de încasări și plăți, % e ciorna lui %: o poți vedea, dar n-o modifici și n-o ștergi. Dacă trebuie schimbată, spune-i lui % sau administratorului cabinetului.', @S@.eticheta_rip(OLD.id), autor, autor;
  END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_regula_rip_ciorna_proprie ON @S@.rip_operatiuni;
CREATE TRIGGER trg_regula_rip_ciorna_proprie BEFORE UPDATE OR DELETE ON @S@.rip_operatiuni
  FOR EACH ROW EXECUTE FUNCTION @S@.regula_rip_ciorna_proprie();
@SF@""".replace("@INC@", MARCAJ_INCEPUT).replace("@SF@", MARCAJ_SFARSIT).replace("@S@", s)


def aplica(conn, schema):
    """True dacă a aplicat; None dacă schema n-are tabelele (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name IN "
                    "('inregistrari', 'inregistrari_linii', 'rip_operatiuni')", (schema,))
        if cur.fetchone()[0] < 3:
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
    print("ciornele proprii: aplicate pe %d / %d scheme" % (n, len(scheme)))


if __name__ == "__main__":
    _main()
