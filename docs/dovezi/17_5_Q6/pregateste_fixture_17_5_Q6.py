"""Fixture pentru copia restaurată. Pornește din checkout-ul de test cu venv-ul proiectului.
python pregateste_fixture_17_5_Q6.py DIRECTOR_NOU. Produce numai inventarul fără secrete.
Restaurarea finală prin unealta oficială elimină datele de lucru.
"""
import io
import json
import os
import re
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from xml.sax.saxutils import escape
from zipfile import ZipFile

def verifica_vies(status, raspuns):
    if status != 200 or not isinstance(raspuns, dict) or raspuns.get("valid") is not True or raspuns.get("tara") != "DE":
        raise ValueError("Fixture F172: VIES nu a confirmat clientul DE")


def verifica_mediu(baza, env, query):
    u = urlsplit(baza)
    if u.scheme != "http" or u.hostname not in {"127.0.0.1", "localhost"} or u.port != 8019:
        raise ValueError("Se cere aplicația copiei locale pe 8019")
    for key in ("ICONTA_EMAIL_CUTIE", "ICONTA_ANAF_SIMULAT"):
        if not env.get(key) or not Path(env[key]).is_dir():
            raise ValueError("Directorul de test lipsește: "+key)
    if query("SELECT current_database()")[0][0] != "iconta_test":
        raise ValueError("Se cere iconta_test")
    return Path(env["ICONTA_EMAIL_CUTIE"])


def main(out):
    from playwright.sync_api import sync_playwright
    rad=Path.cwd()
    sys.path.insert(0,str(rad))
    sys.path.insert(0,str(rad/"frontend_test/e2e"))
    from conftest import BAZA, Ecran, sesiune, sql, cui_cu_control, _db
    from core import tenant_provisioning, spv_receive
    from e2e_bloc_a import AZI, pregateste_firma, _api
    from e2e_lot12_emit import _intrari, _vies, _emiterea
    from e2e_lot6 import UBL_PRIMITA
    mail = verifica_mediu(BAZA, os.environ, sql)
    out.mkdir(parents=True,exist_ok=False)
    tag=uuid.uuid4().hex[:10]
    db=_db(); name=f"Q6 {tag} SRL"; email="patron@prisma-cont.test"
    uid,cab=sql("SELECT id,accounting_firm_id FROM public.users WHERE email=%s",(email,))[0]
    with db.get_conn() as conn:
        res=tenant_provisioning.provision_tenant(conn,name,cui_cu_control(90000000+int(tag,16)%9000000),cab,uid,
             (rad/"tenant_template.sql").read_text(),tip_firma="srl")
        conn.commit()
    tid=res["tenant_id"]; schema=res["schema_name"]
    if not re.fullmatch(r"tenant_[0-9]+",schema):raise ValueError("Schema firmei de test este invalidă")
    firma={"schema":schema,"nume":name,"tenant_id":tid,"cabinet_id":cab}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        ctx=browser.new_context()
        try:
            ctx.add_init_script(sesiune(email));pg=ctx.new_page();pg.goto(BAZA+"/")
            ec=Ecran(pg,"pregatire_Q6");pregateste_firma(ec,firma)
            marfa="Articol Q6 "+tag
            _intrari(firma,[(marfa,20,4)])
            inainte=[r[0] for r in sql(f'SELECT id FROM "{schema}".facturi ORDER BY id')]
            _vies(pg)
            _emiterea(ec,firma)
            pg.fill("#em-cui","DE123456789")
            pg.dispatch_event("#em-cui","change")
            with pg.expect_response(lambda r: urlsplit(r.url).path == f"/tenants/{tid}/verifica-vies"
                                    and parse_qs(urlsplit(r.url).query).get("cod_tva") == ["DE123456789"]) as cerere_vies:
                pg.click("#em-verifica")
            raspuns_vies = cerere_vies.value
            verifica_vies(raspuns_vies.status, raspuns_vies.json())
            pg.locator("#em-cui-stare .em-cui-info").filter(has_text=re.compile(r"^valid în VIES\s*·\s*DE$")).wait_for()

            pg.fill("#em-oras","Berlin")
            pg.fill("#em-l0-cauta-articol",marfa)
            sel=pg.locator("#em-l0-articol")
            sel.select_option(label=sel.locator("option",has_text=marfa).inner_text())
            pg.wait_for_function("den => document.querySelector('#em-l0-descriere').value === den",arg=marfa)
            pg.fill("#em-l0-cantitate","2")
            pg.fill("#em-l0-pret_unitar","100")
            pg.select_option("#em-l0-cota","0")
            pg.select_option("#em-l0-categorie","livrare_ic")
            pg.locator("#em-l0-pret_unitar").blur()
            # Reopen in a clean page in the actual F172 protocol; a persisted draft must exist first.
            import time
            until=time.monotonic()+12
            while True:
                drafts=sql("SELECT continut::text FROM public.ciorne_formular WHERE tenant_id=%s AND user_id=%s AND formular='factura'",(tid,uid))
                if any(marfa in row[0] and "DE123456789" in row[0] for row in drafts): break
                if time.monotonic()>=until:raise ValueError("Ciorna F172 nu este stocată pe copie")
                time.sleep(0.2)
            numar="Q6-"+tag
            cif=re.sub(r"\D","",sql(f'SELECT cui FROM "{schema}".firma_profil WHERE id=1')[0][0])
            xml=UBL_PRIMITA.format(numar=numar,client=escape(name),cui=cif).encode()
            ar=io.BytesIO()
            with ZipFile(ar,"w") as z:z.writestr(numar+".xml",xml)
            msg={"id":tag,"cif_beneficiar":cif,"cif_emitent":"40372003","tip":"FACTURA PRIMITA","id_solicitare":tag}
            from collections import Counter
            stat=Counter()
            # Only the external transport is replaced. The official parser, deduplication and repository run normally.
            with patch.object(spv_receive.efs,"descarca",return_value=SimpleNamespace(status_code=200,content=ar.getvalue())):
                spv_receive.importa_mesaj(schema,None,cif,msg,stat)
            saved=sql(f'SELECT id,status,xml_sha256 FROM "{schema}".efactura_primite WHERE id_mesaj_anaf=%s',(tag,))
            from hashlib import sha256
            if len(saved)!=1 or saved[0][1:] not in [( "ciorna",sha256(xml).hexdigest()),["ciorna",sha256(xml).hexdigest()]]:
                raise ValueError("Factura SPV nu a trecut prin parser")
            (out/"factura_sursa.xml").write_bytes(xml)
            invitati={}
            for w in (603,1366):
                addr=f"q6.{tag}.{w}@exemplu.test"
                ans=_api(ec,"POST","/asistenti",{"nume":f"Asistent Q6 {w}","email":addr,"poate_pregati":True,
                           "poate_valida":False,"poate_depune":False,"firme":[tid]})
                if ans["status"] not in (200,201) or not ans["json"].get("ok") or ans["json"].get("email_trimis") is False:
                    raise ValueError("Crearea invitației locale a eșuat")
                scrisori=[json.loads(f.read_text()) for f in mail.glob("*_"+''.join(c if c.isalnum() else '_' for c in addr)+".json")]
                if len([scr for scr in scrisori if scr.get("catre")==addr and "#activare=" in scr["html"]])!=1:
                    raise ValueError("Lipsește invitația locală unică")
                invitati[w]={"user_id":ans["json"]["user_id"],"email_test":addr,"firme":[tid],"drepturi":[True,False,False]}
            num=_api(ec,"GET",f"/tenants/{tid}/facturi/numerotare?data={AZI.isoformat()}")
            if num["status"]!=200 or not num["json"].get("serie"):raise ValueError("Numerotarea lipsește")
            receipt={"lot":"17.5-Q6","baza_date":"iconta_test","firma":firma,
                     "P-F172":{"articol":marfa,"cantitate_stoc":20,"pret_intrare":4,"client":"DE123456789",
                               "cantitate_factura":2,"pret_factura":100,"serie":num["json"]["serie"],"facturi_initiale":inainte},
                     "P-F179":{"id_intern":saved[0][0],"id_mesaj":tag,"numar":numar,"furnizor":"FURNIZOR E2E SRL","total":"121.00","moneda":"RON","sha256_xml":saved[0][2]},
                     "P-X02":invitati}
            (out/"fixture.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
        finally:ctx.close();browser.close()
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
