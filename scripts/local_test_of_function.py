import json
import logging
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from iotfunctions import bif
from ai.functions import Issue455HTTPPreload
from iotfunctions.metadata import EntityType
from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.DEBUG)

'''
# Getting Db credentials
# Explore > Usage > Watson IOT Platform Analytics > Copy to clipboard
# Paste contents in credentials_as.json file
# Save in scripts
'''

db_schema = 'bluadmin' #  set if you are not using the default
with open('./scripts/credentials_as.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())

'''
Developing Test Pipelines
-------------------------
When creating a set of functions you can test how they these functions will
work together by creating a test pipeline.
'''


'''
1. Create a database object to access Watson IOT Platform Analytics DB.
'''
db = Database(credentials = credentials)

'''
2. To do anything with IoT Platform Analytics, you will need one or more entity type.
You can create entity types through the IoT Platform or using the python API as shown below.
When creating a new entity type you can create it's corresponding dimension table as shown below.
The database schema is only needed if you are not using the default schema. You can also rename the timestamp.
'''
entity_name = 'issue455_0'
entity_dimension_lower =  entity_name.lower() + '_dimension'
entity_dimension_upper =  entity_name.upper() + '_dimension'


db.drop_table(entity_name, schema = db_schema)
db.drop_table(entity_dimension_lower, schema = db_schema)
db.drop_table(entity_dimension_upper, schema = db_schema)

entity = EntityType(entity_name,db,
                    Column('TURBINE_ID',String(50)),
                    Column('TEMPERATURE',Float()),
                    Column('PRESSURE',Float()),
                    Column('STEP',Float()),
                    Column('PRESS_X',Float()),
                    Column('PRESS_Y',Float()),
                    Column('TEMP_X',Float()),
                    Column('TEMP_Y',Float()),
                    Issue455HTTPPreload(username = None,
                                        password = None,
                                        request='GET',
                                        url="https://turbine-simulator.mybluemix.net/v1/api/reading",
                                        output_item = 'http_preload_done'),
                    **{
                      '_timestamp' : 'evt_timestamp',
                      '_db_schema' : db_schema
                    }
                    )
entity.make_dimension(entity_dimension_upper,
                      Column('CLIENT',String(50)),
                      Column('ORGANIZATION',String(50)),
                      Column('FUNCTION',String(50)),
                      **{ 'schema': db_schema}
                      )


entity_dimension = entity.get_attributes_dict()['_dimension_table_name']


'''
When creating an EntityType object you will need to specify the name of the entity, the database
object that will contain entity data

After creating an EntityType you will need to register it so that it visible in the Add Data to Entity Function UI.
To also register the functions and constants associated with the entity type, specify
'publish_kpis' = True.
'''
entity.register(raise_error=False)
# When creating a custom preload function you can register it by uncommenting the following lines
# You must unregister_functions if you change the method signature or required inputs.
db.unregister_functions(['Issue455HTTPPreload'])
db.register_functions([Issue455HTTPPreload])

'''
To test the execution of kpi calculations defined for the entity type locally
use this function.

A local test will not update the server job log or write kpi data to the AS data
lake. Instead kpi data is written to the local filesystem in csv form.
'''

entity.exec_local_pipeline(**{'_production_mode': False})

'''
view entity data
'''
print ("Read Table of new entity" )
df = db.read_table(table_name=entity_name, schema=db_schema)
print(df.head())
print(df.columns)


print ( "Read Table of new dimension" )
df = db.read_table(table_name=entity_dimension, schema=db_schema)
print(df.head())
print(df.columns)

print("Done registering  entity")



