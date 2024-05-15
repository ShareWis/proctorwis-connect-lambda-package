from typing import Optional, Any

import logging
import boto3

logger = logging.getLogger(__name__)

def get_parameter(param_key: str, default_value: Optional[Any] = None) -> Optional[str]:
    """
    Retrieves a parameter value from AWS Systems Manager (SSM) Parameter Store.
    If the parameter is not found, returns the default value. If an error occurs, raises the exception.

    Parameters:
    param_key (str): The key of the parameter to retrieve.
    default_value (Optional[Any]): The value to return if the parameter is not found. Default is None.

    Returns:
    Optional[str]: The value of the parameter if found, otherwise the default value.

    Raises:
    Exception: If an error occurs while retrieving the parameter.
    """
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter
    ssm = boto3.client('ssm')

    try:
        response = ssm.get_parameter(
            Name=param_key,
            WithDecryption=True
        )
    except ssm.exceptions.ParameterNotFound:
        logger.warning("Parameter {%s} not found. Returning default value.", param_key)
        return default_value
    except Exception as e:
        raise

    return response['Parameter']['Value']
