"""Concurență și recuperare între jurnal și OPRIT; callback-uri locale fizice."""
import fcntl
from multiprocessing import get_context
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

if (Path(__file__).resolve().parents[1]/"scripts/reguli_publicare_migrare.py").is_file():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from reguli_publicare_migrare import Plan, Refuz, inchide_sub_lacat

plan=Plan("17.5-P","a"*40,"b"*40,"core/migrare_exemplu.py","c"*64,"bonuri","cui_cumparator")
idop="id-proba"

def apel(d, intrerupe=None):
    d=Path(d)
    def citeste(nume):
        path=d/nume
        if not path.exists(): return None
        rows=path.read_text().splitlines()
        if len(rows)!=1: raise Refuz("Inchideri multiple")
        return tuple(rows[0].split())
    def scrie(nume,valori):
        with (d/nume).open("a") as f:
            f.write(" ".join(valori)+"\n"); f.flush(); os.fsync(f.fileno())
        if intrerupe==nume: raise InterruptedError(nume)
    with (d/"lacat").open("a") as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        inchide_sub_lacat(plan,idop,lambda:citeste("jurnal"),lambda:citeste("oprit"),
            lambda:scrie("jurnal",(plan.lot,plan.e,idop)),lambda:scrie("oprit",(plan.lot,plan.e)))


class Inchidere(unittest.TestCase):
    def assertInchidereUnica(self,d):   # [17.5-P0] ajutorul de aserție, cu nume assert* (contorul static al porții)
        self.assertEqual((d/"jurnal").read_text().splitlines(),[" ".join((plan.lot,plan.e,idop))])
        self.assertEqual((d/"oprit").read_text().splitlines(),[" ".join((plan.lot,plan.e))])

    def test_procese_concurente(self):
        with TemporaryDirectory() as cale:
            with get_context("spawn").Pool(3) as pool: pool.map(apel,[cale]*6)
            self.assertInchidereUnica(Path(cale))

    def test_reia_dupa_jurnal_sau_dupa_semnal(self):
        for pas in ("jurnal","oprit"):
            with self.subTest(pas=pas), TemporaryDirectory() as cale:
                with self.assertRaises(InterruptedError): apel(cale,pas)
                apel(cale); apel(cale); self.assertInchidereUnica(Path(cale))

    def test_stari_contradictorii(self):
        for nume,text in [("jurnal","P alt E"),("jurnal","x\nx"),("oprit","17.5-P "+plan.e)]:
            with self.subTest(nume=nume), TemporaryDirectory() as cale:
                d=Path(cale); (d/nume).write_text(text+"\n")
                with self.assertRaises(Refuz): apel(cale)
                self.assertEqual((d/nume).read_text(),text+"\n")


if __name__=="__main__": unittest.main(verbosity=2)
