# from xmlrpc import client

from fastapi import FastAPI,Depends #create api
# import pymongo #connect to mongodb
# from pymongo.server_api import ServerApi

# import uvicorn #run the api
# from pydantic import BaseModel,Field
# from datetime import date,time,datetime,timedelta
# import json
# from bson import json_util
# from fastapi.middleware.cors import CORSMiddleware
# import pandas as pd
# import requests
# import joblib
# from pathlib import Path
# from fastapi import FastAPI

app = FastAPI()

from fastapi import FastAPI

app = FastAPI()


@app.get("/api")
async def root():
    return {
        "message": "Smart Irrigation API is running"
    }


@app.get("/api/test")
async def test():
    return {
        "message": "FastAPI is working on Vercel"
    }
# This api will received data from arduino esp8266 and store data in mongo db

# url for the arduino esp8266 API endpoint
# client.py
# import requests

# url_esp8266 = "http://192.168.8.13:80/test"  # Replace with your FastAPI server URL

# #Instance of fastapi app
# app = FastAPI()

# class DataModel():
#     def connect_db():
#         try:
#             #Connect to mongo db client
#             myclient = pymongo.MongoClient("mongodb://localhost:27017/")

#             #get list of databses 
#             dblist = myclient.list_database_names()

#             #check if data
#             if "API" in dblist:

#                 mydb = myclient["API"]
#                 mycol = mydb["sensor_data"]
#             else:
#                 mydb = myclient["API"]
#                 mycol = mydb["sensor_data"]
#                 mycol.insert_one({'name': 'Example Sesnor','value':0,"timestamp":"NA"})
            
#             return mycol
#         except TimeoutError as e :
#             print(e)

# #Create a model for thr sensor data to received
# class Sensor_data(BaseModel):
#     name:str
#     temperature:float
#     humidity:float
#     moisture:float
#     moisture_p:float
#     status_moisture:str | None = None,
#     component1:int
#     datestamp:date
#     timestamp: time

# #Create a model for the filter values that will be passed on ;tHE DEAFULT 
# class Filter_value(BaseModel):
#     start_datestamp:date=Field(default=(datetime.now().date()))
#     end_datestamp:date=Field(default=(datetime.now().date()))
#     timestamp:time=Field(default=(datetime.now().time()))
#     frequency: int=Field(default=0)

# #Create data model for validating live feed data         
# class Live_feed(BaseModel):
#     latest_data:str

# class Switch_Value(BaseModel):
#      auto:bool=Field(default=False)
#      number:int =Field(default=0)

# # Load the trained model once when this module is imported


# BASE_DIR = Path(__file__).resolve().parent

# MODEL_PATH = BASE_DIR / "soil_watering_model.pkl"

# model = joblib.load(MODEL_PATH)


# def predict_watering_time(
#     temperature: float,
#     humidity: float,
#     moisture: float,
#     moisture_p: float
# ) -> float:

#     input_data = pd.DataFrame([{
#         "temperature": temperature,
#         "humidity": humidity,
#         "moisture": moisture,
#         "moisture_p": moisture_p
#     }])

#     prediction = model.predict(input_data)[0]

#     return round(float(prediction), 2)

# # Use the port that is on the front end_if you dont use you will have a CORS error
# origins = [
#     "http://localhost:5173"

# ]


# # Set up our CORS _Cross-Origin Resource Sharing(CORS) provides unauthorized webistes ,endpoints,or
# # servers from accessing your API

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# #post the data from arduino esp8266 API all the data in database
# @app.post('/svc/api/')

# async def  post_data(sensor_data:Sensor_data, connect_status: object=Depends(DataModel.connect_db)):
#         print(connect_status)
#         #Change date key to string to insert in mongodb
#         date_str = sensor_data.datestamp.strftime("%Y-%m-%d %H:%M:%S")
#         time_str = sensor_data.timestamp.strftime("%H:%M:%S")
       
#         try:
           
#             connect_status.insert_one({'name': sensor_data.name,
#                                        'temperature':sensor_data.temperature,
#                                        'humidty':sensor_data.humidity,
#                                        'moisture':sensor_data.moisture,
#                                        'moisture_p':sensor_data.moisture_p,
#                                        'status_moisture':sensor_data.status_moisture,
#                                        'component1':sensor_data.component1,
#                                        'datestamp':date_str,
#                                        'timestamp':time_str})
           
#             return{"message":"data posted successfuly"}
#         except TypeError as e:
#             return{"message":"Check console for error"}

# #Get all the data from the collection from database
# @app.get('/svc/api/')

# async def  get_data(connect_status: object=Depends(DataModel.connect_db)):
#         try:
           
#            # Query the database to retrieve all data
            
#             sd = connect_status.find({})
#             json_string = json_util.dumps(sd)
            
#             return json_string
#         except TypeError as e:
#             return{"message":"Check console for error"}
        
# #Eendpoint to filter the temretarics toggles for sensors data
# # Get all the data based on filter   
# @app.post('/svc/api/agg')
# async def get_agg_data(filter_value:Filter_value,connect_status:object=Depends(DataModel.connect_db)):
#         try:
#           print(filter_value)
#           sd = connect_status.find({})
#           unf_data =pd.DataFrame(sd)
          
#           unf_data['datestamp']= pd.to_datetime(unf_data['datestamp'])
#           filter_df = unf_data[unf_data['datestamp'].dt.strftime('%Y-%m-%d').between(str(filter_value.start_datestamp), str(filter_value.end_datestamp))]
          
#           if filter_df.empty:
#               filter_df=""
#               filter_df = {"message":"No data to retrieve"}
#           else:
             
#                # Select only integer columns
#                float_cols_df= filter_df.select_dtypes(include='float64')
#                num_df =float_cols_df.mean()
#                filter_df = num_df


               
#           return filter_df
          
#         except TypeError as e:
#           return{"message":"Check consolde for error"}
        
# #Check if the is latest to data for live feed
# @app.get('/svc/api/livefeed/')
# async def get_live_feed(connect_status:object=Depends(DataModel.connect_db)):
            

#             sd = connect_status.find({})
#             unf_data =pd.DataFrame(sd)
#             # print(unf_data)
          
#             unf_data['datestamp']=pd.to_datetime(unf_data['datestamp'])
#             time_30_seconds_ago = datetime.now()- timedelta(seconds=30)

        
#             # print(unf_data)

#             # Filter for current days data
           
#             unf_data = unf_data[(unf_data['datestamp']==datetime.now().strftime("%Y-%m-%d"))]
          

        
#             # filter_df = unf_data[(unf_data['timestamp'] >=time_30_seconds_ago.time().strftime("%H:%M:%S") & unf_data['timestamp'] < datetime.now().time().strftime("%H:%M:%S"))]
#             unf_data['timestamp']=pd.to_datetime(unf_data['timestamp'],format="%H:%M:%S")
#             #print filtered data
#             # print(f"printing filtered data :/n{filter_df}")
#             filter_df = unf_data.set_index('timestamp')

#             # Filter for data between 9 AM and 12 PM
           
#             filter_df = filter_df.between_time(time_30_seconds_ago.time().strftime("%H:%M:%S"), datetime.now().time().strftime("%H:%M:%S"))
#            # Convert time objects to string before JSON serialization
#             filter_df= filter_df.tail(1)
           
#             if len(filter_df.index) == 0:
#                 filter_df=""
#                 filter_df = {"message":"Smart Irrigation system offline"}
#                 print("Smart Irrigation system offline")
#             else:
#                 #  if len(filter_df.index)>2:
#                 #      print(len(filter_df))
#                 #      filter_df = filter_df.iloc[-1]
#                 #      filter_df = {
#                 #     "temperature":"111",
#                 #     "humidity":"111",
#                 #     "moisture":"111",
#                 #     "moisture_p":"111",
#                 #     "status":"111",
#                 #     #  "component": latest_record_iloc["component1"],
#                 #     }
#                 #  else:
#                 print(str(filter_df['temperature'].values).replace("[", "").replace("]", ""))
#                 print(filter_df)

#                 temperature = float(filter_df['temperature'].iloc[0])
#                 humidity = float(filter_df['humidty'].iloc[0])
#                 moisture = float(filter_df['moisture'].iloc[0])
#                 moisture_p = float(filter_df['moisture_p'].iloc[0])

#                 status = str(filter_df['status_moisture'].iloc[0])
#                 component = int(filter_df['component1'].iloc[0])
#                 # preidct watering time using the model
#                 hours = predict_watering_time(
#                         temperature=temperature,
#                         humidity=humidity,
#                         moisture=moisture,
#                         moisture_p=moisture_p
#                     )

#                 filter_df = {
#                         "temperature": temperature,
#                         "humidity": humidity,
#                         "moisture": moisture,
#                         "moisture_p": moisture_p,
#                         "status": status,
#                         "component": component,
#                         "hours": hours
#                     }

#                 print(filter_df)
#                 print({key: type(value) for key, value in filter_df.items()})
#                 print("Smart Irrigation system online")

#             return filter_df








# @app.post('/api/switch/')

# async def switch_pump(switch_value:Switch_Value,connect_status:object=Depends(DataModel.connect_db)):
#             print("switching...")
#             data = {
#             "auto":switch_value.auto,
#             "number":switch_value.number,
#             }
#             print(data)
#             try:
#                 response = requests.post(url=url_esp8266,json=data)
#                 response.raise_for_status()
#                 print(f"Response JSON:{response.text}")
#                 return response.text

#             except requests.exceptions.RequestException as e:
#                     print(f"error handling reuqtes{e}")





# @app.post("/svc/predict")
# async def predict(data: dict):

#     hours = predict_watering_time(
#         temperature=data["temperature"],
#         humidity=data["humidity"],
#         moisture=data["moisture"],
#         moisture_p=data["moisture_p"]
#     )

#     return {
#         "hours_until_watering": hours
#     }
            
# # Run Uvicorn if the script is executed directly
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="192.168.8.19", port=8000, reload=True)


#     # host="192.168.8.7"