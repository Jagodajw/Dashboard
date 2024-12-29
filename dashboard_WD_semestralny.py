from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Wczytanie danych
data = pd.ExcelFile('Superstore_Sales.xlsx')
orders_data = data.parse("Orders")

# Lista unikalnych miast, posortowanych alfabetycznie
unique_cities = sorted(orders_data["City"].unique())

# Lista unikalnych kategorii sprzedaży
unique_categories = sorted(orders_data["Category"].unique())

# Paleta kolorów
palette = px.colors.qualitative.Pastel

# Funkcja do generowania tytułu na podstawie filtrów
def generate_title(base_title, selected_city, selected_category):
    if selected_city and selected_category:
        return f"{base_title} dla {selected_category} w {selected_city}"
    elif selected_city:
        return f"{base_title} w {selected_city}"
    elif selected_category:
        return f"{base_title} dla {selected_category}"
    return base_title

# Funkcja do generowania wykresu sprzedaży według kategorii produktów
def generate_category_sales_fig(filtered_data, title):
    fig = px.bar(
        filtered_data.groupby("Category")["Sales"].sum().reset_index(),
        x="Category", y="Sales", title=title,
        labels={"Sales": "Sprzedaż", "Category": "Kategoria"},
        color="Sales", text_auto=True, color_continuous_scale=palette
    )
    return fig


# Tworzenie aplikacji Dash z Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])


# 10 najlepszych miast pod względem sprzedaży
top_cities = orders_data.groupby("City")["Sales"].sum().nlargest(10).reset_index()
city_sales_fig = px.bar(
    top_cities, x="City", y="Sales", title="10 najlepszych miast pod względem sprzedaży",
    labels={"Sales": "Sprzedaż", "City": "Miasto"},
    text_auto=True,
    color="Sales",
    color_continuous_scale=palette
)

# 5 najlepszych stanów pod względem sprzedaży
top_states = orders_data.groupby("State")["Sales"].sum().nlargest(5).reset_index()
state_sales_fig = px.bar(
    top_states, x="State", y="Sales", title="5 najlepszych stanów pod względem sprzedaży",
    labels={"Sales": "Sprzedaż", "State": "Stan"},
    text_auto=True,
    color="Sales",
    color_continuous_scale=palette
)

# Style dla komponentów
HEADER_STYLE = {
    "background": "linear-gradient(to right, #141E30, #243B55)",
    "padding": "20px",
    "border-radius": "10px",
    "border": "2px solid #2C3E50",
    "color": "white",
    "margin-bottom": "20px"
}

CARD_STYLE = {
    'border': '1px solid lightgrey',
    'boxShadow': '2px 2px 10px lightgrey',
    'borderRadius': '5px',
    'backgroundColor': '#fff',
}

# Layout aplikacji
app.layout = dbc.Container(
    [
        # Nagłówek z gradientowym tłem
       html.Div(
            children=[
                html.H1("Dashboard Sprzedaży Superstore", className="text-center text-light mb-4 shadow-sm"),
                html.P(
                    "Dane pochodzą z fikcyjnego sklepu Superstore i zawierają informacje o sprzedaży, "
                    "zyskach, segmentach klientów, kategoriach produktów oraz regionach. Zadanie semestralne Wizualizacja danych UŚ.",
                    className="text-center text-light"
                ),
            ],
            style=HEADER_STYLE
        ),

        # Dropdown do wyboru miasta
       dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="city-dropdown",
                        options=[{"label": city, "value": city} for city in unique_cities],
                        placeholder="Wybierz miasto",
                        className="pb-4 pt-4"
                    ),
                    width=6,
                ),
                # Dropdown do wyboru kategorii sprzedaży z lepszym paddingiem
                dbc.Col(
                    dcc.Dropdown(
                        id="category-dropdown",
                        options=[{"label": category, "value": category} for category in unique_categories],
                        placeholder="Wybierz kategorię",
                        className="pb-4 pt-4"
                    ),
                    width=6, 
                ),
            ],
            justify="around"  
        ),

        # Pierwszy wiersz z wykresami
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="category-sales-graph"), width=5, style=CARD_STYLE),
                dbc.Col(dcc.Graph(id="region-sales-graph"), width=5,  style=CARD_STYLE),
            ],
            justify="around",
            style={'margin-bottom': '20px', 'padding': '10px'} 

        ),

        # Drugi wiersz z wykresami
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="ship-mode-graph"),  width=5, style=CARD_STYLE),
                dbc.Col(dcc.Graph(id="profit-sales-graph"), width=5, style=CARD_STYLE),
            ],
            justify="around",
            style={'margin-bottom': '20px', 'padding': '10px'} 
        ),


        # Trzeci wiersz z jednym dużym wykresem
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="segment-sales-graph"), width=5, style=CARD_STYLE),
                dbc.Col(dcc.Graph(id="time-series-sales-graph"), width=5, style=CARD_STYLE),
            ],
            justify="around",
            style={'margin-bottom': '20px', 'padding': '10px'} 
        ),

        # Czwarty wiersz z nowymi wykresami
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=city_sales_fig), width=5, style=CARD_STYLE),
                dbc.Col(dcc.Graph(figure=state_sales_fig), width=5, style=CARD_STYLE),
            ],
            justify="around",
            style={'margin-bottom': '20px', 'padding': '10px'} 
        ),


    ],
    fluid=True,
)

# Callbacki do aktualizacji wykresów w zależności od wybranego miasta i kategorii
@app.callback(
    Output("category-sales-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_category_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    title = generate_title("Sprzedaż według kategorii produktów", selected_city, selected_category)
    return generate_category_sales_fig(filtered_data, title).update_layout(title_font_size=title_size)


@app.callback(
    Output("region-sales-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_region_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    title = generate_title("Rozkład sprzedaży w regionach", selected_city, selected_category)
    return px.pie(filtered_data, names="Region", values="Sales", title=title, color_discrete_sequence=palette).update_layout(title_font_size=title_size)


@app.callback(
    Output("ship-mode-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_ship_mode_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    title = generate_title("Proporcja sposobów wysyłki", selected_city, selected_category)
    return px.pie(filtered_data, names="Ship Mode", title=title, color_discrete_sequence=palette).update_layout(title_font_size=title_size)

@app.callback(
    Output("profit-sales-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_profit_sales_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    title = generate_title("Relacja zysku i sprzedaży", selected_city, selected_category)
    return px.scatter(
        filtered_data, x="Sales", y="Profit", color="Category",
        title=title, labels={"Sales": "Sprzedaż", "Profit": "Zysk"}
    ).update_layout(title_font_size=title_size)

@app.callback(
    Output("segment-sales-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_segment_sales_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    title = generate_title("Sprzedaż według segmentu klientów", selected_city, selected_category)
    return px.bar(
        filtered_data.groupby("Segment")["Sales"].sum().reset_index(),
        x="Segment", y="Sales", title=title,
        labels={"Sales": "Sprzedaż", "Segment": "Segment"},
        color="Sales", text_auto=True, color_continuous_scale=palette
    ).update_layout(title_font_size=title_size)


# Wykres liniowy 
@app.callback(
    Output("time-series-sales-graph", "figure"),
    [Input("city-dropdown", "value"), Input("category-dropdown", "value")]
)

def update_time_series_sales_graph(selected_city, selected_category):
    title_size = 16
    filtered_data = orders_data
    if selected_city:
        filtered_data = filtered_data[filtered_data["City"] == selected_city]
        title_size = 13
    if selected_category:
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
        title_size = 13
    
    title = generate_title("Trend sprzedaży w czasie", selected_city, selected_category)
    fig = px.line(
        filtered_data.groupby("Order Date")["Sales"].sum().reset_index(),
        x="Order Date", y="Sales", title=title,
        labels={"Sales": "Sprzedaż", "Order Date": "Data zamówienia"},
    )
    fig.update_layout(title_font_size=title_size)
    return fig

# Uruchomienie aplikacji
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
