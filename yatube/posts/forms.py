from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text')

        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относится пост',
        }
