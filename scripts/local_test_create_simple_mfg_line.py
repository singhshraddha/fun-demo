import json
import logging
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from iotfunctions import bif
from ai.functions import DemoHTTPPreload
from iotfunctions.metadata import EntityType
from iotfunctions.db import Database
from iotfunctions.enginelog import EngineLogging
from ai import settings
from scripts.simple_mfg_entities import Mfg_Line

EngineLogging.configure_console_logging(logging.DEBUG)

#with open('credentials.json', encoding='utf-8') as F:
db_schema = 'bluadmin' #  set if you are not using the default
with open('credentials_Monitor-Demo.json', encoding='utf-8') as F:
    credentials = json.loads(F.read())
#db_schema = 'dash100462'  # replace if you are not using the default schema
#with open('credentials_dev2.json', encoding='utf-8') as F:
#    credentials = json.loads(F.read())

db = Database(credentials = credentials)
entity_type_name = 'Clients04'
#db.drop_table(entity_type_name, schema = db_schema)

entity = Mfg_Line(name = entity_type_name,
                db = db,
                db_schema = db_schema,
                description = "Manufacturing Operations Control Center 03",
                )

entity.register(raise_error=False)
# You must unregister_functions if you change the mehod signature or required inputs.
#db.unregister_functions(["DataHTTPPreload"])
#db.register_functions([DemoHTTPPreload])

#entity.add_slowly_changing_dimension(self,property_name,datatype,**kwargs):
entity.make_dimension()

entity.exec_local_pipeline()

'''
view entity data
'''
print ( "Read Table of new  entity" )
df = db.read_table(table_name=entity_name, schema=db_schema)
print(df.head())

print ( "Done registering  entity" )
