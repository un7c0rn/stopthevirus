import React from "react";
import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import ExperimentInformation from "./ExperimentInfomation";

const useStyles = makeStyles((theme) => ({
  root: {
    // background: theme.background,
    color: "black",
    height: "45vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
}));

const LandingPageInformation = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <ExperimentInformation />
      </section>
    </>
  );
};

export default withStyles(useStyles)(LandingPageInformation);
/*
      Can a global scale high stakes social game help inspire millions of
      Millennial and Gen-Z individuals across the world to engage in
      social distancing?
*/
