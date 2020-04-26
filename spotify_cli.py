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
import webbrowser
import sys

# Plot
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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



# ------------------------ Connectivity test functions ------------------------
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



# ------------------------ Converters ------------------------
# Artist converter
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



# ------------------------ Get functions ------------------------
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
    
def search_for_artist(keyword):
    ''' Search for artist
    
    Parameters
    ----------
    Str
        An artist name.
    
    Returns
    -------
    List
        A list of internal Artist objects
    '''
    results = spotify.search(q='artist:' + keyword, type='artist')
    items = results['artists']['items']
    
    artists = []
    for item in items:
        artist = get_artist(item['id'])
        artists.append(artist)
    
    return artists

def search_for_track(keyword):
    ''' Search for track
    
    Parameters
    ----------
    Str
        A track name.
    
    Returns
    -------
    List
        A list of internal Track objects
    '''
    results = spotify.search(q='track:' + keyword, type='track')
    items = results['tracks']['items']
    
    tracks = []
    for item in items:
        track = get_track(item['id'])
        tracks.append(track)
    
    return tracks

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



# ------------------------ Testing functions ------------------------
def testing():
    ''' Manual testing
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
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
    
    # Search for artist
    #artists = search_for_artist('Lady Gaga')
    #for artist in artists:
    #    print(artist)
    
    # Search for track
    #tracks = search_for_track('Bad guy')
    #for track in tracks:
   #     print(track)
    
    # Twitter by track
    #twitters = get_twitters_by_track(get_track('3afkJSKX0EAMsJXTZnDXXJ'))
    #for t in twitters:
    #    print(t)

# ------------------------ Plot functions ---------------------
def plot_related_artist_popularity(related_artists):
    ''' Plot for related artist popularity
    
    Parameters
    ----------
    List
        A list of internal artist object
    
    Returns
    -------
    None
    '''
    artist_names = []
    artist_followers = []
    
    for a in related_artists:
        artist_names.append(a.artist_name)
        artist_followers.append(a.followers)

    n = len(artist_names)
    df = pd.DataFrame(dict(artists = artist_names, 
                           followers = artist_followers,
                           category = ["Followers"] * n))

    fig = px.scatter(df, x="followers", y="artists", color="category",
                     title="Number of followers of related artists",
                     labels={"Artist":"Followers"} )

    fig.show()


def plot_related_artist_genres(related_artists):
    ''' Plot for related artist genres
    
    Parameters
    ----------
    List
        A list of internal artist object
    
    Returns
    -------
    None
    '''
    genres = {}
    
    for a in related_artists:
        for genre in a.genres.split(', '):
            genres[genre] = genres.get(genre, 0) + 1

    labels = []
    values = []
    
    for key in genres:
        labels.append(key)
        values.append(genres[key])

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.show()


def plot_track_popularity(tracks):
    ''' Plot for track popularity
    
    Parameters
    ----------
    List
        A list of internal tracks object
    
    Returns
    -------
    None
    '''
    track_names = []
    track_popularity = []
    
    for track in tracks:
        track_names.append(track.track_name)
        track_popularity.append(track.popularity)
    
    fig = go.Figure([go.Bar(x=track_names, y=track_popularity)])
    fig.show()


def plot_singer_percentages(tracks):
    ''' Plot for the number of occurrences of singers in a list of tracks
    
    Parameters
    ----------
    List
        A list of internal tracks object
    
    Returns
    -------
    None
    '''
    singers = {}
    
    for track in tracks:
        for artist in track.artists:
            singer = artist.artist_name
            singers[singer] = singers.get(singer, 0) + 1

    labels = []
    values = []
    
    for key in singers:
        labels.append(key)
        values.append(singers[key])

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.show()

# ------------------------ Command functions ---------------------
def artist_cli(artist):
    ''' Artist command line interface (CLI)
    
    Parameters
    ----------
    Artist
        Internal artist object
    
    Returns
    -------
    None
    '''
    while(True):
        print()
        print(artist)
        
        message = 'Availble commands:' \
            + '\n [1] Go to the spotify artist page on browser' \
            + '\n [2] View popularity chart for related artists of the artist' \
            + '\n [3] View genre chart for percentage of genres among related' \
                   + ' artists' \
            + '\n'
        print(message)
        command = input('Please enter the command index or back or exit: ')
        command = command.strip()

        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        elif command == '1':
            print('Open in browser...')
            webbrowser.open(artist.external_url)
        elif command == '2':
            print('Generating dot plot chart for related artists popularity...')
            artists = get_related_artists(artist.artist_id)
            artists.append(artist)
            plot_related_artist_popularity(artists)
        elif command == '3':
            print('Generating pie chart for related artists genres...')
            artists = get_related_artists(artist.artist_id)
            artists.append(artist)
            plot_related_artist_genres(artists)
        else:
            print('\nWrong command...\n')


def search_artist_cli():
    ''' Search artist command line interface (CLI)
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    while(True):
        command = input('\nPlease enter the artist name or back or exit: ')
        command = command.strip()

        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        
        artists = search_for_artist(command)
        
        while(True):
            print('\nArtists found:\n')
            for i in range(len(artists)):
                print('  [' + str(i+1) + ']: ' + artists[i].artist_name)
            
            command = input('\nPlease enter the index for artist or back or exit: ')

            if command == 'exit':
                sys.exit(0)
            
            if command == 'back':
                break
            
            artist = None
            try:
                index = int(command) - 1
                artist = artists[index]
            except:
                print('\nPlease enter a valid number')
            
            if artist is not None:   
                artist_cli(artist)


def track_cli(track):
    ''' Track command line interface (CLI)
    
    Parameters
    ----------
    Track
        Internal track object
    
    Returns
    -------
    None
    '''
    while(True):
        print()
        print(track)
        
        message = 'Availble commands:' \
            + '\n [1] Go to the spotify track page on browser' \
            + '\n [2] View the artist' \
            + '\n [3] View tweets related to the song' \
            + '\n'
        print(message)
        command = input('Please enter the command index or back or exit: ')
        command = command.strip()
        
        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        elif command == '1':
            print('Open in browser...')
            webbrowser.open(track.external_url)
        elif command == '2':
            while(True):
                for i in range(len(track.artists)):
                    print('  [' + str(i+1) + ']: ' \
                            + track.artists[i].artist_name)
                command = input('\nPlease enter the index for artist or back or exit: ')
                if command == 'exit':
                    sys.exit(0)
                
                if command == 'back':
                    break
                
                artist = None
                try:
                    index = int(command) - 1
                    artist = track.artists[index]
                except:
                    print('\nPlease enter a valid number')
                
                if artist is not None:   
                    artist_cli(artist)
        elif command == '3':
            twitters = get_twitters_by_track(track)
            i = 1
            for twitter in twitters:
                print('[' + str(i) + '] ' + str(twitter))
                i+=1
                print()
        else:
            print('\nWrong command...\n')


def search_track_cli():
    ''' Search track command line interface (CLI)
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    while(True):
        command = input('\nPlease enter the track (song) name or back or exit: ')
        command = command.strip()

        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        
        tracks = search_for_track(command)
        
        while(True):
            print('\nTracks found:\n')
            for i in range(len(tracks)):
                print('  [' + str(i+1) + ']: ' + tracks[i].track_name)
            
            command = input('\nPlease enter the index for track or back or exit: ')

            if command == 'exit':
                sys.exit(0)
            
            if command == 'back':
                break
            
            track = None
            try:
                index = int(command) - 1
                track = tracks[index]
            except:
                print('\nPlease enter a valid number')
            
            if track is not None:
                pass
                track_cli(track)


def playlist_cli(playlist):
    ''' Playlist command line interface (CLI)
    
    Parameters
    ----------
    Playlist
        Internal Playlist object
    
    Returns
    -------
    None
    '''
    while(True):
        print()
        print(playlist)
        
        message = 'Availble commands:' \
            + '\n [1] Go to the playlist page on browser' \
            + '\n [2] Go to a track' \
            + '\n [3] View popularity of each song' \
            + '\n [4] View percentage of singers' \
            + '\n'
        print(message)
        command = input('Please enter the command index or back or exit: ')
        command = command.strip()

        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        elif command == '1':
            print('Open in browser...')
            webbrowser.open(playlist.external_url)
        elif command == '2':
            while(True):
                print(playlist)
                command = input('\nPlease enter the index of track or back or exit: ')

                if command == 'exit':
                    sys.exit(0)
                
                if command == 'back':
                    break
                
                track = None
                try:
                    index = int(command) - 1
                    track = playlist.tracks[index]
                except:
                    print('\nPlease enter a valid number')
                
                if track is not None:
                    pass
                    track_cli(track)
        elif command == '3':
            print('Generating bar chart for track popularity...')
            plot_track_popularity(playlist.tracks)
        elif command == '4':
            print('Generating pie chart for the number of occurrences of ' \
                + 'singers...')
            plot_singer_percentages(playlist.tracks)
        else:
            print('\nWrong command...\n')

def featured_playlist_cli():
    ''' Playlist command line interface (CLI)
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    featured_playlists = get_featured_playlists()
    
    while(True):
        print()
        
        for i in range(len(featured_playlists)):
            print('  [' + str(i+1) + ']: ' \
                    + featured_playlists[i].playlist_name)
        
        command = input('Please enter the playlist index or back or exit: ')
        command = command.strip()

        if command == 'exit':
            sys.exit(0)
        
        if command == 'back':
            break
        
        playlist = None
        try:
            index = int(command) - 1
            playlist = featured_playlists[index]
        except:
            print('\nPlease enter a valid number')
                
        if playlist is not None:
            pass
            playlist_cli(playlist)

def command_line():
    ''' Main command line interface (CLI)
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    while(True):
        message = 'Welcome to Spotify command-line interface (CLI)!' \
            + '\n [1] View today\'s top hits' \
            + '\n [2] View top 5 featured playlists' \
            + '\n [3] Search for a track (song)' \
            + '\n [4] Search for an artist' \
            + '\n'
        print(message)
        
        command = input('Please enter the command index (in number) or exit: ')
        command = command.strip()
        
        if command == '1':
            playlist_cli(get_playlist('37i9dQZF1DXcBWIGoYBM5M'))
        elif command == '2':
            featured_playlist_cli()
        elif command == '3':
            search_track_cli()
        elif command == '4':
            search_artist_cli()
        elif command == 'exit':
            break
        else:
            print('\nWrong command...\n')

# ------------------------ Main function ---------------------
if __name__ == "__main__":
    # Uncomment for testing a specific functionality
    #testing()
    
    # Command line
    command_line()