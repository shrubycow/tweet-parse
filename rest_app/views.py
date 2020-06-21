from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from .models import TweetIds
from .serializers import TweetIdSerializer
import json

# Create your views here.
def id_list(request):

    if request.method == 'GET':
        isPosted = request.GET['isPosted']
        account = request.GET['account']
        count = int(request.GET['count'])
        offset = int(request.GET['offset'])
        if isPosted.lower().startswith('false'):
            is_posted = False
        elif isPosted.lower().startswith('true'):
            is_posted = True
        else:
            is_posted = None
        ids = TweetIds.objects.filter(account=account).filter(is_posted=is_posted)[offset:count+offset]
        my_list = []
        serializer = TweetIdSerializer(ids, many=True)
        for tweet_id_tuple in serializer.data:
            my_list.append(tweet_id_tuple['id'])
        for tweet_id in my_list:
            TweetIds.objects.filter(id=tweet_id).update(is_posted=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def save(request):

    if request.method == 'POST':
        json_data = json.loads(request.body)
        print(request.body)
        account = json_data['account']
        for tweet_id, likes in json_data['id_n_likes'].items():
            try:
                TweetIds.objects.create(id=tweet_id, likes=likes, account=account)
            except IntegrityError:
                pass
