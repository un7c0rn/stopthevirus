import CircularProgress from "@material-ui/core/CircularProgress";
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import React, { createContext, lazy, Suspense, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.scss";
import { makeStyles } from "@material-ui/core/styles";

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

  const [gameInfo, setGameInfo] = useState();

  return (
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
              <Route path="/" element={<LandingPage />} />
              <Route path="/start-game/:gameId" element={<StartGamePage />} />
              <Route path="/join-game" element={<JoinGamePage />} />
              <Route path="/game-info/:gameId" element={<GameInfoPage />} />
              <Route
                path="/challenge-submission/:phone/:game"
                element={<SubmitPage />}
              />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </Suspense>
    </AppContext.Provider>
  );
}
export default App;
