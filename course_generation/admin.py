from django.contrib import admin
from .models import Course, UserKnowledge, Chapter

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'knowledge_level', 'created_at')
    list_filter = ('knowledge_level', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'user', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('name', 'content', 'course__title', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(UserKnowledge)
class UserKnowledgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'knowledge_level', 'last_updated')
    list_filter = ('knowledge_level', 'last_updated')
    search_fields = ('topic', 'user__username')
    date_hierarchy = 'last_updated'
