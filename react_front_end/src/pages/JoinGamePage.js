import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import ButtonAppBar from "./components/AppBar";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import JoinGamePrompt from "./components/JoinGamePrompt";
import JoinGameInputs from "./components/JoinGameInputs";

export default function JoinGamePage() {
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
        <JoinGamePrompt />
        <JoinGameInputs />
        <Footer />
      </section>
    </>
  );
}
