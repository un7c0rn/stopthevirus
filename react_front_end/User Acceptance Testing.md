# Front end user acceptance testing guidance

> “Be a yardstick of quality. Some people aren’t used to an environment where excellence is expected.”— Steve Jobs

The purpose of this documet is to guide the tester though the user journeys facilitated by the front end web application. The follow terms and values of IDs are defined as follows.

**List of terms**

- Page: A webpage that forms the visual display of the web application at a given point in the test.
- Slug: part of the web address used to access a webpage or provide information to the web application through the web address.
- Game ID: a piece of information used to identify a game within the web application.
- Phone ID: a piece of information used to identify a persons phone number within the web application.
- Challenge ID: a piece of information used to identify a games challenge within the web application.

**List of example values**

The Phone ID should be the mobile phone number of the tester.

- Game ID: 0H3RzPqfq4dnf47BSgve
- Phone ID: XXXXXXXXXXXX
- Challenge ID: 2IADVgFgQ0lryWtxiMEr
- Code: 233ff3da-0765-4d9c-8b56-b0932a88aa2a

**Please note**

This assumes that you have followed the instruction on how to start the project within a local development environment and it is running at `http://localhost:8888`.

`ngrok http 8888` was run before hand. And you have updated your `.env` file endpoints with the HTTPS URLS provided by NGROK. I also recommend having the debugger open to take note of the success messages. Not all ends to the user journeys have been defined. If we'd like to show an advert, or a promotion, or something like that.

# Starting a game

1. Navigate to `http://localhost:8888/` and click **GET STARTED**.
2. Enter the required information on the `http://localhost:8888/start-game` page. The hashtag requires a "#" prefix.
3. On your phone. Click the link to verify.
4. On the `http://localhost:8888/verify` page, click the **VERIFY ME** button.

# Joining a game

1. Navigate to `http://localhost:8888/join-game/0H3RzPqfq4dnf47BSgve` and click **HOW THE GAME WORKS** to find out more about the game you have been invited to.
2. Click your mobile phones web browser back button.
3. Enter the required information on the `http://localhost:8888/join-game/0H3RzPqfq4dnf47BSgve` page.
4. On your phone. Click the link to verify.
5. On the `http://localhost:8888/verify` page, click the **VERIFY ME** button.

# Create a challenge

1. Navigate to `http://localhost:8888/create-challenge/447305841979/0H3RzPqfq4dnf47BSgve` page.
2. Enter the required information on the `http://localhost:8888/create-challenge/447305841979/0H3RzPqfq4dnf47BSgve` page.
3. Click the **CREATE CHALLENGE** button.

# Challenge entry submission

1. Navigate to `http://localhost:8888/challenge-submission/447305841979/0H3RzPqfq4dnf47BSgve/jRGdp3VIzNtmg2gd0dvy`.
2. Enter the required information on the `http://localhost:8888/challenge-submission/447305841979/0H3RzPqfq4dnf47BSgve/jRGdp3VIzNtmg2gd0dvy` page.
3. Click the **SUBMIT** button.

# Game info

1. Navigate to `http://localhost:8888/game-info/0H3RzPqfq4dnf47BSgve`.
2. Review the information on the page.

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

Before you begin. You'll need to install [**ngrok**](https://ngrok.com/download). This working in conjunction with `netlify dev` which should be run on port **8888**.

1. Install ngrok
2. Fire it up in your terminal using the following command `ngrok http 8888`. Navigate to the **https** URL. You should see an error stating `the client failed to establish a connection to the local address localhost:8888`. That is good.
3. Update your .env file and set the value of WEBHOOK_CODE_VERIFY to the **ngrok** URL **without** the trailing slash. The **ngrok tunnel** expires after a period of time so be mindful.

Follow the steps below to set up the development server and refresh the window with the **ngrok** URL.

---

In the project directory **react_front_end** , you can run:

### `yarn`

Installs all the packages for the project.

### `netlify dev`

Runs the app in the development mode **with** Netlify environment variables and lambda functions.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.
