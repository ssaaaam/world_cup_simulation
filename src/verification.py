import pandas as pd

def select_random_matches(df, n, seed=50):
    if n > len(df):
        print(f"Avís: S'han demanat {n} partits, però el dataset només en té {len(df)}. Retornant el dataset sencer.")
        return df.sample(frac=1, random_state=seed)
    
    return df.sample(n=n, random_state=seed)    


if __name__ == "__main__":
    # Carreguem les dades
    datapath = "./data/raw/results.csv"
    df = pd.read_csv(datapath)
    
    print(select_random_matches(df, 10))