# Databricks notebook source
from pyspark.sql.types import StringType
import json
import pandas as pd

def recommend(row):
    d = json.loads(row)
    result = {'uid':d['uid'] , 'pred': '' }
    return str(json.dumps(result))

# COMMAND ----------

df = spark.readStream.format("kafka") \
  .option("kafka.bootstrap.servers", "155.138.192.245:9092") \
  .option("subscribe", "quickstart-events") \
  .option("startingOffsets", "latest").load()

# COMMAND ----------

df.printSchema()

# COMMAND ----------

df = df.selectExpr("CAST(value AS STRING)")
recommend_udf = udf(recommend, StringType())
df = df.select(recommend_udf("value").alias("value"))

# COMMAND ----------

query = df.writeStream.format("kafka")\
  .option("kafka.bootstrap.servers", "155.138.192.245:9092")\
  .option("topic", "recommendation-events")\
  .option("checkpointLocation", "/temp").start().awaitTermination()
