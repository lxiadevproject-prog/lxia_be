from django.contrib import admin
from .models import Category, Tag, Article, Resource


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'author', 'views_count', 'published_at')
    list_filter = ('status', 'category', 'published_at', 'tags')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('category', 'tags', 'author')
    readonly_fields = ('views_count', 'reading_time_minutes', 'created_at', 'updated_at')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'category', 'is_featured', 'download_count', 'created_at')
    list_filter = ('resource_type', 'is_featured', 'category')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'created_at', 'updated_at')
