#########################################
##### Name: Xiao Cheng              #####
##### Uniqname: xchengx             #####
#########################################

import sqlite3
import time

# Our own objects
from spotify_objects import Artist
from spotify_objects import Track
from spotify_objects import Playlist
from spotify_objects import Twitter

class DataAccessor:
    ''' Our internal data accessor
    '''
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
    
    # Spotify artist 
    def save_artist(self, artist):
        ''' Save artist in the DB.
    
        Parameters
        ----------
        Artist
            Internal Artist object
    
        Returns
        -------
        Artist
            Internal Artist object
        '''
        db_cursor = self.conn.cursor()
        db_cursor.execute('INSERT INTO artist values (?,?,?,?,?,?)', \
            [artist.artist_id, artist.artist_name, artist.genres,\
             artist.followers, artist.popularity, artist.external_url])
        self.conn.commit()
        return artist
        
    def find_artist(self, artist_id):
        ''' Get artist in the DB. Return None if there is no record.
    
        Parameters
        ----------
        Str
            Artist id
    
        Returns
        -------
        Artist
            Internal Artist object
        '''
        db_cursor = self.conn.cursor()
        record = db_cursor.execute('SELECT * FROM artist WHERE artist_id = ?',\
            [artist_id]).fetchone()
        if record is None:
            return record
        artist = Artist(record[0], record[1], record[2], record[3], record[4],\
                        record[5])
        return artist
        
    # Spotify track 
    def save_track(self, track):
        ''' Save track in the DB.
    
        Parameters
        ----------
        Track
            Internal Track object
    
        Returns
        -------
        Track
            Internal Track object
        '''
        db_cursor = self.conn.cursor()
        db_cursor.execute('INSERT INTO track values (?,?,?,?,?)', \
            [track.track_id, track.track_name, track.duration_ms,\
             track.popularity, track.external_url])
        self.conn.commit()
        
        for artist in track.artists:
            db_cursor.execute('INSERT INTO track_artist values (?,?)', \
              [track.track_id, artist.artist_id])
            self.conn.commit()
        
        return track
        
    def find_track(self, track_id):
        ''' Get track in the DB. Return None if there is no record.
    
        Parameters
        ----------
        Str
            Track id
    
        Returns
        -------
        Track
            Internal Track object
        '''
        db_cursor = self.conn.cursor()
        record = db_cursor.execute('SELECT * FROM track WHERE track_id = ?',\
            [track_id]).fetchone()
        if record is None:
            return record
        track = Track(record[0], record[1], record[2], record[3], record[4])
        
        artist_db_objects = db_cursor\
            .execute('SELECT * FROM track_artist WHERE track_id = ?',\
            [track_id]).fetchall()
        
        for artist_db_object in artist_db_objects:
            track.artists.append(self.find_artist(artist_db_object[1]))
        
        return track
        
    # Spotify playlist 
    def save_playlist(self, playlist):
        ''' Save playlist in the DB.
    
        Parameters
        ----------
        Playlist
            Internal Playlist object
    
        Returns
        -------
        Playlist
            Internal Playlist object
        '''
        db_cursor = self.conn.cursor()
        db_cursor.execute('INSERT INTO playlist values (?,?,?,?,?,?)', \
            [playlist.playlist_id, playlist.playlist_name, playlist.owner_name,\
             playlist.playlist_description, playlist.followers, \
             playlist.external_url])
        self.conn.commit()
        
        for track in playlist.tracks:
            db_cursor.execute('INSERT INTO playlist_track values (?,?)', \
              [playlist.playlist_id, track.track_id])
            self.conn.commit()
        
        return playlist
        
    def find_playlist(self, playlist_id):
        ''' Get playlist in the DB. Return None if there is no record.
    
        Parameters
        ----------
        Str
            Playlist id
    
        Returns
        -------
        Playlist
            Internal Playlist object
        '''
        db_cursor = self.conn.cursor()
        record = db_cursor\
            .execute('SELECT * FROM playlist WHERE playlist_id = ?',\
            [playlist_id]).fetchone()
        
        if record is None:
            return record
        playlist = Playlist(record[0], record[1], record[2], record[3], \
                            record[4], record[5])
        
        track_db_objects = db_cursor\
            .execute('SELECT * FROM playlist_track WHERE playlist_id = ?',\
            [playlist_id]).fetchall()
        
        for track_db_object in track_db_objects:
            playlist.tracks.append(self.find_track(track_db_object[1]))
        
        return playlist
        
    # Spotify related artist 
    def save_related_artists(self, to_artist_id, artists):
        ''' Save related artists in the DB.
    
        Parameters
        ----------
        Str
            Artist id
        
        List
            A list of artist objects
    
        Returns
        -------
        List
            A list of artist objects
        '''
        db_cursor = self.conn.cursor()
        
        for artist in artists:
            if artist is None:
                pass
            db_cursor.execute('INSERT INTO related_artist values (?,?)', \
              [to_artist_id, artist.artist_id])
            self.conn.commit()
        
        return artists
        
    def find_related_artists(self, to_artist_id):
        ''' Get playlist in the DB. Return None if there is no record.
    
        Parameters
        ----------
        Str
            Playlist id
    
        Returns
        -------
        List
            A list of internal Artist object
        '''
        db_cursor = self.conn.cursor()
        
        ids = db_cursor\
        .execute('SELECT * FROM related_artist WHERE related_to_artist_id = ?',\
            [to_artist_id]).fetchall()
        
        artists = []
        for id in ids:
            artists.append(self.find_artist(id[1]))
            
        if len(artists) == 0:
            return None
        
        return artists
        
    # Spotify featured playlists
    def save_featured_palylists(self, playlists):
        ''' Save featured palylist in the DB.
    
        Parameters
        ----------
        List
            A list of internal playlist objects
    
        Returns
        -------
        List
            A list of internal playlist objects
        '''
        cur_timestamp = int(str(time.time()).replace('.', ''))
        
        db_cursor = self.conn.cursor()
        
        for playlist in playlists:
            if playlist is None:
                pass
            db_cursor.execute('INSERT INTO featured_playlist values (?,?)', \
              [playlist.playlist_id, cur_timestamp])
            self.conn.commit()
        
        return playlists
        
    def find_featured_palylists(self):
        ''' Get playlist in the DB. Return None if there is no record.
    
        Parameters
        ----------
        Str
            Playlist id
    
        Returns
        -------
        List
            A list of internal Artist object
        '''
        db_cursor = self.conn.cursor()
        
        ids = db_cursor.execute('SELECT * FROM featured_playlist').fetchall()
        
        playlists = []
        for id in ids:
            playlists.append(self.find_playlist(id[0]))
            
        if len(playlists) == 0:
            return None
        
        return playlists
        
    # Twitter
    def save_twitter(self, twitter):
        ''' Save featured palylist in the DB.
    
        Parameters
        ----------
        List
            A list of internal Twitter objects
    
        Returns
        -------
        List
            A list of internal Twitter objects
        '''
        db_cursor = self.conn.cursor()
        
        try:
            db_cursor.execute('INSERT INTO twitter values (?,?,?,?,?)',\
                [twitter.twitter_id, twitter.user_name, twitter.url, \
                 twitter.text, twitter.created_at])
            self.conn.commit()
        except:
            pass
        
        return twitter
        
    def find_twitter(self, twitter_id):
        ''' Find Twitter by id
    
        Parameters
        ----------
        Str
            Twitter id
    
        Returns
        -------
        List
            A list of internal Twitter objects
        '''
        db_cursor = self.conn.cursor()
        
        record = db_cursor\
            .execute('SELECT * FROM twitter WHERE twitter_id = ?',\
                     [twitter_id]).fetchone()
        if record is None:
            return record
        twitter = Twitter(record[0], record[1], record[2], record[3], record[4])
        return twitter
        
    def save_twitter_by_track(self, track, twitters):
        ''' Save featured palylist in the DB.
    
        Parameters
        ----------
        Track
            Internal Track object
        
        List
            A list of internal Twitter objects
    
        Returns
        -------
        List
            A list of internal Twitter objects
        '''
        db_cursor = self.conn.cursor()
        
        for twitter in twitters:
            if twitter is None:
                pass
            db_cursor.execute('INSERT INTO track_twitter values (?,?)', \
              [track.track_id, twitter.twitter_id])
            self.conn.commit()
        
        return twitters
        
    def find_twitters_by_track(self, track):
        ''' Save featured palylist in the DB.
    
        Parameters
        ----------
        Track
            Internal Track object
        
        List
            A list of internal Twitter objects
    
        Returns
        -------
        List
            A list of internal Twitter objects
        '''
        db_cursor = self.conn.cursor()
        
        ids = db_cursor\
                .execute('SELECT * FROM track_twitter WHERE track_id = ?',\
                 [track.track_id]).fetchall()
        
        twitters = []
        for id in ids:
            twitters.append(self.find_twitter(id[1]))
            
        if len(twitters) == 0:
            return None
        
        return twitters