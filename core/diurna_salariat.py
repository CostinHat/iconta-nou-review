# -*- coding: utf-8 -*-
"""core/diurna_salariat.py — excedentul de diurnă al salariatului, venit de natură salarială (lotul 13, deficiența 670 b).

Comanda Costin 13.1, 670 (b): „excedentul de diurnă e venit de natură salarială (impozit, contribuții, D112). Code verifică la sursă
plafonul în vigoare și leagă excedentul de statul de plată.” Plafonul și regimul diurnei le stabilește decontul (subagentul OPS,
`core/deconturi.py`); aici stă numai partea care DEPĂȘEȘTE plafonul, pe salariat și pe lună, ca statul de plată, D112 și nota
salariilor s-o ia de aici.

TEMEI (textul, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`):
  - CF art.76 alin.(2) lit.k): sunt venituri asimilate salariilor „indemnizația de delegare, indemnizația de detașare […] precum și
    orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de
    salariați […] pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru
    partea care depășește plafonul neimpozabil”;
  - CF art.139 alin.(1) lit.j) (baza CAS), art.157 alin.(1) lit.m) (baza CASS) și art.220^4 alin.(1) lit.h) (baza CAM): aceeași
    „parte care depășește plafonul neimpozabil” intră în baza contribuțiilor;
  - OPANAF 605/2026 anexa 2, E.3 rândul 8.2.1 „Indemnizaţii de delegare impozabile”: „se completează cu sumele reprezentând
    indemnizaţii de delegare impozabile, respectiv cu partea care depăşeşte plafonul neimpozabil stabilit în Codul fiscal” (E3_52,
    cuprins în E3_59 „Venituri asimilate salariilor” și în E3_8 „Total venit brut”).

Contabil: excedentul s-a plătit deja prin decont (625 = 542 / 5311), deci în nota salariilor NU mai intră pe 641 = 421: din el se rețin
numai CAS, CASS și impozitul (din salariul în bani al lunii), iar CAM-ul îl plătește angajatorul (`salarizare.monografie_salariu`).

Interfața cu decontul (OPS): `adauga_excedent` la decontul final (idempotent pe `referinta`), cu `nota_id` = nota decontului.

[684, lotul 13] Excedentul trăiește cât trăiește nota decontului care l-a produs: coloana `inregistrare_id` e cheie străină spre
`inregistrari(id)` cu ON DELETE CASCADE, deci ORICE drum care șterge nota (jurnalul, `note_derivate`, descărcarea Z, ștergerea facturii,
un DELETE scris de mână) scoate și excedentul — venitul salarial nu mai rămâne în statul de plată și în D112 fără decont. Nu e o chemare
pe care un drum de ștergere o poate uita: o face baza. `sterge_excedent` rămâne pentru excedentul fără notă (referință externă).
Garda: `core/test_lot13_sal_salarizare.py::test_684_*` (orice chemare de producție trimite `nota_id`; ștergerea notei scoate excedentul).
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

TABEL = "diurna_excedent"

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".diurna_excedent ('
       ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
       ' salariat_id integer NOT NULL REFERENCES "{s}".salariati(id) ON DELETE RESTRICT,'
       ' an integer NOT NULL,'
       ' luna integer NOT NULL CHECK (luna BETWEEN 1 AND 12),'
       ' suma numeric(12,2) NOT NULL CHECK (suma > 0),'
       ' referinta text NOT NULL CHECK (length(btrim(referinta)) > 0),'
       ' descriere text,'
       ' creat_la timestamp with time zone NOT NULL DEFAULT now(),'
       ' CONSTRAINT diurna_excedent_referinta_uniq UNIQUE (referinta));')

#: [684] legătura excedentului de nota decontului: ștergerea notei îl scoate (ON DELETE CASCADE). Separat de CREATE TABLE, ca tabelele
#: create înainte (lotul 13, înaintea lui 684) s-o primească prin migrare; `ADD COLUMN IF NOT EXISTS` sare cu tot cu cheia străină.
DDL_NOTA = ('ALTER TABLE "{s}".diurna_excedent ADD COLUMN IF NOT EXISTS inregistrare_id integer '
            'REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE;')

#: [684, datele existente] referința pe care decontul OPS o scria înainte de legătură (`uc_tenants`, decontul de deplasare): rândurile ei
#: primesc nota din referință; cele a căror notă nu mai există sunt excedentele rămase orfane prin defectul 684 și se scot.
REPARA_LEGATURA = (
    'UPDATE "{s}".diurna_excedent d SET inregistrare_id = substring(d.referinta from \'^decont-deplasare:([0-9]+)$\')::integer '
    'WHERE d.inregistrare_id IS NULL AND d.referinta ~ \'^decont-deplasare:[0-9]+$\' AND EXISTS (SELECT 1 FROM "{s}".inregistrari i '
    'WHERE i.id = substring(d.referinta from \'^decont-deplasare:([0-9]+)$\')::integer);'
    'DELETE FROM "{s}".diurna_excedent d WHERE d.inregistrare_id IS NULL AND d.referinta ~ \'^decont-deplasare:[0-9]+$\';')


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def _suma(v):
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Excedentul de diurnă trebuie să fie o sumă în lei.")
    if d <= 0:
        raise ValueError("Excedentul de diurnă trebuie să fie mai mare ca 0.")
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # aritmetic (CLAUDE.md „Rotunjire fiscală”)


def adauga_excedent(cur, schema, salariat_id, an, luna, suma, referinta, descriere, nota_id=None):
    """Excedentul de diurnă al salariatului în luna (an, luna) — venit salarial (CF art.76 alin.(2) lit.k). Idempotent pe `referinta`
    (decontul care l-a produs): a doua chemare cu aceeași referință rescrie salariatul, luna, suma, descrierea și nota, nu adaugă un rând.
    `nota_id` = nota decontului [684]: ștergerea ei scoate excedentul (cheia străină, ON DELETE CASCADE). Întoarce id-ul rândului."""
    ref = str(referinta or "").strip()
    if not ref:
        raise ValueError("Excedentul de diurnă cere referința decontului care l-a produs.")
    if not (1 <= int(luna) <= 12):
        raise ValueError("Luna excedentului de diurnă trebuie să fie între 1 și 12.")
    s = _suma(suma)
    cur.execute(f"SELECT 1 FROM {_p(schema)}salariati WHERE id = %s", (int(salariat_id),))
    if cur.fetchone() is None:
        raise ValueError("Salariatul excedentului de diurnă nu există în firmă.")
    nota = int(nota_id) if nota_id is not None else None
    if nota is not None:
        cur.execute(f"SELECT 1 FROM {_p(schema)}inregistrari WHERE id = %s", (nota,))
        if cur.fetchone() is None:
            raise ValueError("Nota decontului care a produs excedentul de diurnă nu există în firmă.")
    # upsert-ok: aceeași referință (același decont) rescrie rândul ei — un decont refăcut nu dublează venitul salarial
    cur.execute(f"INSERT INTO {_p(schema)}diurna_excedent (salariat_id, an, luna, suma, referinta, descriere, inregistrare_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (referinta) DO UPDATE SET salariat_id = EXCLUDED.salariat_id, "
                "an = EXCLUDED.an, luna = EXCLUDED.luna, suma = EXCLUDED.suma, descriere = EXCLUDED.descriere, "
                "inregistrare_id = EXCLUDED.inregistrare_id RETURNING id",
                (int(salariat_id), int(an), int(luna), s, ref, (str(descriere).strip() or None) if descriere else None, nota))
    r = cur.fetchone()
    return int(r["id"] if isinstance(r, dict) else r[0])


def sterge_excedent(cur, schema, referinta):
    """Scoate excedentul cu referința `referinta`. Excedentul legat de o notă cade singur odată cu nota (684); aici, cel fără notă."""
    cur.execute(f"DELETE FROM {_p(schema)}diurna_excedent WHERE referinta = %s", (str(referinta or "").strip(),))


def excedente_luna(cur, schema, an, luna):
    """{salariat_id: [{suma (Decimal), descriere, referinta}]} — excedentele lunii, o singură citire (statul, D112, nota)."""
    cur.execute(f"SELECT salariat_id, suma, descriere, referinta FROM {_p(schema)}diurna_excedent WHERE an = %s AND luna = %s "
                "ORDER BY salariat_id, id", (int(an), int(luna)))
    out = {}
    for r in cur.fetchall():
        sid, suma, desc, ref = (r["salariat_id"], r["suma"], r["descriere"], r["referinta"]) if isinstance(r, dict) else r
        out.setdefault(sid, []).append({"suma": Decimal(str(suma)), "descriere": desc or "", "referinta": ref})
    return out


def total(lista):
    """Suma excedentelor unui salariat (lista din `excedente_luna`), ca Decimal."""
    return sum((x["suma"] for x in lista or ()), Decimal("0"))

