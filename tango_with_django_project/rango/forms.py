from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Вложенный класс позволяющий задавать дополнительную информацию о форме
    class Meta:
        # Создаем связь между ModelForm и моделью
        model = Category
        fields = ('name',)
class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # Если url не пустое и не начинается с 'http://', вставить перед ним 'http://'.
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data
        
    class Meta:
        # Создаем связь между ModelForm и моделью
        model = Page

        # Какие поля мы хотим включить в нашу форму?
        # На мне обязательно добавлять каждое поле, существующее в модели.
        # Некоторые поля могут иметь значения NULL, поэтому мы не захотим добавлять их...
        # Здесь мы скрываем внешний ключ.
        # Мы можем либо исключить поле category из формы,
        exclude = ('category',)
        # или определить поля, которые надо в неё добавить (т. е., не добавлять поле category)
        #fields = ('title', 'url', 'views')
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')