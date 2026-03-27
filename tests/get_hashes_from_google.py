import requests
import json

def get_real_url(g_link):
    try:
        r = requests.get(g_link, allow_redirects=True, timeout=10)
        return r.url
    except Exception as e:
        return str(e)

links = {
    "Delhi": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOGAWYEJJ-ERqN7sMJ12BPOU-3ikqQM0hRgC67wLRG06bhR7lsxBhneOvMRCExifsNIcCvgPOmh2Q8E2kV3-Kq2GegdBQX8vBR0mZz2cJY9sPcLmm47Vhwluxs1WvWuMNOY6oBYzxam3HZG5IlA5CHQZBKrqKsmqPfcuMU8MFtwCZsfDZUK3fEefhw8BQUbJ4XmkSnMw==",
    "Noida": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEapiKtyZEfHwX_rIlDa3Dcf8RabutS_OxyLIK1FsOtyFZSRQIVx_LzoRpiy9dQXWt-5ThnQ9ycrglvoYOexx_TuzQXePBd2k0eotYMwNJthcn4qeWdAg832jtO9M9ZsaqPyhraHOvszcJy0GGSlegTPl95KC8SWdwffMCHCK7AJ8ctwEb6RaE9E4LaYe7Ym4dIng==",
    "Ghaziabad": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHldOMTtlDOjPoEvqXpcCQkQn_wN8hbdmTdABWWehKJawArRgo4nFSq07m_YteF6ogjtvxSoOmKU_cwSfXZbImAbAi-uRN9yIbtvmIOklwNx86XfckLx7MbxLiWs1_3foJ12LNsAOyff8LgB9SYLUln-WfTOllKdYQCnbnQ-RqCrCWCmedi9HjWdIyIm9spXl49luIXc4IxS2QB0OB2V-s="
}

for city, link in links.items():
    print(f"{city}: {get_real_url(link)}")
