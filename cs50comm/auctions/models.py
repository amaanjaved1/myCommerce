from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
 


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=256)
    startingBid = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="matching_listings")
    active = models.BooleanField(default=True)
    publishingDate = models.DateTimeField(default=timezone.now)
    currentBid = models.FloatField(blank=True, null=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posted_listings")
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings")
    buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} for {self.startingBid} published by {self.publisher}"



class Comments(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    post = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="post_comments")
    content = models.CharField(max_length=128)
    commentDate = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.commenter} on {self.post}: {self.content}"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.PROTECT, related_name="current_bids") 
    value = models.FloatField()
    commodity = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bidder} on {self.commodity} for {self.value}"
