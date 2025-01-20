# 🛒 Projekt kmg_store

Projekt ma na celu implementację sklepu internetowego z zaawansowanym algorytmem rekomendacji produktów na podstawie preferencji użytkownika.

---

## 📖 Spis Treści
- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Modele bazodanowe](#modele-bazodanowe)
  - [User](#user)
  - [Address](#address)
  - [Category](#category)
  - [Product](#product)
  - [Order](#order)
  - [Rate](#rate)
  - [Reaction](#reaction)
  - [Cart](#cart)
  - [Pozostałe modele](#pozostałe-modele)
- [Technologie](#technologie)
- [Instalacja](#instalacja)
  - [Krok 1: Klonowanie repozytorium](#krok-1-klonowanie-repozytorium)
  - [Krok 2: Utworzenie wirtualnego środowiska](#krok-2-utworzenie-wirtualnego-środowiska)
  - [Krok 3: Instalacja zależności](#krok-3-instalacja-zależności)
  - [Krok 4: Migracja bazy danych](#krok-4-migracja-bazy-danych)
  - [Krok 5: Tworzenie superużytkownika](#krok-5-tworzenie-superużytkownika)
  - [Krok 6: Uruchomienie serwera](#krok-6-uruchomienie-serwera)
- [Użycie](#użycie)

---

## 📝 Opis projektu
Projekt **kmg_store** to kompleksowy sklep internetowy, który umożliwia użytkownikom:
- Przeglądanie produktów.
- Dodawanie produktów do ulubionych i koszyka.
- Finalizowanie zamówień z wyborem metody płatności (karta, BLIK, płatność za pobraniem).
- Wystawianie ocen i opinii produktom.
- Korzystanie z rekomendacji produktów opartych na preferencjach, historii zakupów i polubieniach.

Dzięki zaawansowanemu algorytmowi rekomendacji użytkownik otrzymuje spersonalizowane propozycje produktów. System uwzględnia m.in.:
- Polubienia użytkownika.
- Zakupy i preferencje innych użytkowników.
- Historię przeglądania kategorii i produktów.

---

## 🌟 Funkcjonalności
- **Rejestracja i logowanie**:
  - Możliwość założenia konta i logowania.
  - Rejestracja wymaga podania podstawowych danych, takich jak email, numer telefonu i hasło.
- **Zarządzanie kontem użytkownika**:
  - Edycja danych osobowych.
  - Zmiana hasła i adresu e-mail.
  - Dodawanie i edycja adresów użytkownika.
- **Koszyk**:
  - Dodawanie produktów do koszyka.
  - Edycja ilości i usuwanie produktów.
  - Podgląd całkowitej wartości zamówienia.
- **Finalizacja zamówień**:
  - Wybór adresu dostawy i metody płatności.
  - Obsługa różnych metod płatności:
    - Karta kredytowa/debetowa.
    - BLIK.
    - Płatność za pobraniem.
  - Podsumowanie zamówienia z listą produktów, adresem i wybraną metodą płatności.
- **Oceny i opinie**:
  - Możliwość wystawiania ocen i opinii dla produktów.
  - Aktualizacja średniej oceny produktu w czasie rzeczywistym.
- **Rekomendacje produktów**:
  - Dynamiczne rekomendacje bazujące na historii użytkownika:
    - Polubione produkty.
    - Wyświetlone kategorie i produkty.
    - Zakupy innych użytkowników.
- **System wiadomości i rozmów**:
  - Możliwość kontaktu z administratorem w ramach zamówień lub ogólnych pytań.
  - Historia konwersacji z możliwością przeglądania starych wiadomości.
- **Zarządzanie produktami przez administratora**:
  - Dodawanie, edycja i usuwanie produktów.
  - Zarządzanie kategoriami i podkategoriami.

---

## 🗄️ Modele bazodanowe

### **User**
Reprezentuje użytkowników aplikacji:
- `email`: Unikalny adres e-mail.
- `birthday`: Data urodzenia.
- `registration_date`: Data rejestracji.
- `phone_number`: Numer telefonu.
- `gender`: Płeć użytkownika.
- `is_admin`: Flaga oznaczająca, czy użytkownik jest administratorem.

---

### **Address**
Reprezentuje adresy użytkowników:
- `user`: Użytkownik, do którego przypisany jest adres.
- `street`, `city`, `postal_code`, `country`: Szczegóły adresu.
- `is_default`: Czy jest to domyślny adres użytkownika.

---

### **Category**
Reprezentuje kategorie produktów:
- `name`: Nazwa kategorii.
- `description`: Opis kategorii.
- `parent`: Relacja hierarchiczna między kategoriami (podkategorie).

---

### **Product**
Reprezentuje produkty w sklepie:
- `name`, `brand`, `image`, `description`: Szczegóły produktu.
- `price`: Cena produktu.
- `average_rate`: Średnia ocena produktu.
- `categories`: Kategorie, do których należy produkt.
- `liked_by`: Użytkownicy, którzy dodali produkt do ulubionych.

---

### **Order**
Reprezentuje zamówienia użytkowników:
- `user`: Użytkownik składający zamówienie.
- `products`: Produkty w zamówieniu.
- `status`: Status zamówienia (np. `created`, `processing`, `completed`).
- `delivery_address`: Adres dostawy.
- `payment_method`: Metoda płatności.
- `total_amount`: Całkowita kwota zamówienia.

---

### **Rate**
Reprezentuje oceny wystawiane produktom:
- `user`: Użytkownik wystawiający ocenę.
- `product`: Produkt, który został oceniony.
- `value`: Wartość oceny (1-5).
- `comment`: Opcjonalny komentarz.

---

### **Reaction**
Reprezentuje reakcje użytkownika na produkt (polubienia i "dislajki"):
- `type`: Typ reakcji (`like`, `dislike`).
- `assigned_date`: Data wystawienia reakcji.

---

### **Cart**
Reprezentuje koszyki użytkowników:
- `user`: Użytkownik, do którego przypisany jest koszyk.
- `items`: Produkty w koszyku.

---

### **Pozostałe modele**
- **UserProductVisibility**: Widoczność produktu dla użytkownika.
- **UserQueryLog**: Historia wyszukiwań użytkownika.
- **Message** i **Conversation**: Obsługa wiadomości między użytkownikami i administratorem.
- **RecommendedProducts**: Produkty rekomendowane dla użytkownika.

---

## 🛠️ Technologie
- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript (opcjonalnie React)
- **Baza danych**: SQLite
- **Inne**: Git, unittest

---

## 🚀 Instalacja

### Krok 1: Klonowanie repozytorium
```bash
git clone https://github.com/kr1s6/EngineerProject
cd EngineerProject/

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
  python manage.py makemigrations
  python manage.py migrate
  ```
### Krok 5: Tworzenie superużytkownika:
  (opcjonalne)
  ```bash
python manage.py createsuperuser
  ```
### Krok 6: Uruchomienie serwera:
  ```bash
python manage.py runserver
```

## Użycie
  - Aby uzyskać dostęp do aplikacji, otwórz przeglądarkę i przejdź do http://127.0.0.1:8000/.
  - Możesz zarejestrować nowe konto lub zalogować się na istniejące.
