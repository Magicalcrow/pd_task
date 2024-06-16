from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.config.db_config import get_db
from app.services.github_service import GitHubService
from app.services.pipedrive_service import PipedriveService
pipedrive_service = PipedriveService()
from app.models.gist import Gist
from app.models.user import User
from app.db.schemas import GistBase, UserBase, UserWithGists
import requests
from datetime import datetime

router = APIRouter()

@router.get("/gists/{username}")
def get_gists(username: str, db: Session = Depends(get_db)):
	github_service = GitHubService(username)
	try:
		user = db.query(User).filter(User.username == username).first()
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		gists = db.query(Gist).filter(Gist.user_id == user.id, Gist.is_new == True).all()
		
		# Set all gists to false (to show that they are old)
		for gist in gists:
			gist.is_new = False
		db.commit()
		new_gists_dict = [gist.to_dict() for gist in gists]
		return new_gists_dict
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.get("/gists/{username}/new")
def get_new_gists(username: str, db: Session = Depends(get_db)):
	github_service = GitHubService(username)
	try:
		new_gists = github_service.sync_gists(db)
		new_gists_dict = [gist.to_dict() for gist in new_gists]
		return new_gists_dict
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
	users = db.query(User).all()
	new_users = [user.to_dict() for user in users]
	return new_users

@router.delete("/gists/delete_random")
def delete_random_gist(db: Session = Depends(get_db)):
	try:
		random_gist = db.query(Gist).order_by(func.random()).first()
		
		if random_gist:
			if pipedrive_service.delete_activity(random_gist.pipedrive_id):
				db.delete(random_gist)
				db.commit()
				return {"message": "Random gist deleted successfully", "gist_id": random_gist.id}
		else:
			raise HTTPException(status_code=404, detail="No gists available to delete")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/users/{user_name}")
def delete_user(username: str, db: Session = Depends(get_db)):
	try:
		user = db.query(User).filter(User.username == username).first()
		if not user:
			raise HTTPException(status_code=404, detail="User not found")

		# Delete associated gists
		gists = db.query(Gist).filter(Gist.user_id == user.id).all()
		pd_ids_delete = []
		for gist in gists:
			pd_ids_delete.append(gist.pipedrive_id)
		if pipedrive_service.delete_activity_bulk(str(pd_ids_delete)[1:-1]):
			for gist in gists:
				db.delete(gist)
			db.commit()
			db.delete(user)
			db.commit()
			return {"message": "User deleted successfully"}
		raise HTTPException(status_code=500, detail="Error deleting from pipedrive")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/github/rate_limit")
def get_github_rate_limit():
	try:
		response = requests.get("https://api.github.com/rate_limit")
		response.raise_for_status()
	except Exception as e:
		raise HTTPException(status_code=500, detail="Error fetching rate limit information")

	data = response.json()
	reset_timestamp = data['resources']['core']['reset']
	remaining = data['resources']['core']['remaining']

	# Calculate the time until reset
	reset_time = datetime.utcfromtimestamp(reset_timestamp)
	current_time = datetime.utcnow()
	time_until_reset = reset_time - current_time
	time_until_reset_str = str(time_until_reset)
	return {"time_until_reset": time_until_reset_str, "with remaining": remaining}