import React from "react";
import { makeStyles } from "@material-ui/core/styles";

export const UiForAppError = ({ error }) => {
  const useStyles = makeStyles((theme) => ({
    root: {
      background: theme.background,
      color: "black",
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
      <section
        className={classes.root}
        id="foo"
        data-testid="Game App Error Page"
      >
        {error.message}
      </section>
    </>
  );
};
