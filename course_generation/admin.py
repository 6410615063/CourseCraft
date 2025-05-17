from django.contrib import admin
from .models import Course, UserKnowledge, Chapter, Question, Exam, Exercise

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
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

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type')
    search_fields = ('text',)
    list_filter = ('question_type',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'is_final', 'created_at')
    list_filter = ('is_final', 'created_at', 'course')
    search_fields = ('course__title',)
    date_hierarchy = 'created_at'

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'created_at')
    list_filter = ('created_at', 'chapter')
    search_fields = ('chapter__name',)
    date_hierarchy = 'created_at'