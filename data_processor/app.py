import os
import boto3
import pandas as pd
import json
from datetime import datetime
from flask import Flask, request, jsonify
import pymysql
from io import StringIO

app = Flask(__name__)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'mysql'),
        user=os.environ.get('MYSQL_USER', 'sales_user'),
        password=os.environ.get('MYSQL_PASSWORD', 'password'),
        db=os.environ.get('MYSQL_DATABASE', 'sales_data'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# S3 connection
s3_client = boto3.client(
    's3',
    endpoint_url=os.environ.get('S3_ENDPOINT', 'http://s3:9000'),
    aws_access_key_id=os.environ.get('S3_ACCESS_KEY', 'minioadmin'),
    aws_secret_access_key=os.environ.get('S3_SECRET_KEY', 'minioadmin'),
    region_name=os.environ.get('S3_REGION', 'us-east-1'),
    config=boto3.session.Config(signature_version='s3v4')
)

# Create buckets if they don't exist
@app.before_first_request
def setup_s3():
    try:
        buckets = s3_client.list_buckets()
        existing_buckets = [bucket['Name'] for bucket in buckets['Buckets']]
        
        if os.environ.get('S3_BUCKET', 'sales-reports') not in existing_buckets:
            s3_client.create_bucket(Bucket=os.environ.get('S3_BUCKET', 'sales-reports'))
            print(f"Created '{os.environ.get('S3_BUCKET', 'sales-reports')}' bucket")
    except Exception as e:
        print(f"Error setting up S3 buckets: {e}")

# List available sales reports
@app.route('/api/reports', methods=['GET'])
def list_reports():
    try:
        response = s3_client.list_objects_v2(Bucket=os.environ.get('S3_BUCKET', 'sales-reports'))
        reports = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                reports.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Process a specific sales report
@app.route('/api/process', methods=['POST'])
def process_report():
    data = request.json
    if not data or 'report_key' not in data:
        return jsonify({
            'success': False,
            'error': 'Report key is required'
        }), 400
    
    report_key = data['report_key']
    
    try:
        # Get the file from S3
        response = s3_client.get_object(Bucket=os.environ.get('S3_BUCKET', 'sales-reports'), Key=report_key)
        report_content = response['Body'].read().decode('utf-8')
        
        # Process the CSV data
        df = pd.read_csv(StringIO(report_content))
        
        # Perform data processing
        # This is a simplified example - in a real scenario you would do more complex transformations
        df['total_amount'] = df['quantity'] * df['price']
        df['process_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Store processed data in MySQL
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Create table if it doesn't exist
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id VARCHAR(50),
                    product_id VARCHAR(50),
                    quantity INT,
                    price DECIMAL(10, 2),
                    total_amount DECIMAL(10, 2),
                    order_date VARCHAR(50),
                    process_date DATE,
                    report_key VARCHAR(255)
                )
                """)
                
                # Insert data
                for _, row in df.iterrows():
                    cursor.execute("""
                    INSERT INTO processed_sales 
                    (order_id, product_id, quantity, price, total_amount, order_date, process_date, report_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['order_id'], 
                        row['product_id'],
                        row['quantity'],
                        row['price'],
                        row['total_amount'],
                        row['order_date'],
                        row['process_date'],
                        report_key
                    ))
                
                conn.commit()
        finally:
            conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed report: {report_key}',
            'rows_processed': len(df)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Upload a sales report
@app.route('/api/upload', methods=['POST'])
def upload_report():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    try:
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            os.environ.get('S3_BUCKET', 'sales-reports'),
            filename
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded file: {filename}',
            'report_key': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get statistics from processed data
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                SELECT COUNT(*) as count FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
                """, (os.environ.get('MYSQL_DATABASE', 'sales_data'), 'processed_sales'))
                result = cursor.fetchone()
                
                if result['count'] == 0:
                    return jsonify({
                        'success': True,
                        'message': 'No data has been processed yet'
                    })
                
                # Get statistics
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales,
                    AVG(total_amount) as average_order_value,
                    MAX(total_amount) as max_order_value,
                    MIN(total_amount) as min_order_value
                FROM processed_sales
                """)
                stats = cursor.fetchone()
                
                return jsonify({
                    'success': True,
                    'statistics': stats
                })
        finally:
            conn.close()
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'E-commerce Data Processing API',
        'status': 'running',
        'endpoints': [
            {'path': '/api/reports', 'method': 'GET', 'description': 'List available sales reports'},
            {'path': '/api/process', 'method': 'POST', 'description': 'Process a specific sales report'},
            {'path': '/api/upload', 'method': 'POST', 'description': 'Upload a new sales report'},
            {'path': '/api/stats', 'method': 'GET', 'description': 'Get statistics from processed data'}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 