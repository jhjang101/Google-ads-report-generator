from google.ads.googleads.client import GoogleAdsClient
import pandas as pd


# --- Selector Function for get_query ---
def select_query(query_type: str):
    """
    Returns the appropriate get_query function based on the query_type.
    """
    function_map = {
            "Ads": get_ads,
            "Keywords": get_keywords,
            "Impressions_and_clicks": get_impressions_clicks,
            "Conversions": get_conversions,
        }
    func = function_map.get(query_type)
    if func is None:
        raise ValueError(f"No metrics function found for query_type: '{query_type}'. "
                         f"Available types are: {list(function_map.keys())}")
    return func
    

# --- Fetch Function for Ads ---
def get_ads(
        client: GoogleAdsClient, 
        customer_id: str, 
        campaign_name_clause: str, # <AND campaign.status = 'ENABLED'> or <AND campaign.name = 'YourCampaignName'>
        start_date_str: str, 
        end_date_str: str
        ) -> pd.DataFrame:
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group.status,
            ad_group_ad.ad.final_urls,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        {campaign_name_clause}
        AND ad_group.status = 'ENABLED'
        """    

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    # Access the iterator and convert to dataframe.
    data = []
    for batch in stream:
        for row in batch.results:
            data.append({
                "Campaign_Name" : row.campaign.name,
                "Ad_product" : row.ad_group_ad.ad.final_urls[0][-5:-1],
                "Impressions" : row.metrics.impressions, 
                "Clicks" : row.metrics.clicks,
                "Conversions" : int(row.metrics.conversions), 
                "Cost" : round(row.metrics.cost_micros/1e+6, 2)
            })
    df = pd.DataFrame(data)

    # Check number of rows in fetched data.
    num_row = df.shape[0]
    if num_row:
        print(f"\tSuccessfully received {num_row} rows of data from Google Ads.")

    return df


# --- Fetch Function for Keywords ---
def get_keywords(client: GoogleAdsClient, 
                 customer_id: str, 
                 campaign_name_clause: str, # <AND campaign.status = 'ENABLED'> or <AND campaign.name = 'YourCampaignName'>
                 start_date_str: str, 
                 end_date_str: str
                 ) -> pd.DataFrame:
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_criterion.criterion_id, 
            ad_group_criterion.keyword.text, 
            ad_group_criterion.status, 
            metrics.impressions,
            metrics.clicks,
            metrics.average_cpc,
            metrics.conversions,
            metrics.conversions_value
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        {campaign_name_clause}
        AND ad_group.status = 'ENABLED'
        AND ad_group_criterion.status = 'ENABLED' -- Ensures only get data for ENABLED keywords
        """    

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    # Access the iterator and convert to dataframe.
    data = []
    for batch in stream:
        for row in batch.results:
            data.append({
                "Keyword" : row.ad_group_criterion.keyword.text,
                "Impressions" : row.metrics.impressions, 
                "Clicks" : row.metrics.clicks, 
                "Cost_per_Click" : round(row.metrics.average_cpc/1e+6,2),
                "Conversions" : int(row.metrics.conversions), 
                "Conversions_Value" : float(row.metrics.conversions_value)
            })
    df = pd.DataFrame(data)

    # Check number of rows in fetched data.
    num_row = df.shape[0]
    if num_row:
        print(f"\tSuccessfully received {num_row} rows of data from Google Ads.")

    return df


# --- Fetch Function for Impressions_and_clicks ---
def get_impressions_clicks(client: GoogleAdsClient, 
                           customer_id: str, 
                           campaign_name_clause: str, # <AND campaign.status = 'ENABLED'> or <AND campaign.name = 'YourCampaignName'>
                           start_date_str: str, 
                           end_date_str: str
                           ) -> pd.DataFrame:
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.geo_target_state,
            segments.geo_target_most_specific_location,
            segments.date,
            metrics.impressions,
            metrics.clicks
        FROM geographic_view
        WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        {campaign_name_clause}        
        """    

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    # Access the iterator and convert to dataframe.
    data = []
    for batch in stream:
        for row in batch.results:
            data.append({
                "State_ID" : row.segments.geo_target_state,
                "Location_ID": row.segments.geo_target_most_specific_location,
                "Date" : row.segments.date,
                "Impressions" : row.metrics.impressions, 
                "Clicks" : row.metrics.clicks, 
            })
    df = pd.DataFrame(data)

    # Check number of rows in fetched data.
    num_row = df.shape[0]
    if num_row:
        print(f"\tSuccessfully received {num_row} rows of data from Google Ads.")
    
    return df

# --- Fetch Function for Conversions ---
def get_conversions(client: GoogleAdsClient, 
                    customer_id: str, 
                    campaign_name_clause: str, # <AND campaign.status = 'ENABLED'> or <AND campaign.name = 'YourCampaignName'>
                    start_date_str: str, 
                    end_date_str: str
                    ) -> pd.DataFrame:
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.geo_target_state,
            segments.geo_target_most_specific_location,
            segments.date,
            segments.conversion_action_name,
            metrics.conversions
        FROM geographic_view
        WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        {campaign_name_clause}
        """    

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    # Access the iterator and convert to dataframe.
    data = []
    for batch in stream:
        for row in batch.results:
            data.append({
                "State_ID" : row.segments.geo_target_state,
                "Location_ID": row.segments.geo_target_most_specific_location,
                "Date" : row.segments.date,
                "Conversions" : int(row.metrics.conversions), 
                "Conversions_Action" : row.segments.conversion_action_name, 
            })
    df = pd.DataFrame(data)

    # Check number of rows in fetched data.
    num_row = df.shape[0]
    if num_row:
        print(f"\tSuccessfully received {num_row} rows of data from Google Ads.")

    return df

if __name__ == "__main__":
    pass
