# E-commerce Data Engineering Infrastructure

This project implements a data engineering infrastructure for an e-commerce company to process daily sales data. It consists of three main components:

1. **S3 Simulator (MinIO)**: For storing sales reports uploaded by business teams
2. **Flask API Server**: For processing sales data through API endpoints
3. **MySQL Database**: For storing processed sales data in a data warehouse

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   S3/MinIO  │────▶│  Flask API   │────▶│    MySQL    │
│  (Storage)  │     │  (Processing)│     │ (Database)  │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Project Structure

- `docker-compose.yml`: Orchestrates the entire infrastructure
- `data_processor/`: Contains the Flask application for data processing
  - `app.py`: Main Flask application with API endpoints
  - `Dockerfile`: Docker configuration for the Flask application
  - `requirements.txt`: Dependencies for the Flask application
  - `generate_sample_data.py`: Script to generate sample sales data
- `mysql`: Contains MySQL initialization scripts and data
  - `init/init.sql`: Creates database and tables
  - `data/`: MySQL data
- `client.py`: Command-line client to interact with the API

## API Endpoints

- **GET /api/reports**: List available sales reports
- **POST /api/upload**: Upload a new sales report
- **POST /api/process**: Process a specific sales report
- **GET /api/stats**: Get statistics from processed data

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Project

1. Clone the repository
2. Start the services:

```bash
docker-compose up -d
```

3. Generate sample data:

```bash
cd data_processor
python generate_sample_data.py
```

4. Use the client to interact with the API:

```bash
python client.py
```

### Usage Workflow

1. Business team uploads sales reports to S3 storage
2. Data team triggers processing of the sales report via API
3. Processed data is stored in MySQL for analytics and reporting

## Technologies Used

- **Storage**: MinIO (S3 compatible)
- **API Server**: Flask
- **Database**: MySQL
- **Containerization**: Docker/Docker Compose
- **Data Processing**: Pandas

## Notes
- The processed data will be *INSERTED* into the MySQL database instead of overwrited, so be careful with the data you insert.
