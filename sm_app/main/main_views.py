
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from validate.forms import User
from django.contrib.auth.decorators import login_required

from main.models import Post
from main.extras import remove_until_character, initialize_page
from main.algorithum import Algorithum
from main.forms import EditProfile, EditPost, Search
from main.models import LikedBy, Following, DateAndOrTimeSave
from main.models import UserStats, Comment, NestedComment, Media
from main.configure import Configure

from datetime import date

# Create your views here.
def home(request):
    return render(request, "main/home.html")


@login_required
def page(request, catagory):
    # Getting relevent variables
    name = request.user.username
    user = User.objects.get(username=name)
    user_stats = UserStats.objects.get(user=user)
    posts = Post.objects.all()
    users_stats = UserStats.objects.all()
    init = initialize_page(request)

    if user_stats.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    # Creating the day save for the interaction check function
    if not DateAndOrTimeSave.objects.filter(abstract='Interaction Check').exists():
        interaction_stamp = DateAndOrTimeSave(abstract='Interaction Check', day=date.today())
        interaction_stamp.save()

    # Forms
    if request.method == 'POST':
        search_bar = Search(request.POST)
    else:
        search_bar = Search()

    # Comment and Reply Processing
    liked_by = {}
    post_comments = {}
    post_replies = {}
    for post in posts:
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
    
    # Getting sub catagory
    catagory = str(catagory)
    if '|' in catagory:
        sub_catagory = remove_until_character(catagory, '|')
    else:
        sub_catagory = None

    # Orders posts baced on catagory: Setup
    popular_type = False
    recommended_type = False

    # Orders posts baced on catagory
    if 'popular' in catagory:

        # Sort the posts baced on the given catergory
        posts = Algorithum.PostSorting.popular_sort(user=user, sub_catagory=sub_catagory)
        if posts == 'Error: No Sub-Catergory.':
            return render(request, 'main/error.html', {'issue': 'No Sub Catergory.'})
        
        display_categories = Algorithum.PostRendering.show_catergories(type='popular', user_obj=user)
        popular_type = True
    elif 'recommended' in catagory:

        # Sort the posts baced on the given catergory
        posts = Algorithum.PostSorting.recommended_sort(user=user, sub_catagory=sub_catagory)
        if posts == 'Error: No Sub-Catergory.':
            return render(request, 'main/error.html', {'issue': 'No Sub Catergory.'})
        
        display_categories = Algorithum.PostRendering.show_catergories(type='recommended', user_obj=user)
        recommended_type = True
    else:
        return render(request, 'main/error.html', {'issue': 'Catagory Dose Not Exist'})

    # Only allows the top 10 posts to be displayed first
    posts_to_append = Algorithum.PostRendering.posts_per_page(post_list=posts, incrementing_factor=1, limit_index=None)

    # Extracts relevant data for the post feed
    feed = Algorithum.PostRendering.get_post_data(post_list=posts_to_append, user_obj=user)

    # Variables
    variables = {
        "username": name, 
        "posts": feed,
        "catagory": catagory,
        "display_catergories": display_categories,
        "type": {
            "popular": popular_type,
            "recommended": recommended_type
        },
        'user_stats': users_stats, 
        'user': user_stats,
        'liked_by': liked_by,
        'search_bar': search_bar,
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }
    return render(request, "main/page.html", variables)

@login_required
def catch_up_page(request):
    # Setup
    user_stats = UserStats.objects.get(user=request.user)
    users_stats = UserStats.objects.all()
    posts = Post.objects.all()
    init = initialize_page(request)
    user_liked_by = LikedBy.objects.get(name=request.user.username)

    if user_stats.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

    # Code to prevent the constant pop up of the location permissions modal
    current_time = timezone.now()
    last_recorded_location_time = user_stats.last_recorded_location

    if timezone.is_naive(last_recorded_location_time):
        last_recorded_location_time = timezone.make_aware(last_recorded_location_time)

    hour_difference = abs(last_recorded_location_time.hour - current_time.hour)
    location_pop_up = 'allow'
    if hour_difference <= 2:
        location_pop_up = 'deny'

    # Algorithum for sorting the posts
    daily_posts, remaining_posts = Algorithum.PostSorting.catch_up_sort(user=request.user)

    # Post Rendering
    daily_post_count = len(daily_posts)
    if daily_post_count > 10:
        daily_posts = Algorithum.PostRendering.posts_per_page(post_list=daily_posts, incrementing_factor=1, limit_index=None)
        remaining_feed = None
    else:
        daily_posts = Algorithum.PostRendering.posts_per_page(post_list=daily_posts, incrementing_factor=1, limit_index=None)
        post_difference = 10 - daily_post_count
        remaining_posts = Algorithum.PostRendering.posts_per_page(posts=remaining_posts, incrementing_factor=1, limit_index=post_difference)

    # Getting post data
    daily_feed = Algorithum.PostRendering.get_post_data(post_list=daily_posts, user_obj=request.user)
    remaining_feed = Algorithum.PostRendering.get_post_data(post_list=remaining_posts, user_obj=request.user)

    # All caught up message
    all_caught_up = '''
        <div class="row">
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
        </div>
    '''

    # Comment and Reply Processing
    liked_by = {}
    post_comments = {}
    post_replies = {}
    for post in posts:
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
        'user_stats':users_stats, 
        'user':user_stats,
        'liked_by': liked_by,
        'user_liked_by': user_liked_by,
        'post_comments': post_comments,
        'post_replies':post_replies,
        'search_bar': init['search_bar'],
        'location_pop_up': location_pop_up,
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }
    return render(request, "main/catch_up.html", variables)


@login_required
def add_post(request):
    # Getting relevant data
    init = initialize_page(request)
    user = request.user
    user_stats = UserStats.objects.get(user=user)
    if user_stats.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

    variables = {
        'user_stats': user_stats,
        'username': init['username'], 
        'search_bar': init['search_bar'],
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }


    return render(request, 'main/add_post.html', variables)


@login_required
def profile(request, name):
    init = initialize_page(request)
    u = User.objects.get(username=name)
    us = UserStats.objects.get(user=u)
    if us.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    follow = Following.objects.all()
    posts = Post.objects.filter(user=u)
    followed_userstats = []
    for x in follow:
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
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
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
        "user_liked_by": user_liked_by, # for the post, not comments
        "post_comments": post_comments,
        "post_replies" : post_replies,
        "search_bar" : init['search_bar'],
        "username": init['username'],
        "post_users": post_users,
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }
    return render(request, 'main/posts.html', variables)

@login_required
def config(request, name):
    init = initialize_page(request)
    
    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    # Checking that the right user is acessing this page.
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
                    try:
                        liked_by_users.append(UserStats.objects.get(user=User.objects.get(username=user_liked_by_obj.name)))
                        liked_by_user_set.add(user_liked_by_obj)
                    except User.DoesNotExist:
                        break
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
        'liked_by_users': liked_by_users,
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }        
    return render(request, 'main/config.html', variables)

def error(request, error):
    init = initialize_page(request)
    return render(request, 'main/error.html', {'issue':error, 'notifications': init['notification_list'], 'notification_count': init['notification_count']})

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
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
        }
    return render(request, 'main/search.html', variables)
