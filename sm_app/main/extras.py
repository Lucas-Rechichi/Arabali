import math
from django.db.models import Sum
from main.forms import Search
from main.models import ICF, PCF, PostTag, Interest, User, Notification, UserStats

def capitalize_plus(string):
    # Dictionary of all 26 English letters and their uppercase counterparts
    lower_to_upper = {
        'a': 'A',
        'b': 'B',
        'c': 'C',
        'd': 'D',
        'e': 'E',
        'f': 'F',
        'g': 'G',
        'h': 'H',
        'i': 'I',
        'j': 'J',
        'k': 'K',
        'l': 'L',
        'm': 'M',
        'n': 'N',
        'o': 'O',
        'p': 'P',
        'q': 'Q',
        'r': 'R',
        's': 'S',
        't': 'T',
        'u': 'U',
        'v': 'V',
        'w': 'W',
        'x': 'X',
        'y': 'Y',
        'z': 'Z',
        'A': 'A',
        'B': 'B',
        'C': 'C',
        'D': 'D',
        'E': 'E',
        'F': 'F',
        'G': 'G',
        'H': 'H',
        'I': 'I',
        'J': 'J',
        'K': 'K',
        'L': 'L',
        'M': 'M',
        'N': 'N',
        'O': 'O',
        'P': 'P',
        'Q': 'Q',
        'R': 'R',
        'S': 'S',
        'T': 'T',
        'U': 'U',
        'V': 'V',
        'W': 'W',
        'X': 'X',
        'Y': 'Y',
        'Z': 'Z'
    }
    # Rebuild the string, giving capitals where they need to be.
    new_string = ''
    caps_to_char = False
    for num, char in enumerate(string):
        if num == 0:
            char = lower_to_upper[char]
        if caps_to_char:
            char = lower_to_upper[char]
        if char == ' ':
            caps_to_char = True
        else:
            caps_to_char = False
        new_string += char
    return new_string

def initialize_page(request):
    if request.method == 'POST':
        search_bar = Search(request.POST)
    else:
        search_bar = Search()
    notifications = Notification.objects.filter(user=UserStats.objects.get(user=request.user)).annotate(Sum('id')).order_by('-id')
    list_of_notifications = {}
    o = 1
    for notification in notifications:
        list_of_notifications[o] = {
            'notification_object': notification,
            'sender_pfp_url': UserStats.objects.get(user=User.objects.get(username=notification.sender)).pfp.url
        }
        o += 1
    data = {
        'username' : request.user.username,
        'search_bar' : search_bar,
        'notification_list': list_of_notifications,
        'notification_count': o - 1
    }
    return data

# For removing string
def remove_until_character(string, target_char):
    string = str(string) 
    index = string.find(target_char)
    if index != -1:
        return string[index:]
    else:
        return string
    
# Removes last character of a string (for exact solutions)
def remove_last_character(string):
    return string[:len(string)-1]

# Gets the reciprocal of a number, and gives 2 for the number 0
def modified_reciprocal(num):
    if num == 0:
        reciprocal = 2
    else:
        reciprocal = 1 / num
    return reciprocal

# Finds the positive difference between two numbers
def difference(num1, num2):
    diff = abs(num1 - num2)
    return diff

# Both functions modify exact and approx values respectively to then be able to show a match percent.
def exact_display(value):
    value = value * 100
    value = round(value)
    return value

def approx_display(value, highest_q_value):
    value = value / highest_q_value
    value = value * 100
    value = round(value)
    return value
    
def algorithm_function(x, tag, interest, type): # Commented print methods are used for debugging and seeing the algorithum in use.
    # Params
    if type == 'posttag':
        parameters = PCF.objects.get(tag=tag)
        # print('Using PCF')
    else:
        parameters = ICF.objects.get(interest=interest)
        # print('Using ICF')

    a = parameters.a
    k = parameters.k

    # Log retrieved parameters
    # print(f"Retrieved function parameters: a={a}, k={k}")

    # Function
    if -((((math.sqrt(50-(a*k))) + (math.sqrt((a*k) + 50)))*(math.sqrt(2)))/(2*(math.sqrt(a*k)))) <= x <= ((((math.sqrt(50-(a*k))) + (math.sqrt((a*k) + 50)))*(math.sqrt(2)))/(2*(math.sqrt(a*k)))):
        result = k * a * (x**2)
    else:
        result = -((k*a)/(x**2)) + 100

    if result == 0:
        result = -10
    new_k = float(1 / abs(result)) if float(1 / abs(result)) <= 50.0 else 50.0

    # Log new k value
    # print(f"Calculated new k value: {new_k}")

    parameters.k = new_k
    parameters.save()

    # Log saved k value
    # print(f"Updated and saved k value: {parameters.k}")

    return result

# Haversine distance, returns it in meters (m)
def haversine_distance(lat1, lat2, lon1, lon2): 
    # Setup
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula broken down
    R = 6371000 # 6.371x10^6 m, radius of earth
    a = math.sin(delta_lat/2) ** 2
    b = math.sin(delta_lon/2) ** 2
    c = b * math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
    distance = 2 * math.asin(math.sqrt(a + c)) * R

    return distance