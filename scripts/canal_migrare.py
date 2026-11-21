"""Verifică octeții aprobării și referința Git. Codul de producție apelează verifica_acord.
Nu există comandă de semnare, instalare, DDL sau backup în acest modul."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

SEMNATARI="scripts/semnatar_migrare.allowed_signers"
NAMESPACE="iconta-publicare-migrare-v1"
CHEI={"versiune","decizie","lot","c","e","fisier","sha256_migrare","operatie","emis_la"}

def cere(conditie, mesaj):
    if not conditie: raise ValueError(mesaj)

def canon(obj):
    return (json.dumps(obj,ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()

def _incarca(raw):
    def perechi(p):
        if len(dict(p))!=len(p): raise ValueError("Cheie duplicata")
        return dict(p)
    obj=json.loads(raw,object_pairs_hook=perechi)
    cere(isinstance(obj,dict) and set(obj)==CHEI and raw==canon(obj),"Formatul acordului difera")
    return obj

def _verifica(raw, semnatura, semnatari, plan, operatie, inceput, acum):
    obj=_incarca(raw)
    cere(type(obj['versiune']) is int and obj['versiune']==1 and obj['decizie']=="APROB_MIGRAREA","Decizie invalida")
    cere((obj["lot"],obj["c"],obj["e"],obj["fisier"],obj["sha256_migrare"],obj["operatie"])==
         (plan.lot,plan.c,plan.e,plan.fisier,plan.digest,operatie),"Acord strain operatiei")
    cere(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",obj["emis_la"]),"Data UTC gresita")
    emis=dt.datetime.fromisoformat(obj["emis_la"])
    # Precizia documentului este de o secundă; operația din aceeași secundă este permisă.
    cere(inceput.replace(microsecond=0)<=emis<=acum,"Acord in afara ferestrei")
    with tempfile.TemporaryDirectory() as d:
        sig=Path(d)/"aprobare.sig";sig.write_bytes(semnatura)
        p=subprocess.run(["/usr/bin/ssh-keygen","-Y","verify","-f",str(semnatari),"-I","costin",
                          "-n",NAMESPACE,"-s",str(sig)],input=raw,capture_output=True,timeout=10)
    cere(p.returncode==0,"Semnatura Costin nu este valida")
    return hashlib.sha256(raw).hexdigest(),emis

def verifica_acord(repo,baza,raw,semnatura,plan,operatie,inceput,acum):
    # Repo, baza si plan provin din operatia oficiala validata sub lacat, niciodata din acord.
    _cheie(repo,plan.e,operatie)
    cere(re.fullmatch(r"[a-f0-9]{40}",baza) and baza!=plan.e,"Baza neverificata")
    def git(*args):
        return subprocess.check_output(["git","-C",str(repo),*args])
    git("merge-base","--is-ancestor",baza,plan.c)
    git("merge-base","--is-ancestor",plan.c,plan.e)
    chei=[]
    for sha in (baza,plan.c,plan.e):
        cere(git("ls-tree",sha,"--",SEMNATARI).startswith(b"100644 blob "),"Ancora lipsa sau mod diferit")
        chei.append(git("show",sha+":"+SEMNATARI))
    cere(len(set(chei))==1,"Ancora de incredere a fost schimbata in lot")
    prefix='costin namespaces="'+NAMESPACE+'" '
    text=chei[0].decode()
    cere(len(text.splitlines())==1 and text.startswith(prefix) and
         re.fullmatch(r"[a-zA-Z0-9@._+-]+ [A-Za-z0-9+/=]+",text[len(prefix):].rstrip("\n")),
         "Este obligatorie o singura cheie pentru Costin si namespace-ul operatiei")
    with tempfile.TemporaryDirectory() as tmp:
        cale=Path(tmp)/"allowed_signers"; cale.write_bytes(chei[0])
        return _verifica(raw,semnatura,cale,plan,operatie,inceput,acum)


def valida_ref(ref):
    prefix="refs/heads/backup/lant-"
    cere(re.fullmatch(re.escape(prefix)+r"[0-9]{4}-[0-9]{2}-[0-9]{2}",ref),"Ref backup invalid")
    dt.date.fromisoformat(ref.removeprefix(prefix))
    return ref

def verifica_remote(repo,e,ref):
    cere(re.fullmatch("[a-f0-9]{40}",e),"E invalid")
    ref=valida_ref(ref)
    result=subprocess.run(["git","-C",str(repo),"ls-remote","--exit-code","--refs","origin",ref],
                          capture_output=True,text=True,check=True,timeout=30)
    cere(result.stdout.splitlines()==[e+"\t"+ref],"Ref-ul confirmat nu indica E")
    return ref


def _cheie(repo,e,operatie):
    cere(re.fullmatch("[a-f0-9]{40}",e) and re.fullmatch(r"[0-9]+-[0-9]+",operatie),"Cheie invalida")
    def git(*args):
        return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
    comun=Path(git("rev-parse","--path-format=absolute","--git-common-dir"))
    cere(Path(repo).resolve()/".git"==comun and git("symbolic-ref","--short","HEAD")=="main" and
         git("rev-parse","HEAD")==e,"Identitate Git diferita")
    return comun/"operatii-migrare"/e/operatie/"backup-git.json"

def retine_ref(repo,e,operatie,ref):
    cale=_cheie(repo,e,operatie)
    date=canon(dict(versiune=1,e=e,operatie=operatie,ref=valida_ref(ref)))
    cale.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=cale.parent) as tmp:
        tmp.write(date);tmp.flush();os.fsync(tmp.fileno())
        try: os.link(tmp.name,cale)
        except FileExistsError: pass
    fd=os.open(cale.parent,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
    cere(cale.read_bytes()==date,"Alta intentie exista pentru aceeasi operatie")

def ref_confirmat(repo,e,operatie):
    raw=_cheie(repo,e,operatie).read_bytes()
    obj=json.loads(raw)
    cere(raw==canon(dict(versiune=1,e=e,operatie=operatie,ref=valida_ref(obj["ref"]))),"Recipisa backup difera")
    return verifica_remote(repo,e,obj["ref"])

def cale_backup_manual(invocatie_anterioara, invocatie_la_start, invocatie_dupa,
                       inceput_ns, sfarsit_ns, linii_backup):
    """Extrage calea din porțiunea nouă a backup.log a invocației manuale observate."""
    cere(re.fullmatch(r"[a-f0-9]{32}", invocatie_la_start) and
         invocatie_anterioara != invocatie_la_start == invocatie_dupa,
         "Invocatie veche sau inlocuita")
    cere(0 < inceput_ns <= sfarsit_ns, "Intervalul invocatiei este invalid")
    sablon = (r"(?P<ora>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:Z|[+-]\d\d:\d\d)) backup LOCAL OK: "
              r"(?P<cale>/var/backups/iconta/iconta_v2_\d{8}_\d{6}\.dump) \([^()\r\n]+\)")
    potriviri = []
    for linie in linii_backup:
        m = re.fullmatch(sablon, linie.rstrip("\r\n"))
        if m is None:
            continue
        secunda = int(dt.datetime.fromisoformat(m['ora'].replace('Z','+00:00')).timestamp())
        if inceput_ns // 10**9 <= secunda <= sfarsit_ns // 10**9:
            potriviri.append(m['cale'])
    cere(len(potriviri) == 1, "Lipseste asocierea unica din backup.log")
    return potriviri[0]


def coroboreaza_backup(info, e, deschis_ns, acord_ns, acum_ns):
    """Adaptorul citește service/journal și arhiva; nu primește acest dicționar de la operator."""
    cere(info.get("serviciu")=="iconta-backup.service" and info.get("rc")==0 and
         info.get("baza")=="iconta_v2" and info.get("e")==e,"Serviciu, rezultat, baza sau E diferit")
    cere(re.fullmatch(r"[a-f0-9]{32}",info["invocatie"]) and
         info["invocatie"]==info["invocatie_jurnal"],"Invocatie neconfirmata")
    cere(max(deschis_ns,acord_ns)<=info["inceput_ns"]<=info["sfarsit_ns"]<=acum_ns,
         "Backup inceput prea devreme sau inca in lucru")
    cere(info["cale"]==info["cale_invocatie"] and
         re.fullmatch(r"/var/backups/iconta/iconta_v2_[0-9]{8}_[0-9]{6}\.dump",info["cale"]) and
         info["arhive_noi"]==[info["cale"]],"Arhiva nu apartine univoc invocatiei")
    cere(info["pg_restore_l_rc"]==0 and info["db_antet"]=="iconta_v2" and
         re.fullmatch(r"[0-9a-f]{64}",info["sha256"]) and info["octeti"]>0,"Dump neverificat")
    return info["sha256"]


if __name__=="__main__":
    import sys
    args=sys.argv[1:]
    if len(args)==4 and args[0]=="retine-ref":
        retine_ref(Path.cwd(),*args[1:])
    elif len(args)==3 and args[0]=="confirma-ref":
        print(ref_confirmat(Path.cwd(),*args[1:]))
    else: raise SystemExit(2)
