from rest_app.models import TweetIds

ids = []
likes = []

with open('21jqofa_tweets.txt', 'r') as file:
    for string in file:
        id_and_like = string.split(' ')
        ids.append(id_and_like[0])
        likes.append(id_and_like[1])

for i in range(len(ids)):        
    TweetIds.objects.create(id=ids[i], likes=likes[i], account='21jqofa')
    
ids = []
likes = []

with open('kotalkin_tweets.txt', 'r') as file:
    for string in file:
        id_and_like = string.split(' ')
        ids.append(id_and_like[0])
        likes.append(id_and_like[1])

for i in range(len(ids)):        
    TweetIds.objects.create(id=ids[i], likes=likes[i], account='kotalkin')


