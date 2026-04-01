from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import pandas as pd
import redshift_connector
import io
import os

# ── CONFIG ──────────────────────────────────────────────
S3_BUCKET        = 'ecommerce-pipeline-saurav'
AWS_REGION       = 'ap-south-1'
AWS_ACCESS_KEY   = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY   = os.environ.get('AWS_SECRET_ACCESS_KEY')

REDSHIFT_HOST     = 'ecommerce-pipeline.447437755883.ap-south-1.redshift-serverless.amazonaws.com'
REDSHIFT_PORT     = 5439
REDSHIFT_DB       = 'dev'
REDSHIFT_USER     = os.environ.get('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.environ.get('REDSHIFT_PASSWORD')
# ────────────────────────────────────────────────────────
default_args = {
    'owner': 'saurav',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def check_s3():
    s3 = boto3.client('s3', region_name=AWS_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix='processed/ecommerce_parquet/')
    files = [obj['Key'] for obj in response.get('Contents', [])]
    print(f"✅ Found {len(files)} files in S3:")
    for f in files:
        print(f"   {f}")

def load_to_redshift():
    s3 = boto3.client('s3', region_name=AWS_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    conn = redshift_connector.connect(
        host=REDSHIFT_HOST, port=REDSHIFT_PORT,
        database=REDSHIFT_DB, user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )
    cursor = conn.cursor()

    tables = [
        'kpi_revenue_by_country',
        'kpi_monthly_revenue',
        'kpi_top_products',
        'kpi_customer_summary'
    ]

    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
        key = f'processed/ecommerce_parquet/{table}/data.parquet'
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        df = pd.read_parquet(io.BytesIO(obj['Body'].read()))
        for _, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            cursor.execute(f"INSERT INTO {table} VALUES ({placeholders})", list(row))
        conn.commit()
        print(f"✅ Loaded {len(df)} rows into {table}")

    cursor.close()
    conn.close()

def verify_redshift():
    conn = redshift_connector.connect(
        host=REDSHIFT_HOST, port=REDSHIFT_PORT,
        database=REDSHIFT_DB, user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )
    cursor = conn.cursor()
    tables = ['kpi_revenue_by_country', 'kpi_monthly_revenue', 'kpi_top_products', 'kpi_customer_summary']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"✅ {table}: {count} rows")
    cursor.close()
    conn.close()

with DAG(
    dag_id='ecommerce_pipeline',
    default_args=default_args,
    description='E-Commerce Sales Pipeline: S3 → Redshift',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'pipeline']
) as dag:

    task_check_s3 = PythonOperator(
        task_id='check_s3_files',
        python_callable=check_s3
    )

    task_load_redshift = PythonOperator(
        task_id='load_to_redshift',
        python_callable=load_to_redshift
    )

    task_verify = PythonOperator(
        task_id='verify_redshift',
        python_callable=verify_redshift
    )

    task_check_s3 >> task_load_redshift >> task_verify
