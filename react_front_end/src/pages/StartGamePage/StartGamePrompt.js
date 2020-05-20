import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React from "react";
import { maxButtonWidth } from "../../utilities/Constants";
import "../common/Effects.scss";

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
}));

export default function StartGamePrompt() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Paper square style={{ maxWidth: maxButtonWidth }}>
        <Typography
          gutterBottom
          className="page-information page-information-animation"
        >
          Can a global high stakes social media game help inspire millions of
          Gen-Z and Millennial individuals to engage in social distancing and
          stop the spread of COVID-19?
        </Typography>
      </Paper>
    </div>
  );
}
