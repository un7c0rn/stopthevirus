import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

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
            <Link to="/">Home</Link>
          </li>
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
          <Route exact path="/">
            <Home />
          </Route>
          <Route path="/start">
            <Start />
          </Route>
          <Route path="/join">
            <Join />
          </Route>
          <Route path="/info">
            <Info />
          </Route>
          <Route path="/submit">
            <Submit />
          </Route>
          <Route path="/create">
            <Create />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

// You can think of these components as "pages"
// in your app.

function Home() {
  return (
    <div>
      <h2>Home</h2>
    </div>
  );
}
function Start() {
  return (
    <div>
      <h2>Start Game</h2>
    </div>
  );
}
function Join() {
  return (
    <div>
      <h2>Join Game</h2>
    </div>
  );
}
function Info() {
  return (
    <div>
      <h2>Game Info</h2>
    </div>
  );
}
function Submit() {
  return (
    <div>
      <h2>Challenge Submission</h2>
    </div>
  );
}
function Create() {
  return (
    <div>
      <h2>Crate Challenge</h2>
    </div>
  );
}
