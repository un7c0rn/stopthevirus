import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React, { useContext } from "react";
import { AppContext } from "../../App";

const useStyles = makeStyles((theme) => ({
  title: {
    width: "100vw",
    height: "auto",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    margin: "0",
    fontSize: "1em",
  },
}));

export const NextChallenge = () => {
  const classes = useStyles();

  return (
    <Typography
      variant="h3"
      component="h4"
      gutterBottom
      className={classes.title}
    >
      <p>
        <span style={{ fontWeight: "bold" }}>Next challenge</span>: 5/1 10am PST
      </p>
    </Typography>
  );
};
