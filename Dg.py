import dash
from dash import html
from dash_cytoscape import Cytoscape

def create_cytoscape_graph(dot_code):
    # Parse DOT code to extract nodes and edges
    elements = parse_dot_code(dot_code)

    # Create the Dash app
    app = dash.Dash(__name__)

    # Define the layout
    app.layout = html.Div([
        Cytoscape(
            id='graph',
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '600px'},
            elements=elements,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(id)',
                        'background-color': '#6FB1FC',
                        'border-color': '#3573A5',
                        'border-width': 2,
                        'font-size': '12px',
                        'width': '50px',
                        'height': '50px',
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'width': 3,
                        'line-color': '#9DB5B2',
                        'curve-style': 'bezier'
                    }
                }
            ]
        )
    ])

    return app

def parse_dot_code(dot_code):
    # Add your logic to parse DOT code and extract nodes and edges
    # For simplicity, let's use a hardcoded example for now
    return [
        {'data': {'id': 'A'}},
        {'data': {'id': 'B'}},
        {'data': {'id': 'C'}},
        {'data': {'id': 'AB', 'source': 'A', 'target': 'B'}},
        {'data': {'id': 'BC', 'source': 'B', 'target': 'C'}},
        {'data': {'id': 'CA', 'source': 'C', 'target': 'A'}}
    ]

if __name__ == '__main__':
    # Your DOT code remains the same
    dot_code = """
    digraph Example {
      A -> B;
      B -> C;
      C -> A;
    }
    """

    app = create_cytoscape_graph(dot_code)
    app.run_server(debug=True)
