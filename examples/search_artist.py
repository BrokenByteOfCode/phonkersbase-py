from phonkersbase.client import phonkerbase, ArtistLabel

print("Fetching first 10 based artists...")
response_data = phonkerbase.get_artists(label=ArtistLabel.BASE, limit=10)

artists = response_data.get("items", [])
if artists:
    print("Based artists found:")
    for artist in artists:
        print(f"- {artist.get('name')}")