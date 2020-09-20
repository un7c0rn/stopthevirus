Demo

https://vimeo.com/459956989/744ca1febd

# VIR-US Integration Testing

VIR-US offers end-to-end integration testing by simulating an entire game, from matchmaking, through each round of challenges until a winner is announced. The only difference between the integration test and a live real world game is that in a real game, players self-join using the website. In the integration test, we add players directly to the database in code. Simulated games include:

1. Emulated players (default 10). These device emulators send real SMS data to the VIR-US SMS endpoint, and make pseudo-random decisions in the game. More players can be added by extending the list.
2. All live services, e.g. AWS SQS, Firestore, GCP Functions, Twilio are all run live in production. The only thing that is mocked during integration testing are the emulated players. If you have enough real players, you can disable emulation entirely and run a real game.
3. Integration with the frontend. All challenge submission links sent as SMS messages map to the frontend routes.

## Setup

### Interactive Mode

In this mode you (the tester) are a player in the game and will receive text messages with the ability to vote and submit challenge TikTok links. You can also be voted out, in which case you'll no longer receive messages.

1. Modify backend/test_integration.py by adding yourself to the list of real players, e.g.:

```
_REAL_PLAYERS = [
    ('Any Name', 'any_tiktok', '+<my_real_phone_number>'),
]
```

2. Update the Twilio configuration of the local game server to point to the right phone number for the country that your phone is in.

Your phone number must include the country code. The Twilio phone number that the game uses to talk to your number must exist in that country. Right now two countries are supported, US and UK. **IMPORTANT** Update `stv-twilio-service-test.json` with the right service phone number before starting the test:

UK: +447380307401
US: +12568184387
JP: TODO(team) We need a workaround for SMS in Japan

In a live game environment, the right Twilio config will exist on each matchmaker service per region.

### Non-Interactive

In this mode *all* players are emulated. You can watch logs to verify the game asserts to confirm that the test passes. This is preferred for continuous integration. In this case there's no additional setup required.

## Test Steps (applies to both modes)

1. `cd backend`
2. `python3 test_integration.py`
3. The game should complete and the test will assert that a winner is announced. Winners are non-deterministic since emulated players make pseudo random decisions. 
4. Confirm that the process terminates successfully after logging the game events.
5. All game events can be found in backend/game_logs