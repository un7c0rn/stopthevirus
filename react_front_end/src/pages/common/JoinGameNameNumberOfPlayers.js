import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React, { useContext } from "react";
import { AppContext } from "../../App";
import NumberFormat from "react-number-format";

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

export const JoinGameNameNumberOfPlayers = () => {
  const classes = useStyles();

  const { gameInfo } = useContext(AppContext);

  return (
    <Typography
      variant="h3"
      component="h4"
      gutterBottom
      className={classes.title}
      style={{ display: "flex", flexDirection: "row" }}
    >
      <NumberFormat
        value={gameInfo.count_players}
        displayType={"text"}
        thousandSeparator={true}
        style={{ display: "inline-block" }}
      />
      <span>+ Players</span>
    </Typography>
  );
};
