
import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine

def main(args):
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    db = args.db
    table_name = args.table_name
    url = args.url

    csv_name = str(url.rsplit('/', 1)[-1].strip())

    os.system(f"wget {url} -O {csv_name}")
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = pd.read_csv(csv_name, nrows=10)
    # print(df.info())
    if ('lpep_pickup_datetime' in df.columns):
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')

    t_start = time()
    count = 0
    for batch in df_iter:
        count += 1

        batch_df = batch
        if ('lpep_pickup_datetime' in df.columns):
            batch_df.lpep_pickup_datetime = pd.to_datetime(batch_df.lpep_pickup_datetime)
            batch_df.lpep_dropoff_datetime = pd.to_datetime(batch_df.lpep_dropoff_datetime)

        print(f'inserting batch {count}...')

        b_start = time()
        batch_df.to_sql(name=table_name, con=engine, if_exists='append')
        b_end = time()

        print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')
        
    t_end = time()   
    print(f'Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches.')


if __name__ == "__main__":
    #Parsing arguments 
    parser = argparse.ArgumentParser(description='Loading data from .paraquet file link to a Postgres datebase.')

    parser.add_argument('--user', help='Username for Postgres.')
    parser.add_argument('--password', help='Password to the username for Postgres.')
    parser.add_argument('--host', help='Hostname for Postgres.')
    parser.add_argument('--port', help='Port for Postgres connection.')
    parser.add_argument('--db', help='Databse name for Postgres')
    parser.add_argument('--table_name', help='Destination table name for Postgres.')
    parser.add_argument('--url', help='URL for .paraquet file.')

    args = parser.parse_args()
    main(args)