# Projekt mkg_store
Projekt ma na celu implementacje sklepu internetowego z algorytmem rekomendacji produktów na podstawie preferencji użytkownika. 

## Spis Treści
- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Modele bazodanowe](#modele-bazodanowe)
    - [User](#user)
    - [Category](#category)
    - [UserCategories](#user-categories)
    - [Product](#product)
    - [Order](#Order)
- [Technologie](#technologie)
- [Instalacja](#instalacja)
    - [Krok 1: Klonowanie repozytorium](#krok-1-klonowanie-repozytorium)
    - [Krok 2: Utworzenie wirtualnego środowiska](#krok-2-utworzenie-wirtualnego-środowiska)
    - [Krok 3: Instalacja zależności](#krok-3-instalacja-zależności)
    - [Krok 4: Migracja bazy danych](#krok-4-migracja-bazy-danych)
    - [Krok 5: Uruchomienie serwera](#krok-5-uruchomienie-serwera)
- [Użycie](#użycie)

## Opis projektu
 - Projekt mkg_store reprezentuje sklep internetowy, w którym użytkownicy bez założonego konta mają możliwość przeglądania dostępnych produktów bez możliwości zakupu. 
 - W przypadku utworzenia konta i zalogowania się użytkownik dostaje możliwość dokonania zakupu dostępnych produktów w sklepie.
 - Po dokonaniu transakcji użytkownik może podzielić się opinią z innymi użytkownikami poprzez wystawienie oceny (skala 1.0 - 5.0). 
 - To Consider 
   - Użytkownik może dodawać własne produkty i w przypadku wystawienia określonej ilości produktów (np. 15) otrzymać status sprzedawcy 

## Funkcjonalności
- **Rejestracja i logowanie użytkowników**: 
  - Użytkownicy mogą zakładać konta i logować się do systemu. Co daje im dodatkowe korzyści w formie zakupu / sprzedaży produktów.
- **Przeglądanie produktów**:
  - Użytkownicy mogą przeglądać dostępne produkty w sklepie. Po kliknięciu w produkt zostaje przedstawiony szczegółowy opis produktu.
- **Zakupy**:
  - Użytkownicy mogą dodawać produkty do koszyka i finalizować zakupy. A po transakcji wystawiać opinie dla danego produktu.
- **Zarządzanie produktami**:
  - Administratorzy mogą dodawać, edytować i usuwać produkty.
- **Koszyk**:
  - Użytkownicy mogą zobaczyć swoje wybrane produkty przed zakupem oraz dokonywać zmian w koszyku
    - Usuwanie produktu z koszyka
    - Zwiększenie/Zmniejszenie ilości produktów 
- **Finalizacja**:
  - Użytkownicy chcący zakupić produkty w koszyku muszę wypełnić:
    - Dane odbiorcy przesyłki:
      - Imię i Nazwisko kupującego
      - Adres  - 
      - Kod pocztowy
      - Numer telefonu
    - Opcje dostawy: Wybór paczkomatu lub dostawa na dany adres
   - Dane przy pierwszym zakupie zostaną uzupełnione domyślnie wartościami z danych użytkownika, lecz jest możliwa ich modyfikacja 

## Modele bazodanowe

### User
Model reprezentujący użytkowników sklepu.
  - **id**: `INTEGER` - unikalny identyfikator użytkownika.
  - **name**: `TEXT` - imie użytkownika.
  - **surname**: `TEXT` - nazwisko użytkownika.
  - **email**: `TEXT` - unikalny adres e-mail użytkownika.
  - **password**: `TEXT` - hasło użytkownika (przechowywane w formie haszowanej).
  - **birthday**: `DATE ` - data urodzenia użytkownika.
  - **registration_date**: `DATETIME ` - data zarejestrowania się użytkownika.
  - **phone_number**: `TEXT ` - unikalny numer telefonu użytkownika.
  - **is_admin**: `Boolean` - informacja, czy użytkownik jest administratorem. 
    - Domyślnie ustawiona na false, tylko inny administrator może zmiennić flage.

### Category
Model reprezentujący kategorie produktu w sklepie.
  - **id**: `INTEGER` - unikalny identyfikator kategorii produktu.
  - **name**: `STRING` - nazwa kategorii.
  - **description**: `TEXT - opis kategorii produktu.

### User Categories
Model reprezentujący relacje wiele do wielu miedzy produktami a kategoriami w sklepie.
  - **user_id**: `INTEGER` - identyfikator użytkownika.
  - **category_id**: `INTEGER` - identyfikator kategorii.

### Product
Model reprezentujący produkty w sklepie.
  - **id**: `INTEGER` - unikalny identyfikator produktu.
  - **name**: `TEXT` - nazwa produktu.
  - **image**  'TEXT' - zdjęcie produktu 
  - **description**: `TEXT` - szczegółowy opis produktu.
  - **price**: `REAL` - cena produktu.
  - **average_rate**: `REAL` - średnia arytmetyczna ocen użytkowników względem produktu.

### Rate
Model reprezentujący ocene produktu wystawioną przez użytkownika w sklepie.
  - **user_id**: `INTEGER` - identyfikator użytkownika wystawiającego ocene.
  - **product_id**: `INTEGER` -identyfikator produktu dla którego wystawiono ocene.
  - **value**: `INTEGER` - wartość oceny produktu wystawionej przez użytkownika (1.0 - 5.0).
  - **comment**: `STRING` - komentarz oceniającego względem produktu (opcjonalne).

### Order
Model reprezentujący zamówienia składane przez użytkowników.
  - **id**: `INTEGER` - unikalny identyfikator zamówienia.
  - **user_id**: `INTEGER` - identyfikator użytkownika, który złożył zamówienie.
  - **order_date**: `DATETIME` - data złożenia zamówienia.
  - **status**: `STRING` - status zamówienia ("pending", "in delivery", "delivered").

### Order Products
Model reprezentujący zamówienia składane przez użytkowników.
  - **order_id**: `INTEGER` - identyfikator zamówienia do którego produkty przynależą.
  - **product_id**: `INTEGER` - identyfikator produktu zamówionego przez użytkownika.
  - **quantity**: `INTEGER` - ilość zamówionych sztuk produktu.

### Reaction
Model reprezentujący reakcje użytkownika na produkt (like / dislike).
  - **id**: `INTEGER` - identyfikator reakcji użytkownika.
  - **product_id**: `DATETIME` - data wystawionej przez użytkownika reakcji
  - **assigned_date**: `DATETIME` - data wystawionej przez użytkownika reakcji
  - **type**: `STRING` - typ wystawianej reakcji

### User Product Visibility
Model reprezentujący widoczność produktu dla użytkownika ( jeśli dawno nie odwiedzał produktu to nie bedziemy mu polecać ).
- **id**: `INTEGER` - identyfikator reakcji użytkownika.
- **product_id**: `INTEGER` - identyfikator produktu odwiedzanego przed użytkownika
- **view_date**: `DATETIME` - data odwiedzenia produktu przez użytkownika

### User Reaction Visibility
Model reprezentujący  produktu dla użytkownika ( jeśli dawno nie odwiedzał produktu to nie bedziemy mu polecać ).
- **id**: `INTEGER` - identyfikator reakcji użytkownika.
- **reaction_id**: `INTEGER` - identyfikator reakcji wystawionej przed użytkownika
- **view_date**: `DATETIME` - data wystawionej przez użytkownika reakcji

## Technologie
  - **Backend**: Django
  - **Frontend**: HTML, CSS, JavaScript, React (probably)
  - **Baza danych**: SQLite
  - **Inne**: Git, unittest, Jenkins (probably)

## Instalacja
### Krok 1: Klonowanie repozytorium
  ```bash
  git clone https://github.com/kr1s6/EngineerProject
  cd sklep-internetowy
  ```
### Krok 2: Utworzenie wirtualnego środowiska:
  ```bash
  python -m venv env
  ```
  W zależności od systemu operacyjnego wykonujemy komende:

  - Windows  
  ```bash
   env/Scripts/activate
  ```
  - Linux:
  ```bash
    source env/bin/activate
  ```
 
### Krok 3: Instalacja zależności:
  ```bash
  pip install -r requirements.txt
  ```
### Krok 4: Migracja bazy danych:
  ```bash
  python manage.py migrate
  ```
### Krok 5: Uruchamiamy serwer:
  ```bash
python manage.py runserver
  ```

## Użycie
  - Aby uzyskać dostęp do aplikacji, otwórz przeglądarkę i przejdź do http://127.0.0.1:8000/.
  - Możesz zarejestrować nowe konto lub zalogować się na istniejące.
