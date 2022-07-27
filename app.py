import requests
import os
import json
from functools import reduce

apiURL = "https://www.warcraftlogs.com/api/v2/client"
tokenURL = "https://www.warcraftlogs.com/oauth/token"

def get_token(store : bool = False) -> requests.models.Response:
    """Retrieves access token for a given client id and secret."""
    data = {"grant_type": "client_credentials"}
    auth = (os.environ.get("user_id"),
                os.environ.get("user_secret"))
    with requests.Session() as session:
        response = session.post(tokenURL ,
                                                data = data ,
                                                auth = auth)
    if store and response.status_code == 200:
        store_token(response)
    return response

def store_token(response : requests.models.Response):
    """Stores token to a hidden json file."""
    try:
        with open(".credentials.json" , mode = "w+" , encoding = "utf-8") as file:
            json.dump(response.json() , file)
    except OSError as e:
        print(e)
        print("Could not create the file!")


def retrieve_token():
    """Extracts access token from json file."""
    try:
        with open(".credentials.json" , mode = "r+" , encoding = "utf-8") as file:
            return json.load(file)
    except OSError as e:
        print(e)
        return

def retrieve_headers() -> dict[str , str]:
    """Retrieves authorization headers to use the public wclogs API."""
    return {"Authorization":f"Bearer {retrieve_token().get('access_token')}"}

reportData = """query ($code:String){
        reportData{
                report(code:$code){
                        fights(difficulty:3){
                            id
                            name
                            startTime
                            endTime
                            }
                        }
                    }
                    }"""

def getData(query , **kwargs):
    """Sends a general query to wclogs API to retrieve report data. The kwargs contain information about the particular endpoint.
    we wish to extract data from. For instance, if we want to extract reportData we must specify as keyword argument the code
    for the report. In general, we the kwargs must contain all the arguments of the query otherwise an exception will be raised.
    Furthermore, you can also specify a ditchItems key which drops unnecessary information."""

    ditchItems = kwargs.pop("ditchItems") if "ditchItems" in kwargs else None
    data = {"query" : query , "variables" : kwargs}
    with requests.Session() as session:
        session.headers = retrieve_headers()
        response = session.get(apiURL , json = data)
    if response.status_code == 200:
        response = response.json()
        return reduce(lambda acc , val : acc.get(val) , ditchItems , response) if ditchItems else response
    return response.json().get("error")

def main():
    ##Step I: retrieve access token for our application
    response = get_token(store = True)
    #Step II: get data for our application
    #example code
    code = "AGF3JyRmg27fN4TV"
    print(getData(reportData , ditchItems = ["data" , "reportData" , "report" , "fights" ] , code = code))

if __name__ == "__main__": main()
