import requests
from base64 import b64encode
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

#hard-coded values specific to your Spotify App
client_id = ""
client_secret = ""
redirect_uri = ""
initial_auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=playlist-modify-public%20playlist-modify-private%20playlist-read-private"

#create pool of songs to recommend from 
#the json files were generated from API calls to Spotify but the calls took an extremely long time to run so we stored them locally instead.
with open('pop.json') as json_file:
    pop = json.load(json_file)

with open('hip-hop.json') as json_file:
    hip_hop = json.load(json_file)

with open('country.json') as json_file:
    country = json.load(json_file)

with open('latin.json') as json_file:
    latin = json.load(json_file)

with open('r&b.json') as json_file:
    rb = json.load(json_file)

with open('rock.json') as json_file:
    rock = json.load(json_file)

genre_tracks = pop + hip_hop + country + latin + rb + rock

#uses refresh token to get updated access token
def refresh(client_id, client_secret, refresh_token):

    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode('ascii')
    base64_bytes = b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    headers = {
        'Authorization' : f"Basic {base64_message}"
    }

    data = {
        'grant_type' : 'refresh_token',
        'refresh_token' : refresh_token
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers = headers, data = data).json()
    return response['access_token']

#helper to get auth header
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}




#function used to intialize the json files that created the recommendation pools
def get_genre_tracks(token, genres):
    genre_tracks_list = []
    for genre in genres:
        for i in range(0, 951, 50):


            url = "https://api.spotify.com/v1/search"
            headers = get_auth_header(token)
            query = f"?q=genre%3A{genre}&type=track&limit=50&offset={i}"
            query_url = url + query
            result = requests.get(query_url, headers=headers, verify=False)
            result_data = json.loads(result.content)
            print(result_data.keys())
            for track in result_data['tracks']["items"]:
                info = parse_track_info(track, token)
                genre_tracks_list.append(info)
            print(f'finished {i} offset of {genre}')

    return genre_tracks_list


#extracts the list of features of each song that are used in the recommendation function
def parse_track_info(track, token):
    artist = track['artists'][0]['name']
    name = track['name']
    popularity = track['popularity']
    uri = track['artists'][0]['uri']
    match = re.search(r'^spotify:artist:(.*)$', uri)
    artist_id = ""
    if match:
        artist_id = match.group(1)
    headers = get_auth_header(token)

    query = f"https://api.spotify.com/v1/artists/{artist_id}"

    response_no = requests.get(query, headers = headers, verify=False)

    response = response_no.json()

    genres = response['genres']

    uri = track['uri']
    match = re.search(r'^spotify:track:(.*)$', uri)
    song_id = ""
    if match:
        song_id = match.group(1)
    headers = get_auth_header(token)

    query = f"https://api.spotify.com/v1/audio-features/{song_id}"

    response =  requests.get(query, headers = headers, verify=False).json()
    
    track_dict = {
                'artist' : artist, 'name' : name, 'popularity' : popularity, 'genres' : genres,
                'danceability' : response['danceability'], 'energy' : response['energy'], 'key' : response['key']
                , 'loudness' : response['loudness'], 'speechiness' : response['speechiness'], 'acousticness' : response['acousticness'],
                'instrumentalness' : response['instrumentalness'], 'liveness' : response['liveness'], 'valence' : response['valence'],
                'tempo' : response['tempo'], 'uri' : uri
                 }
    return track_dict


#gets refresh token
def get_refresh_token(client_id, client_secret, auth_token):

    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode('ascii')
    base64_bytes = b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    headers = {
        'Authorization' : f"Basic {base64_message}"
    }

    data = {
        'grant_type' : 'authorization_code',
        'code' : auth_token,
        'redirect_uri' : redirect_uri
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers = headers, data = data)

    response_data = response.json()
    return response_data['refresh_token']


#uses parse_track_info to get the features of all of the songs in a given playlist
def get_playlist_info(playlist_id, user_token):
    headers = get_auth_header(user_token)
    query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.get(query, headers = headers, verify=False)
    response_json = response.json()
    playlist_tracks = []
    for track in response_json['items']:
        info = parse_track_info(track['track'], user_token)
        playlist_tracks.append(info)
    return playlist_tracks

#helper to return the mean of each feature
def get_feature_mean(feature):
    if feature == 'danceability':
        return 0.6491680000000001
    if feature == 'energy':
        return 0.6764713666666666
    if feature == 'key':
        return 5.211166666666666
    if feature == 'loudness':
        return -6.335322333333332
    if feature == 'speechiness':
        return 0.09930975
    if feature == 'instrumentalness':
        return 0.01386333155
    if feature == 'liveness':
        return 0.18163575000000004
    if feature == 'valence':
        return 0.5315491333333333
    if feature == 'tempo':
        return 122.04902316666666
    if feature == 'popularity':
        return 69.43333333333334
    if feature == 'acousticness':
        return 0.19859564371666663

#helper function to get dot products of feature vectors of songs normalized by mean
def get_dot_product(ut, rt):
    # list of variables
    features = ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
              'liveness', 'valence']
    # return dot product normalized by mean
    return sum([(ut[f] - get_feature_mean(f)) * (rt[f] - get_feature_mean(f)) for f in features])

#helper function to get magnitude
def get_magnitude(ut, rt):
    ut_sum = 0
    rt_sum = 0
    # list of variables
    features = ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
              'liveness', 'valence']
    #sum for (user track - mean)^2
    for f in features:
        ut_sum = ut_sum + ((ut[f] - get_feature_mean(f))**2)
        rt_sum = rt_sum + ((rt[f] - get_feature_mean(f))**2)
    # return total magnitude by square rooting both sums and adding them
    return np.sqrt(ut_sum) + np.sqrt(rt_sum)

#helper to return cosine similarity between two songs
def cosine_sim(playlist_song, potential_song):
    # get the dot product and the magnitude of the two songs combined and then divide to solve for cosine similarity
    dot = get_dot_product(playlist_song, potential_song)
    size = get_magnitude(playlist_song, potential_song)
    return dot/size

#gets recommendations using an input playlist and the other helper functions.
def get_recs(playlist, rec_pool):
    playlist_uris = []
    rec_names= []
    for user_track in playlist:
        playlist_uris.append(user_track['uri'])
    print('starting rec search')
    strength_dict = {}
    for user_track in playlist:
        for rec_track in rec_pool:
            #instantiate dictionary entry if it doesn't already exist and it is not already in the user-provided playlist
            if (rec_track['uri'] not in strength_dict) and (rec_track['uri'] not in playlist_uris) and (rec_track['name'] not in rec_names):
                strength_dict[rec_track['uri']] = 0
                rec_names.append(rec_track['name'])
            #if the uri is not already present in the user-provided playlist, it should enter this block
            if (rec_track['uri'] in strength_dict):
                #find the cosine similarity of the user and rec tracks
                strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + cosine_sim(user_track, rec_track)
                
                #add to strength if it matches multiple genres. 
                if len(set(rec_track['genres']).intersection(user_track['genres'])) > 2:
                    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 3
    sorted_list = sorted(strength_dict.items(), key=lambda x:x[1], reverse = True)
    sorted_dict = dict(sorted_list)
    return sorted_dict

#Uses Spotify API to directly create recommended playlist in the user's profile
def make_playlist(user_id, token, new_playlist_name, user_playlist, rec_pool, num_to_add):
        print('started playlist creation')
        query = f"https://api.spotify.com/v1/users/{user_id}/playlists"

        data = json.dumps({
            "name": new_playlist_name, "public": True
        })
        headers = get_auth_header(token)
        response = requests.post(query, data=data, headers=headers)

        response_json = response.json()
        playlist_id = response_json["id"]

        query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        recs_sorted = get_recs(user_playlist, rec_pool)
        uri_list = list(recs_sorted.keys())[0:num_to_add]

        data = json.dumps({
            "uris" : uri_list
        })
        headers = get_auth_header(token)
        response = requests.post(query, data=data, headers=headers)

        response_json = response.json()






#Helps automate the process of retreiving all neccessary tokens
def get_redirected_urls(initial_url, username, password, max_redirects=100, timeout=100):
    # Create a new instance of a web driver
    driver = webdriver.Chrome()

    # Navigate to the initial URL
    driver.get(initial_url)

    # Fill in login credentials
    username_field = driver.find_element(By.ID, 'login-username')
    username_field.send_keys(username)
    time.sleep(5)  # Pause for 2 seconds to let user see the input
    password_field = driver.find_element(By.ID, "login-password")
    password_field.send_keys(password)
    time.sleep(5)  # Pause for 2 seconds to let user see the input
    password_field.send_keys(Keys.RETURN)

    # Wait for page to load
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Get all redirected URLs
    urls = []
    redirects = 0
    while redirects < max_redirects:
        current_url = driver.current_url
        if current_url not in urls:
            urls.append(current_url)
            time.sleep(5)
        else:
            break
            

        driver.get(current_url)
        redirects += 1

    # Close the driver
    driver.quit()

    return urls


#helper to parse authorization code from final redirected url
def parse_for_authorization_code(url) :
    pattern = r"code=(.*)"
    match = re.search(pattern, url)
    code_value = ""
    if match:
        code_value = match.group(1)
    return code_value

#consolidates all helper functions for a clean main file 
def complete_rec(username, password, user_id, playlist_id, new_playlist_title, new_playlist_length) :
    auth_url = get_redirected_urls(initial_auth_url, username, password)[-1]
    auth_token = parse_for_authorization_code(auth_url)
    refresh_token = get_refresh_token(client_id=client_id, client_secret=client_secret, auth_token=auth_token)
    refreshed_user_token = refresh(client_id, client_secret, refresh_token)
    playlist_info = get_playlist_info(playlist_id, refreshed_user_token)
    make_playlist(user_id, refreshed_user_token, new_playlist_title, playlist_info, genre_tracks, new_playlist_length)
