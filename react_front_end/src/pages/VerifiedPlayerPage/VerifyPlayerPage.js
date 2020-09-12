import React from "react";
import { withStyles } from "@material-ui/core";
import Footer from "../common/Footer";
import { makeStyles } from "@material-ui/core/styles";
import VerifyPlayerPageInputs from "./VerifyPlayerPageInputs";
import AppTitle from "../common/AppTitle";
import LogoContainer from "../common/LogoContainer";
import { StatisticsLeft, StatisticsRight } from "../common/GameStatistics";
import TriangleLogo from "../common/TriangleLogo";

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

const VerifyPlayerPage = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <LogoContainer>
          <StatisticsLeft />
          <TriangleLogo />
          <StatisticsRight />
        </LogoContainer>
        <VerifyPlayerPageInputs />
        <Footer />
      </section>
    </>
  );
};

export default withStyles(useStyles)(VerifyPlayerPage);
