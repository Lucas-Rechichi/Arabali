from messaging.models import ChatRoom
from main.models import UserStats
def get_chat_rooms(user):
    user_stats = UserStats.objects.get(user=user)
    chat_rooms = ChatRoom.objects.filter(users=user_stats)
    return chat_rooms

def replace_spaces_with_underscores(string):
    string_list = [char for char in string]
    for index, char in enumerate(string_list):
        if char == ' ':
            string_list[index] = '_'
    new_string = ''
    for chars in string_list:
        new_string = new_string + chars

    return new_string
