"""Probe r2, fără rețea/servicii; rulează direct sau prin discovery."""
from datetime import datetime,timezone
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here if (here/'canal_migrare.py').exists() else here.parent/'scripts'))
import canal_migrare as m

def cmd(*args,cwd=None):
    return subprocess.check_output(args,cwd=cwd,stderr=subprocess.PIPE).decode().strip()

class Delta(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.d=Path(t.name);self.repo=self.d/'repo';self.repo.mkdir();self.key=self.d/'semnatar'
        cmd('ssh-keygen','-q','-t','ed25519','-N','','-f',str(self.key))
        self.git('init','-q','-b','main')
        self.git('config','user.name','Test');self.git('config','user.email','test@example.invalid')
        f=self.repo/m.SEMNATARI;f.parent.mkdir()
        self.anchor=f; f.write_text('costin namespaces="'+m.NAMESPACE+'" '+' '.join(self.key.with_suffix('.pub').read_text().split()[:2])+'\n')
        self.git('add','.'); self.base=self.commit('baza'); self.c=self.commit('C'); self.e=self.commit('E')
        self.plan=SimpleNamespace(lot="17.5-P",c=self.c,e=self.e,fisier='core/migrare_exemplu.py',digest='a'*64)
        self.op='17-9999';self.data=dict(versiune=1,decizie='APROB_MIGRAREA',lot=self.plan.lot,c=self.c,e=self.e,
                fisier=self.plan.fisier,sha256_migrare=self.plan.digest,operatie=self.op,emis_la='2026-11-21T04:00:00Z')
        self.cand=datetime(2026,11,21,4,0,0,tzinfo=timezone.utc)
    def git(self,*a): return cmd('git','-c','core.hooksPath=/dev/null','-C',str(self.repo),*a)
    def commit(self,mesaj):
        self.git('commit','-qm',mesaj,'--allow-empty');return self.git('rev-parse','HEAD')
    def semneaza(self,obj=None,key=None,namespace=None):
        raw=m.canon(obj or self.data);p=self.d/'acord';p.write_bytes(raw)
        sig=p.with_suffix('.sig');sig.unlink(missing_ok=True)
        cmd('ssh-keygen','-Y','sign','-n',namespace or m.NAMESPACE,'-f',str(key or self.key),str(p))
        return raw,sig.read_bytes()
    def verifica(self,raw,sig):
        return m.verifica_acord(self.repo,self.base,raw,sig,self.plan,self.op,self.cand,self.cand)
    def test_semnatura_reala_si_octeti(self):
        raw,sig=self.semneaza();self.assertEqual(self.verifica(raw,sig)[1],self.cand)
        for alt in (raw.replace(b'APROB',b'REFUZ'),raw+b' ',raw.replace(b'"versiune":1',b'"versiune":1,"versiune":1')):
            with self.subTest(alt=alt),self.assertRaises(ValueError): self.verifica(alt,sig)
    def test_aprobari_straine(self):
        for k,v in [('lot','17.5-Q'),('e','b'*40),('c','f'*40),('fisier','core/migrare_alta.py'),
                    ('sha256_migrare','0'*64),('operatie','1-2'),('emis_la','2026-11-21T03:59:59Z')]:
            with self.subTest(k=k),self.assertRaises(ValueError): self.verifica(*self.semneaza(self.data|{k:v}))
    def test_cheie_si_namespace(self):
        key=self.d/'alta';cmd('ssh-keygen','-q','-t','ed25519','-N','','-f',str(key))
        with self.assertRaises(ValueError): self.verifica(*self.semneaza(key=key))
        with self.assertRaises(ValueError): self.verifica(*self.semneaza(namespace='alt-scop'))
    def test_refuz_ancora_schimbata(self):
        self.anchor.write_text(self.anchor.read_text()+'\n');self.git('add','.');self.plan.e=self.commit('alta ancora')
        self.data['e']=self.plan.e
        with self.assertRaises(ValueError): self.verifica(*self.semneaza())
    def test_ref_din_prima_zi_in_git_real(self):
        origin=self.d/'origin.git';cmd('git','init','--bare','-q',str(origin))
        self.git('remote','add','origin',str(origin)); ref='refs/heads/backup/lant-2026-11-21'
        m.retine_ref(self.repo,self.e,self.op,ref)
        with self.assertRaises(subprocess.CalledProcessError):m.ref_confirmat(self.repo,self.e,self.op)
        self.git('push','-q','origin',self.e+':'+ref)
        self.assertEqual(m.ref_confirmat(self.repo,self.e,self.op),ref)
        with self.assertRaises(ValueError):m.retine_ref(self.repo,self.e,self.op,'refs/heads/backup/lant-2026-11-22')
        with self.assertRaises(OSError):m.ref_confirmat(self.repo,self.e,'17-10000')
        self.git('push','-q','origin',':'+ref)
        self.git('push','-q','origin',self.c+':'+ref)
        with self.assertRaises(ValueError):m.ref_confirmat(self.repo,self.e,self.op)
    def test_backup_atribuire_si_timp(self):
        cale='/var/backups/iconta/iconta_v2_20261121_045700.dump'
        info=dict(serviciu='iconta-backup.service',rc=0,baza='iconta_v2',e=self.e,invocatie='a'*32,
           invocatie_jurnal='a'*32,inceput_ns=30,sfarsit_ns=40,cale=cale,cale_invocatie=cale,
           arhive_noi=[cale],pg_restore_l_rc=0,db_antet='iconta_v2',sha256='e'*64,octeti=10)
        self.assertEqual(m.coroboreaza_backup(info,self.e,10,25,42),'e'*64)
        for key,value in dict(rc=1,inceput_ns=23,sfarsit_ns=43,invocatie_jurnal='b'*32,
               db_antet='iconta_test',arhive_noi=[cale,cale],cale_invocatie='veche',pg_restore_l_rc=1).items():
            with self.subTest(key=key),self.assertRaises(ValueError):
                m.coroboreaza_backup(info|{key:value},self.e,10,25,42)

class BackupManual(unittest.TestCase):
    def test_calea_invocatiei_manual_pornite(self):
        start = int(datetime.fromisoformat("2026-11-21T03:00:01+02:00").timestamp()) * 10**9
        stop = start + 4 * 10**9
        cale = "/var/backups/iconta/iconta_v2_20261121_030001.dump"
        local = "2026-11-21T03:00:03+02:00 backup LOCAL OK: " + cale + " (5.2M)"
        offsite = local.replace("LOCAL OK","OFF-SITE OK")
        def extract(rows, anterior="0"*32, observat="1"*32):
            return m.cale_backup_manual(anterior, "1"*32, observat, start, stop, rows)
        self.assertEqual(extract([local, offsite]),cale)
        for rows in ([local,local], [offsite], [local.replace("03:00:03","02:59:59")]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                extract(rows)
        for anterior,observat in (("1"*32,"1"*32),("0"*32,"2"*32)):
            with self.assertRaises(ValueError):
                extract([local],anterior,observat)

if __name__=='__main__':unittest.main(verbosity=2)
