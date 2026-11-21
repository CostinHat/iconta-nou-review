"""Martorul fiscal P. Conexiune exclusiv la baza iconta_test, din test.env.
Parcurs: semana_bon.py --parcurs [argumentele lansatorului oficial].
E2E: with martor(tenant_id) as bon_id. Curățarea folosește cheia returnată de INSERT.
"""
import contextlib
from pathlib import Path
import subprocess
import sys

COMERCIANT = "Benzinarie Martor P SRL"
DOCUMENT = "P-1"
CUI_F1 = "401002001"
F1 = "F1 Comert Stoc SRL"


def _env():
    valori = {}
    for linie in (Path.home() / ".iconta" / "test.env").read_text(encoding="utf-8").splitlines():
        linie = linie.strip().removeprefix("export ")
        if not linie or linie.startswith("#") or "=" not in linie:
            continue
        nume, valoare = linie.split("=", 1)
        valoare = valoare.strip()
        if len(valoare) >= 2 and valoare[0] == valoare[-1] and valoare[0] in ("'", '"'):
            valoare = valoare[1:-1]
        valori[nume.strip()] = valoare
    if valori.get("DB_NAME") != "iconta_test":
        raise RuntimeError("Fixture indisponibilă: DB_NAME din test.env")
    return {k: valori["DB_" + v] for k, v in
            (("dbname", "NAME"), ("user", "USER"), ("host", "HOST"),
             ("port", "PORT"), ("password", "PASSWORD"))}


def _tinta(cur, tenant_id):
    cur.execute("SELECT current_database()")
    if cur.fetchone() != ("iconta_test",):
        raise RuntimeError("Fixture indisponibilă: baza curentă")
    cur.execute("SELECT schema_name, nume, cui::text FROM public.tenants "
                "WHERE id = %s AND activ IS TRUE", (tenant_id,))
    if cur.fetchone() != ("tenant_9049", F1, CUI_F1):
        raise RuntimeError("Fixture indisponibilă: tenantul F1 din snapshot nu corespunde")
    cur.execute("SELECT cui::text FROM tenant_9049.firma_profil WHERE id = 1")
    if cur.fetchone() != (CUI_F1,):
        raise RuntimeError("Fixture indisponibilă: CUI în profilul F1")


@contextlib.contextmanager
def martor(tenant_id):
    import psycopg2
    from psycopg2.extras import Json
    with contextlib.closing(psycopg2.connect(**_env(), connect_timeout=8)) as conn:
        # Lacăt de sesiune între INSERT și DELETE, inclusiv în timpul citirii din browser.
        with conn, conn.cursor() as cur:
            _tinta(cur, tenant_id)
            cur.execute("SELECT pg_try_advisory_lock(hashtext('iconta_test/17_5_P/F1'))")
            if not cur.fetchone()[0]:
                raise RuntimeError("Fixture ocupată de o altă probă")
            cur.execute("SELECT count(*) FROM tenant_9049.bonuri")
            if cur.fetchone() != (0,):
                raise RuntimeError("Fixture indisponibilă: F1 conține deja bonuri")
            cur.execute("""INSERT INTO tenant_9049.bonuri
                 (comerciant,cui,data,total,tva_21,status,articole,tva,nr_imagini,bon_complet,
                  tip,numar_document,orientare,cui_cumparator)
                 VALUES (%s,'14399840','2026-11-02',60.50,10.50,'de_verificat',%s,%s,
                         0,true,'bon',%s,0,'') RETURNING id""",
                        (COMERCIANT, Json([dict(denumire="Motorina", valoare=60.50,
                                                cota_tva=21, cont_propus="6022")]),
                         Json([dict(cota=21, valoare=10.50)]), DOCUMENT))
            bon_id = cur.fetchone()[0]
        try:
            yield bon_id
        finally:
            with conn, conn.cursor() as cur:
                cur.execute("DELETE FROM tenant_9049.bonuri WHERE id=%s AND comerciant=%s "
                            "AND numar_document=%s AND status='de_verificat'",
                            (bon_id, COMERCIANT, DOCUMENT))
                if cur.rowcount != 1:
                    raise RuntimeError("Curățare neconfirmată pentru martorul creat")


def main(argv):
    if argv[:1] != ["--parcurs"]:
        raise SystemExit("Folosire: semana_bon.py --parcurs [argumentele lansatorului]")
    rest = argv[1:]
    if rest.count("--lot") != 1 or rest[rest.index("--lot") + 1:][:1] != ["17.5-P2"]:
        raise SystemExit("Se cere parcursul oficial pentru 17.5-P2")
    if any(arg == "--baza" or arg.startswith("--baza=") for arg in rest):
        raise SystemExit("Parcursul P folosește baza URL locală implicită")
    script = Path.cwd() / "scripts" / "lanseaza_verificator.py"
    with martor(105779):
        print("semanat: 1", flush=True)
        return subprocess.run([sys.executable, str(script), *rest], check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
