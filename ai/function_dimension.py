import logging
import pandas as pd
import numpy as np


from iotfunctions.base import BasePreload
from iotfunctions import ui

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func

logger = logging.getLogger(__name__)


# Specify the URL to your package here.
# This URL must be accessible via pip install
PACKAGE_URL = 'git+https://github.com/singhshraddha/fun-demo@'


class SampleDimensionPreload_random(BasePreload):
    '''
    Create and add test dimension (dimension_1) and the dimension value (random)
    This function will drop the previous dimension values and reload the dimension table
    '''

    dim_table_name = None

    def __init__(self, output_item ='dimension_preload_done'):

        super().__init__(dummy_items=[],output_item = output_item)


    def execute(self, df, start_ts = None,end_ts=None,entities=None):
        '''
        This class is show how to create and load test dimension with data
        in two ways
        1. randomly generating test data
        2. setting test data to pre-determined values
        '''
        entity_type = self.get_entity_type()
        self.db = entity_type.db
        schema = entity_type._db_schema

        # get dimension table name - to add dimension values to
        try:
            self.dim_table_name = (entity_type.get_attributes_dict()['_dimension_table_name']).lower()
        except:
            self.dim_table_name = entity_type.logical_name + '_dimension'

        msg = 'Dimension table name: ' + str(self.dim_table_name)
        logging.debug(msg)

        # read in the device id for the entity, each dimension is added per device id
        ef = self.db.read_table(entity_type.logical_name, schema=schema, columns=[entity_type._entity_id])
        ids = set(ef[entity_type._entity_id].unique())
        msg = 'entities with device_id present:' + str(ids)
        logger.debug(msg)

        # make dimension can only make a new dimension table
        # old dimension table and all data in it is deleted to add new columns
        self.db.drop_table(self.dim_table_name, schema=schema)
        # make a dimension table before adding data in 1. and 2. below
        entity_type.make_dimension(self.dim_table_name,
                                   Column('dimension_1', String(50)), # add dimension_1
                                   **{'schema': schema})
        # register the entity for the dimension to be added to the metadata
        entity_type.register()
        '''
        randomly generate dimension data
            will generate pseudo-random data for dimension 1
            for deviceids that don't have already have data
        '''
        entity_type.generate_dimension_data(entities=ids)

        return True

    @classmethod
    def build_ui(cls):
        '''
        Registration metadata
        '''
        # define arguments that behave as function inputs
        inputs = []
        # define arguments that behave as function outputs
        outputs=[]
        outputs.append(ui.UIStatusFlag(name='output_item'))
        return (inputs, outputs)


class SampleDimensionPreload_preset(BasePreload):
    '''
    Create and add test dimension (dimension_1) and the dimension value (preload_value)
    This function will drop the previous dimension values and reload the dimension table
    '''

    dim_table_name = None

    def __init__(self, output_item='dimension_preload_done'):

        super().__init__(dummy_items=[], output_item=output_item)

    def execute(self, df, start_ts=None, end_ts=None, entities=None):
        '''
        This class is show how to create and load test dimension with data
        in two ways
        1. randomly generating test data
        2. setting test data to pre-determined values
        '''
        entity_type = self.get_entity_type()
        self.db = entity_type.db
        schema = entity_type._db_schema

        # get dimension table name - to add dimension values to
        try:
            self.dim_table_name = (entity_type.get_attributes_dict()['_dimension_table_name']).lower()
        except:
            self.dim_table_name = entity_type.logical_name + '_dimension'

        msg = 'Dimension table name: ' + str(self.dim_table_name)
        logging.debug(msg)

        # read in the device id for the entity, each dimension is added per device id
        ef = self.db.read_table(entity_type.logical_name, schema=schema, columns=[entity_type._entity_id])
        ids = set(ef[entity_type._entity_id].unique())
        msg = 'entities with device_id present:' + str(ids)
        logger.debug(msg)

        # make dimension can only make a new dimension table
        # old dimension table and all data in it is deleted to add new columns
        self.db.drop_table(self.dim_table_name, schema=schema)
        # make a dimension table before adding data in 1. and 2. below
        entity_type.make_dimension(self.dim_table_name,
                                   Column('dimension_1', String(50)),  # add dimension_1
                                   **{'schema': schema})
        # register the entity for the dimension to be added to the metadata
        entity_type.register()

        '''
         preload dimensional data to pre-determined values

            these are hard coded but can easily be extended to 
            loading data from csv, http_requests, etc
            the values are hardcoded to string term 'preloaded_value'

            will set dimension_1 to the hardcoded values
        '''
        # create hardcoded data
        preload_data = {}
        preload_values = np.repeat('preload_value', len(ids))
        preload_data['dimension_1'] = preload_values
        preload_data[entity_type._entity_id] = list(ids)
        df = pd.DataFrame(preload_data)
        '''
        # load the dummy data into db
        '''
        msg = 'Setting columns for dimensional table\n'
        required_cols = self.db.get_column_names(table=self.dim_table_name, schema=schema)
        missing_cols = list(set(required_cols) - set(df.columns))
        msg = msg + 'required_cols ' + str(required_cols) + '\n'
        msg = msg + 'missing_cols ' + str(missing_cols) + '\n'
        logger.debug(msg)

        # Write the dataframe for dimension to the IBM IOT Platform database table
        self.write_frame(df=df, table_name=self.dim_table_name, if_exists='append')

        kwargs = {
            'dimension_table': self.dim_table_name,
            'schema': schema,
        }
        entity_type.trace_append(created_by=self,
                                 msg='Wrote dimension to table',
                                 log_method=logger.debug,
                                 **kwargs)

        return True

    @classmethod
    def build_ui(cls):
        '''
        Registration metadata
        '''
        # define arguments that behave as function inputs
        inputs = []
        # define arguments that behave as function outputs
        outputs = []
        outputs.append(ui.UIStatusFlag(name='output_item'))
        return (inputs, outputs)
