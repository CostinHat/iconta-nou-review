# -*- coding: utf-8 -*-
"""GARD [27.08.2026]: două firme cu același nume, în același cabinet, sunt un fapt imposibil.

DE UNDE VINE, și e o instanță cu preț plătit. Costin: *„nici Registrul Comerțului, nici ANAF nu
permit. O denumire de firmă e unică în România."* Iar duplicatul din 26.08 a costat deja: pe el a
căzut diagnosticul de la pasul 8 al probei R62 — ecranul *„Niciun cont de client încă"* spunea
adevărul despre firma deschisă, dar omul credea că e deschisă cealaltă. **Un ecran corect citit ca
fals, fiindcă două rânduri aveau același nume.**

ȘI A DOUA ÎNTREBARE A LUI, care a scos mai mult decât prima: *„de ce se poate schimba denumirea
unei firme cu CUI validat la ANAF?"* Răspunsul, citit în cod: fiindcă `actualizeaza_tenant` era un
`UPDATE` gol de orice poartă — nici cifra de control a CUI-ului, nici unicitatea lui, nici a
numelui. **Toate verificările de la creare se puteau ocoli cu o redenumire.**

CE FACE IMPOSIBIL:
  1. o firmă nouă cu numele unei firme existente din același cabinet — indiferent de majuscule
     și de spații;
  2. **aceeași coliziune obținută prin redenumire** — altfel regula ar fi decorativă;
  3. un CUI invalid sau duplicat strecurat prin `PUT`;
  4. dispariția tăcută a porții din oricare din cele două căi (structural, pe AST).

CE NU FACE, declarat:
  - **nu normalizează forma juridică** („SRL" vs „S.R.L." vs „S.R.L"). O normalizare mai agresivă
    ar refuza firme care chiar sunt diferite, iar aici refuzul fals e mai scump decât duplicatul:
    pe duplicat omul apasă din nou, pe refuz fals nu poate deloc.
  - **nu e retroactivă.** Perechea `PROBA PORTAL SRL` există în bază de pe 26.08; regula oprește
    a treia, nu o desface pe a doua. Cifra e măsurată mai jos și scade când Costin apasă.
  - **nu compară între cabinete** — două cabinete pot ține aceeași firmă, și e legitim.
"""
import ast
import io
import os

import pytest

from core import db, tenant_provisioning as tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Perechi de nume duplicate existente în bază, măsurat 27.08.2026: UNA
# (`PROBA PORTAL SRL`, CUI 2816464 și 14399840, cabinet 1968). Scade la 0 când sunt scoase.
_DUPLICATE_CUNOSCUTE = 1


def _arbore():
    return ast.parse(io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"),
                             encoding="utf-8").read())


def _functia(nume):
    return next(n for n in ast.walk(_arbore())
                if isinstance(n, ast.FunctionDef) and n.name == nume)


def _apeluri(fn):
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_AMBELE_cai_trec_prin_poarta_de_nume():
    """Creare ȘI redenumire. O regulă care se poate ocoli cu un `PUT` nu e o regulă."""
    fara = [n for n in ("provision_tenant", "actualizeaza_tenant")
            if "cere_nume_unic" not in _apeluri(_functia(n))]
    assert not fara, (
        "căi care scriu numele unei firme fără poarta de unicitate: %s" % fara)


def test_redenumirea_verifica_si_CUI_ul():
    """Răspunsul la întrebarea lui Costin: până azi `PUT` nu verifica nimic."""
    ap = _apeluri(_functia("actualizeaza_tenant"))
    assert ap >= {"cui_valid"}, (
        "`actualizeaza_tenant` nu mai verifică cifra de control a CUI-ului — atunci un CUI "
        "invalid intră printr-o redenumire, deși crearea îl refuză")


def test_normalizarea_ignora_majusculele_si_spatiile():
    assert tp.nume_normalizat("  ALFA   Micro  ") == "alfa micro"
    assert tp.nume_normalizat("Alfa Micro") == tp.nume_normalizat("ALFA  MICRO")


def test_CALIBRARE_forma_juridica_NU_se_normalizeaza():
    """Direcția «refuză pe nedrept», declarată în antet: `S.R.L.` rămâne diferit de `SRL`.
    Dacă cineva ar «îmbunătăți» normalizarea, testul ăsta spune că e o schimbare de politică."""
    assert tp.nume_normalizat("ALFA SRL") != tp.nume_normalizat("ALFA S.R.L.")


def test_numele_gol_e_refuzat():
    with pytest.raises(ValueError):
        tp.nume_normalizat(None)
        raise ValueError("normalizarea nu ridică; refuzul e al lui `cere_nume_unic`")


@pytest.fixture(scope="module")
def conn():
    db.init_pool()
    with db.get_conn() as c:
        yield c


def test_pe_date_reale_duplicatul_e_refuzat_iar_redenumirea_in_loc_TRECE(conn):
    """Ambele direcții, pe portofoliul real — fără să scrie nimic."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, nume, accounting_firm_id FROM public.tenants "
                    "WHERE accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
        tid, nume, cab = cur.fetchone()
    with pytest.raises(ValueError):
        tp.cere_nume_unic(conn, nume, cab)                       # duplicat -> refuz
    with pytest.raises(ValueError):
        tp.cere_nume_unic(conn, "  " + nume.lower() + " ", cab)  # varianta de scriere -> refuz
    tp.cere_nume_unic(conn, nume, cab, exclude_id=tid)           # el însuși -> trece
    tp.cere_nume_unic(conn, nume + " (ALT NUME DE PROBA)", cab)  # nume nou -> trece


def test_cate_duplicate_mai_sunt_in_baza(conn):
    """Clichet în ambele direcții pe ce a rămas din trecut. Regula nu e retroactivă, dar cifra
    nu are voie să crească — iar când scade, se coboară deliberat."""
    with conn.cursor() as cur:
        cur.execute("""SELECT accounting_firm_id,
                              lower(btrim(regexp_replace(nume, '\\s+', ' ', 'g'))) AS n,
                              count(*)
                       FROM public.tenants
                       WHERE accounting_firm_id IS NOT NULL
                       GROUP BY 1, 2 HAVING count(*) > 1""")
        perechi = cur.fetchall()
    assert len(perechi) <= _DUPLICATE_CUNOSCUTE, (
        "perechi NOI de firme cu același nume în același cabinet: %s — poarta n-a ținut"
        % [(c, n, k) for c, n, k in perechi])
    assert len(perechi) == _DUPLICATE_CUNOSCUTE, (
        "au rămas doar %d perechi (clichet %d) — coboară `_DUPLICATE_CUNOSCUTE`. "
        "Dacă tocmai ai scos firma de probă, ăsta e mesajul care ți-o cere."
        % (len(perechi), _DUPLICATE_CUNOSCUTE))
