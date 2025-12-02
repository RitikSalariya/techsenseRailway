from django.contrib import admin
from .models import Project, BlogPost, ContactMessage, Order, ProjectImage, OrderReview,Profile


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'college', 'year')
    search_fields = ('user__username', 'full_name', 'phone', 'college')

@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at')
    search_fields = ('order__id', 'order__user__username', 'comment')



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'price', 'is_active', 'is_featured', 'created_at')
    list_filter = ('category', 'level', 'is_active', 'is_featured', 'created_at')
    search_fields = ('title', 'short_description', 'description', 'tech_stack', 'slug')
    inlines = [ProjectImageInline]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'idea_description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'project__title')


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption')
