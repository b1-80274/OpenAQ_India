from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException
import os
import sys
from datetime import datetime, timedelta

location_parameters = {
    67569: ['um050', 'pressure', 'humidity', 'temperature', 'um005', 'um003', 'pm1', 'um025', 'um010', 'um100', 'pm25',
            'pm10'],  # Bangalore
    288233: ["pm25", "um100", "pressure", "um010", "um025", "pm10", "um003", "humidity", "um005", "pm1", "temperature",
             "um050"],  # Kalol, Gandhi Nagar
    64931: ["um100", "um050", "um005", 'pm10', 'um025', 'pm1', 'pm25', 'um003', 'um010'],  # Bhatinda
    66673: ['um003', 'um003', 'pm10', 'um005', 'pm25', 'um010''um100''pressure', 'um050', 'um025', 'pm1', 'temperature',
            'humidity'],  # Hisar
    8118: ["pm25"],  # New Delhi
    62543: ['pressure', 'pm25', 'um010', 'humidity', 'um003', 'temperature', 'um100', 'um025', 'um050', 'um005', 'pm10',
            'pm1'],  # Greater Kailash 2
    1667903: ['um010', 'humidity', 'temperature', 'um050', 'pm1', 'um003', 'um005', 'pm25', 'pm10', 'um025', 'pressure',
              'um100'],  # 15 Oak Drive Outdoor
    362098: ['temperature', 'um050', 'pressure', 'um003', 'um005', 'humidity', 'um025', 'um100', 'um010', 'pm10', 'pm1',
             'pm25'],  # Greater Noida
    64934: ['pm10', 'um010', 'um100', 'um050', 'um005', 'pressure', 'um025', 'um003', 'temperature', 'pm1', 'humidity',
            'pm25'],  # Tarkeshwar, West Bengal
    8172: ['pm25'],  # Kolkata
    220704: ['temperature', 'um010', 'pm10', 'pm25', 'pressure', 'um025', 'humidity', 'temperature', 'um003', 'um100',
             'um050', 'um005', 'pm1'],  # Kharagpur, West Bengal
    8039: ['pm25'],  # Mumbai
    8557: ['pm25'],  # Hyderabad
    63704: ['um003', 'um025', 'pm10', 'pm1', 'humidity', 'temperature', 'um010', 'um005', 'um050', 'pm25', 'um100',
            'pressure'],  # Madikeri, Karnataka
    229138: ['um050', 'pm10', 'temperature', 'humidity', 'pm1', 'um003', 'pressure', 'um025', 'um005', 'um010', 'um100',
             'pm25'],  # Srinivaspur, Karnataka
    8558: ['pm25']  # Chennai
}

# get the execution date of the DAG
date1 = sys.argv[1]
print(f'date1 = {date1}')
date1 = date1[1:11]
date1 = datetime.strptime(date1, '%Y-%m-%d').date()
date2 = date1 + timedelta(days=1)

date1 = str(date1)[:10]
date2 = str(date2)[:10]

# hitting the api and getting the data for the dates
dy = date1[-2:]
mnt = date1[5:7]
yr = date1[:4]

# create a SparkSession
spark = SparkSession.builder.appName('read_local_data').getOrCreate()

# reading the local data
for location_id in location_parameters.keys():
    for parameter in location_parameters[location_id]:
        try:
            if os.path.exists(
                    f'/home/sad7_5407/Desktop/Data_Engineering/data/{yr}/{mnt}/{dy}/{location_id}/{parameter}.json'):
                local_data = spark.read \
                    .option('multiline', True) \
                    .json(
                    f'/home/sad7_5407/Desktop/Data_Engineering/data/{yr}/{mnt}/{dy}/{location_id}/{parameter}.json')
                print(f'>>>>>>> {yr}/{mnt}/{dy}/{location_id}/{parameter}.json read success..', end=' ')

                # selecting the required columns
                final_df = local_data.select('locationId', 'date.utc', 'parameter', 'value')

                # dropping the duplicates if any
                final_df = final_df.drop_duplicates()

                # dumping into warehouse
                final_df.write.format("orc") \
                    .mode('append').save("hdfs://localhost:9000/user/OpenAQ/data/input")
                print(f' dumped to HDFS warehouse ...')

        except AnalysisException:
            print(f'>>>>>>>>> inferSchema failed for data/{yr}/{mnt}/{dy}/{location_id}/{parameter}..')

spark.stop()
