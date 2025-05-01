import meraki
import json
from dotenv import load_dotenv
import os
load_dotenv()

# Access the environment variables
API_KEY = os.getenv("MERAKI_API_KEY")
organization_id = os.getenv("ORGANIZATION_ID")





# Defining your API key as a variable in source code is discouraged.
# This API key is for a read-only docs-specific environment.
# In your own code, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/


def device_details():
    dashboard = meraki.DashboardAPI(API_KEY)

    response = dashboard.organizations.getOrganizationDevices(
        organization_id, all
    )
    return response
