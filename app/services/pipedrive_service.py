import requests
import logging
logging.basicConfig(level=logging.INFO)
import os

class PipedriveService:
	def __init__(self):
		self.api_token = os.getenv("PIPEDRIVE_API_TOKEN")
		self.base_url = "https://amogus2.pipedrive.com/api/v1"
	
	def create_activity(self, subject: str):
		url = f"{self.base_url}/activities?api_token={self.api_token}"
		data = {
			"subject": subject,
			"type": "Task",
			# 'email':email
		}
		response = requests.post(url, json=data)
		if response.status_code == 201:
			result = response.json()
			if 'data' in result and 'id' in result['data']:
				logging.info(f"Activity was added successfully with ID {result['data']['id']}")

				return result['data']['id']
			else:
				logging.error("Adding activity failed: No ID returned")
				raise Exception("Adding activity failed: No ID returned")
		else:
			raise Exception("Adding activity fail")

	def delete_activity(self, pd_id: int):
		response = requests.delete(f"{self.base_url}/activities/{pd_id}?api_token={self.api_token}")
		if response.status_code == 200:
			result = response.json()
			if 'data' in result and result['success'] == True:
				logging.info(f"Activity was deleted successfully with ID {pd_id}")

				return result['success']
			else:
				logging.error("Deleting activity failed: No success returned")
				raise Exception("Deleting activity failed: No success returned")
		else:
			raise Exception("Deleting activity fail")

	
	def delete_activity_bulk(self, pd_ids: int):
		url = f"{self.base_url}/activities?api_token={self.api_token}"
		data = {
			"ids": pd_ids,
		}
		response = requests.delete(url, json=data)
		if response.status_code == 200:
			result = response.json()
			if 'data' in result and result['success'] == True:
				logging.info(f"Activities were deleted successfully with IDs {pd_ids}")

				return result['success']
			else:
				logging.error("Deleting activities failed: No success returned")
				raise Exception("Deleting activities failed: No success returned")
		else:
			raise Exception("Deleting activities failed")