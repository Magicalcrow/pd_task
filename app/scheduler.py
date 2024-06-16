from apscheduler.schedulers.background import BackgroundScheduler
from app.services.github_service import GitHubService
from app.services.pipedrive_service import PipedriveService
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING) # for apscheduler to remove clutter
from app.config.db_config import SessionLocal
from app.models.user import User


def check_github_gists(pipedrive_api_token: str):
	db = SessionLocal()
	logging.info("Running scheduled check")
	
	try:
		users = db.query(User).all()  # Retrieve all users from the database
		for user in users:
			github_service = GitHubService(user.username)
			try:
				github_service.sync_gists(db)
			except Exception as e:
				logging.error(f"Error processing gists for user {user.username}: {e}")
	except Exception as e:
		logging.error(f"Error retrieving users: {e}")
	finally:
		db.close()
		logging.info("Scheduled check completed")

def start_scheduler(pipedrive_api_token: str):
	scheduler = BackgroundScheduler()
	scheduler.add_job(check_github_gists, 'interval', hours=3, args=[pipedrive_api_token])
	scheduler.start()
	logging.info("Scheduler started.")

import atexit
atexit.register(lambda: scheduler.shutdown())