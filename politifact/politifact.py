import requests
from bs4 import BeautifulSoup
import pandas as pd
from functools import reduce


def get_image_source(img):
    return img['src'] if img.get('src') else img.get('data-src')


def extract_videos(soup):
    def extract_video_src(video):
        sources = [video['src']]
        sources.extend([source['src'] for source in video.find_all('source', src=True)])
        return sources

    videos = [extract_video_src(video) for video in soup.find_all(['video', 'iframe']) if video.get('src')]
    return reduce(lambda x, y: x + y, videos)


def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Images
    images = soup.find_all('img')
    image_data = [{'src': get_image_source(img), 'alt': img.get('alt', '')} for img in images if get_image_source(img)]

    # Text
    text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div']
    text_data = list(set(tag.text for tag in soup.find_all(text_tags) if tag.text.strip()))

    # Videos
    video_data = extract_videos(soup)

    return image_data, text_data, video_data


def save_to_csv(data, filename, columns=None):
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)


def main():
    url = 'https://www.politifact.com'
    image_data, text_data, video_data = scrape_data(url)

    save_to_csv(image_data, 'images_data.csv', columns=['src', 'alt'])
    save_to_csv(text_data, 'text_data.csv', columns=['text'])
    save_to_csv(video_data, 'videos_data.csv', columns=['video_src'])

    print("Data scraping and saving completed for images, text, and videos.")


if __name__ == "__main__":
    main()
