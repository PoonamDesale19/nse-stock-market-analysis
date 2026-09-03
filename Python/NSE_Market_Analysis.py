#!pip install azure-storage-blob
import subprocess
import os
import shutil
from azure.identity import AzureCliCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
import numpy as np


####################################################################################
#  FUNCTION TO GET A FILE FROM AZURE STORAGE
####################################################################################

def get_file_from_storage():

    credential=AzureCliCredential()
    
    storage_account_name="nsemarketdat2026"
    url=f"https://{storage_account_name}.blob.core.windows.net"
    blob_service_client=BlobServiceClient(account_url=url,credential=credential)
    print("Connected to azure store")
    import pandas as pd
    
    # Connect to raw container
    container_client = blob_service_client.get_container_client("raw")
    
    # Get only BhavCopy files from raw/nse/
    nse_blobs = [
        blob
        for blob in container_client.list_blobs(name_starts_with="nse/")
        if "BhavCopy" in blob.name
    ]
    
    if not nse_blobs:
        print("No BhavCopy files found in raw/nse/")
    else:
        # Select the latest BhavCopy file
        latest_blob = max(
            nse_blobs,
            key=lambda x: x.last_modified
        )
    
        print("Latest BhavCopy file:")
        print(latest_blob.name)
        print("Last modified:", latest_blob.last_modified)
    
        # Download latest file
        blob_client = container_client.get_blob_client(
            latest_blob.name
        )
    
        local_file = "latest_bhavcopy.csv"
    
        with open(local_file, "wb") as f:
            f.write(blob_client.download_blob().readall())
    
        # Read CSV
        df = pd.read_csv(local_file)
        
        print("Rows:", len(df))
        print("Columns:", len(df.columns))
    
        df.head()
        return df




############################################################################
# PROCESS THE FILE FROM STORAGE
############################################################################


def process_nse_file(file):

    # Read NSE CSV
    import pandas as pd
    import numpy as np

    nse=file
    # Keep Equity only
    equity = nse[nse["SctySrs"] == "EQ"].copy()

    # Convert date
    equity["TradDt"] = pd.to_datetime(
        equity["TradDt"],
        errors="coerce"
    )
   
    # Price change %
    equity["ChangePct"] = (
        (equity["ClsPric"] - equity["PrvsClsgPric"])
        / equity["PrvsClsgPric"]
    ) * 100

    # Turnover in ₹ Crore
    equity["TurnOver_cr"] = equity["TtlTrfVal"] / 1e7

    # Daily maximum price movement
    daily_max_move = (
        equity.groupby("TradDt")["ChangePct"]
        .transform(lambda x: x.abs().max())
        .replace(0, np.nan)
    )

    # Daily maximum volume
    daily_max_volume = (
        equity.groupby("TradDt")["TtlTradgVol"]
        .transform("max")
        .replace(0, np.nan)
    )

    # Daily maximum turnover
    daily_max_turnover = (
        equity.groupby("TradDt")["TtlTrfVal"]
        .transform("max")
        .replace(0, np.nan)
    )

    # Scores
    equity["PriceScore"] = (
        equity["ChangePct"].abs() / daily_max_move
    )

    equity["VolumeScore"] = (
        equity["TtlTradgVol"] / daily_max_volume
    )

    equity["TurnoverScore"] = (
        equity["TtlTrfVal"] / daily_max_turnover
    )

    # Market strength
    equity["MarketStrengthScore"] = (
        equity["PriceScore"] * 0.5
        + equity["VolumeScore"] * 0.2
        + equity["TurnoverScore"] * 0.3
    )

    # Daily thresholds
    daily_75th = (
        equity.groupby("TradDt")["MarketStrengthScore"]
        .transform(lambda x: x.quantile(0.75))
    )

    daily_median = (
        equity.groupby("TradDt")["MarketStrengthScore"]
        .transform("median")
    )

    # Signal
    conditions = [
        (equity["ChangePct"] > 0) &
        (equity["MarketStrengthScore"] >= daily_75th),

        (equity["ChangePct"] < 0) &
        (equity["MarketStrengthScore"] >= daily_75th),

        (equity["ChangePct"] > 0) &
        (equity["MarketStrengthScore"] >= daily_median) &
        (equity["MarketStrengthScore"] < daily_75th),

        (equity["ChangePct"] < 0) &
        (equity["MarketStrengthScore"] >= daily_median) &
        (equity["MarketStrengthScore"] < daily_75th)
    ]

    choices = [
        "Strong Bullish",
        "Strong Bearish",
        "Moderate Bullish",
        "Moderate Bearish"
    ]

    equity["Signal"] = np.select(
        conditions,
        choices,
        default="Weak"
    )
     # Market Movers
    equity["MarketMoverScore"] = (
        equity["ChangePct"].abs()
        * equity["TurnOver_cr"]
    )

    equity["ClsPric"] = pd.to_numeric(equity["ClsPric"],errors="coerce")
    equity["PrvsClsgPric"] = pd.to_numeric(equity["PrvsClsgPric"],errors="coerce")
    equity["TtlTrfVal"] = pd.to_numeric(equity["TtlTrfVal"],errors="coerce")
    equity["HghPric"] = pd.to_numeric(equity["HghPric"],errors="coerce")
    equity["LwPric"] = pd.to_numeric(equity["LwPric"],errors="coerce")
    equity["OpnPric"] = pd.to_numeric(equity["OpnPric"],errors="coerce")
    equity["ChangePct"] = pd.to_numeric(equity["ChangePct"],errors="coerce")
    equity["MarketStrengthScore"] = pd.to_numeric(equity["MarketStrengthScore"],errors="coerce")
    equity["MarketMoverScore"] = pd.to_numeric(equity["MarketMoverScore"],errors="coerce")
    equity["TtlTradgVol"] = pd.to_numeric(equity["TtlTradgVol"],errors="coerce")
    # Keep only required columns
    required_columns = [
        "TradDt",
        "TckrSymb",
        "FinInstrmNm",
        "HghPric",
        "LwPric",
        "OpnPric",
        "ClsPric",
        "PrvsClsgPric",
        "ChangePct",
        "TtlTrfVal",
        "TurnOver_cr",
        "PriceScore",
        "VolumeScore",
        "TurnoverScore",
        "MarketStrengthScore",
        "Signal",
        "MarketMoverScore"
    ]
    
    equity = equity[required_columns]
   
    # Top Bullish
    top_bullish = (
        equity[
            equity["Signal"].isin(
                ["Strong Bullish", "Moderate Bullish"]
            )
        ]
        .sort_values("MarketStrengthScore", ascending=False)
        .head(20)
        .copy()
    )

    # Top Bearish
    top_bearish = (
        equity[
            equity["Signal"].isin(
                ["Strong Bearish", "Moderate Bearish"]
            )
        ]
        .sort_values("MarketStrengthScore", ascending=False)
        .head(20)
        .copy()
    )

   

    market_movers = (
        equity
        .sort_values("MarketMoverScore", ascending=False)
        .head(20)
        .copy()
    )
     
    return equity, top_bullish, top_bearish, market_movers

file=get_file_from_storage()
equity,top_bullish,top_bearish,market_movers= process_nse_file(file)
print(equity,top_bullish)


###############################################################
#CHECK IF FILE IS NEW THEN APPEND
###################################################################

def append_if_new_date(new_data,file_path,date_column="TradDt"):
    
    new_data = new_data.copy()
    new_data[date_column] = pd.to_datetime(
        new_data[date_column],
        errors="coerce"
    )

    new_date = new_data[date_column].max()

    if os.path.exists(file_path):

        existing = pd.read_csv(file_path)

        existing[date_column] = pd.to_datetime(
            existing[date_column],
            errors="coerce"
        )

        existing_dates = (
            existing[date_column]
            .dt.normalize()
            .dropna()
            .unique()
        )

        if new_date.normalize() in existing_dates:

            print(f"{new_date.date()} already exists.")
            print("No data appended.")

            return existing

        else:

            updated = pd.concat(
                [existing, new_data],
                ignore_index=True
            )

            updated.to_csv(
                file_path,
                index=False
            )

            print(f"{new_date.date()} appended successfully.")
            print("Total rows:", len(updated))

            return updated

    else:

        new_data.to_csv(
            file_path,
            index=False
        )

        print("File created successfully.")
        print("Total rows:", len(new_data))

        return new_data 



##################################################################################

# DAILY SUMMERY 
#SAVE ALL FILES TO PROCESSED
###############################################################################

history_file = r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\NSE_Stock_Signals_History.csv"
Daily_Market_Summary_file= r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Daily_Market_Summary.csv"
Top_Bearish_file= r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Top_Bearish.csv"
Top_Bullish_file= r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Top_Bullish.csv"
Market_Movers_file= r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Market_Movers.csv"
   


 # Current trading date

current_date = equity["TradDt"].max()

if os.path.exists(history_file):

    history = pd.read_csv(history_file)

    history["TradDt"] = pd.to_datetime(
        history["TradDt"],
        errors="coerce"
    )

    if current_date.normalize() in history["TradDt"].dt.normalize().values:
        print("This date already exists.")
        print("No data appended.")

    else:
        history = pd.concat(
            [history, equity],
            ignore_index=True
        )

        history.to_csv(
            history_file,
            index=False
        )

        print("New date appended successfully!")

else:

    equity.to_csv(
        history_file,
        index=False
    )

print("History file created successfully!")
daily_summary = (
        history.groupby("TradDt")
        .agg(
            TotalStocks=("TckrSymb", "count"),
            StrongBullish=("Signal", lambda x: (x == "Strong Bullish").sum()),
            ModerateBullish=("Signal", lambda x: (x == "Moderate Bullish").sum()),
            StrongBearish=("Signal", lambda x: (x == "Strong Bearish").sum()),
            ModerateBearish=("Signal", lambda x: (x == "Moderate Bearish").sum()),
            Weak=("Signal", lambda x: (x == "Weak").sum()),
            AvgMarketStrength=("MarketStrengthScore", "mean"),
            MarketMoverScore=("MarketMoverScore", "mean"),
            TotalTurnover=("TtlTrfVal", "sum")
        )
        .reset_index()
    )
    
    
daily_summary["MarketDirection"] = np.select(
        [
            daily_summary["StrongBullish"] > daily_summary["StrongBearish"],
            daily_summary["StrongBearish"] > daily_summary["StrongBullish"]
        ],
        [
            "Bullish",
            "Bearish"
        ],
        default="Neutral"
)
daily_summary.to_csv(
        r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Daily_Market_Summary.csv",
        index=False
    )

top_bullish_history = append_if_new_date(
    top_bullish,
    Top_Bullish_file
)
top_bearish_history = append_if_new_date(
    top_bearish,
    Top_Bearish_file
)
market_movers_history = append_if_new_date(
    market_movers,
    Market_Movers_file
)

print("History updated successfully")
print("Top Bullish And Top Bearish files created succeefully")
print("Trading dates:", history["TradDt"].nunique())
print("Total rows:", len(history))
        
print("All NSE files saved successfully!")


########################################################################
# DOWNLOAD PROCESSED FILE TO STORAGE
########################################################################
credential=AzureCliCredential()

az_path=shutil.which("az")
result=subprocess.run(
    [az_path,"account","show"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)


storage_account_name="nsemarketdat2026"
url=f"https://{storage_account_name}.blob.core.windows.net"
blob_service_client=BlobServiceClient(account_url=url,credential=credential)
print("Connected to azure store")

container_client=blob_service_client.get_container_client("processed")
gold_files={
    r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\NSE_Stock_Signals_History.csv",
    r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Daily_Market_Summary.csv",
    r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Top_Bullish.csv",
    r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Top_Bearish.csv",
    r"C:\Users\poonam desale\OneDrive\Documents\DataAnalystProject\NseProject\Processed\Gold\Market_Movers.csv"
    
}
for file_path in gold_files:
    file_name=os.path.basename(file_path)
    with open(file_path,"rb")as data:
        blob_client=container_client.get_blob_client(f"nse/{file_name}")
        blob_client.upload_blob(data,overwrite=True)
        print(f"uploaded nse/{file_name} successfully")

for blob in container_client.list_blobs():
    print(blob.name)

token=credential.get_token("https://storage.azure.com/.default")
print("successful")



