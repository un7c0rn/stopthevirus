import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import logo from "../../assets/vir-us_logotype_white.jpeg";
import bg from "./vir-us_world_map.jpeg";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    //background: "linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)",
  //  backgroundColor:"#424242",
    //backgroundImage:"url('./vir-us_world_map.jpeg')",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
      height: "20vh",
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
