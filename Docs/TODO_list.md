DONE:
Zmiana unikalności username:
np: 2 razy user Grzegorz Golonka
grzegorz.golonka -> grzegorz.1.golonka or grzegorz.golonka1
Wprowadzenie skyptu inicajlizującego aplikacji bash/shell
env/ activate/ makemigrations / migrate / createsuperuser / runserver
User rejestruje się
Loguje się
Widzi dodane produkty
Dodana możliwość tworzenia kategorii i do nich przydzielania podkategorii

IN PROGRESS:
Zmiana modeli:

Seed:
    Mamy takie kategorie i podkategorie:    
Kategoria: Electronics
    Podkategorie:
        - Smartphones
        - Laptops
        - Cameras
        - Smartwatches
        - Audio Devices
        - Gaming Accessories
        - Smart Home Devices
        - Wearable Tech
        - Projectors
----------------------------------------
Kategoria: Home Appliances
    Podkategorie:
        - Kitchen Appliances
        - Vacuum Cleaners
        - Air Conditioners
        - Washing Machines
        - Refrigerators
----------------------------------------
Kategoria: Gaming
    Podkategorie:
        - Consoles
        - Games
        - VR Headsets
        - Gaming Chairs
        - Game Controllers
----------------------------------------
Kategoria: Fashion
    Podkategorie:
        - Men's Fashion
        - Women's Fashion
        - Kids' Fashion
        - Footwear
        - Accessories
----------------------------------------
Kategoria: Books & Media
    Podkategorie:
        - Books
        - Movies & TV
        - Music
        - Magazines
        - Fiction
        - Non-Fiction
        - Music & Movies
    ----------------------------------------
Kategoria: Sports & Outdoors
    Podkategorie:
        - Fitness Equipment
        - Outdoor Gear
        - Bikes
        - Sportswear
        - Fishing & Hunting
        - Camping & Hiking
        - Cycling
        - Water Sports
        - Fishing Gear
        - Winter Sports
----------------------------------------
Kategoria: Beauty & Health
    Podkategorie:
        - Skincare
        - Haircare
        - Makeup
        - Perfumes
        - Health Supplements
----------------------------------------
Kategoria: Automotive
    Podkategorie:
        - Car Accessories
        - Motorbike Accessories
        - Tires
        - Car Electronics
        - Engine Oils
        - Car Electronics
        - Motorcycle Gear
        - Tools & Maintenance
----------------------------------------
Kategoria: Health & Wellness
    Podkategorie:
        - Fitness Equipment
        - Supplements
        - Personal Care
----------------------------------------
Kategoria: Hobbies & Collectibles
    Podkategorie:
        - Board Games
        - Model Kits
        - Trading Cards
        - Art Supplies
----------------------------------------
Kategoria: Baby & Kids
    Podkategorie:
        - Toys
        - Baby Gear
        - Kids' Room Décor
----------------------------------------
Kategoria: Home Improvement
    Podkategorie:
        - Power Tools
        - Gardening Tools
        - Lighting & Fixtures
        - Paint & Supplies
----------------------------------------
Kategoria: Office & Stationery
    Podkategorie:
        - Printers & Scanners
        - Office Furniture
        - Stationery
----------------------------------------
Kategoria: Pet Supplies
    Podkategorie:
        - Pet Food
        - Toys & Accessories
        - Aquariums & Supplies
----------------------------------------




    Storzenie nowych modeli:
        Backet - koszyk dla użytwkonika

    Dodanie Widoków / Formularzy / Styli(dla Krzysiaczek):


TODO:
Widok | Formularz i style:
dla Modelów:
Rate: 1 - 5 threshold with or without comment

            Order:
                User assigned some items to bucket
                Użytkownik możę przydzielić do koszyka wiele produktów
                    (produkty mogą byc zmultyplikowane) x2 xD

        Reaction:
                user może ocenić produkt tylko gdzie jest dostarczony
                może zmienić reakcje (po zastanowieniu stwierdził że mu sie nie podoba)
                    komentarz jest opcjonalny ale fajnie jakby se dodał
                        może go potem zmienić

            #-----------------------------------------------------
        Dodać do projektu zgode na ciasteczka - symulacja ciasteczek
            dla Maćka do zrobienia

    Symulacja:
        # DONE User rejestruje sie -> loguje sie
        # DONE Widzi produkty
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


            Piszemy:
                Przejscie do produktów względem kategorii / podkategorii / {pod}x/kategorie
                Fltracja produktów wzgledem kategorii
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


