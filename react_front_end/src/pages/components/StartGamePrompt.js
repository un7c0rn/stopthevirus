import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "20vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center"
    }
  },
  title: {
    margin: "1em",
    fontSize: "1em"
  }
}));

export default function StartGamePrompt() {
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
          Can a high stakes social media game help inspire millions of Gen-Z and Millennial individuals to engage in social distancing and stop the spread of COVID-19?

        </Typography>
      </Paper>
    </div>
  );
}
