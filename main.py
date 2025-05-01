from meraki_api import *
import snipe_it
import time

def map_meraki_to_snipeit(device):
    """
    Maps a Meraki device's data to Snipe-IT fields.

    Args:
        device (dict): A dictionary containing Meraki device details.

    Returns:
        dict: A dictionary formatted for Snipe-IT.
    """
    model_name = device.get("model")
    product_type = device.get('productType')
    category = snipe_it.get_or_create_entity("categories", product_type, {"category_type": "asset"})

    model_id = snipe_it.get_or_create_entity("models", model_name, {"category_id": category})
    if not model_id:
        raise Exception(f"Model ID could not be retrieved or created for model: {model_name}")

    return {
        "name": device.get("name"),
        "serial": device.get("serial"),
        "asset_tag": device.get("serial"),
        "model_id": model_id,
        "category": category,
        "status_id": 2,
        "purchase_date": device.get("purchase_date", None),
        "purchase_cost": device.get("purchase_cost", None),
        "notes": f"Imported from Meraki. MAC: {device.get('mac')}, Network ID: {device.get('networkId')}"
    }

if __name__ == '__main__':

    try:
        # Get or create the necessary entities in Snipe-IT


        # Fetch devices from Meraki API
        devices = device_details()  # Assuming `get_meraki_devices` fetches device details from Meraki

        # Iterate over devices and post to Snipe-IT
        for device in devices:
            time.sleep(0.5)
            print(f"Processing device: {device.get('name')}")
            snipeit_data = map_meraki_to_snipeit(device)
            print("Device Info Retrived Meraki")
            response = snipe_it.post_hardware_to_snipe_it(snipeit_data)
            if response["success"]:
                print(f"Successfully imported device: {device.get('name')}")
            else:
                print(f"Failed to import device: {device.get('name')}. Error: {response['error']}")

        print("Device import completed.")
    except Exception as e:
        print("Error:", str(e))