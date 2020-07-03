from django.shortcuts import render
import boto3
import time
import base64
from threading import Thread
import json

alerts = []

aws_access_key_id="ASIAWQZQX3A3YRJHRU6L"
aws_secret_access_key="+7tDoDFFrOU3YWThFlDBD5hGhJV88C39TbhDctlP"
aws_session_token="FwoGZXIvYXdzEOr//////////wEaDBWm2MXfJFzh5m+XpyK/AW2xDiTcdSxPUMeqW4dYeuK1h7My3+T/R4w5fpgCRiros0AHA2K5VbQ3wJ7G7/rHSih7XbwH//Z7H9a2OGGz7k3M9Ka42w/aFOoKaplbd17VwhJB0Xs9XJkqrCQTQPIJKYw7poTO4LffJLrIvhAb7/P6inJXfzqe0WHQDoQNT5WjA9BiphChIzTVoRG7ELqHEMWBcESj73l/8KF/zzh8s3HbmevosXHR7b9R4w0mgh9M4MVhjV59VRcgbcGYa2prKIrh+/cFMi3ZAV5UZOLz6/UzHjkojUHeHmvpKL5d9gNXwxfsQiaJxGoWV8e5/vbJyoXo7lk="
my_stream_name = 'message-prestacop'

kinesis_client = boto3.client('kinesis',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
    region_name='us-east-1')

response = kinesis_client.describe_stream(StreamName=my_stream_name)

my_shard_id = response['StreamDescription']['Shards'][0]['ShardId']

shard_iterator = kinesis_client.get_shard_iterator(StreamName=my_stream_name,
                                                      ShardId=my_shard_id,
                                                      ShardIteratorType='LATEST')

my_shard_iterator = shard_iterator['ShardIterator']

record_response = kinesis_client.get_records(ShardIterator=my_shard_iterator,
                                              Limit=2)
def get_response(record_response, kinesis_client, alerts):
    while 'NextShardIterator' in record_response:
        record_response = kinesis_client.get_records(ShardIterator=record_response['NextShardIterator'],
                                                    Limit=2)

        records = record_response.get('Records')
        if records == []:
            print("Empty Records")

        else:
            for record in records:
                res = json.loads(record['Data'])
                # res = res[1:-2]
                # res = res.split(', ')
                # data = []
                # for r in res:
                #     data.append(r.split("=", 1))

                # flat_list = []
                # for sublist in data:
                #     for item in sublist:
                #         flat_list.append(item)

                # dictionary = dict(zip(flat_list[0:][::2], flat_list[1:][::2]))
                alerts.append(res)
                print(type(res))

        # wait for 5 seconds
        time.sleep(5)
    kinesis_client.close()

t1 = Thread(target = get_response, args=[record_response, kinesis_client, alerts])
t1.setDaemon(True)
t1.start()

def index(request):
    if request.method == 'POST':
        l = list(request.POST.dict().keys())
        info = l[-1].split("_")
        print(info)
        for d in alerts:
            print(d)
            if d.get('droneId') == info[0] and d.get('timestamp') == int(info[1]):
                print("deleting")
                alerts.remove(d)
    return render(request, 'index.html', {'alerts': alerts})
