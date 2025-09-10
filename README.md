# Credit System

A Django-based credit management system with customer and loan management. Supports Docker deployment and importing data from Excel files.

-----

## **Project Structure**

```
backend/
├── credit_system/        # Django project
├── loans/                # Django app (models: Customer, Loan)
├── scripts/
│   └── import_excel.py   # Script to import Excel data
├── data/
│   ├── customer_data.xlsx
│   └── loan_data.xlsx
├── manage.py
Dockerfile
docker-compose.yml
```

-----

## **Setup & Docker**

1.  **Clone the repository**

    ```bash
    git clone <your-repo-url>
    cd credit_system_repo_fixed
    ```

2.  **Place Excel files**

    Put your Excel files in `backend/data/`:

    ```
    backend/data/customer_data.xlsx
    backend/data/loan_data.xlsx
    ```

3.  **Build Docker images**

    ```bash
    docker-compose build
    ```

4.  **Start containers**

    ```bash
    docker-compose up -d
    ```

      * Services: `web` (Django), `db` (Postgres), `redis`, `worker` (Celery)

-----

## **Import Excel Data**

Run the import script inside Docker:

```bash
docker-compose run --rm web python scripts/import_excel.py
```

  * The script safely imports `Customer` and `Loan` data.
  * Uses unique `phone_number` to avoid duplicate key errors.
  * AutoFields (`customer_id`, `loan_id`) are automatically managed.

-----

## **Reset Database Sequences (if needed)**

If duplicate key errors occur due to old data:

```bash
docker exec -it db psql -U postgres -d credit_system
```

Inside PostgreSQL shell:

```sql
SELECT setval('loans_customer_customer_id_seq', (SELECT MAX(customer_id) FROM loans_customer));
SELECT setval('loans_loan_loan_id_seq', (SELECT MAX(loan_id) FROM loans_loan));
\q
```

-----

## **Stop Containers**

```bash
docker-compose down
```

  * Use `-v` to remove volumes and reset the database:

    ```bash
    docker-compose down -v
    ```

