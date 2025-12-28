import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# --- Data Loading and Preparation ---
df = pd.read_csv('allDogDescriptions.csv')

# Convert date strings to datetime objects
df['posted'] = pd.to_datetime(df['posted'], errors='coerce')

# GLOBAL FILTERING: Keep only 2019 data for consistency and cleaner visualizations
df = df[df['posted'].dt.year == 2019].copy()
df['posted_date'] = df['posted'].dt.date

# Mapping state abbreviations to full names
state_map = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Clean state column and map to full names
df['contact_state'] = df['contact_state'].str.replace(r'\d+', '', regex=True).str.strip().str.upper()
df['full_state'] = df['contact_state'].map(state_map).fillna(df['contact_state'])

# --- Theme Definitions ---
THEMES = {
    "Natural Brown": {
        "bg": "#f4f1ea", "panel": "#ffffff", "text": "#4b3621", 
        "accent": "#8b5a2b", "scale": "Brwnyl",
        "kpi": "linear-gradient(135deg, #3d2b1f, #a68966)"
    },
    "Ocean Blue": {
        "bg": "#f0f8ff", "panel": "#ffffff", "text": "#004e92", 
        "accent": "#0074d9", "scale": "Blues",
        "kpi": "linear-gradient(135deg, #004e92, #000428)"
    }
}

DOG_IMAGE = "https://i.pinimg.com/originals/22/5f/1b/225f1b2a67dfcb0cb943c587950236c1.jpg"

# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"])

server = app.server

# --- Layout ---
app.layout = html.Div(id="outer-container", style={"minHeight": "100vh"}, children=[
    dbc.Container(fluid=True, children=[
        dbc.Row([
            # LEFT SIDE: FILTER PANEL
            dbc.Col([
                html.Div(id="filter-panel", style={
                    "padding": "25px", "height": "100vh", "position": "sticky", "top": "0",
                    "box-shadow": "4px 0 15px rgba(0,0,0,0.05)", "display": "flex", "flexDirection": "column"
                }, children=[
                    html.Div([
                        html.Div([
                            html.H4([html.I(className="fas fa-paw me-2"), "Rescue 2019"], className="fw-bold d-inline"),
                            dbc.Button([html.I(className="fas fa-undo")], id="reset-btn", color="link", 
                                       className="float-end p-0 text-decoration-none", style={"fontSize": "0.9rem"})
                        ], className="mb-4"),
                        
                        html.Div([
                            html.Label("Theme Selection", className="fw-bold mb-2", style={"fontSize": "0.75rem", "color": "#888"}),
                            dbc.RadioItems(
                                id='palette-filter',
                                options=[{'label': k, 'value': k} for k in THEMES.keys()],
                                value='Natural Brown',
                                label_style={'display': 'block', 'fontSize': '0.85rem', 'marginBottom': '5px'}
                            ),
                        ], className="mb-4"),

                        html.Div([
                            html.Label("State Filter", className="fw-bold mb-2", style={"fontSize": "0.75rem", "color": "#888"}),
                            dcc.Dropdown(id='state-filter', 
                                         options=[{'label': s, 'value': s} for s in sorted(df['full_state'].unique())], 
                                         multi=True, placeholder="All States"),
                        ], className="mb-3"),

                        html.Div([
                            html.Label("Breed Filter", className="fw-bold mb-2", style={"fontSize": "0.75rem", "color": "#888"}),
                            dcc.Dropdown(id='breed-filter', multi=True, placeholder="All Breeds"),
                        ], className="mb-3"),

                        html.Div([
                            html.Label("Gender Selection", className="fw-bold mb-2", style={"fontSize": "0.75rem", "color": "#888"}),
                            dbc.Checklist(id='sex-filter',
                                         options=[{'label': s, 'value': s} for s in df['sex'].unique()],
                                         value=df['sex'].unique().tolist(),
                                         label_style={"display": "block", "fontSize": "0.85rem", "marginBottom": "5px"}),
                        ], className="mb-4"),
                        
                    ], style={"overflowY": "auto", "flex": "1"}),

                    html.Img(src=DOG_IMAGE, style={"width": "100%", "borderRadius": "12px", "opacity": "0.9", "marginTop": "20px"})
                ])
            ], lg=3, md=4, style={"padding": "0"}),

            # RIGHT SIDE: CONTENT
            dbc.Col([
                html.Div(style={"padding": "2rem"}, children=[
                    dbc.Row([dbc.Col(html.H2("Rescue Dog Analytics", id="main-title", className="fw-bold"), width=12)], className="mb-4"),

                    # KPI Section
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([html.H3(id="kpi-total", className="fw-bold"), html.Small("2019 Listings")]), id="kpi-1", className="border-0 text-white text-center shadow-sm")),
                        dbc.Col(dbc.Card(dbc.CardBody([html.H3(id="kpi-fixed", className="fw-bold"), html.Small("Neutered Rate")]), id="kpi-2", className="border-0 text-white text-center shadow-sm")),
                        dbc.Col(dbc.Card(dbc.CardBody([html.H3(id="kpi-special", className="fw-bold"), html.Small("Special Needs")]), id="kpi-3", className="border-0 text-white text-center shadow-sm")),
                    ], className="g-3 mb-4"),

                    # Main Charts
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(id='map-chart', style={"height": "350px"}), className="p-3 rounded-3 bg-white shadow-sm"), lg=7),
                        dbc.Col(html.Div(dcc.Graph(id='age-size-heat', style={"height": "350px"}), className="p-3 rounded-3 bg-white shadow-sm"), lg=5),
                    ], className="g-3 mb-4"),

                    # BOTTOM SECTION: SELECTOR + DYNAMIC CONTENT
                    dbc.Row([
                        dbc.Col(html.Div([
                            dbc.Row([
                                dbc.Col(html.P("Detailed Statistics", className="fw-bold mb-0 ps-3 pt-3", style={"fontSize": "0.95rem"}), width=6),
                                dbc.Col(
                                    dbc.RadioItems(
                                        id='view-selector',
                                        options=[
                                            {'label': 'Activity Trend', 'value': 'chart'},
                                            {'label': 'Data Table', 'value': 'table'}
                                        ],
                                        value='chart',
                                        inline=True,
                                        className="pt-3 pe-3 d-flex justify-content-end",
                                        style={"fontSize": "0.85rem"},
                                        input_style={"marginRight": "5px", "marginLeft": "15px"}
                                    ), width=6
                                )
                            ]),
                            html.Div(id='bottom-content-area', style={"padding": "15px"})
                        ], className="bg-white rounded-3 shadow-sm"), width=12)
                    ])
                ])
            ], lg=9, md=8)
        ])
    ])
])

# --- Callbacks ---

# Update breed dropdown options based on selected states
@app.callback(
    Output('breed-filter', 'options'),
    Input('state-filter', 'value')
)
def update_breed_dropdown(selected_states):
    if not selected_states:
        relevant_breeds = sorted(df['breed_primary'].unique())
    else:
        relevant_breeds = sorted(df[df['full_state'].isin(selected_states)]['breed_primary'].unique())
    return [{'label': b, 'value': b} for b in relevant_breeds]

# Reset all filters to default values
@app.callback(
    [Output('state-filter', 'value'), Output('breed-filter', 'value'), 
     Output('sex-filter', 'value'), Output('palette-filter', 'value'), Output('view-selector', 'value')],
    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_all_filters(n):
    return None, None, df['sex'].unique().tolist(), 'Natural Brown', 'chart'

# Main update callback for all visual elements
@app.callback(
    [Output('kpi-total', 'children'), Output('kpi-fixed', 'children'), Output('kpi-special', 'children'),
     Output('map-chart', 'figure'), Output('age-size-heat', 'figure'), Output('bottom-content-area', 'children'),
     Output('kpi-1', 'style'), Output('kpi-2', 'style'), Output('kpi-3', 'style'),
     Output('outer-container', 'style'), Output('filter-panel', 'style'), Output('main-title', 'style')],
    [Input('state-filter', 'value'), Input('breed-filter', 'value'), 
     Input('sex-filter', 'value'), Input('palette-filter', 'value'),
     Input('view-selector', 'value')]
)
def update_all_content(states, breeds, sexes, theme_name, view_mode):
    # Filter data based on selected criteria
    dff = df[df['sex'].isin(sexes)].copy()
    if states: dff = dff[dff['full_state'].isin(states)]
    if breeds: dff = dff[dff['breed_primary'].isin(breeds)]

    t = THEMES[theme_name]
    
    # KPI Calculations
    total = f"{len(dff):,}"
    fixed = f"{(dff['fixed'].astype(float).mean()*100):.1f}%" if not dff.empty else "0%"
    special = f"{len(dff[dff['special_needs'] == True]):,}"

    # Generate Choropleth Map
    f_map = px.choropleth(dff['contact_state'].value_counts().reset_index(), locations='contact_state', 
                          locationmode="USA-states", color='count', scope="usa", color_continuous_scale=t["scale"])
    
    # Generate Heatmap (Age vs Size)
    f_heat = px.imshow(pd.crosstab(dff['age'], dff['size']), text_auto=True, color_continuous_scale=t["scale"])

    # Bottom Area: Area Chart or Data Table
    if view_mode == 'chart':
        time_data = dff.groupby('posted_date').size().reset_index(name='count')
        f_time = px.area(time_data, x='posted_date', y='count', color_discrete_sequence=[t["accent"]])
        
        # Refine Trendline: Remove axis title, transparent background
        f_time.update_layout(
            xaxis_title=None, yaxis_title=None,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color=t["text"], size=10),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        content = dcc.Graph(figure=f_time, style={"height": "280px"})
    else:
        # Table view with primary data columns
        cols = ['name', 'breed_primary', 'age', 'sex', 'contact_city', 'full_state']
        content = dash_table.DataTable(
            data=dff[cols].head(100).to_dict('records'),
            columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in cols],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '12px', 'fontSize': '0.85rem', 'fontFamily': 'inherit'},
            style_header={'backgroundColor': t['bg'], 'fontWeight': 'bold', 'color': t['text'], 'border': 'none'},
            style_data={'border': 'none', 'color': '#333'}
        )

    # Apply common styling to main charts
    for f in [f_map, f_heat]:
        f.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                        font=dict(color=t["text"], size=10), margin=dict(t=10, b=10, l=10, r=10))
    f_map.update_coloraxes(showscale=False)

    # Dynamic styling for containers based on theme
    kpi_style = {"background": t["kpi"], "borderRadius": "15px", "border": "none", "padding": "20px"}
    panel_style = {"background-color": t["panel"], "color": t["text"], "padding": "25px", 
                   "height": "100vh", "position": "sticky", "top": "0", "display": "flex", "flexDirection": "column"}

    return (total, fixed, special, f_map, f_heat, content,
            kpi_style, kpi_style, kpi_style, 
            {"background-color": t["bg"]}, panel_style, 
            {"color": t["text"], "fontWeight": "800", "fontSize": "2.2rem"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)