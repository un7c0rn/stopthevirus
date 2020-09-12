/* eslint-disable no-restricted-globals */
import { CircularProgress } from "@material-ui/core";
import ErrorOutlineIcon from "@material-ui/icons/ErrorOutline";
import React, { useContext, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
// import { Link } from "react-router-dom";
import { useParams } from "react-router-dom";
import { AppContext } from "../../App";
import { JoinGameName } from "../common/JoinGameName";
import { JoinGameNameNumberOfPlayers } from "../common/JoinGameNameNumberOfPlayers";
import { JoinGameNameStartDateAndTime } from "../common/JoinGameNameStartDateAndTime";

export default function JoinGamePrompt() {
  const useStyles = makeStyles((theme) => ({
    root: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      width: "100vw",
      margin: "3em 0",
    },
    title: {
      margin: "1em",
      fontSize: "1em",
      textAlign: "center",
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

  const navigateToGameInfo = (e) => {
    location.href = `/game-info/${gameId}`;
  };

  return (
    <div className={classes.root}>
      {gameInfo === undefined ? problemWithUi() : null}
      {gameInfo && gameInfo?.game ? (
        <>
          <JoinGameName />
          <JoinGameNameNumberOfPlayers />
          <JoinGameNameStartDateAndTime />

          <Button
            style={{
              backgroundColor: "white",
              width: "100%",
              color: "black",
              alignSelf: "center",
              borderRadius: "0",
              fontWeight: "bold",
            }}
            onClick={navigateToGameInfo}
          >
            HOW THE GAME WORKS
          </Button>
        </>
      ) : gameInfo?.error === undefined ? (
        <CircularProgress className={classes.preloader} />
      ) : (
        <ErrorOutlineIcon className={classes.error} />
      )}
    </div>
  );
}
