Web appsas - internetinės prekybos platforma su funkcionalumais prikėjams, pardavėjams, kurjeriams.
Skirtingi vartotojai turi skirtingas teises ir skirtingus leidimus.

* Naujai užsiregistravusį vartotoją programa "by default" priskiria customers grupei - pirkėjams
* Tik appso administratorius (superuser) gali pakeisti vartotojo tipą.
* Galimi vartotojo tipai: customer, distributor, forwarder

    Anoniminis vartotojas gali matyti tam tikrus url elementus, bet nieko negali koreguoti:
        Mato prekių sąrašą
        Gali ieškoti prekių - search
        Gali matyti bazinę info kaip būtų trackinamas siuntų judėjimas prisijungusiam vartotojui
        Gali registruotis, gali prisijungti jei turi paskyrą

    Prisijungęs vartotojas gali "atnaujinti" savo paskyrą:
        Keisti slapyvardį, emailą, avatarą. Kiti laukai šiek tiek skiriasi, pvz. pardavėjas/kurjeris
            įveda įmonės registracijos kodą, pirkėjas - vardą pavardę
        Gali matyti jam priklausančių krovinių dislokaciją

    Pirkėjas turi prekių krepšelį - gali įdėti, išimti prekes, trinti krepšelį, pirkti.
        Skirtingų pardavėjų krepšeliai formuojami atskirai, nes skirtinga pardavėjų lokacija, formuojami
            atskiri mokėjimai, siuntos gali važiuoti iš skirtingų pasaulio vietų.
        Krepšelio informacijoje pasirenkus siuntų pristatymo būdus - aktyvuojasi funkcija "Checkout"
        Pasirinkus pristatymo būdą rodoma pristatymo kaina ir muito mokestis. Pagal 2022 ES reglamentą -
            muitas skaičiuojamas siuntoms, kurių vertė viršija 150 eur. Programa apskaičiuoja
            muito mokestį pagal vertę (prekių ir transporto kaina), pagal konkrečios prekės HS kodą, kilmę
        Pasirinkus "Checkout" - iš krepšelio formuojami kroviniai ir krepšelis trinamas. Taip pat suformuojami
            invoisai .xlsx  ir išsaugomi programoje.
            ## todo list:
            ## padaryti kad invoisus siųstų emailu pardavėjui + vartotojui sukūrimo momentu
            ## padaryti kad invoisų sąrašą ir bendr1 muito mokesčio sumą kurjeriui emailu siųstų išmuitinimo momentu

    Distributor turi savo prekių sąrašą.
        Gali kurti naujas prekes, redaguoti esamas prekes.
            Prekės pavadinimas, foto kaina - standartiškai bet kuriam kainininkui.
            Prekės svoris, tūris - nuo kurių standartiškai priklauso pristatymo kaina:
                https://parcelbroker.co.uk/help/what-is-volumetric-weight-volume-calculator/
            Galutinė pristatymo kaina apskaičiuojama pagal prekės vkg parametrą ir pagal pristatymo metodą:
                Pristatymo kainos logikos pvz.:
                    1 vkg pristatymo kaina iš Kanados į Šiaurės europą "economy express" metodu kainuoja 8 eur.
                Programoje numatytos pristatymo kainų logikos lentelė (contract_delivery):
                    Iš pardavėjo - iki pirkėjo regiono - vežėjas - pristatymo metodas - vkg kaina
                Numatyta kad kontrakto įrašus gali redaguoti pridėti trinti tik administratorius, nes tai yra
                    tarpinė sutartis tarp user-pardavėjo ir user-vežėjo

        Prekių trynimas apribotas, jei konkreti prekė yra kažkuriame krepšelyje.

    Forwarder turi savo krovinių sąrašą.
        Mato detalią krovinių lokaciją ir gali updeitinti krovinių lokaciją.
            ## todo list:
            ## Prekių išmuitinimo mygtukas pasirinktiems kroviniams:
                ## parodyti muito mokesčio sumą
                ## gauti invoisų sąrašą - pateikiama muitinei
            ## Pristatymas vartotojui - delete krovinio objektas


