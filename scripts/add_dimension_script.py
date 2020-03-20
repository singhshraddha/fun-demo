import json
import logging
from ai.function_dimension import SampleDimensionPreload_SS
from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging

from sqlalchemy import Column, String, Integer, Float

EngineLogging.configure_console_logging(logging.DEBUG)

'''
This script shows how to use an entity's random dimension generator
'''

'''
1. Create a database object to access Watson IOT Platform Analytics DB.
# Getting Db credentials
# Explore > Usage > Watson IOT Platform Analytics > Copy to clipboard
# Paste contents in credentials_as.json file
# Save in scripts
'''
schema = 'bluadmin' #  set if you are not using the default
with open('./scripts/credentials_as.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())
db = Database(credentials = credentials)



'''
2. To do anything with IoT Platform Analytics, you will need one or more entity type.
This example assumes that the entity to which we are adding dimensions already exists
'''
entity_name = 'issue_637_blank'
entity_type = db.get_entity_type(name=entity_name)

# get dimension table name - to add dimension values to
try:
    dim_table_name = (entity_type.get_attributes_dict()['_dimension_table_name']).lower()
except:
    dim_table_name = entity_name + '_dimension'

# db.drop_table(dim_table_name, schema=schema)

'''
3. create new dimensions by specifying them as columns
3.1 Acceptable Dimension Types
Integer, INTEGER, Float, FLOAT, String, VARCHAR, DateTime, Timestamp

3.2 Dimension names that have preset values
Using any of these dimensions will select values from a preset group
On left there is an array of dimension name that will generate the 
dimension vales on the right
Left:Right
['company', 'company_id', 'company_code']: ['ABC', 'ACME', 'JDI']
['plant', 'plant_id', 'plant_code']: ['Zhongshun', 'Holtsburg', 'Midway']
['plant', 'plant_id', 'plant_code']: ['US', 'CA', 'UK', 'DE']
['firmware', 'firmware_version']: ['1.0', '1.12', '1.13', '2.1']
['manufacturer']: ['Rentech', 'GHI Industries']
['zone']: ['27A', '27B', '27C']
['status', 'status_code']: ['inactive', 'active']
['operator', 'operator_id', 'person', 'employee']: ['Fred', 'Joe', 'Mary', 'Steve', 'Henry', 'Jane', 'Hillary', 'Justin', 'Rod']

3.3 Other dimension name
Any other dimension name other than the one above will generate random values
'''
db.drop_table(dim_table_name, schema=schema)
entity_type.make_dimension(dim_table_name,
                           Column('company', String(50))
                           **{'schema': schema})

entity_type.register()

entity_type._functions.extend([SampleDimensionPreload_SS()])

'''
To test the execution of kpi calculations defined for the entity type locally
use this function.

A local test will not update the server job log or write kpi data to the AS data
lake. Instead kpi data is written to the local filesystem in csv form.
'''
# entity_type.exec_local_pipeline(**{'_production_mode': False})

ef = self.db.read_table(entity_type.logical_name, schema=schema, columns=[entity_type._entity_id])
        ids = set(ef[self._entity_id].unique())
entity_type.generate_dimension_data(entities=entities)


