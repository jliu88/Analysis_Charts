"""
Create a table with user input metric and category
"""
import pandas as pd
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource, DataTable, TableColumn

def create_table(df_orig, met, **kwargs):   
    df = df_orig
    cato = kwargs['cato']

#    Removes lots if there is less than 2 data point
    counts = df[cato].value_counts()    
    for index, value in counts.iteritems():
        if value < 2:
            filt = lambda x:x[cato] != index
            df = df.loc[filt]

    groups = df.groupby(cato)
    
    mean = groups[met].mean()
    median = groups[met].median()
    std = groups[met].std(ddof = 0)
    count = groups[met].count()
 
    mean.name = 'Mean'
    median.name = 'Median'
    std.name = 'Stdev'
    count.name = 'Count'
    table_list = [mean, median, std, count]

    columns = [
            TableColumn(field=cato, title =cato),
            TableColumn(field='Mean', title='Mean'),
            TableColumn(field='Median', title='Median'),
            TableColumn(field='Stdev', title='Std'),
            TableColumn(field='Count', title='Count'),
            ]
    
    if 'metric_attrib' in kwargs:
        metric_attrib = kwargs['metric_attrib']
        cpk_tab = cpk_calc(mean,std, metric_attrib)
        cpk_tab.name = 'Cpk'
        
        table_list.append(cpk_tab)
        columns.append(TableColumn(field='Cpk', title='Cpk'))
        
    summary_df = pd.concat(table_list, axis=1)
    summary_df = summary_df.round(2)
    print(summary_df)
    source = ColumnDataSource(summary_df)        
    
    data_table = DataTable(source=source, columns = columns, selectable=False, sortable = False)

    table_fig = widgetbox(data_table)    

    return table_fig

def cpk_calc(mean, std, metric_attrib):
    
    cpk_param = zip(mean, std)
    cpk_list = []
        
    for m, s in cpk_param:
        #Calculates Cpk
        if metric_attrib['usl'] != 'NA':
            usl = float(metric_attrib['usl'])
            cp_u = (usl- m)/(3*s)
        else:
            cp_u = 9999
            
        if metric_attrib['lsl'] != 'NA':
            lsl = float(metric_attrib['lsl'])
            cp_l = (m - lsl)/(3*s)
        else:
            cp_l = 9999
                              
        if cp_l < cp_u:
            cpk = cp_l
        if cp_u < cp_l:
            cpk = cp_u
        if cp_l == cp_u:
            cpk = cp_l

        if cpk == 9999:
            cpk = 'NA'
        cpk_list.append(cpk)

    cpk_tab = pd.Series(cpk_list, index=mean.index)
    
    return cpk_tab