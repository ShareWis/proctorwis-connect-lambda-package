# Proctorwis Connect Lambda Package

## Overview
This package provides utility functions for interacting with a MySQL database and AWS Systems Manager (SSM). It is designed to be used within Lambda functions that require database operations and secure parameter retrieval from SSM.

## Directory Structure
```
.
├── .git                             # Git repository metadata
├── README.md                        # Project documentation
├── __init__.py                      # Package initializer
├── db_utils.py                      # Database utility functions
└── ssm_utils.py                     # AWS SSM parameter retrieval utilities
```

## Features
- **Database Operations**: Perform common database tasks such as retrieving or creating organization spaces and participants.
- **SSM Parameter Retrieval**: Fetch secure parameters (e.g., database credentials) from AWS Systems Manager Parameter Store.
- **Modular Design**: Easily import and use individual utility functions in Lambda functions or other Python scripts.

## Prerequisites
- Python 3.8 or higher
- AWS CLI configured with appropriate permissions
- MySQL or MariaDB database
- Boto3 (AWS SDK for Python)
- PyMySQL (MySQL client for Python)

## Usage
### Importing Utility Functions
```python
from lambda_package import db_utils, ssm_utils
```

### Example: Retrieve Organization App by UUID
```python
import pymysql

conn = pymysql.connect(
    host='your-db-host',
    user='your-db-user',
    password='your-db-password',
    db='your-db-name',
    cursorclass=pymysql.cursors.DictCursor
)

organization_app = db_utils.get_organization_app(conn, '550e8400-e29b-41d4-a716-446655440000')
print(organization_app)
```

### Example: Retrieve Parameter from SSM
```python
parameter_value = ssm_utils.get_parameter('/ProctorWisConnect/DB_PASSWORD', 'default_value')
print(parameter_value)
```

## Function Details
### db_utils.py
- **get_organization_app**: Retrieves organization application data by UUID.
- **get_or_create_space**: Fetches or creates a space record in the database.
- **get_or_create_participant**: Fetches or creates a participant record associated with an organization and space.
- **create_face_auth_log**: Inserts a new face authentication log record into the database.

### ssm_utils.py
- **get_parameter**: Retrieves a secure parameter from AWS SSM Parameter Store. Returns a default value if the parameter does not exist.

## Notes
- Ensure that your Lambda function has IAM permissions to access AWS SSM.
- The database connection must be properly established before invoking functions from `db_utils.py`.
- Exception handling is implemented to manage database errors and missing parameters gracefully.

