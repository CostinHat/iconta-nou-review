# -*- coding: utf-8 -*-
"""core/note_derivate.py — nota DERIVATĂ dintr-un document se corectează numai din documentul-sursă (lotul 07.10 B, C9).

Decizia Costin, 07.10.2026: „o notă derivată dintr-un document (stat de plată, factură, ieșire din stoc, NIR, amortizare și
restul clasei) se corectează numai din documentul-sursă; recontabilizarea înlocuiește nota respinsă și o retrimite la validare;
editarea manuală în jurnal e blocată pentru notele derivate, cu mesaj care spune unde se corectează.”

O notă e derivată când e LEGATĂ de documentul ei — nu după `sursa` (notele din Operațiuni poartă și ele `sursa='facturi'` /
`'banca'` / `'salarii'`, dar nu au document păstrat: acolo jurnalul rămâne calea de corectare). Legăturile, citite din schemă:
`inregistrari.factura_id` (contarea facturii), `miscari_stoc.inregistrare_id` (ieșire / intrare / inventar / rețetă), `nir.
inregistrari_ids`, `casa_operatiuni.inregistrare_id`, `chitante.inregistrare_id`, `extras_linii.alocari.inregistrari_ids` (notele
create din extras, `sursa='banca'`), statul de plată (`sursa='salarii'` cu `numar` = documentul statului), raportul Z
(`sursa` bon / horeca_z / amef), amortizarea (`sursa='amortizare'`).

Retrimiterea: o notă ciornă nouă, scrisă de un utilizator fără drept de validare, intră singură în coadă (middleware-ul
`uc_coada.note_in_coada`, după orice cerere de modificare reușită) — deci înlocuirea e suficientă.
"""

#: (fel, unde se corectează) — textul ajunge în refuzul din jurnal și în ecranul documentului
UNDE = {
    "factura": ("factura %s", "în Facturi: corectezi factura (stornare / factură nouă), apoi «Contabilizează»"),
    "plata_factura": ("plata facturii %s", "în Bancă sau Casă, unde s-a înregistrat plata"),
    "stoc": ("mișcarea de stoc %s", "în Stoc: din documentul mișcării (factura, NIR-ul, inventarul, rețeta)"),
    "nir": ("NIR-ul %s", "în Stoc › NIR-urile lunii: deschizi NIR-ul"),
    "casa": ("operațiunea de casă %s", "în Casă: ștergi operațiunea și o scrii din nou"),
    "chitanta": ("chitanța %s", "în Casă: anulezi chitanța și o emiți din nou"),
    "extras": ("linia de extras %s", "în Bancă: reconcilierea extrasului"),
    "salarii": ("statul de plată %s", "în Salarizare: corectezi statul (salariați, pontaj, contracte) și apeși «Contabilizează statul»"),
    "raport_z": ("raportul Z %s", "în Casa de marcat: raportul Z"),
    "amortizare": ("amortizarea %s", "în Mijloace fixe: amortizarea lunii"),
}
COD = "NOTA_DERIVATA"
#: documentele care INDICĂ nota din alt tabel: ștergerea notei din jurnal ar lăsa legătura în aer
FARA_STERGERE = ("stoc", "nir", "chitanta", "raport_z", "amortizare")


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def documentul_sursa(cur, schema, nota_id):
    """(fel, eticheta) al documentului din care derivă nota, sau None (notă manuală / din Operațiuni). Cursor dict sau tuplu."""
    s = _q(schema)

    def una(sql, *p):
        cur.execute(sql, p)
        r = cur.fetchone()
        if r is None:
            return None
        return list(r.values()) if isinstance(r, dict) else list(r)

    n = una("SELECT sursa, factura_id, numar, document_ref FROM %sinregistrari WHERE id = %%s" % s, nota_id)
    if not n:
        return None
    sursa, factura_id, numar, doc = n
    eticheta = doc or ("#%s" % nota_id)
    if factura_id and sursa == "facturi":
        return ("factura", eticheta)
    if una("SELECT 1 FROM %smiscari_stoc WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return ("stoc", eticheta)
    r = una("SELECT numar FROM %snir WHERE inregistrari_ids @> to_jsonb(%%s::int) LIMIT 1" % s, nota_id)
    if r:
        return ("nir", "nr %s" % r[0])
    if una("SELECT 1 FROM %scasa_operatiuni WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return ("casa", eticheta)
    if una("SELECT 1 FROM %schitante WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return ("chitanta", eticheta)
    if sursa == "banca" and una("SELECT 1 FROM %sextras_linii WHERE alocari->'inregistrari_ids' @> to_jsonb(%%s::int) LIMIT 1" % s,
                                nota_id):
        return ("extras", eticheta)
    if factura_id:                       # plată / încasare legată de factură, fără casă sau extras în spate
        return ("plata_factura", eticheta)
    if sursa == "salarii" and numar:
        return ("salarii", numar)
    if sursa in ("bon", "horeca_z", "amef"):
        return ("raport_z", eticheta)
    if sursa == "amortizare":
        return ("amortizare", eticheta)
    return None


def mesaj_refuz(nota_id, doc):
    fel, eticheta = doc
    ce, unde = UNDE[fel]
    return ("Nota #%s e derivată din %s: se corectează numai de acolo — %s. Dacă a fost respinsă la validare, după corectare "
            "recontabilizarea o înlocuiește și o trimite din nou la validare." % (nota_id, ce % eticheta, unde))


def respinsa(cur, schema, nota_id):
    """Nota e ciornă, iar ultimul ei element din coadă e `respinsa`? (atunci recontabilizarea o poate înlocui)"""
    s = _q(schema)
    cur.execute("SELECT status FROM %sinregistrari WHERE id = %%s" % s, (nota_id,))
    r = cur.fetchone()
    st = (r["status"] if isinstance(r, dict) else r[0]) if r else None
    if st != "ciorna":
        return False
    # aceeași interogare ca `coada_api.nota_la_validare`; schema goală = schema curentă a conexiunii
    cur.execute("SELECT c.stare FROM public.declaratii_coada c JOIN public.tenants t ON t.id = c.tenant_id "
                "WHERE t.schema_name = COALESCE(NULLIF(%s, ''), current_schema()) AND c.fel = 'nota' AND c.perioada = %s "
                "ORDER BY c.id DESC LIMIT 1", (str(schema or "").strip('"'), "nota-%d" % int(nota_id)))
    r = cur.fetchone()
    return bool(r) and (r["stare"] if isinstance(r, dict) else r[0]) == "respinsa"


def sterge_respinsa(cur, schema, nota_id):
    """Scoate nota respinsă înaintea înlocuirii (liniile cad prin ON DELETE CASCADE). Elementul ei din coadă rămâne, `respinsa`,
    ca istoric: motivul respingerii nu se pierde."""
    cur.execute("DELETE FROM %sinregistrari WHERE id = %%s AND status = 'ciorna'" % _q(schema), (nota_id,))
    n = cur.rowcount
    if n:
        # [retest 07.10 seara, S4] o notă înlocuită nu lasă notificarea „a fost respinsă” activă
        from core import notificari_api as _notif
        _notif.rezolva_nota_inlocuita(cur.connection, schema, nota_id)
    return n
