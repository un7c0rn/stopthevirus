import CircularProgress from "@material-ui/core/CircularProgress";
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import React, { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.scss";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const InstructionsPage = lazy(() => import("./pages/InstructionsPage"));
const VotingPage = lazy(() => import("./pages/VotingPage"));
const SubmitPage = lazy(() => import("./pages/SubmitPage"));
const StartGamePage = lazy(() => import("./pages/StartGamePage"));

const theme = createMuiTheme({
  background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)"
});

console.log("MUI Theme");

console.log(theme);

function App() {
  return (
    <Suspense
      fallback={
        <div>
          <CircularProgress />
        </div>
      }
    >
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/instructions" element={<InstructionsPage />} />
            <Route path="/vote" element={<VotingPage />} />
            <Route path="/start-game" element={<StartGamePage />} />
            <Route
              path="/challenge-submission/:phone/:game"
              element={<SubmitPage />}
            />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </Suspense>
  );
}
export default App;
