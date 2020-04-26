import React from "react";
import { withStyles } from "@material-ui/core";
import Footer from "./components/Footer";
import { makeStyles } from "@material-ui/core/styles";
import LandingPageHeaderLogoSvg from "./components/LandingPageHeaderLogoSvg";
import LandingPageInformation from "./components/LandingPageInformation";
import AppTitle from "./components/AppTitle";

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

const LandingPage = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <LandingPageInformation />
        <Footer />
      </section>
    </>
  );
};

export default withStyles(useStyles)(LandingPage);
