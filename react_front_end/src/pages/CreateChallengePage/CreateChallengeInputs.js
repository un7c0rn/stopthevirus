import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import React, { useRef, useState } from "react";
import { maxButtonWidth } from "../../utilities/Constants";
import { useParams } from "react-router-dom";
import { createChallenge } from "../../mediators/GameMediator";
import Notification from "../common/Notification";

export default function CreateChallengeInputs() {
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

  const challengeRef = useRef();
  const challengeInstructionsRef = useRef();

  const [challengeName, setChallengeName] = useState("");
  const [didSubmit, setDidSubmit] = useState(false);
  const [challengeInstructions, setChallengeInstructions] = useState("");

  const { phone, game } = useParams();

  const [responseCode, setResponse] = useState();

  const submit = async () => {
    console.log("send to API endpoint");
    console.log(challengeRef.current.value);
    console.log(challengeInstructionsRef.current.value);

    setDidSubmit(true);

    const payload = {
      game,
      name: challengeRef.current.value,
      message: challengeInstructionsRef.current.value,
      phone,
    };
    const response = await createChallenge(payload);

    // TODO send payload to mediator
    if (response) console.log("show success snack bar ===", response);

    response && setResponse(200);
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

    if (
      e.target === challengeRef?.current &&
      challengeRef.current.value.length
    ) {
      style.setProperty("text-align", "left");
    } else if (
      e.target === challengeInstructionsRef?.current &&
      challengeInstructionsRef.current.value.length
    ) {
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
              id="challenge-name"
              label="YOUR CHALLENGE NAME"
              variant="outlined"
              inputRef={challengeRef}
              error={didSubmit && !challengeName.length}
              onChange={(event) => setChallengeName(event.target.value)}
              value={challengeName}
              className={classes.input}
              onFocus={inputClicked}
              onClick={inputClicked}
              onBlur={inputBlur}
              InputLabelProps={{
                id: "challenge-name-label",
              }}
            />
            <TextField
              id="challenge-instructions"
              label="YOUR CHALLENGE INSTRUCTIONS"
              variant="outlined"
              error={didSubmit && challengeInstructions === ""}
              onChange={(event) => setChallengeInstructions(event.target.value)}
              inputRef={challengeInstructionsRef}
              value={challengeInstructions}
              onFocus={inputClicked}
              onClick={inputClicked}
              onBlur={inputBlur}
              InputLabelProps={{
                id: "challenge-instructions-label",
              }}
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
              CREATE CHALLENGE
            </Button>
          </form>
        </Paper>
      </div>
    </>
  );
}
