from pathlib import Path
import csv,hashlib,json,sys,re
from verifica_grila_Q7 import confrunta_rezumat, grila, sha, citeste
P=Path(__file__).resolve().parent
E="7d9536586ec0da47811f85191d0c7d18efa47811"
def genereaza(destinatie):
    det=P/"masurare_pilot_v3_24_11_detaliat.tsv"
    rez=P/"masurare_pilot_v3_24_11.csv"
    comp=P/"comparatie_v2_v3.tsv"
    asteptate=json.loads((P/"amprente_acceptare_Q7.json").read_text())
    assert all(sha(P/n)==v for n,v in asteptate.items())
    baza=grila(det)
    rezultat=confrunta_rezumat(det,rez)
    cheie=lambda r:(r["cod"],r["criteriu"],r["rezolutie"])
    comparatie={cheie(r):r for r in citeste(comp)}
    assert len(citeste(comp))==len(comparatie)==540 and baza.keys()==comparatie.keys()
    scenarii={s.split(" · ",1)[0]:s for s in (P/"scenarii_sursa_C3.txt").read_text().splitlines() if re.match(r"^(F\d{3}|X\d{2}) · ",s)}
    scenarii.update({r["cod"]:r["scenariu"] for r in citeste(P/"scenarii_corectii_Q7.tsv")})
    cerinte={r["cod"]:r["conditie_verificabila"] for r in citeste(P/"criterii_functii_Q7.tsv")}
    with rez.open(encoding="utf-8-sig",newline="") as f:
        sinteza={r["Cod"]:r["Verdict"] for r in csv.DictReader(f)}
    probe=citeste(P/"probe_plan.tsv")
    criterii={
        "Funcțional":"Parcurge operația completă și confruntă rezultatul, identitatea și starea documentului cu sursa.",
        "Aspect":"Pe rezoluția indicată verifică încadrarea, accesul la fiecare coloană și control, derularea și textul complet.",
        "Design":"Măsoară acțiunea principală, stările, denumirile și comenzile accesibile în ecranul și rolul scenariului.",
        "Simplitate":"Execută pașii din scenariu și verifică ordinea, motivele, lipsa repetițiilor și accesul direct la remediere.",
        "Conformitate":"Compară datele, sumele, stările, documentele sau regulile scenariului cu martorii independenți aplicabili.",
        "Stabilitate":"Repetă gestul scenariului. Păstrează jurnalul, răspunsul și datele înainte/după, inclusiv calea care a eșuat."
    }
    with destinatie.open("x",encoding="utf8",newline="") as f:
        out=csv.writer(f,delimiter="\t",lineterminator="\n")
        out.writerow(["E_R2","cod","criteriu","rezolutie","valoare_v3","observatie_v3","provenienta_v3","localizare_v3","verdict_functie_v3","scenariu","probe","conditie_functie","verificare_criteriu","tinta"])
        for nr,r in enumerate(citeste(det),2):
            k=cheie(r);cod,crit,dim=k; m=comparatie[k]
            assert m["v3"]==r["valoare"]
            ids=" ".join(x["id"] for x in probe if cod in x["coduri"].split())
            out.writerow([E,*k,r["valoare"],r["observatie"],m["sursa_v3"],f"{det.name}#{nr}",sinteza[cod],scenarii[cod],ids or "Scenariu canonic integral de regresie",cerinte[cod],criterii[crit],"1"])
    return rezultat
if __name__=="__main__":
    print(json.dumps(genereaza(Path(sys.argv[1])),ensure_ascii=False))
