import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import logo from "../../assets/vir-us_triangle_logo_white.jpeg";
import Grid from "@material-ui/core/Grid";
import {isL} from "../../utilities/Utilities";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    backgroundColor:"black",
    width: "100vw",//10 by 9 aspect ratio

    "& > *": {
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    },
  },
  title: {
    margin: 0,
    fontSize: "4em"
  },
  text: {
    margin:"0em 2em",
    fontSize:"1em",
    fontFamily: "Helvetica Neue",
    fontWeight:"bold",
  },
  unit: {
    margin:"0 2em",
    fontSize:"0.7em",
    fontFamily: "Helvetica Neue"
  }
}));

export default function TriangleLogo() {
  const classes = useStyles();
  const large = isL();
  const dd=78, hh="06", mm=26, ss=47;

  return (
    <div className={classes.root}
    >
    <img src={logo} style={{width:large? "30vw": "40vh",
    height: large? "30vw": "40vh", margin:"0 auto"}}/>

    <Grid container justify="center">
      <Grid item>
        <span className={classes.text}>
          {dd} <br/>
        </span>
        <span className={classes.unit}>
           DAYS
        </span>

      </Grid>
      <Grid item>
        <span className={classes.text}>
          {hh} <br/>
        </span>
        <span className={classes.unit}>
           HOURS
        </span>
      </Grid>
      <Grid item>
        <span className={classes.text}>
          {mm} <br/>
        </span>
        <span className={classes.unit}>
           MINUTES
        </span>
      </Grid>
      <Grid item>
        <span className={classes.text}>
          {ss} <br/>
        </span>
        <span className={classes.unit}>
           SECONDS
        </span>
      </Grid>
    </Grid>
    </div>
  );
}
