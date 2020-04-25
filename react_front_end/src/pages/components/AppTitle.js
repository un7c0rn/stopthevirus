import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import logo from "../../assets/vir-us_logotype_white.jpeg";
//aspect ratio 310/2744

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "11.29vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    },
  },
  title: {
    margin: 0,
    fontSize: "4em"
  }
}));

export default function AppTitle() {
  const classes = useStyles();

  return (
    <div className={classes.root}
    >
    <img src={logo}/>
    </div>
  );
}
