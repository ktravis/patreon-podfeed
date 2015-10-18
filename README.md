# patreon-podfeed

Because Patreon has yet to provide a private podcast feed for campaign backers,
I wrote a script to progressively scrape them. This was much more complicated
before the Patreon "posts" API was defined, but the script is still useful (to
me). This was primarily written to make it easier to download [The Comedy
Button](https://www.patreon.com/comedybutton) automatically each week, and serve
it to my podcast app of choice.

Add your Patreon email and password separated by a comma to
`.patreon_credentials`, then add the ID of the campaign you'd like download
(e.g., `113261`) to the `CAMPAIGN_IDS` list in `patreon.py`.
The simplest way I've found to get the campaign ID is by clicking a patron post
on the campaign's page, with the "Network" tab of your browser's debug console
open - look for an XHR request to "posts", which will have the ID in the url
(something like "ttps://api.patreon.com/campaigns/113261").

Then run the script with `./patreon.py`. By default, podcasts are downloaded to
the `files/` directory, and the IDs of previously saved posts are written to
`.saved`, these settings can be configured in the script.

In addition I've included a simple Flask application, which serves a directory
of mp3's as podcasts. To do so it generates an atom XML feed based on scraped
ID3 tags, using the [mutagen](https://pypi.python.org/pypi/mutagen) module.

In order to provide the *bare minimum* of security, the atom feed and file
downloads are protected with HTTP Basic Authentication -- set the username and
password to be used in `serve.py`.

To get started:

```shell
pip install Flask mutagen
./serve.py
```

See the routes defined in `serve.py` for more details. I have this application
running behind nginx on a subdomain of my personal website, I then point my
podcast app to the `feed.atom` route and supply the username and password
I defined. Finally, the `patreon.py` script is run every few hours by cron.
