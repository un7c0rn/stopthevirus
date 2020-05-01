import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import React, { useState, useEffect, useContext } from "react";
import { AppContext } from "../../App";

const useStyles = makeStyles((theme) => ({
  root: {
    color: "white",
    height: "50vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  column: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
  },
  row: {
    display: "flex",
    flexDirection: "row",
  },
  characterLine1: {
    fontSize: "50vw",
  },
  characterLine2: {
    fontSize: "13vw",
    marginTop: "-0.4em",
  },
  characterLine3: {
    fontSize: "8vw",
  },
  characterLine4: {
    fontSize: "13vw",
    marginTop: "0.1em",
    marginBottom: "-0.6em",
  },
}));

const LandingPageHeaderHashTag = () => {
  const classes = useStyles();

  return (
    <header className={classes.root}>
      <h1 className={classes.row}>
        <span className={classes.characterLine1}>#</span>
        <div className={classes.column}>
          <span className={classes.characterLine2}>STOP</span>
          <span className={classes.characterLine3}>THE</span>
          <span className={classes.characterLine4}>VIRUS</span>
        </div>
      </h1>
    </header>
  );
};

export default withStyles(useStyles)(LandingPageHeaderHashTag);
