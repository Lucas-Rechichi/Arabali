import os
import pandas as pd
import google.generativeai as genai

from dotenv import load_dotenv

from django.core.files.temp import NamedTemporaryFile
from main.prompts import Prompts
class Algorithum:

    class Core:
        def average(num_list, is_abs):

            total_value = 0.0
            for i in num_list:
                total_value += i 

            if is_abs:
                ave = abs( (total_value) / (len(num_list)) )
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

            media_file = genai.upload_file(media)
            response = model.generate_content([media_file, Prompts.dermine_catergory_prompt(title=title, contents=contents)])

            return response.text



