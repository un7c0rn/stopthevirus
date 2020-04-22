import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import ButtonAppBar from "./components/AppBar";
import AppTitle from "./components/AppTitle";
import Footer from "./components/Footer";
import GameInfo from "./components/GameInfo";
import GameInfoButtonOptions from "./components/GameInfoButtonOptions";

const GameInfoPage = () => {
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
        <ButtonAppBar />
        <AppTitle />
        <GameInfo />
        <GameInfoButtonOptions />
        <Footer />
      </section>
    </>
  );
};

export default GameInfoPage;
