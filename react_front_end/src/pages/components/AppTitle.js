import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import logo from "../../assets/vir-us_logotype_white.jpeg";
import bg from "../../assets/vir-us_world_map_white.jpeg";
//aspect ratio 310/2744

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    "& > *": {
      width: "100vw",
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
  const imgHeight = 20;

  return (
    <div className={classes.root}
    >
    <img src ={bg} style={{
      height:imgHeight+"vh"
    }}/>
    <img src={logo} style = {{
      position:"absolute",
      marginTop:imgHeight/4+"vh"
    }}/>
    </div>
  );
}
