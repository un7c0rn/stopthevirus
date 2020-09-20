<center><img src="documentation/banner.png" width=1000></center>

![Python application](https://github.com/un7c0rn/stopthevirus/workflows/Python%20application/badge.svg?branch=develop) ![JavaScript tests](https://github.com/un7c0rn/stopthevirus/workflows/JavaScript%20tests/badge.svg?branch=develop)

# COVID-19 #STOPTHEVIRUS SOCIAL EXPERIMENT

Selected as a winner of <a href="https://covidglobalhackathon.com">COVID-19 Global Hackathon</a> from among 18,000 innovators, 175 countries and 1,560 projects.

WATCH PROJECT VIDEO <a href="https://vimeo.com/402226460">HERE</a>

Please reach out if interested in collaborating. <a href="mailto:brandon@formless.la">brandon@formless.la</a>

Official Contributors: Bernard Baker, David Zeifman, DL Warfield, Daniel Francois, Edward Alcide, Brandon Tory

## Hypothesis:

Can a global scale high stakes social game help inspire millions of Millennial and Gen-Z individuals across the world to engage in social distancing activities and stop the spread of the COVID-19 virus?

## Background:

It’s Spring 2020 and Coachella, SXSW, the NBA, NHL, MLB and the Tokyo Olympics are cancelled this year. We’re at the height of human technology and innovation, but at the same time facing one of the most devastating viral pandemics in history. The economy is suffering, countries around the world are facing mandatory lockdown orders and hospitals are overwhelmed. Despite this, many people are still unaware of the seriousness of COVID-19 and actions they can take to support our health care professionals such as social distancing to <a href="https://www.wired.com/story/the-promising-math-behind-flattening-the-curve/">flatten the health care demand curve</a>. Reducing the doubling rate of COVID-19 by even a few days can have massive impact. Can we use a high stakes social game to help inspire the youth to stop the virus?

This social game was inspired by the TV show <a href="https://www.youtube.com/watch?v=5xQ-JQEGOHM">Survivor</a> (Watch before reading more). It's a game based on fun challenges, alliances and human psychology. The twist here is that instead of being stranded on a deserted island for 30 days, players are "stranded" inside their homes. This is important because social distancing, i.e. staying home, is the best tool that the youth have right now for collectively fighting the epidemic. All challenges in this game are designed to incentivize social distancing and spreading awareness. Simple activities like <a href="https://www.youtube.com/watch?v=qFmaSNP6_z4">making home made cotton based masks</a> can help reduce droplet based transmission rates by up to 70% and can be turned into social awareness challenges. Young and healthy people are at risk and can engage in activities that can increase risk for others, so the goal is to create home-based activities that reward risk mitigation.

Also, since the game is digital and based on social media, we aren't limited to the standard 20 players. Everyone can play. With the hope of attracting even more players and convincing them to socially distance, a donation is required to join and the winner takes all.

Here's how the game works:

## Game Flow Chart

<img src="documentation/flowchart.svg" width="1000">

## How to Win

New social distancing challenge ideas can be added continuously by the game admins. Some examples include _Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song._ or _Cleaning Challenge — Post a video showing your most creative way to clean your living space._

After thirty days a group of two finalists will have made it to the end. All previous players will have the opportunity to vote for who the winner of the prize money should be. Each finalist will be able to make a case on social media using a video post to say why they should be the final survivor and winner of the prize money.

## Architecture Block Diagram

<img src="documentation/stopthevirus_20200325-2.svg" width="1000">

# Frontend Development

<a href="./react%20front%20end/README.md">Documentation</a>

# Backend Development

## Requirements

```
pip3 install -r requirements.txt
```

## Unit Tests

Running the unit tests is a good way to get started with development. In general, a technical goal here is to minimize the number of dependencies as much as possible.

To run the unit tests:

```console
cd backend
python3 -m unittest -v
```

To continuously run unit tests in a console window as you code:

Install <a href="http://eradman.com/entrproject/">entr</a>

```console
brew install entr
```

```console
cd backend
find . -name '*.py' | entr python3 -m unittest test_game.py -v
```

## Deploying Cloud Function for SMS

Install the gcloud <a href="https://cloud.google.com/sdk/docs/downloads-interactive">SDK</a>
```
cd stopthevirus/backend/functions/sms
gcloud functions deploy sms_http --runtime python37 --trigger-http --allow-unauthenticated
```

## Integration Testing

### Demo

https://vimeo.com/459956989/744ca1febd

VIR-US offers end-to-end integration testing by simulating an entire game, from matchmaking, through each round of challenges until a winner is announced. The only difference between the integration test and a live real world game is that in a real game, players self-join using the website. In the integration test, we add players directly to the database in code. Simulated games include:

1. Emulated players (default 10). These device emulators make pseudo-random decisions in the game and invoke the same SMS endpoint that live players would. More emulated players can be added by extending the list <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/backend/test_integration.py#L74">here.</a>
2. All live services, e.g. AWS SQS, Firestore, GCP Functions, Twilio are all *live* in production. This is to verify that things are really working. The only thing that is mocked during integration testing are the emulated players (if any). If you have enough real players, you can disable emulation entirely and run a real game.
3. Integration with the frontend. All challenge submission links sent as SMS messages map to the frontend routes, e.g. if you click a link in a received message, it should bring you to the correct page on stopthevirus-alpha.netlify.com and the page should be populated with the right information.

### Setup

#### Interactive Mode

In this mode you (the tester) are a player in the game and will receive text messages with the ability to vote and submit challenge TikTok links. You can also be voted out by the emulated players, in which case you'll no longer receive messages.

1. Modify <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/backend/test_integration.py#L87">backend/test_integration.py</a> by adding yourself to the list of real players, e.g.:

```
_REAL_PLAYERS = [
    ('Any Name', 'any_tiktok', '+<my_real_phone_number>'),
]
```

Your phone number must include the country code.

2. Update the test <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/twilio/stv-twilio-service-test.json#L2">Twilio configuration</a> of on your local machine to point to the right phone number for the country that your phone is in.

* UK: +447380307401
* US: +12568184387
* JP: TODO(team) We need a workaround for SMS in Japan

The Twilio phone number that the game uses to talk to your number must exist in the same country. Right now two countries are supported: US and UK.

In a live game environment, the right Twilio config will exist on each matchmaker service machine per region.

#### Non-Interactive

No additional setup required. In this mode *all* players are emulated. This makes testing much faster since there's no human in the loop expected to respond to messages. You can watch logs to verify the game asserts and confirm that the test passes. This is preferred for continuous integration.

### Test Steps (applies to both modes)

1. `cd backend`
2. `python3 test_integration.py`
3. The game should complete and the test will assert that a winner is announced. Winners are non-deterministic since emulated players make pseudo random decisions. 
4. Confirm that the process terminates successfully after logging the game events.
5. All game events can be found in backend/game_logs for further analysis.

## Design

### Data Model

| Type      | Properties                                                        | Comments                |
| --------- | ----------------------------------------------------------------- | ----------------------- |
| Game      | id, count_players/teams/tribes                                    | Counters for Firestore. |
| Player    | id, tiktok, email, tribe_id, team_id, active                      |                         |
| Vote      | id, from_id, to_id, team_id, is_for_win                           |                         |
| Team      | id, name, tribe_id, active, count_players                         |                         |
| Tribe     | id, name, active, count_players/teams                             |                         |
| Challenge | id, name, message, start/end_timestamp, complete                  | Posted by game admin(s) |
| Entry     | id, likes, views, player_id, team_id, tribe_id, challenge_id, url | i.e. TikTok post        |

### Game and Event Model

The game architecture is comprised of a thin frontend (6) and a simple backend microservice (7) processing realtime events through Firebase (4) at scale. The frontend is intentionally thin and only used to display challenge information, perform signup and for player voting.

When challenges start each day, players submit their entry by simply posting to TikTok using the hashtag **#STOPTHEVIRUS**. The scraper service (2) will automatically search for entries from all participants and submit the relevant metrics (likes, views etc.) to the game database (4). As the game engine (7) processes each challenge and tribal council, events are submitted to a queueing service (8) so that notifications can be processed asynchronously at scale and delivered to players via email (10).

The initial proposed components are enumerated here:

1. TikTok

2. Web scraper service - a simple Python job that can run in a cluster in order to read TikTok post metadata and submit it to the game database (4). Due to API rate limiting the thought here is to use the HTTP endpoint rather than the REST API (TBD). If the API is unworkable players may need to submit challenge entry links using the frontend (6) as a fallback.

3. A Python interface for performing game queries and updates in Firebase for use from the backend (7).

4. A <a href="http://firebase.com/">Firebase Cloud FireStore</a> instance for hosting and processing realtime game data.

5. A JavaScript interface for performing game queries and updates in Firebase for use from the frontend (6).

6. A thin HTML5 / JavaScript (possibly React) app for player registration, voting and informational updates.

7. A Python microservice hosted on <a href="https://firebase.google.com/products/functions">Firebase Functions</a> that runs the core game loop and issues events.

8. A scalable <a href="https://aws.amazon.com/sqs/">AWS SQS</a> queueing service for asynchronously processing game events. This is probably available with Firebase as well, haven't looked into it yet.

9. A simple job that can run in a cluster in order to read events from the queue (8) and perform bulk notifications to users via SMTP (SMS if anyone wants to integrate <a href="https://www.twilio.com/">Twilio</a>).

### Getting Started with Development

All contributions are appreciated here and there's no contribution too small. The typical development flow here is:

1. Clone the repo:

```
git clone https://github.com/un7c0rn/stopthevirus.git
```

2. Create a local development branch:

```
git branch my_dev_branch_name
git switch my_dev_branch_name
```

3. Run the unit tests to make sure things pass before you start:

```console
python3 -m unittest -v
```

4. Check the issues <a href="https://github.com/un7c0rn/stopthevirus/issues">list</a>.

5. If you see some work or on the issues list that matches your experience or is something you'd like to learn more about, comment on the thread and jump in. After writing your code and running the unit tests, create a pull request:

```
git commit -m "my new changes"
```

```
git push
```

Use the <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request">GitHub UI to compare changes and submit a pull request.</a>

6. Leadership is appreciated here. If you have a design idea or improvement in mind just do it and send the pull request. Unit tests are key to working collaboratively since they ensure that changes don't cause new problems. As long as we have passing tests, changes are strongly encouraged. Feel free to submit PR's and add tests after the initial code review.

You may notice that the Firestore database credentials are included here in source control. This means that you can run your code against a real database instance without having to set one up. I think this is important especially for frontend development. The credentials are for a test-only public facing instance, a new prod instance will be deployed before the game goes live.

7. This is a collaborative effort that cannot be completed alone. It's important to have a diverse group of perspectives, ideas and skills to bring this together and create impact. No pull request is too small. Seeking both code and simple graphic asset / design ideas for frontend.

### Scalability

<a href="https://github.com/un7c0rn/stopthevirus/blob/master/documentation/scale.md">Scalability Analysis</a>

