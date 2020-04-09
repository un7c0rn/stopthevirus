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
      height: "15vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }
  },
  title: {
    margin: 0,
    fontSize: "4em"
  }
}));

export default function AppTitle() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Paper square>
        <Typography
          variant="h1"
          component="h2"
          gutterBottom
          className={classes.title}
        >
          VIR-"US"
        </Typography>
      </Paper>
    </div>
  );
}
