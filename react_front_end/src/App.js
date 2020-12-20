// eslint-disable-next-line
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import React, { createContext, lazy, Suspense, useState } from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import useErrorBoundary from "use-error-boundary";
import "./App.scss";
import Preloader from "./pages/common/Preloader";
import { CustomUiError } from "./utilities/Utilities";

const JoinGamePage = lazy(() => import("./pages/JoinGamePage/JoinGamePage"));
const LandingPage = lazy(() => import("./pages/LandingPage/LandingPage"));
const SubmitPage = lazy(() => import("./pages/SubmitPage/SubmitPage"));
const StartGamePage = lazy(() => import("./pages/StartGamePage/StartGamePage"));
const GameInfoPage = lazy(() => import("./pages/GameInfoPage/GameInfoPage"));
const CreateChallengePage = lazy(() =>
  import("./pages/CreateChallengePage/CreateChallengePage")
);
const VerifyPlayerPage = lazy(() =>
  import("./pages/VerifiedPlayerPage/VerifyPlayerPage")
);
const VerifiedPlayerPage = lazy(() =>
  import("./pages/VerifiedPlayerPage/VerifiedPlayerPage")
);
const AdvertPage = lazy(() => import("./pages/AdvertPage/AdvertPage"));

const theme = createMuiTheme({
  background: "black",
  palette: {
    type: "dark",
    background: "black",
  },
  typography: {
    fontFamily: ["Helvetica Neue"].join(","),
  },
});

export const AppContext = createContext();

const App = () => {
  // eslint-disable-next-line
  const [gameInfo, setGameInfo] = useState(false);

  const {
    ErrorBoundary, // class - The react component to wrap your children in. This WILL NOT CHANGE
    // eslint-disable-next-line
    didCatch, // boolean - Whether the ErrorBoundary catched something
    // error, // null or the error
    // errorInfo, // null or the error info as described in the react docs
  } = useErrorBoundary();

  return (
    <ErrorBoundary
      render={() => (
        <AppContext.Provider
          value={{
            gameInfo,
            setGameInfo,
          }}
        >
          <Suspense fallback={<Preloader />}>
            <ThemeProvider theme={theme}>
              <Router>
                <Switch>
                  <Route path="/start-game">
                    <StartGamePage />
                  </Route>
                  <Route path="/join-game/:gameId">
                    <JoinGamePage />
                  </Route>
                  <Route path="/game-info/:gameId">
                    <GameInfoPage />
                  </Route>
                  <Route path="/challenge-submission/:phone/:game/:challenge">
                    <SubmitPage />
                  </Route>
                  <Route path="/create-challenge/:phone/:game">
                    <CreateChallengePage />
                  </Route>
                  <Route path="/verify/:phone/:code/:game">
                    <VerifyPlayerPage />
                  </Route>
                  <Route path="/verified">
                    <VerifiedPlayerPage />
                  </Route>
                  <Route path="/advert">
                    <AdvertPage />
                  </Route>
                  <Route path="/*">
                    <LandingPage />
                  </Route>
                </Switch>
              </Router>
            </ThemeProvider>
          </Suspense>
        </AppContext.Provider>
      )}
      renderError={({ error }) => <CustomUiError error={error} type="app" />}
    />
  );
};
export default App;
