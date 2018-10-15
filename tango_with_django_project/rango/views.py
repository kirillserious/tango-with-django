from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    '''
    Це комментарий?
    '''
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
        'pages': page_list}
    
    # Получаем количество посещений сайта.
    # Мы используем функцию COOKIES.get(), чтобы получить cookie с количеством посещений.
    # Если cookie существует, exists, возвращаемое значение преобразуется в целое число.
    # Если cookie не существует, по умолчанию значение преобразуется в нуль.
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if(datetime.now() - last_visit_time).seconds > 0:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    
    return render(request, 'rango/index.html', context_dict)  
def about(request):
    if request.session.get('visits'):
        visits = request.session.get('visits')
    else:
        visits = 0

    context_dict = {'emmessage': "It's about",
        'visits': visits
        }
    return render(request, 'rango/about.html', context_dict)
def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug'] = category.slug
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Все поля формы были заполнены правильно?
        if form.is_valid():
            # Сохранить новую категорию в базе данных.
            form.save(commit=True)

            # Теперь вызвать предсталвение index().
            # Пользователю будет показана главная страница.
            return index(request)
        else:
            # Обрабатываемая форма содержит ошибки - вывести их в терминал.
            print(form.errors)
    else:
        # Если запрос был не POST, вывести форму, чтобы можно было ввести в неё данные.
        form = CategoryForm()

    # Форма с ошибкой (или ошибка с данных), форма не была получена...
    # Вывести форму с сообщениями об ошибках (если они были).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # вероятно здесь лучше использовать redirect.
                return category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)

def register(request):

    # Логическое значение указывающее шаблону прошла ли регистрация успешно.
    # В начале ему присвоено значение False. Код изменяет значение на True, если регистрация прошла успешно.
    registered = False
    # Если это HTTP POST, мы заинтересованы в обработке данных формы.
    if request.method == 'POST':
        # Попытка извлечь необработанную информацию из формы.
        # Заметьте, что мы используем UserForm и UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # Если в две формы введены правильные данные...
        if user_form.is_valid() and profile_form.is_valid():
            # Сохранение данных формы с информацией о пользователе в базу данных.
            user = user_form.save()
            # Теперь мы хэшируем пароль с помощью метода set_password.
            # После хэширования мы можем обновить объект "пользователь".
            user.set_password(user.password)
            user.save()
            # Теперь разберемся с экземпляром UserProfile.
            # Поскольку мы должны сами назначить атрибут пользователя, необходимо приравнять commit=False.
            # Это отложит сохранение модели, чтобы избежать проблем целостности.
            profile = profile_form.save(commit=False)
            profile.user = user
            # Предоставил ли пользователь изображение для профиля?
            # Если да, необходимо извлечь его из формы и поместить в модель UserProfile.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            # Теперь мы сохраним экземпляр модели UserProfile.
            profile.save()

            # Обновляем нашу переменную, чтобы указать, что регистрация прошла успешно.
            registered = True
        # Неправильная формы или формы - ошибки или ещё какая-нибудь проблема?
        # Вывести проблемы в терминал.
        # Они будут также показаны пользователю.
        else:
            print(user_form.errors, profile_form.errors)
    # Не HTTP POST запрос, следователь мы выводим нашу форму, используя два экземпляра ModelForm.
    # Эти формы будут не заполненными и готовы к вводу данных от пользователя.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    # Выводим шаблон в зависимости от контекста.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text")
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')