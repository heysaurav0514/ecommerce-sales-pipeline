# 🛒 E-Commerce Sales Pipeline

An end-to-end data engineering pipeline that ingests raw e-commerce transaction data, transforms it using PySpark, loads KPI tables into Amazon Redshift, and orchestrates the entire workflow with Apache Airflow.

---

## 🏗️ Architecture

```
Kaggle Dataset
     │
     ▼
Amazon S3 (Raw Layer)
s3://ecommerce-pipeline-saurav/raw/ecommerce/data.csv
     │
     ▼
Databricks (PySpark Transformation)
- Data cleaning & validation
- 392,692 rows processed
- 4 KPI tables generated
     │
     ▼
Amazon S3 (Processed Layer)
s3://ecommerce-pipeline-saurav/processed/ecommerce_parquet/
     │
     ▼
Amazon Redshift Serverless
- kpi_revenue_by_country
- kpi_monthly_revenue
- kpi_top_products
- kpi_customer_summary
     │
     ▼
Apache Airflow (Orchestration)
- Daily scheduled DAG
- 3-task pipeline: Check S3 → Load Redshift → Verify
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Source | Kaggle (E-Commerce Dataset) |
| Cloud Storage | Amazon S3 (ap-south-1) |
| Transformation | Apache Spark / PySpark on Databricks |
| Data Warehouse | Amazon Redshift Serverless |
| Orchestration | Apache Airflow 2.8.1 (Docker) |
| Language | Python 3 |
| Containerization | Docker & Docker Compose |

---

## 📊 KPI Tables

| Table | Rows | Description |
|---|---|---|
| `kpi_revenue_by_country` | 37 | Total revenue & orders per country |
| `kpi_monthly_revenue` | 13 | Month-over-month revenue trends |
| `kpi_top_products` | 20 | Top 20 products by revenue |
| `kpi_customer_summary` | 4,346 | Customer spend & order history |

---

## 📁 Project Structure

```
ecommerce-sales-pipeline/
│
├── dags/
│   └── ecommerce_pipeline.py   # Airflow DAG definition
│
├── .gitignore                  # Excludes secrets & logs
└── README.md
```

---

## ⚙️ Airflow DAG

The DAG `ecommerce_pipeline` runs **daily** and consists of 3 tasks:

```
check_s3_files → load_to_redshift → verify_redshift
```

- **check_s3_files** — Validates that all Parquet files exist in S3
- **load_to_redshift** — Truncates and reloads all 4 KPI tables from S3 Parquet
- **verify_redshift** — Confirms row counts in each Redshift table

---

## 🚀 Setup & Running Locally

### Prerequisites
- Docker Desktop
- AWS Account with S3 & Redshift access
- Python 3.8+

### 1. Clone the repository
```bash
git clone https://github.com/heysaurav0514/ecommerce-sales-pipeline.git
cd ecommerce-sales-pipeline
```

### 2. Create a `.env` file
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
REDSHIFT_USER=your_redshift_user
REDSHIFT_PASSWORD=your_redshift_password
```

### 3. Start Airflow
```bash
curl -LfO "https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml"
echo "AIRFLOW_UID=50000" > .env
docker compose up airflow-init
docker compose up -d
```

### 4. Open Airflow UI
Navigate to [http://localhost:8080](http://localhost:8080)
- Username: `airflow`
- Password: `airflow`

### 5. Trigger the DAG
Search for `ecommerce_pipeline` and click the ▶️ Play button.

---

## 📈 Sample Insights

- **Top market**: United Kingdom (highest revenue)
- **Peak month**: November (holiday season spike)
- **Best-selling product**: WHITE HANGING HEART T-LIGHT HOLDER
- **Total transactions processed**: 392,692 rows

---

## 👤 Author

**Saurav Shah**
- GitHub: [@heysaurav0514](https://github.com/heysaurav0514)
- LinkedIn: [linkedin.com/in/sauravshah0514](https://linkedin.com/in/sauravshah0514)
