import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import { GameName } from "./GameName";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "40vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
    },
  },
  title: {
    margin: "1em 0",
    fontSize: "1em",
  },
}));

export default function ChallengeInfo() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Paper square>
        <GameName />
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          <span style={{ fontWeight: "bold" }}>Challenge</span>: Most Creative
          Homemade Mask
        </Typography>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          <span style={{ fontWeight: "bold" }}>Time to submit</span>: 1 hour 27
          min
        </Typography>
      </Paper>
    </div>
  );
}
