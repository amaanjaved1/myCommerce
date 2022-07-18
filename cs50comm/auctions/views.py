from tracemalloc import start
from xml.etree.ElementTree import Comment
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.forms import ModelForm, ValidationError
from django.http import Http404
from django.contrib.auth.decorators import login_required
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
        fields = ["title", "description", "category", "startingBid", "image"]

class CommentForm(ModelForm):
    class Meta: 
        model = Comments
        fields = ["content"]

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["value"]


def index(request):
    all_listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "all_listings": all_listings
    })



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

@login_required
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

@login_required
def watchlist(request):
    scouted = []
    bidded = []
    won = []
    expired = []
    user = request.user #get user 
    listings = user.watched_listings.all() #get all listings that the user has watched
    for each in listings:
        if each.buyer != user and each.active == True:
            scouted.append(each)
        elif each.buyer == user and each.active == True:
            bidded.append(each)
        elif each.buyer == user and each.active == False:
            won.append(each) 
        elif each.buyer != user and each.active == False:
            expired.append(each)  
    return render(request, "auctions/watchlist.html", {
        "scouted": scouted,
        "bidded": bidded, 
        "won": won, 
        "expired": expired
    })

@login_required
def create_listing(request):
    if request.method == "POST": 
        form = ListingForm(request.POST, request.FILES) #get form information
        if form.is_valid(): #if the form is valid receieve all of the users input
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            startingBid = form.cleaned_data["startingBid"]
            image = form.cleaned_data["image"]
            if startingBid <= 0:
               return render(request, "auctions/create_listing.html", {
                "form": form,
                "message": "Invalid Bid Amount"
            }) 
            Listing(title=title, description=description, category=category, startingBid=startingBid, publisher=request.user, image=image).save() #otherwise add it to the database
            return HttpResponseRedirect(reverse("index"))
        else: #if form submission is invalid
            return render(request, "auctions/create_listing.html", {
                "form": form,
                "message": "Invalid Submission"
            })
    else: #if user comes to the page via GET
        return render(request, "auctions/create_listing.html", {
            "all_categories": Category.objects.all(), 
            "form": ListingForm
        })

@login_required 
def listing(request, listing_id):
    try: #see if the listing exists, if it doesn't raise a 404 error, otherwise continue 
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing Not Found")
    else: 
        if request.method == "POST":
            c_form = CommentForm(request.POST)
            if c_form.is_valid():
                content = c_form.cleaned_data["content"]
                Comments(commenter=request.user, post=listing,content=content).save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else: #if the request method is GET
            comments = listing.post_comments.all() #get all of the comments from the listing
            user = request.user
            if listing in user.watched_listings.all():
                status = True 
            else: 
                status = False
            if user == listing.publisher:
                owner = True 
            else:
                owner = False
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "form": CommentForm, 
                "status": status,
                "owner": owner,
                "user": request.user,
                "bid_form": BidForm
            }) 

@login_required
def add_to_watchlist(request, listing_id):
    user = request.user #get user
    listing = Listing.objects.get(id=listing_id) #get listing 
    watchers = listing.watchers.all() #get all the watchers of the post 
    if user in watchers: #if the user has already watched the post 
        raise Http404("Listing is already watched")  
    else: 
        listing.watchers.add(user)
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def remove_from_watchlist(request, listing_id):
    user = request.user #get user
    listing = Listing.objects.get(id=listing_id) #get listing 
    watchers = listing.watchers.all() #get all the watchers of the post 
    if user not in watchers: #if the user has already watched the post 
        raise Http404("Listing is not yet watched")  
    else: 
        listing.watchers.remove(user)
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def close_listing(request, listing_id):
    user = request.user #get user
    listing = Listing.objects.get(id=listing_id) #get listing
    if user != listing.publisher:
        raise Http404("You do not have authorization to close this listing")  
    else: 
        listing.active = False 
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def add_bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id) #get listing
    form = BidForm(request.POST)
    comments = listing.post_comments.all() #get all of the comments from the listing
    user = request.user
    if listing in user.watched_listings.all():
        status = True 
    else: 
        status = False
    if user == listing.publisher:
        owner = True 
    else:
        owner = False
    if form.is_valid():
        value = form.cleaned_data["value"] #get submitted bid value and then validate
        if value >= listing.startingBid and (listing.currentBid is None or value > listing.currentBid):
            valid = True 
        else: 
            valid = False
        if valid == True:
            listing.currentBid = value
            listing.buyer = user
            watchers = listing.watchers.all() #get all the watchers of the post 
            if user not in watchers:
                listing.watchers.add(user) 
            listing.save()
            Bid(bidder=user, value=value, commodity=listing).save()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "form": CommentForm, 
                "status": status,
                "owner": owner,
                "bid_form": BidForm,
                "user": request.user,
                "bidmessage": "Your Bid Has Been Placed!"
            }) 
        else: 
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "form": CommentForm, 
                "status": status,
                "owner": owner,
                "user": request.user,
                "bid_form": BidForm,
                "bidmessage": "Your Bid Is Invalid!"
            })


def past_listings(request):
    all_listings = Listing.objects.all()
    return render(request, "auctions/past_listings.html", {
        "all_listings": all_listings
    })
 
