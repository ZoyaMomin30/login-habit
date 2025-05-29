from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
import random

# Load environment variables
load_dotenv()

# app = Flask(__name__)
app = Flask(__name__, static_folder='static', template_folder='templates')

# Pixela configuration
token = os.getenv('token')
username = os.getenv('username')
pixela_endpoint = os.getenv('pixela_endpoint')
graph_id = "graph3"


@app.route('/')
def home():

    with open('quotes.json') as f:
        quotes = json.load(f)
    random_quote = random.choice(quotes)
    return render_template('index.html', quotes=random_quote)

# Habit Tracker Routes (from app.py)
@app.route("/create_graph", methods=["POST"])
def create_graph():
    if request.method == "POST":
        user_email = request.form.get("email")
        habit_name = request.form.get("habit")
        
        # Create a unique graph ID based on user email
        graph_id = f"graph_{user_email.replace('@', 'a').replace('.', 'b')}"
        
        # Pixela graph creation endpoint
        graph_endpoint = f"{pixela_endpoint}/{username}/graphs"
        
        headers = {
            "X-USER-TOKEN": token
        }
        
        graph_config = {
            "id": graph_id,
            "name": f"{habit_name}",
            "unit": "times",
            "type": "int",  # Green color
            "color": "kuro",
            "timezone": "Asia/Kolkata",
            "isSecret": True,
            "publishOptionalData": False
        }
    
        response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
        
        if response.status_code == 200:
            return {"status": "success", "graph_id": graph_id}
        else:
            return {"status": "error", "message": response.text}, response.status_code


@app.route("/submit", methods=["POST"])
def submit():
    if request.method=="POST":
        quantity = request.form["quantity"]
        graph_id = request.form["graph_id"]  # Get the graph_id from the form
        post_endpoint = f"{pixela_endpoint}/{username}/graphs/{graph_id}"

        headers = {"X-USER-TOKEN": token}
        today = datetime.now()

        color_param = {
            "date": today.strftime("%Y%m%d"),
            "quantity": quantity,
        }
        pixel_color_response = requests.post(url=post_endpoint, json=color_param, headers=headers)

        if pixel_color_response.status_code==200:
            return redirect('/')
        else:
            return f"Error: {pixel_color_response.text}", pixel_color_response.status_code
        
@app.route('/update_habit', methods=['POST'])
def update_habit():
    if request.method=="POST":
        graph_id= "graph1"
        today = request.form["date"]
        quantity = request.form["quantity"]
        update_endpoint = f"{pixela_endpoint}/{username}/graphs/graph3/{today}"

        headers = {"X-USER-TOKEN": token}
        today = datetime.now()

        color_param = {
            "date": today.strftime("%Y%m%d"),
            "quantity": quantity,
        }
        pixel_color_response = requests.put(url=update_endpoint, json=color_param, headers=headers)

        if pixel_color_response.status_code==200:
            return redirect('/')
        else:
            return f"Error: {pixel_color_response.text}", pixel_color_response.status_code

@app.route('/delete_habit', methods=['POST'])
def delete_habit():
    graph_id= "graph2"
    today = request.form["date"]
    if request.method=="POST":
        delete_endpoint = f"{pixela_endpoint}/{username}/graphs/{graph_id}/{today}"

        headers = {"X-USER-TOKEN": token}
        delete_response = requests.delete(url=delete_endpoint, headers=headers)

        if delete_response.status_code==200:
            return redirect('/')
        else:
            return f"Error: {delete_response.text}", delete_response.status_code
        
@app.route('/reset')
def reset():
    """Clear session (for testing)"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)