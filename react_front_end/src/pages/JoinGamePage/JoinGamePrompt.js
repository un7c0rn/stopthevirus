import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import NumberFormat from 'react-number-format';
import Button from "@material-ui/core/Button";
import {Link} from "react-router-dom";
import {isSm} from "../../utilities/Utilities";


export default function JoinGamePrompt() {
  const sm = isSm();
  const useStyles = makeStyles(theme => ({
    root: {
      display: "flex",
      flexWrap: "nowrap",
      "& > *": {
        width: "100vw",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      },
    },
    title: {
      margin: "1em",
      fontSize: "1em",
      textAlign: "center",
    },
  }));

  const classes = useStyles();
  const gameName = "LA Social Survivor";
  const numPlayers = 4000;
  const date = "5/1";
  const time = "9am PST";

  return (
    <div className={classes.root}>
      <Paper square>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}

        >
          You've been invited to "{gameName}"
        </Typography>

        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          <NumberFormat
            value={numPlayers}
            displayType={"text"}
            thousandSeparator={true}
          />
          + Players
        </Typography>

        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          Game starts on {date} at {time}
        </Typography>
        <Typography
          variant="h3"
          component="h4"
          gutterBottom
          className={classes.title}
        >
          <Link to='/game-info' style={{ textDecoration: "none" }} >
            <Button style={{fontWeight: "bold"}} >
              HOW THE GAME WORKS
            </Button>
          </Link>

        </Typography>
      </Paper>
    </div>
  );
}
