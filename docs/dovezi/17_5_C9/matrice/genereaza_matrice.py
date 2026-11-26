# -*- coding: utf-8 -*-
"""17.5-C9 pct.2–3 — matricea sursă → decizie → regulă → probă și indexul de acoperire al celor 412 repere din index_surse_C9.tsv.
Intrare: directorul în care s-a extras repere_17_5_C9.zip (SHA-256 094eb314…). Pentru fiecare reper se recalculează SHA-256 al octeților
intervalului de linii (cu terminatorii) și se confruntă cu indexul; un reper cu alt SHA oprește generarea (rc 2).
Ieșiri (în directorul dat): matrice_C9.tsv (o cerință distinctă pe rând, ID stabil PC9-nn, toate reluările ei legate de același ID) și
index_acoperire_C9.tsv (fiecare reper: trimiterea la ID sau statutul lui, cu motivul verificabil).
Uz: ./venv/bin/python docs/dovezi/17_5_C9/matrice/genereaza_matrice.py <dir_repere> <dir_iesire>"""
import csv
import hashlib
import os
import re
import sys

# ── metadatele fișierelor de decizii (revizia și autorul din text; data numai când textul o dă, altfel „deschisă”) ──
META = {
    "decizii_17_5_Q.txt": ("17.5-Q", "r2", "nedeclarat în text", "deschisă (data fișierului nu e data deciziei)"),
    "decizii_17_5_Q2.txt": ("17.5-Q2", "PRE-P0 r1", "nedeclarat în text", "deschisă"),
    "decizii_17_5_Q3.txt": ("17.5-Q3", "FINAL r2", "nedeclarat în text (868: Costin)", "deschisă; 868: 22.11.2026 (text)"),
    "decizii_17_5_Q4.txt": ("17.5-Q4", "r3 (aprobarea r2)", "Costin", "23.11.2026 03:04 (text; recipisa 2c068c09…)"),
    "decizii_17_5_Q5.txt": ("17.5-Q5", "-", "nedeclarat în text", "deschisă"),
    "decizii_17_5_Q6.txt": ("17.5-Q6", "-", "Costin", "23.11.2026 (text)"),
    "decizii_17_5_Q7.txt": ("17.5-Q7", "r2/r3", "GPT-6", "24.11.2026 (text)"),
    "decizii_17_5_Q8.txt": ("17.5-Q8", "r3 + adăugiri", "GPT-6; adăugiri Claude cu acordul lui Costin 21:02; FINAL.4 Costin", "24.11.2026 (text)"),
    "decizii_17_5_Q9.txt": ("17.5-Q9", "r1/r3", "GPT-6; FINAL.4 Costin 24.11", "25.11.2026 (text)"),
    "decizii_17_5_Q10.txt": ("17.5-Q10", "-", "GPT-6 (autor de conținut); F026 Costin 15:43", "deschisă (ziua nu e în text)"),
    "decizii_17_5_Q11.txt": ("17.5-Q11", "r2", "nedeclarat în text", "deschisă"),
    "decizii_17_5_Q12.txt": ("17.5-Q12", "r2", "Costin", "26.11.2026 (text)"),
    "acceptare_AC_17_5_Q12.tsv": ("17.5-Q12", "r2", "contractele AC ale comenzii Q12", "26.11.2026 (pornirea Q12)"),
    "note_dupa_Q12_pornire.txt": ("17.5-C9", "-", "Claude, la întrebarea lui Costin", "26.11.2026 12:35 (text)"),
}

# ── cerințele distincte: ID, origine (reperele care o formulează, ca fisier:linie), text, domeniu, stări/excepții, capitol DS, ancoră,
#    verificare mecanică, celula grilei, proba bună, proba negativă, martori ──
D = "docs/dovezi/17_5_C9"
R = []


def r(id_, surse, text, domeniu, stari, cap, verificare, celula, buna, negativa, martori, tip="design"):
    R.append(dict(id=id_, surse=surse, text=text, domeniu=domeniu, stari_exceptii=stari, capitol_ds=cap, ancora_ds="PC9:" + id_,
                  verificare_mecanica=verificare, celula_grila=celula, proba_buna=buna, proba_negativa=negativa, martori=martori, tip=tip))


VP = D + "/verificator/proba_verificator.txt"
r("PC9-01", ["decizii_17_5_Q12.txt:9", "DESIGN_SYSTEM.md:1635"], "Suma negativă se afișează cu minusul real U+2212 prin formatorul comun (baniSemn / minusReal), "
  "aceeași funcție în Casă (F015) și Istoric facturi; zero și pozitivele ca bani.", "toate ecranele cu sume", "zero, pozitiv, negativ; refuzul gata scris al serverului",
  "cap.4 Casete de date", "verificator_conformitate.py C9-MINUS (static) + core/casa_sold.py la sursă (D2)", "F015/Design ×2",
  "verificator pe candidat: PILOT_C9 0; e2e_fundatie_17_5_Q12 / proba Q12 F015", VP + " N-MINUS-1, N-MINUS-2, N-NOU", "static/js/api.js:baniSemn, pachete.js, emitere_ecran.js")
r("PC9-02", ["decizii_17_5_Q12.txt:8", "decizii_17_5_Q12.txt:7"], "Rezumatul se taie la primul punct de sfârșit de propoziție, prin piesa comună primaPropozitie "
  "(prescurtările «ex.», «nota nr.», «F1A nr.» nu încheie propoziția).", "rezumatele semnalelor (D394, D406, Control fiscal › E-Factura)", "texte cu prescurtări",
  "cap.6 Mesaje", "verificator C9-REZUMAT (tăietura de mână interzisă în afara ds_piese.js)", "F034/Design ×2", "core/test_fluxuri_17_5_Q12.py (corecția 1)",
  VP + " N-REZUMAT", "static/js/ds_piese.js:primaPropozitie")
r("PC9-03", ["decizii_17_5_Q12.txt:13", "decizii_17_5_Q12.txt:14", "decizii_17_5_Q12.txt:15", "decizii_17_5_Q12.txt:16", "decizii_17_5_Q12.txt:17"],
  "În Parteneri, Clienți și Furnizori adăugarea cu eticheta proprie e unica acțiune principală (bara de jos); în Parteneri «Descarcă PDF» e secundar și funcțional; "
  "harta barei de jos: numai rândul Parteneri schimbat.", "Parteneri, Clienți, Furnizori (nu alte ecrane: Salariați, Registru jurnal au acțiunile lor)",
  "listă goală (PDF inactiv cu motiv) / plină", "cap.9 Ferestre de lucru", "verificator C9-F018 (static) + oracolul B4 f.1/f.2 + grila F018",
  "F018/Design, F018/Funcțional ×2", "pasi_17_5_C9 f.1, f.2 pe bază și candidat; e2e_fundatie_17_5_Q12", VP + " N-F018-a, N-F018-b",
  "static/js/ecrane/clienti_ecran.js, docs/dovezi/17_5_H/harta_bara_jos.txt")
r("PC9-04", ["decizii_17_5_Q8.txt:14", "decizii_17_5_Q9.txt:11", "decizii_17_5_Q9.txt:16"], "Registrul de parteneri e unic: Clienți și Furnizori sunt filtre ale "
  "aceluiași registru, cu formularul și «Salvează» pe rând; în Parteneri se adaugă, caută, editează și șterge aceeași fișă.", "Parteneri / Clienți / Furnizori",
  "rândul neschimbat (rand-neschimbat)", "cap.9 (domeniu Parteneri)", "core/test_randuri_17_5.py:94–108; e2e_pilot_17_5_X e.16–e.18 (protejat)",
  "F018/Funcțional", "core/test_randuri_17_5.py", "nerulată în C9 (testul protejat fixează forma)", "static/js/ecrane/clienti_ecran.js", tip="domeniu")
r("PC9-05", ["decizii_17_5_Q3.txt:18", "decizii_17_5_Q5.txt:15", "decizii_17_5_Q9.txt:18", "DESIGN_SYSTEM.md:1635"], "Bancă: un singur principal «Importă extras» în bară; "
  "«Contează» secundar pe fiecare linie returnată de API, inclusiv cea contată.", "Bancă", "linie eligibilă / contată / drept", "cap.9 (Pilot Q9 pct.3)",
  "e2e_ferestre_17_5_Q5.py:129", "F035/Design", "e2e_ferestre_17_5_Q5.py", "nerulată în C9", "static/js/ecrane/firme.js (Bancă)", tip="domeniu")
r("PC9-06", ["decizii_17_5_Q4.txt:4", "decizii_17_5_Q4.txt:3", "decizii_17_5_Q4.txt:2", "decizii_17_5_Q6.txt:6"], "«De validat»: lista DS-F019 are 8 documente pe pagină (modelul Q4 aprobat, "
  "SHA ae47e340…).", "De validat (Note de validat)", "pagina curentă, filtrul nou duce la prima pagină", "cap.9 (tabele DS)",
  "verificator C9-F019 (paginareDS 8 implicit, apelul val-n fără altă valoare)", "F019/Design ×2", "e2e_ferestre_17_5_Q4.py", VP + " N-F019",
  "static/js/ds_piese.js:paginareDS, static/js/ecrane/validat.js")
r("PC9-07", ["decizii_17_5_Q4.txt:6", "decizii_17_5_Q6.txt:6"], "742: minimum 8 rânduri reale complet vizibile la 1366×768 când setul are cel puțin 8 înregistrări "
  "(distinct de cele 8 documente pe pagină).", "lista 742 (De validat), 1366×768", "set < 8 / ≥ 8 (condiția opusă se probează)", "cap.9",
  "regulă exclusiv dinamică: măsura grilei (rânduri vizibile) — verificatorul static nu o judecă", "F019/Aspect 1366x768", "e2e_ferestre_17_5_Q4.py / Q6",
  "nerulată în C9", "-", tip="dinamic")
r("PC9-08", ["decizii_17_5_Q4.txt:5", "decizii_17_5_Q6.txt:6"], "Excepția DS-814: numai antetele listei «De validat», la lățimi ≤ 700 px.", "De validat, ≤ 700 px",
  "exceptat: antetele acelei liste ≤ 700 px; refuzat: orice altă listă / > 700 px", "cap.9 (excepție)", "static/js/ecrane/tabel_note.js (814) + e2e_ferestre_17_5_Q4.py",
  "F019/Aspect 603x590", "e2e_ferestre_17_5_Q4.py", "nerulată în C9", "static/js/ecrane/tabel_note.js", tip="exceptie")
r("PC9-09", ["decizii_17_5_Q6.txt:4"], "F025-S: un singur buton în funcție de stare; rândul blocajului dacă există, zona fixă altfel; garda 736 păstrată.", "Închidere lună / F025",
  "cu blocaj / fără blocaj", "cap.9 (domeniu)", "e2e_ferestre_17_5_Q6.py", "F025 ×12", "e2e_ferestre_17_5_Q6.py", "nerulată în C9", "-", tip="domeniu")
r("PC9-10", ["decizii_17_5_Q6.txt:8"], "Blocaj anterior reevaluării: ambele rânduri vizibile de la deschidere, butonul unic pe rândul reevaluării, la ambele rezoluții.",
  "Închidere lună / reevaluare", "blocaj anterior / fără", "cap.9 (domeniu)", "e2e_ferestre_17_5_Q6.py", "F025/Design", "e2e_ferestre_17_5_Q6.py", "nerulată în C9", "-", tip="domeniu")
r("PC9-11", ["decizii_17_5_Q9.txt:19", "DESIGN_SYSTEM.md:1635"], "D394: avertismentul operațiunilor N păstrează literal «EXCLUSE»; diacriticele și săgețile restului mesajului.",
  "D394", "operațiuni N prezente / absente", "cap.6 Mesaje (domeniu D394)", "core/test_d394.py:201, :619", "F034/Conformitate", "core/test_d394.py",
  "nerulată în C9", "core/d394.py", tip="domeniu")
r("PC9-12", ["decizii_17_5_Q12.txt:3", "decizii_17_5_Q9.txt:21"], "F085: sold preluat cu termen documentat se judecă după document; fără termen documentat afișează exact "
  "«termen necunoscut» și calculează scadența numai cu termen dovedit; facturile 66, 71 și FB-7 rămân cum sunt.", "solduri preluate (Import / scadențe)",
  "termen dovedit / nedocumentat; firmă fără solduri: un mesaj neutru", "cap.6 (domeniu F085)", "static/js/ecrane/migrare.js:TERMEN_NECUNOSCUT; core/test_fluxuri_17_5_Q12.py",
  "F085 ×12", "core/test_fluxuri_17_5_Q12.py", "nerulată în C9", "static/js/ecrane/migrare.js", tip="domeniu")
r("PC9-13", ["decizii_17_5_Q8.txt:15", "decizii_17_5_Q9.txt:12"], "DS.5: refuzurile nu mai poartă textul «NU s-a salvat.» (caseta refuzului spune ce lipsește).",
  "toate refuzurile de salvare", "-", "cap.6 Mesaje", "verificator Q7_TEXT_REFUZ (pilot_q7)", "F003/Design", "core/test_lot11_u0_erori.py, core/test_lot13_ds_mesaje.py",
  "verificator: textul reintrodus = constatare Q7_TEXT_REFUZ (gardă existentă)", "static/js/api.js:refuzSalvare")
r("PC9-14", ["DESIGN_SYSTEM.md:1635", "decizii_17_5_Q3.txt:10", "decizii_17_5_Q3.txt:11", "decizii_17_5_Q3.txt:12", "decizii_17_5_Q3.txt:13", "decizii_17_5_Q3.txt:14",
             "decizii_17_5_Q3.txt:15", "decizii_17_5_Q5.txt:7", "decizii_17_5_Q5.txt:8", "decizii_17_5_Q5.txt:9", "decizii_17_5_Q5.txt:10", "decizii_17_5_Q5.txt:11",
             "decizii_17_5_Q5.txt:12"],
  "Într-o fereastră de lucru cu acțiune principală, aceasta e unică și vizibilă la intrare pe ambele rezoluții (857 De validat, 858 Stocuri «+ NIR nou», 859 Salariați "
  "«Contabilizează statul», 860 Registru jurnal «+ Notă nouă», 861 «Deblochează luna» în bara formularului, 862 «Blochează luna»); acțiunile de rând rămân secundare.",
  "ferestrele de lucru (harta barei de jos)", "excepțiile FARA_ACTIUNE_PRINCIPALA / EXCEPTII_B", "cap.9 (Pilot Q9 pct.2)",
  "scripts/verificator_design.py RANDURI (rândul b) + verifica_liste_exceptii.py", "principala ×15 coduri (CAZURI_DS_Q7)", "e2e_ferestre_17_5_Q5.py, e2e_actiune_principala_17_5_D.py",
  "verificator_design rândul b (gardă existentă)", "static/js/cadru.js")
r("PC9-15", ["DESIGN_SYSTEM.md:1635"], "Pe 603×590 fiecare rând al unui tabel de lucru se citește în bloc; o singură zonă verticală de derulare; Registru jurnal > 88 px utili.",
  "tabelele de lucru, 603×590", "previzualizarea XML poate derula propriu", "cap.9 (Pilot Q9 pct.1)", "verificator --q7-probe (caz «tabel»)", "tabel ×13 coduri",
  "verificator_conformitate.py --q7-probe", "judeca(\"tabel\") pe măsuri cu celule tăiate", "-", tip="dinamic")
r("PC9-16", ["DESIGN_SYSTEM.md:1635"], "La o încercare se afișează toate erorile aplicabile; motivul rămas corespunde câmpurilor încă necompletate; căutarea goală arată starea goală.",
  "formularele de lucru", "-", "cap.6 (Pilot Q9 pct.4)", "verificator --q7-probe (erori, motiv, cautare)", "erori/motiv/cautare", "--q7-probe", "judeca pe măsuri", "-", tip="dinamic")
r("PC9-17", ["DESIGN_SYSTEM.md:1635"], "Avertismentul are un sumar scurt; inventarul și motivele integrale se citesc în detalii, dintr-o singură acțiune.", "avertismente",
  "-", "cap.5 (Pilot Q9 pct.6)", "verificator --q7-probe (avertisment)", "avertisment ×4 coduri", "--q7-probe", "judeca pe măsuri", "-", tip="dinamic")
r("PC9-18", ["DESIGN_SYSTEM.md:1635", "decizii_17_5_Q9.txt:22", "decizii_17_5_Q.txt:7", "decizii_17_5_Q2.txt:7"], "Declarații: grupul «Datorate înainte de preluarea în "
  "iConta.eu» desfăcut la intrare; perioadele accesibile; «Continuă →» vizibil după alegere; «restanță» numai pe obligațiile de după preluare (AC104).",
  "Declarații pasul 1", "înainte / după preluare", "cap.9 (domeniu Declarații)", "e2e_ferestre_17_5_Q2.py e.4; --q7-probe (declaratii)", "declaratii ×5 coduri",
  "e2e_ferestre_17_5_Q2.py", "nerulată în C9", "static/js/ecrane/declaratii.js", tip="domeniu")
r("PC9-19", ["decizii_17_5_Q3.txt:9", "decizii_17_5_Q3.txt:16", "decizii_17_5_Q5.txt:6", "decizii_17_5_Q5.txt:13"], "Motivul unui control inactiv se citește în același "
  "context fără hover/focus (855); la zero dispare «Arată încă 0 facturi» (863).", "toate controalele inactive", "activ / inactiv", "cap.6 (motiv inactiv)",
  "piesa atributeInactiv / ds-motiv-inactiv; e2e_ferestre_17_5_Q5.py", "motiv", "e2e_ferestre_17_5_Q5.py", "nerulată în C9", "static/js/api.js:atributeInactiv")
r("PC9-20", ["decizii_17_5_Q.txt:9", "decizii_17_5_Q2.txt:9", "decizii_17_5_Q2.txt:14", "decizii_17_5_Q3.txt:25", "decizii_17_5_Q5.txt:22"], "Solduri inițiale: «Încarcă balanța» "
  "din bară e singurul declanșator al selectorului (tastatură inclusă); #mig-drop pasivă, cursor neutru (C236); indicațiile, numele fișierului, formatele, previzualizarea "
  "și confirmarea rămân (formularea Q2 înlocuiește Q).", "Import date › Solduri inițiale F1/F7", "-", "cap.9 (domeniu Import)", "e2e_ferestre_17_5_Q2.py e.1",
  "F084 ×12", "e2e_ferestre_17_5_Q2.py", "nerulată în C9", "static/js/ecrane/migrare.js", tip="domeniu")
for _id, _s, _t, _d, _m in [
        ("PC9-21", ["decizii_17_5_Q.txt:3", "decizii_17_5_Q2.txt:3"], "AC088: rândul «Există deja» primește «Deschide Balanța de verificare» (secundar).", "Solduri inițiale", "e2e_ferestre_17_5_Q2.py"),
        ("PC9-22", ["decizii_17_5_Q.txt:5", "decizii_17_5_Q2.txt:5"], "AC091: «Ce se citește din balanță» devine card-rezumat; un singur tipar de pliere.", "Solduri inițiale", "e2e_ferestre_17_5_Q2.py"),
        ("PC9-23", ["decizii_17_5_Q.txt:6", "decizii_17_5_Q2.txt:6"], "AC093: după audit, începutul raportului (#cf-audit-istoric) adus în vedere.", "Audit de preluare", "e2e_ferestre_17_5_Q2.py"),
        ("PC9-24", ["decizii_17_5_Q.txt:8", "decizii_17_5_Q2.txt:8", "decizii_17_5_Q2.txt:13"], "AC133: «Cod obligație» D110 = «<cod> — <denumire>» din fișierul D110 ANAF; 626 cu «lit. k¹)» (Q2 înlocuiește Q).", "D110", "core/test_d110.py"),
        ("PC9-25", ["decizii_17_5_Q.txt:10", "decizii_17_5_Q2.txt:10", "decizii_17_5_Q2.txt:14"], "749.1: un singur rând «D301 — nu se datorează — …»; aceeași eliminare la D100, D101, D177, D300, D390, D394, D406, D301.", "Control fiscal", "e2e_ferestre_17_5_Q2.py e.4"),
        ("PC9-26", ["decizii_17_5_Q3.txt:5", "decizii_17_5_Q5.txt:2"], "694.1: diferențele TVA reconciliate la ban pe note; ciorna separat; restul real neexplicat cu suma lui.", "Control fiscal D300", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-27", ["decizii_17_5_Q3.txt:6", "decizii_17_5_Q5.txt:3"], "852: explicațiile notelor validate corectate la afișare; ciornele regenerate fără dublare.", "Registru jurnal", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-28", ["decizii_17_5_Q3.txt:7", "decizii_17_5_Q5.txt:4"], "750: bijecție factură ↔ rând în Control fiscal › e-Factura (nereprodus pe E Q2).", "Control fiscal e-Factura", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-29", ["decizii_17_5_Q3.txt:8", "decizii_17_5_Q5.txt:5"], "869: «îl respinge» la subiect singular (nereprodus pe E Q2).", "D394", "core/test_d394.py"),
        ("PC9-30", ["decizii_17_5_Q3.txt:17", "decizii_17_5_Q5.txt:14", "decizii_17_5_Q9.txt:17"], "619 / STOC.3: validarea returului numai după dependențe; stornarea după original, titlul «Stornare factura F1A nr. N din zz.ll.aaaa».", "Registru jurnal / stoc", "core/test_lot12_stoc2_619_validare_document.py"),
        ("PC9-31", ["decizii_17_5_Q3.txt:19", "decizii_17_5_Q5.txt:16"], "r61-F017-C: PDF-ul chitanței: seria, numărul, data, suma în litere (nereprodus).", "Chitanțe", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-32", ["decizii_17_5_Q3.txt:20", "decizii_17_5_Q5.txt:17"], "r61-F045-C: PDF factură: codul beneficiarului plătitor de TVA cu RO; neînregistratul fără RO adăugat.", "Facturi PDF", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-33", ["decizii_17_5_Q3.txt:21", "decizii_17_5_Q5.txt:18"], "r61-F080-C: deducerea 562 (13% × 4.325, rotunjit la leu), confruntată cu d112_struct_anaf.txt:192–193.", "Stat de plată", "core/test_fluxuri_17_5_Q10.py"),
        ("PC9-34", ["decizii_17_5_Q3.txt:22", "decizii_17_5_Q5.txt:19"], "r61-F122-D: previzualizarea contabilizării concediilor fără detalii redundante, liniile accesibile.", "Salariați › Concedii", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-35", ["decizii_17_5_Q3.txt:23", "decizii_17_5_Q5.txt:20"], "r61-F172-D: cât e deschisă poarta «Pleacă marfa acum?», cele două alegeri sunt singurele; o singură emitere.", "Emitere factură", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-36", ["decizii_17_5_Q3.txt:24", "decizii_17_5_Q5.txt:21"], "r61-F252/F254: după emitere fără «Completează datele cerute»; factura pe bon și Raport Z judecate în starea reală.", "Emitere / Raport Z", "e2e_ferestre_17_5_Q5.py"),
        ("PC9-37", ["decizii_17_5_Q9.txt:20"], "FINAL.6: temeiul cotei pe rând, integral, cu diacritice; denumirea dublă semnalată fără produs nou.", "Produse", "e2e_texte_17_5_I.py"),
        ("PC9-38", ["decizii_17_5_Q7.txt:5", "decizii_17_5_Q8.txt:5", "decizii_17_5_Q9.txt:5"], "FISC.2: F1A 17 exclusă din rd.9 cu motiv nominal și refuz de coadă; caz eligibil fără blocaj general; R10/F1A 13 pe bon fără dublare.", "D300", "e2e_fluxuri_17_5_Q9.py"),
        ("PC9-39", ["decizii_17_5_Q10.txt:9"], "AC188 antetul; AC189 confirmarea formatării existente; AC190 numai expirarea sesiunii.", "Verificări F1 / sesiune", "core/test_fluxuri_17_5_Q10.py"),
        ("PC9-40", ["decizii_17_5_Q12.txt:11"], "Bancă F1 603×590: observația de derulare retrasă (603/603 px, tabelele 539 px); cerințele Bancă aprobate își păstrează probele.", "Bancă", "banca_F1_603_desenat.json (export post-Q11)"),
        ("PC9-41", ["acceptare_AC_17_5_Q12.tsv:2"], "AC189: «0,00 lei (0%)» și «4.000,00 lei (0,4%)» în Verificări F1, concordante cu sursa.", "Verificări F1", "core/test_fluxuri_17_5_Q12.py"),
        ("PC9-42", ["acceptare_AC_17_5_Q12.tsv:8"], "AC196: rândul-buton din Istoric facturi crește cu numele, fără intersecție cu rândul următor.", "Istoric facturi", "core/test_fluxuri_17_5_Q12.py"),
]:
    r(_id, _s, _t, _d, "-", "domeniul ecranului (decizie de flux / conținut, nu stil generic)", "testul numit", "-", _m, "nerulată în C9", "-", tip="domeniu")
r("PC9-43", ["decizii_17_5_Q12.txt:5", "acceptare_AC_17_5_Q12.tsv:9"], "AC197: după poarta roșie se verifică imediat pragurile; depășirea oprește candidatul; două porți "
  "complete și două reluări pe lot; publicarea judecă toate rulările eligibile ale SHA-ului final.", "procesul porții", "SHA înlocuit / același SHA / prag egal",
  "— (regulă de proces, în CLAUDE.md §3 / scripts)", "scripts/poarta_rulare.py:116, :146; scripts/publica_lot.py (pragurile)", "-", "core/test_fluxuri_17_5_Q12.py (AC197)",
  "core/test_fluxuri_17_5_Q12.py (depășire pe A)", "scripts/poarta_rulare.py", tip="proces")
for _id, _s, _t, _m in [
        ("PC9-44", ["acceptare_AC_17_5_Q12.tsv:3"], "AC191: o notificare la apariția și una la rezolvarea fiecărui episod de anomalie.", "core/test_fluxuri_17_5_Q12.py (AC191)"),
        ("PC9-45", ["acceptare_AC_17_5_Q12.tsv:4"], "AC192: nicio încercare spre transport extern pentru domeniile rezervate.", "core/test_fluxuri_17_5_Q12.py (AC192)"),
        ("PC9-46", ["acceptare_AC_17_5_Q12.tsv:5"], "AC193: urmărirea livrării Postmark și rezerva deduplicată — nerealizat în Q12, decizia de produs e a lui Costin.", "— (la Costin)"),
        ("PC9-47", ["acceptare_AC_17_5_Q12.tsv:6"], "AC194: anunțuri WhatsApp numai la PORNIT/OPRIT, fără copia e-mail a OPRIT.", "core/test_alerta_whatsapp_17_2_A.py (D3)"),
        ("PC9-48", ["acceptare_AC_17_5_Q12.tsv:7"], "AC195: rotația cheii SPV pe copie izolată; operația live la Costin.", "~/dovezi_17_5_Q12/AC195_proba_copie_izolata.json"),
]:
    r(_id, _s, _t, "operațional", "-", "— (cerință operațională)", "testul numit", "-", _m, "nerulată în C9", "-", tip="operational")
r("PC9-49", ["note_dupa_Q12_pornire.txt:2"], "AC200: intervalul SPV → ciornă: t_SPV = data_creare a listei ANAF (AAAALLZZHHmm, ora României, la minut), t_ciornă = prima "
  "apariție persistentă ca ciornă; 0 ≤ Δ ≤ 30:00; altfel «interval nedovedit», fără valoare fabricată.", "recepția SPV (F179)",
  "29:59 / 30:00 / 30:01; precizie la minut; miezul nopții; dată lipsă; stare intermediară; duplicat; concurență", "— (flux)", "core/spv_receive.py:interval_spv_ciorna, interval_rand",
  "F179/Funcțional (rămâne «-»: factura reală la Costin)", "core/test_consolidare_17_5_C9.py (AC200)", "core/test_consolidare_17_5_C9.py (30:01, 31:00, inversat)", "core/spv_receive.py", tip="flux")
r("PC9-50", ["note_dupa_Q12_pornire.txt:3"], "AC201: emitentul din metadate când e valabil, altfel din partea furnizorului a XML-ului autentic; «-/-/-», ambiguu, codul cumpărătorului "
  "sau contradicția nu dau emitent; beneficiarul se verifică înaintea oricărei scrieri.", "recepția SPV", "zece cazuri (metadate, XML, RO, «-/-/-», ambiguu, contradicție, "
  "cumpărător, firmă străină, neparsabil, corecție negativă)", "— (flux)", "core/spv_receive.py:emitent_din_surse", "-",
  "core/test_consolidare_17_5_C9.py (AC201); frontend_test/e2e/e2e_fundatie_17_5_C9.py e.2", "core/test_consolidare_17_5_C9.py (incompatibile, contradicție)", "core/spv_receive.py", tip="flux")
r("PC9-51", ["decizii_17_5_Q6.txt:5", "decizii_17_5_Q7.txt:2", "decizii_17_5_Q8.txt:2", "decizii_17_5_Q9.txt:2"], "Judecata Pilot: un cod e închis numai cu șase criterii trecute "
  "la ambele rezoluții (12 celule); numitorul rămâne 45 de coduri / 540 de chei.", "bilanțul Pilot", "-", "— (regula grilei)", "scripts/masurare_pilot.py (rezumat.inchis, bilant)",
  "toate", "core/test_consolidare_17_5_C9.py (unealta)", "core/test_consolidare_17_5_C9.py (o celulă 0 / «-» împiedică închiderea)", "scripts/masurare_pilot.py", tip="proces")
r("PC9-52", ["decizii_17_5_Q3.txt:26", "decizii_17_5_Q5.txt:23"], "868: nu e defect (decizia lui Costin 22.11.2026); F081 se măsoară cu data repetată în «Termen».",
  "Cabinet › Termene", "-", "— (decizie: nicio schimbare de produs)", "—", "F081", "măsurarea F081 din Q6", "—", "-", tip="decizie_fara_produs")
r("PC9-53", ["decizii_17_5_Q.txt:11", "decizii_17_5_Q2.txt:11"], "AC138 (D398, F242): în afara Pilotului; închis numai separatorul totalului, rândurile livrărilor rămân deschise.",
  "D398", "-", "— (în afara Pilotului)", "—", "-", "—", "—", "-", tip="in_afara_pilot")
r("PC9-54", ["decizii_17_5_Q.txt:4", "decizii_17_5_Q2.txt:4"], "AC090: închis de 17.5-D; «Încarcă balanța» rămâne acțiunea principală (aserțiune invariantă).", "Solduri inițiale",
  "-", "cap.9 (domeniu Import)", "e2e_actiune_principala_17_5_D.py", "F084", "e2e_actiune_principala_17_5_D.py", "nerulată în C9", "-", tip="domeniu")
r("PC9-55", [], "F028 (decizia D1 a C9): titlul D112 «<luna> <an> (<LL>/<AAAA>)»; lista și rezumatul «09/2026»; extinderea la alte declarații cere alegerea lui Costin.",
  "D112", "numai D112", "cap.6 (domeniu D112)", "frontend_test/e2e/e2e_pilot_17_5_X.py:138–142 (727.2, protejat)", "F028 ×12", "e2e_pilot_17_5_X.py", "nerulată în C9", "-", tip="domeniu")
IDURI = {x["id"] for x in R}

# ── statutul reperelor care nu formulează o cerință (fișierul + linia -> statut, motiv) ──
STATUT = {}


def st(chei, statut, motiv):
    for k in chei:
        STATUT[k] = (statut, motiv)


st(["decizii_17_5_Q.txt:1", "decizii_17_5_Q2.txt:1", "decizii_17_5_Q3.txt:1", "decizii_17_5_Q4.txt:1", "decizii_17_5_Q5.txt:1", "decizii_17_5_Q6.txt:1",
    "decizii_17_5_Q7.txt:1", "decizii_17_5_Q8.txt:1", "decizii_17_5_Q9.txt:1", "decizii_17_5_Q12.txt:1"], "antet", "antetul fișierului: lotul, revizia, sursa deficiențelor")
st(["decizii_17_5_Q3.txt:2", "decizii_17_5_Q3.txt:3", "decizii_17_5_Q4.txt:7", "decizii_17_5_Q4.txt:8"], "fapt istoric",
   "identitatea bazei / numărul de ID-uri / starea propunerii la redactare / autorizația operațională a reviziei; nu e regulă de design")
st(["decizii_17_5_Q6.txt:2", "decizii_17_5_Q6.txt:3", "decizii_17_5_Q6.txt:7", "decizii_17_5_Q7.txt:3", "decizii_17_5_Q7.txt:4", "decizii_17_5_Q7.txt:7",
    "decizii_17_5_Q7.txt:8", "decizii_17_5_Q7.txt:10", "decizii_17_5_Q8.txt:3", "decizii_17_5_Q8.txt:4", "decizii_17_5_Q8.txt:7", "decizii_17_5_Q8.txt:8",
    "decizii_17_5_Q8.txt:10", "decizii_17_5_Q8.txt:12", "decizii_17_5_Q8.txt:13", "decizii_17_5_Q9.txt:3", "decizii_17_5_Q9.txt:4", "decizii_17_5_Q9.txt:7",
    "decizii_17_5_Q9.txt:8", "decizii_17_5_Q9.txt:9", "decizii_17_5_Q9.txt:10", "decizii_17_5_Q9.txt:13", "decizii_17_5_Q9.txt:14", "decizii_17_5_Q9.txt:15",
    "decizii_17_5_Q9.txt:23", "decizii_17_5_Q9.txt:24", "decizii_17_5_Q10.txt:1", "decizii_17_5_Q10.txt:2", "decizii_17_5_Q10.txt:3", "decizii_17_5_Q10.txt:6",
    "decizii_17_5_Q10.txt:7", "decizii_17_5_Q10.txt:8", "decizii_17_5_Q11.txt:1"], "regulă a procesului",
   "ordinea loturilor, plasa, pragurile, REAL/B4, worktree-ul, contul de probă: se execută prin lanțul și poarta de lot (CLAUDE.md §3), nu prin DS")
st(["decizii_17_5_Q7.txt:6", "decizii_17_5_Q8.txt:6", "decizii_17_5_Q9.txt:6", "decizii_17_5_Q10.txt:4"], "dependență deschisă",
   "F026 / FINAL.10c rămân deschise în lipsa originalelor (limite_C4_Q7.txt); reimportul controlat probează comportamentul curent")
st(["decizii_17_5_Q10.txt:5"], "regulă a procesului (măsurare)", "F003 într-o lună cu Z; geometria cu interfața activă; C238/C239 probe distincte (verificator reguli_c238_c239)")
st(["decizii_17_5_Q12.txt:7"], "antet de secțiune", "introduce cele două corecții comune (PC9-01, PC9-02)")
st(["decizii_17_5_Q12.txt:14", "decizii_17_5_Q12.txt:16"], "identitate (SHA)", "SHA-ul hărții barei de jos pe E11 / pe candidat: martorul înlocuirii unei singure linii (PC9-03)")
st(["decizii_17_5_Q12.txt:15"], "fapt istoric (rândul înlocuit)", "rândul vechi al hărții, înlocuit explicit de decizia F018 r2 (PC9-03)")
st(["decizii_17_5_Q12.txt:11"], "propunere amânată + observație retrasă", "data din viitor, «Generează notă» la Raport Z 603 și bara ResizeObserver = propuneri după Pilot; "
   "Bancă F1 603 retrasă după remăsurare (PC9-40 păstrează domeniul)")
st(["acceptare_AC_17_5_Q12.tsv:1"], "antet", "capul tabelului")
LEGATE = {}   # reper -> ID (din `surse` ale cerințelor)
for x in R:
    for s in x["surse"]:
        LEGATE.setdefault(s, []).append(x["id"])


def sha_interval(cale, a, b):
    lin = open(cale, "rb").read().splitlines(keepends=True)
    return hashlib.sha256(b"".join(lin[a - 1:b])).hexdigest()


def statut_reper(r_):
    f, a = r_["fisier"], int(r_["prima_linie"])
    k = "%s:%d" % (f, a)
    if k in LEGATE:
        return "trimitere", ", ".join(LEGATE[k]), "cerința formulată / reluată aici"
    if k in STATUT:
        s, m = STATUT[k]
        return s, "-", m
    if f == "audit_pilot.tsv":
        return "observație de audit", "-", "poziție istorică cu ID (audit_pilot); nu devine decizie de design; urmărită prin grila Pilot (pct.5) când e pe un cod din cei 45"
    if f == "celule_17_5_Q12.tsv":
        return "celulă pe E11 (măsurătoare de stare)", "-", "celula grilei măsurată în Q12; bilanțul C9 o confruntă (masurare_pilot.py importa-q12 + bilant)"
    if f == "masurare_pilot_v3_24_11.csv":
        return "rezumat istoric pe funcție", "-", "cod din numitorul de 45; rezumatul nu e măsurătoare (cele 540 de chei se judecă prin unealtă)"
    if f == "DESIGN_SYSTEM.md":
        if a == 1635:
            return "trimitere", "PC9-01, PC9-05, PC9-11, PC9-14, PC9-15, PC9-16, PC9-17, PC9-18", "secțiunea Pilot 17.5-Q9 descompusă pe capitole"
        return "regulă DS existentă", "-", "capitolul DS de pe E11, confruntat cu DS-ul activ (v2.133): textul capitolului neschimbat, regulile C9 adăugate cu ancore PC9"
    return "NECLASIFICAT", "-", "reper fără statut"


def main(dir_rep, iesire):
    idx = list(csv.DictReader(open(os.path.join(dir_rep, "index_surse_C9.tsv"), encoding="utf-8"), delimiter="\t"))
    rele, randuri = [], []
    for x in idx:
        cale = os.path.join(dir_rep, "surse_C9", x["fisier"])
        sha = sha_interval(cale, int(x["prima_linie"]), int(x["ultima_linie"]))
        if sha != x["sha256_octeti_interval"]:
            rele.append("%s:%s SHA %s ≠ index %s" % (x["fisier"], x["prima_linie"], sha[:12], x["sha256_octeti_interval"][:12]))
        statut, idr, motiv = statut_reper(x)
        lot, rev, autor, data = META.get(x["fisier"], ("-", "-", "-", "-"))
        randuri.append({"fisier": x["fisier"], "linii": "%s-%s" % (x["prima_linie"], x["ultima_linie"]), "sha256": sha, "reper": x["reper"][:80],
                        "natura": x["natura_sursei"], "lot": lot, "revizia": rev, "autor": autor, "data": data, "statut": statut, "id": idr, "motiv": motiv})
    if rele:
        print("REFUZ: reperele nu corespund indexului:\n  " + "\n  ".join(rele))
        return 2
    necl = [x for x in randuri if x["statut"] == "NECLASIFICAT"]
    os.makedirs(iesire, exist_ok=True)
    col = ("fisier", "linii", "sha256", "reper", "natura", "lot", "revizia", "autor", "data", "statut", "id", "motiv")
    with open(os.path.join(iesire, "index_acoperire_C9.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=col, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(randuri)
    colm = ("id", "tip", "lot", "data", "provenienta", "text", "domeniu", "stari_exceptii", "capitol_ds", "ancora_ds", "verificare_mecanica", "celula_grila",
            "proba_buna", "proba_negativa", "martori")
    with open(os.path.join(iesire, "matrice_C9.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colm, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for x in R:
            prima = x["surse"][0].split(":")[0] if x["surse"] else "decizii_17_5_C9.txt"
            lot, rev, autor, data = META.get(prima, ("17.5-C9", "r2", "arhitect (decizii_17_5_C9.txt D1)", "26.11.2026"))
            w.writerow(dict(x, lot=lot, data=data, provenienta="; ".join(x["surse"]) or "decizii_17_5_C9.txt:D1"))
    print("repere: %d (SHA conforme) · cerințe: %d · trimiteri: %d · cu statut: %d · neclasificate: %d" % (
        len(randuri), len(R), sum(1 for x in randuri if x["statut"] == "trimitere"), sum(1 for x in randuri if x["statut"] not in ("trimitere", "NECLASIFICAT")),
        len(necl)))
    for x in necl:
        print("  NECLASIFICAT %s:%s %s" % (x["fisier"], x["linii"], x["reper"]))
    return 1 if necl else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
