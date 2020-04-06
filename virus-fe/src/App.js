import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import ChallengeSubmissionPage from './components/ChallengeSubmissionPage';
import CreateChallengePage from './components/CreateChallengePage';
import GameInfoPage from './components/GameInfoPage';
import JoinGamePage from './components/JoinGamePage';
import StartGamePage from './components/StartGamePage';


// This site has 3 pages, all of which are rendered
// dynamically in the browser (not server rendered).
//
// Although the page does not ever refresh, notice how
// React Router keeps the URL up to date as you navigate
// through the site. This preserves the browser history,
// making sure things like the back button and bookmarks
// work properly.

export default function BasicExample() {
  return (
    <Router>
      <div>
        <ul>
          <li>
            <Link to="/start">Start Game</Link>
          </li>
          <li>
            <Link to="/join">Join Game</Link>
          </li>
          <li>
            <Link to="/info">Game Info</Link>
          </li>
          <li>
            <Link to="/submit">Challenge Submission</Link>
          </li>
          <li>
            <Link to="/create">Create Challenge</Link>
          </li>
        </ul>

        <hr />

        {/*
          A <Switch> looks through all its children <Route>
          elements and renders the first one whose path
          matches the current URL. Use a <Switch> any time
          you have multiple routes, but you want only one
          of them to render at a time
        */}
        <Switch>
          <Route path="/start">
            <StartGamePage />
          </Route>
          <Route path="/join">
            <JoinGamePage />
          </Route>
          <Route path="/info">
            <GameInfoPage />
          </Route>
          <Route path="/submit">
            <ChallengeSubmissionPage />
          </Route>
          <Route path="/create">
            <CreateChallengePage />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}
