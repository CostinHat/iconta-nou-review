"""
core/migrare_texte_control_fiscal.py — notificările de control fiscal scrise înainte de lotul 13 spun culoarea pe care o arată ecranul.

Comanda 13.1, deficiența 570 (anexa, verbatim): „Notificarea «2 controale fiscale în roșu (TVA, D112)» la F6, dar detaliul firmei arată
doar galben (ciornă / stat necontabilizat): aceeași regulă de culoare în ambele locuri.” Regula ecranului (deficiența 220, decizia Costin
10.10.2026: „Roșu înseamnă termen depășit.”): o constatare se arată cel mult galben, „de urmărit” (`control_verdict.stareAfisata`). Textul
notificării noi îl scrie `core.alerte_control_fiscal.text_alerta`.

DATELE EXISTENTE: notificările deja scrise în clopoțel (`tip = 'control_fiscal'`) primesc aceeași formă: „N controale fiscale în roșu (…)”
-> „N controale fiscale de urmărit (…)”, iar eticheta „D390 (intracom.)” -> „D390 (intracomunitare)”. Numai textul aplicației; nimic altceva
din rând. Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_texte_control_fiscal.py`.
"""
from core import db


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE public.notificari SET text = replace(replace(text, ' în roșu (', ' de urmărit ('), 'D390 (intracom.)', "
                    "'D390 (intracomunitare)') WHERE tip = 'control_fiscal' AND (text LIKE '% în roșu (%' OR text LIKE '%(intracom.)%')")


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 0 FROM public.notificari WHERE tip = 'control_fiscal' AND text LIKE '% în roșu (%'")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_texte_control_fiscal: %s" % ("nicio notificare veche rămasă" if verifica(conn) else "RĂMASE"))


if __name__ == "__main__":
    _main()
