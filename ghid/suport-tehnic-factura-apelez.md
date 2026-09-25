---
title: "Suport tehnic pentru e-Factura: unde apelez"
description: "Canalele reale de asistență pentru probleme tehnice cu sistemul RO e-Factura și obligația legală a ANAF de a îndruma contribuabilul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Suport tehnic pentru e-Factura: unde apelez

Sistemul RO e-Factura e administrat de Ministerul Finanțelor prin Centrul Național pentru Informații Financiare, iar problemele tehnice (erori de validare, blocaje la încărcare, probleme cu certificatul digital) se rezolvă prin canalele oficiale de asistență ale ANAF, nu printr-un „suport" separat, dedicat exclusiv e-Facturii. Legea nu prevede un SLA (termen de răspuns) specific pentru asistența tehnică, dar organul fiscal are obligația generală de a îndruma contribuabilul în aplicarea legislației fiscale.

## Temeiul legal

::: ghid-temei
„(2) Organul fiscal are obligația să examineze starea de fapt în mod obiectiv și în limitele stabilite de lege, precum și să îndrume contribuabilul/plătitorul în aplicarea prevederilor legislației fiscale, în îndeplinirea obligațiilor și exercitarea drepturilor sale, ca urmare a solicitării contribuabilului/plătitorului sau din inițiativa organului fiscal, după caz."
— Legea 207/2015, art. 7 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Canalele reale prin care se solicită sprijin pentru probleme tehnice cu e-Factura:

- **Spațiul Privat Virtual (SPV)** — secțiunea de mesagerie/solicitări, pentru probleme legate de cont, certificat digital sau acces la sistem.
- **Portalul ANAF, secțiunea dedicată RO e-Factura** — publică ghiduri de utilizare, întrebări frecvente și, periodic, anunțuri despre mentenanță sau erori cunoscute ale sistemului.
- **Registrul RO e-Factura**, în care operatorul care a optat pentru sistem trebuie să fie înscris — problemele de înscriere/dezînscriere se rezolvă tot prin canalele ANAF, procedura fiind stabilită prin ordin al președintelui ANAF.
- Pentru erori de validare a facturii electronice (XML respins), primul pas practic e verificarea mesajului de eroare returnat de sistem la încărcare — majoritatea erorilor sunt de structură a fișierului, nu probleme de infrastructură ANAF.
- Nu există, potrivit cadrului legal, o linie telefonică dedicată exclusiv e-Facturii cu termen de răspuns garantat — asistența se încadrează în obligația generală de îndrumare a contribuabilului, prevăzută la art. 7 din Codul de procedură fiscală.

## Ce se greșește în practică

- Se așteaptă un răspuns telefonic imediat, presupunând că există un „call center" dedicat e-Facturii cu obligație de timp de răspuns — un asemenea SLA nu e prevăzut legal, iar canalele reale sunt SPV și portalul ANAF.
- Se confundă erorile de validare a facturii (probleme de structură XML, care apar la contribuabil) cu indisponibilitatea sistemului RO e-Factura (problemă de infrastructură ANAF) — soluția diferă complet în funcție de cauză.
- Se ignoră mesajul de eroare returnat de sistem la încărcare, care de cele mai multe ori indică exact câmpul sau regula de validare nerespectată.

## Ce face iConta.eu

iConta.eu generează și validează factura electronică înainte de trimitere (`core/efactura_send.py`, funcția `valideaza`), încarcă fișierul UBL în sistemul RO e-Factura și urmărește starea mesajului trimis (`stare_mesaj`, `descarca`, `lista_mesaje`). Multe dintre erorile de structură XML sunt astfel prinse și semnalate contabilului înainte de trimitere, reducând nevoia de a mai apela suportul ANAF pentru probleme de format. La data acestui ghid, iConta.eu **nu oferă suport tehnic direct pentru infrastructura RO e-Factura administrată de ANAF** — pentru indisponibilitatea sistemului sau probleme de cont/certificat, contribuabilul rămâne dependent de canalele oficiale (SPV, portalul ANAF).

[iConta.eu](/)
