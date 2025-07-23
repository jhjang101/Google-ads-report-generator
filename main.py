from google.ads.googleads.client import GoogleAdsClient
import os
import query
import util
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


# --- Report Process Function---
def process_report(client: GoogleAdsClient, 
                   customer_id : str, 
                   geotarget_file : str,
                   query_type : str, 
                   campaign_name: str | None = None,
                   start_date_str: str | None = None, # YYYY-MM-DD
                   end_date_str: str | None = None, # YYYY-MM-DD
                   ) -> None:
    save_file_path = f"Data/Report_{query_type}.csv"

    print(f"Starting {query_type} report process...")

    # Build campaign name clause
    campaign_name_clause = util.build_campaign_name_clause(campaign_name)

    # Calculate start_date_str and end_date_str if needed
    start_date_str, end_date_str = util.calc_date_range(start_date_str, end_date_str)

    # Fetch data from Google Ads 
    fecth_function = query.select_query(query_type)
    df: pd.DataFrame = fecth_function(client, customer_id, campaign_name_clause, start_date_str, end_date_str)
    if df.empty:
        print(f"No data found for {query_type}. CSV not created.")
    else:

        # Location mapping if needed
        if set(["State_ID", "Location_ID"]).issubset(df.columns):
            lookup = util.geo_reference(geotarget_file)
            df = util.map_location(df, lookup)
        else:
            print(f"\tSkipping geo mapping for {query_type}.")
        
        # Add date range columns to Dataframe
        df = util.add_date_range(df, start_date_str, end_date_str)

        # Update CSV
        util.update_csv(df, save_file_path)

        # Verify and print the last few rows of the saved CSV
        util.verify_csv(save_file_path)

    print(f"{query_type} report process completed.\n")



# --- Main Execution Block ---
def main():
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    customer_id = str(os.getenv("CUSTOMER_ID"))
    geotarget_file = "geotargets-2025-06-26.csv"

    query_types = ["Ads", "Keywords", "Impressions_and_clicks", "Conversions"]
    campaign_name = str(os.getenv("CAMPAIGN_NAME"))

    # Dates for specific range; commented out to use default in calc_date_range for now
    # start_date_str = "2025-07-06"
    # end_date_str = "2025-07-12"

    for query_type in query_types:
        process_report(client = client,
                       customer_id = customer_id, 
                       geotarget_file = geotarget_file, 
                       query_type = query_type,
                       campaign_name = campaign_name,
                       # If you want to use specific dates, uncomment these:
                       # start_date_str = start_date_str,
                       # end_date_str = end_date_str
                       )
    print("All reports generation process completed.")


if __name__ == "__main__":
    main()