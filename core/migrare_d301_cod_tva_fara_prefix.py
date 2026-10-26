"""
core/migrare_d301_cod_tva_fara_prefix.py — codul de TVA al furnizorului în operațiunile D301, fără prefixul țării (lotul 13, deficiența 539).

DEFECTUL. `d301_operatiuni` ține țara furnizorului (`partener_tara`) și codul lui de TVA (`partener_cod`), codul FĂRĂ prefix (ecranul D301 o
spunea: „fără prefix țară”). Achiziția intracomunitară (`uc_tenants`, factura + operațiunea D301 legată de ea) scria însă codul întreg,
cu prefix, iar ecranul D301 lipea țara de cod: la F3, achiziția IE-100 de la IE6388047V apărea „IEIE6388047V”; prin D390 (operațiunile D301
nelegate de o factură devin rânduri D390 cu `codO` = codul) codul cu prefix ar fi ajuns dublat și acolo. Reparat în cod: codul se
normalizează o singură dată, la scriere (`d301_operatiuni_api.cod_tva_fara_prefix`, chemat de ecranul D301 și de achiziția
intracomunitară).

DATELE EXISTENTE: fiecare rând al cărui cod începe cu prefixul țării lui (Grecia: EL / GR) primește codul fără prefix — aceeași funcție ca
la scriere. Nimic altceva (sumele, tipul, factura legată). Tabela e creată la prima operațiune D301 (`d301.py`): firma fără ea se sare.
Idempotentă (un cod fără prefix rămâne neschimbat).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_d301_cod_tva_fara_prefix.py`.
"""
from core import db


def _are_tabela(cur, schema):
    cur.execute("SELECT to_regclass(%s)", ('"%s".d301_operatiuni' % schema,))
    return cur.fetchone()[0] is not None


def de_corectat(conn, schema):
    """[(id, cod_vechi, cod_nou)] — rândurile cu prefixul țării în cod."""
    from core.d301_operatiuni_api import cod_tva_fara_prefix
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        if not _are_tabela(cur, schema):
            return []
        cur.execute('SELECT id, partener_tara, partener_cod FROM "%s".d301_operatiuni WHERE COALESCE(partener_cod, \'\') <> \'\' ORDER BY id'
                    % schema)
        out = []
        for oid, tara, cod in cur.fetchall():
            nou = cod_tva_fara_prefix(tara, cod)
            if nou != cod:
                out.append((oid, cod, nou))
        return out


def aplica(conn, schema):
    """Câte rânduri s-au corectat."""
    rand = de_corectat(conn, schema)
    with conn.cursor() as cur:
        for oid, _vechi, nou in rand:
            cur.execute('UPDATE "%s".d301_operatiuni SET partener_cod = %%s WHERE id = %%s' % schema, (nou, oid))
    return len(rand)


def verifica(conn, schema):
    return not de_corectat(conn, schema)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    total, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                total += aplica(conn, s)
                conn.commit()
        except Exception as e:  # noqa: BLE001 — firma care cade se numește, celelalte merg mai departe
            esec.append((s, str(e)))
    print("migrare_d301_cod_tva_fara_prefix: %d coduri corectate, %d firme cu eșec" % (total, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
