import { CircularProgress } from "@material-ui/core";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import fetch from "node-fetch";
import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { AppContext } from "../../App";
import { GameName } from "./GameName";
import { NextChallenge } from "./NextChallenge";
import { NextTribalCouncil } from "./NextTribalCouncil";
import { NumberOfPlayers } from "./NumberOfPlayers";

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
          body: JSON.stringify({
            game: gameId,
          }),
        });
        const json = await response.json();
        setGameInfo(json);
      })();
    }
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
      <Paper square>
        {gameInfo === undefined ? problemWithUi() : null}
        {gameInfo&&gameInfo.name ? (
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
