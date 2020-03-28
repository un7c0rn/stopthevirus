<center><img src="https://github.com/unicorn1337x/stopthevirus/blob/master/banner.png" width=1000></center>

# COVID-19 #STOPTHEVIRUS SOCIAL EXPERIMENT

## Hypothesis:

Can a global scale high stakes social game help inspire millions of Millennial and Gen-Z individuals across the world to engage in social distancing activities and stop the spread of the COVID-19 virus?

## Background:

It’s Spring 2020 and Coachella, SXSW, the NBA, NHL, MLB and the Tokyo Olympics are cancelled this year. We’re at the height of human technology and innovation, but at the same time facing one of the most devastating viral pandemics in history. The economy is suffering, countries around the world are facing mandatory lockdown orders and hospitals are overwhelmed. Despite this, many people are still unaware of the seriousness of COVID-19 and actions they can take to support our health care professionals such as social distancing to <a href="https://www.wired.com/story/the-promising-math-behind-flattening-the-curve/">flatten the health care demand curve</a>. Reducing the doubling rate of COVID-19 by even a few days can have massive impact. Can we use a high stakes social game to help inspire the youth to stop the virus?

This social game was inspired by the TV show Survivor. It's a game based on fun challenges, alliances and human psychology. The twist here is that instead of being stranded on a deserted island for 30 days, players are "stranded" inside their homes. This is important because social distancing, i.e. staying home, is the best tool that the youth have right now for collectively fighting the epidemic. All challenges in this game are designed to incentivize social distancing and spreading awareness. Simple activities like <a href="https://www.youtube.com/watch?v=qFmaSNP6_z4">making home made cotton based masks</a> can help reduce droplet based transmission rates by up to 70% and can be turned into social awareness challenges. Young and healthy people are at risk and can engage in activities that can increase risk for others, so the goal is to create home-based activities that reward risk mitigation.

Also, since the game is digital and based on social media, we aren't limited to the standard 20 players. Everyone can play. With the hope of attracting even more players and convinving them to socially distance, a $1 donation is required to join and the winner takes all.

Here's how the game works:

## Game Flow Chart

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/flowchart.svg" width="1000">

## How To Win

New social distancing challenge ideas can be added continuously by the game admins. Some examples include *Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song.* or *Cleaning Challenge — Post a video showing your most creative way to clean your living space.*

After thirty days a group of two finalists will have made it to the end. All previous players will have the opportunity to vote for who the winner of the prize money should be. Each finalist will be able to make a case on social media using a video post to say why they should be the final survivor and winner of the prize money.

## Architecture Block Diagram

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/blockdiagram.svg" width="1000">

## Requirements

```
pip3 install -r requirements.txt
```

## Unit Tests

Running the unit tests is a good way to get started with development. In general, a technical goal here is to minimize the number of dependencies as much as possible.

To run the unit tests:

```console
python3 -m unittest game_test.py -v
```

To continuously run unit tests in a console window as you code:

Install <a href="http://eradman.com/entrproject/">entr</a>

```console
brew install entr
```

```console
find . -name '*.py' | entr python3 -m unittest game_test.py -v
```

## Design

### Data Model

| Type         | Properties                                                        | Comments                |
| ------------ | ----------------------------------------------------------------- | ------------------------|
| Player       | id, tiktok, email, tribe_id, team_id, active                      |                         |
| Vote         | id, from_id, to_id, is_for_win                                    |                         |
| Team         | id, name, size, tribe_id, active                                  |                         |
| Tribe        | id, name, size, active                                            |                         |
| Challenge    | id, name, message, start/end_timestamp, complete                  | Posted by game admin(s) |
| Entry        | id, likes, views, player_id, team_id, tribe_id, challenge_id, url | i.e. TikTok post        |


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

## Scalability

In order for this game to have impact, it needs to scale. Scalability in this context means several things:

1. The number of people that can join the game and have fun must increase over time as awareness grows. For example, it provides little value if a relatively small number of people play the game with no ability for more to join in.

2. Since the game is virtually free ($1 donation to play), the cost to run the servers must be extremely low.

3. The game must run for long enough for awareness to grow, but be short enough for people to complete. For example we assume that people won't stick around for a 3 month game that requires daily challenges.

To address the scalability requirements we've performed some analysis on game cost with respect to number of players, where cost is represented by both time to game completion and dollar amount to run infrastructure:

There are 4 phases in the game: 

1. **Phase 1:** 2 large tribes compete against eachother and the losing tribe must vote players out.
2. **Phase 2:** The tribes from phase 1 join together and smaller teams compete within the tribe. Losing teams must vote players out.
3. **Phase 3:** The teams from phase 2 join together into 1 team and players compete head to head. Losing players can be voted out.
4. **Phase 4:** The last 2 finalists remaining from phase 3 have a chance to win based on votes from other players in the game.

<img src="http://latex.codecogs.com/svg.latex?\phi%20\%20=\%201\%20-\%20\left(\frac{1}{2s}%20\%20*\%20(%201\%20-\%20\alpha%20)\right" width="1000">




