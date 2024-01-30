import dash
from dash import html
from dash_cytoscape import Cytoscape

# Your DOT code remains the same
dot_code = """
digraph Example {
  A -> B;
  B -> C;
  C -> A;
}
"""

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    Cytoscape(
        id='graph',
        layout={'name': 'circle'},
        style={'width': '100%', 'height': '600px'},
        elements=[
            {'data': {'id': 'A'}},
            {'data': {'id': 'B'}},
            {'data': {'id': 'C'}},
            {'data': {'id': 'AB', 'source': 'A', 'target': 'B'}},
            {'data': {'id': 'BC', 'source': 'B', 'target': 'C'}},
            {'data': {'id': 'CA', 'source': 'C', 'target': 'A'}}
        ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
