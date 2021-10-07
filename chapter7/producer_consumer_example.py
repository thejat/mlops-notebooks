#!/usr/bin/env python
# coding: utf-8

# In[1]:


from kafka import KafkaProducer
from json import dumps
import time
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
          value_serializer=lambda x: dumps(x).encode('utf-8'))


# In[3]:


data = ['Hello from python', 'Theja from python']
producer.send('quickstart-events', data)


# In[12]:


from kafka import KafkaConsumer
from json import loads
consumer = KafkaConsumer('quickstart-events',
     bootstrap_servers=['localhost:9092'],
     value_deserializer=lambda x: loads(x.decode('utf-8')))


# In[ ]:


for x in consumer:
    print(x.value)

