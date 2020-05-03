import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "../../pages/components/AppTitle";
import Footer from "../../pages/components/Footer";
import StartGamePrompt from "../../pages/components/StartGamePrompt";
import TriangleLogo from "../../pages/components/TriangleLogo";
import LogoContainer from "../../pages/components/LogoContainer";
import {
  StatisticsLeft,
  StatisticsRight,
} from "../../pages/components/GameStatistics";

export default function UiForAppError({ error }) {
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
      <section className={classes.root} data-testid="Game App Error Page">
        <AppTitle />
        <StartGamePrompt />
        <LogoContainer>
          <StatisticsLeft />
          <TriangleLogo />
          <StatisticsRight />
        </LogoContainer>
        <h1>{error.message}</h1>
        <Footer />
      </section>
    </>
  );
}
