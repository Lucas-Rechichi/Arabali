import os
import base64
import magic
import google.generativeai as genai

from datetime import date

from dotenv import load_dotenv
from main.extras import capitalize_plus, exact_display, approx_display, haversine_distance
from main.extras import remove_last_character, modified_reciprocal, difference

from main.prompts import Prompts
from main.models import Category, PostTag, Interest, UserStats, Following
from main.models import Media, LikedBy, Post

from messaging.models import ChatRoom, Message, PollMessage
from messaging.extras import emoticons_dict

from django.db.models import Count, Q
from django.core.files.storage import default_storage
from django.contrib.auth.models import User


class Algorithum:
    class Core:

        # Function for finding the average value within the list
        def average(num_list, is_abs):
            total_value = 0.0
            for num in num_list:
                total_value += num

            if is_abs:
                if len(num_list) == 0:
                    ave = abs( (total_value) / 1 )
                else:
                    ave = abs( (total_value) / (len(num_list)) )
                
            else:
                if len(num_list) == 0:
                    ave = (total_value) / 1
                else:
                    ave = (total_value) / (len(num_list))
            return ave
        
        # Function for finding the difference between 2 numbers 
        def difference(num_final, num_initial, is_abs):
            if is_abs:
                return abs(num_final - num_initial)
            else:
                return num_final - num_initial
        
        # Function for sorting objects baced on the value
        def basic_sort(object_name, sub_category, user_obj=None):

            # Setup
            order = []

            # Logic for what to sort
            if object_name == 'tag':
                if sub_category == 'all':
                    sorted_objects = PostTag.objects.all().annotate(Count('value')).order_by('-value')
                else:
                    filtered_objects = PostTag.objects.filter(name=sub_category)
                    sorted_objects = filtered_objects.annotate(Count('value')).order_by('-value')

            else:
                if sub_category == 'all':
                    sorted_objects = Interest.objects.all().annotate(Count('value')).order_by('-value')
                else:
                    filtered_objects = Interest.objects.filter(name=sub_category, user=user_obj)
                    sorted_objects = filtered_objects.annotate(Count('value')).order_by('-value')

            # Appends the sorted queryset to a list
            for obj in sorted_objects:
                order.append(obj)

            return order

        # Function for sorting objects with respect to their individual value compared to the average value
        def shuffle_sort(values_list, names_list, iterations):
            # Setup
            order = []
            name_exclusions = []

            # Loops for as many iterationa as specified
            for _ in range(0, iterations):
                # Get the average value, the highest value and it's index
                average = Algorithum.Core.average(num_list=values_list, is_abs=True)
                highest_value = max(values_list)
                value_index = values_list.index(highest_value)

                # Get the modified value, replace the highest value with it's modified value in the list
                modified_value = highest_value - average
                values_list[value_index] = modified_value

                # Sees if the number of iterations of the order exceeds the number of posts in the database
                relevant_tag_count = PostTag.objects.filter(name=names_list[value_index]).count()
                name_count = order.count(names_list[value_index])

                if name_count >= relevant_tag_count:
                    name_exclusions.append(names_list[value_index])

                # If the limit has been reached for interests.
                if sorted(names_list) == sorted(name_exclusions):
                    break

                # Append the name to the order list
                if names_list[value_index] in name_exclusions:
                    continue
                else:
                    order.append(names_list[value_index])

            return order


    class PostCreations:
        def predict_catergory_request(post_obj):

            # Setup of the LLM used to detrmine the catergory of the post
            load_dotenv()
            google_gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

            genai.configure(api_key=google_gemini_api_key)
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            chat = model.start_chat()

            for i, media in enumerate(post_obj.media.all()):
                # Get content type of the media
                media_path = media.media_obj.name
                full_media_path = default_storage.path(media_path)

                mime = magic.Magic(mime=True)
                media_content_type = mime.from_file(full_media_path)

                # Format media URL
                encoded_image = base64.b64encode(media.media_obj.read()).decode('utf-8')
                media_url = f'data:{media_content_type};base64,{encoded_image}'

                caption_list = {
                    'text': media.caption_text,
                    'colour': media.caption_colour,
                    'font': media.caption_font
                }

                response = chat.send_message(Prompts.store_media_data(media_url=media_url, caption_list=caption_list, index=i))

            # Get post data for the AI to deside what tag it should be
            title = post_obj.title
            contents = post_obj.contents

            # AI decision
            current_catergories = Category.objects.all()
            response = chat.send_message(Prompts.dermine_catergory_prompt(title=title, contents=contents, catergories_list=current_catergories))

            return response.text

    class PostRendering:
        def get_post_data(post_list, user_obj):

            # Setup
            feed = []
            user = user_obj
            user_liked_by = LikedBy.objects.get(name=user.username).name # for has_liked
            
            # Loops though all selected posts
            for i, post in enumerate(post_list):
                user_stats = UserStats.objects.get(user=post.user)
                # Gets the nested data within comments, liked_by and replies

                # Setup
                post_liked_by = []
                post_media = []
                post_comments = []
                post_liked_by_users = list(post.liked_by.all())

                for j in range(0, len(post_liked_by_users)): # liked_by
                    # Getting relevant data
                    user_liked_user_obj = User.objects.get(username=post_liked_by_users[j].name)
                    user_liked_userstats = UserStats.objects.get(user=user_liked_user_obj)

                    # Packaging data into a dictionary
                    post_liked_by.append({
                        'username': post_liked_by_users[j].name,
                        'user_pfp_url': user_liked_userstats.pfp.url,
                    })
                
                for k, media in enumerate(Media.objects.filter(post=post)):
                    post_media.append({
                        'media_url': media.media_obj.url,
                        'caption_text': media.caption_text,
                        'caption_colour': media.caption_colour,
                        'caption_font': media.caption_font
                    })

                for l, comment in enumerate(post.comments.all()): # comments
                    # Setup
                    post_comment_replies = []

                    for m, reply in enumerate(comment.replies.all()): # replies
                        # Getting relevant data
                        reply_user_userstats = UserStats.objects.get(user=reply.user)

                        # If the user has liked this reply
                        liked_reply = reply.liked_by.filter(name=user_liked_by).exists()

                        # Packaging data into a dictionary
                        post_comment_replies.append({ 
                            'reply_id': reply.pk,
                            'reply_username': reply.user.username,
                            'has_liked': liked_reply,
                            'reply_user_pfp_url': reply_user_userstats.pfp.url,
                            'reply_text': reply.text,
                            'reply_likes': reply.likes,
                        })
                    # Getting relevant data
                    comment_user_userstats = UserStats.objects.get(user=comment.user)

                    # If the user has liked this comment
                    liked_comment = comment.liked_by.filter(name=user_liked_by).exists()

                    # Packaging data into a dictionary
                    post_comments.append({
                        'comment_id': comment.pk,
                        'comment_username': comment.user.username,
                        'has_liked': liked_comment,
                        'comment_user_pfp_url': comment_user_userstats.pfp.url,
                        'comment_text': comment.text,
                        'comment_likes': comment.likes,
                        'comment_replies': post_comment_replies
                    })

                # If the user has liked the post
                liked_post = post.liked_by.filter(name=user_liked_by).exists()

                # Packaging data into a dictionary
                feed.append({
                    'post_id': post.pk,
                    'post_username': post.user.username,
                    'has_liked': liked_post,
                    'post_user_pfp_url': user_stats.pfp.url, 
                    'post_title': post.title,
                    'post_contents': post.contents,
                    'post_media': post_media,
                    'post_likes': post.likes,
                    'post_date_created': post.date_created,
                    'post_liked_by': post_liked_by,
                    'post_comments': post_comments
                })

            return feed
            
        def show_catergories(type, user_obj):
            catergory_list = []

            # Type logic
            if type == 'popular':

                # Setup
                catergories = Category.objects.all()
                category_dict = {}

                # Loops though all catergories
                for category in catergories:
                    tags = PostTag.objects.filter(name=category.name)
                    total_value = 0.0

                    # Loops though all tags with the same name as the catergories
                    for tag in tags:
                        total_value += tag.value # append the individual tag value to the total for this catergory

                    # Append the name and the total value of the catergory so that they share the same index order
                    category_dict[category] = total_value

                    category_dict = dict(sorted(category_dict.items(), key=lambda v: v[1]))

                # Loops though all catergories, gets the one with the highest value then appends the name to the catergory list
                for i in range(0, len(category_dict.keys())):
                    selected_name = list(category_dict.keys())[i]
                    catergory_list.append(selected_name)

            else:
                interest_list = Algorithum.Core.basic_sort(object_name='interests', sub_category='all', user_obj=user_obj)
                catergory_list = interest_list

            return catergory_list

        # Function for restricting the post count to 10 for the first loading of the feed
        def posts_per_page(post_list, incrementing_factor, limit_index):
            appending_posts = []

            # Logic for the left and right bounds
            if limit_index:
                limit_index = 10 - limit_index
            else:
                limit_index = 0

            # Restrict the post count
            for i, post in enumerate(post_list):
                i += 1
                if (10 * (incrementing_factor - 1)) < i < ((10 * incrementing_factor) + 1) - limit_index:
                    appending_posts.append(post)

            return appending_posts
    
        # Function for loading the next 10 posts for the feed
        def auto_post_loading(incrementing_factor, catergory, user):
            if catergory == 'all':
                posts = list(Post.objects.annotate(Count('date_created')).order_by('-created-at'))

            elif catergory == 'popular':
                post_tags = PostTag.objects.annotate(Count('value')).order_by('-value')
                posts = []
                for post_tag in post_tags:
                    posts.append(post_tag.post)

            else: # catergory is recommended or catch up (yet to add features for followers)
                interests = list(user.interests.annotate(Count('value')).order_by('-value'))
                best_interest = interests[0]
                posts = list(PostTag.objects.get(name=best_interest.name).posts.all())

            appending_posts = []
            for i, post in enumerate(posts):
                i += 1
                if (10 * (incrementing_factor - 1)) < i < ((10 * incrementing_factor) + 1):
                    appending_posts.append(post)

            return appending_posts

    class Depreciations:
        def calculate_post_consequence_function(post_tag_obj):

            # Getting tag value
            current_tag_value = post_tag_obj.value

            # Getting the old and new interactions, And putting them in a list
            old_interactions_list = list(post_tag_obj.post_interactions.filter(is_new=False).values_list('value', flat=True))
            current_interactions_list = list(post_tag_obj.post_interactions.filter(is_new=True).values_list('value', flat=True))

            # Making the lists the same length
            if len(old_interactions_list) > len(current_interactions_list):
                for _ in range(0, len(old_interactions_list)):
                    current_interactions_list.append(0)

            if len(old_interactions_list) < len(current_interactions_list):
                for _ in range(0, len(current_interactions_list)):
                    old_interactions_list.append(0)

            # Computing the difference list
            difference_list = []
            interaction_count = len(old_interactions_list) # current_interactions_list can be used here also
            for index in range(0, interaction_count):
                difference = Algorithum.Core.difference(num_final=current_interactions_list[index], num_initial=old_interactions_list[index], is_abs=False)
                difference_list.append(difference)

            # Getting the average of the post_tags
            post_tag_values_list = list(PostTag.objects.all().values_list('value', flat=True))
            average_post_tag_value = Algorithum.Core.average(num_list=post_tag_values_list, is_abs=False) # ABS dosen't mattter here due to all tag values always being positive

            # Getting the sum of the difference_list
            sum_of_difference = 0.0
            for index in range(0, len(difference_list)):
                sum_of_difference += difference_list[index]

            # Getting the function parameters
            function_obj = post_tag_obj.PCF
            current_factor = function_obj.factor
            is_active = function_obj.is_active
            if is_active:
                
                # Computing the function
                function_result = (current_factor) * ( (sum_of_difference) ** (1/3) )

                # Updating tag value and function factor
                if function_result == 0:
                    new_post_tag_value = current_tag_value - average_post_tag_value

                else:
                    new_post_tag_value = current_tag_value + (average_post_tag_value * function_result)
                
                new_function_factor = (current_tag_value/new_post_tag_value)

                # Recording updates to the database
                post_tag_obj.value = new_post_tag_value
                post_tag_obj.save()

                function_obj.factor = new_function_factor
                function_obj.save()

        def calculate_interest_consequence_function(interest_obj):

            # Getting interest value
            current_interest_value = interest_obj.value

            # Getting the old and new interactions, And putting them in a list
            old_interactions_list = list(interest_obj.interest_interactions.filter(is_new=False).values_list('value', flat=True))
            current_interactions_list = list(interest_obj.interest_interactions.filter(is_new=True).values_list('value', flat=True))

            # Making the lists the same length
            if len(old_interactions_list) > len(current_interactions_list):
                for _ in range(0, len(old_interactions_list)):
                    current_interactions_list.append(0)

            if len(old_interactions_list) < len(current_interactions_list):
                for _ in range(0, len(current_interactions_list)):
                    old_interactions_list.append(0)

            # Computing the difference list
            difference_list = []
            interaction_count = len(old_interactions_list) # current_interactions_list can be used here also
            for index in range(0, interaction_count):
                difference = Algorithum.Core.difference(num_final=current_interactions_list[index], num_initial=old_interactions_list[index], is_abs=False)
                difference_list.append(difference)

            # Getting the average of the interests
            interest_values_list = list(Interest.objects.all().values_list('value', flat=True))
            average_interest_value = Algorithum.Core.average(num_list=interest_values_list, is_abs=False) # ABS dosen't mattter here due to all interest values always being positive

            # Getting the sum of the difference_list
            sum_of_difference = 0.0
            for index in range(0, len(difference_list)):
                sum_of_difference += difference_list[index]

            # Getting the function parameters
            function_obj = interest_obj.ICF
            current_factor = function_obj.factor
                
            # Computing the function
            function_result = (current_factor) * ( (sum_of_difference) ** (1/3) )

            # Updating tag value and function factor
            if function_result == 0:
                new_interest_value = current_interest_value - average_interest_value

            else:
                new_interest_value = current_interest_value + (average_interest_value * function_result)
            
            new_function_factor = (current_interest_value/new_interest_value)

            # Checking to see if the interest value is too low, deletes outliers that are too low
            interest_userstats = interest_obj.userstats
            user_interests = Interest.objects.filter(user=interest_userstats)
            user_interest_values = user_interests.values_list('value', flat=True)
            user_average_interest_value = Algorithum.Core.average(num_list=user_interest_values, is_abs=False)

            for interest in user_interests:
                if interest * 7 < user_average_interest_value:
                    interest.delete()
        
            # Recording updates to the database
            interest_obj.value = new_interest_value
            interest_obj.save()

            function_obj.factor = new_function_factor
            function_obj.save()

    class PostSorting:

        # Sorts posts baced on their value
        def popular_sort(sub_category):

            # Setup
            order = []

            # Returns an error if the url has no sub-catergory specified
            if sub_category == None:
                return 'Error: No Sub-Category.'

            # Gets the order of the posts using basic sort
            sub_category = str(sub_category)
            tag_order = Algorithum.Core.basic_sort(object_name='tag', sub_category=sub_category)

            # Gets the post related to the tag
            for tag in tag_order:
                order.append(tag.post)

            return order

        # Sorting posts baced on their relevance to the user's interest.   
        def recommended_sort(user, sub_category):

            # Setup
            order = []
            interest_names_list = []
            interest_values_list = []
            tag_iterations = {}

            # Returns an error if the url has no sub-catergory specified
            if sub_category == None:
                return 'Error: No Sub-Category.'
            
            # Get all the interest values and names for the specified user
            interests = Interest.objects.filter(user=user)

            # Loops though all interests the user has, appends to lists such that they have the same index
            for interest in interests:
                interest_names_list.append(interest.name)
                interest_values_list.append(interest.value)

            # Defines the amount of iterations for the names list to generate
            iterations = Post.objects.count()

            # Gets the list of names using a shuffle sort
            name_order = Algorithum.Core.shuffle_sort(values_list=interest_values_list, names_list=interest_names_list, iterations=iterations)

            # Gets the relevant tags for the selected name
            for name in name_order:
                # Logic for new tag entries
                if name not in tag_iterations:
                    tag_iterations[name] = 0
                
                # Orders the tags based on individual value
                tag_order = Algorithum.Core.basic_sort(object_name='tag', sub_category=name, user_obj=user)

                # Select the tag depending on what iteration that name is on
                selected_tag = tag_order[tag_iterations[name]]
                order.append(selected_tag.post) # appends the tag's relevant post to the order

                # Increments the tag iterations so that the next post in order is chosen
                tag_iterations[name] += 1

            return order

        def catch_up_sort(user):

            # Setup
            user_stats = UserStats.objects.get(user=user)
            user_follower_object = Following.objects.get(name=user_stats.user.username)
            followers = UserStats.objects.filter(following=user_follower_object)

            daily_feed = []
            remaining_feed = []
            distances_dict = {}

            # Defining the latitude and longitude of the user acessing the page
            user_lat = user_stats.last_recorded_latitude
            user_lon = user_stats.last_recorded_longitude

            # Loop though all follwers, calculate distance, add data to a dictionary
            for follower in followers:
                follower_lat = follower.last_recorded_latitude
                follower_lon = follower.last_recorded_longitude

                distance_between_users = haversine_distance(lat1=user_lat, lat2=follower_lat, lon1=user_lon, lon2=follower_lon)
                distances_dict[follower] = distance_between_users

            # Sort the dictionary
            distances_dict = dict(sorted(distances_dict.items(), key=lambda d: d[1]))

            # Put user's posts into their respective post type
            for distance_key in distances_dict.keys():
                follower_daily_posts = Post.objects.filter(Q(user=distance_key.user) & (Q(date_created__date=date.today()) | Q(date_modified__date=date.today())))
                print(follower_daily_posts)
                for daily_post in follower_daily_posts:
                    daily_feed.append(daily_post)

                follower_remaining_posts = Post.objects.filter(user=distance_key.user).exclude(Q(date_created__date=date.today()) & Q(date_modified__date=date.today()))
                for remaining_post in follower_remaining_posts:
                    remaining_feed.append(remaining_post)


            return daily_feed, remaining_feed


    class Search:

        def result_values_users(results_dict, solutions_data, highest_q_value):

            # Setup
            user_stats = UserStats.objects.all()
            solution_type = solutions_data['type']

            # Solution logic
            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                # Loops though all users to see if their name relates to the search query (exact)
                for user_stat in user_stats:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(user_stat.user.username): # if the string is present within this user's name
                            if user_stat.user.pk not in results_dict['exact']['users'].keys() and user_stat.user.pk not in results_dict['approx']['users'].keys(): # Removes duplicates for both exact and approx solutions
                                results_dict['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk, 'object': user_stat, 'value': exact_display(modified_reciprocal(combination_id))}

                        if str(solution.lower()) in str(user_stat.user.username):
                            if user_stat.user.pk  not in results_dict['exact']['users'].keys() and user_stat.user.pk not in results_dict['approx']['users'].keys():
                                results_dict['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk, 'object': user_stat, 'value': exact_display(modified_reciprocal(combination_id))}
                
            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                # Loops though all users to see if their name relates to the search query (approximate)
                for user_stat in user_stats:
                    split_result_dict = {}
                    split_result_list = [x for x in (user_stat.user.username)] 
                    for a in range(len(user_stat.user.username)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(user_stat.user.username):
                            if user_stat.user.pk  not in results_dict['approx']['users'].keys() and user_stat.user.pk not in results_dict['exact']['users'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk, 'object': user_stat, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(user_stat.user.username):
                            if user_stat.user.pk  not in results_dict['approx']['users'].keys() and user_stat.user.pk not in results_dict['exact']['users'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk, 'object': user_stat, 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def result_values_posts(results_dict, solutions_data, highest_q_value):

            # Setup
            posts = Post.objects.all()
            solution_type = solutions_data['type']

            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                # Loops though all posts to see if the title relates to the search query
                for post in posts:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(post.title):
                            if post.pk not in results_dict['exact']['posts'].keys() and post.pk not in results_dict['approx']['posts'].keys():
                                results_dict['exact']['posts'][post.pk] = {'id': post.pk, 'object': post, 'value': exact_display(modified_reciprocal(combination_id))}
                                
                        if str(solution.lower()) in str(post.title):
                            if post.pk not in results_dict['exact']['posts'].keys() and post.pk not in results_dict['approx']['posts'].keys():
                                results_dict['exact']['posts'][post.pk] = {'id': post.pk, 'object': post, 'value': exact_display(modified_reciprocal(combination_id))}

            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                # Loops though all posts to see if the title relates to the search query
                for post in posts:
                    split_result_dict = {}
                    split_result_list = [x for x in (post.title)] 
                    for a in range(len(post.title)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(post.title):
                            if post.pk not in results_dict['approx']['posts'].keys() and post.pk not in results_dict['exact']['posts'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['posts'][post.pk] = {'id': post.pk, 'object': post, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(post.title):
                            if post.pk not in results_dict['approx']['posts'].keys() and post.pk not in results_dict['exact']['posts'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['posts'][post.pk] = {'id': post.pk, 'object': post, 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def result_values_categories(results_dict, solutions_data, highest_q_value):

            # Setup
            categories = Category.objects.all()
            solution_type = solutions_data['type']

            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                # Loops though all catergories to see if the name of the catergory relates to the search query
                for category in categories:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(category.name):
                            if category.name not in results_dict['exact']['catergories'].keys() and category.name not in results_dict['approx']['catergories'].keys():
                                results_dict['exact']['catergories'][category.name] = {'id': category.pk, 'object': category, 'value': exact_display(modified_reciprocal(combination_id))}
                                

                        if str(solution.lower()) in str(category.name):
                            if category.name not in results_dict['exact']['catergories'].keys() and category.name not in results_dict['approx']['catergoires'].keys():
                                results_dict['exact']['catergoires'][category.name] = {'id': category.pk, 'object': category, 'value': exact_display(modified_reciprocal(combination_id))}
            
            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                # Loops though all categories to see if the name of the category relates to the search query
                for category in categories:
                    split_result_dict = {}
                    split_result_list = [x for x in (category.name)] 
                    for a in range(len(category.name)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(category.name):
                            if category.name not in results_dict['approx']['categories'].keys() and category.name not in results_dict['exact']['categories'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['categories'][category.name] = {'id': category.pk, 'object': category, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(category.name):
                            if category.name not in results_dict['approx']['categories'].keys() and category.name not in results_dict['exact']['categories'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['categories'][category.name] = {'id': category.pk, 'object': category, 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def result_values_emoticons(results_dict, solutions_data, highest_q_value):

            # Setup
            emoticons = emoticons_dict.keys()
            solution_type = solutions_data['type']

            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                for emoticon in emoticons:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(emoticon): # if the string is present within this user's name
                            if emoticon not in results_dict['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                results_dict['exact']['emoticons'][emoticon] = {'name': emoticon, 'unicode': emoticons_dict[emoticon], 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(emoticon):
                            if emoticon not in results_dict['exact'].keys():
                                results_dict['exact']['emoticons'][emoticon] = {'name': emoticon, 'unicode': emoticons_dict[emoticon], 'value': approx_display(combination_id, highest_q_value)}

            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                for emoticon in emoticons:
                    split_result_dict = {}
                    split_result_list = [x for x in (emoticon)] 
                    for a in range(len(emoticon)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(emoticon):
                            if emoticon  not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['emoticons'][emoticon] = {'name': emoticon, 'unicode': emoticons_dict[emoticon], 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(emoticon):
                            if emoticon not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['emoticons'][emoticon] = {'name': emoticon, 'unicode': emoticons_dict[emoticon], 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def result_values_chatrooms(results_dict, solutions_data, highest_q_value):

            # Setup
            chatrooms = ChatRoom.objects.all()
            solution_type = solutions_data['type']

            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                for chatroom in chatrooms:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(chatroom.name): # if the string is present within this user's name
                            if chatroom.name not in results_dict['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                results_dict['exact']['chatrooms'][chatroom.name] = {'id': chatroom.pk, 'object': chatroom, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(chatroom.name):
                            if chatroom.name not in results_dict['exact'].keys():
                                results_dict['exact']['chatrooms'][chatroom.name] = {'id': chatroom.pk, 'object': chatroom, 'value': approx_display(combination_id, highest_q_value)}

                    
            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                for chatroom in chatrooms:
                    split_result_dict = {}
                    split_result_list = [x for x in (chatroom.name)] 
                    for a in range(len(chatroom.name)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(chatroom.name):
                            if chatroom.name not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['chatrooms'][chatroom.name] = {'id': chatroom.pk, 'object': chatroom, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(chatroom.name):
                            if chatroom.name not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['chatrooms'][chatroom.name] = {'id': chatroom.pk, 'object': chatroom, 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def result_values_messages(results_dict, solutions_data, highest_q_value):

            # Setup
            messages = Message.objects.exclude(text=None)
            solution_type = solutions_data['type']

            if solution_type == 'exact':
                solutions = solutions_data['solutions']

                for message in messages:
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(message.text): # if the string is present within this message's text
                            if message.text not in results_dict['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                results_dict['exact']['chatrooms'][message.text] = {'id': message.pk, 'object': message, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(message.text):
                            if message.text not in results_dict['exact'].keys():
                                results_dict['exact']['chatrooms'][message.text] = {'id': message.pk, 'object': message, 'value': approx_display(combination_id, highest_q_value)}

            else: # solution_type == 'approx'
                solutions = solutions_data['solutions']

                for message in messages:
                    split_result_dict = {}
                    split_result_list = [x for x in (message.text)] 
                    for a in range(len(message.text)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in solutions.items():
                        if str(solution) in str(message.text):
                            if message.text not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['chatrooms'][message.text] = {'id': message.pk, 'object': message, 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(message.text):
                            if message.text not in results_dict['approx'].keys():
                                for char_index, char in solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                results_dict['approx']['chatrooms'][message.text] = {'id': message.pk, 'object': message, 'value': approx_display(combination_id, highest_q_value)}

            return results_dict

        def query_solutions(query, abs_cutoff_value):

            # Getting the query, the capitalised query, and th highest value a match can have
            query = str(query)
            captialized_query = capitalize_plus(query)
            solutions = {}

            # Query solutions logic
            if len(query) < abs_cutoff_value:
                solution_type = 'approx'

                # Gets all possible approximate solutions for the inserted query
                broken_query = [x for x in captialized_query] 
                for a in range(len(captialized_query)):
                    solutions[a + 1] =  broken_query[a]

            elif len(query) == abs_cutoff_value:
                solution_type = 'exact'

                # Gets all possible exact solutions for the inserted query
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

            else: # len(query) > abs_cuttof_value 
                solution_type = 'exact'

                # Gets all possible exact solutions for the inserted query. Removes the least likely value every charater over 2.
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

                extra_chars = len(query) - abs_cutoff_value
                for _ in range(0, extra_chars):
                    solutions.popitem()

            # Package type and solutions into a list
            solution_data = {
                'type': solution_type,
                'solutions': solutions
            }

            return solution_data

        def query_sorting(results_dict, search_type, search_object_name):
            sorted_objects = sorted(results_dict[search_type][search_object_name].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict[search_type][search_object_name] = {k: v for k, v in sorted_objects}

            return results_dict

        # Gives results that are related to the query searched.
        def results_order(query):
            query = str(query)
            captialized_query = capitalize_plus(query)
            highest_q_value = len(query) * 2

            # Setup
            exact_solutions = {}
            results_dict = {
                'exact': {
                    'users': {},
                    'tags': {},
                    'posts': {}
                },
                'approx' : {
                    'users': {},
                    'tags': {},
                    'posts': {}
                }
            }

            user_stats = UserStats.objects.all()
            tags = PostTag.objects.all()
            posts = Post.objects.all()

            # Gets all possible exact solutions for the inserted query
            changed_query = captialized_query
            for b in range(len(changed_query)):
                exact_solutions[b + 1] = changed_query
                changed_query = remove_last_character(changed_query)

            # Gets all possible approximate solutions for the inserted query
            approximate_solutions = {}
            broken_query = [x for x in captialized_query] 
            for a in range(len(captialized_query)):
                approximate_solutions[a + 1] =  broken_query[a] 

            # EXACT SOLUTIONS

            # Loops though all users to see if their name relates to the search query
            for user_stat in user_stats:
                for combination_id, solution in exact_solutions.items():
                    if str(solution) in str(user_stat.user.username): # if the string is present within this user's name
                        if user_stat.user.pk not in results_dict['exact']['users'].keys() and user_stat.user.pk not in results_dict['approx']['users'].keys(): # Removes duplicates for both exact and approx solutions
                            results_dict['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                    if str(solution.lower()) in str(user_stat.user.username):
                        if user_stat.user.pk  not in results_dict['exact']['users'].keys() and user_stat.user.pk not in results_dict['approx']['users'].keys():
                            results_dict['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': exact_display(modified_reciprocal(combination_id))}
                            

            # Loops though all tags to see if the name of the tag relates to the search query
            for tag in tags:
                for combination_id, solution in exact_solutions.items():
                    if str(solution) in str(tag.name):
                        if tag.name not in results_dict['exact']['tags'].keys() and tag.name not in results_dict['approx']['tags'].keys():
                            results_dict['exact']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                    if str(solution.lower()) in str(tag.name):
                        if tag.name not in results_dict['exact']['tags'].keys() and tag.name not in results_dict['approx']['tags'].keys():
                            results_dict['exact']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': exact_display(modified_reciprocal(combination_id))}
                            

            # Loops though all posts to see if the title relates to the search query
            for post in posts:
                for combination_id, solution in exact_solutions.items():
                    if str(solution) in str(post.title):
                        if post.pk not in results_dict['exact']['posts'].keys() and post.pk not in results_dict['approx']['posts'].keys():
                            results_dict['exact']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': exact_display(modified_reciprocal(combination_id))}
                            
                    if str(solution.lower()) in str(post.title):
                        if post.pk not in results_dict['exact']['posts'].keys() and post.pk not in results_dict['approx']['posts'].keys():
                            results_dict['exact']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': exact_display(modified_reciprocal(combination_id))}

            # APPROXIMATE SOLUTIONS

            # Loops though all users to see if their name relates to the search query
            for user_stat in user_stats:
                split_result_dict = {}
                split_result_list = [x for x in (user_stat.user.username)] 
                for a in range(len(user_stat.user.username)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(user_stat.user.username):
                        if user_stat.user.pk  not in results_dict['approx']['users'].keys() and user_stat.user.pk not in results_dict['exact']['users'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': approx_display(combination_id, highest_q_value)}

                    if str(solution.lower()) in str(user_stat.user.username):
                        if user_stat.user.pk  not in results_dict['approx']['users'].keys() and user_stat.user.pk not in results_dict['exact']['users'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': approx_display(combination_id, highest_q_value)}

            # Loops though all tags to see if the name of the tag relates to the search query
            for tag in tags:
                split_result_dict = {}
                split_result_list = [x for x in (tag.name)] 
                for a in range(len(tag.name)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(tag.name):
                        if tag.name not in results_dict['approx']['tags'].keys() and tag.name not in results_dict['exact']['tags'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': approx_display(combination_id, highest_q_value)}

                    if str(solution.lower()) in str(tag.name):
                        if tag.name not in results_dict['approx']['tags'].keys() and tag.name not in results_dict['exact']['tags'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': approx_display(combination_id, highest_q_value)}
            
            # Loops though all posts to see if the title relates to the search query
            for post in posts:
                split_result_dict = {}
                split_result_list = [x for x in (post.title)] 
                for a in range(len(post.title)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(post.title):
                        if post.pk not in results_dict['approx']['posts'].keys() and post.pk not in results_dict['exact']['posts'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': approx_display(combination_id, highest_q_value)}

                    if str(solution.lower()) in str(post.title):
                        if post.pk not in results_dict['approx']['posts'].keys() and post.pk not in results_dict['exact']['posts'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            results_dict['approx']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': approx_display(combination_id, highest_q_value)}

            # SORTING OF RESULTS

            # Sort all by value
            sorted_users = sorted(results_dict['exact']['users'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['exact']['users'] = {k: v for k, v in sorted_users}

            sorted_tags = sorted(results_dict['exact']['tags'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['exact']['tags'] = {k: v for k, v in sorted_tags}

            sorted_posts = sorted(results_dict['exact']['posts'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['exact']['posts'] = {k: v for k, v in sorted_posts}

            sorted_users = sorted(results_dict['approx']['users'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['approx']['users'] = {k: v for k, v in sorted_users}

            sorted_tags = sorted(results_dict['approx']['tags'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['approx']['tags'] = {k: v for k, v in sorted_tags}

            sorted_posts = sorted(results_dict['approx']['posts'].items(), key=lambda item: item[1]['value'], reverse=True)
            results_dict['approx']['posts'] = {k: v for k, v in sorted_posts}

            return results_dict


    class Recommend:

        def recommend_users(userstats_obj, max_recommendations):
            user_follower_object = Following.objects.get(name=userstats_obj.user.username)
            followers = UserStats.objects.filter(following=user_follower_object)

            user_recommendations = []
            for i, follower in enumerate(followers):
                if i + 1 <= max_recommendations:
                    user_recommendations.append({
                        'username': follower.user.username,
                        'user_pfp_url': follower.pfp.url,
                    })
                else:
                    break

            return user_recommendations

        def recommend_posts(userstats_obj, max_recommendations):
            # Setup
            interest_names_list = []
            interest_values_list = []

            # Get user's interests
            interests = Interest.objects.filter(user=userstats_obj.user)
            for interest in interests:
                interest_names_list.append(interest.name)
                interest_values_list.append(interest.value)

            # Preform a shuffle sort to get the names_list
            name_order = Algorithum.Core.shuffle_sort(names_list=interest_names_list, values_list=interest_values_list, iterations=max_recommendations)

            # Gets the relevant tags for the selected name
            tag_iterations = {}
            posts = []
            for name in name_order:
                # Logic for new tag entries
                if name not in tag_iterations:
                    tag_iterations[name] = 0
                
                # Orders the tags based on individual value
                tag_order = Algorithum.Core.basic_sort(object_name='tag', sub_category=name, user_obj=userstats_obj.user)

                # Select the tag depending on what iteration that name is on
                selected_tag = tag_order[tag_iterations[name]]
                posts.append(selected_tag.post) # appends the tag's relevant post to the order

                # Increments the tag iterations so that the next post in order is chosen
                tag_iterations[name] += 1

            # Get post data
            post_recommendations = []
            for index, post in enumerate(posts):
                if index < max_recommendations:
                    media_obj = post.media.first()
                    post_recommendations.append({
                        'post_id': post.pk,
                        'post_title': post.title,
                        'post_media_url': media_obj.media_obj.url
                    })
                else:
                    break

            return post_recommendations


        def recommend_catergories(userstats_obj, max_recommendations):

            # Preform a basic sort, limiting the number of categories shown
            interests = Algorithum.Core.basic_sort(object_name='interest', sub_category='all', user_obj=None)

            category_recommendations = []
            for index, interest in enumerate(interests):
                if index < max_recommendations:
                    category_recommendations.append({
                        'category_name': interest.name
                    })
                else:
                    break

            return category_recommendations
        











