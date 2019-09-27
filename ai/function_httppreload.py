import inspect
import logging
import datetime as dt
import math
from sqlalchemy.sql.sqltypes import TIMESTAMP,VARCHAR
import numpy as np
import pandas as pd
import json


#from iotfunctions.base import BaseTransformer
from iotfunctions.base import BasePreload
from iotfunctions import ui
from iotfunctions.db import Database
from iotfunctions import bif
#import datetime as dt
import datetime
import urllib3
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


# Specify the URL to your package here.
# This URL must be accessible via pip install
#PACKAGE_URL = 'git+https://github.com/madendorff/functions@'
PACKAGE_URL = 'git+https://github.com/fe01134/fun-demo@'


class WeatherHTTPPreload(BasePreload):
    '''
    Do a HTTP request as a preload activity. Load results of the get into the Entity Type time series table.
    HTTP request is experimental
    '''

    out_table_name = None

    def __init__(self, request, url, headers = None, body = None, column_map = None, output_item  = 'http_preload_done'):

        if body is None:
            body = {}

        if headers is None:
            headers = {}

        if column_map is None:
            column_map = {}

        super().__init__(dummy_items=[],output_item = output_item)

        # create an instance variable with the same name as each arg

        self.url = url
        self.request = request
        self.headers = headers
        self.body = body
        self.column_map = column_map

        # do not do any processing in the init() method. Processing will be done in the execute() method.

    def execute(self, df, start_ts = None,end_ts=None,entities=None):

        entity_type = self.get_entity_type()
        db = entity_type.db
        encoded_body = json.dumps(self.body).encode('utf-8')
        encoded_headers = json.dumps(self.headers).encode('utf-8')

        # This class is setup to write to the entity time series table
        # To route data to a different table in a custom function,
        # you can assign the table name to the out_table_name class variable
        # or create a new instance variable with the same name

        if self.out_table_name is None:
            table = entity_type.name
        else:
            table = self.out_table_name

        schema = entity_type._db_schema

        # There is a a special test "url" called internal_test
        # Create a dict containing random data when using this
        '''
        response_data:
        metrics   [-2.17257716  0.02561278 -0.6094071 ]
        datetime   2019-09-14T14:29:29.514
        categoricals   ['A' 'B' 'C']
        '''

        if self.url == 'internal_test':
            logging.debug('Condition is internal_test ')
            rows = 3
            response_data = {}
            (metrics,dates,categoricals,others) = db.get_column_lists_by_type(
                table = table,
                schema= schema,
                exclude_cols = []
            )
            for m in metrics:
                response_data[m] = np.random.normal(0,1,rows)

            logging.debug('response_data[m] ===' )
            logging.debug( response_data[m] )

            for d in dates:
                response_data[d] = dt.datetime.utcnow() - dt.timedelta(seconds=15)

            logging.debug('response_data[d] ===' )
            logging.debug( response_data[d] )

            for c in categoricals:
                response_data[c] = np.random.choice(['A','B','C'],rows)
            logging.debug('response_data[c] ===' )
            logging.debug( response_data[c] )

        # make an http request
        else:
            response = db.http.request(self.request,
                                       self.url,
                                       body=encoded_body,
                                       headers=self.headers)
            response_data = response.data.decode('utf-8')
            response_data = json.loads(response_data)

        df = pd.DataFrame(data=response_data)

        logging.debug('Generated DF from response_data ===' )
        logging.debug( df.head() )

        # align dataframe with data received

        # use supplied column map to rename columns
        df = df.rename(self.column_map, axis='columns')
        # fill in missing columns with nulls
        required_cols = db.get_column_names(table = table, schema=schema)
        logging.debug('required_cols columns === %s' %required_cols )

        missing_cols = list(set(required_cols) - set(df.columns))
        logging.debug('missing_cols columns === %s' %missing_cols )

        if len(missing_cols) > 0:
            kwargs = {
                'missing_cols' : missing_cols
            }
            entity_type.trace_append(created_by = self,
                                     msg = 'http data was missing columns. Adding values.',
                                     log_method=logger.debug,
                                     **kwargs)
            for m in missing_cols:
                if m==entity_type._timestamp:
                    df[m] = dt.datetime.utcnow() - dt.timedelta(seconds=15)
                elif m=='devicetype':
                    df[m] = entity_type.logical_name
                else:
                    df[m] = None

        # remove columns that are not required
        df = df[required_cols]
        logging.debug('Generated DF from remove columns that are not required ===' )
        logging.debug( df.head() )

        # write the dataframe to the database table
        self.write_frame(df=df,table_name=table)
        kwargs ={
            'table_name' : table,
            'schema' : schema,
            'row_count' : len(df.index)
        }
        entity_type.trace_append(created_by=self,
                                 msg='Wrote data to table',
                                 log_method=logger.debug,
                                 **kwargs)
        logging.debug('Function completed execution ')
        return True

    @classmethod
    def build_ui(cls):
        '''
        Registration metadata
        '''
        # define arguments that behave as function inputs
        inputs = []
        inputs.append(ui.UISingle(name='request',
                              datatype=str,
                              description='comma separated list of entity ids',
                              values=['GET','POST','PUT','DELETE']
                              ))
        inputs.append(ui.UISingle(name='url',
                                  datatype=str,
                                  description='request url',
                                  tags=['TEXT'],
                                  required=True
                                  ))
        inputs.append(ui.UISingle(name='headers',
                               datatype=dict,
                               description='request url',
                               required = False
                               ))
        inputs.append(ui.UISingle(name='body',
                               datatype=dict,
                               description='request body',
                               required=False
                               ))
        # define arguments that behave as function outputs
        outputs=[]
        outputs.append(ui.UIStatusFlag(name='output_item'))
        return (inputs, outputs)
