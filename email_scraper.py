import streamlit as st

import email
import imaplib
import re
import requests

from bs4 import BeautifulSoup


SOCIALS = ['twitter', 'facebook', 'instagram', 'pinterest']
IGNORE_TERMS = [
    '_logo',
    '-logo',
    'shop now',
    'barcode',
    'click here to track',
    'share us on',
]

TOP_TERMS = ['tee', 'top', 'sweater', 'turtleneck', 'tank']
BOTTOM_TERMS = ['bottom', 'pants', 'joggers', 'pants', 'skirt', 'jeans', 'pant']

CLOTHING_TERMS = TOP_TERMS + BOTTOM_TERMS + [
    'blazer', ' hat', 'bag', 'sneaker', 'dress',
    'headband', 'belt', 'slippers', 'necklace', 'jumpsuit'
]


def extract_item_images(emails):
    item_images = []
    for msg in emails:
        if msg.get_content_type() == 'text/html':  # 'text/plain':
            body = msg.get_payload(decode=True)

            try:
                body = body.decode('utf-8')
            except UnicodeDecodeError:
                continue

            print('Extracting info from html...')
            clothing_image_urls = extract_info_from_html(body)

            if clothing_image_urls:
                item_images += clothing_image_urls
    return item_images


def is_order_receipt(soup):
    # Search the email subject for keywords
    subject = soup.find('subject')
    if subject:
        subject = subject.text
        if (
            'order receipt' in subject.lower()
            or 'confirmation' in subject.lower()
            or 'invoice' in subject.lower()
        ):
            return True

    # Search the email body for keywords
    body = soup.find('body')
    if body:
        body = body.text
        if (
            'order receipt' in body.lower()
            or 'confirmation' in body.lower()
            or 'invoice' in body.lower()
        ):
            return True

    # If no keywords or order/invoice number is found, return False
    return False


def is_irrelevant_image(image_term):
    return any(term in image_term.lower() for term in SOCIALS + IGNORE_TERMS)


def is_relevant_image(image_term):
    return any(term in image_term.lower() for term in CLOTHING_TERMS)


def extract_info_from_html(html):
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    image_urls = []
    if soup:
        # Extract the information that you are interested in
        info = {}
        title = soup.title
        if title:
            info['title'] = soup.title.text
            print('title:', soup.title)

        info['links'] = [a.get('href') for a in soup.find_all('a')]

        # if soup.body:
        #    print(soup.body.prettify)

        # is_receipt = is_order_receipt(soup)

        if True:  # is_receipt:
            # Find all image tags
            images = soup.find_all('img')
            info['images'] = images

            # Iterate over the images
            for image in images:
                if not image:
                    continue

                # st.write(image.get('alt', ''))
                # st.image(image['src'])

                if not is_relevant_image(image.get('alt', '')):
                    continue

                st.write(image.get('alt', ''))
                st.image(image['src'])

                if image['src'] not in image_urls:
                    image_urls.append(image['src'])

                # Download the image
                # response = requests.get(image_url)
                # image_data = response.content

    return image_urls


def extract_all_items_from_emails(subject_term):
    # Set the email address and password of the account you want to scrape
    email_address = 'rismakov@gmail.com'
    password = 'aashgeojxwuzozhl'  # lubas: klykeemdlnmvieku

    # email_address = 'luba.ismakov@gmail.com'
    # password = 'klykeemdlnmvieku'

    # Connect to the email server and login
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(email_address, password)

    # Select the inbox folder and search for receipts
    # email_folder = 'inbox' "order-confirmations"
    server.select('Inbox')

    # status, data = server.search(None, 'SUBJECT "order" OR SUBJECT "receipt"')
    st.header(subject_term)
    print('Searching the email server...')
    _, data = server.search(None, f'SUBJECT "{subject_term}"')
    # _, data = server.search(None, 'ALL')

    print('Fetching the email info...')
    emails = []
    for email_id in data[0].split()[:5000]:
        # Fetch the email with the given ID
        _, data = server.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        # Print the subject
        print('Subject:', msg['Subject'])

        emails.append(msg)

    item_images = extract_item_images(emails)

    # Close the server connection
    server.close()
    server.logout()

    return item_images


def extract_items_from_email():
    for subject in ['receipt']:  # ['order']:
        item_images = extract_all_items_from_emails(subject)
        for item in list(dict.fromkeys(item_images)):
            st.image(item)

    # item_images = extract_all_items_from_emails('receipt')
    # for item in list(dict.fromkeys(item_images)):
    #    st.image(item)
