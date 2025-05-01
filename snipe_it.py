import os
import requests
from dotenv import load_dotenv
import time
# Load environment variables from .env file
load_dotenv()

import os
import requests
def find_asset_by_tag_or_serial(asset_tag=None, serial=None):
    SNIPE_IT_URL = os.getenv("SNIPE_IT_URL")
    API_TOKEN = os.getenv("SNIPE_IT_API_KEY")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    search_fields = []
    if asset_tag:
        search_fields.append(("asset_tag", asset_tag))
    if serial:
        search_fields.append(("serial", serial))

    for field_name, value in search_fields:
        response = requests.get(
            f"{SNIPE_IT_URL}/api/v1/hardware",
            headers=headers,
            params={"search": value}
        )

        if response.status_code == 200:
            for item in response.json().get("rows", []):
                if item.get(field_name) == value:
                    return item["id"]

    return None


def get_or_create_entity(entity_type, name, additional_fields=None):
    """
    Gets or creates an entity by name from Snipe-IT.

    Args:
        entity_type (str): The type of entity (e.g., "models", "statuses", "companies").
        name (str): The name of the entity.
        additional_fields (dict, optional): Additional fields required to create the entity.

    Returns:
        int: The ID of the entity.

    Raises:
        Exception: If the entity cannot be retrieved or created.
    """
    SNIPE_IT_URL = os.getenv("SNIPE_IT_URL")
    API_TOKEN = os.getenv("SNIPE_IT_API_KEY")

    if not SNIPE_IT_URL or not API_TOKEN:
        raise ValueError("SNIPE_IT_URL and API_TOKEN must be set in the .env file.")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Search for the entity by name
    print(f"Searching for {entity_type} with name: {name}")
    response = requests.get(f"{SNIPE_IT_URL}/api/v1/{entity_type}", headers=headers, params={"search": name})

    if response.status_code == 200:
        results = response.json().get("rows", [])
        for result in results:
            if result.get("name") == name:
                print(f"Found {entity_type[:-1]} with ID: {result.get('id')}")
                return result.get("id")
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 10))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return get_or_create_entity(entity_type, name, additional_fields)

    # Create the entity if not found
    payload = {"name": name}
    if additional_fields:
        payload.update(additional_fields)

    print(f"Creating new {entity_type[:-1]} with name: {name}")
    post_response = requests.post(f"{SNIPE_IT_URL}/api/v1/{entity_type}", headers=headers, json=payload)
    print(f"POST Response Status Code: {post_response.status_code}")
    print(f"POST Response Text: {post_response.text}")

    if post_response.status_code in [200, 201]:
        return post_response.json()["payload"]["id"]

    raise Exception(f"Failed to create {entity_type[:-1]} '{name}'.")

def post_hardware_to_snipe_it(hardware_data):
    SNIPE_IT_URL = os.getenv("SNIPE_IT_URL")
    API_TOKEN = os.getenv("SNIPE_IT_API_KEY")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    asset_id = find_asset_by_tag_or_serial(
        asset_tag=hardware_data.get("asset_tag"),
        serial=hardware_data.get("serial")
    )
    if asset_id:
        print(f"Asset already exists. Updating asset ID: {asset_id}")
        put_url = f"{SNIPE_IT_URL}/api/v1/hardware/{asset_id}"
        hardware_data.pop("serial")
        hardware_data.pop('status_id')
        response = requests.put(put_url, json=hardware_data, headers=headers)
    else:
        print(f"Creating new asset.")
        response = requests.post(f"{SNIPE_IT_URL}/api/v1/hardware", json=hardware_data, headers=headers)

    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 10))
        print(f"Rate limit hit. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return post_hardware_to_snipe_it(hardware_data)

    if response.status_code in [200, 201]:
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "status_code": response.status_code, "error": response.text}

# Example usage
if __name__ == "__main__":
    model_name = "Example Model"
    status_name = "Ready to Deploy"
    company_name = "Example Company"

    try:
        model_id = get_or_create_entity("models", model_name, {"name": model_name})

        hardware_data = {
            "name": "Example Hardware",
            "serial": "123456789",
            "model_id": model_id,
            "status_id": 2,
            "company_id": 1
        }

        result = post_hardware_to_snipe_it(hardware_data)
        if result["success"]:
            print("Hardware information posted successfully:", result["data"])
        else:
            print("Failed to post hardware information:", result["status_code"], result["error"])
    except Exception as e:
        print("Error:", str(e))