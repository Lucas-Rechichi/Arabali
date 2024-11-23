import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Comment, LikedBy, NestedComment, Post, UserStats, PostTag, Interest, ICF, InterestInteraction, PostInteraction, Notification, Following
from messaging.models import Message, ChatRoom, PollMessage
from messaging.extras import emoticons_dict
from django.core.exceptions import ObjectDoesNotExist
from main.algorithum import Algorithum


def add_post(request):

    # Getting sent data
    title = request.POST.get('title')
    contents = request.POST.get('contents')
    media = request.FILES.get('media')
    user = request.user