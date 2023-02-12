#################################################
###########  FINANCIAL DASHBOARD       ##########
###########  DIEGO VALVERDE CISNEROS	#########
#################################################

# Started Sunday January 9th by dvc
# Last updated on September 25th

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import openpyxl
import plotly.express as px
import pandas as pd

import plotly.graph_objects as go
#dash_daq: Default Graduated bar
import dash_daq as daq


app = dash.Dash(__name__)

#### Excel. 
#### Note: To be migrated a real DB
df = pd.ExcelFile(r"G:/Mi unidad/02_Proyectos/1_Finance/Finance/FT_2023.xlsx", engine='openpyxl')

#### Dataframes.
df_balance = df.parse("balance")  # hoja de excel "balance"
df = df.parse("database")  # hoja de excel "database"

#### List of months
meses = df["Fecha"].dt.strftime("%B").unique().tolist()

#### Balance and Forecast graphs
fig_balance = go.Figure()

fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['Total'], legendgroup="group1", legendgrouptitle_text="Totales",  name="Balance", mode="lines+markers+text",text = df_balance['Total'])) #, mode = 'lines', name = 'Balance'))
fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['Forecast'], legendgroup="group1", name="Forecast", mode="markers+text",text = df_balance['Forecast'], marker=dict(size=8,
            line=dict(width=2,  color='DarkSlateGrey')),)) 
fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['ING'], legendgroup="group2",  legendgrouptitle_text="Inversion", text = df_balance['ING'], name="ING", mode="lines+markers+text")) #, mode = 'lines', name = 'Balance'))
fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['DeGiro'], legendgroup="group2", name="DeGiro", mode="lines+markers+text", text = df_balance['DeGiro'])) #, mode = 'lines', name = 'Balance'))
fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['Autonomo'], legendgroup="group3", legendgrouptitle_text="Ahorros",  name="Autonomo", mode="lines+markers+text",text = df_balance['Autonomo'])) #, mode = 'lines', name = 'Balance'))
fig_balance.add_trace(go.Scatter(x=df_balance['Mes'], y=df_balance['LaCaixa'], legendgroup="group3", legendgrouptitle_text="Ahorros",  name="LaCaixa", mode="lines+markers+text",text = df_balance['LaCaixa'])) #, mode = 'lines', name = 'Balance'))
fig_balance.update_xaxes(
    dtick="M1",
    tickformat="%b")

fig_balance.update_traces(textposition="bottom center")
fig_balance.update_layout(  title={'text': "Current vs Target 2023", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})

#### Holidays. Note: This value is the acumulated qtty along the year.
Holidays = df[df["Categorias"]=="Vacaciones"]
Holidays = Holidays["Importe"].sum().round()
Holidays = int(abs(Holidays))

#### Layout	
app.layout = html.Div([ 
	html.Div([
		html.H1('Finance Dashboard Application')], className="banner"),
	html.Div([
		#dcc.Dropdown(id="my_dropdown", options=[{"label": str(month), "value": str(month)} for month in meses], multi=False , placeholder="Select a Month" , value="January")]), #You also have to change in the callback from ".isin(dd_value)" to ""== dd_value""
		dcc.Dropdown(id="my_dropdown", options=[{"label": month, "value": str(month)} for month in meses], multi=True , placeholder="Select a Month" , value= ["December"] )]),
	html.Div([
		html.Div([			
				html.Div([		
			dcc.Graph(id="graph_monthly"), ], className = "graph_monthly") ,
				html.Div([ 
			daq.GraduatedBar(id="graph_holidays", label="Holidays", vertical = True,  color={"gradient":True,"ranges":{"green":[0,1400],"yellow":[1400,2300],"red":[2300,2800]}}, showCurrentValue=True, step = 200, max=2800, value= Holidays ), ], className = "graph_holidays"),			
				html.Div([		
			dcc.Graph(id="graph_object"), ], className = "graph_object") , 
			html.H3(id="fixed_costs", style={'whiteSpace': 'pre-wrap','text align': 'right'}), #],className="text"),
				], id='top-container'),
		html.Div([ 
    		dcc.Graph(id="graph_balance", figure=fig_balance),], className = "graph_balance", id='bottom-container'), 	], id='container'), 
	html.Div([
		html.H4('© 2022 Diego Valverde Cisneros. All Rights Reserved')], className="footer")
])

#Monthly graph
@app.callback(
	Output(component_id="graph_monthly", component_property="figure"),
	[Input(component_id="my_dropdown", component_property="value")],
)

def build_graph(dd_value):
	
	#df_dd1 = df_week1[df_week1["Fecha"].dt.strftime("%B") == dd_value]
	df_dd1 = df[df["Fecha"].dt.strftime("%B").isin(dd_value)]
	#No contabilizo Nomina porque disvirtua las graficas. Tampoco contabilizo Gastos Fijos/Hobbies/Investments
	df_dd1_f = df_dd1[~df_dd1.Categorias.isin(["Nomina","Piso","Alimentacion","Simyo","Spotify","Guitarra","DeGiro","Luz","Agua","Salsa"])]
	df_dd1_f_no_null = df_dd1_f[df_dd1_f.Categorias.notnull()]

	# text_auto used to format values and display them with 0 decimals.
	fig = px.histogram(df_dd1_f_no_null, x="Categorias", y="Importe",  title= "Monthly Variable Expenses", text_auto=".0f"
    ).update_xaxes( tickangle=0, showgrid=True,  ticks="outside", tickson="boundaries") # , categoryorder="total ascending")
	fig.update_layout(title_x=0.5 , margin=dict(l=80, r=25, t=50, b=60))
	#tickangle forces the X axe labels to be displayed in horizontal.
	return fig


#Object graph : Indicator
@app.callback(
	Output(component_id="graph_object", component_property="figure"),
	[Input(component_id="my_dropdown", component_property="value")],
)

def build_graph(dd_value):

	df_mes = df[df["Fecha"].dt.strftime("%B").isin(dd_value)]

	degiro = df_mes[df_mes["Categorias"]=="DeGiro"]
	degiro = degiro["Importe"].sum().round()
	degiro = int(abs(degiro))

	df_mes_not_null = df_mes[df_mes.Categorias.notnull()]
	df_variable = df_mes_not_null[~df_mes_not_null.Categorias.isin(["Nomina","Piso","Alimentacion","Simyo","Spotify","Guitarra","DeGiro","Luz","Agua","Salsa","Vacaciones"])]
	gasto_variable = int(df_variable["Importe"].sum().round())

	df_fijo = df_mes[df_mes.Categorias.isin(["Piso","Alimentacion","Simyo","Spotify","Luz","Agua"])]
	gasto_fijo = int(df_fijo["Importe"].sum().round())

	vacaciones = df_mes[df_mes["Categorias"]=="Vacaciones"]
	vacaciones = int(vacaciones["Importe"].sum().round())

	hobbies = df_mes[df_mes.Categorias.isin(["Guitarra","Salsa"])]
	hobbies = int(hobbies["Importe"].sum().round())

	nomina = df_mes[df_mes["Categorias"]=="Nomina"]
	nomina = int(nomina["Importe"].sum().round())
	
	#El monto de "Vacaciones" va por otro flujo.
	Savings = nomina + gasto_fijo + gasto_variable + hobbies - degiro
	gasto_total = gasto_fijo + gasto_variable + hobbies
	Savings = int(Savings)

	#new layout to delete the whitespaces margin from charts. The default values are 80px LRB and 100px on the Top.
	layout = go.Layout(
  	margin=go.layout.Margin(
        l=0, #left margin
        r=30, #right margin
        b=20, #bottom margin
        t=40, #top margin
    	)
	)
	#new layout applied.
	fig1 = go.Figure(layout=layout)

	fig1.add_trace(go.Indicator(
    mode = "number",
    value = nomina,
    title = {"text": "Income"},
    domain = {'x': [0, 0.2], 'y': [0.5, 1]}))

	### Total expenses: Max -1083
	fig1.add_trace(go.Indicator(
    mode = "number",
    value = abs(gasto_total),
    title = {"text": "Expenses"},
    domain = {'x': [0, 0.2], 'y': [0, 0.5]}))

	### Variable expenses: Max -200€
	fig1.add_trace(go.Indicator(
    mode = "number",
    value = gasto_variable,
    title = {"text": "Variables"},
    domain = {'x': [0.8, 1], 'y': [0, 0.5]}))

	fig1.add_trace(go.Indicator(
    mode = "delta",
    value = Savings,
	title = {"text": "Balance"},
    delta = {'reference': 0},
	domain = {'x': [0.3, 0.7], 'y': [0.3, 0.7]}))
    

	fig1.add_trace(go.Indicator(
    mode = "delta",
    value = degiro,
    title = {"text": "Degiro"},
    delta = {'position' : "top", 'reference': 0},
    domain = {'x': [0.8, 1], 'y': [0.5, 1]}))



	return fig1 
		

#### Fixed costs - Values
@app.callback(Output("fixed_costs", "children"), Input("my_dropdown", "value"))

def update_output(value):

	df_mes = df[df["Fecha"].dt.strftime("%B").isin(value)]

	#### Nomina
	#nomina = df_mes[df_mes.Categorias.isin(["Nomina"])]
	#nomina = nomina["Importe"].sum().round()

	#######  Fixed Costs ##############################
	#int -> delete decimals
	Piso = df_mes[df_mes["Categorias"]=="Piso"]
	Piso = int(Piso["Importe"].sum().round())

	Alimentacion = df_mes[df_mes["Categorias"]=="Alimentacion"]
	Alimentacion = int(Alimentacion["Importe"].sum().round())

	Agua = df_mes[df_mes["Categorias"]=="Agua"]
	Agua = int(Agua["Importe"].sum().round())

	Luz = df_mes[df_mes["Categorias"]=="Luz"]
	Luz = int(Luz["Importe"].sum().round())

	Simyo = df_mes[df_mes["Categorias"]=="Simyo"]
	Simyo = int(Simyo["Importe"].sum().round())
	
	Spotify = df_mes[df_mes["Categorias"]=="Spotify"]
	Spotify = int(Spotify["Importe"].sum().round())

	Recibos = Spotify + Simyo + Luz + Agua
	#df_fijo = df_mes[df_mes.Categorias.isin(["Piso","Alimentacion", "Recibos", "Guitarra","Spotify","Simyo"])]
	Gasto_fijo = Piso + Alimentacion + Recibos

	#######  Hobies Costs  ###########################
	Guitarra = df_mes[df_mes["Categorias"]=="Guitarra"]
	Guitarra = int(Guitarra["Importe"].sum().round())

	Salsa = df_mes[df_mes["Categorias"]=="Salsa"]
	Salsa = int(Salsa["Importe"].sum().round())

	Hobbies = Guitarra + Salsa
	#######  Variable Costs  ###########################
	df_mes_not_null = df_mes[df_mes.Categorias.notnull()]
	df_variable = df_mes_not_null[~df_mes_not_null.Categorias.isin(["Nomina","Piso","Alimentacion","Simyo","Spotify","Guitarra","DeGiro","Luz","Agua","Salsa"])]
	Gasto_variable = int(df_variable["Importe"].sum().round())

	return '\n\nFixed \t\t\t{}\t\t-715 \n\tPiso \t\t{}\t\t-500 \n\tAlimentac \t{}\t\t-150 \n\tRecibos  \t{}\t\t-65 \n\t\tAgua  \t{}\t\t-10 \n\t\tLuz \t\t{}\t\t-32 \n\t\tSimyo \t{}\t\t-21 \n\t\tSpotify \t{}\t\t-2  \n\nHobbies \t\t\t{}\t\t-168 \n\tGuitarra \t\t{}\t\t-100 \n\tSalsa \t\t{}\t\t-68'.format(Gasto_fijo,Piso,Alimentacion,Recibos,Agua,Luz,Simyo,Spotify,Hobbies,Guitarra,Salsa)



if __name__ == "__main__":	
	app.run_server(debug=True)


import base64
import plotly.express as px
from xhtml2pdf import pisa

def figure_to_base64(figures):
    images_html = ""
    for figure in figures:
        image = str(base64.b64encode(figure.to_image(format="png", scale=2)))[2:-1]
        images_html += (f'<img src="data:image/png;base64,{image}"><br>')
    return images_html
 
def create_html_report(template_file, images_html):
    with open(template_file,'r') as f:
        template_html = f.read()
    report_html = template_html.replace("{{ FIGURES }}", images_html)
    return report_html
 
def convert_html_to_pdf(source_html, output_filename):
    with open(f"{output_filename}", "w+b") as f:
        pisa_status = pisa.CreatePDF(source_html, dest=f)
    return pisa_status.err

images_html = figure_to_base64(figures)
report_html = create_html_report("template.html", images_html)
convert_html_to_pdf(report_html, "report.pdf")