// eslint-disable-next-line
import {
  createMuiTheme,
  makeStyles,
  ThemeProvider,
} from "@material-ui/core/styles";
import React, { createContext, lazy, Suspense, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
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
const VerifiedPlayerPage = lazy(() =>
  import("./pages/VerifiedPlayerPage/VerifiedPlayerPage")
);

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

// eslint-disable-next-line
const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    flexWrap: "wrap",
    width: "100vw",
    height: "100vh",
    backgroundColor: "black",
  },
}));

function App() {
  // eslint-disable-next-line
  const classes = useStyles();
  const [gameInfo, setGameInfo] = useState(false);
  const [blurUi, setBlurUi] = useState(false);

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
            blurUi,
            setBlurUi,
          }}
        >
          <Suspense fallback={<Preloader />}>
            <ThemeProvider theme={theme}>
              <BrowserRouter>
                <Routes>
                  <Route path="/start-game" element={<StartGamePage />} />
                  <Route path="/join-game/:gameId" element={<JoinGamePage />} />
                  <Route path="/game-info/:gameId" element={<GameInfoPage />} />
                  <Route
                    path="/challenge-submission/:phone/:game"
                    element={<SubmitPage />}
                  />
                  <Route
                    path="/create-challenge/:phone/:game"
                    element={<CreateChallengePage />}
                  />
                  <Route path="/verified" element={<VerifiedPlayerPage />} />
                  <Route path="/*" element={<LandingPage />} />
                </Routes>
              </BrowserRouter>
            </ThemeProvider>
          </Suspense>
        </AppContext.Provider>
      )}
      renderError={({ error }) => <CustomUiError error={error} type="app" />}
    />
  );
}
export default App;
