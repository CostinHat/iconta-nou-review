// [operatiuni] Ecran generic "Operatiuni speciale" - condus de configuratie.
// O operatiune noua = o intrare in REGISTRU (titlu, ruta, campuri), zero cod nou de ecran.
import { api, ultimaCerere, cate, esc, bani, arataMesaj, semnAjutor, dataIso, stareNota, pasNota, eroareCamp, curataEroriCamp, dupaGenerare, noteGenerate } from "../api.js?v=e38843b1ec";
import { permis } from "../drepturi.js?v=34d0fb0afd";  /* [drepturi_rol 04.10.2026] */
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
// [lotul 07.10 B] câmpurile-cont (`cont`, `cont_*`) cu sugestie se precompletează (DS cap.17 corectat: cazul uzual, vizibil, schimbabil — regula în `camp`)
const CONT_PRECOMPLETAT = (c) => c.tip === "text" && /^cont(_|$)/.test(c.nume) && !!c.sugestie && !c.optional;

const REGISTRU = [
  { cat: "Finanțare", cheie: "leasing", titlu: "Leasing", ruta: "nota-leasing", frecventa: "lunar", faraPropunere: "contractul de leasing (scadențarul ratelor) nu e înregistrat în aplicație", campuri: [
    C("data", "Data", "data"), 
    C("tip", "Tip operațiune", "select", { optiuni: [["primire","Primire bun (financiar)"],["rata","Rată lunară"],["reziduala","Valoare reziduală"],["operational","Chirie leasing operațional"]] }),
    C("valoare_capital", "Valoare capital", "numar", { cond: { camp: "tip", val: "primire" } }),
    C("dobanda_totala", "Dobândă totală", "numar", { cond: { camp: "tip", val: "primire" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "tip", val: "primire" }, sugestie: "2133" }),
    C("capital", "Capital rată", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("dobanda", "Dobândă", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("comision", "Comision", "numar", { cond: { camp: "tip", val: "rata" } }),
    C("valoare_reziduala", "Valoare reziduală", "numar", { cond: { camp: "tip", val: "reziduala" } }),
    C("chirie", "Chirie lunară", "numar", { cond: { camp: "tip", val: "operational" } }),
    C("cont_cheltuiala", "Cont cheltuială", "text", { cond: { camp: "tip", val: "operational" }, sugestie: "612" }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "tip", val: ["rata", "reziduala", "operational"] }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "credit", titlu: "Credite bancare", ruta: "nota-credit", frecventa: "lunar", faraPropunere: "contractul de credit (scadențarul ratelor și al dobânzilor) nu e înregistrat în aplicație", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["primire","Primire credit"],["dobanda","Dobândă"],["plata","Plată rată"],["restanta","Restanță"],["garantie","Garanție"]] }),
    C("tip", "Termen", "select", { optiuni: [["scurt","Sub 1 an (519)"],["lung","Peste 1 an (162)"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "operatie", val: ["primire", "restanta", "garantie"] } }),
    C("fel", "Garanție", "select", { optiuni: [["primita","Primită (8021)"],["acordata","Acordată (8011)"]], neales: "— alege —", cond: { camp: "operatie", val: "garantie" } }),
    C("actiune", "Acțiune", "select", { optiuni: [["inregistrare","Înregistrare"],["eliberare","Eliberare / stingere"]], neales: "— alege —", cond: { camp: "operatie", val: "garantie" } }),
    C("dobanda", "Dobândă", "numar", { cond: { camp: "operatie", val: ["dobanda", "plata"] } }),
    C("rata", "Rata (capital)", "numar", { cond: { camp: "operatie", val: "plata" } }),
    C("comision", "Comision bancar (627)", "numar", { cond: { camp: "operatie", val: "plata" } }),
    DN("dobanda_angajata", "Dobânda a fost înregistrată deja pe 666", { cond: { camp: "operatie", val: "plata" }, ajutor: "Da: se plătește din 1682/5198; Nu: 666 = 5121 direct." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Finanțare", cheie: "asociati", titlu: "Decontări asociați (455/457)", ruta: "nota-asociati", frecventa: "lunar", propune: "Dividendul se împarte singur pe asociații din Date firmă → Asociați, valabili la data hotărârii, și se ia din profitul nerepartizat; scrii suma și hotărârea.", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["dividend","Dividend"],["imprumut","Împrumut asociat"],["regularizare","Regularizare interimare"],["restituire_dividend","Restituire dividend încasată"]] }),
    C("brut", "Dividend brut (total)", "numar", { cond: { camp: "operatie", val: "dividend" }, ajutor: "Se împarte pe asociați după cotele din Date firmă → Asociați, valabile la data hotărârii (Legea 31/1990 art. 67 alin. (2))." }),
    // [lotul 10, deficiența 430c] documentul justificativ al notei: hotărârea adunării asociaților / decizia asociatului unic
    C("numar_hotarare", "Numărul hotărârii (adunarea asociaților sau decizia asociatului unic)", "text", { cond: { camp: "operatie", val: "dividend" } }),
    C("data_hotarare", "Data hotărârii", "data", { cond: { camp: "operatie", val: "dividend" }, ajutor: "Asociații și cotele se iau la data ei; profitul disponibil, la fel." }),
    C("interimar", "Fel", "select", { optiuni: [["0","Anual (1171/457)"],["1","Interimar (463/456)"]], neales: "— alege —", cond: { camp: "operatie", val: "dividend" } }),
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
    C("furnizor_nume", "Furnizor", "text"),
    C("furnizor_cui", "CUI furnizor", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
  ] },  /* [0a_rute_v1] */
  { cat: "Imobilizări și capital", cheie: "reevaluare", titlu: "Reevaluare imobilizări (105)", ruta: "reevaluare-imobilizare", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["reevaluare","Reevaluare MF"],["surplus","Transfer surplus la 1175"]] }),
    C("mijloc_fix_id", "Mijlocul fix", "mijloc_fix", { cond: { camp: "operatie", val: "reevaluare" } }),   // [C4, 07.10.2026] din registru
    C("valoare_justa", "Valoare justă", "numar", { cond: { camp: "operatie", val: "reevaluare" } }),
    C("sold_105_activ", "Sold 105 existent pentru acest activ", "numar", { cond: { camp: "operatie", val: "reevaluare" }, ajutor: "0 dacă activul n-a mai fost reevaluat; o scădere se acoperă întâi din el (105), restul pe 655." }),
    C("pierdere_655_anterioara", "Pierdere din reevaluări anterioare (655)", "numar", { cond: { camp: "operatie", val: "reevaluare" }, ajutor: "0 dacă nu există; o creștere o compensează întâi pe 755, restul pe 105 (OMFP 1802/2014 pct. 111–116)." }),
    C("suma", "Suma surplus", "numar", { cond: { camp: "operatie", val: "surplus" } }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "obiect_inv", titlu: "Obiecte de inventar (303)", ruta: "nota-obiect-inventar", frecventa: "lunar", faraPropunere: "intrarea obiectelor de inventar (NIR pe 303) nu propune darea în folosință", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["achizitie","Achizi\u021bie"],["dare_folosinta","Dare în folosință (603=303)"],["scoatere","Scoatere din folosință"]] }),
    C("valoare", "Valoare"), C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "achizitie" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("durata_sub_1_an", "Durata de utilizare sub un an", { cond: { camp: "operatie", val: "achizitie" }, ajutor: "Da: e obiect de inventar oricare i-ar fi valoarea; Nu: peste pragul mijloacelor fixe se înregistrează ca mijloc fix." }) ] },
  { cat: "Imobilizări și capital", cheie: "provizion", titlu: "Provizioane și ajustări", ruta: "nota-provizion", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["creanta","Ajustare creanțe (491)"],["provizion","Provizion (151)"],["stoc","Ajustare stocuri (39x)"]] }),
    C("actiune", "Acțiune", "select", { optiuni: [["constituire","Constituire"],["reluare","Reluare"]] }),
    C("suma", "Suma"),
    C("cont_ajustare", "Cont ajustare stocuri", "text", { cond: { camp: "fel", val: "stoc" }, sugestie: "397" }),
    C("tip", "Tip provizion", "select", { optiuni: [["litigii","Litigii"],["garantii","Garanții"],["dezafectare","Dezafectare"],["restructurare","Restructurare"],["impozite","Impozite"],["altele","Altele"]], cond: { camp: "fel", val: "provizion" } }),
    C("descriere", "Descriere", "text", { optional: true }),
    C("zile_depasire", "Zile de la scadență (neîncasată)", "numar", { cond: { camp: "fel", val: "creanta" }, ajutor: "Peste 270 de zile: 30% deductibil (art. 26 alin. (1) lit. c))." }),
    DN("garantata", "Creanța e garantată de altă persoană", { cond: { camp: "fel", val: "creanta" } }),
    DN("afiliata", "Debitorul e persoană afiliată", { cond: { camp: "fel", val: "creanta" } }),
    DN("faliment", "Debitorul e în faliment declarat prin hotărâre judecătorească", { cond: { camp: "fel", val: "creanta" }, ajutor: "Da: 100% deductibil (art. 26 alin. (1) lit. j))." }) ] },
  { cat: "Imobilizări și capital", cheie: "productie", titlu: "Producție (711/345)", ruta: "nota-productie", frecventa: "lunar", faraPropunere: "comenzile de producție și costul standard nu sunt înregistrate în aplicație", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["obtinere","Ob\u021binere produse"],["pic","Produc\u021bie \u00een curs (331)"],["vanzare","V\u00e2nzare + desc\u0103rcare"]] }),
    C("cost_standard", "Cost standard", "numar", { cond: { camp: "operatie", val: "obtinere" } }),
    C("cost_efectiv", "Cost efectiv", "numar", { cond: { camp: "operatie", val: "obtinere" } }),
    C("suma", "Suma PIC", "numar", { cond: { camp: "operatie", val: "pic" } }),
    C("moment", "Moment", "select", { optiuni: [["constatare","Constatare"],["reluare","Reluare"]], cond: { camp: "operatie", val: "pic" } }),
    C("pret_vanzare", "Preț vânzare", "numar", { cond: { camp: "operatie", val: "vanzare" } }),
    C("cost_standard_iesit", "Cost standard ieșit", "numar", { cond: { camp: "operatie", val: "vanzare" } }),
    C("coef_348", "Coeficientul diferențelor de preț (348)", "numar", { cond: { camp: "operatie", val: "vanzare" }, ajutor: "0 dacă nu există diferențe; pozitiv = nefavorabilă (711 = 348), negativ = favorabilă." }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "vanzare" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Imobilizări și capital", cheie: "inventariere", titlu: "Inventariere anuală", ruta: "nota-inventariere", frecventa: "rar", campuri: [
    C("data", "Data", "data"),
    C("operatie", "Opera\u021bie", "select", { optiuni: [["plus","Plus stoc"],["plus_mf","Plus mijloc fix"],["minus","Minus"],["casare","Casare"]] }),
    // [C117, lotul 12] la Casare valoarea vine din registrul activelor (mijlocul fix ales, cu amortizarea lui): câmpul nu se mai cere
    C("valoare", "Valoare", "numar", { cond: { camp: "operatie", val: ["plus", "plus_mf", "minus"] } }),
    C("cont_stoc", "Cont stoc", "text", { cond: { camp: "operatie", val: ["plus", "minus"] }, sugestie: "371" }),
    DN("imputabil", "Imputabil", { cond: { camp: "operatie", val: "minus" } }),
    C("valoare_imputare", "Valoare imputare", "numar", { cond: { camp: "imputabil", val: "true" } }),
    C("vinovat", "Cui se impută", "select", { cond: { camp: "imputabil", val: "true" }, optiuni: [["salariat","Salariat (4282)"],["tert","Terț (461)"]] }),
    C("denumire", "Denumire mijloc fix", "text", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "operatie", val: "plus_mf" }, sugestie: "2131" }),
    C("cont_amortizare", "Cont amortizare", "text", { cond: { camp: "operatie", val: "plus_mf" }, sugestie: "2813" }),
    C("dnf_luni", "Durat\u0103 normal\u0103 (luni)", "numar", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("data_pif", "Dat\u0103 punere \u00een func\u021biune", "data", { cond: { camp: "operatie", val: "plus_mf" } }),
    C("metoda", "Metod\u0103 amortizare", "select", { cond: { camp: "operatie", val: "plus_mf" }, optiuni: [["liniara","Liniar\u0103"],["degresiva","Degresiv\u0103"],["accelerata","Accelerat\u0103"],["superaccelerata","Superaccelerat\u0103"]] }),
    DN("destinatie_cd", "Destinat cercetării-dezvoltării", { cond: { camp: "operatie", val: "plus_mf" }, ajutor: "Da: amortizarea accelerată e permisă pe orice cont (CF art. 20 alin. (1) lit. b))." }),
    C("mijloc_fix_id", "Mijlocul fix", "mijloc_fix", { cond: { camp: "operatie", val: "casare" } }),   // [C4, 07.10.2026] din registru
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "minus" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("asigurat_sau_distrus", "Bunul lipsă era asigurat sau a fost distrus", { cond: { camp: "operatie", val: "minus" }, ajutor: "Da: fără ajustarea TVA dedusă pe bunul lipsă (art. 304); Nu: ajustarea 635 = 4426 pe costul bunului." }) ] },

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
  { cat: "TVA regimuri speciale", cheie: "marja", titlu: "Vânzare regim marjă (second-hand)", ruta: "vanzare-marja", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"), C("pret_vanzare", "Preț vânzare"), C("pret_cumparare", "Preț cumpărare"),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
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
    C("furnizor_nume", "Furnizor", "text"),
    C("furnizor_cui", "CUI furnizor (RO, plătitor TVA)", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("categorie", "Categorie art. 331", "select", { optiuni: [["deseuri","Deșeuri"],["masa_lemnoasa","Masă lemnoasă"],["cereale","Cereale"],["certificate_emisii","Certificate emisii"],["energie_electrica","Energie electrică"],["certificate_verzi","Certificate verzi"],["cladiri_terenuri","Clădiri/terenuri"],["aur_investitii","Aur de investiții"],["telefoane","Telefoane"],["circuite_integrate","Circuite integrate"],["console_tablete","Console/tablete"],["gaze_naturale","Gaze naturale"]] }),
    C("valoare", "Valoare (fără TVA)"),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    DN("furnizor_platitor_tva", "Furnizor plătitor TVA"),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "agricultor_achizitie", titlu: "Achiziție de la agricultor (compensare 8%)", ruta: "achizitie-agricultor", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare (fără taxă)"),
    C("cont_cheltuiala", "Cont cheltuială/stoc", "text", { sugestie: "301" }),
    DN("agricultor_in_registru", "Agricultor în registru"),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "TVA regimuri speciale", cheie: "aur", titlu: "Aur de investiții (art. 313)", ruta: "vanzare-aur-investitii", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["lingou","Lingou"],["plancheta","Plachetă"],["moneda","Moneda"]] }),
    C("puritate", "Puritate (ex. 995)", "numar"),   // [C6 vecin de tip] serverul o citește ca număr (tva_aur._numar)
    C("suma", "Valoare vânzare"),
    C("calitate_client", "Client", "select", { optiuni: [["PF","Persoană fizică"],["PJ","Persoană juridică"]] }),
    C("client_identificare", "Identificare client", "text"),
    C("an_emisie", "Anul emisiunii monedei", "numar", { cond: { camp: "tip", val: "moneda" }, ajutor: "Moneda de aur e de investiții dacă e emisă după 1800 (art. 313 alin. (1) lit. b))." }),
    C("pret_unitar", "Prețul monedei", "numar", { cond: { camp: "tip", val: "moneda" } }),
    C("valoare_aur", "Valoarea aurului conținut", "numar", { cond: { camp: "tip", val: "moneda" }, ajutor: "Prețul nu poate depăși valoarea aurului cu mai mult de 80% (art. 313 alin. (1) lit. b))." }),
    DN("optiune_taxare", "Opțiune de taxare", { cond: { camp: "calitate_client", val: "PJ" }, ajutor: "Da: taxare inversă în locul scutirii — permisă numai către o persoană impozabilă (art. 313 alin. (4)–(5))." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Extern", cheie: "decont_valuta", titlu: "Decontare în valută (665/765)", ruta: "decontare-valuta", frecventa: "lunar", faraPropunere: "plata facturii în valută din Bancă nu calculează diferența de curs la decontare (665 / 765)", campuri: [
    C("data", "Data", "data"),
    C("tip", "Tip", "select", { optiuni: [["creanta","Încasare creanță"],["datorie","Plată datorie"]] }),
    C("valoare_valuta", "Valoare în valută"),
    C("moneda", "Moneda (EUR/USD...)", "text", { sugestie: "EUR" }),
    C("curs_evidenta", "Curs de evidență"),
    C("cont_tert", "Cont terț", "text", { sugestie: "4111" }),
    C("cont_banca", "Cont bancă", "text", { sugestie: "5124" }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("in_lei_cu_clauza", "Factură în lei cu clauză valutară", { ajutor: "Da: diferența pe 668/768 (OMFP 1802/2014 pct. 94 lit. b)); Nu: pe 665/765." }) ] },
  { cat: "Extern", cheie: "achizitie_ic", titlu: "Achiziție intracomunitară", ruta: "achizitie-ic", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare (RON)"),
    C("cod_tva_furnizor", "Cod TVA furnizor UE (ex. DE123456789)", "text"),
    C("numar", "Nr. factură furnizor", "text"),
    C("furnizor_nume", "Furnizor", "text", { optional: true }),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("tip", "Tip", "select", { optiuni: [["bunuri","Bunuri"],["servicii","Servicii"]] }),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("data_faptului_generator", "Data faptului generator", "data", { ajutor: "Exigibilitatea = MIN(data facturii, ziua 15 a lunii următoare faptului generator) — art. 284. Dacă e aceeași cu a facturii, scrie data facturii." }),
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
    C("data", "Data", "data"), C("valoare_vamala", "Valoare vamală (RON)"),
    C("cont_destinatie", "Cont destinație", "text", { sugestie: "371" }),
    C("procent_taxa_vamala", "Taxă vamală %", "numar", {}),
    C("accize", "Accize", "numar", {}),
    C("accesorii", "Accesorii", "numar", {}),
    C("cota", "Cota TVA %", "numar", { sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }),
    DN("certificat_amanare", "Certificat de amânare a plății TVA în vamă", { ajutor: "Da: TVA în decont, 4426 = 4427 (art. 326 alin. (4)); Nu: TVA plătită în vamă." }) ] },
  { cat: "Extern", cheie: "export_ec", titlu: "Export extracomunitar (DVE)", ruta: "export-extracomunitar", frecventa: "lunar", faraPropunere: "e documentul operațiunii (factura, borderoul, declarația vamală) — nu vine din alt ecran al aplicației, se introduce la fiecare operațiune", campuri: [
    C("data", "Data", "data"), C("valoare", "Valoare"),
    C("tara_client", "Țara clientului", "text"),
    C("cont_venit", "Cont venit", "text", { sugestie: "707" }),
    DN("dovada_export", "Ai declarația vamală de export (DVE)", { ajutor: "Fără ea scutirea nu se aplică (art. 294 alin. (1) lit. a)) — se facturează cu TVA până la obținerea dovezii." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },

  { cat: "Personal și deconturi", cheie: "decont", titlu: "Decont deplasare / diurnă", ruta: "nota-decont-deplasare", frecventa: "lunar", faraPropunere: "ordinul de deplasare și documentele lui nu sunt înregistrate în aplicație", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["avans","Avans deplasare (542)"],["decont","Decont final"],["plafon","Calcul plafon neimpozabil diurnă"]] }),
    C("sursa", "Sursa", "select", { optiuni: [["casa","Casa"],["banca","Banca"]], cond: { camp: "fel", val: ["avans", "decont"] } }),
    C("diurna_pe_zi", "Diurna acordată pe zi", "numar", { cond: { camp: "fel", val: "plafon" } }),
    C("zile", "Zile de deplasare", "numar", { cond: { camp: "fel", val: "plafon" } }),
    C("salariu_baza", "Salariul de bază", "numar", { cond: { camp: "fel", val: "plafon" } }),
    C("zile_lucratoare", "Zile lucrătoare în lună", "numar", { cond: { camp: "fel", val: "plafon" } }),
    C("deplasare", "Deplasare", "select", { cond: { camp: "fel", val: "plafon" }, optiuni: [["interna","În țară (diurna bugetară 23 lei — HG 714/2018)"],["externa","În străinătate (HG 518/1995)"]] }),
    C("diurna_bugetara", "Diurna bugetară a țării (în valută)", "numar", { cond: { camp: "deplasare", val: "externa" } }),
    C("curs", "Cursul valutei", "numar", { cond: { camp: "deplasare", val: "externa" } }),
    C("suma", "Suma avans", "numar", { cond: { camp: "fel", val: "avans" } }),
    C("avans", "Avans acordat", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("diurna", "Diurnă", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("transport", "Transport", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("cazare", "Cazare", "numar", { cond: { camp: "fel", val: "decont" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "fel", val: "decont" }, sugestie: "21" }),
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
    C("mod", "Mod", "select", { optiuni: [["contract","Contract (6582=401)"],["plata","Plată directă (6582=5121)"]] }),
    C("tip_impozit", "Tip impozit", "select", { optiuni: [["profit","Impozit pe profit"],["micro","Microîntreprindere"]] }),
    C("cifra_afaceri", "Cifra de afaceri (pt credit)", "numar", {}),
    C("impozit_profit", "Impozit datorat (pt credit)", "numar", {}),
    DN("beneficiar_in_registru", "Beneficiarul e înscris în Registrul entităților/unităților de cult", { ajutor: "Nu: fără credit fiscal din impozit (art. 25 alin. (4) lit. i))." }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
  { cat: "Diverse", cheie: "subventie", titlu: "Subvenții (445/741)", ruta: "nota-subventie", frecventa: "lunar", faraPropunere: "registrul mijloacelor fixe nu ține subvenția activului (pentru reluarea lunară 4751 = 7584)", campuri: [
    C("data", "Data", "data"),
    C("fel", "Fel", "select", { optiuni: [["exploatare","Exploatare"],["investitii","Investiții (475)"],["reluare","Reluare la venituri"]] }),
    C("suma", "Suma", "numar", { cond: { camp: "fel", val: ["exploatare", "investitii"] } }),
    C("moment", "Moment", "select", { optiuni: [["drept","La dreptul de a primi"],["incasare","La încasare"]], cond: { camp: "fel", val: ["exploatare", "investitii"] } }),
    C("cont_venit", "Cont venit din subvenție", "text", { cond: { camp: "fel", val: "exploatare" }, sugestie: "741" }),
    C("valoare_activ", "Valoarea activului subvenționat", "numar", { cond: { camp: "fel", val: "reluare" } }),
    C("subventie", "Subvenția primită pentru activ", "numar", { cond: { camp: "fel", val: "reluare" } }),
    C("amortizare_lunara", "Amortizarea lunii", "numar", { cond: { camp: "fel", val: "reluare" } }),
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
    C("valoare", "Valoarea bunului", "numar", { cond: { camp: "fel", val: "comodat" } }),
    C("moment", "Moment", "select", { cond: { camp: "fel", val: "comodat" }, optiuni: [["primire","Primire"],["restituire","Restituire"]] }),
    C("chirie", "Chiria", "numar", { cond: { camp: "fel", val: ["chirie_platita", "chirie_incasata"] } }),
    C("proprietar", "Proprietar", "select", { cond: { camp: "fel", val: "chirie_platita" }, optiuni: [["pj","Persoană juridică"],["pf","Persoană fizică"]] }),
    C("total_factura", "Total factură utilități", "numar", { cond: { camp: "fel", val: "refacturare" } }),
    C("parte_refacturata", "Partea refacturată", "numar", { cond: { camp: "fel", val: "refacturare" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "fel", val: ["chirie_platita", "chirie_incasata", "refacturare"] }, sugestie: "21" }),
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
    C("operatie", "Opera\u021bie", "select", { optiuni: [["vanzare_activ","V\u00e2nzare activ la lichidare"],["partaj","Partaj către asociați"]] }),
    C("pret", "Preț vânzare", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("valoare_bruta", "Valoare brută activ", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("amortizare_cumulata", "Amortizare cumulată", "numar", { cond: { camp: "operatie", val: "vanzare_activ" } }),
    C("cont_imobilizare", "Cont imobilizare", "text", { cond: { camp: "operatie", val: "vanzare_activ" }, sugestie: "2131" }),
    C("cont_amortizare", "Cont amortizare", "text", { cond: { camp: "operatie", val: "vanzare_activ" }, sugestie: "2813" }),
    C("capital_social", "Capital social", "numar", { cond: { camp: "operatie", val: "partaj" } }),
    C("rezerve", "Rezerve", "numar", { cond: { camp: "operatie", val: "partaj" } }),
    C("profituri", "Profituri nerepartizate", "numar", { cond: { camp: "operatie", val: "partaj" } }),
    C("cota", "Cota TVA %", "numar", { cond: { camp: "operatie", val: "vanzare_activ" }, sugestie: "21" }),
    C("descriere", "Descriere", "text", { optional: true }) ] },
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

// [drepturi_rol 04.10.2026] Fiecare operațiune merge pe ruta ei (`POST /tenants/{tenant_id}/<ruta>`), deci acțiunea se
// DERIVĂ din registru, nu se scrie a doua oară. Butonul o poartă ca `data-actiune` — poarta globală (drepturi.js)
// îl scoate dacă serverul o refuză. `core/test_drepturi_ui.py` verifică: fiecare `ruta` din REGISTRU e o rută reală.
export const actiuneOp = (o) => "POST /tenants/{tenant_id}/" + o.ruta;

export async function ecranOperatiuni(corp, nav, t) {
  let opCurenta = null;

  const lista = (c) => {
    if (c) corp = c;
    nav.setInapoi(undefined);
    corp.innerHTML = `
      <h2 class="pf-titlu">Opera\u021biuni speciale</h2>
      <p class="pf-intro">Note contabile pentru opera\u021biuni punctuale. Toate intr\u0103 drept <b>ciorn\u0103</b> \u2014 se valideaz\u0103 din Registru jurnal.</p>
      ${GRUPURI.map(([frecventa, titlu, intro]) => `
        <section class="op-grup" data-frecventa="${frecventa}">
          <h3 class="pf-frand-nume">${esc(titlu)}</h3>
          <p class="ecran-nota">${esc(intro)}</p>
          ${CATEGORII.filter((cat) => REGISTRU.some((o) => o.cat === cat && o.frecventa === frecventa)).map((cat) => `
            <div class="op-categorie" style="display:block;margin-bottom:12px;background:var(--fundal);border:1px solid var(--linie);border-radius:var(--raza);padding:14px">
              <div class="pf-frand-nume" style="margin-bottom:8px">${esc(cat)}</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px">
                ${REGISTRU.filter((o) => o.cat === cat && o.frecventa === frecventa).map((o) =>
                  `<button class="buton-secundar" data-op="${o.cheie}" data-actiune="${actiuneOp(o)}">${esc(o.titlu)}</button>`).join("")}
              </div>
              ${REGISTRU.filter((o) => o.cat === cat && o.frecventa === frecventa && o.propune).map((o) =>
                `<p class="ecran-nota op-propune" data-propune="${o.cheie}"><b>${esc(o.titlu)}</b> — se propune automat: ${esc(o.propune)}</p>`).join("")}
            </div>`).join("")}
        </section>`).join("")}`;
    // [drepturi_rol 04.10.2026] Nicio operațiune permisă (asistent fără „Poate pregăti”): ecranul spune de ce e gol.
    if (!REGISTRU.some((o) => permis(actiuneOp(o)))) {
      corp.querySelectorAll(".op-grup").forEach((g) => g.remove());
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
    const camp = (c) => {
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
        const gol = c.optional ? '<option value="">-</option>'
          : `<option value="" selected>${esc(c.neales || "— alege —")}</option>`;
        input = `<select id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">${gol + c.optiuni.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select>`;
      } else if (c.tip === "mijloc_fix") {
        // [decizia Costin 07.10.2026, C4] „«ID mijloc fix» la reevaluare și casare: devine listă din registrul activelor firmei.”
        // Până azi era un câmp numeric: contabilul trebuia să știe ID-ul intern, iar refuzul îi cerea „alege-l din listă” fără listă.
        input = `<select id="op-${c.nume}" class="camp-input op-mijloc-fix" aria-label="${esc(c.eticheta)}"><option value="">— se încarcă registrul activelor… —</option></select>`;
      } else if (c.tip === "data") {
        input = `<input type="date" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}">`;
      } else if (c.tip === "numar") {
        input = `<input type="number" step="0.01" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" placeholder="${c.sugestie || ""}">`;
      } else if (CONT_PRECOMPLETAT(c)) {
        // [lotul 07.10 B, DS cap.17 corectat] un CONT vine precompletat VIZIBIL cu sugestia standard (707, 5124, 612 …): e cazul
        // uzual, se vede înainte de „Generează nota” și se schimbă; golit, câmpul obligatoriu se refuză lângă el (`eroareCamp`).
        input = `<input type="text" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" value="${esc(c.sugestie)}">`;
      } else {
        input = `<input type="text" id="op-${c.nume}" class="camp-input" aria-label="${esc(c.eticheta)}" placeholder="${c.sugestie || ""}">`;
      }
      const ajutor = c.ajutor ? `<span class="camp-ajutor">${esc(c.ajutor)}</span>` : "";
      // [lotul 12, C78.1] răspunsul VIES sub câmp: aceeași linie de stare ca la CUI-ul din „Emite factură” (`.em-cui-stare`; textul serverului cu `.pe-randuri`, DS cap.6 v2.100)
      const vies = c.vies ? `<div class="em-cui-stare" id="op-${c.nume}-vies" aria-live="polite"></div>` : "";
      return `<div class="camp"${cond}><label class="camp-eticheta" for="op-${c.nume}">${esc(c.eticheta)}${c.optional ? "" : '<span class="oblig">*</span>'}</label>${input}${ajutor}${vies}</div>`;
    };
    corp.innerHTML = `
      <h2 class="pf-titlu">${esc(opCurenta.titlu)}${_OP_AJUTOR[opCurenta.cheie] ? " " + semnAjutor(_OP_AJUTOR[opCurenta.cheie]) : ""}</h2>
      <div class="pf-frand" style="display:block">
        <div class="grila-campuri">
          ${opCurenta.campuri.map(camp).join("")}
        </div>
        ${opCurenta.multi ? `<div class="op-multi-bloc"${opCurenta.multiCond ? ` data-cond-camp="${opCurenta.multiCond.camp}" data-cond-val="${[].concat(opCurenta.multiCond.val).join("|")}"` : ""}><div class="pf-frand-nume" style="margin:12px 0 6px">${esc(opCurenta.multiTitlu || "Solduri")}</div><div id="op-multi"></div></div>` : ""}
        ${opCurenta.cheie === "asociati" ? '<div id="op-propunere"></div>' : ""}
        ${opCurenta.spreEmitere ? `<div class="caseta-info op-spre-emitere" id="op-spre-emitere" data-cond-camp="${opCurenta.spreEmitere.camp}" data-cond-val="${opCurenta.spreEmitere.val}" style="display:none"><span class="ci-mesaj">${esc(opCurenta.spreEmitere.text)}</span><p style="margin:8px 0 0"><button type="button" class="buton-secundar" id="op-spre-emitere-buton" data-actiune="POST /tenants/{tenant_id}/facturi/emite">Deschide «Emite factură»</button></p></div>` : ""}
        <div class="bara-fixa">
          <p style="margin-top:12px"><button class="buton-primar" id="op-trimite" data-genereaza-nota data-actiune="${actiuneOp(opCurenta)}">Genereaz\u0103 nota (ciorn\u0103)</button></p>
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
      const { ecranJurnal } = await import("./firme.js?v=2b27eebcaf");
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
        if (sc.tip === "select") return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><select id="m${i}-${sc.nume}" class="camp-input"><option value="" selected>— alege —</option>${sc.optiuni.map(([v,l])=>`<option value="${v}">${esc(l)}</option>`).join("")}</select></div>`;
        const t2 = sc.tip === "numar" ? "number" : "text";
        return `<div class="camp"><label class="camp-eticheta" for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label><input type="${t2}" step="0.0001" id="m${i}-${sc.nume}" class="camp-input" placeholder="${sc.sugestie||""}"></div>`;
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
    };
    const btnSpre = corp.querySelector("#op-spre-emitere-buton");
    if (btnSpre) btnSpre.addEventListener("click", async () => {   // [C84] peste formular: „←” readuce operațiunea
      const { randeazaEmitere } = await import("./emitere_ecran.js?v=8d3aa3015f");
      nav.deschide("Emite factură", (c2) => randeazaEmitere(c2, nav, t.id, { inapoi: () => nav.inapoi() }));
    });
    opCurenta.campuri.filter((c) => c.tip === "select").forEach((c) =>
      corp.querySelector(`#op-${c.nume}`).addEventListener("change", actualizeazaCond));
    actualizeazaCond();
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
          if (v && v.valid) {
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
        const val = c.tip === "numar" ? parseFloat(v) : c.tip === "mijloc_fix" ? parseInt(v, 10) : v;
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
          dupaGenerare(zona, corp.querySelector("#op-trimite"), {
            note: (citite.length ? citite : note.map(() => ({ linii: [] }))).map((n, i) => ({ linii: n.linii,
              eticheta: `${note[i] || n.eticheta || ""} — ${stareNota(r)}` })),
            detalii: [vies, nota.trim()], pas: pasNota(r, note.length > 1),
            reactiveazaLa: [...opCurenta.campuri.map((c) => corp.querySelector(`#op-${c.nume}`)),
                            ...corp.querySelectorAll("#op-multi input, #op-multi select, #op-multi textarea")] });
          if (r.avertisment) mesajIn(zona, r.avertisment, "avert");
          if (ids.length) butoaneNote(zona, ids, note, corpReq.data);   // data notei = data trimisă (toate operațiunile)
          if (zonaProp && r.asociati) arataImpartirea(r, "Nota împarte dividendul pe asociați");   // [430b] tabelul notei generate
        } else {
          zona.innerHTML = `<p class="pf-intro">Calcul (nu s-a generat nicio notă):</p><ul class="pf-intro">${Object.entries(r || {}).map(([k, v]) => `<li>${esc(k.replace(/_/g, " "))}: <b>${esc(String(v))}</b></li>`).join("")}</ul>`;
        }
      } catch (e) {
        // [410] refuzul serverului care își numește câmpurile: fiecare lângă câmpul lui; restul, în zona formularului
        const peCamp = ((e && e.erori_campuri) || []).filter((x) => eroareCamp(corp, x.camp, x.mesaj)).length;
        arataMesaj(zona, (peCamp ? "Nota nu s-a generat: " : "") + (e.mesaj || e.message || "Nu s-a putut genera nota — verifică datele introduse și reîncearcă."), "eroare");
      }
    });
  };

  lista();
}

// precompletari_rest_v1
