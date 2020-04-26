import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import React, { useRef } from "react";
import { useParams } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "25vh",
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
      <Paper square>
        <form className={classes.form} noValidate autoComplete="off">
          <Button variant="contained" onClick={watchAciveVirusVideos}
          style={{backgroundColor:'white',
                width:'100vw',
                fontWeight: 'bold',}}>
            watch active #vir-us videos
          </Button>
          <Button variant="contained" onClick={copyLinkToClipBoard}
          style={{backgroundColor:'white',
                width:'100vw',
                fontWeight: 'bold',}}>
            copy game invitation link
          </Button>
        </form>
      </Paper>
    </div>
  );
}
