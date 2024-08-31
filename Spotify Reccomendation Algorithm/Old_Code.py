# Code to get the JSON files for each category of music

#save genre tracks to local json
pop_tracks = get_genre_tracks(token2, genres = ['pop'])
with open('../pop.json', 'w') as fp:
    fp.truncate(0)
    json.dump(pop_tracks, fp, indent = 4)

hiphop_tracks = get_genre_tracks(token2, genres = ['hip-hop'])
with open('../hip-hop.json', 'w') as fp:
    fp.truncate(0)
    json.dump(hiphop_tracks, fp, indent = 4)


country_tracks = get_genre_tracks(token2, genres = ['country'])
with open('../country.json', 'w') as fp:
    fp.truncate(0)
    json.dump(country_tracks, fp, indent = 4)

latin_tracks = get_genre_tracks(token2, genres = ['latin'])
with open('../latin.json', 'w') as fp:
    fp.truncate(0)
    json.dump(latin_tracks, fp, indent = 4)

rock_tracks = get_genre_tracks(token2, genres = ['rock'])
with open('../rock.json', 'w') as fp:
    fp.truncate(0)
    json.dump(rock_tracks, fp, indent = 4)

rb_tracks = get_genre_tracks(token2, genres = ['r&b'])
with open('../r&b.json', 'w') as fp:
    fp.truncate(0)
    json.dump(rb_tracks, fp, indent = 4)


# Strong Triadic Closure Mirroring Algorithm
# This code was in the for loop currently used for rec_track and user_track
if rec_track['artist'] == user_track['artist']:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + .5
# point for same genre
if len(set(rec_track['genres']).intersection(user_track['genres'])) > 0:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 0.5
# point for being within one half standard deviation of the playlist song's feature
if abs(user_track['danceability'] - rec_track['danceability']) < 0.14195476860801667 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['energy'] - rec_track['energy']) < 0.16528522215821018 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['key'] - rec_track['key']) < 3.6378427673554006 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['loudness'] - rec_track['loudness']) < 2.554221396196674 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['speechiness'] - rec_track['speechiness']) < 0.09816293136696538 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['acousticness'] - rec_track['acousticness']) < 0.2293866062728317 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['instrumentalness'] - rec_track['instrumentalness']) < 0.07701621363274254 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['liveness'] - rec_track['liveness']) < 0.14201931464260611 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['valence'] - rec_track['valence']) < 0.212884337054903 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['tempo'] - rec_track['tempo']) < 29.464131853206 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1
if abs(user_track['popularity'] - rec_track['popularity']) < 26.17288163984496 / 10:
    strength_dict[rec_track['uri']] = strength_dict[rec_track['uri']] + 1

# code for cosine similaritys

# code to get the magnitude for a feature
def get_magnitude_feature(ut, rt, feature):
    # add each square rooted squared feature
    return math.sqrt(ut[feature] * ut[feature]) + math.sqrt(rt[feature]*rt[feature])
# code to get the dot product for a feature
def get_dot_product_feature(ut, rt, feature):
    # multiply each feature
    return abs(ut[feature]) * abs(rt[feature])