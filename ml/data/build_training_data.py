# | year | state | county  | crop  | yield | rain | temp | previous_yield | price |
# | ---- | ----- | ------- | ----- | ----- | ---- | ---- | -------------- | ----- |
# | 2022 | WA    | WHITMAN | WHEAT | 82    | 14.2 | 63   | 79             | 7.20  |


import pandas as pd
import os


YIELD_FILE = (
    "ml/data/processed/yield_data.csv"
)

WEATHER_FILE = (
    "ml/data/processed/weather_data.csv"
)

PRICE_FILE = (
    "ml/data/processed/price_data.csv"
)


OUTPUT_FILE = (
    "ml/data/processed/training_data.csv"
)



# -----------------------------
# CLEAN FUNCTIONS
# -----------------------------

def clean_strings(df):

    df = df.copy()


    for col in [
        "state",
        "county",
        "crop"
    ]:

        if col in df.columns:

            df[col] = (
                df[col]
                .astype(str)
                .str.upper()
                .str.strip()
            )


    return df



# -----------------------------
# LOAD DATA
# -----------------------------

def build_training_data():


    print("Loading datasets...")


    yield_df = pd.read_csv(
        YIELD_FILE
    )


    weather_df = pd.read_csv(
        WEATHER_FILE
    )


    price_df = pd.read_csv(
        PRICE_FILE
    )



    yield_df = clean_strings(
        yield_df
    )


    weather_df = clean_strings(
        weather_df
    )


    price_df = clean_strings(
        price_df
    )



    # numeric cleanup

    yield_df["year"] = (
        pd.to_numeric(
            yield_df["year"],
            errors="coerce"
        )
    )


    weather_df["year"] = (
        pd.to_numeric(
            weather_df["year"],
            errors="coerce"
        )
    )


    price_df["year"] = (
        pd.to_numeric(
            price_df["year"],
            errors="coerce"
        )
    )



    # -----------------------------
    # MERGE WEATHER
    # -----------------------------


    print("Merging weather...")


    df = yield_df.merge(

        weather_df,

        on=[
            "state",
            "county",
            "year"
        ],

        how="inner"

    )



    print(
        "After weather merge:",
        len(df)
    )



    # -----------------------------
    # MERGE PRICE
    # -----------------------------


    print("Merging prices...")


    df = df.merge(

        price_df,

        on=[
            "crop",
            "year"
        ],

        how="left"

    )



    print(
        "After price merge:",
        len(df)
    )



    # -----------------------------
    # CLEAN MISSING VALUES
    # -----------------------------


    df = df.dropna(
        subset=[
            "yield"
        ]
    )



    # Fill missing prices
    # (some crops may not have yearly prices)

    df["price"] = (
        df.groupby("crop")["price"]
        .transform(
            lambda x:
            x.fillna(
                x.mean()
            )
        )
    )



    # Remove remaining missing rows

    df = df.dropna()



    # -----------------------------
    # SAVE
    # -----------------------------


    os.makedirs(
        "ml/data/processed",
        exist_ok=True
    )


    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print()
    print(
        "Training dataset created"
    )

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:"
    )

    print(
        df.columns.tolist()
    )



if __name__ == "__main__":

    build_training_data()