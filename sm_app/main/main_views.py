from main.extras import capitalize_plus
from main.extras import initialize_page
from main.algorithum import Algorithum
from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import F
from django.db.models import Count, Sum
from django.utils import timezone
from validate.forms import User
from django.contrib.auth.decorators import login_required
from main.models import Post
from main.forms import AddPost, EditProfile, EditPost, AddComment, Search
from main.models import LikedBy, Following, DateAndOrTimeSave
from main.models import UserStats, Comment, NestedComment, PostTag, PCF
from validate.views import create_user_directory
from main.errors import UsernameError
from main.configure import Configure
from datetime import datetime, date, timedelta

# For removing string
def remove_until_character(string, target_char):
    index = string.find(target_char)
    if index != -1:
        return string[index:]
    else:
        return string

# Create your views here.
def home(request):
    return render(request, "main/home.html")


@login_required
def page(request, catagory, increment):
    # Getting relevent variables
    name = request.user.username
    u = User.objects.get(username=name)
    us = UserStats.objects.get(user=u)
    p = Post.objects.all()
    s = UserStats.objects.all()
    user_liked_by = LikedBy.objects.get(name=name)

    if us.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    # Creating the day save for the interaction check function
    if not DateAndOrTimeSave.objects.filter(abstract='Interaction Check').exists():
        interaction_stamp = DateAndOrTimeSave(abstract='Interaction Check', day=date.today())
        interaction_stamp.save()
    
    Algorithum.AutoAlterations.interaction_check()

    # Getting Relelvent Profile Pictures
    post_users = {}
    for user_stat in s:
        post_users[str(user_stat.user.username)] = user_stat.pfp.url
    

    # Forms
    if request.method == 'POST':
        comment_form = AddComment(request.POST)
        sub_comment_form = AddComment(request.POST)
        search_bar = Search(request.POST)
    else:
        comment_form = AddComment()
        sub_comment_form = AddComment()
        search_bar = Search()
    


    # Comment and Reply Processing
    liked_by = {}
    post_comments = {}
    post_replies = {}
    for post in p:
        liked_by[f'{post.pk}'] = list(post.liked_by.all())
        comments_for_post = Comment.objects.filter(post=post)
        for comment in comments_for_post:
            sub_comments = NestedComment.objects.filter(comment=comment)
            for sub_comment in sub_comments:
                post_replies[f'{sub_comment.pk}'] = {
                    'id':sub_comment.pk,
                    'comment':sub_comment.comment,
                    'comment_id':sub_comment.comment.pk,
                    'user':sub_comment.user,
                    'text':sub_comment.text,
                    'liked__by':sub_comment.liked_by,
                    'likes':sub_comment.likes,
                    'created_at':sub_comment.created_at
                }
            post_comments[f'{comment.pk}'] = {
                'id':comment.pk,
                'post':comment.post,
                'post_id':comment.post.pk,
                'user':comment.user,
                'text':comment.text,
                'liked__by':comment.liked_by,
                'likes':comment.likes,
                'created_at':comment.created_at               
            }
    post_comments = dict(post_comments)  # Convert defaultdict to regular dictionary

    
    # Getting sub catagory
    catagory = str(catagory)
    if '|' in catagory:
        sub_catagory = remove_until_character(catagory, '|')
    else:
        sub_catagory = None

    # Orders posts baced on catagory: Setup
    trend_categories = []
    popular_type = False
    recommended_type = False

    # Orders posts baced on catagory
    if 'popular' in catagory:
        posts = Algorithum.Sorting.popular_sort(user=u, sub_catagory=sub_catagory)
        if posts == 'Error: No Sub-Catergory.':
            return render(request, 'main/error.html', {'issue': 'No Sub Catergory.'})
        trend_categories = Algorithum.Core.trending_catagories(catagory_list=trend_categories, type='popular')
        popular_type = True
    elif 'recommended' in catagory:
        posts = Algorithum.Sorting.recommended_sort(user=u, sub_catagory=sub_catagory)
        if posts == 'Error: No Sub-Catergory.':
            return render(request, 'main/error.html', {'issue': 'No Sub Catergory.'})
        trend_categories = Algorithum.Core.trending_catagories(catagory_list=trend_categories, type='recommended')
        recommended_type = True
    else:
        return render(request, 'main/error.html', {'issue': 'Catagory Dose Not Exist'})

    # Only allows 10 posts to be displayed per page, as the increment increases, the post range will change to acompany the next 10 posts..
    feed = []
    feed = Algorithum.Core.posts_per_page(list=feed, incrementing_factor=increment, posts=posts)
    
    # Variables
    variables = {
        "username":name, 
        "post":feed,
        "catagory":catagory,
        "trend_catagories":trend_categories,
        "type": {
            "popular": popular_type,
            "recommended": recommended_type
        },
        "increment": {
            "previous": increment - 1,
            "current": increment,
            "next": increment + 1 
        },
        'user_stats':s, 
        'user':us,
        'post_users': post_users,
        'liked_by': liked_by,
        'user_liked_by': user_liked_by,
        'post_comments': post_comments,
        'post_replies':post_replies, 
        'comment_form': comment_form,
        'sub_comment_form': sub_comment_form,
        'search_bar': search_bar
    }
    return render(request, "main/page.html", variables)

@login_required
def catch_up_page(request, increment):
    # Setup
    us = UserStats.objects.get(user=request.user)
    s = UserStats.objects.all()
    p = Post.objects.all()
    init = initialize_page(request)
    user_liked_by = LikedBy.objects.get(name=request.user.username)
    feed = []

    if us.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

    # Code to prevent the constant pop up of the location permissions modal
    current_time = timezone.now()
    last_recorded_location_time = us.last_recorded_location

    if timezone.is_naive(last_recorded_location_time):
        last_recorded_location_time = timezone.make_aware(last_recorded_location_time)

    hour_difference = abs(last_recorded_location_time.hour - current_time.hour)
    print(hour_difference)
    location_pop_up = 'allow'
    if hour_difference <= 2:
        location_pop_up = 'deny'

    # Algorithum
    daily_posts, remaining_posts = Algorithum.Sorting.catch_up_sort(user=request.user)

    # Special Sorting for this specific page.
    all_posts = {}
    daily_feed = []
    remaining_feed = []
    all_caught_up = None
    i = 0
    for post in daily_posts:
        i += 1
        print(post, i)
        all_posts['daily'] = {
            'no': i, 
            'post': post
        }
        
    
    all_posts['all caught up'] = {
        'no': i + 1,
        'post':  '''<div class="row">
                        <div class="col-12">
                            <div class="card m-5">
                                <div class="row">
                                    <div class="col">
                                        <h4 class="display-4 text-center">You Are All Caught Up!</4>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col d-flex justify-content-center">
                                        <div class="fs-1">
                                            <i class="bi bi-person-fill-check" style="font-size: 15rem; color: #198754;"></i>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <p class="lead text-center">Below are older posts from the people that you follow.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>'''
    }
    x = i + 2
    for post in remaining_posts:
        x += 1
        all_posts['remaining'] = {
            'no': x, 
            'post': post
        }
    for key, value in all_posts.items():
        if (10 * (increment - 1)) < value['no'] < ((10 * increment) + 1):
            if key == 'daily':
                daily_feed.append(value['post'])
            elif key == 'remaining':
                remaining_feed.append(value['post'])
            elif key == 'all caught up':
                all_caught_up = value['post']

    # Getting Relelvent Profile Pictures
    post_users = {}
    for user_stat in s:
        post_users[str(user_stat.user.username)] = user_stat.pfp.url
    
    # Forms
    if request.method == 'POST':
        comment_form = AddComment(request.POST)
        sub_comment_form = AddComment(request.POST)
    else:
        comment_form = AddComment()
        sub_comment_form = AddComment()
    
    # Comment and Reply Processing
    liked_by = {}
    post_comments = {}
    post_replies = {}
    for post in p:
        liked_by[f'{post.pk}'] = list(post.liked_by.all())
        comments_for_post = Comment.objects.filter(post=post)
        for comment in comments_for_post:
            sub_comments = NestedComment.objects.filter(comment=comment)
            for sub_comment in sub_comments:
                post_replies[f'{sub_comment.pk}'] = {
                    'id':sub_comment.pk,
                    'comment':sub_comment.comment,
                    'comment_id':sub_comment.comment.pk,
                    'user':sub_comment.user,
                    'text':sub_comment.text,
                    'liked__by':sub_comment.liked_by,
                    'likes':sub_comment.likes,
                    'created_at':sub_comment.created_at
                }
            post_comments[f'{comment.pk}'] = {
                'id':comment.pk,
                'post':comment.post,
                'post_id':comment.post.pk,
                'user':comment.user,
                'text':comment.text,
                'liked__by':comment.liked_by,
                'likes':comment.likes,
                'created_at':comment.created_at               
            }
    post_comments = dict(post_comments)  # Convert defaultdict to regular dictionary

    # Variables
    variables = {
        "username":init['username'], 
        "daily_posts":daily_feed if daily_posts else None,
        "remaining_posts":remaining_feed if remaining_posts else None,
        "all_caught_up": all_caught_up,
        "increment": {
            "previous": increment - 1,
            "current": increment,
            "next": increment + 1 
        },
        'user_stats':s, 
        'user':us,
        'post_users': post_users,
        'liked_by': liked_by,
        'user_liked_by': user_liked_by,
        'post_comments': post_comments,
        'post_replies':post_replies, 
        'comment_form': comment_form,
        'sub_comment_form': sub_comment_form,
        'search_bar': init['search_bar'],
        'location_pop_up': location_pop_up
    }
    return render(request, "main/catch_up.html", variables)


@login_required
def add_post(request):
    user = request.user
    user_stats = UserStats.objects.get(user=user)
    if user_stats.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    if user_stats.can_post:
        if request.method == "POST": # POST requests are encrypted, safer
            f = AddPost(request.POST, request.FILES) # enables the form for POST request
            print(request.POST, request.FILES)
            print("valid")


            # Getting relevant data
            username = request.user.username
            a = request.POST.get("title")
            c = request.POST.get("content")
            user = User.objects.get(username=username)
            d = request.FILES.get("image")
            create_user_directory(user=user, sub_directory='posts')
            tag = request.POST.get("tag")
            
            # Checking to make sure that the tag is valid
            if '|' in tag:
                return render(request, 'main/error.html', {'issue': 'Tag cannot contain the vertical line symbol ( | )'})
            
            # Capitalization for consistancy and search functionality
            tag = capitalize_plus(tag)

            # Database Things
            b = Post(user=user, title=a, contents=c, likes=0, media=d, created_at=datetime.now())
            b.save()
            base_value = Algorithum.AutoAlterations.base_value(catergory=tag)
            t = PostTag(post=b, name=tag, value=base_value, current_increace=0, previous_increace=0, date_of_change=date.today())
            t.save()
            func = PCF(form='Parabolic Truncus', a=1, k=1, tag=t)
            func.save()

        
            return HttpResponseRedirect("/page/popular|All/1")
        else:
            f = AddPost()
    else:
        return render(request, 'main/error.html', {'issue': 'Cannot Post.'})
    return render(request, 'main/add_post.html', {"input_fields": f, 'username': username})


@login_required
def profile(request, name):
    init = initialize_page(request)
    u = User.objects.get(username=name)
    us = UserStats.objects.get(user=u)

    if us.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    follow = Following.objects
    posts = Post.objects.filter(user=u)
    followed_userstats = []
    for x in follow.all():
        if us.following.filter(subscribers=x).exists():
            followed_userstats.append(UserStats.objects.filter(user=User.objects.get(username=follow.get(subscribers=x))))
    

    is_following = us.following.filter(subscribers=request.user.username).exists()

    if request.user.username == name:
        self_profile = True
    else:
        self_profile = False
    if request.method == 'POST':
        if 'follow' in request.POST:
            if request.POST['follow'] == 'follow':
                us.following.add(follow.get(subscribers=request.user.username))
                us.followers += 1
            elif request.POST['follow'] == 'unfollow':
                us.followers -= 1
                us.following.remove(follow.get(subscribers=request.user.username))
            us.save()
            is_following = us.following.filter(subscribers=request.user.username).exists()
            return HttpResponseRedirect(f'/profile/{u.username}')
    profile_vars = {
        'user': u, 
        'userstats': us, 
        'is_following': is_following, 
        'self_profile': self_profile, 
        'post': posts,
        'followed_user': followed_userstats,
        'search_bar': init['search_bar'],
    }

    return render(request, 'main/profile.html', profile_vars)


def post_view(request, post_id):
    init = initialize_page(request)
    post = Post.objects.get(id=post_id)
    user = User.objects.get(username=post.user.username)
    user_stats = UserStats.objects.get(user=user)
    user_liked_by = LikedBy.objects.get(name=request.user.username)
    s = UserStats.objects.all()

    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

    # Profile pictures
    post_users = {}
    for user_stat in s:
        post_users[str(user_stat.user.username)] = user_stat.pfp.url

    # Comments
    liked_by = {}
    post_comments = {}
    post_replies = {}
    liked_by[f'{post.pk}'] = list(post.liked_by.all())
    comments_for_post = Comment.objects.filter(post=post)
    for comment in comments_for_post:
        sub_comments = NestedComment.objects.filter(comment=comment)
        for sub_comment in sub_comments:
            post_replies[f'{sub_comment.pk}'] = {
                'id':sub_comment.pk,
                'comment':sub_comment.comment,
                'comment_id':sub_comment.comment.pk,
                'user':sub_comment.user,
                'text':sub_comment.text,
                'liked__by':sub_comment.liked_by,
                'likes':sub_comment.likes,
                'created_at':sub_comment.created_at
            }
        post_comments[f'{comment.pk}'] = {
            'id':comment.pk,
            'post':comment.post,
            'post_id':comment.post.pk,
            'user':comment.user,
            'text':comment.text,
            'liked__by':comment.liked_by,
            'likes':comment.likes,
            'created_at':comment.created_at               
        }
    post_comments = dict(post_comments)  # Convert defaultdict to regular dictionary
    variables = {
        "post": post, 
        "user_stats": user_stats, 
        "user_liked_by": user_liked_by,
        "post_comments": post_comments,
        "post_replies" : post_replies,
        "search_bar" : init['search_bar'],
        "username": init['username'],
        "post_users": post_users
    }
    return render(request, 'main/posts.html', variables)

@login_required
def config(request, name):
    init = initialize_page(request)
    # Checking that the right user is acessing this page.

    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    username = request.user.username
    if name != username:
        return render(request, 'main/error.html', {'issue': 'Cannot access this users profile'})
    
    # Getting needed databace values
    user = User.objects.get(username=username)
    user_stats = UserStats.objects.get(user=user)
    liked_bys = LikedBy.objects.all()
    

    # LikedBy Preperation
    liked_by_users = []
    liked_by_user_set = set()
    user_posts = Post.objects.filter(user=user)
    post_list = user_posts
    for user_liked_by_obj in liked_bys:
        for post in post_list:
            if user_liked_by_obj in post.liked_by.all():
                if user_liked_by_obj not in liked_by_user_set:
                    liked_by_users.append(UserStats.objects.get(user=User.objects.get(username=user_liked_by_obj.name)))
                    liked_by_user_set.add(user_liked_by_obj)
    print(post.liked_by.all(), liked_by_users)

    # Form init
    if request.method == 'POST':
        # Forms
        edit_profile_form = EditProfile(request.POST, request.FILES)
        edit_post_form = EditPost(request.POST, request.FILES)

        if request.POST.get('change'):
            if edit_profile_form.is_valid():
                # Form function
                edit_profile = Configure.edit_profile(request=request, current_username=username)
            
                # Editing Error Management
                if edit_profile in ['Cannot be named Images due to the default image directory being called Images.', 'Username Cannot Contain Spaces', 'Username Taken.']:
                    return render(request, 'main/error.html', {'issue': edit_profile})
            
                if edit_profile:
                    return HttpResponseRedirect(f'/edit/{edit_profile.username}')
        
        elif request.POST.get('delete'):
            for p in post_list:
                if int(request.POST.get('post-id')) == int(p.pk):
                    Configure.delete_post(request=request, post=p)
                
        elif request.POST.get('edit'):
            for p in post_list:
                if int(request.POST.get('post-id')) == int(p.pk):
                    Configure.edit_post(request=request, post=p)

        else:
            print('Other button pressed')
            print(request.POST)

    else:

        # Forms
        edit_profile_form = EditProfile()
        edit_post_form = EditPost()
        
    user_posts = Post.objects.filter(user=user)
    post_list = list(user_posts)
    variables = {
        'edit_profile_form': edit_profile_form,
        'edit_post_form': edit_post_form, 
        'user_stats': user_stats, 
        'username': username,
        'posts': post_list,
        'search_bar': init['search_bar'],
        'liked_by_users': liked_by_users
    }        
    return render(request, 'main/config.html', variables)

def error(request, error):
    return render(request, 'main/error.html', {'issue':error})

@login_required
def search_results(request, q, post_increment, user_increment, catergory_increment):
    init = initialize_page(request=request) # initialize for topbar

    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    try:
        query = request.POST.get('query') # getting query
        if not query:
            query = q
    except:
        query = q
    results = Algorithum.Search.results_order(query=query)
    filtered_results = {
        'exact' : {
            'users' : {},
            'posts' : {},
            'tags' : {},
        },
        'approx' : {
            'users' : {},
            'posts' : {},
            'tags' : {},
        }
    }
    p = 0
    for key, value in results['exact']['posts'].items():
        p += 1
        if (10 * (post_increment - 1)) < p < ((8 * post_increment) + (2 * (post_increment - 1))):
            filtered_results['exact']['posts'][key] = value
        if p > ((8 * post_increment) + (2 * (post_increment - 1))):
            break

    for key, value in results['approx']['posts'].items():
        if ((8 * post_increment) + (2 * post_increment)) < p < ((10 * post_increment) + 1):
            filtered_results['approx']['posts'][key] = value
        p += 1
        if p > ((10 * post_increment) + 1):
            break
    
    u = 0
    for key, value in results['exact']['users'].items():
        u += 1
        if (10 * (user_increment - 1)) < u < ((8 * user_increment) + (2 * user_increment - 1)):
            filtered_results['exact']['users'][key] = value
        if u > ((8 * user_increment) + (2 * (user_increment - 1))):
            break

    for key, value in results['approx']['users'].items():
        if ((8 * user_increment) + (2 * user_increment)) < u < ((10 * user_increment) + 1):
            filtered_results['approx']['users'][key] = value
        u += 1
        if u > ((10 * user_increment) + 1):
            break

    c = 0
    for key, value in results['exact']['tags'].items():
        c += 1
        if (10 * (catergory_increment - 1)) < c < ((8 * catergory_increment) + (2 * catergory_increment - 1)):
            filtered_results['exact']['tags'][key] = value
        if c > ((8 * catergory_increment) + (2 * (catergory_increment - 1))):
            break

    for key, value in results['approx']['tags'].items():
        if ((8 * catergory_increment) + (2 * catergory_increment)) < c < ((10 * catergory_increment) + 1):
            filtered_results['approx']['tags'][key] = value
        c += 1
        if c > ((10 * catergory_increment) + 1):
            break
    print(init['username'])
    variables = {
        'feed':filtered_results, 
        'search_bar': init['search_bar'], 
        'username': init['username'],
        'query': query,
        "post_increment" : {
            "previous" : post_increment - 1,
            "current": post_increment,
            "next": post_increment + 1
        },
        "user_increment" : {
            "previous" : user_increment - 1,
            "current": user_increment,
            "next": user_increment + 1
        },
        "category_increment" : {
            "previous" : catergory_increment - 1,
            "current": catergory_increment,
            "next": catergory_increment + 1
        },
        }
    return render(request, 'main/search.html', variables)
