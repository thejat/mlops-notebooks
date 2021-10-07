# Databricks notebook source
# MAGIC %md In Cmd 2, the AWS_ACCESS_KEY and AWS_SECRET_KEY variables are set and kept hidden.

# COMMAND ----------

AWS_ACCESS_KEY = "notsecret"
AWS_SECRET_KEY = "secret"

# COMMAND ----------

sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId", AWS_ACCESS_KEY)
sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", AWS_SECRET_KEY)

# COMMAND ----------

df = spark.read.csv("s3://databricks-recsys/u.data",header=True, sep="\t",inferSchema = True)
pdf = df.toPandas()

# COMMAND ----------

!pip install scikit-surprise

# COMMAND ----------

# https://github.com/NicolasHug/Surprise
#https://github.com/NicolasHug/Surprise/blob/master/examples/top_n_recommendations.py
from surprise import SVD, Dataset, Reader
from surprise.accuracy import rmse
from collections import defaultdict

# COMMAND ----------

def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.
    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.
    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

# COMMAND ----------

# A reader is still needed but only the rating_scale param is requiered.
reader = Reader(rating_scale=(1, 5))

# The columns must correspond to user id, item id and ratings (in that order).
data = Dataset.load_from_df(pdf[['uid', 'iid', 'rating']], reader)

# COMMAND ----------

# Load the movielens-100k dataset (download it if needed).
trainset = data.build_full_trainset()

# Use an example algorithm: SVD.
algo = SVD()
algo.fit(trainset)                                                              

# COMMAND ----------

#actual predictions as thse items have not been seen by the users. there is no ground truth. 
# We predict ratings for all pairs (u, i) that are NOT in the training set.
testset = trainset.build_anti_testset()
predictions = algo.test(testset)
top_n = get_top_n(predictions, n=10)

# COMMAND ----------

from pyspark.sql.types import StringType
import json
import pandas as pd

def recommend(row):
    d = json.loads(row)
    result = {'uid':d['uid'] , 'pred': [x[0] for x in top_n[int(d['uid'])]] }
    return str(json.dumps(result))

# COMMAND ----------

df = spark.readStream.format("kafka") \
  .option("kafka.bootstrap.servers", "155.138.192.245:9092") \
  .option("subscribe", "quickstart-events") \
  .option("startingOffsets", "latest").load()
df = df.selectExpr("CAST(value AS STRING)")
recommend_udf = udf(recommend, StringType())
df = df.select(recommend_udf("value").alias("value"))

# COMMAND ----------

query = df.writeStream.format("kafka")\
  .option("kafka.bootstrap.servers", "155.138.192.245:9092")\
  .option("topic", "recommendation-events")\
  .option("checkpointLocation", "/temp").start().awaitTermination()
