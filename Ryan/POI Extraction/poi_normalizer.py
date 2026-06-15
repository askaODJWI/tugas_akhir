import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_with_poi.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "scaled_poi_density.npy")


def main():
    df = pd.read_csv(INPUT_FILE)

    poi_columns = [
        "POI_Pendidikan",
        "POI_Kesehatan_Kebugaran",
        "POI_Transportasi",
        "POI_Perbelanjaan",
        "POI_Olahraga_Rekreasi",
        "POI_Tempat_Ibadah",
        "POI_Makanan_Minuman",
        "POI_Fasilitas_Keuangan",
        "POI_Lainnya",
    ]

    # Normalisasi (0 sampai 1)
    poi_data = df[poi_columns].fillna(0).values
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(poi_data)

    np.save(OUTPUT_FILE, scaled_data)
    print(f"Proses selesai. Cek file {os.path.basename(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()
