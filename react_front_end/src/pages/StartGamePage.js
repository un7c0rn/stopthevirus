import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import StartGamePrompt from "./components/StartGamePrompt";
import StartGameInputs from "./components/StartGameInputs";
import TriangleLogo from "./components/TriangleLogo";
import LogoContainer from "./components/LogoContainer";
import { StatisticsLeft, StatisticsRight } from "./components/GameStatistics";

export default function StartGamePage() {
  const useStyles = makeStyles((theme) => ({
    root: {
      background: theme.background,
      color: "white",
      height: "100vh",
      width: "100vw",
      display: "flex",
      flexDirection: "column",
      justifyContent: "flex-start",
    },
  }));

  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <StartGamePrompt />
        <LogoContainer>
          <StatisticsLeft />
          <TriangleLogo />
          <StatisticsRight />
        </LogoContainer>
        <StartGameInputs />
        <Footer />
      </section>
    </>
  );
}
