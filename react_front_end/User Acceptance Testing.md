# Front end user acceptance testing guidance

> “Be a yardstick of quality. Some people aren’t used to an environment where excellence is expected.”— Steve Jobs

The purpose of this documet is to guide the tester though the user journeys facilitated by the front end web application.

## Acceptance Test Procedure

### Initialization

1. Install Netlify CLI https://www.npmjs.com/package/netlify-cli

*The account associated with the CLI install must also contain the site name used in step (5)*

2. git clone https://github.com/un7c0rn/stopthevirus.git
3. ```cd react_front_end```
4. ```yarn```
5. ```netlify link```

When prompted, enter *stopthevirus-develop*

TODO(frontend): Create a single test Netlify account and site-name for all testers.

6. ```yarn build```
7. ```netlify build``` 
8. ```netlify deploy --prod --open --message "STV-FE-ATP" --json --dir="./build"```

*This may take several minutes*

9. Download and install ngrok https://ngrok.com/download
10. ```sudo mv ~/Downloads/ngrok /usr/bin/ngrok```

**The following command will occupy the entire window and should therefore be run in a dedicated terminal:**

11. ```ngrok http 8888```
12. copy the URL from ngrok output https://[identifier].ngrok.io
13. ```export WEBHOOK_CODE_VERIFY=https://[identifier].ngrok.io```

**The following command will occupy the entire window and should therefore be run in a dedicated terminal:**

14. ```pkill netlify```
15. ```netlify dev```
16. Using Chrome with developer tools enabled and visible, navigate to http://localhost:8888
17. Select iPhone X form factor

### Starting a game

1. Click **GET STARTED**.
2. Enter the following field values:

* TIK TOK: who
* PHONE NUMBER: 1-(XXX)-XXX-XXXX *You must enter a valid phone number in order to verify SMS message reception*

* GAME HASHTAG: #ATP

Click **START A GAME**

3. On the phone associated with the number entered in step (2), click the link to verify.
4. On the `http://localhost:8888/verify` page, click the **VERIFY ME** button.
5. Confirm that a success message is displayed.

### Joining a game

1. Navigate to `http://localhost:8888/join-game/0H3RzPqfq4dnf47BSgve` and click **HOW THE GAME WORKS** to find out more about the game you have been invited to.
2. Click your mobile phones web browser back button.
3. Enter the required information on the `http://localhost:8888/join-game/0H3RzPqfq4dnf47BSgve` page.
4. On your phone. Click the link to verify.
5. On the `http://localhost:8888/verify` page, click the **VERIFY ME** button.

### Create a challenge

1. Navigate to `http://localhost:8888/create-challenge/447305841979/0H3RzPqfq4dnf47BSgve` page.
2. Enter the required information on the `http://localhost:8888/create-challenge/447305841979/0H3RzPqfq4dnf47BSgve` page.
3. Click the **CREATE CHALLENGE** button.

### Challenge entry submission

1. Navigate to `http://localhost:8888/challenge-submission/447305841979/0H3RzPqfq4dnf47BSgve/jRGdp3VIzNtmg2gd0dvy`.
2. Enter the required information on the `http://localhost:8888/challenge-submission/447305841979/0H3RzPqfq4dnf47BSgve/jRGdp3VIzNtmg2gd0dvy` page.
3. Click the **SUBMIT** button.

# Game info

1. Navigate to `http://localhost:8888/game-info/0H3RzPqfq4dnf47BSgve`.
2. Review the information on the page.

## Glossary of Terms

- Page: A webpage that forms the visual display of the web application at a given point in the test.
- Slug: part of the web address used to access a webpage or provide information to the web application through the web address.
- Game ID: a piece of information used to identify a game within the web application.
- Phone ID: a piece of information used to identify a persons phone number within the web application.
- Challenge ID: a piece of information used to identify a games challenge within the web application.

### Example Values

The Phone ID should be the mobile phone number of the tester.

- Game ID: 0H3RzPqfq4dnf47BSgve
- Phone ID: XXXXXXXXXXXX
- Challenge ID: 2IADVgFgQ0lryWtxiMEr
- Code: 233ff3da-0765-4d9c-8b56-b0932a88aa2a
