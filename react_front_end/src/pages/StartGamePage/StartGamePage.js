import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "../common/AppTitle";
import Footer from "../common/Footer";
import StartGamePrompt from "./StartGamePrompt";
import StartGameInputs from "./StartGameInputs";
import TriangleLogo from "../common/TriangleLogo";
import LogoContainer from "../common/LogoContainer";
import { StatisticsLeft, StatisticsRight } from "../common/GameStatistics";

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
      marginTop: "4em",
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
