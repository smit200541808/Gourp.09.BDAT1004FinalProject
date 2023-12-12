from flask import Flask
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pymongo
import re
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('mongodb+srv://200541808:IqqPvMpTys2uLQWa@cluster1111.p6rdc1z.mongodb.net/')
db = client['sales_database']
collection_names = db.list_collection_names()

# Extract dates from collection names and convert to datetime objects
date_list = [re.search(r'\d{4}-\d{2}-\d{2}', collection_name).group(0) for collection_name in collection_names]
date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in date_list]

# Set the default min date to '2023-06-01'
default_min_date = datetime(2023, 6, 1)

# Find the min and max dates
min_date = max(min(date_objects), default_min_date)
max_date = datetime.now()

# Combine collections within the date range
combined_data = []
for collection_name, date_object in zip(collection_names, date_objects):
    if min_date <= date_object <= max_date:
        collection = db[collection_name]
        data = list(collection.find())
        combined_data.extend(data)

df = pd.DataFrame(combined_data)
df['Quantity'] = df['Quantity'].abs()
df['Date'] = pd.to_datetime(df['Date'])
df['TotalSales'] = df['Quantity'] * df['Price']
# Initialize Flask app and Dash app
server = Flask(__name__)
app = Dash(__name__, server=server)

# Layout of the dashboard
app.layout = html.Div(children=[
    html.H1(children='Sales Dashboard', style={'textAlign': 'center', 'color': 'white'}),

    # Total Sales Over Time for Top 10 Products
    dcc.Graph(
        id='total-sales-over-time',
        figure={
            'data': [
                px.line(df, x='Date', y='TotalSales', color='ProductName',
                        title='Total Sales Over Time for Top 10 Products').update_layout(
                    paper_bgcolor='#1e1e1e',
                    plot_bgcolor='#1e1e1e',
                    font={'color': 'white'})
            ],
        }
    ),

    # Quantity Sold Over Time for Top Products
    dcc.Graph(
        id='quantity-sold-over-time',
        figure={
            'data': [
                px.line(df, x='Date', y='Quantity', color='ProductName',
                        title='Quantity Sold Over Time for Top Products').update_layout(
                    paper_bgcolor='#1e1e1e',
                    plot_bgcolor='#1e1e1e',
                    font={'color': 'white'})
            ],
        }
    ),

    # Total Sales per Country on World Map
    dcc.Graph(
        id='total-sales-per-country',
        figure={
            'data': [
                px.choropleth(df, locations='Country', color='TotalSales',
                              title='Total Sales per Country', color_continuous_scale='Viridis',
                              labels={'TotalSales': 'Total Sales'}, hover_name='Country').update_geos(
                    showcoastlines=True, coastlinecolor="Black").update_layout(
                    paper_bgcolor='#1e1e1e',
                    plot_bgcolor='#1e1e1e',
                    font={'color': 'white'})
            ],
        }
    ),

    # Product Price Distribution Over Time for Top Products
    dcc.Graph(
        id='product-price-distribution',
        figure={
            'data': [
                px.box(df[df['ProductName'].isin(df['ProductName'].value_counts().index[:5])],
                       x='ProductName', y='Price',
                       title='Product Price Distribution Over Time for Top Products').update_layout(
                    paper_bgcolor='#1e1e1e',
                    plot_bgcolor='#1e1e1e',
                    font={'color': 'white'})
            ],
        }
    ),

    # Total Sales Distribution Among Top 10 Products
# Total Sales Distribution Among Top 10 Products
dcc.Graph(
    id='total-sales-distribution',
    figure={
        'data': [
            px.pie(names=df['ProductName'].value_counts().head(10).index,
                   values=df['ProductName'].value_counts().head(10).values,
                   title='Total Sales Distribution Among Top 10 Products',
                   labels=[f"{label} ({percent:.1%})" for label, percent in zip(df['ProductName'].value_counts().head(10).index,
                                                                                 df['ProductName'].value_counts().head(10).values / df['ProductName'].value_counts().head(10).values.sum())],
                   startangle=90).update_layout(
                paper_bgcolor='#1e1e1e',
                plot_bgcolor='#1e1e1e',
                font={'color': 'white'})
        ],
    }
),

])

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
