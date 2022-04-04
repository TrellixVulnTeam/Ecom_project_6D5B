from genericpath import exists
from http.client import responses
from itertools import product
from urllib import response
from django import views
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from .models import *
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.hashers import make_password,check_password
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse_lazy
import datetime
from django.db.models import Q
from django.core import serializers
from django.contrib.contenttypes.models import ContentType


class HomeView(View):
     def get(self,request):
          print(type(ContentType.objects.get_for_model(Category)),"78923475892749238472389472389472394273498")
          return render(request,'app/index.html',{"products":Product.objects.filter(is_active=True)})

class MyAccountView(View):
     def get(self,request):
          return render(request,'app/my-account.html')

class MySellerAccountView(View):
     def get(self,request):
          try:
               if request.session['seller_email']:
                    return render(request,'app/seller-account.html')
          except:
               return redirect('HomeView')

class ProductListPage(View):
     def get(self,request):
          try:
               products = Product.objects.filter(is_active=True,seller__email=request.session['seller_email']).order_by('date_created')
               paginator = Paginator(products, 1)
               page_number = request.GET.get('page')
               page_object = paginator.get_page(page_number)
               categories=Category.objects.all()
               return render(request,'app/product-list.html',{"page_object":page_object,"categories":categories})
          except:
               return redirect('HomeView')
     
class AllProductList(ListView):
     model=Product
     

class ProductView(DetailView):
    model = Product
    template_name = 'app/product-details.html'
    context_object_name = 'product_page'
    pk_url_kwarg = 'product'


class RemoveProductPage(View):
     def get(self,request,product):
          get_product=Product.objects.filter(id=product).first()
          if get_product:
               get_product.is_active=False
               get_product.save()
               return redirect('ProductListPage')

class DeleteProductPage(DeleteView):
    model = Product
    pk_url_kwarg ='pk'
    success_url = '/product-list/'
    
class RegisterView(View):

     def get(self,request):
          if 'email' in request.session:
               return redirect('HomeView')
          else:
               return render(request,'app/register.html')

     def post(self, request):
          user_name = request.POST.get('username')
          email = request.POST.get('email')
          password = request.POST.get('password')
          bool = request.POST.get('check1')
          if bool != 'on':
               try:
                    user_create=Customers(email=email,username=user_name,password=make_password(password))
                    user_create.save()
                    print("bang***************************")
                    return redirect('LoginView')
               except:
                    messages.warning(request, f'User {email} is already exists please take another email-id')
                    print("boom***************************")
                    return redirect('RegisterView')
          else:
               try:
                    seller_create=Sellers(email=email,username=user_name,password=make_password(password))
                    seller_create.save()
                    return redirect('SellerLoginView')
               except:
                    messages.warning(request, f'Seller {email} is already exists please take another email-id')
                    return redirect('RegisterView')

class UserLoginView(View):
     def get(self,request):
          if 'user_email' in request.session:
               return redirect('HomeView')
          else:
               return render(request,'app/login.html')

     def post(self, request):
          email = request.POST.get('email')
         
          password = request.POST.get('password')
          user=Customers.objects.filter(email=email)
          if user.exists():
               user=user.first()
               if check_password(password,user.password):
                    request.session['user_email']=email
                    return redirect('HomeView')
               else:
                    messages.warning(request, f'password is incorrect please enter right password')
                    return redirect('LoginView')
          else:
               messages.warning(request, f'User doesnot exists please register it')
               return redirect('LoginView')

class SellerLoginView(View):
     def get(self,request):
          if 'seller_email' in request.session:
               return redirect('HomeView')
          else:
               return render(request,'app/seller_login.html')
     def post(self, request):
          email = request.POST.get('email')
          password = request.POST.get('password') 
          seller=Sellers.objects.filter(email=email)
          if seller.exists():
               print("********************************1111******************************************************************")
               seller=seller.first()
               if check_password(password,seller.password):
                    print("******************************222********************************************************************")
                    request.session['seller_email']=email
                    return redirect('MySellerAccountView')
               else:
                    messages.warning(request, f'password is incorrect please enter right password')
                    return redirect('SellerLoginView')
          else:
               messages.warning(request, f'Seller doesnot exists please register it')
               return redirect('SellerLoginView')

class AddProductView(View):
     def get(self,request):
          try:
               all_category=Category.objects.all().order_by('-id')
               return render(request,'app/add-product.html',{"categories":all_category})
          except:
               return render(request,'app/add-product.html')

     def post(self, request):
          current_datetime = datetime.datetime.now()
          product_name = request.POST.get('product_name')
          product_description = request.POST.get('product_description')
          product_price = request.POST.get('product_price')
          product_category = request.POST.get('product_category')
          product_image = request.FILES['product_image']
          live_seller=Sellers.objects.get(email=request.session['seller_email'])
          cat=Category.objects.get(category_name=product_category)
          try:
               create_product=Product(product_name=product_name,product_description=product_description,product_price=product_price,product_image=product_image,seller=live_seller,product_category=cat,date_created=current_datetime)
               create_product.save()
               return redirect('ProductListPage')
          except:
               messages.warning(request, f'product "{product_name}" is already exists')
               return redirect('AddProductView')

class EditProductView(View):
     def get(self,request,product):
          get_product=Product.objects.get(id=product)
          categories=Category.objects.all().order_by("-id")
          return render(request,'app/edit-product.html',{'product':get_product,'categories':categories})

     def post(self, request,product):
          current_datetime = datetime.datetime.now()
          product_name = request.POST.get('product_name')
          product_description = request.POST.get('product_description')
          product_price = request.POST.get('product_price')
          product_category = request.POST.get('product_category')
          exist_product=Product.objects.get(id=product)
          cat=Category.objects.get(category_name=product_category)
          try:
               exist_product.product_name=product_name
          except:
                messages.warning(request, f'product "{product_name}" is already exists')
                return redirect('EditProductView')
          exist_product.product_description=product_description
          exist_product.product_price=product_price
          current_datetime = datetime.datetime.now()
          exist_product.date_modified=current_datetime
          try:
               product_image = request.FILES['product_image']
               if product_image:
                    exist_product.product_image=product_image
          except:
               pass
          exist_product.product_category=cat
          exist_product.date_modified=current_datetime
          exist_product.save()
          return redirect('ProductListPage')
         

class AddCategoryView(View):
    def get(self,request):
          categories=Category.objects.all().order_by("-id")
          return render(request,'app/add-category.html',{'categories':categories})
    def post(self, request):  
          try:
               category = request.POST['product_category']
               add_category = Category(category_name=category)
               add_category.save()
          #   categories=Category.objects.all()
          #   cat_list=[[category.id,category.category_name] for category in categories]
            

               response={
                 "success":"success",
                 "id":add_category.id,
               #   "categories":cat_list,
               }
               return JsonResponse(response)
               
          except:
               response={
                 "error":"error",
            }
               return JsonResponse(response)

class DeleteCategoryView(View):
     
     def post(self,request,pk):
          Category.objects.filter(id=pk).delete()
          response={
               "delete":True,
          }
          return JsonResponse(response)


class FilterFunction(View):
     
     def get(self,request):
          categories=Category.objects.all().order_by("-id")
          return render(request,'app/product-list.html',{"categories":categories})
     def post(self, request):
          category_list=list(map(int, request.POST.getlist('cat_list[]')))
          if len(category_list) != 0:
               product_list=Product.objects.filter(product_category__in=category_list,is_active=True)
               data = serializers.serialize('json', list(product_list),fields=('product_name','product_description','product_price','product_image','product_category','pk'))
               print(data,"**********************************^^^DDDDDDDDDDDDDDDD**************")
               return JsonResponse(data,safe=False)
          else:
                return JsonResponse({"err":'err'})


class InactiveProductList(View):
     def get(self,request):
          products = Product.objects.filter(is_active=False).order_by('date_created')
          paginator = Paginator(products, 10)
          page_number = request.GET.get('page')
          page_object = paginator.get_page(page_number)
          categories=Category.objects.all().order_by("-id")
          return render(request,'app/inactive-products.html',{"page_object":page_object,"categories":categories})
     def post(self,request):
          print()
          activate_product=Product.objects.filter(id=request.POST.get('activate_product')).update(is_active=True)
     
          return redirect('InactiveProductList')
    
class SearchProduct(View):
     def post(self,request):
          
          search=request.POST.get('search_product')
          
          # searched = Product.objects.filter(Q(product_name__icontains=search) | Q(content__icontains=search))
          searched = Product.objects.filter(Q(product_name__icontains=search)|Q(product_category__category_name__icontains=search)).exclude(is_active=False)
          if searched.exists():
               data = serializers.serialize('json', list(searched),fields=('product_name','product_description','product_price','product_image','product_category','pk'))
               
               print(data,"**********************************^^^DDDDDDDDDDDDDDDD**************")
                    
               return JsonResponse(data,safe=False)
          

class Logout(View):
     def get(self, request):
          if 'user_email' in request.session:
               del request.session['user_email']
               return redirect('HomeView')
          if 'seller_email' in request.session:
               del request.session['seller_email']
               return redirect('HomeView')

       