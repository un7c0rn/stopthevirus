# stopthevirus

## COVID 19 #STOPTHEVIRUS HIGH STAKES SOCIAL GAME

## Objective:

Design a global scale high stakes social game to help inspire millions of Millennial and Gen-Z individuals across the planet Earth to stop the spread of the COVID-19 virus.

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
* Each participant will be able to make a case on social media using a video post to state why they should be the final survivor and winner of the prize money.
* Social awareness competitions will be user submitted e.g. Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song, Cleaning Challenge — Post a video showing your most creative way to clean your living space.

## Design:

The game consists of the following system level components:

1. Game engine: AWS Lambda Microservice Python application that runs the scoring, team assignment and voting algorithms
1. Game database: Amazon RDL / MySQL
1. High speed input/output event queues: Amazon SQS 
1. User API using JSON
1. Scraping service: scrapes Instagram webdata for #STOPTHEVIRUS and posts challenge submission scores to input event queue using (4)
1. Notification service: sends out team assignments, challenge announcements, kick notifications and voting ceremony announcements (globally)
1. User device social media channels: used to submit challenges with hashtag and to score points for user tribes.
1. Email / SMS / Web: Used to communicate announcements and administration to users. This is necessary since it is not possible to reliably automate announcements via Instagram. Alternate option: we could use Twitter to post announcements and potentially automate.

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/stopthevirus_architecture1.svg" width="500">

## Detailed Design:

The core of the system is the game engine (1). Input events are ingested asynchronously onto the queue (3.1) and processed by the game engine. There are a finite number of input event types:

1. New player
1. New challenge creation
1. New vote (kick off)
1. New vote (win)
1. New challenge entry submission

And a finite number of output event types:

1. New team assignment
1. New challenge announcement
1. Voted out notification
1. New voting ceremony announcement







