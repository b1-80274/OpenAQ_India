from pyspark.sql import SparkSession
from pyspark.sql.functions import year, current_date, date_format, avg, round, to_timestamp

# creating a spark session
spark = SparkSession.builder \
    .appName("build_latest") \
    .config("spark.jars", "/home/sad7_5407/mysql-connector-java-8.0.20.jar") \
    .config("spark.executor.extraClassPath", "file:///home/sad7_5407/mysql-connector-java-8.0.20.jar") \
    .config("spark.executor.extraLibrary", "file:///home/sad7_5407/mysql-connector-java-8.0.20.jar") \
    .config('spark.driver.extraClassPath', "file:///home/sad7_5407/mysql-connector-java-8.0.20.jar") \
 \
.getOrCreate()

# build the latest table
schema = "locationId INT, utc TIMESTAMP, parameter STRING, value DOUBLE"
wrh_data = spark.read \
    .option('schema', schema) \
    .orc('hdfs://localhost:9000/user/OpenAQ/data/input')

# filter for latest year only
recent_df = wrh_data.filter(year('utc') == year(current_date()))

# aggregate for hourly average value
recent_df = recent_df.withColumn('utc', date_format('utc', 'yyyy-MM-dd HH:00:00'))
hourly_df = recent_df.groupBy(['locationId', 'utc', 'parameter']) \
    .agg((avg('value')).alias('hourly_avg')) \
    .select('locationId', to_timestamp('utc').alias('utc_timestamp'), 'parameter', round('hourly_avg', 2).alias('hourly_avg_value'))\
    .drop_duplicates()

# Dump to HDFS
hourly_df.coalesce(1) \
    .write.mode('overwrite') \
    .option("header", "true") \
    .format('csv') \
    .save("hdfs://localhost:9000/user/OpenAQ/data/latest")
print('latest table HDFS dump success...')

# save to Local FS
hourly_df.coalesce(1) \
    .write.mode('overwrite') \
    .option("header", "true") \
    .format('csv') \
    .save("/home/sad7_5407/Downloads/OpenAQ")
print(f'latest table local dump success...')

# save to MySQL database
db_url = 'jdbc:mysql://localhost:3306/OpenAQ'
db_table = 'latest'
db_user = 'root'
db_password = 'manager'

hourly_df.write.format("jdbc") \
    .option("url", db_url) \
    .option("dbtable", db_table) \
    .option("user", db_user) \
    .option("password", db_password) \
    .option("driver", "com.mysql.cj.jdbc.Driver")\
    .mode("overwrite") \
    .save()


spark.stop()