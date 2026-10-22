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
    # [lotul 10, deficiența 401, comanda Costin 10.2 pct.7a, verbatim] „sub nota borderoului, textul zice «factura de achiziție BA-1» și
    # trimite la Facturi.” Borderoul de achiziție (OMFP 2634/2015, cod 14-4-13) e documentul firmei, scris din Operațiuni; nu e o factură
    # și nu se stornează din Facturi (`facturi_api.storneaza`: numai facturi emise) — după validare, greșeala lui se corectează printr-o
    # notă de corecție, ca la NIR-ul aflat în evidență (`stocuri_api._nir_de_refacut`)
    # [lotul 11, patch B (P9), decizia 10.3: „Borderoul se corectează prin stornare, ca factura.”] ecranul propriu al borderoului, cu stornare
    "borderou": ("borderoul de achiziție %s", "în Stocuri › „Borderou de achiziție”: îl stornezi din lista lunii (borderoul de stornare și "
                                              "nota inversă), apoi îl scrii din nou corect"),
    "plata_borderou": ("plata borderoului de achiziție %s", "în Bancă sau Casă, unde s-a înregistrat plata"),
    "stoc": ("mișcarea de stoc %s", "în Stoc: din documentul mișcării (factura, NIR-ul, inventarul, rețeta)"),
    "nir": ("NIR-ul %s", "în Stoc › NIR-urile lunii: deschizi NIR-ul"),
    "casa": ("operațiunea de casă %s", "în Casă: ștergi operațiunea și o scrii din nou"),
    "chitanta": ("chitanța %s", "în Casă: anulezi chitanța și o emiți din nou"),
    "extras": ("linia de extras %s", "în Bancă: reconcilierea extrasului"),
    "salarii": ("statul de plată %s", "în Salarizare: corectezi statul (salariați, pontaj, contracte) și apeși «Contabilizează statul»"),
    "raport_z": ("raportul Z %s", "în Casa de marcat: raportul Z"),
    "amortizare": ("amortizarea %s", "în Mijloace fixe: amortizarea lunii"),
    # [lotul 10, 428] nota compensării derivă din ordinul de compensare (HG 685/1999 anexa 2 art.11: „Ordinul de compensare se anexeaza la
    # nota contabila”) și din rândul `compensari`: editată în jurnal, suma notei s-ar despărți de compensare. Ștergerea (ciornă) rămâne:
    # rândul `compensari` cade odată cu nota (ON DELETE CASCADE), iar facturile redevin deschise
    "compensare": ("%s", "în Compensări: ștergi nota ciornă a compensării din Registrul jurnal și generezi "
                                                  "compensarea din nou"),
}
COD = "NOTA_DERIVATA"
#: documentele care INDICĂ nota din alt tabel: ștergerea notei din jurnal ar lăsa legătura în aer
#: [deficiența 328, 18.10.2026] + nota statului de plată: statul rămâne, iar „Contabilizează statul” își înlocuiește singur ciorna
#: (`uc_tenants.salarii_contare_scrie`) — ștergerea din jurnal nu e drumul niciunei corecturi.
FARA_STERGERE = ("stoc", "nir", "chitanta", "raport_z", "amortizare", "salarii")


def se_sterge(cur, schema, doc, nota_id):
    """Nota derivată (ciornă) se poate șterge din Registrul jurnal? [deficiența 328, 18.10.2026] Contarea facturii se șterge numai cât
    factura e ciornă — e drumul ștergerii ciornei (`facturi_api.sterge_factura` cere întâi nota ștearsă). A facturii emise nu: factura
    nu se mai șterge (CF art.330 alin.(1), stornare), iar „Șterge” în jurnal o lăsa emisă și necontată, fără ca ceva să fi fost corectat."""
    if doc[0] in FARA_STERGERE:
        return False
    if doc[0] not in ("factura", "borderou"):   # [401] borderoul: aceeași regulă ca factura primită (statusul lui)
        return True
    from core import nomenclator_status_factura as _nsf
    cur.execute("SELECT COALESCE(f.status, %%s) AS status FROM %sinregistrari i JOIN %sfacturi f ON f.id = i.factura_id "
                "WHERE i.id = %%s" % (_q(schema), _q(schema)), (_nsf.IMPLICITA, nota_id))
    r = cur.fetchone()
    return (r["status"] if isinstance(r, dict) else r[0]) in _nsf.STERGIBILE if r else True


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def documentul_sursa(cur, schema, nota_id):
    """(fel, eticheta documentului, eticheta notei) al documentului din care derivă nota, sau None (notă manuală / din Operațiuni).
    Cursor dict sau tuplu. [deficiența 258] Nimic din ce se arată nu e id-ul intern: nota e „nr. crt. N din ZZ.LL.AAAA”
    (`eticheta_nota`, ca în Registrul jurnal), documentul fără număr scris e numit prin factura lui sau prin data notei."""
    s = _q(schema)

    def una(sql, *p):
        cur.execute(sql, p)
        r = cur.fetchone()
        if r is None:
            return None
        return list(r.values()) if isinstance(r, dict) else list(r)

    n = una("SELECT i.sursa, i.factura_id, i.numar, i.document_ref, f.tip AS f_tip, f.serie AS f_serie, f.numar AS f_numar, "
            "f.data_emitere AS f_data, i.data, %seticheta_nota(i.id) AS eticheta FROM %sinregistrari i "
            "LEFT JOIN %sfacturi f ON f.id = i.factura_id WHERE i.id = %%s" % (s, s, s), nota_id)
    if not n:
        return None
    sursa, factura_id, numar, doc, f_tip, f_serie, f_nr, f_data, data, et_nota = n
    from core import pdf_util as _pu
    if not doc:
        # [401] numărul și data documentului, fără felul lui (felul îl spune `UNDE`): înainte, eticheta tăiată la primul cuvânt
        # („Borderou de achiziție BA-1” -> „de achiziție BA-1”) ajungea în „factura %s” -> „factura de achiziție BA-1”
        doc = ("%s din %s" % (_pu.serie_nr(f_serie, f_nr), _pu.data_ro(f_data)) if f_nr is not None   # [lotul 11, 443] „F6 nr. 1”
               else "din %s" % _pu.data_ro(data))
    borderou = f_tip == "borderou"

    def d(fel, eticheta=doc):
        return (fel, eticheta, et_nota)
    if factura_id and sursa == "facturi":
        return d("borderou" if borderou else "factura")
    if una("SELECT 1 FROM %smiscari_stoc WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return d("stoc")
    r = una("SELECT numar FROM %snir WHERE inregistrari_ids @> to_jsonb(%%s::int) LIMIT 1" % s, nota_id)
    if r:
        return d("nir", "nr %s" % r[0])
    if una("SELECT 1 FROM %scasa_operatiuni WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return d("casa")
    if una("SELECT 1 FROM %schitante WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return d("chitanta")
    if sursa == "banca" and una("SELECT 1 FROM %sextras_linii WHERE alocari->'inregistrari_ids' @> to_jsonb(%%s::int) LIMIT 1" % s,
                                nota_id):
        return d("extras")
    if una("SELECT 1 FROM %scompensari WHERE inregistrare_id = %%s LIMIT 1" % s, nota_id):
        return d("compensare")
    if factura_id:                       # plată / încasare legată de factură, fără casă sau extras în spate
        return d("plata_borderou" if borderou else "plata_factura")
    if sursa == "salarii" and numar:
        return d("salarii", numar)
    if sursa in ("bon", "horeca_z", "amef"):
        return d("raport_z")
    if sursa == "amortizare":
        return d("amortizare")
    return None


def mesaj_refuz(nota_id, doc):
    """Refuzul editării / ștergerii din jurnal. [258] Nota se numește prin eticheta ei (`doc[2]`, din `documentul_sursa`), nu prin
    `nota_id` (păstrat în semnătură pentru apelanți: numărul intern nu ajunge în text)."""
    fel, eticheta, et_nota = doc
    ce, unde = UNDE[fel]
    return ("Nota %s e derivată din %s: se corectează numai de acolo — %s. Dacă a fost respinsă la validare, după corectare "
            "recontabilizarea o înlocuiește și o trimite din nou la validare." % (et_nota, ce % eticheta, unde))


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


def ciorna_nevalidata(cur, schema, nota_id):
    """[retest 08.10 pct.1] Nota e ciornă și nu e respinsă (în afara cozii sau la validare)? — ciorna pe care contabilizarea
    documentului o poate înlocui cu nota din documentul de acum."""
    s = _q(schema)
    cur.execute("SELECT status FROM %sinregistrari WHERE id = %%s" % s, (nota_id,))
    r = cur.fetchone()
    st = (r["status"] if isinstance(r, dict) else r[0]) if r else None
    return st == "ciorna" and not respinsa(cur, schema, nota_id)


def sterge_ciorna_inlocuita(cur, schema, nota_id):
    """[retest 08.10 pct.1, decizia Costin] Scoate ciorna nevalidată pe care o înlocuiește nota din documentul de acum (liniile cad
    prin ON DELETE CASCADE; elementul ei `la_senior` din coadă cade prin `trg_coada_nota_sincron`, iar notificarea „de validat” se
    rezolvă „înlocuită”). Numai o ciornă — o notă validată nu se atinge."""
    cur.execute("DELETE FROM %sinregistrari WHERE id = %%s AND status = 'ciorna'" % _q(schema), (nota_id,))
    return cur.rowcount


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
