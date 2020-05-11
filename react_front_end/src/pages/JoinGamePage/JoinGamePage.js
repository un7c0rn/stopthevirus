import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "../common/AppTitle";
import Footer from "../common/Footer";
import JoinGamePrompt from "./JoinGamePrompt";
import JoinGameInputs from "./JoinGameInputs";

export default function JoinGamePage() {
  const useStyles = makeStyles((theme) => ({
    root: {
      background: theme.background,
      color: "white",
      height: "100vh",
      width: "100vw",
      display: "flex",
      flexDirection: "column",
      justifyContent: "flex-start",
      marginTop: "4em",
    },
  }));

  const classes = useStyles();

  return (
    <>
      <section className={classes.root} data-testid="Join Game Page">
        <AppTitle />
        <JoinGamePrompt />
        <JoinGameInputs />
        <Footer />
      </section>
    </>
  );
}
