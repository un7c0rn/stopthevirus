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

export default function CreateChallengePrompt() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Paper square style={{ maxWidth: maxButtonWidth }}>
        <Typography
          gutterBottom
          className="page-information page-information-animation"
        >
          Challenges are scored using Tik Tok video likes divided by the number
          of views. Challenges are reviewed and may be removed without notice.
        </Typography>
        <Typography
          gutterBottom
          className="page-information page-information-animation"
        >
          Good challange ideas are fun, encouraging social distancing and are
          easy to score by liking on Tik Tok.
        </Typography>
      </Paper>
    </div>
  );
}
