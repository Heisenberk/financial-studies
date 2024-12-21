from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# Constants for identifying the candlestick patterns
BEARISH_ENGULFING_BAR = 1
DOJI_CANDLESTICK = 1

# Function to load vertical lines data (bearish engulfing and doji candlestick patterns)
def load_patterns():
    # Load Bearish Engulfing Bar data
    bearish_engulfing_bar = []
    with open("bearish_engulfing_bar.txt", 'r') as file:
        for line in file:
            bearish_engulfing_bar.append(line.strip())  # Removing newlines

    # Load Doji Candlestick data
    doji_candlestick = []
    with open("doji_candlestick.txt", 'r') as file:
        for line in file:
            doji_candlestick.append(line.strip())  # Removing newlines

    return bearish_engulfing_bar, doji_candlestick

# Function to create shapes (vertical lines) for the candlestick patterns
def create_shapes(bearish_engulfing_bar, doji_candlestick):
    list_of_blue_shapes = []
    list_of_red_shapes = []

    # Create blue shapes for Bearish Engulfing Bars
    for x_value in bearish_engulfing_bar:
        line_dict = {
            'type': 'line',
            'x0': x_value, 'x1': x_value,
            'y0': 0, 'y1': 1,
            'xref': 'x', 'yref': 'paper',
            'line': {'color': 'blue', 'width': 2}
        }
        list_of_blue_shapes.append(line_dict)

    # Create red shapes for Doji Candlesticks
    for x_value in doji_candlestick:
        line_dict = {
            'type': 'line',
            'x0': x_value, 'x1': x_value,
            'y0': 0, 'y1': 1,
            'xref': 'x', 'yref': 'paper',
            'line': {'color': 'red', 'width': 2}
        }
        list_of_red_shapes.append(line_dict)

    return list_of_blue_shapes, list_of_red_shapes

# Function to create the Dash app layout
def create_layout():
    return html.Div([
        html.H4('Crypto analysis'),
        
        # Checklist to toggle blue and red lines visibility
        dcc.Checklist(
            id='toggle-lines',
            options=[
                {'label': 'Bearish Engulfing Bar (Blue)', 'value': 'show_blue_lines'},
                {'label': 'Doji Candlestick (Red)', 'value': 'show_red_lines'}
            ],
            value=[],  # Default, no lines are shown
            inline=False  # Set to False to have options on separate lines
        ),
        
        # Graph to display the candlestick chart
        dcc.Graph(
            id="graph",
            style={'width': '80%', 'height': '500px', 'margin': '0 auto'}  # 80% width and centered
        ),
    ])

# Main function to run the app
def main():
    # Create the Dash app instance here
    app = Dash(__name__)

    # Load the candlestick patterns
    bearish_engulfing_bar, doji_candlestick = load_patterns()

    # Create shapes for the patterns
    list_of_blue_shapes, list_of_red_shapes = create_shapes(bearish_engulfing_bar, doji_candlestick)

    # Define the layout of the app
    app.layout = create_layout()

    # Callback function to update the figure based on checklist input
    @app.callback(
        Output("graph", "figure"), 
        [Input("toggle-lines", "value")]
    )
    def display_candlestick(lines_visibility):
        # Load the crypto data from CSV
        df = pd.read_csv("./data_crypto.txt")  # Make sure the file is correctly formatted

        # Create the candlestick chart
        fig = go.Figure(go.Candlestick(
            x=df['OpenTime'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        ))

        # Determine which shapes (lines) to display based on the selected options
        shapes_to_use = []
        
        if 'show_blue_lines' in lines_visibility:
            shapes_to_use.extend(list_of_blue_shapes)  # Add the blue lines for Bearish Engulfing Bars
        if 'show_red_lines' in lines_visibility:
            shapes_to_use.extend(list_of_red_shapes)  # Add the red lines for Doji Candlesticks

        # Update the layout with the selected shapes
        fig.update_layout(
            title=dict(text='BTCUSDT'),
            yaxis=dict(
                title=dict(text='Price $')
            ),
            shapes=shapes_to_use,  # Use the selected shapes
            template='plotly_dark',  # Apply dark theme
        )

        return fig

    # Run the Dash app
    app.run_server(debug=True)

# Entry point of the program
if __name__ == "__main__":
    main()
