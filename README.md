# Rhynio Raffle Bot
![image](https://user-images.githubusercontent.com/32105756/125825810-4d11ff00-3613-4929-a36c-5e2c77a41af0.png)

My old code written with a friend for RhynioBot - A Sneaker Raffle Bot

- Automated email forwarding and account registration on various websites using HTTP requests (and the occasional Selenium Webdriver)
- Handled captchas via an external API (Supports 2Captcha, Anticaptcha, and Capmonster)
- Authenticated users via MongoDB IP/Key pairings
- Ported the terminal-based version of the application to a Qt user interface

TL;DR: Software to mass-enter raffles for Sneakers on a bunch of different websites, with unique IPs/Names/Addresses/Emails etc.

https://twitter.com/RhynioBot

https://www.rhyn.io/

Code will not run in its current state as I removed private URIs to my Mongo DB, as well as the endpoints to my Address / Authentication server.
Was a fun project that I worked on during college with a friend and eventually monetized. Helped me learn Python and Requests throughout the year. In addition, utilized the Cloudscraper (Helheim) API which is currently closed-source and unavailable to the public.

The address API server has been turned off as well, but would take in a request and return a real US Address (From a Mongo Database we set up with 9 Million real addresses from https://openaddresses.io/)

The code is sloppy and hasn't been updated in the last 6 months, but uploading regardless.

Thanks for taking a look.

# Screenshots of each page
Main Page

![image](https://user-images.githubusercontent.com/32105756/125826276-afdecb8d-b349-46bf-add6-78aabc371887.png)

Task Setup

![image](https://user-images.githubusercontent.com/32105756/125826307-51c980f0-8f1a-49e0-ae5b-b75c33acecb9.png)

Proxies

![image](https://user-images.githubusercontent.com/32105756/125826322-abdee524-610b-4933-a8a4-257a37c632d2.png)

Email

![image](https://user-images.githubusercontent.com/32105756/125826337-afc3076a-9f15-4611-b4cd-fdf048eb4df0.png)

Settings

![image](https://user-images.githubusercontent.com/32105756/125826353-e148b10c-b9b5-48fc-b1e5-fc0431bf3f6b.png)
