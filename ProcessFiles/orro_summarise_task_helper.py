import ProcessFiles.comm as comm
from datetime import datetime
import pandas as pd

def get_month_year_str(date_str,f1, f2):
    return datetime.strptime(date_str,f1).strftime(f2)

def get_lnarr1_str(date_str,f1,f2):
    month_year_str = get_month_year_str(date_str,f1, f2)
    return f'Orro | SDWan Charge | {month_year_str}' 

def get_col_names_from_enum(enum_class):
    return [item.display_name for item in enum_class if item.is_keep]

def add_hard_coded_columns(df):
    dt_tmp = df[comm.BillChargeDetailColumns.FROM.display_name].iloc[0]
    v_tmp = get_lnarr1_str(dt_tmp,comm.format_1,comm.format_2)
    
    hard_coded = {
        comm.BillChargeDetailColumns.LLDGCODE.display_name:'GL',
        comm.BillChargeDetailColumns.LNARR1.display_name:v_tmp
    }
    for k, v in hard_coded.items():
        df[k] = v
    
    return df
def add_summary(df_grouped):
    result = []
    for name, group in df_grouped:
        summary = group[[comm.BillChargeDetailColumns.CHARGE_AMOUNT_EX_TAX.display_name]].sum()
        summary[comm.BillChargeDetailColumns.SALES_ORDER.display_name] = 'Charge Back Journal'
        keep = group[[comm.BillChargeDetailColumns.LLDGCODE.display_name, comm.BillChargeDetailColumns.COST_CENTER.display_name,
                     comm.BillChargeDetailColumns.LNARR1.display_name]].iloc[0]
    
        summary = pd.concat([summary,keep] )
        summary_df = pd.DataFrame([summary],columns=group.columns)
        result.append(summary_df)
        result.append(group)
    final_df = pd.concat(result,ignore_index=True)
    return final_df
def reorder_df(df):
    new_col_order = [comm.BillChargeDetailColumns.LLDGCODE.display_name,
                 comm.BillChargeDetailColumns.COST_CENTER.display_name,
                 comm.BillChargeDetailColumns.CHARGE_AMOUNT_EX_TAX.display_name,
                 comm.BillChargeDetailColumns.LNARR1.display_name,
                 comm.BillChargeDetailColumns.SALES_ORDER.display_name,
                 comm.BillChargeDetailColumns.CHARGE_DESCRIPTION.display_name,
                 ]
    return df[new_col_order]

def load_transform_df(df):
    
    df = add_hard_coded_columns(df)
    # reorder the columns
    df = reorder_df(df)
    return df

def summarise_by_cost_center(df):
    cols = get_col_names_from_enum(comm.BillChargeDetailColumns)
    df = df[cols]
    df = load_transform_df(df)
    df_grouped = df.groupby(comm.BillChargeDetailColumns.COST_CENTER.display_name)
    final_df = add_summary(df_grouped)
    return final_df  

    