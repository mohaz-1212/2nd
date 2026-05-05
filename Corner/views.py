from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.views import View


class Product_ListView(ListView):
    model = Product
    template_name = "shop/home.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = Product.objects.all()
        category_id = self.request.GET.get("category")
        if category_id:
            qs = qs.filter(category__id=category_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected"] = self.request.GET.get("category", "")
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = "shop/product_form.html"
    fields = ["category", "name", "description", "price", "stock", "image_url"]
    success_url = reverse_lazy("home")


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "shop/Details.html"
    context_object_name = "details"


class Product_DeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "shop/product_confirm_delete.html"
    success_url = reverse_lazy("home")


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = "shop/product_form.html"
    fields = ["category", "name", "description", "price", "stock", "image_url"]
    success_url = reverse_lazy("home")


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "shop/address.html"
    context_object_name = "address"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = "shop/Put_address.html"
    fields = ["phone", "city", "street", "building"]
    success_url = reverse_lazy("address-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = "shop/product_form.html"
    fields = ["name"]
    success_url = reverse_lazy("home")


class CartDetailView(LoginRequiredMixin, View):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("product").all()
        total = sum(item.product.price * item.quantity for item in items)
        return render(
            request,
            "shop/cart.html",
            {
                "cart": cart,
                "items": items,
                "total": total,
            },
        )


class AddToCart(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()
            messages.success(request, f'✓ "{product.name}" added to cart')
        return redirect("home")


class RemoveFromCart(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        item.delete()
        return redirect("cart")


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "shop/detail_order.html"
    context_object_name = "detail_orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.select_related("product").all()
        total = sum(item.product.price * item.quantity for item in items)
        address = Address.objects.filter(user=request.user)
        return render(
            request,
            "shop/checkout.html",
            {
                "items": items,
                "total": total,
                "address": address,
            },
        )

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.select_related("product").all()

        if not items:
            return redirect("cart")

        address_id = request.POST.get("address_id")
        if not address_id:
            return redirect("address-create")

        address = get_object_or_404(Address, pk=address_id, user=request.user)

        # التحقق من الـ stock قبل أي حاجة
        for item in items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f'"{item.product.name}" only has {item.product.stock} units in stock.',
                )
                return redirect("cart")

        total = sum(item.product.price * item.quantity for item in items)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total=total,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()
        messages.success(request, f"Order #{order.pk} placed successfully!")
        return redirect("order-detail", pk=order.pk)


class PaymentView(LoginRequiredMixin, View):
    def post(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk, user=request.user)
        method = request.POST.get("method")

        Payment.objects.create(
            order=order,
            method=method,
            status="pending",
        )

        order.status = "confirmed"
        order.save()

        return redirect("order-detail", pk=order.pk)


class UserLogin(LoginView):
    template_name = "shop/login.html"

    def get_success_url(self):
        return reverse_lazy("home")


class UserLogout(LogoutView):
    next_page = reverse_lazy("home")


class Register(View):
    def get(self, request):
        return render(request, "shop/register.html")

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")
        if pass1 != pass2:
            return render(
                request, "shop/register.html", {"error": "password not match"}
            )
        if User.objects.filter(email=email).exists():
            return render(
                request, "shop/register.html", {"error": "Email already exists"}
            )
        User.objects.create_user(name=name, email=email, password=pass1)
        return redirect("login")
    
class RegisterAdmin(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('home')
        return render(request, "shop/register.html")

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('home')
        name = request.POST.get("name")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")
        if pass1 != pass2:
            return render(
                request, "shop/register.html", {"error": "password not match"}
            )
        if User.objects.filter(email=email).exists():
            return render(
                request, "shop/register.html", {"error": "Email already exists"}
            )
        User.objects.create_superuser(name=name, email=email, password=pass1)
        return redirect("login")


# Create your views here.
