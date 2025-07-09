# Technical Assignment: Cloud-Native Data Synchronization Service

This project presents a **proof-of-concept** for an Extract, Transform, Load (ETL) pipeline implemented using Python on Google Cloud Platform (GCP).

It fetches order data from a mock Shopify API and customer data from a mock Zoho CRM API, merges them by customer's email address, and prepares the unified data for storage in a data warehouse.

The service is implemented as a GCP Cloud Function, focusing on API interaction, cloud architecture design, and production-quality code.

## Approach

The core logic is contained within the `main.py` script, structured as a GCP Cloud Function (`sync_data` function). The service performs the following steps:

1.  **Data Fetching:**

    - It makes an HTTP GET request to a mock Shopify API endpoint to retrieve a list of recent e-commerce orders.
    - Next, it makes an HTTP GET request to a mock Zoho CRM API endpoint to retrieve customer contact information.

2.  **Data Merging:**

    - After fetching, the Zoho CRM data is pre-processed into a dictionary for efficient lookup, using the customer's email address as the key. This allows for near O(1) time complexity when searching for corresponding CRM records for each Shopify order, rather than iterating through the entire CRM dataset repeatedly.
    - The service then iterates through each Shopify order. For each order, it attempts to find a matching customer record in the pre-indexed Zoho CRM data using the `customer_email` as the unique identifier.
    - If a match is found, relevant fields from the Shopify order (order ID, total price) are merged with the customer's CRM data (name, email, company) into a single, unified JSON object.

3.  **Preparation for Storage:**
    - The resulting merged JSON objects are collected into a list, making them ready to be sent to a data warehousing service.
    - The function includes error handling to manage API request failures, network issues, and JSON parsing errors.

## GCP Architecture

This service is designed to be deployed on Google Cloud Platform (GCP) as part of an event-driven data pipeline.

### 1. Cloud Function Trigger

The `sync_data` Cloud Function would be triggered on a scheduled basis to ensure regular data synchronization.

- **Service:** **Cloud Scheduler**
- **Mechanism:** A Cloud Scheduler job would be configured to send an HTTP GET request to the Cloud Function's HTTP endpoint at a defined interval (e.g., daily, hourly, every 15 minutes). This provides a reliable, cron-based scheduling mechanism to automatically initiate the data ingestion process.

### 2. Data Storage for Merged Data

The final, merged JSON objects, ready for analytical querying, would be stored in a fully managed, scalable data warehouse.

- **Service:** **Google BigQuery**
- **Mechanism:** The Cloud Function, after successfully merging data, would leverage the BigQuery API (using the `google-cloud-bigquery` client library) to insert the prepared JSON objects as new rows into a designated BigQuery table.
  - Each merged JSON object directly maps to a row in the BigQuery table, with keys becoming column names.
  - BigQuery's serverless nature and automatic scaling are ideal for handling fluctuating data volumes from the synchronization process.

### 3. Securely Managing API Keys or Other Secrets

Handling sensitive information like API keys for Shopify or Zoho CRM, or any other credentials, is critical in a production environment.

- **Service:** **Google Secret Manager**
- **Mechanism:**
  - API keys (e.g., for Shopify, Zoho, or even Google Cloud service accounts if granular permissions are needed beyond the Cloud Function's default service account) would be stored in Google Secret Manager.
  - The Cloud Function's associated Service Account would be granted the necessary IAM permissions (`Secret Manager Secret Accessor` role) to retrieve these secrets at runtime.
  - The Cloud Function code (`main.py`) would then fetch these secrets from Secret Manager using the `google-cloud-secret-manager` client library instead of hardcoding them or relying on environment variables set directly on the function. This ensures secrets are encrypted at rest and in transit, and access is tightly controlled via IAM policies.

## Instructions: How to Set Up and Run Locally

To set up and run this proof-of-concept locally, follow these steps:

1.  **Clone the Repository (if applicable):**

    ```bash
    git clone <this-repo-url>
    cd POC-data-sync-service
    ```

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies and avoid conflicts.

        ```bash
        python3 -m venv .venv
        ```

        - **On macOS/Linux:**
          ```bash
          source .venv/bin/activate
          ```
        - **On Windows (Command Prompt):**
          ```bash
          .venv\Scripts\activate.bat
          ```
        - **On Windows (PowerShell):**
          `powershell

    .venv\Scripts\Activate.ps1
    `      Your terminal prompt should show`(.venv)`or`(venv)` indicating the virtual environment is active.

3.  **Install Dependencies:**
    Install the required Python packages listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Local Test Script:**
    Execute the `test_local.py` script to simulate the Cloud Function execution and see the merged output.

    ```bash
    python test_local.py
    ```

## Sample Output

A sample of the expected merged JSON structure for Order #1001, is provided in `output.json`:

**`output.json` content:**

```json
{
  "order_id": 1,
  "customer_name": "Sanjeev Gupta",
  "customer_email": "sanjeev@example.com",
  "customer_company": "Innovate Inc.",
  "order_total_price": "99.95"
}
```
