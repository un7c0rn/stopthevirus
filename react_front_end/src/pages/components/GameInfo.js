import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import React, { useEffect, useContext } from "react";
import { GameName } from "./GameName";
import { NextChallenge } from "./NextChallenge";
import { NextTribalCouncil } from "./NextTribalCouncil";
import { NumberOfPlayers } from "./NumberOfPlayers";
import { useParams } from "react-router-dom";
import fetch from "node-fetch";
import { AppContext } from "../../App";
import { CircularProgress } from "@material-ui/core";

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
      alignItems: "space-around",
    },
  },
  title: {
    margin: "1em 0",
    fontSize: "1em",
  },
  preloader: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignSelf: "center",
  },
}));

export default function GameInfo() {
  const classes = useStyles();

  const { gameId } = useParams();

  const { gameInfo, setGameInfo } = useContext(AppContext);

  useEffect(() => {
    if (gameId) {
      console.log("game", gameId);
      (async () => {
        const response = await fetch(`/.netlify/functions/get_game_info`, {
          method: "POST",
          body: JSON.stringify({ game: gameId }),
        });
        const json = await response.json();
        console.log("API", json);
        setGameInfo(json);
      })();
    }
  }, []);

  return (
    <div className={classes.root}>
      <Paper square>
        {gameInfo ? (
          <>
            <GameName />
            <NumberOfPlayers />
            <NextChallenge />
            <NextTribalCouncil />
          </>
        ) : (
          <CircularProgress className={classes.preloader} />
        )}
      </Paper>
    </div>
  );
}
