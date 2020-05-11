import dash
import dash_table
import pandas as pd
import numpy as np
import datatable as dt
import json
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

def pretty(jsonmap):
    print(json.dumps(jsonmap, sort_keys=False, indent=4, separators=(',', ': ')))

fullTable = dt.fread("full-latest.csv")
print(fullTable.keys())
cases = fullTable[:,'AnzahlFall'].sum()[0,0]
dead = fullTable[:,'AnzahlTodesfall'].sum()[0,0]

lastDay=fullTable[:,'MeldeDay'].max()[0,0]
print("lastDay {} cases {} dead{}".format(lastDay, cases, dead))

newTable=fullTable[:,dt.f[:].extend({"erkMeldeDelay": dt.f.MeldeDay-dt.f.RefDay})]
#print(newTable.keys())


#dt.by(dt.f.Bundesland)]
alldays=fullTable[:,
          [dt.sum(dt.f.AnzahlFall),
           dt.sum(dt.f.FaellePro100k),
           dt.sum(dt.f.AnzahlTodesfall),
           dt.sum(dt.f.TodesfaellePro100k),
           dt.mean(dt.f.Bevoelkerung)],
   dt.by(dt.f.Landkreis)]

last7days=fullTable[dt.f.newCaseOnDay>lastDay-7,:][:,
          [dt.sum(dt.f.AnzahlFall),
           dt.sum(dt.f.FaellePro100k),
           dt.sum(dt.f.AnzahlTodesfall),
           dt.sum(dt.f.TodesfaellePro100k)],
   dt.by(dt.f.Landkreis)]
last7days.names=["Landkreis","AnzahlFallLetzte7Tage","FaellePro100kLetzte7Tage","AnzahlTodesfallLetzte7Tage","TodesfaellePro100kLetzte7Tage"]

def merge(largerTable, smallerTable, keyFieldName):
    keys = smallerTable[:, keyFieldName].to_list()[0]
    extTable = largerTable.copy()
    for colName in smallerTable.names:
        if colName != keyFieldName:
            values = smallerTable[:, colName].to_list()[0]
            valuesDict = dict(zip(keys, values))

            extTable = extTable[:, dt.f[:].extend({colName: 0.0})]

            for i, lk in enumerate(extTable[:,keyFieldName].to_list()[0]):
                if lk in valuesDict:
                    extTable[i,colName] = valuesDict[lk]
    return extTable


## todo: increase when more data here
lastWeek7days=fullTable[(dt.f.newCaseOnDay > lastDay-13) & (dt.f.newCaseOnDay<=lastDay-6),:][:,
          [dt.sum(dt.f.AnzahlFall),
           dt.sum(dt.f.FaellePro100k),
           dt.sum(dt.f.AnzahlTodesfall),
           dt.sum(dt.f.TodesfaellePro100k)],
   dt.by(dt.f.Landkreis)]
lastWeek7days.names=["Landkreis","AnzahlFallLetzte7TageDavor","FaellePro100kLetzte7TageDavor","AnzahlTodesfallLetzte7TageDavor","TodesfaellePro100kLetzte7TageDavor"]

allDaysExt0 = merge(alldays, last7days, "Landkreis")
allDaysExt1 = merge(allDaysExt0, lastWeek7days, "Landkreis")

Rw = dt.f.AnzahlFallLetzte7Tage/dt.f.AnzahlFallLetzte7TageDavor

allDaysExt2=allDaysExt1[:,dt.f[:].extend({"AnzahlFallTrend":  Rw})]
allDaysExt3=allDaysExt2[:,dt.f[:].extend({"FaellePro100kTrend": dt.f.FaellePro100kLetzte7Tage-dt.f.FaellePro100kLetzte7TageDavor})]
allDaysExt4=allDaysExt3[:,dt.f[:].extend({"TodesfaellePro100kTrend": dt.f.TodesfaellePro100kLetzte7Tage-dt.f.TodesfaellePro100kLetzte7TageDavor})]

allDaysExt=allDaysExt4[:,dt.f[:].extend({"Kontaktrisiko": dt.f.Bevoelkerung/6.25/((dt.f.AnzahlFallLetzte7Tage+dt.f.AnzahlFallLetzte7TageDavor)*Rw)})]

print(list(enumerate(allDaysExt.names)))

FormatFixed1 = Format(
                precision=1,
                scheme=Scheme.fixed,
                symbol=Symbol.no,
            )
FormatFixed2 = Format(
                precision=2,
                scheme=Scheme.fixed,
                symbol=Symbol.no,
            )

FormatInt = Format(
                precision=0,
                scheme=Scheme.fixed,
                symbol=Symbol.no,
#                symbol_suffix=u'˚F'
            )
#FormatInt=FormatTemplate.money(0)
#FormatFixed1=FormatTemplate.money(0)
(15, 'TodesfaellePro100kTrend')

desiredOrder = [(0, 'Landkreis', ['Kreis','Name'],'text',Format()),
                (5, 'Bevoelkerung', ['Kreis','Einwohner'],'numeric',FormatInt),
                (17, 'Kontaktrisiko', ['Kreis','Risiko 1:N'],'numeric',FormatInt),
                (1, 'AnzahlFall', ['Fälle','total'],'numeric',FormatInt),
                (6, 'AnzahlFallLetzte7Tage', ['Fälle','letzte Woche'] ,'numeric',FormatInt),
                (14, 'AnzahlFallTrend', ['Fälle','R'] ,'numeric',FormatFixed2),
                (10, 'AnzahlFallLetzte7TageDavor',['Fälle','vorletzte Woche'],'numeric',FormatInt),
                (2, 'FaellePro100k',['Fälle je 100000','total'],'numeric',FormatFixed1),
                (15, 'FaellePro100kTrend',['Fälle je 100000','Differenz'] ,'numeric',FormatFixed1),
                (7, 'FaellePro100kLetzte7Tage',['Fälle je 100000','letzte Woche'] ,'numeric',FormatFixed1),
                (11, 'FaellePro100kLetzte7TageDavor', ['Fälle je 100000','vorletzte Woche'],'numeric',FormatFixed1),
                (3, 'AnzahlTodesfall', ['Todesfälle','total'],'numeric',FormatInt),
                (8, 'AnzahlTodesfallLetzte7Tage', ['Todesfälle','letzte Woche'],'numeric',FormatInt),
                (12, 'AnzahlTodesfallLetzte7TageDavor', ['Todesfälle','vorletzte Woche'],'numeric',FormatInt),
                (4, 'TodesfaellePro100k', ['Todesfälle je 100000','total'],'numeric',FormatFixed2),
                (9, 'TodesfaellePro100kLetzte7Tage', ['Todesfälle je 100000','letzte Woche'],'numeric',FormatFixed2),
                (16, 'TodesfaellePro100kTrend', ['Todesfälle je 100000','Differenz'],'numeric',FormatFixed2),
                (13, 'TodesfaellePro100kLetzte7TageDavor', ['Todesfälle je 100000','vorletzte Woche'],'numeric',FormatFixed2)]

orderedIndices, orderedCols, orderedNames, orderedTypes, orderFormats = zip(*desiredOrder)
orderedIndices = np.array(orderedIndices)+1
print(orderedIndices)

#pretty(allDaysExt.to_dict())

# fig = go.Figure(data=[go.Table(
#     #columnorder=[0,1,5],
#     #columnwidth=[80, 400],
#
#     header=dict(values=orderedNames,
#                 line_color='darkslategray',
#                 fill_color='lightskyblue',
#                 align='left'),
#     cells=dict(values=allDaysExt.to_list(),
#                line_color='darkslategray',
#                fill_color='lightcyan',
#                align='left'))
# ])

print("allDaysExt.names",allDaysExt.names)
print("allDaysExt.to_dict",allDaysExt.to_pandas().to_dict("records"))

#columns = [{'name': L1, 'id': L2} for (L1,L2) in zip(orderedNames,orderedCols)]
columns = [{'name': L1, 'id': L2, 'type':L3, 'format':L4} for (L1,L2,L3,L4) in zip(orderedNames,orderedCols,orderedTypes,orderFormats)]
print("columns=",columns)

data=allDaysExt.to_pandas().to_dict("records")

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
print("columns=",[{"name": i, "id": i} for i in df.columns],)
print("data=",df.to_dict('records'))

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=columns,
    data=data,
    sort_action='native',
    page_size= 500,
#    fixed_rows={ 'headers': True, 'data': 0 },
    style_cell={'textAlign': 'right',
                'padding': '5px',
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
    },
    style_cell_conditional=[
        {
            'if': {'column_id': 'Landkreis'},
            'textAlign': 'left'
        }
    ],
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(70, 70, 70)'
        },
        ############################################################################
        {
            'if': {
                'filter_query': '{FaellePro100kLetzte7Tage} < 1',
                'column_id': ['FaellePro100kLetzte7Tage', 'Landkreis']
            },
            'backgroundColor': 'green',
            'fontWeight': 'bold',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{FaellePro100kLetzte7Tage} >= 1 && {FaellePro100kLetzte7Tage} < 5',
                'column_id': ['FaellePro100kLetzte7Tage', 'Landkreis']
            },
            #            'backgroundColor': 'tomato',
            'fontWeight': 'bold',
            'color': 'lightgreen'
        },
        {
            'if': {
                'filter_query': '{FaellePro100kLetzte7Tage} > 10 && {FaellePro100kLetzte7Tage} < 20',
                'column_id': ['FaellePro100kLetzte7Tage','Landkreis']
            },
            #            'backgroundColor': 'tomato',
            'fontWeight': 'bold',
            'color': 'yellow'
        },
        {
            'if': {
                'filter_query': '{FaellePro100kLetzte7Tage} > 20 && {FaellePro100kLetzte7Tage} < 50',
                'column_id': ['FaellePro100kLetzte7Tage','Landkreis']
            },
            #            'backgroundColor': 'tomato',
            'fontWeight': 'bold',
            'color': 'tomato'
        },
        {
            'if': {
                'filter_query': '{FaellePro100kLetzte7Tage} > 50',
                'column_id': ['FaellePro100kLetzte7Tage','Landkreis']
            },
            'fontWeight': 'bold',
            'backgroundColor': 'firebrick',
            'color': 'white'
        },

        ############################################################################

        {
            'if': {
                'filter_query': '{FaellePro100kTrend} > 0',
                'column_id': 'FaellePro100kTrend'
            },
            'fontWeight': 'bold',
            #'backgroundColor': 'tomato',
            'color': 'tomato'
        },
        ############################################################################
        {
            'if': {
                'filter_query': '{AnzahlFallTrend} > 1',
                'column_id': 'AnzahlFallTrend'
            },
            'fontWeight': 'bold',
            #'backgroundColor': 'tomato',
            'color': 'tomato'
        },
        {
            'if': {
                'filter_query': '{AnzahlFallTrend} > 0.9 && {AnzahlFallTrend} <= 1',
                'column_id': 'AnzahlFallTrend'
            },
            'fontWeight': 'bold',
            # 'backgroundColor': 'tomato',
            'color': 'yellow'
        },
        {
            'if': {
                'filter_query': '{AnzahlFallTrend} < 0.7',
                'column_id': 'AnzahlFallTrend'
            },
            'fontWeight': 'bold',
            # 'backgroundColor': 'tomato',
            'color': 'lightgreen'
        },
        ############################################################################
        {
            'if': {
                'filter_query': '{Kontaktrisiko} > 0 && {Kontaktrisiko} < 100',
                'column_id': ['Kontaktrisiko','Landkreis']
            },
            'fontWeight': 'bold',
            'backgroundColor': 'firebrick',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{Kontaktrisiko} >= 100 && {Kontaktrisiko} < 1000',
                'column_id': ['Kontaktrisiko','Landkreis']
            },
            'fontWeight': 'bold',
            # 'backgroundColor': 'tomato',
            'color': 'tomato'
        },
        {
            'if': {
                'filter_query': '{Kontaktrisiko} >= 1000 && {Kontaktrisiko} < 2500',
                'column_id': ['Kontaktrisiko','Landkreis']
            },
            'fontWeight': 'bold',
            # 'backgroundColor': 'tomato',
            'color': 'yellow'
        },
        {
            'if': {
                'filter_query': '{Kontaktrisiko} >= 5000 && {Kontaktrisiko} < 10000',
                'column_id': ['Kontaktrisiko','Landkreis']
            },
            'fontWeight': 'bold',
            # 'backgroundColor': 'tomato',
            'color': 'lightgreen'
        },
        {
            'if': {
                'filter_query': '{Kontaktrisiko} > 10000',
                'column_id': ['Kontaktrisiko','Landkreis']
            },
            'fontWeight': 'bold',
            'backgroundColor': 'green',
            'color': 'white'
        },

    ],
#    style_as_list_view = True,
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'fontWeight': 'bold',
#        'height': '100px',
        'whiteSpace': 'normal',
        'height': 'auto',
        'overflow-wrap': 'normal',
        'textAlign': 'center'
    },
    merge_duplicate_headers=True,
)

if __name__ == '__main__':
    app.run_server(debug=True)