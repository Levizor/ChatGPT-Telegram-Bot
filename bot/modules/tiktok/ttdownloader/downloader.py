import sys

try:
    import requests
    import bs4
except ImportError:
    sys.exit('- module not installed!')


class TiktokDownloader:

    @staticmethod
    def musicaldown(url, output_name):
        try:
            # Create a "Session" object from the "requests" library to make requests to the server.
            ses = requests.Session()
            server_url = 'https://musicaldown.com/'
            # Set request headers, including "User-Agent," "Accept-Language," etc.
            headers = {
                "Host": "musicaldown.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers"
            }
            ses.headers.update(headers)
            # Send a GET request to the server 'https://musicaldown.com/' and get the response as an HTML page.
            req = ses.get(server_url)
            # Use 'BeautifulSoup' to find all 'input' tags on the page and save their values in the 'data' dictionary.
            data = {}
            parse = bs4.BeautifulSoup(req.text, 'html.parser')
            for input_tag in parse.findAll('input'):
                data[input_tag.get("name")] = url if input_tag.get("id") == "link_url" else input_tag.get("value")
            # Send a POST request to the server to download the video using the 'data' dictionary.
            post_url = server_url + "id/download"
            req_post = ses.post(post_url, data=data, allow_redirects=True)
            # Check for possible errors
            mistakes = [302, 'This video is currently not available', 'Video is private or removed!']
            if req_post.status_code == mistakes[0] or (mistakes[1] in req_post.text) or (mistakes[2] in req_post.text):
                # print('- video is private or removed')
                return 'private/remove'
            elif ('Submitted Url is Invalid, Try Again' in req_post.text) or ('err' in req_post.url):
                # print('- URL is invalid')
                return 'url-invalid'
            elif 'photo' in req_post.url:
                return 'not-a-video'
            get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
                'a', attrs={'target': '_blank'})
            # If the download is successful, get the video download link and save the file locally with the name "output_name."
            download_link = get_all_blank[0].get('href')
            get_content = requests.get(download_link)

            with open(output_name, 'wb') as fd:
                fd.write(get_content.content)
            return True
        except IndexError:
            return False
