**Welcome To Arabali**

Arabali is a Django powered social media application. It has basic features and is only available locally.
Feel free to see the code and test it for yourself. I would love any feedback you may have.


The creation of Arabali has been documented on YouTube.
Link to my YouTube channel: https://www.youtube.com/channel/UCPuNpdzS9GEJxLWwu2kB2jA

**Testing Instructions**

If you wish to test the functionality of Arabali, here are the prerequisite things that you need to have in order to get Arabali up and running on your local machine.

1. Installing Necessary Packages

Here are the packages that are required:
- Django

```pip install django```

- django-crispy-forms

```pip install django-crispy-forms```

2. Adding in the root image directory, and it's corresponding nested directories.

The name of the root image directory is `arabali_users`. Create a directory with that name. Once that is complete, you want to add in a other directory inside of arabali_users called `Images`. Within that directory, another folder also needs to be created called `Default_User_Images`. 

If you wish to change any of these folder or file names or reorder their path, code within Arabali will need to be changed so that the app works as expected. 

3. Default user images

Inside of our newly created directory called Default_User_Images, add in these files. Due to these files being image files, you will need to save them onto your computer 
by right clicking on the image and saving it that way. 

- Default user profile picture, for reference, this image is 306 X 306 pixels. Save this image as Default_Profile_Picture.png

![Default_Profile_Picture](https://github.com/Lucas-Rechichi/Arabali/assets/157940317/c347a2f3-0ad2-48fb-9b74-1dfbf94766ac)

- Default banner image, for reference, this image is 2106 X 494 pixels. Save this image as Default_Banner_Image.png

![Default_Banner_Image](https://github.com/Lucas-Rechichi/Arabali/assets/157940317/e6e7348a-ee75-439f-ad95-acdb13b252ef)

4. Database Migrations
The way in which you do these commands depends on what machine that you are running. These instructions assume that you know what machine you are using.

Inside of your terminal, make sure you are inside the sm_app directory. Then run these commands:

```python manage.py makemigrations```

or

```python3 manage.py makemigrations```

Afterwards, run these commands:

```python manage.py migrate```

or

```python3 manage.py migrate```

5. Testing

Now that the setup is done, you can now test the application. To run the server, inside the terminal, with the same directory used in step 4, input this command:

```python manage.py runserver```

or

```python3 manage.py runserver```

Then go to your browser and put in the URL given. 

Note that the URL on its own doesn’t have a relevant view. To see the URLs used, access the urls.py files inside of the app directories (validate, main).
