import klaviyo  # friendly interface to Track & Identify API
import requests  # standard http library, used to provide interface to Templates API and Pexels API
import urllib.parse  # used for URL encoding
import json  # Pexels response is JSON formatted
from types import SimpleNamespace  # used to parse Pexels JSON response into an object

pub_key = 'INSERTKEY'  # Klaviyo Public Key
pri_key = 'INSERTKEY'  # Klaviyo Private Key - this should never be exposed to public

pexels_key = 'INSERTKEY'  # Pexels Key - this should never be exposed to public

'''
The Track API is intended to capture unique customer events (metrics).
In order to demonstrate interfacing with the Track API, we will use it here to create metrics to serve as a log for
whenever the "Business Owner" pulls media from Pexels and pushes it to Klaviyo.
'''
business_owner = klaviyo.Klaviyo(public_token=pub_key, private_token=pri_key)

template_url = "https://a.klaviyo.com/api/v1/email-templates"  # Template API endpoint
pexels_url = "https://api.pexels.com/v1"  # Pexels base endpoint

# Make business owner profile picture the Pexel Logo
business_owner_logo = "https://theme.zdassets.com/theme_assets/9028340/1e73e5cb95b89f1dce8b59c5236ca1fc28c7113b.png"

pexel_headers = {  # Pexel GET request headers (Authentication provided in header)
    "Accept": "application/json",
    "Authorization": pexels_key
}

pexels_url_search = pexels_url + "/search"  # Pexels image search API endpoint
query_str = input("Please type your image search request:") # Prompt user for image search

pexels_params = {  # set parameters for Pexel query
    "query":query_str,
    "page":1,
    "per_page":1  # get only 1 image
}

'''
Send a GET request to Pexel, searching for images that match the user's input
An image will be returned. The JSON response data can be found in pexel_response.text
'''
pexel_response = requests.request("GET", pexels_url_search, headers=pexel_headers, params=pexels_params)

# Convert the JSON data into an object in python
pexel_response_obj = json.loads(pexel_response.text, object_hook=lambda d: SimpleNamespace(**d))

pexel_img_large2x = pexel_response_obj.photos[0].src.large2x  # get the URL of the image (large2x format)
pexel_img_small = pexel_response_obj.photos[0].src.small      # get the URL of the image (small format)

template_name = query_str + " template"  # what we will name our new Klaviyo template
template_name_URL_enc = urllib.parse.quote(template_name)  # URL encode the template name

html_template = "<html><body><img src=" + pexel_img_large2x + "></body></html>"  # Insert picture into simple HTML structure
html_template_URL_enc = urllib.parse.quote(html_template)  # URL encode template content to prepare it for sending to Klaviyo

payload = "api_key=" + pri_key + "&name=" + template_name_URL_enc + "&html=" + html_template_URL_enc  # create the payload for Klaviyo POST request

klaviyo_headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.request("POST", template_url, data=payload, headers=klaviyo_headers)  # push image to Klaviyo, create new template


def logPexelsImportAsMetric():
    business_owner.Public.track(
        'Imported Pexels Image',
        email='ninaephremidze@gmail.com',  # represents business owner, although Track API is intended to track customers
        customer_properties={
            "$first_name":"Business",
            "$last_name":"Owner",
            "$city":"Tblisi",
            "$phone_number":"4797904555",
            "image": business_owner_logo,
        },
        properties={
            "image":pexel_img_small,
            "search_term":query_str
        }
    )

logPexelsImportAsMetric()

print("Imported Image from Pexels to Klaviyo!")