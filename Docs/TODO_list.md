
Zmiana unikalności username:
    np: 2 razy user Grzegorz Golonka
        grzegorz.golonka -> grzegorz.1.golonka or grzegorz.golonka1

Widok | Formularz i style:
    dla Modelów:
        Rate:    1 - 5 treshold with or without comment 
            
        Order:  
            User assigned some items to bucket
            Użytkownik możę przydzielić do koszyka wiele produktów (produkty mogą byc zmultyplikowane) x2 xD
            
        zaraz se napisze 
            x2 
        
    Reaction: 
            user może ocenić produkt tylko gdzie jest dostarczony
            może zmienić reakcje (po zastanowieniu stwierdził że mu sie nie podoba)
                komentarz jest opcjonalny ale fajnie jakby se dodał
                    może go potem zmienić

        #-----------------------------------------------------
    Dodać do projektu zgode na ciasteczka (dzwonisz do babci o przepis):
        ona ci go daje
            https://wszystkiegoslodkiego.pl/przepisy/ciasta-francuskie-i-polfrancuskie/ciastka-francuskie-z-jablkami
                to ten przepis od babci ( jej blog)
            if (rece and rece.are_clean() and piekarnik and narzyndzia ()
            {
                if (rece.are_clean() and piekarnik.is_cieply()
                {
                    Krok1
                        Zacznij od przygotowania jabłkowego nadzienia! 🍏
                        Umyte i obrane ze skórki jabłka pokrój na małą kostkę i przełóż na patelnię. Dodaj sok z cytryny, cukry oraz cynamon. Wymieszaj.
                        Na patelni pokrojone jabłka. Obok w miseczce cynamon, opakowanie cukru z wanilią oraz połówka cytryny.
                    Krok 2
                        Podprażaj jabłka przez kilka minut, aż będę miękkie i zaczną się rozpadać. Odstaw je do wystudzenia.
                        Podprażone jabłka na patelni.
                    Krok 3
                        Arkusz ciasta francuskiego podziel na 12 równych części. U mnie jeden prostokąt miał wymiary 13 x 7cm. Natnij 6 z nich, tak jak na zdjęciu.
                        Arkusz ciasta francuskiego podzielony na części.
                    Krok 4
                        Piesz 180 stopni i delektuj sie 
               }
            }
        #-----------------------------------------------------
    
Symulacja:
    User rejestruje sie -> loguje sie
        Widzi produkty 
        Może je przeglądać i przeglądać reakcje innych 
        Może dodać je do koszyka
        
        Koszyk -> KLik podsumuj zamówienie
            Adres -> za pierwszym musi dodać adres ( view do koszyka)
            Pierwszy adres zapisany jako defaultowy ( nie wyswietla sie ikonka)
            Za drugim adresem możesz przypisać jako domyślny ( do przekminienia)
                Albo domyśłny ostatni użyty adres 
            TODO dodać do model adresu date użycie danego adresu
            
        Opcja dostawy --> paczkomaty / do domu ( ale wyjebane i tak to jest symulacja ) -- MATRIX
        Sumulacja wysyłania powiadomieć odnośnie statusu przesyłki
        + zmiana danych z view informacji o zamówieniu  
            powiadomienia są widoczne tylko w aplikacji / nie smsy czy gmail 
        

        View z zakupionymi produktami
            Możliwośc kupna tego samego produktu jeśli jest dostępny (dodanie do koszyka)
    
        TODO dodac do modelu kategorii opcje podkategorii 
            -> KOlejny model podkategorie -> i do nich powinny przynależeć produkty
        
        Piszemy:
            Przejscie do produktów względem kategorii / podkategorii / {pod}x/kategorie 
            FIltracja produktów wzgledem kategorii
                MOżliwosć zobaczenia produktów sprzedających -> mnie

        TODO zmiana modelu PRoduktu żeby posiadał sprzedającego (super/usera)
        
        TODO dodać model koszyka:
            produkty oraz ich ilość
            Możliwość dodania produktów do koszyka z widoku koszyka
                Co by  się chłop mógł wincyj napatrzeć na produkty i jak mu sie spodoba to hej
            
            Jeden koszyk przypada jedemu useroowi -> nie ma wincyj cza se zapleść
        
        TODO wstpenie dodajemy model ulubione
            Użytkownik może polubic (dać reakcje) wzgledem produktu nie koniecznie zakupionego
            I dodajemy go do listy ulubionych
            Jeden produkt może pulibić wiele użytkowników
                Model ulubione ma usera i wielu produktów
            Coś ala idea że użytkownik nie chce zapisywać gdzie indzie linka z produktem
                Tylko dodaje se go do polubionych i tam może sobie je oglądać
        
        Model czatu miedzy userem a sprzedającym (superusera)
            w przypadku pytań o dany produkt
            lub w przypadku chęci zwrotu zakupionego produktu ( bijo sie )


UserPRoduct/Reaction- VIsibility - kiedys imoplemetnacja
    jak bedama robic ten algorytm

                
