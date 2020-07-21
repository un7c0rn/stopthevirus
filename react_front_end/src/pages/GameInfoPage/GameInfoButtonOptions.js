import Button from "@material-ui/core/Button";
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
    marginBottom: "0.35em",
    paddingBottom: "4em",
  },
  title: {
    margin: "1em 0",
    fontSize: "1em",
  },
  form: {
    display: "flex",
    flexDirection: "column",
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
            borderRadius: "0",
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
            borderRadius: "0",
            marginTop: "2em",
          }}
        >
          copy game invitation link
        </Button>
      </form>
    </div>
  );
}
