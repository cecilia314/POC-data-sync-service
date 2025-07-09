import requests
import os
import json

SHOPIFY_API_URL = os.environ.get('SHOPIFY_API_URL', 'https://my-json-server.typicode.com/cecilia314/demo/shopify')
ZOHO_CRM_API_URL = os.environ.get('ZOHO_CRM_API_URL', 'https://my-json-server.typicode.com/cecilia314/demo/zoho')

def sync_data(request):
    """
        Cloud Function entry point to synchronize and prepare data.
        Triggered by an HTTP request.
    """
    print("Cloud Function 'sync_data' triggered.")

    try:
        shopify_orders = fetch_shopify_orders(SHOPIFY_API_URL)
        zoho_crm_records = fetch_zoho_crm_customers(ZOHO_CRM_API_URL)
       
        if not shopify_orders:
            print("No Shopify orders found.")
            return json.dumps({"status": "success", "message": "No Shopify orders to process."}), 200, {'Content-Type': 'application/json'}
        if not zoho_crm_records:
            print("No Zoho CRM records found.")
            return json.dumps({"status": "success", "message": "No Zoho CRM data available for matching."}), 200, {'Content-Type': 'application/json'}

        index_crm_customers_by_email = index_customers_by_email(zoho_crm_records)
        merged_data_list = merge_orders_and_customers_data(shopify_orders, index_crm_customers_by_email)

        if not merged_data_list:
            print("No records merged after processing.") 
            return json.dumps({"status": "success", "message": "No matching data found to merge."}), 200, {'Content-Type': 'application/json'} 
       
        return json.dumps({"status": "success", "processed_records_count": len(merged_data_list), "merged_data": merged_data_list}), 200, {'Content-Type': 'application/json'}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return json.dumps({"status": "error", "message": f"Failed to fetch data: {e}"}), 500, {'Content-Type': 'application/json'}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return json.dumps({"status": "error", "message": f"Failed to decode API response: {e}"}), 500, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"}), 500, {'Content-Type': 'application/json'}
    
def fetch_shopify_orders(api_url): 
    """
        Fetches Shopify orders from the provided API URL
    """
    response = requests.get(api_url, timeout=10)
    response.raise_for_status() 
    print(f"Successfully fetched Shopify data.")
    return response.json()

def fetch_zoho_crm_customers(api_url):
    """    
        Fetches Zoho CRM customer records from the provided API URL.
    """
    response = requests.get(api_url, timeout=10)
    response.raise_for_status() 
    print(f"Successfully fetched Zoho CRM data.")
    return response.json()

def index_customers_by_email(customers):
    """
    Indexes Zoho CRM customer records by email for quick lookup.

    Arguments:
        - customers: List of Zoho CRM customer records.
        
    Returns:
        A dictionary where keys are customer emails and values are customer data.
    """
    indexed_customers = {}

    for customer in customers:
        customer_data = customer.get('user')
        
        if not customer_data or not isinstance(customer_data, dict):
            print(f"Skipping CRM record due to missing or invalid 'user' data: {customer}")
            continue
        
        customer_email = customer_data.get('email')
        if not customer_email:
            print(f"Skipping CRM record due to missing customer email in 'user' data: {customer_data}")
            continue

        indexed_customers[customer_email] = customer_data
   
    return indexed_customers

def merge_orders_and_customers_data(orders, customers_by_email):
    """
    Merges Shopify orders with Zoho CRM customer data based on email.
    
    Arguments:
        - orders: List of Shopify order records.
        - customers_by_email: Dictionary of Zoho CRM customer records indexed by email.
    
    Returns: 
        A list of merged records containing combined order and customer data.
    """
    merged_data_list = [] 
    
    for order in orders: 
        order_id = order.get('id')
        customer_email = order.get('customer_email')
        total_price = order.get('total_price')

        if not customer_email:
            print(f"Skipping Order ID {order_id}: Missing customer email.")
            continue

        matched_customer = customers_by_email.get(customer_email) 

        if matched_customer:
            print(f"Found matching CRM customer for {matched_customer.get('name')}")
            
            merged_record = {
                "order_id": order_id,
                "customer_name": matched_customer.get('name'),
                "customer_email": matched_customer.get('email'),
                "customer_company": matched_customer.get('company'),
                "order_total_price": total_price 
            }
            merged_data_list.append(merged_record)
            
        else:
            print(f"No matching CRM customer found for email: {customer_email} for Order ID {order_id}.")
    return merged_data_list