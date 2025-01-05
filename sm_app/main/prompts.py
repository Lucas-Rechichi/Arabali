class Prompts:
    def dermine_catergory_prompt(title, contents, catergories_list):
        prompt = f'''
            Here is the post title: {title}, the post text being: {contents}. With the media for this 
            post evaluated, what catergory would you classify this post with? 
            List only the most fitting catergory. If you think it fits inside these existing catergories: 
            {str(catergories_list)}, then assign it to that catergory please. 
            Only include the catergory name in your response, and have the the category name be in 
            all lowercase.
        '''

        return prompt
    
    def store_media_data(media_url, caption_list, index):

        caption_text = caption_list['text']
        caption_colour = caption_list['colour']
        caption_font = caption_list['font']

        prompt = f'''
            Here is image {index + 1} of the post. The media URL is: {media_url}. The media's caption 
            has the text: {caption_text}, with the text colour being in HEX format: {caption_colour},
            and the font of the text being {caption_font}. Keep this media file in mind for when it comes 
            to evaluating the catergory that this post should go into. 
        '''

        return prompt