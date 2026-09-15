
import pandas as pd
import os 

def load_csv(file_name,data_path):
    """reusable csv loader to avoid repeating file-loading logic across datasets
    encoding is set to latin1 because the csv is not encoded in UTF-8, hence errors when reading the csv file 
    use sep=';' so that  we can split fields. But csv are comma-delimited by default"""
    #data_path = 'C:/Users/DELL/Projects/ecommerce-sales-pipeline/data/raw'
    raw=os.path.join(data_path,file_name)
    return pd.read_csv(raw,encoding='latin1', sep=";")

def convert_type(df,desired_type):
    """reusable type conversion to avoid repeating multiple type conversions across datasets"""
    column = df.astype(desired_type)
    return  column


def convert_datetype(date,date_format="%d/%m/%Y"):
    """reusable date conversion to avoid repeating multiple date conversions across datasets"""
    appropriate_dateformat = pd.to_datetime(date,format=date_format)
    return appropriate_dateformat


def profile_col(df):
    """reusable DataFrame profiler to avoid repeating dataset profiling logic across datasets"""
    profile = {
            "Data types": df.dtypes,
            "Missing values":df.isna().sum(),
            "Missing percentage": (df.isna().mean() * 100 ).round(2),
            "Unique values": df.nunique(),
            "duplicate":df.duplicated().sum()
            }
    return pd.DataFrame(profile)

def date_summary(date_column,operation):
    """reusable date summarisation to avoid repeating date summarisation logic across datasets"""
    latest= date_column.max()
    oldest = date_column.min()
    
    if operation == 'latest':
        return  latest
    elif operation == 'oldest':
        return oldest
        
    return operation