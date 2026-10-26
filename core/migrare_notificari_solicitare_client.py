"""
core/migrare_notificari_solicitare_client.py — „O solicitare nouă de la un client” bifată și la conturile care și-au salvat deja bifele.

Deficiența 566 (comanda Costin 13.1, verbatim): „«O solicitare nouă de la un client» e debifată implicit la administrator; mesajele
clienților pot trece neobservate.” Codul (`core/notificari.py`, `TIPURI["solicitare_client"]["implicit"]`) o bifează din oficiu de acum.

DATELE EXISTENTE: ecranul Setări cont → Notificări trimite la „Salvează” TOATE bifele pe care omul le vede (`uc_cont_notificari.canal_seteaza`),
deci un cont care a salvat o dată cât implicitul era greșit are `notificari_tipuri.solicitare_client = false` scris în bază, fără să fi
ales asta (bifa îi apărea goală din oficiu). Contul NU se poate deosebi de unul care a debifat-o cu intenție: nu există nicio urmă a
schimbării bifei. Varianta sigură pentru contabil (mesajul clientului nu trece neobservat): bifa se pune la loc pe toate conturile
cabinetelor (nu și la clienți / superadmini, care nu văd tipul); omul o poate debifa din nou, iar de acum alegerea lui rămâne.
Alternativa respinsă: a lăsa bifele salvate cum sunt — mesajele clienților ar rămâne nesemnalate pe email exact la conturile care au
apucat să salveze (prima intrare a lotului 7 cerea salvarea), adică tocmai cazul raportat.

Pragul = momentul PRIMEI rulări (rândul ei din `public.migrari_rulate`, scris de rulator; la prima rulare, acum): bifele salvate
înaintea lui au văzut implicitul greșit; o bifă debifată DUPĂ el e alegerea omului (implicitul era deja corect) și nu se atinge — deci o a
doua rulare nu schimbă nimic (idempotent).
Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_notificari_solicitare_client.py`.
"""
from core import db
from core.migrari_registru import DDL as _DDL_REGISTRU

FISIER = "core/migrare_notificari_solicitare_client.py"
#: pragul: momentul primei rulări (publicarea reparației); bifele salvate înainte au implicitul greșit, cele de după sunt alegeri
PRAG = ("(SELECT COALESCE(MIN(rulat_la), now()) FROM public.migrari_rulate WHERE fisier = '%s')" % FISIER)

SQL = """
UPDATE public.users
   SET notificari_tipuri = jsonb_set(notificari_tipuri, '{solicitare_client}', 'true'::jsonb)
 WHERE rol IN ('admin_firma', 'angajat')
   AND notificari_tipuri ? 'solicitare_client'
   AND notificari_tipuri->>'solicitare_client' = 'false'
   AND (notificari_salvate_la IS NULL OR notificari_salvate_la < """ + PRAG + """)
"""


def aplica(conn):
    """Întoarce câte conturi au primit bifa înapoi."""
    with conn.cursor() as cur:
        cur.execute(_DDL_REGISTRU)   # pragul se citește din registru (o bază fără registru: prima rulare, pragul = acum)
        cur.execute(SQL)
        return cur.rowcount


def ramase(conn):
    """Câte conturi ale cabinetelor, salvate înaintea pragului, au încă bifa „nu” (0 după aplicare)."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.users WHERE rol IN ('admin_firma', 'angajat') "
                    "AND notificari_tipuri->>'solicitare_client' = 'false' "
                    "AND (notificari_salvate_la IS NULL OR notificari_salvate_la < " + PRAG + ")")
        return cur.fetchone()[0]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        n = aplica(conn)
        conn.commit()
        print("migrare_notificari_solicitare_client: %d conturi cu bifa pusă la loc; rămase: %d" % (n, ramase(conn)))


if __name__ == "__main__":
    _main()
