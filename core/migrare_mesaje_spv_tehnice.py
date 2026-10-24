"""
core/migrare_mesaje_spv_tehnice.py — motivele eșecurilor SPV scrise ÎNAINTE de lotul 12, rescrise pe înțelesul contabilului (deficiența 598).

DEFECTUL. Până la lotul 12, eșecul drumului spre ANAF se scria cu textul excepției, iar ecranul îl arată ca atare:
  - `efactura_trimiteri.error_message` / `etransport_trimiteri.error_message` (rândul trimiterii, „vezi mesajul” din detaliul facturii):
    „exceptie upload: HTTPSConnectionPool(host='api.anaf.ro', …): Read timed out.”, „403 fara drept SPV: 403 ANAF: certificatul …”,
    „403 fara drept e-Transport: …”; iar dublura găsită la interogare: „ANAF: ok. ANAF a primit și această încărcare, …”;
  - `public.spv_cui_acoperit.eroare` (ultima citire a CUI-ului: „ANAF a răspuns: …” în Facturi primite, „nedeterminat: …” în Conectare
    SPV): „principalul Principal(kind='firm', id=3) nu are token SPV activ”, „refresh eșuat pentru token 12 — …”, „ANAF n-a răspuns la
    timp (ReadTimeout); citirea se reia la următoarea rulare.”
Codul de acum scrie textul pentru om (`spv_conector.mesaj_pentru_contabil`); rândurile vechi rămâneau cu textul tehnic până la o
trimitere / citire nouă (citirea se reia singură la :17 și :47 numai cât conexiunea e activă).

CE FACE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): rescrie numai textele care au forma veche, recunoscută
după prefixul pe care îl scria codul vechi (`rescrie`, PURĂ); un text al ANAF (răspunsul de validare „nok”, „Nu aveti drept in SPV …”) sau
unul deja nou rămâne neatins. Felul eșecului se citește din textul vechi (rețeaua căzută, conexiunea lipsă, accesul expirat, dreptul
lipsă); restul -> „eroare a aplicației”. Nimic fiscal nu se atinge (starea trimiterii, indexul, facturile rămân). Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_mesaje_spv_tehnice.py`.
"""
import re

import requests

from core import db
from core import spv_conector as _C
from core.efactura_trimitere import MESAJ_NETRIMISA as CE_FACTURA
from core.etransport_send import MESAJ_NETRIMISA as CE_ETRANSPORT
from core.spv_receive import MESAJ_ANAF_FARA_RASPUNS, MESAJ_NECITITE as CE_CITIRE

#: textele pe care le scria codul vechi pe drumul spre ANAF (prefixele lor) — numai acestea se rescriu
_PREFIX_UPLOAD = "exceptie upload: "
_PREFIX_DREPT_EF = "403 fara drept SPV: "
_PREFIX_DREPT_ET = "403 fara drept e-Transport: "
_DUBLURA = re.compile(r"^ANAF: [a-z_]+\. (ANAF a primit și această încărcare.*)$", re.S)
_RETEA = re.compile(r"HTTPSConnectionPool|timed out|Max retries|NewConnectionError|RemoteDisconnected|ConnectionError|ReadTimeout|"
                    r"ConnectTimeout|Connection (refused|reset|aborted)", re.I)
_NECONECTAT = re.compile(r"nu are token SPV activ")
_EXPIRAT = re.compile(r"^refresh eșuat pentru token")
_CITIRE_TACE = re.compile(r"^ANAF n-a răspuns la timp \(\w+\); citirea se reia la următoarea rulare\.$")



def _fel(detaliu):
    """Excepția pe care o arată textul vechi, ca `mesaj_pentru_contabil` să aleagă același text ca acum."""
    if _NECONECTAT.search(detaliu):
        return _C.EroareSpvNeconectat()
    if _EXPIRAT.search(detaliu):
        return _C.EroareSpvRefreshEsuat()
    if _RETEA.search(detaliu):
        return requests.exceptions.ConnectionError()
    return RuntimeError()


def rescrie(text, unde, cif=None):
    """PURĂ. Textul nou pentru un motiv scris de codul vechi, sau None dacă textul nu e unul de-al lui (atunci rămâne cum e).
    `unde`: 'efactura' | 'etransport' (rândul trimiterii) | 'citire' (`spv_cui_acoperit.eroare`)."""
    if not text:
        return None
    if unde in ("efactura", "etransport"):
        ce = CE_FACTURA if unde == "efactura" else CE_ETRANSPORT
        if text.startswith(_PREFIX_DREPT_EF) and unde == "efactura":
            return _C.mesaj_fara_drept(cif, None)
        if text.startswith(_PREFIX_DREPT_ET):
            return _C.mesaj_pentru_contabil(_C.EroareSpvFaraDrept(), ce)
        if text.startswith(_PREFIX_UPLOAD):
            return _C.mesaj_pentru_contabil(_fel(text[len(_PREFIX_UPLOAD):]), ce)
        m = _DUBLURA.match(text)
        return m.group(1) if m else None
    if unde == "citire":
        if _CITIRE_TACE.match(text):
            return MESAJ_ANAF_FARA_RASPUNS
        if _NECONECTAT.search(text) or _EXPIRAT.search(text) or text.startswith(("principalul ", "token ", "HTTP ")):
            return _C.mesaj_pentru_contabil(_fel(text), CE_CITIRE)
        return None
    raise ValueError("loc necunoscut: %r" % (unde,))


def aplica_firma(conn, schema):
    """Rândurile trimiterilor unei firme. Întoarce câte s-au rescris."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    n = 0
    with conn.cursor() as cur:
        cur.execute('SELECT cui FROM "%s".firma_profil WHERE id = 1' % schema)
        r = cur.fetchone()
        cif = "".join(c for c in str((r or [None])[0] or "") if c.isdigit()) or None
        for tabel, unde in (("efactura_trimiteri", "efactura"), ("etransport_trimiteri", "etransport")):
            cur.execute("SELECT to_regclass(%s)", ('"%s".%s' % (schema, tabel),))
            if cur.fetchone()[0] is None:
                continue
            cur.execute('SELECT id, error_message FROM "%s".%s WHERE error_message IS NOT NULL' % (schema, tabel))
            for tid, text in cur.fetchall():
                nou = rescrie(text, unde, cif)
                if nou and nou != text:
                    cur.execute('UPDATE "%s".%s SET error_message = %%s WHERE id = %%s' % (schema, tabel), (nou, tid))
                    n += 1
    return n


def aplica_citiri(conn):
    """`public.spv_cui_acoperit.eroare`. Întoarce câte s-au rescris."""
    n = 0
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.spv_cui_acoperit')")
        if cur.fetchone()[0] is None:
            return 0
        cur.execute("SELECT token_id, cui, eroare FROM public.spv_cui_acoperit WHERE eroare IS NOT NULL")
        for token_id, cui, text in cur.fetchall():
            nou = rescrie(text, "citire")
            if nou and nou != text:
                cur.execute("UPDATE public.spv_cui_acoperit SET eroare = %s WHERE token_id = %s AND cui = %s", (nou, token_id, cui))
                n += 1
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, total = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                total += aplica_firma(conn, s)
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    with db.get_conn() as conn:
        citiri = aplica_citiri(conn)
        conn.commit()
    print("migrare_mesaje_spv_tehnice: %d firme ok, %d eșec, %d motive de trimitere rescrise, %d motive de citire rescrise"
          % (ok, len(esec), total, citiri))
    for s, e in esec:
        print("  EȘEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
