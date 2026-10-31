// [operatiuni] Ecran generic "Operatiuni speciale" - condus de configuratie.
// O operatiune noua = o intrare in REGISTRU (titlu, ruta, campuri), zero cod nou de ecran.
import { api, ultimaCerere, activ, inactiv, dataRo, cate, cantitate, esc, bani, arataMesaj, semnAjutor, dataIso, stareNota, pasNota, eroareCamp, curataEroriCamp, dupaGenerare, noteGenerate } from "../api.js?v=c6c45aefe4";
import { siraCarduri } from "../carduri.js?v=98c15a1738";
import { formularGrupat, actualizeazaGrupe, cardRezumat } from "../ds_piese.js?v=2e31f52e03";   // [15.1] piesele formularului grupat
import { ciornaFormular } from "../ciorna_formular.js?v=461bec469f";   // [15.1, 721] ciorna formularului, pe server
import { permis } from "../drepturi.js?v=34d0fb0afd";  /* [drepturi_rol 04.10.2026] */
import { legaDateAnaf } from "./date_anaf.js?v=503d474ed1";   // [lotul 13, 506 / 633] datele aduse de la ANAF țin de CUI-ul lor
import { butonSpreEcran } from "./ecran_destinatie.js?v=5152ec2b0a";   // [lotul 13, 551 / 548] refuzul care trimite în Date firmă are butonul lui
import { actiuniRefuz, scoateActiuniRefuz } from "./coada_trimite.js?v=50cade9fc8";   // rândul de butoane de lângă caseta „NU s-a salvat”
// [ajutor_contextual] mapare cheie operatiune -> ID functionalitate (semnul "?" dinamic)
const _OP_AJUTOR = { avans:"F009", bacsis:"F010", leasing:"F056", asociati:"F039",
  credit:"F024", chirie:"F020", decont:"F040", contract_special:"F021", reevaluare:"F074",
  provizion:"F071", sponsorizare:"F086", subventie:"F090", obiect_inv:"F063", inventariere:"F052" };

// tipuri de camp: data | numar | text | select(optiuni) | bool
// conditie: {camp: "tip", val: "rata"} - campul apare doar cand alt camp are valoarea.
// [R145] `val` poate fi si o LISTA: campul apare la oricare din valori. Trebuia fiindca ruta
// `nota-chirie` cere acelasi camp (`chirie`) la doua feluri, iar declarat de doua ori producea
// doua elemente cu acelasi `id` — al doilea nu se mai colecta.
const C = (nume, eticheta, tip = "numar", extra = {}) => ({ nume, eticheta, tip, ...extra });
// [C6, comanda Costin 07.10.2026] Un DA/NU pe care serverul îl citește prin `bifa` se cere EXPLICIT: select Da/Nu, cu „— alege —”,
// fără preselecție (DS cap.17). Până azi: două erau câmpuri text („Dovada export (DVE)” invita la numărul DVE, iar serverul răspundea
// „acceptă doar da sau nu”), șapte lipseau din formular (serverul punea tăcut „nu”), trei aveau „Da” preselectat. Gard:
// core/test_formulare_operatiuni_campuri.py::test_bifele_serverului_se_cer_explicit_da_nu.
const DN = (nume, eticheta, extra = {}) => C(nume, eticheta, "select", { optiuni: [["true", "Da"], ["false", "Nu"]], neales: "— alege —", ...extra });
// [lotul 13, deficiența 504, comanda Costin 13.1: „Câmpurile nu au voie să arate valori gri sau precompletate care induc în eroare […] la
// Ajustare stocuri contul vine precompletat cu 397. Câmpul rămâne gol.”] Nicio valoare și niciun text gri în câmp: contul, cota, codul
// pornesc goale; contul uzual (`sugestie`) se spune în explicația câmpului („de regulă 704”), nu ca valoare. Gard:
// core/test_lot13_ops_formular.py::test_niciun_camp_precompletat_sau_gri.
// [lotul 13, 631 / 670] monedele: aceeași listă ca la „Emite factură” (`#em-moneda`), fără RON — operațiunea e în valută
export const MONEDE = ["EUR", "USD", "GBP", "CHF", "HUF", "PLN"];

const REGISTRU = [
{ cat: "Finanțare", cheie: "leasing", titlu: "Leasing", ruta: "nota-leasing", frecventa: "lunar", faraPropunere: "contractul de leasing (scadențarul ratelor) nu e înregistrat în aplicație", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip operațiune", "select", { optiuni: [["primire","Primire bun (financiar)"],["rata","Rată lunară"],["reziduala","Valoare reziduală"],["operational","Chirie leasing operațional"]] }),
    C("locator_cui", "CUI locator (societatea de leasing)", "cui", { cond: { camp: "tip", val: ["primire", "rata", "reziduala", "operational"] }, numeCamp: "locator_nume" }),
    C("locator_nume", "Denumirea locatorului", "text", { cond: { camp: "tip", val: ["primire", "rata", "reziduala", "operational"] } }),
    C("denumire", "Bunul primit (denumire)", "text", { cond: { camp: "tip", val: "primire" } }),
    C("valoare_capital", "Valoare capital", "numar", { cond: { camp: "tip", val: "primire" } }),
    C("dobanda_totala", "Dobândă totală (din contract)", "numar", { cond: { camp: "tip", val: "primire" }, ajutor: "Se ține în afara bilanțului, pe 8051, într-o singură parte." }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "tip", val: "primire" }, sugestie: "2133" }),
    C("cod_catalog", "Cod din catalog (HG 2139/2004)", "catalog", { cond: { camp: "tip", val: "primire" } }),
    C("dnf_luni", "Durata normală (luni, în plaja catalogului)", "numar", { cond: { camp: "tip", val: "primire" } }),
    C("data_pif", "Data punerii în funcțiune", "data", { cond: { camp: "tip", val: "primire" } }),
    C("metoda", "Metoda de amortizare", "select", { cond: { camp: "tip", val: "primire" }, optiuni: [["liniara","Liniară"],["degresiva","Degresivă"],["accelerata","Accelerată"]] }),
    C("numar_inventar", "Număr de inventar", "text", { cond: { camp: "tip", val: "primire" }, optional: true, ajutor: "Gol: următorul din registru (MF-001, MF-002 …)." }),
    C("capital", "Capital rată", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("dobanda", "Dobândă", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("comision", "Comision", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("valoare_reziduala", "Valoare reziduală", "numar", { cond: { camp: "tip", val: "reziduala" } }),
    C("chirie", "Chirie lunară", "numar", { cond: { camp: "tip", val: "operational" } }),
    C("cont_cheltuiala", "Cont cheltuială", "text", { cond: { camp: "tip", val: "operational" }, sugestie: "612" }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "tip", val: ["rata", "reziduala", "operational"] } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "credit", titlu: "Credite bancare", ruta: "nota-credit", frecventa: "lunar", faraPropunere: "contractul de credit (scadențarul ratelor și al dobânzilor) nu e înregistrat în aplicație", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["primire","Primire credit"],["dobanda","Dobândă"],["plata","Plată rată"],["restanta","Restanță"],["garantie","Garanție"]] }),
    C("tip", "Termen", "select", { optiuni: [["scurt","Sub 1 an (519)"],["lung","Peste 1 an (162)"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "operatie", val: ["primire", "restanta", "garantie"] } }),
    C("fel", "Garanție", "select", { optiuni: [["primita","Primită (8021)"],["acordata","Acordată (8011)"]], neales: "— alege —", cond: { camp: "operatie", val: "garantie" } }),
    C("actiune", "Acțiune", "select", { optiuni: [["inregistrare","Înregistrare"],["eliberare","Eliberare / stingere"]], neales: "— alege —", cond: { camp: "operatie", val: "garantie" } }),
    C("dobanda", "Dobândă", "numar", { cond: { camp: "operatie", val: ["dobanda", "plata"] } }),
    C("rata", "Rata (capital)", "numar", { cond: { camp: "operatie", val: "plata" }, ajutor: "Dobânda se plătește din 1682 / 5198 dacă e înregistrată acolo; altfel e cheltuiala lunii (666) — o stabilește aplicația din sold." }),
    C("comision", "Comision bancar (627)", "numar", { cond: { camp: "operatie", val: "plata" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "asociati", titlu: "Decontări asociați (455/457)", ruta: "nota-asociati", frecventa: "lunar", propune: "Dividendul se împarte singur pe asociații din Date firmă → Asociați, valabili la data hotărârii, și se ia din profitul nerepartizat; scrii suma și hotărârea.", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["dividend","Dividend"],["imprumut","Împrumut asociat"],["regularizare","Regularizare interimare"],["restituire_dividend","Restituire dividend încasată"]] }),
    C("brut", "Dividend brut (total)", "numar", { cond: { camp: "operatie", val: "dividend" }, ajutor: "Se împarte pe asociați după cotele din Date firmă → Asociați, valabile la data hotărârii (Legea 31/1990 art. 67 alin. (2))." }),
    // [lotul 10, deficiența 430c] documentul justificativ al notei: hotărârea adunării asociaților / decizia asociatului unic
    C("numar_hotarare", "Numărul hotărârii (adunarea asociaților sau decizia asociatului unic)", "text", { cond: { camp: "operatie", val: "dividend" } }),
    C("data_hotarare", "Data hotărârii", "data", { cond: { camp: "operatie", val: "dividend" }, ajutor: "Asociații și cotele se iau la data ei; profitul disponibil, la fel." }),
    C("interimar", "Fel", "select", { optiuni: [["0","Anual, din profitul nerepartizat (1171 = 457)"],["1","Interimar (463/456)"]], neales: "— alege —", cond: { camp: "operatie", val: "dividend" } }),
    DN("cu_plata", "Dividendul se plătește acum", { cond: { camp: "operatie", val: "dividend" }, ajutor: "Da: nota cuprinde și plata netului (457/456 = 5121)." }),
    C("suma", "Suma împrumut", "numar", { cond: { camp: "operatie", val: "imprumut" } }),
    C("fel", "Sens", "select", { optiuni: [["primire","Primire de la asociat"],["restituire","Restituire către asociat"]], cond: { camp: "operatie", val: "imprumut" } }),
    C("dobanda", "Dobânda plătită asociatului", "numar", { cond: { camp: "fel", val: "restituire" }, ajutor: "0 dacă împrumutul e fără dobândă; din dobândă se reține impozitul (4551 = 446)." }),
    C("total_interimar", "Total dividende interimare", "numar", { cond: { camp: "operatie", val: "regularizare" } }),
    C("dividend_anual", "Dividend anual final", "numar", { cond: { camp: "operatie", val: "regularizare" } }),
    C("impozit_interimar", "Impozit reținut pe interimare", "numar", { cond: { camp: "operatie", val: "regularizare" }, optional: true,
      ajutor: "Necesar când interimarele depășesc dividendul anual: asociatul restituie netul, impozitul se recuperează de la buget (CPF art. 170^1)." }),
    C("suma_restituita", "Suma încasată", "numar", { cond: { camp: "operatie", val: "restituire_dividend" },
      ajutor: "Ce a intrat efectiv în cont: netul restituit de asociat sau impozitul restituit de buget (5121 = 463)." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "avans", titlu: "Avansuri (409/419)", ruta: "nota-avans", frecventa: "lunar", propune: "Avansul de la client: factura de avans și regularizarea ei, din Facturi (4111 = 419). Avansul plătit în numerar pentru un NIR: din Casă (409x = 5311). Formularul rămâne pentru avansul prin bancă.", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["avans_platit","Avans plătit (409)"],["regularizare_platit","Regularizare 409"],["avans_incasat","Avans încasat (419)"],["regularizare_incasat","Regularizare 419"]] }),
    C("suma", "Suma (fără TVA)"), C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    // [R149] La regularizare, cota e cea de la LIVRARE (art. 291 alin. 6) — de-aia campul apare
    // numai pe cele doua operatii de regularizare.
    C("data_livrare", "Data livrării/prestării", "data",
      { cond: { camp: "operatie", val: ["regularizare_platit", "regularizare_incasat"] },
        ajutor: "Regularizarea aplică cota în vigoare la data livrării, nu la data regularizării (art. 291 alin. 6)." }),
    C("destinatie", "Destinație", "select", { optiuni: [["stocuri","Stocuri"],["servicii","Servicii"],["imobilizari","Imobilizări"],["imobilizari_necorporale","Imobilizări necorporale"]], cond: { camp: "operatie", val: ["avans_platit", "regularizare_platit"] } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Vânzări speciale", cheie: "agricultor", titlu: "Vânzare către agricultor (regim special)", ruta: "vanzare-agricultor", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"),
    C("pret", "Preț (fără taxă)", "numar"),
    C("descriere", "Descriere", "text", { optional: true }),
  ] },  /* [0a_rute_v1] backend existent, legat in registru */
{ cat: "Imobilizări și capital", cheie: "necorporala", titlu: "Achiziție necorporală (software/licență/brevet)", ruta: "achizitie-necorporala", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("denumire", "Denumire", "text"),
    C("valoare", "Valoare (fără TVA)", "numar"),
    C("tip", "Tip", "select", { optiuni: [["software","Software (36 luni)"],["licenta","Licență"],["brevet","Brevet"]] }),
    C("dnf_luni", "Durată contract (luni)", "numar", { cond: { camp: "tip", val: "licenta" } }),
    C("furnizor_cui", "CUI furnizor", "cui", { numeCamp: "furnizor_nume" }),
    C("furnizor_nume", "Furnizor", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("cota", "Cota TVA %", "numar"),
  ] },  /* [0a_rute_v1] */
{ cat: "Imobilizări și capital", cheie: "reevaluare", titlu: "Reevaluare imobilizări (105)", ruta: "reevaluare-imobilizare", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Operație", "select", { optiuni: [["reevaluare","Reevaluare MF"],["surplus","Transfer surplus la 1175"]] }),
    C("mijloc_fix_id", "Mijlocul fix", "mijloc_fix", { cond: { camp: "operatie", val: "reevaluare" }, ajutor: "Rezerva din reevaluare (105) și pierderea anterioară (655) ale activului le ia aplicația din reevaluările lui." }),   // [C4, 07.10.2026] din registru
    C("valoare_justa", "Valoare justă", "numar", { cond: { camp: "operatie", val: "reevaluare" } }),
    C("suma", "Suma surplus", "numar", { cond: { camp: "operatie", val: "surplus" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Imobilizări și capital", cheie: "obiect_inv", titlu: "Obiecte de inventar (303)", ruta: "nota-obiect-inventar", frecventa: "lunar", faraPropunere: "intrarea obiectelor de inventar (NIR pe 303) nu propune darea în folosință", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Operație", "select", { optiuni: [["achizitie","Achiziție"],["dare_folosinta","Dare în folosință (603=303)"],["scoatere","Scoatere din folosință"]] }),
    C("denumire", "Obiectul (denumire)", "text", { cond: { camp: "operatie", val: "achizitie" } }),
    C("valoare", "Valoare fără TVA", "numar", { cond: { camp: "operatie", val: "achizitie" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "achizitie" } }),
    C("furnizor_cui", "CUI furnizor", "cui", { cond: { camp: "operatie", val: "achizitie" }, numeCamp: "furnizor_nume" }),
    C("furnizor_nume", "Furnizor", "text", { cond: { camp: "operatie", val: "achizitie" } }),
    C("numar", "Nr. factură furnizor", "text", { cond: { camp: "operatie", val: "achizitie" }, ajutor: "Dacă factura e deja în Facturi primite, obiectul se leagă de ea și nu se înregistrează a doua oară." }),
    C("obiect_id", "Obiectul de inventar", "obiect", { cond: { camp: "operatie", val: ["dare_folosinta", "scoatere"] }, ajutor: "Valoarea vine de la obiect." }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("durata_sub_1_an", "Durata de utilizare sub un an", { cond: { camp: "operatie", val: "achizitie" }, ajutor: "Da: e obiect de inventar oricare i-ar fi valoarea; Nu: peste pragul mijloacelor fixe se înregistrează ca mijloc fix." }) ] },
{ cat: "Imobilizări și capital", cheie: "provizion", titlu: "Provizioane și ajustări", ruta: "nota-provizion", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["creanta","Ajustare creanțe — constituire (6814 = 491)"],["creanta_reluare","Ajustare creanțe — reluare (491 = 7814)"],["provizion","Provizion (151)"],["stoc","Ajustare stocuri (39x)"]] }),
    C("actiune", "Acțiune", "select", { optiuni: [["constituire","Constituire"],["reluare","Reluare"]], cond: { camp: "fel", val: ["provizion", "stoc"] } }),
    C("factura_id", "Factura neîncasată", "factura_neincasata", { cond: { camp: "fel", val: "creanta" }, ajutor: "Suma (soldul facturii) și zilele de la scadență le ia aplicația." }),
    C("suma", "Suma", "numar", { cond: { camp: "fel", val: ["creanta_reluare", "provizion", "stoc"] } }),
    C("cont_ajustare", "Cont ajustare stocuri", "select", { cond: { camp: "fel", val: "stoc" }, optiuni: [["391","391 materii prime"],["392","392 materiale"],["393","393 producția în curs"],["394","394 produse"],["395","395 stocuri la terți"],["396","396 animale"],["397","397 mărfuri"],["398","398 ambalaje"]] }),
    C("tip", "Tip provizion", "select", { optiuni: [["litigii","Litigii (1511)"],["garantii","Garanții acordate clienților (1512)"],["dezafectare","Dezafectare (1513)"],["restructurare","Restructurare (1514)"],["pensii","Pensii și obligații similare (1515)"],["impozite","Impozite (1516)"],["terminare_cm","Terminarea contractului de muncă (1517)"],["altele","Altele (1518)"]], cond: { camp: "fel", val: "provizion" } }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("garantata", "Creanța e garantată de altă persoană", { cond: { camp: "fel", val: "creanta" } }),
    DN("afiliata", "Debitorul e persoană afiliată", { cond: { camp: "fel", val: "creanta" } }),
    DN("faliment", "Debitorul e în faliment declarat prin hotărâre judecătorească", { cond: { camp: "fel", val: "creanta" }, ajutor: "Da: 100% deductibil (art. 26 alin. (1) lit. j))." }) ] },
  // [lotul 13, deficiența 510] obținerea cere produsul, cantitatea și gestiunea (intră în fișa de magazie, cu Bonul de predare); vânzarea
  // e factura către client cu produsul din stoc — costul ieșit și coeficientul 348 le dă aplicația (OMFP 1802/2014 pct.286 alin.(4))
  { cat: "Imobilizări și capital", cheie: "productie", titlu: "Producție (711/345)", ruta: "nota-productie", frecventa: "lunar", faraPropunere: "comenzile de producție și costul standard nu sunt înregistrate în aplicație", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["obtinere","Ob\u021binere produse (predare la magazie)"],["pic","Produc\u021bie \u00een curs (331)"],["vanzare","V\u00e2nzare (factur\u0103 + desc\u0103rcare din stoc)"]] }),
    C("produs", "Produsul", "articol", { cond: { camp: "operatie", val: ["obtinere", "vanzare"] }, felStoc: "produs", nou: true, ajutor: "Din fișa de magazie (produse finite, 345). La obținere, un produs nou intră în stoc." }),
    C("um", "Unitatea de măsură (numai produs nou)", "text", { cond: { camp: "operatie", val: "obtinere" }, optional: true }),
    C("cantitate", "Cantitatea", "numar", { cond: { camp: "operatie", val: ["obtinere", "vanzare"] } }),
    C("cost_standard", "Cost standard unitar", "numar", { cond: { camp: "operatie", val: "obtinere" } }),
    C("cost_efectiv", "Cost efectiv total", "numar", { cond: { camp: "operatie", val: "obtinere" }, optional: true, ajutor: "Dacă diferă de cantitate × cost standard, diferența trece pe 348." }),
    C("gestiune", "Gestiunea (magazia)", "text", { cond: { camp: "operatie", val: "obtinere" } }),
    C("suma", "Suma PIC", "numar", { cond: { camp: "operatie", val: "pic" } }),
    C("moment", "Moment", "select", { optiuni: [["constatare","Constatare"],["reluare","Reluare"]], cond: { camp: "operatie", val: "pic" } }),
    C("client_cui", "CUI client", "cui", { cond: { camp: "operatie", val: "vanzare" }, numeCamp: "client_nume" }),
    C("client_nume", "Clientul", "text", { cond: { camp: "operatie", val: "vanzare" } }),
    C("pret_vanzare", "Preț de vânzare unitar (fără TVA)", "numar", { cond: { camp: "operatie", val: "vanzare" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "vanzare" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Imobilizări și capital", cheie: "inventariere", titlu: "Inventariere anuală", ruta: "nota-inventariere", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Operație", "select", { optiuni: [["plus","Plus stoc"],["plus_mf","Plus mijloc fix"],["minus","Minus"],["casare","Casare"]] }),
    C("valoare", "Valoare", "numar", { cond: { camp: "operatie", val: ["plus", "plus_mf", "minus"] } }),
    C("cont_stoc", "Cont stoc", "text", { cond: { camp: "operatie", val: ["plus", "minus"] }, sugestie: "371" }),
    DN("imputabil", "Imputabil", { cond: { camp: "operatie", val: "minus" } }),
    C("valoare_imputare", "Valoare imputare", "numar", { cond: { camp: "imputabil", val: "true" } }),
    C("vinovat", "Cui se impută", "select", { cond: { camp: "imputabil", val: "true" }, optiuni: [["salariat","Salariat (4282)"],["tert","Terț (461)"]] }),
    C("salariat_id", "Salariatul vinovat", "salariat", { cond: { camp: "vinovat", val: "salariat" }, ajutor: "Reținerea ajunge în statul lui de plată." }),
    C("denumire", "Denumire mijloc fix", "text", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "operatie", val: "plus_mf" }, sugestie: "2131", ajutor: "Contul de amortizare îl stabilește aplicația din el." }),
    C("cod_catalog", "Cod din catalog (HG 2139/2004)", "catalog", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("dnf_luni", "Durată normală (luni, în plaja catalogului)", "numar", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("data_pif", "Dată punere în funcțiune", "data", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("metoda", "Metodă amortizare", "select", { cond: { camp: "operatie", val: "plus_mf" }, optiuni: [["liniara","Liniară"],["degresiva","Degresivă"],["accelerata","Accelerată"],["superaccelerata","Superaccelerată"]] }),
    C("numar_inventar", "Număr de inventar", "text", { cond: { camp: "operatie", val: "plus_mf" }, optional: true, ajutor: "Gol: următorul din registru (MF-001, MF-002 …)." }),
    DN("destinatie_cd", "Destinat cercetării-dezvoltării", { cond: { camp: "operatie", val: "plus_mf" }, ajutor: "Da: amortizarea accelerată e permisă pe orice cont (CF art. 20 alin. (1) lit. b))." }),
    C("mijloc_fix_id", "Mijlocul fix", "mijloc_fix", { cond: { camp: "operatie", val: "casare" }, ajutor: "Valoarea și amortizarea vin din registru; luna casării se amortizează în nota ei." }),   // [C4, 07.10.2026] din registru
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "minus" } }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("lipsa_dovedita", "Lipsa e dovedită ca distrugere, pierdere sau furt", { cond: { camp: "operatie", val: "minus" }, ajutor: "Da (cu documentul): fără ajustarea TVA dedusă (art. 304 alin. (2) lit. a)); asigurarea nu scutește. Nu: 635 = 4426 pe costul bunului." }),
    C("document_lipsa", "Documentul doveditor (ex. PV al organelor judiciare)", "text", { cond: { camp: "lipsa_dovedita", val: "true" } }) ] },
  { cat: "TVA regimuri speciale", cheie: "tva_incasare", titlu: "TVA la încasare (art. 282)", ruta: "nota-tva-incasare", frecventa: "lunar", propune: "La încasarea sau plata facturii (Bancă, Casă) și la compensare, aplicația propune singură exigibilizarea TVA (4428 = 4427, 4426 = 4428). Formularul rămâne pentru cazurile speciale (art. 291 alin. (5)).", campuri: [
    C("data", "Data", "data"),
    C("sens", "Sens", "select", { optiuni: [["incasare","Încasare de la client (4428=4427)"],["plata","Plată către furnizor (4426=4428)"]] }),
    C("suma_incasata", "Suma încasată/plătită (cu TVA)"),
    // [R149] Cota se ia din legea de la FAPTUL GENERATOR, nu de la incasare (art. 291 alin. 5).
    C("data_fapt_generator", "Data livr\u0103rii/prest\u0103rii (faptul generator)", "data",
      { ajutor: "Cota de TVA e cea \u00een vigoare la data livr\u0103rii, nu la data \u00eencas\u0103rii (art. 291 alin. 5 Cod fiscal)." }),
    // [R151] Art. 291 alin. (5) are DOUA ramuri, iar aplicatia nu poate sti care e cazul: datele
    // operatiunii nu spun care document a fost primul. Se CERE (decizia lui Costin, 05.09.2026),
    // cu `neales` ca sa nu vina niciuna preselectata.
    C("ramura_291_5", "Care a fost primul: livrarea, sau factura/avansul?", "select",
      { neales: "\u2014 alege \u2014",
        optiuni: [["fapt_generator", "Livrarea sau prestarea a fost prima \u2014 cota de la data livr\u0103rii"],
                  ["factura_avans", "Factura ori avansul au fost \u00eenainte de livrare \u2014 cota de la data lor"]],
        ajutor: "Art. 291 alin. (5): la TVA la \u00eencasare cota e cea de la faptul generator, "
          + "Dar dac\u0103 factura ori avansul au fost emise \u00eenainte de livrare, se aplic\u0103 cota de la "
          + "data acelui document. Alegerea nu se poate deduce din datele opera\u021biunii, de aceea "
          + "se cere aici." }),
    C("data_factura_avans", "Data facturii ori a avansului", "data",
      { cond: { camp: "ramura_291_5", val: "factura_avans" },
        ajutor: "Trebuie s\u0103 fie \u00eenainte de data livr\u0103rii \u2014 altfel excep\u021bia nu se aplic\u0103, "
          + "iar opera\u021biunea e \u00een situa\u021bia general\u0103." }),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  // [lotul 13, deficiența 548] bunul se alege din stoc și iese din gestiune la CMP (prețul de cumpărare al marjei); clientul e cerut
  { cat: "TVA regimuri speciale", cheie: "marja", titlu: "Vânzare regim marjă (second-hand)", ruta: "vanzare-marja", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"),
    C("articol", "Bunul vândut (din stoc)", "articol", { felStoc: "marfa", ajutor: "Prețul de cumpărare e valoarea bunului în stoc (CMP), nu se scrie." }),
    C("cantitate", "Cantitatea", "numar"),
    C("pret_vanzare", "Preț de vânzare (total)"),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("client_cui", "CUI client (persoană juridică)", "cui", { numeCamp: "client_nume", optional: true, ajutor: "Gol pentru o persoană fizică." }),
    C("client_nume", "Clientul", "text"),
    C("document", "Documentul vânzării (factura / bonul)", "text"),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "marja_turism", titlu: "Marjă agenții de turism", ruta: "vanzare-marja-turism", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune",
    multi: "componente", multiTitlu: "Componentele pachetului (regim normal)", multiCond: { camp: "optiune_normal", val: "true" }, campuri: [
    C("data", "Data", "data"),
    C("calitate_client", "Client", "select", { optiuni: [["PF","Persoană fizică"],["PJ","Persoană juridică"]] }),
    DN("intermediar", "Agenția acționează ca intermediar", { ajutor: "Da: baza e comisionul (art. 311 alin. (9)); sumele încasate în numele altora nu sunt venit." }),
    DN("optiune_normal", "Opțiune pentru regimul normal de TVA", { cond: { camp: "intermediar", val: "false" }, ajutor: "Permisă numai pentru client persoană juridică și servicii toate în România (art. 311 alin. (10))." }),
    C("locuri", "Locul serviciilor", "select", { cond: { camp: "optiune_normal", val: "true" }, lista: true, optiuni: [["RO","Toate în România"],["UE","Și în alte state UE"],["NONUE","Și în afara UE"]] }),
    C("incasat", "Încasat de la client", "numar", { cond: { camp: "optiune_normal", val: "false" } }),
    C("cost_ue", "Cost servicii UE", "numar", { cond: { camp: "optiune_normal", val: "false" } }),
    C("cost_non_ue", "Cost servicii non-UE", "numar", { cond: { camp: "optiune_normal", val: "false" } }),
    C("comision", "Comisionul agenției", "numar", { cond: { camp: "intermediar", val: "true" } }),
    DN("tva_inclus", "Comisionul include TVA", { cond: { camp: "intermediar", val: "true" } }),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ], subcampuri: [
    C("descriere", "Componenta", "text"),
    C("baza", "Baza (cu marja alocată)"),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }) ] },
{ cat: "TVA regimuri speciale", cheie: "taxare_inversa", titlu: "Taxare inversă internă (art. 331)", ruta: "achizitie-taxare-inversa", frecventa: "lunar", propune: "Factura primită cu taxare inversă se contează singură în Facturi primite (4426 = 4427). Formularul rămâne pentru factura care nu e în aplicație.", campuri: [
    C("data", "Data", "data"),
    C("furnizor_cui", "CUI furnizor (RO, plătitor TVA)", "cui", { numeCamp: "furnizor_nume", ajutor: "Aplicația verifică la ANAF dacă furnizorul e plătitor de TVA: taxarea inversă se aplică numai între plătitori (art. 331)." }),
    C("furnizor_nume", "Furnizor", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("categorie", "Categorie art. 331", "select", { optiuni: [["deseuri","Deșeuri"],["masa_lemnoasa","Masă lemnoasă"],["cereale","Cereale"],["certificate_emisii","Certificate emisii"],["energie_electrica","Energie electrică"],["certificate_verzi","Certificate verzi"],["cladiri_terenuri","Clădiri/terenuri"],["aur_investitii","Aur de investiții"],["telefoane","Telefoane"],["circuite_integrate","Circuite integrate"],["console_tablete","Console/tablete"],["gaze_naturale","Gaze naturale"]] }),
    C("valoare", "Valoare (fără TVA)"),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("cota", "Cota TVA %", "numar"),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "TVA regimuri speciale", cheie: "agricultor_achizitie", titlu: "Achiziție de la agricultor (compensare 8%)", ruta: "achizitie-agricultor", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"),
    C("agricultor_cui", "CNP sau CUI agricultor", "cui", { numeCamp: "agricultor_nume" }),
    C("agricultor_nume", "Agricultorul (nume)", "text"),
    C("valoare", "Valoare (fără taxă)"),
    C("cont_cheltuiala", "Cont cheltuială/stoc", "text", { sugestie: "301" }),
    DN("agricultor_in_registru", "Agricultor în registru", { ajutor: "Nu: achiziția se înregistrează fără compensație (art. 315^1 alin. (17))." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "aur", titlu: "Aur de investiții (art. 313)", ruta: "vanzare-aur-investitii", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["lingou","Lingou"],["plancheta","Plachetă"],["moneda","Moneda"]] }),
    C("puritate", "Puritate (ex. 995)", "numar"),   // [C6 vecin de tip] serverul o citește ca număr (tva_aur._numar)
    C("articol", "Aurul vândut (din stoc)", "articol", { felStoc: "marfa", ajutor: "Iese din gestiune la CMP (607 = 371)." }),
    C("cantitate", "Cantitatea", "numar"),
    C("suma", "Valoare vânzare"),
    C("calitate_client", "Client", "select", { optiuni: [["PF","Persoană fizică"],["PJ","Persoană juridică"]] }),
    C("client_nume", "Numele clientului", "text"),
    C("client_identificare", "Identificare client (CNP / act de identitate / CUI)", "text", { ajutor: "Obligatorie la livrarea de aur de investiții (art. 313 alin. (10))." }),
    C("document", "Documentul livrării (factura)", "text"),
    C("an_emisie", "Anul emisiunii monedei", "numar", { cond: { camp: "tip", val: "moneda" }, ajutor: "Moneda de aur e de investiții dacă e emisă după 1800 (art. 313 alin. (1) lit. b))." }),
    C("pret_unitar", "Prețul monedei", "numar", { cond: { camp: "tip", val: "moneda" } }),
    C("valoare_aur", "Valoarea aurului conținut", "numar", { cond: { camp: "tip", val: "moneda" }, ajutor: "Prețul nu poate depăși valoarea aurului cu mai mult de 80% (art. 313 alin. (1) lit. b))." }),
    DN("optiune_taxare", "Opțiune de taxare", { cond: { camp: "calitate_client", val: "PJ" }, ajutor: "Da: taxare inversă în locul scutirii — permisă numai către o persoană impozabilă (art. 313 alin. (4)–(5))." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  // [lotul 13, deficiența 524] decontarea se face pe factura din care provine (moneda, contul de terț, partenerul și cursul de evidență vin
  // de pe ea și din ultima ei reevaluare), cu suma în valută cel mult cât a rămas pe factură; cursul de evidență nu se mai scrie de mână
  { cat: "Extern", cheie: "decont_valuta", titlu: "Decontare în valută (665/765)", ruta: "decontare-valuta", frecventa: "lunar", faraPropunere: "plata facturii în valută din Bancă nu calculează diferența de curs la decontare (665 / 765)", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["creanta","Încasare creanță"],["datorie","Plată datorie"]] }),
    C("factura_id", "Factura", "factura_valuta", { cond: { camp: "tip", val: ["creanta", "datorie"] } }),
    C("valoare_valuta", "Suma în valută", "numar", { cond: { camp: "tip", val: ["creanta", "datorie"] } }),
    // [lotul 13, decizia Costin după 524 / 504] contul prin care s-a decontat: listă închisă din planul firmei — 5124, 5121, 5314 (casa în
    // valută) și analiticele lor (un procesator de plăți ținut ca analitic), fără nimic ales
    C("cont_banca", "Contul de trezorerie (bancă sau casă)", "cont_trezorerie", { cond: { camp: "tip", val: ["creanta", "datorie"] } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Extern", cheie: "achizitie_ic", titlu: "Achiziție intracomunitară", ruta: "achizitie-ic", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data facturii", "data"),
    C("moneda", "Moneda facturii", "moneda", { cuRon: true }),
    C("valoare", "Valoarea din factură (în moneda ei)", "numar", { ajutor: "Cursul BNR al zilei exigibilității îl ia aplicația (art. 290 alin. (2))." }),
    C("cod_tva_furnizor", "Cod TVA furnizor UE (ex. DE123456789)", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("furnizor_nume", "Furnizor", "text", { optional: true }),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("tip", "Tip", "select", { optiuni: [["bunuri","Bunuri"],["servicii","Servicii"]] }),
    C("cota", "Cota TVA %", "numar"),
    C("data_faptului_generator", "Data faptului generator", "data", { ajutor: "Exigibilitatea = data facturii sau ziua 15 a lunii următoare faptului generator, dacă factura n-a fost emisă până atunci (art. 284 alin. (2)). Dacă e aceeași cu a facturii, scrie data facturii." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  // [C84, decizia Costin (b), lotul 12] „livrarea intracomunitară de BUNURI trece pe «Emite factură» (care descarcă stocul), iar Operațiuni
  // rămân pentru servicii”. Până acum, pe o firmă cu stocul cantitativ-valoric, livrarea de bunuri de aici era imposibilă (refuzul cerea
  // articolul din stoc pe linia 707, iar formularul n-avea câmp de articol) și oricum nu descărca stocul. Alegerea „Bunuri” arată acum
  // drumul (`spreEmitere`): textul și butonul spre «Emite factură»; „Generează nota” nu se oferă pentru bunuri.
  { cat: "Extern", cheie: "vanzare_ic", titlu: "Livrare/prestare intracomunitară (VIES live)", ruta: "vanzare-ic", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune",
    spreEmitere: { camp: "tip", val: "bunuri", text: "Livrarea intracomunitară de bunuri se face din «Emite factură»: acolo scrii codul de TVA al clientului (se verifică în VIES), alegi articolul din stoc și categoria „livrare intracomunitară”, iar marfa se descarcă din gestiune odată cu factura. Aici rămân prestările de servicii intracomunitare." },
    campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare"),
    // [lotul 12, C78.1] `vies`: rezultatul VIES (cod valid sau nu, numele firmei) se vede sub câmp înainte de „Generează nota”
    C("cod_tva_client", "Cod TVA client (ex. DE123456789)", "text", { vies: true }),
    C("tip", "Tip", "select", { optiuni: [["bunuri","Bunuri"],["servicii","Servicii"]] }),
    C("cont_venit", "Cont venit", "text", { sugestie: "704", cond: { camp: "tip", val: "servicii" }, ajutor: "Prestările de servicii: de regulă 704." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Extern", cheie: "import_ec", titlu: "Import extracomunitar (DVI)", ruta: "import-extracomunitar", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data DVI", "data"),
    C("numar_dvi", "Numărul DVI", "text"),
    C("furnizor_nume", "Furnizorul extern", "text"),
    C("valoare_vamala", "Valoare vamală (lei, din DVI)", "numar", { ajutor: "Valoarea în vamă în lei, cum o stabilește DVI-ul (art. 290 alin. (1))." }),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("procent_taxa_vamala", "Taxă vamală %", "numar", {}),
    C("accize", "Accize", "numar", {}),
    C("accesorii", "Accesorii (transport, asigurare până la destinație)", "numar", { ajutor: "Intră în baza TVA din vamă (art. 289 alin. (2)); costul lor intră în stoc prin factura transportatorului, din Facturi primite." }),
    C("cota", "Cota TVA %", "numar"),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("certificat_amanare", "Certificat de amânare a plății TVA în vamă", { ajutor: "Da: TVA în decont, 4426 = 4427 (art. 326 alin. (4)); Nu: TVA plătită în vamă." }) ] },
  { cat: "Extern", cheie: "export_ec", titlu: "Export extracomunitar (DVE)", ruta: "export-extracomunitar", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare"),
    C("tara_client", "Țara clientului", "text"),
    C("cont_venit", "Cont venit", "text", { sugestie: "707" }),
    DN("dovada_export", "Ai declarația vamală de export (DVE)", { ajutor: "Fără ea scutirea nu se aplică (art. 294 alin. (1) lit. a)) — se facturează cu TVA până la obținerea dovezii." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  // [lotul 13, deficiența 670, comanda Costin 13.1] (a) salariatul din salariații firmei (542 pe persoană); (b) diurna cu zilele și
  // deplasarea în țară / în străinătate: serverul verifică plafonul neimpozabil (CF art.76 alin.(2) lit.k) și trimite excedentul în statul
  // de plată; (c) transportul și cazarea, fiecare cu baza fără TVA și cota ei; diurna fără TVA; (d) nimic precompletat, transportul și
  // cazarea opționale. Calculul separat al plafonului a ieșit: îl face decontul.
  { cat: "Personal și deconturi", cheie: "decont", titlu: "Decont deplasare / diurnă", ruta: "nota-decont-deplasare", frecventa: "lunar", faraPropunere: "ordinul de deplasare și documentele lui nu sunt înregistrate în aplicație", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["avans","Avans spre decontare (542)"],["decont","Decont final"]] }),
    C("salariat_id", "Salariatul", "salariat"),
    C("sursa", "Sursa banilor", "select", { optiuni: [["casa","Casa (5311)"],["banca","Banca (5121)"]] }),
    C("suma", "Suma avansului", "numar", { cond: { camp: "fel", val: "avans" } }),
    C("avans", "Avansul primit de salariat", "numar", { cond: { camp: "fel", val: "decont" }, ajutor: "0 dacă n-a primit avans. Nu poate depăși soldul contului 542." }),
    C("diurna", "Diurna acordată (total, fără TVA)", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("deplasare", "Deplasarea", "select", { cond: { camp: "fel", val: "decont" }, optiuni: [["interna","În țară"],["externa","În străinătate"]] }),
    C("zile", "Zile de deplasare", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("diurna_bugetara", "Diurna pe zi a țării (anexa HG 518/1995)", "numar", { cond: { camp: "deplasare", val: "externa" }, ajutor: "În valuta din anexă; cursul BNR îl ia aplicația." }),
    C("moneda", "Moneda diurnei din anexă", "moneda", { cond: { camp: "deplasare", val: "externa" } }),
    C("transport", "Transport — baza fără TVA", "numar", { cond: { camp: "fel", val: "decont" }, optional: true }),
    C("cota_transport", "Cota TVA a transportului %", "numar", { cond: { camp: "fel", val: "decont" }, optional: true, ajutor: "Se cere numai dacă ai transport." }),
    C("cazare", "Cazare — baza fără TVA", "numar", { cond: { camp: "fel", val: "decont" }, optional: true }),
    C("cota_cazare", "Cota TVA a cazării %", "numar", { cond: { camp: "fel", val: "decont" }, optional: true, ajutor: "Cazarea hotelieră are cota redusă (art. 291 alin. (2) lit. m))." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Personal și deconturi", cheie: "contract_special", titlu: "Contracte speciale (zilieri, mandat, cenzori)", ruta: "nota-contract-special", frecventa: "lunar", faraPropunere: "zilierii și contractele de mandat nu sunt în Salarizare", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["zilier","Zilier"],["mandat","Mandat administrator"],["cenzor","Cenzor"]] }),
    C("brut", "Suma brută"),
    C("sursa", "Sursa plata", "select", { optiuni: [["casa","Casa"],["banca","Banca"]] }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Personal și deconturi", cheie: "bacsis", titlu: "Bacșiș (HoReCa)", ruta: "nota-bacsis", frecventa: "lunar", faraPropunere: "raportul Z nu poartă bacșișul separat", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["incasare","Încasare"],["distribuire","Distribuire la salariați"]] }),
    C("suma", "Suma"),
    C("sursa", "Sursa", "select", { optiuni: [["card","Card"],["numerar","Numerar"]], cond: { camp: "fel", val: "incasare" } }),
    C("sursa_distribuire", "Plata către salariați", "select", { trimiteCa: "sursa", optiuni: [["banca","Bancă (5121)"],["numerar","Numerar (5311)"]], cond: { camp: "fel", val: "distribuire" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

{ cat: "Diverse", cheie: "sponsorizare", titlu: "Sponsorizare (credit fiscal)", ruta: "nota-sponsorizare", frecventa: "rar", campuri: [
    C("data", "Data", "data"), C("suma", "Suma sponsorizată"),
    C("beneficiar_cui", "CUI beneficiar", "cui", { numeCamp: "beneficiar_nume" }),
    C("beneficiar_nume", "Beneficiarul", "text"),
    C("mod", "Mod", "select", { optiuni: [["contract","Contract (6582=401)"],["plata","Plată directă (6582=5121)"]] }),
    DN("beneficiar_in_registru", "Beneficiarul e înscris în Registrul entităților/unităților de cult", { ajutor: "Nu: fără credit fiscal din impozit (art. 25 alin. (4) lit. i)). Creditul îl calculează D101 la nivelul anului." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Diverse", cheie: "subventie", titlu: "Subvenții (445/741)", ruta: "nota-subventie", frecventa: "lunar", propune: "Reluarea la venituri a subvenției pentru investiții (4751 = 7584) se generează singură odată cu amortizarea lunară a activului finanțat.", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["exploatare","Exploatare"],["investitii","Investiții (475)"]] }),
    C("suma", "Suma", "numar"),
    C("moment", "Moment", "select", { optiuni: [["drept","La dreptul de a primi"],["incasare","La încasare"]] }),
    C("cont_venit", "Cont venit din subvenție", "text", { cond: { camp: "fel", val: "exploatare" }, sugestie: "741" }),
    C("mijloc_fix_id", "Mijlocul fix finanțat", "mijloc_fix", { cond: { camp: "fel", val: "investitii" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  // [R145, 04.09.2026] Formularul colecta UN camp, «Suma», si il trimitea asa. Ruta `nota-chirie`
  // cere insa nume DIFERITE dupa `fel` — `valoare` la comodat, `chirie` la chirii, iar la refacturare
  // DOUA sume (`total_factura` + `parte_refacturata`). Deci operatiunea nu putea reusi niciodata din
  // interfata, pe niciun fel: cu date perfect valide, raspunsul era «Lipseste campul `valoare` din
  // cererea trimisa». Gasit apasand, in lotul 13, si confirmat cu date VALIDE — intrebarea nu era
  // daca refuza, ci daca poate reusi vreodata.
  //
  // Reparat in ECRAN, nu in ruta, si cu `cond` — mecanismul exista deja aici (leasing il foloseste
  // de la nasterea lui). Numele campurilor sunt acum CELE DIN CONTRACTUL RUTEI, luate din docstringul
  // ei, nu inventate. Refacturarea primeste cele doua sume pe care le cere, si «Suma» dispare: un
  // camp care nu ajunge nicaieri e mai rau decat unul lipsa, fiindca omul crede ca l-a completat.
{ cat: "Diverse", cheie: "chirie", titlu: "Chirii / comodat / refacturări", ruta: "nota-chirie", frecventa: "lunar", faraPropunere: "contractele de chirie și comodat nu sunt înregistrate în aplicație (șabloanele de contract nu se păstrează)", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["comodat","Comodat"],["chirie_platita","Chirie plătită (612)"],["chirie_incasata","Chirie încasată (706)"],["refacturare","Refacturare utilități"]] }),
    C("valoare", "Valoarea bunului", "numar", { grup: "Sume", cond: { camp: "fel", val: "comodat" } }),
    C("moment", "Moment", "select", { grup: "Document", cond: { camp: "fel", val: "comodat" }, optiuni: [["primire","Primire"],["restituire","Restituire"]] }),
    C("furnizor_cui", "CUI furnizor", "cui", { cond: { camp: "fel", val: ["chirie_platita", "refacturare"] }, numeCamp: "furnizor_nume" }),
    C("furnizor_nume", "Denumire furnizor", "text", { cond: { camp: "fel", val: ["chirie_platita", "refacturare"] } }),
    C("client_cui", "CUI chiriaș", "cui", { cond: { camp: "fel", val: ["chirie_incasata", "refacturare"] }, numeCamp: "client_nume" }),
    C("client_nume", "Denumire chiriaș", "text", { cond: { camp: "fel", val: ["chirie_incasata", "refacturare"] } }),
    C("chirie", "Chiria (fără TVA)", "numar", { cond: { camp: "fel", val: ["chirie_platita", "chirie_incasata"] } }),
    C("proprietar", "Proprietar", "select", { grup: "Furnizor / Client", deduceDinCui: "furnizor_cui", valoareCuiVerificat: "pj", cond: { camp: "fel", val: "chirie_platita" }, optiuni: [["pj","Persoană juridică"],["pf","Persoană fizică"]] }),
    C("tip_bun", "Bunul închiriat", "select", { grup: "Document", cond: { camp: "fel", val: "chirie_incasata" }, optiuni: [["imobil","Bun imobil (clădire, teren, spațiu)"],["alt_bun","Alt bun (utilaj, mijloc de transport)"]] }),
    DN("optiune_taxare", "Firma a optat pentru taxare (notificare art. 292 alin. (3))", { cond: { camp: "tip_bun", val: "imobil" }, ajutor: "Nu: chiria e scutită fără drept de deducere (art. 292 alin. (2) lit. e)), rândul 15 din D300." }),
    C("numar", "Nr. factură utilități", "text", { lat: "s", grup: "Document", cond: { camp: "fel", val: "refacturare" } }),
    C("total_factura", "Total factură (fără TVA)", "numar", { cond: { camp: "fel", val: "refacturare" } }),
    C("parte_refacturata", "Parte refacturată (fără TVA)", "numar", { cond: { camp: "fel", val: "refacturare" } }),
    C("cota", "Cota TVA", "cota_tva", { cond: { camp: "fel", val: ["chirie_platita", "chirie_incasata", "refacturare"] }, optional: true, ajutor: "Se cere la chiria taxabilă și la refacturare; nu la chiria de la persoană fizică sau la cea scutită." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "perisabilitati", titlu: "Perisabilități și scăzăminte", ruta: "nota-perisabilitati", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("valoare_intrari", "Valoare intrări (bază calcul)"),
    C("procent_limita", "Procent limită HG 831/2004 (%)"),
    C("pierdere_constatata", "Pierdere constatată"),
    C("cont_stoc", "Cont stoc", "text", { sugestie: "371" }),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("degradare_dovedita_distrusa", "Bunuri degradate calitativ și distruse, dovedit", { ajutor: "Da: fără ajustarea TVA pe pierderea peste limită; Nu: ajustarea 635 = 4426." }) ] },
  { cat: "Diverse", cheie: "sgr", titlu: "SGR - garanție ambalaje", ruta: "nota-sgr", frecventa: "lunar", faraPropunere: "garanțiile SGR nu se recunosc separat pe facturi și pe raportul Z", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["achizitie","Achizi\u021bie (garan\u021bii pl\u0103tite)"],["vanzare","V\u00e2nzare (garan\u021bii \u00eencasate)"],["restituire","Restituire"],["autofactura","Autofactura SGR"],["virare","Virare"]] }),
    C("nr_ambalaje", "Nr. ambalaje (0,50 lei/buc)", "numar", { optional: true }),
    C("suma", "Suma (alternativ la nr.)", "numar", { optional: true }),
    C("sursa", "Sursa", "select", { optiuni: [["casa","Casa"],["banca","Banca"]], cond: { camp: "operatie", val: ["vanzare", "restituire"] } }),
    C("catre", "Virarea garanțiilor", "select", { cond: { camp: "operatie", val: "virare" }, optiuni: [["furnizor","Către furnizor (462 = 401)"],["plata","Plată directă (462 = 5121)"]] }),
    C("garantii_returnate", "Garanții returnate (încasate de la RetuRO)", "numar", { cond: { camp: "operatie", val: "autofactura" } }),
    C("tarif_gestionare", "Tarif de gestionare (cu TVA)", "numar", { cond: { camp: "operatie", val: "autofactura" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "autofactura" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "ong", titlu: "Operațiuni ONG (OMFP 3103/2017)", ruta: "nota-ong", frecventa: "lunar", faraPropunere: "registrul membrilor și al cotizațiilor nu există în aplicație", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["venit","Venit AFSP"],["scutire","Calcul scutire art. 15 CF"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "operatie", val: "venit" } }),
    C("fel", "Fel venit", "select", { optiuni: [["cotizatie","Cotizație (731)"],["contributie","Contribuție"],["donatie","Donație (733)"],["sponsorizare","Sponsorizare primită (733)"],["financiar","Financiar (734)"]], cond: { camp: "operatie", val: "venit" } }),
    C("sursa", "Încasat în", "select", { cond: { camp: "operatie", val: "venit" }, optiuni: [["casa","Casă (5311)"],["banca","Bancă (5121)"]] }),
    C("venituri_economice", "Venituri economice ale anului", "numar", { cond: { camp: "operatie", val: "scutire" } }),
    C("venituri_neimpozabile", "Venituri neimpozabile ale anului", "numar", { cond: { camp: "operatie", val: "scutire" } }),
    C("curs_eur", "Curs EUR (BNR)", "numar", { cond: { camp: "operatie", val: "scutire" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
{ cat: "Diverse", cheie: "lichidare", titlu: "Lichidare / radiere firmă", ruta: "nota-lichidare", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Operație", "select", { optiuni: [["vanzare_activ","Vânzare activ la lichidare"],["partaj","Partaj către asociați"]] }),
    C("pret", "Preț vânzare", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("valoare_bruta", "Valoare brută activ", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("amortizare_cumulata", "Amortizare cumulată", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "operatie", val: "vanzare_activ" }, sugestie: "2131" }),
    C("cont_amortizare", "Cont amortizare", "text", { cond: { camp: "operatie", val: "vanzare_activ" }, sugestie: "2813" }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("descriere", "Descriere", "text", { optional: true, ajutor: "La partaj, capitalul, rezervele și profitul vin din soldurile conturilor, împărțite pe asociații din Date firmă." }) ] },
];

const CATEGORII = [...new Set(REGISTRU.map((o) => o.cat))];
// [lotul 10, pct.9, comanda Costin 20.10.2026] „separă-le pe cele lunare sau recurente (TVA la încasare, valută, avansuri și altele) de cele
// rare (lichidare, reevaluare imobilizări etc.). Pentru cele lunare, aplicația propune nota din datele firmei; formularul manual rămâne
// pentru cele rare.” Fiecare intrare are `frecventa` („lunar” = lunară sau recurentă; „rar”); o lunară are fie `propune` (unde o propune
// aplicația din datele firmei — formularul rămâne pentru cazurile speciale), fie `faraPropunere` (de ce aplicația n-are încă datele din
// care s-o propună — fără să inventeze). Gard: core/test_lot10_operatiuni_frecventa.py.
const GRUPURI = [
  ["lunar", "Lunare și recurente", "Aplicația propune singură nota acolo unde are datele firmei (scrie mai jos unde); formularul de aici rămâne pentru cazurile speciale."],
  ["rar", "Rare", "Operațiuni ocazionale: nota se completează din formular."],
];

// [lotul 14, 687] ce propune aplicația singură (explicațiile lungi) stă în cardul de sub titlu, nu între butoane
const CU_PROPUNERE = REGISTRU.filter((o) => o.propune);

// [drepturi_rol 04.10.2026] Fiecare operațiune merge pe ruta ei (`POST /tenants/{tenant_id}/<ruta>`), deci acțiunea se
// DERIVĂ din registru, nu se scrie a doua oară. Butonul o poartă ca `data-actiune` — poarta globală (drepturi.js)
// îl scoate dacă serverul o refuză. `core/test_drepturi_ui.py` verifică: fiecare `ruta` din REGISTRU e o rută reală.
export const actiuneOp = (o) => "POST /tenants/{tenant_id}/" + o.ruta;

/** [lotul 13] Ce mai spune răspunsul operației, pe lângă notă, într-o frază fiecare: regimul chiriei (531), reluarea subvenției (528),
 *  partea nedeductibilă a provizionului (512), factura deja primită (506), creditul de sponsorizare (532), evidența în afara bilanțului
 *  (507), numărul de inventar și cursul BNR folosit (521 / 537). */
// [lotul 13, 507] textul operației fără rânduri în bilanț (scoaterea din folosință, garanția: `mesaj`; comodatul: `extrabilant_text`)
function faraNote(r) {
  return r ? (r.mesaj || r.extrabilant_text || "") : "";
}

export function detaliiOperatie(r) {
  if (!r) return [];
  const d = [];
  // [lotul 13, 670 b] decontul spune ce s-a întâmplat cu diurna: partea neimpozabilă și cea care pleacă în statul de plată
  const dz = r.diurna;
  if (dz) d.push(`${r.salariat ? r.salariat + ": " : ""}diurnă neimpozabilă ${bani(dz.neimpozabil)} lei (plafon ${bani(dz.plafon_zi)} lei/zi × ${dz.zile})`
    + (Number(dz.impozabil) > 0 ? `; peste plafon ${bani(dz.impozabil)} lei, venit salarial — intră în statul de plată ${r.excedent_in_stat || ""} (impozit, contribuții, D112).` : "; nimic peste plafon."));
  if (r.dobanda_din) d.push(`Dobânda se plătește din ${r.dobanda_din}.`);   // [lotul 13, 524] dobânda angajată stabilită de aplicație
  if (r.regim && r.cost == null) d.push(`Chiria e ${r.regim}.`);   // chiria încasată (531); aurul își spune regimul mai jos
  if (r.reluare) d.push(r.reluare);
  if (r.nedeductibil && Number(r.nedeductibil) > 0) d.push(`Deductibil fiscal: ${bani(r.deductibil || 0)} lei; nedeductibil: ${bani(r.nedeductibil)} lei.`);
  if (r.ajustare_fiscala) d.push(r.ajustare_fiscala);
  if (r.factura_furnizor) d.push(`Factura furnizorului e ${r.factura_furnizor}.`);
  if (r.credit_fiscal && r.credit_fiscal.credit) d.push(r.credit_fiscal.credit);
  if (!faraNote(r) && (r.extrabilant || []).length) d.push(`În afara bilanțului: ${r.extrabilant.join("; ")}.`);
  if (r.numar_inventar) d.push(`Numărul de inventar: ${r.numar_inventar}; activul intră în registru la validarea notei.`);
  if (r.curs && r.moneda && r.moneda !== "RON") d.push(`${bani(r.valoare_valuta)} ${r.moneda} × ${String(r.curs).replace(".", ",")} (cursul BNR valabil la exigibilitate, ${r.exigibilitate}) = ${bani(r.valoare)} lei.`);
  if (r.factura_numar) d.push(`Factura emisă: ${r.factura_numar} (în Facturi emise).`);
  // [lotul 13, 510 / 548] ce a luat aplicația din stoc: costul bunului ieșit și coeficientul diferențelor de preț
  if (r.pret_cumparare != null) d.push(`Prețul de cumpărare = valoarea bunului ieșit din stoc (CMP): ${bani(r.pret_cumparare)} lei; marja ${bani(r.marja_bruta)} lei.`);
  if (r.cost != null && r.regim) d.push(`Livrarea e ${r.regim === "taxare_inversa" ? "cu taxare inversă (art. 331 alin. (2) lit. h))" : "scutită (art. 313 alin. (3))"}; aurul a ieșit din stoc la CMP: ${bani(r.cost)} lei (607 = 371).`);
  if (r.numar_factura) d.push(`Factura emisă: ${r.numar_factura} (în Facturi emise); produsul a ieșit din stoc (711 = 345).`);
  if (r.coeficient_348 != null && r.numar_factura) d.push(`Coeficientul diferențelor de preț (348): ${String((Number(r.coeficient_348) * 100).toFixed(4)).replace(".", ",")}% (OMFP 1802/2014 pct. 286).`);
  if (r.document && r.produs) d.push(`${r.produs} a intrat în ${r.gestiune} (cantitatea: ${cantitate(r.cantitate)}), cu ${r.document}.`);
  return d;
}

export async function ecranOperatiuni(corp, nav, t) {
  let opCurenta = null;

  const lista = (c) => {
    if (c) corp = c;
    nav.setInapoi(undefined);
    corp.innerHTML = `
      <h2 class="pf-titlu">Opera\u021biuni speciale</h2>
      <p class="pf-intro">Note contabile pentru opera\u021biuni punctuale. Toate intr\u0103 drept <b>ciorn\u0103</b> \u2014 se valideaz\u0103 din Registru jurnal.</p>
      <div id="op-carduri"></div>
      <div class="rap-tabs" role="tablist" aria-label="Felul operațiunilor">${GRUPURI.map(([frecventa, titlu], i, _t, cls = i ? "rap-tab" : "rap-tab rap-tab-activ") =>
        `<button type="button" class="${cls}" role="tab" aria-selected="${i === 0}" data-grup="${frecventa}" data-fara-actiune="alegerea listei — nu scrie nimic">${esc(titlu)}</button>`).join("")}</div>
      ${GRUPURI.map(([frecventa, , intro], i) => `
        <section class="op-grup" data-frecventa="${frecventa}" role="tabpanel"${i ? " hidden" : ""}>
          ${i ? `<p class="ecran-nota">${esc(intro)}</p>` : ""}
          <div style="columns:300px;column-gap:12px">
          ${CATEGORII.filter((cat) => REGISTRU.some((o) => o.cat === cat && o.frecventa === frecventa)).map((cat) => `
            <div class="op-categorie" style="display:block;break-inside:avoid;margin-bottom:10px;background:var(--fundal);border:1px solid var(--linie);border-radius:var(--raza);padding:10px 14px">
              <div class="pf-frand-nume" style="margin-bottom:6px">${esc(cat)}</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px">
                ${REGISTRU.filter((o) => o.cat === cat && o.frecventa === frecventa).map((o) =>
                  `<button class="buton-secundar" data-op="${o.cheie}" data-actiune="${actiuneOp(o)}">${esc(o.titlu)}</button>`).join("")}
              </div>
            </div>`).join("")}
          </div>
        </section>`).join("")}`;
    siraCarduri(corp.querySelector("#op-carduri"), [{ id: "propune", ton: "info",
      text: `Aplicația propune singură nota pentru ${cate(CU_PROPUNERE.length, "operațiune", "operațiuni")}`, titlu: "Ce propune aplicația singură",
      deschide: (fer) => { fer.innerHTML = `<h2 class="pf-titlu">Ce propune aplicația singură</h2><p class="ecran-nota">${esc(GRUPURI[0][2])}</p>
        ${CU_PROPUNERE.map((o) => `<p class="ecran-nota op-propune" data-propune="${o.cheie}"><b>${esc(o.titlu)}</b> — se propune automat: ${esc(o.propune)}</p>`).join("")}`; } }], nav);
    // [lotul 14, 687] două liste (lunare / rare) în file: una la vedere, ca fereastra să încapă pe ecran; prima fereastră deschisă e a lunarelor
    corp.querySelectorAll(".rap-tab[data-grup]").forEach((b) => b.addEventListener("click", () => {
      corp.querySelectorAll(".rap-tab[data-grup]").forEach((x) => {
        const ales = x === b;
        x.classList.toggle("rap-tab-activ", ales);
        x.setAttribute("aria-selected", String(ales));
      });
      corp.querySelectorAll(".op-grup").forEach((g) => { g.hidden = g.dataset.frecventa !== b.dataset.grup; });
    }));
    // [drepturi_rol 04.10.2026] Nicio operațiune permisă (asistent fără „Poate pregăti”): ecranul spune de ce e gol.
    if (!REGISTRU.some((o) => permis(actiuneOp(o)))) {
      corp.querySelectorAll(".op-grup, .rap-tabs, #op-carduri").forEach((g) => g.remove());
      corp.insertAdjacentHTML("beforeend", `<p class="ecran-nota drept-motiv">Operațiunile speciale cer dreptul «Poate pregăti», pe care nu-l ai. Îl acordă administratorul cabinetului, din ecranul Asistenți.</p>`);
    }
    corp.querySelectorAll("[data-op]").forEach((b) => b.addEventListener("click", () => {
      opCurenta = REGISTRU.find((o) => o.cheie === b.dataset.op);
      nav.mergi(opCurenta.titlu, formular);
    }));
  };

  const formular = (corpNou) => {
    if (corpNou) corp = corpNou;
    const ziAzi = dataIso();
    const camp = (c, clasaLat = "") => {
      const cond = c.cond ? ` data-cond-camp="${c.cond.camp}" data-cond-val="${[].concat(c.cond.val).join("|")}"` : "";
      let input;
      if (c.tip === "select") {
        // [R151] `neales` = o intrebare la care aplicatia NU are voie sa raspunda in locul
        // omului. Fara ea, un `select` obligatoriu vine cu prima optiune deja aleasa — ceea ce
        // pentru o alegere JURIDICA (art. 291 alin. 5) ar fi un default tacit imbracat in
        // interfata. Campul ramane OBLIGATORIU: gol -> refuzul lângă câmp (`eroareCamp`), ca la orice altul.
        // [comanda Costin 07.10.2026, „Cele 33 de chei” — DS cap.17] Regula e acum a MOTORULUI: ORICE select obligatoriu
        // pornește cu „— alege —” (sau textul lui `neales`). Măsurat: 36 de selecturi obligatorii veneau cu prima opțiune aleasă
        // (felul operației, termenul creditului 519/162, metoda de amortizare) — o alegere fiscală făcută de ecran.
        const gol = c.optional ? '<option value="" data-alege>-</option>'
          : `<option value="" data-alege selected>${esc(c.neales || "— alege —")}</option>`;   // [15.1, 720] „— alege —” nu e buton: nimic ales la început
        input = `<select id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" data-butoane="">${gol + c.optiuni.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select>`;
      } else if (c.tip === "cota_tva") {
        // [15.1, 722 / 676.1] cota nu se tastează: grup de alegere cu cotele legale la data documentului (`facturi/numerotare?data=`)
        input = `<select id="op-${c.nume}" class="camp-input op-cota-tva" aria-label="${esc(c.eticheta)}" data-butoane=""><option value="" data-alege selected>— alege —</option></select>`;
      } else if (c.tip === "mijloc_fix") {
        // [decizia Costin 07.10.2026, C4] „«ID mijloc fix» la reevaluare și casare: devine listă din registrul activelor firmei.”
        // Până azi era un câmp numeric: contabilul trebuia să știe ID-ul intern, iar refuzul îi cerea „alege-l din listă” fără listă.
        input = `<select id="op-${c.nume}" class="camp-input op-mijloc-fix" aria-label="${esc(c.eticheta)}"><option value="">— se încarcă registrul activelor… —</option></select>`;
      } else if (c.tip === "salariat") {
        // [lotul 13, 670 a] salariatul se alege din salariații firmei (Salarizare), nu se scrie: 542 se urmărește pe persoană
        input = `<select id="op-${c.nume}" class="camp-input op-salariat" aria-label="${esc(c.eticheta)}"><option value="">— se încarcă salariații… —</option></select>`;
      } else if (c.tip === "cui") {
        // [lotul 13, deficiențele 506 / 633] partenerul se alege din Parteneri (lista firmei, după nume sau CUI) sau se scrie CUI-ul și
        // „Verifică” aduce denumirea de la ANAF — același drum ca la „Emite factură” (`#em-verifica`, `date_anaf.legaDateAnaf`)
        input = `<div class="em-benef"><input type="text" id="op-${esc(c.nume)}" class="camp-input op-cui" data-nume-camp="${c.numeCamp || ""}" list="op-${esc(c.nume)}-lista" autocomplete="off" aria-label="${esc(c.eticheta)}">
          <button type="button" class="buton-secundar em-buton-sec" id="op-${esc(c.nume)}-verifica" data-fara-actiune="citire ANAF; salvarea formularului poartă acțiunea">Verifică</button></div>
          <datalist id="op-${esc(c.nume)}-lista"></datalist><div class="em-cui-stare" id="op-${esc(c.nume)}-stare" aria-live="polite"></div>`;
      } else if (c.tip === "cont_trezorerie") {
        input = `<select id="op-${esc(c.nume)}" class="camp-input op-lista-date" data-ce="cont_trezorerie" data-butoane="" aria-label="${esc(c.eticheta)}"><option value="" data-alege>— se încarcă planul de conturi… —</option></select>`;
      } else if (c.tip === "obiect" || c.tip === "factura_neincasata") {
        // [lotul 13, 508 / 511] obiectul de inventar / factura neîncasată se aleg din ce are aplicația; valoarea vine de la ele
        input = `<select id="op-${c.nume}" class="camp-input op-lista-date" data-ce="${c.tip}" aria-label="${esc(c.eticheta)}"><option value="">— alege întâi operația —</option></select>`;
      } else if (c.tip === "articol") {
        // [lotul 13, 510 / 548] bunul din fișa de magazie (produse finite 345 / mărfuri 371), cu stocul lui sub câmp
        input = `<input type="text" id="op-${esc(c.nume)}" class="camp-input op-articol" data-fel-stoc="${esc(c.felStoc)}"${c.nou ? " data-nou" : ""} list="op-${esc(c.nume)}-lista" autocomplete="off" aria-label="${esc(c.eticheta)}">
          <datalist id="op-${esc(c.nume)}-lista"></datalist><div class="em-cui-stare" id="op-${esc(c.nume)}-stare" aria-live="polite"></div>`;
      } else if (c.tip === "catalog") {
        // [lotul 13, 521] codul din Catalogul HG 2139/2004: sub câmp, denumirea și plaja duratei
        input = `<input type="text" id="op-${c.nume}" class="camp-input op-catalog" aria-label="${esc(c.eticheta)}"><div class="em-cui-stare" id="op-${c.nume}-stare" aria-live="polite"></div>`;
      } else if (c.tip === "factura_valuta") {
        // [lotul 13, 524] facturile în valută deschise ale tipului ales (creanțe / datorii), cu soldul rămas și cursul de evidență
        input = `<select id="op-${c.nume}" class="camp-input op-factura-valuta" aria-label="${esc(c.eticheta)}"><option value="">— alege întâi tipul —</option></select>`;
      } else if (c.tip === "moneda") {
        // [lotul 13, 631 / 670 b] moneda din lista facturii (`MONEDE`), nu scrisă de mână
        input = `<select id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}"><option value="" selected>— alege moneda —</option>${(c.cuRon ? ["RON"] : []).concat(MONEDE).map((m) => `<option value="${m}">${m === "RON" ? "RON (lei)" : m}</option>`).join("")}</select>`;
      } else if (c.tip === "data") {
        input = `<input type="date" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">`;
      } else if (c.tip === "numar") {
        input = `<input type="number" step="0.01" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">`;
      } else {
        input = `<input type="text" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">`;
      }
      // [504] contul uzual se spune în explicație, nu stă în câmp
      const uzual = c.sugestie && /^cont(_|$)/.test(c.nume) ? `De regulă ${c.sugestie}.` : "";
      const ajutor = c.ajutor || uzual ? `<span class="camp-ajutor">${esc([uzual, c.ajutor || ""].filter(Boolean).join(" "))}</span>` : "";
      // [lotul 12, C78.1] răspunsul VIES sub câmp: aceeași linie de stare ca la CUI-ul din „Emite factură” (`.em-cui-stare`; textul serverului cu `.pe-randuri`, DS cap.6 v2.100)
      const vies = c.vies ? `<div class="em-cui-stare" id="op-${c.nume}-vies" aria-live="polite"></div>` : "";
      return `<div class="camp ${clasaLat}"${cond}><label class="camp-eticheta" for="op-${c.nume}">${esc(c.eticheta)}${c.optional ? "" : '<span class="oblig">*</span>'}</label>${input}${ajutor}${vies}</div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">${esc(opCurenta.titlu)}${_OP_AJUTOR[opCurenta.cheie] ? " " + semnAjutor(_OP_AJUTOR[opCurenta.cheie]) : ""}</h2>
      <div class="pf-frand" style="display:block">
        <div id="op-refuz-fel"></div>
        ${formularGrupat(opCurenta.campuri, camp)}
        ${opCurenta.multi ? `<div class="op-multi-bloc"${opCurenta.multiCond ? ` data-cond-camp="${opCurenta.multiCond.camp}" data-cond-val="${[].concat(opCurenta.multiCond.val).join("|")}"` : ""}><div class="pf-frand-nume" style="margin:12px 0 6px">${esc(opCurenta.multiTitlu || "Solduri")}</div><div id="op-multi"></div></div>` : ""}
        ${opCurenta.cheie === "asociati" ? '<div id="op-propunere"></div>' : ""}
        ${opCurenta.spreEmitere ? `<div class="caseta-info op-spre-emitere" id="op-spre-emitere" data-cond-camp="${opCurenta.spreEmitere.camp}" data-cond-val="${opCurenta.spreEmitere.val}" style="display:none"><span class="ci-mesaj">${esc(opCurenta.spreEmitere.text)}</span><p style="margin:8px 0 0"><button type="button" class="buton-secundar" id="op-spre-emitere-buton" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Deschide «Emite factură»</button></p></div>` : ""}
        <div class="bara-fixa">
          <p style="margin-top:4px"><button class="buton-secundar" id="op-renunta" data-fara-actiune="închide formularul fără să scrie nimic">Renunță</button> <button class="buton-primar" id="op-trimite" data-genereaza-nota data-actiune="${actiuneOp(opCurenta)}">Genereaz\u0103 nota (ciorn\u0103)</button></p>
          <p class="ds-motiv-inactiv" id="op-motiv-inactiv" aria-live="polite"></p>
          <div id="op-mesaj"></div>
        </div>
      </div>`;

    // [lotul 10, deficiența 430b, comanda Costin 20.10.2026] „nu se cer asociații și cotele lor, deci nu se vede cât revine fiecăruia și cât
    // impozit se reține pe fiecare”: la dividend, tabelul împărțirii (asociat, cota, brut, impozit, net) se arată ÎNAINTE de generare, din
    // asociații de la data hotărârii (Date firmă → Asociați) — aceleași reguli ca nota (`GET …/dividende-impartire`, nu scrie nimic)
    const zonaProp = corp.querySelector("#op-propunere");
    const tabelAsociati = (p) => `<table class="fd-tabel" id="op-div-tabel">
        <thead><tr><th>Asociat</th><th class="fd-td-num">Cota</th><th class="fd-td-num">Dividend brut</th><th class="fd-td-num">Impozit ${esc(p.cota || "")}</th><th class="fd-td-num">Net</th></tr></thead>
        <tbody>${(p.asociati || []).map((a) => `<tr><td>${esc(a.nume || "")}</td><td class="fd-td-num">${esc(a.cota)}</td><td class="fd-td-num">${bani(a.brut)}</td><td class="fd-td-num">${bani(a.impozit)}</td><td class="fd-td-num">${bani(a.net)}</td></tr>`).join("")}
        </tbody><tfoot><tr><td><b>Total</b></td><td></td><td class="fd-td-num"><b>${bani(p.brut)}</b></td><td class="fd-td-num"><b>${bani(p.impozit)}</b></td><td class="fd-td-num"><b>${bani(p.net)}</b></td></tr></tfoot>
      </table>`;
    const mesajIn = (zona, txt, tip) => { const d = document.createElement("div"); zona.appendChild(d); arataMesaj(d, txt, tip); };
    const arataImpartirea = (p, titlu) => {
      zonaProp.innerHTML = `<div class="pf-frand-nume" style="margin-top:12px">${esc(titlu)}: ${esc(p.document)}${p.cont_sursa ? `, din contul ${esc(p.cont_sursa)}` : ""}</div>${tabelAsociati(p)}`;
      // avertismentul despre sursa profitului e o afirmație tipată (`afirmatie.motiv`, decizia 21.08), ca în firme.js
      if (p.afirmatie && p.afirmatie.motiv) mesajIn(zonaProp, p.afirmatie.motiv, "avert");
    };
    const cerereNoua = ultimaCerere();   // [C103] brutul / datele editate în șir: numai împărțirea ultimelor valori ajunge pe ecran
    const propuneImpartirea = async () => {
      const actuala = cerereNoua();   // și golirea (altă operație) oprește o cerere în zbor
      const v = (n) => (corp.querySelector(`#op-${n}`) || {}).value || "";
      if (!zonaProp) return;
      if (v("operatie") !== "dividend" || !v("brut") || !v("data_hotarare")) { zonaProp.innerHTML = ""; return; }
      const q = new URLSearchParams({ brut: v("brut"), data_hotarare: v("data_hotarare"), numar_hotarare: v("numar_hotarare"),
                                      interimar: v("interimar") || "0", data: v("data") });
      try {
        const p = await api.get(`/tenants/${t.id}/dividende-impartire?${q}`);
        if (!actuala()) return;
        arataImpartirea(p, "Împărțirea pe asociați");
      } catch (e) {
        if (!actuala()) return;
        // refuzul (fără asociați, peste profitul disponibil) se vede înainte de generare, ca avertisment; butonul spre Date firmă îl pune api.js
        zonaProp.innerHTML = "";
        mesajIn(zonaProp, e.mesaj || e.message || "Împărțirea pe asociați nu s-a putut calcula.", "avert");
      }
    };
    if (zonaProp) corp.querySelector(".pf-frand").addEventListener("change", (ev) =>
      ["op-operatie", "op-brut", "op-data_hotarare", "op-numar_hotarare", "op-interimar", "op-data"].includes(ev.target.id) && propuneImpartirea());

    // [lotul 10, deficiența 430f] „după generare, mesajul nu arată nota și nu duce la ea”: confirmarea (DS cap.6, `arataMesaj` „ok”) numește
    // nota și conturile ei, iar butonul o deschide în Registrul jurnal, în luna ei, evidențiată (același drum ca legătura din notificări)
    const deschideNota = async (nid, data) => {
      const [an, luna] = String(data || "").split("-").map((x) => parseInt(x, 10));
      const { ecranJurnal } = await import("./firme.js?v=b7cceffab4");
      nav.deschide("Registru jurnal", (c2) => ecranJurnal(c2, nav, t, Object.assign({ evidentiaza: nid },
        Number.isFinite(an) && Number.isFinite(luna) ? { an, luna } : {})), { lat: "tabel" });   // [394] Registrul jurnal se deschide lat
    };
    const butoaneNote = (zona, ids, etichete, data) => {
      const rand = document.createElement("p");
      rand.className = "op-note-generate";
      ids.forEach((nid, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "buton-secundar";
        b.id = ids.length === 1 ? "op-deschide-nota" : `op-deschide-nota-${i}`;
        b.dataset.faraActiune = "navigare la Registrul jurnal; validarea de acolo poartă acțiunea";
        b.textContent = `Deschide nota ${String(etichete[i] || "").replace(/^nota\s+/i, "")} în Registrul jurnal`.replace(/\s+/g, " ");
        b.addEventListener("click", () => deschideNota(nid, data));
        rand.appendChild(b);
      });
      zona.appendChild(rand);
    };

    // [multi] randuri repetabile (ex. reevaluare valuta)
    let randuriMulti = opCurenta.multi ? [0] : [];
    const zonaMulti = corp.querySelector("#op-multi");
    const randMulti = (i) => `<div class="grila-campuri grila-campuri-compacta">
      ${opCurenta.subcampuri.map((sc) => {
        if (sc.tip === "select") return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><select id="m${i}-${sc.nume}" class="camp-input" data-butoane=""><option value="" selected>— alege —</option>${sc.optiuni.map(([v,l])=>`<option value="${v}">${esc(l)}</option>`).join("")}</select></div>`;
        const t2 = sc.tip === "numar" ? "number" : "text";
        return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><input type="${t2}" step="0.0001" id="m${i}-${sc.nume}" class="camp-input"></div>`;   // [504] fără text gri
      }).join("")}</div>`;
    if (opCurenta.multi && zonaMulti) {
      zonaMulti.innerHTML = randMulti(0) + '<p><button class="buton-secundar" id="op-plus-rand" data-fara-actiune="rând în formular; salvarea formularului poartă acțiunea">+ Rând</button></p>';
      corp.querySelector("#op-plus-rand").addEventListener("click", () => {
        const i = randuriMulti.length; randuriMulti.push(i);
        const d = document.createElement("div"); d.innerHTML = randMulti(i);
        zonaMulti.insertBefore(d.firstElementChild, corp.querySelector("#op-plus-rand").parentElement);
      });
    }

    // vizibilitate conditionata
    // [07.10.2026] În LANȚ: un câmp se vede numai dacă și câmpul de care depinde se vede (vinovatul cere „Imputabil: Da”, iar
    // „Imputabil” cere „Minus”) — altfel o valoare rămasă într-un select ascuns ar arăta (și ar cere) un câmp fără sens.
    const actualizeazaCond = () => {
      const deps = [...corp.querySelectorAll(".camp[data-cond-camp], .op-multi-bloc[data-cond-camp], .op-spre-emitere[data-cond-camp]")];
      for (let tura = 0; tura < 4; tura++) {
        deps.forEach((l) => {
          const sel = corp.querySelector(`#op-${l.dataset.condCamp}`);
          const parinte = sel && sel.closest(".camp");
          const vizibil = parinte && parinte.style.display !== "none";
          l.style.display = sel && vizibil && l.dataset.condVal.split("|").includes(sel.value) ? "" : "none";
        });
      }
      // [C84] operațiunea care se face din «Emite factură» nu se generează de aici: butonul notei nu se oferă cât e aleasă
      const spre = corp.querySelector(".op-spre-emitere");
      corp.querySelector("#op-trimite").style.display = spre && spre.style.display !== "none" ? "none" : "";
      actualizeazaGrupe(corp);   // [15.1] grupul fără câmp la vedere dispare; grupurile alăturate nu lasă jumătate de ecran goală
    };
    const btnSpre = corp.querySelector("#op-spre-emitere-buton");
    if (btnSpre) btnSpre.addEventListener("click", async () => {   // [C84] peste formular: „←” readuce operațiunea
      const { randeazaEmitere } = await import("./emitere_ecran.js?v=ec25cec559");
      nav.deschide("Emite factură", (c2) => randeazaEmitere(c2, nav, t.id, { inapoi: () => nav.inapoi() }));
    });
    opCurenta.campuri.filter((c) => c.tip === "select").forEach((c) =>
      corp.querySelector(`#op-${c.nume}`).addEventListener("change", actualizeazaCond));
    actualizeazaCond();
    // [15.1, 722 / 676.1] cota TVA: grup de alegere cu cotele legale la DATA documentului; o cotă inexistentă la data aceea nu se poate alege
    const selCota = [...corp.querySelectorAll(".op-cota-tva")];
    const cerereCote = ultimaCerere();
    const incarcaCote = async () => {
      if (!selCota.length) return;
      const actuala = cerereCote();
      const data = (corp.querySelector("#op-data") || {}).value || dataIso();   // [15.1] data documentului; până e aleasă, azi (se spune lângă cotă)
      const ALEGE_OPT = '<option value="" data-alege selected>— alege —</option>';
      try {
        const n = await api.get(`/tenants/${t.id}/facturi/numerotare?data=${encodeURIComponent(data)}`);
        if (!actuala()) return;
        const cote = (n && n.cote_permise) || [];
        selCota.forEach((x) => {
          const camp = x.closest(".camp");
          let nota = camp.querySelector(".cota-la-data");
          if (!nota) {   // ajutorul câmpului și data cotelor stau pe un singur rând
            nota = document.createElement("span");
            nota.className = "camp-ajutor cota-la-data";
            const vechi = camp.querySelector(".camp-ajutor");
            nota.dataset.baza = vechi ? vechi.textContent : "";
            if (vechi) vechi.remove();
            camp.appendChild(nota);
          }
          nota.textContent = [`Cotele legale la ${dataRo(data)}${(corp.querySelector("#op-data") || {}).value ? "" : " (data de azi, până alegi data documentului)"}.`, nota.dataset.baza].filter(Boolean).join(" ");
          const veche = x.value;
          x.innerHTML = cote.length ? ALEGE_OPT + cote.map((q) => `<option value="${q}">${q}%</option>`).join("") : '<option value="" data-alege selected>Nicio cotă de TVA la această dată</option>';
          if (cote.map(String).includes(veche)) x.value = veche;
        });
      } catch { if (!actuala()) return; selCota.forEach((x) => { x.innerHTML = '<option value="" data-alege selected>Cotele nu s-au putut citi — reîncearcă</option>'; }); }
    };
    // [15.1, 720] refuzul 714 se vede imediat după alegerea felului (și a datei), nu abia la „Generează nota”: card-rezumat de eroare, cu drum
    // spre Facturi primite; „Generează nota” rămâne inactiv, cu motivul scris dedesubt
    const zonaRefuz = corp.querySelector("#op-refuz-fel");
    const cerereRefuz = ultimaCerere();
    const verificaRefuz = async () => {
      const actuala = cerereRefuz();
      const fel = (corp.querySelector("#op-fel") || {}).value || "";
      const data = (corp.querySelector("#op-data") || {}).value || dataIso();   // [15.1] fără dată aleasă, regimul de azi
      const btn = corp.querySelector("#op-trimite");
      const motivEl = corp.querySelector("#op-motiv-inactiv");
      const curat = () => { zonaRefuz.innerHTML = ""; activ(btn); if (motivEl) motivEl.textContent = ""; };
      if (opCurenta.cheie !== "chirie" || !fel || !data) { curat(); return; }
      try {
        const r = await api.get(`/tenants/${t.id}/operatiuni-date?ce=refuz_fel&tip=${encodeURIComponent(fel)}&data=${encodeURIComponent(data)}`);
        if (!actuala()) return;
        if (!r || !r.refuz) { curat(); return; }
        zonaRefuz.innerHTML = "";
        zonaRefuz.appendChild(cardRezumat({ text: "Firma aplică TVA la încasare: factura furnizorului se înregistrează în Facturi primite.", ton: "eroare",
          detalii: r.refuz, actiune: { eticheta: "Deschide Facturi primite", laClic: async () => {
            const { primiteSPV } = await import("./facturi_ecran.js?v=eca02921e0");
            nav.deschide("Facturi primite", (c2) => primiteSPV(c2, nav, t.id, {}));
          } } }));
        inactiv(btn, "Nota nu se poate genera: factura se înregistrează în Facturi primite.");
        if (motivEl) motivEl.textContent = "Nota nu se poate genera: factura se înregistrează în Facturi primite.";
      } catch { if (!actuala()) return; curat(); }
    };
    const dataEl = corp.querySelector("#op-data");
    if (dataEl) dataEl.addEventListener("change", () => { incarcaCote(); verificaRefuz(); });
    const felEl = corp.querySelector("#op-fel");
    if (felEl && opCurenta.cheie === "chirie") felEl.addEventListener("change", verificaRefuz);
    // [15.1, 721] ciorna pe server: formularul început se păstrează pe utilizator și firmă până la salvare sau „Renunță”; după refacere,
    // câmpurile condiționate, cota și refuzul se recalculează din valorile refăcute
    const dupaRefacere = async () => {
      await incarcaCote();
      actualizeazaCond();
      verificaRefuz();
    };
    const idsCiorna = opCurenta.campuri.map((c) => `op-${c.nume}`);
    let pastrare = null;
    incarcaCote().then(() => {
      pastrare = ciornaFormular(corp, "iconta_ciorna_op_" + opCurenta.cheie, idsCiorna, { tenantId: t.id, formular: "op_" + opCurenta.cheie });
      if (pastrare.refacuta) dupaRefacere();
      pastrare.gata.then((r) => { if (r) dupaRefacere(); });
    });
    corp.querySelector("#op-renunta").addEventListener("click", () => { if (pastrare) pastrare.sterge(); nav.inapoiPas(); });
    // [lotul 12, C78.1, comanda Costin 12.2 pct.7: „ecranul nu arată rezultatul VIES (cod valid sau nu, numele firmei) înainte de
    // generare”] la ieșirea din câmpul codului de TVA, verificarea VIES (aceeași rută ca „Emite factură”, `GET …/verifica-vies`): valid, cu
    // statul și numele firmei; invalid; VIES căzut — înainte de „Generează nota”. Tastarea șterge răspunsul codului vechi, iar un răspuns
    // întârziat al codului vechi nu se mai scrie peste cel nou (`ultimaCerere`, C103).
    // codul verificat valid și numele firmei din VIES: confirmarea notei îl numește (răspunsul rutei notei nu-l întoarce pe toate rutele)
    let viesVerificat = null;
    opCurenta.campuri.filter((c) => c.vies).forEach((c) => {
      const inp = corp.querySelector(`#op-${c.nume}`), st = corp.querySelector(`#op-${c.nume}-vies`);
      const cerereVies = ultimaCerere();
      const arata = (text, rau) => { st.textContent = text; st.className = "em-cui-stare" + (rau ? " em-cui-rau pe-randuri" : ""); };
      inp.addEventListener("input", () => { cerereVies(); viesVerificat = null; arata("", false); });
      inp.addEventListener("change", async () => {
        const actuala = cerereVies();
        const cod = inp.value.trim().toUpperCase();
        if (!cod) { arata("", false); return; }
        if (/^(RO)?\d+$/.test(cod)) {
          arata("Codul e românesc: livrarea / prestarea intracomunitară cere un client înregistrat în scopuri de TVA în alt stat membru "
                + "(codul începe cu prefixul statului, ex. DE, IE).", true);
          return;
        }
        arata("se verifică în VIES…", false);
        try {
          const v = await api.get(`/tenants/${t.id}/verifica-vies?cod_tva=${encodeURIComponent(cod)}`);
          if (!actuala()) return;
          if (v && v.stare === "indisponibil") {   // [lotul 13, 550] VIES căzut pentru statul membru nu e un cod invalid
            arata(`VIES n-a putut verifica acum codul: serviciul statului membru e indisponibil${v.eroare ? " (" + v.eroare + ")" : ""}. Nu înseamnă că `
                  + "codul e invalid — reîncearcă peste câteva minute; până atunci nu trata prestarea ca taxabilă în România.", true);
          } else if (v && v.valid) {
            // unele state (ex. DE) nu publică numele: VIES întoarce „---”
            const nume = v.nume && v.nume.trim() !== "---" ? v.nume.trim() : "statul clientului nu publică numele în VIES";
            viesVerificat = { cod, nume: v.nume && v.nume.trim() !== "---" ? v.nume.trim() : "" };
            st.className = "em-cui-stare";
            st.innerHTML = `<span class="em-cui-info">valid în VIES · ${esc(v.tara || cod.slice(0, 2))} · ${esc(nume)}</span>`;
          } else {
            arata("Cod TVA invalid în VIES: clientul nu e persoană impozabilă dovedită, deci serviciul nu se înregistrează aici ca "
                  + "prestare intracomunitară — se facturează cu TVA românesc (art. 278 alin.(3) Cod fiscal).", true);
          }
        } catch (e) {
          if (!actuala()) return;
          st.textContent = (e && e.mesaj) || "VIES nu răspunde acum — încearcă din nou peste un minut.";
          st.className = "em-cui-stare em-cui-rau pe-randuri";
        }
      });
    });
    // [lotul 13, 670 a] salariații firmei în serviciu (aceeași rută ca Salarizare); fără salariați, lista o spune
    const selSal = [...corp.querySelectorAll(".op-salariat")];
    if (selSal.length) {
      api.get(`/tenants/${t.id}/salariati?activ=true`).then((r) => {
        const sal = (r && r.salariati) || [];
        const opt = sal.length
          ? `<option value="">— alege salariatul —</option>` + sal.map((x) =>
              `<option value="${x.id}">${esc([x.nume, x.prenume].filter(Boolean).join(" "))}</option>`).join("")
          : `<option value="">Firma nu are salariați în Salarizare</option>`;
        selSal.forEach((s2) => { s2.innerHTML = opt; });
      }).catch(() => selSal.forEach((s2) => { s2.innerHTML = `<option value="">Salariații nu s-au putut încărca — reîncearcă</option>`; }));
    }
    // [lotul 13, 524] facturile în valută deschise, la tipul și data alese (`GET …/operatiuni-date?ce=facturi_valuta`)
    const selFv = corp.querySelector(".op-factura-valuta");
    if (selFv) {
      const cerereFv = ultimaCerere();
      const incarcaFv = async () => {
        const actuala = cerereFv();
        const tip = (corp.querySelector("#op-tip") || {}).value || "";
        if (!tip) { selFv.innerHTML = `<option value="">— alege întâi tipul —</option>`; return; }
        selFv.innerHTML = `<option value="">— se încarcă facturile… —</option>`;
        try {
          const r = await api.get(`/tenants/${t.id}/operatiuni-date?ce=facturi_valuta&tip=${tip}&data=${encodeURIComponent((corp.querySelector("#op-data") || {}).value || "")}`);
          if (!actuala()) return;
          const fs = (r && r.facturi) || [];
          selFv.innerHTML = fs.length ? `<option value="">— alege factura —</option>` + fs.map((f) =>
            `<option value="${f.id}">${esc(f.document)} · ${esc(f.partener || "")} · rămas ${bani(f.rest_valuta)} ${esc(f.moneda)} · curs de evidență ${esc(String(f.curs_evidenta).replace(".", ","))} (${esc(f.curs_din)})</option>`).join("")
            : `<option value="">Nicio ${tip === "creanta" ? "factură emisă" : "factură primită"} în valută cu sold rămas (contată prin notă validată)</option>`;
        } catch (e) {
          if (!actuala()) return;
          selFv.innerHTML = `<option value="">Facturile nu s-au putut încărca — reîncearcă</option>`;
        }
      };
      ["#op-tip", "#op-data"].forEach((id) => { const el = corp.querySelector(id); if (el) el.addEventListener("change", incarcaFv); });
    }
    // [lotul 13, 506 / 633] partenerii firmei (Parteneri) în lista câmpului CUI; „Verifică” la ANAF / VIES aduce denumirea
    const campuriCui = [...corp.querySelectorAll(".op-cui")];
    if (campuriCui.length) {
      // partenerii din documentele firmei (`GET parteneri-firma`, ca fișa partenerului); `GET parteneri` e rezumatul soldurilor de preluare
      api.get(`/tenants/${t.id}/parteneri-firma`).then((r) => {
        const ps = ((r && r.parteneri) || []).filter((p) => p.cui);
        campuriCui.forEach((inp) => {
          const dl = corp.querySelector(`#${inp.id}-lista`);
          if (dl) dl.innerHTML = ps.map((p) => `<option value="${esc(p.cui)}">${esc(p.nume || "")}</option>`).join("");
          inp.addEventListener("change", () => {   // partenerul ales din listă: denumirea lui
            const p = ps.find((x) => String(x.cui) === inp.value.trim());
            const tinta = inp.dataset.numeCamp && corp.querySelector(`#op-${inp.dataset.numeCamp}`);
            if (p && tinta && !tinta.value.trim()) tinta.value = p.nume || "";
          });
        });
      }).catch(() => {});
    }
    // [15.1, 720] câmpul care se deduce din CUI-ul verificat (tipul proprietarului) se ascunde cât CUI-ul e verificat și se cere iar dacă CUI-ul se schimbă
    const deduDinCui = (inp, verificat) => {
      opCurenta.campuri.filter((c) => c.deduceDinCui === inp.id.replace(/^op-/, "")).forEach((c) => {
        const el = corp.querySelector(`#op-${c.nume}`);
        if (!el) return;
        if (verificat) el.value = c.valoareCuiVerificat;
        else if (el.closest(".camp").classList.contains("camp-dedus")) el.value = "";
        el.closest(".camp").classList.toggle("camp-dedus", verificat);
      });
      actualizeazaGrupe(corp);
    };
    campuriCui.forEach((inp) => {
      const tinta = inp.dataset.numeCamp ? corp.querySelector(`#op-${inp.dataset.numeCamp}`) : null;
      const stare = corp.querySelector(`#${inp.id}-stare`);
      const anaf = legaDateAnaf(inp, [tinta], stare);
      inp.addEventListener("input", () => deduDinCui(inp, false));
      const b = corp.querySelector(`#${inp.id}-verifica`);
      const cerere = ultimaCerere();
      b.addEventListener("click", async () => {
        const cui = inp.value.trim();
        if (!cui || b.disabled) return;
        const actuala = cerere();
        b.disabled = true; b.setAttribute("aria-busy", "true"); b.textContent = "Se verifică…";
        stare.className = "em-cui-stare"; stare.textContent = "se verifică la ANAF…";
        try {
          const r = await api.get(`/tenants/${t.id}/verifica-cui/${encodeURIComponent(cui)}`);
          if (!actuala()) return;
          if (r && r.gasit) {
            anaf.pune([r.denumire], { suprascrie: true });
            deduDinCui(inp, true);   // [15.1, 720] „Verifică” stabilește și tipul (persoană juridică): nu se mai cere separat
            stare.innerHTML = `<span class="em-cui-info">${r.platitor_tva ? "plătitor TVA" : "neplătitor TVA"}${r.inactiv ? " · inactivă fiscal" : ""}</span>`;
          } else { stare.textContent = "CUI negăsit la ANAF"; stare.className = "em-cui-stare em-cui-rau"; }
        } catch (e) {
          if (!actuala()) return;
          stare.textContent = (e && e.mesaj) || "ANAF nu răspunde acum — încearcă din nou peste un minut.";
          stare.className = "em-cui-stare em-cui-rau pe-randuri";
        } finally { b.disabled = false; b.removeAttribute("aria-busy"); b.textContent = "Verifică"; }
      });
    });
    // [lotul 13, 508 / 511] listele din datele firmei: obiectele de inventar (după operație), facturile emise neîncasate
    const listeDate = [...corp.querySelectorAll(".op-lista-date")];
    const cerereListe = ultimaCerere();   // [lotul 13] o încărcare veche nu se scrie peste una nouă
    const incarcaListe = async () => {
      const actuala = cerereListe();
      for (const sel of listeDate) {
        const op = (corp.querySelector("#op-operatie") || {}).value || "";
        let url = null, gol = "", eticheta = null;
        if (sel.dataset.ce === "cont_trezorerie") {
          url = `/tenants/${t.id}/operatiuni-date?ce=conturi_trezorerie`;
          gol = "Planul firmei n-are niciun cont 5124, 5121 sau 5314";
          eticheta = (c) => `${esc(c.cont)} ${esc(c.denumire || "")}`;
        } else if (sel.dataset.ce === "obiect") {
          const stare = op === "dare_folosinta" ? "magazie" : op === "scoatere" ? "folosinta" : "";
          if (!stare) { sel.innerHTML = `<option value="">— alege întâi operația —</option>`; continue; }
          url = `/tenants/${t.id}/operatiuni-date?ce=obiecte&tip=${stare}`;
          gol = stare === "magazie" ? "Niciun obiect intrat și nedat în folosință (intrarea cu nota validată)" : "Niciun obiect dat în folosință (nota validată) și nescos";
          eticheta = (o) => `${esc(o.denumire)} · ${bani(o.valoare)} lei · intrat ${esc(o.data)}`;
        } else {
          url = `/tenants/${t.id}/operatiuni-date?ce=facturi_neincasate&data=${encodeURIComponent((corp.querySelector("#op-data") || {}).value || "")}`;
          gol = "Nicio factură emisă neîncasată";
          eticheta = (f) => `${esc(f.document)} · ${esc(f.partener || "")} · sold ${bani(f.sold)} lei${f.zile == null ? " · fără scadență" : f.zile > 0 ? ` · ${cate(f.zile, "zi", "zile")} de la scadență` : f.zile < 0 ? ` · scadentă peste ${cate(-f.zile, "zi", "zile")}` : " · scadentă azi"}`;
        }
        try {
          const r = await api.get(url);
          if (!actuala()) return;
          const xs = (r && (r.obiecte || r.facturi || r.conturi)) || [];
          // [lotul 13] alegerea omului rămâne aleasă când lista se reîncarcă (data sau operația schimbată) și elementul e tot acolo
          const ales = sel.value;
          sel.innerHTML = xs.length ? `<option value="" data-alege>— alege —</option>` + xs.map((x) => `<option value="${esc(x.id)}">${eticheta(x)}</option>`).join("")
            : `<option value="">${gol}</option>`;
          if (ales && [...sel.options].some((o) => o.value === ales)) sel.value = ales;
        } catch { if (!actuala()) return; sel.innerHTML = `<option value="">Lista nu s-a putut încărca — reîncearcă</option>`; }
      }
    };
    if (listeDate.length) {
      ["#op-operatie", "#op-data", "#op-fel"].forEach((id) => { const el = corp.querySelector(id); if (el) el.addEventListener("change", incarcaListe); });
      incarcaListe();
    }
    // [lotul 13, 510 / 548] bunurile din stoc: lista din fișa de magazie, iar sub câmp stocul și CMP-ul bunului ales
    corp.querySelectorAll(".op-articol").forEach(async (inp) => {
      const lista = corp.querySelector(`#${inp.id}-lista`);
      const st = corp.querySelector(`#${inp.id}-stare`);
      let xs = [];
      try {
        xs = ((await api.get(`/tenants/${t.id}/operatiuni-date?ce=articole&tip=${encodeURIComponent(inp.dataset.felStoc)}`)) || {}).articole || [];
      } catch {
        st.className = "em-cui-stare em-cui-rau"; st.textContent = "Lista bunurilor din stoc nu s-a putut încărca — reîncearcă."; return;
      }
      lista.innerHTML = xs.map((a) => `<option value="${esc(a.denumire)}">${esc(a.denumire)} · în stoc ${esc(cantitate(a.stoc, a.um))}</option>`).join("");
      const arata = () => {
        const v = inp.value.trim().toLowerCase();
        const a = xs.find((x) => String(x.denumire).toLowerCase() === v);
        st.className = "em-cui-stare";
        // un produs nou intră în stoc numai la obținere; la vânzare bunul trebuie să existe
        const nou = inp.hasAttribute("data-nou") && (corp.querySelector("#op-operatie") || {}).value === "obtinere";
        if (a) st.innerHTML = `<span class="em-cui-info">în stoc ${esc(cantitate(a.stoc, a.um))}${a.cmp ? ` · CMP ${bani(a.cmp)} lei` : ""}</span>`;
        else st.textContent = !v ? "" : nou ? "Produs nou: intră în stoc cu unitatea de măsură scrisă." : "Nu e în stoc — alege din listă.";
      };
      inp.addEventListener("input", arata);
      const opSel = corp.querySelector("#op-operatie");
      if (opSel) opSel.addEventListener("change", arata);
      arata();
    });
    // [lotul 13, 521] codul din catalog: denumirea și plaja duratei, sub câmp
    corp.querySelectorAll(".op-catalog").forEach((inp) => {
      const st = corp.querySelector(`#${inp.id}-stare`);
      const cerere = ultimaCerere();
      inp.addEventListener("input", () => { cerere(); st.textContent = ""; st.className = "em-cui-stare"; });
      inp.addEventListener("change", async () => {
        const actuala = cerere();
        const cod = inp.value.trim();
        if (!cod) return;
        try {
          const r = await api.get(`/tenants/${t.id}/operatiuni-date?ce=catalog&tip=${encodeURIComponent(cod)}`);
          if (!actuala()) return;
          if (r.gasit) { st.className = "em-cui-stare"; st.innerHTML = `<span class="em-cui-info">${esc(r.denumire)} · durata între ${r.ani_min * 12} și ${cate(r.ani_max * 12, "lună", "luni")} (${r.ani_min}–${cate(r.ani_max, "an", "ani")})</span>`; }
          else { st.className = "em-cui-stare em-cui-rau"; st.textContent = "Codul nu e în Catalogul HG 2139/2004."; }
        } catch { if (!actuala()) return; st.className = "em-cui-stare em-cui-rau"; st.textContent = "Catalogul nu s-a putut citi — reîncearcă."; }
      });
    });
    // [lotul 13, 529] „la schimbarea operației mesajul vechi rămâne pe ecran”: alegerea altei operații (primul select al formularului)
    // golește confirmarea / refuzul de dinainte — erau ale operației vechi
    const primulSelect = opCurenta.campuri.find((c) => c.tip === "select");
    if (primulSelect) corp.querySelector(`#op-${primulSelect.nume}`).addEventListener("change", () => {
      const z = corp.querySelector("#op-mesaj");
      if (z) z.innerHTML = "";
      curataEroriCamp(corp);
    });
    // [C4] lista mijloacelor fixe ACTIVE ale firmei (registrul activelor, aceeași rută ca ecranul Mijloace fixe)
    const selMf = [...corp.querySelectorAll(".op-mijloc-fix")];
    if (selMf.length) {
      api.get(`/tenants/${t.id}/mijloace-fixe`).then((r) => {
        const active = ((r && r.mijloace) || []).filter((m) => m.activ);
        const opt = active.length
          ? `<option value="">— alege mijlocul fix —</option>` + active.map((m) =>
              `<option value="${m.id}">${esc(m.cod || "")} · ${esc(m.denumire || "")}${m.ramas != null ? " · rămas " + bani(m.ramas) + " lei" : ""}</option>`).join("")
          : `<option value="">Niciun mijloc fix activ în registrul firmei</option>`;
        selMf.forEach((s) => { s.innerHTML = opt; });
      }).catch(() => selMf.forEach((s) => { s.innerHTML = `<option value="">Registrul activelor nu s-a putut încărca — reîncearcă</option>`; }));
    }

    corp.querySelector("#op-trimite").addEventListener("click", async () => {
      const zona = corp.querySelector("#op-mesaj");
      scoateActiuniRefuz(zona);   // butonul spre ecran al refuzului de la clicul trecut
      const corpReq = {};
      // [deficiența 410, clasa — toate formularele] TOATE câmpurile lipsă, fiecare lângă el (și în lista „NU s-a salvat” de lângă
      // buton), nu numai primul (fail-fast, DS cap.6 G10 pct.4)
      curataEroriCamp(corp);
      let lipsa = 0;
      for (const c of opCurenta.campuri) {
        const el = corp.querySelector(`#op-${c.nume}`);
        const ascuns = el.closest(".camp").style.display === "none";
        if (ascuns) continue;
        const v = el.value;
        if (!v && !c.optional) { eroareCamp(corp, "op-" + c.nume, "Completează: " + c.eticheta + "."); lipsa++; continue; }
        const val = c.tip === "numar" || c.tip === "cota_tva" ? parseFloat(v) : c.tip === "mijloc_fix" ? parseInt(v, 10) : v;
        // `trimiteCa`: aceeași cheie, alt câmp (bacșiș: sursa are alte valori la distribuire); `lista`: serverul cere o listă
        if (v) corpReq[c.trimiteCa || c.nume] = c.lista ? [val] : val;
      }
      if (lipsa) return;
      const blocMulti = corp.querySelector(".op-multi-bloc");
      if (opCurenta.multi && blocMulti && blocMulti.style.display !== "none") {
        corpReq[opCurenta.multi] = [...corp.querySelectorAll("#op-multi > div")].map((rand) => {
          const o = {};
          opCurenta.subcampuri.forEach((sc) => {
            const el = rand.querySelector(`[id$="-${sc.nume}"]`);
            if (el && el.value) o[sc.nume] = sc.tip === "numar" ? parseFloat(el.value) : el.value;
          });
          return o;
        }).filter((o) => Object.keys(o).length > 1 || (Object.keys(o).length === 1 && !o.tip));
        if (!corpReq[opCurenta.multi].length) { arataMesaj(zona, "Completează cel puțin un rând.", "eroare"); return; }
      }
      try {
        const r = await api.post(`/tenants/${t.id}/${opCurenta.ruta}`, corpReq);
        if (pastrare) pastrare.sterge();   // [15.1, 721] salvat: formularul se golește
        // [lot 19 defect 13] o operatie de CALCUL (ex. ONG › scutire) nu genereaza nota — nu se spune ca a generat
        // [C5, comanda Costin 07.10.2026] O rută scrie o notă (`inregistrare_id`) sau mai multe (`inregistrari`, ex. chiria cu
        // refacturare): ecranul le citește pe amândouă. Până azi „nicio notă” apărea și când nota-chirie scrisese ciorna (DS cap.27).
        // [258] notele se numesc cum le arată Registrul jurnal (`nota_eticheta` / `note_etichete`, „nr. crt. 5 din 12.03.2026”), nu prin id
        const note = r ? (r.note_etichete || (r.nota_eticheta ? [r.nota_eticheta] : [])) : [];
        const ids = r ? (r.inregistrari || (r.inregistrare_id ? [r.inregistrare_id] : [])) : [];
        if (note.length) {
          // [lotul 11, 8c — decizia 10.3 „reparația centrală”; P1b] drumul unic al confirmării: caseta verde cu conturile și sumele
          // fiecărei note (citite din Registrul jurnal după id), „Generează nota” inactiv cu motivul, reactivat la o modificare a câmpurilor
          const citite = await noteGenerate(t.id, ids, corpReq.data);
          // [401] nota se arată după generare (conturile și suma). [lotul 12, C78.1: „mesajul de confirmare repetă nota de trei ori”] când
          // rândurile notei s-au citit din Registrul jurnal, „Nota: 4111 = 704 1.000,00 lei.” le repeta: rămâne numai textul operațiunii
          // care spune altceva decât conturile și sumele (o mențiune, o explicație), sau conturile când rândurile n-au putut fi citite
          const doarConturi = (x) => !String(x || "").replace(/lei/gi, "").replace(/[\d\s.,=+;:\-−]/g, "");
          const nota = r && r.nota && !(citite.length && doarConturi(r.nota)) ? ` Nota: ${r.nota}.` : "";
          // [C78.1] partenerul din VIES, pe care s-a scris factura (livrarea / prestarea intracomunitară)
          const codTrimis = String(corpReq.cod_tva_client || "").trim().toUpperCase();
          const vies = viesVerificat && codTrimis && viesVerificat.cod === codTrimis
            ? `Client: ${viesVerificat.nume ? viesVerificat.nume + ", " : ""}cod ${codTrimis} valid în VIES.` : "";
          // [lotul 13, 670 e] „confirmarea apare de trei ori”: o singură casetă — nota cu conturile, ce mai e de spus, pasul următor și
          // butonul spre nota din Registrul jurnal, în aceeași casetă
          const caseta = dupaGenerare(zona, corp.querySelector("#op-trimite"), {
            note: (citite.length ? citite : note.map(() => ({ linii: [] }))).map((n, i) => ({ linii: n.linii,
              eticheta: `${note[i] || n.eticheta || ""} — ${stareNota(r)}` })),
            detalii: [vies, nota.trim(), ...detaliiOperatie(r)],
            pas: pasNota(r, note.length > 1),
            reactiveazaLa: [...opCurenta.campuri.map((c) => corp.querySelector(`#op-${c.nume}`)),
                            ...corp.querySelectorAll("#op-multi input, #op-multi select, #op-multi textarea")] });
          if (r.avertisment) mesajIn(zona, r.avertisment, "avert");
          if (ids.length) butoaneNote(caseta || zona, ids, note, corpReq.data);   // data notei = data trimisă (toate operațiunile)
          if (zonaProp && r.asociati) arataImpartirea(r, "Nota împarte dividendul pe asociați");   // [430b] tabelul notei generate
        } else if (faraNote(r)) {
          // [lotul 13, 507] o operație fără rânduri în bilanț (scoaterea din folosință, comodatul, garanția): înregistrarea în afara
          // bilanțului, spusă într-o singură casetă
          dupaGenerare(zona, corp.querySelector("#op-trimite"), { titlu: "Înregistrat în afara bilanțului", note: [], detalii: [faraNote(r), ...detaliiOperatie(r)],
            reactiveazaLa: opCurenta.campuri.map((c) => corp.querySelector(`#op-${c.nume}`)) });
        } else {
          zona.innerHTML = `<p class="pf-intro">Calcul (nu s-a generat nicio notă):</p><ul class="pf-intro">${Object.entries(r || {}).map(([k, v]) => `<li>${esc(k.replace(/_/g, " "))}: <b>${esc(String(v))}</b></li>`).join("")}</ul>`;
        }
      } catch (e) {
        // [410] refuzul serverului care își numește câmpurile: fiecare lângă câmpul lui; restul, în zona formularului
        const peCamp = ((e && e.erori_campuri) || []).filter((x) => eroareCamp(corp, x.camp, x.mesaj)).length;
        arataMesaj(zona, (peCamp ? "Nota nu s-a generat: " : "") + (e.mesaj || e.message || "Nu s-a putut genera nota — verifică datele introduse și reîncearcă."), "eroare");
        // [lotul 13, 551 / 548] refuzul numește ecranul unde se repară (metoda de stoc -> Date firmă): butonul stă după caseta „NU s-a salvat”, nu în
        // zona ascunsă a mesajului (unde l-ar pune `api.js`) — ca la „Trimite în coadă” (`coada_trimite.actiuniRefuz`)
        const det = (e && e.detaliu && typeof e.detaliu === "object") ? e.detaliu : {};
        if (det.ecran && window._navGlobal) butonSpreEcran(actiuniRefuz(zona), det.ecran, window._navGlobal, t.id, { clasa: "buton-secundar", camp: det.camp_ecran || null });
      }
    });
  };

  lista();
}

// precompletari_rest_v1
