import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React, { useContext } from "react";
import { AppContext } from "../../App";

const useStyles = makeStyles((theme) => ({
  title: {
    display: "flex",
    fontSize: "1em",
    alignItems: "center",
    flexDirection: "column",
    justifyContent: "center",
    boxSizing: "border-box",
    margin: "1em",
  },
}));

export const JoinGameName = () => {
  const classes = useStyles();

  const { gameInfo } = useContext(AppContext);

  return (
    <Typography
      variant="h3"
      component="h4"
      gutterBottom
      className={classes.title}
      data-testid="Join Game Name"
    >
      You've been invited to "{gameInfo.game}"
    </Typography>
  );
};
