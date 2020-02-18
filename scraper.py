import re
from urllib.parse import urlparse
import lxml.html
from bs4 import BeautifulSoup
import sys

import hashlib
import requests


def tokenize(text):
    tokens = set()
    words = re.split('[^a-zA-Z0-9]',text)
    for word in words:
        if word != '':
            tokens.add(word.lower())
    return tokens

def read_robots(url):
    can_fetch = True
    parsed = urlparse(url)
    robot_resp = requests.get('http://' + str(parsed.hostname + '/robots.txt'))
    if robot_resp.status_code == 200:
        resp_list = robot_resp.text.split()
        disallow_indexes = []
        allow_indexes = []
        for i in range(len(resp_list)):
            if resp_list[i] == 'Disallow:':
                disallow_indexes.append(i)
            elif resp_list[i] == 'Allow:':
                allow_indexes.append(i)
        for l in range(len(disallow_indexes)):
            if str(resp_list[disallow_indexes[l]+1]) in url:
                can_fetch = False
        for a in range(len(allow_indexes)):
            if str(resp_list[allow_indexes[a]+1]) in url:
                can_fetch = True

    elif robot_resp.status_code == 404:
        print('Not Found.')
        pass
    return can_fetch

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    links = set()
    try:
        html_content = resp.raw_response.content
        file_size = sys.getsizeof(resp.raw_response.content)
        soup = BeautifulSoup(html_content, "xml")
        for script in soup(["script", "style"]): # referenced from "https://stackoverflow.com/questions/22799990/beatifulsoup4-get-text-still-has-javascript/22800287#22800287"
            script.extract()    # rip it out
        tokens = tokenize(str(soup.get_text()))
        lengthTokens = len(tokens)
        #f = open("urlTokens1.txt", "a+")
        #f.write("URL: " + str(url) + " Tokens:" + str(lengthTokens) + "\n")
        #f.close()
        #f = open("tokens1.txt", "a+")
        #for i in tokens:
        #    f.write(i + "\n")
        #f.close()
        can_fetch = read_robots(url)
        if can_fetch == True and 200 <= int(resp.status) and int(resp.status) <= 299 and int(resp.status) != 204 and file_size > 300 and file_size <= 1000000:
            dom = lxml.html.fromstring(html_content) #referenced from "https://www.mschweighauser.com/fast-url-parsing-with-python/"
            for link in dom.xpath('//a/@href'):
                if "#" in link:
                    link = link.split("#")[0]
                links.add(str(link))
    except:
        pass
    finally:
        return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        flag = False
        if "calendar/day/" in parsed.path and "2020" not in parsed.path:
            return False
        if parsed.hostname == "wics.ics.uci.edu" and "events/" in parsed.path and "2020" not in parsed.path:
            return False
        if ".pdf" in url or ".z" in url or ".ppsx" in url:
            return False
        if "~kay/wordlist.txt" in url:
            return False
        if "replytocom=" in url or "action=login" in url or "action=edit" in url or "share=" in url:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        if ".ics.uci.edu" in str(parsed.hostname):
            #f = open("icsLinks1.txt", "a+")
            #f.write(url + "\n")
            #f.close()
            flag = True
        elif ".cs.uci.edu" in str(parsed.hostname):
            flag = True
        elif ".informatics.uci.edu" in str(parsed.hostname):
            flag = True
        elif ".stat.uci.edu" in str(parsed.hostname):
            flag = True
        elif "today.uci.edu/department/information_computer_sciences" in str(parsed.hostname):
            flag = True
        else:
            flag = False
        return flag and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
