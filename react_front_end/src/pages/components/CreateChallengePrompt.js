import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "20vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
    },
  },
  title: {
    margin: "1em",
    fontSize: "100%",
    textAlign: "center",
    width: "40vw",
    [theme.breakpoints.down("md")]: {
      width: "60vw",
    },
    [theme.breakpoints.down("sm")]: {
      width: "90vw",
    },
  },
}));

export default function CreateChallengePrompt() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Paper square>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          Challenges are scored using Tik Tok video likes divided by the number
          of views. Challenges are reviewed and may be removed without notice.
        </Typography>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          Good challange ideas are fun, encouraging social distancing and are
          easy to score by liking on Tik Tok.
        </Typography>
      </Paper>
    </div>
  );
}
