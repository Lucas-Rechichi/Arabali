import json

from django.http import JsonResponse
from main.models import Post, Media, PostTag, Category, PCF
from main.algorithum import Algorithum


def add_post(request):

    # Getting sent data
    title = request.POST.get('title')
    contents = request.POST.get('contents')
    media = request.FILES.getlist('media')
    captions = json.loads(request.POST.get('captions'))

    user = request.user

    # Creating the post and it's media
    new_post = Post(title=title, contents=contents, user=user, likes=0)
    new_post.save()

    # Creating media objects for the post (the slides of the carousel)
    for i, media_obj in enumerate(media):
        caption_text = captions[i]['text']
        caption_colour = captions[i]['colour']
        caption_font = captions[i]['font']
        new_media = Media(post=new_post, media_obj=media_obj, caption_text=caption_text, caption_colour=caption_colour, caption_font=caption_font)
        new_media.save()

    # Determining the catergory for this post using AI
    post_catergory = Algorithum.PostCreations.predict_catergory_request(post_obj=new_post)

    # Getting the average post value.
    tag_values = list(PostTag.objects.all().values_list('value', flat=True))

    # Creating the post tag
    ave_tag_value = Algorithum.Core.average(num_list=tag_values, is_abs=True)
    new_post_tag = PostTag(post=new_post, name=post_catergory, value=ave_tag_value)
    new_post_tag.save()

    new_post_function = PCF(tag=new_post_tag, factor=1, is_active=True)
    new_post_function.save()

    # Creating a new catergory instance if this is a new type of post.
    if not Category.objects.filter(name=post_catergory).exists():
        new_catergory = Category(name=post_catergory)
        new_catergory.save()

    response = {}

    return JsonResponse(response)


