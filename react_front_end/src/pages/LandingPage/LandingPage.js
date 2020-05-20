import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import ReactPlayer from "react-player";
import AppTitle from "../common/AppTitle";
import Footer from "../common/Footer";
import { StatisticsLeft, StatisticsRight } from "../common/GameStatistics";
import LogoContainer from "../common/LogoContainer";
import LandingPageInformation from "./LandingPageInformation";

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

const LandingPage = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <ReactPlayer
            url="/video/stopthevirus.mp4"
            playing
            light
            width="100%"
          />
        </div>
        <LogoContainer>
          <StatisticsLeft layout="row" />
          <StatisticsRight layout="row" />
        </LogoContainer>
        <LandingPageInformation />
        <Footer />
      </section>
    </>
  );
};

export default withStyles(useStyles)(LandingPage);
