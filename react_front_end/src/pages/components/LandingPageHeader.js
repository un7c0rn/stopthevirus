import { withStyles } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import React, { useState, useEffect, useContext, useCallback } from "react";
import { AppContext } from "../../App";

const useStyles = makeStyles((theme) => ({
  root: {
    color: "white",
    height: "50vh",
    width: "100vw",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  character: {
    fontSize: "30vw",
  },
}));

const LandingPageHeader = () => {
  const classes = useStyles();

  const { characterRef } = useContext(AppContext);

  let SPEED = 300;

  const CHARACTER_SET = "STOPTHEVIRUS#";

  const [character, setCharacter] = useState("#");
  const [characterIndex, setCharacterIndex] = useState(0);

  const incrementCharacterIndex = () => {
    setCharacterIndex((characterIndex) => characterIndex + 1);
    setCharacter(CHARACTER_SET[characterIndex]);
    if (characterIndex === CHARACTER_SET.length - 1) {
      console.log("hello");
      setCharacterIndex(0);
    } else {
    }
  };

  useEffect(() => {
    console.log("running interval once");
    characterRef.current = setInterval(incrementCharacterIndex, SPEED);

    console.log("characterIndex", characterIndex);
    return () => clearInterval(characterRef.current);
  }, [characterIndex]);

  return (
    <header className={classes.root}>
      <span className={classes.character}>{character}</span>
    </header>
  );
};

export default withStyles(useStyles)(LandingPageHeader);
