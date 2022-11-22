# Duke-Energy-Usage-Tracking
A web app where you can fill in your duke credentials and view a dashboard of your energy usage.

## Introduction

Electricity is an essential service that many of us use which is essential to our survival in many senses in his modern world. In one of the discussions with our group of friends, we were wondering why our electricity bill has shot up during the winter months and were wondering vaguely hypothesising the reason to be increased heater usage in the winter months. Then one day I happened to visit the duke website to pay my bill and at that moment I noticed that Duke provided us with our hourly energy usage data in kWh on our account home page. This data can be used to make further complex Time series analysis and predict our energy usage and the bill amount for subsequent months. Building an automated pipeline to scrape this data would be the first step to achieve that. Keeping that in mind in this project I built and automated a pipeline to extract energy usage data for a Duke Energy consumer and create a Dashboard to visualize the same. 


## Methodology

Overall architecture of the pipeline is as follows- 

 ![image](https://user-images.githubusercontent.com/44323045/203209964-06e38d71-67b3-4863-a1c5-b971179d1579.png)




The first issue while setting up this pipeline that I faced was Duke does not allow to get the Energy usage data via an API. You have to manually login to the duke’s website, go to the energy usage page and download your data in XML format. 

 ![image](https://user-images.githubusercontent.com/44323045/203209978-687764bb-413d-456e-a9ea-3ba99fc67f7b.png)


Once you download the data you see that the data is not comprehensible before its cleaned. The snapshot of the data is shown below. 
 
![image](https://user-images.githubusercontent.com/44323045/203209998-78c36ceb-70ab-4c6d-85c7-cf68040b2d43.png)


The datetime in the above snapshot is in the unix datetime format and the value is the KW measurement for the 15-minute window prior to that datetime. 

So, in order to get the users energy usage data automatically I built a web bot using Selenium which logs in to the duke website using the user’s credential, goes to the desired web page for downloading data and clicks download. 

For this purpose, we need to get user’s Duke credentials and for that purpose I built a Flask web app which asks for user credentials. Link to the website- http://dukeenergyusage.pythonanywhere.com/ 

This is a simple Flask App that I hosted freely on https://www.pythonanywhere.com/ 
Python Anywhere is a platform where one can simply develop and host your website or any other code directly from your browser without having to install software or manage your own server. We can simply host our code on this platform quickly and they provide free web app hosting for one app per account. 

Once the user enters their credentials on this platform it is inserted into Google Big Query Table.  Once the credentials data is in Big Query table the next steps will be handled by Google Composer and Airflow. Google composer is a fully managed workflow orchestration service built on Apache Airflow. It is used to author, schedule and monitor pipelines. Apache Airflow is an open-source workflow management platform for building data engineering pipelines.

Inside Google Composer Environment, I hosted a Dag script which triggers the web bot every day at 1 25 AM EST. The web bot read all the credential from the Big Query credentials table and logs in to each users Duke account using the UserID and Password. It then makes the appropriate clicks and Downloads the XML formatted energy usage data for that user. Then a function to parse the XML file into a dataframe is triggered. Post parsing the data contains the following attributes- Date Time, Value, Account. Such downloading and parsing of data is done for each user that have their credentials stored in the credentials table and then its inserted into Big Query Table. 

In the parsing step from XML to Data frame the following transformation takes place- converting datetime from Unix format to YYYY-DD-MM T HH:MM and Adding account name to the dataframe. Once the XML data is parsed for all users, we insert it into the Big Query Table. 

This data that resides in Big Query table is the source for the dashboard visualization that is done in the Google Data Studio. The DAG runs once a day and refreshes the data with the most up to date usage for the user and the Google Data Studio Visualization refreshes every 12 hours to keep the dashboard updated.


## Results

The below snapshot shows the Flask App (http://dukeenergyusage.pythonanywhere.com/) designed to get the users credentials for Duke website. 

 ![image](https://user-images.githubusercontent.com/44323045/203210039-a69b481c-697c-47bf-b307-580a1953bdfb.png)


Once the user fills the credentials in the web app the data is populated in the credentials table in Big Query as shown below.
![image](https://user-images.githubusercontent.com/44323045/203210047-0c0901fb-2873-4e0f-8143-2d1009c2b384.png)

 
Airflow DAG from Airflow UI-
![image](https://user-images.githubusercontent.com/44323045/203210059-a4b1888c-c545-413c-9242-64e9cd5e9755.png)

 
The DAG runs on a daily basis at 1 25 AM and populates the below Big Query table with new data for each account.
 
![image](https://user-images.githubusercontent.com/44323045/203210078-e63c95e8-888e-4234-b978-97196eb4100d.png)

 


Below shown is the Dashboard that is generated from the above data. This dashboard shows a line graph of each account’s energy usage with respect to time. This is useful to compare the energy usage patterns of different users. Link to Dashboard - Link

 ![image](https://user-images.githubusercontent.com/44323045/203210108-f71a64da-5df4-47fa-b8dc-c01eebd316fb.png)


We can also filter the Dashboard according to account and Date Range-

 ![image](https://user-images.githubusercontent.com/44323045/203210124-ab40faf5-bb53-4833-a81c-16241d8f4e10.png)



Result Links- 
1.	GitHub link- https://github.com/maddy3940/Duke-Energy-Usage-Tracking
2.	Flask Web App Link- http://dukeenergyusage.pythonanywhere.com/
3.	Dashboard link- Link 
