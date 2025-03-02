from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, stddev, col
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType

spark = SparkSession.builder.appName("IoT_Processing").getOrCreate()

schema = StructType([
    StructField("sensor_id", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("timestamp", TimestampType(), True)
])

df = spark.readStream.format("kafka")\
    .option("kafka.bootstrap.servers", "kafka:9092")\
    .option("subscribe", "sensor_data")\
    .load()

sensor_data = df.selectExpr("CAST(value AS STRING)").selectExpr("from_json(value, schema) as data").select("data.*")

agg_data = sensor_data.groupBy("sensor_id").agg(
    avg("temperature").alias("avg_temp"),
    stddev("temperature").alias("std_temp"),
)

def detect_anomalies(df, epoch_id):
    df = df.withColumn("is_anomaly", col("temperature") > col("avg_temp") + 2 * col("std_temp"))
    df.write.format("console").save()

query = sensor_data.writeStream.foreachBatch(detect_anomalies).start()
query.awaitTermination()

