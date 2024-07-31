import os

from messaging.models import ChatRoom
from main.models import UserStats

def get_chat_rooms(user):
    user_stats = UserStats.objects.get(user=user)
    chat_rooms = ChatRoom.objects.filter(users=user_stats)
    return chat_rooms


def replace_spaces(string, replacement):
    string_list = [char for char in string]
    for index, char in enumerate(string_list):
        if char == ' ':
            string_list[index] = str(replacement)
    new_string = ''
    for chars in string_list:
        new_string = new_string + chars

    return new_string

# define the changing of the username's directory (for neatness of code)
def change_user_directory(old_dir, new_dir):
    os.replace(old_dir, new_dir)
