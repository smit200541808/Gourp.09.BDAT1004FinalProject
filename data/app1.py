import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime
from pymongo import MongoClient
import re

def connect_to_mongodb():
    client = MongoClient('mongodb+srv://200541808:IqqPvMpTys2uLQWa@cluster1111.p6rdc1z.mongodb.net/')
    return client['sales_database']

def get_combined_data(db, min_date, max_date):
    collection_names = db.list_collection_names()
    
    date_objects = [datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}', name).group(0), '%Y-%m-%d') for name in collection_names]
    
    combined_data = []
    for name, date_object in zip(collection_names, date_objects):
        if min_date <= date_object <= max_date:
            collection = db[name]
            data = list(collection.find())
            combined_data.extend(data)
    
    df = pd.DataFrame(combined_data)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').abs()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Total Sales'] = df['Quantity'] * df['Price']
    
    return df

def get_top_n_items(data, column, n):
    return data.groupby(column)['Total Sales'].sum().nlargest(n)

def create_pie_chart(data, title, labels=None):
    return px.pie(data, values='Total Sales', names=labels if labels else data.index, title=title)

# def create_pie_chart_figure(df, selection):
#     if selection == 'Country':
#         top_10_data = get_top_n_items(df, 'Country', 10)
#         title = 'Top 10 Countries by Sales'
#     elif selection == 'Product':
#         total_sales_per_product = df.groupby('ProductName')['Quantity'].sum().reset_index()
#         top_10_data = total_sales_per_product.sort_values(by='Quantity', ascending=False).head(10)
#         title = 'Top 10 Products by Sales'
#     else:
#         top_10_data = pd.DataFrame()
#         title = ''

#     return create_pie_chart(top_10_data, title)

def create_bar_chart(data, x, y, title, labels=None):
    return px.bar(data, x=x, y=y, title=title, labels=labels)

def create_line_chart(data, x, y, color, title):
    return px.line(data, x=x, y=y, color=color, title=title)

def create_choropleth_map(data, locations, locationmode, color, title, color_continuous_scale):
    return px.choropleth(data, locations=locations, locationmode=locationmode, color=color,
                         title=title, color_continuous_scale=color_continuous_scale)

def create_pie_chart_figure(df, selection):
    if selection == 'Country':
        top_10_data = get_top_n_items(df, 'Country', 10)
        title = 'Top 10 Countries by Sales'
        return px.pie(top_10_data, values='Total Sales', names=top_10_data.index, title=title)

    elif selection == 'Product':
        total_sales_per_product = df.groupby('ProductName')['Total Sales'].sum().reset_index()
        top_10_data = total_sales_per_product.sort_values(by='Total Sales', ascending=False).head(10)
        title = 'Top 10 Products by Sales'
        return px.pie(top_10_data, values='Total Sales', names='ProductName', title=title)

    else:
        # If neither 'Country' nor 'Product' is selected, return country pie chart by default
        total_sales_per_country = df.groupby('Country')['Total Sales'].sum().reset_index()
        title = 'Total Sales by Country'
        return px.pie(total_sales_per_country, values='Total Sales', names='Country', title=title)


def create_dash_app_layout(df):
    # Custom styling for charts
    chart_style = {
        'height': '400px',
        'margin': {'t': 10, 'b': 10, 'r': 10, 'l': 10},
        'template': 'plotly_dark'
    }

    # Set overall style for the app
    return html.Div([
        html.H1("Sales Dashboard", style={'color': 'white', 'text-align': 'center', 'margin-top': '20px'}),

        html.Div([
            dcc.Dropdown(
                id='pie-chart-dropdown',
                options=[
                    {'label': 'Top 10 Countries by Sales', 'value': 'Country'},
                    {'label': 'Top 10 Products by Sales', 'value': 'Product'},
                ],
                value='Country',
                style={'width': '50%'}
            ),
            dcc.Graph(id='pie-chart'),
        ], className='row'),

        html.Div([
            
            html.Div(dcc.Graph(id='bar-chart', figure=create_bar_chart(df, 'ProductName', 'Quantity', 'Total Sales for Top 10 Products', {'Quantity': 'Total Sales'})), className='six columns', style=chart_style),
            html.Div(dcc.Graph(id='line-chart', figure=create_line_chart(df, 'Date', 'Total Sales', 'ProductName', 'Total Sales Over Time for Top 10 Products')), className='six columns', style=chart_style),
        ], className='row'),

        html.Div([
            html.Div(dcc.Graph(id='world-map', figure=create_choropleth_map(df, 'Country', 'country names', 'Total Sales', 'Total Sales by Country', 'Viridis')), className='twelve columns', style=chart_style),
        ], className='row'),

    ], style={'backgroundColor': '#1E1E1E', 'color': 'white', 'padding': '20px'})  # Set background color and text color for the entire app

def run_dash_app(app):
    app.run_server(debug=True)

def main():
    # MongoDB Connection
    db = connect_to_mongodb()

    # Date Range
    
    min_date = datetime(2023, 12, 1)
    max_date = datetime.now()

    # Combined Data
    df = get_combined_data(db, min_date, max_date)

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Set layout
    app.layout = create_dash_app_layout(df)

    # Callback to update pie chart based on dropdown selection
    @app.callback(
        Output('pie-chart', 'figure'),
        [Input('pie-chart-dropdown', 'value')]
    )
    def update_pie_chart(selection):
        return create_pie_chart_figure(df, selection)

    # Run the app
    run_dash_app(app)

if __name__ == '__main__':
    main()
