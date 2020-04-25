import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import logo from "../../assets/vir-us_triangle_logo_white.jpeg";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",//10 by 9 aspect ratio
      height: "10vh",
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

export default function TriangleLogo() {
  const classes = useStyles();

  return (
    <div className={classes.root}
    >
      <img src={logo} style={{width:"30vw",height:"27vw", margin:"0 auto"}}/>
    </div>
  );
}
