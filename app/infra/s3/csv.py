from io import StringIO

import boto3
import pandas as pd


class S3CsvInferface:
    def __init__(self, bucket: str):
        self.s3 = boto3.resource("s3", endpoint_url="http://localhost:4566")
        self.bucket = bucket

    def save_csv(self, df: pd.DataFrame, filename: str) -> None:
        s3_obj = self.s3.Object(self.bucket, filename)
        s3_obj.put(Body=df.to_csv(None, index=False).encode("utf8"))

    def load_csv(self, filename: str) -> pd.DataFrame:
        obj = self.s3.Object(self.bucket, filename)
        body_in = obj.get()["Body"].read().decode("utf8")
        buffer_in = StringIO(body_in)
        loaded_df = pd.read_csv(buffer_in)
        return loaded_df


def main():
    filename = "historical_data/sample_candles.csv"
    df = pd.read_csv(filename, nrows=15)
    print(df)

    s3_inferface = S3CsvInferface(bucket="historical-data")
    save_name = "test.csv"

    s3_inferface.save_csv(df, save_name)

    loaded_df = s3_inferface.load_csv(save_name)
    print(loaded_df)


if __name__ == "__main__":
    main()
