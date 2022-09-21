# Commerce Website (No Styling) -
Ecommerce website sumulator built to test my skills of database manipulation (doesn't contain css).

## Description
### Tech Stack
- Django: Manages database, routing, and function calls
- HTML (Jinja) / CSS: Used to render pages
- Python: Database executions, template rendering, function calls
### Challenges
- Adding images to listings
### Future To Implement
- Add CSS

### Requirements
1. Install Python (https://python.org/download/)
1. Install SetupTools ($ pip install setuptools)
1. Install pip ($ easy_install pip)
1. Install Django ($ pip install django)
1. Install Pillow ($ pip install pillow)

### How to run
1. $ cd cs50comm
1. $ python3 manage.py runserver

# Features

## Navbar
- Login/Register: Diseappear once the user is logged in/registerd
- Home (Active Listings): Home Page which displays all listings in the database which are currently active.
- Categories: Gives users the ability to add new product cateogires and filter active listings by category type.
- Watchlist: Contains 4 categories of watched listings
1. Recently Bidded: All biddings which user has recently bidded on appear here.
1. Won Listings: All the biddings which the user has won appear here.
1. Scouted Listings: All scouted listings appear here.
1. Expired Listings: All "watched" listings that have expired appear here.
- Create Listing: Users can create a new listing and add a Title, Description, Category, Image(optional), and a starting bid price
- Log Out

## View Listing
- Viewing Listing: Contains the title of the listing
- Comment Section: Contains a comment section where users can comment on the listing 
- Bidding: Users can view the current bid price and add valid bids (must be greater than the current bid price)
- Watchlist: Users can add the listing to their watchlist
