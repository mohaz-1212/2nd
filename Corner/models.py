from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name       = models.CharField(max_length=255)
    email      = models.EmailField(unique=True)
    is_active  = models.BooleanField(default=True)
    is_admin   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']
    objects = UserManager()

    def __str__(self): return self.name
    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True

    @property
    def is_staff(self): return self.is_admin


class Address(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    city     = models.CharField(max_length=100)
    street   = models.CharField(max_length=255)
    building = models.CharField(max_length=100)
    phone    = models.CharField(max_length=20)

    def __str__(self): return f"{self.city} - {self.street}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta: verbose_name_plural = "Categories"
    def __str__(self): return self.name


class Product(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    image_url   = models.ImageField(upload_to='products/' ,blank=True , null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name


class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Cart of {self.user.name}"


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta: unique_together = ('cart', 'product')
    def __str__(self): return f"{self.quantity}x {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address    = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Order #{self.id} - {self.user.name}"


class OrderItem(models.Model):
    order             = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product           = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity          = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self): return f"{self.quantity}x {self.product.name}"


class Payment(models.Model):
    METHOD_CHOICES = [('credit_card','Credit Card'),('debit_card','Debit Card'),('cash','Cash')]
    STATUS_CHOICES = [('pending','Pending'),('completed','Completed'),('failed','Failed')]

    order          = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Payment for Order #{self.order.id} - {self.status}"
