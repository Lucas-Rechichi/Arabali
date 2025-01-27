from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from validate.forms import User
from django.contrib.auth.decorators import login_required

from main.models import Post
from main.extras import initialize_page
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
def page(request, category, sub_category, increment):

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
                    'date_created':sub_comment.date_created
                }
            post_comments[f'{comment.pk}'] = {
                'id':comment.pk,
                'post':comment.post,
                'post_id':comment.post.pk,
                'user':comment.user,
                'text':comment.text,
                'liked__by':comment.liked_by,
                'likes':comment.likes,
                'date_created':comment.date_created               
            }

    # Orders posts baced on category
    if category == 'popular':

        # Sort the posts baced on the given catergory
        posts = Algorithum.PostSorting.popular_sort(sub_category=sub_category)
        if posts == 'Error: No Sub-Category.':
            return render(request, 'main/error.html', {'issue': 'No Sub Category.'})

        display_categories = Algorithum.PostRendering.show_catergories(type='popular', user_obj=user)

    elif category == 'recommended':

        # Sort the posts baced on the given catergory
        posts = Algorithum.PostSorting.recommended_sort(user=user, sub_category=sub_category)
        if posts == 'Error: No Sub-Category.':
            return render(request, 'main/error.html', {'issue': 'No Sub Category.'})

        display_categories = Algorithum.PostRendering.show_catergories(type='recommended', user_obj=user)

    else:
        return render(request, 'main/error.html', {'issue': 'Category Dose Not Exist'})

    # Only allows the top 10 posts to be displayed first
    posts_to_append = Algorithum.PostRendering.posts_per_page(post_list=posts, incrementing_factor=increment, limit_index=None)

    # Extracts relevant data for the post feed
    feed = Algorithum.PostRendering.get_post_data(post_list=posts_to_append, user_obj=user)

    # Variables
    variables = {
        "username": name, 
        "posts": feed,
        "category": category,
        'sub_category': sub_category,
        "display_catergories": display_categories,
        'increment': {
            'backwards': increment - 5,
            'previous': increment - 1,
            'current': increment,
            'next': increment + 1,
            'forwards': increment + 5
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
def catch_up_page(request, increment):
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
    if daily_post_count > increment * 10:
        daily_posts = Algorithum.PostRendering.posts_per_page(post_list=daily_posts, incrementing_factor=increment, limit_index=None)
        remaining_feed = None
    else:
        daily_posts = Algorithum.PostRendering.posts_per_page(post_list=daily_posts, incrementing_factor=increment, limit_index=None)
        post_difference = (increment * 10) - daily_post_count
        remaining_posts = Algorithum.PostRendering.posts_per_page(post_list=remaining_posts, incrementing_factor=increment, limit_index=post_difference)

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
                    'date_created':sub_comment.date_created
                }
            post_comments[f'{comment.pk}'] = {
                'id':comment.pk,
                'post':comment.post,
                'post_id':comment.post.pk,
                'user':comment.user,
                'text':comment.text,
                'liked__by':comment.liked_by,
                'likes':comment.likes,
                'date_created':comment.date_created               
            }
    post_comments = dict(post_comments)  # Convert defaultdict to regular dictionary

    # For the following segment
    user_following_object = Following.objects.get(name=request.user.username)
    following_userstats = UserStats.objects.filter(following=user_following_object)

    # Variables
    variables = {
        'username': init['username'], 
        'daily_posts': daily_feed if daily_feed else None,
        'remaining_posts': remaining_feed if remaining_feed else None,
        'increment': {
            'backwards': increment - 5,
            'previous': increment - 1,
            'current': increment,
            'next': increment + 1,
            'forwards': increment + 5
        },
        'following': following_userstats,
        'all_caught_up': all_caught_up,
        'user_stats': users_stats, 
        'user': user_stats,
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

    # Setup
    init = initialize_page(request)
    user = User.objects.get(username=name)
    user_stats = UserStats.objects.get(user=user)
    followers = user_stats.following.filter(name=name)
    posts = Post.objects.filter(user=user)

    if user_stats.is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

    # For the followers of this user
    followed_userstats = []
    for follower in followers:
        follower_user_obj = User.objects.get(username=follower)
        follower_userstats = UserStats.objects.get(user=follower_user_obj)
        followed_userstats.append(follower_userstats)

    # For if the user acessing the page is following this user
    is_following = user_stats.following.filter(name=request.user.username).exists()

    # For the media of the post, to show the first image of the carousel
    user_posts_data = []
    for post in posts:
        media_obj = post.media.first()

        post_data = {
            'post_id': post.pk,
            'post_title': post.title,
            'post_media_url': media_obj.media_obj.url
        }

        user_posts_data.append(post_data)

    # If you are on your own profile
    if request.user.username == name:
        self_profile = True
    else:
        self_profile = False

    # Form logic
    if request.method == 'POST':
        if 'follow' in request.POST:
            user_following_obj = Following.objects.get(name=request.user.username)

            # Following logic
            if request.POST['follow'] == 'follow':
                user_stats.following.add(user_following_obj)
                user_stats.followers += 1
            elif request.POST['follow'] == 'unfollow':
                user_stats.followers -= 1
                user_stats.following.remove(user_following_obj)
            user_stats.save()

            # Update is_following boolean
            is_following = user_stats.following.filter(name=request.user.username).exists()
            return HttpResponseRedirect(f'/profile/{user.username}')

    # Sending over data
    profile_vars = {
        'username': request.user.username, # for the user acessing this page
        'user': user, 
        'userstats': user_stats, 
        'is_following': is_following, 
        'self_profile': self_profile, 
        'user_posts_data': user_posts_data,
        'followed_users': followed_userstats,
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

    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})

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
                'date_created':sub_comment.date_created
            }
        post_comments[f'{comment.pk}'] = {
            'id':comment.pk,
            'post':comment.post,
            'post_id':comment.post.pk,
            'user':comment.user,
            'text':comment.text,
            'liked__by':comment.liked_by,
            'likes':comment.likes,
            'date_created':comment.date_created               
        }
    post_comments = dict(post_comments)  # Convert defaultdict to regular dictionary

    post_data = Algorithum.PostRendering.get_post_data(post_list=[post], user_obj=user)[0]

    variables = {
        "post": post_data, 
        "user_stats": user_stats, 
        "user_liked_by": user_liked_by, # for the post, not comments
        "post_comments": post_comments,
        "post_replies" : post_replies,
        "search_bar" : init['search_bar'],
        "username": init['username'],
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
def search_results(request, query, increment):
    init = initialize_page(request=request) # initialize for topbar

    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    
    # Getting search results
    highest_q_value = len(query) * 2

    solutions_data = Algorithum.Search.query_solutions(query=query, abs_cutoff_value=4)
    solution_type = solutions_data['type']

    results_dict = {
        'exact': {
            'users': [],
            'categories': [],
        },
        'approx' : {
            'users': [],
            'categories': [],
        }
    }

    id_dict = {}

    # Searches for apropriate solutions given the query 
    results_dict = Algorithum.Search.result_values_users(results_dict=results_dict, solutions_data=solutions_data, id_dict=id_dict, highest_q_value=highest_q_value)
    results_dict = Algorithum.Search.result_values_categories(results_dict=results_dict, solutions_data=solutions_data, id_dict=id_dict, highest_q_value=highest_q_value)

    # Solution sorting
    results_dict = Algorithum.Search.query_sorting(results_dict=results_dict, search_type=solution_type)

    # Extract relevant data from search results so that they can be serialized though JSON to the front-end.
    results_data = {
        'users': [],
        'categories': []
    }

    # Limits the results of the suggestions to 10 per type, per page
    for index, user_solution in enumerate(results_dict[solution_type]['users']):
        index += 1
        if (10 * (increment - 1)) < index < ((10 * increment) + 1):
            results_data['users'].append({
                'username': user_solution['object'].user.username,
                'user_pfp_url': user_solution['object'].pfp.url
            })
        else:
            break

    for index, category_solution in enumerate(results_dict[solution_type]['categories']):
        index += 1
        if (10 * (increment - 1)) < index < ((10 * increment) + 1):
            results_data['categories'].append({
                'category_name': category_solution['object'].name
            })
        else:
            break

    print(results_dict)

    variables = {
        'results_data': results_data,
        'query': query,
        'results_type': solution_type,
        'increment': {
            'previous': increment - 1,
            'current': increment,
            'next': increment + 1
        },
        'username': init['username'],
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }

    return render(request, 'main/search.html', variables)
