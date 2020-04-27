import React from "react";
import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import ExperimentInformation from "./ExperimentInfomation";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import {Link} from "react-router-dom";
import Button from "@material-ui/core/Button";
import {maxButtonWidth} from "../../utilities/Constants";

const useStyles = makeStyles((theme) => ({
  root: {
    background: theme.background,
    color: "black",
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
        <Paper square style={{maxWidth:maxButtonWidth}}>
          <Typography
            gutterBottom
            className={classes.title}
          >
          It’s Spring 2020 and Coachella, SXSW, the NBA, NHL, MLB and the
          Tokyo Olympics are cancelled this year. We’re at the height of human
          technology and innovation, but at the same time facing one of the
          most devastating viral pandemics in history. The economy is
          suffering, countries around the world are facing mandatory lockdown
          orders and hospitals are overwhelmed. Despite this, many people are
          still unaware of the seriousness of COVID-19 and actions they can
          take to support our health care professionals such as social
          distancing to flatten the health care demand curve. Reducing the
          doubling rate of COVID-19 by even a few days can have massive
          impact. Can we use a high stakes social game to help inspire the
          youth to stop the virus?
          </Typography>
        </Paper>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}

        >
          <Link to='/start-game' style={{ textDecoration: "none" }} >
            <Button style={{backgroundColor:'white',
                  width:'100vw',fontWeight: "bold",
                  maxWidth:maxButtonWidth,
                color:"black"}} >
              GET STARTED
            </Button>
          </Link>
        </Typography>

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
