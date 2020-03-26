# COVID-19 #STOPTHEVIRUS SOCIAL GAME

## Objective:

Design a global scale high stakes social game to help inspire millions of Millennial and Gen-Z individuals across the world to engage in social distancing and stop the spread of the COVID-19 virus.

## Background:

It’s Spring 2020 and Coachella is cancelled. We’re at the height of human technology and innovation, but at the same time facing one of the most devastating viral pandemics in history. The economy is suffering, countries around the world are facing mandatory lockdown orders and hospitals are overwhelmed. Despite this, many people are still unaware of the seriousness of COVID-19 and actions they can take to support our health care professionals, like social distancing in order to flatten the health care demand curve. Reducing the doubling rate of COVID-19 by even a few days can have massive impact. Can we use a high stakes social game to help inspire the youth to stop the virus?

This social game was inspired by the TV show Survivor. It's a social game based on fun challenges, alliances and human psychology. The twist here is that instead of being stranded on a deserted island for 30 days, players are "stranded" inside their homes. Also, since the game is digital and based on social media, we aren't limited to the standard 20 players. Everyone can play. $1 donation to join and winner takes all.

Here's how the game works:

## Game Flow Chart

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/flowchart.svg" width="1000">

## How To Win

New social distancing challenge ideas can be added continuously by the game admins. Some examples include *Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song.* or *Cleaning Challenge — Post a video showing your most creative way to clean your living space.*

After thirty days a group of two finalists will have made it to the end. All players, everyone who donated the $1 entry fee, will vote on who the winner of the prize money should be. Each finalist will be able to make a case on social media using a video post to say why they should be the final survivor and winner of the prize money.

## Architecture Block Diagram

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/blockdiagram.svg" width="1000">

The game consists of the following system level components:

1. Game engine: AWS Lambda Microservice Python application that runs the scoring, team assignment and voting algorithms
1. Game database: Amazon RDL / MySQL
1. High speed input/output event queues: Amazon SQS 
1. User API using JSON
1. Scraping service: scrapes Instagram webdata for #STOPTHEVIRUS and posts challenge submission scores to input event queue using (4)
1. Notification service: sends out team assignments, challenge announcements, kick notifications and voting ceremony announcements (globally)
1. User device social media channels: used to submit challenges with hashtag and to score points for user tribes.
1. Email / SMS / Web: Used to communicate announcements and administration to users. This is necessary since it is not possible to reliably automate announcements via Instagram. Alternate option: we could use Twitter to post announcements and potentially automate.

## Requirements

## Unit Tests

Running the unit tests is a good way to get started and to verify that any dependencies are present. In general, the goal is to minimize the number of dependencies as much as possible.

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

| Type         | Properties                                               | Comments                |
| ------------ | -------------------------------------------------------- | ------------------------|
| Player       | id, instagram, email, tribe_id, team_id, active          |                         |
| Vote         | id, from_id, to_id, is_for_win                           |                         |
| Team         | id, name, size, tribe_id, active                         |                         |
| Tribe        | id, name, size, active                                   |                         |
| Challenge    | id, name, message, start/end_timestamp, complete         | Posted by game admin(s) |
| Entry        | id, likes, views, player_id, tribe_id, challenge_id, url | i.e. Instagram post     |


### Game and Event Model




