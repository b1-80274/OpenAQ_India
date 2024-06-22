# OpenAQ_India
Hourly average air pollutant values for Indian cities. 


## Description
This is a batch processing ETL pipeline which is aimed to give hourly average values for different air pollutants being measured at Indian cities, updated on a daily basis.  
Data used is made available by [OpenAQ](https://openaq.org/) . 


## Architecture
![PipeLine Architecture](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Architecture.png)

Python is used to get the data from API and store it to the local file system. The data then will be transformed using Apache PySpark to build data warehouse maintained using Hadoop HDFS. A small recent subset of warehouse will be put in MySQL database to be consumed by PowerBI. Except for PowerBI, the whole process will be automated using Apache Airflow.


## Development 

### 1. API and Staging Area
Here is a list of helpful API documents for reference.
- https://docs.openaq.org/docs/introduction
- https://py-openaq.readthedocs.io/en/latest/#
- https://dhhagan.github.io/py-openaq/tutorial/api.html


URL providing the data - 

`https://api.openaq.org/v2/measurements?location_id=8039&parameter=pm25&date_from=2024-02-08T21:54:40+05:30&date_to=2024-02-10T21:54:40+05:30&limit=1000`

This url string is manipulated for `location_id` , `parameter`, `date_from` and `date_to` with the hardcoded values for India. 

Data sample from the data available via api URL - 

```
[  
    
    {"locationId":8039,"location":"Mumbai","parameter":"pm25","value":67.0,"date":{"utc":"2024-02-10T04:30:00+00:00","local":"2024-02-10T10:00:00+05:30"},"unit":"µg/m³","coordinates":{"latitude":19.07283,"longitude":72.88261},"country":"IN","city":null,"isMobile":false,"isAnalysis":null,"entity":"Governmental Organization","sensorType":"reference grade"},

    {"locationId":8039,"location":"Mumbai","parameter":"pm25","value":90.0,"date":{"utc":"2024-02-10T03:30:00+00:00","local":"2024-02-10T09:00:00+05:30"},"unit":"µg/m³","coordinates":{"latitude":19.07283,"longitude":72.88261},"country":"IN","city":null,"isMobile":false,"isAnalysis":null,"entity":"Governmental Organization","sensorType":"reference grade"},

    ...
]
```

Function `save_date()` hits the URL and saves json response in the local file system. It also handles the errors like hit limit error (429), bad request (400),etc.

### Data Modelling 
By normalising the json data,3 tables can be created.`city` and `parameter` are 2 dimension tables that needs to be connected to a central facts table `readings`, forming a star schema model.

![Data Modelling - Star Schema](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Star_Schema.png)

### 2. PySpark ETL 

##### 2.1 HDFS Warehouse
As the data comes in json, using `OpenAQ_extract_transform` script it will be transformed using PySpark to create a dataframe; which will be inserted in the central fact table `readings`. As the values for `locationId` and `parameter` are hard-coded in a dictionary, the 2 dimension tables will never be updated for the new values. Hence, they are not touched in the process.


##### 2.2 Latest Table
The rate of insertion of records is different for different stations; for example, the stations with `entity` 'Governmental Organization' insert data each hour, while some 'Community Organization' stations insert them at as low as at every 2 minutes.So, to make analysis easier, the data is aggregated to hourly values taking mean of all the values for an hour.

As data will be inserted into the warehouse, it will grow over the time and at some point if this is used for Buissness Intelligence softwares, they can slow down or fail to fetch the data. Hence, a small subset of the warehouse data, specifically latest year data is taken from warehouse and saved to a RDBMS.
`OpenAQ_build_latest` script reads the `readings` from the warehouse, filters for only latest year readings and writes them to MySQL database table in the overwrite mode.

##### 2.3 Delete Local Data
The staging data can be deleted using bash script as it is no longer needed.


##### 2.4 Wait for SafeMode
As scripts perform writes to HDFS, it is important to ensure that it has come out of the safe mode. A bashscript is implemented with HDFS admin command and a while loop to check HDFS safemode status and sleep for 10 seconds if HDFS is in the safemode.


### 3. Airflow
Apache Airflow is used to schedule the whole ETL process. The pipeline is planned to be executed daily, with the **max_active_runs** set to 1, as to avoid API hit limit issues. **catchup** is set to true to overcome local system failure or any other problems of similar sort that might prevent the DAG execution for a particular day.

`dag_run.execution_date` is used to extract the date of the running DAG dynamically. This is an important parameter and used for API hits.

![AirFlow DAG Run](https://github.com/b1-80274/OpenAQ_India/blob/main/images/airflow_openaq_dagrun.png)

### 4. PowerBI
![Power BI Dashboard](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Dashboard.png)


## Business Usecases
- Power BI dashboard can be used to monitor the parameters. This can help to discover recent trends, take data driven decisions and many other data analysis tasks.
- Warehouse built in the HDFS can accomodate huge amount of data which can be consumed by the data science team to built ML models on it.

## Possible Improvents
- The code used for fetching the data from the API is string manipulation using `location_id`s and `parameter`s lists. Better approach is to use [pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28).
- Partitioning and bucketing can be implemented for the warehouse data in HDFS to provide more optimised storage functionalities.
- The `location_id`s and `parameter`s have been hard-coded, but they can be dynamically fetched from the endpoint.
- The local file system structure used for temperorily storing the data is a bit nested and unnecessary. 
- The pipeline only uses Indian cities data, but OpenAQ has data for the whole world.
- Spark has been configured in the runtime (for JDBC connectivity). It can be pre-configured by putting the required JDBC connector jar file in the jars directory of Pyspark.
 

## Contributions
Huge thanks to [OpenAQ](https://openaq.org/) for providing the API. 
