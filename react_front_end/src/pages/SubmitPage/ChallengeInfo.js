import { CircularProgress } from "@material-ui/core";
import ErrorOutlineIcon from "@material-ui/icons/ErrorOutline";
import { makeStyles } from "@material-ui/core/styles";
import fetch from "node-fetch";
import React, { useContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import { AppContext } from "../../App";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import { GameName } from "../common/GameName";

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

  const { game } = useParams();

  const { gameInfo, setGameInfo } = useContext(AppContext);

  useEffect(() => {
    if (game) {
      console.log("game", game);
      (async () => {
        let response, json;
        response = await fetch(`/.netlify/functions/get_game_info`, {
          method: "POST",
          body: JSON.stringify({
            game: game,
          }),
        });

        json = await response?.json();

        if (response.status === 200 && json.error) {
          setGameInfo(json);
          problemWithUi();
        } else if (response.status === 200) {
          setGameInfo(json);
        }
      })();
    }
    // eslint-disable-next-line
  }, []);

  // Refactor into a group of custom errors
  const problemWithUi = () => {
    throw new Error("error with game info request");
  };

  useEffect(() => {
    if (gameInfo === undefined) {
      problemWithUi();
    }
  }, [gameInfo]);

  return (
    <div className={classes.root}>
      {gameInfo === undefined ? problemWithUi() : null}
      {gameInfo && gameInfo?.game ? (
        <>
          <Paper square>
            <GameName />
            <Typography
              variant="h3"
              component="h4"
              gutterBottom
              className={classes.title}
            >
              <span style={{ fontWeight: "bold" }}>Challenge</span>: Most
              Creative Homemade Mask
            </Typography>
            <Typography
              variant="h3"
              component="h4"
              gutterBottom
              className={classes.title}
            >
              <span style={{ fontWeight: "bold" }}>Time to submit</span>: 1 hour
              27 min
            </Typography>
          </Paper>
        </>
      ) : gameInfo?.error === undefined ? (
        <CircularProgress className={classes.preloader} />
      ) : (
        <ErrorOutlineIcon className={classes.error} />
      )}
    </div>
  );
}
