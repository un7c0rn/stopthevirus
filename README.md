# COVID 19 #STOPTHEVIRUS SOCIAL GAME

## Objective:

Design a worldwide high stakes social game to help inspire millions of Millennial and Gen-Z individuals across the planet to engage in social distancing and stop the spread of the COVID-19 virus.

## Background:

* We base the game on [Survivor](https://en.wikipedia.org/wiki/Survivor_(American_TV_series)) rules with modifications to make it work at global scale. 
* Define 2 "tribes" worldwide O(~millions) of members each.
* $1 buy-in to play, single person winner takes all (as an incentivization mechanism)
* Each tribe is divided into small sub-teams of 5 where people can pick their own team
* Daily, tribe 1 is pitted against tribe 2 with an awareness and social distancing challenge
* All participants post social content in order to score points
* Points are aggregated across all tribe members and the tribe with the highest number of points wins for the day
* If your tribe loses the challenge of the day, every sub-team on the tribe (so for example 200,000 sub teams on a tribe of 1M) must vote out 1 member.
* Sub-teams will continue to merge into groups of 5 using the algorithm automatically
* The algorithm will email players with new team assignments and social media info of their group continuously
* After 30 days we’ll have a final group of contestants (possibly 10 or so?) and the entire group of all participants (everyone who donated the $1) will vote on who the winner of the money should be
* Each finalist will be able to make a case on social media using a video post to state why they should be the final survivor and winner of the prize money.
* Social awareness competitions will be user submitted e.g. *Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song, Cleaning Challenge — Post a video showing your most creative way to clean your living space.*

## Game Flow Chart

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/flowchart.svg" width="1000">

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




