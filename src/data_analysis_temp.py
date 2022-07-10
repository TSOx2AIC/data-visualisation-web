import os  
import json
import pandas as pd

def load_data():
    user_data = {}
    top_50 = pd.DataFrame()

    #entries = os.listdir("data/clean")
    
    entries = os.listdir("../data/clean")
    #entries.remove('.DS_Store')
    for entry in entries:
        # Load user info
        # with open("data/clean/" + entry + "/userinfo.json") as f:
        with open("../data/clean/" + entry + "/userinfo.json") as f:
            user_data[entry] = json.load(f)
        
        # Load top 50 data
        #df = pd.read_csv("data/clean/" + entry + "/top50.csv")
        df = pd.read_csv("../data/clean/" + entry +  "/top50.csv")
        df["user_id"] = user_data[entry]["id"]
        top_50 = top_50.append(df, ignore_index=True)
    return user_data, top_50


def main():
    user_data, top_50 = load_data()
    print(top_50)


if __name__ == "__main__":
    main()
