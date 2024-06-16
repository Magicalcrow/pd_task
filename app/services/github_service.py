import requests
from sqlalchemy.orm import Session
from app.models.gist import Gist
from app.models.user import User
from app.services.pipedrive_service import PipedriveService
pipedrive_service = PipedriveService()
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING) # for apscheduler to remove clutter

class GitHubService:
	def __init__(self, username: str):
		self.username = username
		self.base_url = f"https://api.github.com/users/{username}/gists"

	def get_gists(self):
		response = requests.get(self.base_url)
		if response.status_code == 200:
			return response.json()
		else:
			response.raise_for_status()

	def sync_gists(self, db: Session):
		new_gists = []
		try:
			fetched_gists = self.get_gists()
			fetched_gist_ids = {gist['id'] for gist in fetched_gists}

			# Get all stored gists for the user
			user = db.query(User).filter(User.username == self.username).first()
			if not user:
				user = User(username=self.username)
				db.add(user)
				db.commit()
				db.refresh(user)

			stored_gists = db.query(Gist).filter_by(user_id=user.id).all()
			stored_gist_ids = {gist.gist_id for gist in stored_gists}

			# Add new gists
			new_gist_ids = fetched_gist_ids - stored_gist_ids
			for gist_id in new_gist_ids:
				gist_data = next(gist for gist in fetched_gists if gist['id'] == gist_id)
				new_gist = Gist(
					gist_id=gist_data['id'],
					description=gist_data['description'],
					user_id=user.id
				)
				title = new_gist.description if new_gist.description else "No_description"
				pd_id = pipedrive_service.create_activity(subject=title)
				if pd_id:
					new_gist.pipedrive_id = pd_id
					new_gists.append(new_gist)
					db.add(new_gist)
					db.commit()
					logging.info(f"Processed gist: {title}, user_id: {new_gist.user_id}")
			# Delete removed gists
			removed_gist_ids = stored_gist_ids - fetched_gist_ids
			for gist_id in removed_gist_ids:
				gist_to_delete = db.query(Gist).filter_by(gist_id=gist_id).first()
				if gist_to_delete:
					if pipedrive_service.delete_activity(gist_to_delete.pipedrive_id):
						db.delete(gist_to_delete)
						db.commit()
						logging.info(f"Deleted gist: {gist_to_delete.description}, user_id: {gist_to_delete.user_id}")

		except Exception as e:
			logging.error(f"Error processing gists for user {self.username}: {e}")

		return new_gists