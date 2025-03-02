import requests
import os
import sys
import json

BASE_URL = "http://localhost:5001/api"

def list_reports():
    """List all available sales reports"""
    response = requests.get(f"{BASE_URL}/reports")
    data = response.json()
    
    if data['success']:
        if not data['reports']:
            print("No reports found.")
            return []
        
        print("\nAvailable reports:")
        for idx, report in enumerate(data['reports'], 1):
            print(f"{idx}. {report['key']} (Size: {report['size']} bytes, Modified: {report['last_modified']})")
        return data['reports']
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
        return []

def upload_report(file_path):
    """Upload a sales report"""
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    data = response.json()
    
    if data['success']:
        print(f"Successfully uploaded: {data['report_key']}")
        return data['report_key']
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
        return None

def process_report(report_key):
    """Process a specific sales report"""
    response = requests.post(
        f"{BASE_URL}/process", 
        json={'report_key': report_key},
        headers={'Content-Type': 'application/json'}
    )
    
    data = response.json()
    
    if data['success']:
        print(f"Successfully processed report: {report_key}")
        print(f"Rows processed: {data['rows_processed']}")
        return True
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
        return False

def get_stats():
    """Get statistics from processed sales data"""
    response = requests.get(f"{BASE_URL}/stats")
    data = response.json()
    
    if data['success']:
        if 'statistics' in data:
            stats = data['statistics']
            print("\nSales Statistics:")
            print(f"Total Orders: {stats['total_orders']}")
            print(f"Total Sales: ${float(stats['total_sales']):.2f}")
            print(f"Average Order Value: ${float(stats['average_order_value']):.2f}")
            print(f"Max Order Value: ${float(stats['max_order_value']):.2f}")
            print(f"Min Order Value: ${float(stats['min_order_value']):.2f}")
        else:
            print(data.get('message', 'No statistics available.'))
        return True
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
        return False

def main():
    print("E-commerce Data Processing Client")
    print("=================================")
    
    while True:
        print("\nOptions:")
        print("1. List available reports")
        print("2. Upload a sales report")
        print("3. Process a report")
        print("4. Get sales statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            list_reports()
        
        elif choice == '2':
            file_path = input("Enter path to CSV file: ")
            upload_report(file_path)
        
        elif choice == '3':
            reports = list_reports()
            if reports:
                try:
                    idx = int(input("Enter report number to process: ")) - 1
                    if 0 <= idx < len(reports):
                        process_report(reports[idx]['key'])
                    else:
                        print("Invalid report number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == '4':
            get_stats()
        
        elif choice == '5':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 