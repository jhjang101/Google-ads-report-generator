import pandas as pd
import datetime
import os


def build_campaign_name_clause(campaign_name: str | None = None):
    if campaign_name:
        # Query using provided campaign name
        campaign_name_clause = f"AND campaign.name = '{campaign_name}'"
        print(f"\tQuery using provided campaign name: {campaign_name}.")
    else:
        # Query using default campaigns status = enabled
        campaign_name_clause = "AND campaign.status = 'ENABLED'"
        print("\tQuery using default campaign status: ENABLED.")
    return campaign_name_clause 


def calc_date_range(start_date_str: str | None = None) -> tuple[str, str]:
    if start_date_str:
        # Query using user provided dates
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = start_date + datetime.timedelta(days=6)
        end_date_str = end_date.strftime("%Y-%m-%d")
        print(f"\tQuery using provided date range: {start_date_str} - {end_date_str}.")
    else:
        # Query using default dates (last SUN to SAT)
        today = datetime.date.today()
        # Assuming the report is starting on Sunday of previous week.
        days_to_subtract = (today.weekday() + 1) % 7 + 7
        start_date = today - datetime.timedelta(days=days_to_subtract)
        # The default report is ending on Saturday of previous week.
        end_date = start_date + datetime.timedelta(days=6)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        print(f"\tQuery using default calculated date range: {start_date_str} - {end_date_str}.")
        
    if start_date.strftime("%A") != "Sunday":
        # Check the provided date range
        raise ValueError("start_date_str must be Sunday.")

    return start_date_str, end_date_str


def add_date_range(df: pd.DataFrame, start_date_str: str, end_date_str: str) -> pd.DataFrame:
    # Format the date range string (e.g., "07/06-07/12)
    start_date: datetime.datetime = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date: datetime.datetime = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    report_date_range = f"{start_date.strftime('%m.%d')}-{end_date.strftime('%m.%d')}"
    
    df["Report_Start"] = start_date
    df["Report_End"] = end_date
    df["Report_Date_Range"] = report_date_range

    print("\tSuccessfully updated date range to the DataFrame.")
    return df


def update_csv(df: pd.DataFrame, save_file_path: str):
    if os.path.exists(save_file_path):
        # if file exist, append the data without header
        df.to_csv(save_file_path, mode="a",header=False, index=False, encoding="utf-8-sig")
        print(f"\tSuccessfully appended the DataFrame to '{save_file_path}'.")
    else:
        # if no file exist, create file and save the data with header
        df.to_csv(save_file_path, mode="a",header=True, index=False, encoding="utf-8-sig")
        print(f"\tSuccessfully created '{save_file_path}' from the DataFrame.")
    


def geo_reference(geotarget_file: str) -> dict:
    geo_reference = pd.read_csv(geotarget_file)
    # Filter by Country (US only)
    geo_reference = geo_reference[geo_reference["Country Code"]=="US"]
    # Drop NA
    geo_reference.dropna(subset=["Criteria ID", "Name"], inplace=True)
    # Change data type
    geo_reference["Criteria ID"] = geo_reference["Criteria ID"].astype(str)
    # Create lookup dict
    lookup = geo_reference.set_index("Criteria ID")["Name"].to_dict()

    print("\tSuccessfully built geo_reference lookup dict.")
    return lookup


def map_location(df: pd.DataFrame, lookup: dict) -> pd.DataFrame:
    # Extract raw Criteria IDs by stripping the prefix
    df["State"] = df["State_ID"].str.strip("geoTargetConstants/")
    df["Location"] = df["Location_ID"].str.strip("geoTargetConstants/")

    # Perform the mapping
    df["State"] = df["State"].map(lookup)
    df["Location"] = df["Location"].map(lookup)

    print("\tSuccessfully updated geo_location on the DataFrame.")
    return df


def verify_csv(save_file_path):
    # Read and print the last few rows of the saved CSV to verify
    if os.path.exists(save_file_path):
        print(f"--- Last 5 rows of the updated '{save_file_path}' ---")
        print(pd.read_csv(save_file_path).tail())
    else:
        print(f"'{save_file_path}' was not found.")

if __name__ == "__main__":
    print(calc_date_range())
