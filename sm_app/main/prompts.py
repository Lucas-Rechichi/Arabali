class Prompts:
    def dermine_catergory_prompt(title, contents, catergories_list):
        prompt = f'''
            If I made a post with the title: {title}, the post text being: {contents} and the attached 
            image as media for the post, what catergory would you put it into? 
            List only the most fitting catergory. If you think it fits inside these existing catergories: 
            {str(catergories_list)}, then assign it to that catergory please. 
            Only include the catergory name in your response.
        '''

        return prompt