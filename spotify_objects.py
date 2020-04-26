#########################################
##### Name: Xiao Cheng              #####
##### Uniqname: xchengx             #####
#########################################

import json

# Define Spotify objects
class Artist:
    ''' Our internal Artist ojbect
    '''
    def __init__(self, artist_id, artist_name, genres, followers, popularity,\
                 external_url):
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.genres = genres
        self.followers = followers
        self.popularity = popularity
        self.external_url = external_url
    
    def __str__(self):
        return 'Artist name: ' + str(self.artist_name) \
             + '\nArtist genres: ' + str(self.genres) \
             + '\nArtist followers: ' + str(self.followers) \
             + '\nArtist popularity: ' + str(self.popularity) \
             + '\n'

class Track:
    ''' Our internal Track ojbect
    '''
    def __init__(self, track_id, track_name, duration_ms, popularity,\
                 external_url):
        self.track_id = track_id
        self.track_name = track_name
        self.duration_ms = duration_ms
        self.popularity = popularity
        self.external_url = external_url
        
        # List of internal Artist objects
        self.artists = []
    
    def __str__(self):
        artist_names = ''
        
        for artist in self.artists:
            if len(artist_names) == 0:
                artist_names += artist.artist_name
            else:
                artist_names += ', ' + artist.artist_name
        
        return 'Track name: ' + str(self.track_name) \
             + '\nTrack artists: ' + artist_names \
             + '\nTrack durations (in ms): ' + str(self.duration_ms) \
             + '\nTrack popularity: ' + str(self.popularity)  \
             + '\n'

class Playlist:
    ''' Our internal Playlist ojbect
    '''
    def __init__(self, playlist_id, playlist_name, owner_name, \
                 playlist_description, followers, external_url):
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.owner_name = owner_name
        self.playlist_description = playlist_description
        self.followers = followers
        self.external_url = external_url
        
        # List of internal Track objects
        self.tracks = []
    
    def __str__(self):
        track_names = ''
        
        for i in range(len(self.tracks)):
            track_names += '\n  [' + str(i+1) + ']: ' + self.tracks[i].track_name
        
        return 'Playlist name: ' + str(self.playlist_name) \
             + '\nPlaylist owner: ' + str(self.owner_name) \
             + '\nPlaylist description: ' + str(self.playlist_description) \
             + '\nPlaylist followers: ' + str(self.followers)  \
             + '\nPlaylist tracks: ' + track_names  \
             + '\n'


class Twitter:
    ''' Our internal Twitter ojbect
    '''
    def __init__(self, twitter_id, user_name, url, text, created_at):
        self.twitter_id = twitter_id
        self.user_name = user_name
        self.url = url
        self.text = text
        self.created_at = created_at
    
    def __str__(self):
        return 'Twitter user: ' + str(self.user_name) \
             + '\nTwitter text: ' + str(self.text) \
             + '\n'