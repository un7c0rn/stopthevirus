import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import { isSm } from "../../utilities/Utilities";
import React, { useRef, useState, useEffect } from "react";
import { startGame } from "../../mediators/GameMediator";
import { maxButtonWidth } from "../../utilities/Constants";

export default function StartGameInputs() {
  const sm = isSm();
  const useStyles = makeStyles(() => ({
    root: {
      backgroundColor: "black",
      display: "flex",
      flexWrap: "wrap",
      "& > *": {
        width: "100vw",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      },
      "& > div div fieldset": {
        borderRadius: "0px",
        borderColor: "white",
      },
      "& > div label": {
        textAlign: "center",
        width: "calc(100% - 28px)",
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
  const classes = useStyles();

  const tikTokRef = useRef();
  const gameNameRef = useRef();

  const [tikTok, setTikTok] = useState("");
  const [didSubmit, setDidSubmit] = useState(false);
  const [gameName, setGameName] = useState("");
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState({});

  const submit = async () => {
    console.log("send to API endpoint");
    console.log(tikTokRef.current.value);
    console.log(gameNameRef.current.value);
    console.log(phone);
    console.log(country);

    setDidSubmit(true);

    const payload = {
      handle: tikTokRef.current.value,
      phone,
      hashtag: gameNameRef.current.value,
    };

    const response = await startGame(payload);
    if (response) console.log("show success snack bar ===", response);
  };

  function handleOnPhoneChange(value, countryObj) {
    setPhone(value);
    setCountry(countryObj);
  }

  const inputLabelProps = {
    style: {
      textAlign: "left",
    },
  };

  const inputClicked = (e) => {
    let style = document.querySelector(`#${e.target.getAttribute("id")}-label`)
      .style;

    style.setProperty("text-align", "left");
    style.setProperty("width", "auto");
    style.setProperty("color", "white");
  };

  const inputBlur = (e) => {
    document.querySelector(
      `#${e.target.getAttribute("id")}-label`
    ).style.textAlign = "center";
    document.querySelector(
      `#${e.target.getAttribute("id")}-label`
    ).style.width = "calc(100% - 28px)";
  };

  useEffect(() => {
    document.querySelectorAll(`fieldset`).forEach((element) => {
      element.style.borderColor = "white";
    });
    document.querySelectorAll(`label`).forEach((element) => {
      element.style.color = "white";
    });
  }, []);

  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} autoComplete="off">
          <TextField
            id="start-game-inputs-tiktok"
            label="TIK TOK"
            variant="outlined"
            inputRef={tikTokRef}
            error={didSubmit && tikTok === ""}
            onChange={(event) => setTikTok(event.target.value)}
            value={tikTok}
            className={classes.input}
            onClick={inputClicked}
            onBlur={inputBlur}
            InputLabelProps={{ id: "start-game-inputs-tiktok-label" }}
          />
          <MuiPhoneNumber
            error={didSubmit && phone.length <= 6}
            label="PHONE NUMBER"
            defaultCountry={"us"}
            disableAreaCodes={true}
            onChange={handleOnPhoneChange}
            value={phone}
            id="start-game-inputs-phone"
            variant="outlined"
            InputLabelProps={inputLabelProps}
          />
          <TextField
            id="start-game-inputs-game-name"
            label="GAME HASHTAG"
            variant="outlined"
            error={didSubmit && gameName === ""}
            onChange={(event) => setGameName(event.target.value)}
            inputRef={gameNameRef}
            value={gameName}
            onClick={inputClicked}
            onBlur={inputBlur}
            InputLabelProps={{ id: "start-game-inputs-game-name-label" }}
          />
        </form>
        <form className={classes.form} autoComplete="off">
          <Button
            variant="contained"
            onClick={submit}
            style={{
              backgroundColor: "white",
              width: "100vw",
              maxWidth: maxButtonWidth,
              fontWeight: "bold",
            }}
          >
            START A GAME
          </Button>
        </form>
      </Paper>
    </div>
  );
}
