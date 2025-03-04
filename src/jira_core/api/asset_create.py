# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json

url = "https://api.atlassian.com/jsm/assets/workspace/{workspaceId}/v1/object/create"

headers = {
  "Accept": "application/json",
  "Content-Type": "application/json",
  "Authorization": "Bearer <access_token>"
}

payload = json.dumps( {
  "objectTypeId": "23",
  "attributes": [
    {
      "objectTypeAttributeId": "135",
      "objectAttributeValues": [
        {
          "value": "NY-1"
        }
      ]
    },
    {
      "objectTypeAttributeId": "144",
      "objectAttributeValues": [
        {
          "value": "99"
        }
      ]
    }
  ]
} )

response = requests.request(
   "POST",
   url,
   data=payload,
   headers=headers
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))