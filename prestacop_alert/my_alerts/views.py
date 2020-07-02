from django.shortcuts import render
import boto3
import time
import base64
from threading import Thread
import json

alerts = []

aws_access_key_id="ASIAWQZQX3A3YK7CQ2MH"
aws_secret_access_key="qYUyW0oirufbNXWd3+ewjQYEZyk8hhvf+u2oN8Pl"
aws_session_token="FwoGZXIvYXdzENT//////////wEaDLSybSPaSPWrNXhmECK/AblfKGVhT4a8CoCm4IeNJBLlYbkXNwNxXxpwUbN+tEhH+7kFXyfllPflHiU2EeJRFn84cZqrGYw91So1ykkTckfZaNjdpO1Z/Sde4MoXA+esaEM4E7w1amVCrG1UPEHXpZcRXaMpCJ4/tUW7A04H5CIgkTpskSMFS08+zHmw+JcrtMggI9+l0TZnIsKj3irs27F3nuadnFRL10rCFLEUHsZW00mjr02AHeypHEy/nlcLq73xbUb8zBvdtWA7g9yEKOb69vcFMi1TNUL5DGaqbLilKviRdOohaBiibFQLLqyE1NgGg50kuDf2LoIQyjbc2Qf5fJY="
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
                res = res[1:-2]
                res = res.split(', ')
                data = []
                for r in res:
                    data.append(r.split("=", 1))

                flat_list = []
                for sublist in data:
                    for item in sublist:
                        flat_list.append(item)

                dictionary = dict(zip(flat_list[0:][::2], flat_list[1:][::2]))
                alerts.append(dictionary)
                print(type(dictionary))

        # wait for 5 seconds
        time.sleep(5)
    kinesis_client.close()

t1 = Thread(target = get_response, args=[record_response, kinesis_client, alerts])
t1.setDaemon(True)
t1.start()

def index(request):


    return render(request, 'index.html', {'alerts': alerts})
