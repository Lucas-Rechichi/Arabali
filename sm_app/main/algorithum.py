import os
import base64
import magic
import google.generativeai as genai

from datetime import date

from dotenv import load_dotenv
from main.extras import capitalize_plus, exact_display, approx_display, harvinsine_distance
from main.extras import remove_last_character, modified_reciprocal, difference

from main.prompts import Prompts
from main.models import Catergory, PostTag, Interest, UserStats, Following
from main.models import Media, Comment, NestedComment, LikedBy, Post

from django.db.models import Count, Sum
from django.core.files.storage import default_storage
from django.contrib.auth.models import User


class Algorithum:
    class Core:
        def average(num_list, is_abs):
            total_value = 0.0
            for i in num_list:
                total_value += i 

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
        
        def difference(num_final, num_initial, is_abs):
            if is_abs:
                return abs(num_final - num_initial)
            else:
                return num_final - num_initial
        

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

            title = post_obj.title
            contents = post_obj.contents

            current_catergories = Catergory.objects.all()
            response = chat.send_message(Prompts.dermine_catergory_prompt(title=title, contents=contents, catergories_list=current_catergories))

            return response.text

    class PostRendering:
        def get_post_data(post_list, user_obj):

            # Setup
            feed = []
            user = user_obj
            
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
                        liked_reply = NestedComment.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

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
                    liked_comment = Comment.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

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
                liked_post = Post.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

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
                    'post_created_at': post.created_at,
                    'post_liked_by': post_liked_by,
                    'post_comments': post_comments
                })

                return feed
            
        def show_catergories(type):
            if type == 'popular':
                # Show popular catergories based on the tag (basic sorting)
                pass
            else:
                # Show recommended catergories baces on interest first than the tag value (shuffle, than basic sorting)
                pass

        # TODO: Make function for both sorting types to be used (in Algorithum.Sorting)
            
        def auto_post_loading(incrementing_factor, catergory, user):
            if catergory == 'all':
                posts = list(Post.objects.annotate(Count('created_at')).order_by('-created-at'))

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

            # Recording updates to the database
            interest_obj.value = new_interest_value
            interest_obj.save()

            function_obj.factor = new_function_factor
            function_obj.save()

    class Maintenence:
        def delete_interest():
            pass

    class Sorting:

        # Sorts posts baced on their value
        def popular_sort(user, sub_catagory):
            if sub_catagory == None:
                return 'Error: No Sub-Catergory.'
            sub_catagory = str(sub_catagory)
            if sub_catagory == '|All':
                all_tags = PostTag.objects.annotate(Count('value')).order_by('-value')
                order = []
                for tag in all_tags:
                    order.append(tag.post)
                return order
            else:
                relevent_tags = PostTag.objects.filter(name=sub_catagory.removeprefix('|'))
                all_tags = relevent_tags.annotate(Count('value')).order_by('-value')
                order = []
                for tag in all_tags:
                    order.append(tag.post)
                return order

        # Sorting posts baced on their relevance to the user's interest.   
        def recommended_sort(user, sub_catagory):
            if sub_catagory == None:
                return 'Error: No Sub-Catergory.'
            order = []
            i = 0
            if sub_catagory == '|All':
                interests = Interest.objects.filter(user=user).annotate(Count('value')).order_by('-value')
                for _ in range(len(interests)):
                    for interest in interests:
                        tags = PostTag.objects.filter(name=interest.name).annotate(Count('value')).order_by('-value')
                        for tag_id, tag in enumerate(tags):
                            if tag_id == i:
                                post = Post.objects.get(post_tag=tag)
                                order.append(post)
                    i += 1

            else:
                interest = Interest.objects.get(name=sub_catagory.removeprefix('|'), user=user)
                tags = PostTag.objects.filter(name=interest.name)
                for tag in tags:
                    post = Post.objects.get(post_tag=tag)
                    order.append(post)
            return order
        
        def catch_up_sort(user):

            # Setup
            user_stats = UserStats.objects.get(user=user.pk)
            user_follower_object = Following.objects.get(name=user_stats.user.username)
            followers = UserStats.objects.filter(following=user_follower_object)
            distances = {}

            # Calculate harvinsine distance between every follower that user follows and the user
            for follower in followers:
                distance_between_users = harvinsine_distance(lat1=user_stats.last_recorded_latitude, lat2=follower.last_recorded_latitude, lon1=user_stats.last_recorded_longitude, lon2=follower.last_recorded_longitude)
                distances[f'{follower.user.username}'] = distance_between_users

            print(followers)

            # Sorts them baced on the one that is the closest to the user in distance
            distances = dict(sorted(distances.items(), key=lambda item: item[1]))

            # Filters posts that were created today and also are followers of the user acessing the page. 
            # The followers come from the distance dictionary and therefore is ordered baced on the distances as well.
            daily_feed = []
            remaining_feed = []
            todays_posts = Post.objects.filter(created_at__date=date.today())
            for post in todays_posts:
                if post.user.username in distances.keys():
                    daily_feed.append(post)
            remaining_posts = Post.objects.exclude(created_at__date=date.today())
            for post in remaining_posts:
                if post.user.username in distances.keys():
                    remaining_feed.append(post)
            print(daily_feed, remaining_feed)
            return daily_feed, remaining_feed

    class Search:

        # Gives results that are related to the query searched.
        def results_order(query):
            query = str(query)
            captialized_query = capitalize_plus(query)
            highest_q_value = len(query) * 2

            # Setup
            exact_solutions = {}
            feed = {
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
                        if user_stat.user.pk not in feed['exact']['users'].keys() and user_stat.user.pk not in feed['approx']['users'].keys(): # Removes duplicates for both exact and approx solutions
                            feed['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                        #print(f"found {solution} in {user_stat.user.username}")
                    else:
                        #print(f"didn't find {solution} in {user_stat.user.username}")
                        pass
                    if str(solution.lower()) in str(user_stat.user.username):
                        if user_stat.user.pk  not in feed['exact']['users'].keys() and user_stat.user.pk not in feed['approx']['users'].keys():
                            feed['exact']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                        #print(f"found {solution.lower()} in {user_stat.user.username}")
                    else:
                        #print(f"didn't find {solution.lower()} in {user_stat.user.username}")
                        pass

            # Loops though all tags to see if the name of the tag relates to the search query
            for tag in tags:
                for combination_id, solution in exact_solutions.items():
                    if str(solution) in str(tag.name):
                        if tag.name not in feed['exact']['tags'].keys() and tag.name not in feed['approx']['tags'].keys():
                            feed['exact']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                        #print(f"found {solution} in {tag.name}")
                    else:
                        #print(f"didn't find {solution} in {tag.name}")
                        pass
                    if str(solution.lower()) in str(tag.name):
                        if tag.name not in feed['exact']['tags'].keys() and tag.name not in feed['approx']['tags'].keys():
                            feed['exact']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': exact_display(modified_reciprocal(combination_id))}
                            

                        #print(f"found {solution.lower()} in {tag.name}")
                    else:
                        #print(f"didn't find {solution.lower()} in {tag.name}")
                        pass
            
            # Loops though all posts to see if the title relates to the search query
            for post in posts:
                for combination_id, solution in exact_solutions.items():
                    if str(solution) in str(post.title):
                        if post.pk not in feed['exact']['posts'].keys() and post.pk not in feed['approx']['posts'].keys():
                            feed['exact']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': exact_display(modified_reciprocal(combination_id))}
                            
                        #print(f"found {solution} in {post.title}")
                    else:
                        #print(f"didn't find {solution} in {post.title}")
                        pass
                    if str(solution.lower()) in str(post.title):
                        if post.pk not in feed['exact']['posts'].keys() and post.pk not in feed['approx']['posts'].keys():
                            feed['exact']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': exact_display(modified_reciprocal(combination_id))}
                            
                        #print(f"found {solution.lower()} in {post.title}")
                    else:
                        #print(f"didn't find {solution.lower()} in {post.title}")
                        pass

            # APPROXIMATE SOLUTIONS

            # Loops though all users to see if their name relates to the search query
            for user_stat in user_stats:
                split_result_dict = {}
                split_result_list = [x for x in (user_stat.user.username)] 
                for a in range(len(user_stat.user.username)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(user_stat.user.username):
                        if user_stat.user.pk  not in feed['approx']['users'].keys() and user_stat.user.pk not in feed['exact']['users'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': approx_display(combination_id, highest_q_value)}
                            
                        #print(f"found {solution} in {user_stat.user.username}")
                    else:
                        #print(f"didn't find {solution} in {user_stat.user.username}")
                        pass
                    if str(solution.lower()) in str(user_stat.user.username):
                        if user_stat.user.pk  not in feed['approx']['users'].keys() and user_stat.user.pk not in feed['exact']['users'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['users'][user_stat.user.pk] = {'id': user_stat.user.pk,'name': user_stat.user.username, 'value': approx_display(combination_id, highest_q_value)}
                            
                        #print(f"found {solution.lower()} in {user_stat.user.username}")
                    else:
                        #print(f"didn't find {solution.lower()} in {user_stat.user.username}")
                        pass

            # Loops though all tags to see if the name of the tag relates to the search query
            for tag in tags:
                split_result_dict = {}
                split_result_list = [x for x in (tag.name)] 
                for a in range(len(tag.name)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(tag.name):
                        if tag.name not in feed['approx']['tags'].keys() and tag.name not in feed['exact']['tags'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': approx_display(combination_id, highest_q_value)}
                            
                        #print(f"found {solution} in {tag.name}")
                    else:
                        #print(f"didn't find {solution} in {tag.name}")
                        pass
                    if str(solution.lower()) in str(tag.name):
                        if tag.name not in feed['approx']['tags'].keys() and tag.name not in feed['exact']['tags'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['tags'][tag.name] = {'id': tag.pk,'name': tag.name, 'value': approx_display(combination_id, highest_q_value)}
                            

                        #print(f"found {solution.lower()} in {tag.name}")
                    else:
                        #print(f"didn't find {solution.lower()} in {tag.name}")
                        pass
            
            # Loops though all posts to see if the title relates to the search query
            for post in posts:
                split_result_dict = {}
                split_result_list = [x for x in (post.title)] 
                for a in range(len(post.title)):
                    split_result_dict[split_result_list[a]] =  [a + 1]
                for combination_id, solution in approximate_solutions.items():
                    if str(solution) in str(post.title):
                        if post.pk not in feed['approx']['posts'].keys() and post.pk not in feed['exact']['posts'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': approx_display(combination_id, highest_q_value)}

                        # order here
                            feed['approx']['posts'][post.pk]['value']
                        #print(f"found {solution} in {post.title}")
                    else:
                        #print(f"didn't find {solution} in {post.title}")
                        pass
                    if str(solution.lower()) in str(post.title):
                        if post.pk not in feed['approx']['posts'].keys() and post.pk not in feed['exact']['posts'].keys():
                            for char_index, char in approximate_solutions.items():
                                if char in split_result_list:
                                    combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                            feed['approx']['posts'][post.pk] = {'id': post.pk,'name': post.title, 'value': approx_display(combination_id, highest_q_value)}
                            
                    else:
                        #print(f"didn't find {solution.lower()} in {post.title}")
                        pass

            # SORTING OF RESULTS

            # Sort users by value
            sorted_users = sorted(feed['exact']['users'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['exact']['users'] = {k: v for k, v in sorted_users}

            # Sort tags by value
            sorted_tags = sorted(feed['exact']['tags'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['exact']['tags'] = {k: v for k, v in sorted_tags}

            # Sort posts by value
            sorted_posts = sorted(feed['exact']['posts'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['exact']['posts'] = {k: v for k, v in sorted_posts}

            # Sort users by value
            sorted_users = sorted(feed['approx']['users'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['approx']['users'] = {k: v for k, v in sorted_users}

            # Sort tags by value
            sorted_tags = sorted(feed['approx']['tags'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['approx']['tags'] = {k: v for k, v in sorted_tags}

            # Sort posts by value
            sorted_posts = sorted(feed['approx']['posts'].items(), key=lambda item: item[1]['value'], reverse=True)
            feed['approx']['posts'] = {k: v for k, v in sorted_posts}

            return feed










