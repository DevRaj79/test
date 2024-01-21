from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
from bs4 import BeautifulSoup
import html

app = Flask(__name__)
socketio = SocketIO(app)

# Function to perform web scraping with keyword filtering
def scrape_website(url, tag, num_lines=5):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad HTTP responses
        soup = BeautifulSoup(response.text, 'html.parser')
        data = [html.escape(link.text) for link in soup.find_all(tag) if 'diode' in link.text][:num_lines]
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data. Error: {e}")
        data = []
    return data

@app.route('/')
def index():
    return render_template('test.html')

@socketio.on('message_from_client')
@socketio.on('url_from_client')
def handle_message(url, tag):
    print('Received message from client:',tag)
    
    # Perform web scraping for the first 5 lines containing the keyword
    scraped_data = scrape_website(url, tag, num_lines=5)
    
    # Send the scraped data line by line to the client
    for line in scraped_data:
        socketio.emit('message_from_server', f'<a>{line}</a>')
        socketio.sleep(0.1)  # Add a small delay to simulate asynchronous processing

if __name__ == '__main__':
    socketio.run(app, debug=True)
