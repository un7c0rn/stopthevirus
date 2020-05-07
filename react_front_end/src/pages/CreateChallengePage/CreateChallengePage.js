import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "../common/AppTitle";
import Footer from "../common/Footer";
import CreateChallengePrompt from "./CreateChallengePrompt";
import CreateChallengeInputs from "./CreateChallengeInputs";
import TriangleLogo from "../common/TriangleLogo";
import LogoContainer from "../common/LogoContainer";
import { StatisticsLeft, StatisticsRight } from "../common/GameStatistics";
import "./CreateChallengePage.scss";

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
