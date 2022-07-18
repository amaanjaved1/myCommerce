from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("past_listings", views.past_listings, name="past_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"), 
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path("add_bid/<int:listing_id>", views.add_bid, name="add_bid")
]
