from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FlorystaForm, PracowniaForm, LoginForm, FlorystaRegistrationForm, RealizacjaForm, PracownicyForm,\
                    KandydatForm, AssignPracownikForm, FlorystaProfileForm, RealizacjaOpisForm, RealizacjaPlikForm,\
                    RealizacjaEditForm, KomentarzStanowiskaForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Florysta, Pracownia, Realizacja, Pracownicy, Kandydat, StatusKandydata, StatusPrzypisania, \
                    RealizacjaPlik, Powiadomienie
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from datetime import time
from django.utils import timezone
from django.utils.formats import date_format
from collections import defaultdict
from .utils.notifications import notify_user


def notify(user, tresc, link=None):
    Powiadomienie.objects.create(
        user=user,
        tresc=tresc,
        link=link
    )


from django.contrib.auth.models import User
from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        form = FlorystaRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # 1️⃣ Tworzymy Usera
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )

            # 2️⃣ Tworzymy Florystę
            florysta = form.save(commit=False)
            florysta.user = user
            florysta.save()

            login(request, user)
            return redirect("dashboard")
    else:
        form = FlorystaRegistrationForm()

    return render(request, "register_florysta.html", {"form": form})


def index(request):
    if request.user.is_authenticated:
        florysta = Florysta.objects.get(user=request.user)
        pracownie_usera = florysta.pracownie.all()

        # filtrowanie po pracowni
        pracownia_id = request.GET.get("pracownia")
        if pracownia_id:
            realizacje = Realizacja.objects.filter(pracownia_id=pracownia_id)
        else:
            realizacje = Realizacja.objects.filter(pracownia__in=pracownie_usera)
    else:
        realizacje = None
        pracownie_usera = None
        pracownia_id = None

    context = {
        "realizacje": realizacje,
        "pracownie": pracownie_usera,
        "selected_pracownia": pracownia_id
    }
    return render(request, "index.html", context)


@login_required
def create_pracownia(request):
    if request.method == "POST":
        form = PracowniaForm(request.POST)
        if form.is_valid():
            pracownia = form.save(commit=False)
            florysta = Florysta.objects.get(user=request.user)  # pobieramy florystę zalogowanego usera
            pracownia.owner = florysta
            pracownia.save()
            return redirect("index")
    else:
        form = PracowniaForm()
    return render(request, "create_pracownia.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")  # 👈 po zalogowaniu wraca na stronę główną
            else:
                form.add_error(None, "Nieprawidłowa nazwa użytkownika lub hasło")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def create_realizacja(request):
    florysta = Florysta.objects.get(user=request.user)
    # dostępne tylko pracownie należące do zalogowanego florysty
    pracownie_usera = florysta.pracownie.all()

    if request.method == "POST":
        form = RealizacjaForm(request.POST)
        form.fields["pracownia"].queryset = pracownie_usera  # ograniczamy wybór do pracowni właściciela
        if form.is_valid():
            realizacja = form.save()
            return redirect("index")
    else:
        form = RealizacjaForm()
        form.fields["pracownia"].queryset = pracownie_usera  # to samo dla GET

    return render(request, "create_realizacja.html", {"form": form})


@login_required
def realizacje_dashboard(request):
    florysta = Florysta.objects.get(user=request.user)
    pracownie_usera = florysta.pracownie.all()

    # opcjonalnie: filtrowanie po wybranej pracowni
    pracownia_id = request.GET.get("pracownia")
    if pracownia_id:
        realizacje = Realizacja.objects.filter(pracownia_id=pracownia_id)
    else:
        realizacje = Realizacja.objects.filter(pracownia__in=pracownie_usera)

    context = {
        "pracownie": pracownie_usera,
        "realizacje": realizacje,
        "selected_pracownia": pracownia_id
    }
    return render(request, "realizacje_dashboard.html", context)


@login_required
def edit_realizacja(request, pk):
    realizacja = get_object_or_404(Realizacja, pk=pk, pracownia__owner__user=request.user)
    if request.method == "POST":
        form = RealizacjaForm(request.POST, instance=realizacja)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = RealizacjaForm(instance=realizacja)
    return render(request, "create_realizacja.html", {"form": form})


@login_required
def delete_realizacja(request, pk):
    realizacja = get_object_or_404(Realizacja, pk=pk, pracownia__owner__user=request.user)
    if request.method == "POST":
        realizacja.delete()
        return redirect("index")
    return render(request, "confirm_delete.html", {"realizacja": realizacja})


@login_required
def edit_pracownia(request, pk):
    pracownia = get_object_or_404(
        Pracownia,
        id=pk,
        owner=request.user.florysta
    )

    realizacje = Realizacja.objects.filter(
        pracownia=pracownia
    ).order_by("-data_rozpoczecia")

    if request.method == "POST":
        form = PracowniaForm(request.POST, instance=pracownia)
        if form.is_valid():
            form.save()
            return redirect("edit_pracownia", pk=pracownia.id)
    else:
        form = PracowniaForm(instance=pracownia)

    return render(request, "edit_pracownia.html", {
        "form": form,
        "pracownia": pracownia,
        "realizacje": realizacje,
    })


@login_required
def realizacja_detail(request, pk):
    realizacja = get_object_or_404(
        Realizacja.objects.select_related(
            "pracownia",
            "pracownia__owner"
        ),
        pk=pk
    )
    florysta = get_object_or_404(Florysta, user=request.user)
    is_owner = realizacja.pracownia.owner == florysta

    stanowiska = []
    for s in realizacja.pracownicy_set.all():
        s.already_applied = s.kandydaci.filter(florysta=florysta).exists()
        stanowiska.append(s)

    is_assigned = Pracownicy.objects.filter(
        realizacja=realizacja,
        przypisany_florysta=request.user.florysta,
        status_przypisania="zaakceptowane"
    ).exists()

    can_view_files = is_owner or is_assigned

    return render(
        request,
        "realizacja_detail.html",
        {
            "realizacja": realizacja,
            "is_owner": is_owner,
            "stanowiska": stanowiska,
            "can_view_files": can_view_files,
        }
    )


@login_required
def create_pracownicy(request, realizacja_id):
    realizacja = get_object_or_404(
        Realizacja,
        id=realizacja_id,
        pracownia__owner__user=request.user
    )
    if request.method == "POST":
        form = PracownicyForm(request.POST, realizacja=realizacja)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.realizacja = realizacja
            obj.save()
            return redirect("realizacja_detail", realizacja_id=realizacja.id)
    else:
        form = PracownicyForm(realizacja=realizacja)

    return render(request, "create_pracownicy.html", {
        "form": form,
        "realizacja": realizacja
    })


@login_required
def edit_pracownicy(request, realizacja_id, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=realizacja_id,
        pracownia__owner__user=request.user
    )
    stanowisko = get_object_or_404(Pracownicy, id=pk, realizacja=realizacja)

    if request.method == "POST":
        form = PracownicyForm(request.POST, instance=stanowisko, realizacja=realizacja)
        if form.is_valid():
            form.save()
            return redirect("realizacja_detail", realizacja_id=realizacja.id)
    else:
        form = PracownicyForm(instance=stanowisko, realizacja=realizacja)

    return render(request, "edit_pracownicy.html", {
        "form": form,
        "realizacja": realizacja,
        "stanowisko": stanowisko
    })


@login_required
def delete_pracownicy(request, realizacja_id, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=realizacja_id,
        pracownia__owner__user=request.user
    )
    stanowisko = get_object_or_404(Pracownicy, id=pk, realizacja=realizacja)

    if request.method == "POST":
        stanowisko.delete()
        return redirect("realizacja_detail", realizacja_id=realizacja.id)

    return render(request, "delete_pracownicy.html", {
        "realizacja": realizacja,
        "stanowisko": stanowisko
    })


@login_required
def znajdz_zlecenie(request):
    realizacje = Realizacja.objects.select_related(
        "pracownia",
        "pracownia__owner"
    ).annotate(
        ma_stanowiska=Exists(
            Pracownicy.objects.filter(realizacja=OuterRef('pk'))
        )
    ).filter(ma_stanowiska=True)

    return render(request, "znajdz_zlecenie.html", {"realizacje": realizacje})


@login_required
def apply_stanowisko(request, stanowisko_id):
    stanowisko = get_object_or_404(Pracownicy, pk=stanowisko_id)
    florysta = get_object_or_404(Florysta, user=request.user)

    if stanowisko.is_filled:
        messages.error(request, "To stanowisko jest już obsadzone.")
        return redirect("realizacja_detail", stanowisko.realizacja.id)

    # ❌ owner nie może aplikować do własnej realizacji
    if stanowisko.realizacja.pracownia.owner == florysta:
        messages.error(request, "Nie możesz aplikować do własnej realizacji.")
        return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)

    # blokada jeśli stanowisko już obsadzone
    if stanowisko.kandydaci.filter(status=StatusKandydata.WYBRANY).exists():
        messages.error(request, "To stanowisko jest już obsadzone.")
        return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)

    # ❌ blokada ponownej aplikacji
    if Kandydat.objects.filter(stanowisko=stanowisko, florysta=florysta).exists():
        messages.warning(request, "Już aplikowałeś na to stanowisko.")
        return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)

    if request.method == "POST":
        form = KandydatForm(request.POST)
        if form.is_valid():
            kandydat = form.save(commit=False)
            kandydat.stanowisko = stanowisko
            kandydat.florysta = florysta
            kandydat.save()
            messages.success(request, "Twoja aplikacja została wysłana!")
            realizacja = stanowisko.realizacja

            notify_user(
                user=realizacja.pracownia.owner.user,
                tresc=f"Nowa aplikacja do realizacji: {realizacja.nazwa_eventu}",
                link=reverse("realizacja_detail", args=[realizacja.id]),
            )

            return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)
    else:
        form = KandydatForm()

    return render(request, "apply_stanowisko.html", {"form": form, "stanowisko": stanowisko})


@login_required
def lista_kandydatow(request, pk):
    realizacja = get_object_or_404(Realizacja, pk=pk)

    # tylko właściciel pracowni ma dostęp
    if realizacja.pracownia.owner.user != request.user:
        messages.error(request, "Nie masz dostępu do listy kandydatów.")
        return redirect("realizacja_detail", pk=pk)

    # pobieramy wszystkich kandydatów przypisanych do stanowisk tej realizacji
    kandydaci = Kandydat.objects.filter(stanowisko__realizacja=realizacja).select_related("florysta", "stanowisko")

    if request.method == "POST":
        kandydat_id = request.POST.get("kandydat_id")
        kandydat = get_object_or_404(
            Kandydat,
            id=kandydat_id,
            stanowisko__realizacja=realizacja
        )

        stanowisko = kandydat.stanowisko  # 👈 TO BYŁO BRAKUJĄCE
        with transaction.atomic():
            # przypisanie florysty do stanowiska
            stanowisko.przypisany_florysta = kandydat.florysta
            stanowisko.save()

            # oznacz wybranego

            kandydat.status = StatusKandydata.WYBRANY
            kandydat.save()

        # odrzuć pozostałych kandydatów na to samo stanowisko
        Kandydat.objects.filter(
            stanowisko=kandydat.stanowisko
        ).exclude(id=kandydat.id).update(
            status=StatusKandydata.ODRZUCONY
        )

        messages.success(
            request,
            f"{kandydat.florysta.user.username} został wybrany. Pozostali kandydaci odrzuceni."
        )
        return redirect("lista_kandydatow", pk=pk)

    return render(request, "lista_kandydatow.html", {"realizacja": realizacja, "kandydaci": kandydaci})


@login_required
def moje_aplikacje(request):
    florysta = Florysta.objects.get(user=request.user)

    aplikacje = Kandydat.objects.filter(
        florysta=florysta
    ).select_related(
        "stanowisko",
        "stanowisko__realizacja",
        "stanowisko__realizacja__pracownia"
    ).order_by("-id")

    return render(
        request,
        "moje_aplikacje.html",
        {"aplikacje": aplikacje}
    )


@login_required
def edit_stanowisko(request, pk):
    stanowisko = get_object_or_404(Pracownicy, pk=pk)
    florysta = Florysta.objects.get(user=request.user)

    # 🔒 tylko owner realizacji
    if stanowisko.realizacja.pracownia.owner != florysta:
        messages.error(request, "Nie masz dostępu do edycji tego stanowiska.")
        return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)

    if request.method == "POST":
        form = PracownicyForm(
            request.POST,
            instance=stanowisko,
            realizacja=stanowisko.realizacja
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Stanowisko zostało zaktualizowane.")
            return redirect("realizacja_detail", pk=stanowisko.realizacja.pk)
    else:
        form = PracownicyForm(
            instance=stanowisko,
            realizacja=stanowisko.realizacja
        )

    return render(
        request,
        "edit_stanowisko.html",
        {
            "form": form,
            "stanowisko": stanowisko,
        }
    )


@login_required
def assign_pracownik(request, realizacja_id, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=realizacja_id,
        pracownia__owner__user=request.user
    )
    stanowisko = get_object_or_404(Pracownicy, id=pk, realizacja=realizacja)

    owner = realizacja.pracownia.owner

    if request.method == "POST":
        form = AssignPracownikForm(
            request.POST,
            stanowisko=stanowisko,
            owner=owner
        )
        if form.is_valid():
            with transaction.atomic():

                # 🔄 wyczyść stare przypisanie
                stanowisko.przypisany_florysta = None
                stanowisko.przypisane_imie = None
                stanowisko.przypisane_nazwisko = None
                stanowisko.przypisany_telefon = None
                stanowisko.status_przypisania = StatusPrzypisania.OCZEKUJE

                kandydat = form.cleaned_data.get("kandydat")
                florysta = form.cleaned_data.get("florysta")

                if kandydat:
                    stanowisko.przypisany_florysta = kandydat.florysta
                    stanowisko.status_przypisania = StatusPrzypisania.OCZEKUJE
                    kandydat.status = "wybrany"
                    kandydat.save()

                    notify(
                        kandydat.florysta.user,
                        f"Twoja aplikacja do realizacji '{stanowisko.realizacja.nazwa_eventu}' została zaakceptowana",
                        link=reverse("dashboard")
                    )


                elif florysta:
                    stanowisko.przypisany_florysta = florysta
                    stanowisko.status_przypisania = StatusPrzypisania.OCZEKUJE

                    notify(florysta.user,
                           f"Zostałeś zaproszony do realizacji: {stanowisko.realizacja.nazwa_eventu}",
                           link=reverse("dashboard")
                           )

                    notify_user(
                        user=florysta.user,
                        tresc=f"Zostałeś zaproszony do realizacji: {realizacja.nazwa_eventu}",
                        link=reverse("dashboard"),
                    )



                else:
                    stanowisko.przypisane_imie = form.cleaned_data["imie"]
                    stanowisko.przypisane_nazwisko = form.cleaned_data["nazwisko"]
                    stanowisko.przypisany_telefon = form.cleaned_data.get("telefon")

                    # osoba spoza systemu = od razu zaakceptowana
                    stanowisko.status_przypisania = StatusPrzypisania.ZAAKCEPTOWANE

                stanowisko.save()

            return redirect("realizacja_detail", realizacja.id)


    else:
        form = AssignPracownikForm(
            stanowisko=stanowisko,
            owner=owner
        )


    return render(request, "assign_pracownik.html", {
        "form": form,
        "stanowisko": stanowisko,
        "realizacja": realizacja
    })


@login_required
def florysta_detail(request, florysta_id):
    florysta = get_object_or_404(Florysta, id=florysta_id)

    return render(request, "florysta_detail.html", {
        "florysta": florysta
    })


@login_required
def twoje_zaproszenia(request):
    florysta = request.user.florysta

    zaproszenia = Pracownicy.objects.filter(
        przypisany_florysta=florysta,
        status_przypisania=StatusPrzypisania.OCZEKUJE
    ).select_related("realizacja", "realizacja__pracownia")

    return render(request, "twoje_zaproszenia.html", {
        "zaproszenia": zaproszenia
    })


@login_required
def odpowiedz_na_zaproszenie(request, stanowisko_id):
    stanowisko = get_object_or_404(
        Pracownicy,
        id=stanowisko_id,
        przypisany_florysta=request.user.florysta,
        status_przypisania=StatusPrzypisania.OCZEKUJE
    )

    if request.method == "POST":
        decyzja = request.POST.get("decyzja")

        if decyzja == "accept":
            stanowisko.status_przypisania = StatusPrzypisania.ZAAKCEPTOWANE
            realizacja = stanowisko.realizacja
            stanowisko.save()

            notify_user(
                user=realizacja.pracownia.owner.user,
                tresc=f"{request.user.florysta.imie} zaakceptował zaproszenie do realizacji {realizacja.nazwa_eventu}",
                link=reverse("realizacja_detail", args=[realizacja.id]),
            )

        elif decyzja == "reject":
            stanowisko.przypisany_florysta = None
            stanowisko.status_przypisania = StatusPrzypisania.ODRZUCONE
            stanowisko.save()

    return redirect("twoje_zaproszenia")


def group_by_month(events):
    grouped = defaultdict(list)

    for e in events:
        date = e["date"]
        if timezone.is_aware(date):
            date = timezone.localtime(date)

        key = date.strftime("%Y-%m")
        grouped[key].append(e)

    months = []
    for _, items in grouped.items():
        first_date = items[0]["date"]
        if timezone.is_aware(first_date):
            first_date = timezone.localtime(first_date)

        months.append({
            "label": date_format(first_date, "F Y").capitalize(),
            "events": items,
        })

    return months



@login_required
def dashboard(request):
    florysta = request.user.florysta
    events = []

    # 1️⃣ Realizacje ownera
    for r in Realizacja.objects.filter(pracownia__owner=florysta):
        events.append({
            "type": "owner",
            "date": r.data_rozpoczecia,
            "realizacja": r,
            "realizacja_url": reverse("realizacja_detail", args=[r.id]),
            "opis": r.opis,
        })

    # 2️⃣ Zaproszenia / przypisania
    for s in Pracownicy.objects.filter(
            przypisany_florysta=florysta
    ):
        r = s.realizacja

        events.append({
            "type": "invite",
            "date": r.data_rozpoczecia,
            "realizacja": r,
            "realizacja_url": reverse("realizacja_detail", args=[r.id]),
            "opis": s.szczegoly,
            "stanowisko": s,
            "status": s.status_przypisania,
        })

    # 3️⃣ Aplikacje
    for k in Kandydat.objects.filter(florysta=florysta):
        r = k.stanowisko.realizacja

        events.append({
            "type": "application",
            "date": r.data_rozpoczecia,
            "realizacja": r,
            "realizacja_url": reverse("realizacja_detail", args=[r.id]),
            "opis": k.stanowisko.szczegoly,
            "stanowisko": k.stanowisko,
            "status": k.status,
            "kandydatura_id": k.id,
        })

    # 🔥 SORTOWANIE – NAJWAŻNIEJSZE
    now = timezone.now()

    upcoming = []
    archive = []

    for e in events:
        date = e["date"]
        if timezone.is_aware(date):
            date = timezone.localtime(date)

        if date >= now:
            upcoming.append(e)
        else:
            archive.append(e)

    grouped_events = defaultdict(list)

    for e in events:
        # ujednolicamy datetime (na wypadek timezone)
        date = e["date"]
        if timezone.is_aware(date):
            date = timezone.localtime(date)

        month_key = date.strftime("%Y-%m")  # np. "2025-03"
        grouped_events[month_key].append(e)

    months = []

    for month_key, items in grouped_events.items():
        first_date = items[0]["date"]
        if timezone.is_aware(first_date):
            first_date = timezone.localtime(first_date)

        months.append({
            "label": date_format(first_date, "F Y"),  # np. "marzec 2025"
            "events": items,
        })

    upcoming.sort(key=lambda e: e["date"])
    archive.sort(key=lambda e: e["date"], reverse=True)

    context = {
        "upcoming_months": group_by_month(upcoming),
        "archive_months": group_by_month(archive),
    }

    return render(request, "dashboard.html", context)

    return render(request, "dashboard.html", {
        "months": months
    })


@login_required
def withdraw_application(request, pk):
    kandydatura = get_object_or_404(
        Kandydat,
        pk=pk,
        florysta=request.user.florysta,
        status="oczekuje"
    )

    stanowisko = kandydatura.stanowisko
    kandydatura.delete()

    return redirect("dashboard")


@login_required
def accept_invite(request, pk):
    stanowisko = get_object_or_404(
        Pracownicy,
        pk=pk,
        przypisany_florysta=request.user.florysta,
        status_przypisania="oczekuje"
    )

    stanowisko.status_przypisania = "zaakceptowane"
    stanowisko.save()

    return redirect("dashboard")


@login_required
def reject_invite(request, pk):
    stanowisko = get_object_or_404(
        Pracownicy,
        pk=pk,
        przypisany_florysta=request.user.florysta,
        status_przypisania="oczekuje"
    )

    # czyścimy przypisanie
    stanowisko.przypisany_florysta = None
    stanowisko.status_przypisania = None
    stanowisko.save()

    return redirect("dashboard")


@login_required
def edit_profile(request):
    florysta = request.user.florysta

    if request.method == "POST":
        form = FlorystaProfileForm(
            request.POST,
            request.FILES,
            instance=florysta
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profil został zaktualizowany.")
            return redirect("dashboard")
    else:
        form = FlorystaProfileForm(instance=florysta)

    return render(request, "profile_edit.html", {
        "form": form
    })


@login_required
def edit_realizacja_opis(request, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=pk,
        pracownia__owner=request.user.florysta
    )

    if request.method == "POST":
        form = RealizacjaOpisForm(request.POST, instance=realizacja)
        if form.is_valid():
            form.save()
            return redirect("realizacja_detail", realizacja.id)
    else:
        form = RealizacjaOpisForm(instance=realizacja)

    return render(request, "edit_realizacja_opis.html", {
        "form": form,
        "realizacja": realizacja
    })


@login_required
def add_realizacja_plik(request, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=pk,
        pracownia__owner=request.user.florysta
    )

    if request.method == "POST":
        form = RealizacjaPlikForm(request.POST, request.FILES)
        if form.is_valid():
            plik = form.save(commit=False)
            plik.realizacja = realizacja
            plik.save()
            return redirect("realizacja_detail", realizacja.id)
    else:
        form = RealizacjaPlikForm()

    return render(request, "add_realizacja_plik.html", {
        "form": form,
        "realizacja": realizacja
    })


@login_required
def edit_realizacja(request, pk):
    realizacja = get_object_or_404(
        Realizacja,
        id=pk,
        pracownia__owner__user=request.user
    )

    if request.method == "POST":
        form = RealizacjaEditForm(request.POST, instance=realizacja)
        if form.is_valid():
            form.save()
            return redirect("realizacja_detail", realizacja.id)
    else:
        form = RealizacjaEditForm(instance=realizacja)

    return render(request, "edit_realizacja.html", {
        "form": form,
        "realizacja": realizacja,
    })


@login_required
def delete_realizacja_plik(request, pk):
    plik = get_object_or_404(
        RealizacjaPlik,
        id=pk,
        realizacja__pracownia__owner__user=request.user
    )

    realizacja_id = plik.realizacja.id

    if request.method == "POST":
        plik.plik.delete(save=False)  # usuń fizyczny plik
        plik.delete()
        return redirect("realizacja_detail", realizacja_id)


@login_required
def edit_realizacja_notatki(request, realizacja_id):
    realizacja = get_object_or_404(
        Realizacja,
        id=realizacja_id,
        pracownia__owner__user=request.user
    )

    if request.method == "POST":
        realizacja.notatki_prywatne = request.POST.get("notatki_prywatne", "")
        realizacja.save()
        return redirect("realizacja_detail", realizacja.id)


@login_required
def add_komentarz_stanowiska(request, stanowisko_id):
    stanowisko = get_object_or_404(
        Pracownicy,
        id=stanowisko_id,
        realizacja__pracownia__owner__user=request.user
    )

    if request.method == "POST":
        form = KomentarzStanowiskaForm(request.POST)
        if form.is_valid():
            komentarz = form.save(commit=False)
            komentarz.stanowisko = stanowisko
            komentarz.autor = request.user.florysta
            komentarz.save()

    return redirect("realizacja_detail", stanowisko.realizacja.id)


@login_required
def mark_notification_read(request, pk):
    p = get_object_or_404(
        Powiadomienie,
        pk=pk,
        user=request.user
    )
    p.is_read = True
    p.save()
    return redirect(p.link or "dashboard")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Konto zostało usunięte.")
        return redirect("index")

    return render(request, "delete_account.html")

