from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/shop/category/{self.slug}"
    
    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', default='static/default-product-image.png', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/shop/{self.slug}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
# New FAQ model
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name_plural = 'FAQS'

# New Policy model
class Policy(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField()

    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name_plural = 'Policies'

class UserBehavior(models.Model):
    class InteractionType(models.TextChoices):
        VIEW = 'view', 'Product View'
        SEARCH = 'search', 'Product Search'
        CART_ADD = 'cart_add', 'Added to Cart'
        CART_REMOVE = 'cart_remove', 'Removed from Cart'
        PURCHASE = 'purchase', 'Product Purchase'
        RATING = 'rating', 'Product Rating'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behaviors')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_behaviors')
    interaction_type = models.CharField(max_length=20, choices=InteractionType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # For storing additional data like search terms, ratings, etc.

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['product', 'timestamp']),
            models.Index(fields=['interaction_type', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_interaction_type_display()} - {self.product.name}"