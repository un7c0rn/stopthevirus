Demo

https://vimeo.com/459956989/744ca1febd

# VIR-US Integration Testing

VIR-US offers end-to-end integration testing by simulating an entire game, from matchmaking, through each round of challenges until a winner is announced. The only difference between the integration test and a live real world game is that in a real game, players self-join using the website. In the integration test, we add players directly to the database in code. Simulated games include:

1. Emulated players (default 10). These device emulators make pseudo-random decisions in the game and invoke the same SMS endpoint that live players would. More emualted players can be added by extending the list <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/backend/test_integration.py#L74">here.</a>
2. All live services, e.g. AWS SQS, Firestore, GCP Functions, Twilio are all *live* in production. This is to verify that things are really working. The only thing that is mocked during integration testing are the emulated players (if any). If you have enough real players, you can disable emulation entirely and run a real game.
3. Integration with the frontend. All challenge submission links sent as SMS messages map to the frontend routes, e.g. if you click a link in a received message, it should bring you to the correct page on stopthevirus-alpha.netlify.com and the page should be populated with the right information.

## Setup

### Interactive Mode

In this mode you (the tester) are a player in the game and will receive text messages with the ability to vote and submit challenge TikTok links. You can also be voted out by the emulated players, in which case you'll no longer receive messages.

1. Modify <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/backend/test_integration.py#L87">backend/test_integration.py</a> by adding yourself to the list of real players, e.g.:

```
_REAL_PLAYERS = [
    ('Any Name', 'any_tiktok', '+<my_real_phone_number>'),
]
```

Your phone number must include the country code.

2. Update the test <a href="https://github.com/un7c0rn/stopthevirus/blob/37bd934ae7fbed3c9baac7b0f21ebb01db669ad3/twilio/stv-twilio-service-test.json#L2">Twilio configuration</a> of on your local machine to point to the right phone number for the country that your phone is in.

UK: +447380307401
US: +12568184387
JP: TODO(team) We need a workaround for SMS in Japan

The Twilio phone number that the game uses to talk to your number must exist in the same country. Right now two countries are supported: US and UK.

In a live game environment, the right Twilio config will exist on each matchmaker service machine per region.

### Non-Interactive

No additional setup required. In this mode *all* players are emulated. This makes testing much faster since there's no human in the loop expected to respond to messages. You can watch logs to verify the game asserts and confirm that the test passes. This is preferred for continuous integration.

## Test Steps (applies to both modes)

1. `cd backend`
2. `python3 test_integration.py`
3. The game should complete and the test will assert that a winner is announced. Winners are non-deterministic since emulated players make pseudo random decisions. 
4. Confirm that the process terminates successfully after logging the game events.
5. All game events can be found in backend/game_logs for further analysis.