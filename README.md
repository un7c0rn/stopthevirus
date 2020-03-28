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

In order for this game to have impact it needs to scale. Scalability in this context means several things:

1. The number of people that can join the game must increase over time as awareness grows. It provides little value if a relatively small number of people complete the game with no ability for more to join.

2. Since the game is virtually free the cost to run the servers must be low.

3. The game must run for long enough for awareness to grow but be short enough for people to complete it. We assume that people won't stick around for a 3 month game that requires daily social isolation challenges.

To address the scalability constraints we've performed some analysis on game cost with respect to number of players, where cost is represented by both time to game completion and dollar amount to run infrastructure:

Typically in Survivor there are three game phases. Since this game is designed for a much larger number of players, one additional phase (phase two below) where teams within a tribe compete has been added:

1. **Phase 1:** 2 large tribes compete against eachother and the losing tribe must vote players out.
2. **Phase 2:** The tribes from phase 1 join together and smaller teams compete within the tribe. Losing teams must vote players out.
3. **Phase 3:** The teams from phase 2 join together into 1 team and players compete head to head. Losing players can be voted out.
4. **Phase 4:** The last 2 finalists remaining from phase 3 have a chance to win based on votes from other players in the game.

Equations are included below for reference but the TL;DR here is that one monolithic million player game would cost about $10,000 in server fees and take 60-75 days to get down to one winner since each challenge takes 1 day. The cost could be covered by entry donations but the time seems way too long. It would also be extremely hard to get the game started since no one could start playing until millions of people had joined. For these reasons, in order to maximize impact the game will be *sharded*. Many games can be played in parallel, all with varying sizes. Players that want to try the game and engage in distancing activities can be placed into game settings that optimize for time (smaller number of players) and players that want to compete with lots of people can be placed into games that optimize for size i.e. waiting for the most participants. When a player is voted out they can join a new game which hopefully keeps the social distancing activities going for an even longer amount of time and increases fun, awareness and social impact for all.

* *p* = the number of total remaining players across all teams and tribes in one game.
* *alpha* = the probability of a team or player having immunity (i.e. they can't be voted off).
* *s* = the average team size (the size the algorithm tries to maintain for teams on average).
* *n* = the number of challenges (each challenge is 1 day) and tribal councils.

**Phase 1 equations**

<img src="http://latex.codecogs.com/svg.latex?\phi%20\%20=\%201\%20-\%20\left(\frac{1}{2s}%20\%20*\%20(%201\%20-\%20\alpha%20)\right)" height=70>

<img src="http://latex.codecogs.com/svg.latex?%24%5Cdisplaystyle%20p_%7Bn%7D%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%24" height=70>

<img src="http://latex.codecogs.com/svg.latex?n%5C%20%3D%5C%20%5Clog_%7B%5Cphi%20%7D%5Cleft%28%5Cfrac%7Bp_%7Bn%7D%7D%7Bp_%7B0%7D%7D%5Cright%29%24" height=70>

**Phase 2 equations**

<img src="http://latex.codecogs.com/svg.latex?%5Cgamma%20%5C%20%3D%5C%201-%5Calpha%20%2C%5C%20%5Czeta%20%5C%20%3D%5C%201-%5Cbeta%20%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?%5Cphi%20%5C%20%3D%5C%201-%5Cfrac%7B%5Cgamma%20%7D%7Bs%7D%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%5C%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%20%5C%20%2B%5C%20%5Cgamma%20%5Csum%20%5E%7Bn-1%7D_%7Bk%5C%20%3D%5C%200%7D%20%5Cphi%20%5E%7Bk%7D%20%5C%20%5C%20%28%20sum%5C%20here%5C%20is%5C%20a%5C%20geometric%5C%20series%29%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%5C%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%20%2B%5Cfrac%7B%5Cgamma%20-%5Cgamma%20%5Cphi%20%5E%7Bn%7D%20%5C%20%7D%7B%5Czeta%20%7D%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?n%5C%20%3D%5C%20log_%7B%5Cphi%20%7D%5Cleft%28%5Cfrac%7Bp_%7Bn%7D%20-%5Cfrac%7B%5Cgamma%20%7D%7B%5Czeta%20%7D%7D%7Bp_%7B0%7D%20-%5Cfrac%7B%5Cgamma%20%7D%7B%5Czeta%20%7D%7D%5Cright%29%5C%5C" height=70>

**Phase 3 equations**

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%3Dp_%7B0%7D%20-n%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?n%3Dp_%7B0%7D%20-n%5C%5C" height=70>

**Phase 4 equations**

<img src="http://latex.codecogs.com/svg.latex?p_%7B0%7D%20%3D2%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%3D1%5C%5C" height=70>

<img src="http://latex.codecogs.com/svg.latex?n%3D1" height=70>

The time cost of one game is equal to the sum of the number of challenges across all four game phases. The dollar cost of one game is equal to the sum of the number of database reads and writes per challenge across all four game phases. Code to calculate approximage figures using these equations is included in <a href="https://github.com/un7c0rn/stopthevirus/blob/master/cost.py">cost.py</a>.
