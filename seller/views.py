from django.shortcuts import render, redirect
import pandas
from .models import *
from home.models import Car,Cart
from django.views.generic.edit import CreateView
from django.contrib import messages
import pickle 
import pandas as pd
import numpy as np
from django.contrib.auth import login , logout, authenticate
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.urls import reverse

from django.http import Http404

model=pickle.load(open('LinearRegressionModel.pkl','rb'))
df=pd.read_csv('Cleaned_Car_data.csv')

# Create your views here.
def seller(request):
    return render(request, 'seller/index.html')


def loginpage(request):
    if request.method=='POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            # email = request.POST.get('email')

            user_obj = User.objects.filter(username = username)
            if not user_obj.exists():
                messages.error(request, 'User not found.')
                return redirect('/sell/login/')

            
            
            if user_obj  := authenticate(username = username, password=password):
                login(request, user_obj)
                return redirect('/sell/')

            messages.error(request, 'Wrong Password.')

            return redirect('/sell/login/')

        except Exception as e:
            messages.error(request, 'something went wrong')

            return redirect('/register/')
    return render(request, 'seller/login.html')

def registerpage(request):
    if request.method =='POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            # email = request.POST.get('email')

            user_obj = User.objects.filter(username = username)
            if user_obj.exists():
                messages.error(request, 'User already exist try to forget Password.')
                return redirect('/sell/register/')

            user_obj = User.objects.create(username = username)
            user_obj.set_password(password)
            user_obj.save()
            messages.error(request, 'Account Created Login Plz.')

            return redirect('/sell/login/')

        except Exception as e:
            messages.error(request, 'something went wrong')

            return redirect('/sell/register/')

    return render(request, 'seller/register.html')


def sell(request):
    
    companies=sorted(df['company'].unique())
    car_models=sorted(df['name'].unique())
    companies.insert(0,'Select Company')
    car_models.insert(0,'Select Company')
    return render(request, 'seller/sell.html', {'companies':companies,'car_models':car_models})

def get_car_models(request):
    selected_company = request.GET.get('company')
    filtered_models = df[df['name'].str.startswith(selected_company)]['name'].unique()
    car_models = sorted(filtered_models)
    
    return JsonResponse(car_models, safe=False)

def result(request):
    name=request.GET['name']
    company=request.GET['company']
    year=request.GET['year']
    kms_driven=request.GET['kms_driven']
    fuel_type=request.GET['fuel_type']

    result=model.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                              data=np.array([name,company,year,kms_driven,fuel_type]).reshape(1, 5)))
    result = int(result)
    print(result)

    return render(request, 'seller/result.html', {'result':result})

# def car(request):
#     return render(request, 'seller/car.html')

class CarCreateView(CreateView):
    model = Car
    template_name = "seller/car.html"
    fields = ['category', 'car_name', 'desc', 'price', 'color', 'images', 'images2', 'images3', 'images4', 'images5']

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        print(self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your additional context here
        # context['car'] = Car.objects.first()  # Example: Get the first Car object
        context['car'] = "TBC"  # Example: Get the first Car object

        return context

    def get_success_url(self):
        return reverse_lazy('dashboard') 

# def car(request):
#     if request.method =='POST':
#         category = request.POST.get('category')
#         car_name = request.POST.get('car_name')
#         desc = request.POST.get('desc')
#         price = request.POST.get('price')
#         color = request.POST.get('color')
#         images = request.FILES('images')
#         images2 = request.FILES('images2')
#         images3 = request.FILES('images3')
#         images4 = request.FILES('images4')
#         images5 = request.FILES('images5')
#         car = Car(category=category, car_name=car_name, desc=desc, price=price, color=color, images=images, images2=images2, images3=images3, images4=images4, images5=images5)
#         car.save()
#     return render(request, 'seller/car.html')




def dashboard(request):
    cars = Car.objects.filter(added_by=request.user)

    context={'cars':cars}
    return render(request, 'seller/dashboard.html', context)


def delete_car(request, car_uid):
    try:
        car = Car.objects.get(uid=car_uid)
        if car.added_by == request.user:
            car.delete()
            return redirect(reverse('dashboard'))
        else:
            raise Http404("You are not allowed to delete this car.")
    except Car.DoesNotExist:
        raise Http404("Car does not exist.")

# Legacy
def sell2(request):
    return render(request, 'seller/sell1.html')

def result2(request):
    return render(request, 'seller/result2.html')


