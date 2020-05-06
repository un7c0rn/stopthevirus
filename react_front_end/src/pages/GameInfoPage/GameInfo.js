import { CircularProgress } from "@material-ui/core";
import ErrorOutlineIcon from "@material-ui/icons/ErrorOutline";
import { makeStyles } from "@material-ui/core/styles";
import fetch from "node-fetch";
import React, { useContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import { AppContext } from "../../App";
import { GameName } from "../common/GameName";
import { NextChallenge } from "./NextChallenge";
import { NextTribalCouncil } from "./NextTribalCouncil";
import { NumberOfPlayers } from "./NumberOfPlayers";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    flexWrap: "wrap",
    width: "100vw",
    margin: "3em 0",
    "& > *": {
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
  error: {
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
        let response, json;
        response = await fetch(`/.netlify/functions/get_game_info`, {
          method: "POST",
          body: JSON.stringify({
            game: gameId,
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
          <GameName />
          <NumberOfPlayers />
          <NextChallenge />
          <NextTribalCouncil />
        </>
      ) : gameInfo?.error === undefined ? (
        <CircularProgress className={classes.preloader} />
      ) : (
        <ErrorOutlineIcon className={classes.error} />
      )}
    </div>
  );
}
