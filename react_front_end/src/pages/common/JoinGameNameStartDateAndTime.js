import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React from "react";
// import { AppContext } from "../../App";

const useStyles = makeStyles((theme) => ({
  title: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    fontSize: "1em",
    margin: "1em",
  },
}));

export const JoinGameNameStartDateAndTime = () => {
  const classes = useStyles();

  const date = "5/1";
  const time = "9am PST";

  // const { gameInfo } = useContext(AppContext);

  return (
    <Typography
      variant="h3"
      component="h4"
      gutterBottom
      className={classes.title}
    >
      Game starts on {date} at {time}
    </Typography>
  );
};
