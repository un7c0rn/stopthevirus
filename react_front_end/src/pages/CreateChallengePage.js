import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import CreateChallengePrompt from "./components/CreateChallengePrompt";
import CreateChallengeInputs from "./components/CreateChallengeInputs";
import TriangleLogo from "./components/TriangleLogo";
import LogoContainer from "./components/LogoContainer";
import { StatisticsLeft, StatisticsRight } from "./components/GameStatistics";

export default function CreateChallengePage() {
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
      <section className={classes.root} data-testid="Create Challenge Page">
        <AppTitle />
        <LogoContainer>
          <StatisticsLeft />
          <TriangleLogo />
          <StatisticsRight />
        </LogoContainer>
        <CreateChallengePrompt />
        <CreateChallengeInputs />
        <Footer />
      </section>
    </>
  );
}
