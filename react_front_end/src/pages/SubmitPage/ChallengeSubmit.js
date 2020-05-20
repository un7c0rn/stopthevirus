import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import React, { useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { maxButtonWidth } from "../../utilities/Constants";

const useStyles = makeStyles((theme) => ({
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

export default function ChallengeSubmit() {
  const classes = useStyles();

  const tikTokRef = useRef();

  const { phone } = useParams();

  const { game } = useParams();

  const [tikTok, setTikTok] = useState("");
  const [didSubmit, setDidSubmit] = useState(false);

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
    } else {
      style.setProperty("text-align", "center");
    }
  };

  const submit = async () => {
    console.log("send to API endpoint");
    console.log(tikTokRef.current.value);

    setDidSubmit(true);

    // const payload = {
    //   handle: tikTokRef.current.value,
    //   phone: phone.replace(/\+/, "").replace(/ /g, ""),
    //   hashtag: gameNameRef.current.value,
    // };

    // const response = await startGame(payload);
    // if (response) console.log("show success snack bar ===", response);
  };

  return (
    <div className={classes.root}>
      <Paper square>
        <form className={classes.form} noValidate autoComplete="off">
          <TextField
            id="challenge-submission-inputs-tiktok"
            label="YOUR TIKTOK VIDEO LINK"
            variant="outlined"
            inputRef={tikTokRef}
            error={didSubmit && !tikTok.length}
            onChange={(event) => setTikTok(event.target.value)}
            value={tikTok}
            className={classes.input}
            onFocus={inputClicked}
            onClick={inputClicked}
            onBlur={inputBlur}
            InputLabelProps={{ id: "challenge-submission-inputs-tiktok-label" }}
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
            submit
          </Button>
        </form>
      </Paper>
    </div>
  );
}
