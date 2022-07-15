from tracemalloc import start
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm

from .models import User, Category, Bid, Comments, Listing

def find_listings_by_category():
    empty_list = [] #list which stores all of the listings
    categories = Category.objects.all() #retrieve all existing categories
    for cat in categories: #iterate through all categories
        listings = cat.matching_listings.all() #find all listings in the respective category
        listing_type = cat #listing category
        thisdict = {
            "title": listing_type,
            "listings": listings
        }
        empty_list.append(thisdict)
        thisdict = None
    return empty_list

class CategoryForm(ModelForm):
    class Meta: 
        model = Category
        fields = ["category"]

class ListingForm(ModelForm):
    class Meta: 
        model = Listing
        fields = ["title", "description", "category", "startingBid"]

def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def categories(request):
    if request.method == "POST": 
        form = CategoryForm(request.POST) #get form information
        if form.is_valid(): #if the form is valid
            n_category = form.cleaned_data["category"] #get the user's submission for add category
            categories = Category.objects.all() #get all of the categories under the Category model
            for each in categories: #for every existing cateogry, check if the new category already exists
                if each.category.lower() == n_category.lower(): #if it does then render this error
                    return render(request, "auctions/category.html", {
                "form": CategoryForm,
                "message": "Category Already Exists!",  
                "category": find_listings_by_category()
        }) 
            Category(category=n_category).save() #otherwise add it to the database
            n_category = None
            return render(request, "auctions/category.html", {
                "form": CategoryForm,
                "message": f"Category Added!",
                "category": find_listings_by_category()
        }) 
        else: #if form submission is invalid
            return render(request, "auctions/category.html", {
                "form": form,
                "message": "Invalid Submission",
                "category": find_listings_by_category()
            })
    else: #if user comes to the page via GET
        return render(request, "auctions/category.html", {
            "form": CategoryForm,
            "message": "Add Category",
            "category": find_listings_by_category()
        })

def watchlist(request):
    active = [] #list to store all active listings 
    inactive = [] #list to store all inactive listings
    user = request.user #get user 
    listings = user.watched_listings.all() #get all listings that the user has watched
    for each in listings:
        if each.active == True: # if the listing is active, add it to active list 
            active.append(each)
        else: #otherwise add it to the inactive list
            inactive.append(each)
    return render(request, "auctions/watchlist.html", {
        "active_listings": active,
        "inactive_listings": inactive 
    })

def create_listing(request):
    if request.method == "POST": 
        form = ListingForm(request.POST) #get form information
        if form.is_valid(): #if the form is valid receieve all of the users input
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            startingBid = form.cleaned_data["startingBid"]
            Listing(title=title, description=description, category=category, startingBid=startingBid, publisher=request.user).save() #otherwise add it to the database
            return HttpResponseRedirect(reverse("index"))
        else: #if form submission is invalid
            return render(request, "auctions/create_listing.html", {
                "form": ListingForm,
                "message": "Invalid Submission"
            })
    else: #if user comes to the page via GET
        return render(request, "auctions/create_listing.html", {
            "all_categories": Category.objects.all(), 
            "form": ListingForm
        })
        