# Pozitii PLANIFICATE — export din FUNCTIONALITATI.csv

Total: 37 pozitii, in ordinea din fisier.

| ID | Nume | Descriere scurta | Categorie |
|---|---|---|---|
| F120 | Educatie AI pe tipare (varianta generativa) | Extensia ecranului G: AI genereaza explicatii si recomandari personalizate din tiparele de erori ale asistentului (azi exista d... | Planificat |
| F121 | Trimitere e-Transport prin API SPV | Trimiterea directa a notificarii UIT prin API-ul SPV (azi doar XML pentru upload manual, F044). | Carenta |
| F123 | Provider real de plata | Configurarea Netopia sau Stripe pe cont real (azi F067 functioneaza cu provider mock). | Planificat |
| F124 | Testare pilot P1-P5 | Campania de testare pentru pilot: fluxul lunar complet pe firma reala, salarizare cap-coada, TVA la incasare, operatiuni specia... | Planificat |
| F125 | Trimitere D390 clasificari manuale | Ecran pentru clasificarea manuala a serviciilor (P/S) si triangulatiilor (T/R) la D390 (azi avertisment, clasificarea se face i... | Planificat |
| F126 | e-Factura SPV complet | Trimitere automata a facturilor emise in SPV (cu retry la indisponibilitate ANAF), urmarirea starii cu recipisa/erori, primirea... | Analiza concurentei |
| F127 | Transmitere declaratii direct la ANAF | Depunerea declaratiilor din aplicatie cu certificat digital/token, preluarea automata a recipiselor, istoric depuneri cu stare. | Analiza concurentei |
| F128 | Monitorizare mesaje SPV ale firmelor | Citirea automata a mesajelor din SPV pentru fiecare firma (somatii, notificari, decizii) cu alerte catre cabinet. | Analiza concurentei |
| F129 | Declaratii D392, D094, D207, D700, D710 | Generatoarele pentru declaratiile informative/de inregistrare ramase. | Analiza concurentei |
| F130 | Open Banking PSD2 (extrase automate) | Conectarea conturilor bancare prin PSD2: extrasele sosesc zilnic automat (toate bancile + Revolut + Trezoreria), fara import ma... | Analiza concurentei |
| F131 | Notificari de plata si alerte neplatnici | Notificari automate catre clientii cu facturi scadente/restante, alerte in aplicatie, scadentar si fisa de client. | Analiza concurentei |
| F132 | Import borderouri curieri si procesatori card | Incasarile ramburs si decontarile procesatorilor de card ca surse de reconciliere. | Analiza concurentei |
| F133 | Tichete de masa si beneficii | Tichete de masa/cadou/cultura in statul de plata: tratament fiscal, note contabile, evidenta per salariat. | Analiza concurentei |
| F134 | Plata salariilor pe card (fisier bancar) | Generarea fisierului de plati salariale pentru banca. | Analiza concurentei |
| F135 | Pontaj angajati | Pontaj lunar (prezenta/concedii) completabil si de client pe portal, alimenteaza statul de plata. | Analiza concurentei |
| F136 | Adeverinte salariati | Generarea adeverintelor uzuale (venit, CIC, medic) din datele de salarizare. | Analiza concurentei |
| F137 | Coduri COR pe contracte | Nomenclatorul ocupatiilor pe contractele de munca (cerut de REGES). | Analiza concurentei |
| F138 | Transfer intre gestiuni | Nota de transfer intre gestiuni si schimbarea tipului de produs (materie prima -> marfa). | Analiza concurentei |
| F139 | Landed cost pe NIR | Repartizarea costului de transport si a taxelor in costul de achizitie al articolelor. | Analiza concurentei |
| F140 | Analitica de stoc | Stocuri critice/fara miscare, necesar de aprovizionare, prognoza pe perioade comparabile. | Analiza concurentei |
| F141 | Coduri de bare in gestiune | Lucru cu coduri de bare la articole (NIR, inventar, vanzare). | Analiza concurentei |
| F142 | Inventar pe mobil | Inventarierea cu telefonul, cantitatile urca in timp real. | Analiza concurentei |
| F143 | Centre de cost si bugete | Dimensiunea centre de cost pe note/documente + plan de buget (linii de venituri/cheltuieli) cu urmarire realizat-vs-plan. | Analiza concurentei |
| F144 | Rapoarte comerciale | Profit pe produs, vanzari pe agent/articol/partener, durata medie de incasare, fisa client/furnizor. | Analiza concurentei |
| F145 | Rapoarte configurabile salvabile | Orice raport re-filtrat/re-grupat de utilizator se salveaza ca varianta proprie. | Analiza concurentei |
| F146 | Registratura documente | Numere de intrare/iesire alocate automat pe documentele firmei. | Analiza concurentei |
| F147 | Generare contracte | Contracte generate din sabloane cu datele partenerului. | Analiza concurentei |
| F148 | Arhivare in cloud extern (Drive/OneDrive) | Sincronizarea arhivei de documente in cloud-ul utilizatorului. | Analiza concurentei |
| F149 | Case de marcat / POS / imprimante (DECIZIE: probabil in afara scopului) | Legatura live cu case de marcat, POS retail/HoReCa, imprimante termice, cantare - iConta e platforma de cabinet, nu de vanzare;... | Analiza concurentei |
| F154 | Proforme si avize in contul gratuit | Legarea modulului existent de proforme/avize in meniul Facturi al contului gratuit. | Roadmap cont gratuit |
| F155 | Facturi recurente in contul gratuit | Legarea sabloanelor recurente (F110, cron existent) - abonamente, chirii. | Roadmap cont gratuit |
| F156 | Import WooCommerce in contul gratuit | Legarea conectorului WooCommerce (F111): config in profil + import comenzi -> facturi | Roadmap cont gratuit |
| F157 | Chitante in contul gratuit | Emiterea chitantelor (F017) la incasarea cash a facturilor proprii. | Roadmap cont gratuit |
| F158 | Model factura in contul gratuit | Personalizarea PDF-ului (F045): logo, culoare, font. | Roadmap cont gratuit |
| F159 | Link de plata in contul gratuit | Legarea linkurilor de plata pe facturile emise. | Roadmap cont gratuit |
| F160 | e-Factura SPV pentru contul gratuit | XML UBL + incarcare SPV: OAuth ANAF per firma | Roadmap cont gratuit |
| F161 | Vreau contabil - conversia contului gratuit | Butonul care leaga firma de un cabinet iConta: tenantul migreaza sub accounting_firm, datele raman | Roadmap cont gratuit |
