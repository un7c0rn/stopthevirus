import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import React, { useRef } from "react";
import { useParams } from "react-router-dom";
import ButtonAppBar from "./components/AppBar";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import ChallengeInfo from "./components/ChallengeInfo";
import ChallengeSubmit from "./components/ChallengeSubmit";
import StartGamePrompt from "./components/StartGamePrompt";
import StartGameInputs from "./components/StartGameInputs";

export default function StartGamePage() {
  const useStyles = makeStyles(theme => ({
    root: {
      background: theme.background,
      color: "white",
      height: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "flex-start"
    }
  }));

  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <ButtonAppBar />
        <AppTitle />
        <StartGamePrompt />
        <StartGameInputs />
        <Footer />
      </section>
    </>
  );
}
