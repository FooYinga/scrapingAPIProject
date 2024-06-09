import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyPlaylistCreator:
    def __init__(self, user_id, client_id, client_secret, redirect_uri):
        self.user_id = user_id
        scope = "playlist-modify-public"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret,
                                      redirect_uri=redirect_uri))

    def create_playlist(self, name, description='', visibility='public'):
        playlist = self.sp.user_playlist_create(self.user_id, name,
                                                public=False if visibility.lower() == 'private' else True,
                                                description=description)
        self.playlist_id = playlist['id']
        return self.playlist_id

    def add_tracks_to_playlist(self, track_uris):
        if not self.playlist_id:
            return

        results = self.sp.user_playlist_add_tracks(self.user_id, self.playlist_id, track_uris)
        return results is not None  # returns True if tracks were successfully added

    def get_playlist_uri(self):
        if self.playlist_id:
            return f"spotify:playlist:{self.playlist_id}"
        else:
            return None

