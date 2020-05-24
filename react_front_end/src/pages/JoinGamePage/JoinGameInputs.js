import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import { isL } from "../../utilities/Utilities";
import React, { useRef, useState } from "react";
import { maxButtonWidth } from "../../utilities/Constants";
import { joinGame } from "../../mediators/GameMediator";
import { useParams } from "react-router-dom";
import Notification from "../common/Notification";

export default function JoinGameInputs() {
  const isLarge = isL();
  const useStyles = makeStyles((theme) => ({
    root: {
      backgroundColor: "black",
      display: "flex",
      flexWrap: "wrap",
      marginBottom: "0.35em",
      paddingBottom: "4em",
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
        "&:nth-child(even)": {
          margin: "2em 0",
        },
      },
    },
  }));
  const classes = useStyles();

  const tikTokRef = useRef();

  const [tikTok, setTikTok] = useState("");
  const [didSubmit, setDidSubmit] = useState(false);
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState({});

  const MINIMUM_PHONE_NUMBER_LENGTH = 6;

  const { gameId } = useParams();

  const [responseCode, setResponse] = useState();

  const submit = async (event) => {
    console.log("send to API endpoint");
    console.log(tikTokRef.current.value);
    console.log(phone);
    console.log(country);

    setDidSubmit(true);

    const payload = {
      tiktok: tikTokRef.current.value,
      phone: phone.replace(/\+/, "").replace(/ /g, ""),
      game: gameId,
    };

    const response = await joinGame(payload);
    if (response) console.log("show success snack bar ===", response);

    response && setResponse(200);
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
  };

  const inputBlur = (e) => {
    let style = document.querySelector(`#${e.target.getAttribute("id")}-label`)
      .style;

    style.setProperty("width", "calc(100% - 28px)");
    style.removeProperty("transform");

    if (e.target === tikTokRef?.current && tikTokRef.current.value.length) {
      style.setProperty("text-align", "left");
    } else if (phone.length >= MINIMUM_PHONE_NUMBER_LENGTH) {
      style.setProperty("text-align", "left");
    } else {
      style.setProperty("text-align", "center");
    }
  };

  return (
    <>
      <Notification status={responseCode} />
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
              error={didSubmit && phone.length <= MINIMUM_PHONE_NUMBER_LENGTH}
              label="PHONE NUMBER"
              defaultCountry={"us"}
              disableAreaCodes={true}
              onFocus={inputClicked}
              onChange={handleOnPhoneChange}
              value={phone}
              id="join-game-inputs-phone"
              variant="outlined"
              InputLabelProps={inputLabelProps}
            />
            <Button
              variant="contained"
              onClick={submit}
              style={{
                backgroundColor: "white",
                width: "100vw",
                maxWidth: maxButtonWidth,
                fontWeight: "bold",
                borderRadius: "0",
              }}
            >
              JOIN THIS GAME
            </Button>
          </form>
        </Paper>
      </div>
    </>
  );
}
