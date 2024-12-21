from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# Charger les données des formes (lignes verticales)
file_to_read = "bearish_engulfing_bar.txt"
bearish_engulfing_bar = []
with open(file_to_read, 'r') as fichier:
    for ligne in fichier:
        bearish_engulfing_bar.append(ligne.strip())  # .strip() pour enlever les sauts de ligne
        
file_to_read = "doji_candlestick.txt"
doji_candlestick = []
with open(file_to_read, 'r') as fichier:
    for ligne in fichier:
        doji_candlestick.append(ligne.strip())  # .strip() pour enlever les sauts de ligne

# Initialisation de la liste des formes (lignes verticales)
list_of_blue_shapes = []
list_of_red_shapes = []

# Boucle pour ajouter chaque "bearish engulfing bar" (lignes bleues)
for x_value in bearish_engulfing_bar:
    line_dict = {
        'type': 'line',
        'x0': x_value, 'x1': x_value,
        'y0': 0, 'y1': 1,
        'xref': 'x', 'yref': 'paper',
        'line': {'color': 'blue', 'width': 2}
    }
    list_of_blue_shapes.append(line_dict)

# Boucle pour ajouter chaque "doji candlestick" (lignes rouges)
for x_value in doji_candlestick:
    line_dict = {
        'type': 'line',
        'x0': x_value, 'x1': x_value,
        'y0': 0, 'y1': 1,
        'xref': 'x', 'yref': 'paper',
        'line': {'color': 'red', 'width': 2}
    }
    list_of_red_shapes.append(line_dict)

# Création de l'application Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H4('Crypto analysis'),
    
    # Checklist pour afficher ou non les lignes bleues et rouges
    dcc.Checklist(
        id='toggle-lines',
        options=[
            {'label': 'Bearish Engulfing Bar (Blue)', 'value': 'show_blue_lines'},
            {'label': 'Doji Candlestick (Red)', 'value': 'show_red_lines'}
        ],
        value=[],  # Par défaut, aucune ligne n'est affichée
        inline=True
    ),
    
    # Graphique
    dcc.Graph(
        id="graph",
        style={'width': '80%', 'height': '500px', 'margin': '0 auto'}  # Largeur ajustée à 80% et centré
    ),
])

@app.callback(
    Output("graph", "figure"), 
    [Input("toggle-lines", "value")]
)
def display_candlestick(lines_visibility):
    df = pd.read_csv("./data_crypto.txt")  # Assurez-vous que votre fichier de données existe et est bien formatté
    fig = go.Figure(go.Candlestick(
        x=df['OpenTime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'], 
        name="Price"
    ))

    # Déterminer les formes à afficher en fonction des options choisies dans la checklist
    shapes_to_use = []
    
    if 'show_blue_lines' in lines_visibility:
        shapes_to_use.extend(list_of_blue_shapes)  # Ajouter les lignes bleues
    if 'show_red_lines' in lines_visibility:
        shapes_to_use.extend(list_of_red_shapes)  # Ajouter les lignes rouges

    fig.update_layout(
        title=dict(text='BTCUSDT'),
        yaxis=dict(
            title=dict(text='Price $')
        ),
        shapes=shapes_to_use,  # Utilisation des formes selon les choix de la checklist
        template='plotly_dark',  # Application du mode sombre
    )

    return fig

# Lancer le serveur
app.run_server(debug=True)
