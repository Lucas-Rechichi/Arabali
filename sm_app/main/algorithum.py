import logging
from main.models import Post, PostTag, UserStats, Interest, ICF, PCF, InterestInteraction, PostInteraction, DateAndOrTimeSave, User, Following
from django.db.models import Count, Sum
from datetime import date
import math
from main.extras import capitalize_plus, algorithm_function
from main.extras import remove_until_character, remove_last_character, modified_reciprocal, difference, exact_display, approx_display, harvinsine_distance

class Algorithum:
    
    class AutoAlterations:
        def base_value(catergory):
            total_value = 0
            no_of_posts = 0
            posts = Post.objects.filter(posttag = catergory)
            for post in posts:
                total_value += post.posttag.value
                no_of_posts += 1
            average = total_value / no_of_posts
            return average
        
        def predictions(interest, tag):
            if interest:
                # Setup
                yest_performance = []
                curr_performance = []
                diff_matrix = []

                # Getting relevant interaction values
                yest_interactions = InterestInteraction.objects.filter(type='yesterday', interest=interest).annotate(Sum('id')).order_by('id')
                curr_interactions = InterestInteraction.objects.filter(type='current', interest=interest).annotate(Sum('id')).order_by('id')

                # Creating the value matrices
                for interaction in yest_interactions:
                    yest_performance.append(interaction.value)
                for interaction in curr_interactions:
                    curr_performance.append(interaction.value)

                # Making the matrices the same size
                if len(yest_performance) > len(curr_performance):
                    change = len(yest_performance) - len(curr_performance)
                    for _ in range(0, change):
                        curr_performance.append(0)
                if len(curr_performance) > len(yest_performance):
                    change = len(curr_performance) - len(yest_performance)
                    for _ in range(0, change):
                        yest_performance.append(0)

                # Getting the dot difference: Getting the difference
                for x in range(0, len(curr_performance)):
                    diff_matrix.append(curr_performance[x] - yest_performance[x])

                # Getting the dot difference: Adding up values
                total = 0
                for y in range(0, len(diff_matrix)):
                    total += diff_matrix[y]

                # Function and application
                processed_result = algorithm_function(x=total, interest=interest, tag=None, type='interest')

                multiplier = (1 + (processed_result / 100))
                interest.value = interest.value * multiplier
                interest.save()

            else:
                # Setup
                yest_performance = []
                curr_performance = []
                diff_matrix = []

                # Getting relevant interaction values
                yest_interactions = PostInteraction.objects.filter(type='yesterday', tag=tag).annotate(Sum('id')).order_by('id')
                curr_interactions = PostInteraction.objects.filter(type='current', tag=tag).annotate(Sum('id')).order_by('id')

                # Creating the value matrices
                for interaction in yest_interactions:
                    yest_performance.append(interaction.value)
                for interaction in curr_interactions:
                    curr_performance.append(interaction.value)

                # Making the matrices the same size
                if len(yest_performance) > len(curr_performance):
                    change = len(yest_performance) - len(curr_performance)
                    for _ in range(0, change):
                        curr_performance.append(0)
                if len(curr_performance) > len(yest_performance):
                    change = len(curr_performance) - len(yest_performance)
                    for _ in range(0, change):
                        yest_performance.append(0)

                # Getting the dot difference: Getting the difference
                for x in range(0, len(curr_performance)):
                    diff_matrix.append(curr_performance[x] - yest_performance[x])

                # Getting the dot difference: Adding up values
                total = 0
                for y in range(0, len(diff_matrix)):
                    total += diff_matrix[y]

                # Function and application
                processed_result = algorithm_function(x=total, tag=tag, interest=None, type='posttag')

                multiplier = (1 + (processed_result / 100))
                tag.value = tag.value * multiplier
                tag.save()

            return None
        
        def interaction_check():
            interaction_stamp = DateAndOrTimeSave.objects.get(abstract='Interaction Check')
            if interaction_stamp.day != date.today():
                interest_interactions = InterestInteraction.objects.all()
                post_interactions = PostInteraction.objects.all()
                for interaction in interest_interactions:
                    if interaction.type == 'current':
                        interaction.type = 'yesterday'
                        interaction.save()
                    else:
                        interaction.delete()
                for interaction in post_interactions:
                    if interaction.type == 'current':
                        interaction.type = 'yesterday'
                        interaction.save()
                    else:
                        interaction.delete()
                        
            return None
    class Core:
        
        # Uses the incrementing system to display only a number of posts at a time.
        def posts_per_page(list, incrementing_factor, posts):
            for i, post in enumerate(posts):
                i += 1
                print(post, i)
                if (10 * (incrementing_factor - 1)) < i < ((10 * incrementing_factor) + 1):
                    list.append(post)
            return list
        
        # Gives the catergories that are trending and only one instance of it.
        def trending_catagories(catagory_list, type):
            # Aggregate total points for each tag name
            if type == 'popular':
                categories = PostTag.objects.values().annotate(Sum('value')).order_by('-value')
                tag_names = set()  # Keep track of unique tag names
                for category in categories:
                    nown = category['name']
                    if nown not in tag_names:
                        tag_names.add(nown)
                        catagory_list.append({
                            'name': nown,
                            'value__sum': category['value__sum']
                        })
            elif type == 'recommended':
                categories = Interest.objects.values().annotate(Sum('value')).order_by('-value')
                tag_names = set()  # Keep track of unique tag names
                for category in categories:
                    nown = category['name']
                    if nown not in tag_names:
                        tag_names.add(nown)
                        catagory_list.append({
                            'name': nown,
                            'value__sum': category['value__sum']
                        })
            return catagory_list
        
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
                                post = Post.objects.get(posttag=tag)
                                order.append(post)
                    i += 1

            else:
                interest = Interest.objects.get(name=sub_catagory.removeprefix('|'), user=user)
                tags = PostTag.objects.filter(name=interest.name)
                for tag in tags:
                    post = Post.objects.get(posttag=tag)
                    order.append(post)
            return order
        
        def catch_up_sort(user):

            # Setup
            user_stats = UserStats.objects.get(user=user.pk)
            user_follower_object = Following.objects.get(subscribers=user_stats.user.username)
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
            feed = []
            relevent_posts = []
            todays_posts = Post.objects.filter(created_at=date.today())
            for post in todays_posts:
                if post.user.username in distances.keys():
                    relevent_posts.append(post)
            print(relevent_posts)
            return feed



            



