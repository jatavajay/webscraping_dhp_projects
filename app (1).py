from flask import Flask, send_from_directory, jsonify
import csv
from datetime import datetime
from collections import defaultdict
import random
import math
import os

app = Flask(__name__, static_folder='static')

def generate_growth_pattern(base_count, years):
    """Generate a more realistic growth pattern with variations"""
    counts = []
    # Different growth patterns for different base counts
    if base_count > 1500:  # Very popular tags (like Python)
        for year_index in range(4):
            growth = 0.4 + (math.log(year_index + 2) * 0.3)  # Logarithmic growth
            variation = random.uniform(0.95, 1.05)  # Add 5% random variation
            count = int(base_count * growth * variation)
            counts.append(count)
    elif base_count > 800:  # Moderately popular tags
        for year_index in range(4):
            growth = 0.4 + (year_index * 0.18) + random.uniform(-0.05, 0.05)
            count = int(base_count * growth)
            counts.append(count)
    else:  # Less popular tags
        for year_index in range(4):
            # More volatile growth for less popular tags
            growth = 0.4 + (year_index * 0.15) + random.uniform(-0.1, 0.15)
            count = int(base_count * growth)
            counts.append(count)
    return counts

def process_csv():
    # Read and process CSV data
    tag_counts = defaultdict(int)
    year_tag_counts = defaultdict(lambda: defaultdict(int))
    
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'combined.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Clean the tag by removing extra quotes
            tag = row['Tag'].strip('"')
            # Extract year from Posted Time
            year = row['Posted Time'].split('-')[0]  # Get just the year part
            
            tag_counts[tag] += 1
            year_tag_counts[year][tag] += 1
    
    # Get top 10 tags
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_tags = [tag for tag, _ in top_tags]
    
    # Prepare data for the chart
    years = sorted(year_tag_counts.keys())
    datasets = []
    
    # Generate random colors for each tag
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF9F40'
    ]
    
    for idx, tag in enumerate(top_tags):
        data = [year_tag_counts[year][tag] for year in years]
        datasets.append({
            'label': tag,
            'data': data,
            'borderColor': colors[idx],
            'backgroundColor': colors[idx],
            'tension': 0.1,
            'fill': False
        })
    
    return {
        'years': years,
        'datasets': datasets
    }

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/data')
def get_data():
    try:
        data = process_csv()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=3000) 