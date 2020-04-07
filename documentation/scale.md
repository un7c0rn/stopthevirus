# Scalability

## Game phases

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

## Math

* *p* = the number of total remaining players across all teams and tribes in one game.
* *alpha* = the probability of a team or player having immunity (i.e. they can't be voted off).
* *s* = the average team size (the size the algorithm tries to maintain for teams on average).
* *n* = the number of challenges (each challenge is 1 day) and tribal councils.

**Phase 1 equations**

<img src="http://latex.codecogs.com/svg.latex?%5Cphi%20%5C%20%3D%5C%201%5C%20-%5C%20%5Cleft%28%5Cfrac%7B1%7D%7B2s%7D%20%5C%20%2A%5C%20%28%201%5C%20-%5C%20%5Calpha%20%29%5Cright%29">

<img src="http://latex.codecogs.com/svg.latex?%24%5Cdisplaystyle%20p_%7Bn%7D%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%24">

<img src="http://latex.codecogs.com/svg.latex?n%5C%20%3D%5C%20%5Clog_%7B%5Cphi%20%7D%5Cleft%28%5Cfrac%7Bp_%7Bn%7D%7D%7Bp_%7B0%7D%7D%5Cright%29%24">

**Phase 2 equations**

<img src="http://latex.codecogs.com/svg.latex?%5Cgamma%20%5C%20%3D%5C%201-%5Calpha%20%2C%5C%20%5Czeta%20%5C%20%3D%5C%201-%5Cphi%20">

<img src="http://latex.codecogs.com/svg.latex?%5Cphi%20%5C%20%3D%5C%201-%5Cfrac%7B%5Cgamma%20%7D%7Bs%7D%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%5C%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%20%5C%20%2B%5C%20%5Cgamma%20%5Csum%20%5E%7Bn-1%7D_%7Bk%5C%20%3D%5C%200%7D%20%5Cphi%20%5E%7Bk%7D%20%5C%20%5C%20%28%20sum%5C%20here%5C%20is%5C%20a%5C%20geometric%5C%20series%29%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%5C%20%3D%5C%20p_%7B0%7D%20%5Cphi%20%5E%7Bn%7D%20%2B%5Cfrac%7B%5Cgamma%20-%5Cgamma%20%5Cphi%20%5E%7Bn%7D%20%5C%20%7D%7B%5Czeta%20%7D%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?n%5C%20%3D%5C%20log_%7B%5Cphi%20%7D%5Cleft%28%5Cfrac%7Bp_%7Bn%7D%20-%5Cfrac%7B%5Cgamma%20%7D%7B%5Czeta%20%7D%7D%7Bp_%7B0%7D%20-%5Cfrac%7B%5Cgamma%20%7D%7B%5Czeta%20%7D%7D%5Cright%29%5C%5C">

**Phase 3 equations**

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%3Dp_%7B0%7D%20-n%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?n%3Dp_%7B0%7D%20-n%5C%5C">

**Phase 4 equations**

<img src="http://latex.codecogs.com/svg.latex?p_%7B0%7D%20%3D2%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?p_%7Bn%7D%20%3D1%5C%5C">

<img src="http://latex.codecogs.com/svg.latex?n%3D1">

The time cost of one game is equal to the sum of the number of challenges across all four game phases. The dollar cost of one game is equal to the sum of the number of database reads and writes per challenge across all four game phases. Code to calculate approximage figures using these equations is included in <a href="https://github.com/un7c0rn/stopthevirus/blob/master/cost.py">cost.py</a>.
