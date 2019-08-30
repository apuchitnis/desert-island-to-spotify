from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import urllib
import os

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
redirect_uri = os.environ.get('REDIRECT_URI')

username = 'apuschin'

token = util.prompt_for_user_token(username,
                                   'playlist-modify-public',
                                   client_id, client_secret, redirect_uri)

spotify = spotipy.Spotify(auth=token)

page = 'https://www.bbc.co.uk/programmes/p0093v9l'
while page:
    print('----------------------------------')
    print('processing: ' + page)

    html_source = urllib.request.urlopen(page)
    soup = BeautifulSoup(html_source, 'html.parser')

    title = soup.find('div', class_="island").find('h1', class_="no-margin").text
    interviewee = title.split(',', 1)[0]
    print('interviewee: ' + interviewee)

    # find songs
    songs = []  # a tuple of (song, artist)
    for h3 in soup.find_all('h3'):
        # find all span tags inside
        span = h3.find('span', class_='artist')
        if span:
            artist = span.text
            song = h3.parent.contents[3].find('span').text
            songs.append((song, artist))
    print("found " + str(len(songs)) + " songs")
## still broken - autocompleteion, elpy isnt automatic, flycheck doesn't work
    if songs:
        # get spotify_uris from songs
        spotify_uris = []
        for x in range(0, len(songs)):
            query = songs[x][0] + ' '+songs[x][1]
            results = spotify.search(q=query, type='track')
            if results['tracks']['total'] != 0:
                uri = results['tracks']['items'][0]['uri']
                spotify_uris.append(uri)
            else:
                print("could not find track for query " + query)
        print("found " + str(len(spotify_uris)) + " spotify_uris")

        if spotify_uris:
            # create a playlist of the spotify uris
            playlist = spotify.user_playlist_create(username,
                                                    "Desert Island Discs: " + interviewee,
                                                    public=True)

            spotify.user_playlist_add_tracks(username, playlist['id'], spotify_uris)

    page = soup.find_all('h4', class_='programme__titles')[0] \
               .find('a').get('href')
