import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


def extract_images(driver):
    images = []

    for img in driver.find_elements(By.TAG_NAME, 'img'):
        img_url = img.get_attribute('src')
        images.append(img_url)
    return images


def extract_videos(driver):
    videos = []

    # Extract videos from video tags
    for video in driver.find_elements(By.TAG_NAME, 'video'):
        if video.get_attribute('src'):
            videos.append(video.get_attribute('src'))
        for source in video.find_elements(By.TAG_NAME, 'source'):
            if source.get_attribute('src'):
                videos.append(source.get_attribute('src'))

    # Extract videos from iframe tags
    for iframe in driver.find_elements(By.TAG_NAME, 'iframe'):
        if iframe.get_attribute('src'):
            videos.append(iframe.get_attribute('src'))

    return videos


def extract_links(driver):
    links = []

    for link in driver.find_elements(By.TAG_NAME, 'a'):
        link_url = link.get_attribute('href')
        links.append(link_url)

    return links


def extract_texts(driver):
    texts = []

    for tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div']:
        for element in driver.find_elements(By.TAG_NAME, tag):
            texts.append(element.text)

    return texts


def save_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Value'])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def download_images(image_urls, folder):
    try:
        # Create the folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Iterate over each image URL
        for url in image_urls:
            # Extract filename from URL (last part after last '/' character, remove query parameters)
            filename = os.path.join(folder, url.split('/')[-1].split('?')[0])

            # Open a file in binary write mode to save the image
            with open(filename, 'wb') as f:
                # Send a GET request to the image URL
                response = requests.get(url)
                # If the response status code is 200 (OK), write the image content to the file
                if response.status_code == 200:
                    f.write(response.content)
                else:
                    # If the request fails, print an error message with the URL and status code
                    print(f"Failed to download image from {url}. Status code: {response.status_code}")

    # Handle any exceptions that may occur during the download process
    except requests.exceptions.RequestException as e:
        # Print an error message if there's an issue with the request
        print(f"Error downloading images: {e}")

    except FileNotFoundError as e:
        # Print an error message if the specified folder doesn't exist
        print(f"Error: The specified folder '{folder}' does not exist.")


def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # time so content can load
    time.sleep(3)


def scrape_data(url, folder):
    # Set up Chrome WebDriver with headless option
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    # Open the provided URL in the WebDriver
    driver.get(url)

    try:
        # Initialize lists to store extracted data
        links = []
        texts = []
        videos = []
        images = []

        # Scroll down the page 5 times to load additional content
        for _ in range(5):
            scroll_down(driver)

            # Extract links, texts, videos, and images from the webpage
            links += extract_links(driver)
            texts += extract_texts(driver)
            videos += extract_videos(driver)
            images += extract_images(driver)

        return images, videos, links, texts

    finally:
        # Close the WebDriver session
        driver.quit()


def main():
    # Specify the URL and folder
    url = 'https://altnews.in/'
    folder = 'images'

    images, videos, links, texts = scrape_data(url, folder)

    # Save extracted data to CSV files
    save_to_csv(images, 'image_data.csv')
    save_to_csv(videos, 'video_data.csv')
    save_to_csv(links, 'link_data.csv')
    save_to_csv(texts, 'text_data.csv')

    # Download images to the specified folder
    download_images(images, folder)


if __name__ == "__main__":
    main()
