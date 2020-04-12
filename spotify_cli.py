#########################################
##### Name: Xiao Cheng              #####
##### Uniqname: xchengx             #####
#########################################

from requests_oauthlib import OAuth1
from spotipy.oauth2 import SpotifyClientCredentials
import os
import json
import requests
import sqlite3
import spotipy

# Secrets
import twitter_secrets
import spotify_secrets

# Our own objects
from spotify_objects import Artist
from spotify_objects import Track
from spotify_objects import Playlist
from spotify_objects import Twitter

# Twitter config
twitter_client_key = twitter_secrets.TWITTER_API_KEY
twitter_client_secret = twitter_secrets.TWITTER_API_SECRET
twitter_access_token = twitter_secrets.TWITTER_ACCESS_TOKEN
twitter_access_token_secret = twitter_secrets.TWITTER_ACCESS_TOKEN_SECRET

twitter_oauth = OAuth1(twitter_client_key,
            client_secret=twitter_client_secret,
            resource_owner_key=twitter_access_token,
            resource_owner_secret=twitter_access_token_secret)

twitter_base_url = "https://api.twitter.com/1.1/search/tweets.json"

# Local database config
from data_accessor import DataAccessor
local_db_name = 'final_pj.sqlite'
local_db_accessor = DataAccessor(local_db_name)


# Spotify config
# Set environment variables for spotipy
spotify_client_id = spotify_secrets.SPOTIFY_CLIENT_ID
spotify_client_secret = spotify_secrets.SPOTIFY_CLIENT_SECRET
os.environ['SPOTIPY_CLIENT_ID'] = spotify_client_id
os.environ['SPOTIPY_CLIENT_SECRET'] = spotify_client_secret
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())



# Connectivity test functions
def test_twitter_oauth():
    ''' Test twittwer oauth. Expect 200 OK.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    Dict 
        A dict representing authorization result
    '''
    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    authentication_state = requests.get(url, auth=twitter_oauth).json()
    return authentication_state

def test_spotify_oauth():
    ''' Test spotify oauth. Expect 200 OK.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    Dict
        A dict representing authorization result
    '''
    lz_uri = 'spotify:artist:3WGpXCj9YhhfX11TToZcXP'
    
    results = spotify.artist_top_tracks(lz_uri)
    return results



# Spotify converters
def convert_spotify_artist_object(spotify_object):
    ''' Object converter
    
    Parameters
    ----------
    Dict
        Spotify artist object
    
    Returns
    -------
    Artist 
        Our Artist object
    '''
    artist_id = spotify_object['id']
    artist_name = spotify_object['name']
    genres = ', '.join(spotify_object['genres'])
    followers = spotify_object['followers']['total']
    popularity = spotify_object['popularity']
    external_url = spotify_object['external_urls']['spotify']
    
    artist = Artist(artist_id, artist_name, genres, followers, popularity,\
                 external_url)
    return artist


# Track converters
def convert_spotify_track_object(track_object):
    ''' Object converter
    
    Parameters
    ----------
    Dict
        Spotify track object
    
    Returns
    -------
    Track 
        Internal Track object
    '''
    track_id = track_object['id']
    track_name = track_object['name']
    duration_ms = track_object['duration_ms']
    popularity = track_object['popularity']
    external_url = track_object['external_urls']['spotify']
    
    track = Track(track_id, track_name, duration_ms, popularity, external_url)
    
    for artist_object in track_object['artists']:
        try:
            track.artists.append(get_artist(artist_object['id']))
        except:
            pass
    
    return track


# Playlist converters
def convert_spotify_playlist_object(playlist_object):
    ''' Object converter
    
    Parameters
    ----------
    Dict
        Spotify playlist object
    
    Returns
    -------
    Playlist 
        Internal Playlist object
    '''
    playlist_id = playlist_object['id']
    playlist_name = playlist_object['name']
    owner_name = playlist_object['owner']['id']
    playlist_description = playlist_object['description']
    followers = playlist_object['followers']['total']
    external_url = playlist_object['external_urls']['spotify']
    
    palylist = Playlist(playlist_id, playlist_name, owner_name, \
                        playlist_description, followers, external_url)
                        
    for track_object in playlist_object['tracks']['items']:
        try:
            palylist.tracks.append(get_track(track_object['track']['id']))
        except:
            pass
    
    return palylist
    
# Twitter converters
def convert_twitter_status_object(twitter_status_obj):
    ''' Object converter
    
    Parameters
    ----------
    Dict
        Twitter status object
    
    Returns
    -------
    Twitter 
        Internal Twitter object
    '''
    twitter_id = twitter_status_obj['id_str']
    user_name = twitter_status_obj['user']['name']
    url = twitter_status_obj['user']['url']
    text = twitter_status_obj['text']
    created_at = twitter_status_obj['created_at']
    
    twitter = Twitter(twitter_id, user_name, url, text, created_at)
    
    return twitter



# Get functions
def get_artist(artist_id):
    ''' Get artist.
    
    Parameters
    ----------
    Str
        A spotify URI, URL or ID. We restrict to ID.
    
    Returns
    -------
    Artist
        Internal Artist object
    '''
    result = local_db_accessor.find_artist(artist_id)
    if result is not None:
        print('Cache hit - artist')
        return result
    print('Cache miss - artist')
    artist = convert_spotify_artist_object(spotify.artist(artist_id))
    local_db_accessor.save_artist(artist)
    return artist

def get_track(track_id):
    ''' Get track.
    
    Parameters
    ----------
    Str
        A spotify URI, URL or ID. We restrict to ID.
    
    Returns
    -------
    Track
        Internal Track object
    '''
    result = local_db_accessor.find_track(track_id)
    if result is not None:
        print('Cache hit - track')
        return result
    print('Cache miss - track')
    track = convert_spotify_track_object(spotify.track(track_id))
    local_db_accessor.save_track(track)
    return track

def get_playlist(playlist_id):
    ''' Get related artists to artist_id.
    
    Parameters
    ----------
    Str
        A spotify URI, URL or ID. We restrict to ID.
    
    Returns
    -------
    Artist
        Internal Playlist object
    '''
    result = local_db_accessor.find_playlist(playlist_id)
    if result is not None:
        print('Cache hit - playlist')
        return result
    print('Cache miss - playlist')
    playlist = convert_spotify_playlist_object(spotify.playlist(playlist_id))
    local_db_accessor.save_playlist(playlist)
    return playlist

def get_related_artists(artist_id):
    ''' Get related artists to artist_id.
    
    Parameters
    ----------
    Str
        A spotify URI, URL or ID. We restrict to ID.
    
    Returns
    -------
    List
        A list of internal Artist objects
    '''
    to_artist = get_artist(artist_id)
    result = local_db_accessor.find_related_artists(artist_id)
    if result is not None:
        print('Cache hit - related artists')
        return result
    
    ('Cache miss - related artists')
    artists = []
    spotify_result = spotify.artist_related_artists(artist_id)
    for spotify_artist in spotify_result['artists']:
        artists.append(get_artist(spotify_artist['id']))
    local_db_accessor.save_related_artists(artist_id, artists)
    return artists

def get_featured_playlists():
    ''' Get top 5 featured playlists.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    List
        A list of internal Playlist objects
    '''
    result = local_db_accessor.find_featured_palylists()
    if result is not None:
        print('Cache hit - featured playlists')
        return result
    
    print('Cache miss - featured playlists')
    spotify_palylist_objects = spotify.featured_playlists()['playlists']['items']
    featured_playlists = []
    for i in range(min(5, len(spotify_palylist_objects))):
        featured_playlists\
            .append(get_playlist(spotify_palylist_objects[i]['id']))
    local_db_accessor.save_featured_palylists(featured_playlists)
    return featured_playlists

def get_twitters_by_track(track, limit = 100):
    ''' Get a list of twitter posts by keyword
    
    Parameters
    ----------
    Track
        Internal Track object
        
    int
        A number representing the limit of number of posts
    
    Returns
    -------
    Dict
        A list of internal twitter object
    '''
    result = local_db_accessor.find_twitters_by_track(track)
    if result is not None:
        print('Cache hit - twitters by track')
        return result
    
    print('Cache miss - twitters by track')
    search_params = {'q': track.track_name, 'count': limit}
    response = requests.get(twitter_base_url, params=search_params, \
                            auth=twitter_oauth).json()
    twitters = []
    for status in response['statuses']:
        twitter = convert_twitter_status_object(status)
        twitters.append(twitter)
        local_db_accessor.save_twitter(twitter)
    local_db_accessor.save_twitter_by_track(track, twitters)
    return twitters


# Main
if __name__ == "__main__":
    # Artist
    #print(get_artist('0C8ZW7ezQVs4URX5aX7Kqx'))
    
    # Track
    #print(get_track('3afkJSKX0EAMsJXTZnDXXJ'))
    
    # Playlist
    #print(get_playlist('37i9dQZF1DX1lVhptIYRda'))
    
    # Related Artists
    #print(get_related_artists('0C8ZW7ezQVs4URX5aX7Kqx'))
    
    # Feature playlist
    #print(get_featured_playlists())
    
    # Twitter by track
    #twitters = get_twitters_by_track(get_track('3afkJSKX0EAMsJXTZnDXXJ'))
    #for t in twitters:
    #    print(t)
    
    pass