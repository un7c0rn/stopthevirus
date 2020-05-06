import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import { maxButtonWidth } from "../../utilities/Constants";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    width: "100vw",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    margin: "1em 0",
    fontSize: "1em",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    "& > *": {
      margin: "1em 0",
    },
  },
}));

export default function GameInfoButtonOptions() {
  const classes = useStyles();

  const watchAciveVirusVideos = (e) => {
    console.log("do something");
  };

  const copyLinkToClipBoard = (e) => {
    console.log("do something");
  };

  return (
    <div className={classes.root}>
      <form className={classes.form} noValidate autoComplete="off">
        <Button
          variant="contained"
          onClick={watchAciveVirusVideos}
          style={{
            backgroundColor: "white",
            width: "100vw",
            maxWidth: maxButtonWidth,
            fontWeight: "bold",
          }}
        >
          watch active #vir-us videos
        </Button>
        <Button
          variant="contained"
          onClick={copyLinkToClipBoard}
          style={{
            backgroundColor: "white",
            width: "100vw",
            maxWidth: maxButtonWidth,
            fontWeight: "bold",
          }}
        >
          copy game invitation link
        </Button>
      </form>
    </div>
  );
}
