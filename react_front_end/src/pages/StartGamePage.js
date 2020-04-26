import { makeStyles } from "@material-ui/core/styles";
import React from "react";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import StartGamePrompt from "./components/StartGamePrompt";
import StartGameInputs from "./components/StartGameInputs";
import TriangleLogo from "./components/TriangleLogo";

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
        <TriangleLogo />
        <StartGameInputs />
        <Footer />
      </section>
    </>
  );
}
