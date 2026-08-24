# -*- coding: utf-8 -*-
"""core/migrare_verdict_validare.py — verdictul oficial de validare, PERSISTAT.

Sursa UNICA a DDL-ului. Idempotent (ADD COLUMN IF NOT EXISTS).
Aplica pe existenti: `python3 -m core.migrare_verdict_validare`.

DE CE (R41, 24.08.2026). Validatorul oficial ruleaza deja - `GET /coada/{id}/continut` cheama
DUKIntegrator la fiecare deschidere a unui element. Ruta e `Read-only`, deci verdictul se PRODUCE,
se afiseaza si se ARUNCA. Consecinta masurata: `coerenta` era NULL pe 3 din 3, badge-ul spunea
"neverificat" pentru orice declaratie, iar ecranul numea "De depus" o lista care continea declaratii
fara verdict. Nu o lista incompleta - o afirmatie falsa.

CE ADAUGA, si de ce PATRU campuri, nu unul (Costin, 24.08.2026):
  - verdict           : 'valid' | 'erori' | 'gri' - cele trei stari ale lui duk.valideaza. `gri` =
                        NU S-A PUTUT valida (validator lipsa, java lipsa, timeout); un XML nevalidat
                        NU se declara valid.
  - verdict_erori     : textul erorilor, ca sa nu se piarda CE a spus validatorul.
  - verdict_la        : momentul.
  - verdict_versiune  : CU CE s-a validat - numele jarului ANAF si amprenta lui. Un verdict dat de
                        un validator vechi nu e acelasi lucru cu unul dat de cel curent.
  - verdict_amprenta  : AMPRENTA XML-ULUI VALIDAT. Campul care schimba totul: un verdict pe un XML
                        care s-a regenerat intre timp nu mai e verdict. Daca amprenta stocata difera
                        de a XML-ului din coada, verdictul e STATUT si se trateaza ca ABSENT, nu ca
                        favorabil. Aceeasi forma cu regula de la D112/D300 din aceeasi zi: un verdict,
                        ca si o declaratie, e despre UN ANUMIT CONTINUT, nu despre un moment.

Si trei pentru trecerea peste blocare, fiindca "se poate trece" fara "cine si de ce" e o poarta
care nu tine:
  - trecere_motiv, trecut_de_id, trecut_la.

CE NU FACE: nu atinge `coerenta`. Aia ramane cum e - un camp vechi, nescris de nimeni; se scoate
separat, cu masuratoare proprie, nu pe furis intr-o migrare care adauga altceva.
"""
from core import db

DDL = """
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS verdict text;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS verdict_erori text;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS verdict_la timestamptz;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS verdict_versiune text;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS verdict_amprenta text;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS trecere_motiv text;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS trecut_de_id integer;
ALTER TABLE public.declaratii_coada ADD COLUMN IF NOT EXISTS trecut_la timestamptz;
"""


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
    print("migrare_verdict_validare: OK")


if __name__ == "__main__":
    _main()
