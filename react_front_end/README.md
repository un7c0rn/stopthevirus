# Front end development team guidance

Duplication is far cheaper than the wrong absctraction. - Sandi Metz

Information about where files are and what does what and goes where is listed below.

**Files are in**

1. Pages are in ./src/pages
2. Page components are in ./src/pages/components
3. Utilities are in ./src/utilities
4. Service are in ./src/services

**Routes + Suspense + lazy loading (go here)**

1. Routes should be in the ./src/App.js

**Utilities**

1. Common JS function helpers, e.g. date using moment.js, or a toCurrency function using Intl are in ./src/utilities

---

# Netlify setup

## Create a Netlify account

**Most of this is simply clicking buttons, entering a search term, waiting a few minutes and refreshing the page. Shouldn't be difficult to get sorted.**

1. Set up an account with [Netlify](www.netlify.com).
2. Link your GitHub account.
3. Follow the steps to create a new site.
4. Search for the repo in GitHub.
5. Deploy from GitHub.
6. Purchase a domain name.
7. Set up SSL certificate.

## Install Netlify CLI

1. Install [Netlify CLI](https://www.npmjs.com/package/netlify-cli) globally on your machine.
2. Install the packages in the **react_front_end** folder using the `yarn` command.
3. Inside that folder run `netlify link`.
4. You will be presented with questions. Pick the options in bold.
   ? How do you want to link this folder to a site? **Search by full or partial site name**
   ? Enter the site name (or just part of it): **stopthevirus**

### Deploy from the command line

1. Run `yarn build` from wihin the `react_front_end` folder.
2. Run the following command in the **react_front_end** directory `netlify deploy --prod --open --message "Example message: Testing deployment of different GitHub repository." --json --dir="./build"`.
3. You should see output in the terminal like below. CMD + Click the `deploy_url` in the terminal to view the deployed website.

```
{
  "site_id": "c796e2cd-97db-405f-b404-68b8556e396d",
  "site_name": "stopthevirus",
  "deploy_id": "5e8c39c92937e456beeeb335",
  "deploy_url": "https://5e8c39c92937e456beeeb335--stopthevirus.netlify.com",
  "logs": "https://app.netlify.com/sites/stopthevirus/deploys/5e8c39c92937e456beeeb335",
  "url": "https://stopthevirus.netlify.com"
}
```

# Project setup

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

After cloning the repo, in the base directory run `cd react_front_end/` to move into the React project. After which time you can run the scripts below.

## Available Scripts

In the project directory **react_front_end** , you can run:

### `yarn`

Installs all the packages for the project.

### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### `yarn build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify

---

# Pages / features built

# Landing page

This is the page for route **http://localhost:8888/** used as a visitor landing page.

# Start game page

This is the page for route **http://localhost:8888/start-game/a1b2c3d4e5f6g7h8** used for starting
a new game.

# Join game page

This is the page for route **http://localhost:8888/join-game** used for joining
an existing game.

## Challenge submission page

After running `netlify dev` in the **react_front_end** directory. This url will load the page **http://localhost:8888/challenge-submission/0044703947287/789632**. Please pay attention to the phone number and game ID in the URL. They are extracted on that page. If they are not present. Then do something? TBD.

# Game info page

This is the page for route **http://localhost:8888/game-info/0JnfIU9ke5gWO3TxXTt5** displays information about a game.

---

## TicTok metric parser

All commands should be run in the **react_front_end** directory. Each in separate terminal windows.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke tiktok_video --no-identity --querystring "url=https://www.tiktok.com/@jadethirlwall/video/6813412701310635269"`

## TicTok profile

All commands should be run in the **react_front_end** directory. Each in separate terminal windows.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke tiktok_profile --no-identity --querystring "handle=who"`

---

## Firebase API **batch-update-tribe**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `batch_update_tribe.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke batch_update_tribe --payload '{"game":"7rPwCJaiSkxYgDocGDw4", "from":"77TMV9omdLeW7ORvuheX", "to":"cbTgYdPh97K6rRTDdEPL"}' --no-identity`

## Firebase API **count_votes**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `count_votes.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke count_votes --payload '{"game":"7rPwCJaiSkxYgDocGDw4", "from_tribe":"Q09FeEtoIgjNI57Bnl1E", "is_for_win":"false"}' --no-identity`

## Firebase API **get_game_info**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `get_game_info.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke get_game_info --payload '{"game":"0GiiOrglZoBvfilgulzs"}' --no-identity`

## Firebase API **add_game**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_game.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_game --payload '{"game":"A NEW GAME", "hashtag":"#ANEWGAME"}' --no-identity`

## Firebase API **add_challenge**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_challenge.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_challenge --payload '{"game":"A NEW CHALLENGE", "name":"CHALLENGE NAME", "message":"A CHALLENGE MESSAGE"} ' --no-identity`

## Firebase API **add_challenge**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_submission_entry.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_submission_entry --payload '{"game":"a1b2c3d4e5f6g7h8i9j10", "likes":"1000", "views":"2000", "player_id": "1234567890", "team_id":"Q09FeEtoIgjNI57Bnl1E", "tribe_id":"77TMV9omdLeW7ORvuheX", "challenge_id":"a1b2c3d4e5f6g7h8i9j10", "url":"https://vir-us.io"}' --no-identity`

## Firebase API **add_player**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_player.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_player --payload '{"game":"a1b2c3d4e5f6g7h8i9j10", "tiktok":"@user1234", "email":"user@domain.com", "trib e_id":"77TMV9omdLeW7ORvuheX", "team_id":"Q09FeEtoIgjNI57Bnl1E", "active":"false"}' --no-identity`

## Firebase API **add_vote**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_vote.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. # `yarn test`

3. `yarn && netlify dev`
4. `yarn test`
5. `netlify functions:invoke get_game_info --payload '{"game":"f49f0cfd-c93b-4132-8c5b-ebea4bf81eae"}' --no-identity`

## Firebase API **add_game**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_game.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_game --payload '{"game":"A NEW GAME", "hashtag":"#ANEWGAME"}' --no-identity`

## Firebase API **add_challenge**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_challenge.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_challenge --payload '{"game":"A NEW CHALLENGE", "name":"CHALLENGE NAME", "message":"A CHALLENGE MESSAGE"} ' --no-identity`

## Firebase API **add_challenge**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_submission_entry.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_submission_entry --payload '{"game":"a1b2c3d4e5f6g7h8i9j10", "likes":"1000", "views":"2000", "player_id": "1234567890", "team_id":"Q09FeEtoIgjNI57Bnl1E", "tribe_id":"77TMV9omdLeW7ORvuheX", "challenge_id":"a1b2c3d4e5f6g7h8i9j10", "url":"https://vir-us.io"}' --no-identity`

## Firebase API **add_player**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_player.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_player --payload '{"game":"a1b2c3d4e5f6g7h8i9j10", "tiktok":"@user1234", "email":"user@domain.com", "trib e_id":"77TMV9omdLeW7ORvuheX", "team_id":"Q09FeEtoIgjNI57Bnl1E", "active":"false"}' --no-identity`

## Firebase API **add_vote**

All commands should be run in the **react front end** directory. Each in separate terminal windows.

Please note: It appears that after running the Netlify function once. The function is cached/stored.

And Firebase `initializeApp` doesn't like that and throws an error.

Current work around is run the function. And then to **open the lambda function** `add_vote.js` **and save the file** before running the Netlify `functions:invoke` command again. So that the function is reloaded.

1. `yarn && netlify dev`
2. `yarn test`
3. `netlify functions:invoke add_vote --payload '{"game":"a1b2c3d4e5f6g7h8i9j10", "from_id":"a1b2c3CJaiSkxYgDocGDw4", "to_id":"a1b2c3CJaiS kxYgDocGDw4", "team_id":"Q09FeEtoIgjNI57Bnl1E", "is_for_win":"false"}' --no-identity`
