import os
import pandas as pd
import googlegenerativeai as genai

from dotenv import load_dotenv

class Algorithum:

    class Core:
        def average(num_list, is_abs)

        total_value = 0.0
        total value += i for i in num_list

        if is_abs:
            ave = abs( (total value) / (len(num_list)) )
        else:
            ave = (total value) / (len(num_list)) 
        
        return ave


    class PostCreations:
        def predict_catergory_request(request_data)
        # Setup of the LLM used to detrmine the catergory of the post
        load_dotenv()
        google_gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

        genai.configure(api_key=google_gemini_api_key)
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')

        # Getting relevant data for the post


