import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import ButtonAppBar from "./components/AppBar";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import StartGamePrompt from "./components/StartGamePrompt";
import StartGameInputs from "./components/StartGameInputs";

export default function StartGamePage() {
  const useStyles = makeStyles((theme) => ({
    root: {
      background: theme.background,
      color: "white",
      height: "100vh",
      width: "100vw",
      display: "flex",
      flexDirection: "column",
      justifyContent: "flex-start",
    },
  }));

  const classes = useStyles();

  return (
    <>
      <section className={classes.root}>
        <AppTitle />
        <StartGamePrompt />
        <StartGameInputs />
        <Footer />
      </section>
    </>
  );
}
