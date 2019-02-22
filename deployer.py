import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print ("[x] Received %r" % body)
    print (" [x] Done")

channel.basic_consume(callback, queue='hello', no_ack=True)
print ('listening')
channel.start_consuming()




