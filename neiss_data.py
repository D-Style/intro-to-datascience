import pandas as pd

def load_neiss():
    infile = "neiss.csv"

    use_fields = "case_id trmt_date age narr sex diag body_part disposition location race_text prod1_text fire_involvement hospital_stratum".split()
    categorical_fields = "sex race_text diag body_part disposition location prod1_text fire_involvement hospital_stratum".split()
    specified_dtypes = {field:'category' for field in categorical_fields}

    data = pd.read_table(infile, usecols=use_fields,
                         parse_dates=['trmt_date'],
                         dtype=specified_dtypes, 
                         index_col=0)

    # Add incident_count field to clarify summary statistics
    data['incident_count'] = 1

    # Create a short product description for each product, similarly for body parts and diagnosis
    products = set(data['prod1_text'].unique())
    short_products = {s:s.split('(')[0].split(',')[0].strip() for s in products}
    data['product'] = data['prod1_text'].apply(lambda p: short_products[p]).astype('category')

    body_parts = set(data['body_part'].unique())
    short_bodyparts = {s:s.split('(')[0].strip() for s in body_parts}
    data['body_part'] = data['body_part'].apply(lambda b: short_bodyparts[b]).astype('category')

    # Additionally, collapse all 'Burns' diagnoses
    diagnoses = set(data['diag'].unique())
    short_diags = {s:s.split('(')[0].strip() for s in diagnoses}
    for diag in diagnoses:
        if diag[:5]=='Burns':
            short_diags[diag] = "Burns"
    data['diagnosis'] = data['diag'].apply(lambda d: short_diags[d]).astype('category')

    # For this demo, I didn't bother with dates.
    # Instead, work with day-from-start, setting the first day to 1
    # This is equivalent to day-of-month for our dataset
    data['day'] = [(day - data['trmt_date'].min()).days + 1 for day in data['trmt_date']]

    # Restrict our dataset to top few products
    NUM_PRODUCTS = 12
    top_products = set(data['product'].value_counts()[:NUM_PRODUCTS].index)
    data = data[ data['product'].isin(top_products) ]
    data['product'].cat.remove_unused_categories(inplace=True)

    return data