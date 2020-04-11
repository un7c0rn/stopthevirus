import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import useMediaQuery from "@material-ui/core/useMediaQuery";

import React, { useRef } from "react";

export default function StartGameInputs() {
  const sm = useMediaQuery('(max-height:650px)');//for iphone 5SE
  const useStyles = makeStyles(theme => ({
    root: {
      display: "flex",
      flexWrap: "wrap",
      "& > *": {
        width: "100vw",
        height: sm ? "55vh" : "45vh",
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
  const classes = useStyles();

  const tikTokRef = useRef();
  const gameNameRef = useRef();
  let phone, country;

  const submit = event => {
    console.log("send to API endpoint");
    console.log(tikTokRef.current.value);
    console.log(gameNameRef.current.value);
    console.log(phone);
    console.log(country);
  };

  function handleOnPhoneChange(value,countryObj) {
    phone=value;
    country=countryObj;
 }

  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} noValidate autoComplete="off">
          <TextField
            id="outlined-basic"
            label="Tik Tok"
            variant="outlined"
            inputRef={tikTokRef}
          />
          <MuiPhoneNumber label="SMS Phone Number" defaultCountry={'us'} disableAreaCodes={true}
          onChange={handleOnPhoneChange}/>
          <TextField
            id="outlined-basic"
            label="Your Game Name"
            variant="outlined"
            inputRef={gameNameRef}
          />
          <Button variant="contained" onClick={submit}>
            Start a game
          </Button>
        </form>

      </Paper>
    </div>
  );
}
