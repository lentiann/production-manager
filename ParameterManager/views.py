from django.shortcuts import redirect
from .forms import NodeForm
from django.views.generic import View
from django.contrib.auth import views as auth_views, authenticate, login
from .get_from_db import *
from .update_db import *
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required, user_passes_test



class UserFormView(View):
    form_class = RegisterForm
    template_name = 'registration/registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('show-database')

        return render(request, self.template_name, {'form': form})


# @user_passes_test(lambda u: u.is_superuser)
def show_database(request):
    dbs = Database.objects.all()
    for db in dbs:
        if db.pk == 1:
            db.active = True
        else:
            db.active = False
    dbs = [(db.db_name, db.id, db.active) for db in dbs]
    # dbs = [('database 1', 1), ('database 2', 2)]
    return render(request, 'show_databases.html', {'dbs': dbs, 'db_num': len(dbs)})


def login(request):
    return render(request,'login.html')


# @login_required()
def show_dashboard(request):
    return render(request,'dashboard.html')


class OptimalFormView(View):
    form_class = NodeForm
    template_name = 'set-optimal-values.html'

    def get(self, request):
        important_nodes = Node.objects.filter(important=True)
        parameters = []
        for node in important_nodes:
            if node.value_set.all():
                parameters.append(node)
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form, 'parameters': parameters})

    def post(self, request):
        parameter = request.POST['parameter']
        str_optimal = request.POST['str_optimal']
        high = request.POST['highest_optimal']
        low = request.POST['lowest_optimal']
        limits_dict = {parameter: {'str_optimal': str_optimal, 'highest_optimal': high, 'lowest_optimal': low}}
        for key, value in limits_dict.items():
            for k in value:
                try:
                    parameter_value = Node.objects.get(name=str(key))
                    var = str(k)
                    if var == "lowest_optimal":
                        parameter_value.lowest_optimal = str(value[k])
                        parameter_value.save()
                    elif var == "highest_optimal":
                        parameter_value.highest_optimal = str(value[k])
                        parameter_value.save()
                    elif var == "str_optimal":
                        parameter_value.str_optimal = str(value[k])
                        parameter_value.save()
                except:
                    pass

        return redirect('set-optimal-values')