# Import depdendencies
from mcp.server.fastmcp import FastMCP
import json
import requests
from typing import List

# Server created
mcp = FastMCP("churnandburn")


# Create the tool
@mcp.tool()
def PredictChurn(data: List[dict]) -> str:
    """This tool predicts whether an employee will churn or not, pass through the input as a list of samples.
    Args:
        data: employee attributes which are used for inference. Example payload

[{
"YearsAtCompany": 10,
"EmployeeSatisfaction": 0.99,
"Position": "Non-Manager",
"Salary": 5.0
}]

    Returns:
        str: 1=churn or 0 = no churn"""

    
    
    response =[{"prediction":0}]

    return json.dumps(response)


if __name__ == "__main__":
    mcp.run(transport="stdio")