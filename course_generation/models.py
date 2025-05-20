from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.JSONField()  # Store the course content that will be used to generate chapters

    def __str__(self):
        return self.title

class Chapter(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)  # Score with 2 decimal places

    class Meta:
        ordering = ['created_at']
        # unique_together = ['course', 'name'] # make it so that 1 course can only have 1 chapter with a name?
        # 1 course need to have more than 1 chapter with the same name due to multiple users

    def __str__(self):
        return f"{self.name} - {self.course.title}"

class UserKnowledge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    knowledge_list = models.JSONField(default=list)      # List of strings: what the user knows
    unknown_list = models.JSONField(default=list)  # List of strings: what the user does not know
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user',)

    def __str__(self):
        return f"{self.user.username}"

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('EXERCISE', 'Exercise'),
        ('EXAM', 'Exam'),
    ]
    text = models.TextField()
    golden_answer = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    # Optionally, relate to Exercise or Exam via ForeignKey (nullable, set in parent)
    # These will be set from the parent side

    def __str__(self):
        return f"{self.text[:50]}..."

class Exercise(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='exercises')
    questions = models.ManyToManyField(Question, related_name='exercises')
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)  # Score with 2 decimal places

    def __str__(self):
        return f"Exercise for {self.chapter.name}"

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    questions = models.ManyToManyField(Question, related_name='exams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)  # True for final exam, False for pre-course exam
    is_done = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)  # Score with 2 decimal places

    def __str__(self):
        return f"Exam for {self.course.title} ({'Final' if self.is_final else 'Pre-course'})"