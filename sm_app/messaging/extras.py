from messaging.models import ChatRoom
from main.models import UserStats
def get_chat_rooms(user):
    user_stats = UserStats.objects.get(user=user)
    chat_rooms = ChatRoom.objects.filter(users=user_stats)
    return chat_rooms