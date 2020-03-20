import json
import logging
from ai.function_dimension import (SampleDimensionPreload_random,
                                   SampleDimensionPreload_preset)
from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

EngineLogging.configure_console_logging(logging.DEBUG)

'''
# Getting Db credentials
# Explore > Usage > Watson IOT Platform Analytics > Copy to clipboard
# Paste contents in credentials_as.json file
# Save in scripts
'''


'''
1. Create a database object to access Watson IOT Platform Analytics DB.
'''
schema = 'bluadmin' #  set if you are not using the default
with open('./scripts/credentials_as.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())
db = Database(credentials = credentials)

'''
2. Register custom function
You must unregister_functions if you change the method signature or required inputs
'''
db.unregister_functions(['SampleDimensionPreload_preset'])
db.register_functions([SampleDimensionPreload_preset])


'''
3. To do anything with IoT Platform Analytics, you will need one or more entity type.
This example assumes that the entity to which we are adding dimensions already exists
We add the custom function to this entity type to test it locally
'''
entity_name = 'issue_455_blank_preset'
entity_type = db.get_entity_type(name=entity_name)

# get dimension table name - to add dimension values to
try:
    dim_table_name = (entity_type.get_attributes_dict()['_dimension_table_name']).lower()
except:
    dim_table_name = entity_name + '_dimension'

entity_type._functions.extend([SampleDimensionPreload_preset()])

'''
To test the execution of kpi calculations defined for the entity type locally
use this function.

A local test will not update the server job log or write kpi data to the AS data
lake. Instead kpi data is written to the local filesystem in csv form.
'''
entity_type.exec_local_pipeline(**{'_production_mode': False})


'''
view entity data
'''
print ("Read Table of new dimension")
print(dim_table_name)
df = db.read_dimension(dimension=dim_table_name, schema=schema)
print(df.head())

print("Done reading  entity dimension table")