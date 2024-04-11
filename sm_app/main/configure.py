import os

from datetime import datetime
from main.models import User, UserStats, LikedBy, Following, Post
from django.shortcuts import render, HttpResponseRedirect
class Configure():

    # setup: geting useful databace objects.
    def edit_profile(request, current_username):
        user = User.objects.get(username=current_username)
        old_username = user.username
        user_stats = UserStats.objects.get(user=user)
        user_liked_by = LikedBy.objects.get(name=current_username)
        user_following = Following.objects.get(subscribers=current_username)
        user_posts = Post.objects.filter(user=user)
        users = User.objects.all()
        print(users)

        # Username change
        if request.POST.get('username') != current_username: # if the user has changed their username
            print('Username is being changed')
            
            # Checks
            if request.POST.get('username') == 'Images': # if the new username is Images
                issue = 'Cannot be named Images due to the default image directory being called Images.'
                print(f'error: {issue}')
                return issue
            for x in range(0, users.count()):
                if request.POST.get('username') == str(users[x]): # if the new usermane is any existing username on the app
                    issue = 'Username Taken.'
                    print(f'error: {issue}')
                    return issue
            for character in request.POST.get('username'):
                if character == ' ':
                    issue = 'Username Cannot Contain Spaces'
                    print(f'error: {issue}')
                    return issue
                
            # Changes username and important models that rely on the name being the username.
            new_username = request.POST.get('username')
            user_liked_by.name = new_username
            user_liked_by.save()
            print('Likedby Changed Sucessfully')
            user_following.subscribers = new_username
            user_following.save()
            print('Following Changed Sucessfully')

            # define the changing of the username's directory (for neatness of code)
            def change_user_directory(old_dir, new_dir):
                os.replace(old_dir, new_dir)
            
            # Changing directories
            old_dir = os.path.join('arabali_users', old_username)
            new_dir = os.path.join('arabali_users', new_username)
            print(f'New name: {new_username}')

        else:
            new_username = current_username
            print('Username remains the same')

            old_dir = os.path.join('arabali_users', old_username)
            new_dir = os.path.join('arabali_users', new_username)
            
        
            def change_user_directory(old_dir, new_dir):
                os.replace(old_dir, new_dir)
            print(f'Current name: {new_username}')

        

        # Saving relevant information from the old user_stats
        followers_instance = user_stats.followers # now the new username is used.
        following_instance = list(user_stats.following.all())

        # function that unpacks followers and adds nthem to the following of a userstats object.
        def adding_following_to_userstats(user_stats, following_instance):
            for follower in following_instance:
                user_stats.following.add(follower)
            user_stats.save()

        if request.FILES.get('profile_picture') and request.FILES.get('profile_banner'): # both changed
            print('New pfp and banner')

            print('-------------')

            # old file paths for old images
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            print('-------------')

            # new paths for new images
            new_pfp = request.FILES.get('profile_picture')
            new_banner = request.FILES.get('profile_banner')
            print(f'New pfp: {new_pfp} \nNew banner: {new_banner}')

            # if the old images are not the default ones (cannot delete default paths).
            if old_pfp_path != 'arabali_users/Images/Default_User_Images/Screenshot_2024-03-03_at_7.30.10pm.png' and old_banner_path != 'arabali_users/Images/Default_User_Images/Screenshot_2024-03-03_at_7.37.14pm_d2VufHD.png':
                # delete old image paths
                os.remove(old_pfp_path)
                print(f'Deleted file at {old_pfp_path}')

                print('-------------')

                os.remove(old_banner_path)
                print(f'Deleted file at {old_banner_path}')


                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')
            else:
                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')

            
        elif request.FILES.get('profile_picture'): # only pfp changed
            print('New pfp, old banner')

            print('-------------')

            # old file paths for old images.
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old image for resubmission to userstats.
            raw_banner_path = user_stats.banner
            raw_banner_path_string = str(raw_banner_path)
            modified_old_banner = raw_banner_path_string.replace(old_username, new_username)
            new_banner = modified_old_banner

            # getting new image. 
            new_pfp = request.FILES.get('profile_picture')

            print(f'New pfp: {new_pfp} \nCurrent banner (path modified): {new_banner}')

            print('-------------')

            # if the old images are not the default ones (cannot delete default paths).
            if old_pfp_path != 'arabali_users/Images/Default_User_Images/Screenshot_2024-03-03_at_7.30.10pm.png':
                # delete old image paths
                os.remove(old_pfp_path)
                print(f'Deleted file at {old_pfp_path}')

                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')
            else:

                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')

        elif request.FILES.get('profile_banner'): # only banner changed
            print('Old pfp, new banner')

            print('-------------')

            # old file paths for old images.
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old image for resubmission to userstats.
            raw_pfp_path = user_stats.pfp
            raw_pfp_path_string = str(raw_pfp_path)
            modified_old_pfp = raw_pfp_path_string.replace(old_username, new_username)
            new_pfp = modified_old_pfp

            # getting new image. 
            new_banner = request.FILES.get('profile_banner')

            print(f'Current pfp (path modified): {new_pfp} \nNew banner: {new_banner}')

            print('-------------')

            if old_banner_path != 'arabali_users/Images/Default_User_Images/Screenshot_2024-03-03_at_7.37.14pm_d2VufHD.png':

                # delete old image paths
                os.remove(old_banner_path)
                print(f'Deleted file at {old_banner_path}')

                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')
            else:

                # happends after the images are deleted, 
                # otherwise OS cannot find the images so that they can be deleted.
                change_user_directory(old_dir, new_dir)
                print('Directory Updated Sucessfully')

        else: # neither changed
            print('Old pfp and banner')

            # old file paths for old images
            raw_old_pfp_path = user_stats.pfp.url
            raw_old_banner_path = user_stats.banner.url
            
            old_pfp_path = raw_old_pfp_path.removeprefix('/')
            old_banner_path = raw_old_banner_path.removeprefix('/')
            print(f'Old pfp path: {old_pfp_path} \nOld banner path: {old_banner_path}')

            # preparing old images for resubmission to userstats.
            raw_banner_path = user_stats.banner
            raw_banner_path_string = str(raw_banner_path)
            modified_old_banner = raw_banner_path_string.replace(old_username, new_username)
            new_banner = modified_old_banner
            raw_pfp_path = user_stats.pfp
            raw_pfp_path_string = str(raw_pfp_path)
            modified_old_pfp = raw_pfp_path_string.replace(old_username, new_username)
            new_pfp = modified_old_pfp
            print(f'Current pfp (path modified): {new_pfp} \nCurrent banner (path modified): {new_banner}')

            # happends after the images are deleted, 
            # otherwise OS cannot find the images so that they can be deleted.
            change_user_directory(old_dir, new_dir)
            print('Directory Updated Sucessfully')

        # deletion of old userstats
        user_stats.delete()
        
        # create new userstats, modify username here due to issues with image directories
        new_user = User.objects.get(username=old_username)
        new_user.username = new_username
        new_user.save()
        new_user_stats = UserStats(user=new_user, followers=followers_instance, pfp=new_pfp, banner=new_banner)
        new_user_stats.save()
        
        print('Username Changed Sucessfully')
        
        # preparing data for new userstats
        adding_following_to_userstats(user_stats=new_user_stats, following_instance=following_instance)
        new_user_stats.save()
        return new_user
    
    def delete_post(request, post):
        image_path = post.media.url
        processed_image_path = image_path.removeprefix('/')
        os.remove(processed_image_path)
        print(f'Deleted File At: {processed_image_path}')
        post.delete()
        print('Post Deleted Successfully')
        
    def edit_post(request, post):
        if request.POST.get('title'): # If the title was changed
            post.title = request.POST.get('title')
            post.save()
            post.date_modified = datetime.now()
            post.save()
        
        if request.POST.get('content'): # If the content inside of the post was changed
            post.contents = request.POST.get('content')
            post.save()
            post.date_modified = datetime.now()
            post.save()

        if request.FILES.get('image'): # If the media was changed
            # Path Management
            old_image_path = post.media.url
            processed_image_path = old_image_path.removeprefix('/')
            
            # Keep Old Data
            preserved_user = post.user
            preserved_title = post.title
            preserved_content = post.contents
            preserved_creation_date = post.created_at
            preserved_likes = post.likes
            preserved_liked_by = list(post.liked_by.all())

            # Get new image
            new_image = request.FILES.get('image')

            # Delete old media path
            os.remove(processed_image_path)

            # Delete old post
            post.delete()

            # Create new post object
            new_post = Post(user=preserved_user, title=preserved_title, contents=preserved_content, created_at=preserved_creation_date, likes=preserved_likes, media=new_image)
            new_post.save()
            new_post.date_modified = datetime.now()
            new_post.save()
            for liked_by in preserved_liked_by:
                new_post.liked_by.add(liked_by)
            new_post.save() 



        

