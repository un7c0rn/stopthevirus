import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import { isSm, isL } from "../../utilities/Utilities";
import React, { useRef, useState, useEffect } from "react";
import { maxButtonWidth } from "../../utilities/Constants";

export default function JoinGameInputs() {
  const sm = isSm();
  const isLarge = isL();
  const useStyles = makeStyles((theme) => ({
    root: {
      backgroundColor: "black",
      display: "flex",
      flexWrap: "wrap",
      "& > *": {
        width: "100vw",
        height: isLarge ? "50vh" : "",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      },
      "& > div div fieldset": {
        borderRadius: "0px",
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

  const [tikTok, setTikTok] = useState("");
  const [didSubmit, setDidSubmit] = useState(false);
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState({});

  const submit = (event) => {
    console.log("send to API endpoint");
    console.log(tikTokRef.current.value);
    console.log(phone);
    console.log(country);

    setDidSubmit(true);
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
    const node = document.querySelector(`#${e.target.getAttribute("id")}`);
    let style = document.querySelector(`#${e.target.getAttribute("id")}-label`)
      .style;

    if (!node.value.length) {
      style.setProperty("text-align", "center");
      style.setProperty("width", "calc(100% - 28px)");
    }
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
            id="join-game-inputs-tiktok"
            label="TIK TOK"
            variant="outlined"
            inputRef={tikTokRef}
            error={didSubmit && tikTok === ""}
            onChange={(event) => setTikTok(event.target.value)}
            value={tikTok}
            onFocus={inputClicked}
            onClick={inputClicked}
            onBlur={inputBlur}
            InputLabelProps={{ id: "join-game-inputs-tiktok-label" }}
          />
          <MuiPhoneNumber
            error={didSubmit && phone.length <= 6}
            label="PHONE NUMBER"
            defaultCountry={"us"}
            disableAreaCodes={true}
            onChange={handleOnPhoneChange}
            value={phone}
            id="join-game-inputs-phone"
            variant="outlined"
            InputLabelProps={inputLabelProps}
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
            JOIN THIS GAME
          </Button>
        </form>
      </Paper>
    </div>
  );
}
