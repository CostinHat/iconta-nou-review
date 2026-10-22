# -*- coding: utf-8 -*-
"""core/migrare_serie_nr_descrieri.py — notele și mișcările de stoc scrise înainte de 443 cu seria lipită de număr („Contare factura F61”,
„Factură F1A3 din 06.10.2026”) trec pe forma de acum („Contare factura F6 nr. 1”, „Factură F1A nr. 3 din 06.10.2026”) acolo unde se mai
pot schimba (lotul 11, deficiența 443; regula Costin 11.2 pct.3a, verbatim: „Orice reparație acoperă și datele existente.”).

443 (comanda Costin 11.1 pct.19, verbatim): „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”. Reparația din lotul 11
(`pdf_util.serie_nr`, folosită de `contare_facturi._descriere`, `jurnal_api.eticheta_factura`, `stocuri_cv_api.document_retur`,
`compensari_api`) scrie forma nouă numai pe ce se scrie de acum; textele deja salvate păstrau forma lipită — pe copia firmelor de test
(22.10.2026): F1 10 note de contare „Contare factura F1A3”…„F1A12” și 6 note / mișcări de stoc „Factură F1A3 din …”, F6 „Contare factura F61”.

CE RESCRIE (numai textul scris de APLICAȚIE pentru o factură — `jurnal_api.SCRISE_DE_APLICATIE`; numărul nou din aceeași funcție ca la
scriere, `pdf_util.serie_nr`, prin `jurnal_api.fara_serie_lipita` — nu o a doua formulă):
  · CIORNELE (`status = 'ciorna'`): descrierea notei de contare (factura din `factura_id`), documentul notei de stoc (factura mișcării ei),
    descrierea compensării (cele două facturi). Lista o dă `jurnal_api.note_cu_serie_lipita` — aceeași cu care Registrul jurnal arată
    notele validate. La ciorna de stoc, documentul rescris e și cel pe care regenerarea pe uscat (451, `ciorne_depasite`) îl compară: fără
    rescriere, ciorna ar apărea „depășită” numai pentru eticheta numărului;
  · MIȘCĂRILE DE STOC ale unei facturi care nu sunt în evidență (`miscare_in_evidenta` — regula de fond R5; aceeași ca
    `migrare_borderou_tip_vechi`): documentul din fișa de magazie („Factură …”, „Retur la Factură …”, „Diferență de preț NIR … / factura …”).
CE NU RESCRIE (și raportează):
  · NOTELE VALIDATE și mișcările lor în evidență: nota validată nu se modifică (OMFP 1802/2014 pct.69; triggerele `regula_nota`,
    `regula_stoc`). Registrul jurnal le ARATĂ cu seria separat, derivat din factură (`jurnal_api.note_fara_serie_lipita`), fără să le scrie;
  · ciornele și mișcările din LUNA ÎNCHISĂ (triggerul perioadei blocate): rămân, se arată derivat;
  · documentul de stoc care nu încape în coloană (`miscari_stoc.document` are 100 de caractere): nu se taie, rămâne;
  · textul omului și al băncii (documentul tastat la casă, extrasul): nu e al aplicației (CLAUDE.md §8).

Idempotentă: a doua rulare nu mai găsește nimic (forma nouă nu mai conține numărul lipit). Fiecare firmă se comite separat și se raportează
(ciorne rescrise, mișcări rescrise, validate arătate derivat, lăsate cu motivul). Pe uscat (`plan`, numai citire): `python -m
core.migrare_serie_nr_descrieri --uscat` — nu scrie nimic, nu comite.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_serie_nr_descrieri.py`.
"""
import sys

from core import db
from core.common import cate as _cate

#: coloanele notei pe care le rescrie (lista închisă; vine din `jurnal_api.note_cu_serie_lipita`)
CAMPURI_NOTA = ("descriere", "document_ref")
#: `miscari_stoc.document` character varying(100) (tenant_template.sql)
LUNGIME_DOCUMENT_STOC = 100


def _s(schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    return '"%s"' % schema


def _luni_inchise(cur, s):
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", ("%s.perioade_blocate" % s,))
    if not cur.fetchone()[0]:
        return set()
    cur.execute("SELECT an, luna FROM %s.perioade_blocate" % s)
    return {(int(a), int(l)) for a, l in cur.fetchall()}


def _are_tabelele(cur, s):
    cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL",
                ("%s.inregistrari" % s, "%s.miscari_stoc" % s, "%s.compensari" % s))
    return cur.fetchone()[0]


def _miscari_cu_serie_lipita(cur, s):
    """[(mișcare, data, în evidență, document de acum, document cu seria separat)] — documentul scris de aplicație al mișcărilor unei facturi."""
    from core import jurnal_api as _j
    cur.execute(f"""SELECT m.id, m.data, {s}.miscare_in_evidenta(m.id), m.document, f.serie, f.numar
                    FROM {s}.miscari_stoc m JOIN {s}.facturi f ON f.id = m.factura_id
                    WHERE m.document IS NOT NULL AND COALESCE(btrim(f.serie), '') <> '' ORDER BY m.id""")
    out = []
    for mid, data, in_ev, doc, serie, numar in cur.fetchall():
        nou = _j.scris_de_aplicatie_fara_serie_lipita(doc, [(serie, numar)])
        if nou != doc:
            out.append((mid, data, bool(in_ev), doc, nou))
    return out


def plan(cur, schema):
    """Ce ar face migrarea, FĂRĂ să scrie: {"ciorne": [(nota, câmp, vechi, nou)], "validate": [(nota, câmp, vechi, nou)] (arătate derivat),
    "ciorne_lasate": [(nota, câmp, vechi, nou, motiv)], "miscari": [(mișcare, vechi, nou)], "miscari_lasate": [(mișcare, vechi, nou, motiv)]}."""
    from core import jurnal_api as _j
    s = _s(schema)
    gol = {"ciorne": [], "validate": [], "ciorne_lasate": [], "miscari": [], "miscari_lasate": []}
    if not _are_tabelele(cur, s):
        return gol
    inchise = _luni_inchise(cur, s)
    for nid, status, data, camp, vechi, nou in _j.note_cu_serie_lipita(cur, s):
        if status == "validata":
            gol["validate"].append((nid, camp, vechi, nou))
        elif status != "ciorna":
            gol["ciorne_lasate"].append((nid, camp, vechi, nou, "nota are starea %r, nu e ciornă: se arată derivat" % status))
        elif camp not in CAMPURI_NOTA:
            gol["ciorne_lasate"].append((nid, camp, vechi, nou, "câmpul %s nu e în lista migrării" % camp))
        elif (data.year, data.month) in inchise:
            gol["ciorne_lasate"].append((nid, camp, vechi, nou, "luna %02d/%d e închisă: se arată derivat" % (data.month, data.year)))
        else:
            gol["ciorne"].append((nid, camp, vechi, nou))
    for mid, data, in_ev, vechi, nou in _miscari_cu_serie_lipita(cur, s):
        if in_ev:
            gol["miscari_lasate"].append((mid, vechi, nou, "mișcarea e în evidență (nota ei e validată): nu se modifică"))
        elif (data.year, data.month) in inchise:
            gol["miscari_lasate"].append((mid, vechi, nou, "luna %02d/%d e închisă" % (data.month, data.year)))
        elif len(nou) > LUNGIME_DOCUMENT_STOC:
            gol["miscari_lasate"].append((mid, vechi, nou, "forma nouă are peste %s: nu se taie"
                                          % _cate(LUNGIME_DOCUMENT_STOC, "caracter", "caractere")))
        else:
            gol["miscari"].append((mid, vechi, nou))
    return gol


def aplica(conn, schema):
    """Scrie planul în tranzacția `conn` (fără commit): numai ciorne (`status = 'ciorna'` și în condiția UPDATE-ului) și mișcări din afara
    evidenței. Întoarce planul (raportul firmei)."""
    s = _s(schema)
    with conn.cursor() as cur:
        p = plan(cur, schema)
        for nid, camp, vechi, nou in p["ciorne"]:
            cur.execute(f"UPDATE {s}.inregistrari SET {camp} = %s WHERE id = %s AND status = 'ciorna' AND {camp} = %s",
                        (nou, nid, vechi))
        for mid, vechi, nou in p["miscari"]:
            cur.execute(f"UPDATE {s}.miscari_stoc SET document = %s WHERE id = %s AND document = %s", (nou, mid, vechi))
    return p


def verifica(conn, schema):
    """După rulare: nicio ciornă și nicio mișcare rescriptibilă rămasă."""
    with conn.cursor() as cur:
        p = plan(cur, schema)
    return not p["ciorne"] and not p["miscari"]


def text_raport(schema, r):
    lin = ["%s: %s, %s, %s, %s" % (
        schema, _cate(len(r["ciorne"]), "ciornă rescrisă", "ciorne rescrise"),
        _cate(len(r["miscari"]), "mișcare de stoc rescrisă", "mișcări de stoc rescrise"),
        _cate(len(r["validate"]), "notă validată arătată derivat", "note validate arătate derivat"),
        _cate(len(r["ciorne_lasate"]) + len(r["miscari_lasate"]), "text lăsat", "texte lăsate"))]
    lin += ["  ciornă %s (%s): «%s» -> «%s»" % (n, c, v, x) for n, c, v, x in r["ciorne"]]
    lin += ["  mișcare %s: «%s» -> «%s»" % (m, v, x) for m, v, x in r["miscari"]]
    lin += ["  validată %s (%s), arătată derivat: «%s» -> «%s»" % (n, c, v, x) for n, c, v, x in r["validate"]]
    lin += ["  ciornă %s (%s) lăsată: «%s» — %s" % (n, c, v, m) for n, c, v, _x, m in r["ciorne_lasate"]]
    lin += ["  mișcare %s lăsată: «%s» — %s" % (i, v, m) for i, v, _x, m in r["miscari_lasate"]]
    return "\n".join(lin)


def _main(uscat=False):
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                if uscat:
                    with conn.cursor() as cur:
                        r = plan(cur, s)
                    conn.rollback()
                else:
                    r = aplica(conn, s)
                    conn.commit()
            ok += 1
            if any(r.values()):
                print(text_raport(s, r))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_serie_nr_descrieri%s: %d ok, %d esec" % (" (pe uscat, nimic scris)" if uscat else "", ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main(uscat="--uscat" in sys.argv[1:])
