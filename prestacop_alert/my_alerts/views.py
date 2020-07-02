from django.shortcuts import render
import boto3
import time
from threading import Thread

alerts = []

aws_access_key_id="ASIAWQZQX3A3RYFRHIVL"
aws_secret_access_key="F8ny/9Zq8QPdGXQ0DNOdjzgtFrP7bB+9IvvmuMup"
aws_session_token="FwoGZXIvYXdzENP//////////wEaDN2WbyqZl15wb9gmwiK/AV7W5p9+9JlOOy95APMrISAnE9+FGGowWUeXV/C70M+Ydtsi8AO0CavkYix6coYQZ31FvR0FNjH7DNFR7wBavTs9jR0tjPLBExX3hX/Rft3sUOeW+yYJoxKuMsilXCKfbvvVZG7RV2BuhBpvKq0labrXRzapvu98XuoO/sZzmznMV7dFIM4bg4Hs0jVIYtPTEuNeacHFqPf/HZDTr/B2iSszqrMlbOLwBBbfqGsWdVYkWctQyrxOoYT5H1lzlNdFKJzX9vcFMi2cM5jyZg2VjMuoV5NwxS3O7mmcWs2rdkLW1YG2vvsN5cmROlyN1FaFDzHPXOE="

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
            alerts.append(records)

        # wait for 5 seconds
        time.sleep(5)

t1 = Thread(target = get_response, args=[record_response, kinesis_client, alerts])
t1.setDaemon(True)
t1.start()

def index(request):


    return render(request, 'index.html', {'alerts': alerts})
