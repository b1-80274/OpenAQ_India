# OpenAQ_India
Hourly average air pollutant values for Indian cities. 


## Description
This is a batch processing ETL pipeline which is aimed to give hourly average values for different air pollutants being measured at Indian cities, updated on a daily basis.  

I used data made available by [OpenAQ](https://openaq.org/) . 


## Architecture
![PipeLine Architecture](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Architecture.png)


## Development 

### 1. API
Let's start with the API first. Here is a list of helpful API documents.
- https://docs.openaq.org/docs/introduction
- https://py-openaq.readthedocs.io/en/latest/#
- https://dhhagan.github.io/py-openaq/tutorial/api.html

I tried to get started with getting the data about the Indian cities via the endpoint `cities`. As per the documentation, it supports a `**kwarg` `country` which requires a 2 character code of a country. But it didn't give any response. OpenAQ has a beautiful [explorer](https://explore.openaq.org/#3.2/26.17/80.54), a web-based dashboard. I hardcoded this data with the help of the explorer.

Instead of using the API endpoints directly, I used `requests` package along with string manipulation due to unrealiable responses from the endpoint `measurements`. 

URL providing the data - 

`https://api.openaq.org/v2/measurements?location_id=8039&parameter=pm25&date_from=2024-02-08T21:54:40+05:30&date_to=2024-02-10T21:54:40+05:30&limit=1000`

This url string is manipulated for `location_id` , `parameter`, `date_from` and `date_to` with the hardcoded values for India. 

Data available via api URL - 

```
[  
    
    {"locationId":8039,"location":"Mumbai","parameter":"pm25","value":67.0,"date":{"utc":"2024-02-10T04:30:00+00:00","local":"2024-02-10T10:00:00+05:30"},"unit":"µg/m³","coordinates":{"latitude":19.07283,"longitude":72.88261},"country":"IN","city":null,"isMobile":false,"isAnalysis":null,"entity":"Governmental Organization","sensorType":"reference grade"},

    {"locationId":8039,"location":"Mumbai","parameter":"pm25","value":90.0,"date":{"utc":"2024-02-10T03:30:00+00:00","local":"2024-02-10T09:00:00+05:30"},"unit":"µg/m³","coordinates":{"latitude":19.07283,"longitude":72.88261},"country":"IN","city":null,"isMobile":false,"isAnalysis":null,"entity":"Governmental Organization","sensorType":"reference grade"},

    ...
]
```

### Data Modelling 

Here, there are 2 dimensions - city(location) and parameter with a central dimension latest(readings). So, I used a Star schema to model the data. 

![Data Modelling - Star Schema](https://github.com/b1-80274/OpenAQ_India/blob/main/images/OpenAQ_Star_Schema.png)

### 2. PySpark ETL 

##### 2.1 HDFS Warehouse

Using PySpark dataframes, I transformed the above json to select the required fields. I dumped the dataframe to HDFS in ORC format.

##### 2.2 Latest Table

-- Add images

### 3. Airflow
-- Add images

### 4. PowerBI
-- Add images


## Business Usecases

## Possible Improvents


## Contrinutions
Huge thanks to OpenAQ for providing the API. 
