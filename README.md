# Google Ads Report Generator

Retrieve metrics (Ads, Keywords, Impressions, Clicks, Conversions, and Geographic data) from Google Ads.


## What You Needs
  
- **Google Ads API Access:** A Developer Token, and OAuth 2.0 credentials (Client ID, Client Secret, Refresh Token). Follow [my blog post](https://jhjang101.github.io/Google-Ads-API-in-Python/) or [Google documentation](https://developers.google.com/google-ads/api/docs/start) to obtain the API access and put those in `google-ads.yaml`

    ```
    developer_token: YOUR_DEVELOPER_TOKEN
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET
    refresh_token: YOUR_REFRESH_TOKEN
    login_customer_id: YOUR_MCC_CUSTOMER_ID
    ```

- **Environment Variable Configuration (`.env` file):** You need Google Ads `CUSTOMER_ID`. Optionally, you can specify `CAMPAIGN_NAME`.

    ```
    CUSTOMER_ID=YOUR_GOOGLE_ADS_CUSTOMER_ID_WITHOUT_HYPHENS # e.g., 1234567890
    CAMPAIGN_NAME=Your Specific Campaign Name # Optional: Omit this line to query all enabled campaigns.
    ```
- **Required Python Libraries:** `google-ads`, `pandas`, and `python-dotenv`


## Output Reports

The generated CSV files, including mapped geographical locations and specified date ranges, will be accessible in the `Data/` directory.

## TODOs

- Create CSV files with headers if no files found.
- Get list of geotargets using API.