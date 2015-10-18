#!/usr/bin/python
import os
import sys
import requests

OUTPUT_DIR   = "./files"
CAMPAIGN_IDS = [

]

def get_credentials(creds_file=".patreon_credentials"):
    try:
        with open(creds_file, 'rb') as f:
            patreon_user, patreon_pass = f.read().strip().split(',', 1)
    except (IOError, ValueError) as error:
        sys.stderr.write("Couldn't read credentials from '{0}':\n".format(creds_file))
        sys.stderr.write("\t{0}\n".format(error.message))
        sys.exit(1)
    return patreon_user, patreon_pass

# retrieve list of previously downloaded post IDs
def get_history(hist_file=".saved"):
    saved = set()
    if os.path.isfile(hist_file):
      with open(hist_file, 'rb') as f:
        for x in f:
          saved.add(x.strip())
    return saved

# write saved post IDs to file
def write_history(posts, hist_file=".saved"):
    with open(hist_file, 'wb') as f:
      f.write('\n'.join(posts))

# login to Patreon and return an authenticated Session
def patreon_login(user, pw):
    s = requests.Session()
    headers = { 'Content-Type': 'application/json' }

    resp = s.post('https://api.patreon.com/login',
            data='{"data":{"email":"{0}","password":"{1}"}}'.format(user, pw),
            headers=headers)

    if resp.status_code != 200:
      sys.stderr.write("Error!\n  {0}\n".format(resp.text))
      sys.exit(1)

    return s

def main():
    user, pw = get_credentials()
    saved = get_history()
    s = patreon_login(user, pw)

    # get audio file posts
    for cid in CAMPAIGN_IDS:
        sys.stderr.write("Starting campaign {0}...\n".format(cid))

        url = 'https://api.patreon.com/campaigns/{0}/posts'.format(cid)
        posts = s.get(url).json().get('data')
        audio_posts = [x for x in posts if x.get('post_type') == 'audio_file']

        for post in audio_posts:
            if post['id'] in saved:
                sys.stderr.write("Post {0} already saved. Skipping...\n".format(post['id']))
                continue
            if 'post_file' not in post:
                sys.stderr.write("No audio link in post {0}. Skipping...\n".format(post['id']))
                continue
            fname = post['post_file']['name']
            resp = s.get(post['post_file']['url'], stream=True)
            size = int(resp.headers.get('content-length'))
            prog = 0
            sys.stderr.write("{0}: {1}kb / {2}Mb ({3}%)".format(fname, prog / 1000, size, 100 * prog / size))
            with open('{0}/{1}'.format(OUTPUT_DIR, fname), 'wb') as f:
              for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                  prog += len(chunk)
                  sys.stderr.write("\r{0}: {1}kb / {2:0.2f}Mb ({3}%)".format(
                      fname, prog / 1000, (size / 10000) / 100.00, 100 * prog / size))
                  f.write(chunk)
                  f.flush()
            sys.stderr.write('\n')
            saved.add(post['id'])

        # write history after each campaign to avoid loss
        write_history(saved)

if __name__ == '__main__':
    if not CAMPAIGN_IDS:
        sys.stderr.write("Add campaign ids to the CAMPAIGN_IDS list!\n")
        sys.exit(1)
    main()
