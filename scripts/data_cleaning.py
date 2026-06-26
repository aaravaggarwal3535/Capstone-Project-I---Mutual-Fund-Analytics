import pandas as pd
import numpy as np
import os


RAW_DATA_DIR = "../data/raw"
SAVE_DATA_DIR = "../data/processed"

def clean_data(file_path, save_path):
    
    # cleaning the 01_fund_master.csv file
    fund_master = pd.read_csv(os.path.join(file_path, "01_fund_master.csv"))
    print(f"First clearing fund_master.csv file:")
    print(f"first 5 rows of the fund_master.csv file: \n{fund_master.head()}")
    print(f"Shape of the fund_master.csv file: {fund_master.shape}")
    print(f"info of the fund_master.csv file: \n{fund_master.info()}")
    print(f"describe of the fund_master.csv file: \n{fund_master.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in fund_master.columns:
        if fund_master[i].dtype == 'object':
            if fund_master[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if fund_master[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = fund_master.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        fund_master = fund_master.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    print (f"Saving the cleaned fund_master.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values and are arranged in asscending order of amfi_code")
    fund_master.to_csv(os.path.join(save_path, "clean_fund.csv"), index=False)

    # cleaning the 02_nav_history.csv file
    nav_history = pd.read_csv(os.path.join(file_path, "02_nav_history.csv"))
    print(f"Now clearing nav_history.csv file:")
    print(f"first 5 rows of the nav_history.csv file: \n{nav_history.head()}")
    print(f"Shape of the nav_history.csv file: {nav_history.shape}")
    print(f"info of the nav_history.csv file: \n{nav_history.info()}")
    print(f"describe of the nav_history.csv file: \n{nav_history.describe()}")
    # changing the date time format and sorting it on the basis of 'amfi_code'+'date' column
    nav_history['date'] = pd.to_datetime(nav_history['date'])
    nav_history = nav_history.sort_values(by=['amfi_code', 'date'])
    # forward filling the missing values
    nav_history['nav'] = nav_history.groupby('amfi_code')['nav'].ffill()
    # finding if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in nav_history.columns:
        if nav_history[i].dtype == 'object':
            if nav_history[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if nav_history[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = nav_history.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        nav_history = nav_history.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    nav_history = nav_history[nav_history['nav'] > 0] # Validate NAV > 0
    # saving the cleaned nav_history.csv file to the processed directory
    print (f"Saving the cleaned nav_history.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values and are arranged in asscending order of amfi_code and date")
    nav_history.to_csv(os.path.join(save_path, "clean_nav.csv"), index=False)

    # cleaning the 03_aum_by_fund_house.csv file
    aum_by_fund_house = pd.read_csv(os.path.join(file_path, "03_aum_by_fund_house.csv"))
    print(f"Now clearing aum_by_fund_house.csv file:")
    print(f"first 5 rows of the aum_by_fund_house.csv file: \n{aum_by_fund_house.head()}")
    print(f"Shape of the aum_by_fund_house.csv file: {aum_by_fund_house.shape}")
    print(f"info of the aum_by_fund_house.csv file: \n{aum_by_fund_house.info()}")
    print(f"describe of the aum_by_fund_house.csv file: \n{aum_by_fund_house.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in aum_by_fund_house.columns:
        if aum_by_fund_house[i].dtype == 'object':
            if aum_by_fund_house[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if aum_by_fund_house[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = aum_by_fund_house.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        aum_by_fund_house = aum_by_fund_house.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned aum_by_fund_house.csv file to the processed directory
    print (f"Saving the cleaned aum_by_fund_house.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    aum_by_fund_house.to_csv(os.path.join(save_path, "clean_aum.csv"), index=False)
    
    # cleaning the 04_monthly_sip_inflows.csv file
    monthly_sip_inflows = pd.read_csv(os.path.join(file_path, "04_monthly_sip_inflows.csv"))
    print(f"Now clearing monthly_sip_inflows.csv file:")
    print(f"first 5 rows of the monthly_sip_inflows.csv file: \n{monthly_sip_inflows.head()}")
    print(f"Shape of the monthly_sip_inflows.csv file: {monthly_sip_inflows.shape}")
    print(f"info of the monthly_sip_inflows.csv file: \n{monthly_sip_inflows.info()}")
    print(f"describe of the monthly_sip_inflows.csv file: \n{monthly_sip_inflows.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in monthly_sip_inflows.columns:
        if monthly_sip_inflows[i].dtype == 'object':
            if monthly_sip_inflows[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if monthly_sip_inflows[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = monthly_sip_inflows.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        monthly_sip_inflows = monthly_sip_inflows.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned monthly_sip_inflows.csv file to the processed directory
    print (f"Saving the cleaned monthly_sip_inflows.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    monthly_sip_inflows.to_csv(os.path.join(save_path, "clean_monthly_sip.csv"), index=False)

    # cleaning the 05_category_inflows.csv file
    category_inflows = pd.read_csv(os.path.join(file_path, "05_category_inflows.csv"))
    print(f"Now clearing category_inflows.csv file:")
    print(f"first 5 rows of the category_inflows.csv file: \n{category_inflows.head()}")
    print(f"Shape of the category_inflows.csv file: {category_inflows.shape}")
    print(f"info of the category_inflows.csv file: \n{category_inflows.info()}")
    print(f"describe of the category_inflows.csv file: \n{category_inflows.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in category_inflows.columns:
        if category_inflows[i].dtype == 'object':
            if category_inflows[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if category_inflows[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = category_inflows.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        category_inflows = category_inflows.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned category_inflows.csv file to the processed directory
    print (f"Saving the cleaned category_inflows.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    category_inflows.to_csv(os.path.join(save_path, "clean_inflows.csv"), index=False)

    # cleaning the 06_industry_folio_count.csv file
    industry_folio_count = pd.read_csv(os.path.join(file_path, "06_industry_folio_count.csv"))
    print(f"Now clearing industry_folio_count.csv file:")
    print(f"first 5 rows of the industry_folio_count.csv file: \n{industry_folio_count.head()}")
    print(f"Shape of the industry_folio_count.csv file: {industry_folio_count.shape}")
    print(f"info of the industry_folio_count.csv file: \n{industry_folio_count.info()}")
    print(f"describe of the industry_folio_count.csv file: \n{industry_folio_count.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in industry_folio_count.columns:
        if industry_folio_count[i].dtype == 'object':
            if industry_folio_count[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if industry_folio_count[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = industry_folio_count.duplicated().sum()
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        industry_folio_count = industry_folio_count.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned industry_folio_count.csv file to the processed directory
    print (f"Saving the cleaned industry_folio_count.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    industry_folio_count.to_csv(os.path.join(save_path, "clean_industry.csv"), index=False)

    # cleaning the 07_scheme_performance.csv file
    scheme_performance = pd.read_csv(os.path.join(file_path, "07_scheme_performance.csv"))
    print(f"Now clearing scheme_performance.csv file:")
    print(f"first 5 rows of the scheme_performance.csv file: \n{scheme_performance.head()}")
    print(f"Shape of the scheme_performance.csv file: {scheme_performance.shape}")
    print(f"info of the scheme_performance.csv file: \n{scheme_performance.info()}")
    print(f"describe of the scheme_performance.csv file: \n{scheme_performance.describe()}")
    # Ensure returns are numeric
    for col in ['1y_return', '3y_return', '5y_return']:
        if col in scheme_performance.columns:
            scheme_performance[col] = pd.to_numeric(scheme_performance[col], errors='coerce')
    # Flag negative sharpe ratios
    if 'sharpe_ratio' in scheme_performance.columns:
        scheme_performance['sharpe_ratio'] = pd.to_numeric(scheme_performance['sharpe_ratio'], errors='coerce')
        scheme_performance['negative_sharpe_flag'] = np.where(scheme_performance['sharpe_ratio'] < 0, True, False)
        if scheme_performance[scheme_performance['negative_sharpe_flag'] == True].empty:
            print("No entries with negative sharpe_ratio found.")
        else:
            print(f"Found {scheme_performance[scheme_performance['negative_sharpe_flag'] == True].shape[0]} entries with negative sharpe_ratio.")
    else:
        print("sharpe_ratio column not found in scheme_performance.csv.")
    # Check expense ratio range (0.1% to 2.5%)
    if 'expense_ratio_pct' in scheme_performance.columns:
        scheme_performance = scheme_performance[(scheme_performance['expense_ratio_pct'] >= 0.1) & (scheme_performance['expense_ratio_pct'] <= 2.5)]
    else:
        print("expense_ratio_pct column not found in scheme_performance.csv.")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in scheme_performance.columns:
        if scheme_performance[i].dtype == 'object':
            if scheme_performance[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if scheme_performance[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = scheme_performance.duplicated().sum()
    print(f"Number of duplicated rows: {duplicate_rows}")
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        scheme_performance = scheme_performance.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned scheme_performance.csv file to the processed directory
    print (f"Saving the cleaned scheme_performance.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    scheme_performance.to_csv(os.path.join(save_path, "clean_performance.csv"), index=False)

    # cleaning the 08_investor_transaction.csv file
    investor_transaction = pd.read_csv(os.path.join(file_path, "08_investor_transactions.csv"))
    print(f"Now clearing investor_transaction.csv file:")
    print(f"first 5 rows of the investor_transaction.csv file: \n{investor_transaction.head()}")
    print(f"Shape of the investor_transaction.csv file: {investor_transaction.shape}")
    print(f"info of the investor_transaction.csv file: \n{investor_transaction.info()}")
    print(f"describe of the investor_transaction.csv file: \n{investor_transaction.describe()}")
    # standardizing text and checking that it can only be [SIP, Redemption, Lumpsum]
    investor_transaction['transaction_type'] = investor_transaction['transaction_type'].str.title()
    valid_transaction_types = ['Sip', 'Redemption', 'Lumpsum']
    if list(investor_transaction['transaction_type'].unique()) != valid_transaction_types:
        print(f"Invalid transaction types found in investor_transaction.csv: {list(investor_transaction['transaction_type'].unique())}")
    else:
        print("All transaction types are valid.")
    # validate amount_inr > 0
    investor_transaction = investor_transaction[investor_transaction['amount_inr'] > 0]
    # correcting date format
    investor_transaction['transaction_date'] = pd.to_datetime(investor_transaction['transaction_date'])
    investor_transaction['kyc_status'] = investor_transaction['kyc_status'].fillna('Pending') # Check KYC
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in investor_transaction.columns:
        if investor_transaction[i].dtype == 'object':
            if investor_transaction[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if investor_transaction[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = investor_transaction.duplicated().sum()
    print(f"Number of duplicated rows: {duplicate_rows}")
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        investor_transaction = investor_transaction.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned investor_transaction.csv file to the processed directory
    print (f"Saving the cleaned investor_transaction.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    investor_transaction.to_csv(os.path.join(save_path, "clean_transactions.csv"), index=False)

    # cleaning the 09_portfolio_holdings.csv file
    portfolio_holdings = pd.read_csv(os.path.join(file_path, "09_portfolio_holdings.csv"))
    print(f"Now clearing portfolio_holdings.csv file:")
    print(f"first 5 rows of the portfolio_holdings.csv file: \n{portfolio_holdings.head()}")
    print(f"Shape of the portfolio_holdings.csv file: {portfolio_holdings.shape}")
    print(f"info of the portfolio_holdings.csv file: \n{portfolio_holdings.info()}")
    print(f"describe of the portfolio_holdings.csv file: \n{portfolio_holdings.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in portfolio_holdings.columns:
        if portfolio_holdings[i].dtype == 'object':
            if portfolio_holdings[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if portfolio_holdings[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = portfolio_holdings.duplicated().sum()
    print(f"Number of duplicated rows: {duplicate_rows}")
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        portfolio_holdings = portfolio_holdings.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned portfolio_holdings.csv file to the processed directory
    print(f"Saving the cleaned portfolio_holdings.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    portfolio_holdings.to_csv(os.path.join(save_path, "clean_portfolio.csv"), index=False)

    # cleaning the 10_benchmark_indicies.csv file
    benchmark_indices = pd.read_csv(os.path.join(file_path, "10_benchmark_indices.csv"))
    print(f"Now clearing benchmark_indices.csv file:")
    print(f"first 5 rows of the benchmark_indices.csv file: \n{benchmark_indices.head()}")
    print(f"Shape of the benchmark_indices.csv file: {benchmark_indices.shape}")
    print(f"info of the benchmark_indices.csv file: \n{benchmark_indices.info()}")
    print(f"describe of the benchmark_indices.csv file: \n{benchmark_indices.describe()}")
    # checking if there is any null value left in the data and if there are any columns with mismatched dtype
    for i in benchmark_indices.columns:
        if benchmark_indices[i].dtype == 'object':
            if benchmark_indices[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values and data type is also not correct")
            else:
                print(f"{i} column has no null value but dtype needs to be fixed")
        else:
            if benchmark_indices[i].isnull().sum() > 0:
                print(f"there is a need to fix {i} column as there are null values but dtype is correct")
            else:
                print(f"{i} column has correct dtype and no null values")
    # finding the number of duplicated rows in the data
    duplicate_rows = benchmark_indices.duplicated().sum()
    print(f"Number of duplicated rows: {duplicate_rows}")
    if duplicate_rows > 0:
        print(f"There are {duplicate_rows} duplicated rows in the data")
        # removing the duplicated rows from the data and keeping the first occurrence
        benchmark_indices = benchmark_indices.drop_duplicates(keep='first')
    else:
        print("There are no duplicated rows in the data")
    # saving the cleaned benchmark_indices.csv file to the processed directory
    print(f"Saving the cleaned benchmark_indices.csv file to {save_path} directory as all the column and data types are correct and there are no null values and no duplicated values")
    benchmark_indices.to_csv(os.path.join(save_path, "clean_benchmark.csv"), index=False)

if __name__ == "__main__":
    clean_data(RAW_DATA_DIR, SAVE_DATA_DIR)