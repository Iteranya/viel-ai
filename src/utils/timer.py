# scheduler.py
import json
import uuid
import time
import threading
from datetime import datetime
from src.controller.plugin_registry import plugin
SCHEDULE_FILE = 'schedules.json'

try:
    with open(SCHEDULE_FILE, 'x') as f:
        json.dump([], f)
except FileExistsError:
    pass

def load_schedules():
    with open(SCHEDULE_FILE, 'r') as f:
        return json.load(f)

def save_schedules(schedules):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedules, f, indent=2)

def schedule(timestamp):
    task_id = str(uuid.uuid4())
    task = {'id': task_id, 'timestamp': timestamp, 'fired': False}
    schedules = load_schedules()
    schedules.append(task)
    save_schedules(schedules)
    print(f"Scheduled task {task_id} at {timestamp}")

#@plugin
def schedule_task(year, month, day, hour, minute):
    """
    Schedules a task to run at a specific date and time by creating an ISO 8601 timestamp.

    This function wraps up the datetime creation and calls an underlying `schedule()` function,
    which is presumably responsible for actually queuing the task or sending it to a scheduler.

    Parameters:
        year (int): The year (e.g., 2025)
        month (int): The month (1–12)
        day (int): The day of the month (1–31)
        hour (int): The hour in 24-hour format (0–23)
        minute (int): The minute (0–59)

    Returns:
        None

    Example:
        schedule_task(2025, 7, 10, 14, 30)
        # Schedules the task for July 10, 2025 at 2:30 PM.

    Warning:
        No validation is performed on the input values — invalid dates will raise exceptions faster than you can say
        “February 30th.”
    """
    dt = datetime(year, month, day, hour, minute)
    schedule(dt.isoformat())


def do_the_thing(task):
    print(f"🔥 Firing task {task['id']} at {datetime.now().isoformat()} - Doing the thing!")

def check_schedules():
    while True:
        now = datetime.now()
        schedules = load_schedules()
        updated = False
        for task in schedules:
            if not task['fired'] and datetime.fromisoformat(task['timestamp']) <= now:
                do_the_thing(task)
                task['fired'] = True
                updated = True
        if updated:
            save_schedules(schedules)
        time.sleep(60)

def list_schedules():
    schedules = load_schedules()
    if not schedules:
        print("No schedules found.")
    else:
        print("Current schedules:")
        for task in schedules:
            status = '✅ Fired' if task['fired'] else '🕒 Pending'
            print(f"- ID: {task['id']}, Time: {task['timestamp']}, Status: {status}")

def start_scheduler():
    thread = threading.Thread(target=check_schedules, daemon=True)
    thread.start()
    print("⏰ Scheduler started!")