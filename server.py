from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
import random

load_dotenv()

# app = Flask(__name__)
app = Flask(__name__, static_folder='static', template_folder='templates')

token = os.getenv('token')
pixela_endpoint = os.getenv('pixela_endpoint')

@app.route('/')
def home():
    with open('quotes.json') as f:
        quotes = json.load(f)
    random_quote = random.choice(quotes)
    return render_template('index.html', quotes=random_quote)

# Habit Tracker Routes (from app.py)

# STEP1: CREATE ACCOUNT ON PIXELA and CREATE GRAPH

def create_pixela_user_and_graph(email,habit):
        username = f"graph{email.replace('@', 'b').replace('.', 'a')}"

        user_params = {
        "token": token,
        "username": username,
        "agreeTermsOfService": "yes",
        "notMinor": "yes",
        }

        create_account_response = requests.post(url="https://pixe.la/v1/users", json=user_params)
        print(create_account_response.text)

        # STEP2: CREATE GRAPH
        graph_id = "graph1"
        graph_config = {
            "id": graph_id,
            "name": habit,
            "unit": "times",
            "type": "int",
            "color": "kuro",
            "timezone": "Asia/Kolkata",
            "isSecret": False,
            "publishOptionalData": False
        }

        graph_endpoint = f"https://pixe.la/v1/users/{username}/graphs"

        headers = {
            "X-USER-TOKEN": token
        }
        graph_response = requests.post(graph_endpoint, json=graph_config, headers=headers)


        print("USER RESPONSE:", create_account_response.text)
        print("GRAPH RESPONSE:", graph_response.text)

        if graph_response.status_code == 200:
            return True, username, graph_id
        else:
            return False, None, None

@app.route('/reset')
def reset():
    """Clear session (for testing)"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)