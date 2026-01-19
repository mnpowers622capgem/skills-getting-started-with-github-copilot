"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess": {
        "capacity": 20,
        "signup": [],
        "description": "Improve strategic thinking and problem-solving through weekly chess matches and tutorials.",
        "schedule": "Tuesdays 3:30 PM - 5:00 PM, Room 204",
    },
    "Drama": {
        "capacity": 16,
        "signup": [],
        "description": "Participate in acting workshops and school theater productions.",
        "schedule": "Thursdays 3:30 PM - 5:30 PM, Auditorium",
    },
    "Robotics": {
        "capacity": 10,
        "signup": [],
        "description": "Design, build, and program robots for competitions and exhibitions.",
        "schedule": "Mondays 3:30 PM - 5:30 PM, Lab 3",
    },
    "Geology": {
        "capacity": 15,
        "signup": [],
        "description": "Explore rocks, minerals, and earth sciences through hands-on activities.",
        "schedule": "Wednesdays 3:30 PM - 5:00 PM, Room 118",
    },
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Get the specific activity
    activity = activities[activity_name]
# Validate student is not already signed up

    # Add student
    activity["signup"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
