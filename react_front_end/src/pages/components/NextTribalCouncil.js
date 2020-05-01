import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import React from "react";

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

export const NextTribalCouncil = () => {
  const classes = useStyles();

  return (
    <Typography
      variant="h3"
      component="h4"
      gutterBottom
      className={classes.title}
    >
      <p>
        <span style={{ fontWeight: "bold" }}>Next tribal council</span>: 8pm PST
      </p>
    </Typography>
  );
};
