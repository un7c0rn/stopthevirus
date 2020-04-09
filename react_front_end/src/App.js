import CircularProgress from "@material-ui/core/CircularProgress";
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import React, { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.scss";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const SubmitPage = lazy(() => import("./pages/SubmitPage"));

const theme = createMuiTheme({
  background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
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
            <Route path="/start-game" element={<h1>START GAME PAGE</h1>} />
            <Route path="/join-game" element={<h1>JOIN GAME PAGE</h1>} />
            <Route path="/game-info" element={<h1>GAME INFO PAGE</h1>} />
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
