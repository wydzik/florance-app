from django import forms
from django.forms import ModelForm
from .models import Florysta, Umiejetnosci, Pracownia, Realizacja, Pracownicy, Kandydat, RealizacjaPlik, KomentarzStanowiska
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.safestring import mark_safe
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



# Lista polskich województw
WOJEWODZTWA = [
    ("dolnośląskie", "Dolnośląskie"),
    ("kujawsko-pomorskie", "Kujawsko-Pomorskie"),
    ("lubelskie", "Lubelskie"),
    ("lubuskie", "Lubuskie"),
    ("łódzkie", "Łódzkie"),
    ("małopolskie", "Małopolskie"),
    ("mazowieckie", "Mazowieckie"),
    ("opolskie", "Opolskie"),
    ("podkarpackie", "Podkarpackie"),
    ("podlaskie", "Podlaskie"),
    ("pomorskie", "Pomorskie"),
    ("śląskie", "Śląskie"),
    ("świętokrzyskie", "Świętokrzyskie"),
    ("warmińsko-mazurskie", "Warmińsko-Mazurskie"),
    ("wielkopolskie", "Wielkopolskie"),
    ("zachodniopomorskie", "Zachodniopomorskie"),
]

# Kraje sąsiadujące z Polską + Polska
KRAJE = [
    ("Polska", "Polska"),
    ("Niemcy", "Niemcy"),
    ("Czechy", "Czechy"),
    ("Słowacja", "Słowacja"),
    ("Ukraina", "Ukraina"),
    ("Białoruś", "Białoruś"),
    ("Litwa", "Litwa"),
    ("Rosja", "Rosja (Obwód Kaliningradzki)"),
]


class FlorystaForm(ModelForm):
    lokalizacja_wojewodztwo = forms.ChoiceField(
        choices=WOJEWODZTWA,
        label="Województwo"
    )

    lokalizacja_kraj = forms.ChoiceField(
        choices=KRAJE,
        initial="Polska",   # domyślna wartość
        label="Kraj"
    )

    umiejetnosci = forms.MultipleChoiceField(
        choices=[
            ('czy_prawo_jazdy_b', 'Prawo jazdy kat. B'),
            ('czy_prawo_jazdy_c', 'Prawo jazdy kat. C'),
            ('czy_uklada_kwiaty', 'Umiejętność układania kwiatów'),
            ('czy_moze_dzwigac', 'Możliwość dźwigania ciężkich przedmiotów'),
            ('czy_pracuje_na_wysokosci', 'Praca na wysokości'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Umiejętności"
    )

    class Meta:
        model = Florysta
        fields = [
            'imie',
            'nazwisko',
            'lokalizacja_miasto',
            'lokalizacja_wojewodztwo',
            'lokalizacja_kraj',
            'czy_freelancuje',
            'czy_ma_auto'
        ]
        labels = {
            'imie': 'Imię',
            'nazwisko': 'Nazwisko',
            'lokalizacja_miasto': 'Miasto',
            'lokalizacja_wojewodztwo': 'Województwo',
            'lokalizacja_kraj': 'Kraj',
            'czy_freelancuje': 'Czy freelancujesz?',
            'czy_ma_auto': 'Czy masz własne auto?',
        }

    def save(self, commit=True):
        florysta = super().save(commit=False)
        if commit:
            florysta.save()
        umiejetnosci = self.cleaned_data['umiejetnosci']
        for umiejetnosc in umiejetnosci:
            Umiejetnosci.objects.create(
                florysta=florysta,
                umiejetnosc=umiejetnosc,
                wartość=True
            )
        return florysta


class PracowniaForm(forms.ModelForm):
    WOJEWODZTWA = [
        ("dolnośląskie", "Dolnośląskie"),
        ("kujawsko-pomorskie", "Kujawsko-pomorskie"),
        ("lubelskie", "Lubelskie"),
        ("lubuskie", "Lubuskie"),
        ("łódzkie", "Łódzkie"),
        ("małopolskie", "Małopolskie"),
        ("mazowieckie", "Mazowieckie"),
        ("opolskie", "Opolskie"),
        ("podkarpackie", "Podkarpackie"),
        ("podlaskie", "Podlaskie"),
        ("pomorskie", "Pomorskie"),
        ("śląskie", "Śląskie"),
        ("świętokrzyskie", "Świętokrzyskie"),
        ("warmińsko-mazurskie", "Warmińsko-mazurskie"),
        ("wielkopolskie", "Wielkopolskie"),
        ("zachodniopomorskie", "Zachodniopomorskie"),
    ]

    KRAJE = [
        ("Polska", "Polska"),
        ("Niemcy", "Niemcy"),
        ("Czechy", "Czechy"),
        ("Słowacja", "Słowacja"),
        ("Ukraina", "Ukraina"),
        ("Białoruś", "Białoruś"),
        ("Litwa", "Litwa"),
        ("Rosja", "Rosja"),
    ]

    lokalizacja_wojewodztwo = forms.ChoiceField(choices=WOJEWODZTWA, label="Województwo")
    lokalizacja_kraj = forms.ChoiceField(choices=KRAJE, initial="Polska", label="Kraj")

    class Meta:
        model = Pracownia
        fields = ["nazwa", "lokalizacja_miasto", "lokalizacja_wojewodztwo", "lokalizacja_kraj"]
        labels = {
            "nazwa": "Nazwa pracowni",
            "lokalizacja_miasto": "Miasto",
        }


class LoginForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika", max_length=150)
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)


from django.contrib.auth.models import User

class FlorystaRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Nazwa użytkownika")
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Powtórz hasło", widget=forms.PasswordInput)

    class Meta:
        model = Florysta
        fields = [
            "imie", "nazwisko", "lokalizacja_miasto",
            "lokalizacja_wojewodztwo", "lokalizacja_kraj",
            "czy_pracownia", "czy_freelancuje",
            "czy_prawo_jazdy_b", "czy_prawo_jazdy_c",
            "czy_uklada_kwiaty", "czy_moze_dzwigac",
            "czy_pracuje_na_wysokosci", "czy_ma_auto"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].help_text = mark_safe(
            "<ul class='mb-0'>" +
            "".join(f"<li>{text}</li>" for text in password_validators_help_texts()) +
            "</ul>"
        )

    def clean(self):
        cleaned = super().clean()

        password = cleaned.get("password")
        password2 = cleaned.get("password2")

        if password and password2 and password != password2:
            self.add_error("password2", "Hasła muszą się zgadzać")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error("password", e)

        if User.objects.filter(username=cleaned.get("username")).exists():
            self.add_error("username", "Taki użytkownik już istnieje")

        if User.objects.filter(email=cleaned.get("email")).exists():
            self.add_error("email", "Ten email jest już używany")

        return cleaned


class RealizacjaForm(forms.ModelForm):
    class Meta:
        model = Realizacja
        fields = ["pracownia", "nazwa_eventu", "miejsce", "data_rozpoczecia", "data_zakonczenia", "opis"]
        widgets = {
            "data_rozpoczecia": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "data_zakonczenia": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class PracownicyForm(forms.ModelForm):
    class Meta:
        model = Pracownicy
        fields = [
            "czy_wlasny_transport",
            "czy_wymagane_dzwiganie",
            "czy_wymagane_ukladanie_kwiatow",
            "czy_wymagane_prawo_jazdy",
            "data_pracy",
            "stawka",
            "stawka_dzienna_czy_godzinowa",
            "minimalny_czas_pracy",
            "szczegoly",
        ]
        labels = {
            "czy_wlasny_transport": "Własny transport wymagany",
            "czy_wymagane_dzwiganie": "Wymagane dźwiganie",
            "czy_wymagane_ukladanie_kwiatow": "Układanie kwiatów",
            "czy_wymagane_prawo_jazdy": "Prawo jazdy (B/C) – opcjonalnie",
            "data_pracy": "Dzień pracy",
            "stawka": "Stawka",
            "stawka_dzienna_czy_godzinowa": "Rodzaj stawki",
            "minimalny_czas_pracy": "Minimalny czas pracy (h)",
            "szczegoly": "Szczegóły / opis",
        }
        widgets = {
            "data_pracy": forms.DateInput(attrs={"type": "date"}),
            "szczegoly": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, realizacja=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._realizacja = realizacja  # potrzebne do walidacji zakresu dat
        # Uporządkuj wybory: pokaż pustą opcję „—” dla prawo jazdy
        self.fields["czy_wymagane_prawo_jazdy"].empty_label = "—"

        # Ustaw min/max na input date, jeśli mamy realizację
        if realizacja:
            start = realizacja.data_rozpoczecia.date()
            end = realizacja.data_zakonczenia.date()
            self.fields["data_pracy"].widget.attrs.update({
                "min": start.isoformat(),
                "max": end.isoformat(),
            })

    def clean_data_pracy(self):
        d = self.cleaned_data["data_pracy"]
        if self._realizacja and d:
            start = self._realizacja.data_rozpoczecia.date()
            end = self._realizacja.data_zakonczenia.date()
            if not (start <= d <= end):
                raise forms.ValidationError(
                    f"Data pracy musi mieścić się w zakresie realizacji: {start} – {end}."
                )
        return d


class KandydatForm(forms.ModelForm):
    class Meta:
        model = Kandydat
        fields = ["wiadomosc"]
        widgets = {
            "wiadomosc": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Napisz coś o sobie, swoim doświadczeniu itp."
            })
        }


class AssignPracownikForm(forms.Form):
    kandydat = forms.ModelChoiceField(
        queryset=Kandydat.objects.none(),
        required=False,
        label="Wybierz kandydata"
    )

    florysta = forms.ModelChoiceField(
        queryset=Florysta.objects.all(),
        required=False,
        label="Wybierz florystę z systemu"
    )

    imie = forms.CharField(required=False, label="Imię (osoba spoza systemu)")
    nazwisko = forms.CharField(required=False, label="Nazwisko")
    telefon = forms.CharField(required=False, label="Telefon")

    def __init__(self, *args, stanowisko=None, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stanowisko = stanowisko
        self.owner = owner

        if stanowisko:
            self.fields["kandydat"].queryset = Kandydat.objects.filter(
                stanowisko=stanowisko,
                status="oczekuje"
            )

    def clean(self):
        cleaned = super().clean()

        kandydat = cleaned.get("kandydat")
        florysta = cleaned.get("florysta")
        imie = cleaned.get("imie")
        nazwisko = cleaned.get("nazwisko")

        wyborow = sum([
            bool(kandydat),
            bool(florysta),
            bool(imie and nazwisko)
        ])

        if wyborow != 1:
            raise forms.ValidationError(
                "Wybierz dokładnie jedną opcję: kandydata, florystę lub wpisz dane ręcznie."
            )

        # ❌ owner nie może przypisać samego siebie
        if florysta and florysta == self.owner:
            raise forms.ValidationError(
                "Nie możesz przypisać siebie do własnej realizacji."
            )

        if kandydat and kandydat.florysta == self.owner:
            raise forms.ValidationError(
                "Nie możesz przypisać siebie do własnej realizacji."
            )

        return cleaned


class FlorystaProfileForm(forms.ModelForm):
    class Meta:
        model = Florysta
        fields = [
            "avatar",
            "imie",
            "nazwisko",
            "lokalizacja_miasto",
            "lokalizacja_wojewodztwo",

            "czy_pracownia",
            "czy_freelancuje",
            "czy_prawo_jazdy_b",
            "czy_prawo_jazdy_c",
            "czy_uklada_kwiaty",
            "czy_moze_dzwigac",
            "czy_pracuje_na_wysokosci",
            "czy_ma_auto",
        ]


# forms.py
class RealizacjaOpisForm(forms.ModelForm):
    class Meta:
        model = Realizacja
        fields = ["opis"]
        widgets = {
            "opis": forms.Textarea(attrs={"rows": 5})
        }

# forms.py
class RealizacjaPlikForm(forms.ModelForm):
    class Meta:
        model = RealizacjaPlik
        fields = ["plik", "nazwa"]


class RealizacjaEditForm(forms.ModelForm):
    class Meta:
        model = Realizacja
        fields = [
            "nazwa_eventu",
            "miejsce",
            "data_rozpoczecia",
            "data_zakonczenia",
            "opis",
        ]
        widgets = {
            "data_rozpoczecia": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "data_zakonczenia": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "opis": forms.Textarea(attrs={"rows": 4}),
        }


class KomentarzStanowiskaForm(forms.ModelForm):
    class Meta:
        model = KomentarzStanowiska
        fields = ["tresc"]
        widgets = {
            "tresc": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Dodaj komentarz wewnętrzny..."
            })
        }
