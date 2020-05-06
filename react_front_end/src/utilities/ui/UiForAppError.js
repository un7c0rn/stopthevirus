import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "../../pages/common/AppTitle";
import Footer from "../../pages/common/Footer";
import StartGamePrompt from "../../pages/StartGamePage/StartGamePrompt";
import TriangleLogo from "../../pages/common/TriangleLogo";
import LogoContainer from "../../pages/common/LogoContainer";
import {
  StatisticsLeft,
  StatisticsRight,
} from "../../pages/common/GameStatistics";

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
