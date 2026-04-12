import requests

url = "https://www.fcbarcelona.com/en/tickets/football/regular/laliga/fcbarcelona-realmadrid?_gl=1*1w2gghi*_gcl_aw*R0NMLjE3NzU4MTUwNzQuQ2owS0NRand2LUxPQmhDZEFSSXNBTTVoZEtkV2JUQk9od3AzYjJ3RkNMLWhHcXRUbWxlcWEyaDM4WlZ1UVo4bjFMeDJfZ3MwWTExMF81c2FBdnJYRUFMd193Y0I.*_gcl_dc*R0NMLjE3NzU4MTUwNzQuQ2owS0NRand2LUxPQmhDZEFSSXNBTTVoZEtkV2JUQk9od3AzYjJ3RkNMLWhHcXRUbWxlcWEyaDM4WlZ1UVo4bjFMeDJfZ3MwWTExMF81c2FBdnJYRUFMd193Y0I.*_gcl_au*MzQzMzkxOTUxLjE3NzQzNTI1NzE."
html = requests.get(url).text

if "Temporarily unavailable" in html:
    print("Found!")