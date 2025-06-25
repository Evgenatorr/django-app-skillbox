from django.http import HttpResponse, HttpRequest
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
)
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import (
    UserPassesTestMixin,
)
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext as _, ngettext
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from .models import Profile
from .forms import UserForm, ProfileForm


class HelloView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        product_line = products_line.format(count=items)
        welcome_message = _("Hello World!")
        return HttpResponse(f"<h1>{welcome_message}</h1>\n<h2>{product_line}</h2>")


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class AuthIndexView(TemplateView):
    template_name = "myauth/auth-index.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self) -> bool | None:
        if self.request.user.is_staff:
            return True
        profile = self.get_object()
        if profile.user == self.request.user:
            return True

    model = Profile
    template_name_suffix = "_update_form"
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["user_form"] = UserForm(
                self.request.POST, instance=self.request.user
            )
        else:
            context["user_form"] = UserForm(instance=self.request.user)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context["user_form"]

        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()

            else:
                context.update({"user_form": user_form})
                return self.render_to_response(context)

        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("myauth:profiles_details", kwargs={"pk": self.object.pk})


class ProfileDetailsView(DetailView):
    model = Profile
    template_name = "myauth/profiles-details.html"
    context_object_name = "profile"


class ProfileListView(ListView):
    model = Profile
    template_name = "myauth/profiles-list.html"
    context_object_name = "profiles"


@user_passes_test(lambda u: u.is_superuser, login_url="myauth:about-me")
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth:view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")
