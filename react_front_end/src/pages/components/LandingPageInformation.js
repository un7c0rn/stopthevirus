import React from "react";
import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import ExperimentInformation from "./ExperimentInfomation";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import {Link} from "react-router-dom";
import Button from "@material-ui/core/Button";

const useStyles = makeStyles((theme) => ({
  root: {
    background: theme.background,
    color: "black",
    height: "80vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    margin: "1em",
    fontSize: "1em",
    textAlign: "center",
  }

}));

const LandingPageInformation = () => {
  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <Paper square style={{maxWidth:"850px"}}>
          <Typography
            gutterBottom
            className={classes.title}
          >
          Can a global scale high stakes social game help inspire millions of
          Millennial and Gen-Z individuals across the world to engage in
          social distancing?
          Can a global scale high stakes social game help inspire millions of
          Millennial and Gen-Z individuals across the world to engage in
          social distancing?
          Can a global scale high stakes social game help inspire millions of
          Millennial and Gen-Z individuals across the world to engage in
          social distancing?

          </Typography>
          <Typography
            variant="h3"
            component="h4"
            gutterBottom
            className={classes.title}

          >
            <Link to='/start-game' style={{ textDecoration: "none" }} >
              <Button style={{fontWeight: "bold"}} >
                GET STARTED
              </Button>
            </Link>
          </Typography>
        </Paper>
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
