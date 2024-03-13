import random
import importlib
import Database
importlib.reload(Database)

#TODO: remove duplicates anf make sure they are all good
adjectives = list(set(['happy', 'silly', 'clever', 'funny', 'smart', 'kind', 'brave', 'friendly', 'calm', 'shy',
              'curious', 'gentle', 'eager', 'honest', 'loyal', 'polite', 'generous', 'energetic', 'playful',
              'sincere', 'creative', 'cheerful', 'helpful', 'graceful', 'witty', 'determined', 'thoughtful',
              'optimistic', 'charming', 'modest', 'confident', 'mysterious', 'fierce', 'resourceful', 'patient',
              'adventurous', 'carefree', 'independent', 'radiant', 'sensitive', 'grateful', 'prudent', 'innocent',
              'persistent', 'genuine', 'sympathetic', 'dynamic', 'insightful', 'cooperative', 'harmonious',
              'adaptable', 'resilient', 'tolerant', 'enthusiastic', 'peaceful', 'loyal', 'glamorous', 'sophisticated',
              'tenacious', 'gregarious', 'tenacious', 'vibrant', 'versatile', 'exuberant', 'capable', 'frank',
              'sociable', 'diplomatic', 'spontaneous', 'astute', 'intrepid', 'intuitive', 'pragmatic', 'quirky',
              'enterprising', 'zestful', 'versatile', 'candid', 'dynamic', 'cosmopolitan', 'mellow', 'exuberant',
              'affable', 'discerning', 'nurturing', 'gregarious', 'elegant', 'adventurous', 'gregarious', 'radiant',
              'introspective', 'vivacious', 'gracious', 'boisterous', 'gregarious', 'brilliant', 'gregarious', 'vivacious',
              'silly', 'clever', 'funny', 'smart', 'kind', 'brave', 'friendly', 'calm', 'shy', 'curious',
              'gentle', 'eager', 'honest', 'loyal', 'polite', 'generous', 'energetic', 'playful', 'sincere',
              'creative', 'cheerful', 'helpful', 'graceful', 'witty', 'determined', 'thoughtful', 'optimistic',
              'charming', 'modest', 'confident', 'mysterious', 'fierce', 'resourceful', 'patient', 'adventurous',
              'carefree', 'independent', 'radiant', 'sensitive', 'grateful', 'prudent', 'innocent', 'persistent',
              'genuine', 'sympathetic', 'dynamic', 'insightful', 'cooperative', 'harmonious', 'adaptable',
              'resilient', 'tolerant', 'enthusiastic', 'peaceful', 'loyal', 'glamorous', 'sophisticated', 'tenacious',
              'gregarious', 'vibrant', 'versatile', 'exuberant', 'capable', 'frank', 'sociable', 'diplomatic',
              'spontaneous', 'astute', 'intrepid', 'intuitive', 'pragmatic', 'quirky', 'enterprising', 'zestful',
              'versatile', 'candid', 'dynamic', 'cosmopolitan', 'mellow', 'exuberant', 'affable', 'discerning',
              'nurturing', 'gregarious', 'elegant', 'adventurous', 'gregarious', 'radiant', 'introspective',
              'vivacious', 'gracious', 'boisterous', 'gregarious', 'brilliant', 'gregarious', 'vivacious',
              'impulsive', 'imaginative', 'humble', 'ambitious', 'bold', 'delightful', 'majestic', 'mysterious',
              'melodious']))

nouns = list(set(['cat', 'dog', 'bird', 'rabbit', 'turtle', 'elephant', 'lion', 'monkey', 'fish', 'penguin',
         'bear', 'tiger', 'deer', 'dolphin', 'zebra', 'giraffe', 'kangaroo', 'koala', 'hippo', 'rhino',
         'cheetah', 'fox', 'wolf', 'owl', 'eagle', 'hawk', 'sparrow', 'swan', 'peacock', 'parrot',
         'hamster', 'guinea pig', 'rat', 'mouse', 'squirrel', 'chipmunk', 'gerbil', 'hamster', 'ferret',
         'rabbit', 'frog', 'toad', 'newt', 'lizard', 'gecko', 'snake', 'turtle', 'tortoise', 'crocodile',
         'alligator', 'iguana', 'chameleon', 'salamander', 'axolotl', 'dinosaur', 'shark', 'whale', 'dolphin',
         'jellyfish', 'octopus', 'squid', 'lobster', 'crab', 'shrimp', 'clam', 'oyster', 'snail',
         'slug', 'butterfly', 'moth', 'bee', 'wasp', 'ant', 'dragonfly', 'grasshopper', 'cricket',
         'beetle', 'ladybug', 'caterpillar', 'centipede', 'millipede', 'spider', 'scorpion', 'tick',
         'flea', 'mosquito', 'fly', 'bee', 'wasp', 'ant', 'dragonfly', 'grasshopper', 'cricket',
         'beetle', 'ladybug', 'caterpillar', 'centipede', 'millipede', 'spider', 'scorpion', 'tick',
         'flea', 'mosquito', 'fly','apple', 'banana', 'orange', 'pear', 'strawberry', 'blueberry', 'raspberry', 'grape', 'pineapple', 'watermelon',
         'kiwi', 'mango', 'peach', 'plum', 'apricot', 'cherry', 'lemon', 'lime', 'coconut', 'avocado',
         'pomegranate', 'fig', 'date', 'papaya', 'melon', 'dragonfruit', 'guava', 'passionfruit', 'lychee', 'cantaloupe',
         'blackberry', 'cranberry', 'elderberry', 'boysenberry', 'tangerine', 'apricot', 'persimmon', 'honeydew', 'nectarine', 'gooseberry',
         'grapefruit', 'kumquat', 'quince', 'rutabaga', 'turnip', 'potato', 'carrot', 'beet', 'radish', 'celery',
         'cabbage', 'lettuce', 'spinach', 'kale', 'arugula', 'broccoli', 'cauliflower', 'asparagus',
         'cucumber', 'zucchini', 'eggplant', 'jalapeno', 'habanero', 'pumpkin', 'squash',
          'yam', 'corn', 'peas', 
         'chickpeas', 'lentils', 'soybeans', 
         'barley', 'oats', 'rice', 'quinoa', 'bulgur', 'millet', 'amaranth', 'buckwheat', 'wheat', 'rye']))


def generate_username(): 
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return adjective.capitalize() + noun.capitalize()






