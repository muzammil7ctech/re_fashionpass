from pyspark.sql.functions import concat,concat_ws
from pyspark.sql.functions import datediff,to_date,col
import numpy as np
from pyspark.sql.types import IntegerType,FloatType
from pyspark.sql.functions import datediff, current_date
def feature_list(df=None):
    """
    Extract feature lists from the input DataFrame.

    Parameters:
    - df (pyspark.sql.DataFrame): Input DataFrame containing feature columns.

    Returns:
    dict: A dictionary containing different feature lists.

    Feature Lists:
    - 'category_collection_FE': List of values extracted from the 'category_collection_FE' column.
    - 'categoey_collection_tag_L': List of values extracted from the 'category_collection_tag_L' column.
    - 'tag_cloud': List of values extracted from the 'tag_cloud' column.
    """
    # Extract values from 'category_collection_FE', 'category_collection_tag_L', and 'tag_cloud' columns
    category_collection_FE = [i[0] for i in df.select('category_collection_FE').collect()]
    category_collection_tag_L = [i[0] for i in df.select('category_collection_tag_L').collect()]
    tag_cloud = [i[0] for i in df.select('tag_cloud').collect()]

    # Return a dictionary containing the extracted feature lists
    return {
        'category_collection_FE': category_collection_FE,
        'categoey_collection_tag_L': category_collection_tag_L,
        'tag_cloud': tag_cloud
    }


def string_column(data_df):
    """
    Modify values in the input DataFrame by replacing non-empty and positive numeric values with the corresponding column name,
    and setting other values to an empty string.

    Parameters:
    - data_df (dict): A dictionary where keys are column names and values are lists of numeric or string values.

    Returns:
    dict: A modified dictionary where values in each column are replaced with the column name if the value is non-empty and positive,
    otherwise set to an empty string.

    Example:
    If input data_df is {'column1': ['3', '', '5'], 'column2': ['2', '-1', '']}, the output will be
    {'column1': ['column1', '', 'column1'], 'column2': ['column2', '', '']}.
    """
    for key, value in data_df.items():
        data_df[key] = [key if (v != '' and int(v) > 0) else '' for v in value]

    return data_df


def tag_cloud_join_df(collection_category_df, collection_category_tag_df, tag_cloud_df, product_tag_df, feature_list, join_type):
    """
    Perform a series of joins and transformations on the provided DataFrames to create a new DataFrame representing tag-cloud-related information.

    Parameters:
    - collection_category_df (pyspark.sql.DataFrame): DataFrame containing collection category information.
    - collection_category_tag_df (pyspark.sql.DataFrame): DataFrame containing collection category tag information.
    - tag_cloud_df (pyspark.sql.DataFrame): DataFrame containing tag cloud information.
    - product_tag_df (pyspark.sql.DataFrame): DataFrame containing product tag information.
    - feature_list (dict): A dictionary containing feature lists, including 'tag_cloud'.
    - join_type (str): Type of join to be used in DataFrame joins.

    Returns:
    pandas.DataFrame: A DataFrame representing tag-cloud-related information for products.

    Note:
    - The function performs left joins and filtering based on feature_list['tag_cloud'] values.
    - It creates a new DataFrame with tag-related information for each product.
    - The final DataFrame includes a 'tag_string' column representing a concatenated string of tag information for each product.
    """
    product_product_tag_df = product_tag_df.join(tag_cloud_df, product_tag_df.tag_id == tag_cloud_df.id, 'left')
    product_product_tag_df = product_product_tag_df.filter(product_product_tag_df['tag_id'].isin(feature_list['tag_cloud']))

    collection_product_product_tag_df = product_product_tag_df.join(collection_category_tag_df, collection_category_tag_df.tag_id == product_product_tag_df.tag_id, 'left')
    collection_product_product_tag_df = collection_product_product_tag_df.join(collection_category_df, collection_product_product_tag_df.category_id == collection_category_df.id, 'left')
    collection_product_product_tag_df = duplicate_col(collection_product_product_tag_df)
    collection_product_product_tag_df = collection_product_product_tag_df.select(['product_id', 'tag_name', 'name'])
    collection_product_product_tag_df = collection_product_product_tag_df.select(concat_ws(' ', collection_product_product_tag_df.name, collection_product_product_tag_df.tag_name).alias('collection_tag'), 'product_id')

    data = (collection_product_product_tag_df.groupby('product_id').pivot('collection_tag').count())
    data = data.na.fill(0)
    data_df = data.toPandas()
    data_df = data_df.set_index('product_id')
    data_df = string_column(data_df)
    columns = data_df.columns
    data_df['tag_string'] = data_df[columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    data_df = data_df.reset_index()

    return data_df




def duplicate_col(data=None):
  """
    Duplicate columns in a DataFrame by appending '_duplicate_' and the index to the column name.

    Parameters:
    - data (pd.DataFrame): The input DataFrame with columns to be duplicated.

    Returns:
    pd.DataFrame: A new DataFrame with duplicated columns.
    """
  df_cols = data.columns
  duplicate_col_index = [idx for idx,
  val in enumerate(df_cols) if val in df_cols[:idx]]
  for i in duplicate_col_index:
    df_cols[i] = df_cols[i] + '_duplicate_'+ str(i)
  data = data.toDF(*df_cols)
  return data





def collection_tag_join_df(collection_category_df, collection_category_tag_df, tag_cloud_df, product_tag_df, feature_list, join_type):
    """
    Perform a series of joins and transformations on the provided DataFrames to create a new DataFrame representing collection tag-related information.

    Parameters:
    - collection_category_df (pyspark.sql.DataFrame): DataFrame containing collection category information.
    - collection_category_tag_df (pyspark.sql.DataFrame): DataFrame containing collection category tag information.
    - tag_cloud_df (pyspark.sql.DataFrame): DataFrame containing tag cloud information.
    - product_tag_df (pyspark.sql.DataFrame): DataFrame containing product tag information.
    - feature_list (dict): A dictionary containing feature lists, including 'tag_cloud' and 'categoey_collection_tag_L'.
    - join_type (str): Type of join to be used in DataFrame joins.

    Returns:
    pandas.DataFrame: A DataFrame representing collection tag-related information for products.

    Note:
    - The function performs left joins and filtering based on feature_list['tag_cloud'] and feature_list['categoey_collection_tag_L'] values.
    - It creates a new DataFrame with collection tag-related information for each product.
    - The final DataFrame includes a 'tag_string' column representing a concatenated string of tag information for each product.
    """
    product_product_tag_df = product_tag_df.join(tag_cloud_df, product_tag_df.tag_id == tag_cloud_df.id, 'left')
    product_product_tag_df = product_product_tag_df.filter(product_product_tag_df['tag_id'].isin(feature_list['tag_cloud']))

    collection_product_product_tag_df = product_product_tag_df.join(collection_category_tag_df, collection_category_tag_df.tag_id == product_product_tag_df.tag_id, 'left')
    collection_product_product_tag_df = collection_product_product_tag_df.join(collection_category_df, collection_product_product_tag_df.category_id == collection_category_df.id, 'left')
    collection_product_product_tag_df = collection_product_product_tag_df.filter(collection_product_product_tag_df['category_id'].isin(feature_list['categoey_collection_tag_L']))
    collection_product_product_tag_df = duplicate_col(collection_product_product_tag_df)
    collection_product_product_tag_df = collection_product_product_tag_df.select(['product_id', 'tag_name', 'name'])
    collection_product_product_tag_df = collection_product_product_tag_df.select(concat_ws(' ', collection_product_product_tag_df.name, collection_product_product_tag_df.tag_name).alias('collection_tag'), 'product_id')

    data = (collection_product_product_tag_df.groupby('product_id').pivot('collection_tag').count())
    data = data.na.fill(0)
    data_df = data.toPandas()
    data_df = data_df.set_index('product_id')
    data_df = string_column(data_df)
    columns = data_df.columns
    data_df['tag_string'] = data_df[columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    data_df = data_df.reset_index()
    return data_df






def collection_FE_tag_join_df(collection_category_df, collection_category_tag_df, tag_cloud_df, product_tag_df, feature_list, join_type):
    """
    Perform a series of joins and transformations on the provided DataFrames to create a new DataFrame representing
    collection feature and tag-related information.

    Parameters:
    - collection_category_df (pyspark.sql.DataFrame): DataFrame containing collection category information.
    - collection_category_tag_df (pyspark.sql.DataFrame): DataFrame containing collection category tag information.
    - tag_cloud_df (pyspark.sql.DataFrame): DataFrame containing tag cloud information.
    - product_tag_df (pyspark.sql.DataFrame): DataFrame containing product tag information.
    - feature_list (dict): A dictionary containing feature lists, including 'tag_cloud', 'category_collection_FE', and 'categoey_collection_tag_L'.
    - join_type (str): Type of join to be used in DataFrame joins.

    Returns:
    pandas.DataFrame: A DataFrame representing collection feature and tag-related information for products.

    Note:
    - The function performs left joins and filtering based on feature_list values.
    - It creates a new DataFrame with collection feature and tag-related information for each product.
    - The final DataFrame includes a 'tag_string' column representing a concatenated string of tag information for each product.
    """
    product_product_tag_df = product_tag_df.join(tag_cloud_df, product_tag_df.tag_id == tag_cloud_df.id, 'left')
    product_product_tag_df = product_product_tag_df.filter(product_product_tag_df['tag_id'].isin(feature_list['tag_cloud']))

    collection_product_product_tag_df = product_product_tag_df.join(collection_category_tag_df, collection_category_tag_df.tag_id == product_product_tag_df.tag_id, 'left')
    collection_category_df = collection_category_df.filter(collection_category_df['id'].isin(feature_list['category_collection_FE']))
    collection_product_product_tag_df = collection_product_product_tag_df.join(collection_category_df, collection_product_product_tag_df.category_id == collection_category_df.id, 'left')
    collection_product_product_tag_df = collection_product_product_tag_df.filter(collection_product_product_tag_df['category_id'].isin(feature_list['categoey_collection_tag_L']))
    collection_product_product_tag_df = duplicate_col(collection_product_product_tag_df)
    collection_product_product_tag_df = collection_product_product_tag_df.select(['product_id', 'tag_name', 'name'])
    collection_product_product_tag_df = collection_product_product_tag_df.select(concat_ws(' ', collection_product_product_tag_df.name, collection_product_product_tag_df.tag_name).alias('collection_tag'), 'product_id')

    data = (collection_product_product_tag_df.groupby('product_id').pivot('collection_tag').count())
    data = data.na.fill(0)
    data_df = data.toPandas()
    data_df = data_df.set_index('product_id')
    data_df = string_column(data_df)
    columns = data_df.columns
    data_df['tag_string'] = data_df[columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    data_df = data_df.reset_index()
    return data_df


# def cosin_transformation(df):
#     df=df.withColumn('cosin_score',df.cosin_score.cast(FloatType()))
#     df=df.withColumnRenamed('Product_A','original_product').\
#     withColumnRenamed('Product_B','matched_product')
#     # df=df.toPandas()
#     # df['cosin_score']=df['cosin_score'].round(3)
#     # df=df.drop(columns=['cosin_score','_c0'],axis=1).rename(columns={'cosin_score_1':'cosin_score'})
#     df=df.select(['original_product','matched_product','cosin_score'])
#     return df
def cosin_transformation(df):
    """
    Perform cosine transformation on the DataFrame.

    Args:
        df (DataFrame): Input DataFrame containing columns 'cosin_score', 'Product_A', and 'Product_B'.

    Returns:
        DataFrame: Transformed DataFrame containing columns 'original_product', 'matched_product', and 'cosin_score'.
    """
    # Cast 'cosin_score' column to FloatType if it's not already in that format
    df = df.withColumn('cosin_score', df.cosin_score.cast(FloatType()))
    
    # Rename columns 'Product_A' to 'original_product' and 'Product_B' to 'matched_product'
    df = df.withColumnRenamed('Product_A', 'original_product') \
           .withColumnRenamed('Product_B', 'matched_product')
    
    # Select necessary columns
    df = df.select(['original_product', 'matched_product', 'cosin_score'])
    # Return the transformed DataFrame
    return df

# def min_max_scaling(feature_vector):
#     min_val = min(feature_vector)
#     max_val = max(feature_vector)
#     scaled_vector = [round(((x - min_val) / (max_val - min_val)),2) for x in feature_vector]
#     return scaled_vector

def min_max_scaling(feature_vector):
    """
    Perform min-max scaling on the input feature vector.

    Args:
        feature_vector (list): Input list representing the feature vector.

    Returns:
        list: Scaled feature vector.
    """
    # Find the minimum and maximum values in the feature vector
    min_val = min(feature_vector)
    max_val = max(feature_vector)
    
    # Scale each value in the feature vector using min-max scaling formula
    scaled_vector = [round(((x - min_val) / (max_val - min_val)), 2) for x in feature_vector]
    
    return scaled_vector

# def standardize_feature_vector(feature_vector):
#     mean_val = sum(feature_vector) / len(feature_vector)
#     std_dev = (sum([(x - mean_val) ** 2 for x in feature_vector]) / len(feature_vector)) ** 0.5
#     standardized_vector = [(x - mean_val) / std_dev for x in feature_vector]
#     return standardized_vector
def standardize_feature_vector(feature_vector):
    """
    Perform standardization on the input feature vector.

    Args:
        feature_vector (list): Input list representing the feature vector.

    Returns:
        list: Standardized feature vector.
    """
    # Calculate the mean and standard deviation of the feature vector
    mean_val = sum(feature_vector) / len(feature_vector)
    std_dev = (sum([(x - mean_val) ** 2 for x in feature_vector]) / len(feature_vector)) ** 0.5
    
    # Standardize each value in the feature vector
    standardized_vector = [(x - mean_val) / std_dev for x in feature_vector]
    
    return standardized_vector

def date_difference_normalize(Product_df, cosin_date):
    """
    Normalize cosine scores based on date differences between products.

    Args:
        Product_df (DataFrame): DataFrame containing product information.
        cosin_date (DataFrame): DataFrame containing cosine similarity scores and publication dates.

    Returns:
        DataFrame: DataFrame with normalized cosine scores based on date differences.
    """
    # Join Product_df and cosin_date on 'original_product' and 'product_id'
    cosin_date = Product_df.join(cosin_date, cosin_date.original_product == Product_df.product_id, 'inner')
    
    # Rename and select necessary columns
    cosin_date = cosin_date.withColumnRenamed('published_at', 'reference_date') \
                           .select(['original_product', 'matched_product', 'reference_date', 'cosin_score'])
    
    # Calculate date differences
    cosin_date = cosin_date.withColumn('datediff', datediff(to_date(current_date()), to_date('reference_date')))
    
    # Collect date differences and perform min-max scaling
    date_diff = [int(d[0]) for d in cosin_date.select('datediff').collect()]
    min_max_vector = min_max_scaling(date_diff)
    
    # Convert to Pandas DataFrame for easier manipulation
    cosin_date = cosin_date.toPandas()
    print('change to pandas')
    
    # Perform min-max scaling on cosine scores
    cosin_date['Min_Max_scalling'] = min_max_vector
    cosin_date['cosin_score_min_max'] = cosin_date.Min_Max_scalling * cosin_date.cosin_score.astype(float)
    print(cosin_date.head())
    
    # Select necessary columns and rename
    cosin_date = cosin_date[['original_product', 'matched_product', 'cosin_score_min_max']]
    cosin_date = cosin_date.rename(columns={'cosin_score_min_max': 'cosin_score'})

    return cosin_date


def date_difference(Product_df, cosin_date):
    """
    Extracts the original_product, matched_product, and cosin_score from the cosin_date DataFrame
    after joining it with Product_df.

    Args:
        Product_df (DataFrame): DataFrame containing product information.
        cosin_date (DataFrame): DataFrame containing cosine similarity scores and publication dates.

    Returns:
        DataFrame: DataFrame with columns 'original_product', 'matched_product', and 'cosin_score'.
    """
    # Join Product_df and cosin_date on 'original_product' and 'product_id'
    cosin_date = Product_df.join(cosin_date, cosin_date.original_product == Product_df.product_id, 'inner')
    
    # Rename and select necessary columns
    cosin_date = cosin_date.withColumnRenamed('published_at', 'reference_date') \
                           .select(['original_product', 'matched_product', 'cosin_score'])

    # Convert to Pandas DataFrame for easier manipulation
    cosin_date = cosin_date.toPandas()

    # Select necessary columns
    cosin_date = cosin_date[['original_product', 'matched_product', 'cosin_score']]

    return cosin_date


def combine_cosin_df(cosin_accessories_df,cosin_clothing_df,product_tag_df,tag_cloud_df,Product_df,collection_category_tag_df,feature_accesories_df,feature_clothing_df):
    """
    Combine cosine similarity DataFrames for accessories and clothing products.

    Args:
        cosin_accessories_df (DataFrame): DataFrame containing cosine similarity scores for accessories.
        cosin_clothing_df (DataFrame): DataFrame containing cosine similarity scores for clothing.
        product_tag_df (DataFrame): DataFrame containing product tag table.
        tag_cloud_df (DataFrame): DataFrame containing tag cloud table.
        Product_df (DataFrame): DataFrame containing product table.
        collection_category_tag_df (DataFrame): DataFrame containing collection category tag information.
        feature_accesories_df (DataFrame): DataFrame containing features of accessories.
        feature_clothing_df (DataFrame): DataFrame containing features of clothing.

    Returns:
        DataFrame: Combined DataFrame containing cosine similarity scores, and product IDs for accessories and clothing.
    """

    product_tag_name_df=product_tag_df.join(tag_cloud_df,product_tag_df.tag_id==tag_cloud_df.id)
    product_tag_name_df=product_tag_name_df.join(Product_df,Product_df.product_id==product_tag_name_df.product_id,'inner')
    product_tag_name_df=duplicate_col(product_tag_name_df)
    product_tag_name_df=product_tag_name_df.select(['product_id','tag_id','id','tag_name','product_title'])
    product_tag_name_collection_df=product_tag_name_df.join(collection_category_tag_df,product_tag_name_df.tag_id==collection_category_tag_df.tag_id)
    product_accesories_ids=[  int(i) for i in np.unique(product_tag_name_collection_df.filter
    (product_tag_name_collection_df['category_id'].isin(
        
        feature_accesories_df['category_collection_FE']
        
    )).select('product_id').collect())]
    product_clothing_ids=[ int(i)  for i in np.unique(product_tag_name_collection_df.filter
    (product_tag_name_collection_df['category_id'].isin(
     feature_clothing_df['category_collection_FE']

    )).select('product_id').collect())]
    
    #--testing cosin csv--#
        # import pandas as pd
        # cosin_clothing_df.to_csv('cosin_clothing_df.csv')
        # cosin_accessories_df.to_csv('cosin_accessories_df.csv')
    #--testing cosin csv--#
    cosin_clothing_df=cosin_clothing_df[~cosin_clothing_df['Product_A'].isin(product_accesories_ids)]
    cosin_accessories_df=cosin_accessories_df[~cosin_accessories_df['Product_A'].isin(product_clothing_ids)]
    #--wrote for pyspark--#
    # cosin_accessories_df=cosin_accessories_df.filter(~cosin_accessories_df['Product_B'].isin(product_clothing_ids))  
    # cosin_clothing_df=cosin_clothing_df.filter(~cosin_clothing_df['Product_B'].isin(product_accesories_ids))
    # cosin_clothing_df=cosin_clothing_df.toPandas()
    # cosin_accessories_df=cosin_accessories_df.toPandas()
    #--wrote for pyspark--#
    merge_csv=cosin_accessories_df._append(cosin_clothing_df,ignore_index = True)  
    merge_csv=merge_csv[['cosin_score',  'Product_A'  ,'Product_B']]
    return merge_csv  