import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import React, { useRef } from "react";
import { useParams } from "react-router-dom";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "25vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center"
    }
  },
  title: {
    margin: "1em 0",
    fontSize: "1em"
  },
  form: {
    display: "flex",
    flexDirection: "column",
    "& > *": {
      margin: "1em 0"
    }
  }
}));

export default function ChallengeSubmit() {
  const classes = useStyles();

  const inputRef = useRef();

  const { phone } = useParams();

  const { game } = useParams();

  const submit = event => {
    console.log("send to API endpoint");
    console.log(inputRef.current.value);
    console.log(phone);
    console.log(game);
  };

  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} noValidate autoComplete="off">
          <TextField
            id="outlined-basic"
            label="Your TikTok Video Link"
            variant="outlined"
            inputRef={inputRef}
          />
          <Button variant="contained" onClick={submit}>
            submit
          </Button>
        </form>
      </Paper>
    </div>
  );
}
