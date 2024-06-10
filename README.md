# OpenAQ_India
Hourly average air pollutant values for Indian cities. 


## Description
This is a batch processing ETL pipeline which is aimed to give hourly average values for different air pollutants being measured at Indian cities, updated on a daily basis.  
Data used is made available by [OpenAQ](https://openaq.org/) . 


## Architecture
![PipeLine Architecture](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Architecture.png)


## Development 

### 1. API
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

### Data Modelling 
There are 3 tables, `city` and `parameter` are 2 dimension tables connected to a central facts table `readings`, forming a star schema model.

![Data Modelling - Star Schema](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Star_Schema.png)

### 2. PySpark ETL 

##### 2.1 HDFS Warehouse
As the data will come in json, it will be transformed using PySpark to create a dataframe; which will be inserted in the central fact table `readings`. As the values for `locationId` and `parameter` are hard-coded in a dictionary, the 2 fact tables will never be updated for the new values. Hence, they are not touched in the process.


##### 2.2 Latest Table

-- Add images

### 3. Airflow
-- Add images

### 4. PowerBI
-- Add images


## Business Usecases
- Power BI dashboard can be used to monitor the parameters. This can help to discover recent trends, take data driven decisions and many other data analysis tasks.
- Warehouse built in the HDFS can accomodate huge amount of data which can be consumed by the data science team to built ML models on it.

## Possible Improvents
- The code used for fetching the data from the API is string manipulation using `location_id`s and `parameter`s lists. Better approach is to use [pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28).
- The `location_id`s and `parameter`s have been hard-coded, but they can be dynamically fetched from the endpoint.
- The local file system structure used for temperorily storing the data is a bit nested and unnecessary. 
- The pipeline only uses Indian cities data, but OpenAQ has data for the whole world.
- Spark has been configured in the runtime (for JDBC connectivity). It can be pre-configured by putting the required JDBC connector jar file in the jars directory of Pyspark.
 

## Contributions
Huge thanks to OpenAQ for providing the API. 
