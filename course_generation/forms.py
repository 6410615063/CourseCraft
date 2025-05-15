from django import forms
from .models import UserKnowledge

class UserKnowledgeForm(forms.ModelForm):
    class Meta:
        model = UserKnowledge
        fields = ['topic', 'knowledge_level']
        widgets = {
            'knowledge_level': forms.Select(choices=[
                ('beginner', 'Beginner'),
                ('intermediate', 'Intermediate'),
                ('advanced', 'Advanced')
            ])
        } 