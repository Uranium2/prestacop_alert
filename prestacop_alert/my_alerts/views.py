from django.shortcuts import render
import boto3
import time
import base64
from threading import Thread
import json

alerts = []

aws_access_key_id="ASIAWQZQX3A3ZN7PU4UE"
aws_secret_access_key="dtVUDiFmE78t76aKCGAkXFs8/M+DYKkfAKOA5ahX"
aws_session_token="FwoGZXIvYXdzEO///////////wEaDBqahmbh9zVe7+8pESK/ASd4+hwQ/50uQQqCVlP4HK59aJ0Vu9wkfFNq31TB1LJMii4XIXiHVhxlOPiTILm+y7Ir1EOY7exkv65ZGx9db7r6jUjS8hjpIss9GAkLuOnK1V/+3yr99rcyj7/q/OwXEfodI/h/k1vFhbJ7MFtles3s30Q9N/yteRQjaZa1HpFdQTN8X7jqvLwsLbOUCsllGfblU0nJ9bRJF0A94yyL7g1exRptF7lKClrH2ap3yAhphqxz1Ol+agigrz+Iu2JvKOvp/PcFMi39j/d1AcDiknPlDqdiyEhwFjRyxGaEjpT8tufqJLVf3vCeraP2C65HWoR2vnw="
my_stream_name = 'Prestacop-Kinesis-alert'

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
            if d.get('droneId') == info[0] and d.get('timestamp_drone') == int(info[1]):
                print("deleting")
                alerts.remove(d)
    return render(request, 'index.html', {'alerts': alerts})
