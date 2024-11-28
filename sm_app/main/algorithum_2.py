import os
import google.generativeai as genai

from dotenv import load_dotenv

from main.prompts import Prompts
from main.models import Catergory, PostTag
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

            title = post_obj.title
            contents = post_obj.contents
            media = post_obj.media.all()[0].media_obj.url.removeprefix('/')

            # Getting the current tags
            current_catergories = Catergory.objects.all()

            media_file = genai.upload_file(media)
            response = model.generate_content([media_file, Prompts.dermine_catergory_prompt(title=title, contents=contents, catergories_list=current_catergories)])

            return response.text
        

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
            average_post_tag_value = Algorithum.Core.average(num_list=post_tag_values_list, is_abs=False) # ABS dosen't mattter here due to all tags always being positive

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
                    new_tag_value = current_tag_value - average_post_tag_value

                else:
                    new_tag_value = current_tag_value + (average_post_tag_value * function_result)
                
                new_function_factor = (current_tag_value/new_tag_value)

                # Recording updates to the database
                post_tag_obj.value = new_tag_value
                post_tag_obj.save()

                function_obj.factor = new_function_factor
                function_obj.save()



            

            










