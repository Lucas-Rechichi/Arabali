import os
import pandas as pd
import google.generativeai as genai

from dotenv import load_dotenv

from main.prompts import Prompts
from main.models import Catergory
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


    class PostCreations:
        def predict_catergory_request(post):
            
            # Setup of the LLM used to detrmine the catergory of the post
            load_dotenv()
            google_gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

            genai.configure(api_key=google_gemini_api_key)
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')

            title = post.title
            contents = post.contents
            media = post.media.all()[0].media_obj.url.removeprefix('/')

            # Getting the current tags
            current_catergories = Catergory.objects.all()

            media_file = genai.upload_file(media)
            response = model.generate_content([media_file, Prompts.dermine_catergory_prompt(title=title, contents=contents, catergories_list=current_catergories)])

            return response.text



