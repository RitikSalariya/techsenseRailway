from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('ml', 'Machine Learning / AI'),
        ('desktop', 'Desktop Application'),
        ('mobile', 'Mobile App'),
        ('iot', 'IoT / Hardware'),
        ('other', 'Other'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='web')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_weeks = models.PositiveIntegerField(default=4, help_text="Approx. time to complete (in weeks)")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    project_file = models.FileField(upload_to='projects/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not set
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # ensure slug is unique
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    # optional but recommended:
    slug = models.SlugField(unique=True, blank=True)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    # NEW: blog image / thumbnail
    image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title



class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    idea_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

from django.conf import settings
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.project.title}"
class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='project_images/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.project.title}"

class OrderReview(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order #{self.order.id}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    college = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=30, blank=True)  # e.g. "3rd Year", "Final Year"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"



