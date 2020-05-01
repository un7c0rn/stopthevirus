import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import MuiPhoneNumber from "material-ui-phone-number";
import { isSm } from "../../utilities/Utilities";
import React, { useRef, useState } from "react";
import { startGame } from "../../mediators/GameMediator";

export default function StartGameInputs() {
  const sm = isSm();
  const useStyles = makeStyles(() => ({
    root: {
      display: "flex",
      flexWrap: "wrap",
      "& > *": {
        width: "100vw",
        height: sm ? "55vh" : "45vh",
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

  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} autoComplete="off">
          <TextField
            id="start-game-inputs-tiktok"
            label="Tik Tok"
            variant="outlined"
            inputRef={tikTokRef}
            error={didSubmit && tikTok === ""}
            onChange={(event) => setTikTok(event.target.value)}
            value={tikTok}
          />
          <MuiPhoneNumber
            error={didSubmit && phone.length <= 6}
            label="SMS Phone Number"
            defaultCountry={"us"}
            disableAreaCodes={true}
            onChange={handleOnPhoneChange}
            value={phone}
            id="start-game-inputs-phone"
          />
          <TextField
            id="start-game-inputs-game-name"
            label="Game Hashtag"
            variant="outlined"
            error={didSubmit && gameName === ""}
            onChange={(event) => setGameName(event.target.value)}
            inputRef={gameNameRef}
            value={gameName}
          />
          <Button variant="contained" onClick={submit}>
            Start a game
          </Button>
        </form>
      </Paper>
    </div>
  );
}
