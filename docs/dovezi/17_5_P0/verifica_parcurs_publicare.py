"""Judecă urmele din mediul de calibrare. Se lansează pe directorul celor 12 familii de probe.
Fiecare .jsonl: o observație per linie, ordinea scrierii sub lacăt; schema în comanda lotului."""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

CAZURI = {
    "I01": ["normal"], "I02": ["asteptare"], "I03": ["migrare_in_plus","drift","necunoscut"],
    "I04": ["alt_E","alt_C","alt_lot","alt_digest","worktree","local"],
    "I05": ["vechi","lipsa","ilizibil","serviciu_esuat","alta_db","alt_acord","invocatie_inlocuita","doua_locale","doar_off_site"],
    "I06": ["complet"], "I07": ["registru","marcata","tip","nullable","implicit"],
    "I08": ["restart","static","worker","backup_git"], "I09": ["concurenta"],
    "I10": ["dupa_registru","dupa_restart","dupa_jurnal","dupa_oprit"],
    "I11": ["ddl_necunoscut"], "I12": ["eligibil","peste_miezul_noptii"]}
EV = set("poarta pass push asteapta succesor_refuzat acord backup ddl registru schema static restart fourway publicat oprit alerta succesor_eligibil revenire intrerupere reconciliere scriere_db acces_scriere concurenta alta_zi ref_backup restart_legacy confirmare_operator".split())

def cere(ok, mesaj):
    if not ok: raise ValueError(mesaj)

def verifica(grupa,caz,rows):
    h=rows[0]
    cere(h.get("tip")=="identitate" and h.get("caz")==grupa+"-"+caz and
         all(re.fullmatch(r"[0-9a-f]{40}",h.get(x,"")) for x in ("c","e")), "antet sau SHA")
    ev=[]
    cere(h.get("conditie")==caz, "conditie injectata diferita")
    for row in rows[1:-1]:
        name=row.get("eveniment")
        cere(name in EV and row.get("sha")==h["c" if name=="poarta" else "e"], "eveniment/commit")
        cere(isinstance(row.get("sursa"),str) and row["sursa"].strip(), "sursa lipsa")
        ev.append(name)
    sf=rows[-1]; cere(sf.get("tip")=="iesire" and type(sf.get("rc")) is int, "lipseste iesirea CLI")
    def exact(name,n): cere(ev.count(name)==n, f"{name} gasit {ev.count(name)}, cerut {n}")
    def ordine(*names):
        i=-1
        for name in names:
            i=ev.index(name,i+1)
    def lipsesc(*names):
        for name in names: exact(name,0)
    for name in ("poarta","pass","push"): exact(name,1)
    ordine("poarta","pass","push")
    if grupa != "I01":
        lipsesc("restart_legacy")
    if grupa == "I06":
        exact("confirmare_operator",1)
        ordine("registru","confirmare_operator","restart")
        confirma = next(row for row in rows[1:-1] if row["eveniment"]=="confirmare_operator")
        apel = json.loads(confirma["extras"])
        lot = h.get("lot", "")
        operatie = h.get("operatie", "")
        cere(re.fullmatch(r"\d+(?:\.\d+)*-[A-Z]+\d*", lot) and
             re.fullmatch(r"[0-9]+-[0-9]+", operatie), "lot/operatie in antet")
        argv = apel.get("argv")
        cere(isinstance(argv,list) and len(argv)>=4 and
             Path(argv[-4]).parts[-2:]==("scripts","publica_lot.sh") and
             argv[-3:]==["--confirma-migrare",lot,h["e"]] and
             apel.get("operatie")==operatie and type(apel.get("pid")) is int and apel["pid"]>0,
             "confirmarea nu provine din apelul operatorului pentru aceasta operatie")
    if grupa in ("I01","I06","I09","I10","I12"):
        for name in ("restart","fourway","publicat","oprit","alerta"): exact(name,1)
        cere(sf["rc"]==0 and sf.get("stare")=="publicat","terminal publicat")
        exact("static",1)
        ordine("push","static","restart","fourway","publicat","oprit","alerta")
        if grupa=="I01":
            lipsesc("asteapta","ddl"); return
        for name in ("asteapta","backup","acord","ddl","registru"): exact(name,1)
        ordine("push","asteapta","acord","backup","ddl","registru","schema","static")
        if grupa=="I09":
            exact("concurenta",1)
            ordine("asteapta","concurenta","revenire","revenire","publicat","revenire")
            cere(ev.count("revenire")>=3, "doua continuari plus repetarea")
        if grupa=="I10":
            exact("intrerupere",1)
            anterior={"dupa_registru":"registru","dupa_restart":"restart","dupa_jurnal":"publicat","dupa_oprit":"oprit"}[caz]
            ordine(anterior,"intrerupere","revenire")
        if grupa=="I12":
            ordine("asteapta","succesor_refuzat","publicat","succesor_eligibil")
            if caz=="peste_miezul_noptii": ordine("asteapta","alta_zi","ref_backup","publicat")
        return
    lipsesc("publicat","succesor_eligibil")
    if grupa=="I02":
        cere(sf["rc"]==75 and sf.get("stare")=="asteapta_migrare","asteptare")
        ordine("push","asteapta","succesor_refuzat")
        lipsesc("scriere_db","ddl","registru","static","restart","oprit","alerta"); return
    cere(sf["rc"]!=0 and sf["rc"]!=75 and sf.get("stare") in ("refuz","nepublicat","reconciliere"),"refuz real")
    cere(sf.get("motiv")==caz, "motivul refuzului difera de conditia injectata")
    if grupa in ("I03","I04","I05"): lipsesc("ddl","scriere_db","restart")
    if grupa=="I04": lipsesc("acces_scriere")
    if grupa=="I07": cere(ev.count("ddl")<=1,"DDL repetat"); lipsesc("restart")
    if grupa=="I08" and caz=="restart":
        exact("restart",1); exact("oprit",1); cere(sf["stare"]=="nepublicat","restartul esuat a fost mascat")
    if grupa=="I11":
        exact("ddl",1); lipsesc("registru","restart")
        ordine("ddl","intrerupere","revenire","reconciliere")


def sursa_bruta(root, row):
    cale=Path(row["sursa"])
    cere(not cale.is_absolute() and ".." not in cale.parts,"cale de proba nepermisa")
    real=(root/cale).resolve(strict=True)
    cere(real.is_relative_to(root.resolve()) and real.is_file(),"proba din afara directorului")
    brut=real.read_bytes()
    cere(sha256(brut).hexdigest()==row["sha256_sursa"],"SHA al probei diferit")
    rand=row["linie"]
    linii=brut.decode("utf-8").splitlines()
    cere(type(rand) is int and 1<=rand<=len(linii) and linii[rand-1].strip() and
         row["extras"]==linii[rand-1],"randul citat nu coincide cu originalul")


def main(d):
    erori=[]; total=0
    for grupa, cazuri in CAZURI.items():
        for caz in cazuri:
            total+=1
            try:
                path=d/(grupa+"-"+caz+".jsonl")
                rows=[json.loads(line) for line in path.read_text().splitlines()]
                verifica(grupa,caz,rows)
                for row in rows: sursa_bruta(d,row)
            except (OSError,KeyError,IndexError,TypeError,ValueError) as ex:
                erori.append(f"{grupa}-{caz}: {ex}")
    print(f"{total-len(erori)}/{total} trasee conforme")
    for e in erori: print(e)
    return int(bool(erori))
def proba():
    """Verifică judecătorul pe observații sintetice. Nicio intrare de publicare nu este rulată."""
    from tempfile import TemporaryDirectory
    from unittest import TestCase

    test = TestCase()
    refuzuri = []
    c, e = "c" * 40, "e" * 40
    lot, operatie = "17.5-P", "10-15"

    def randuri(grupa, caz, evenimente, stare, rc, operatie_apel=operatie):
        antet = dict(tip="identitate", caz=f"{grupa}-{caz}", conditie=caz,
                     c=c, e=e, lot=lot, operatie=operatie)
        rezultat = [antet]
        for nume in evenimente:
            rand = dict(eveniment=nume, sha=c if nume == "poarta" else e, sursa="observat.log")
            if nume == "confirmare_operator":
                rand["extras"] = json.dumps(dict(argv=["sh", "scripts/publica_lot.sh", "--confirma-migrare", lot, e],
                                                 pid=123, operatie=operatie_apel))
            rezultat.append(rand)
        return [*rezultat, dict(tip="iesire", rc=rc, stare=stare)]

    def refuz(eticheta, mesaj, apel, *argumente):
        with test.assertRaises(ValueError) as rezultat:
            apel(*argumente)
        test.assertEqual(str(rezultat.exception), mesaj)
        refuzuri.append(eticheta)

    asteptare = "poarta pass push asteapta succesor_refuzat".split()
    complet = ("poarta pass push asteapta acord backup ddl registru confirmare_operator schema "
               "static restart fourway publicat oprit alerta").split()

    def i02(evenimente, rc=75):
        verifica("I02", "asteptare", randuri("I02", "asteptare", evenimente, "asteapta_migrare", rc))

    def i06(evenimente, operatie_apel=operatie):
        verifica("I06", "complet", randuri("I06", "complet", evenimente, "publicat", 0, operatie_apel))

    i02(asteptare)
    i06(complet)
    refuz("OPRIT în așteptare", "oprit gasit 1, cerut 0", i02, asteptare + ["oprit"])
    refuz("succes în loc de 75", "asteptare", i02, asteptare, 0)
    refuz("restart pe calea veche", "restart_legacy gasit 1, cerut 0", i06, complet + ["restart_legacy"])
    refuz("confirmare lipsă", "confirmare_operator gasit 0, cerut 1", i06,
          [nume for nume in complet if nume != "confirmare_operator"])
    refuz("altă operație", "confirmarea nu provine din apelul operatorului pentru aceasta operatie",
          i06, complet, "10-16")
    refuz("restart dublat", "restart gasit 2, cerut 1", i06, complet + ["restart"])

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        brut = b"confirmare observata\n"
        (root / "observat.log").write_bytes(brut)
        sursa = dict(sursa="observat.log", extras="confirmare observata", linie=1, sha256_sursa=sha256(brut).hexdigest())
        sursa_bruta(root, sursa)
        refuz("amprentă eronată", "SHA al probei diferit", sursa_bruta, root, sursa | {"sha256_sursa": "0"*64})
        refuz("citat diferit de jurnal", "randul citat nu coincide cu originalul",
              sursa_bruta, root, sursa | {"extras": "alt eveniment"})

    for eticheta in refuzuri:
        print("REFUZ CONFIRMAT:", eticheta)
    print(f"PROBE OK: {len(refuzuri)} negative, I02/I06 și sursa validă acceptate")


if __name__=='__main__':
    if sys.argv[1:] == ['--proba']:
        proba()
        sys.exit(0)
    sys.exit(main(Path(sys.argv[1])))
