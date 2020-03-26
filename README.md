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
* Each finalist will be able to make a case on social media using a video post to state why they should be the final survivor and winner of the prize money.
* Social awareness competitions will be user submitted e.g. *Karaoke Challenge — Post a video doing your best lyric for lyric rendition of your favorite song, Cleaning Challenge — Post a video showing your most creative way to clean your living space.*

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

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/stopthevirus_architecture1.svg" width="1000">

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

## Event Driven Model

When a **NewPlayer event** is received, the game engine creates an entry in GameDB. If a team is specified for the player, the player is placed on that team. Otherwise, the algorithm finds a team and associates the player with that team in the DB. A new team assignment event is placed on the output queue. NewPlayer events are only valid during the valid entry window. After the entry deadline, all NewPlayer events are ignored. New player events received during tribal council are placed back on the input event queue. New Player events are generated from the REST API. The REST API is called by a JavaScript frontend (8) which validates that the player is not a bot, accepts a $1 donation, and all required player info: preferred team ID (optional), IG account (required), email address (required). The registration client must also verify that the email account belongs to the user before submitting a NewPlayer event.

When a **NewChallengeCreation event** is received, the gamer engine creates an entry in GameDB. The NewChallengeCreation event must contain information that indicates when the challenge starts, when the challenge should be announced, and when the deadline for entry ends. All rules pertaining to the challenge must be included in the description. When NewChallengeCreation events are received and are validated, the game engine creates a NewChallengeAnnouncement and places it on the output queue. The notification service is responsible for dequeuing the output event and making all participants aware of the daily challenge information. In addition, the notification service must post new challenge information to the web front end. New challenges should never be announced until the completion of the tribal council associated with the previous challenge. The notification service must wait for all VotedOutNotifications to be processed before sending a NewChallengeAnnouncement. NewChallengeAnnouncements are sent to all active players.

When a **NewChallengeEntrySubmission event** is received, the game engine identifies the head to head opponent and verifies that both submissions have been received. It also ensures that both entries have been available for at least 1 hour. It scores the entries using the following tentative formula: score = likes / views. This normalizes entries to control for time and popularity. We want to reduce the effects of celebrity status on the ability to win. The metrics such as likes, views, etc. are included in the NewChallengeEntrySubmission event from the scraping service (5). The scraping service is a highly parallelized group of jobs that continuously check for #STOPTHEVIRUS posts. All posts are submitted to the input event queue as challenge entries. Posts by non-participants, or duplicate posts, are ignored by the game engine. The way to enter a challenge is simply to post to Instagram using the hashtag #STOPTHEVIRUS and to be a registered participant. Posts should tag the @stopthevirus IG account to spread awareness of the game and objective. After all entries are scored and the winning tribe is computed, a NewTribalCouncilAnnouncement is placed on the output queue. The notification system uses these events to announce the winning tribe and to let the losing tribe know when the tribal council voting window opens. Tribal council voting windows are open for 4 hours.

**NewVoteOut events** are ignored if the game engine state is not in tribal council state. Tribal council state is controlled by the game clock. The game engine decides when to cut off challenge entries and when to enter tribal council state. Voting Ceremony states are synonymous with tribal challenge winner announcements. In other words, saying “BLUE TRIBE WINS!” is the same as saying “RED TRIBE HAS TRIBAL COUNCIL!”.

**NewVoteWin events** are ignored if the game engine state is not in finalist state. Once the game engine enters the finalist state, all players that have ever played the game are allowed to vote for their favorite finalist. The game engine records NewVoteWin events for each finalist in the gamedb. The final winner announcement will be made manually via Instagram live by inspecting the database logs on the final day of the challenge.

## Game Engine Finite State Machine Diagram

<img src="https://github.com/unicorn1337x/stopthevirus/blob/master/gameflow.svg" width="1000">






