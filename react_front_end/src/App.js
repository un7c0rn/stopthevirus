import CircularProgress from "@material-ui/core/CircularProgress";
import {
  createMuiTheme,
  makeStyles,
  ThemeProvider,
} from "@material-ui/core/styles";
import React, { createContext, lazy, Suspense, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import useErrorBoundary from "use-error-boundary";
import { CustomUiError } from "./utilities/Utilities";
import "./App.scss";

const JoinGamePage = lazy(() => import("./pages/JoinGamePage"));
const LandingPage = lazy(() => import("./pages/LandingPage"));
const SubmitPage = lazy(() => import("./pages/SubmitPage"));
const StartGamePage = lazy(() => import("./pages/StartGamePage"));
const GameInfoPage = lazy(() => import("./pages/GameInfoPage"));

const theme = createMuiTheme({
  background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
});

export const AppContext = createContext();

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "flex-end",
    },
  },
  preloader: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignSelf: "center",
  },
}));

function App() {
  const classes = useStyles();
  const [gameInfo, setGameInfo] = useState(false);

  const {
    ErrorBoundary, // class - The react component to wrap your children in. This WILL NOT CHANGE
    didCatch, // boolean - Whether the ErrorBoundary catched something
    // error, // null or the error
    // errorInfo, // null or the error info as described in the react docs
  } = useErrorBoundary();

  return (
    <ErrorBoundary
      render={() => (
        <AppContext.Provider value={{ gameInfo, setGameInfo }}>
          <Suspense
            fallback={
              <div className={classes.root}>
                <CircularProgress className={classes.preloader} />
              </div>
            }
          >
            <ThemeProvider theme={theme}>
              <BrowserRouter>
                <Routes>
                  <Route
                    path="/start-game/:gameId"
                    element={<StartGamePage />}
                  />
                  <Route path="/join-game" element={<JoinGamePage />} />
                  <Route path="/game-info/:gameId" element={<GameInfoPage />} />
                  <Route
                    path="/challenge-submission/:phone/:game"
                    element={<SubmitPage />}
                  />
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
