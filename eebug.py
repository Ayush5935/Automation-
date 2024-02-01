stylesheet = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'font-size': '12px',
            'width': '90px',
            'height': '90px',
            'shape': 'ellipse',
            'text-halign': 'center',
            'text-valign': 'bottom',
        }
    },
    {
        'selector': '[type = "ENI"]',
        'style': {
            'background-color': '#6FB1FC',  # Blue
            'border-color': '#3573A5',
            'background-image': 'url(https://fontawesome.com/v5.15/assets/img/icons-solid/envelope-open-text.svg)',
            'background-fit': 'cover',
            'background-width': '80%',
            'background-height': '80%',
        }
    },
    {
        'selector': '[type = "Subnet"]',
        'style': {
            'background-color': '#98FB98',  # Green
            'border-color': '#4CAF50',
            'background-image': 'url(https://fontawesome.com/v5.15/assets/img/icons-solid/building.svg)',
            'background-fit': 'cover',
            'background-width': '80%',
            'background-height': '80%',
        }
    },
    {
        'selector': '[type = "Route Table"]',
        'style': {
            'background-color': '#FFD700',  # Yellow
            'border-color': '#FFC107',
            'background-image': 'url(https://fontawesome.com/v5.15/assets/img/icons-solid/table.svg)',
            'background-fit': 'cover',
            'background-width': '80%',
            'background-height': '80%',
        }
    },
    {
        'selector': '[type = "Transit Gateway"]',
        'style': {
            'background-color': '#FF6347',  # Red
            'border-color': '#E57373',
            'background-image': 'url(https://fontawesome.com/v5.15/assets/img/icons-solid/network-wired.svg)',
            'background-fit': 'cover',
            'background-width': '80%',
            'background-height': '80%',
        }
    },
    {
        'selector': '[type = "Transit Gateway Attachment"]',
        'style': {
            'background-color': '#8A2BE2',  # Purple
            'border-color': '#7B1FA2',
            'background-image': 'url(https://fontawesome.com/v5.15/assets/img/icons-solid/link.svg)',
            'background-fit': 'cover',
            'background-width': '80%',
            'background-height': '80%',
        }
    },
    {
        'selector': 'edge',
        'style': {
            'width': 3,
            'line-color': '#9DB5B2',
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
        }
    }
]
