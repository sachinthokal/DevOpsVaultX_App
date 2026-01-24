from django.shortcuts import render
# Products app मधील मॉडेल इम्पोर्ट करणे आवश्यक आहे
from products.models import Product 

def home(request):
    # Fakt is_new=True aslele products fetch kara
    featured_products = Product.objects.filter(is_new=True)
    return render(request, 'pages/home.html', {'products': featured_products})

# def products(request):
#     return render(request, 'products/product_list.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    return render(request, 'pages/contact.html')