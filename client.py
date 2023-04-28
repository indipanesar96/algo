from binance.client import Client


def getClient():
    apiKey = 'izGXBPBp8CDK5m70ChlYrMJ4cqNzwMJUPLGNo39QLZc9fhLhRqwhSgJBZYFHzqWC'
    apiSecret = 'EKgvZtSW5ZBi0pHJUjEU0gJixTqZ4c9FoJ2i3oKQAX9Yl42UOsrVZya8rE4aRz3o'
    client = Client(apiKey, apiSecret)
    return client
