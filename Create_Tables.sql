CREATE TABLE artist (
    artist_id varchar(255) NOT NULL PRIMARY KEY,
    artist_name varchar(255),
    genres varchar(255),
    followers int,
    popularity int,
    external_url varchar(255)
);

CREATE TABLE track (
    track_id varchar(255) NOT NULL PRIMARY KEY,
    track_name varchar(255),
    duration_ms int,
    popularity int,
    external_url varchar(255)
);

CREATE TABLE track_artist (
    track_id varchar(255) NOT NULL,
    artist_id varchar(255) NOT NULL,
    FOREIGN KEY (track_id) REFERENCES Track(track_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id),
    PRIMARY KEY(track_id, artist_id)
);

CREATE TABLE related_artist (
    related_to_artist_id varchar(255) NOT NULL,
    artist_id varchar(255) NOT NULL,
    FOREIGN KEY (related_to_artist_id) REFERENCES Artist(artist_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id),
    PRIMARY KEY(related_to_artist_id, artist_id)
);

CREATE TABLE playlist (
    playlist_id varchar(255) NOT NULL PRIMARY KEY,
    playlist_name varchar(255),
    owner_name varchar(255),
    playlist_description varchar(255),
    followers int,
    external_url varchar(255)
);

CREATE TABLE featured_playlist (
    playlist_id varchar(255) NOT NULL PRIMARY KEY,
    updated_on int NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id)
);

CREATE TABLE playlist_track (
    playlist_id varchar(255) NOT NULL,
    track_id varchar(255) NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id),
    FOREIGN KEY (track_id) REFERENCES Track(track_id),
    PRIMARY KEY(playlist_id, track_id)
);

CREATE TABLE twitter (
    twitter_id varchar(255) NOT NULL PRIMARY KEY,
    user_name varchar(255),
    url varchar(255),
    text varchar(255),
    created_at varchar(255)
);

CREATE TABLE track_twitter (
    track_id varchar(255) NOT NULL,
    twitter_id varchar(255) NOT NULL,
    FOREIGN KEY (track_id) REFERENCES Track(track_id),
    FOREIGN KEY (twitter_id) REFERENCES Twitter(twitter_id),
    PRIMARY KEY(track_id, twitter_id)
);